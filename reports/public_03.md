# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.366 | +7.3% | 0.244 | +0.0% | 0.534 | +6.7% | 47% | 390 (408) |
| arav_kyc_1 | 0.429 | +21.2% | 0.251 | +17.0% | 0.594 | -0.3% | 0% | 420 (370) |
| arav_renewal_0 | 0.471 | +17.1% | 0.277 | +5.0% | 0.599 | +10.2% | 51% | 451 (440) |
| kest_cancel_2 | 0.360 | +6.2% | 0.243 | +0.0% | 0.525 | +5.4% | 39% | 377 (411) |
| kest_kyc_1 | 0.471 | +33.4% | 0.272 | +27.0% | 0.596 | +0.3% | 0% | 432 (339) |
| kest_renewal_0 | 0.461 | +15.5% | 0.274 | +3.8% | 0.594 | +9.5% | 47% | 427 (433) |
| nort_cancel_2 | 0.359 | +6.1% | 0.242 | -0.1% | 0.528 | +5.9% | 41% | 415 (393) |
| nort_kyc_1 | 0.473 | +33.6% | 0.274 | +28.5% | 0.596 | +0.0% | 0% | 424 (323) |
| nort_renewal_0 | 0.455 | +12.4% | 0.271 | +2.8% | 0.592 | +8.0% | 40% | 422 (411) |
| tide_cancel_2 | 0.358 | +5.6% | 0.244 | -0.2% | 0.523 | +4.7% | 36% | 364 (407) |
| tide_kyc_1 | 0.439 | +24.3% | 0.256 | +19.4% | 0.594 | +0.4% | 0% | 431 (356) |
| tide_renewal_0 | 0.466 | +16.3% | 0.275 | +4.0% | 0.600 | +10.6% | 53% | 468 (438) |
| ALL | 0.426 | +16.7% | 0.260 | +8.2% | 0.574 | +5.6% | 28% | 5021 (4729) |

## Changes applied by the controller

39 applied — neutral: 6, beneficial: 32, harmful: 1

- nort_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- arav_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- tide_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- kest_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nort_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.018 → **beneficial**
- tide_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.092 → **beneficial**
- nort_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.093 → **beneficial**
- arav_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.018 → **beneficial**
- tide_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.018 → **beneficial**
- nort_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.099 → **beneficial**
- kest_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.061 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v3 (controller_approved) dims=['voice'] engageΔ=+0.056 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v3 (controller_approved) dims=['voice'] engageΔ=-0.017 didΔ=+0.000 → **harmful**
- tide_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.062 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.059 → **beneficial**
- arav_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.062 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v4 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.048 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.049 → **beneficial**
- arav_cancel_2 v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.023 didΔ=+0.000 → **beneficial**
- arav_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.093 → **beneficial**
- nort_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.441 → **beneficial**
- kest_renewal_0 v3 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.083 didΔ=-0.016 → **beneficial**
- tide_renewal_0 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.019 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.019 didΔ=+0.000 → **beneficial**
- nort_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.062 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.060 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.483 → **beneficial**
- nort_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.055 → **beneficial**
- kest_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.059 → **beneficial**
- nort_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.032 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.021 didΔ=+0.000 → **beneficial**
- tide_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.411 → **beneficial**
- arav_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.463 → **beneficial**
- tide_cancel_2 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.033 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v6 (controller_approved) dims=['voice'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- tide_cancel_2 v7 (controller_approved) dims=['voice'] engageΔ=+0.000 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 41,
  "decisions": {
    "approved": 35,
    "rejected": 6,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 6
  },
  "applied_via_approval": 35,
  "auto_applied": 4,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nort_renewal_0": 2,
    "nort_kyc_1": 1,
    "nort_cancel_2": 3,
    "kest_renewal_0": 2,
    "kest_kyc_1": 1,
    "kest_cancel_2": 3,
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
    "3": 0.85,
    "4": 0.849
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.848,
    "4": 0.851
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.847,
    "4": 0.849
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.853,
    "4": 0.85
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0