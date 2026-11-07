#!/usr/bin/env python3
"""Kill the controller with SIGKILL at several random moments of a public_02 run, restart it each time, and verify
the run still finishes with no duplicate side effects. Writes reports/crash_recovery.md.

    .venv/bin/python scripts/crash_demo.py [--kills 4] [--seed 7]
"""
import argparse
import json
import os
import random
import signal
import sqlite3
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
PORT = 8710


def sim_state():
    return httpx.get(f"http://127.0.0.1:{PORT}/sim/state", timeout=30).json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kills", type=int, default=4)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--scenario", default="02_incidents")
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    db = ROOT / "runs" / "ctl_crash.db"
    for suffix in ("", "-wal", "-shm"):
        Path(str(db) + suffix).unlink(missing_ok=True)
    sim = subprocess.Popen([str(ROOT / "scripts/serve.sh"), a.scenario, str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           start_new_session=True)
    for _ in range(120):
        try:
            httpx.get(f"http://127.0.0.1:{PORT}/health", timeout=2)
            break
        except Exception:
            time.sleep(1)
    env = {**os.environ, "CONTROLLER_DB": str(db)}
    log = ["# Crash-recovery run", "", f"scenario `{a.scenario}`, SIGKILL x{a.kills}, seed {a.seed}", ""]
    runs = 0
    kills_done = 0
    while True:
        p = subprocess.Popen([str(ROOT / "run.sh"), f"http://127.0.0.1:{PORT}"], env=env, cwd=ROOT)
        runs += 1
        if kills_done < a.kills:
            time.sleep(rnd.uniform(3.0, 7.0))
            if p.poll() is None:
                st = sim_state()
                c = sqlite3.connect(db)
                open_ = c.execute("SELECT pid,state FROM proposals WHERE state IN ('PLANNED','PENDING','APPROVED')").fetchall()
                cur = c.execute("SELECT v FROM kv WHERE k='cur_events'").fetchone()
                c.close()
                p.send_signal(signal.SIGKILL)
                p.wait()
                kills_done += 1
                log.append(f"- kill {kills_done}: sim {st['ts']}, event cursor={cur and cur[0]}, open proposals at kill={open_}")
                print(log[-1], flush=True)
                continue
        rc = p.wait()
        log.append(f"- final run exit code {rc}")
        break
    st = sim_state()
    base = f"http://127.0.0.1:{PORT}"
    appr = httpx.get(f"{base}/approvals").json()
    pids = Counter(x["proposal_id"] for x in appr)
    problems = []
    if not st["finished"]:
        problems.append("scenario did not finish")
    problems += [f"proposal {k} submitted {v}x" for k, v in pids.items() if v > 1]
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    wfs = [r[0] for r in c.execute("SELECT wf FROM workflows")]
    applied_by_sim = Counter()
    for wf in wfs:
        for h in httpx.get(f"{base}/workflows/{wf}/config/history").json():
            for k in ("approval_id", "proposal_id"):
                if h[k]:
                    applied_by_sim[(wf, k, h[k])] += 1
    problems += [f"{k} applied {v}x" for k, v in applied_by_sim.items() if v > 1]
    mine = {r["pid"]: r for r in c.execute("SELECT * FROM proposals")}
    for pid, r in mine.items():
        if r["state"] == "APPLIED" and (r["wf"], "proposal_id", pid) not in applied_by_sim:
            problems.append(f"{pid} recorded APPLIED but simulator has no such version")
    for x in appr:
        if x["status"] == "applied" and mine.get(x["proposal_id"], {"state": None})["state"] != "APPLIED":
            problems.append(f"{x['proposal_id']} applied in simulator but not recorded locally")
    starts = c.execute("SELECT summary FROM audit WHERE kind='controller_start' ORDER BY id").fetchall()
    n_audit = c.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
    log += ["", f"- controller starts recorded in audit: {len(starts)} ({sum('RESTARTED' in s[0] for s in starts)} restarts)",
            f"- approvals in simulator: {len(appr)}, unique proposal ids: {len(pids)}",
            f"- proposals by local state: {dict(Counter(r['state'] for r in mine.values()))}",
            f"- audit rows: {n_audit} (continuous across restarts)", f"- scenario finished: {st['finished']}",
            f"- **violations: {problems or 'none'}**"]
    Path(ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "crash_recovery.md").write_text("\n".join(log) + "\n")
    print("\n".join(log))
    os.killpg(sim.pid, signal.SIGTERM)
    subprocess.run(["fuser", "-k", f"{PORT}/tcp"], capture_output=True)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
