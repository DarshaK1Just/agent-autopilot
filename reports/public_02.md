# Grade report — public_02_incidents

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.348 | +40.4% | 0.233 | +26.6% | 0.511 | +7.2% | 41% | 104 (330) |
| nw_kyc | 0.466 | +24.2% | 0.291 | +20.2% | 0.605 | +2.2% | 0% | 37 (31) |
| nw_renewal | 0.487 | +14.2% | 0.290 | +10.9% | 0.558 | +1.9% | 14% | 68 (55) |
| ALL | 0.419 | +25.4% | 0.264 | +18.9% | 0.549 | +3.6% | 27% | 209 (416) |

## Changes applied by the controller

17 applied — beneficial: 14, neutral: 3

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.020 didΔ=+0.000 → **beneficial**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.038 didΔ=+0.026 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.043 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.034 didΔ=+0.000 → **beneficial**
- ks_cancel v3 (controller_auto) dims=['voice'] engageΔ=+0.001 didΔ=+0.000 → **neutral**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.078 → **beneficial**
- nw_renewal v5 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.011 → **neutral**
- ks_cancel v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.472 → **beneficial**
- nw_renewal v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.051 didΔ=+0.000 → **beneficial**
- ks_cancel v6 (controller_approved) dims=['prompt_version'] engageΔ=+0.102 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.223 → **beneficial**
- ks_cancel v7 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.267 → **beneficial**
- nw_kyc v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- nw_renewal v7 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.093 didΔ=+0.011 → **beneficial**
- ks_cancel v8 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.108 → **beneficial**
- ks_cancel v9 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.097 → **beneficial**
- ks_cancel v10 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.135 → **beneficial**

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
    "ks_cancel": 2,
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
      "3": 0.033,
      "4": 0.033,
      "5": 0.03,
      "6": 0.033,
      "7": 0.029,
      "8": 0.031,
      "9": 0.03
    }
  },
  {
    "type": "supervisor_edit",
    "workflow": "ks_cancel",
    "at": "D3 11:30",
    "mttr_minutes": 270,
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
    "3": 0.848,
    "4": 0.847,
    "5": 0.319,
    "6": 0.0,
    "7": 0.0,
    "8": 0.0,
    "9": 0.0
  }
}
```

Credits used: 5 · validation runs: 1 · LLM fix calls: 0