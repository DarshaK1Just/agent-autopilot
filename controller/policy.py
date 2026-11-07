"""All tunable thresholds in one place so the audit trail can cite them and reviews can change them."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Policy:
    # --- experiments
    explore_control_share: float = 0.4     # incumbent keeps >= 40% while arms are explored
    human_incumbent_share: float = 0.7     # when a supervisor chose the incumbent, challengers get at most 30% in total
    holdout_share: float = 0.15            # promoted winner keeps this much on the incumbent for decay detection
    min_trials_arm: int = 250              # KPI denominators per arm before any verdict
    min_trials_slice: int = 200
    rel_min_lift: float = 0.03             # practical significance: >= 3% relative
    rel_harm: float = 0.02                 # arm is harmful if credibly worse than control by 2% relative
    family_alpha: float = 0.07             # familywise error budget across challenger arms (Sidak)
    slice_confidence: float = 0.975        # posterior probability for slice-level wins (after EB shrinkage)
    harm_confidence: float = 0.95
    futility_p: float = 0.10               # prune an arm when P(arm beats control) <= 10% with enough data
    het_alpha: float = 0.10                # familywise level for 'does the effect differ across slices' (Bonferroni over features x options)
    min_cohort_share: float = 0.08         # a cohort must cover >= 8% of traffic
    min_cohort_gain: float = 0.004         # and add >= 0.4pt absolute KPI to be worth a config object
    max_cohorts: int = 6
    guardrail_confidence: float = 0.80     # P(guardrail drop within tolerance) required
    decay_window_blocks: int = 6           # 36h
    decay_p: float = 0.20                  # roll back when P(winner still >= half its lift) falls below this
    decay_min_trials: int = 100
    retire_minutes: int = 3 * 1440
    # --- caller id
    did_window_blocks: int = 6
    did_min_dials: int = 200
    did_rel_drop: float = 0.15
    did_alpha: float = 0.01
    did_floor_share: float = 0.03
    did_probe_share: float = 0.08
    did_min_interval: int = 12 * 60
    # --- schedule
    sched_min_z: float = 3.0
    sched_min_gain: float = 0.015
    sched_w_lo: float = 0.35
    sched_w_hi: float = 3.0
    # --- incidents
    inc_min_conn: int = 150
    inc_min_flags: int = 5
    inc_alpha: float = 3e-3
    inc_rel: float = 2.0
    inc_val_n: int = 500
    credit_reserve: float = 60.0           # never spend the last N credits on anything but incidents
    # --- governance
    routine_earliest_hour: int = 11
    routine_max_per_day: int = 2
    incident_slots: int = 1                # per-24h request slots kept for incidents
    supervisor_hold_minutes: int = 48 * 60
    eval_interval_minutes: int = 120
