"""Pure, deterministic statistics. No randomness anywhere: the same counts always give the same decision.

Rates are modelled as Beta posteriors, and differences between arms use the normal approximation to
the posterior difference (valid for the minimum denominators the policy enforces).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

_N = NormalDist()


def phi(z: float) -> float:
    return _N.cdf(z)


def zinv(p: float) -> float:
    return _N.inv_cdf(p)


def beta_post(k: int, n: int, prior_mean: float, prior_strength: float = 4.0) -> tuple[float, float]:
    """Posterior mean and variance of a rate with a Beta(prior_mean*s, (1-prior_mean)*s) prior."""
    a = k + prior_mean * prior_strength
    b = n - k + (1 - prior_mean) * prior_strength
    s = a + b
    return a / s, a * b / (s * s * (s + 1))


@dataclass(frozen=True)
class Contrast:
    diff: float          # arm - control, absolute
    sd: float            # posterior sd of the difference
    n_arm: int
    n_ctl: int
    rate_arm: float
    rate_ctl: float

    def p_greater(self, thr: float = 0.0) -> float:
        return 1.0 - phi((thr - self.diff) / self.sd) if self.sd > 0 else float(self.diff > thr)

    def lower(self, level: float = 0.95) -> float:
        return self.diff - zinv(level) * self.sd


def contrast(arm: tuple[int, int], ctl: tuple[int, int], prior_mean: float, strength: float = 4.0) -> Contrast:
    ma, va = beta_post(arm[0], arm[1], prior_mean, strength)
    mc, vc = beta_post(ctl[0], ctl[1], prior_mean, strength)
    return Contrast(ma - mc, math.sqrt(va + vc), arm[1], ctl[1], ma, mc)


def pool(cs: list[Contrast]) -> Contrast | None:
    """Inverse-variance pooling across strata (config version x cohort). Strata are randomised
    separately, so pooling their contrasts removes allocation-mix confounding (Simpson's paradox)."""
    cs = [c for c in cs if c.sd > 0]
    if not cs:
        return None
    w = [1.0 / (c.sd ** 2) for c in cs]
    W = sum(w)
    d = sum(wi * c.diff for wi, c in zip(w, cs)) / W
    n_arm, n_ctl = sum(c.n_arm for c in cs), sum(c.n_ctl for c in cs)
    ra = sum(c.rate_arm * c.n_arm for c in cs) / max(n_arm, 1)
    rc = sum(c.rate_ctl * c.n_ctl for c in cs) / max(n_ctl, 1)
    return Contrast(d, math.sqrt(1.0 / W), n_arm, n_ctl, ra, rc)


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X~Bin(n,p). Exact for small mean, continuity-corrected normal otherwise."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    p = min(max(p, 1e-12), 1 - 1e-12)
    mean, var = n * p, n * p * (1 - p)
    if var > 30:
        return 1.0 - phi((k - 0.5 - mean) / math.sqrt(var))
    lp, lq = math.log(p), math.log1p(-p)
    cdf = 0.0
    for i in range(k):
        cdf += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq)
    return max(0.0, 1.0 - cdf)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def two_prop_z(k1: int, n1: int, k0: int, n0: int) -> float:
    """One-sided pooled z for p1 > p0 (used for caller-ID and incident detection, not for winners)."""
    if n1 == 0 or n0 == 0:
        return 0.0
    p = (k1 + k0) / (n1 + n0)
    se = math.sqrt(max(p * (1 - p) * (1 / n1 + 1 / n0), 1e-12))
    return (k1 / n1 - k0 / n0) / se
