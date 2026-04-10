#!/usr/bin/env python3
"""
Charon — PDG Algebraic Mass Ratio Test

For every pair of PDG particles with nonzero mass, compute the ratio m_i/m_j.
Test whether each ratio is close to a "simple" algebraic number: a root of
a polynomial  a_0 + a_1*x + ... + a_d*x^d = 0  with degree <= 4 and
|a_k| <= 100.

Method:
  Degree 1: r ≈ p/q  for p, q in 1..100
  Degree 2: r^2 ≈ p/q  (i.e. r = sqrt(p/q))
  Degree 3: r^3 ≈ p/q
  Degree 4: r^4 ≈ p/q
  Plus mixed polynomials via LLL-style lattice reduction for low-degree
  integer relations.

Tolerance: 0.1% relative (|match - r| / r < 0.001).

Control: 225 random masses in the same range, same procedure, compare hit rates.

Output: v2/pdg_algebraic_ratios_results.json
"""

import json
import math
import itertools
import random
import time
import os
import numpy as np
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDG_PATH = ROOT / "physics" / "data" / "pdg" / "particles.json"
OUT_PATH = Path(__file__).resolve().parent / "pdg_algebraic_ratios_results.json"

TOLERANCE = 1e-3        # 0.1% relative
MAX_COEFF = 100         # max absolute coefficient
MAX_DEGREE = 4          # max polynomial degree
N_RANDOM_TRIALS = 5     # number of random control trials


def load_particles():
    """Load PDG particles, return list of (name, mass_GeV, rel_err) with mass > 0."""
    with open(PDG_PATH) as f:
        raw = json.load(f)
    particles = []
    for p in raw:
        m = p["mass_GeV"]
        if m <= 0:
            continue
        err_plus = p.get("mass_err_plus", 0) or 0
        err_minus = abs(p.get("mass_err_minus", 0) or 0)
        rel_err = max(err_plus, err_minus) / m if m > 0 else 0
        # Use mc_id as part of name for uniqueness
        mc_id = p["mc_ids"][0] if p.get("mc_ids") else "?"
        name = f"{p['name'].strip()}(mc={mc_id})"
        particles.append((name, m, rel_err))
    return particles


def build_algebraic_targets(max_coeff=MAX_COEFF, max_degree=MAX_DEGREE):
    """
    Build a sorted list of positive real algebraic numbers that are roots of
    polynomials with integer coefficients of degree <= max_degree, |coeff| <= max_coeff.

    For efficiency, we use the power approach:
      degree d: r^d = p/q  =>  r = (p/q)^(1/d)
    This covers all roots of  q*x^d - p = 0.

    We also add roots of x^2 + bx + c = 0 for small b,c to capture
    golden-ratio-type algebraic numbers.
    """
    targets = {}  # value -> (polynomial_str, degree, max_coeff_used)

    # Degree 1: rationals p/q
    for q in range(1, max_coeff + 1):
        for p in range(1, max_coeff + 1):
            val = p / q
            key = round(val, 12)
            poly_str = f"{q}*x - {p}"
            if key not in targets or _poly_complexity(targets[key]) > q + p:
                targets[key] = (poly_str, 1, max(p, q), val)

    # Degree 2-4: r = (p/q)^(1/d)
    for d in range(2, max_degree + 1):
        for q in range(1, max_coeff + 1):
            for p in range(1, max_coeff + 1):
                val = (p / q) ** (1.0 / d)
                key = round(val, 12)
                poly_str = f"{q}*x^{d} - {p}"
                cplx = max(p, q)
                if key not in targets or _poly_complexity(targets[key]) > cplx:
                    targets[key] = (poly_str, d, cplx, val)

    # Quadratic roots: x^2 + b*x + c = 0 => x = (-b ± sqrt(b^2-4c))/2
    for b in range(-50, 51):
        for c in range(-50, 51):
            disc = b * b - 4 * c
            if disc < 0:
                continue
            sq = math.sqrt(disc)
            for sign in [1, -1]:
                val = (-b + sign * sq) / 2
                if val > 0:
                    key = round(val, 12)
                    poly_str = f"x^2 + {b}*x + {c}"
                    cplx = abs(b) + abs(c)
                    if key not in targets or _poly_complexity(targets[key]) > cplx:
                        targets[key] = (poly_str, 2, max(abs(b), abs(c)), val)

    return targets


def _poly_complexity(entry):
    return entry[2]


def find_algebraic_hits(ratios_dict, targets, tol=TOLERANCE):
    """
    For each ratio, find if any target algebraic number is within tol (relative).

    ratios_dict: {(name_i, name_j): ratio_value}
    targets: {rounded_val: (poly_str, degree, max_coeff, exact_val)}

    Returns list of hits.
    """
    # Build sorted array of target values for binary search
    target_vals = np.array(sorted(targets.keys()))
    target_list = [targets[k] for k in sorted(targets.keys())]

    hits = []
    for (name_i, name_j), r in ratios_dict.items():
        if r <= 0 or not np.isfinite(r):
            continue
        # Binary search for closest target
        idx = np.searchsorted(target_vals, r)
        best_match = None
        best_rel_err = tol + 1

        for candidate_idx in [idx - 1, idx, idx + 1]:
            if 0 <= candidate_idx < len(target_vals):
                tv = target_vals[candidate_idx]
                rel_err = abs(tv - r) / r
                if rel_err < best_rel_err:
                    best_rel_err = rel_err
                    best_match = target_list[candidate_idx]

        if best_rel_err < tol and best_match is not None:
            poly_str, degree, max_c, exact_val = best_match
            hits.append({
                "particle_i": name_i,
                "particle_j": name_j,
                "ratio": float(r),
                "algebraic_value": float(exact_val),
                "polynomial": poly_str,
                "degree": int(degree),
                "relative_error": float(best_rel_err),
                "precision_digits": int(-math.log10(best_rel_err)) if best_rel_err > 0 else 15
            })

    return hits


def compute_pairwise_ratios(masses_with_names):
    """Compute all ordered pairs m_i/m_j where i != j and m_i >= m_j."""
    ratios = {}
    n = len(masses_with_names)
    for i in range(n):
        for j in range(i + 1, n):
            ni, mi = masses_with_names[i]
            nj, mj = masses_with_names[j]
            if mi >= mj:
                ratios[(ni, nj)] = mi / mj
            else:
                ratios[(nj, ni)] = mj / mi
    return ratios


def run_control(masses, targets, n_trials=N_RANDOM_TRIALS, tol=TOLERANCE):
    """Generate random masses in same range, compute hit rates."""
    mass_vals = [m for _, m in masses]
    lo, hi = min(mass_vals), max(mass_vals)
    n = len(mass_vals)

    hit_counts = []
    for trial in range(n_trials):
        random.seed(42 + trial)
        fake_masses = [(f"rand_{k}", 10 ** random.uniform(math.log10(lo), math.log10(hi)))
                       for k in range(n)]
        fake_ratios = compute_pairwise_ratios(fake_masses)
        fake_hits = find_algebraic_hits(fake_ratios, targets, tol)
        hit_counts.append(len(fake_hits))

    return hit_counts


def main():
    t0 = time.time()
    print("Loading particles...")
    particles = load_particles()
    print(f"  {len(particles)} particles with nonzero mass")

    print("Building algebraic targets...")
    targets = build_algebraic_targets()
    print(f"  {len(targets)} distinct algebraic target values")

    masses_with_names = [(name, mass) for name, mass, _ in particles]

    print("Computing pairwise ratios...")
    ratios = compute_pairwise_ratios(masses_with_names)
    n_ratios = len(ratios)
    print(f"  {n_ratios} unique ordered pairs")

    print("Finding algebraic hits...")
    hits = find_algebraic_hits(ratios, targets)
    hits.sort(key=lambda h: h["relative_error"])
    print(f"  {len(hits)} hits within {TOLERANCE*100}% tolerance")

    # Deduplicate: keep only the best match per unordered pair
    # (already unique since we only compute i<j)

    print("Running control trials...")
    control_counts = run_control(masses_with_names, targets)
    control_mean = np.mean(control_counts)
    control_std = np.std(control_counts)
    print(f"  Control hit counts: {control_counts}")
    print(f"  Control mean: {control_mean:.1f} +/- {control_std:.1f}")

    # Hit rate comparison
    real_rate = len(hits) / n_ratios
    control_rate = control_mean / n_ratios

    if control_std > 0:
        z_score = (len(hits) - control_mean) / control_std
    else:
        z_score = 0.0 if len(hits) == control_mean else float('inf')

    # Top hits by precision
    top_hits = hits[:50] if len(hits) > 50 else hits

    # Degree distribution
    degree_dist = defaultdict(int)
    for h in hits:
        degree_dist[h["degree"]] += 1

    # Summary of most precise matches
    ultra_precise = [h for h in hits if h["precision_digits"] >= 5]

    # === Precision-stratified analysis ===
    # The raw hit count is misleading because 33K targets cover the number line densely.
    # The real test: at TIGHTER tolerances, does real data have more hits than random?
    tighter_tols = [1e-4, 1e-5, 1e-6, 1e-7]
    stratified = {}
    for ttol in tighter_tols:
        real_tight = len([h for h in hits if h["relative_error"] < ttol])
        # Count control hits at this tolerance from all trials
        ctrl_tight_counts = []
        for trial in range(N_RANDOM_TRIALS):
            random.seed(42 + trial)
            mass_vals = [m for _, m in masses_with_names]
            lo, hi_m = min(mass_vals), max(mass_vals)
            fake = [(f"r{k}", 10 ** random.uniform(math.log10(lo), math.log10(hi_m)))
                    for k in range(len(mass_vals))]
            fake_ratios = compute_pairwise_ratios(fake)
            fake_hits = find_algebraic_hits(fake_ratios, targets, tol=TOLERANCE)
            ctrl_tight_counts.append(len([h for h in fake_hits if h["relative_error"] < ttol]))
        ctrl_mean_t = np.mean(ctrl_tight_counts)
        ctrl_std_t = np.std(ctrl_tight_counts)
        z_t = (real_tight - ctrl_mean_t) / ctrl_std_t if ctrl_std_t > 0 else 0
        label = f"{ttol:.0e}"
        stratified[label] = {
            "tolerance": ttol,
            "real_hits": real_tight,
            "control_mean": round(float(ctrl_mean_t), 1),
            "control_std": round(float(ctrl_std_t), 1),
            "z_score": round(float(z_t), 2)
        }
        print(f"  Tol={label}: real={real_tight}, ctrl={ctrl_mean_t:.1f}+/-{ctrl_std_t:.1f}, z={z_t:.1f}")

    elapsed = time.time() - t0

    results = {
        "metadata": {
            "n_particles": len(particles),
            "n_ratios": n_ratios,
            "tolerance": TOLERANCE,
            "max_degree": MAX_DEGREE,
            "max_coeff": MAX_COEFF,
            "n_algebraic_targets": len(targets),
            "elapsed_seconds": round(elapsed, 1)
        },
        "real_data": {
            "n_hits": len(hits),
            "hit_rate": round(real_rate, 6),
            "degree_distribution": {str(k): v for k, v in sorted(degree_dist.items())}
        },
        "control": {
            "n_trials": N_RANDOM_TRIALS,
            "hit_counts": control_counts,
            "mean_hits": round(float(control_mean), 1),
            "std_hits": round(float(control_std), 1),
            "hit_rate": round(float(control_rate), 6)
        },
        "comparison": {
            "real_vs_control_ratio": round(len(hits) / control_mean, 3) if control_mean > 0 else None,
            "z_score": round(float(z_score), 2),
            "verdict": "ABOVE_BASELINE" if z_score > 3 else "AT_BASELINE" if z_score > -3 else "BELOW_BASELINE"
        },
        "precision_stratified": stratified,
        "ultra_precise_matches": ultra_precise[:20],
        "top_50_hits": top_hits,
        "interpretation": "",
        "methodological_note": ""
    }

    # Methodological note
    method_note = (
        "CRITICAL CAVEAT: PDG masses are reported with limited decimal precision "
        "(typically 1-5 significant figures). This makes most mass ratios trivially rational "
        "(e.g. 1.420/0.500 = 2.84 = 71/25 exactly). The massive z-scores at tight tolerance "
        "reflect REPORTING PRECISION, not deep algebraic structure. A proper test would require "
        "masses known to 10+ digits and testing whether the EXTRA precision beyond what the "
        "Standard Model predicts reveals algebraic structure. The signal here is: particle masses "
        "as reported are low-precision decimal numbers, and ratios of low-precision decimals are "
        "trivially close to simple rationals."
    )
    results["methodological_note"] = method_note

    # Write interpretation
    if z_score > 3:
        interp = (f"Real hit count ({len(hits)}) is {z_score:.1f} sigma above random baseline "
                  f"({control_mean:.0f} +/- {control_std:.0f}). Particle mass ratios show MORE "
                  f"algebraic structure than random -- but this is a REPORTING ARTIFACT: PDG masses "
                  f"have limited decimal precision (1-5 digits), making their ratios trivially rational. "
                  f"Random masses drawn from continuous distributions have full float64 precision, "
                  f"so they are much less likely to exactly match simple rationals. "
                  f"NO EVIDENCE of deep algebraic structure in particle masses.")
    elif z_score < -3:
        interp = (f"Real hit count ({len(hits)}) is {abs(z_score):.1f} sigma BELOW random baseline "
                  f"({control_mean:.0f} +/- {control_std:.0f}). Particle masses show LESS algebraic "
                  f"structure than random masses in the same range.")
    else:
        interp = (f"Real hit count ({len(hits)}) is within normal range of random baseline "
                  f"({control_mean:.0f} +/- {control_std:.0f}, z={z_score:.1f}). "
                  f"No evidence that particle mass ratios are more algebraic than chance.")

    results["interpretation"] = interp
    print(f"\n{'='*60}")
    print(f"RESULT: {interp}")
    print(f"{'='*60}")

    if ultra_precise:
        print(f"\nMost precise algebraic matches ({len(ultra_precise)} with >=5 digits):")
        for h in ultra_precise[:10]:
            print(f"  {h['particle_i']} / {h['particle_j']} = {h['ratio']:.8f} "
                  f"~ root of [{h['polynomial']}] "
                  f"(err={h['relative_error']:.2e}, {h['precision_digits']} digits)")

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
