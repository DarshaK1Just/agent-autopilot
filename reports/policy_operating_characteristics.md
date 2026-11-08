# Whole-policy operating characteristics (Monte Carlo, 300 runs per cell, 8 simulated days)

The real `plan_lever` policy (explore → provisional → confirm → promote → decay watch) run against synthetic arms; 4 voice options, control 50% engagement, one challenger with the stated relative lift, planner run every 12 h, approvals instantaneous. Volume = connected calls per day for the workflow. Times are *statistical* detection times: real approvals add hours.

## Null and effect sizes

| true relative lift of the one better arm | connected calls/day | provisional win | confirmed final promotion | confirmed by day 1 | by day 3 | by day 8 | median days to confirm | confirmed arm later rolled back (false rollback) | proposals per run (mean) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| +0% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +0% | 1000 | 4% | 1% | 0% | 0% | 1% | 4.2 | 100% | 1.3 |
| +0% | 4000 | 3% | 1% | 0% | 0% | 1% | 4.5 | 100% | 1.2 |
| +2% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +2% | 1000 | 4% | 2% | 0% | 0% | 2% | 4.8 | 50% | 1.2 |
| +2% | 4000 | 5% | 2% | 0% | 0% | 2% | 5.5 | 80% | 1.2 |
| +5% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +5% | 1000 | 17% | 9% | 0% | 0% | 9% | 5.5 | 22% | 1.4 |
| +5% | 4000 | 35% | 30% | 0% | 9% | 30% | 4.0 | 40% | 1.9 |
| +10% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +10% | 1000 | 66% | 53% | 0% | 5% | 53% | 5.5 | 4% | 2.4 |
| +10% | 4000 | 99% | 97% | 0% | 52% | 97% | 3.0 | 10% | 3.2 |
| +20% | 300 | 0% | 0% | 0% | 0% | 0% | - | 0% | 0.0 |
| +20% | 1000 | 100% | 100% | 0% | 28% | 100% | 3.5 | 0% | 3.1 |
| +20% | 4000 | 100% | 100% | 0% | 100% | 100% | 1.5 | 0% | 3.0 |

`+0%` rows are the null (all arms equal): *confirmed final promotion* is the false-promotion rate of the whole policy; *proposals per run* is the approval load under the null (1 = just the initial exploration request).

## A promoted arm that regresses or decays on day 4 (true lift +10% before, then −15% or 0%)

| change | connected calls/day | promoted before the change | rolled back after the change | rolled back *before* the change (false) | median days from change to rollback |
|---|---:|---:|---:|---:|---:|
| regresses to −15% | 300 | 0% | 0% | 0% | - |
| regresses to −15% | 1000 | 14% | 100% | 0% | 1.5 |
| regresses to −15% | 4000 | 74% | 97% | 3% | 0.5 |
| decays to 0% | 300 | 0% | 0% | 0% | - |
| decays to 0% | 1000 | 14% | 86% | 0% | 2.5 |
| decays to 0% | 4000 | 74% | 91% | 3% | 1.5 |
