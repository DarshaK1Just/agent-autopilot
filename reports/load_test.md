# public_03_load — load-test summary

Full latency model, memory model, query plans, scaling model and performance budgets: [`performance.md`](performance.md). This file is the headline result of the official simulator run.

Method: `scripts/run_scenario.sh 03_load 8703` — simulator and controller on one 16-core / 54 GB dev box, controller measured with `/usr/bin/time -v`, fresh DB, includes the 7-day history bootstrap. Ingest rates vary by roughly ±10% between runs.

| metric | value |
|---|---|
| scenario | 12 workflows, 7 history days + 5 live days, ~840k events/day live |
| wall clock, whole run (simulator generating events concurrently) | **3 min 32 s** (≈ 43 s per live simulated day; budget was 10 min) |
| events ingested | 9.74 M (5.54 M history bootstrap + 4.20 M live) |
| ingest rate | mean 71.7k events/s of ingest time (p50 70.9k, max 139k) |
| decision path per step (governance + incident + planning) | mean 0.06 s, p95 0.12 s, p99 0.17 s, max 0.18 s |
| ingestion per step | mean 0.40 s, p95 0.88 s, p99 12.2 s, max 17.5 s (steps that read four chunks) |
| peak resident memory (controller) | **345 MB** (previous design: 483 MB) |
| SQLite size | 99.5 MB after 12 simulated days |
| HTTP errors / retries | 0 / 0 |
| backlog high-water | 19 chunks (history bootstrap), drained in 5 iterations |
| outcome vs baseline | conclusion rate +16.2%; 40 changes: 33 beneficial, 7 neutral, 0 harmful |

Where it breaks at 10× and the shard-by-workflow path are in `performance.md` §7; the synthetic 10× ingest benchmark (`scripts/bench_ingest.py`, labelled synthetic) is in §3.
