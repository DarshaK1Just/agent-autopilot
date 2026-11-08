# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.365 | +7.0% | 0.245 | +0.4% | 0.529 | +5.6% | 36% | 418 (408) |
| arav_kyc_1 | 0.429 | +21.2% | 0.251 | +17.0% | 0.595 | -0.1% | 0% | 410 (370) |
| arav_renewal_0 | 0.466 | +15.8% | 0.275 | +4.2% | 0.596 | +9.7% | 46% | 449 (440) |
| kest_cancel_2 | 0.351 | +3.6% | 0.243 | -0.2% | 0.515 | +3.3% | 27% | 400 (411) |
| kest_kyc_1 | 0.473 | +33.8% | 0.272 | +27.3% | 0.596 | +0.3% | 0% | 436 (339) |
| kest_renewal_0 | 0.461 | +15.4% | 0.274 | +3.9% | 0.594 | +9.5% | 43% | 441 (433) |
| nort_cancel_2 | 0.358 | +5.6% | 0.243 | +0.3% | 0.521 | +4.4% | 32% | 377 (393) |
| nort_kyc_1 | 0.470 | +32.6% | 0.273 | +28.0% | 0.594 | -0.2% | 0% | 437 (323) |
| nort_renewal_0 | 0.465 | +14.9% | 0.274 | +3.9% | 0.598 | +9.1% | 48% | 445 (411) |
| tide_cancel_2 | 0.367 | +8.1% | 0.244 | -0.2% | 0.533 | +6.9% | 48% | 390 (407) |
| tide_kyc_1 | 0.439 | +24.3% | 0.256 | +19.3% | 0.595 | +0.5% | 0% | 437 (356) |
| tide_renewal_0 | 0.462 | +15.2% | 0.275 | +4.2% | 0.590 | +8.8% | 42% | 475 (438) |
| ALL | 0.425 | +16.5% | 0.260 | +8.3% | 0.573 | +5.3% | 26% | 5115 (4729) |

## Changes applied by the controller

48 applied — neutral: 15, beneficial: 33

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
- kest_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=-0.015 → **neutral**
- nort_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v3 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.061 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.049 → **beneficial**
- tide_cancel_2 v4 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.038 didΔ=+0.000 → **beneficial**
- nort_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.036 didΔ=+0.050 → **beneficial**
- arav_renewal_0 v4 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.036 didΔ=+0.051 → **beneficial**
- kest_renewal_0 v4 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.053 → **beneficial**
- arav_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.096 → **beneficial**
- nort_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.452 → **beneficial**
- arav_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v3 (controller_approved) dims=['voice'] engageΔ=+0.026 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.494 → **beneficial**
- kest_renewal_0 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nort_renewal_0 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- nort_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- tide_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.422 → **beneficial**
- arav_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- arav_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.474 → **beneficial**
- arav_renewal_0 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- nort_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- kest_renewal_0 v6 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- tide_cancel_2 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.003 didΔ=+0.000 → **neutral**
- kest_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v6 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- kest_renewal_0 v7 (controller_approved) dims=['voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- arav_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- kest_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v7 (controller_approved) dims=['voice'] engageΔ=+0.011 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v6 (controller_approved) dims=['welcome_message'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nort_cancel_2 v6 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.002 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 50,
  "decisions": {
    "approved": 46,
    "rejected": 4,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 4
  },
  "applied_via_approval": 46,
  "auto_applied": 2,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nort_renewal_0": 2,
    "tide_cancel_2": 2,
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
    "4": 0.852
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.85,
    "4": 0.851
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.851,
    "4": 0.85
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.852,
    "4": 0.851
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0