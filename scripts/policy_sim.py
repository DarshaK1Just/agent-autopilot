#!/usr/bin/env python3
"""Whole-policy Monte Carlo: the real planner (plan_lever) driven through simulated days. Not the simulator, not public data.

Each 6-hour block, connected calls are split by the allocation the controller has set; engaged calls are binomial draws from the
arms' true rates. Every 12 hours the planner is run and its intents are applied instantly (zero approval latency, so these are
detection times of the *statistics*; real approvals add hours). Reported per cell over N independent runs of 8 days.

    .venv/bin/python scripts/policy_sim.py --trials 100 > reports/policy_operating_characteristics.md
"""
import argparse
import copy
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from controller import cfgutil  # noqa: E402
from controller.planner import WfCtx, apply_exp_update, load_exp, plan_lever  # noqa: E402
from controller.policy import Policy  # noqa: E402
from controller.store import Store  # noqa: E402

POL = Policy()
SPEC = {"workflow_id": "w1", "options": {"voice": ["V1", "V2", "V3", "V4"], "welcome_message": ["W1"], "caller_id": ["D1"], "prompt_version": ["P1"]},
        "objective": {"primary": "engagement_rate", "guardrail": {"pickup_rate_max_drop": 0.02}}}
CFG = {"cohorts": [], "allocations": {"default": {"welcome_message": {"W1": 1.0}, "voice": {"V1": 1.0}, "caller_id": {"D1": 1.0}}},
       "prompt_version": "P1", "schedule": {"hour_weights": {}, "lead_preferred_hour": {}}}
BASE, DAYS, CHANGE_BLK = 0.5, 8, 16


def run(effect: float, conn_per_day: int, seed: int, shift: str | None = None):
    rng = np.random.default_rng(seed)
    s = Store(":memory:")
    cfg, version = copy.deepcopy(CFG), 1
    per_blk = conn_per_day // 4
    for b in range(-4, 0):
        s.run("INSERT INTO agg VALUES('w1',?,1,'default','voice','V1','all','',?,?,?)", (b, per_blk * 3, per_blk, per_blk // 2))
    rate = lambda opt, blk: BASE * (1 + effect) if opt == "V2" and (shift is None or blk < CHANGE_BLK) else (
        BASE * 0.85 if opt == "V2" and shift == "regress" else BASE)   # 'regress': V2 collapses; 'decay': V2 falls back to the control rate
    ev = {"proposals": 0, "provisional": None, "confirmed": None, "rollback": None, "unconfirmed": 0, "rollbacks": 0}
    for blk in range(DAYS * 4):
        dist = cfgutil.dist(cfg, "default", "voice")
        for opt, share in dist.items():
            n = int(rng.binomial(per_blk, share))
            e = int(rng.binomial(n, rate(opt, blk)))
            s.run("INSERT INTO agg VALUES('w1',?,?,'default','voice',?,'all','',?,?,?)", (blk, version, opt, n * 3, n, e))
        if blk % 2 == 1:
            s.set_clock((blk + 1) * 360, "x")
            ctx = WfCtx(s, SPEC, cfg, version, (blk + 1) * 360, DAYS * 1440, POL)
            intents = [i for i in plan_lever(ctx, "voice", False) if i.patch or i.exp_update]
            if not intents:
                continue
            version += 1
            for i in intents:
                cfg = cfgutil.apply_patch(cfg, i.patch)
                if i.exp_update:
                    apply_exp_update(s, "w1", i.exp_update, version)
                if i.patch:
                    ev["proposals"] += 1 if i is intents[0] else 0
                if i.kind.startswith("promote") and ev["provisional"] is None:
                    ev["provisional"] = blk
                if i.kind == "confirm" and ev["confirmed"] is None:
                    ev["confirmed"] = blk
                if i.kind == "unconfirmed":
                    ev["unconfirmed"] += 1
                if i.kind == "rollback":
                    ev["rollbacks"] += 1
                    if ev["rollback"] is None and blk >= CHANGE_BLK:
                        ev["rollback"] = blk
    ds = load_exp(WfCtx(s, SPEC, cfg, version, 0, 1, POL), "voice")["scopes"].get("default", {})
    ev["final_winner"] = ds.get("winner") if ds.get("phase") == "PROMOTED" else None
    return ev


def cell(effect, vol, trials, shift=None):
    rs = [run(effect, vol, 1000 * k + int(effect * 100) + vol, shift) for k in range(trials)]
    return rs


def pct(x, n):
    return f"{100 * x / n:.0f}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=100)
    t = ap.parse_args().trials
    print(f"# Whole-policy operating characteristics (Monte Carlo, {t} runs per cell, {DAYS} simulated days)\n")
    print("The real `plan_lever` policy (explore → provisional → confirm → promote → decay watch) run against synthetic arms; 4 voice options,"
          " control 50% engagement, one challenger with the stated relative lift, planner run every 12 h, approvals instantaneous. "
          "Volume = connected calls per day for the workflow. Times are *statistical* detection times: real approvals add hours.\n")
    print("## Null and effect sizes\n")
    print("| true relative lift of the one better arm | connected calls/day | provisional win | confirmed final promotion | confirmed by day 1 | by day 3 | by day 8 | median days to confirm | confirmed arm later rolled back (false rollback) | proposals per run (mean) |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for eff in (0.0, 0.02, 0.05, 0.10, 0.20):
        for vol in (300, 1000, 4000):
            rs = cell(eff, vol, t)
            conf = [r["confirmed"] for r in rs if r["confirmed"] is not None]
            by = lambda d: sum(1 for c in conf if (c + 1) / 4 <= d)
            med = f"{statistics.median([(c + 1) / 4 for c in conf]):.1f}" if conf else "-"
            print(f"| {eff:+.0%} | {vol} | {pct(sum(r['provisional'] is not None for r in rs), t)} | {pct(len(conf), t)} | {pct(by(1), t)} | {pct(by(3), t)} | "
                  f"{pct(by(8), t)} | {med} | "
                  f"{pct(sum(1 for r in rs if r['confirmed'] is not None and r['rollbacks'] > 0), max(len(conf), 1))} | {statistics.mean(r['proposals'] for r in rs):.1f} |")
    print("\n`+0%` rows are the null (all arms equal): *confirmed final promotion* is the false-promotion rate of the whole policy; "
          "*proposals per run* is the approval load under the null (1 = just the initial exploration request).\n")
    print("## A promoted arm that regresses or decays on day 4 (true lift +10% before, then −15% or 0%)\n")
    print("| change | connected calls/day | promoted before the change | rolled back after the change | rolled back *before* the change (false) | median days from change to rollback |")
    print("|---|---:|---:|---:|---:|---:|")
    for shift, label in (("regress", "regresses to −15%"), ("decay", "decays to 0%")):
        for vol in (300, 1000, 4000):
            rs = cell(0.10, vol, t, shift)
            promoted = [r for r in rs if r["confirmed"] is not None and r["confirmed"] < CHANGE_BLK]
            rb = [r["rollback"] for r in promoted if r["rollback"] is not None]
            early = [r for r in promoted if r["rollback"] is None and r["rollbacks"] > 0]
            med = f"{statistics.median([(b + 1 - CHANGE_BLK) / 4 for b in rb]):.1f}" if rb else "-"
            print(f"| {label} | {vol} | {pct(len(promoted), t)} | {pct(len(rb), max(len(promoted), 1))} | {pct(len(early), max(len(promoted), 1))} | {med} |")


if __name__ == "__main__":
    main()
