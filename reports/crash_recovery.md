# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-05T07:00:00+05:30, event cursor=40, open proposals at kill=[('nw_kyc-v1-155e06fcd024', 'PENDING')]
- kill 2: sim 2027-01-06T23:15:00+05:30, event cursor=98, open proposals at kill=[('nw_renewal-v7-87e80e4fbcee', 'PENDING')]
- kill 3: sim 2027-01-09T04:45:00+05:30, event cursor=147, open proposals at kill=[('nw_kyc-v2-df5872b2ac0e', 'PENDING')]
- kill 4: sim 2027-01-11T10:45:00+05:30, event cursor=185, open proposals at kill=[]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 15, unique proposal ids: 15
- proposals by local state: {'APPLIED': 19, 'REJECTED': 1}
- audit rows: 109 (continuous across restarts)
- scenario finished: True
- **violations: none**
