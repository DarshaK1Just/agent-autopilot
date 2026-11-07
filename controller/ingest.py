"""Streaming, idempotent, memory-bounded event ingestion.

Each chunk is parsed line by line, reduced to integer columns, grouped with numpy and merged into
additive SQLite counters. Counters and cursor commit in one transaction (exactly-once per chunk).
Peak memory is one chunk's columns plus the live lead->feature map (leads are evicted once their
campaign can no longer be dialled).
"""
from __future__ import annotations

import json
import logging
import time
from datetime import date

import numpy as np

from .client import SimClient
from .store import Store

log = logging.getLogger("controller.ingest")

FEATURES = ("lang", "city_tier", "age_band", "value_band")
AGENT_DIMS = ("welcome_message", "voice", "caller_id", "prompt_version")
BLK_MIN = 360  # aggregation block, minutes
UNK = "?"


class Interner:
    def __init__(self):
        self.ids: dict[str, int] = {}
        self.names: list[str] = []

    def __call__(self, s: str) -> int:
        i = self.ids.get(s)
        if i is None:
            i = self.ids[s] = len(self.names)
            self.names.append(s)
        return i


def _group_sum(cols: list[tuple[np.ndarray, int]], vals: list[np.ndarray]):
    """Group-by on packed int64 keys; returns decoded key columns and per-group sums."""
    key = np.zeros(len(vals[0]), dtype=np.int64)
    for c, radix in cols:
        key = key * radix + c
    uk, inv = np.unique(key, return_inverse=True)
    sums = [np.bincount(inv, weights=v, minlength=len(uk)).astype(np.int64) for v in vals]
    out = []
    rem = uk.copy()
    for c, radix in reversed(cols):
        out.append(rem % radix)
        rem //= radix
    out.reverse()
    return out, sums


class Ingestor:
    def __init__(self, store: Store, client: SimClient):
        self.store, self.client = store, client
        self.feat_list: list[list[str]] = store.get("feat_list", [])
        self.feat_idx: dict[tuple, int] = {tuple(f): i for i, f in enumerate(self.feat_list)}
        self.leads: dict[str, int] = {}
        for r in store.q("SELECT lead_id, feat FROM leads"):
            self.leads[r["lead_id"]] = r["feat"]
        self.d0: date | None = date.fromisoformat(store.get("d0")) if store.get("d0") else None
        self._date_cache: dict[str, int] = {}
        self.totals = {"events": 0, "calls": 0, "malformed": 0, "unjoined": 0, "seconds": 0.0, "chunks": 0}

    def set_d0(self, ts: str, sim_minute: int):
        if self.d0 is None:
            d = date.fromisoformat(ts[:10])
            self.d0 = date.fromordinal(d.toordinal() - sim_minute // 1440)
            self.store.put("d0", self.d0.isoformat())

    def _day(self, d: str) -> int:
        v = self._date_cache.get(d)
        if v is None:
            v = self._date_cache[d] = date.fromisoformat(d).toordinal() - self.d0.toordinal()
        return v

    def minute_of(self, ts: str) -> int:
        return self._day(ts[:10]) * 1440 + int(ts[11:13]) * 60 + int(ts[14:16])

    # ------------------------------------------------------------------ public
    def pending(self) -> list[dict]:
        """Chunks not yet ingested, history first, in global order."""
        done_h, done_e = self.store.get("cur_history", -1), self.store.get("cur_events", -1)
        return self.client.chunks("history", done_h) + self.client.chunks("events", done_e)

    def ingest_chunk(self, meta: dict) -> dict:
        t0 = time.perf_counter()
        kind = meta["kind"]
        last_eid = self.store.get("last_event_id", 0)
        if meta["last_event_id"] <= last_eid and kind == "events":
            self.store.put(f"cur_{kind}", meta["chunk"])
            return {"skipped": True}
        n_ev = 0
        with self.store.tx():
            batch: list[dict] = []
            for ln in self.client.stream_chunk(meta["chunk"]):
                try:
                    batch.append(json.loads(ln))
                except ValueError:
                    self.totals["malformed"] += 1
                    continue
                if len(batch) >= 60000:
                    n_ev += self._process(batch, last_eid, kind)
                    batch = []
            if batch:
                n_ev += self._process(batch, last_eid, kind)
            self.store.put(f"cur_{kind}", meta["chunk"])
            self.store.put("last_event_id", max(last_eid, meta["last_event_id"]))
            self.store.put("feat_list", self.feat_list)
        dt = time.perf_counter() - t0
        self.totals["seconds"] += dt
        self.totals["chunks"] += 1
        return {"events": n_ev, "seconds": dt}

    def prune_leads(self, current_day: int, horizon_days: int):
        """Evict leads whose campaign can no longer be dialled (bounds memory and table size)."""
        cutoff = current_day - horizon_days
        old = [r["lead_id"] for r in self.store.q("SELECT lead_id FROM leads WHERE day < ?", (cutoff,))]
        if not old:
            return
        for k in old:
            self.leads.pop(k, None)
        with self.store.tx():
            self.store.run("DELETE FROM leads WHERE day < ?", (cutoff,))

    # ------------------------------------------------------------------ internals
    def _process(self, evs: list[dict], last_eid: int, kind: str) -> int:
        wfs, cohs, opts, vers = Interner(), Interner(), Interner(), Interner()
        c_wf, c_ver, c_coh, c_min = [], [], [], []
        c_dims: list[list[int]] = [[], [], [], []]
        c_feat, c_conn, c_eng, c_flag = [], [], [], []
        new_leads: list[tuple[str, int, int]] = []
        ctl: list[tuple] = []
        leads = self.leads
        minute_of = self.minute_of
        n = 0
        for ev in evs:
            if kind == "events" and ev.get("event_id", 0) <= last_eid:
                continue
            n += 1
            t = ev.get("type")
            if t == "call":
                try:
                    v = ev["variant"]
                    row = (ev["workflow_id"], ev["config_version"], ev["cohort_id"], minute_of(ev["ts"]),
                           v["welcome_message"], v["voice"], v["caller_id"], v["prompt_version"],
                           bool(ev["connected"]), bool(ev["engaged"]), ev["lead_id"], ev.get("qa"))
                except (KeyError, TypeError, ValueError):
                    self.totals["malformed"] += 1
                    continue
                c_wf.append(wfs(row[0]))
                c_ver.append(row[1])
                c_coh.append(cohs(row[2]))
                c_min.append(row[3])
                for i in range(4):
                    c_dims[i].append(opts(row[4 + i]))
                f = leads.get(row[10], -1)
                if f < 0:
                    self.totals["unjoined"] += 1
                c_feat.append(f)
                c_conn.append(1 if row[8] else 0)
                c_eng.append(1 if row[9] else 0)
                c_flag.append(1 if row[8] and row[11] and row[11].get("hallucination_flag") else 0)
            elif t == "lead":
                ft = tuple(ev["features"].get(k, UNK) for k in FEATURES)
                i = self.feat_idx.get(ft)
                if i is None:
                    i = self.feat_idx[ft] = len(self.feat_list)
                    self.feat_list.append(list(ft))
                leads[ev["lead_id"]] = i
                new_leads.append((ev["lead_id"], self._day(ev["ts"][:10]), i))
            elif t in ("config_changed", "approval_decided"):
                ctl.append((ev["event_id"], t, ev.get("workflow_id"), ev["ts"], minute_of(ev["ts"]), json.dumps(ev)))
        if new_leads:
            self.store.db.executemany("INSERT OR IGNORE INTO leads(lead_id,day,feat) VALUES(?,?,?)", new_leads)
        if ctl:
            self.store.db.executemany(
                "INSERT OR IGNORE INTO ctl_events(event_id,type,wf,ts,minute,payload) VALUES(?,?,?,?,?,?)", ctl)
        if c_wf:
            self._aggregate(wfs, cohs, opts, vers, c_wf, c_ver, c_coh, c_min, c_dims, c_feat, c_conn, c_eng, c_flag)
            self.totals["calls"] += len(c_wf)
        self.totals["events"] += n
        return n

    def _aggregate(self, wfs, cohs, opts, vers, c_wf, c_ver, c_coh, c_min, c_dims, c_feat, c_conn, c_eng, c_flag):
        a_wf = np.array(c_wf, dtype=np.int64)
        a_ver = np.array(c_ver, dtype=np.int64)
        a_coh = np.array(c_coh, dtype=np.int64)
        minute = np.array(c_min, dtype=np.int64)
        blk = minute // BLK_MIN
        blk_lo = int(blk.min())
        blk_rel = blk - blk_lo
        day = minute // 1440
        day_lo = int(day.min())
        day_rel = day - day_lo
        hour = (minute % 1440) // 60
        conn = np.array(c_conn, dtype=np.int64)
        eng = np.array(c_eng, dtype=np.int64)
        flag = np.array(c_flag, dtype=np.int64)
        ones = np.ones(len(conn), dtype=np.int64)
        feat = np.array(c_feat, dtype=np.int64)

        # per-feature value codes, with an extra slot for "unknown lead"
        slices: list[tuple[str, np.ndarray, list[str]]] = [("all", np.zeros(len(conn), dtype=np.int64), [""])]
        for fi, fname in enumerate(FEATURES):
            vals = Interner()
            lut = np.array([vals(f[fi]) for f in self.feat_list] + [vals(UNK)], dtype=np.int64)
            slices.append((fname, lut[feat], vals.names))  # feat == -1 indexes the trailing UNK slot
        R_wf, R_blk = len(wfs.names), int(blk_rel.max()) + 1
        R_ver = int(a_ver.max()) + 1
        R_coh, R_opt = len(cohs.names), len(opts.names)
        R_day = int(day_rel.max()) + 1

        agg_rows, hr_rows = [], []
        for di, dim in enumerate(AGENT_DIMS):
            o = np.array(c_dims[di], dtype=np.int64)
            for sname, scode, snames in slices:
                R_sv = len(snames)
                (g_wf, g_blk, g_ver, g_coh, g_opt, g_sv), (d, c, e) = _group_sum(
                    [(a_wf, R_wf), (blk_rel, R_blk), (a_ver, R_ver), (a_coh, R_coh), (o, R_opt), (scode, R_sv)],
                    [ones, conn, eng])
                for i in range(len(d)):
                    agg_rows.append((wfs.names[g_wf[i]], int(g_blk[i]) + blk_lo, int(g_ver[i]), cohs.names[g_coh[i]],
                                     dim, opts.names[g_opt[i]], sname, snames[g_sv[i]], int(d[i]), int(c[i]), int(e[i])))
        for sname, scode, snames in slices:
            (g_wf, g_day, g_hour, g_sv), (d, c, e) = _group_sum(
                [(a_wf, R_wf), (day_rel, R_day), (hour, 24), (scode, len(snames))], [ones, conn, eng])
            for i in range(len(d)):
                hr_rows.append((wfs.names[g_wf[i]], int(g_day[i]) + day_lo, int(g_hour[i]), sname, snames[g_sv[i]],
                                int(d[i]), int(c[i]), int(e[i])))
        # QA only exists on connected calls; the prompt is the 4th agent dim
        m = conn == 1
        qa_rows = []
        if m.any():
            p = np.array(c_dims[3], dtype=np.int64)[m]
            (g_wf, g_blk, g_ver, g_p), (n_c, n_f) = _group_sum(
                [(a_wf[m], R_wf), (blk_rel[m], R_blk), (a_ver[m], R_ver), (p, R_opt)], [ones[m], flag[m]])
            for i in range(len(n_c)):
                qa_rows.append((wfs.names[g_wf[i]], int(g_blk[i]) + blk_lo, int(g_ver[i]), opts.names[g_p[i]],
                                int(n_c[i]), int(n_f[i])))
        db = self.store.db
        db.executemany("INSERT INTO agg VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(wf,blk,ver,coh,dim,opt,sl,sv) DO UPDATE "
                       "SET dials=dials+excluded.dials, conn=conn+excluded.conn, eng=eng+excluded.eng", agg_rows)
        db.executemany("INSERT INTO hr VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(wf,day,hour,sl,sv) DO UPDATE "
                       "SET dials=dials+excluded.dials, conn=conn+excluded.conn, eng=eng+excluded.eng", hr_rows)
        db.executemany("INSERT INTO qa VALUES(?,?,?,?,?,?) ON CONFLICT(wf,blk,ver,prompt) DO UPDATE "
                       "SET conn=conn+excluded.conn, flagged=flagged+excluded.flagged", qa_rows)
