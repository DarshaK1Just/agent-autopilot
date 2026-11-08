"""Adversarial / hidden-scenario-class tests. All inputs are synthetic and contract-shaped; none is derived from scenario files."""
import copy
import json
import random

import pytest

from controller import evidence as ev, stats
from controller.client import SimUnavailable
from controller.governance import Governor
from controller.incidents import Incidents
from controller.main import Controller, ensure_matching_db, pick_due
from controller.planner import Intent, WfCtx, _cohort_candidates, _confirm, _decide, load_exp, plan_caller_id, plan_lever, save_exp
from controller.store import Store
from tests.test_controller import (CFG, POL, SPEC, FakeLLMClient, _confirming, _did_ctx, _exploring, _incident_ctx,  # noqa: F401,F811
                                   _qa, store)  # noqa


def _put_promoted(store, rows, start_ver=2, now_blk=8, ctl_pickup_dials=3, w_pickup_dials=3):
    """rows: {blk: ((w_conn, w_eng), (c_conn, c_eng))}. W3 is the promoted winner at 85/15 over W1."""
    cfg = copy.deepcopy(CFG)
    cfg["allocations"]["default"]["welcome_message"] = {"W3": 0.85, "W1": 0.15}
    save_exp(store, "w1", "welcome_message", {"scopes": {"default": {"phase": "PROMOTED", "winner": "W3", "control": "W1", "start_ver": start_ver}},
                                              "retired": {}, "dropped": {}})
    store.run("INSERT INTO agg VALUES('w1',-5,1,'default','voice','V1','all','',6000,2000,1100)")
    for blk, ((wc, we), (cc, ce)) in rows.items():
        store.run("INSERT INTO agg VALUES('w1',?,2,'default','welcome_message','W3','all','',?,?,?)", (blk, wc * w_pickup_dials, wc, we))
        store.run("INSERT INTO agg VALUES('w1',?,2,'default','welcome_message','W1','all','',?,?,?)", (blk, cc * ctl_pickup_dials, cc, ce))
    return WfCtx(store, SPEC, cfg, 2, now_blk * 360, 10 * 1440, POL)


# ------------------------------------------------------------------- families A, E, D, L, AW, AX, AY: volume and rates
def test_sparse_workflow_is_insufficient_not_no_effect(store):
    ctx = _exploring(store, v2=(40, 25), v3=(40, 20), ctl=(80, 40))
    assert plan_lever(ctx, "voice", held=False) == []
    assert load_exp(ctx, "voice")["evidence"]["label"] == "INSUFFICIENT"


def test_measured_equal_arms_are_labelled_no_practical_effect(store):
    ctx = _exploring(store, v2=(4000, 2000), v3=(4000, 2000), ctl=(4000, 2000))
    assert plan_lever(ctx, "voice", held=False) == []
    assert load_exp(ctx, "voice")["evidence"]["label"] == "NO_PRACTICAL_EFFECT"


def test_microscopic_true_effect_is_not_worth_a_production_change(store):
    ctx = _exploring(store, v2=(20000, 10060), v3=(20000, 10000), ctl=(20000, 10000))  # +0.3 points, huge sample
    assert plan_lever(ctx, "voice", held=False) == []


def test_obvious_large_effect_is_found_with_modest_data(store):
    ctx = _exploring(store, v2=(300, 195), v3=(300, 150), ctl=(600, 300))  # 65% vs 50%
    (intent,) = plan_lever(ctx, "voice", held=False)
    assert intent.kind == "promote" and intent.patch["allocations"]["default"]["voice"]["V2"] == pytest.approx(0.5)


def test_empty_workflow_does_nothing(store):
    ctx = WfCtx(store, SPEC, copy.deepcopy(CFG), 1, 100, 10000, POL)
    assert plan_lever(ctx, "voice", held=False) == [] and plan_caller_id(ctx, -10**9) == []


def test_rate_near_zero_needs_an_absolute_effect_not_just_a_relative_one(store):
    ctx = _exploring(store, v2=(3000, 45), v3=(3000, 30), ctl=(3000, 30))  # 1.0% -> 1.5%: +50% relative, +0.5 points
    assert [r for r in [_decide(ctx, {(2, "default", "V1"): (9000, 3000, 30), (2, "default", "V2"): (9000, 3000, 45)}, ["V1", "V2"], "V1", {})][0][1]] == []
    assert POL.min_absolute_lift == 0.005


def test_too_few_events_near_zero_or_one_is_insufficient(store):
    ctx = _exploring(store)
    low = {(2, "default", "V1"): (900, 300, 3), (2, "default", "V2"): (900, 300, 9)}      # 3 vs 9 successes
    high = {(2, "default", "V1"): (900, 300, 297), (2, "default", "V2"): (900, 300, 299)}  # 3 vs 1 failures
    for counts in (low, high):
        rows, win, harm = _decide(ctx, counts, ["V1", "V2"], "V1", {})
        assert rows["V2"]["status"] == "insufficient" and not win


def test_engagement_uses_connected_not_dials():
    assert ev.kpi_of("engagement_rate", (100, 30, 15)) == (15, 30) and ev.kpi_of("pickup_rate", (100, 30, 15)) == (30, 100)


def test_statistics_are_numerically_safe_at_the_edges():
    cases = [((0, 0), (0, 0)), ((0, 10), (10, 10)), ((10**9 // 2, 10**9), (10**9 // 2 + 10**5, 10**9)), ((5, 5), (0, 5))]
    for arm, ctl in cases:
        c = stats.contrast(arm, ctl, 0.5)
        for thr in (-1.0, 0.0, 0.01, 1.0):
            p = c.p_greater(thr)
            assert 0.0 <= p <= 1.0 and p == p
        assert c.sd >= 0 and c.diff == c.diff
    assert stats.binom_sf(0, 0, 0.5) == 1.0 and 0.0 <= stats.binom_sf(5, 10**6, 1e-6) <= 1.0


# ------------------------------------------------------------------- families M, H, G, F: selection and confounding
def test_simpson_paradox_is_not_fooled_by_changing_allocation_mix():
    counts = {(2, "default", "V1"): (600, 200, 140), (2, "default", "V2"): (2400, 800, 520),   # high-baseline version: V2 is 5 points WORSE
              (3, "default", "V1"): (2400, 800, 240), (3, "default", "V2"): (600, 200, 50)}    # low-baseline version: 5 points WORSE again
    naive = lambda o: sum(v[2] for k, v in counts.items() if k[2] == o) / sum(v[1] for k, v in counts.items() if k[2] == o)
    assert naive("V2") > naive("V1") + 0.15               # pooled naively, V2 looks hugely better
    assert ev.stratified(counts, "V2", "V1", "engagement_rate", 0.5).diff < 0   # stratified by version it is worse


def test_multiple_real_winners_are_ranked_by_lower_bound_not_point_estimate(store):
    ctx = _exploring(store)
    counts = {(2, "default", "V1"): (9000, 3000, 1500), (2, "default", "V2"): (9000, 3000, 1740), (2, "default", "V3"): (900, 300, 180)}
    rows, win, harm = _decide(ctx, counts, ["V1", "V2", "V3"], "V1", {})
    assert rows["V2"]["status"] == rows["V3"]["status"] == "winner"
    assert rows["V3"]["diff"] > rows["V2"]["diff"]          # V3 has the larger point estimate ...
    assert win[0][1] == "V2"                                 # ... but V2 has the better lower credible bound


def test_rolled_back_winner_cannot_be_promoted_again_inside_retirement(store):
    ctx = _exploring(store)
    counts = {(2, "default", "V1"): (3000, 1000, 500), (2, "default", "V2"): (3000, 1000, 650)}
    assert _decide(ctx, counts, ["V1", "V2"], "V1", {})[1]
    assert not _decide(ctx, counts, ["V1", "V2"], "V1", {"V2": ctx.minute - 60})[1]


def test_early_false_winner_does_not_starve_the_unresolved_arm_and_is_withdrawn(store):
    ctx = _exploring(store, v2=(500, 290), v3=(500, 262), ctl=(1000, 500))
    (prov,) = plan_lever(ctx, "voice", held=False)
    assert prov.patch["allocations"]["default"]["voice"]["V3"] > 0           # unresolved arm keeps traffic
    store2 = Store(":memory:")
    store2.set_clock(3 * 1440, "x")
    ctx2 = _confirming(store2, (1600, 720), (800, 400))                        # fresh data: the winner was luck
    (out,) = plan_lever(ctx2, "voice", held=False)
    assert out.kind == "unconfirmed"


def test_expired_harm_stop_brings_the_arm_back_but_a_fresh_one_does_not(store):
    ctx = _exploring(store, v2=(300, 150), v3=(300, 150), ctl=(600, 300))
    ctx.cfg["allocations"]["default"]["voice"] = {"V1": 0.5, "V2": 0.5}
    ctx.minute = 5 * 1440
    save_exp(store, "w1", "voice", {"scopes": {"default": {"phase": "EXPLORING", "control": "V1", "start_ver": 2}}, "retired": {}, "dropped": {"V3": 0}})
    (back,) = plan_lever(ctx, "voice", held=False)
    assert back.kind == "reintroduce" and "V3" in back.patch["allocations"]["default"]["voice"]
    save_exp(store, "w1", "voice", {"scopes": {"default": {"phase": "EXPLORING", "control": "V1", "start_ver": 2}}, "retired": {},
                                    "dropped": {"V3": ctx.minute - 60}})
    assert plan_lever(ctx, "voice", held=False) == []


def test_a_rolled_back_winner_is_not_re_offered_automatically(store):
    ctx = _exploring(store, v2=(300, 150), v3=(300, 150), ctl=(600, 300))
    ctx.cfg["allocations"]["default"]["voice"] = {"V1": 0.5, "V2": 0.5}
    ctx.minute = 9 * 1440
    save_exp(store, "w1", "voice", {"scopes": {"default": {"phase": "EXPLORING", "control": "V1", "start_ver": 2}}, "retired": {"V3": 0}, "dropped": {}})
    assert plan_lever(ctx, "voice", held=False) == []


# ------------------------------------------------------------------- families I, J, K: decay, severe regression, guardrail
def test_busy_workflow_is_demoted_after_one_day_of_evidence(store):
    rows = {b: ((1000, 540), (200, 108)) for b in range(5, 9)}  # 4 blocks = 24h, flat winner, 800 control trials
    (intent,) = plan_lever(_put_promoted(store, rows), "welcome_message", held=False)
    assert intent.kind == "rollback"


def test_quiet_workflow_waits_for_evidence_not_for_the_clock(store):
    rows = {b: ((60, 32), (10, 5)) for b in range(2, 9)}  # 7 blocks (42h) but only 70 control trials: not enough to say anything
    assert plan_lever(_put_promoted(store, rows), "welcome_message", held=False) == []


def test_sudden_severe_regression_is_rolled_back_within_two_blocks(store):
    rows = {7: ((150, 60), (150, 92)), 8: ((150, 60), (150, 92))}  # winner collapses to 40% vs 61% control for two blocks
    (intent,) = plan_lever(_put_promoted(store, rows), "welcome_message", held=False)
    assert intent.kind == "rollback" and "severe" in intent.summary


def test_guardrail_collapse_after_promotion_is_caught(store):
    rows = {b: ((300, 170), (200, 108)) for b in range(2, 9)}  # engagement looks fine ...
    ctx = _put_promoted(store, rows, w_pickup_dials=8)          # ... but the winner's pickup is 12% vs 33% for the control
    (intent,) = plan_lever(ctx, "welcome_message", held=False)
    assert intent.kind == "rollback"


def test_healthy_winner_with_a_noisy_dip_is_kept(store):
    rows = {b: ((1000, 590), (200, 106)) for b in range(2, 9)}
    assert plan_lever(_put_promoted(store, rows), "welcome_message", held=False) == []


# ------------------------------------------------------------------- families N, O, P, Q: cohorts
def _slice_rows(store, tot_extra, slice_conn):
    spec = copy.deepcopy(SPEC)
    for opt, (conn, eng) in {"W1": (250, 100), "W2": (250, 160)}.items():
        store.run("INSERT INTO agg VALUES('w1',5,2,'default','welcome_message',?,'age_band','60+',?,?,?)", (opt, conn * 3, slice_conn[opt][0], slice_conn[opt][1]))
        store.run("INSERT INTO agg VALUES('w1',5,2,'default','welcome_message',?,'all','',?,?,?)", (opt, 1, conn + tot_extra, eng))
    return WfCtx(store, spec, copy.deepcopy(CFG), 2, 2 * 1440, 10**5, POL)


def test_tiny_cohort_with_a_big_lift_does_not_become_a_cohort(store):
    ctx = _slice_rows(store, tot_extra=9000, slice_conn={"W1": (250, 100), "W2": (250, 160)})  # ~5% of traffic
    assert _cohort_candidates(ctx, "welcome_message", {}, {"control": "W1", "start_ver": 2}, "W1", set()) == {}


def test_sizeable_cohort_with_a_big_lift_is_provisional_not_final(store):
    ctx = _slice_rows(store, tot_extra=100, slice_conn={"W1": (250, 100), "W2": (250, 160)})
    out = _cohort_candidates(ctx, "welcome_message", {}, {"control": "W1", "start_ver": 2}, "W1", set())
    (cid, (where, dist, evd)), = out.items()
    assert where == {"age_band": ["60+"]} and dist["W2"] == pytest.approx(POL.provisional_share) and evd["hold"] == "W1"


def test_no_useful_slice_means_no_cohort(store):
    ctx = _slice_rows(store, tot_extra=100, slice_conn={"W1": (250, 125), "W2": (250, 127)})
    assert _cohort_candidates(ctx, "welcome_message", {}, {"control": "W1", "start_ver": 2}, "W1", set()) == {}


def _cohort_state(store, fresh_w, fresh_c):
    cfg = copy.deepcopy(CFG)
    cfg["cohorts"] = [{"id": "age_band=60+", "where": {"age_band": ["60+"]}}]
    cfg["allocations"]["age_band=60+"] = {"welcome_message": {"W2": 0.5, "W1": 0.5}}
    save_exp(store, "w1", "welcome_message", {"scopes": {"default": {"phase": "EXPLORING", "control": "W1", "start_ver": 2},
                                                         "age_band=60+": {"phase": "CONFIRMING", "winner": "W2", "control": "W1", "start_ver": 3, "promo_lift": 0.2}},
                                              "retired": {}, "dropped": {}})
    store.run("INSERT INTO agg VALUES('w1',-5,1,'default','voice','V1','all','',6000,2000,1100)")
    for opt, (conn, eng) in (("W2", fresh_w), ("W1", fresh_c)):
        store.run("INSERT INTO agg VALUES('w1',8,3,'age_band=60+','welcome_message',?,'all','',?,?,?)", (opt, conn * 3, conn, eng))
    return WfCtx(store, SPEC, cfg, 3, 3 * 1440, 10**5, POL)


def test_cohort_override_that_does_not_replicate_falls_back_to_its_own_control(store):
    ctx = _cohort_state(store, (1600, 720), (800, 400))
    (intent,) = _confirm(ctx, "welcome_message", load_exp(ctx, "welcome_message"), "age_band=60+")
    assert intent.kind == "unconfirmed"
    assert intent.patch["allocations"]["age_band=60+"]["welcome_message"] == {"W1": 1.0}  # never the default's (possibly exploratory) mix


def test_cohort_override_that_replicates_is_confirmed(store):
    ctx = _cohort_state(store, (800, 480), (400, 200))
    (intent,) = _confirm(ctx, "welcome_message", load_exp(ctx, "welcome_message"), "age_band=60+")
    assert intent.kind == "confirm" and intent.patch["allocations"]["age_band=60+"]["welcome_message"]["W2"] == pytest.approx(0.85)


# ------------------------------------------------------------------- families R, S, T: caller IDs
def test_common_mode_degradation_does_not_reshuffle_caller_ids(store):
    cur = {"D1": 0.25, "D2": 0.25, "D3": 0.25, "D4": 0.25}
    ctx = _did_ctx(store, {o: (1000, 150) for o in cur}, cur)  # all IDs at 15% pickup
    assert plan_caller_id(ctx, -10**9) == []


def test_a_recovered_caller_id_is_rehabilitated(store):
    cur = {"D1": 0.32, "D2": 0.32, "D3": 0.33, "D4": 0.03}
    ctx = _did_ctx(store, {"D1": (1000, 260), "D2": (1000, 262), "D3": (1000, 258), "D4": (400, 105)}, cur)
    store.put("did_bad:w1", {"D4": 0})
    intents = plan_caller_id(ctx, -10**9)
    assert intents and intents[0].exp_update["did_bad"]["remove"] == ["D4"]
    assert intents[0].patch["allocations"]["default"]["caller_id"]["D4"] > 0.1


# ------------------------------------------------------------------- families U, V, W, AN, AO, AQ: incidents
def test_burst_that_subsides_never_opens_an_incident(store):
    ctx = _incident_ctx(store)
    _qa(store, 800, 40)
    inc = Incidents(store, None, POL)
    assert inc.check(ctx) is None                      # armed
    _qa(store, 2000, 29)                               # the burst is over: at baseline
    store.set_clock(store.now_minute + 60, "x")
    assert inc.check(ctx) is None and store.get("inc_hit:w1") is None


def test_old_incident_periods_do_not_become_the_baseline(store):
    _ = _incident_ctx(store)
    store.run("INSERT INTO qa VALUES('w1',1,3,'P2',1000,90)")                 # an earlier incident on P2: 9%
    store.run("""INSERT INTO incidents(id,wf,kind,state,opened_minute,evidence,data) VALUES('old','w1','hallucination','RESOLVED',0,'{}',
                 '{"bad_prompt": "P2", "since_version": 3}')""")
    k, n = Incidents(store, None, POL)._baseline("w1", since=5, blk_now=1)
    assert n == 20000 and k / n == pytest.approx(0.014, abs=1e-4)             # P2's incident rows are excluded


def test_baseline_follows_slow_drift_instead_of_freezing(store):
    store.run("INSERT INTO qa VALUES('w1',-100,1,'P1',20000,200)")            # a year ago: 1%
    store.run("INSERT INTO qa VALUES('w1',10,1,'P1',2000,60)")                # recent: 3%
    k, n = Incidents(store, None, POL)._baseline("w1", since=5, blk_now=12)
    assert k / n == pytest.approx(0.03)


def _wf_incident(store, wf, client, inc):
    cfg = copy.deepcopy(CFG)
    cfg["prompt_version"] = "P2"
    store.run("INSERT INTO config_versions VALUES(?,1,'business_default',NULL,0,'[]',NULL,NULL,?)", (wf, json.dumps(CFG)))
    store.run("INSERT INTO config_versions VALUES(?,2,'supervisor',NULL,0,'[]',NULL,NULL,?)", (wf, json.dumps(cfg)))
    store.run("INSERT INTO qa VALUES(?,1,1,'P1',20000,280)", (wf,))
    store.run("INSERT INTO qa VALUES(?,1,2,'P2',800,40)", (wf,))
    spec = dict(SPEC, workflow_id=wf)
    ctx = WfCtx(store, spec, cfg, 2, store.now_minute, 10000, POL)
    inc.check(ctx)
    store.set_clock(store.now_minute + 60, "x")
    inc.check(ctx)
    return ctx


def test_two_incidents_on_different_workflows_stay_separate_and_share_credits_coherently(store):
    client = FakeLLMClient({"P1": 7})
    inc = Incidents(store, client, POL)
    inc.credits = 200.0
    a, b = _wf_incident(store, "wa", client, inc), _wf_incident(store, "wb", client, inc)
    assert len(inc.respond(a)) == 1 and len(inc.respond(b)) == 1
    rows = store.q("SELECT wf, state FROM incidents ORDER BY wf")
    assert [(r["wf"], r["state"]) for r in rows] == [("wa", "PROPOSING"), ("wb", "PROPOSING")]
    assert {r["wf"] for r in store.q("SELECT wf FROM validations")} == {"wa", "wb"}
    assert store.one("SELECT COUNT(*) n FROM credits")["n"] == 2


def test_a_second_incident_on_the_same_workflow_waits_for_the_first(store):
    ctx = _incident_ctx(store)
    _qa(store, 800, 40)
    inc = Incidents(store, FakeLLMClient({"P1": 7}), POL)
    inc.check(ctx); store.set_clock(store.now_minute + 60, "x"); inc.check(ctx)
    assert inc.check(ctx) is None and store.one("SELECT COUNT(*) n FROM incidents")["n"] == 1


def test_running_out_of_credits_escalates_without_looping(store):
    client = FakeLLMClient({"P1": 7})
    inc = Incidents(store, client, POL)
    inc.credits = 2.0
    ctx = _wf_incident(store, "w1", client, inc)
    assert inc.respond(ctx) == [] and client.calls == []
    assert store.one("SELECT state FROM incidents")["state"] == "ESCALATED"
    assert inc.respond(ctx) == [] and client.calls == []


class _BadLLM(FakeLLMClient):
    def suggest_fixes(self, wf, problem):
        self.calls.append(("llm", None))
        return {"suggestions": [{}, {"prompt_version": None}, {"prompt_version": "NOPE"}, {"prompt_version": "P2"}, "garbage",
                                {"prompt_version": "P3"}], "credits_remaining": 90.0}


def test_malformed_duplicate_or_unknown_llm_candidates_are_ignored(store):
    client = _BadLLM({"P1": 60, "P3": 5, "P2": 14})
    inc = Incidents(store, client, POL)
    inc.credits = 200.0
    ctx = _wf_incident(store, "w1", client, inc)
    intents = inc.respond(ctx)                               # must not raise
    assert [i.patch["prompt_version"] for i in intents] in ([], ["P3"])
    assert all(c[1] in (None, "P1", "P3", "P2") for c in client.calls)   # only real option names were ever validated


# ------------------------------------------------------------------- supervisor families Y, Z, AA
def _sup_edit(store, version, dims):
    store.run("INSERT INTO config_versions VALUES('w1',?,'supervisor',NULL,0,?,NULL,NULL,'{}')", (version, json.dumps(dims)))


def test_supervisor_edit_of_the_same_lever_resets_the_experiment(store):
    ctx = _exploring(store, v2=(500, 290))
    _sup_edit(store, 3, ["voice"])
    (intent,) = plan_lever(ctx, "voice", held=False)
    assert intent.kind == "exp_reset" and intent.evidence["supervisor_edit"] is True


def test_supervisor_edit_of_another_dimension_keeps_the_experiment(store):
    ctx = _exploring(store, v2=(500, 290))
    _sup_edit(store, 3, ["schedule"])
    (intent,) = plan_lever(ctx, "voice", held=False)
    assert intent.kind == "promote"          # evidence and experiment survive an unrelated edit


# ------------------------------------------------------------------- scheduling, resilience, world switch
def test_hot_workflow_cannot_starve_the_rest():
    wfs = [f"w{i:02d}" for i in range(20)]
    last, served = {}, {}
    for tick in range(6):
        now = tick * 15
        for wf in pick_due(last, wfs, now, 0, 8):  # interval 0: everything is always due
            last[wf] = now + 1
            served[wf] = served.get(wf, 0) + 1
    assert set(served) == set(wfs) and max(served.values()) - min(served.values()) <= 1


def _bare_controller(store):
    c = Controller.__new__(Controller)
    c.store, c.pol, c.sleep, c.slept = store, POL, lambda s: c.slept.append(s), []
    c.finished, c.backlog, c.specs = False, 0, {"w1": SPEC}
    c.startup = lambda: None
    c.client = type("C", (), {"state": lambda s: {"finished": False}})()
    c.ing = type("I", (), {"pending": lambda s: []})()
    return c


def test_long_outage_backs_off_then_exits_with_code_2_and_keeps_state(store):
    c = _bare_controller(store)
    def boom():
        raise SimUnavailable("down")
    c._iteration = boom
    assert c.run() == 2
    assert len(c.slept) == POL.outage_retries and max(c.slept) <= 30
    assert store.one("SELECT 1 FROM audit WHERE kind='controller_giving_up'") is not None


def test_short_outage_recovers_and_finishes_cleanly(store):
    c = _bare_controller(store)
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] <= 3:
            raise SimUnavailable("blip")
        return True
    c._iteration = flaky
    assert c.run() == 0 and c.slept == [2, 4, 8]


def test_backlog_does_not_postpone_incident_work_but_pauses_routine_planning(store):
    c = _bare_controller(store)
    seen = {"safety": 0, "routine": 0}
    c.backlog, c.last_eval = 3, {}
    c.advance = lambda m: pytest.fail("must not advance while data is unread")
    c.ingest_pending = lambda: 2
    c.reconcile = lambda: None
    c.safety = lambda wf: seen.__setitem__("safety", seen["safety"] + 1)
    c.plan_routine = lambda wf: seen.__setitem__("routine", seen["routine"] + 1)
    c.followups = lambda: None
    c.inc = type("N", (), {"credits": 1})()
    c.client = type("C", (), {"stats": {"errors": 0, "retries": 0}})()
    assert c._iteration() is False
    assert seen == {"safety": 1, "routine": 0}


def test_world_switch_never_reuses_state_even_without_a_recorded_key(tmp_path):
    path = str(tmp_path / "c.db")
    s = Store(path); s.put("started", True); s.put("cur_events", 99); s.close()    # ran before, key never written
    assert ensure_matching_db(path, "world-B") is not None
    path2 = str(tmp_path / "fresh.db")
    Store(path2).close()
    assert ensure_matching_db(path2, "world-B") is None                             # never ran: safe to use


# ------------------------------------------------------------------- randomized model test of the proposal state machine
class ModelSim:
    """Just enough of the governance contract: versions, stale bases, approvals that expire or get rejected."""
    def __init__(self):
        self.version, self.approvals, self.history = 1, [], []

    def post_approval(self, body):
        from controller.client import SimError
        if any(a["proposal_id"] == body["proposal_id"] for a in self.approvals):
            raise SimError(409, "duplicate_proposal_id", "")
        if body["base_version"] != self.version:
            raise SimError(409, "stale_base_version", {"current_version": self.version})
        a = {"approval_id": f"apr_{len(self.approvals) + 1}", "proposal_id": body["proposal_id"], "workflow_id": "w1", "status": "pending",
             "base": body["base_version"], "created_at": "2027-01-05T12:00:00+05:30", "expires_at": "2027-01-06T12:00:00+05:30"}
        self.approvals.append(a)
        return dict(a)

    def approvals_(self):
        return [dict(a) for a in self.approvals]

    def approval(self, aid):
        return dict(next(a for a in self.approvals if a["approval_id"] == aid), decided_at="2027-01-05T13:00:00+05:30",
                    apply_by="2027-01-05T15:00:00+05:30", reasons=[])

    def apply(self, wid, aid):
        from controller.client import SimError
        a = next(x for x in self.approvals if x["approval_id"] == aid)
        if a["status"] == "applied":
            raise SimError(409, "not_approved", {"status": "applied"})
        if a["status"] != "approved":
            raise SimError(409, "not_approved", {"status": a["status"]})
        if a["base"] != self.version:
            raise SimError(409, "stale_base_version", {"current_version": self.version})
        a["status"] = "applied"
        self.version += 1
        self.history.append({"version": self.version, "proposal_id": a["proposal_id"], "approval_id": aid})
        return {"version": self.version}

    def config_history(self, wid):
        return [{"version": 1, "proposal_id": None, "approval_id": None}] + self.history


@pytest.mark.parametrize("seed", range(40))
def test_random_interleavings_never_break_the_governance_invariants(seed):
    from tests.test_controller import FakeClient
    rnd = random.Random(seed)
    store = Store(":memory:")
    store.set_clock(1440 + 11 * 60, "x")
    sim = ModelSim()
    fc = FakeClient(sim)
    fc.approvals = lambda wf=None, status=None: sim.approvals_()
    mk = lambda: Governor(store, fc, POL, lambda ts: 24 * 60 if ts.startswith("2027-01-06") else 12 * 60 + 5, lambda wf, info: 7)
    gov = mk()
    voices = [{"V1": 0.5, "V2": 0.5}, {"V1": 0.6, "V2": 0.4}, {"V1": 0.7, "V2": 0.3}, {"V1": 0.8, "V2": 0.2}]
    for step in range(60):
        op = rnd.choice(["plan", "plan_urgent", "approve", "reject", "expire", "supervisor", "restart", "reconcile", "reconcile"])
        ctx = WfCtx(store, SPEC, copy.deepcopy(CFG), sim.version, store.now_minute, 10**5, POL)
        if op in ("plan", "plan_urgent"):
            urgent = op == "plan_urgent"
            dim = rnd.choice(["voice", "welcome_message"])
            patch = {"allocations": {"default": {dim: rnd.choice(voices) if dim == "voice" else {"W1": 0.5, "W2": 0.5}}}}
            gov.propose(ctx, [Intent(f"k{step}", "x", "w1", (dim,), patch, "s", "r", {}, urgent=urgent, protective=urgent)])
            store.set_clock(store.now_minute + 1440 * rnd.choice([0, 0, 1]), "x") if False else None
        elif op in ("approve", "reject", "expire"):
            pend = [a for a in sim.approvals if a["status"] == "pending"]
            if pend:
                rnd.choice(pend)["status"] = {"approve": "approved", "reject": "rejected", "expire": "expired"}[op]
        elif op == "supervisor":
            sim.version += 1
            sim.history.append({"version": sim.version, "proposal_id": None, "approval_id": None})
        elif op == "restart":
            gov = mk()
        gov.reconcile({"w1": SPEC}, {"w1": sim.version})
    gov.reconcile({"w1": SPEC}, {"w1": sim.version})
    rows = store.q("SELECT pid, state, applied_version FROM proposals")
    applied_ids = [h["proposal_id"] for h in sim.history if h["proposal_id"]]
    assert len(applied_ids) == len(set(applied_ids)), "a proposal produced two versions"
    assert len({a["proposal_id"] for a in sim.approvals}) == len(sim.approvals), "a proposal was submitted twice"
    for r in rows:
        if r["state"] == "APPLIED":
            assert r["pid"] in applied_ids, "recorded applied but the simulator never applied it"
        else:
            assert r["pid"] not in applied_ids or r["state"] in ("PENDING", "APPROVED"), f"{r['state']} proposal was applied"
    assert all(r["state"] in ("PLANNED", "PENDING", "APPROVED", "APPLIED", "REJECTED", "EXPIRED", "LAPSED", "STALE", "REFUSED", "FAILED", "ABANDONED")
               for r in rows)
