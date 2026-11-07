# Grade report — public_01_dev

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.344 | +3.2% | 0.241 | +1.1% | 0.497 | +1.3% | 5% | 60 (47) |
| nw_kyc | 0.447 | +22.9% | 0.294 | +21.4% | 0.588 | -0.4% | 0% | 28 (21) |
| nw_renewal | 0.449 | +7.0% | 0.277 | +5.2% | 0.556 | +1.9% | 21% | 44 (42) |
| ALL | 0.401 | +8.8% | 0.264 | +6.4% | 0.538 | +1.6% | 10% | 132 (110) |

## Changes applied by the controller

10 applied — neutral: 2, beneficial: 8

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.017 → **beneficial**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.080 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.060 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.063 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.151 → **beneficial**
- nw_kyc v4 (controller_approved) dims=['cohorts', 'schedule'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- nw_kyc v5 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.086 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nw_renewal v5 (controller_approved) dims=['welcome_message'] engageΔ=+0.079 didΔ=+0.000 → **beneficial**

## Governance

```
{
  "approval_requests": 9,
  "decisions": {
    "approved": 9,
    "expired": 0
  },
  "rejection_reasons": {},
  "applied_via_approval": 9,
  "auto_applied": 1,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nw_renewal": 1,
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
    "3": 0.842,
    "4": 0.85,
    "5": 0.851,
    "6": 0.848,
    "7": 0.09
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0