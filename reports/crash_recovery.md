# Crash-recovery run

scenario `02_incidents`, SIGKILL x4, seed 7

- kill 1: sim 2027-01-05T00:30:00+05:30, event cursor=40, open proposals at kill=[('nw_kyc-v1-155e06fcd024', 'PENDING')]
- kill 2: sim 2027-01-06T15:45:00+05:30, event cursor=79, open proposals at kill=[('ks_cancel-v3-0e4d0946c2d0', 'PENDING')]
- kill 3: sim 2027-01-08T19:15:00+05:30, event cursor=150, open proposals at kill=[('nw_kyc-v2-ae126aeb8cfc', 'PENDING')]
- kill 4: sim 2027-01-09T22:45:00+05:30, event cursor=188, open proposals at kill=[('nw_kyc-v3-df5872b2ac0e', 'PENDING'), ('nw_renewal-v9-e2bb85358851', 'PENDING')]
- final run exit code 0

- controller starts recorded in audit: 5 (4 restarts)
- approvals in simulator: 17, unique proposal ids: 17
- proposals by local state: {'APPLIED': 21, 'REJECTED': 1}
- audit rows: 122 (continuous across restarts)
- scenario finished: True
- **violations: none**
