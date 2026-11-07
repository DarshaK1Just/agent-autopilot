# public_03_load — load-test numbers

Method: `scripts/run_scenario.sh 03_load 8703` (simulator and controller on the same 16-core/54 GB dev box, controller measured with `/usr/bin/time -v`; a fresh DB each run; includes the 7-day history bootstrap). Reproducible; numbers below are from the final commit.

| metric | value |
|---|---|
| scenario | 12 workflows, 7 history days + 5 live days, ~840k events/day live |
| wall clock, whole run (history + 5 live days, simulator generating events concurrently) | **3 min 48 s** (≈ 46 s per live simulated day, vs. the 10 min budget) |
| events ingested | 9.74 M (5.54 M history in one bootstrap, 4.20 M live) |
| ingest throughput, history bootstrap | 62 k events/s (5.54 M in 89.7 s) |
| ingest throughput, live chunks | 74 k events/s mean (4.20 M in 56.6 s, 171 chunks) |
| decision lag per step (chunk available → evaluated all 12 workflows) | mean 0.26 s, p95 0.85 s, max 3.7 s (a step that ingests most of a day) |
| peak resident memory (controller) | 482 MB |
| state size | 95 MB SQLite (WAL) after 12 days × 12 workflows |
| HTTP errors / retries | 0 |
| outcome vs baseline | +17.8% conclusion rate, 40 changes applied: 31 beneficial, 9 neutral, 0 harmful |

Where it breaks at 10×:
1. **Memory first**: the live `lead_id → features` map (~770 k leads now, ~7.7 M at 10×, ≈ 4–5 GB) — shard workflows across processes (each owns a DB and a lead map) or move the map to a compact on-disk/numpy index.
2. **Aggregate growth**: `agg` is ~8 MB/day for 12 workflows; at 10× roll 6-hour blocks older than 7 days into daily rows.
3. **Planner cost**: ~0.2 s/step for 12 workflows; hundreds of workflows need per-workflow evaluation scheduling (already staggered by `eval_interval_minutes`) and a worker pool.
4. Raw ingest is not the constraint: production load is ~100–200 events/s at 10×, three orders of magnitude below the 74 k/s measured; the single SQLite writer is fine until the sharding above.
