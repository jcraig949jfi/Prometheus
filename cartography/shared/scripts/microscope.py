"""
Microscope — Strip prime structure and small-integer noise to find real bridges.
=================================================================================
The problem: primes and small integers dominate every mathematical dataset.
Any two datasets correlate because both encode prime factorization.
The solution: decompose, detrend, and test the RESIDUAL.

Three layers of decontamination:
  Layer 1: PRIME DETREND — regress out prime factorization features
           (n_factors, largest_factor, sum_of_exponents, is_prime, smoothness)
  Layer 2: SMALL INTEGER FILTER — remove or downweight values < 100
           where overlap is guaranteed by base rate
  Layer 3: SCALE NORMALIZATION — work in log-space, rank-space, or
           fractional-part space to remove monotone growth

After decontamination, run geometric probes on the residuals.
If a correlation survives all three layers, it's real structure.

Usage:
    python microscope.py                    # full decontaminated survey
    python microscope.py --pair Genus2 NF   # one pair
"""

import json
import math
import sys
import time
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from scipy import stats as sp_stats

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
RESULTS_FILE = ROOT / "cartography" / "convergence" / "data" / "microscope_results.json"


# =====================================================================
# Layer 1: Prime Detrend
# =====================================================================

def _smallest_factor(n):
    """Smallest prime factor of n."""
    if n < 2:
        return n
    if n % 2 == 0:
        return 2
    for i in range(3, min(int(n**0.5) + 1, 10000), 2):
        if n % i == 0:
            return i
    return n


def _factorize(n):
    """Return prime factorization as {prime: exponent}."""
    if n < 2:
        return {}
    factors = {}
    d = 2
    while d * d <= n and n > 1:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def prime_features(n):
    """Extract prime factorization features from an integer."""
    n = int(abs(n))
    if n < 2:
        return [0, 0, 0, 0, 0, 0]

    factors = _factorize(n)
    n_distinct = len(factors)
    total_exp = sum(factors.values())
    largest = max(factors.keys()) if factors else 0
    smallest = min(factors.keys()) if factors else 0
    is_prime = 1 if n_distinct == 1 and total_exp == 1 else 0

    # Smoothness: ratio of largest prime factor to n
    smoothness = math.log(largest) / math.log(max(n, 2))

    return [n_distinct, total_exp, math.log(max(largest, 2)),
            math.log(max(smallest, 2)), is_prime, smoothness]


def detrend_primes(values):
    """Remove prime factorization structure from an integer array.

    Returns the residuals after regressing out prime features.
    """
    arr = np.array(values, dtype=float)
    valid = arr[arr > 1]
    if len(valid) < 20:
        return arr, None

    # Build feature matrix
    features = np.array([prime_features(int(v)) for v in valid])
    target = np.log(valid)  # work in log-space

    # Handle constant columns
    good_cols = [i for i in range(features.shape[1]) if np.std(features[:, i]) > 1e-10]
    if not good_cols:
        return arr, None
    X = features[:, good_cols]

    # Add intercept
    X = np.column_stack([X, np.ones(len(X))])

    # Least squares
    try:
        coeffs, _, _, _ = np.linalg.lstsq(X, target, rcond=None)
        predicted = X @ coeffs
        residuals = target - predicted
        r2 = 1 - np.var(residuals) / max(np.var(target), 1e-15)
    except Exception:
        return arr, None

    return residuals, {
        "r2_prime_model": round(float(r2), 6),
        "n_values": len(valid),
        "variance_explained_by_primes": round(float(r2), 4),
        "coefficients": {
            "n_distinct_factors": round(float(coeffs[0]) if len(good_cols) > 0 else 0, 4),
        },
    }


# =====================================================================
# Layer 2: Small Integer Filter
# =====================================================================

def filter_small_integers(values, threshold=100):
    """Remove values below threshold and return the large-value subset."""
    arr = np.array(values, dtype=float)
    large = arr[arr >= threshold]
    small_frac = 1 - len(large) / max(len(arr), 1)
    return large, {
        "threshold": threshold,
        "n_total": len(arr),
        "n_large": len(large),
        "small_fraction": round(small_frac, 4),
    }


# =====================================================================
# Layer 3: Scale Normalization (beyond z-score)
# =====================================================================

def to_rank_space(values):
    """Convert to rank space — removes all distributional information,
    keeps only ordering. Most robust against scale artifacts."""
    arr = np.array(values, dtype=float)
    return sp_stats.rankdata(arr) / len(arr)


def to_fractional_parts(values):
    """Extract fractional parts of log values — strips integer structure,
    reveals fine arithmetic detail."""
    arr = np.array(values, dtype=float)
    positive = arr[arr > 0]
    if len(positive) < 10:
        return None
    log_vals = np.log(positive)
    return log_vals - np.floor(log_vals)


def to_digit_signature(values, base=10):
    """Extract leading digit + second digit as a 2D signature."""
    arr = np.array(values, dtype=float)
    positive = arr[arr > 0].astype(int)
    if len(positive) < 50:
        return None
    sigs = []
    for v in positive:
        s = str(v)
        d1 = int(s[0])
        d2 = int(s[1]) if len(s) > 1 else 0
        sigs.append([d1, d2])
    return np.array(sigs, dtype=float)


# =====================================================================
# Microscope Probes — correlation tests on decontaminated data
# =====================================================================

def microscope_correlation(a, b, name_a="a", name_b="b"):
    """Full microscope analysis on a pair of integer arrays."""
    results = {"pair": f"{name_a}--{name_b}"}

    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    # Raw correlation (the polluted baseline)
    n = min(len(a), len(b))
    if n < 30:
        results["status"] = "SKIP"
        return results

    a_s, b_s = np.sort(a)[:n], np.sort(b)[:n]
    raw_rho = float(sp_stats.spearmanr(a_s, b_s)[0])
    results["raw_rho"] = round(raw_rho, 6)

    # Layer 1: Prime detrend
    a_resid, a_prime_info = detrend_primes(a)
    b_resid, b_prime_info = detrend_primes(b)
    results["prime_detrend_a"] = a_prime_info
    results["prime_detrend_b"] = b_prime_info

    if a_resid is not None and b_resid is not None:
        n_r = min(len(a_resid), len(b_resid))
        if n_r >= 20:
            a_rs, b_rs = np.sort(a_resid)[:n_r], np.sort(b_resid)[:n_r]
            detrended_rho = float(sp_stats.spearmanr(a_rs, b_rs)[0])
            results["detrended_rho"] = round(detrended_rho, 6)
            results["prime_removed_pct"] = round(abs(raw_rho - detrended_rho) / max(abs(raw_rho), 1e-10) * 100, 1)

    # Layer 2: Filter small integers
    a_large, a_filt_info = filter_small_integers(a)
    b_large, b_filt_info = filter_small_integers(b)
    results["filter_a"] = a_filt_info
    results["filter_b"] = b_filt_info

    n_l = min(len(a_large), len(b_large))
    if n_l >= 20:
        a_ls, b_ls = np.sort(a_large)[:n_l], np.sort(b_large)[:n_l]
        filtered_rho = float(sp_stats.spearmanr(a_ls, b_ls)[0])
        results["filtered_rho"] = round(filtered_rho, 6)

    # Layer 3: Fractional parts of log
    a_frac = to_fractional_parts(a)
    b_frac = to_fractional_parts(b)
    if a_frac is not None and b_frac is not None:
        n_f = min(len(a_frac), len(b_frac))
        if n_f >= 20:
            a_fs, b_fs = np.sort(a_frac)[:n_f], np.sort(b_frac)[:n_f]
            frac_rho = float(sp_stats.spearmanr(a_fs, b_fs)[0])
            results["fractional_rho"] = round(frac_rho, 6)

            # KS test on fractional parts — are they from the same fine structure?
            ks_stat, ks_p = sp_stats.ks_2samp(a_frac[:n_f], b_frac[:n_f])
            results["fractional_ks_p"] = round(float(ks_p), 6)
            results["fractional_match"] = ks_p > 0.05

    # Layer 1+2 combined: detrend primes on large values only
    if n_l >= 20:
        a_lr, a_lr_info = detrend_primes(a_large)
        b_lr, b_lr_info = detrend_primes(b_large)
        if a_lr is not None and b_lr is not None:
            n_lr = min(len(a_lr), len(b_lr))
            if n_lr >= 15:
                a_lrs, b_lrs = np.sort(a_lr)[:n_lr], np.sort(b_lr)[:n_lr]
                deep_rho = float(sp_stats.spearmanr(a_lrs, b_lrs)[0])
                results["deep_rho"] = round(deep_rho, 6)

    # Digit signature comparison (2D)
    a_dig = to_digit_signature(a)
    b_dig = to_digit_signature(b)
    if a_dig is not None and b_dig is not None:
        n_d = min(len(a_dig), len(b_dig))
        if n_d >= 30:
            # Compare leading digit distributions
            a_d1 = a_dig[:n_d, 0]
            b_d1 = b_dig[:n_d, 0]
            digit_rho = float(sp_stats.spearmanr(
                np.sort(a_d1), np.sort(b_d1))[0])
            results["digit_rho"] = round(digit_rho, 6)

    # Verdict: does any signal survive all layers?
    rhos = [results.get(k, 0) for k in ["raw_rho", "detrended_rho", "filtered_rho",
                                          "fractional_rho", "deep_rho"]]
    rhos = [r for r in rhos if r != 0]

    if len(rhos) >= 3:
        # Signal survives if deep_rho or fractional_rho is significant
        deep = results.get("deep_rho", 0)
        frac = results.get("fractional_rho", 0)
        if abs(deep) > 0.3 or (results.get("fractional_match") and abs(frac) > 0.3):
            results["verdict"] = "SIGNAL_SURVIVES"
        elif abs(deep) < 0.1 and abs(results.get("detrended_rho", 0)) < 0.1:
            results["verdict"] = "KILLED_BY_DETREND"
        else:
            results["verdict"] = "WEAK"
    else:
        results["verdict"] = "INSUFFICIENT"

    return results


def run_microscope(focus_pair=None):
    """Run the microscope on all dataset pairs."""
    print("=" * 70)
    print("  MICROSCOPE — Sub-prime resolution cross-dataset analysis")
    print("  Strip primes. Filter small integers. Test what's left.")
    print("=" * 70)

    t0 = time.time()

    # Extract arrays
    from search_engine import (
        _load_genus2, _genus2_cache, _load_nf, _nf_cache,
        _load_smallgroups, _smallgroups_cache, _load_knots, _knots_cache,
        _load_maass, _maass_cache, _get_duck,
    )

    _load_genus2(); _load_nf(); _load_smallgroups(); _load_knots(); _load_maass()

    arrays = {}

    arrays["Genus2_cond"] = np.array(
        [c["conductor"] for c in _genus2_cache[:5000] if c.get("conductor")], dtype=float)

    arrays["NF_disc"] = np.array(
        [abs(int(f["disc_abs"])) for f in _nf_cache[:5000]
         if f.get("disc_abs") and str(f["disc_abs"]).lstrip("-").isdigit()], dtype=float)

    arrays["NF_class"] = np.array(
        [int(f["class_number"]) for f in _nf_cache[:5000]
         if f.get("class_number") and str(f["class_number"]).isdigit()], dtype=float)

    arrays["SG_counts"] = np.array(
        [g["n_groups"] for g in _smallgroups_cache[:2000]
         if isinstance(g.get("n_groups"), int) and 0 < g["n_groups"] < 1e9], dtype=float)

    arrays["SG_orders"] = np.array(
        [g["order"] for g in _smallgroups_cache[:2000] if g.get("order")], dtype=float)

    knot_list = _knots_cache.get("knots", [])
    arrays["Knot_det"] = np.array(
        [k["determinant"] for k in knot_list
         if isinstance(k, dict) and isinstance(k.get("determinant"), (int, float)) and k["determinant"] > 0
        ][:5000], dtype=float)

    arrays["Maass_spec"] = np.array(
        [m["spectral_parameter"] for m in _maass_cache if m.get("spectral_parameter")], dtype=float)

    try:
        con = _get_duck()
        rows = con.execute(
            "SELECT conductor FROM objects WHERE object_type='elliptic_curve' AND conductor <= 50000"
        ).fetchall()
        con.close()
        arrays["LMFDB_cond"] = np.array([r[0] for r in rows], dtype=float)
    except Exception:
        pass

    print(f"\n  Loaded {len(arrays)} arrays")

    # Run microscope on all pairs
    if focus_pair:
        pairs = [(focus_pair[0], focus_pair[1])]
    else:
        pairs = list(combinations(sorted(arrays.keys()), 2))

    print(f"  Testing {len(pairs)} pairs through 3-layer decontamination...\n")

    all_results = []
    for name_a, name_b in pairs:
        result = microscope_correlation(arrays[name_a], arrays[name_b], name_a, name_b)
        all_results.append(result)

        verdict = result.get("verdict", "?")
        raw = result.get("raw_rho", 0)
        deep = result.get("deep_rho", 0)
        frac_match = result.get("fractional_match", False)

        marker = ""
        if verdict == "SIGNAL_SURVIVES":
            marker = " <-- REAL SIGNAL"
        elif verdict == "KILLED_BY_DETREND":
            marker = " (prime artifact)"

        if abs(raw) > 0.3 or verdict == "SIGNAL_SURVIVES":
            print(f"  {name_a:15s} -- {name_b:15s}: raw={raw:+.4f} deep={deep:+.4f} "
                  f"frac_match={frac_match} [{verdict}]{marker}")

    elapsed = time.time() - t0

    # Save
    def _default(obj):
        if isinstance(obj, (np.integer, np.bool_)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return str(obj)

    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_s": round(elapsed, 1),
            "n_pairs": len(pairs),
            "results": all_results,
        }, f, indent=2, default=_default)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  MICROSCOPE COMPLETE in {elapsed:.1f}s")

    survivors = [r for r in all_results if r.get("verdict") == "SIGNAL_SURVIVES"]
    killed = [r for r in all_results if r.get("verdict") == "KILLED_BY_DETREND"]
    weak = [r for r in all_results if r.get("verdict") == "WEAK"]

    print(f"  Signal survives decontamination: {len(survivors)}")
    print(f"  Killed by prime detrend: {len(killed)}")
    print(f"  Weak / ambiguous: {len(weak)}")

    if survivors:
        print(f"\n  SURVIVORS (real bridges beyond prime structure):")
        for r in survivors:
            print(f"    {r['pair']:35s} raw={r.get('raw_rho',0):+.4f} "
                  f"deep={r.get('deep_rho',0):+.4f} "
                  f"frac_match={r.get('fractional_match', False)}")

    if killed:
        print(f"\n  KILLED (prime artifacts):")
        for r in killed[:10]:
            pct = r.get("prime_removed_pct", "?")
            print(f"    {r['pair']:35s} raw={r.get('raw_rho',0):+.4f} "
                  f"detrended={r.get('detrended_rho',0):+.4f} "
                  f"({pct}% was primes)")

    print(f"\n  Results saved to {RESULTS_FILE}")
    print(f"{'=' * 70}")

    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Microscope — sub-prime resolution")
    parser.add_argument("--pair", nargs=2, default=None, help="Focus on one pair")
    args = parser.parse_args()

    run_microscope(focus_pair=args.pair)
