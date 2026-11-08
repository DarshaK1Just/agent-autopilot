# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-05T04:00:00+05:30, event cursor=40, open proposals at kill=[('nw_kyc-v1-155e06fcd024', 'PENDING')]
- kill 2: sim 2027-01-06T20:15:00+05:30, event cursor=95, open proposals at kill=[('nw_renewal-v7-87e80e4fbcee', 'PENDING')]
- kill 3: sim 2027-01-07T21:15:00+05:30, event cursor=121, open proposals at kill=[]
- kill 4: sim 2027-01-09T10:15:00+05:30, event cursor=161, open proposals at kill=[]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 16, unique proposal ids: 16
- proposals by local state: {'APPLIED': 20, 'REJECTED': 1}
- audit rows: 119 (continuous across restarts)
- scenario finished: True
- **violations: none**
