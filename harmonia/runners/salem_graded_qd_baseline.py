"""First slice of the higher-success engine (Harmonia C, proposal
`pivot/harmonia_C_higher_success_engine_2026-05-27.md`).

GOAL: build the *graded orthogonal landscape* for the Salem domain and establish
the random-arm MAP-Elites COVERAGE FRONTIER — the baseline any LLM-mutation arm
must beat. This replaces the band CLIFF (which made the near-miss shell empty and
forced the rank-1 artifact) with a continuous, multi-axis descriptor defined for
ALL candidates, so there is a dense gradient to climb.

Two disciplines carried from the re-audit:
  1. Grade everything continuously — do NOT gate to in-band (no cliff).
  2. MEASURE and report the descriptor correlation matrix; never assert
     orthogonality. (out_of_band ≡ F9 collinearity was the lesson.)

SCOPE / HONESTY: cypari-free reference (numpy roots + sympy), validated against
the Lehmer anchor. This is the CONTROL ARM (random mutation). The LLM arms and
the real prometheus_math battery (on a cypari host) come later. Salem/Lehmer is
the proposal's *negative control* domain (sparse + prior-leaky).
"""
from __future__ import annotations
import json, math, os
import numpy as np

OUT = r"D:\Prometheus\harmonia\tmp\_salem_graded_qd_baseline.json"
DEG = 10                       # Lehmer's degree; Salem numbers densest at low deg
COEFFS = (-2, -1, 0, 1, 2)
BAND = (1.001, 1.18)
SEED = 20260529
RNG = np.random.default_rng(SEED)
ON_CIRCLE_TOL = 1e-3

# ----------------------------- poly utilities ------------------------------
def roots_of(coeffs):
    return np.roots(coeffs)

def mahler(coeffs, r=None):
    if r is None:
        r = roots_of(coeffs)
    return float(abs(coeffs[0]) * np.prod(np.maximum(1.0, np.abs(r))))

# calibration gate (anchor: Lehmer deg-10, M=1.17628081826)
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
assert abs(mahler(LEHMER) - 1.17628081826) < 1e-7, "Mahler off-anchor"

# ------------------------- graded descriptor axes --------------------------
def descriptor(coeffs):
    """Continuous, multi-axis 'distance to Salem structure'. Defined for ALL
    polynomials (no cliff). Salem minimal poly = reciprocal, irreducible, exactly
    one root >1 (+ its reciprocal <1), all others ON the unit circle."""
    c = np.asarray(coeffs, float)
    r = roots_of(coeffs)
    mod = np.abs(r)
    n = len(coeffs)
    log_M = math.log(max(mahler(coeffs, r), 1e-12))
    # reciprocity defect (0 for palindromic)
    recip_defect = float(max(abs(coeffs[i] - coeffs[n - 1 - i]) for i in range(n // 2))) if n > 1 else 0.0
    # roots strictly off the unit circle (Salem -> exactly 2)
    n_off_circle = int(np.sum(np.abs(mod - 1.0) > ON_CIRCLE_TOL))
    # roots strictly outside (Salem -> exactly 1)
    n_outside = int(np.sum(mod > 1.0 + 1e-9))
    # coefficient entropy (structure richness; trivial polys -> low)
    a = np.abs(c); s = a.sum()
    p = a / s if s > 0 else np.ones_like(a) / len(a)
    p = p[p > 0]
    coeff_entropy = float(-np.sum(p * np.log(p)))
    return {
        "log_M": log_M,
        "recip_defect": recip_defect,
        "n_off_circle": float(n_off_circle),
        "n_outside": float(n_outside),
        "coeff_entropy": coeff_entropy,
    }

AXES = ["log_M", "recip_defect", "n_off_circle", "n_outside", "coeff_entropy"]

def salem_proximity(d):
    """Fitness: higher = closer to Salem structure. Dense gradient (no cliff).
    Built from M-in-band + minimal off-circle mass + reciprocity. Deliberately
    NOT a behavior axis (niches must not be a fitness proxy -- Knockout B)."""
    M = math.exp(d["log_M"])
    band_pen = 0.0 if BAND[0] < M < BAND[1] else min(abs(M - BAND[0]), abs(M - BAND[1]))
    off_pen = abs(d["n_off_circle"] - 2.0)      # Salem has exactly 2 off-circle
    return -(2.0 * band_pen + 0.5 * off_pen + 0.25 * d["recip_defect"])

# ------------------------- candidate sampling ------------------------------
def random_poly():
    """Monic degree-DEG integer poly, constant term +/-1 (reciprocal-eligible)."""
    mid = [int(RNG.choice(COEFFS)) for _ in range(DEG - 1)]
    return [1] + mid + [int(RNG.choice([-1, 1]))]

def mutate(coeffs):
    """Random-arm mutation: perturb 1-2 middle coefficients by +/-1 (clamped)."""
    c = list(coeffs)
    for _ in range(int(RNG.integers(1, 3))):
        i = int(RNG.integers(1, DEG))          # middle index
        c[i] = int(np.clip(c[i] + RNG.choice([-1, 1]), min(COEFFS), max(COEFFS)))
    return c

# ---------------------- Phase 1: orthogonality audit -----------------------
def phase1_correlation(n_sample=20000):
    rows = []
    for _ in range(n_sample):
        try:
            rows.append([descriptor(random_poly())[a] for a in AXES])
        except Exception:
            continue
    X = np.array(rows)
    # drop constant columns from corr
    std = X.std(axis=0)
    live = [i for i in range(len(AXES)) if std[i] > 1e-9]
    C = np.corrcoef(X[:, live], rowvar=False)
    return X, live, C

# ----------------------------- Phase 2: QD ---------------------------------
def phase2_map_elites(bx="recip_defect", by="coeff_entropy", n_evals=40000,
                      grid=(20, 20), warmup=4000):
    """MAP-Elites over a 2D behavior descriptor decorrelated from fitness.
    Coverage of this space = the random-arm frontier the LLM arm must beat."""
    bi, byi = AXES.index(bx), AXES.index(by)
    # estimate behavior ranges from a warmup sample
    warm = np.array([[descriptor(random_poly())[a] for a in (bx, by)]
                     for _ in range(warmup)])
    lo, hi = warm.min(axis=0), warm.max(axis=0)
    hi = np.where(hi > lo, hi, lo + 1.0)
    def cell(d):
        u = (np.array([d[bx], d[by]]) - lo) / (hi - lo)
        ix = np.clip((u * np.array(grid)).astype(int), 0, np.array(grid) - 1)
        return (int(ix[0]), int(ix[1]))
    archive = {}   # cell -> (fitness, coeffs, descriptor)
    def consider(coeffs):
        try:
            d = descriptor(coeffs)
        except Exception:
            return
        f = salem_proximity(d)
        k = cell(d)
        if k not in archive or f > archive[k][0]:
            archive[k] = (f, list(coeffs), d)
    for _ in range(warmup):
        consider(random_poly())
    for _ in range(n_evals):
        if archive and RNG.random() < 0.7:
            parent = archive[list(archive.keys())[int(RNG.integers(len(archive)))]][1]
            consider(mutate(parent))
        else:
            consider(random_poly())
    total_cells = grid[0] * grid[1]
    coverage = len(archive) / total_cells
    # quality stats
    fits = np.array([v[0] for v in archive.values()])
    in_band = [v for v in archive.values() if BAND[0] < math.exp(v[2]["log_M"]) < BAND[1]]
    salem_like = [v for v in in_band if v[2]["n_off_circle"] <= 2 and v[2]["recip_defect"] == 0]
    return {
        "behavior_axes": [bx, by], "grid": list(grid), "n_evals": n_evals,
        "cells_filled": len(archive), "total_cells": total_cells,
        "coverage": coverage,
        "fitness_max": float(fits.max()), "fitness_median": float(np.median(fits)),
        "n_in_band_cells": len(in_band), "n_salem_like_cells": len(salem_like),
        "best_elites": sorted(
            ({"fitness": round(v[0], 4), "coeffs": v[1],
              "M": round(math.exp(v[2]["log_M"]), 6),
              "n_off_circle": int(v[2]["n_off_circle"]),
              "recip_defect": v[2]["recip_defect"]}
             for v in archive.values()), key=lambda e: -e["fitness"])[:8],
    }

def main():
    print(f"=== Phase 1: descriptor orthogonality audit (deg {DEG}) ===")
    X, live, C = phase1_correlation()
    names = [AXES[i] for i in live]
    print("live axes:", names)
    print("correlation matrix:")
    print("            " + " ".join(f"{n[:9]:>10s}" for n in names))
    for a, n in enumerate(names):
        print(f"{n[:11]:>11s} " + " ".join(f"{C[a, b]:10.3f}" for b in range(len(names))))
    # flag collinear pairs (the re-audit lesson)
    collin = [(names[a], names[b], round(C[a, b], 3))
              for a in range(len(names)) for b in range(a + 1, len(names))
              if abs(C[a, b]) > 0.9]
    print("COLLINEAR pairs (|corr|>0.9):", collin if collin else "none")

    print(f"\n=== Phase 2: MAP-Elites random-arm baseline ===")
    res = phase2_map_elites()
    for k in ("behavior_axes", "grid", "n_evals", "cells_filled", "total_cells",
              "coverage", "fitness_max", "fitness_median",
              "n_in_band_cells", "n_salem_like_cells"):
        print(f"  {k}: {res[k]}")
    print("  best elites:")
    for e in res["best_elites"]:
        print(f"    f={e['fitness']:+.4f}  M={e['M']:.6f}  off_circle={e['n_off_circle']}  "
              f"recip_defect={e['recip_defect']}  coeffs={e['coeffs']}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"phase1_corr": {"axes": names, "matrix": C.tolist(),
                                   "collinear_pairs": collin},
                   "phase2_map_elites": res}, f, indent=2)
    print(f"\nwrote {OUT}")
    print("\nFRONTIER: coverage above is the random-arm baseline. An LLM-mutation "
          "arm must beat THIS coverage (and the in-band/salem-like cell counts) to "
          "show the near-miss shell is sampled better than by chance.")

if __name__ == "__main__":
    main()
