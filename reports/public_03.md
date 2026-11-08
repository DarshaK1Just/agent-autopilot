# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.360 | +5.6% | 0.244 | +0.1% | 0.524 | +4.7% | 34% | 390 (408) |
| arav_kyc_1 | 0.427 | +20.7% | 0.250 | +16.5% | 0.596 | +0.0% | 0% | 368 (370) |
| arav_renewal_0 | 0.461 | +14.6% | 0.273 | +3.5% | 0.594 | +9.3% | 44% | 437 (440) |
| kest_cancel_2 | 0.361 | +6.6% | 0.242 | -0.6% | 0.529 | +6.2% | 42% | 396 (411) |
| kest_kyc_1 | 0.472 | +33.6% | 0.272 | +27.4% | 0.594 | -0.0% | 0% | 439 (339) |
| kest_renewal_0 | 0.459 | +15.0% | 0.276 | +4.7% | 0.587 | +8.3% | 40% | 460 (433) |
| nort_cancel_2 | 0.365 | +7.8% | 0.243 | +0.2% | 0.530 | +6.3% | 41% | 374 (393) |
| nort_kyc_1 | 0.468 | +32.2% | 0.271 | +27.2% | 0.596 | +0.1% | 0% | 430 (323) |
| nort_renewal_0 | 0.458 | +13.2% | 0.274 | +4.2% | 0.589 | +7.5% | 40% | 429 (411) |
| tide_cancel_2 | 0.366 | +8.0% | 0.244 | -0.1% | 0.532 | +6.6% | 48% | 392 (407) |
| tide_kyc_1 | 0.436 | +23.4% | 0.255 | +19.0% | 0.592 | +0.0% | 0% | 408 (356) |
| tide_renewal_0 | 0.456 | +13.7% | 0.273 | +3.2% | 0.588 | +8.5% | 44% | 431 (438) |
| ALL | 0.424 | +16.2% | 0.260 | +8.1% | 0.572 | +5.2% | 26% | 4954 (4729) |

## Changes applied by the controller

48 applied — neutral: 13, beneficial: 35

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
- tide_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_cancel_2 v3 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.061 didΔ=+0.000 → **beneficial**
- arav_cancel_2 v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.052 → **beneficial**
- tide_cancel_2 v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- kest_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v3 (controller_approved) dims=['voice'] engageΔ=+0.026 didΔ=+0.000 → **beneficial**
- nort_renewal_0 v3 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.025 didΔ=+0.052 → **beneficial**
- arav_cancel_2 v4 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.015 didΔ=+0.000 → **beneficial**
- arav_kyc_1 v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.096 → **beneficial**
- tide_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- nort_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.452 → **beneficial**
- arav_renewal_0 v4 (controller_approved) dims=['cohorts', 'voice', 'caller_id'] engageΔ=+0.010 didΔ=+0.054 → **beneficial**
- kest_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v4 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**
- kest_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.494 → **beneficial**
- nort_renewal_0 v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.036 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- arav_renewal_0 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- kest_renewal_0 v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- tide_renewal_0 v4 (controller_approved) dims=['cohorts', 'welcome_message', 'voice', 'caller_id'] engageΔ=+0.045 didΔ=+0.048 → **beneficial**
- tide_cancel_2 v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.003 didΔ=+0.000 → **neutral**
- arav_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=+0.018 didΔ=+0.000 → **beneficial**
- tide_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.412 → **beneficial**
- kest_renewal_0 v6 (controller_approved) dims=['cohorts', 'welcome_message', 'voice'] engageΔ=+0.045 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- arav_kyc_1 v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.475 → **beneficial**
- arav_cancel_2 v6 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- tide_renewal_0 v5 (controller_approved) dims=['voice'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- kest_renewal_0 v7 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**
- arav_cancel_2 v7 (controller_approved) dims=['voice'] engageΔ=+0.011 didΔ=+0.000 → **beneficial**
- nort_cancel_2 v7 (controller_approved) dims=['welcome_message'] engageΔ=+0.003 didΔ=+0.000 → **neutral**
- arav_renewal_0 v6 (controller_approved) dims=['voice'] engageΔ=+0.005 didΔ=+0.000 → **neutral**
- arav_renewal_0 v7 (controller_approved) dims=['voice'] engageΔ=+0.011 didΔ=+0.000 → **beneficial**

## Governance

```
{
  "approval_requests": 52,
  "decisions": {
    "approved": 46,
    "rejected": 6,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 6
  },
  "applied_via_approval": 46,
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
    "3": 0.848,
    "4": 0.851
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.852,
    "4": 0.849
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.846,
    "4": 0.85
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.85,
    "4": 0.85
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0