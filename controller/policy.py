"""Every tunable in one place. Class of each value: A = contract, B = business policy, C = derived, D = heuristic."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Policy:
    # --- experiments
    explore_control_share: float = 0.4     # D: incumbent keeps >= 40% so the control arm is never starved
    human_incumbent_share: float = 0.7     # D: a supervisor-chosen incumbent is challenged with <= 30% (prior favours a human's choice)
    holdout_share: float = 0.15            # B: promoted winner keeps 15% on the control so decay stays measurable
    min_trials_arm: int = 250              # D: keeps the normal approximation valid at p~0.5 and blocks decisions on tiny samples
    rel_min_lift: float = 0.03             # B: a customer-facing change must be worth >= 3% relative to bother an approver
    rel_harm: float = 0.02                 # B: credibly worse than control by 2% relative = harmful
    harm_confidence: float = 0.95          # C: 1 - alpha
    alpha: float = 0.05                    # C: family-wise error; Bonferroni over simultaneous comparisons
    guardrail_confidence: float = 0.80     # D: block only when there is >= 20% posterior chance the guardrail breaches its tolerance
    min_trials_slice: int = 200            # D
    min_cohort_share: float = 0.08         # D: a cohort must cover >= 8% of traffic ...
    min_cohort_gain: float = 0.004         # D: ... and add >= 0.4pt absolute KPI
    max_cohorts: int = 6                   # D
    decay_window_blocks: int = 6           # D: 36h window (6h blocks)
    decay_p: float = 0.20                  # D: roll back when P(winner still clears the practical-lift bar vs its holdout) <= 20%
    decay_min_trials: int = 100            # D
    retire_minutes: int = 3 * 1440         # D: a rolled-back option is not re-promoted for 3 days
    # --- caller id
    did_window_blocks: int = 6             # D: 36h
    did_min_dials: int = 200               # D
    did_rel_drop: float = 0.15             # B: pickup >= 15% below sibling IDs
    did_alpha: float = 0.01                # C: per-ID test, Bonferroni over IDs
    did_floor_share: float = 0.03          # B: a flagged ID keeps 3% so recovery is observable
    did_probe_share: float = 0.08          # B: untested IDs get 8% until measured
    did_min_interval: int = 12 * 60        # D: at most one caller-ID change per 12h
    # --- incidents
    inc_min_conn: int = 150                # D
    inc_min_flags: int = 5                 # D
    inc_alpha: float = 1e-3                # C: strict, because the test is repeated every step
    inc_rel: float = 2.0                   # B: and rate must be >= 2x the workflow's own baseline
    inc_val_n: int = 500                   # D: validation sample (5 credits)
    inc_max_llm_rounds: int = 2            # B: credit cap per incident
    inc_max_new_candidates: int = 3        # B
    # --- governance
    routine_earliest_hour: int = 11        # B: Kestrel memo
    routine_max_per_day: int = 2           # B: Kestrel memo
    incident_slots: int = 1                # B: one of max_requests_per_24h is kept for incidents
    supervisor_hold_minutes: int = 48 * 60 # B
    eval_interval_minutes: int = 120       # D
