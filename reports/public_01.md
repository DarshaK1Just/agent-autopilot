# Grade report — public_01_dev

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.351 | +5.5% | 0.244 | +2.4% | 0.502 | +2.2% | 18% | 58 (47) |
| nw_kyc | 0.423 | +16.3% | 0.279 | +15.3% | 0.590 | -0.0% | 0% | 22 (21) |
| nw_renewal | 0.453 | +7.8% | 0.280 | +6.4% | 0.554 | +1.5% | 15% | 39 (42) |
| ALL | 0.400 | +8.7% | 0.263 | +6.3% | 0.539 | +1.7% | 12% | 119 (110) |

## Changes applied by the controller

12 applied — neutral: 2, beneficial: 10

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.017 → **beneficial**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.085 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.051 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.098 → **beneficial**
- nw_renewal v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.001 didΔ=+0.000 → **neutral**
- nw_kyc v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.082 → **beneficial**
- ks_cancel v4 (controller_approved) dims=['voice'] engageΔ=+0.025 didΔ=+0.000 → **beneficial**
- nw_renewal v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.090 didΔ=+0.000 → **beneficial**
- ks_cancel v5 (controller_approved) dims=['voice'] engageΔ=+0.029 didΔ=+0.000 → **beneficial**

## Governance

```
{
  "approval_requests": 13,
  "decisions": {
    "approved": 11,
    "rejected": 1,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 1
  },
  "applied_via_approval": 11,
  "auto_applied": 1,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "ks_cancel": 1,
    "nw_kyc": 1,
    "nw_renewal": 1
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
    "3": 0.498,
    "4": 0.675,
    "5": 0.843,
    "6": 0.556,
    "7": 0.0
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0