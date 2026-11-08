# Final closure audit

Scope: read the final code for defects that would make the controller behave *incorrectly* (not merely conservatively) on a hidden scenario. Result: **no correctness bug found, no controller behaviour changed**. One test was added for an invariant that had none.

## 1. Ten plausible hidden failures, classified

| # | Hidden scenario | Where it would bite | Verdict | Evidence |
|---|---|---|---|---|
| 1 | Evidence from an old config regime leaks into a new decision | counts are stratified by (config version × cohort) and pooled; windows trail | NOT A BUG | `test_simpson_paradox_is_not_fooled…`, `test_fresh_promotion_is_not_demoted…` |
| 2 | Wrong denominator (engagement over dials, pickup over connects) | `evidence.kpi_of` | NOT A BUG | `test_engagement_uses_connected_not_dials` |
| 3 | Primary improves while the guardrail worsens, before or after promotion | `_cohort_candidates` gate, `_watch_decay` guardrail breach | NOT A BUG | `test_guardrail_regression_blocks_winner`, `test_guardrail_collapse_after_promotion_is_caught` |
| 4 | Approval goes stale, or a supervisor edits while a proposal is pending | `reconcile` (PENDING with an older base → ABANDONED), `STALE` on 409 | NOT A BUG | `test_stale_base_is_terminal_and_replannable`, `test_supervisor_edit_while_pending_abandons…` |
| 5 | HTTP succeeded but the response was lost (submit, auto-apply, apply) | write-ahead PLANNED row, deterministic id, reconcile by server lookup; apply retry gets `409 not_approved` and reads history | NOT A BUG | `test_crash_after_server_accepted…`, `test_apply_timeout_keeps_proposal_approved…`; apply order checked against the contract (`not_approved` is returned before the stale-base check) |
| 6 | Duplicate / replayed events | chunk skipped when its last id ≤ committed id; individual events with id ≤ committed id skipped | **ACCEPTED TRADE-OFF**: an id repeated *inside* one chunk would be counted twice. The contract says ids are strictly increasing, so this needs a broken simulator; a hole in ids is audited as `ingest_gap`. | `test_duplicate_chunk_is_idempotent` |
| 7 | Incident fix changes the prompt while an experiment is running | evidence is version-stratified; an urgent proposal supersedes a routine one on overlapping dims | NOT A BUG | `test_urgent_change_supersedes_routine…`, `test_backlog_does_not_postpone_incident_work…` |
| 8 | Common-mode degradation (every arm drops together) | contrasts are relative to the concurrent control | NOT A BUG | `test_common_mode_drop_of_every_arm…` |
| 9 | KPI near 0 or 1, tiny counts | absolute-lift floor, `min_events`, safe normal approximation | NOT A BUG | `test_rate_near_zero…`, `test_too_few_events_near_zero_or_one…`, `test_statistics_are_numerically_safe…` |
| 10 | New winner after a reopen / neutral incumbent at low volume | see §2 | **INFORMATION LIMIT** | `reports/low_volume_experiments.md` |

Also noted, not defects: a lost credit result is detected but not recoverable (the simulator charged, we never saw it); one process on one SQLite file loses local memory if the disk is lost (the simulator stays authoritative for config); a normal-approximation posterior is used for large-sample rates.

## 2. The low-volume limit, in plain numbers

Setup (from the code): after a reopen the incumbent keeps 70% and three challengers share 30%, i.e. 10% of connected calls each. A challenger needs at least 250 trials, and its first look must clear P ≥ 0.983 (Bonferroni over three challengers); a fresh-data confirmation then needs P ≥ 0.90. Engagement ≈ 0.54, so one trial has a standard deviation of about 0.5.

Trials needed per challenger (first look + confirmation) and the days that takes:

| connected calls/day | challenger gets | +10% relative (≈ +5 pts) | +15% relative (≈ +8 pts) |
|---|---|---|---|
| 300 | 30/day | ~440 + ~160 trials = 20 days | ~250 + ~70 = 11 days |
| 1,000 | 100/day | ~440 + ~160 = 6 days | ~250 + ~70 = 3.2 days |
| 4,000 | 400/day | ~440 + ~160 = 1.5 days | ~250 + ~70 = 0.8 days |

Before any of that, the controller has to *notice* that the promoted winner stopped working. With a 15% holdout it needs ~800 holdout trials: 17.8 days at 300/day, 5.3 days at 1,000/day, 1.3 days at 4,000/day.

So at 1,000/day, a winner that goes neutral on day 4 is recognised at about day 9, and a +15% successor is then confirmed about 3 days later: roughly 12 days from the change, against an 8-day scenario. The policy simulation agrees (new winner found in 1% of 8-day runs, 53% of 14-day runs). At 300/day even the first challenger cannot finish inside a typical horizon, so the controller declines to experiment.

The only ways to shorten this are to put more traffic on fewer arms (measured: more harmful changes and approvals, `reports/low_volume_experiments.md`), to lower the evidence bar (more false actions), or to borrow information from other workflows (out of scope). I chose not to.

## 3. Invariants and where they are enforced / tested

| Invariant | Enforced by | Test |
|---|---|---|
| committed cursor ⇒ matching counters committed | one `store.tx()` per chunk covers counters, leads and cursor | `test_crash_mid_chunk_rolls_back_and_restart_resumes` |
| replay cannot double-count | chunk skip + per-event id filter | `test_duplicate_chunk_is_idempotent` |
| no stale proposal applies blindly | `base_version` check in `reconcile`, 409 → STALE | `test_stale_base_is_terminal_and_replannable` |
| remote config is authoritative | each planning pass starts from the config fetched from the simulator; local state is only the experiment memory | `test_supervisor_edit_resets_only_the_scopes_that_predate_it`, `test_patch_preserves_supervisor_edit_and_counts_shift` |
| supervisor changes are preserved | patches change only the dimensions the controller owns | `test_patch_preserves_supervisor_edit…` |
| terminal proposals cannot apply | `TRANSITIONS` + DB `CHECK` | `test_state_machine_rejects_illegal_moves`, `test_rejected_or_expired_proposal_is_never_applied`, `test_random_interleavings_never_break_the_governance_invariants` |
| every side effect has a stable id and reconciliation | `wf-v<base>-<hash>` ids, PLANNED written before any request | `test_deterministic_proposal_id_and_no_second_inflight`, `test_crash_after_server_accepted…` |
| no final winner without confirmation | EXPLORING → CONFIRMING → PROMOTED | `test_provisional_winner_is_confirmed_only_by_fresh_data`, `test_first_look_winner_gets_a_provisional_split…` |
| guardrail checked before and after promotion | candidate gate + decay watch | see row 3 above |
| incident safety outranks routine work | `safety()` runs every iteration before planning; urgent uses best-case approver latency | `test_backlog_does_not_postpone_incident_work…`, `test_urgent_fix_is_sent_when_the_fastest_approver…` |
| applied changes are reconstructable from local state | APPLIED row + `proposal_applied` audit row + stored body | **`test_every_applied_change_can_be_reconstructed_from_local_state_alone` (added now)** |
| decisions are deterministic | sorted float sums, no wall clock in decisions | `test_decisions_are_deterministic`, `scripts/determinism_check.sh` |

## 4. Performance freeze (public_03, the load scenario)

| measure | value |
|---|---|
| wall time | 2:42 |
| peak RSS | 346 MB (sampled 308 MB) |
| ingest throughput | mean 94k events/s, p95 108k |
| decision lag p99 | 0.096 s (max 0.117 s) |
| backlog | peaked at 19 chunks, back to 0 |
| DB size | 100 MB (72 MB file at rest after the run) |
| HTTP errors / retries | 0 / 0 |

Within assignment scale; no further optimisation attempted.
