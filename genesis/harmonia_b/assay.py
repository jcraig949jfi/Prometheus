#!/usr/bin/env python
"""Harmonia B Gen-3B -- the navigability assay. Computes the frozen Q vector.

Every number here is a deterministic function of exactly-enumerated truth
tables. No sampling of the behaviour space, no estimation of a phenotype, no
LLM anywhere. Where an ESTIMAND is a sample rather than a population (the
operator-drawn cells, and the capped sweeps) that is recorded on the row
itself as `estimand`, because the campaign charter forbids interchanging a
site-population statistic with an operator-weighted one.
"""
from __future__ import annotations

import numpy as np

import substrates as S
import mutators as M

DOM = S.DOM
N = S.N


# ------------------------------------------------------------- target battery

def _bits():
    return S.INPUT_COLS            # DOM x N bool, column j = bit j of the index


def build_targets():
    """The frozen battery. Built from standard Boolean families, fixed before
    any substrate was profiled. Order is frozen; names travel with values."""
    X = _bits()
    idx = np.arange(DOM)
    t = {}
    t["T1_PARITY5"] = np.logical_xor.reduce([X[:, j] for j in range(5)])
    t["T2_MAJORITY10"] = X.sum(axis=1) >= 5
    t["T3_THRESH7"] = X.sum(axis=1) >= 7
    # MUX: x0,x1 address one of x2..x5
    addr = X[:, 0].astype(int) + 2 * X[:, 1].astype(int)
    mux = np.zeros(DOM, dtype=bool)
    for a in range(4):
        mux |= (addr == a) & X[:, 2 + a]
    t["T4_MUX"] = mux
    lo = sum(X[:, j].astype(int) << j for j in range(5))
    hi = sum(X[:, 5 + j].astype(int) << j for j in range(5))
    t["T5_CMP"] = lo > hi
    run3 = np.zeros(DOM, dtype=bool)
    for j in range(N - 2):
        run3 |= X[:, j] & X[:, j + 1] & X[:, j + 2]
    t["T6_RUN3"] = run3
    t["T7_RANDBAL"] = _balanced(4242)
    t["T8_INTERVAL"] = (idx >= 300) & (idx < 800)
    t["T9_P1_TARGET"] = S.BlocksPositive().target
    t["T10_N1_TARGET"] = S.SmoothUnreachable().own_target
    return t


def _balanced(seed):
    rng = S.rng_for(seed, 0x7A)
    v = np.zeros(DOM, dtype=bool)
    v[rng.permutation(DOM)[: DOM // 2]] = True
    return v


TARGETS = build_targets()
TARGET_NAMES = list(TARGETS)
TARGET_MAT = np.stack([TARGETS[k] for k in TARGET_NAMES])       # 10 x DOM


def dists_to_targets(f):
    """Vectorised d(f, T) for every target at once."""
    return (TARGET_MAT != f[None, :]).mean(axis=1)


# ------------------------------------------------------------------ neighbours

def neighbours(sub, g, rng, cap_per_site=None, operator=None, n_draws=None):
    """Yield (site, child_genotype). Either the exhaustive sweep or an
    operator-weighted draw -- never silently mixed; the caller records which."""
    if operator is None:
        for site, _val, g2 in M.ExhaustiveSiteSweep.neighbourhood(
                sub, g, rng, cap_per_site=cap_per_site):
            yield site, g2
    else:
        for _ in range(n_draws):
            r = operator(sub, g, rng)
            if r is None:
                yield None, None          # a DECLINE, counted by the caller
                continue
            yield r[1], r[0]


# ------------------------------------------------------------------ the assay

def measure_cell(sub, operator=None, seeds=range(60), cap_per_site=None,
                 n_draws=400, q12_neutral_cap=3, q12_edit_cap=60, seed_key=0):
    """Compute the frozen Q vector for one (substrate x operator) cell.

    operator=None means SWEEP-ALL (site-population estimand).
    Returns (Q, per_target, raw) -- raw carries the counts a reviewer needs to
    recompute every ratio without rerunning anything.
    """
    rng = S.rng_for(seed_key, 0xA5, len(list(seeds)))
    n_edit = 0
    n_declines = 0
    cls = {"NEUTRAL": 0, "SMALL": 0, "LARGE": 0, "DESTRUCTION": 0}
    d_all = []
    # target-relative accumulators, per target
    n_t = len(TARGET_NAMES)
    improve = np.zeros(n_t)
    worsen = np.zeros(n_t)
    equal_nonneutral = np.zeros(n_t)
    improve_mag = np.zeros(n_t)
    reach1 = np.zeros(n_t)          # objects with >=1 improving edit
    base_d = np.zeros(n_t)
    n_obj = 0
    q12_vals = []

    for s in seeds:
        g = sub.sample(int(s))
        f = sub.phenotype(g)
        n_obj += 1
        d0 = dists_to_targets(f)
        base_d += d0
        found = np.zeros(n_t, dtype=bool)
        parent_pheno_ids = set()

        for site, g2 in neighbours(sub, g, rng, cap_per_site, operator, n_draws):
            if g2 is None:
                n_declines += 1
                continue
            f2 = sub.phenotype(g2)
            n_edit += 1
            c = S.r_vec2(f, f2)
            cls[c] += 1
            d = S.d_of(f, f2)
            d_all.append(d)
            if d > 0:
                parent_pheno_ids.add(f2.tobytes())
            d2 = dists_to_targets(f2)
            imp = d2 < d0
            wor = d2 > d0
            improve += imp
            worsen += wor
            equal_nonneutral += (~imp) & (~wor) & (d > 0)
            improve_mag += np.maximum(0.0, d0 - d2)
            found |= imp
        reach1 += found

        # q12: do NEUTRAL neighbours buy options the parent did not have?
        q12_vals.extend(_neutral_option_gain(
            sub, g, f, rng, parent_pheno_ids, q12_neutral_cap, q12_edit_cap,
            operator))

    tot = max(n_edit, 1)
    d_all = np.asarray(d_all) if d_all else np.zeros(0)
    nz = d_all[d_all > 0]
    q1 = cls["NEUTRAL"] / tot
    q4 = float(np.mean((d_all > 0) & (d_all <= S.LOCAL_BAND))) if len(d_all) else 0.0
    per_target = {}
    for j, name in enumerate(TARGET_NAMES):
        nonneutral = tot - cls["NEUTRAL"]
        per_target[name] = {
            "q7_improving_rate": improve[j] / tot,
            "q8_improve_given_nonneutral":
                (improve[j] / nonneutral) if nonneutral else 0.0,
            "q9_mean_improve_magnitude": improve_mag[j] / tot,
            "q10_reach_improve_at1": reach1[j] / max(n_obj, 1),
            "q11_drift": (improve[j] - worsen[j]) / nonneutral if nonneutral else 0.0,
            "q13_baseline_d": base_d[j] / max(n_obj, 1),
            "n_improve": int(improve[j]), "n_worsen": int(worsen[j]),
            "n_equal_nonneutral": int(equal_nonneutral[j]),
        }
    Q = {
        "q1_neutral_rate": q1,
        "q2_destruction_rate": cls["DESTRUCTION"] / tot,
        "q3_band_rate": cls["SMALL"] / tot,
        "q4_middle_mass": q4,
        "q5_median_nonzero_d": float(np.median(nz)) if len(nz) else None,
        "q6_gapped": int(q4 <= 0.05),
        "q12_neutral_option_gain":
            float(np.mean(q12_vals)) if q12_vals else None,
        # target-relative coordinates averaged over the battery; per-target
        # rows always travel with them and are never replaced by these.
        "q7_improving_rate": float(np.mean(
            [per_target[k]["q7_improving_rate"] for k in TARGET_NAMES])),
        "q8_improve_given_nonneutral": float(np.mean(
            [per_target[k]["q8_improve_given_nonneutral"] for k in TARGET_NAMES])),
        "q9_mean_improve_magnitude": float(np.mean(
            [per_target[k]["q9_mean_improve_magnitude"] for k in TARGET_NAMES])),
        "q10_reach_improve_at1": float(np.mean(
            [per_target[k]["q10_reach_improve_at1"] for k in TARGET_NAMES])),
        "q11_drift": float(np.mean(
            [per_target[k]["q11_drift"] for k in TARGET_NAMES])),
        "q13_baseline_d": float(np.mean(
            [per_target[k]["q13_baseline_d"] for k in TARGET_NAMES])),
    }
    raw = {
        "substrate": sub.name,
        "operator": (operator.name if operator is not None else "SWEEP-ALL"),
        "estimand": ("site_population_exhaustive" if operator is None and
                     cap_per_site is None else
                     "site_population_capped" if operator is None else
                     "operator_weighted"),
        "cap_per_site": cap_per_site,
        "n_objects": n_obj, "n_edits": n_edit, "n_declines": n_declines,
        "class_counts": dict(cls),
        "n_q12_samples": len(q12_vals),
    }
    return Q, per_target, raw


def _neutral_option_gain(sub, g, f, rng, parent_ids, n_cap, edit_cap, operator):
    """Fraction of a neutral neighbour's non-neutral consequences that the
    parent could not reach. Capped; caps are recorded on the row."""
    out = []
    neutral_children = []
    for site, val, g2 in M.ExhaustiveSiteSweep.neighbourhood(
            sub, g, rng, cap_per_site=4):
        if len(neutral_children) >= n_cap:
            break
        if np.array_equal(sub.phenotype(g2), f):
            neutral_children.append(g2)
    for g2 in neutral_children:
        seen, novel = 0, 0
        for site3, val3, g3 in M.ExhaustiveSiteSweep.neighbourhood(
                sub, g2, rng, cap_per_site=4):
            if seen >= edit_cap:
                break
            f3 = sub.phenotype(g3)
            if np.array_equal(f3, f):
                continue
            seen += 1
            if f3.tobytes() not in parent_ids:
                novel += 1
        if seen:
            out.append(novel / seen)
    return out
