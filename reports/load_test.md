# public_03_load — load-test numbers

Method: `scripts/run_scenario.sh 03_load 8703` — simulator and controller on one 16-core / 54 GB dev box, controller measured with `/usr/bin/time -v`, fresh DB, includes the 7-day history bootstrap. Numbers are from the final commit; ingest rates vary by roughly ±10% between runs.

| metric | value |
|---|---|
| scenario | 12 workflows, 7 history days + 5 live days, ~840k events/day live |
| wall clock, whole run (simulator generating events concurrently) | **4 min 09 s** (about 50 s per live simulated day; budget was 10 min) |
| events ingested | 9.74 M (5.54 M history bootstrap + 4.20 M live) |
| ingest rate | 62.5k events/s (history), 63.5k events/s (live chunks) |
| decision lag per step (chunk available → all 12 workflows evaluated) | mean 0.33 s, p95 0.94 s, max 6.6 s (a step that ingests most of a day) |
| peak resident memory (controller) | 483 MB |
| SQLite size after 12 simulated days | 95 MB |
| HTTP errors | 0 |
| outcome vs baseline | conclusion rate +16.7%; 39 changes: 32 beneficial, 6 neutral, 1 harmful |

Profile of ingest (200k synthetic events): JSON parsing 41%, field extraction 23%, numpy grouping 7%, SQLite upsert and the rest 29%. A pure-Python marginal counter was 0.89 s versus 0.24 s for the grouping step alone.

Where it breaks at 10×:
1. Memory: the live `lead_id → features` map (~770k entries now, ~7.7M at 10×, 4–5 GB). Shard workflows across workers, each with its own DB and map.
2. `agg` growth (~8 MB per simulated day for 12 workflows): roll 6-hour blocks older than a week into day rows.
3. Planner time for hundreds of workflows (about 0.2 s per step for 12): stagger and spread across workers.
Raw ingest is not the limit. Production at 10× is roughly 100–200 events/s, far below what was measured.
