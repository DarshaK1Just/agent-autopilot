# Grade report — public_02_incidents

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.328 | +32.5% | 0.223 | +21.5% | 0.505 | +6.0% | 45% | 117 (330) |
| nw_kyc | 0.449 | +19.8% | 0.286 | +18.3% | 0.594 | +0.4% | 0% | 31 (31) |
| nw_renewal | 0.476 | +11.6% | 0.284 | +8.6% | 0.558 | +1.9% | 13% | 54 (55) |
| ALL | 0.403 | +20.6% | 0.257 | +15.6% | 0.545 | +2.8% | 29% | 202 (416) |

## Changes applied by the controller

17 applied — beneficial: 13, neutral: 3, harmful: 1

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.020 didΔ=+0.000 → **beneficial**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.038 didΔ=+0.026 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.043 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.034 didΔ=+0.000 → **beneficial**
- ks_cancel v3 (controller_auto) dims=['voice'] engageΔ=+0.001 didΔ=+0.000 → **neutral**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.078 → **beneficial**
- nw_renewal v5 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.011 → **neutral**
- ks_cancel v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.472 → **beneficial**
- nw_renewal v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.051 didΔ=+0.000 → **beneficial**
- ks_cancel v5 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.009 didΔ=+0.000 → **neutral**
- ks_cancel v7 (controller_approved) dims=['prompt_version'] engageΔ=+0.102 didΔ=+0.000 → **beneficial**
- nw_renewal v7 (controller_approved) dims=['voice'] engageΔ=+0.016 didΔ=+0.000 → **beneficial**
- ks_cancel v8 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.308 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.207 → **beneficial**
- nw_renewal v8 (controller_approved) dims=['welcome_message'] engageΔ=+0.093 didΔ=+0.000 → **beneficial**
- ks_cancel v9 (controller_approved) dims=['welcome_message'] engageΔ=+0.016 didΔ=+0.000 → **beneficial**
- nw_renewal v10 (controller_approved) dims=['welcome_message'] engageΔ=-0.030 didΔ=+0.000 → **harmful**

## Governance

```
{
  "approval_requests": 17,
  "decisions": {
    "approved": 15,
    "rejected": 2,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 2
  },
  "applied_via_approval": 14,
  "auto_applied": 3,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "ks_cancel": 4,
    "nw_kyc": 1,
    "nw_renewal": 2
  }
}
```

## Incidents

```
[
  {
    "type": "did_flagged",
    "workflow": "ks_cancel",
    "at": "D2 10:00",
    "flagged_did_share_by_day": {
      "2": 0.334,
      "3": 0.031,
      "4": 0.025,
      "5": 0.029,
      "6": 0.029,
      "7": 0.031,
      "8": 0.031,
      "9": 0.032
    }
  },
  {
    "type": "supervisor_edit",
    "workflow": "ks_cancel",
    "at": "D3 11:30",
    "mttr_minutes": 1365,
    "fixed_by": "controller_approved"
  },
  {
    "type": "supervisor_edit",
    "workflow": "nw_renewal",
    "at": "D5 15:00"
  }
]
```

## Decaying variants — share of in-population calls still on the variant, by day after onset

```
{
  "nw_renewal:welcome_message=W3": {
    "2": 0.677,
    "3": 0.847,
    "4": 0.851,
    "5": 0.09,
    "6": 0.0,
    "7": 0.0,
    "8": 0.267,
    "9": 0.304
  }
}
```

Credits used: 5 · validation runs: 1 · LLM fix calls: 0