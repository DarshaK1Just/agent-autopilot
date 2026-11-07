"""Read-only queries over the controller's own store.

  python -m controller.cli --db controller_state.db explain  --wf nw_renewal --at "D3 14:00"
  python -m controller.cli --db controller_state.db proposal <proposal_id>
  python -m controller.cli --db controller_state.db supervisor
  python -m controller.cli --db controller_state.db health
  python -m controller.cli --db controller_state.db log --wf ks_cancel [--limit 50]
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import date, timedelta


def fmt(db, minute: int) -> str:
    d0 = date.fromisoformat(json.loads(db.execute("SELECT v FROM kv WHERE k='d0'").fetchone()[0]))
    d = d0 + timedelta(days=minute // 1440)
    return f"{d.isoformat()} {minute % 1440 // 60:02d}:{minute % 60:02d} (D{minute // 1440})"


def parse_at(s: str) -> int:
    m = re.match(r"D(\d+)\s+(\d+):(\d+)", s.strip())
    if not m:
        raise SystemExit("--at must look like 'D3 14:00'")
    return int(m[1]) * 1440 + int(m[2]) * 60 + int(m[3])


def j(x):
    return json.loads(x) if x else None


def explain(db, wf: str, at: int):
    vers = db.execute("SELECT * FROM audit WHERE wf=? AND kind='proposal_applied' ORDER BY minute", (wf,)).fetchall()
    chosen = None
    for v in vers:
        if v["minute"] <= at:
            chosen = v
    sup = db.execute("SELECT * FROM audit WHERE wf=? AND kind='supervisor_edit' AND minute<=? ORDER BY minute DESC LIMIT 1", (wf, at)).fetchone()
    if sup and (chosen is None or sup["minute"] > chosen["minute"]):
        print(f"[{wf}] at {fmt(db, at)} the most recent change was a SUPERVISOR edit at {fmt(db, sup['minute'])}: {sup['summary']}")
        print("   (supervisor edits bypass governance; the controller recorded it and placed a 48h hold on those dimensions)")
        if chosen is None:
            return
        print("   Last controller change before it:")
    if chosen is None:
        print(f"[{wf}] no controller change on or before {fmt(db, at)}")
        return
    pid = chosen["proposal_id"]
    p = db.execute("SELECT * FROM proposals WHERE pid=?", (pid,)).fetchone()
    body = j(p["body"])
    print(f"[{wf}] config v{p['applied_version']} went live at {fmt(db, chosen['minute'])} (route: {p['route']}; dims: {', '.join(j(p['dims']))})")
    print(f"  WHY    : {body['change_summary']}")
    print(f"           {body['rationale']}")
    print(f"  CHANGE : {json.dumps(body['diff'], default=str)[:700]}")
    print(f"  SCOPE  : affected_leads={body['affected_leads']}  impact_score={body['impact_score']}  base_version={p['base_version']}")
    print(f"  DRY RUN: {json.dumps(body['dry_run'], default=str)[:600]}")
    print("  TIMELINE (from controller audit):")
    for a in db.execute("SELECT * FROM audit WHERE proposal_id=? ORDER BY id", (pid,)):
        print(f"    {fmt(db, a['minute'])}  {a['kind']:<20} [{a['actor']}] {a['summary'][:150]}")
    planned = db.execute("SELECT detail FROM audit WHERE proposal_id=? AND kind='proposal_planned'", (pid,)).fetchone()
    if planned:
        th = j(planned["detail"]).get("thresholds", {})
        keep = ("tail_prob", "min_relative_lift", "min_absolute_lift", "harm_relative_drop", "min_trials_arm", "confirm_prob", "holdout_share", "provisional_share")
        print("  THRESHOLDS:", ", ".join(f"{k}={th[k]}" for k in keep if k in th))
    ev = body.get("evidence") or {}
    for key, e in (ev.get("intents") or {}).items():
        print(f"  EVIDENCE {key}: {json.dumps(e, default=str)[:700]}")
    nxt = db.execute("SELECT * FROM audit WHERE wf=? AND minute>? AND kind IN ('followup','proposal_applied','supervisor_edit','incident_resolved','incident_opened') "
                     "ORDER BY minute LIMIT 4", (wf, chosen["minute"])).fetchall()
    print("  WHAT HAPPENED NEXT:")
    for a in nxt:
        print(f"    {fmt(db, a['minute'])}  {a['kind']:<18} {a['summary'][:150]}")


def proposal(db, pid: str):
    p = db.execute("SELECT * FROM proposals WHERE pid=?", (pid,)).fetchone()
    if not p:
        raise SystemExit("unknown proposal")
    print(json.dumps({k: p[k] for k in p.keys() if k not in ("proposed_config", "body")}, indent=1))
    print(json.dumps(j(p["body"]), indent=1, default=str)[:3000])
    for a in db.execute("SELECT * FROM audit WHERE proposal_id=? ORDER BY id", (pid,)):
        print(f"  {fmt(db, a['minute'])} {a['kind']} {a['summary']}")


def supervisor(db):
    now = int(json.loads(db.execute("SELECT v FROM kv WHERE k='now_minute'").fetchone()[0]))
    print(f"=== Supervisor view @ {fmt(db, now)} ===")
    for w in db.execute("SELECT wf, spec FROM workflows ORDER BY wf"):
        wf, spec = w["wf"], j(w["spec"])
        print(f"\n## {wf}  (primary {spec['objective']['primary']}, guardrail {spec['objective']['guardrail']})")
        for e in db.execute("SELECT * FROM experiments WHERE wf=?", (wf,)):
            ev_ = j(e["state"]).get("evidence")
            if ev_:
                print(f"   EVIDENCE {e['dim']:<16} {ev_['label']} (smallest arm has {ev_['min_trials_seen']} of {ev_['min_trials_needed']} trials needed)")
            for scope, s in j(e["state"])["scopes"].items():
                win = f" winner={s.get('winner')}" if s.get("winner") else ""
                print(f"   TESTING {e['dim']:<16} scope={scope:<16} phase={s['phase']}{win} control={s['control']}")
        coh = db.execute("SELECT cid FROM cohorts WHERE wf=? AND status='active'", (wf,)).fetchall()
        if coh:
            print("   cohorts:", ", ".join(c["cid"] for c in coh))
        pend = db.execute("SELECT pid,state,route,body FROM proposals WHERE wf=? AND state IN ('PLANNED','PENDING','APPROVED')", (wf,)).fetchall()
        for p in pend:
            b = j(p["body"])
            print(f"   WAITING ON YOU  [{p['state']}] impact={b['impact_score']} leads={b['affected_leads']}: {b['change_summary'][:120]}")
        day0 = (now // 1440) * 1440
        for a in db.execute("SELECT * FROM audit WHERE wf=? AND minute>=? AND kind IN ('proposal_applied','supervisor_edit','incident_opened','incident_resolved') ORDER BY id", (wf, day0)):
            print(f"   TODAY {fmt(db, a['minute'])[11:16]} {a['kind']}: {a['summary'][:120]}")
        for i in db.execute("SELECT id,state FROM incidents WHERE wf=? AND state NOT IN ('RESOLVED')", (wf,)):
            print(f"   INCIDENT {i['id']} state={i['state']}")


def pct(vals, q):
    vals = sorted(vals)
    return vals[min(int(len(vals) * q), len(vals) - 1)] if vals else None


def health(db):
    q = lambda sql, *a: db.execute(sql, a).fetchall()
    now = int(json.loads(db.execute("SELECT v FROM kv WHERE k='now_minute'").fetchone()[0]))
    print(f"=== Controller health @ {fmt(db, now)} ===")
    print(f"  {'metric':<26}{'last':>10}{'mean':>10}{'p50':>9}{'p95':>9}{'p99':>9}{'max':>10}  n")
    for name in ("t_ingest_seconds", "t_governance_seconds", "t_incident_seconds", "t_planning_seconds", "decision_lag_seconds", "step_seconds",
                 "stage_fetch_seconds", "stage_decode_seconds", "stage_transform_seconds", "stage_aggregate_seconds", "stage_db_seconds",
                 "ingest_events_per_sec", "ingest_backlog_chunks", "rss_mb", "db_mb", "credits_remaining", "open_proposals", "open_incidents",
                 "sim_http_errors", "sim_http_retries"):
        v = [r[0] for r in q("SELECT value FROM metrics WHERE name=? ORDER BY rowid", name)]
        if v:
            f = lambda x: f"{x:.3f}" if abs(x) < 100 else f"{x:.0f}"
            print(f"  {name:<26}{f(v[-1]):>10}{f(sum(v) / len(v)):>10}{f(pct(v, .5)):>9}{f(pct(v, .95)):>9}{f(pct(v, .99)):>9}{f(max(v)):>10}  {len(v)}")
    print("  proposals by state:", {r["state"]: r["n"] for r in q("SELECT state, COUNT(*) n FROM proposals GROUP BY state")})
    print("  credits spent:", q("SELECT COALESCE(SUM(amount),0) s FROM credits")[0]["s"])
    alerts = [a["summary"] for a in q("SELECT summary FROM audit WHERE kind IN ('incident_escalated','credit_skip','credit_spend_unrecorded') ORDER BY id DESC LIMIT 3")]
    alerts += [f"proposal {s['pid']} unsent >2h" for s in q("SELECT pid FROM proposals WHERE state='PLANNED' AND ? - created_minute > 120", now)]
    print("  PAGE-WORTHY NOW:", alerts or "none")


def log(db, wf: str | None, limit: int):
    sql, args = "SELECT * FROM audit" + (" WHERE wf=?" if wf else "") + " ORDER BY id DESC LIMIT ?", ([wf] if wf else []) + [limit]
    for a in reversed(db.execute(sql, args).fetchall()):
        print(f"{fmt(db, a['minute'])}  {a['wf'] or '-':<11} {a['kind']:<22} {a['summary'][:140]}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="controller_state.db")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("explain"); e.add_argument("--wf", required=True); e.add_argument("--at", required=True)
    pr = sub.add_parser("proposal"); pr.add_argument("pid")
    sub.add_parser("supervisor"); sub.add_parser("health")
    lg = sub.add_parser("log"); lg.add_argument("--wf"); lg.add_argument("--limit", type=int, default=40)
    a = ap.parse_args(argv)
    db = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    {"explain": lambda: explain(db, a.wf, parse_at(a.at)), "proposal": lambda: proposal(db, a.pid), "supervisor": lambda: supervisor(db),
     "health": lambda: health(db), "log": lambda: log(db, a.wf, a.limit)}[a.cmd]()


if __name__ == "__main__":
    main()
