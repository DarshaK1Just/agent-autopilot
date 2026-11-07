# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-05T10:15:00+05:30, event cursor=38, open proposals at kill=[]
- kill 2: sim 2027-01-06T07:15:00+05:30, event cursor=79, open proposals at kill=[('nw_kyc-v1-6f8e2a50b05a', 'PENDING'), ('nw_renewal-v3-fb2200a88641', 'PENDING')]
- kill 3: sim 2027-01-07T22:30:00+05:30, event cursor=148, open proposals at kill=[('nw_kyc-v3-4059785c3fb9', 'PENDING'), ('nw_renewal-v5-bb96b941a35a', 'PENDING')]
- kill 4: sim 2027-01-09T11:15:00+05:30, event cursor=169, open proposals at kill=[]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 16, unique proposal ids: 16
- proposals by local state: {'APPLIED': 14, 'REJECTED': 2, 'STALE': 1}
- audit rows: 101 (continuous across restarts)
- scenario finished: True
- **violations: none**
