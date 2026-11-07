# Grade report — public_02_incidents

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.322 | +30.1% | 0.222 | +20.5% | 0.506 | +6.2% | 38% | 86 (330) |
| nw_kyc | 0.463 | +23.6% | 0.295 | +21.8% | 0.594 | +0.3% | 0% | 29 (31) |
| nw_renewal | 0.481 | +12.8% | 0.289 | +10.5% | 0.555 | +1.2% | 22% | 64 (55) |
| ALL | 0.405 | +21.2% | 0.259 | +16.7% | 0.544 | +2.7% | 28% | 179 (416) |

## Changes applied by the controller

15 applied — beneficial: 13, neutral: 2

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.020 didΔ=+0.000 → **beneficial**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.038 didΔ=+0.025 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.056 → **beneficial**
- nw_kyc v2 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.074 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['cohorts', 'voice'] engageΔ=-0.003 didΔ=+0.000 → **neutral**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.087 didΔ=+0.000 → **beneficial**
- ks_cancel v4 (controller_approved) dims=['voice', 'caller_id'] engageΔ=-0.003 didΔ=+0.473 → **beneficial**
- ks_cancel v6 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.091 → **beneficial**
- nw_renewal v5 (controller_approved) dims=['voice'] engageΔ=+0.021 didΔ=+0.000 → **beneficial**
- ks_cancel v7 (controller_approved) dims=['prompt_version'] engageΔ=+0.102 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.216 → **beneficial**
- ks_cancel v8 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.067 → **beneficial**
- nw_renewal v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.090 didΔ=+0.000 → **beneficial**
- nw_kyc v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.058 → **beneficial**
- ks_cancel v9 (controller_approved) dims=['voice'] engageΔ=+0.003 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 18,
  "decisions": {
    "approved": 14,
    "rejected": 4,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 4
  },
  "applied_via_approval": 14,
  "auto_applied": 1,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nw_renewal": 2,
    "nw_kyc": 1,
    "ks_cancel": 3
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
      "2": 0.385,
      "3": 0.033,
      "4": 0.031,
      "5": 0.034,
      "6": 0.032,
      "7": 0.032,
      "8": 0.03,
      "9": 0.032
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
    "2": 0.698,
    "3": 0.857,
    "4": 0.333,
    "5": 0.0,
    "6": 0.0,
    "7": 0.0,
    "8": 0.0,
    "9": 0.0
  }
}
```

Credits used: 5 · validation runs: 1 · LLM fix calls: 0