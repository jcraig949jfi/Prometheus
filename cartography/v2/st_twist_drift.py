#!/usr/bin/env python3
"""
Sato-Tate Moment Drift Under Quadratic Twist
==============================================
From symmetry_detection's 148 twist pairs (100 same-level + 48 cross-level),
for each pair (f, f_twisted):
  1. Compute 6-moment vector M = (M1, M2, M3, M4, M5, M6) of normalised
     x_p = a_p / (2*sqrt(p)) over good primes up to 997.
  2. Drift = ||M(f) - M(f_twisted)||_2.
  3. Test: Is drift zero (twisting preserves moments exactly)?
  4. If nonzero: does drift correlate with |discriminant|?
  5. Fit drift ~ |d|^{-alpha} power law.

SU(2) theory moments: M1=0, M2=1/4, M3=0, M4=1/8, M5=0, M6=5/64.

Charon / Project Prometheus -- 2026-04-10
"""

import json
import math
import sys
import time
from pathlib import Path
from collections import defaultdict

import duckdb
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import spearmanr, pearsonr

sys.stdout.reconfigure(line_buffering=True)

# -- Paths ------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
SYM_PATH = REPO_ROOT / "cartography" / "shared" / "scripts" / "v2" / "symmetry_detection_results.json"
OUT_PATH = Path(__file__).resolve().parent / "st_twist_drift_results.json"


def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


PRIMES = sieve_primes(997)  # 168 primes


def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def compute_moments_6(traces, level):
    """
    Compute 6-moment vector of x_p = a_p / (2*sqrt(p)) for good primes.
    Returns (M1, M2, M3, M4, M5, M6), n_points.
    """
    bad = prime_factors(level)
    sums = np.zeros(6)
    n = 0
    for p in PRIMES:
        if p in bad:
            continue
        if p - 1 >= len(traces):
            continue
        ap = traces[p - 1]
        x = ap / (2.0 * math.sqrt(p))
        xk = x
        for k in range(6):
            sums[k] += xk
            xk *= x
        n += 1
    if n == 0:
        return None, 0
    return sums / n, n


def load_twist_pairs():
    """Load twist pairs from symmetry detection results."""
    with open(SYM_PATH) as f:
        data = json.load(f)

    pairs = []
    # Same-level pairs
    for p in data["quadratic_twists"]["pairs"]:
        pairs.append({
            "form_f": p["form_f"],
            "form_g": p["form_g"],
            "discriminant": p["discriminant"],
            "type": "same_level"
        })
    # Cross-level pairs
    for p in data["cross_level_twists"]["pairs"]:
        pairs.append({
            "form_f": p["form_f"],
            "form_g": p["form_g"],
            "discriminant": p["discriminant"],
            "type": "cross_level"
        })
    print(f"[load] {len(pairs)} twist pairs ({len(data['quadratic_twists']['pairs'])} same-level + "
          f"{len(data['cross_level_twists']['pairs'])} cross-level)")
    return pairs


def load_forms_db():
    """Load all weight-2 dim-1 forms from duckdb, keyed by label."""
    print(f"[load] Connecting to {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, traces
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()

    forms = {}
    for label, level, traces in rows:
        forms[label] = {"level": level, "traces": traces}
    print(f"[load] {len(forms)} forms in database")
    return forms


def main():
    t0 = time.time()

    pairs = load_twist_pairs()
    forms = load_forms_db()

    # -- Compute moment drift for each pair --
    results_pairs = []
    drifts = []
    abs_discs = []
    missing = 0

    su2_theory = np.array([0.0, 1/4, 0.0, 1/8, 0.0, 5/64])

    for pair in pairs:
        label_f = pair["form_f"]
        label_g = pair["form_g"]

        if label_f not in forms or label_g not in forms:
            missing += 1
            continue

        f_data = forms[label_f]
        g_data = forms[label_g]

        M_f, n_f = compute_moments_6(f_data["traces"], f_data["level"])
        M_g, n_g = compute_moments_6(g_data["traces"], g_data["level"])

        if M_f is None or M_g is None:
            missing += 1
            continue

        drift_vec = M_f - M_g
        drift_norm = float(np.linalg.norm(drift_vec))

        # Distance from SU(2) for each form
        dist_f_su2 = float(np.linalg.norm(M_f - su2_theory))
        dist_g_su2 = float(np.linalg.norm(M_g - su2_theory))

        rec = {
            "form_f": label_f,
            "form_g": label_g,
            "discriminant": pair["discriminant"],
            "abs_disc": abs(pair["discriminant"]),
            "type": pair["type"],
            "drift_L2": round(drift_norm, 8),
            "drift_vec": [round(float(x), 8) for x in drift_vec],
            "moments_f": [round(float(x), 8) for x in M_f],
            "moments_g": [round(float(x), 8) for x in M_g],
            "dist_f_SU2": round(dist_f_su2, 8),
            "dist_g_SU2": round(dist_g_su2, 8),
            "n_primes_f": n_f,
            "n_primes_g": n_g,
        }
        results_pairs.append(rec)
        drifts.append(drift_norm)
        abs_discs.append(abs(pair["discriminant"]))

    print(f"\n[drift] Computed {len(results_pairs)} pair drifts, {missing} pairs skipped")

    drifts = np.array(drifts)
    abs_discs = np.array(abs_discs, dtype=float)

    # -- Summary statistics --
    print(f"\n=== Twist-Moment Drift Summary ===")
    print(f"  N pairs:     {len(drifts)}")
    print(f"  Drift mean:  {drifts.mean():.6f}")
    print(f"  Drift median:{np.median(drifts):.6f}")
    print(f"  Drift std:   {drifts.std():.6f}")
    print(f"  Drift min:   {drifts.min():.6f}")
    print(f"  Drift max:   {drifts.max():.6f}")

    # Is drift ~zero?
    threshold = 1e-3
    n_zero = int(np.sum(drifts < threshold))
    print(f"  Drift < {threshold}: {n_zero}/{len(drifts)} ({100*n_zero/len(drifts):.1f}%)")

    # -- Same-level vs cross-level breakdown --
    same_drifts = [r["drift_L2"] for r in results_pairs if r["type"] == "same_level"]
    cross_drifts = [r["drift_L2"] for r in results_pairs if r["type"] == "cross_level"]
    print(f"\n  Same-level pairs:  N={len(same_drifts)}, mean drift={np.mean(same_drifts):.6f}")
    print(f"  Cross-level pairs: N={len(cross_drifts)}, mean drift={np.mean(cross_drifts):.6f}")

    # -- Correlation with |discriminant| --
    if len(drifts) > 5:
        r_spearman, p_spearman = spearmanr(abs_discs, drifts)
        r_pearson, p_pearson = pearsonr(abs_discs, drifts)
        print(f"\n  Spearman(|d|, drift): r={r_spearman:.4f}, p={p_spearman:.4g}")
        print(f"  Pearson(|d|, drift):  r={r_pearson:.4f}, p={p_pearson:.4g}")
    else:
        r_spearman = p_spearman = r_pearson = p_pearson = None

    # -- Power law fit: drift ~ A * |d|^(-alpha) --
    alpha_fit = None
    A_fit = None
    fit_info = {}

    # Group by |d| and take mean drift for each
    disc_groups = defaultdict(list)
    for d, drift in zip(abs_discs, drifts):
        disc_groups[d].append(drift)

    group_discs = sorted(disc_groups.keys())
    group_means = [np.mean(disc_groups[d]) for d in group_discs]

    print(f"\n  Drift by |discriminant|:")
    for d, m in zip(group_discs, group_means):
        n = len(disc_groups[d])
        print(f"    |d|={d:>4.0f}: mean drift={m:.6f} (N={n})")

    if len(group_discs) >= 3:
        gd = np.array(group_discs, dtype=float)
        gm = np.array(group_means)

        # Filter out zero drifts for log fitting
        mask = gm > 1e-15
        if mask.sum() >= 3:
            try:
                def power_law(x, A, alpha):
                    return A * x ** (-alpha)

                popt, pcov = curve_fit(power_law, gd[mask], gm[mask],
                                       p0=[0.1, 0.5], maxfev=5000)
                A_fit, alpha_fit = popt
                perr = np.sqrt(np.diag(pcov))
                A_err, alpha_err = perr

                # Log-log linear fit for comparison
                log_d = np.log(gd[mask])
                log_m = np.log(gm[mask])
                coeffs = np.polyfit(log_d, log_m, 1)
                alpha_loglog = -coeffs[0]
                A_loglog = np.exp(coeffs[1])

                # R^2
                pred = power_law(gd[mask], A_fit, alpha_fit)
                ss_res = np.sum((gm[mask] - pred) ** 2)
                ss_tot = np.sum((gm[mask] - gm[mask].mean()) ** 2)
                r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

                fit_info = {
                    "A": round(float(A_fit), 6),
                    "alpha": round(float(alpha_fit), 6),
                    "A_err": round(float(A_err), 6),
                    "alpha_err": round(float(alpha_err), 6),
                    "R_squared": round(float(r2), 6),
                    "alpha_loglog": round(float(alpha_loglog), 6),
                    "A_loglog": round(float(A_loglog), 6),
                    "n_disc_groups": int(mask.sum()),
                }

                print(f"\n  Power law fit: drift ~ {A_fit:.4f} * |d|^(-{alpha_fit:.4f})")
                print(f"    alpha = {alpha_fit:.4f} +/- {alpha_err:.4f}")
                print(f"    R^2 = {r2:.4f}")
                print(f"    Log-log alpha = {alpha_loglog:.4f}")
            except Exception as e:
                print(f"\n  Power law fit failed: {e}")
                fit_info = {"error": str(e)}
        else:
            fit_info = {"error": "too few nonzero groups for fitting"}
    else:
        fit_info = {"error": "too few discriminant groups"}

    # -- Null test: random pairing of forms --
    print(f"\n=== Null Test: Random Pairing ===")
    all_labels = list(set(r["form_f"] for r in results_pairs) |
                      set(r["form_g"] for r in results_pairs))
    rng = np.random.default_rng(42)
    null_drifts = []
    n_null = min(500, len(all_labels) * (len(all_labels) - 1) // 2)

    for _ in range(n_null):
        i, j = rng.choice(len(all_labels), size=2, replace=False)
        la, lb = all_labels[i], all_labels[j]
        if la not in forms or lb not in forms:
            continue
        Ma, na = compute_moments_6(forms[la]["traces"], forms[la]["level"])
        Mb, nb = compute_moments_6(forms[lb]["traces"], forms[lb]["level"])
        if Ma is None or Mb is None:
            continue
        null_drifts.append(float(np.linalg.norm(Ma - Mb)))

    null_drifts = np.array(null_drifts)
    print(f"  Null pairs computed: {len(null_drifts)}")
    if len(null_drifts) > 0:
        print(f"  Null drift mean:  {null_drifts.mean():.6f}")
        print(f"  Null drift median:{np.median(null_drifts):.6f}")
        print(f"  Null drift std:   {null_drifts.std():.6f}")
        # Effect size
        if null_drifts.std() > 0:
            cohens_d = (null_drifts.mean() - drifts.mean()) / null_drifts.std()
            print(f"  Cohen's d (null - twist): {cohens_d:.4f}")
        else:
            cohens_d = None
    else:
        cohens_d = None

    # -- Per-moment analysis --
    print(f"\n=== Per-Moment Drift ===")
    moment_labels = ["M1", "M2", "M3", "M4", "M5", "M6"]
    per_moment = {}
    for k in range(6):
        mk_drifts = np.array([abs(r["drift_vec"][k]) for r in results_pairs])
        per_moment[moment_labels[k]] = {
            "mean_abs_drift": round(float(mk_drifts.mean()), 8),
            "median_abs_drift": round(float(np.median(mk_drifts)), 8),
            "max_abs_drift": round(float(mk_drifts.max()), 8),
            "parity": "odd" if k % 2 == 0 else "even",
        }
        tag = "ODD " if k % 2 == 0 else "EVEN"
        print(f"  {moment_labels[k]} ({tag}): mean={mk_drifts.mean():.6f}, "
              f"median={np.median(mk_drifts):.6f}, max={mk_drifts.max():.6f}")

    # Even moments should be exactly zero for true quadratic twists
    even_max = max(per_moment[f"M{k+1}"]["max_abs_drift"] for k in [1, 3, 5])
    odd_mean = np.mean([per_moment[f"M{k+1}"]["mean_abs_drift"] for k in [0, 2, 4]])
    print(f"\n  Even-moment max drift: {even_max:.2e} (should be ~0 for true twists)")
    print(f"  Odd-moment mean drift: {odd_mean:.6f}")

    # Odd-moment-only L2 drift
    odd_drifts = np.array([
        np.sqrt(sum(r["drift_vec"][k]**2 for k in [0, 2, 4]))
        for r in results_pairs
    ])
    print(f"\n  Odd-only L2 drift: mean={odd_drifts.mean():.6f}, median={np.median(odd_drifts):.6f}")

    # Correlation of odd-only drift with |d|
    if len(odd_drifts) > 5:
        r_odd_sp, p_odd_sp = spearmanr(abs_discs, odd_drifts)
        print(f"  Spearman(|d|, odd_drift): r={r_odd_sp:.4f}, p={p_odd_sp:.4g}")
    else:
        r_odd_sp = p_odd_sp = None

    # -- Final verdict --
    # Key mathematical insight: quadratic twist chi_d flips sign of a_p at primes
    # where chi_d(p) = -1. So x_p^{2k} is invariant but x_p^{2k+1} is not.
    # => Even moments (M2, M4, M6) are EXACTLY preserved.
    # => Odd moments (M1, M3, M5) shift proportional to character imbalance.
    even_preserved = even_max < 1e-10
    drift_is_zero = drifts.mean() < 0.01 and np.median(drifts) < 0.01
    if even_preserved and not drift_is_zero:
        verdict = "EVEN_EXACT_ODD_NONZERO"
    elif drift_is_zero:
        verdict = "ZERO"
    elif fit_info.get("R_squared", 0) > 0.5:
        verdict = "NONZERO_WITH_PATTERN"
    else:
        verdict = "NONZERO_NO_CLEAR_PATTERN"
    print(f"\n  VERDICT: {verdict}")
    if even_preserved:
        print("  => Even moments (M2,M4,M6) EXACTLY preserved under twist (theory confirms)")
        print("  => Odd moments (M1,M3,M5) shift: twist flips sign of a_p at ~half of primes")

    elapsed = time.time() - t0

    # -- Assemble output --
    output = {
        "experiment": "st_twist_drift",
        "description": "Sato-Tate 6-moment drift under quadratic twist",
        "n_pairs": len(results_pairs),
        "n_pairs_same_level": len(same_drifts),
        "n_pairs_cross_level": len(cross_drifts),
        "n_missing": missing,
        "drift_summary": {
            "mean": round(float(drifts.mean()), 8),
            "median": round(float(np.median(drifts)), 8),
            "std": round(float(drifts.std()), 8),
            "min": round(float(drifts.min()), 8),
            "max": round(float(drifts.max()), 8),
            "n_below_1e-3": n_zero,
            "frac_below_1e-3": round(n_zero / len(drifts), 4),
        },
        "drift_by_type": {
            "same_level_mean": round(float(np.mean(same_drifts)), 8) if same_drifts else None,
            "cross_level_mean": round(float(np.mean(cross_drifts)), 8) if cross_drifts else None,
        },
        "correlation_disc_drift": {
            "spearman_r": round(float(r_spearman), 6) if r_spearman is not None else None,
            "spearman_p": round(float(p_spearman), 6) if p_spearman is not None else None,
            "pearson_r": round(float(r_pearson), 6) if r_pearson is not None else None,
            "pearson_p": round(float(p_pearson), 6) if p_pearson is not None else None,
        },
        "power_law_fit": fit_info,
        "drift_by_discriminant": {
            str(int(d)): {
                "mean_drift": round(float(m), 8),
                "n_pairs": len(disc_groups[d]),
            }
            for d, m in zip(group_discs, group_means)
        },
        "even_odd_decomposition": {
            "even_moments_max_drift": round(float(even_max), 12),
            "even_moments_exactly_preserved": bool(even_preserved),
            "odd_moments_mean_drift": round(float(odd_mean), 8),
            "odd_only_L2_mean": round(float(odd_drifts.mean()), 8),
            "odd_only_L2_median": round(float(np.median(odd_drifts)), 8),
            "odd_disc_spearman_r": round(float(r_odd_sp), 6) if r_odd_sp is not None else None,
            "odd_disc_spearman_p": round(float(p_odd_sp), 6) if r_odd_sp is not None else None,
            "explanation": "Quadratic twist chi_d maps a_p -> chi_d(p)*a_p. "
                           "Even powers x^{2k} invariant; odd powers x^{2k+1} flip at primes with chi_d(p)=-1.",
        },
        "per_moment_drift": per_moment,
        "null_test": {
            "n_null_pairs": len(null_drifts),
            "null_mean": round(float(null_drifts.mean()), 8) if len(null_drifts) > 0 else None,
            "null_median": round(float(np.median(null_drifts)), 8) if len(null_drifts) > 0 else None,
            "null_std": round(float(null_drifts.std()), 8) if len(null_drifts) > 0 else None,
            "cohens_d": round(float(cohens_d), 6) if cohens_d is not None else None,
        },
        "verdict": verdict,
        "pairs": results_pairs,
        "elapsed_s": round(elapsed, 2),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
