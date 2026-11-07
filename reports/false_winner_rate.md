# Decision-rule operating characteristics (Monte Carlo, 1000 experiments per row)

tail_prob=0.05 (Bonferroni over challengers), min_relative_lift=0.03, min_trials_arm=250, confirm_prob=0.9. Stage 1 = up to 8 looks of 150 connected calls per arm; stage 2 = fresh data only.

| true situation | first-look promotion | confirmed promotion |
|---|---|---|
| all arms identical, 1 challenger | 3.5% | 0.5% |
| all arms identical, 3 challengers | 4.8% | 0.6% |
| one challenger +6% relative | 35.8% | 17.9% |
| one challenger +10% relative | 75.6% | 60.9% |
| one challenger +10% of 3 | 53.5% | 42.0% |
