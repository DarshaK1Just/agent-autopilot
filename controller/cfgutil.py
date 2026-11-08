"""Helpers over the workflow config document (cohorts / allocations / prompt_version / schedule)."""
from __future__ import annotations

import copy
import hashlib
import json

AGENT_DIMS = ("welcome_message", "voice", "caller_id")
CUSTOMER_FACING = ("welcome_message", "voice", "prompt_version", "cohorts")


def dist(cfg: dict, cohort: str, dim: str) -> dict[str, float]:
    return (cfg["allocations"].get(cohort) or {}).get(dim) or cfg["allocations"]["default"][dim]


def eff(cfg: dict, k: str, dim: str) -> dict[str, float]:
    return dist(cfg, k, dim) if _has(cfg, k) else dist(cfg, "default", dim)


def tv(a: dict, b: dict) -> float:
    return 0.5 * sum(abs(a.get(o, 0.0) - b.get(o, 0.0)) for o in sorted(set(a) | set(b)))


def changed_dims(old: dict, new: dict) -> list[str]:
    ch = []
    if old.get("cohorts", []) != new.get("cohorts", []):
        ch.append("cohorts")
    keys = set(old["allocations"]) | set(new["allocations"])
    for dim in AGENT_DIMS:
        if any(tv(eff(old, k, dim), eff(new, k, dim)) > 1e-9 for k in keys):
            ch.append(dim)
    if old.get("prompt_version") != new.get("prompt_version"):
        ch.append("prompt_version")
    if old.get("schedule") != new.get("schedule"):
        ch.append("schedule")
    return ch


def max_shift(old: dict, new: dict) -> float:
    keys = {"default"} | {c["id"] for c in old.get("cohorts", [])} | {c["id"] for c in new.get("cohorts", [])}
    worst = 0.0
    for k in keys:
        for dim in AGENT_DIMS:
            worst = max(worst, tv(eff(old, k, dim), eff(new, k, dim)))
    return worst


def _has(cfg: dict, k: str) -> bool:
    return k == "default" or k in {c["id"] for c in cfg.get("cohorts", [])}


def clean_dist(d: dict[str, float], floor: float = 0.01) -> dict[str, float]:
    d = {o: w for o, w in d.items() if w >= floor}
    s = sum(d.values())
    out = {o: round(w / s, 4) for o, w in d.items()}
    drift = round(1.0 - sum(out.values()), 4)
    if drift:
        top = max(out, key=out.get)
        out[top] = round(out[top] + drift, 4)
    return out


def modal(d: dict[str, float]) -> str:
    return max(sorted(d), key=lambda o: d[o])


def fingerprint(cfg: dict) -> str:
    return hashlib.sha1(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]


def apply_patch(cfg: dict, patch: dict) -> dict:
    """Return cfg with a declarative planner patch applied. Unrelated keys (including a supervisor's) are untouched."""
    new = copy.deepcopy(cfg)
    for cid in patch.get("cohorts_remove", []):
        new["cohorts"] = [c for c in new["cohorts"] if c["id"] != cid]
        new["allocations"].pop(cid, None)
        new["schedule"]["hour_weights"].pop(cid, None)
    have = {c["id"] for c in new["cohorts"]}
    for c in patch.get("cohorts_add", []):
        if c["id"] not in have:
            new["cohorts"].append(c)
    for coh, dims in patch.get("allocations", {}).items():
        for dim, d in dims.items():
            if d is None:
                if coh != "default":
                    (new["allocations"].get(coh) or {}).pop(dim, None)
            else:
                new["allocations"].setdefault(coh, {})[dim] = d
    for coh in [k for k, v in new["allocations"].items() if k != "default" and not v]:
        del new["allocations"][coh]
    if "prompt_version" in patch:
        new["prompt_version"] = patch["prompt_version"]
    for coh, hw in patch.get("hour_weights", {}).items():
        if hw is None:
            new["schedule"]["hour_weights"].pop(coh, None)
        else:
            new["schedule"]["hour_weights"][coh] = hw
    return new


def diff(old: dict, new: dict) -> dict:
    out: dict = {}
    oc, nc = {c["id"]: c["where"] for c in old["cohorts"]}, {c["id"]: c["where"] for c in new["cohorts"]}
    if oc != nc:
        out["cohorts"] = {"added": {k: v for k, v in nc.items() if k not in oc},
                          "removed": [k for k in oc if k not in nc]}
    for k in sorted(set(old["allocations"]) | set(new["allocations"])):
        for dim in AGENT_DIMS:
            if k != "default" and dim not in (old["allocations"].get(k) or {}) and dim not in (new["allocations"].get(k) or {}):
                continue  # inherited from default; the default entry already shows the change
            a, b = eff(old, k, dim), eff(new, k, dim)
            if tv(a, b) > 1e-9:
                out[f"allocations.{k}.{dim}"] = {"from": a, "to": b}
    if old["prompt_version"] != new["prompt_version"]:
        out["prompt_version"] = {"from": old["prompt_version"], "to": new["prompt_version"]}
    if old["schedule"] != new["schedule"]:
        ow, nw = old["schedule"]["hour_weights"], new["schedule"]["hour_weights"]
        out["schedule.hour_weights"] = {k: {"from": ow.get(k), "to": nw.get(k)}
                                        for k in sorted(set(ow) | set(nw)) if ow.get(k) != nw.get(k)}
    return out
