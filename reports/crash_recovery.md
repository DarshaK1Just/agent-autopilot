# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-04T19:15:00+05:30, event cursor=32, open proposals at kill=[]
- kill 2: sim 2027-01-06T03:00:00+05:30, event cursor=76, open proposals at kill=[('nw_kyc-v1-6f8e2a50b05a', 'PENDING')]
- kill 3: sim 2027-01-07T17:00:00+05:30, event cursor=131, open proposals at kill=[('nw_renewal-v5-64ca2ec224a0', 'PENDING')]
- kill 4: sim 2027-01-08T14:30:00+05:30, event cursor=160, open proposals at kill=[]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 17, unique proposal ids: 17
- proposals by local state: {'APPLIED': 16, 'REJECTED': 2}
- audit rows: 106 (continuous across restarts)
- scenario finished: True
- **violations: none**
