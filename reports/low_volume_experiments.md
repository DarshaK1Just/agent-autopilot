# Low-volume learning: diagnosis and experiments (a documented negative result)

Goal of the experiment: improve the controller's power at ~1,000 connected calls/day (finding a new winner after a reopen, recognising a neutral winner) **without** raising harmful changes, false promotions, approval load, latency or complexity. Outcome: the cause is understood and measured, none of the candidate remedies met that bar, and **no behavioural change was kept**. The measurement tooling (`scripts/policy_compare.py`, `PS_DAYS` / `PS_CHANGE_BLK` in `scripts/policy_sim.py`) was kept.

## 1. Diagnosis (instrumented real planner, 200 runs, "old winner neutral, a new +10% arm appears on day 4")
| | 1,000 calls/day | 4,000 calls/day |
|---|---|---|
| runs in which exploration is reopened | 34 / 200 (17%) | 117 / 200 (59%) |
| the new arm reaches 250 trials in both arms | 5 / 34 | 104 / 117 (median 1.2 d after reopening) |
| the new arm passes the win bar | 1 / 34 | 62 / 117 (median 1.8 d) |
| share of the challenger samples that went to the arm that matters | 34% | 33% |
| trials per challenger by the end of the horizon | ~140 (below the 250 floor) | ~700 |

* **Where samples are wasted**: the 30% challenge is split equally over three challengers, so two thirds of the exploration samples go to arms that cannot win; each challenger ends the horizon below the 250-trial floor, and Bonferroni over three arms demands P ≥ 0.983 instead of 0.95 for one.
* **Monitoring starvation** (15% holdout): 45 / 150 / 600 control trials per day at 300 / 1,000 / 4,000 calls/day, i.e. 17.8 / 5.3 / 1.3 days to collect the ~800 needed to call a flat winner "not clearing the bar".
* **Not the cause**: the 250 floor, the evidence window length and the confirmation sample would all be met quickly if traffic were not fragmented; stale history is not mixed into decisions (stratified by version, windows trailing).
* **Arithmetic**: a +5-point (10% relative) lift needs ~2.4 days of one challenger at 60% share, but ~7 days with three challengers at 20% each (and 1.6 vs 10.5 days for a reopen at 30%). Concentrating traffic is where the speed is.

## 2. Candidates tried (policy simulation, 8-day horizon unless stated, 300–500 runs per cell)
| candidate | what it did | benefit | cost / why rejected |
|---|---|---|---|
| **Sequential, ranked probing + rotation + power-derived feasibility gate**, applied to the first exploration and to reopens | probe the challengers with the highest credible upside first, as many at once as the traffic can decide, rotate out measured duds | stable +10% winner at 1,000/day found in 65% of runs vs 52% (median 4.5 vs 5.5 d); new winner after a reopen 1% → 11%; harmful traffic 12.6% → 8.1% | **public_01: harmful changes 0 → 2, approval requests 7 → 17.** Without evidence the ranking is arbitrary: it probed 2 of 3 voices and left out the one good arm, and rotations put 60% of traffic on a single arm. Concentration raises the *variance of each change's expected effect*, and changes are judged one by one. Null: proposals per workflow 1.1 → 3.1. |
| Same, **reopen path only** (first exploration back to "test everyone at once") | ranked/sized probing only when reopening from a promoted incumbent | 14-day horizon: new winner 53% → 60%, harmful traffic 9.5% → 8.9% | 8-day horizon: **no change** (new winner 1% → 1% at 1,000/day, 76% → 77% at 4,000); ~70 lines of ranking/rotation logic for a marginal gain. Not material. |
| **Two-timescale rollback**: also roll back if the recent half-window is credibly worse | faster response to a collapse | harmful traffic after a collapse −1 point | false action on a *stable* winner 3% → 5% (8 d), 9% → 13% (14 d): an extra, noisier look. Rejected. |
| **Cheaper reopen trigger** (P(clears the bar) ≤ 0.35 instead of 0.2), on top of the probing variant | recognise a neutral winner on less data | neutral winner at 1,000/day recognised in 84% of runs vs 69%; new winner at 4,000/day 77% → 91% | false reopen of a *good* winner at 4,000/day 2% → 6% (8 d), 8% → 17% (14 d): costs 30% of traffic, approvals, and can be graded as a harmful change. Rejected. |
| Larger holdout at low volume | more monitoring data | 5.3 → ~4 days to classify a flat winner at 1,000/day | gives up 5–10% of the winner's traffic for a small speed-up. Not tried in simulation beyond the arithmetic. |

Final comparison for the last candidate that was close (reopen-only probing vs the accepted policy), 1,000 calls/day, 500 runs per cell:

**8-day horizon, regime change on day 4**

| regime (1,000 calls/day) | detect: baseline → reopen-only variant | median time | false action | harmful traffic | proposals/workflow |
|---|---|---|---|---|---|
| 1 stable +10% winner | 52% → 52% | 5.5d → 5.5d | 1% → 1% | 0.0% → 0.0% | 2.2 → 2.3 |
| 2 old winner becomes neutral | 68% → 68% | 2.0d → 2.0d | 0% → 0% | 0.0% → 0.0% | 1.9 → 2.0 |
| 3 new +15% winner appears | 1% → 1% | 4.0d → 4.0d | 0% → 0% | 12.6% → 12.5% | 2.5 → 2.5 |
| 4 old winner suddenly -15% | 100% → 100% | 1.5d → 1.5d | 0% → 0% | 23.5% → 21.8% | 2.0 → 2.0 |
| 5 all arms equal | n/a → n/a | - → - | - → - | 0.0% → 0.0% | 1.1 → 1.1 |

**14-day horizon, regime change on day 6**

| regime (1,000 calls/day) | detect: baseline → reopen-only variant | median time | false action | harmful traffic | proposals/workflow |
|---|---|---|---|---|---|
| 1 stable +10% winner | 81% → 81% | 7.0d → 7.0d | 1% → 1% | 0.0% → 0.0% | 2.9 → 3.1 |
| 2 old winner becomes neutral | 93% → 93% | 2.5d → 2.5d | 0% → 0% | 0.0% → 0.0% | 2.5 → 3.0 |
| 3 new +15% winner appears | 53% → 60% | 6.5d → 5.5d | 3% → 3% | 9.5% → 8.9% | 4.0 → 4.2 |
| 4 old winner suddenly -15% | 98% → 98% | 1.5d → 1.5d | 2% → 2% | 20.3% → 18.4% | 3.0 → 3.0 |
| 5 all arms equal | n/a → n/a | - → - | - → - | 0.0% → 0.0% | 1.1 → 1.1 |

("false action" = a rollback or reopen before the regime change, i.e. of a still-good winner; "harmful traffic" = share of calls served by arms worse than the control, taken over runs that had a promoted winner in the collapse and neutral regimes.)

## 3. Conclusion
* At ~1,000 calls/day the controller is **information-limited**: the traffic that would let it decide faster is the traffic it does not have. Every remedy that makes decisions faster either concentrates traffic (higher variance of each applied change, more approvals) or decides on weaker evidence (more false actions). Both break a stated invariant (0 harmful changes in the public regression runs; false-promotion and approval load at the current level).
* What the system does instead is stay honest about it: it declines to experiment where a verdict is impossible, labels thin evidence `INSUFFICIENT`, and keeps the incumbent.
* What would change this trade-off, and was deliberately not done: accept per-change variance and a higher approval rate in return for speed (a product decision), or add information from outside this workflow (priors from other workflows or tenants, explicitly out of scope for the assignment).
