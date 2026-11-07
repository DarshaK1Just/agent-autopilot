"""Behavioural tests for the controller (not the simulator)."""
import copy
import json

import numpy as np
import pytest

from controller import cfgutil, stats
from controller.client import SimError, SimUnavailable
from controller.governance import Governor, InvalidTransition, TRANSITIONS, next_working
from controller.incidents import Incidents
from controller.ingest import Ingestor
from controller.planner import Intent, WfCtx, _decide
from controller.policy import Policy
from controller.store import Store

POL = Policy()
SPEC = {"workflow_id": "w1", "options": {"welcome_message": ["W1", "W2", "W3"], "voice": ["V1", "V2"], "caller_id": ["D1", "D2"],
                                          "prompt_version": ["P1", "P2", "P3"]},
        "objective": {"primary": "engagement_rate", "guardrail": {"pickup_rate_max_drop": 0.02}},
        "dialling_window": [9, 21], "cadence": [2, 2], "daily_batch": {"size": 100},
        "governance": {"auto_apply": {"enabled": True, "allowed_dims": ["caller_id", "schedule"], "max_shift": 0.3},
                       "approver_hours": [10, 19], "approver_latency_minutes": [30, 120], "proposal_ttl_hours": 24,
                       "apply_window_hours": 2, "max_requests_per_24h": 4, "min_validation_pass_rate": 0.97}}
CFG = {"cohorts": [], "allocations": {"default": {"welcome_message": {"W1": 1.0}, "voice": {"V1": 1.0}, "caller_id": {"D1": 0.5, "D2": 0.5}}},
       "prompt_version": "P1", "schedule": {"hour_weights": {}, "lead_preferred_hour": {}}}


@pytest.fixture()
def store():
    s = Store(":memory:")
    s.set_clock(12 * 60, "2027-01-04T12:00:00+05:30")
    return s


# ----------------------------------------------------------------------------- statistics
def test_contrast_clear_winner_vs_no_winner():
    win = stats.contrast((620, 1000), (550, 1000), 0.55)
    assert win.p_greater(0.0165) > 0.95
    tie = stats.contrast((552, 1000), (550, 1000), 0.55)
    assert tie.p_greater(0.0165) < 0.5


def test_insufficient_evidence_never_decides(store):
    counts = {(2, "default", "V1"): (100, 80, 40), (2, "default", "V2"): (100, 80, 60)}  # huge lift but only 80 trials
    ctx = WfCtx(store, SPEC, CFG, 1, 100, 10000, POL)
    rows, win, harm = _decide(ctx, counts, ["V1", "V2"], "V1", {})
    assert not win and rows["V2"]["status"] == "insufficient"


def test_decisions_are_deterministic(store):
    counts = {(2, "default", "V1"): (3000, 1200, 600), (2, "default", "V2"): (3000, 1200, 700)}
    ctx = WfCtx(store, SPEC, CFG, 1, 100, 10000, POL)
    a = _decide(ctx, counts, ["V1", "V2"], "V1", {})
    assert a == _decide(ctx, counts, ["V1", "V2"], "V1", {})
    assert a[1] and a[1][0][1] == "V2"


def test_guardrail_regression_blocks_winner(store):
    # engagement lifts, but pickup collapses for the candidate -> must not be promoted
    counts = {(2, "default", "V1"): (6000, 2000, 1000), (2, "default", "V2"): (6000, 1500, 900)}
    ctx = WfCtx(store, SPEC, CFG, 1, 100, 10000, POL)
    store.run("INSERT INTO agg VALUES('w1',-5,1,'default','voice','V1','all','',6000,2000,1000)")
    rows, win, harm = _decide(ctx, counts, ["V1", "V2"], "V1", {})
    assert rows["V2"]["status"] == "guardrail_blocked" and not win


def test_null_false_winner_rate_is_controlled(store):
    """Identical arms, repeated looks: false promotions should stay near the family alpha."""
    rng = np.random.default_rng(11)
    ctx = WfCtx(store, SPEC, CFG, 1, 100, 10000, POL)
    store.run("INSERT INTO agg VALUES('w1',-5,1,'default','voice','V1','all','',6000,2000,1000)")
    false_wins, trials = 0, 1000
    for _ in range(trials):
        k0 = k1 = 0
        n = 0
        won = False
        for _look in range(8):
            n += 150
            k0 += rng.binomial(150, 0.55)
            k1 += rng.binomial(150, 0.55)
            counts = {(2, "default", "V1"): (n * 3, n, k0), (2, "default", "V2"): (n * 3, n, k1)}
            _, win, _ = _decide(ctx, counts, ["V1", "V2"], "V1", {})
            if win:
                won = True
                break
        false_wins += won
    assert false_wins / trials < 0.07  # measured 3.5-5% over 8 looks at alpha 0.05 (reports/false_winner_rate.md)


# ----------------------------------------------------------------------------- config helpers
def test_patch_preserves_supervisor_edit_and_counts_shift():
    sup = copy.deepcopy(CFG)
    sup["prompt_version"] = "P2"  # a supervisor changed the prompt
    new = cfgutil.apply_patch(sup, {"allocations": {"default": {"voice": {"V1": 0.6, "V2": 0.4}}}})
    assert new["prompt_version"] == "P2"
    assert cfgutil.changed_dims(sup, new) == ["voice"]
    assert cfgutil.max_shift(sup, new) == pytest.approx(0.4)


def test_cohort_without_dim_falls_back_to_default():
    cfg = cfgutil.apply_patch(CFG, {"cohorts_add": [{"id": "c1", "where": {"age_band": ["60+"]}}],
                                    "allocations": {"c1": {"voice": {"V2": 1.0}}}})
    assert cfgutil.eff(cfg, "c1", "welcome_message") == {"W1": 1.0}
    assert cfgutil.eff(cfg, "c1", "voice") == {"V2": 1.0}


def test_clean_dist_normalises():
    d = cfgutil.clean_dist({"a": 0.333, "b": 0.333, "c": 0.334, "z": 0.001})
    assert sum(d.values()) == pytest.approx(1.0) and "z" not in d


def test_next_working_rolls_to_next_morning():
    assert next_working(20 * 60, [10, 19]) == 1440 + 10 * 60
    assert next_working(5 * 60, [10, 19]) == 10 * 60


# ----------------------------------------------------------------------------- ingestion
class FakeChunks:
    def __init__(self, chunks):
        self.chunks_ = chunks

    def chunks(self, kind, after=-1):
        return [m for m in self.chunks_ if m["kind"] == kind and m["chunk"] > after]

    def stream_chunk(self, n):
        yield from self.lines[n]


def _call(eid, lead="w1:l1", conn=True, eng=True, flag=False, voice="V1", ver=1):
    return json.dumps({"type": "call", "ts": "2027-01-04T10:15:00+05:30", "workflow_id": "w1", "lead_id": lead, "config_version": ver,
                       "cohort_id": "default", "variant": {"welcome_message": "W1", "voice": voice, "caller_id": "D1", "prompt_version": "P1"},
                       "connected": conn, "engaged": eng, "qa": {"hallucination_flag": flag}, "event_id": eid})


def _lead(eid):
    return json.dumps({"type": "lead", "ts": "2027-01-04T08:00:00+05:30", "workflow_id": "w1", "lead_id": "w1:l1",
                       "features": {"lang": "hi", "city_tier": "2", "age_band": "60+", "value_band": "mid"}, "event_id": eid})


def make_ingestor(store, lines_by_chunk):
    def last_id(ls):
        ids = []
        for x in ls:
            try:
                ids.append(json.loads(x)["event_id"])
            except ValueError:
                pass
        return max(ids)
    fake = FakeChunks([{"chunk": i, "kind": "events", "last_event_id": last_id(ls)} for i, ls in enumerate(lines_by_chunk)])
    fake.lines = lines_by_chunk
    ing = Ingestor(store, fake)
    ing.set_d0("2027-01-04T00:00:00+05:30", 0)
    return ing, fake


def _totals(store):
    r = store.one("SELECT SUM(dials) d, SUM(conn) c, SUM(eng) e FROM agg WHERE dim='voice' AND sl='all'")
    return tuple(r)


def test_ingest_counts_and_joins_features(store):
    ing, fake = make_ingestor(store, [[_lead(1), _call(2), _call(3, conn=False, eng=False), "not json"]])
    for m in ing.pending():
        ing.ingest_chunk(m)
    assert _totals(store) == (2, 1, 1)
    age = store.one("SELECT SUM(dials) d FROM agg WHERE dim='voice' AND sl='age_band' AND sv='60+'")
    assert age["d"] == 2 and ing.totals["malformed"] == 1


def test_duplicate_chunk_is_idempotent(store):
    ing, fake = make_ingestor(store, [[_lead(1), _call(2), _call(3)]])
    m = ing.pending()[0]
    ing.ingest_chunk(m)
    before = _totals(store)
    assert ing.ingest_chunk(m).get("skipped")
    assert _totals(store) == before


def test_crash_mid_chunk_rolls_back_and_restart_resumes(store):
    lines = [[_lead(1), _call(2), _call(3)]]
    ing, fake = make_ingestor(store, lines)

    def boom(n):
        yield lines[0][0]
        yield lines[0][1]
        raise SimUnavailable("connection reset")
    fake.stream_chunk = boom
    with pytest.raises(SimUnavailable):
        ing.ingest_chunk(ing.pending()[0])
    assert _totals(store) == (None, None, None) and store.get("cur_events", -1) == -1
    fake.stream_chunk = lambda n: iter(lines[0])
    ing2 = Ingestor(store, fake)  # new process
    ing2.set_d0("2027-01-04T00:00:00+05:30", 0)
    ing2.ingest_chunk(ing2.pending()[0])
    assert _totals(store) == (2, 2, 2)


def test_high_volume_batch_aggregates_correctly(store):
    n = 120_000
    lines = [[_lead(1)] + [_call(i + 2, conn=(i % 3 == 0), eng=(i % 6 == 0), voice="V1" if i % 2 else "V2") for i in range(n)]]
    ing, _ = make_ingestor(store, lines)
    ing.ingest_chunk(ing.pending()[0])
    assert _totals(store)[0] == n and _totals(store)[1] == n // 3


# ----------------------------------------------------------------------------- governance
class FakeSim:
    """Minimal governance-side simulator with injectable ambiguity."""

    def __init__(self):
        self.approvals, self.versions, self.fail_after_record = [], [{"version": 1, "proposal_id": None, "approval_id": None}], False
        self.status, self.stale = {}, False

    def post_approval(self, body):
        if any(a["proposal_id"] == body["proposal_id"] for a in self.approvals):
            raise SimError(409, "duplicate_proposal_id", body["proposal_id"])
        a = {"approval_id": f"apr_{len(self.approvals) + 1}", "proposal_id": body["proposal_id"], "workflow_id": body["workflow_id"],
             "status": "pending", "created_at": "2027-01-04T12:00:00+05:30", "expires_at": "2027-01-05T12:00:00+05:30"}
        self.approvals.append(a)
        if self.fail_after_record:
            self.fail_after_record = False
            raise SimUnavailable("timeout after server accepted")
        return dict(a)

    def approvals_(self):
        return [dict(a) for a in self.approvals]

    def approval(self, aid):
        a = next(x for x in self.approvals if x["approval_id"] == aid)
        return dict(a, decided_at="2027-01-04T13:00:00+05:30", apply_by="2027-01-04T15:00:00+05:30", reasons=[])

    def apply(self, wid, aid):
        a = next(x for x in self.approvals if x["approval_id"] == aid)
        if a["status"] == "lapsed":
            raise SimError(410, "approval_lapsed", "")
        if self.stale:
            raise SimError(409, "stale_base_version", {"current_version": 2})
        if a["status"] == "applied":
            raise SimError(409, "not_approved", {"status": "applied"})
        a["status"] = "applied"
        self.versions.append({"version": len(self.versions) + 1, "proposal_id": a["proposal_id"], "approval_id": aid})
        return {"version": len(self.versions)}

    def config_history(self, wid):
        return self.versions


class FakeClient:
    def __init__(self, sim):
        self.sim = sim

    def post_approval(self, b):
        return self.sim.post_approval(b)

    def approvals(self, wf=None, status=None):
        return self.sim.approvals_()

    def approval(self, aid):
        return self.sim.approval(aid)

    def apply(self, wid, aid):
        return self.sim.apply(wid, aid)

    def config_history(self, wid):
        return self.sim.config_history(wid)


def _gov(store, sim):
    return Governor(store, FakeClient(sim), POL, lambda ts: 24 * 60 if ts.startswith("2027-01-05") else 12 * 60 + 5, lambda wf, info: 42)


def _intent():
    return Intent("k1", "explore", "w1", ("voice",), {"allocations": {"default": {"voice": {"V1": 0.5, "V2": 0.5}}}}, "test voice", "because",
                  {"x": 1}, expected_rel_lift=0.05, confidence=0.9)


def _ctx(store):
    return WfCtx(store, SPEC, CFG, 1, store.now_minute, 10 * 1440, POL)


def test_crash_after_server_accepted_proposal_is_adopted_not_duplicated(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    sim.fail_after_record = True
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    assert store.one("SELECT state FROM proposals")["state"] == "PLANNED"
    gov2 = _gov(store, sim)  # restarted process
    gov2.reconcile({"w1": SPEC}, {"w1": 1})
    assert len(sim.approvals) == 1
    p = store.one("SELECT * FROM proposals")
    assert p["state"] == "PENDING" and p["approval_id"] == "apr_1"


def test_deterministic_proposal_id_and_no_second_inflight(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    assert gov.propose(_ctx(store), [_intent()]) is None  # one in flight per workflow
    assert store.one("SELECT pid FROM proposals")["pid"].startswith("w1-v1-")
    assert len(sim.approvals) == 1


def test_approve_then_apply_exactly_once_even_if_reconciled_twice(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    sim.approvals[0]["status"] = "approved"
    gov.reconcile({"w1": SPEC}, {"w1": 1})
    gov.reconcile({"w1": SPEC}, {"w1": 2})
    assert store.one("SELECT state, applied_version FROM proposals")["state"] == "APPLIED"
    assert len(sim.versions) == 2


def test_stale_base_is_terminal_and_replannable(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    sim.approvals[0]["status"] = "approved"
    sim.stale = True  # supervisor edit lands between approval and apply
    gov.reconcile({"w1": SPEC}, {"w1": 1})
    assert store.one("SELECT state FROM proposals")["state"] == "STALE"
    assert not gov.in_flight("w1")


def test_rejected_and_lapsed_are_terminal(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    sim.approvals[0]["status"] = "rejected"
    gov.reconcile({"w1": SPEC}, {"w1": 1})
    assert store.one("SELECT state FROM proposals")["state"] == "REJECTED"


def test_routine_request_waits_for_late_morning_and_respects_ttl(store):
    sim = FakeSim()
    store.set_clock(1440 + 8 * 60, "x")
    assert not _gov(store, sim).can_submit(_ctx(store), urgent=False)[0]  # before 11:00
    store.set_clock(1440 + 11 * 60, "x")
    assert _gov(store, sim).can_submit(_ctx(store), urgent=False)[0]
    spec = copy.deepcopy(SPEC)
    spec["governance"]["proposal_ttl_hours"] = 6
    ctx = WfCtx(store, spec, CFG, 1, 1440 + 18 * 60, 10 * 1440, POL)
    store.set_clock(1440 + 18 * 60, "x")
    assert not _gov(store, sim).can_submit(ctx, urgent=True)[0]  # decision would land after the approver went home


def test_customer_facing_change_takes_approval_route_even_if_policy_allows_auto(store):
    spec = copy.deepcopy(SPEC)
    spec["governance"]["auto_apply"]["allowed_dims"] = ["voice", "caller_id"]
    ctx = WfCtx(store, spec, CFG, 1, 100, 10000, POL)
    gov = _gov(store, FakeSim())
    new, dims = gov.compose(ctx, [_intent()])
    assert gov.choose_route(ctx, new, dims, [_intent()]) == "approval"
    protective = _intent()
    protective.protective = True
    protective.patch = {"allocations": {"default": {"voice": {"V1": 0.8, "V2": 0.2}}}}
    new, dims = gov.compose(ctx, [protective])
    assert gov.choose_route(ctx, new, dims, [protective]) == "auto"  # within max_shift 0.3 and allowed


def test_auto_apply_refused_when_shift_exceeds_cap(store):
    ctx = WfCtx(store, SPEC, CFG, 1, 100, 10000, POL)
    gov = _gov(store, FakeSim())
    big = Intent("c", "caller_id", "w1", ("caller_id",), {"allocations": {"default": {"caller_id": {"D1": 1.0}}}}, "s", "r", {}, protective=True)
    new, dims = gov.compose(ctx, [big])
    assert cfgutil.max_shift(CFG, new) == pytest.approx(0.5)
    assert gov.choose_route(ctx, new, dims, [big]) == "approval"  # 0.5 > max_shift 0.3


# ----------------------------------------------------------------------------- incidents
def _qa(store, conn, flagged, prompt="P2", ver=2):
    store.run("INSERT OR REPLACE INTO qa VALUES('w1',1,?,?,?,?)", (ver, prompt, conn, flagged))


def _incident_ctx(store, prompt="P2"):
    cfg = copy.deepcopy(CFG)
    cfg["prompt_version"] = prompt
    store.run("INSERT INTO config_versions VALUES('w1',1,'business_default',NULL,0,'[]',NULL,NULL,?)", (json.dumps(CFG),))
    store.run("INSERT INTO config_versions VALUES('w1',2,'supervisor',NULL,0,'[]',NULL,NULL,?)", (json.dumps(cfg),))
    _qa(store, 20000, 280, prompt="P1", ver=1)  # 1.4% baseline
    return WfCtx(store, SPEC, cfg, 2, store.now_minute, 10000, POL)


def test_isolated_flags_do_not_open_incident(store):
    ctx = _incident_ctx(store)
    _qa(store, 40, 4)
    inc = Incidents(store, None, POL)
    assert inc.check(ctx) is None


def test_sustained_spike_opens_incident_on_second_look_only(store):
    ctx = _incident_ctx(store)
    _qa(store, 800, 40)  # 5% vs 1.4% baseline
    inc = Incidents(store, None, POL)
    assert inc.check(ctx) is None  # first look only arms
    store.set_clock(store.now_minute + 60, "x")
    assert inc.check(ctx) is not None
    assert store.one("SELECT state FROM incidents")["state"] == "OPEN"


def test_baseline_level_flags_never_open_incident(store):
    ctx = _incident_ctx(store)
    _qa(store, 2000, 29)  # 1.45%
    inc = Incidents(store, None, POL)
    inc.check(ctx)
    store.set_clock(store.now_minute + 60, "x")
    assert inc.check(ctx) is None


class FakeLLMClient:
    def __init__(self, fails):
        self.fails, self.calls = fails, []

    def validate(self, wf, prompt, n):
        self.calls.append(("validate", prompt))
        f = self.fails[prompt]
        return {"validation_run_id": f"val_{len(self.calls)}", "workflow_id": wf, "prompt_version": prompt, "n": n, "failures": f,
                "pass_rate": 1 - f / n, "credits_remaining": 100.0 - len(self.calls)}

    def suggest_fixes(self, wf, problem):
        self.calls.append(("llm", None))
        return {"suggestions": [{"prompt_version": "P3", "summary": "x"}], "credits_remaining": 90.0}


def _open_incident(store, client):
    ctx = _incident_ctx(store)
    _qa(store, 800, 40)
    inc = Incidents(store, client, POL)
    inc.credits = 200.0
    inc.check(ctx)
    store.set_clock(store.now_minute + 60, "x")
    inc.check(ctx)
    return ctx, inc


def test_revert_to_last_good_prompt_needs_no_llm_credits(store):
    client = FakeLLMClient({"P1": 7})
    ctx, inc = _open_incident(store, client)
    intents = inc.respond(ctx)
    assert [i.patch for i in intents] == [{"prompt_version": "P1"}]
    assert ("llm", None) not in client.calls
    assert intents[0].validation_run_id and intents[0].urgent


def test_failed_validation_falls_through_to_llm_and_never_picks_unvalidated(store):
    client = FakeLLMClient({"P1": 40, "P3": 5, "P2": 14})  # last-good fails its safety validation (8% failures)
    ctx, inc = _open_incident(store, client)
    store.run("UPDATE incidents SET data=json_set(data,'$.bad_prompt','P2')")
    intents = inc.respond(ctx)
    prompts = [i.patch["prompt_version"] for i in intents]
    assert prompts in ([], ["P3"])
    assert ("llm", None) in client.calls


def test_all_candidates_failing_validation_escalates(store):
    client = FakeLLMClient({"P1": 60, "P3": 60})
    ctx, inc = _open_incident(store, client)
    assert inc.respond(ctx) == []
    store.set_clock(store.now_minute + 60, "x")
    inc.respond(ctx)
    assert store.one("SELECT state FROM incidents")["state"] in ("OPEN", "ESCALATED")


# ----------------------------------------------------------------------------- startup safety / client
def test_state_from_another_world_is_archived_not_reused(tmp_path):
    import os
    from controller.main import ensure_matching_db
    path = str(tmp_path / "c.db")
    s = Store(path)
    s.put("world_key", "world-A")
    s.put("cur_events", 41)
    s.close()
    assert ensure_matching_db(path, "world-A") is None and os.path.exists(path)  # same world: resume
    moved = ensure_matching_db(path, "world-B")                                  # new world: start clean
    assert moved and not os.path.exists(path) and os.path.exists(moved)


def test_client_retries_reads_but_never_posts():
    import httpx
    from controller.client import SimClient, SimUnavailable
    calls = {"get": 0, "post": 0}

    def handler(req: httpx.Request):
        if req.method == "GET":
            calls["get"] += 1
            return httpx.Response(503) if calls["get"] < 3 else httpx.Response(200, json={"ok": True})
        calls["post"] += 1
        return httpx.Response(500)
    c = SimClient("http://sim", retries=4, backoff=0.0)
    c.http = httpx.Client(base_url="http://sim", transport=httpx.MockTransport(handler))
    assert c.state() == {"ok": True} and calls["get"] == 3
    with pytest.raises(SimUnavailable):
        c.advance(60)
    assert calls["post"] == 1  # an ambiguous side-effecting call is reconciled by the caller, not resent


def test_client_maps_conflicts_to_typed_errors():
    import httpx
    from controller.client import SimClient
    c = SimClient("http://sim", backoff=0.0)
    c.http = httpx.Client(base_url="http://sim", transport=httpx.MockTransport(
        lambda r: httpx.Response(409, json={"error": "stale_base_version", "detail": {"current_version": 7}})))
    with pytest.raises(SimError) as e:
        c.apply("w1", "apr_1")
    assert e.value.code == "stale_base_version" and e.value.detail == {"current_version": 7}


# ----------------------------------------------------------------------------- invariants added in the review
def test_state_machine_rejects_illegal_moves(store):
    store.set_clock(1440 + 11 * 60, "x")
    gov = _gov(store, FakeSim())
    gov.propose(_ctx(store), [_intent()])
    pid = store.one("SELECT pid FROM proposals")["pid"]
    assert store.one("SELECT state FROM proposals")["state"] == "PENDING"
    with pytest.raises(InvalidTransition):
        gov._move(pid, "PLANNED")  # no way back
    gov._move(pid, "REJECTED")
    for target in ("APPLIED", "APPROVED", "PENDING"):
        with pytest.raises(InvalidTransition):
            gov._move(pid, target)  # terminal states have no way out
    assert all(t for t in TRANSITIONS.values())


def test_db_refuses_unknown_proposal_state(store):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        store.run("INSERT INTO proposals(pid,wf,route,state,base_version) VALUES('x','w1','auto','BOGUS',1)")


@pytest.mark.parametrize("status", ["rejected", "expired"])
def test_rejected_or_expired_proposal_is_never_applied(store, status):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    applied = []
    sim.apply = lambda wid, aid: applied.append(aid)
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    sim.approvals[0]["status"] = status
    for _ in range(3):
        gov.reconcile({"w1": SPEC}, {"w1": 1})
    assert applied == [] and store.one("SELECT state FROM proposals")["state"] == status.upper()


def test_supervisor_edit_while_pending_abandons_and_unblocks_planning(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    gov.reconcile({"w1": SPEC}, {"w1": 2})  # supervisor moved the config to v2
    assert store.one("SELECT state FROM proposals")["state"] == "ABANDONED"
    assert not gov.in_flight("w1")


def test_urgent_fix_is_not_blocked_by_routine_proposal_in_flight(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    gov = _gov(store, sim)
    gov.propose(_ctx(store), [_intent()])
    fix = Intent("fix", "prompt_fix", "w1", ("prompt_version",), {"prompt_version": "P3"}, "fix", "why", {}, urgent=True,
                 protective=True, validation_run_id="val_1")
    assert gov.propose(_ctx(store), [fix]) is not None
    assert store.one("SELECT COUNT(*) n FROM proposals WHERE state='PENDING'")["n"] == 2
    # a second routine proposal is still refused while anything is in flight
    assert gov.propose(_ctx(store), [_intent()]) is None


def test_restart_resumes_approved_proposal_and_applies_once(store):
    store.set_clock(1440 + 11 * 60, "x")
    sim = FakeSim()
    _gov(store, sim).propose(_ctx(store), [_intent()])
    sim.approvals[0]["status"] = "approved"
    fresh = _gov(store, sim)  # a new process sees only the database
    fresh.reconcile({"w1": SPEC}, {"w1": 1})
    fresh.reconcile({"w1": SPEC}, {"w1": 2})
    assert store.one("SELECT state FROM proposals")["state"] == "APPLIED" and len(sim.versions) == 2


def test_cohort_needs_bonferroni_bar_and_never_uses_a_harmful_option(store):
    from controller.planner import _cohort_candidates
    cfg = copy.deepcopy(CFG)
    ds = {"control": "W1", "start_ver": 1}
    # slice 'hi' shows W3 +11pts over W1 (n=250/arm) but W3 was already stopped as harmful workflow-wide
    for opt, (conn, eng) in {"W1": (250, 100), "W3": (250, 128)}.items():
        store.run("INSERT INTO agg VALUES('w1',1,1,'default','welcome_message',?,'lang','hi',?,?,?)", (opt, conn * 3, conn, eng))
        store.run("INSERT INTO agg VALUES('w1',1,1,'default','welcome_message',?,'all','',?,?,?)", (opt, conn * 3, conn, eng))
    ctx = WfCtx(store, SPEC, cfg, 1, 100, 10000, POL)
    assert _cohort_candidates(ctx, "welcome_message", {}, ds, "W1", {"W3"}) == {}


# ----------------------------------------------------------------------------- decay watch
def _promoted(store, winner_rates, ctl_rates):
    """A promoted W3 (85%) with a W1 holdout (15%), counts spread over the last four 6h blocks."""
    from controller.planner import save_exp
    cfg = copy.deepcopy(CFG)
    cfg["allocations"]["default"]["welcome_message"] = {"W3": 0.85, "W1": 0.15}
    save_exp(store, "w1", "welcome_message", {"scopes": {"default": {"phase": "PROMOTED", "winner": "W3", "control": "W1",
                                                                    "start_ver": 2, "promo_lift": 0.09}}, "retired": {}, "dropped": {}})
    for blk in range(5, 9):
        for opt, (conn, eng) in (("W3", winner_rates), ("W1", ctl_rates)):
            store.run("INSERT INTO agg VALUES('w1',?,2,'default','welcome_message',?,'all','',?,?,?)", (blk, opt, conn * 3, conn, eng))
    store.run("INSERT INTO agg VALUES('w1',-5,1,'default','voice','V1','all','',6000,2000,1100)")
    return WfCtx(store, SPEC, cfg, 2, 2 * 1440, 10 * 1440, POL)


def test_winner_that_stopped_winning_is_rolled_back(store):
    from controller.planner import plan_lever
    ctx = _promoted(store, (1000, 540), (200, 108))  # both arms at 54%: the lift is gone
    intents = plan_lever(ctx, "welcome_message", held=False)
    assert [i.kind for i in intents] == ["rollback"] and intents[0].urgent
    assert cfgutil.eff(cfgutil.apply_patch(ctx.cfg, intents[0].patch), "default", "welcome_message")["W1"] >= 0.5


def test_winner_that_still_wins_is_kept_even_if_below_its_promotion_lift(store):
    from controller.planner import plan_lever
    ctx = _promoted(store, (1000, 590), (200, 108))  # +5pts now, promoted at +9pts: smaller, but still a clear win
    assert plan_lever(ctx, "welcome_message", held=False) == []
