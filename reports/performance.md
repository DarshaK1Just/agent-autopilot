# Performance, latency and scaling

All numbers are measured on one 16-core / 54 GB dev box (simulator and controller on the same machine), Python 3.10, SQLite WAL. "Public" = official simulator run of `public_03_load`. "Synthetic" = `scripts/bench_ingest.py` (generated events through a fake client; **not** comparable with the public numbers). Three kinds of latency are kept apart: *compute* (what the controller controls), *system* (HTTP round trips, polling granularity) and *governance* (human approvers).

## 1. Critical path, public_03 (final commit, `controller.cli health`)
One loop iteration = one simulated step (15 or 60 simulated minutes). 354 steps, 169 of which ingested data.

| stage | mean | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|---:|
| `T_fetch` (HTTP stream of a chunk, per ingesting step) | 0.06 s | 0.03 | 0.10 | 0.88 | 1.08 |
| `T_decode` (JSON) | 0.20 s | 0.05 | 0.43 | 4.33 | 4.50 |
| `T_transform` (field extraction, interning) | 0.09 s | 0.02 | 0.29 | 1.59 | 1.65 |
| `T_aggregate` (numpy group-by) | 0.03 s | 0.01 | 0.04 | 0.61 | 0.63 |
| `T_db` (lead insert/lookup, counter upsert, commit) | 0.10 s | 0.03 | 0.22 | 1.78 | 1.96 |
| **ingestion, whole step** | 0.29 s | 0.01 | 0.56 | 8.6 | 14.4 |
| `T_governance` (reconcile: poll approvals, apply) | 0.03 s | 0.03 | 0.06 | 0.09 | 0.12 |
| `T_incident` (all workflows, every step) | 0.001 s | 0.001 | 0.002 | 0.003 | 0.005 |
| `T_planning` (routine planners, ≤8 workflows) | 0.005 s | 0.000 | 0.02 | 0.05 | 0.11 |
| **decision path (governance + incident + planning)** | **0.04 s** | **0.03** | **0.07** | **0.10** | **0.14** |

Reading it: ingestion is bursty (a step that finds a day's worth of chunks costs seconds; most steps cost milliseconds). The decision path never exceeds 0.2 s and does not grow with ingest volume, because it reads counters, not events. `T_external` (the HTTP round trips for polling approvals, proposals and applies) is inside `T_governance` and is loopback-fast here; on a real network it would be the dominant term, bounded by the client's timeouts (connect 5 s, read 120 s) and at most 5 retries for reads only.
Where the time goes inside ingestion (summed over the run, 86.1 s of the 92.5 s spent ingesting; the rest is chunk listing and bookkeeping): JSON decode 42%, SQLite 21%, transform 18%, fetch 12%, numpy aggregation 6%.

## 2. Throughput and memory, public_03
| metric | value |
|---|---|
| events ingested | 9.74 M (5.54 M history bootstrap + 4.20 M live) |
| wall clock, whole run | 2 min 47 s |
| ingest rate (events per second of ingest time) | mean 94.3k, p50 95.1k, max 178k |
| peak RSS | 345 MB (previous design: 483 MB) |
| RSS at steady state | ≈ 250–300 MB, flat across the run |
| SQLite size | 99.5 MB after 12 simulated days × 12 workflows |
| HTTP errors / retries | 0 / 0 |
| backlog high-water | 19 chunks (the history bootstrap), drained 4 chunks per tick |

## 3. Memory model and the 10× question (synthetic, `scripts/bench_ingest.py`)
Before: a Python dict `lead_id → feature` held every live lead (**128 bytes per lead**, measured: 98 MB for 768 k leads), was rebuilt from SQLite at start-up and scanned by `affected_leads`. After: leads live only in SQLite (≈67 bytes per lead on disk including the day index), and each batch looks up the lead ids it needs with `IN (…)` queries (0.13 s per 100 k ids).

| synthetic run | version | events | ingest rate | RSS after ingest | note |
|---|---|---:|---:|---:|---|
| 12 workflows × 2 days (public_03 shape) | before (`1b4e3a1`) | 1.54 M | 106 k/s | 357 MB | |
| | after | 1.54 M | 113 k/s | **138 MB** | RSS identical after day 1 and day 2: no growth with event count |
| 120 workflows × 1 day (≈10×) | before | 7.68 M | 67 k/s | 1125 MB | |
| | after | 7.68 M | 87 k/s | **287 MB** | 1.92 M live leads, DB 90 MB |

Memory therefore tracks the working set (one 60 k-event batch) and not the number of leads or events: ≈ 0 bytes of heap growth per million events at steady state; the 10× run needs about 1 GB less than the dict design would. The `hr` table (five extra group-bys per batch, nothing reading it since the call-time planner was removed) was deleted, which is most of the speed-up.

## 4. NumPy, measured end to end
numpy is already a dependency of the simulator. The grouping step is ≈ 3.7× faster than the equivalent pure-Python counters (0.24 s vs 0.89 s per 200 k events, and the pure version had not yet summed connected/engaged). In the 12-workflow synthetic run, aggregate is 0.9 s of 13.6 s, so replacing it would cost about **15% more ingest time** end to end — not a 4× controller speed-up. Kept because it is small and already available; JSON decoding (43% of ingest) is the real cost and is **not** worth a third-party library at 70 k events/s against a required ~10–20 events/s.

## 5. Database hot path
* One transaction per chunk: counters (`agg`, `qa`), new leads, queued control events, `cur_*` cursor and `last_event_id` commit together. Nothing is committed per event.
* WAL, `synchronous=NORMAL`: a process crash cannot corrupt or tear a commit; a power failure can lose the last commit but not consistency (the cursor then replays that chunk).
* `EXPLAIN QUERY PLAN` on the load DB (4,910 `agg` rows for the workflow, 102 matching):

| query | plan | time |
|---|---|---:|
| evidence per arm (`arm_counts`) | `SEARCH agg USING INDEX agg_scan (wf, dim, sl, sv)` | 0.08 ms |
| same, planner's own choice without `INDEXED BY` | `SEARCH agg USING PRIMARY KEY (wf=?)` — grows with history | 0.25 ms |
| history baseline | `SEARCH agg USING PRIMARY KEY (wf, blk<)` | 0.05 ms |
| hallucination rate | `SEARCH qa USING PRIMARY KEY (wf)` | 0.01 ms |
| lead features for a batch | `SEARCH leads USING PRIMARY KEY (lead_id)` | ~1.3 µs / id |
| open proposals | `SEARCH proposals USING INDEX prop_state` (was `SCAN proposals`) | <0.01 ms |
| proposal / workflow audit | `audit_prop` / `audit_wf` indexes | <0.01 ms |

SQLite does not pick `agg_scan` on its own without `ANALYZE` statistics, so the one hot evidence query pins it with `INDEXED BY`.

## 6. Work budgets, priority and backpressure
Each loop iteration runs in this order, with explicit bounds:
1. **P1 ingestion** — at most `max_chunks_per_tick` = 4 chunks (≈ 1 M events, ≈ 14 s at the measured rate). The simulator is not advanced while any chunk is unread.
2. **P0 reconcile** — poll/apply pending approvals, abandon stale ones (always runs).
3. **P0 incidents** — detection, verification, fix proposals for every workflow (always runs, ~2 ms).
4. **P2/P3 routine planning** — only when the backlog is zero, at most `max_routine_evals_per_tick` = 8 workflows, oldest-due first.
If events arrive faster than they are processed, the backlog is the number of unread chunks; it is drained 4 chunks per iteration, memory stays at one batch, nothing is dropped (the cursor only advances on commit), routine optimisation pauses and safety work continues. Measured: the 19-chunk history backlog drained in 5 iterations.

## 7. Scaling model
| | current (12 workflows) | 10× (120 workflows) | 100× (conceptual) |
|---|---|---|---|
| events/day | 0.84 M | 8.4 M | 84 M |
| real-time ingest need | ~10 events/s average | ~100 | ~1,000 |
| ingest cost per simulated day (measured/derived) | 11 s | 97 s (synthetic 88 s) | ~16 min, one core |
| heap | ~300 MB | ~300 MB (batch-bound) | ~300 MB per worker |
| SQLite | 100 MB / 12 days | ~1 GB / 12 days (leads dominate; pruned after the cadence window) | per shard |
| decision path | 0.04 s / step | ~0.4 s / step (linear in workflows; routine planning is capped at 8 workflows per step) | per shard |
| what limits it | nothing | single-writer SQLite and one core for decode | needs sharding |
Migration path: `workflow_id → shard`. Everything stored is keyed by workflow, so a worker owning a set of workflows needs only its own SQLite file, its own cursor over the event stream filtered to its workflows, and read access to the shared items below. Global state is explicit and small: the simulator's `/sim/state` credit balance (spent only inside `incidents.py`), the world key, the event cursor (would become one cursor per shard) and the approver request counts (derived per workflow from `proposals`). Not built: Kafka, a work queue or distributed workers. At the assignment's scale they add failure modes without removing a bottleneck.

## 8. Performance budgets (derived from the required scale)
| budget | target | measured |
|---|---|---|
| sustained ingest | ≥ 5,000 events/s (≥ 250× the peak real-time need of ~20 events/s) | 94k/s |
| decision path per step, p99 | < 1 s (decisions are acted on at 15-minute granularity) | 0.10 s |
| one tick's ingest, max | < 30 s (bounded by `max_chunks_per_tick`) | 14.4 s |
| RSS | < 1 GB on the 8 GB evaluator box | 345 MB peak |
| DB growth | < 15 MB per simulated day at 12 workflows | ~8 MB/day |
| backlog recovery | ≥ 1 M events per iteration | 1 M |

## 9. Incident latency, decomposed (public_02, ks_cancel)
| segment | time | who controls it |
|---|---|---|
| supervisor ships the bad prompt → incident opened | 195 min (11:30 → 14:45) | statistics: needs ≥150 connected calls, p < 0.001 and two looks 45 min apart |
| candidate choice + validation (one 500-conversation run) | < 1 min (same step) | controller |
| proposal sent → approver decision | ~40 min | policy (approver latency 20–120 min, hours 10–19) |
| decision → applied | ≤ 15 min | polling granularity (15 simulated minutes while anything is pending) |
| applied → verified | 3 h | verification sample size (not part of MTTR) |
MTTR (grader) 240 min, of which the controller owns detection (shortenable only by weakening the false-positive guard) and the ≤15-minute apply step. Prompt changes cannot be auto-applied under any public policy (`allowed_dims` never contains `prompt_version`), so the approver wait is not reducible.
