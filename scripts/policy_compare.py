#!/usr/bin/env python3
"""Compact old-vs-new comparison of the whole policy on five regimes at three volumes (see policy_sim.py for the method).

    .venv/bin/python scripts/policy_compare.py --trials 300 > out.md
Run it from two checkouts to compare two versions of the controller.
"""
import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import policy_sim as ps  # noqa: E402

HARM = {"V3": -.08}   # one genuinely harmful challenger is present in the regimes where exposure matters
SC = {
    "1 stable +10% winner":            ({"V2": .10}, None),
    "2 old winner becomes neutral":    ({"V2": .10}, {"V2": 0.0}),
    "3 new +15% winner appears":       ({"V2": .10, **HARM}, {"V2": 0.0, "V4": .15, **HARM}),
    "4 old winner suddenly -15%":      ({"V2": .10}, {"V2": -.15}),
    "5 all arms equal":                ({}, None),
}


def med(xs):
    return f"{statistics.median(xs):.1f}d" if xs else "-"


def main():
    t = argparse.ArgumentParser(); t.add_argument("--trials", type=int, default=300); t = t.parse_args().trials
    print("| regime | calls/day | detect | median time | false promotion | false rollback/reopen | harmful traffic | proposals/workflow |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, (lb, la) in SC.items():
        for vol in (300, 1000, 4000):
            rs = [ps.run(lb, la, vol, 7919 * k + vol + len(name)) for k in range(t)]
            prom = [r for r in rs if r["confirmed"] is not None and (la is None or r["confirmed"] < ps.CHANGE_BLK)]
            if name.startswith("1"):
                det = [r["confirmed"] for r in rs if r["confirmed"] is not None]; times = [(b + 1) / 4 for b in det]; p_det = len(det) / t
                fp = "-"; fr = sum(1 for r in prom if r["early_rollbacks"] + (1 if r["rollback"] is not None else 0) + r["early_reopens"] > 0) / max(len(prom), 1)
            elif name.startswith("5"):
                p_det, times, fp, fr = 0, [], f"{100 * sum(r['confirmed'] is not None for r in rs) / t:.1f}%", 0
            elif name.startswith("3"):
                det = [r["new_winner"] for r in prom if r["new_winner"] is not None]
                times = [(b + 1 - ps.CHANGE_BLK) / 4 for b in det]; p_det = len(det) / max(len(prom), 1)
                fp = "-"; fr = sum(1 for r in prom if r["early_rollbacks"] + r["early_reopens"] > 0) / max(len(prom), 1)
            else:
                act = [min(x for x in (r["rollback"], r["reopen"]) if x is not None) for r in prom if r["rollback"] is not None or r["reopen"] is not None]
                times = [(b + 1 - ps.CHANGE_BLK) / 4 for b in act]; p_det = len(act) / max(len(prom), 1)
                fp = "-"; fr = sum(1 for r in prom if r["early_rollbacks"] + r["early_reopens"] > 0) / max(len(prom), 1)
            # harmful exposure = calls on worse-than-control arms; in regimes 2 and 4 it is taken over runs that HAD a promoted winner
            # (otherwise a policy that finds fewer winners looks safer than it is)
            pool = prom if name[0] in "24" else rs
            expo = 100 * sum(r["worse_calls"] for r in pool) / max(sum(r["total_calls"] for r in pool), 1)
            lab = "n/a" if name.startswith("5") else f"{100 * p_det:.0f}%"
            fr_s = "-" if name.startswith("5") else f"{100 * fr:.0f}%"
            print(f"| {name} | {vol} | {lab} | {med(times)} | {fp} | {fr_s} | {expo:.1f}% | {statistics.mean(r['proposals'] for r in rs):.1f} |")


if __name__ == "__main__":
    main()
