"""
Depth Probes — Sequence-to-sequence cross-dataset analysis.
=============================================================
Phase 2 of the Prometheus discovery pipeline. Operates on the
POLYNOMIAL COEFFICIENTS and SEQUENCE DATA attached to each object,
not the scalar invariants (which are empty after prime detrending).

Available depth data:
  - EC a_p lists: L-function coefficients at primes (25 per curve)
  - EC a_n lists: full Dirichlet coefficients (21 per curve)
  - Knot Alexander polynomials: palindromic coefficient sequences
  - Knot Jones polynomials: coefficient sequences
  - EC Weierstrass ainvs: [a1,a2,a3,a4,a6]

Probe types:
  1. MATCHED-OBJECT: For shared primes p, compare the full algebraic
     objects from both sides (knot with det=p vs EC with conductor=p)
  2. COEFFICIENT SPECTRAL: FFT of coefficient sequences, compare
     frequency structure across domains
  3. COEFFICIENT CORRELATION: Do specific coefficient positions
     correlate between matched objects?
  4. SYMMETRY: Alexander polys are palindromic. Do matched EC a_p
     sequences share any symmetry structure?
  5. GROWTH PROFILE: How do coefficients grow? Same rate?

Usage:
    python depth_probes.py                      # full depth scan
    python depth_probes.py --probe matched      # matched-object only
"""

import json
import sys
import time
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats as sp_stats
from scipy.fft import fft

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
RESULTS_FILE = ROOT / "cartography" / "convergence" / "data" / "depth_probe_results.json"


def load_ec_coefficients():
    """Load EC a_p and a_n lists from DuckDB, indexed by conductor."""
    from search_engine import _get_duck
    con = _get_duck()

    # a_p lists (L-function coefficients at primes)
    rows = con.execute("""
        SELECT conductor, aplist, anlist, rank, ainvs, lmfdb_label
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND conductor <= 50000
    """).fetchall()
    con.close()

    ec_data = defaultdict(list)
    for row in rows:
        cond = int(row[0])
        ec = {
            "conductor": cond,
            "label": row[5],
            "rank": row[3],
        }
        # Parse coefficient lists
        if row[1]:
            ap = row[1] if isinstance(row[1], list) else json.loads(row[1]) if isinstance(row[1], str) else None
            if ap:
                ec["aplist"] = [int(x) for x in ap]
        if row[2]:
            an = row[2] if isinstance(row[2], list) else json.loads(row[2]) if isinstance(row[2], str) else None
            if an:
                ec["anlist"] = [int(x) for x in an]
        if row[4]:
            ainvs = row[4] if isinstance(row[4], list) else json.loads(row[4]) if isinstance(row[4], str) else None
            if ainvs:
                ec["ainvs"] = [float(x) for x in ainvs]

        if ec.get("aplist") or ec.get("anlist"):
            ec_data[cond].append(ec)

    return ec_data


def load_knot_polynomials():
    """Load knot polynomial coefficients indexed by determinant."""
    from search_engine import _load_knots, _knots_cache
    _load_knots()

    knot_data = defaultdict(list)
    knot_list = _knots_cache.get("knots", []) if isinstance(_knots_cache, dict) else []

    for k in knot_list:
        if not isinstance(k, dict):
            continue
        det = k.get("determinant")
        if not det or not isinstance(det, (int, float)) or det <= 0:
            continue

        knot = {
            "determinant": int(det),
            "crossing_number": k.get("crossing_number", 0),
        }

        if k.get("alex_coeffs"):
            knot["alex_coeffs"] = k["alex_coeffs"]
            knot["alex_min_power"] = k.get("alexander", {}).get("min_power", 0)
        if k.get("jones_coeffs"):
            knot["jones_coeffs"] = k["jones_coeffs"]

        if knot.get("alex_coeffs") or knot.get("jones_coeffs"):
            knot_data[int(det)].append(knot)

    return knot_data


def find_matched_primes(ec_data, knot_data):
    """Find primes that appear as both EC conductor and knot determinant."""
    ec_conductors = set(ec_data.keys())
    knot_dets = set(knot_data.keys())
    shared = ec_conductors & knot_dets

    # Filter to actual primes (stronger bridge)
    def is_prime(n):
        if n < 2: return False
        for i in range(2, min(int(n**0.5)+1, 10000)):
            if n % i == 0: return False
        return True

    shared_primes = {p for p in shared if is_prime(p)}
    shared_composites = shared - shared_primes

    return shared, shared_primes, shared_composites


def probe_matched_coefficients(ec_data, knot_data, shared_values):
    """For matched objects (same prime as conductor/determinant),
    correlate their coefficient sequences."""

    results = {
        "n_matched": len(shared_values),
        "coefficient_correlations": [],
        "aggregate_stats": {},
    }

    # For each shared value, pair an EC with a knot and compare coefficients
    all_ap_coeffs = []    # EC side: a_p at position i
    all_alex_coeffs = []  # Knot side: Alexander at position i
    matched_pairs = []

    for val in sorted(shared_values):
        ecs = ec_data.get(val, [])
        knots = knot_data.get(val, [])
        if not ecs or not knots:
            continue

        # Take first EC and first knot at this value
        ec = ecs[0]
        knot = knots[0]

        ap = ec.get("aplist", [])
        alex = knot.get("alex_coeffs", [])

        if not ap or not alex:
            continue

        matched_pairs.append({
            "value": val,
            "ec_label": ec.get("label", ""),
            "ec_rank": ec.get("rank"),
            "knot_crossing": knot.get("crossing_number"),
            "ap_length": len(ap),
            "alex_length": len(alex),
        })

        # Pad shorter sequence with zeros for comparison
        max_len = max(len(ap), len(alex))
        ap_padded = ap + [0] * (max_len - len(ap))
        alex_padded = alex + [0] * (max_len - len(alex))

        all_ap_coeffs.append(ap_padded[:25])    # standardize length
        all_alex_coeffs.append(alex_padded[:25])

    if len(all_ap_coeffs) < 5:
        results["status"] = "INSUFFICIENT"
        results["n_pairs"] = len(all_ap_coeffs)
        return results

    # Convert to arrays
    ap_arr = np.array(all_ap_coeffs, dtype=float)
    alex_arr = np.array(all_alex_coeffs, dtype=float)
    n_pairs, n_coeffs = ap_arr.shape[0], min(ap_arr.shape[1], alex_arr.shape[1])

    results["n_pairs"] = n_pairs
    results["n_coeffs_compared"] = n_coeffs

    # Probe 1: Position-wise correlation
    # For each coefficient position i, correlate a_p[i] across all matched pairs
    # with Alexander[i] across all matched pairs
    pos_correlations = []
    for i in range(min(n_coeffs, 15)):
        ap_col = ap_arr[:, i]
        alex_col = alex_arr[:, i]
        if np.std(ap_col) < 1e-10 or np.std(alex_col) < 1e-10:
            continue
        rho, p_val = sp_stats.spearmanr(ap_col, alex_col)
        pos_correlations.append({
            "position": i,
            "rho": round(float(rho), 4),
            "p": round(float(p_val), 6),
        })
    results["position_correlations"] = pos_correlations

    # Any significant after Bonferroni?
    n_tests = len(pos_correlations)
    significant = [pc for pc in pos_correlations if pc["p"] < 0.05 / max(n_tests, 1)]
    results["significant_positions"] = significant
    results["n_significant"] = len(significant)

    # Probe 2: Row-wise correlation
    # For each matched pair, correlate the AP sequence with the Alexander sequence
    row_correlations = []
    for i in range(n_pairs):
        ap_row = ap_arr[i, :n_coeffs]
        alex_row = alex_arr[i, :n_coeffs]
        if np.std(ap_row) < 1e-10 or np.std(alex_row) < 1e-10:
            continue
        rho, p_val = sp_stats.spearmanr(ap_row, alex_row)
        row_correlations.append({
            "value": matched_pairs[i]["value"],
            "rho": round(float(rho), 4),
            "p": round(float(p_val), 6),
        })

    results["row_correlations_summary"] = {
        "n": len(row_correlations),
        "mean_rho": round(float(np.mean([r["rho"] for r in row_correlations])), 4) if row_correlations else 0,
        "std_rho": round(float(np.std([r["rho"] for r in row_correlations])), 4) if row_correlations else 0,
        "n_positive": sum(1 for r in row_correlations if r["rho"] > 0),
        "n_negative": sum(1 for r in row_correlations if r["rho"] < 0),
    }

    # Probe 3: FFT comparison
    # Compare frequency content of AP vs Alexander sequences
    fft_correlations = []
    for i in range(n_pairs):
        ap_fft = np.abs(fft(ap_arr[i, :n_coeffs]))[:n_coeffs//2]
        alex_fft = np.abs(fft(alex_arr[i, :n_coeffs]))[:n_coeffs//2]
        if len(ap_fft) >= 3 and np.std(ap_fft) > 1e-10 and np.std(alex_fft) > 1e-10:
            rho, _ = sp_stats.spearmanr(ap_fft, alex_fft)
            fft_correlations.append(float(rho))

    results["fft_correlation"] = {
        "mean_rho": round(float(np.mean(fft_correlations)), 4) if fft_correlations else 0,
        "std_rho": round(float(np.std(fft_correlations)), 4) if fft_correlations else 0,
        "n": len(fft_correlations),
    }

    # Probe 4: Symmetry
    # Alexander polys are palindromic. Count how many AP sequences have palindromic-like structure
    palindrome_scores_ap = []
    palindrome_scores_alex = []
    for i in range(n_pairs):
        ap_row = ap_arr[i, :n_coeffs]
        alex_row = alex_arr[i, :n_coeffs]
        # Palindrome score: correlation of sequence with its reverse
        if len(ap_row) >= 4:
            ap_pal = float(np.corrcoef(ap_row, ap_row[::-1])[0, 1])
            palindrome_scores_ap.append(ap_pal)
        if len(alex_row) >= 4:
            alex_pal = float(np.corrcoef(alex_row, alex_row[::-1])[0, 1])
            palindrome_scores_alex.append(alex_pal)

    results["symmetry"] = {
        "ap_palindrome_mean": round(float(np.mean(palindrome_scores_ap)), 4) if palindrome_scores_ap else 0,
        "alex_palindrome_mean": round(float(np.mean(palindrome_scores_alex)), 4) if palindrome_scores_alex else 0,
        "ap_n_palindromic": sum(1 for s in palindrome_scores_ap if s > 0.8),
        "alex_n_palindromic": sum(1 for s in palindrome_scores_alex if s > 0.8),
    }

    # Probe 5: Growth profile
    # Compare how coefficients grow in absolute value
    growth_correlations = []
    for i in range(n_pairs):
        ap_abs = np.abs(ap_arr[i, :n_coeffs])
        alex_abs = np.abs(alex_arr[i, :n_coeffs])
        if np.std(ap_abs) > 1e-10 and np.std(alex_abs) > 1e-10:
            rho, _ = sp_stats.spearmanr(ap_abs, alex_abs)
            growth_correlations.append(float(rho))

    results["growth_correlation"] = {
        "mean_rho": round(float(np.mean(growth_correlations)), 4) if growth_correlations else 0,
        "std_rho": round(float(np.std(growth_correlations)), 4) if growth_correlations else 0,
        "n": len(growth_correlations),
    }

    # Permutation test on the position-wise correlations
    # Null: shuffle which knot pairs with which EC (break the matching)
    if n_pairs >= 10 and pos_correlations:
        rng = np.random.RandomState(42)
        real_max_rho = max(abs(pc["rho"]) for pc in pos_correlations)
        null_max_rhos = []
        for _ in range(1000):
            # Shuffle rows of alex_arr (break the prime matching)
            shuffled = alex_arr[rng.permutation(n_pairs)]
            for j in range(min(n_coeffs, 15)):
                if np.std(ap_arr[:, j]) > 1e-10 and np.std(shuffled[:, j]) > 1e-10:
                    rho, _ = sp_stats.spearmanr(ap_arr[:, j], shuffled[:, j])
                    null_max_rhos.append(abs(float(rho)))

        null_arr = np.array(null_max_rhos)
        p_perm = float((np.sum(null_arr >= real_max_rho) + 1) / (len(null_arr) + 1))
        z_perm = float((real_max_rho - null_arr.mean()) / max(null_arr.std(), 1e-10))
        results["permutation_test"] = {
            "real_max_abs_rho": round(real_max_rho, 4),
            "null_mean": round(float(null_arr.mean()), 4),
            "null_std": round(float(null_arr.std()), 4),
            "p": round(p_perm, 6),
            "z": round(z_perm, 1),
            "verdict": "SIGNIFICANT" if p_perm < 0.01 else "NOT_SIGNIFICANT",
        }

    results["matched_pairs_sample"] = matched_pairs[:10]
    return results


def run_depth_probes():
    """Run all depth probes."""
    print("=" * 70)
    print("  DEPTH PROBES — Sequence-to-Sequence Cross-Dataset Analysis")
    print("  Phase 2: Polynomial coefficients, not scalar invariants")
    print("=" * 70)

    t0 = time.time()

    print("\n  Loading EC coefficient data...")
    ec_data = load_ec_coefficients()
    n_ec = sum(len(v) for v in ec_data.values())
    n_with_ap = sum(1 for ecs in ec_data.values() for ec in ecs if ec.get("aplist"))
    print(f"    {n_ec} curves at {len(ec_data)} conductors, {n_with_ap} with a_p lists")

    print("  Loading knot polynomial data...")
    knot_data = load_knot_polynomials()
    n_knots = sum(len(v) for v in knot_data.values())
    n_with_alex = sum(1 for knots in knot_data.values() for k in knots if k.get("alex_coeffs"))
    print(f"    {n_knots} knots at {len(knot_data)} determinants, {n_with_alex} with Alexander polys")

    # Find matched objects
    shared, shared_primes, shared_composites = find_matched_primes(ec_data, knot_data)
    print(f"\n  Matched values (det=conductor): {len(shared)}")
    print(f"    Primes: {len(shared_primes)}")
    print(f"    Composites: {len(shared_composites)}")

    # Run matched-object probes
    print(f"\n  Running matched-object coefficient probes...")

    # All shared values
    print(f"\n  --- ALL shared values ({len(shared)}) ---")
    all_results = probe_matched_coefficients(ec_data, knot_data, shared)
    _print_results(all_results)

    # Primes only (stronger bridge)
    print(f"\n  --- PRIMES only ({len(shared_primes)}) ---")
    prime_results = probe_matched_coefficients(ec_data, knot_data, shared_primes)
    _print_results(prime_results)

    elapsed = time.time() - t0

    # Save
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(elapsed, 1),
        "n_ec": n_ec,
        "n_knots": n_knots,
        "n_shared": len(shared),
        "n_shared_primes": len(shared_primes),
        "all_values_results": all_results,
        "primes_only_results": prime_results,
    }

    def _default(obj):
        if isinstance(obj, (np.integer, np.bool_)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return str(obj)

    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2, default=_default)

    print(f"\n{'=' * 70}")
    print(f"  DEPTH PROBES COMPLETE in {elapsed:.1f}s")
    print(f"  Results saved to {RESULTS_FILE}")
    print(f"{'=' * 70}")

    return output


def _print_results(results):
    """Print depth probe results."""
    print(f"    Matched pairs: {results.get('n_pairs', 0)}")
    print(f"    Coefficients compared: {results.get('n_coeffs_compared', 0)}")

    # Position correlations
    pos = results.get("position_correlations", [])
    if pos:
        print(f"    Position-wise correlations (a_p[i] vs Alexander[i]):")
        for pc in pos[:8]:
            sig = " *" if pc["p"] < 0.05 else ""
            print(f"      pos={pc['position']:2d}: rho={pc['rho']:+.4f} p={pc['p']:.4f}{sig}")

    sig = results.get("significant_positions", [])
    print(f"    Significant after Bonferroni: {len(sig)}")
    for s in sig:
        print(f"      pos={s['position']}: rho={s['rho']:+.4f} p={s['p']:.6f}")

    # Row correlations
    rc = results.get("row_correlations_summary", {})
    if rc:
        print(f"    Row correlations (per-pair): mean_rho={rc.get('mean_rho', 0):+.4f} "
              f"std={rc.get('std_rho', 0):.4f} "
              f"(+:{rc.get('n_positive', 0)}, -:{rc.get('n_negative', 0)})")

    # FFT
    fft_c = results.get("fft_correlation", {})
    if fft_c:
        print(f"    FFT correlation: mean_rho={fft_c.get('mean_rho', 0):+.4f}")

    # Symmetry
    sym = results.get("symmetry", {})
    if sym:
        print(f"    Palindrome: AP mean={sym.get('ap_palindrome_mean', 0):.4f}, "
              f"Alexander mean={sym.get('alex_palindrome_mean', 0):.4f}")

    # Growth
    gc = results.get("growth_correlation", {})
    if gc:
        print(f"    Growth correlation: mean_rho={gc.get('mean_rho', 0):+.4f}")

    # Permutation test
    perm = results.get("permutation_test", {})
    if perm:
        print(f"    Permutation test: max|rho|={perm.get('real_max_abs_rho', 0):.4f} "
              f"null={perm.get('null_mean', 0):.4f}+/-{perm.get('null_std', 0):.4f} "
              f"p={perm.get('p', 1):.4f} z={perm.get('z', 0):.1f} "
              f"[{perm.get('verdict', '?')}]")


if __name__ == "__main__":
    run_depth_probes()
