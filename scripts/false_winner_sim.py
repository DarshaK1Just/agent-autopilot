#!/usr/bin/env python3
"""Monte Carlo of the controller's own decision rule (no simulator involved): how often is a neutral arm promoted, and
how often is a real lift found, when evidence is checked at 8 sequential looks of 150 connected calls per arm.
    .venv/bin/python scripts/false_winner_sim.py > reports/false_winner_rate.md
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from controller.planner import WfCtx, _decide  # noqa: E402
from controller.policy import Policy  # noqa: E402
from controller.store import Store  # noqa: E402

SPEC = {"workflow_id": "w1", "objective": {"primary": "engagement_rate", "guardrail": {"pickup_rate_max_drop": 0.02}}}


def run(lift: float, challengers: int, trials: int = 600, looks: int = 8, seed: int = 5):
    s = Store(":memory:")
    s.set_clock(100, "x")
    s.run("INSERT INTO agg VALUES('w1',-5,1,'default','voice','V1','all','',6000,2000,1000)")
    ctx = WfCtx(s, SPEC, {}, 1, 100, 10000, Policy())
    rng = np.random.default_rng(seed)
    opts = ["V1"] + [f"V{i}" for i in range(2, 2 + challengers)]
    hits, at = 0, []
    for _ in range(trials):
        ks, n = {o: 0 for o in opts}, 0
        for look in range(looks):
            n += 150
            for i, o in enumerate(opts):
                ks[o] += rng.binomial(150, 0.55 * (1 + (lift if i == 1 else 0.0)))
            counts = {(2, "default", o): (n * 3, n, ks[o]) for o in opts}
            _, win, _ = _decide(ctx, counts, opts, "V1", {})
            if win:
                hits += 1
                at.append(look + 1)
                break
    return hits / trials, (float(np.mean(at)) * 150 if at else None)


if __name__ == "__main__":
    print("# Decision-rule operating characteristics\n")
    print(f"family_alpha={Policy().family_alpha}, rel_min_lift={Policy().rel_min_lift}, min_trials_arm={Policy().min_trials_arm}; "
          "8 looks x 150 connected calls per arm, 600 simulated experiments per row.\n")
    print("| scenario | P(promote some arm) | mean connected calls per arm at promotion |\n|---|---|---|")
    for name, lift, k in [("all arms identical, 1 challenger", 0.0, 1), ("all arms identical, 3 challengers", 0.0, 3),
                          ("one challenger +6% relative", 0.06, 1), ("one challenger +10% relative", 0.10, 1),
                          ("one challenger +10% of 3", 0.10, 3)]:
        p, n = run(lift, k)
        print(f"| {name} | {p:.1%} | {'-' if n is None else int(n)} |")
