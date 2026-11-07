"""Hallucination incident response: detect -> pick a fix -> validate -> propose -> verify.

The LLM only *suggests* candidates; the choice is made from validation counts with a deterministic rule.
Credits are spent only here, and a reserve is kept so a second incident can still be handled.
"""
from __future__ import annotations

import json
import logging

from . import stats
from .client import SimClient, SimError, SimUnavailable
from .planner import Intent, WfCtx
from .policy import Policy
from .store import Store

log = logging.getLogger("controller.incidents")


class Incidents:
    def __init__(self, store: Store, client: SimClient, pol: Policy):
        self.s, self.c, self.pol = store, client, pol
        self.credits = None

    # ------------------------------------------------------------------ credits
    def spend_ok(self, cost: float) -> bool:
        return self.credits is not None and self.credits >= cost

    def _ledger(self, wf, kind, amount, purpose, balance):
        self.credits = balance
        self.s.run("INSERT INTO credits(minute,wf,kind,amount,balance,purpose) VALUES(?,?,?,?,?,?)",
                   (self.s.now_minute, wf, kind, amount, balance, purpose))

    # ------------------------------------------------------------------ detection
    def _prompt_since(self, ctx: WfCtx) -> tuple[str, int]:
        """Current prompt and the first config version that carried it."""
        rows = self.s.q("SELECT version, config FROM config_versions WHERE wf=? ORDER BY version DESC", (ctx.wf,))
        cur, since = ctx.cfg["prompt_version"], ctx.version
        for r in rows:
            if json.loads(r["config"])["prompt_version"] == cur:
                since = r["version"]
            else:
                break
        return cur, since

    def _flag_rate(self, wf: str, prompt: str | None, min_ver: int = 0, max_ver: int | None = None):
        sql, args = "SELECT SUM(conn) n, SUM(flagged) k FROM qa WHERE wf=? AND ver>=?", [wf, min_ver]
        if prompt:
            sql += " AND prompt=?"
            args.append(prompt)
        if max_ver is not None:
            sql += " AND ver<?"
            args.append(max_ver)
        r = self.s.one(sql, args)
        return (r["k"] or 0), (r["n"] or 0)

    def check(self, ctx: WfCtx) -> dict | None:
        """Open an incident if the flag rate is credibly and materially above baseline on a population of calls."""
        pol = self.pol
        if self.s.one("SELECT 1 FROM incidents WHERE wf=? AND state NOT IN ('RESOLVED','ESCALATED')", (ctx.wf,)):
            return None
        cur, since = self._prompt_since(ctx)
        k, n = self._flag_rate(ctx.wf, cur, since)
        kb, nb = self._flag_rate(ctx.wf, None, 0, since)
        b0 = kb / nb if nb >= 400 else 0.012
        if n < pol.inc_min_conn or k < pol.inc_min_flags:
            self.s.put(f"inc_hit:{ctx.wf}", None)
            return None
        h0 = min(b0 * 1.25 + 0.001, 0.5)
        p = stats.binom_sf(k, n, h0)
        hit = p < pol.inc_alpha and k / n >= pol.inc_rel * b0
        prev = self.s.get(f"inc_hit:{ctx.wf}")
        if not hit:
            self.s.put(f"inc_hit:{ctx.wf}", None)
            return None
        if prev is None or self.s.now_minute - prev < 45:
            if prev is None:
                self.s.put(f"inc_hit:{ctx.wf}", self.s.now_minute)
            return None
        iid = f"inc:{ctx.wf}:{cur}:v{since}"
        if self.s.one("SELECT 1 FROM incidents WHERE id=?", (iid,)):
            return None
        evd = {"prompt": cur, "since_version": since, "flagged": k, "connected": n, "rate": round(k / n, 4),
               "baseline_rate": round(b0, 4), "baseline_n": nb, "h0_rate": round(h0, 4), "p_value": p,
               "rule": f"P(X>={k} | n={n}, p={h0:.4f}) < {pol.inc_alpha} and rate >= {pol.inc_rel}x baseline, on two looks >=45min apart"}
        data = {"bad_prompt": cur, "since_version": since, "candidates": {}, "failed": [], "llm_rounds": 0, "ref": None}
        with self.s.tx():
            self.s.run("INSERT INTO incidents(id,wf,kind,state,opened_minute,evidence,data) VALUES(?,?,?,?,?,?,?)",
                       (iid, ctx.wf, "hallucination", "OPEN", self.s.now_minute, json.dumps(evd), json.dumps(data)))
            self.s.audit("incident_opened", f"hallucination flag rate {k}/{n}={k / n:.1%} vs baseline {b0:.1%} on prompt {cur}",
                         wf=ctx.wf, ref=iid, detail=evd)
        return {"id": iid}

    # ------------------------------------------------------------------ response
    def active(self, wf: str):
        return self.s.one("SELECT * FROM incidents WHERE wf=? AND state NOT IN ('RESOLVED','ESCALATED') ORDER BY opened_minute DESC", (wf,))

    def _save(self, inc, data: dict, state: str | None = None):
        self.s.run("UPDATE incidents SET data=?, state=COALESCE(?,state), closed_minute=CASE WHEN ? IN ('RESOLVED','ESCALATED') THEN ? ELSE closed_minute END WHERE id=?",
                   (json.dumps(data), state, state, self.s.now_minute, inc["id"]))

    def _validate(self, ctx: WfCtx, inc, data: dict, prompt: str, n: int) -> dict | None:
        cost = -(-n // 100)
        if not self.spend_ok(cost):
            self.s.audit("credit_skip", f"validation of {prompt} skipped: {self.credits} credits left", wf=ctx.wf, ref=inc["id"])
            return None
        try:
            r = self.c.validate(ctx.wf, prompt, n)
        except SimError as e:
            self.s.audit("validation_error", f"{prompt}: {e}", wf=ctx.wf, ref=inc["id"])
            return None
        except SimUnavailable:
            return None
        rec = {"run_id": r["validation_run_id"], "n": r["n"], "failures": r["failures"], "pass_rate": r["pass_rate"]}
        with self.s.tx():
            self.s.run("INSERT OR REPLACE INTO validations VALUES(?,?,?,?,?,?,?,?)", (rec["run_id"], ctx.wf, prompt, n,
                       rec["failures"], rec["pass_rate"], self.s.now_minute, inc["id"]))
            self._ledger(ctx.wf, "validation", cost, f"validate {prompt} n={n}", r["credits_remaining"])
            self.s.audit("validation", f"{prompt}: pass_rate {rec['pass_rate']} on n={n} (cost {cost})", wf=ctx.wf,
                         ref=inc["id"], detail=rec)
        return rec

    def _prod_evidence(self, wf: str, prompt: str, b0: float) -> tuple[bool, int]:
        k, n = self._flag_rate(wf, prompt)
        return (n >= 300 and k / n <= b0 * 1.5 + 0.002), n

    def respond(self, ctx: WfCtx) -> list[Intent]:
        inc = self.active(ctx.wf)
        if not inc or inc["state"] not in ("OPEN",):
            return []
        data = json.loads(inc["data"])
        evd = json.loads(inc["evidence"])
        min_pass = ctx.spec["governance"]["min_validation_pass_rate"]
        n = self.pol.inc_val_n
        b0 = evd["baseline_rate"]
        bad = data["bad_prompt"]
        allowed = [p for p in ctx.spec["options"]["prompt_version"] if p != bad and p not in data["failed"]]
        history = [r["config"] for r in self.s.q("SELECT config FROM config_versions WHERE wf=? ORDER BY version DESC", (ctx.wf,))]
        seen: list[str] = []
        for c in history:
            p = json.loads(c)["prompt_version"]
            if p != bad and p not in seen and p in allowed:
                seen.append(p)
        last_good = [p for p in seen if self._prod_evidence(ctx.wf, p, b0)[0]]
        cands = data["candidates"]
        order = last_good + [p for p in cands if p not in last_good and p in allowed]
        for p in order:
            if p not in cands:
                rec = self._validate(ctx, inc, data, p, n)
                if rec:
                    cands[p] = rec
                    self._save(inc, data)
        choice = self._pick(ctx, cands, min_pass, last_good, data, evd, n, inc)
        if choice is None and data["llm_rounds"] < self.pol.inc_max_llm_rounds and self.spend_ok(3):
            try:
                r = self.c.suggest_fixes(ctx.wf, f"hallucination flag rate {evd['rate']:.1%} vs baseline {evd['baseline_rate']:.1%} "
                                                 f"on prompt {bad} over {evd['connected']} connected calls")
                with self.s.tx():
                    self._ledger(ctx.wf, "llm", 3, "suggest-fixes", r["credits_remaining"])
                    self.s.audit("llm_suggestions", "LLM proposed candidates (not trusted; validated below)", wf=ctx.wf,
                                 ref=inc["id"], detail=r)
                data["llm_rounds"] += 1
                for sug in r["suggestions"]:
                    p = sug["prompt_version"]
                    if p in allowed and p not in cands and len([x for x in cands if x not in last_good]) < self.pol.inc_max_new_candidates:
                        rec = self._validate(ctx, inc, data, p, n)
                        if rec:
                            cands[p] = rec
                self._save(inc, data)
                choice = self._pick(ctx, cands, min_pass, last_good, data, evd, n, inc)
            except (SimError, SimUnavailable) as e:
                self.s.audit("llm_error", str(e), wf=ctx.wf, ref=inc["id"])
        if choice is None:
            if data["llm_rounds"] >= self.pol.inc_max_llm_rounds or not self.spend_ok(3):
                self.s.audit("incident_escalated", "no candidate passed validation within credit/round limits; needs a human",
                             wf=ctx.wf, ref=inc["id"], detail={"candidates": cands})
                self._save(inc, data, "ESCALATED")
            return []
        prompt, rec = choice
        data["chosen"] = prompt
        self._save(inc, data, "PROPOSING")
        why = (f"{prompt} validated at pass_rate {rec['pass_rate']} (n={rec['n']}, policy floor {min_pass})"
               + ("; it ran in production before with a flag rate within baseline" if prompt in last_good else ""))
        return [Intent(f"{inc['id']}:fix:{prompt}", "prompt_fix", ctx.wf, ("prompt_version",), {"prompt_version": prompt},
                       f"Replace prompt {bad} with {prompt} (hallucination flag rate {evd['rate']:.1%} vs {evd['baseline_rate']:.1%} baseline)",
                       f"Incident {inc['id']}: {evd['flagged']}/{evd['connected']} connected calls flagged on {bad}. {why}. "
                       f"Validation measures safety only; engagement is verified after rollout.",
                       {"incident": inc["id"], "detection": evd, "validation": rec, "all_candidates": cands},
                       expected_rel_lift=0.5, pop_share=1.0, confidence=0.9, protective=True, urgent=True,
                       validation_run_id=rec["run_id"], dry_run={"method": "validation run (synthetic conversations, safety only)",
                                                                  "n": rec["n"], "pass_rate": rec["pass_rate"],
                                                                  "current_prompt_production_flag_rate": evd["rate"],
                                                                  "engagement_effect": "not measured by validation; verified post-apply"})]

    def _pick(self, ctx, cands, min_pass, last_good, data, evd, n, inc):
        ok = {p: r for p, r in cands.items() if r["pass_rate"] >= min_pass and p not in data["failed"]}
        if not ok:
            return None
        pref = [p for p in ok if p in last_good]
        if pref:
            p = max(pref, key=lambda x: (ok[x]["pass_rate"], x))
            return p, ok[p]
        # untried prompts: must also look credibly safer than the current one on a same-scale reference run
        if data["ref"] is None:
            data["ref"] = self._validate(ctx, inc, data, data["bad_prompt"], n)
            self._save(inc, data)
        ref = data["ref"]
        best = sorted(ok, key=lambda x: (-ok[x]["pass_rate"], x))
        for p in best:
            r = ok[p]
            if ref is None:
                return p, r
            z = stats.two_prop_z(ref["failures"], ref["n"], r["failures"], r["n"])
            if z >= 1.64:
                return p, r
        return None

    # ------------------------------------------------------------------ outcomes
    def on_applied(self, prop: dict, version: int):
        for it in json.loads(prop["intent_keys"] or "[]"):
            if it["kind"] == "prompt_fix":
                iid = it["key"].split(":fix:")[0]
                inc = self.s.one("SELECT * FROM incidents WHERE id=?", (iid,))
                if inc:
                    data = json.loads(inc["data"])
                    data.update(applied_version=version, applied_minute=self.s.now_minute, fix=it["key"].split(":fix:")[1])
                    self._save(inc, data, "VERIFYING")
                    self.s.audit("incident_fix_applied", f"prompt {data['fix']} live at v{version}; verifying", wf=prop["wf"],
                                 ref=iid, proposal_id=prop["pid"])

    def reopen(self, wf: str):
        """A fix that could not be submitted yet (approver offline, budget) goes back to OPEN; validation is kept."""
        inc = self.s.one("SELECT * FROM incidents WHERE wf=? AND state='PROPOSING'", (wf,))
        if inc:
            self._save(inc, json.loads(inc["data"]), "OPEN")

    def on_failed(self, prop: dict, state: str):
        for it in json.loads(prop["intent_keys"] or "[]"):
            if it["kind"] == "prompt_fix":
                inc = self.s.one("SELECT * FROM incidents WHERE id=?", (it["key"].split(":fix:")[0],))
                if inc and inc["state"] == "PROPOSING":
                    self._save(inc, json.loads(inc["data"]), "OPEN")
                    self.s.audit("incident_reopened", f"fix proposal {state}; will re-propose with fresh base", wf=prop["wf"], ref=inc["id"])

    def verify(self, ctx: WfCtx):
        inc = self.s.one("SELECT * FROM incidents WHERE wf=? AND state='VERIFYING'", (ctx.wf,))
        if not inc:
            return
        data, evd = json.loads(inc["data"]), json.loads(inc["evidence"])
        fix, v0 = data["fix"], data["applied_version"]
        k, n = self._flag_rate(ctx.wf, fix, v0)
        if n < 200:
            return
        rate = k / n
        b0 = evd["baseline_rate"]
        if rate <= max(0.5 * evd["rate"], b0 * 1.5 + 0.003):
            # engagement guard: validation said nothing about it
            eng = self.s.one("SELECT SUM(conn) n, SUM(eng) k FROM agg WHERE wf=? AND dim='prompt_version' AND opt=? AND sl='all' AND ver>=?",
                             (ctx.wf, fix, v0))
            base = self.s.one("SELECT SUM(conn) n, SUM(eng) k FROM agg WHERE wf=? AND dim='prompt_version' AND opt!=? AND sl='all' AND ver<?",
                              (ctx.wf, fix, v0))
            note = {}
            if eng["n"] and eng["n"] >= 300 and base["n"] and base["n"] >= 500:
                c = stats.contrast((eng["k"], eng["n"]), (base["k"], base["n"]), base["k"] / base["n"])
                note = {"engagement_new": round(c.rate_arm, 4), "engagement_before": round(c.rate_ctl, 4),
                        "p_drop_gt_7pct": round(1 - c.p_greater(-0.07 * c.rate_ctl), 3)}
                if note["p_drop_gt_7pct"] >= 0.9:
                    data["failed"].append(fix)
                    data["candidates"].pop(fix, None)
                    self.s.audit("incident_engagement_regression", f"{fix} fixed hallucinations but engagement fell: {note}",
                                 wf=ctx.wf, ref=inc["id"], detail=note)
                    self._save(inc, data, "OPEN")
                    return
            self.s.audit("incident_resolved", f"flag rate {k}/{n}={rate:.1%} after fix (was {evd['rate']:.1%}); incident closed",
                         wf=ctx.wf, ref=inc["id"], detail={"after": {"flagged": k, "connected": n}, **note})
            self._save(inc, data, "RESOLVED")
        elif n >= 400:
            data["failed"].append(fix)
            data["candidates"].pop(fix, None)
            self.s.audit("incident_fix_ineffective", f"flag rate still {k}/{n}={rate:.1%} on {fix}", wf=ctx.wf, ref=inc["id"])
            self._save(inc, data, "OPEN")
