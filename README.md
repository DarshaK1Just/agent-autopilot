# Voice Agent Autopilot

An autonomous controller that tunes outbound voice agents for insurers and lenders, and earns the right to do it: it runs controlled experiments on live traffic, asks a human to approve anything a customer can hear, applies changes safely, and backs out when something stops working. Every change can be explained from its audit record.

> Built as a response to the *Outcome-First Agent Loop* brief ([docs/ASSIGNMENT.md](docs/ASSIGNMENT.md)). Design write-up: [SUBMISSION.md](SUBMISSION.md).

## The problem
A voice-agent workflow is configured once (welcome message, voice, caller ID, prompt version, call hours) and rarely revisited. Two rates matter and are never blended: **pickup** (connected / dials) and **engagement** (engaged / connected). The business outcome is **leads concluded / leads uploaded**. Hand-tuning is slow and nobody can say which setting helped.

## What it does
| Job | How |
|---|---|
| Find better options | Randomised welcome/voice tests, one Bayesian rule, contrasts stratified by config version and cohort so allocation changes cannot fool it |
| Avoid false wins | A first-look winner is only *provisional*; it must be confirmed on fresh data before it is promoted, and a small holdout keeps watching it afterwards |
| Back out | Rolls back a winner that turns harmful; reopens limited exploration when a winner goes neutral; stops a harmful arm outright |
| Protect callers | Learns caller-ID health, parks degraded IDs, keeps a probe share on unmeasured ones |
| Handle incidents | Detects hallucination spikes, reverts to the last good prompt, otherwise asks the LLM for *candidates* and validates each one before use |
| Stay governed | Customer-facing changes go to a human approver; every request has a stable id, a diff, a dry run and a reason; supervisor edits always win |

## How it runs
```
simulator ──events──▶ ingest ──▶ SQLite counters (one transaction per chunk)
                                      │
   incidents (P0) ─▶ governance ◀── planner (experiments, decay, caller ID)
                         │
                 approvals / apply  ──▶ simulator
```
One process, one SQLite file, deterministic decisions. It survives being killed: counters and cursor commit together, proposals are written before they are sent, and on restart the simulator is the source of truth for config and approvals.

## Quick start
```bash
pip install -r requirements.txt
python -m sim serve --scenario scenarios/public_01_dev.yaml --run-dir runs/demo --port 8700 &
./run.sh http://127.0.0.1:8700          # runs until the scenario finishes; state in controller_state.db
python -m controller.cli --db controller_state.db health      # latency, throughput, open proposals, alerts
python -m controller.cli --db controller_state.db log --limit 20   # audit trail: what changed and why
python -m pytest -q tests
```
`scripts/run_scenario.sh 01_dev` serves, runs and grades a public scenario in one command. `scripts/crash_demo.py --kills 4` kills the controller mid-run and checks that nothing is duplicated or lost.

## Results (public scenarios, against a do-nothing baseline)
| Scenario | Conclusion rate | Changes applied | Harmful | Notes |
|---|---|---|---|---|
| public_01 (dev) | +9.0% | 8 | 0 | |
| public_02 (incidents) | +25.4% | 17 | 0 | hallucinated calls 416 → 209 |
| public_03 (load) | +16.5% | 48 | 0 | 2 min 40 s, 346 MB peak, ~94k events/s |

Public scenarios are regression tests only; no threshold was tuned to their scores. Reports: [reports/](reports/).

## Limits, stated plainly
At about 1,000 connected calls/day the controller needs roughly 12 days to notice a neutral winner and confirm a better one, so on short horizons it deliberately does nothing rather than guess. The arithmetic is in [reports/final_audit.md](reports/final_audit.md); the remedies I tried and rejected are in [reports/low_volume_experiments.md](reports/low_volume_experiments.md).

## Layout
`controller/` planner, governance, incidents, ingest, store · `tests/` 156 tests including adversarial and crash cases · `scripts/` policy simulation, crash demo, benchmarks · `reports/` measured results · `docs/` simulator contract and controller notes · `sim/` the provided simulator (unchanged)
