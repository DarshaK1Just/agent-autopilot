# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-05T00:00:00+05:30, event cursor=40, open proposals at kill=[('nw_kyc-v1-155e06fcd024', 'PENDING')]
- kill 2: sim 2027-01-06T11:30:00+05:30, event cursor=74, open proposals at kill=[]
- kill 3: sim 2027-01-08T09:00:00+05:30, event cursor=132, open proposals at kill=[]
- kill 4: sim 2027-01-09T14:15:00+05:30, event cursor=170, open proposals at kill=[]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 14, unique proposal ids: 14
- proposals by local state: {'APPLIED': 16, 'REJECTED': 1}
- audit rows: 103 (continuous across restarts)
- scenario finished: True
- **violations: none**
