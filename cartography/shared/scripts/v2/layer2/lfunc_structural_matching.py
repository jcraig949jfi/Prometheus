"""
L-function Structural Matching (S37) — Direct Modularity Probe
================================================================
Takes L-function coefficient sequences from LMFDB elliptic curves and
structurally matches them against modular form Hecke eigenvalues.

The modularity theorem: every EC/Q has an associated weight-2 newform
such that their L-functions are identical (a_p match at every prime).
In our DuckDB, invariant_vector stores a_p at primes 2..97 (indices 0-24
for ECs, 0-49 for MFs).

If modularity is structurally detectable, this tool finds it.

Algorithm:
  1. Load EC invariant_vectors (first 25 a_p values) from DuckDB
  2. Load MF invariant_vectors (first 25+ a_p values) from DuckDB
  3. For each EC, find MFs whose coefficient prefix matches:
     - Exact match (all 25 a_p identical): modularity rediscovery
     - Partial match (first N match, rest diverge): partial modularity
  4. Cross-check: conductor(EC) == level(MF) for known pairs
  5. Berlekamp-Massey recurrence + mod-p fingerprints for structural probes

Usage:
    python lfunc_structural_matching.py
    python lfunc_structural_matching.py --max-curves 500 --max-forms 10000
    python lfunc_structural_matching.py --min-match 15
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from search_engine import _get_duck

ROOT = Path(__file__).resolve().parents[5]
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "lfunc_matches.jsonl"

# First 25 primes (indices 0-24 in invariant_vector)
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

# Modular primes for fingerprinting
MOD_PRIMES = [5, 7, 11, 13, 17, 19, 23]


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ---------------------------------------------------------------------------
# Berlekamp-Massey over integers (finds minimal linear recurrence)
# ---------------------------------------------------------------------------
def berlekamp_massey_int(seq):
    """
    Berlekamp-Massey for integer sequences.
    Returns the minimal recurrence coefficients [c1, c2, ..., cL]
    such that s[n] = c1*s[n-1] + c2*s[n-2] + ... + cL*s[n-L].
    Returns None if no recurrence of length < len(seq)//2 is found.
    """
    from fractions import Fraction
    n = len(seq)
    if n == 0:
        return None
    s = [Fraction(x) for x in seq]

    # LFSR synthesis
    C = [Fraction(1)]
    B = [Fraction(1)]
    L, m, b = 0, 1, Fraction(1)

    for i in range(n):
        d = s[i]
        for j in range(1, L + 1):
            if j < len(C):
                d += C[j] * s[i - j]
        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = list(C)
            coeff = d / b
            while len(C) < len(B) + m:
                C.append(Fraction(0))
            for j in range(len(B)):
                C[j + m] -= coeff * B[j]
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            coeff = d / b
            while len(C) < len(B) + m:
                C.append(Fraction(0))
            for j in range(len(B)):
                C[j + m] -= coeff * B[j]
            m += 1

    if L == 0 or L >= n // 2:
        return None

    # Return recurrence coefficients: s[n] = -C[1]*s[n-1] - C[2]*s[n-2] - ...
    return [-float(C[j]) for j in range(1, L + 1)]


def characteristic_poly(recurrence):
    """
    Given recurrence [c1, c2, ..., cL], return characteristic polynomial
    coefficients [1, -c1, -c2, ..., -cL] (monic).
    """
    if recurrence is None:
        return None
    return [1.0] + [-c for c in recurrence]


# ---------------------------------------------------------------------------
# Mod-p fingerprint
# ---------------------------------------------------------------------------
def mod_p_fingerprint(vec, mod_primes=None):
    """
    Compute a tuple of (a_p mod m) for each modular prime m.
    This creates a compact arithmetic fingerprint.
    """
    if mod_primes is None:
        mod_primes = MOD_PRIMES
    fp = []
    for m in mod_primes:
        fp.append(tuple(int(round(v)) % m for v in vec))
    return tuple(fp)


# ---------------------------------------------------------------------------
# Data loading from DuckDB
# ---------------------------------------------------------------------------
def load_elliptic_curves(max_curves=None):
    """Load EC labels, conductors, and a_p vectors from DuckDB."""
    con = _get_duck()
    query = """
        SELECT lmfdb_label, conductor, invariant_vector, properties
        FROM objects
        WHERE object_type = 'elliptic_curve'
        ORDER BY conductor
    """
    if max_curves:
        query += f" LIMIT {int(max_curves)}"
    rows = con.execute(query).fetchall()
    con.close()

    curves = []
    for label, conductor, ivec, props in rows:
        if ivec is None:
            continue
        # Extract non-None a_p values
        ap = [v for v in ivec if v is not None]
        if len(ap) < 5:
            continue
        props_dict = json.loads(props) if isinstance(props, str) else (props or {})
        curves.append({
            "label": label,
            "conductor": int(conductor),
            "ap": np.array(ap, dtype=float),
            "n_coeffs": len(ap),
            "rank": props_dict.get("rank"),
        })
    return curves


def load_modular_forms(max_forms=None):
    """Load MF labels, levels, and Hecke eigenvalue vectors from DuckDB."""
    con = _get_duck()
    query = """
        SELECT lmfdb_label, conductor, invariant_vector, properties
        FROM objects
        WHERE object_type = 'modular_form'
        ORDER BY conductor
    """
    if max_forms:
        query += f" LIMIT {int(max_forms)}"
    rows = con.execute(query).fetchall()
    con.close()

    forms = []
    for label, conductor, ivec, props in rows:
        if ivec is None:
            continue
        ap = [v for v in ivec if v is not None]
        if len(ap) < 5:
            continue
        props_dict = json.loads(props) if isinstance(props, str) else (props or {})
        forms.append({
            "label": label,
            "level": int(conductor),
            "ap": np.array(ap, dtype=float),
            "n_coeffs": len(ap),
            "dim": props_dict.get("dim"),
            "weight": props_dict.get("weight"),
        })
    return forms


# ---------------------------------------------------------------------------
# Matching engine
# ---------------------------------------------------------------------------
def count_matching_coeffs(vec_a, vec_b, tol=1e-6):
    """Count how many leading coefficients match exactly."""
    n = min(len(vec_a), len(vec_b))
    for i in range(n):
        if abs(vec_a[i] - vec_b[i]) > tol:
            return i
    return n


def build_fingerprint_index(forms):
    """Build hash index from first-N a_p tuple -> list of form indices.
    This avoids O(n*m) brute force matching."""
    index = defaultdict(list)
    for i, mf in enumerate(forms):
        # Use first 10 a_p as integer tuple for fast hashing
        n = min(10, len(mf["ap"]))
        key = tuple(int(round(v)) for v in mf["ap"][:n])
        index[key].append(i)
    return index


def find_matches(curves, forms, min_match=10, verbose=True):
    """
    For each EC, find MFs with matching coefficient prefixes.

    Uses hash-index on first 10 coefficients for exact-match fast path,
    then falls back to partial matching for near-misses.
    """
    results = []
    # Build fast index for exact matching
    fp_index = build_fingerprint_index(forms)

    # Also build recurrence + mod-p data lazily
    ec_recurrences = {}
    mf_recurrences = {}
    ec_fingerprints = {}
    mf_fingerprints = {}

    n_exact = 0
    n_partial = 0
    n_novel = 0
    n_recurrence = 0
    n_modp = 0

    t0 = time.time()
    for ci, ec in enumerate(curves):
        if verbose and ci > 0 and ci % 1000 == 0:
            elapsed = time.time() - t0
            print(f"  [{ci}/{len(curves)}] {elapsed:.1f}s  exact={n_exact} partial={n_partial} novel={n_novel}")

        ec_key = tuple(int(round(v)) for v in ec["ap"][:min(10, len(ec["ap"]))])

        # --- Fast path: exact first-10 match ---
        candidates = fp_index.get(ec_key, [])
        for fi in candidates:
            mf = forms[fi]
            n_match = count_matching_coeffs(ec["ap"], mf["ap"])
            if n_match < min_match:
                continue

            is_exact = (n_match >= ec["n_coeffs"])  # All EC coefficients matched
            conductor_match = (ec["conductor"] == mf["level"])

            match_type = "exact" if is_exact else "partial"
            if is_exact and conductor_match:
                match_type = "exact_modularity"
                n_exact += 1
            elif is_exact and not conductor_match:
                match_type = "exact_novel"
                n_novel += 1
            else:
                n_partial += 1

            result = {
                "ec_label": ec["label"],
                "mf_label": mf["label"],
                "match_type": match_type,
                "n_matching_coeffs": n_match,
                "n_ec_coeffs": ec["n_coeffs"],
                "n_mf_coeffs": mf["n_coeffs"],
                "conductor": ec["conductor"],
                "level": mf["level"],
                "conductor_eq_level": conductor_match,
                "ec_rank": ec["rank"],
                "mf_dim": mf["dim"],
                "mf_weight": mf["weight"],
            }

            if verbose:
                tag = "***NOVEL***" if match_type == "exact_novel" else match_type
                print(f"  MATCH [{tag}] EC {ec['label']} <-> MF {mf['label']}  "
                      f"n_match={n_match}/{ec['n_coeffs']}  "
                      f"conductor={ec['conductor']} level={mf['level']}")

            results.append(result)

        # --- Recurrence matching (for ECs without exact match) ---
        if not candidates:
            if ci not in ec_recurrences:
                ec_recurrences[ci] = berlekamp_massey_int(
                    [int(round(v)) for v in ec["ap"]]
                )
            ec_rec = ec_recurrences[ci]
            if ec_rec is not None:
                ec_cpoly = tuple(round(c, 8) for c in characteristic_poly(ec_rec))
                ec_fp = mod_p_fingerprint(ec["ap"])

                # Check a sample of MFs for recurrence/fingerprint match
                # (full scan only for ECs that had no exact match)
                for fi, mf in enumerate(forms):
                    if mf["level"] != ec["conductor"]:
                        continue  # Only check same-conductor MFs for structural match
                    if fi not in mf_recurrences:
                        mf_recurrences[fi] = berlekamp_massey_int(
                            [int(round(v)) for v in mf["ap"][:ec["n_coeffs"]]]
                        )
                    mf_rec = mf_recurrences[fi]
                    if mf_rec is not None:
                        mf_cpoly = tuple(round(c, 8) for c in characteristic_poly(mf_rec))
                        if ec_cpoly == mf_cpoly:
                            n_match = count_matching_coeffs(ec["ap"], mf["ap"])
                            n_recurrence += 1
                            result = {
                                "ec_label": ec["label"],
                                "mf_label": mf["label"],
                                "match_type": "recurrence_match",
                                "n_matching_coeffs": n_match,
                                "n_ec_coeffs": ec["n_coeffs"],
                                "n_mf_coeffs": mf["n_coeffs"],
                                "conductor": ec["conductor"],
                                "level": mf["level"],
                                "conductor_eq_level": True,
                                "ec_rank": ec["rank"],
                                "mf_dim": mf["dim"],
                                "mf_weight": mf["weight"],
                                "recurrence_length": len(ec_rec),
                                "char_poly": list(ec_cpoly),
                            }
                            if verbose:
                                print(f"  MATCH [recurrence] EC {ec['label']} <-> MF {mf['label']}  "
                                      f"rec_len={len(ec_rec)}")
                            results.append(result)

                    # Mod-p fingerprint check
                    if fi not in mf_fingerprints:
                        mf_fingerprints[fi] = mod_p_fingerprint(mf["ap"][:ec["n_coeffs"]])
                    if ec_fp == mf_fingerprints[fi]:
                        # Verify it's not already captured
                        already = any(r["ec_label"] == ec["label"] and r["mf_label"] == mf["label"]
                                      for r in results[-20:])
                        if not already:
                            n_match = count_matching_coeffs(ec["ap"], mf["ap"])
                            n_modp += 1
                            result = {
                                "ec_label": ec["label"],
                                "mf_label": mf["label"],
                                "match_type": "mod_p_fingerprint",
                                "n_matching_coeffs": n_match,
                                "n_ec_coeffs": ec["n_coeffs"],
                                "n_mf_coeffs": mf["n_coeffs"],
                                "conductor": ec["conductor"],
                                "level": mf["level"],
                                "conductor_eq_level": True,
                                "ec_rank": ec["rank"],
                                "mf_dim": mf["dim"],
                                "mf_weight": mf["weight"],
                            }
                            if verbose:
                                print(f"  MATCH [mod-p] EC {ec['label']} <-> MF {mf['label']}  "
                                      f"n_match={n_match}")
                            results.append(result)

    elapsed = time.time() - t0
    return results, {
        "n_exact_modularity": n_exact,
        "n_partial": n_partial,
        "n_novel": n_novel,
        "n_recurrence": n_recurrence,
        "n_modp": n_modp,
        "total_matches": len(results),
        "n_curves": len(curves),
        "n_forms": len(forms),
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Verification: sanity checks on matches
# ---------------------------------------------------------------------------
def verify_matches(results):
    """
    Post-match verification:
    - Exact modularity: conductor must == level
    - Novel matches: flag for manual investigation
    - Check for duplicate matches (same EC matched to multiple MFs)
    """
    issues = []
    ec_match_counts = defaultdict(int)

    for r in results:
        ec_match_counts[r["ec_label"]] += 1

        if r["match_type"] == "exact_modularity":
            if not r["conductor_eq_level"]:
                issues.append(f"BUG: exact_modularity but conductor != level: {r}")

        if r["match_type"] == "exact_novel":
            issues.append(
                f"INVESTIGATE: exact match with conductor != level: "
                f"EC {r['ec_label']} (N={r['conductor']}) <-> "
                f"MF {r['mf_label']} (level={r['level']})"
            )

    # Check for ECs with multiple MF matches (expected for isogenous curves)
    multi = {ec: n for ec, n in ec_match_counts.items() if n > 1}
    if multi:
        issues.append(f"INFO: {len(multi)} ECs matched multiple MFs (expected for isogenous curves)")

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="S37: L-function structural matching (modularity probe)"
    )
    parser.add_argument("--max-curves", type=int, default=None,
                        help="Max elliptic curves to load (default: all)")
    parser.add_argument("--max-forms", type=int, default=None,
                        help="Max modular forms to load (default: all)")
    parser.add_argument("--min-match", type=int, default=10,
                        help="Min matching coefficients to report (default: 10)")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-match output")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSONL path (default: convergence/data/lfunc_matches.jsonl)")
    args = parser.parse_args()

    out_path = Path(args.output) if args.output else OUT_FILE
    verbose = not args.quiet

    print("=" * 72)
    print("S37: L-function Structural Matching — Direct Modularity Probe")
    print("=" * 72)

    # 1. Load data
    print("\n[1] Loading elliptic curves from DuckDB...")
    t0 = time.time()
    curves = load_elliptic_curves(max_curves=args.max_curves)
    print(f"    Loaded {len(curves)} ECs in {time.time()-t0:.1f}s")
    if not curves:
        print("    ERROR: No elliptic curves found. Exiting.")
        return

    print("\n[2] Loading modular forms from DuckDB...")
    t0 = time.time()
    forms = load_modular_forms(max_forms=args.max_forms)
    print(f"    Loaded {len(forms)} MFs in {time.time()-t0:.1f}s")
    if not forms:
        print("    ERROR: No modular forms found. Exiting.")
        return

    # 2. Conductor/level overlap
    ec_conductors = set(c["conductor"] for c in curves)
    mf_levels = set(f["level"] for f in forms)
    overlap = ec_conductors & mf_levels
    print(f"\n    Conductor/level overlap: {len(overlap)} values "
          f"(EC has {len(ec_conductors)} distinct, MF has {len(mf_levels)} distinct)")

    # 3. Match
    print(f"\n[3] Matching (min_match={args.min_match})...")
    results, summary = find_matches(curves, forms, min_match=args.min_match, verbose=verbose)

    # 4. Verify
    print(f"\n[4] Verification...")
    issues = verify_matches(results)
    for issue in issues:
        print(f"    {issue}")

    # 5. Summary
    print(f"\n{'=' * 72}")
    print(f"SUMMARY")
    print(f"{'=' * 72}")
    print(f"  Elliptic curves scanned:     {summary['n_curves']:>8,}")
    print(f"  Modular forms scanned:       {summary['n_forms']:>8,}")
    print(f"  Total matches found:         {summary['total_matches']:>8,}")
    print(f"  ---- By match type ----")
    print(f"  Exact modularity (N==level): {summary['n_exact_modularity']:>8,}")
    print(f"  Partial (first N match):     {summary['n_partial']:>8,}")
    print(f"  Novel (exact, N!=level):     {summary['n_novel']:>8,}")
    print(f"  Recurrence match:            {summary['n_recurrence']:>8,}")
    print(f"  Mod-p fingerprint:           {summary['n_modp']:>8,}")
    print(f"  Elapsed:                     {summary['elapsed_s']:>8.1f}s")

    if summary["n_exact_modularity"] > 0:
        pct = 100.0 * summary["n_exact_modularity"] / summary["n_curves"]
        print(f"\n  MODULARITY DETECTION RATE: {pct:.1f}% of ECs matched a MF exactly")
        print(f"  (Theoretical expectation: 100% for weight-2 dim-1 newforms)")

    if summary["n_novel"] > 0:
        print(f"\n  *** {summary['n_novel']} NOVEL MATCHES FOUND (conductor != level) ***")
        print(f"  *** These require careful investigation ***")

    # 6. Write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        # Write summary as first line
        f.write(json.dumps({"_type": "summary", **summary}, cls=_NumpyEncoder) + "\n")
        for r in results:
            f.write(json.dumps(r, cls=_NumpyEncoder) + "\n")
    print(f"\n  Output: {out_path} ({len(results)+1} lines)")

    # 7. Sample matches for inspection
    if results:
        print(f"\n{'=' * 72}")
        print(f"SAMPLE MATCHES (first 10)")
        print(f"{'=' * 72}")
        for r in results[:10]:
            print(f"  EC {r['ec_label']:>12s} <-> MF {r['mf_label']:>12s}  "
                  f"type={r['match_type']:<20s}  "
                  f"n_match={r['n_matching_coeffs']}/{r['n_ec_coeffs']}  "
                  f"N={r['conductor']}  level={r['level']}")


if __name__ == "__main__":
    main()
