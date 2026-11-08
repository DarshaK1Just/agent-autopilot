# Controller runbook

## Run
```bash
pip install -r requirements.txt                      # numpy, httpx (+ sim deps); nothing else is needed
python -m sim serve --scenario scenarios/public_01_dev.yaml --run-dir runs/mine --force
./run.sh http://127.0.0.1:8700                      # state in ./controller_state.db (override: CONTROLLER_DB=...)
python -m pytest -q tests
scripts/determinism_check.sh                        # same audit trail under different hash seeds
scripts/run_scenario.sh 01_dev                      # serve + run + grade -> reports/public_01.md  (needs runs/base_public_<name> from `make baseline`)
.venv/bin/python scripts/crash_demo.py --kills 4    # SIGKILL/restart demo -> reports/crash_recovery.md
```
Re-running `./run.sh` against the same simulator and the same DB resumes; a DB from a different simulator world is moved aside automatically.

## Layout
| file | role |
|---|---|
| `client.py` | HTTP client; only reads are auto-retried; side-effecting calls reconcile instead of resend |
| `store.py` | SQLite schema, `tx()`, `audit()`; the only durable state |
| `ingest.py` | chunk → bounded batches → integer columns → numpy group-by → additive counters + leads + cursor in **one** transaction; leads are SQLite rows, not a resident map |
| `evidence.py`, `stats.py` | read-side queries; pure deterministic statistics (no RNG) |
| `planner.py` | welcome/voice tests (explore → promote / harm-stop / cohorts → decay watch) and caller-ID health; emits `Intent`s |
| `incidents.py` | hallucination detect → candidate → validate → propose → verify; owns credit spending |
| `governance.py` | proposal state machine, routing (approval vs auto), TTL/hours/fatigue gating, reconciliation |
| `main.py` | the loop; supervisor-edit detection and holds |
| `cli.py` | `explain`, `proposal`, `supervisor`, `health`, `log` |
| `policy.py` | every threshold |

## Data flow
One iteration: `advance (only if nothing unread) → ingest ≤4 chunks (P1) → reconcile proposals (P0) → incidents for every workflow (P0) → routine planners for ≤8 due workflows, only if no backlog (P2/P3) → metrics`. Planners emit `Intent`s; the governor merges them into one proposal built from the live config.
Planners are pure functions of (aggregates, current config, small experiment memory), so supervisor edits and restarts only change their inputs.

## Operating it
```bash
python -m controller.cli --db controller_state.db supervisor     # one screen: testing / winning / waiting on you / changed today
python -m controller.cli --db controller_state.db explain --wf nw_renewal --at "D3 14:00"
python -m controller.cli --db controller_state.db health
python -m controller.cli --db controller_state.db log --wf ks_cancel --limit 60
```
**Page on:** a proposal stuck `PLANNED` > 2h (simulator unreachable or rejecting), `incident_escalated`, `credit_skip`, ingest failing for > 30 min of wall time, process not advancing.
**Do not page on:** rejected/expired proposals (re-planned automatically), `deferred` (waiting for approver hours), supervisor edits, single failed HTTP calls (retried).

## Invariants
1. A committed cursor implies all counters through it are committed (one transaction per chunk).
2. The remote live config is authoritative; proposals are `live config + intended diff`.
3. Proposal state changes only through `Governor._move` against `TRANSITIONS` (and a DB `CHECK`); apply is attempted only from `APPROVED`.
4. Every external intent has a deterministic id and a recovery path; the proposal row is written before the request.
5. Experiment state advances only when its proposal is **applied**; no option (workflow or cohort) becomes a final winner without confirmation on fresh data; a promoted arm has three outcomes (keep / reopen limited exploration / roll back); rollback mirrors confirmation; severe regressions use a separate fast path.
6. One routine proposal in flight per workflow; an urgent one may go alongside only on disjoint dimensions (overlap supersedes the routine one); one urgent at a time.
7. Customer-facing changes never auto-apply unless protective.
8. Incidents and reconciliation run every iteration, including under backlog; routine planning pauses while evidence is incomplete.
9. State from a different simulator world is archived, never reused. No randomness anywhere: the audit trail is identical across hash seeds.

## Known sharp edges
- Credits spent between the simulator charging and our commit are lost on a crash at that exact instant (the result is not retrievable).
- `lead_id → features` is held in memory (bounded by cadence window) and rebuilt from SQLite on start.

## Measurements
`scripts/bench_ingest.py` (synthetic events, not simulator runs) for ingest cost and memory at 1× and 10× shapes; `scripts/false_winner_sim.py` for the decision rule's behaviour under repeated looks; `controller.cli health` prints per-stage latency percentiles for a finished run. Numbers and plans are in `reports/performance.md`.
`scripts/policy_sim.py` runs the real planner through simulated days (false promotion, power, regression detection; `reports/policy_operating_characteristics.md`).
