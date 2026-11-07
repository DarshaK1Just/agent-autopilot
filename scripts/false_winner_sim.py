#!/usr/bin/env python3
"""Monte Carlo of the controller's own two-stage promotion rule (no simulator involved).

Stage 1 (explore): up to 8 looks of 150 connected calls per arm; the first arm that passes `_decide` becomes the provisional winner.
Stage 2 (confirm): fresh data only, up to 6 looks of 150 winner / 75 control calls; confirm if P(winner better than control) >= confirm_prob,
withdraw if P(winner better than control) <= 1 - confirm_prob. The result is the share of experiments that end with a *confirmed* promotion.
The threshold is a Bayesian credibility level, not a classical alpha: this table is the operating characteristic.

    .venv/bin/python scripts/false_winner_sim.py > reports/false_winner_rate.md
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from controller import stats  # noqa: E402
from controller.planner import WfCtx, _decide  # noqa: E402
from controller.policy import Policy  # noqa: E402
from controller.store import Store  # noqa: E402

SPEC = {"workflow_id": "w1", "objective": {"primary": "engagement_rate", "guardrail": {"pickup_rate_max_drop": 0.02}}}
POL = Policy()


def run(lift: float, challengers: int, trials: int = 1000, seed: int = 5):
    s = Store(":memory:")
    s.set_clock(100, "x")
    s.run("INSERT INTO agg VALUES('w1',-5,1,'default','voice','V1','all','',6000,2000,1000)")
    ctx = WfCtx(s, SPEC, {}, 1, 100, 10000, POL)
    rng = np.random.default_rng(seed)
    opts = ["V1"] + [f"V{i}" for i in range(2, 2 + challengers)]
    rate = lambda i: 0.55 * (1 + (lift if i == 1 else 0.0))
    first = confirmed = 0
    for _ in range(trials):
        ks, n, winner = {o: 0 for o in opts}, 0, None
        for _look in range(8):
            n += 150
            for i, o in enumerate(opts):
                ks[o] += rng.binomial(150, rate(i))
            counts = {(2, "default", o): (n * 3, n, ks[o]) for o in opts}
            _, win, _ = _decide(ctx, counts, opts, "V1", {})
            if win:
                winner = win[0][1]
                break
        if winner is None:
            continue
        first += 1
        i = opts.index(winner)
        kw = kc = nw = nc = 0
        for _look in range(6):
            kw, nw = kw + rng.binomial(150, rate(i)), nw + 150
            kc, nc = kc + rng.binomial(75, rate(0)), nc + 75
            c = stats.contrast((kw, nw), (kc, nc), 0.55)
            if min(nw, nc) < POL.min_trials_arm:
                continue
            if c.p_greater(0.0) >= POL.confirm_prob:
                confirmed += 1
                break
            if c.p_greater(0.0) <= 1 - POL.confirm_prob:
                break
    return first / trials, confirmed / trials


if __name__ == "__main__":
    print("# Decision-rule operating characteristics (Monte Carlo, 1000 experiments per row)\n")
    print(f"tail_prob={POL.tail_prob} (Bonferroni over challengers), min_relative_lift={POL.min_relative_lift}, min_trials_arm={POL.min_trials_arm}, "
          f"confirm_prob={POL.confirm_prob}. Stage 1 = up to 8 looks of 150 connected calls per arm; stage 2 = fresh data only.\n")
    print("| true situation | first-look promotion | confirmed promotion |\n|---|---|---|")
    for name, lift, k in [("all arms identical, 1 challenger", 0.0, 1), ("all arms identical, 3 challengers", 0.0, 3),
                          ("one challenger +6% relative", 0.06, 1), ("one challenger +10% relative", 0.10, 1),
                          ("one challenger +10% of 3", 0.10, 3)]:
        a, b = run(lift, k)
        print(f"| {name} | {a:.1%} | {b:.1%} |")
