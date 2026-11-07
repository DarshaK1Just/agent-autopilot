"""The always-on loop: advance -> ingest -> reconcile governance -> detect/plan -> propose."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

from . import evidence as ev
from .client import SimClient, SimError, SimUnavailable
from .governance import Governor
from .incidents import Incidents
from .ingest import Ingestor
from .planner import LEVERS, WfCtx, apply_exp_update, plan_caller_id, plan_lever
from .policy import Policy
from .store import Store

log = logging.getLogger("controller")


class Controller:
    def __init__(self, url: str, db_path: str, pol: Policy | None = None):
        self.pol = pol or Policy()
        self.store = Store(db_path)
        self.client = SimClient(url)
        self.ing = Ingestor(self.store, self.client)
        self.inc = Incidents(self.store, self.client, self.pol)
        self.gov = Governor(self.store, self.client, self.pol, self.ing.minute_of, self.affected_leads,
                            on_applied=self._applied, on_failed=self._failed)
        self.specs: dict[str, dict] = {}
        self.cfgs: dict[str, dict] = {}
        self.end_minute = 0
        self.last_eval: dict[str, int] = {}
        self.step_wall = 0.0

    # ------------------------------------------------------------------ hooks
    def _applied(self, prop: dict, version: int):
        self.refresh_config(prop["wf"])
        self.inc.on_applied(prop, version)

    def _failed(self, prop: dict, state: str):
        self.inc.on_failed(prop, state)

    def affected_leads(self, wf: str, info: dict) -> int:
        lo, hi = f"{wf}:", f"{wf};"
        n = self.store.one("SELECT COUNT(*) n FROM leads WHERE lead_id>=? AND lead_id<?", (lo, hi))["n"]
        if info.get("all") or not info.get("patch_scopes"):
            return n
        where = {c["id"]: c["where"] for c in info["cohorts"]}
        cnt = 0
        feats = {r["feat"]: r["n"] for r in self.store.q(
            "SELECT feat, COUNT(*) n FROM leads WHERE lead_id>=? AND lead_id<? GROUP BY feat", (lo, hi))}
        for fi, c in feats.items():
            ft = dict(zip(("lang", "city_tier", "age_band", "value_band"), self.ing.feat_list[fi]))
            for cid in info["patch_scopes"]:
                w = where.get(cid)
                if w and all(ft.get(k) in v for k, v in w.items()):
                    cnt += c
                    break
        return cnt

    # ------------------------------------------------------------------ startup
    def startup(self):
        st = self.client.state()
        self.ing.set_d0(st["ts"], st["sim_minute"])
        self.end_minute = st["end_minute"]
        self.store.set_clock(st["sim_minute"], st["ts"])
        self.inc.credits = st["credits_remaining"]
        for w in self.client.workflows():
            self.specs[w["workflow_id"]] = w
            self.store.run("INSERT OR REPLACE INTO workflows VALUES(?,?)", (w["workflow_id"], json.dumps(w)))
        first = not self.store.get("started")
        self.store.audit("controller_start", f"controller {'started' if first else 'RESTARTED'} at {st['ts']}",
                         detail={"cursor_events": self.store.get("cur_events", -1), "cursor_history": self.store.get("cur_history", -1),
                                 "open_proposals": [r["pid"] for r in self.store.q("SELECT pid FROM proposals WHERE state IN ('PLANNED','PENDING','APPROVED')")]})
        self.store.put("started", True)
        seen = self.store.get("credits_seen")
        if seen is not None and st["credits_remaining"] < seen - 1e-9:
            # The simulator charged credits that our ledger never recorded: a crash between the charge and our commit.
            self.store.audit("credit_spend_unrecorded", f"{seen - st['credits_remaining']:.0f} credits were spent but no result was recorded "
                             "(crash between charge and commit; the API has no way to fetch a past validation/LLM result)",
                             detail={"ledger_balance": seen, "simulator_balance": st["credits_remaining"]})
        self.store.put("credits_seen", st["credits_remaining"])
        for wf in self.specs:
            self.refresh_config(wf)
        self.reconcile()

    def ingest_pending(self) -> int:
        """Ingest up to `max_chunks_per_tick` chunks; returns how many are still waiting (the backlog)."""
        pend = self.ing.pending()
        before = dict(self.ing.stage)
        t0 = time.perf_counter()
        n = 0
        for m in pend[: self.pol.max_chunks_per_tick]:
            n += self.ing.ingest_chunk(m).get("events", 0)
        dt = time.perf_counter() - t0
        if n:
            self.store.metric("ingest_events", n)
            self.store.metric("ingest_seconds", dt)
            self.store.metric("ingest_events_per_sec", n / max(dt, 1e-9))
            for k, v in self.ing.stage.items():
                self.store.metric(f"stage_{k}_seconds", v - before[k])
        self.handle_control_events()
        cur_day = self.store.now_minute // 1440
        horizon = max((len(s["cadence"]) for s in self.specs.values()), default=3) + 1
        self.ing.prune_leads(cur_day, horizon)
        return max(len(pend) - self.pol.max_chunks_per_tick, 0)

    # ------------------------------------------------------------------ config tracking / supervisor edits
    def refresh_config(self, wf: str):
        doc = self.client.config(wf)
        prev = self.cfgs.get(wf)
        self.cfgs[wf] = doc
        if self.store.one("SELECT 1 FROM config_versions WHERE wf=? AND version=?", (wf, doc["version"])):
            return
        hist = {h["version"]: h for h in self.client.config_history(wf)}
        h = hist.get(doc["version"], {})
        with self.store.tx():
            self.store.run("INSERT OR REPLACE INTO config_versions VALUES(?,?,?,?,?,?,?,?,?)",
                           (wf, doc["version"], doc["actor"], doc["applied_at"], self.store.now_minute,
                            json.dumps(h.get("changed_dims", [])), h.get("proposal_id"), h.get("approval_id"), json.dumps(doc["config"])))
            if doc["actor"] == "supervisor":
                dims = h.get("changed_dims", [])
                for d in dims:
                    if d != "prompt_version":
                        self.store.run("INSERT OR REPLACE INTO holds VALUES(?,?,?,?)",
                                       (wf, d, self.store.now_minute + self.pol.supervisor_hold_minutes, f"supervisor edit v{doc['version']}"))
                mine = self.store.q("SELECT pid,state FROM proposals WHERE wf=? AND state IN ('PLANNED','PENDING','APPROVED')", (wf,))
                self.store.audit("supervisor_edit", f"supervisor changed {dims} -> v{doc['version']}; holds placed, in-flight "
                                 f"proposals {[p['pid'] for p in mine]} will go stale and be re-planned from the new config", wf=wf, actor="supervisor",
                                 detail={"version": doc["version"], "changed_dims": dims, "previous_version": prev["version"] if prev else None})
            elif doc["actor"].startswith("controller"):
                pass
            else:
                self.store.audit("config_observed", f"v{doc['version']} by {doc['actor']}", wf=wf, actor=doc["actor"])

    def handle_control_events(self):
        for r in self.store.q("SELECT * FROM ctl_events WHERE handled=0 ORDER BY event_id"):
            if r["type"] == "config_changed" and r["wf"] in self.specs:
                self.refresh_config(r["wf"])
            self.store.run("UPDATE ctl_events SET handled=1 WHERE event_id=?", (r["event_id"],))

    def held(self, wf: str) -> set[str]:
        return {r["dim"] for r in self.store.q("SELECT dim FROM holds WHERE wf=? AND until_minute>?", (wf, self.store.now_minute))}

    # ------------------------------------------------------------------ governance
    def reconcile(self):
        versions = {wf: d["version"] for wf, d in self.cfgs.items()}
        self.gov.reconcile(self.specs, versions)
        for wf in self.specs:
            self.refresh_config(wf)

    # ------------------------------------------------------------------ evaluation
    def ctx(self, wf: str) -> WfCtx:
        d = self.cfgs[wf]
        return WfCtx(self.store, self.specs[wf], d["config"], d["version"], self.store.now_minute, self.end_minute, self.pol)

    def safety(self, wf: str):
        """P0 work, every tick: incident detection, verification and the fix proposal."""
        ctx = self.ctx(wf)
        self.inc.check(ctx)
        self.inc.verify(ctx)
        urgent = self.inc.respond(ctx)
        if urgent and self.gov.propose(ctx, urgent) is None:
            self.inc.reopen(wf)

    def plan_routine(self, wf: str):
        """P2/P3 work: welcome/voice tests, decay watch, caller-ID health. One batched proposal per workflow."""
        ctx = self.ctx(wf)
        if self.inc.active(wf) or self.gov.in_flight(wf):
            return
        held = self.held(wf)
        intents = []
        for dim in LEVERS:
            intents += plan_lever(ctx, dim, dim in held or "cohorts" in held)
        if "caller_id" not in held:
            last = self.store.one("SELECT MAX(created_minute) m FROM proposals WHERE wf=? AND dims LIKE '%caller_id%' AND state!='STALE'", (wf,))
            intents += plan_caller_id(ctx, (last["m"] or -10**9))
        for i in [i for i in intents if not i.patch and i.exp_update]:
            apply_exp_update(self.store, wf, i.exp_update, ctx.version)  # state-only: no config change, no proposal
            self.store.audit("experiment_reset", i.summary, wf=wf, detail=i.evidence)
        intents = [i for i in intents if i.patch]
        if intents:
            self.gov.propose(ctx, intents)

    def followups(self):
        for r in self.store.q("SELECT a.proposal_id pid, a.wf wf, a.minute m FROM audit a WHERE a.kind='proposal_applied' AND a.minute<=?",
                              (self.store.now_minute - 1440,)):
            if self.store.get(f"followup:{r['pid']}"):
                continue
            p = self.specs.get(r["wf"])
            if not p:
                continue
            b = r["m"] // ev.BLK
            def window(lo, hi):
                x = self.store.one("SELECT SUM(dials) d, SUM(conn) c, SUM(eng) e FROM agg WHERE wf=? AND dim='voice' AND sl='all' AND blk>=? AND blk<?",
                                   (r["wf"], lo, hi))
                return {"dials": x["d"] or 0, "pickup_rate": round((x["c"] or 0) / max(x["d"] or 1, 1), 4),
                        "engagement_rate": round((x["e"] or 0) / max(x["c"] or 1, 1), 4)}
            pre_w, post_w = window(b - 4, b), window(b, b + 4)
            self.store.put(f"followup:{r['pid']}", True)
            self.store.audit("followup", f"24h after apply: {p['objective']['primary']} pre {pre_w[p['objective']['primary']]} -> post {post_w[p['objective']['primary']]} "
                             "(descriptive; not causal)", wf=r["wf"], proposal_id=r["pid"], detail={"pre": pre_w, "post": post_w})

    # ------------------------------------------------------------------ main loop
    def step_minutes(self) -> int:
        busy = self.store.one("SELECT 1 FROM proposals WHERE state IN ('PENDING','APPROVED','PLANNED')")
        return 15 if busy else 60

    def advance(self, minutes: int) -> dict:
        before = self.store.now_minute
        try:
            return self.client.advance(minutes)
        except SimUnavailable:
            st = self.client.state()
            if st["sim_minute"] > before:
                return {"sim_minute": st["sim_minute"], "ts": st["ts"], "finished": st["finished"], "new_chunks": []}
            raise
        except SimError as e:
            if e.code == "finished":
                st = self.client.state()
                return {"sim_minute": st["sim_minute"], "ts": st["ts"], "finished": True, "new_chunks": []}
            raise

    def run(self) -> int:
        self.startup()
        finished = self.client.state()["finished"]
        backlog = len(self.ing.pending())
        while True:
            if not finished and backlog == 0:  # never ask for more data while there is unread data
                r = self.advance(self.step_minutes())
                finished = r["finished"]
                st = self.client.state()
                self.store.set_clock(st["sim_minute"], st["ts"])
                self.inc.credits = st["credits_remaining"]
                self.store.put("credits_seen", st["credits_remaining"])
            t0 = time.perf_counter()
            backlog = self.ingest_pending()                       # P1: ingestion, bounded per tick
            t1 = time.perf_counter()
            self.reconcile()                                      # P0: approved changes, stale/abandoned proposals
            t2 = time.perf_counter()
            for wf in self.specs:
                self.safety(wf)                                   # P0: incidents
            t3 = time.perf_counter()
            due = sorted((wf for wf in self.specs if self.store.now_minute - self.last_eval.get(wf, -10**9) >= self.pol.eval_interval_minutes),
                         key=lambda w: self.last_eval.get(w, -10**9))
            if backlog == 0:                                      # P2/P3 are deferred while evidence is incomplete
                for wf in due[: self.pol.max_routine_evals_per_tick]:
                    self.last_eval[wf] = self.store.now_minute
                    self.plan_routine(wf)
            self.followups()
            t4 = time.perf_counter()
            m = self.store.metric
            m("ingest_backlog_chunks", backlog)
            m("t_ingest_seconds", t1 - t0)
            m("t_governance_seconds", t2 - t1)
            m("t_incident_seconds", t3 - t2)
            m("t_planning_seconds", t4 - t3)
            m("decision_lag_seconds", t4 - t1)                    # everything except ingestion
            m("step_seconds", t4 - t0)
            m("routine_due", len(due))
            m("rss_mb", rss_mb())
            m("db_mb", sum(os.path.getsize(f) for f in (self.store.path, self.store.path + "-wal") if os.path.exists(f)) / 1e6)
            m("open_proposals", self.store.one("SELECT COUNT(*) n FROM proposals WHERE state IN ('PENDING','APPROVED','PLANNED')")["n"])
            m("open_incidents", self.store.one("SELECT COUNT(*) n FROM incidents WHERE state NOT IN ('RESOLVED','ESCALATED')")["n"])
            m("credits_remaining", self.inc.credits or 0)
            m("sim_http_errors", self.client.stats["errors"])
            m("sim_http_retries", self.client.stats["retries"])
            if finished and backlog == 0:
                break
        self.store.audit("controller_done", f"scenario finished at {self.store.now_ts}; controller exiting cleanly")
        return 0


def rss_mb() -> float:
    with open("/proc/self/statm") as f:
        return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 1e6


def world_key(client: SimClient) -> str:
    """Identity of the simulated world: a restarted simulator (or another scenario) is a new world."""
    st = client.state()
    first = (client.chunks("history") or client.chunks("events") or [{}])[0]
    wfs = sorted(w["workflow_id"] for w in client.workflows())
    return json.dumps([st["scenario"], st["end_minute"], first.get("last_event_id"), first.get("until_ts"), wfs])


def ensure_matching_db(path: str, key: str) -> str | None:
    """If `path` belongs to a different world, move it aside so stale cursors can never be applied to a new world."""
    import os
    import sqlite3
    if not os.path.exists(path):
        return None
    try:
        db = sqlite3.connect(path)
        row = db.execute("SELECT v FROM kv WHERE k='world_key'").fetchone()
        db.close()
    except sqlite3.DatabaseError:
        row = None
    if row is None or json.loads(row[0]) == key:
        return None
    dest = f"{path}.{int(time.time())}.old"
    for suffix in ("", "-wal", "-shm"):
        if os.path.exists(path + suffix):
            os.replace(path + suffix, dest + suffix)
    return dest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--db", default="controller_state.db")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING, format="%(asctime)s %(name)s %(message)s")
    probe = SimClient(a.url)
    key = world_key(probe)
    probe.close()
    moved = ensure_matching_db(a.db, key)
    if moved:
        log.warning("existing state belongs to a different simulator world; archived as %s", moved)
    c = Controller(a.url, a.db)
    c.store.put("world_key", key)
    try:
        return c.run()
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
