# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.363 | +6.4% | 0.244 | -0.2% | 0.531 | +6.0% | 46% | 419 (408) |
| arav_kyc_1 | 0.441 | +24.6% | 0.258 | +20.2% | 0.596 | +0.0% | 0% | 392 (370) |
| arav_renewal_0 | 0.469 | +16.7% | 0.276 | +4.6% | 0.598 | +10.1% | 51% | 404 (440) |
| kest_cancel_2 | 0.360 | +6.2% | 0.244 | +0.4% | 0.527 | +5.8% | 40% | 406 (411) |
| kest_kyc_1 | 0.451 | +27.8% | 0.263 | +23.0% | 0.593 | -0.3% | 0% | 410 (339) |
| kest_renewal_0 | 0.467 | +16.8% | 0.274 | +4.0% | 0.600 | +10.6% | 51% | 429 (433) |
| nort_cancel_2 | 0.367 | +8.3% | 0.245 | +0.9% | 0.533 | +6.8% | 48% | 415 (393) |
| nort_kyc_1 | 0.473 | +33.4% | 0.275 | +28.9% | 0.592 | -0.6% | 0% | 441 (323) |
| nort_renewal_0 | 0.462 | +14.3% | 0.276 | +4.8% | 0.592 | +8.1% | 43% | 445 (411) |
| tide_cancel_2 | 0.364 | +7.2% | 0.244 | +0.1% | 0.530 | +6.3% | 45% | 390 (407) |
| tide_kyc_1 | 0.470 | +32.9% | 0.274 | +27.5% | 0.590 | -0.3% | 0% | 409 (356) |
| tide_renewal_0 | 0.462 | +15.3% | 0.277 | +4.7% | 0.592 | +9.1% | 44% | 481 (438) |
| ALL | 0.429 | +17.5% | 0.262 | +9.1% | 0.574 | +5.6% | 29% | 5041 (4729) |

## Changes applied by the controller

40 applied — neutral: 8, beneficial: 30, harmful: 2

- nort_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- arav_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- tide_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- kest_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- arav_kyc_1 v2 (controller_approved) dims=['cohorts', 'caller_id', 'schedule'] engageΔ=+0.000 didΔ=+0.089 → **beneficial**
- nort_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.018 → **beneficial**
- arav_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.018 → **beneficial**
- tide_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.018 → **beneficial**
- tide_kyc_1 v2 (controller_approved) dims=['cohorts', 'caller_id', 'schedule'] engageΔ=+0.000 didΔ=+0.095 → **beneficial**
- nort_kyc_1 v2 (controller_approved) dims=['cohorts', 'caller_id', 'schedule'] engageΔ=+0.000 didΔ=+0.100 → **beneficial**
- kest_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.061 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v3 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.039 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v3 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.092 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v2 (controller_approved) dims=['cohorts', 'caller_id', 'schedule'] engageΔ=+0.000 didΔ=+0.079 → **beneficial**
- nort_renewal_0 v3 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.062 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v3 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.062 didΔ=+0.000 → **beneficial**
- nort_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.049 → **beneficial**
- tide_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.049 → **beneficial**
- nort_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.050 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.055 didΔ=+0.000 → **beneficial**
- tide_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.413 → **beneficial**
- tide_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.055 didΔ=+0.000 → **beneficial**
- nort_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.421 → **beneficial**
- kest_renewal_0 v3 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id', 'schedule'] engageΔ=+0.082 didΔ=-0.018 → **beneficial**
- arav_renewal_0 v4 (controller_approved) dims=['cohorts', 'voice', 'caller_id', 'schedule'] engageΔ=+0.019 didΔ=+0.053 → **beneficial**
- kest_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.305 → **beneficial**
- nort_renewal_0 v5 (controller_approved) dims=['voice'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- arav_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.358 → **beneficial**
- kest_renewal_0 v4 (controller_approved) dims=['voice', 'caller_id'] engageΔ=+0.005 didΔ=+0.000 → **neutral**
- arav_renewal_0 v5 (controller_approved) dims=['voice'] engageΔ=-0.001 didΔ=+0.000 → **neutral**
- kest_cancel_2 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'schedule'] engageΔ=-0.012 didΔ=+0.000 → **harmful**
- kest_renewal_0 v5 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.049 → **beneficial**
- kest_kyc_1 v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.129 → **beneficial**
- nort_cancel_2 v5 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.013 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.007 didΔ=+0.000 → **neutral**
- arav_cancel_2 v5 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.013 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v5 (controller_approved) dims=['welcome_message'] engageΔ=-0.042 didΔ=+0.000 → **harmful**

## Governance

```
{
  "approval_requests": 39,
  "decisions": {
    "approved": 37,
    "rejected": 2,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 2
  },
  "applied_via_approval": 37,
  "auto_applied": 3,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nort_renewal_0": 2,
    "nort_kyc_1": 1,
    "nort_cancel_2": 2,
    "kest_renewal_0": 2,
    "kest_kyc_1": 1,
    "kest_cancel_2": 2,
    "arav_renewal_0": 2,
    "arav_kyc_1": 1,
    "arav_cancel_2": 2,
    "tide_renewal_0": 2,
    "tide_kyc_1": 1,
    "tide_cancel_2": 2
  }
}
```

## Incidents

```
[]
```

## Decaying variants — share of in-population calls still on the variant, by day after onset

```
{
  "nort_renewal_0:welcome_message=W3": {
    "3": 0.848,
    "4": 0.849
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.847,
    "4": 0.847
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.851,
    "4": 0.848
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.849,
    "4": 0.849
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0