"""Read-side queries over the aggregates. All evidence comes from calls that actually happened."""
from __future__ import annotations

from collections import defaultdict

from . import stats
from .store import Store

BLK = 360


def kpi_of(primary: str, c: tuple[int, int, int]) -> tuple[int, int]:
    """(successes, trials) for a KPI from (dials, conn, eng)."""
    return (c[2], c[1]) if primary == "engagement_rate" else (c[1], c[0])


def other_kpi(primary: str) -> str:
    return "pickup_rate" if primary == "engagement_rate" else "engagement_rate"


def arm_counts(store: Store, wf: str, dim: str, *, min_ver: int = 0, min_blk: int | None = None,
               max_blk: int | None = None, cohs: list[str] | None = None, sl: str = "all", sv: str = ""):
    """{(ver, coh, opt): (dials, conn, eng)} for one lever and one population slice."""
    # INDEXED BY: without ANALYZE statistics SQLite prefers the (wf, blk, ...) primary key, whose cost grows with history.
    sql = ["SELECT ver, coh, opt, SUM(dials) d, SUM(conn) c, SUM(eng) e FROM agg INDEXED BY agg_scan",
           "WHERE wf=? AND dim=? AND sl=? AND sv=? AND ver>=?"]
    args: list = [wf, dim, sl, sv, min_ver]
    if min_blk is not None:
        sql.append("AND blk>=?")
        args.append(min_blk)
    if max_blk is not None:
        sql.append("AND blk<?")
        args.append(max_blk)
    if cohs is not None:
        sql.append(f"AND coh IN ({','.join('?' * len(cohs))})")
        args += cohs
    sql.append("GROUP BY ver, coh, opt")
    return {(r["ver"], r["coh"], r["opt"]): (r["d"], r["c"], r["e"]) for r in store.q(" ".join(sql), args)}


def stratified(counts: dict, opt: str, ctl: str, kpi_primary: str, prior: float, min_trials: int = 30):
    """Pooled contrast of opt vs ctl across (version, cohort) strata that contain both arms."""
    strata: dict = defaultdict(dict)
    for (ver, coh, o), c in counts.items():
        strata[(ver, coh)][o] = c
    parts = []
    for arms in strata.values():
        if opt in arms and ctl in arms:
            a, b = kpi_of(kpi_primary, arms[opt]), kpi_of(kpi_primary, arms[ctl])
            if a[1] >= min_trials and b[1] >= min_trials:
                parts.append(stats.contrast(a, b, prior))
    return stats.pool(parts)


def totals(counts: dict, opt: str | None = None) -> tuple[int, int, int]:
    d = c = e = 0
    for (_, _, o), v in counts.items():
        if opt is None or o == opt:
            d, c, e = d + v[0], c + v[1], e + v[2]
    return d, c, e


def baseline_rate(store: Store, wf: str, primary: str, before_blk: int = 0) -> float:
    """KPI rate from pre-D0 history (any lever's marginal covers every call)."""
    r = store.one("SELECT SUM(dials) d, SUM(conn) c, SUM(eng) e FROM agg WHERE wf=? AND dim='voice' AND sl='all' AND blk<?",
                  (wf, before_blk))
    if not r or not r["d"]:
        return 0.4
    k, n = kpi_of(primary, (r["d"], r["c"], r["e"]))
    return k / n if n else 0.4


def recent_rate(store: Store, wf: str, primary: str, blk_from: int) -> tuple[int, int]:
    r = store.one("SELECT SUM(dials) d, SUM(conn) c, SUM(eng) e FROM agg WHERE wf=? AND dim='voice' AND sl='all' AND blk>=?",
                  (wf, blk_from))
    return kpi_of(primary, (r["d"] or 0, r["c"] or 0, r["e"] or 0))
