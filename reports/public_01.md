# Grade report — public_01_dev

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.359 | +7.7% | 0.244 | +2.3% | 0.512 | +4.3% | 17% | 61 (47) |
| nw_kyc | 0.444 | +22.2% | 0.288 | +19.1% | 0.597 | +1.0% | 0% | 34 (21) |
| nw_renewal | 0.458 | +9.2% | 0.275 | +4.5% | 0.570 | +4.4% | 30% | 47 (42) |
| ALL | 0.410 | +11.3% | 0.263 | +6.3% | 0.551 | +3.9% | 17% | 142 (110) |

## Changes applied by the controller

13 applied — neutral: 5, beneficial: 8

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.017 → **beneficial**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.080 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.060 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.063 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.151 → **beneficial**
- ks_cancel v4 (controller_auto) dims=['voice'] engageΔ=+0.004 didΔ=+0.000 → **neutral**
- nw_renewal v5 (controller_approved) dims=['voice'] engageΔ=+0.002 didΔ=+0.000 → **neutral**
- nw_renewal v6 (controller_approved) dims=['voice'] engageΔ=-0.003 didΔ=+0.000 → **neutral**
- nw_kyc v4 (controller_approved) dims=['cohorts', 'caller_id', 'schedule'] engageΔ=+0.000 didΔ=+0.064 → **beneficial**
- nw_renewal v7 (controller_approved) dims=['welcome_message'] engageΔ=+0.079 didΔ=+0.000 → **beneficial**
- nw_renewal v8 (controller_approved) dims=['voice'] engageΔ=+0.000 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 13,
  "decisions": {
    "approved": 11,
    "rejected": 2,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 2
  },
  "applied_via_approval": 11,
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
    "3": 0.857,
    "4": 0.85,
    "5": 0.426,
    "6": 0.0,
    "7": 0.0
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0