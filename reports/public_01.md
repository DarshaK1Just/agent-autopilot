# Grade report — public_01_dev

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.356 | +6.9% | 0.244 | +2.3% | 0.508 | +3.5% | 12% | 62 (47) |
| nw_kyc | 0.439 | +20.9% | 0.282 | +16.5% | 0.605 | +2.4% | 0% | 26 (21) |
| nw_renewal | 0.440 | +4.7% | 0.279 | +5.7% | 0.543 | -0.5% | 6% | 51 (42) |
| ALL | 0.402 | +9.0% | 0.263 | +6.2% | 0.541 | +2.1% | 6% | 139 (110) |

## Changes applied by the controller

8 applied — neutral: 2, beneficial: 6

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=-0.004 didΔ=+0.000 → **neutral**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.060 didΔ=-0.017 → **beneficial**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.085 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.051 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['welcome_message'] engageΔ=+0.035 didΔ=+0.000 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.024 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.207 → **beneficial**
- nw_renewal v5 (controller_approved) dims=['welcome_message'] engageΔ=-0.004 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 7,
  "decisions": {
    "approved": 7,
    "expired": 0
  },
  "rejection_reasons": {},
  "applied_via_approval": 7,
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
    "3": 0.445,
    "4": 0.595,
    "5": 0.839,
    "6": 0.856,
    "7": 0.853
  }
}
```

Credits used: 0 · validation runs: 0 · LLM fix calls: 0