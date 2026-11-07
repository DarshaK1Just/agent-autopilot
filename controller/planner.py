"""Learning-loop planners. Each returns Intents: declarative patches to the *current* config plus the
evidence behind them. Planners are stateless functions of (aggregates, current config, small experiment memory),
so a restart or a supervisor edit simply changes their inputs.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field

from . import cfgutil, evidence as ev, stats
from .ingest import FEATURES
from .policy import Policy
from .store import Store

LEVERS = ("welcome_message", "voice")


@dataclass
class Intent:
    key: str
    kind: str
    wf: str
    dims: tuple
    patch: dict
    summary: str
    rationale: str
    evidence: dict
    expected_rel_lift: float = 0.0
    pop_share: float = 1.0
    confidence: float = 0.5
    protective: bool = False
    urgent: bool = False
    validation_run_id: str | None = None
    exp_update: dict | None = None
    dry_run: dict = field(default_factory=dict)


@dataclass
class WfCtx:
    store: Store
    spec: dict
    cfg: dict
    version: int
    minute: int
    end_minute: int
    pol: Policy

    @property
    def wf(self) -> str:
        return self.spec["workflow_id"]

    @property
    def primary(self) -> str:
        return self.spec["objective"]["primary"]

    @property
    def guardrail(self) -> tuple[str, float]:
        g = next(iter(self.spec["objective"]["guardrail"].items()))
        return g[0].replace("_max_drop", ""), float(g[1])

    @property
    def blk_now(self) -> int:
        return self.minute // ev.BLK

    @property
    def days_left(self) -> float:
        return max(0.0, (self.end_minute - self.minute) / 1440)

    @property
    def prior(self) -> float:
        return ev.baseline_rate(self.store, self.wf, self.primary)

    def okey(self, *parts) -> str:
        h = hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:10]
        return f"{self.wf}:{parts[0]}:{h}"


# --------------------------------------------------------------------------------------- experiment memory
def load_exp(ctx: WfCtx, dim: str) -> dict:
    eid = f"{ctx.wf}:{dim}"
    r = ctx.store.one("SELECT state FROM experiments WHERE id=?", (eid,))
    st = json.loads(r["state"]) if r else {"scopes": {}, "retired": {}}
    st.setdefault("dropped", {})  # options stopped as harmful for this lever: never offered again
    return st


def save_exp(store: Store, wf: str, dim: str, st: dict, phase: str = "ACTIVE"):
    store.run("INSERT INTO experiments(id,wf,dim,phase,state,updated_minute) VALUES(?,?,?,?,?,?) "
              "ON CONFLICT(id) DO UPDATE SET phase=excluded.phase, state=excluded.state, updated_minute=excluded.updated_minute",
              (f"{wf}:{dim}", wf, dim, phase, json.dumps(st, sort_keys=True), store.now_minute))


def apply_exp_update(store: Store, wf: str, upd: dict, version: int):
    """Called when the proposal carrying `upd` is applied: only then does the experiment state advance."""
    def sub(o):
        if isinstance(o, dict):
            return {k: sub(v) for k, v in o.items()}
        return version if o == "$V" else o
    upd = sub(upd)
    for dim, patch in upd.get("dims", {}).items():
        r = store.one("SELECT state FROM experiments WHERE id=?", (f"{wf}:{dim}",))
        st = json.loads(r["state"]) if r else {"scopes": {}, "retired": {}}
        for scope, s in patch.get("scopes", {}).items():
            if s is None:
                st["scopes"].pop(scope, None)
            else:
                st["scopes"].setdefault(scope, {}).update(s)
        st["retired"].update(patch.get("retired", {}))
        st.setdefault("dropped", {}).update(patch.get("dropped", {}))
        save_exp(store, wf, dim, st)
    for cid, (where, evd) in upd.get("cohorts_add", {}).items():
        store.run("INSERT OR REPLACE INTO cohorts(wf,cid,where_json,status,evidence,created_minute) VALUES(?,?,?,?,?,?)",
                  (wf, cid, json.dumps(where), "active", json.dumps(evd, default=str), store.now_minute))
    if "did_bad" in upd:
        bad = store.get(f"did_bad:{wf}", {})
        for o in upd["did_bad"]["add"]:
            bad[o] = store.now_minute
        for o in upd["did_bad"]["remove"]:
            bad.pop(o, None)
        store.put(f"did_bad:{wf}", bad)
    for cid in upd.get("cohorts_remove", []):
        store.run("UPDATE cohorts SET status='retired' WHERE wf=? AND cid=?", (wf, cid))


# --------------------------------------------------------------------------------------- helpers
def _kdist(d: dict, floor: float = 0.05) -> list[str]:
    return [o for o, w in d.items() if w >= floor]


def explore_dist(opts: list[str], ctl: str, share: float) -> dict[str, float]:
    others = [o for o in opts if o != ctl]
    ctl_w = max(share, 1.0 / len(opts))
    return cfgutil.clean_dist({ctl: ctl_w, **{o: (1 - ctl_w) / len(others) for o in others}})


def den_per_day(ctx: WfCtx) -> float:
    r = ctx.store.one("SELECT SUM(dials) d, SUM(conn) c, SUM(eng) e, MIN(blk) b0, MAX(blk) b1 FROM agg "
                      "WHERE wf=? AND dim='voice' AND sl='all' AND blk>=?", (ctx.wf, ctx.blk_now - 28))
    if not r or not r["d"]:
        return 0.0
    n = ev.kpi_of(ctx.primary, (r["d"], r["c"], r["e"]))[1]
    return n / max(1.0, (r["b1"] - r["b0"] + 1) / 4)


def replay(counts: dict, cohs: list[str], primary: str, old: dict, new: dict, ctl: str, prior: float) -> dict:
    """Dry run: expected KPI of the old vs new allocation using the *recorded* outcomes of each randomised arm."""
    rates, var, ns = {}, {}, {}
    for o in set(old) | set(new):
        c = ev.totals({k: v for k, v in counts.items() if k[1] in cohs}, o)
        k, n = ev.kpi_of(primary, c)
        m, v = stats.beta_post(k, n, prior)
        rates[o], var[o], ns[o] = m, v, n
    e_old = sum(w * rates.get(o, 0) for o, w in old.items())
    e_new = sum(w * rates.get(o, 0) for o, w in new.items())
    sd = math.sqrt(sum(((new.get(o, 0) - old.get(o, 0)) ** 2) * var.get(o, 0) for o in set(old) | set(new)))
    return {"method": "replay of recorded randomised arms", "kpi": primary, "n_per_arm": ns,
            "expected_old": round(e_old, 4), "expected_new": round(e_new, 4), "delta": round(e_new - e_old, 4),
            "delta_ci95": [round(e_new - e_old - 1.96 * sd, 4), round(e_new - e_old + 1.96 * sd, 4)]}


def guardrail_ok(ctx: WfCtx, counts: dict, opt: str, ctl: str) -> tuple[bool, dict]:
    gname, drop = ctx.guardrail
    prior = ev.baseline_rate(ctx.store, ctx.wf, gname)
    c = ev.stratified(counts, opt, ctl, gname, prior)
    if c is None:
        return True, {"guardrail": gname, "note": "no overlapping strata; guardrail not measurable yet"}
    p_ok = c.p_greater(-drop)
    return p_ok >= ctx.pol.guardrail_confidence, {"guardrail": gname, "diff": round(c.diff, 4), "sd": round(c.sd, 4),
                                                   "p_within_tolerance": round(p_ok, 3), "max_drop": drop}


def _contrast_row(c: stats.Contrast) -> dict:
    return {"diff": round(c.diff, 4), "sd": round(c.sd, 4), "rate_arm": round(c.rate_arm, 4),
            "rate_ctl": round(c.rate_ctl, 4), "n_arm": c.n_arm, "n_ctl": c.n_ctl}


# --------------------------------------------------------------------------------------- experiments
def plan_lever(ctx: WfCtx, dim: str, held: bool) -> list[Intent]:
    """Explore -> evidence -> controlled promotion -> decay watch, for one lever (welcome_message or voice)."""
    opts = ctx.spec["options"][dim]
    if len(opts) < 2 or ctx.primary != "engagement_rate" or held:
        return []
    st = load_exp(ctx, dim)
    cur_def = cfgutil.dist(ctx.cfg, "default", dim)
    scopes = st["scopes"]
    ds = scopes.get("default")
    # a supervisor (or anyone) rewrote the allocation under a running experiment -> restart from reality
    if ds and ds["phase"] in ("EXPLORING", "CONFIRMING") and len(_kdist(cur_def)) < 2:
        return [Intent(ctx.okey("reset", dim, ctx.version), "exp_reset", ctx.wf, (), {}, f"{dim}: experiment reset",
                       "allocation changed externally; experiment assumptions invalid",
                       {"allocation": cur_def}, exp_update={"dims": {dim: {"scopes": {"default": None}}}})]
    if ds is None:
        return _start_explore(ctx, dim, st, cur_def)
    if ds["phase"] == "EXPLORING":
        return _evaluate_exploring(ctx, dim, st)
    if ds["phase"] == "CONFIRMING":
        return _confirm(ctx, dim, st)
    if ds["phase"] == "PROMOTED":
        return _watch_decay(ctx, dim, st)
    return []


def _start_explore(ctx: WfCtx, dim: str, st: dict, cur_def: dict) -> list[Intent]:
    pol = ctx.pol
    ctl = cfgutil.modal(cur_def)
    opts = [o for o in ctx.spec["options"][dim] if o == ctl or o not in st["dropped"]]
    k = len(opts)
    if k < 2:
        return []
    human = ctx.store.one("SELECT 1 FROM holds WHERE wf=? AND dim=? AND reason LIKE 'supervisor%'", (ctx.wf, dim)) is not None
    base_share = pol.human_incumbent_share if human else pol.explore_control_share
    ctl_w = max(base_share, 1.0 / k)
    arm_share = (1 - ctl_w) / (k - 1)
    n_exp = den_per_day(ctx) * arm_share * ctx.days_left * 0.5
    if n_exp < pol.min_trials_arm:
        return []  # the scenario is too short / too quiet for this test to ever reach a verdict
    target = explore_dist(opts, ctl, base_share)
    if cfgutil.tv(cur_def, target) < 0.05:
        return []
    ev_ = {"control": ctl, "options": opts, "den_per_day": round(den_per_day(ctx)),
           "expected_trials_per_arm": round(n_exp), "history_note": "history has no variant variation; no priors on options",
           "incumbent_chosen_by_supervisor": human}
    return [Intent(ctx.okey("explore", dim, ctl, target), "explore", ctx.wf, (dim,),
                   {"allocations": {"default": {dim: target}}},
                   f"Test {dim} options {', '.join(o for o in opts if o != ctl)} against {ctl}",
                   f"Start a randomised {dim} test: incumbent {ctl} keeps {target[ctl]:.0%}; the rest is split across "
                   f"{k - 1} alternatives. Expected ~{n_exp:.0f} {ctx.primary} trials per arm before the scenario ends.",
                   ev_, expected_rel_lift=0.0, confidence=0.5,
                   exp_update={"dims": {dim: {"scopes": {"default": {"phase": "EXPLORING", "control": ctl, "start_ver": "$V"}}}}})]


def _decide(ctx: WfCtx, counts: dict, opts: list[str], ctl: str, retired: dict):
    """Per-arm verdicts against the control within one scope."""
    pol, prior = ctx.pol, ctx.prior
    arms = [o for o in opts if o != ctl and ev.totals(counts, o)[0] > 0]
    m = max(len(arms), 1)
    need = 1.0 - pol.tail_prob / m  # Bonferroni over the challengers compared with this control
    rows, win, harm = {}, [], []
    for o in arms:
        c = ev.stratified(counts, o, ctl, ctx.primary, prior)
        if c is None or min(c.n_arm, c.n_ctl) < pol.min_trials_arm:
            rows[o] = {"status": "insufficient", "n_arm": c.n_arm if c else 0, "n_ctl": c.n_ctl if c else 0}
            continue
        dmin, dh = pol.min_relative_lift * c.rate_ctl, pol.harm_relative_drop * c.rate_ctl
        p_win, p_harm = c.p_greater(dmin), 1.0 - c.p_greater(-dh)
        row = {**_contrast_row(c), "p_lift_gt_min": round(p_win, 4), "p_harm": round(p_harm, 4), "need": round(need, 4)}
        if p_harm >= pol.harm_confidence:
            row["status"] = "harmful"
            harm.append(o)
        elif p_win >= need and (retired.get(o, -10**9) + pol.retire_minutes < ctx.minute):
            ok, g = guardrail_ok(ctx, counts, o, ctl)
            row["guardrail"] = g
            row["status"] = "winner" if ok else "guardrail_blocked"
            if ok:
                win.append((c.lower(1 - pol.tail_prob), o))  # rank by lower credible bound: damps winner's curse
        else:
            row["status"] = "undecided"
        rows[o] = row
    return rows, sorted(win, reverse=True), harm


def _evaluate_exploring(ctx: WfCtx, dim: str, st: dict) -> list[Intent]:
    pol, opts = ctx.pol, ctx.spec["options"][dim]
    ds = st["scopes"]["default"]
    ctl = ds["control"]
    counts = ev.arm_counts(ctx.store, ctx.wf, dim, min_ver=ds["start_ver"], cohs=["default"])
    rows, win, harm = _decide(ctx, counts, [o for o in opts if o not in st["dropped"]], ctl, st["retired"])
    cur = cfgutil.dist(ctx.cfg, "default", dim)
    patch: dict = {"allocations": {}}
    upd_scopes: dict = {}
    cohorts_add: dict = {}
    dims_note = {"verdicts": rows, "control": ctl}
    a0 = ctl
    kinds = []
    if win:
        # First-look winners are biased upward (maximum of several noisy arms), so the first move is provisional: the
        # winner gets half the traffic, the control and every challenger that has not been ruled out keep the rest.
        # Full promotion happens only after fresh post-promotion data confirms it (see _confirm).
        w = win[0][1]
        a0 = w
        live = [o for o in opts if o not in (w, ctl) and o not in harm and o not in st["dropped"]]
        rest = 1 - pol.provisional_share
        prov = {w: pol.provisional_share, ctl: rest / 2, **{o: rest / 2 / len(live) for o in live}} if live else {w: 1 - rest / 2, ctl: rest / 2}
        patch["allocations"]["default"] = {dim: cfgutil.clean_dist(prov)}
        upd_scopes["default"] = {"phase": "CONFIRMING", "winner": w, "control": ctl, "start_ver": "$V",
                                 "promo_minute": ctx.minute, "promo_lift": rows[w]["diff"]}
        kinds.append("promote")
    elif harm:
        target = cfgutil.clean_dist({o: wgt for o, wgt in cur.items() if o not in harm})
        if len(target) >= 2 and cfgutil.tv(cur, target) > 0.02:
            patch["allocations"]["default"] = {dim: target}
            kinds.append("harm_stop")
    c_int = _cohort_candidates(ctx, dim, st, ds, a0, set(harm) | set(st["dropped"]))
    if c_int:
        patch["cohorts_add"] = [{"id": cid, "where": w} for cid, (w, _, _) in c_int.items()]
        for cid, (w, dist, evd) in c_int.items():
            patch["allocations"].setdefault(cid, {})[dim] = dist
            cohorts_add[cid] = (w, evd)
            upd_scopes[cid] = {"phase": "PROMOTED", "winner": cfgutil.modal(dist), "control": ctl, "start_ver": "$V",
                               "promo_minute": ctx.minute, "promo_lift": max(evd["diff"], 0)}
        kinds.append("cohort")
    if not kinds:
        return []
    if not patch["allocations"]:
        patch.pop("allocations")
    dry = {}
    if "default" in patch.get("allocations", {}):
        dry["default"] = replay(counts, ["default"], ctx.primary, cur, patch["allocations"]["default"][dim], ctl, ctx.prior)
    for cid, (_, _, e) in c_int.items():
        dry[cid] = {"method": "recorded randomised arms in this slice", "kpi": ctx.primary, "best": e["best"], "vs": e["vs"],
                    "expected_old": e["raw"]["rate_ctl"], "expected_new": e["raw"]["rate_arm"], "delta": e["raw"]["diff"], "n_arm": e["raw"]["n_arm"], "n_ctl": e["raw"]["n_ctl"]}
    lift = max([rows[w_]["diff"] / max(rows[w_]["rate_ctl"], 1e-6) for _, w_ in win] or [0.0])
    summary_bits = []
    if "promote" in kinds:
        summary_bits.append(f"Provisionally promote {dim} {a0} (+{rows[a0]['diff']:.3f} abs {ctx.primary}; to be confirmed on fresh data)")
    if "harm_stop" in kinds:
        summary_bits.append(f"Stop harmful {dim} options {harm}")
    if "cohort" in kinds:
        summary_bits.append(f"Tailor {dim} for cohorts {', '.join(cohorts_add)}")
    conf = rows[a0]["p_lift_gt_min"] if win else max([e[2]["p_win"] for e in c_int.values()] or [0.5])
    return [Intent(ctx.okey("+".join(kinds), dim, patch, ds["start_ver"]), "+".join(kinds), ctx.wf, (dim,) if patch else (),
                   patch, "; ".join(summary_bits),
                   "Randomised test result: " + "; ".join(summary_bits) + f". Control {ctl} keeps its share so the "
                   "result can be confirmed and later decay detected.",
                   {**dims_note, "cohorts": {c: e for c, (_, _, e) in c_int.items()}},
                   expected_rel_lift=lift if lift else max([e[2]["diff"] / max(ctx.prior, 1e-6) for e in c_int.values()] or [0]),
                   pop_share=1.0 if win else sum(e[2]["share"] for e in c_int.values()), confidence=conf,
                   protective=("promote" not in kinds and "cohort" not in kinds), urgent=("harm_stop" in kinds),
                   exp_update={"dims": {dim: {"scopes": upd_scopes,
                                              "dropped": {o: ctx.minute for o in harm if "harm_stop" in kinds}}},
                               "cohorts_add": cohorts_add}, dry_run=dry)]


def _confirm(ctx: WfCtx, dim: str, st: dict) -> list[Intent]:
    """Second, independent look at a provisional winner using only data collected since the provisional split."""
    pol, opts = ctx.pol, ctx.spec["options"][dim]
    ds = st["scopes"]["default"]
    w, ctl = ds["winner"], ds["control"]
    counts = ev.arm_counts(ctx.store, ctx.wf, dim, min_ver=ds["start_ver"], cohs=["default"])
    c = ev.stratified(counts, w, ctl, ctx.primary, ctx.prior)
    if c is None or min(c.n_arm, c.n_ctl) < pol.min_trials_arm:
        return []
    p_pos, p_bar = c.p_greater(0.0), c.p_greater(pol.min_relative_lift * c.rate_ctl)
    evd = {"fresh": _contrast_row(c), "p_better_than_control": round(p_pos, 4), "p_clears_practical_lift": round(p_bar, 4),
           "first_look_lift": ds.get("promo_lift"), "confirm_prob": pol.confirm_prob}
    ok, g = guardrail_ok(ctx, counts, w, ctl)
    if p_pos >= pol.confirm_prob and ok:
        target = cfgutil.clean_dist({w: 1 - pol.holdout_share, ctl: pol.holdout_share})
        return [Intent(ctx.okey("confirm", dim, w), "confirm", ctx.wf, (dim,), {"allocations": {"default": {dim: target}}},
                       f"Confirm {dim} {w}: fresh data +{c.diff:.3f} abs {ctx.primary} (first look +{ds.get('promo_lift', 0):.3f})",
                       "The provisional winner still beats the control on data collected after it was chosen; moving to a "
                       f"{1 - pol.holdout_share:.0%}/{pol.holdout_share:.0%} split with the control as holdout.",
                       {**evd, "guardrail": g}, expected_rel_lift=c.diff / max(c.rate_ctl, 1e-6), confidence=p_pos,
                       dry_run=replay(counts, ["default"], ctx.primary, cfgutil.dist(ctx.cfg, "default", dim), target, ctl, ctx.prior),
                       exp_update={"dims": {dim: {"scopes": {"default": {"phase": "PROMOTED", "start_ver": "$V"}}}}})]
    if p_pos <= 1 - pol.confirm_prob:  # symmetric with confirmation: withdraw only on equally strong evidence against
        live = [o for o in opts if o != w and o not in st["dropped"]]
        target = explore_dist(live, ctl, pol.explore_control_share) if len(live) >= 2 else {ctl: 1.0}
        return [Intent(ctx.okey("unconfirmed", dim, w), "unconfirmed", ctx.wf, (dim,), {"allocations": {"default": {dim: target}}},
                       f"Withdraw provisional {dim} {w}: fresh data does not support the first-look lift",
                       f"Fresh lift {c.diff:+.3f}; P(better than control) {p_pos:.2f}. The first-look estimate was selection-biased; "
                       "back to exploring the remaining options.", evd, protective=True, urgent=True, confidence=0.8,
                       exp_update={"dims": {dim: {"scopes": {"default": {"phase": "EXPLORING", "control": ctl, "start_ver": "$V"}},
                                                  "retired": {w: ctx.minute}}}})]
    return []


def _axis(ctx: WfCtx) -> str | None:
    return ctx.store.get(f"axis:{ctx.wf}")


def _cohort_candidates(ctx: WfCtx, dim: str, st: dict, ds: dict, a0: str, bad_opts: set) -> dict:
    """{cohort_id: (where, allocation, evidence)} for single-value cohorts where some option beats the workflow-wide
    action `a0` inside that slice. Same rule as the workflow-level decision, with Bonferroni over every
    (slice, option) pair examined, so looking at more slices makes each verdict harder to reach."""
    pol, opts, ctl = ctx.pol, ctx.spec["options"][dim], ds["control"]
    existing = {c["id"] for c in ctx.cfg["cohorts"]}
    if len(existing) >= pol.max_cohorts:
        return {}
    base = ev.arm_counts(ctx.store, ctx.wf, dim, min_ver=ds["start_ver"], cohs=["default"])
    tot_conn = ev.totals(base)[1]
    axis = _axis(ctx)
    cands = []  # (feature, value, option, contrast, share)
    for F in ([axis] if axis else FEATURES):
        for r in ctx.store.q("SELECT DISTINCT sv FROM agg WHERE wf=? AND dim=? AND sl=?", (ctx.wf, dim, F)):
            v = r["sv"]
            if v == "?" or f"{F}={v}" in existing:
                continue
            cv = ev.arm_counts(ctx.store, ctx.wf, dim, min_ver=ds["start_ver"], cohs=["default"], sl=F, sv=v)
            share = ev.totals(cv)[1] / max(tot_conn, 1)
            if share < pol.min_cohort_share:
                continue
            for o in opts:
                if o == a0 or o in bad_opts:
                    continue
                c = ev.stratified(cv, o, a0, ctx.primary, ctx.prior)
                if c and min(c.n_arm, c.n_ctl) >= pol.min_trials_slice:
                    cands.append((F, v, o, c, share))
    if not cands:
        return {}
    need = 1.0 - pol.tail_prob / len(cands)
    best: dict = {}
    for F, v, o, c, share in cands:
        p_win = c.p_greater(pol.min_relative_lift * c.rate_ctl)
        if p_win >= need and c.diff >= pol.min_cohort_gain and ((F, v) not in best or c.diff > best[(F, v)][3].diff):
            best[(F, v)] = (F, v, o, c, share, p_win)
    if not best:
        return {}
    score: dict = {}
    for (F, _), x in best.items():
        score[F] = score.get(F, 0.0) + x[4] * x[3].diff
    F = max(score, key=score.get)
    if axis is None:
        ctx.store.put(f"axis:{ctx.wf}", F)
    out = {}
    chosen = sorted((x for (f, _), x in best.items() if f == F), key=lambda x: -x[3].diff)[: pol.max_cohorts - len(existing)]
    for _, v, o, c, share, p_win in chosen:
        hold = a0 if a0 != o else ctl
        out[f"{F}={v}"] = ({F: [v]}, cfgutil.clean_dist({o: 1 - pol.holdout_share, hold: pol.holdout_share}),
                           {"feature": F, "value": v, "best": o, "vs": a0, "diff": round(c.diff, 4), "p_win": round(p_win, 4),
                            "share": round(share, 3), "candidates_examined": len(cands), "bonferroni_need": round(need, 4),
                            "raw": _contrast_row(c)})
    return out


def _watch_decay(ctx: WfCtx, dim: str, st: dict) -> list[Intent]:
    """Compare each promoted winner against its holdout over a rolling window; roll back when it stops winning."""
    pol, opts = ctx.pol, ctx.spec["options"][dim]
    out_patch: dict = {"allocations": {}}
    upd: dict = {}
    reasons, evd = [], {}
    for scope, s in st["scopes"].items():
        if s.get("phase") != "PROMOTED" or s["winner"] == s["control"]:
            continue
        if scope != "default" and scope not in {c["id"] for c in ctx.cfg["cohorts"]}:
            continue
        w, ctl = s["winner"], s["control"]
        cur = cfgutil.eff(ctx.cfg, scope, dim)
        if w not in cur or ctl not in cur:
            continue
        first = ctx.store.one("SELECT MIN(blk) b FROM agg WHERE wf=? AND dim=? AND coh=? AND ver>=?", (ctx.wf, dim, scope, s["start_ver"]))["b"]
        if first is None or ctx.blk_now - first < pol.decay_window_blocks:
            continue  # the decay test is defined over a full window of post-promotion data
        recent = ev.arm_counts(ctx.store, ctx.wf, dim, min_ver=s["start_ver"], min_blk=ctx.blk_now - pol.decay_window_blocks, cohs=[scope])
        whole = ev.arm_counts(ctx.store, ctx.wf, dim, min_ver=s["start_ver"], cohs=[scope])
        cr, cw = ev.stratified(recent, w, ctl, ctx.primary, ctx.prior), ev.stratified(whole, w, ctl, ctx.primary, ctx.prior)
        if cr is None or min(cr.n_arm, cr.n_ctl) < pol.min_trials_arm:
            continue  # a demotion needs at least the sample a promotion needs; otherwise promote/demote can flap on noise
        # A promoted arm must keep clearing the bar it was promoted on (practical lift over its own holdout). The lift
        # measured at promotion is not used: it is a maximum over noisy arms and biased upward.
        p_still = cr.p_greater(pol.min_relative_lift * cr.rate_ctl)
        p_harm = 1.0 - (cw.p_greater(-pol.harm_relative_drop * cw.rate_ctl) if cw else 1.0)
        evd[scope] = {"recent": _contrast_row(cr), "p_still_clears_practical_lift": round(p_still, 3),
                      "whole": _contrast_row(cw) if cw else None, "window_blocks": pol.decay_window_blocks}
        if p_still <= pol.decay_p or p_harm >= pol.harm_confidence:
            others = [o for o in opts if o not in (w, ctl) and o not in st['dropped']]
            if scope == "default":
                target = cfgutil.clean_dist({ctl: 0.7, **{o: 0.3 / len(others) for o in others}}) if others else {ctl: 1.0}
                out_patch["allocations"]["default"] = {dim: target}
                upd[scope] = {"phase": "EXPLORING", "control": ctl, "start_ver": "$V"}
            else:
                out_patch["allocations"][scope] = {dim: None}
                upd[scope] = None
            reasons.append(f"{dim}={w} in {scope}: recent lift {cr.diff:+.3f} (P still clears the {pol.min_relative_lift:.0%} practical bar: {p_still:.2f})")
    if not reasons:
        return []
    return [Intent(ctx.okey("rollback", dim, sorted(upd)), "rollback", ctx.wf, (dim,), out_patch,
                   "Roll back decayed winner: " + "; ".join(reasons),
                   "Winner no longer beats its holdout over the recent window; reverting to the control and re-exploring.",
                   evd, protective=True, urgent=True, confidence=0.8, expected_rel_lift=0.02,
                   exp_update={"dims": {dim: {"scopes": upd, "retired": {s_["winner"]: ctx.minute for sc, s_ in st["scopes"].items() if sc in upd}}}})]


# --------------------------------------------------------------------------------------- caller id
def did_bad_set(store: Store, wf: str) -> dict:
    return store.get(f"did_bad:{wf}", {})


def plan_caller_id(ctx: WfCtx, last_change_minute: int) -> list[Intent]:
    pol = ctx.pol
    known_bad = did_bad_set(ctx.store, ctx.wf)
    opts = ctx.spec["options"]["caller_id"]
    if len(opts) < 2 or ctx.minute - last_change_minute < pol.did_min_interval:
        return []
    recent = ev.arm_counts(ctx.store, ctx.wf, "caller_id", min_blk=ctx.blk_now - pol.did_window_blocks)
    prior = ev.arm_counts(ctx.store, ctx.wf, "caller_id", min_blk=ctx.blk_now - 28, max_blk=ctx.blk_now - pol.did_window_blocks)
    cur = cfgutil.dist(ctx.cfg, "default", "caller_id")
    stat = {}
    for o in opts:
        d, c, _ = ev.totals(recent, o)
        d0, c0, _ = ev.totals(prior, o)
        stat[o] = {"dials": d, "conn": c, "rate": c / d if d else None, "base_dials": d0, "base_rate": c0 / d0 if d0 else None}
    tested = [o for o in opts if stat[o]["dials"] >= pol.did_min_dials and o not in known_bad]
    bad, notes = [], {}
    # a previously flagged ID stays at its floor until a longer window shows it back in line with its siblings
    recovered = []
    for o, since in known_bad.items():
        since_counts = ev.arm_counts(ctx.store, ctx.wf, "caller_id", min_blk=since // ev.BLK)
        d, c, _ = ev.totals(since_counts, o)
        sib = [x for x in opts if x != o and x not in known_bad]
        sd_ = sum(ev.totals(since_counts, x)[0] for x in sib)
        sc_ = sum(ev.totals(since_counts, x)[1] for x in sib)
        if d >= 300 and sd_ and c / d >= 0.9 * sc_ / sd_ and -stats.two_prop_z(c, d, sc_, sd_) < 1.0:
            recovered.append(o)
    for o in tested:
        others = [x for x in tested if x != o]
        if not others:
            continue
        ref_c = sum(stat[x]["conn"] for x in others)
        ref_d = sum(stat[x]["dials"] for x in others)
        ref = ref_c / ref_d
        r = stat[o]["rate"]
        z = -stats.two_prop_z(stat[o]["conn"], stat[o]["dials"], ref_c, ref_d)
        thr = stats.zinv(1 - pol.did_tail_prob / len(tested))
        notes[o] = {"rate": round(r, 4), "sibling_rate": round(ref, 4), "z_below_siblings": round(z, 2)}
        if z >= thr and r <= (1 - pol.did_relative_drop) * ref:
            bad.append(o)
    still_bad = [o for o in known_bad if o not in recovered]
    bad = bad + [o for o in still_bad if o not in bad]
    # An ID without enough data is unmeasured, not healthy: it stays at the probe share until it has been judged.
    untested = [o for o in opts if o not in tested and o not in bad]
    healthy = [o for o in opts if o not in bad]
    if not healthy:
        return []
    probe = {o: pol.did_probe_share for o in untested}
    floor = {o: pol.did_floor_share for o in bad}
    rest = 1.0 - sum(probe.values()) - sum(floor.values())
    keep = [o for o in healthy if o not in probe]
    if not keep:
        return []
    target = cfgutil.clean_dist({**{o: rest / len(keep) for o in keep}, **probe, **floor}, floor=0.0)
    if cfgutil.tv(cur, target) < 0.08:
        return []
    rep = _did_replay(stat, cur, target)
    why = []
    if bad:
        why.append(f"degraded caller IDs {bad} (pickup well below sibling IDs)")
    if untested:
        why.append(f"probe untested IDs {untested} at {pol.did_probe_share:.0%}")
    if not bad and not untested:
        why.append("re-spread volume across healthy caller IDs")
    return [Intent(ctx.okey("caller_id", target), "caller_id", ctx.wf, ("caller_id",), {"allocations": {"default": {"caller_id": target}}},
                   "Caller-ID rotation: " + "; ".join(why),
                   "Population-level pickup comparison across concurrent caller IDs (randomised per dial): " + "; ".join(why),
                   {"window_blocks": pol.did_window_blocks, "per_id": notes, "stats": stat, "bad": bad, "untested": untested},
                   expected_rel_lift=max(rep["delta"], 0) / max(ctx.prior, 0.01) if rep.get("delta") else 0.01,
                   confidence=0.9 if bad else 0.6, protective=bool(bad), dry_run=rep,
                   exp_update={"did_bad": {"add": [o for o in bad if o not in known_bad], "remove": recovered}})]


def _did_replay(stat: dict, old: dict, new: dict) -> dict:
    rates = {o: (s["conn"] / s["dials"]) for o, s in stat.items() if s["dials"] >= 50}
    fb = sum(s["conn"] for s in stat.values()) / max(sum(s["dials"] for s in stat.values()), 1)
    r = lambda o: rates.get(o, fb)
    e_old, e_new = sum(w * r(o) for o, w in old.items()), sum(w * r(o) for o, w in new.items())
    return {"method": "replay of recorded per-caller-ID pickup", "kpi": "pickup_rate", "expected_old": round(e_old, 4),
            "expected_new": round(e_new, 4), "delta": round(e_new - e_old, 4),
            "n_per_arm": {o: s["dials"] for o, s in stat.items()}}
