# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-04T10:00:00+05:30, event cursor=1, open proposals at kill=[]
- kill 2: sim 2027-01-05T12:15:00+05:30, event cursor=47, open proposals at kill=[]
- kill 3: sim 2027-01-08T07:45:00+05:30, event cursor=118, open proposals at kill=[('nw_kyc-v2-ae126aeb8cfc', 'PENDING')]
- kill 4: sim 2027-01-09T01:30:00+05:30, event cursor=146, open proposals at kill=[('nw_renewal-v6-5baff4e24601', 'PENDING'), ('nw_kyc-v3-df5872b2ac0e', 'PENDING')]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 15, unique proposal ids: 15
- proposals by local state: {'APPLIED': 15, 'REJECTED': 2, 'ABANDONED': 1}
- audit rows: 101 (continuous across restarts)
- scenario finished: True
- **violations: none**
