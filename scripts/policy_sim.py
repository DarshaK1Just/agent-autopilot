#!/usr/bin/env python3
"""Whole-policy Monte Carlo: the real planner (plan_lever) driven through simulated days. Not the simulator, not public data.

Each 6-hour block, connected calls are split by the allocation the controller currently has; engaged calls are binomial draws from
the arms' true rates. Every 12 hours the planner runs and its intents are applied instantly (zero approval latency, so these are
detection times of the *statistics*; real approvals add hours). 4 voice options, control 50% engagement, 8 days, N runs per cell.

    .venv/bin/python scripts/policy_sim.py --trials 300 > reports/policy_operating_characteristics.md
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
BASE, DAYS, CHANGE_BLK = 0.5, 8, 16   # the regime changes at block 16 (day 4) in the shift scenarios

# true relative lift of each arm over the control (V1) before / after the change
SCENARIOS = {
    "effect": None,                                          # {V2: x} at all times, x given per row
    "regress": ({"V2": .10}, {"V2": -.15}),                  # promoted arm collapses
    "neutral": ({"V2": .10}, {"V2": 0.0}),                   # promoted arm decays to the control rate
    "new_winner": ({"V2": .10}, {"V2": 0.0, "V4": .10}),     # the old winner goes neutral and a different arm becomes good
    "switch": ({"V2": .10}, {"V2": -.10, "V4": .12}),        # the winner turns bad while another arm becomes good
    "harmful_arm": ({"V2": .10, "V3": -.08}, {"V2": .10, "V3": -.08}),
}


def run(lifts_before: dict, lifts_after: dict | None, conn_per_day: int, seed: int):
    rng = np.random.default_rng(seed)
    s = Store(":memory:")
    cfg, version = copy.deepcopy(CFG), 1
    per_blk = conn_per_day // 4
    for b in range(-4, 0):
        s.run("INSERT INTO agg VALUES('w1',?,1,'default','voice','V1','all','',?,?,?)", (b, per_blk * 3, per_blk, per_blk // 2))
    lift = lambda opt, blk: (lifts_before if lifts_after is None or blk < CHANGE_BLK else lifts_after).get(opt, 0.0)
    ev = {"proposals": 0, "confirmed": None, "provisional": None, "rollback": None, "reopen": None, "new_winner": None,
          "early_rollbacks": 0, "worse_calls": 0, "total_calls": 0, "harm_stopped": None}
    for blk in range(DAYS * 4):
        dist = cfgutil.dist(cfg, "default", "voice")
        for opt, share in dist.items():
            n = int(rng.binomial(per_blk, share))
            rate = BASE * (1 + lift(opt, blk))
            s.run("INSERT INTO agg VALUES('w1',?,?,'default','voice',?,'all','',?,?,?)", (blk, version, opt, n * 3, n, int(rng.binomial(n, rate))))
            ev["total_calls"] += n
            if lift(opt, blk) < 0:
                ev["worse_calls"] += n
        if blk % 2 == 1:
            s.set_clock((blk + 1) * 360, "x")
            ctx = WfCtx(s, SPEC, cfg, version, (blk + 1) * 360, DAYS * 1440, POL)
            intents = [i for i in plan_lever(ctx, "voice", False) if i.patch or i.exp_update]
            if not intents:
                continue
            version += 1
            ev["proposals"] += 1 if any(i.patch for i in intents) else 0
            for i in intents:
                cfg = cfgutil.apply_patch(cfg, i.patch)
                if i.exp_update:
                    apply_exp_update(s, "w1", i.exp_update, version)
                post = blk >= CHANGE_BLK
                if i.kind == "promote" and ev["provisional"] is None:
                    ev["provisional"] = blk
                if i.kind == "confirm":
                    w = load_exp(WfCtx(s, SPEC, cfg, version, 0, 1, POL), "voice")["scopes"]["default"]["winner"]
                    if ev["confirmed"] is None:
                        ev["confirmed"] = blk
                    if post and w == "V4" and ev["new_winner"] is None:
                        ev["new_winner"] = blk
                if i.kind == "rollback":
                    if post and ev["rollback"] is None:
                        ev["rollback"] = blk
                    elif not post:
                        ev["early_rollbacks"] += 1
                if i.kind == "reexplore" and post and ev["reopen"] is None:
                    ev["reopen"] = blk
                if i.kind == "harm_stop" and ev["harm_stopped"] is None:
                    ev["harm_stopped"] = blk
    return ev


def cells(lb, la, vol, trials, tag):
    return [run(lb, la, vol, 7919 * k + vol + hash(tag) % 1000) for k in range(trials)]


def pct(x, n):
    return f"{100 * x / max(n, 1):.0f}%"


def days(blks):
    return f"{statistics.median([(b + 1 - (CHANGE_BLK if b >= CHANGE_BLK else 0)) / 4 for b in blks]):.1f}" if blks else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=100)
    t = ap.parse_args().trials
    print(f"# Whole-policy operating characteristics (Monte Carlo, {t} runs per cell, {DAYS} simulated days)\n")
    print("The real `plan_lever` policy (explore → provisional → confirm → promote → decay watch / reopen) run against synthetic arms. "
          "Volume = connected calls per day for the workflow. Times are *statistical* detection times: real approvals add hours. "
          "\"Proposals\" = approval requests per workflow per run.\n")
    print("## 1. Null and effect sizes (one better arm, static)\n")
    print("| true relative lift of the better arm | calls/day | provisional win | **confirmed (false if +0%)** | confirmed by day 3 | by day 8 | median days to confirm | confirmed arm later rolled back | proposals / workflow |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for eff in (0.0, 0.02, 0.05, 0.10, 0.20):
        for vol in (300, 1000, 4000):
            rs = cells({"V2": eff}, None, vol, t, f"e{eff}")
            conf = [r["confirmed"] for r in rs if r["confirmed"] is not None]
            by3 = sum(1 for c in conf if (c + 1) / 4 <= 3)
            fr = sum(1 for r in rs if r["confirmed"] is not None and (r["early_rollbacks"] + (1 if r["rollback"] is not None else 0)) > 0)
            print(f"| {eff:+.0%} | {vol} | {pct(sum(r['provisional'] is not None for r in rs), t)} | {pct(len(conf), t)} | {pct(by3, t)} | {pct(len(conf), t)} | "
                  f"{statistics.median([(c + 1) / 4 for c in conf]):.1f} | {pct(fr, max(len(conf), 1))} | {statistics.mean(r['proposals'] for r in rs):.1f} |"
                  if conf else f"| {eff:+.0%} | {vol} | {pct(sum(r['provisional'] is not None for r in rs), t)} | 0% | 0% | 0% | - | - | {statistics.mean(r['proposals'] for r in rs):.1f} |")
    print("\n## 2. The promoted arm's world changes on day 4 (arm +10% before)\n")
    print("| what changes | calls/day | promoted before | **acts** after the change | median days to act | action | **new better arm found** | median days to find | false rollback before the change | proposals / workflow |")
    print("|---|---:|---:|---:|---:|---|---:|---:|---:|---:|")
    labels = {"regress": "V2 collapses to −15%", "neutral": "V2 decays to the control rate", "new_winner": "V2 → neutral, V4 becomes +10%", "switch": "V2 → −10%, V4 becomes +12%"}
    for key, label in labels.items():
        for vol in (1000, 4000):
            rs = cells(*SCENARIOS[key], vol, t, key)
            prom = [r for r in rs if r["confirmed"] is not None and r["confirmed"] < CHANGE_BLK]
            acted = [min(x for x in (r["rollback"], r["reopen"]) if x is not None) for r in prom if r["rollback"] is not None or r["reopen"] is not None]
            roll = sum(1 for r in prom if r["rollback"] is not None and (r["reopen"] is None or r["rollback"] <= r["reopen"]))
            reop = sum(1 for r in prom if r["reopen"] is not None and (r["rollback"] is None or r["reopen"] < r["rollback"]))
            nw = [r["new_winner"] for r in prom if r["new_winner"] is not None]
            action = f"rollback {pct(roll, len(prom))} / reopen {pct(reop, len(prom))}" if prom else "-"
            print(f"| {label} | {vol} | {pct(len(prom), t)} | {pct(len(acted), len(prom))} | {days(acted)} | {action} | "
                  f"{pct(len(nw), len(prom)) if key in ('new_winner', 'switch') else 'n/a'} | {days(nw) if key in ('new_winner', 'switch') else '-'} | "
                  f"{pct(sum(1 for r in prom if r['early_rollbacks'] > 0), len(prom))} | {statistics.mean(r['proposals'] for r in rs):.1f} |")
    print("\n## 3. A harmful arm in the mix (V2 +10%, V3 −8%)\n")
    print("| calls/day | calls served by the harmful arm | harm-stopped by day 8 | median days to stop | confirmed V2 by day 8 |")
    print("|---:|---:|---:|---:|---:|")
    for vol in (300, 1000, 4000):
        rs = cells(*SCENARIOS["harmful_arm"], vol, t, "harm")
        stop = [r["harm_stopped"] for r in rs if r["harm_stopped"] is not None]
        print(f"| {vol} | {100 * sum(r['worse_calls'] for r in rs) / max(sum(r['total_calls'] for r in rs), 1):.1f}% | {pct(len(stop), t)} | "
              f"{statistics.median([(b + 1) / 4 for b in stop]):.1f} | {pct(sum(r['confirmed'] is not None for r in rs), t)} |" if stop else
              f"| {vol} | {100 * sum(r['worse_calls'] for r in rs) / max(sum(r['total_calls'] for r in rs), 1):.1f}% | 0% | - | {pct(sum(r['confirmed'] is not None for r in rs), t)} |")


if __name__ == "__main__":
    main()
