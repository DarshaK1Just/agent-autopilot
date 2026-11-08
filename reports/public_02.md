# Grade report — public_02_incidents

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.345 | +39.2% | 0.232 | +26.1% | 0.509 | +6.8% | 46% | 118 (330) |
| nw_kyc | 0.448 | +19.6% | 0.287 | +18.8% | 0.591 | -0.1% | 0% | 40 (31) |
| nw_renewal | 0.477 | +11.9% | 0.288 | +9.9% | 0.553 | +0.9% | 16% | 52 (55) |
| ALL | 0.411 | +22.9% | 0.262 | +18.0% | 0.543 | +2.5% | 30% | 210 (416) |

## Changes applied by the controller

21 applied — beneficial: 17, neutral: 3, harmful: 1

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
- ks_cancel v9 (controller_approved) dims=['welcome_message'] engageΔ=+0.016 didΔ=+0.000 → **beneficial**
- nw_renewal v8 (controller_approved) dims=['welcome_message', 'caller_id'] engageΔ=+0.093 didΔ=+0.011 → **beneficial**
- nw_kyc v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=-0.061 → **harmful**
- nw_kyc v5 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.047 → **beneficial**
- ks_cancel v10 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.142 → **beneficial**
- ks_cancel v11 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.125 → **beneficial**
- ks_cancel v12 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.051 → **beneficial**

## Governance

```
{
  "approval_requests": 22,
  "decisions": {
    "approved": 19,
    "rejected": 3,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 3
  },
  "applied_via_approval": 18,
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
      "5": 0.028,
      "6": 0.03,
      "7": 0.027,
      "8": 0.021,
      "9": 0.031
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
    "5": 0.271,
    "6": 0.0,
    "7": 0.0,
    "8": 0.0,
    "9": 0.0
  }
}
```

Credits used: 5 · validation runs: 1 · LLM fix calls: 0