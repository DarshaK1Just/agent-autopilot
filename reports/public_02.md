# Grade report — public_02_incidents

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.339 | +36.9% | 0.232 | +26.0% | 0.506 | +6.2% | 42% | 111 (330) |
| nw_kyc | 0.476 | +27.1% | 0.298 | +23.0% | 0.604 | +2.0% | 0% | 33 (31) |
| nw_renewal | 0.482 | +13.1% | 0.284 | +8.6% | 0.565 | +3.2% | 30% | 56 (55) |
| ALL | 0.416 | +24.4% | 0.263 | +18.3% | 0.550 | +3.7% | 33% | 200 (416) |

## Changes applied by the controller

17 applied — beneficial: 14, neutral: 3

- ks_cancel v2 (controller_approved) dims=['welcome_message', 'voice'] engageΔ=+0.020 didΔ=+0.000 → **beneficial**
- nw_renewal v2 (controller_approved) dims=['welcome_message', 'voice', 'caller_id'] engageΔ=+0.038 didΔ=+0.025 → **beneficial**
- nw_renewal v3 (controller_auto) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.056 → **beneficial**
- ks_cancel v3 (controller_approved) dims=['voice'] engageΔ=-0.005 didΔ=+0.000 → **neutral**
- nw_kyc v2 (controller_approved) dims=['cohorts', 'caller_id', 'schedule'] engageΔ=+0.000 didΔ=+0.053 → **beneficial**
- nw_renewal v4 (controller_approved) dims=['welcome_message'] engageΔ=+0.092 didΔ=+0.000 → **beneficial**
- nw_kyc v3 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.187 → **beneficial**
- ks_cancel v4 (controller_approved) dims=['voice', 'caller_id'] engageΔ=+0.004 didΔ=+0.471 → **beneficial**
- nw_renewal v5 (controller_approved) dims=['voice'] engageΔ=+0.021 didΔ=+0.000 → **beneficial**
- ks_cancel v6 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.103 → **beneficial**
- nw_kyc v4 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.067 → **beneficial**
- ks_cancel v7 (controller_approved) dims=['prompt_version'] engageΔ=+0.102 didΔ=+0.000 → **beneficial**
- nw_renewal v6 (controller_approved) dims=['welcome_message'] engageΔ=+0.070 didΔ=+0.000 → **beneficial**
- ks_cancel v8 (controller_approved) dims=['cohorts', 'welcome_message'] engageΔ=+0.026 didΔ=+0.000 → **beneficial**
- ks_cancel v9 (controller_approved) dims=['caller_id'] engageΔ=+0.000 didΔ=+0.034 → **beneficial**
- nw_renewal v8 (controller_approved) dims=['welcome_message'] engageΔ=+0.000 didΔ=+0.000 → **neutral**
- ks_cancel v10 (controller_approved) dims=['welcome_message'] engageΔ=+0.000 didΔ=+0.000 → **neutral**

## Governance

```
{
  "approval_requests": 20,
  "decisions": {
    "approved": 17,
    "rejected": 3,
    "expired": 0
  },
  "rejection_reasons": {
    "approver declined (judgement call)": 3
  },
  "applied_via_approval": 16,
  "auto_applied": 1,
  "auto_apply_rejected": 0,
  "apply_conflicts": 1,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nw_renewal": 2,
    "nw_kyc": 1,
    "ks_cancel": 2
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
      "2": 0.297,
      "3": 0.029,
      "4": 0.029,
      "5": 0.032,
      "6": 0.027,
      "7": 0.029,
      "8": 0.033,
      "9": 0.03
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
    "2": 0.852,
    "3": 0.848,
    "4": 0.089,
    "5": 0.0,
    "6": 0.0,
    "7": 0.0,
    "8": 0.0,
    "9": 0.0
  }
}
```

Credits used: 5 · validation runs: 1 · LLM fix calls: 0