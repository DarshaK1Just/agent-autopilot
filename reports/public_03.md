# Grade report — public_03_load

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| arav_cancel_2 | 0.360 | +5.5% | 0.244 | -0.1% | 0.527 | +5.3% | 39% | 388 (408) |
| arav_kyc_1 | 0.430 | +21.4% | 0.251 | +17.0% | 0.595 | -0.1% | 0% | 417 (370) |
| arav_renewal_0 | 0.473 | +17.7% | 0.278 | +5.1% | 0.601 | +10.6% | 51% | 445 (440) |
| kest_cancel_2 | 0.362 | +6.9% | 0.244 | +0.2% | 0.527 | +5.8% | 39% | 369 (411) |
| kest_kyc_1 | 0.472 | +33.5% | 0.272 | +27.3% | 0.595 | +0.1% | 0% | 414 (339) |
| kest_renewal_0 | 0.460 | +15.2% | 0.273 | +3.8% | 0.593 | +9.4% | 48% | 437 (433) |
| nort_cancel_2 | 0.361 | +6.6% | 0.243 | +0.2% | 0.528 | +5.9% | 41% | 402 (393) |
| nort_kyc_1 | 0.475 | +34.2% | 0.275 | +28.9% | 0.596 | +0.1% | 0% | 412 (323) |
| nort_renewal_0 | 0.457 | +12.9% | 0.271 | +2.9% | 0.593 | +8.3% | 40% | 414 (411) |
| tide_cancel_2 | 0.358 | +5.6% | 0.243 | -0.5% | 0.524 | +5.0% | 36% | 381 (407) |
| tide_kyc_1 | 0.437 | +23.6% | 0.255 | +18.9% | 0.594 | +0.4% | 0% | 409 (356) |
| tide_renewal_0 | 0.471 | +17.5% | 0.276 | +4.5% | 0.602 | +11.0% | 53% | 472 (438) |
| ALL | 0.426 | +16.8% | 0.260 | +8.3% | 0.575 | +5.7% | 28% | 4960 (4729) |

## Changes applied by the controller

40 applied — neutral: 6, beneficial: 32, harmful: 2

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
- arav_cancel_2 v5 (controller_approved) dims=['voice'] engageΔ=-0.068 didΔ=+0.000 → **harmful**

## Governance

```
{
  "approval_requests": 42,
  "decisions": {
    "approved": 36,
    "rejected": 6,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 6
  },
  "applied_via_approval": 36,
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
    "4": 0.85
  },
  "kest_renewal_0:welcome_message=W3": {
    "3": 0.848,
    "4": 0.85
  },
  "arav_renewal_0:welcome_message=W3": {
    "3": 0.847,
    "4": 0.85
  },
  "tide_renewal_0:welcome_message=W3": {
    "3": 0.853,
    "4": 0.85
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0