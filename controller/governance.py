"""Proposal lifecycle against the governance boundary.

PLANNED -> PENDING -> APPROVED -> APPLIED     (approval route)
PLANNED -> APPLIED                            (policy-permitted auto-apply route)
PENDING -> REJECTED | EXPIRED | ABANDONED (base moved while waiting) ;  APPROVED -> LAPSED | STALE (base moved)

A row is written PLANNED *before* any request leaves the process, with a deterministic id derived from
(workflow, base version, proposed config). After a crash, `reconcile` finds out from the simulator whether the
request landed and adopts it instead of resending, so restarts cannot duplicate or lose a proposal.
"""
from __future__ import annotations

import json
import math
from typing import Callable

from . import cfgutil
from .client import SimClient, SimError, SimUnavailable
from .planner import Intent, WfCtx, apply_exp_update
from .policy import Policy
from .store import Store

OPEN_STATES = ("PLANNED", "PENDING", "APPROVED")
# The whole state machine. Anything not listed is terminal. Every change of `proposals.state` goes through Governor._move.
TRANSITIONS = {
    "PLANNED": {"PENDING", "APPLIED", "STALE", "REFUSED", "FAILED", "ABANDONED"},
    "PENDING": {"APPROVED", "REJECTED", "EXPIRED", "LAPSED", "APPLIED", "ABANDONED", "FAILED"},
    "APPROVED": {"APPLIED", "LAPSED", "STALE", "FAILED", "ABANDONED"},
}


class InvalidTransition(Exception):
    pass


def next_working(minute: int, hours: list[int]) -> int:
    lo, hi = hours
    day, mod = divmod(minute, 1440)
    if mod < lo * 60:
        return day * 1440 + lo * 60
    if mod >= hi * 60:
        return (day + 1) * 1440 + lo * 60
    return minute


class Governor:
    def __init__(self, store: Store, client: SimClient, pol: Policy, minute_of: Callable[[str], int],
                 affected_fn: Callable[[str, dict], int], on_applied: Callable[[dict, int], None] | None = None,
                 on_failed: Callable[[dict, str], None] | None = None):
        self.s, self.c, self.pol, self.minute_of = store, client, pol, minute_of
        self.affected_fn = affected_fn
        self.on_applied = on_applied
        self.on_failed = on_failed

    def _move(self, pid: str, new: str, **cols):
        cur = self.s.one("SELECT state FROM proposals WHERE pid=?", (pid,))["state"]
        if new not in TRANSITIONS.get(cur, ()):
            raise InvalidTransition(f"{pid}: {cur} -> {new}")
        sets = ", ".join(f"{k}=?" for k in ("state", *cols))
        self.s.run(f"UPDATE proposals SET {sets} WHERE pid=?", (new, *cols.values(), pid))

    # ------------------------------------------------------------------ queries
    def in_flight(self, wf: str):
        return self.s.q("SELECT * FROM proposals WHERE wf=? AND state IN ('PLANNED','PENDING','APPROVED')", (wf,))

    def submitted_last_24h(self, wf: str) -> int:
        return self.s.one("SELECT COUNT(*) n FROM proposals WHERE wf=? AND route='approval' AND submitted_minute IS NOT NULL "
                          "AND submitted_minute > ?", (wf, self.s.now_minute - 1440))["n"]

    def routine_today(self, wf: str) -> int:
        day0 = (self.s.now_minute // 1440) * 1440
        return self.s.one("SELECT COUNT(*) n FROM proposals WHERE wf=? AND route='approval' AND urgent=0 "
                          "AND submitted_minute >= ?", (wf, day0))["n"]

    # ------------------------------------------------------------------ composition + routing
    def compose(self, ctx: WfCtx, intents: list[Intent]) -> tuple[dict, list[str]]:
        new = ctx.cfg
        for i in intents:
            new = cfgutil.apply_patch(new, i.patch)
        return new, cfgutil.changed_dims(ctx.cfg, new)

    def choose_route(self, ctx: WfCtx, new: dict, dims: list[str], intents: list[Intent]) -> str:
        pol_a = ctx.spec["governance"]["auto_apply"]
        shift = cfgutil.max_shift(ctx.cfg, new)
        permitted = pol_a.get("enabled") and all(d in pol_a.get("allowed_dims", []) for d in dims) \
            and shift <= pol_a.get("max_shift", 0) + 1e-9
        customer = any(d in cfgutil.CUSTOMER_FACING for d in dims)
        protective = all(i.protective for i in intents)
        # Customer-facing growth moves go to a human even where policy would allow auto-apply: supervisors asked to
        # be told first. Protective moves (rollbacks, harm stops, incident fixes) use the fast path when permitted.
        return "auto" if permitted and (not customer or protective) else "approval"

    def can_submit(self, ctx: WfCtx, urgent: bool) -> tuple[bool, str]:
        g, pol = ctx.spec["governance"], self.pol
        now = self.s.now_minute
        worst_decision = next_working(now + g["approver_latency_minutes"][1], g["approver_hours"])
        if worst_decision - now > g["proposal_ttl_hours"] * 60 - 15:
            return False, "worst-case decision time falls after proposal TTL (approver offline)"
        slots = g["max_requests_per_24h"] - (0 if urgent else pol.incident_slots)
        if self.submitted_last_24h(ctx.wf) + 1 > slots:
            return False, f"request budget ({g['max_requests_per_24h']}/24h, {pol.incident_slots} reserved for incidents)"
        if not urgent:
            if (now % 1440) // 60 < pol.routine_earliest_hour:
                return False, f"routine requests wait until {pol.routine_earliest_hour}:00"
            if self.routine_today(ctx.wf) >= pol.routine_max_per_day:
                return False, "daily routine request cap reached (batching)"
        return True, ""

    # ------------------------------------------------------------------ submission
    def propose(self, ctx: WfCtx, intents: list[Intent]) -> dict | None:
        if not intents:
            return None
        new, dims = self.compose(ctx, intents)  # always built from the live config plus the intended diff
        if not dims:
            return None
        urgent = any(i.urgent for i in intents)
        flying = self.in_flight(ctx.wf)
        if flying and not urgent:
            return None  # one routine proposal at a time, and never alongside anything else
        superseded = []
        for p in flying:
            if p["urgent"]:
                return None  # one urgent proposal at a time
            if set(dims) & set(json.loads(p["dims"])):
                superseded.append(p)  # same dimension: the routine one would race the urgent one, so it yields
            # Disjoint dimensions may coexist; the base-version check still serialises their applies, so the second one
            # to land goes STALE and is re-planned from the new base.
        route = self.choose_route(ctx, new, dims, intents)
        fp = cfgutil.fingerprint(new)
        prior = self.s.q("SELECT state, submitted_minute, created_minute FROM proposals WHERE wf=? AND base_version=? AND pid LIKE ?",
                         (ctx.wf, ctx.version, f"{ctx.wf}-v{ctx.version}-{fp}%"))
        if any(p["state"] in OPEN_STATES for p in prior):
            return None
        n_prev = len(prior)
        if route == "approval" and not urgent:
            same = self.s.q("SELECT state, created_minute FROM proposals WHERE wf=? AND pid LIKE ? ORDER BY created_minute DESC",
                            (ctx.wf, f"%-{fp}%"))
            attempts = len(same)
            if attempts >= 3 or (same and self.s.now_minute - same[0]["created_minute"] < 6 * 60):
                return None
        if route == "approval":
            ok, why = self.can_submit(ctx, urgent)
            if not ok:
                if self.s.get(f"deferred:{ctx.wf}") != why:
                    self.s.put(f"deferred:{ctx.wf}", why)
                    self.s.audit("deferred", f"proposal deferred: {why}", wf=ctx.wf,
                                 detail={"intents": [i.key for i in intents], "reason": why})
                return None
            self.s.put(f"deferred:{ctx.wf}", None)
        for p in superseded:
            self._terminal(p, "ABANDONED", f"superseded by an urgent change touching {sorted(set(dims) & set(json.loads(p['dims'])))}", {})
        pid = f"{ctx.wf}-v{ctx.version}-{fp}" + (f"-r{n_prev}" if n_prev else "")
        body = self._body(ctx, intents, new, dims, pid)
        with self.s.tx():
            self.s.run("INSERT INTO proposals(pid,wf,route,state,base_version,dims,intent_keys,proposed_config,body,created_minute,urgent) "
                       "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                       (pid, ctx.wf, route, "PLANNED", ctx.version, json.dumps(dims),
                        json.dumps([{"key": i.key, "kind": i.kind, "exp_update": i.exp_update, "summary": i.summary} for i in intents]),
                        json.dumps(new, sort_keys=True), json.dumps(body, default=str), self.s.now_minute, int(urgent)))
            self.s.audit("proposal_planned", body["change_summary"], wf=ctx.wf, proposal_id=pid, actor="controller",
                         detail={"route": route, "dims": dims, "base_version": ctx.version, "diff": body["diff"],
                                 "evidence": body.get("evidence"), "dry_run": body["dry_run"], "impact_score": body["impact_score"],
                                 "affected_leads": body["affected_leads"], "rationale": body["rationale"],
                                 "intents": [{"key": i.key, "kind": i.kind, "evidence": i.evidence} for i in intents],
                                 "policy": {"max_shift": cfgutil.max_shift(ctx.cfg, new), "auto": ctx.spec["governance"]["auto_apply"]}})
        return self._send(self._row(pid), ctx.spec)

    def _body(self, ctx: WfCtx, intents: list[Intent], new: dict, dims: list[str], pid: str) -> dict:
        d = cfgutil.diff(ctx.cfg, new)
        gain = max(i.expected_rel_lift * i.pop_share * i.confidence for i in intents)
        impact = max(0.01, min(1.0, round(1 - math.exp(-gain / 0.03), 3)))
        if any(i.kind == "prompt_fix" for i in intents):
            impact = max(impact, 0.9)
        dry = {i.kind: i.dry_run for i in intents if i.dry_run} or {"note": "no historical replay possible for this change",
                                                                      "reason": "operational change without recorded counterfactual"}
        evidence: dict = {"intents": {i.key: i.evidence for i in intents}}
        vr = next((i.validation_run_id for i in intents if i.validation_run_id), None)
        if vr:
            evidence["validation_run_id"] = vr
        scopes = {}
        for i in intents:
            scopes.update(i.patch.get("allocations", {}))
        affected = self.affected_fn(ctx.wf, {"patch_scopes": list(scopes), "cohorts": new["cohorts"],
                                              "all": any(s == "default" for s in scopes) or "prompt_version" in dims
                                              or ("schedule" in dims and not scopes)})
        return {"proposal_id": pid, "workflow_id": ctx.wf, "base_version": ctx.version, "proposed_config": new,
                "change_summary": "; ".join(i.summary for i in intents)[:300], "diff": d, "affected_leads": int(affected),
                "dry_run": dry, "impact_score": impact,
                "rationale": " ".join(i.rationale for i in intents), "evidence": evidence}

    def _row(self, pid: str):
        return self.s.one("SELECT * FROM proposals WHERE pid=?", (pid,))

    def _send(self, p, spec: dict) -> dict | None:
        wf, pid = p["wf"], p["pid"]
        body = json.loads(p["body"])
        try:
            if p["route"] == "auto":
                r = self.c.auto_apply(wf, {k: body[k] for k in ("proposal_id", "base_version", "proposed_config", "rationale", "evidence")})
                self._applied(p, r["version"])
            else:
                r = self.c.post_approval(body)
                self._adopt(p, r)
        except SimError as e:
            self._on_error(p, e)
        except SimUnavailable as e:
            self.s.audit("sim_unavailable", f"{pid}: ambiguous failure, will reconcile ({e})", wf=wf, proposal_id=pid)
        return self._row(pid)

    def _adopt(self, p, appr: dict):
        exp = self.minute_of(appr["expires_at"])
        sub = self.s.now_minute
        with self.s.tx():
            self._move(p["pid"], "PENDING", approval_id=appr["approval_id"], submitted_minute=sub, expires_minute=exp)
            self.s.audit("proposal_submitted", f"approval {appr['approval_id']} requested; expires {appr['expires_at']}",
                         wf=p["wf"], proposal_id=p["pid"], detail={"approval": appr})

    def _on_error(self, p, e: SimError):
        pid, wf = p["pid"], p["wf"]
        if e.code == "stale_base_version":
            self._terminal(p, "STALE", f"base version moved (current {e.detail})", {"detail": e.detail})
        elif e.code == "duplicate_proposal_id":
            found = [a for a in self.c.approvals(wf) if a["proposal_id"] == pid]
            if found:
                self._adopt(p, found[0])
            else:
                hist = [h for h in self.c.config_history(wf) if h["proposal_id"] == pid]
                if hist:
                    self._applied(p, hist[0]["version"])
                else:
                    self._terminal(p, "FAILED", "duplicate id but no trace in simulator", {})
        elif e.code == "auto_apply_not_permitted":
            self._terminal(p, "REFUSED", f"auto-apply refused: {e.detail}", {"reasons": e.detail})
        elif e.code == "out_of_credits" or e.status == 409 and e.code == "finished":
            self._terminal(p, "FAILED", e.code, {})
        else:
            self._terminal(p, "FAILED", f"{e.status} {e.code}: {e.detail}", {"detail": e.detail})

    def _terminal(self, p, state: str, why: str, detail: dict):
        with self.s.tx():
            self._move(p["pid"], state, result=json.dumps(detail, default=str), reasons=why)
            self.s.audit(f"proposal_{state.lower()}", why, wf=p["wf"], proposal_id=p["pid"], detail=detail,
                         actor="simulator" if state in ("REJECTED", "EXPIRED", "LAPSED") else "controller")
        if self.on_failed:
            self.on_failed(dict(self._row(p["pid"])), state)

    def _applied(self, p, version: int):
        with self.s.tx():
            self._move(p["pid"], "APPLIED", applied_version=version,
                       decided_minute=self._row(p["pid"])["decided_minute"] or self.s.now_minute)
            self.s.audit("proposal_applied", f"config v{version} live", wf=p["wf"], proposal_id=p["pid"],
                         detail={"version": version, "route": p["route"]})
            for it in json.loads(p["intent_keys"] or "[]"):
                if it.get("exp_update"):
                    apply_exp_update(self.s, p["wf"], it["exp_update"], version)
        if self.on_applied:
            self.on_applied(dict(self._row(p["pid"])), version)

    # ------------------------------------------------------------------ reconciliation (every tick and on restart)
    def reconcile(self, specs: dict[str, dict], current_versions: dict[str, int]):
        for p in self.s.q("SELECT * FROM proposals WHERE state IN ('PLANNED','PENDING','APPROVED')"):
            wf = p["wf"]
            try:
                if p["state"] == "PLANNED":
                    self._reconcile_planned(p, current_versions[wf])
                elif p["state"] == "PENDING":
                    if p["base_version"] < current_versions[wf]:
                        self._terminal(p, "ABANDONED", f"config moved v{p['base_version']} -> v{current_versions[wf]} while pending; "
                                       "the approval can no longer be applied, planning resumes from the new base", {})
                        continue
                    self._poll_pending(p)
                elif p["state"] == "APPROVED":
                    self._apply_approved(self._row(p["pid"]))
            except SimUnavailable as e:
                self.s.audit("sim_unavailable", f"{p['pid']}: {e}", wf=wf, proposal_id=p["pid"])

    def _reconcile_planned(self, p, cur_ver: int):
        wf, pid = p["wf"], p["pid"]
        if p["route"] == "approval":
            found = [a for a in self.c.approvals(wf) if a["proposal_id"] == pid]
            if found:
                self._adopt(p, found[0])
                return
        else:
            hist = [h for h in self.c.config_history(wf) if h["proposal_id"] == pid]
            if hist:
                self._applied(p, hist[0]["version"])
                return
        if p["base_version"] != cur_ver:
            self._terminal(p, "STALE", f"base v{p['base_version']} superseded by v{cur_ver} before submission", {})
            return
        self._send(p, {})

    def _poll_pending(self, p):
        a = self.c.approval(p["approval_id"])
        st = a["status"]
        if st == "pending":
            return
        dm = self.minute_of(a["decided_at"]) if a.get("decided_at") else self.s.now_minute
        if st == "approved":
            with self.s.tx():
                self._move(p["pid"], "APPROVED", decided_minute=dm, apply_by_minute=self.minute_of(a["apply_by"]))
                self.s.audit("proposal_approved", f"approved by client approver at {a['decided_at']}; apply by {a['apply_by']}",
                             wf=p["wf"], proposal_id=p["pid"], actor="client_approver", detail=a)
            self._apply_approved(self._row(p["pid"]))
        elif st == "applied":
            hist = [h for h in self.c.config_history(p["wf"]) if h["approval_id"] == p["approval_id"]]
            self._applied(p, hist[0]["version"]) if hist else self._terminal(p, "FAILED", "applied without history", a)
        else:
            self._terminal(p, st.upper() if st in ("rejected", "expired", "lapsed") else "FAILED",
                           f"{st}: {'; '.join(a.get('reasons') or []) or 'no reason given'}", a)

    def _apply_approved(self, p):
        try:
            r = self.c.apply(p["wf"], p["approval_id"])
            self._applied(p, r["version"])
        except SimError as e:
            if e.code == "stale_base_version":
                self._terminal(p, "STALE", f"approved but config changed before apply (current {e.detail})", {"detail": e.detail})
            elif e.code == "approval_lapsed":
                self._terminal(p, "LAPSED", "approved change not applied inside apply window", {})
            elif e.code == "not_approved":
                self.s.audit("apply_state_mismatch", f"{e.detail}", wf=p["wf"], proposal_id=p["pid"])
                a = self.c.approval(p["approval_id"])
                if a["status"] == "applied":
                    hist = [h for h in self.c.config_history(p["wf"]) if h["approval_id"] == p["approval_id"]]
                    if hist:
                        self._applied(p, hist[0]["version"])
            else:
                self._terminal(p, "FAILED", f"apply failed {e.status} {e.code}", {"detail": e.detail})
