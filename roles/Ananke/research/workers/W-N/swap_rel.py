"""W-N T-SWAP-LOWACC: RELATIVE carrier-swap verdict for low-accuracy specimens.

Problem. lens.swap_verdict says FLIP iff hi99(swap acc) < .40. Under complete
transfer of the bit, a mirror-pair swap drives accuracy to 1 - normal, so a
specimen with normal ~.6 can never FLIP and reads CHANCE.

Rule (frozen in PLAN.md s2). Per mirror pair i (the independent unit), pool the
scored trials of the arm: a_i = normal accuracy, s_i = swap accuracy (both over
the SAME world-trials). Let g = a - .5. The three hypotheses are
    FLIP       s = .5 - g   (= 1 - normal)
    CHANCE     s = .5
    NO_EFFECT  s = .5 + g   (= normal)
Decision boundaries sit at the midpoints (z = (s - .5) / g = -1/2, +1/2), written
as LINEAR paired statistics so the CI needs no ratio:
    DF_i = (s_i - .5) + (a_i - .5) / 2      (< 0  <=>  z < -1/2)
    DN_i = (s_i - .5) - (a_i - .5) / 2      (> 0  <=>  z > +1/2)
Pair bootstrap (99 %, 2000 resamples, seed 0 = lens.ci conventions), resampling
pairs jointly for a and s (paired):
    FLIP_REL       hi99(DF) < 0
    NO_EFFECT_REL  lo99(DN) > 0
    CHANCE_REL     lo99(DF) > 0 and hi99(DN) < 0
    INDETERMINATE  otherwise (CI straddles a midpoint: partial transfer or low power)
    NOT_ELIGIBLE   (checked first) lo99(normal) < p_min(P, K): the three
                   hypotheses are not separable at this sample size.
Every verdict needs its CI entirely inside its own cell (burden symmetry: CHANCE
needs a certificate too; a straddle is INDETERMINATE, never CHANCE).

p_min(P, K) is the smallest normal accuracy p (grid .50-1.00 step .01) such that
for every p' >= p, under each truth simulated with ARM-INDEPENDENT noise (the
worst case: pairing buys nothing), mirror-identical pair outcomes (pair value in
{0, 1}; the worst case for averaging) and K independent trials per pair, the rule
returns the correct verdict in >= 80 % of simulations.
"""
from __future__ import annotations

import functools

import numpy as np

N_BOOT = 2000
LEVEL = 0.99
POWER = 0.80
VERDICTS = ("FLIP_REL", "CHANCE_REL", "NO_EFFECT_REL", "INDETERMINATE", "NOT_ELIGIBLE")


# ------------------------------------------------------------------ core rule
def pair_means(per_trial: np.ndarray, trials=None) -> np.ndarray:
    """[M, trials] world-trial scores (0 / .5 / 1, NaN = not scored for this
    arm) -> [P] pair means over the chosen trials (NaN-aware)."""
    x = np.asarray(per_trial, float)
    if trials is not None:
        keep = np.zeros(x.shape[1], bool)
        keep[list(trials)] = True
        x = np.where(keep[None], x, np.nan)
    M = x.shape[0]
    xp = x.reshape(M // 2, 2 * x.shape[1])
    return np.nanmean(xp, 1)


def _boot_idx(P: int, n_boot: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, P, size=(n_boot, P))


def _ci(v: np.ndarray, idx: np.ndarray, level=LEVEL):
    bs = v[..., idx].mean(-1)
    q = (1 - level) / 2
    return v.mean(-1), np.quantile(bs, q, axis=-1), np.quantile(bs, 1 - q, axis=-1)


def rule(a: np.ndarray, s: np.ndarray, idx: np.ndarray | None = None, n_boot=N_BOOT, seed=0) -> dict:
    """Midpoint rule WITHOUT the eligibility gate. a, s: [P] (or [..., P]
    batched) pair means over the same world-trials."""
    a = np.asarray(a, float)
    s = np.asarray(s, float)
    if idx is None:
        idx = _boot_idx(a.shape[-1], n_boot, seed)
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    mF, loF, hiF = _ci(DF, idx)
    mN, loN, hiN = _ci(DN, idx)
    v = np.full(np.shape(mF), "INDETERMINATE", dtype="<U13")
    v = np.where((loF > 0) & (hiN < 0), "CHANCE_REL", v)
    v = np.where(loN > 0, "NO_EFFECT_REL", v)
    v = np.where(hiF < 0, "FLIP_REL", v)
    return {"verdict": v, "DF": (mF, loF, hiF), "DN": (mN, loN, hiN)}


# ------------------------------------------------------------------ attainability
def _simulate(truth: str, p: float, P: int, K: int, n_sim: int, rng) -> tuple:
    a = (rng.random((n_sim, P, K)) < p).mean(-1)
    ps = {"FLIP": 1 - p, "CHANCE": 0.5, "NO_EFFECT": p}[truth]
    s = (rng.random((n_sim, P, K)) < ps).mean(-1)
    return a, s


TRUTH_VERDICT = {"FLIP": "FLIP_REL", "CHANCE": "CHANCE_REL", "NO_EFFECT": "NO_EFFECT_REL"}


def power(p: float, P: int, K: int, n_sim=200, n_boot=N_BOOT, seed=12345) -> dict:
    """Correct-verdict rate of the (ungated) rule under each truth at normal p."""
    rng = np.random.default_rng([seed, P, K, int(round(p * 1000))])
    idx = _boot_idx(P, n_boot, seed)
    out = {}
    for truth, want in TRUTH_VERDICT.items():
        a, s = _simulate(truth, p, P, K, n_sim, rng)
        step = max(1, 2_000_000 // (len(idx) * P))
        v = np.concatenate([rule(a[i:i + step], s[i:i + step], idx=idx)["verdict"]
                            for i in range(0, n_sim, step)])
        out[truth] = float(np.mean(v == want))
    return out


def p_min(P: int, K: int, n_sim=200, power_req=POWER) -> float:
    """Table lookup (out/attain_table.json, same function, precomputed) else compute."""
    import json
    import pathlib
    f = pathlib.Path(__file__).resolve().parent / "out" / "attain_table.json"
    if n_sim == 200 and power_req == POWER and f.exists():
        t = json.loads(f.read_text())
        if f"P{P}_K{K}" in t:
            return t[f"P{P}_K{K}"]["p_min"]
    return _p_min(P, K, n_sim, power_req)


@functools.lru_cache(maxsize=None)
def _p_min(P: int, K: int, n_sim=200, power_req=POWER) -> float:
    """Smallest grid p (.50..1.00 step .01) such that every p' >= p on the
    grid has power >= power_req for all three truths. 1.01 = never."""
    grid = [round(0.5 + 0.01 * i, 2) for i in range(51)]
    ok = [min(power(p, P, K, n_sim=n_sim).values()) >= power_req for p in grid]
    pm = 1.01
    for p, o in zip(reversed(grid), reversed(ok)):
        if not o:
            break
        pm = p
    return pm


# ------------------------------------------------------------------ public verdict
def swap_verdict_rel(normal_pt: np.ndarray, swap_pt: np.ndarray, trials=None, n_boot=N_BOOT,
                     seed=0, pmin: float | None = None) -> dict:
    """normal_pt, swap_pt: [M, trials] world-trial scores, NaN where not scored
    FOR THE ARM. The normal arm is restricted to exactly the world-trials the
    swap arm scored (paired). Returns verdict + CIs + eligibility."""
    n = np.asarray(normal_pt, float)
    sw = np.asarray(swap_pt, float)
    both = ~np.isnan(n) & ~np.isnan(sw)
    if trials is not None:
        keep = np.zeros(n.shape[1], bool)
        keep[list(trials)] = True
        both &= keep[None]
    n = np.where(both, n, np.nan)
    sw = np.where(both, sw, np.nan)
    a, s = pair_means(n), pair_means(sw)
    good = ~np.isnan(a) & ~np.isnan(s)
    a, s = a[good], s[good]
    P = int(len(a))
    K = int(round(both.sum() / max(1, 2 * P)))          # mean scored trials per world
    idx = _boot_idx(P, n_boot, seed)
    nm, nlo, nhi = _ci(a, idx)
    sm, slo, shi = _ci(s, idx)
    pm = p_min(P, max(K, 1)) if pmin is None else pmin
    r = rule(a, s, idx=idx)
    g = nm - 0.5
    out = {"P": P, "K": K, "normal": (float(nm), float(nlo), float(nhi)),
           "swap": (float(sm), float(slo), float(shi)),
           "DF": tuple(float(x) for x in r["DF"]), "DN": tuple(float(x) for x in r["DN"]),
           "z": float((sm - 0.5) / g) if g > 0 else None, "p_min": pm,
           "flip_rate": flip_rate(n, sw)}
    out["eligible"] = bool(nlo >= pm)
    out["verdict"] = str(r["verdict"]) if out["eligible"] else "NOT_ELIGIBLE"
    out["verdict_ungated"] = str(r["verdict"])
    return out


def flip_rate(normal_pt: np.ndarray, swap_pt: np.ndarray) -> dict:
    """Accuracy-free companion: over world-trials where BOTH arms are decisive
    (0 or 1), the fraction whose outcome the swap changed. Complete transfer ->
    1, independent chance -> .5, no effect -> 0, at any normal accuracy. Pair
    bootstrap 99 % CI (pairs with no decisive cells dropped)."""
    n, s = np.asarray(normal_pt, float), np.asarray(swap_pt, float)
    dec = np.isin(n, (0.0, 1.0)) & np.isin(s, (0.0, 1.0))
    ch = np.where(dec, (n != s).astype(float), np.nan)
    M = ch.shape[0]
    num = np.nansum(ch.reshape(M // 2, -1), 1)
    den = dec.reshape(M // 2, -1).sum(1).astype(float)
    ok = den > 0
    num, den = num[ok], den[ok]
    if len(den) == 0:
        return {"f": None, "lo": None, "hi": None, "cells": 0}
    idx = _boot_idx(len(den), N_BOOT, 0)
    bs = num[idx].sum(1) / den[idx].sum(1)
    return {"f": float(num.sum() / den.sum()), "lo": float(np.quantile(bs, 0.005)),
            "hi": float(np.quantile(bs, 0.995)), "cells": int(den.sum())}


def absolute_verdict(normal_pt, swap_pt) -> str:
    """lens.swap_verdict on the same paired pair means (for comparison)."""
    from prometheus.ananke import lens
    n = np.asarray(normal_pt, float)
    sw = np.asarray(swap_pt, float)
    both = ~np.isnan(n) & ~np.isnan(sw)
    a = pair_means(np.where(both, n, np.nan))
    s = pair_means(np.where(both, sw, np.nan))
    g = ~np.isnan(a) & ~np.isnan(s)
    return lens.swap_verdict(a[g], s[g])
