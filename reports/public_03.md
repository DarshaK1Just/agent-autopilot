# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.358 | +4.8% | 0.244 | -0.2% | 0.521 | +4.1% | 34% | 385 (408) |
| arav_kyc_1 | 0.431 | +21.8% | 0.251 | +17.2% | 0.597 | +0.2% | 0% | 374 (370) |
| arav_renewal_0 | 0.461 | +14.6% | 0.273 | +3.3% | 0.594 | +9.4% | 46% | 416 (440) |
| kest_cancel_2 | 0.356 | +5.0% | 0.244 | +0.2% | 0.519 | +4.1% | 30% | 370 (411) |
| kest_kyc_1 | 0.472 | +33.6% | 0.273 | +27.6% | 0.593 | -0.2% | 0% | 434 (339) |
| kest_renewal_0 | 0.460 | +15.1% | 0.274 | +4.0% | 0.592 | +9.1% | 45% | 467 (433) |
| nort_cancel_2 | 0.362 | +6.8% | 0.242 | +0.0% | 0.529 | +6.0% | 40% | 422 (393) |
| nort_kyc_1 | 0.470 | +32.7% | 0.272 | +27.6% | 0.596 | +0.1% | 0% | 475 (323) |
| nort_renewal_0 | 0.459 | +13.5% | 0.275 | +4.4% | 0.589 | +7.6% | 40% | 453 (411) |
| tide_cancel_2 | 0.360 | +6.1% | 0.244 | -0.2% | 0.525 | +5.2% | 38% | 392 (407) |
| tide_kyc_1 | 0.439 | +24.2% | 0.256 | +19.3% | 0.594 | +0.3% | 0% | 411 (356) |
| tide_renewal_0 | 0.467 | +16.6% | 0.275 | +4.1% | 0.597 | +10.2% | 49% | 464 (438) |
| ALL | 0.425 | +16.3% | 0.260 | +8.2% | 0.572 | +5.2% | 26% | 5063 (4729) |

## Changes applied by the controller

49 applied — neutral: 15, beneficial: 34

- tide_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nort_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nort_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.018 → **beneficial**
- arav_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- tide_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.092 → **beneficial**
- kest_cancel_2 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- tide_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.018 → **beneficial**
- nort_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.098 → **beneficial**
- arav_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.061 didΔ=-0.017 → **beneficial**
- kest_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.103 → **beneficial**
- kest_renewal_0 v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.061 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=-0.015 → **neutral**
- tide_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.049 → **beneficial**
- tide_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.015 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v3 (controller_approved) dims=['voice'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- nort_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.052 → **beneficial**
- arav_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.096 → **beneficial**
- tide_renewal_0 v5 (controller_approved) dims=['cohorts', 'welcome_message', 'voice'] engageΔ=+0.045 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- kest_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.016 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.035 didΔ=+0.055 → **beneficial**
- nort_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.452 → **beneficial**
- arav_renewal_0 v4 (controller_approved) dims=['cohorts', 'voice', 'caller_id'] engageΔ=+0.009 didΔ=+0.054 → **beneficial**
- nort_cancel_2 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice'] engageΔ=+0.038 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.495 → **beneficial**
- nort_renewal_0 v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- nort_renewal_0 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=-0.000 didΔ=+0.000 → **neutral**
- nort_cancel_2 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.017 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v6 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.026 didΔ=+0.000 → **beneficial**
- tide_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.410 → **beneficial**
- arav_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- kest_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- arav_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.475 → **beneficial**
- nort_cancel_2 v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.002 didΔ=+0.000 → **neutral**
- arav_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- nort_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- arav_cancel_2 v7 (controller_approved) dims=['welcome_message'] engageΔ=+0.003 didΔ=+0.000 → **neutral**
- kest_cancel_2 v6 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 52,
  "decisions": {
    "approved": 47,
    "rejected": 5,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 5
  },
  "applied_via_approval": 47,
  "auto_applied": 2,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nort_renewal_0": 2,
    "tide_cancel_2": 3,
    "tide_kyc_1": 1,
    "tide_renewal_0": 2,
    "arav_cancel_2": 2,
    "arav_kyc_1": 1,
    "arav_renewal_0": 2,
    "kest_cancel_2": 2,
    "kest_kyc_1": 1,
    "kest_renewal_0": 2,
    "nort_cancel_2": 3,
    "nort_kyc_1": 1
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
    "3": 0.853,
    "4": 0.851
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.849,
    "4": 0.851
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.847,
    "4": 0.85
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.851,
    "4": 0.851
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0