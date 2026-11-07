# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-04T14:00:00+05:30, event cursor=15, open proposals at kill=[('nw_renewal-v1-874ed436610d', 'PENDING'), ('nw_kyc-v1-155e06fcd024', 'PENDING')]
- kill 2: sim 2027-01-05T05:15:00+05:30, event cursor=44, open proposals at kill=[('nw_kyc-v1-155e06fcd024', 'PENDING')]
- kill 3: sim 2027-01-06T16:00:00+05:30, event cursor=92, open proposals at kill=[('nw_kyc-v2-f817dd0d78da', 'PENDING')]
- kill 4: sim 2027-01-07T05:00:00+05:30, event cursor=113, open proposals at kill=[('nw_kyc-v2-f817dd0d78da', 'PENDING')]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 17, unique proposal ids: 17
- proposals by local state: {'APPLIED': 13, 'REJECTED': 3, 'ABANDONED': 1, 'PENDING': 1}
- audit rows: 101 (continuous across restarts)
- scenario finished: True
- **violations: none**
