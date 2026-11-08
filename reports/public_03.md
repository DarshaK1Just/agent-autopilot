# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.359 | +5.0% | 0.244 | -0.2% | 0.524 | +4.6% | 33% | 394 (408) |
| arav_kyc_1 | 0.430 | +21.5% | 0.251 | +16.9% | 0.597 | +0.3% | 0% | 383 (370) |
| arav_renewal_0 | 0.465 | +15.6% | 0.274 | +3.7% | 0.598 | +10.0% | 49% | 404 (440) |
| kest_cancel_2 | 0.357 | +5.5% | 0.243 | -0.1% | 0.522 | +4.6% | 33% | 406 (411) |
| kest_kyc_1 | 0.473 | +33.9% | 0.274 | +28.0% | 0.594 | -0.1% | 0% | 466 (339) |
| kest_renewal_0 | 0.450 | +12.7% | 0.272 | +3.4% | 0.585 | +7.8% | 38% | 433 (433) |
| nort_cancel_2 | 0.360 | +6.2% | 0.245 | +0.9% | 0.521 | +4.4% | 36% | 403 (393) |
| nort_kyc_1 | 0.474 | +33.7% | 0.273 | +28.3% | 0.596 | +0.1% | 0% | 410 (323) |
| nort_renewal_0 | 0.456 | +12.8% | 0.274 | +3.9% | 0.588 | +7.3% | 40% | 437 (411) |
| tide_cancel_2 | 0.355 | +4.6% | 0.243 | -0.4% | 0.519 | +4.0% | 32% | 385 (407) |
| tide_kyc_1 | 0.436 | +23.3% | 0.255 | +19.0% | 0.592 | +0.0% | 0% | 407 (356) |
| tide_renewal_0 | 0.457 | +14.0% | 0.273 | +3.2% | 0.589 | +8.5% | 44% | 457 (438) |
| ALL | 0.423 | +15.8% | 0.260 | +8.2% | 0.570 | +4.8% | 25% | 4985 (4729) |

## Changes applied by the controller

48 applied — neutral: 12, beneficial: 34, harmful: 2

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
- tide_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v3 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.039 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v3 (controller_approved) dims=['cohorts', 'welcome_message', 'voice'] engageΔ=+0.044 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.005 didΔ=+0.000 → **neutral**
- tide_cancel_2 v4 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.001 didΔ=+0.000 → **neutral**
- nort_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nort_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.052 → **beneficial**
- arav_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.096 → **beneficial**
- kest_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=-0.017 → **beneficial**
- tide_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.021 didΔ=+0.000 → **beneficial**
- nort_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.452 → **beneficial**
- nort_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.010 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.045 didΔ=+0.054 → **beneficial**
- nort_cancel_2 v5 (controller_approved) dims=['cohorts', 'welcome_message', 'voice'] engageΔ=+0.016 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.495 → **beneficial**
- nort_renewal_0 v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v4 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v5 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- kest_renewal_0 v5 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.050 → **beneficial**
- tide_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.045 didΔ=+0.048 → **beneficial**
- tide_cancel_2 v6 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.020 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v6 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- tide_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.411 → **beneficial**
- arav_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.027 didΔ=+0.000 → **beneficial**
- arav_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.474 → **beneficial**
- tide_renewal_0 v5 (controller_approved) dims=['voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- arav_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.018 didΔ=+0.000 → **beneficial**
- kest_cancel_2 v6 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v7 (controller_approved) dims=['welcome_message'] engageΔ=+0.005 didΔ=+0.000 → **neutral**
- arav_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.005 didΔ=+0.000 → **neutral**
- nort_cancel_2 v7 (controller_approved) dims=['welcome_message'] engageΔ=+0.002 didΔ=+0.000 → **neutral**
- tide_cancel_2 v8 (controller_approved) dims=['voice'] engageΔ=-0.068 didΔ=+0.000 → **harmful**
- arav_cancel_2 v6 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.001 didΔ=+0.000 → **neutral**
- tide_cancel_2 v9 (controller_approved) dims=['welcome_message'] engageΔ=-0.013 didΔ=+0.000 → **harmful**

## Governance

```
{
  "approval_requests": 55,
  "decisions": {
    "approved": 47,
    "rejected": 8,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 8
  },
  "applied_via_approval": 47,
  "auto_applied": 1,
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
    "kest_cancel_2": 3,
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
    "3": 0.852,
    "4": 0.85
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.85,
    "4": 0.848
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.85,
    "4": 0.85
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.849,
    "4": 0.852
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0