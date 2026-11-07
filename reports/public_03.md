# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.352 | +3.0% | 0.244 | -0.3% | 0.515 | +2.9% | 27% | 399 (408) |
| arav_kyc_1 | 0.431 | +21.7% | 0.252 | +17.6% | 0.595 | -0.0% | 0% | 402 (370) |
| arav_renewal_0 | 0.467 | +16.2% | 0.275 | +4.1% | 0.599 | +10.3% | 51% | 485 (440) |
| kest_cancel_2 | 0.364 | +7.4% | 0.244 | +0.2% | 0.530 | +6.4% | 43% | 425 (411) |
| kest_kyc_1 | 0.474 | +34.2% | 0.274 | +28.0% | 0.595 | +0.1% | 0% | 414 (339) |
| kest_renewal_0 | 0.453 | +13.3% | 0.273 | +3.6% | 0.584 | +7.8% | 38% | 478 (433) |
| nort_cancel_2 | 0.366 | +8.0% | 0.243 | +0.4% | 0.532 | +6.6% | 43% | 412 (393) |
| nort_kyc_1 | 0.473 | +33.4% | 0.272 | +27.6% | 0.597 | +0.3% | 0% | 435 (323) |
| nort_renewal_0 | 0.460 | +13.7% | 0.272 | +3.3% | 0.595 | +8.6% | 44% | 404 (411) |
| tide_cancel_2 | 0.355 | +4.6% | 0.244 | -0.1% | 0.519 | +4.0% | 31% | 379 (407) |
| tide_kyc_1 | 0.436 | +23.4% | 0.256 | +19.1% | 0.593 | +0.2% | 0% | 452 (356) |
| tide_renewal_0 | 0.467 | +16.4% | 0.275 | +4.2% | 0.596 | +9.9% | 50% | 429 (438) |
| ALL | 0.425 | +16.4% | 0.260 | +8.3% | 0.572 | +5.3% | 26% | 5114 (4729) |

## Changes applied by the controller

39 applied — neutral: 7, beneficial: 31, harmful: 1

- arav_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- tide_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nort_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- tide_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.092 → **beneficial**
- kest_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- tide_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.018 → **beneficial**
- nort_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.017 → **beneficial**
- nort_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.098 → **beneficial**
- arav_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.017 → **beneficial**
- nort_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.103 → **beneficial**
- arav_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.061 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v3 (controller_auto) dims=['voice'] engageΔ=+0.004 didΔ=+0.000 → **neutral**
- nort_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v3 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.060 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.031 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.026 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.056 didΔ=+0.051 → **beneficial**
- kest_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.055 didΔ=+0.052 → **beneficial**
- arav_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.096 → **beneficial**
- kest_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=-0.017 → **beneficial**
- nort_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.452 → **beneficial**
- nort_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.495 → **beneficial**
- kest_renewal_0 v4 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v5 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.050 → **beneficial**
- tide_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.411 → **beneficial**
- nort_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.056 didΔ=+0.050 → **beneficial**
- arav_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.474 → **beneficial**
- tide_cancel_2 v6 (controller_approved) dims=['voice'] engageΔ=+0.008 didΔ=+0.000 → **neutral**
- arav_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.033 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v7 (controller_approved) dims=['voice'] engageΔ=-0.016 didΔ=+0.000 → **harmful**
- arav_renewal_0 v5 (controller_approved) dims=['voice'] engageΔ=+0.005 didΔ=+0.000 → **neutral**
- arav_cancel_2 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.020 didΔ=+0.000 → **beneficial**

## Governance

```
{
  "approval_requests": 42,
  "decisions": {
    "approved": 37,
    "rejected": 5,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 5
  },
  "applied_via_approval": 37,
  "auto_applied": 2,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "arav_cancel_2": 2,
    "tide_renewal_0": 2,
    "tide_kyc_1": 1,
    "tide_cancel_2": 2,
    "nort_renewal_0": 2,
    "nort_kyc_1": 1,
    "nort_cancel_2": 2,
    "kest_renewal_0": 2,
    "kest_kyc_1": 1,
    "kest_cancel_2": 2,
    "arav_renewal_0": 2,
    "arav_kyc_1": 1
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
    "3": 0.851,
    "4": 0.852
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.849,
    "4": 0.846
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.848,
    "4": 0.848
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.851,
    "4": 0.85
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0