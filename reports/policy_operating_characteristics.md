# Whole-policy operating characteristics (Monte Carlo, 300 runs per cell, 8 simulated days)

The real `plan_lever` policy (explore → provisional → confirm → promote → decay watch / reopen) run against synthetic arms. Volume = connected calls per day for the workflow. Times are *statistical* detection times: real approvals add hours. "Proposals" = approval requests per workflow per run.

## 1. Null and effect sizes (one better arm, static)

| true relative lift of the better arm | calls/day | provisional win | **confirmed (false if +0%)** | confirmed by day 3 | by day 8 | median days to confirm | confirmed arm later rolled back | proposals / workflow |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| +0% | 300 | 0% | 0% | 0% | 0% | - | - | 0.0 |
| +0% | 1000 | 3% | 1% | 1% | 1% | 3.0 | 0% | 1.1 |
| +0% | 4000 | 2% | 0% | 0% | 0% | 3.0 | 0% | 1.1 |
| +2% | 300 | 0% | 0% | 0% | 0% | - | - | 0.0 |
| +2% | 1000 | 7% | 2% | 0% | 2% | 5.0 | 0% | 1.1 |
| +2% | 4000 | 7% | 5% | 2% | 5% | 4.5 | 13% | 1.2 |
| +5% | 300 | 0% | 0% | 0% | 0% | - | - | 0.0 |
| +5% | 1000 | 19% | 11% | 0% | 11% | 5.0 | 0% | 1.4 |
| +5% | 4000 | 34% | 29% | 9% | 29% | 4.5 | 0% | 1.8 |
| +10% | 300 | 0% | 0% | 0% | 0% | - | - | 0.0 |
| +10% | 1000 | 68% | 54% | 3% | 54% | 5.0 | 1% | 2.3 |
| +10% | 4000 | 100% | 99% | 57% | 99% | 3.0 | 0% | 3.2 |
| +20% | 300 | 0% | 0% | 0% | 0% | - | - | 0.0 |
| +20% | 1000 | 100% | 100% | 26% | 100% | 3.5 | 0% | 3.0 |
| +20% | 4000 | 100% | 100% | 100% | 100% | 1.5 | 0% | 3.0 |

## 2. The promoted arm's world changes on day 4 (arm +10% before)

| what changes | calls/day | promoted before | **acts** after the change | median days to act | action | **new better arm found** | median days to find | false rollback before the change | proposals / workflow |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| V2 collapses to −15% | 1000 | 19% | 100% | 1.5 | rollback 72% / reopen 28% | n/a | - | 0% | 2.1 |
| V2 collapses to −15% | 4000 | 79% | 98% | 0.5 | rollback 64% / reopen 34% | n/a | - | 0% | 4.2 |
| V2 decays to the control rate | 1000 | 17% | 63% | 2.0 | rollback 13% / reopen 50% | n/a | - | 0% | 1.9 |
| V2 decays to the control rate | 4000 | 79% | 94% | 1.0 | rollback 20% / reopen 74% | n/a | - | 0% | 3.5 |
| V2 → neutral, V4 becomes +10% | 1000 | 17% | 87% | 2.0 | rollback 13% / reopen 73% | 0% | - | 0% | 2.0 |
| V2 → neutral, V4 becomes +10% | 4000 | 75% | 96% | 1.0 | rollback 14% / reopen 82% | 42% | 3.0 | 0% | 4.2 |
| V2 → −10%, V4 becomes +12% | 1000 | 15% | 100% | 1.5 | rollback 48% / reopen 52% | 5% | 4.0 | 0% | 2.1 |
| V2 → −10%, V4 becomes +12% | 4000 | 75% | 99% | 0.5 | rollback 47% / reopen 51% | 95% | 2.0 | 0% | 5.2 |

## 3. A harmful arm in the mix (V2 +10%, V3 −8%)

| calls/day | calls served by the harmful arm | harm-stopped by day 8 | median days to stop | confirmed V2 by day 8 |
|---:|---:|---:|---:|---:|
| 300 | 0.0% | 0% | - | 0% |
| 1000 | 11.4% | 36% | 3.5 | 51% |
| 4000 | 4.4% | 44% | 2.0 | 100% |
