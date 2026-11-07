# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.355 | +3.9% | 0.245 | +0.3% | 0.516 | +3.1% | 27% | 379 (408) |
| arav_kyc_1 | 0.429 | +21.1% | 0.251 | +16.9% | 0.596 | +0.1% | 0% | 389 (370) |
| arav_renewal_0 | 0.465 | +15.7% | 0.275 | +4.0% | 0.598 | +10.1% | 51% | 505 (440) |
| kest_cancel_2 | 0.363 | +7.2% | 0.244 | +0.1% | 0.530 | +6.2% | 43% | 406 (411) |
| kest_kyc_1 | 0.471 | +33.4% | 0.274 | +28.0% | 0.592 | -0.4% | 0% | 434 (339) |
| kest_renewal_0 | 0.452 | +13.0% | 0.272 | +3.2% | 0.586 | +8.0% | 39% | 469 (433) |
| nort_cancel_2 | 0.368 | +8.5% | 0.244 | +0.5% | 0.534 | +7.0% | 44% | 380 (393) |
| nort_kyc_1 | 0.473 | +33.6% | 0.272 | +27.5% | 0.598 | +0.5% | 0% | 439 (323) |
| nort_renewal_0 | 0.456 | +12.7% | 0.271 | +3.0% | 0.592 | +8.1% | 43% | 428 (411) |
| tide_cancel_2 | 0.356 | +5.0% | 0.243 | -0.4% | 0.522 | +4.6% | 36% | 369 (407) |
| tide_kyc_1 | 0.433 | +22.5% | 0.255 | +18.7% | 0.591 | -0.1% | 0% | 424 (356) |
| tide_renewal_0 | 0.469 | +17.0% | 0.275 | +4.2% | 0.599 | +10.4% | 50% | 430 (438) |
| ALL | 0.424 | +16.2% | 0.260 | +8.1% | 0.573 | +5.3% | 27% | 5052 (4729) |

## Changes applied by the controller

40 applied — neutral: 7, beneficial: 33

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
- arav_cancel_2 v5 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.020 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v6 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.002 didΔ=+0.000 → **neutral**
- tide_cancel_2 v7 (controller_approved) dims=['voice'] engageΔ=+0.011 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v6 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.013 didΔ=+0.000 → **beneficial**

## Governance

```
{
  "approval_requests": 43,
  "decisions": {
    "approved": 38,
    "rejected": 5,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 5
  },
  "applied_via_approval": 38,
  "auto_applied": 2,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "arav_cancel_2": 3,
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
    "4": 0.85
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.85,
    "4": 0.853
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.854,
    "4": 0.852
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.848,
    "4": 0.851
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0