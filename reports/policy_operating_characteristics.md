# Whole-policy operating characteristics (Monte Carlo, 300 runs per cell, 8 simulated days)

The real `plan_lever` policy (explore → provisional → confirm → promote → decay watch) run against synthetic arms; 4 voice options, control 50% engagement, one challenger with the stated relative lift, planner run every 12 h, approvals instantaneous. Volume = connected calls per day for the workflow. Times are *statistical* detection times: real approvals add hours.

## Null and effect sizes

| true relative lift of the one better arm | connected calls/day | provisional win | confirmed final promotion | confirmed by day 1 | by day 3 | by day 8 | median days to confirm | confirmed arm later rolled back (false rollback) | proposals per run (mean) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| +0% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +0% | 1000 | 4% | 1% | 0% | 0% | 1% | 4.2 | 50% | 1.1 |
| +0% | 4000 | 2% | 1% | 0% | 0% | 1% | 3.8 | 50% | 1.1 |
| +2% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +2% | 1000 | 4% | 2% | 0% | 0% | 2% | 4.8 | 17% | 1.1 |
| +2% | 4000 | 5% | 2% | 0% | 0% | 2% | 5.5 | 20% | 1.1 |
| +5% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +5% | 1000 | 17% | 9% | 0% | 0% | 9% | 5.5 | 4% | 1.3 |
| +5% | 4000 | 35% | 29% | 0% | 9% | 29% | 4.0 | 11% | 1.7 |
| +10% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +10% | 1000 | 65% | 51% | 0% | 5% | 51% | 5.5 | 1% | 2.2 |
| +10% | 4000 | 99% | 97% | 0% | 51% | 97% | 3.0 | 0% | 3.0 |
| +20% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +20% | 1000 | 100% | 100% | 0% | 28% | 100% | 3.5 | 0% | 3.0 |
| +20% | 4000 | 100% | 100% | 0% | 100% | 100% | 1.5 | 0% | 3.0 |

`+0%` rows are the null (all arms equal): *confirmed final promotion* is the false-promotion rate of the whole policy; *proposals per run* is the approval load under the null (1 = just the initial exploration request).

## A promoted arm that regresses or decays on day 4 (true lift +10% before, then −15% or 0%)

| change | connected calls/day | promoted before the change | rolled back after the change | rolled back *before* the change (false) | median days from change to rollback |
|---|---:|---:|---:|---:|---:|
| regresses to −15% | 300 | 0% | 0% | 0% | - |
| regresses to −15% | 1000 | 14% | 98% | 0% | 2.0 |
| regresses to −15% | 4000 | 72% | 100% | 0% | 1.0 |
| decays to 0% | 300 | 0% | 0% | 0% | - |
| decays to 0% | 1000 | 14% | 31% | 0% | 2.5 |
| decays to 0% | 4000 | 72% | 47% | 0% | 2.5 |
