# Outcome-First Agent Loop — Submission

**Name:** · **Date:** · **Hours actually spent (be honest):** · **Language / storage:**

> Copy this file to `SUBMISSION.md`. Keep the headings. Be concrete: numbers, examples, diagrams. If a
> section doesn't apply, say why in a line rather than deleting it.

---

## 0. TL;DR
__TLDR__

## 1. Assumptions
1. **Welcome message and voice act after pickup**, so they can move engagement but not pickup; only caller ID and *who is dialled when* (schedule) can move pickup. Pickup-primary workflows therefore get caller-ID and schedule work, not welcome/voice tests. Guardrail checks still measure the other KPI for every candidate.
2. **Guardrail `*_max_drop` is an absolute drop in the guardrail rate** (0.02 = two points), checked as P(drop within tolerance) ≥ 0.80.
3. **History carries no variant information**: the default config allocates one welcome message and one voice, so pre-D0 data gives baselines, hour profiles, caller-ID baselines and the hallucination base rate, never option priors.
4. A global hour-weight table is a no-op (it scales every eligible lead equally), so schedule tables only make sense per cohort.
5. Each dial's welcome/voice/caller-ID is sampled independently (per the contract), so marginal arm contrasts are unbiased even when the other dimensions vary. Contrasts are stratified by (config version × cohort) so allocation changes cannot confound them.
6. QA hallucination flags are noisy: baseline is estimated from the workflow's own pre-incident flag rate (false positives included), never assumed to be zero.
7. Validation measures safety only. Engagement after a prompt change is verified from production calls; a fix that hurts engagement is treated as a regression.
8. The approver is a black box with working hours and latency; decision time ≈ next_working(now + latency). Requests that cannot be decided inside their TTL are not sent (they would be guaranteed to expire).
9. Fatigue limit (`max_requests_per_24h`) counts every request, including rejected and expired ones; the controller keeps one slot per 24h in reserve for incidents.
10. A supervisor edit is legitimate and wins: the edited dimensions are put on a 48h hold, experiments are re-derived from the live config, in-flight proposals are left to go stale and are re-planned. The one exception is an incident fix, which is *proposed* (never forced) and explains the evidence.
11. Hidden scenarios share the public schema/ranges (≤20 cohorts, 15-minute ticks, same event types and start date). The date of D0 is read from `/sim/state`, never hard-coded.
12. Per-person call-time was not built; a person has too few calls for a defensible preferred-hour estimate in the scenario horizon.

## 2. Scope decisions
| # | Capability | Built / Partial / Cut | Why | What it would take to finish |
|---|---|---|---|---|
| C1 | Event ingestion | **Built** | Everything else depends on fresh, correct counters. Streaming NDJSON, numpy group-by, one transaction per chunk with the cursor, idempotent replay. | Partition by workflow across processes for 10×. |
| C2 | Shared cohort object | **Built** | One `cohorts` registry and one config representation used by experiments, schedule, audit and the supervisor view. Single partition axis per workflow, single-value cohorts, ids like `age_band=60+`. | Cross-axis cohorts (see §13). |
| C3 | History bootstrap | **Built (scoped)** | Baseline rates, hour profiles, caller-ID baselines and the hallucination base rate come from history. No option priors exist in history (assumption 3). | Decay-weighted priors once history contains real variation. |
| C4 | Call-time optimisation | **Partial** | Per-cohort hour weights from history, gated by significance and expected gain. Per-person cut. | Per-person preferred hour for returning persons with ≥3 connects. |
| C5 | Caller-ID health | **Built** | Concurrent sibling comparison + own-history drift, persisted bad set with floor share and re-probe, untested IDs probed at 8%. | Load-aware (dials/hour per ID) allocation. |
| C6 | Welcome/voice experiments | **Built** | Randomised multi-arm tests, Šidák over arms, minimum trials, futility pruning, harm stop, EB-shrunk slice effects with a Q heterogeneity gate. | Joint welcome×voice cells when traffic allows. |
| C7 | Promotion, decay, rollback | **Built** | 85/15 controlled promotion; winner vs. holdout over a 36h window; rollback + retirement. | Per-arm sequential tests (CUSUM) for faster decay detection. |
| C8 | Hallucination incident loop | **Built** | Detect → revert-to-last-good first (free) → LLM only if needed → validate → evidence-backed proposal → verify (flags and engagement). | Multi-incident credit arbitration. |
| C9 | Governance client | **Built** | Full state machine, deterministic ids, TTL/hours/fatigue-aware submission, batching, stale/lapse/reject handling, auto-apply rules. | — |
| C10 | Honest scores/dry runs | **Partial** | `affected_leads` from live lead table, dry runs replay recorded randomised arms, impact is a documented bounded formula. No cross-validation of the replay. | Hold-out replay on a past window. |
| C11 | Supervisor view | **Partial** | `python -m controller.cli supervisor` (one screen); no web UI. | Thin HTTP/JSON endpoint over the same query. |
| C12 | Audit store | **Built** | Every decision, evidence, route, approval transition, apply and follow-up is in SQLite; `explain` answers the "why" question. | Retention/partitioning. |
| C13 | Crash recovery | **Built** | Demonstrated with SIGKILLs (§9). | — |
| C14 | Observability | **Partial** | `metrics` table + `health` command; alert list is explicit (§10). No exporter. | Prometheus endpoint. |
| C15 | Fair credit/attention allocation | **Partial** | Credits are only spent on incidents with a reserve; approver attention is protected by per-workflow budgets and one slot reserved. No cross-tenant arbitration. | Weighted fair queue across tenants. |

**Principle:** build the loop end to end and make the parts that can hurt a client (governance, statistics, incident response, crash safety, audit) correct before adding breadth. Everything cut is a lever (per-person timing, cross-axis cohorts, UI) whose evidence base is too thin in the scenario horizon to defend.

## 3. Stakeholders
### 01 Sales — Nikhil Rao
- **Accepted:** speed where it is safe: rollbacks, harm stops and caller-ID rotations use the fast path; routine batching is minimal; the supervisor view gives a per-client lift table.
- **Declined:** a single blended score (violates the KPI definition and Product's memo); promoting a winner to everyone by evening (we promote 85/15 with a holdout and need evidence first); the "persuasive" prompt (it is the one that raises hallucination risk; prompts only change through an incident fix with validation).
- **Wrong against the contract:** "Kestrel has auto-apply for everything" — `ks_cancel` allows only schedule, caller_id, welcome_message, voice, capped at a 0.2 shift; prompts and cohorts are not allowed. "Northwind is fine with auto-apply on KYC" — `nw_kyc` has auto-apply **disabled**.
- **Reply:** *Nikhil — you'll get a lift figure per client per KPI (pickup, engagement, conclusion), not a blend; blending hides which lever moved. Winners go live at 85% with a 15% holdout so we can prove the lift and catch decay; I won't take it to 100% by evening. Kestrel's policy only auto-applies schedule, caller-ID, welcome and voice within a 0.2 shift, and Northwind KYC has auto-apply off, so those changes go through the approver. The "persuasive" prompt is out unless an incident fix validates it. For the summit I can show the audit trail of one real change end to end.*

### 02 Compliance — Meera Iyer (Northwind)
- **Accepted:** all customer-facing changes (welcome, voice, prompt, cohorts) go through a named approval on Northwind workflows (their policy permits auto only for schedule/caller_id, and we don't auto-apply customer-facing growth moves anywhere); prompt changes carry a validation run; every proposal has diff/dry-run/rationale; `explain` reconstructs variant-and-reason by config version.
- **Declined:** "no customer even briefly worse off" cannot be guaranteed by any experiment; we bound it (futility/harm stops, minimum evidence, control share ≥ 40%) and say so. A per-customer "what did they hear" answer needs the call events (`variant`, `config_version`) held by the platform; our store gives the version-level reason and the lookup key.
- **Wrong/clarify:** approvers work 10–19 (KYC 10–18); a request sent at night is *guaranteed* to expire on a 12h TTL, so we hold such requests until the window opens.
- **Reply:** *Meera — agreed on all five. Anything a customer hears (opening line, voice, script) is proposed to your named approver with the diff, dry run and, for scripts, a validation run; operational changes (timing, caller-ID rotation) are applied within policy and listed in the weekly summary. For an auditor's question we can show, per config version, the variant and the reason it was live; the per-call lookup uses the platform's call event, which carries that version. Experiments are bounded (the incumbent keeps ≥40%, harmful arms are stopped on evidence) but I can't promise zero exposure to a worse variant.*

### 03 Platform/SRE — Kabir Menon
- **Accepted:** kill/restart test (§9), idempotent writes with deterministic proposal ids, no new infrastructure (embedded SQLite file, one process), `health` command, explicit pageable-alert list (§10), 10× analysis (§8).
- **Declined:** reusing Postgres/Redis for now — a single-writer embedded store is enough at this scale and has no 2 a.m. operator; sharding by workflow is the migration path.
- **Wrong/clarify:** none factually wrong; the 10 min/day target is measured in §8.
- **Reply:** *Kabir — killed with SIGKILL four times mid-run (including with approvals pending); it resumed from a durable cursor, never double-applied and kept one continuous audit trail (reports/crash_recovery.md). State is one SQLite file (WAL) written transactionally; no Redis/Postgres needed at this scale, and the 10× plan is to shard workflows across processes with a DB each. `controller.cli health` shows ingest lag, decisions, credits and what is page-worthy; only stuck proposals, escalated incidents, ingest failure and credit exhaustion should page.*

### 04 Client ops supervisor — Anita Desai (Kestrel)
- **Accepted:** her edits are never undone (48h hold on edited dimensions; in-flight proposals go stale and are re-planned); one batched request per workflow, routine requests never before 11:00 and at most 2 a day; one-screen supervisor view; fixes are checked for engagement after rollout (the verbatim-script failure mode).
- **Declined:** "tell me *before* anything changes": changes that go through an approval are announced by the request itself; auto-applied changes are limited to protective moves (rollbacks, caller-ID health, incident fixes where permitted) and appear in the view and digest. We cannot block those without losing the fast path.
- **Wrong/clarify:** Kestrel's policy allows up to 4 requests/24h; her "2 a day, not before 11:00" is stricter and is adopted as our self-imposed routine limit, with incident fixes exempt.
- **Reply:** *Anita — your edits stay: if you change something we hold off that dimension for 48 hours and re-plan around it. You'll get one batched request at a time, never before 11:00, at most two routine requests a day; fixes for a bad prompt are the exception. `controller.cli supervisor` is the one screen: what's being tested, what's winning, what's waiting on you, what changed today. Prompt fixes are re-checked on engagement after rollout, so a safe-but-lifeless script gets flagged. One thing I can't promise: protective changes (rolling back a decayed winner, rotating a bad caller ID) may apply without a prior request.*

### 05 Product — Tara Kulkarni
- **Accepted:** pickup/engagement/conclusion never blended; one cohort object (`cohorts` table, same id in config, experiments, schedule, audit and view); minimum sizes with the cost stated (§5); proposals carry impact/diff/affected/dry-run with a documented formula; only observed exposure counts (evidence = recorded calls by variant and version); a winner changes that workflow only.
- **Declined:** per-person call-time as P0 (cut, assumption 12); treating an expired proposal as a bare rejection — we do treat it as a non-decision, wait for a cooldown and re-propose with *fresh* data and a new id, never the stale body.
- **Wrong/clarify:** "ranking the queue by impact" works only if the score is comparable across workflows; ours is bounded and based on expected lift × population × confidence.
- **Reply:** *Tara — held to all your definitions: pickup, engagement and conclusion are separate everywhere; one cohort object with one id across detection, experiments, schedule and the supervisor view; only calls that actually ran count as evidence. Minimum cohort size is 8% of traffic and ≥200 trials per arm-slice, which costs days of speed to avoid false winners. Impact score = 1−exp(−(expected relative lift × share affected × confidence)/0.03), so it ranks. Per-person call-time and a web UI are cut; caller-ID health and the supervisor CLI are in.*

### 06 CTO — Aryamann
- **Accepted:** choose and say no; spend credits only where they change a decision (5 credits in public_02: one validation, no LLM call because the last-good prompt validated); trust the contract over memos; documentation for the on-call.
- **Declined:** nothing to decline; this memo is a rubric.
- **Reply:** *Aryamann — understood. Cut: per-person timing, cross-axis cohorts, UI, cross-tenant arbitration. Built end to end: ingest, shared cohorts, experiments with decay/rollback, caller-ID health, incident loop, governance, audit, crash recovery. Public_02 spent 5 credits: the last-good prompt was free to propose and needed one validation. What breaks first at 10× is the single-process aggregation of one workflow's chunks; the plan is per-workflow sharding.*

## 4. Architecture
Diagram (ASCII or Mermaid) from events in to config changes out. Components, state, where the state lives,
and what happens on restart.

## 5. The learning loop
- **Cohorts**: how they're formed, the minimum size and why, and how you avoid fragmenting traffic.
- **Experiment design**: allocation strategy, exploration vs. exploitation, how you handle two dimensions
  (welcome × voice) and interactions between them.
- **Deciding a winner**: test or posterior, stopping rule, multiple comparisons, and your false-winner rate.
- **Decay and rollback**: how you notice a winner stop winning, and how fast.
- **Call time and caller ID**: what you did with history, per-cohort vs. per-person, and how you explore.
- **Guardrail KPI**: how a change that helps the primary KPI but hurts the guardrail gets caught.

## 6. Governance
- Proposal lifecycle as a state machine, including expired, lapsed, stale and re-proposal paths.
- Batching and timing under approver hours, latency, TTL, apply windows and fatigue limits.
- When you use auto-apply and when you voluntarily don't, and why.
- How impact score, affected leads and dry run are computed, and how honest they are.
- What happens when a supervisor edits config mid-experiment.

## 7. Incidents
Detection thresholds and their expected false-positive rate, how you pick a fix, credit spend, and how you
verify a fix worked after applying it. Give a timeline from public_02.

## 8. Scale
Measured on public_03_load: ingest events/sec, end-to-end decision lag, peak memory, wall-clock time per
simulated day. What breaks first at 10×, and how you'd partition the work across workflows and tenants.

## 9. Reliability
Crash-recovery test: method, results, and what state you lose (if any). Idempotency keys. The behaviour when
the simulator returns 4xx/5xx.

## 10. Audit & observability
Show a real query or command that answers *"why did workflow X change at time T, who approved it, and what
happened after?"* using your store, with its output. List the alerts you'd page on and the ones you wouldn't.

## 11. Results
Paste the summary tables from `reports/public_01.md` and `reports/public_02.md`. Interpret them: where you
helped, where you were **harmful** and why, and what you'd change.

## 12. Trade-offs & rejected alternatives
| Option | Why considered | Why rejected / what instead |
|---|---|---|

## 13. Known weaknesses
Honest and specific.

## 14. If this went to production at Formi next month
What you'd do in the first two weeks, in order.
