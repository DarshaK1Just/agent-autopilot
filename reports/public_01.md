# Grade report — public_01_dev

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.363 | +9.1% | 0.241 | +1.2% | 0.522 | +6.3% | 29% | 65 (47) |
| nw_kyc | 0.437 | +20.1% | 0.288 | +19.1% | 0.589 | -0.3% | 0% | 28 (21) |
| nw_renewal | 0.442 | +5.3% | 0.274 | +3.8% | 0.554 | +1.6% | 15% | 42 (42) |
| ALL | 0.405 | +10.0% | 0.261 | +5.6% | 0.548 | +3.4% | 16% | 135 (110) |

## Changes applied by the controller

11 applied — neutral: 2, beneficial: 8, harmful: 1

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.017 → **beneficial**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.085 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=-0.034 → **harmful**
- nw_renewal v4 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.101 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.152 → **beneficial**
- nw_renewal v5 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.032 didΔ=+0.000 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.034 didΔ=+0.000 → **beneficial**
- ks_cancel v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nw_kyc v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.062 → **beneficial**
- ks_cancel v5 (controller_approved) dims=['voice'] engageΔ=+0.010 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 10,
  "decisions": {
    "approved": 9,
    "rejected": 1,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 1
  },
  "applied_via_approval": 9,
  "auto_applied": 2,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nw_renewal": 1,
    "nw_kyc": 1,
    "ks_cancel": 2
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
  "nw_renewal:welcome_message=W3": {
    "3": 0.568,
    "4": 0.577,
    "5": 0.576,
    "6": 0.566,
    "7": 0.589
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0