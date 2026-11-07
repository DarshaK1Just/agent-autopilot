# Grade report — public_01_dev

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.356 | +7.0% | 0.241 | +1.1% | 0.514 | +4.8% | 26% | 45 (47) |
| nw_kyc | 0.448 | +23.3% | 0.290 | +20.0% | 0.597 | +1.1% | 0% | 21 (21) |
| nw_renewal | 0.466 | +11.1% | 0.282 | +7.2% | 0.564 | +3.4% | 34% | 50 (42) |
| ALL | 0.412 | +11.9% | 0.265 | +6.9% | 0.550 | +3.9% | 22% | 116 (110) |

## Changes applied by the controller

16 applied — neutral: 8, beneficial: 8

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.017 → **beneficial**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.080 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.060 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.063 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.152 → **beneficial**
- ks_cancel v4 (controller_auto) dims=['voice'] engageΔ=+0.004 didΔ=+0.000 → **neutral**
- nw_renewal v5 (controller_approved) dims=['voice'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- ks_cancel v5 (controller_approved) dims=['voice'] engageΔ=+0.007 didΔ=+0.000 → **neutral**
- nw_kyc v4 (controller_approved) dims=['cohorts', 'schedule'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- nw_renewal v6 (controller_approved) dims=['voice'] engageΔ=+0.001 didΔ=+0.000 → **neutral**
- nw_kyc v5 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.058 → **beneficial**
- nw_renewal v7 (controller_approved) dims=['cohorts', 'voice'] engageΔ=+0.001 didΔ=+0.000 → **neutral**
- nw_renewal v8 (controller_approved) dims=['welcome_message'] engageΔ=-0.005 didΔ=+0.000 → **neutral**
- ks_cancel v6 (controller_approved) dims=['cohorts', 'voice', 'schedule'] engageΔ=+0.026 didΔ=+0.000 → **beneficial**

## Governance

```
{
  "approval_requests": 14,
  "decisions": {
    "approved": 14,
    "expired": 0
  },
  "rejection_reasons": {},
  "applied_via_approval": 14,
  "auto_applied": 2,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nw_renewal": 2,
    "nw_kyc": 1,
    "ks_cancel": 1
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
    "3": 0.865,
    "4": 0.554,
    "5": 0.0,
    "6": 0.0,
    "7": 0.0
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0