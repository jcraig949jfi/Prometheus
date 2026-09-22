"""Random-subset null with split-half and Poisson controls (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: the mean-spacing normaliser is imported UNCHANGED
from charon/agents/pollux/daemon.py (_mean_spacing_normalize).  The KS distance
is computed here (ten lines) rather than through
prometheus_math/research/anomaly_surface.py::kolmogorov_smirnov_p because that
function compares ONE sample against a cached named ensemble, not two samples
against each other; scipy.stats.ks_2samp is used for the p-value cross-check
when scipy is importable and the pure-python D is reported regardless.

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_resampling_null.*

This is the statistic block of FRANK-004 (coroner plan CR-001).  It is
GENERIC: it takes a pool of values and two index sets or two value lists and
never loads anything itself.  Calling it on a synthetic pool is a control;
calling it on Mahler subsets is the coroner run and needs HITL approval.
"""
from __future__ import annotations

import importlib
import math
import random
from typing import Optional, Sequence


def ks_distance(x: Sequence[float], y: Sequence[float]) -> float:
    """sup_t |F_x(t) - F_y(t)| over the pooled sample points."""
    xs, ys = sorted(x), sorted(y)
    nx, ny = len(xs), len(ys)
    if nx == 0 or ny == 0:
        return float("nan")
    i = j = 0
    d = 0.0
    while i < nx and j < ny:
        if xs[i] <= ys[j]:
            i += 1
        else:
            j += 1
        d = max(d, abs(i / nx - j / ny))
    return d


def normalised_gaps(values: Sequence[float]) -> list:
    D = importlib.import_module("charon.agents.pollux.daemon")
    return D._mean_spacing_normalize(list(values))


def gap_distance(a_vals: Sequence[float], b_vals: Sequence[float]) -> float:
    """KS distance between the FULL normalised-gap series of two value lists (no truncation)."""
    return ks_distance(normalised_gaps(a_vals), normalised_gaps(b_vals))


def random_subset_null(pool: Sequence[float], n_a: int, n_b: int, *, n_draws: int = 1000, seed: int = 0,
                       disjoint: bool = True) -> list:
    """D between two random same-size subsets of the pool, n_draws times."""
    rng = random.Random(seed)
    pool = list(pool)
    out = []
    for _ in range(n_draws):
        if disjoint and n_a + n_b <= len(pool):
            idx = rng.sample(range(len(pool)), n_a + n_b)
            a = [pool[i] for i in idx[:n_a]]
            b = [pool[i] for i in idx[n_a:]]
        else:
            a = rng.sample(pool, min(n_a, len(pool)))
            b = rng.sample(pool, min(n_b, len(pool)))
        out.append(gap_distance(a, b))
    return out


def p_lower(d_obs: float, null: Sequence[float]) -> float:
    """Fraction of null draws at or below the observed distance (+1 regularised)."""
    null = [v for v in null if not math.isnan(v)]
    if not null:
        return float("nan")
    return (sum(1 for v in null if v <= d_obs) + 1) / (len(null) + 1)


def split_half_control(values: Sequence[float], pool: Sequence[float], *, n_halvings: int = 5, n_draws: int = 1000,
                       seed: int = 0, alpha: float = 0.05 / 9) -> dict:
    """Is a subset judged coincident with a random half of itself at these sizes?"""
    rng = random.Random(seed)
    values = list(values)
    n = len(values)
    h1n, h2n = n // 2, n - n // 2
    if h1n < 3:
        return {"resolvable": False, "reason": "too small to halve", "n": n, "hits": 0, "halvings": []}
    null = random_subset_null(pool, h1n, h2n, n_draws=n_draws, seed=seed + 101)
    halvings = []
    for k in range(n_halvings):
        v = values[:]
        rng.shuffle(v)
        d = gap_distance(v[:h1n], v[h1n:])
        halvings.append({"d": d, "p_lower": p_lower(d, null)})
    hits = sum(1 for h in halvings if h["p_lower"] < alpha)
    return {"resolvable": hits >= 4, "n": n, "hits": hits, "alpha": alpha, "halvings": halvings,
            "null_quantiles": _quantiles(null)}


def poisson_negative_control(a_vals: Sequence[float], n_b: int, pool: Sequence[float], *, n_draws: int = 1000,
                             seed: int = 0) -> dict:
    """Subset A vs an exponential(1) spacing sample of size n_b-1 (Poisson spacing after normalisation).

    The instrument must NOT call this coincident; if it does, a lower-tail p on a real pair is void.
    """
    rng = random.Random(seed)
    gaps = [rng.expovariate(1.0) for _ in range(max(1, n_b - 1))]
    d = ks_distance(normalised_gaps(a_vals), gaps)
    null = random_subset_null(pool, len(a_vals), n_b, n_draws=n_draws, seed=seed + 202)
    p = p_lower(d, null)
    return {"d": d, "p_lower": p, "void_if_below": 0.05, "void": p < 0.05}


def _quantiles(vals: Sequence[float]) -> dict:
    v = sorted(x for x in vals if not math.isnan(x))
    if not v:
        return {}
    q = lambda f: v[min(len(v) - 1, int(f * len(v)))]  # noqa: E731
    return {"min": v[0], "q05": q(0.05), "q50": q(0.5), "q95": q(0.95), "max": v[-1], "n": len(v)}


def scipy_crosscheck(a_vals: Sequence[float], b_vals: Sequence[float]) -> Optional[dict]:
    try:
        from scipy.stats import ks_2samp
    except Exception:  # noqa: BLE001
        return None
    r = ks_2samp(normalised_gaps(a_vals), normalised_gaps(b_vals))
    return {"D": float(r.statistic), "p_two_sided": float(r.pvalue)}


def two_sample_read(a_vals: Sequence[float], b_vals: Sequence[float], pool: Sequence[float], *, seeds=(0,),
                    n_draws: int = 1000, alpha: float = 0.05 / 9) -> dict:
    """The full FRANK-004 read for one pair on caller-supplied values: D, p_lower per seed, both controls."""
    a_vals, b_vals = list(a_vals), list(b_vals)
    d_obs = gap_distance(a_vals, b_vals)
    per_seed = []
    for s in seeds:
        null = random_subset_null(pool, len(a_vals), len(b_vals), n_draws=n_draws, seed=s)
        per_seed.append({"seed": s, "p_lower": p_lower(d_obs, null), "null_quantiles": _quantiles(null)})
    sh_a = split_half_control(a_vals, pool, n_draws=n_draws, seed=seeds[0], alpha=alpha)
    sh_b = split_half_control(b_vals, pool, n_draws=n_draws, seed=seeds[0] + 1, alpha=alpha)
    neg = poisson_negative_control(a_vals, len(b_vals), pool, n_draws=n_draws, seed=seeds[0])
    coincident_all_seeds = all(ps["p_lower"] < alpha for ps in per_seed)
    resolvable = sh_a["resolvable"] and sh_b["resolvable"]
    if not resolvable:
        verdict = "UNRESOLVABLE_AT_THIS_N"
    elif neg["void"]:
        verdict = "VOID_NEGATIVE_CONTROL_COINCIDENT"
    elif coincident_all_seeds:
        verdict = "COINCIDENT_BEYOND_SCALE"
    else:
        verdict = "NOT_COINCIDENT"
    return {
        "n_a": len(a_vals), "n_b": len(b_vals), "d_observed": d_obs, "alpha": alpha,
        "per_seed": per_seed, "split_half": {"a": sh_a, "b": sh_b}, "negative_control": neg,
        "scipy_crosscheck": scipy_crosscheck(a_vals, b_vals), "verdict": verdict,
        "forbidden_inference": "COINCIDENT_BEYOND_SCALE under the unmatched null is not yet 'beyond M-range'; "
                               "the M-matched null is a second read the caller must run with a matched pool.",
    }
