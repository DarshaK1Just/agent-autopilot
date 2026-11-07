"""Durable state. One SQLite file in WAL mode; every multi-row change happens in one transaction.

Invariant: the ingest cursor and the aggregates it produced are committed together, so a crash
replays a chunk from scratch or not at all. Proposals are written (PLANNED) before their side
effect and reconciled against the simulator on restart.
"""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL);

-- Additive counters. dim in (welcome_message, voice, caller_id, prompt_version); sl is the one-feature
-- slice ('all' or a feature name) and sv its value. blk = 6h block index since D0 (negative = history).
CREATE TABLE IF NOT EXISTS agg (
  wf TEXT, blk INT, ver INT, coh TEXT, dim TEXT, opt TEXT, sl TEXT, sv TEXT,
  dials INT NOT NULL, conn INT NOT NULL, eng INT NOT NULL,
  PRIMARY KEY (wf, blk, ver, coh, dim, opt, sl, sv)
) WITHOUT ROWID;

-- Hour-of-day behaviour by slice, bucketed by day.
CREATE TABLE IF NOT EXISTS hr (
  wf TEXT, day INT, hour INT, sl TEXT, sv TEXT, dials INT NOT NULL, conn INT NOT NULL, eng INT NOT NULL,
  PRIMARY KEY (wf, day, hour, sl, sv)
) WITHOUT ROWID;

-- Automated QA flags on connected calls.
CREATE TABLE IF NOT EXISTS qa (
  wf TEXT, blk INT, ver INT, prompt TEXT, conn INT NOT NULL, flagged INT NOT NULL,
  PRIMARY KEY (wf, blk, ver, prompt)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS leads (lead_id TEXT PRIMARY KEY, day INT NOT NULL, feat INT NOT NULL) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS leads_day ON leads(day);

-- Rare control-plane events (config_changed, approval_decided) queued inside the ingest transaction so
-- a crash between ingest and handling cannot lose them.
CREATE TABLE IF NOT EXISTS ctl_events (event_id INT PRIMARY KEY, type TEXT, wf TEXT, ts TEXT, minute INT,
  payload TEXT, handled INT DEFAULT 0);

CREATE TABLE IF NOT EXISTS workflows (wf TEXT PRIMARY KEY, spec TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS config_versions (
  wf TEXT, version INT, actor TEXT, applied_at TEXT, minute INT, changed_dims TEXT,
  proposal_id TEXT, approval_id TEXT, config TEXT, PRIMARY KEY (wf, version)
);

CREATE TABLE IF NOT EXISTS cohorts (
  wf TEXT, cid TEXT, where_json TEXT NOT NULL, status TEXT NOT NULL, evidence TEXT, created_minute INT,
  PRIMARY KEY (wf, cid)
);

-- One row per (workflow, lever). `state` carries the phase machine; `design` the allocation under test.
CREATE TABLE IF NOT EXISTS experiments (
  id TEXT PRIMARY KEY, wf TEXT NOT NULL, dim TEXT NOT NULL, phase TEXT NOT NULL,
  control TEXT, arms TEXT, started_minute INT, started_version INT, updated_minute INT, state TEXT
);
CREATE INDEX IF NOT EXISTS exp_wf ON experiments(wf, dim);

-- Holds placed on a dimension (e.g. after a supervisor edit) so we do not fight a human.
CREATE TABLE IF NOT EXISTS holds (wf TEXT, dim TEXT, until_minute INT, reason TEXT, PRIMARY KEY (wf, dim));

CREATE TABLE IF NOT EXISTS proposals (
  pid TEXT PRIMARY KEY, wf TEXT NOT NULL, route TEXT NOT NULL, state TEXT NOT NULL, base_version INT NOT NULL,
  dims TEXT, intent_keys TEXT, proposed_config TEXT, body TEXT, approval_id TEXT,
  created_minute INT, submitted_minute INT, decided_minute INT, expires_minute INT, apply_by_minute INT,
  applied_version INT, result TEXT, reasons TEXT, urgent INT DEFAULT 0
);
CREATE INDEX IF NOT EXISTS prop_wf ON proposals(wf, state);

CREATE TABLE IF NOT EXISTS incidents (
  id TEXT PRIMARY KEY, wf TEXT NOT NULL, kind TEXT NOT NULL, state TEXT NOT NULL,
  opened_minute INT, closed_minute INT, evidence TEXT, data TEXT
);
CREATE INDEX IF NOT EXISTS inc_wf ON incidents(wf, state);

CREATE TABLE IF NOT EXISTS validations (
  run_id TEXT PRIMARY KEY, wf TEXT, prompt TEXT, n INT, failures INT, pass_rate REAL, minute INT, incident_id TEXT
);

CREATE TABLE IF NOT EXISTS credits (id INTEGER PRIMARY KEY AUTOINCREMENT, minute INT, wf TEXT, kind TEXT,
  amount REAL, balance REAL, purpose TEXT);

CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, minute INT, ts TEXT, wall REAL, wf TEXT, kind TEXT, actor TEXT,
  summary TEXT, detail TEXT, proposal_id TEXT, ref TEXT
);
CREATE INDEX IF NOT EXISTS audit_wf ON audit(wf, minute);
CREATE INDEX IF NOT EXISTS audit_prop ON audit(proposal_id);

CREATE TABLE IF NOT EXISTS metrics (wall REAL, minute INT, name TEXT, value REAL);
"""


class Store:
    def __init__(self, path: str):
        self.path = path
        self.db = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")
        self.db.executescript(SCHEMA)
        self._depth = 0
        self.now_minute = int(self.get("now_minute", 0))
        self.now_ts = self.get("now_ts", "")

    @contextmanager
    def tx(self):
        if self._depth:
            self._depth += 1
            try:
                yield self.db
            finally:
                self._depth -= 1
            return
        self.db.execute("BEGIN IMMEDIATE")
        self._depth = 1
        try:
            yield self.db
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        finally:
            self._depth = 0

    def q(self, sql: str, args=()) -> list[sqlite3.Row]:
        return self.db.execute(sql, args).fetchall()

    def one(self, sql: str, args=()):
        return self.db.execute(sql, args).fetchone()

    def run(self, sql: str, args=()):
        if self._depth:
            return self.db.execute(sql, args)
        with self.tx():
            return self.db.execute(sql, args)

    # --- key/value
    def get(self, k: str, default=None):
        r = self.one("SELECT v FROM kv WHERE k=?", (k,))
        return json.loads(r["v"]) if r else default

    def put(self, k: str, v):
        self.run("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, json.dumps(v)))

    def set_clock(self, minute: int, ts: str):
        self.now_minute, self.now_ts = minute, ts
        self.put("now_minute", minute)
        self.put("now_ts", ts)

    # --- audit: the answer to "why did workflow X change"
    def audit(self, kind: str, summary: str, *, wf: str | None = None, actor: str = "controller",
              detail: dict | None = None, proposal_id: str | None = None, ref: str | None = None):
        self.run("INSERT INTO audit(minute,ts,wall,wf,kind,actor,summary,detail,proposal_id,ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
                 (self.now_minute, self.now_ts, time.time(), wf, kind, actor, summary,
                  json.dumps(detail or {}, default=str, sort_keys=True), proposal_id, ref))

    def metric(self, name: str, value: float):
        self.run("INSERT INTO metrics(wall,minute,name,value) VALUES(?,?,?,?)", (time.time(), self.now_minute, name, value))

    def close(self):
        self.db.close()
