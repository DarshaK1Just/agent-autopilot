# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-04T00:00:00+05:30, event cursor=None, open proposals at kill=[]
- kill 2: sim 2027-01-05T09:30:00+05:30, event cursor=45, open proposals at kill=[('nw_kyc-v1-155e06fcd024', 'PENDING')]
- kill 3: sim 2027-01-08T16:45:00+05:30, event cursor=132, open proposals at kill=[('nw_renewal-v6-bb96b941a35a', 'PENDING'), ('nw_kyc-v2-ae126aeb8cfc', 'PENDING')]
- kill 4: sim 2027-01-09T19:15:00+05:30, event cursor=171, open proposals at kill=[('nw_kyc-v3-df5872b2ac0e', 'PENDING')]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 18, unique proposal ids: 18
- proposals by local state: {'APPLIED': 17, 'REJECTED': 2, 'ABANDONED': 1}
- audit rows: 113 (continuous across restarts)
- scenario finished: True
- **violations: none**
