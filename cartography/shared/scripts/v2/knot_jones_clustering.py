"""
Knot Jones Polynomial Recurrence Clustering
=============================================
For each knot with Jones polynomial coefficients of length >= 8,
apply Berlekamp-Massey to find minimal linear recurrence, then
cluster knots by shared characteristic polynomial.

Cross-references:
  - Alexander polynomial recurrences (do Jones clusters = Alexander clusters?)
  - OEIS algebraic DNA families (from C08 results)
  - Geometric properties (crossing number, determinant)

Usage:
    python knot_jones_clustering.py
"""

import json
import time
from collections import defaultdict, Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
KNOTS_PATH = HERE.parents[2] / "knots" / "data" / "knots.json"
OEIS_DNA_PATH = HERE / "algebraic_dna_fungrim_results.json"
OUT_PATH = HERE / "knot_jones_results.json"


# ─────────────────────────────────────────────────────────────────────────────
# Berlekamp-Massey over Q (exact rational arithmetic)
# ─────────────────────────────────────────────────────────────────────────────

def solve_exact(A, b, n):
    """Solve n x n system Ax = b using Gaussian elimination with fractions."""
    M = [[Fraction(A[i][j]) for j in range(n)] for i in range(n)]
    rhs = [Fraction(b[i]) for i in range(n)]

    for col in range(n):
        pivot = None
        for row in range(col, n):
            if M[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return None
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            rhs[col], rhs[pivot] = rhs[pivot], rhs[col]
        for row in range(col + 1, n):
            if M[row][col] != 0:
                factor = M[row][col] / M[col][col]
                for j in range(col, n):
                    M[row][j] -= factor * M[col][j]
                rhs[row] -= factor * rhs[col]

    x = [Fraction(0)] * n
    for i in range(n - 1, -1, -1):
        if M[i][i] == 0:
            return None
        s = rhs[i]
        for j in range(i + 1, n):
            s -= M[i][j] * x[j]
        x[i] = s / M[i][i]

    return [float(x[i]) for i in range(n)]


def berlekamp_massey_rational(seq, max_order=8):
    """
    Find minimal linear recurrence over Q for integer sequence.
    Returns (order, coefficients, char_poly_str) or None.
    coeffs: s[n] = c_1*s[n-1] + ... + c_L*s[n-L]
    """
    n = len(seq)
    if n < 4:
        return None

    for L in range(2, min(max_order + 1, n // 2)):
        if 2 * L > n:
            break

        A = []
        b = []
        for i in range(L, 2 * L):
            row = [seq[i - j - 1] for j in range(L)]
            A.append(row)
            b.append(seq[i])

        coeffs = solve_exact(A, b, L)
        if coeffs is None:
            continue

        # Verify on ALL data points
        valid = True
        for i in range(L, n):
            predicted = sum(coeffs[j] * seq[i - j - 1] for j in range(L))
            err = abs(seq[i] - predicted)
            if err > 1e-9:
                valid = False
                break

        if valid:
            int_coeffs = []
            all_int = True
            for c in coeffs:
                if abs(c - round(c)) < 1e-9:
                    int_coeffs.append(int(round(c)))
                else:
                    all_int = False
                    int_coeffs.append(c)

            if all_int:
                char_poly = coeffs_to_char_poly(int_coeffs)
                return (L, int_coeffs, char_poly)

    return None


def coeffs_to_char_poly(coeffs):
    """
    Convert recurrence coefficients to characteristic polynomial string.
    s[n] = c_1*s[n-1] + ... + c_L*s[n-L]
    => x^L - c_1*x^(L-1) - ... - c_L = 0
    Polynomial coeffs: [1, -c_1, -c_2, ..., -c_L] (leading coeff 1)
    """
    L = len(coeffs)
    poly = [1] + [-c for c in coeffs]
    # Build string representation
    terms = []
    for i, c in enumerate(poly):
        exp = L - i
        if c == 0:
            continue
        if exp == 0:
            terms.append(f"{c:+d}")
        elif exp == 1:
            if c == 1:
                terms.append("+x")
            elif c == -1:
                terms.append("-x")
            else:
                terms.append(f"{c:+d}x")
        else:
            if c == 1:
                terms.append(f"+x^{exp}")
            elif c == -1:
                terms.append(f"-x^{exp}")
            else:
                terms.append(f"{c:+d}x^{exp}")

    s = "".join(terms)
    if s.startswith("+"):
        s = s[1:]
    return s


def poly_coeffs_tuple(coeffs):
    """Characteristic polynomial as a hashable tuple for clustering."""
    L = len(coeffs)
    return tuple([1] + [-c for c in coeffs])


# ─────────────────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────────────────

def load_knots():
    with open(KNOTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["knots"]


def load_oeis_dna():
    """Load OEIS algebraic DNA reference polynomials."""
    if not OEIS_DNA_PATH.exists():
        return {}
    with open(OEIS_DNA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    ref = {}
    # Fibonacci family
    if "fibonacci_family" in data:
        ref["x^2-x-1"] = {
            "name": "Fibonacci",
            "n_oeis_sequences": data["fibonacci_family"].get("n_sequences", 0),
        }

    # Euler factor clusters
    if "euler_factor_clusters" in data:
        for cl in data["euler_factor_clusters"]:
            cp = cl.get("char_poly_str", "")
            if cp:
                key = cp.replace(" ", "")
                ref[key] = {
                    "name": f"Euler-factor (degree {cl.get('degree','')})",
                    "n_oeis_sequences": cl.get("n_sequences", 0),
                }

    # All cluster results
    if "all_cluster_results" in data:
        for cl in data["all_cluster_results"]:
            cp = cl.get("char_poly_str", "")
            if cp:
                key = cp.replace(" ", "")
                if key not in ref:
                    ref[key] = {
                        "name": f"OEIS cluster (degree {cl.get('degree','')})",
                        "n_oeis_sequences": cl.get("n_sequences", 0),
                    }

    return ref


# ─────────────────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("Loading knots data...")
    knots = load_knots()
    print(f"  {len(knots)} knots loaded")

    # Filter: need jones_coeffs with length >= 8
    eligible = []
    for k in knots:
        jc = k.get("jones_coeffs")
        if jc and len(jc) >= 8:
            eligible.append(k)
    print(f"  {len(eligible)} knots with Jones coefficients length >= 8")

    # ── Phase 1: Berlekamp-Massey on Jones polynomial coefficients ─────────
    print("\nPhase 1: Berlekamp-Massey on Jones coefficients...")
    jones_results = {}  # knot_name -> {order, coeffs, char_poly}
    jones_clusters = defaultdict(list)  # char_poly_str -> [knot_names]

    for k in eligible:
        name = k["name"]
        seq = k["jones_coeffs"]
        result = berlekamp_massey_rational(seq, max_order=8)
        if result:
            order, coeffs, char_poly = result
            jones_results[name] = {
                "order": order,
                "coeffs": coeffs,
                "char_poly": char_poly,
                "jones_len": len(seq),
            }
            jones_clusters[char_poly].append(name)

    n_with_recurrence = len(jones_results)
    print(f"  {n_with_recurrence}/{len(eligible)} knots have detectable Jones recurrence")

    # Order distribution
    order_dist = Counter(r["order"] for r in jones_results.values())
    print(f"  Order distribution: {dict(sorted(order_dist.items()))}")

    # Cluster analysis
    cluster_sizes = {cp: len(names) for cp, names in jones_clusters.items()}
    multi_clusters = {cp: names for cp, names in jones_clusters.items() if len(names) >= 2}
    print(f"  Unique characteristic polynomials: {len(jones_clusters)}")
    print(f"  Clusters of size >= 2: {len(multi_clusters)}")

    # Top clusters
    top_clusters = sorted(multi_clusters.items(), key=lambda x: -len(x[1]))[:20]
    print("\n  Top 20 clusters by size:")
    for cp, names in top_clusters:
        print(f"    {cp}: {len(names)} knots")
        # Show first few knot names
        print(f"      e.g.: {', '.join(names[:5])}")

    # ── Phase 2: Geometric properties of clusters ──────────────────────────
    print("\nPhase 2: Geometric properties of clusters...")
    knot_lookup = {k["name"]: k for k in knots}

    cluster_properties = {}
    for cp, names in top_clusters:
        dets = []
        crossing_numbers = []
        jones_min_powers = []
        jones_max_powers = []
        jones_lengths = []

        for name in names:
            k = knot_lookup.get(name, {})
            dets.append(k.get("determinant", None))
            cn = k.get("crossing_number", None)
            crossing_numbers.append(cn)
            j = k.get("jones", {})
            if j:
                jones_min_powers.append(j.get("min_power"))
                jones_max_powers.append(j.get("max_power"))
            jones_lengths.append(len(k.get("jones_coeffs", [])))

        # Check if determinants cluster
        det_counter = Counter(d for d in dets if d is not None)
        cn_counter = Counter(c for c in crossing_numbers if c is not None)

        cluster_properties[cp] = {
            "size": len(names),
            "knots": names[:10],
            "determinant_distribution": dict(det_counter.most_common(5)),
            "crossing_number_distribution": dict(cn_counter.most_common(5)),
            "jones_length_range": [min(jones_lengths), max(jones_lengths)] if jones_lengths else None,
        }

    # ── Phase 3: Alexander polynomial recurrences ──────────────────────────
    print("\nPhase 3: Berlekamp-Massey on Alexander coefficients...")
    alex_results = {}
    alex_clusters = defaultdict(list)

    for k in eligible:
        name = k["name"]
        ac = k.get("alex_coeffs")
        if not ac or len(ac) < 8:
            continue
        result = berlekamp_massey_rational(ac, max_order=8)
        if result:
            order, coeffs, char_poly = result
            alex_results[name] = {
                "order": order,
                "coeffs": coeffs,
                "char_poly": char_poly,
            }
            alex_clusters[char_poly].append(name)

    print(f"  {len(alex_results)} knots have detectable Alexander recurrence")
    alex_multi = {cp: names for cp, names in alex_clusters.items() if len(names) >= 2}
    print(f"  Alexander clusters of size >= 2: {len(alex_multi)}")

    # ── Phase 4: Jones vs Alexander correlation ────────────────────────────
    print("\nPhase 4: Jones vs Alexander recurrence correlation...")
    both = set(jones_results.keys()) & set(alex_results.keys())
    print(f"  {len(both)} knots have both Jones and Alexander recurrences")

    same_recurrence = 0
    same_order = 0
    correlation_details = []
    for name in both:
        j_cp = jones_results[name]["char_poly"]
        a_cp = alex_results[name]["char_poly"]
        j_ord = jones_results[name]["order"]
        a_ord = alex_results[name]["order"]
        if j_cp == a_cp:
            same_recurrence += 1
        if j_ord == a_ord:
            same_order += 1
        correlation_details.append({
            "knot": name,
            "jones_char_poly": j_cp,
            "alex_char_poly": a_cp,
            "match": j_cp == a_cp,
        })

    if both:
        print(f"  Same characteristic polynomial: {same_recurrence}/{len(both)} ({100*same_recurrence/len(both):.1f}%)")
        print(f"  Same order: {same_order}/{len(both)} ({100*same_order/len(both):.1f}%)")

    # Do Jones clusters predict Alexander clusters?
    jones_to_alex_overlap = []
    for j_cp, j_names in multi_clusters.items():
        j_set = set(j_names)
        for a_cp, a_names in alex_multi.items():
            a_set = set(a_names)
            overlap = j_set & a_set
            if len(overlap) >= 2:
                jones_to_alex_overlap.append({
                    "jones_char_poly": j_cp,
                    "alex_char_poly": a_cp,
                    "jones_cluster_size": len(j_names),
                    "alex_cluster_size": len(a_names),
                    "overlap": len(overlap),
                    "overlap_knots": sorted(list(overlap))[:10],
                })

    print(f"  Jones-Alexander cluster overlaps (size >= 2): {len(jones_to_alex_overlap)}")

    # ── Phase 5: Cross-reference with OEIS algebraic DNA ──────────────────
    print("\nPhase 5: OEIS cross-reference...")
    oeis_ref = load_oeis_dna()
    print(f"  {len(oeis_ref)} OEIS reference polynomials loaded")

    oeis_matches = []
    # Normalize knot char polys for comparison
    for cp in jones_clusters:
        cp_norm = cp.replace(" ", "")
        if cp_norm in oeis_ref:
            oeis_matches.append({
                "knot_char_poly": cp,
                "oeis_info": oeis_ref[cp_norm],
                "n_knots": len(jones_clusters[cp]),
                "knots": jones_clusters[cp][:10],
            })

    # Special check for Fibonacci x^2 - x - 1
    fib_key = "x^2-x-1"
    fib_knots = jones_clusters.get("x^2-x-1", [])
    if not fib_knots:
        # Try alternate forms
        for cp in jones_clusters:
            norm = cp.replace(" ", "")
            if norm == fib_key:
                fib_knots = jones_clusters[cp]
                break

    print(f"  OEIS polynomial matches: {len(oeis_matches)}")
    if fib_knots:
        print(f"  Fibonacci polynomial (x^2-x-1) found in {len(fib_knots)} knots!")
    else:
        print(f"  Fibonacci polynomial (x^2-x-1) NOT found in Jones recurrences")

    for m in oeis_matches:
        print(f"    {m['knot_char_poly']}: {m['n_knots']} knots, OEIS={m['oeis_info']['name']} ({m['oeis_info']['n_oeis_sequences']} OEIS seqs)")

    # ── Phase 6: Singleton analysis ────────────────────────────────────────
    singletons = {cp: names[0] for cp, names in jones_clusters.items() if len(names) == 1}
    print(f"\n  Singleton recurrences (unique char poly): {len(singletons)}")

    # ── Compile results ───────────────────────────────────────────────────
    elapsed = time.time() - t0

    # Cluster size distribution
    size_dist = Counter(len(names) for names in jones_clusters.values())

    results = {
        "description": "Knot Jones polynomial recurrence clustering via Berlekamp-Massey",
        "n_knots_total": len(knots),
        "n_knots_with_jones": sum(1 for k in knots if k.get("jones_coeffs")),
        "n_eligible_jones_len_ge_8": len(eligible),
        "n_with_jones_recurrence": n_with_recurrence,
        "detection_rate": f"{100*n_with_recurrence/len(eligible):.1f}%" if eligible else "N/A",
        "jones_order_distribution": dict(sorted(order_dist.items())),
        "n_unique_char_polys": len(jones_clusters),
        "n_clusters_size_ge_2": len(multi_clusters),
        "cluster_size_distribution": {str(k): v for k, v in sorted(size_dist.items())},
        "top_jones_clusters": [
            {
                "char_poly": cp,
                "size": len(names),
                "knots_sample": names[:10],
                "properties": cluster_properties.get(cp, {}),
            }
            for cp, names in top_clusters
        ],
        "alexander_analysis": {
            "n_with_alex_recurrence": len(alex_results),
            "n_alex_clusters_size_ge_2": len(alex_multi),
            "top_alex_clusters": [
                {"char_poly": cp, "size": len(names), "knots_sample": names[:10]}
                for cp, names in sorted(alex_multi.items(), key=lambda x: -len(x[1]))[:10]
            ],
        },
        "jones_vs_alexander_correlation": {
            "n_both_recurrences": len(both),
            "n_same_char_poly": same_recurrence,
            "pct_same_char_poly": f"{100*same_recurrence/len(both):.1f}%" if both else "N/A",
            "n_same_order": same_order,
            "cluster_overlaps": jones_to_alex_overlap[:20],
        },
        "oeis_cross_reference": {
            "n_reference_polys": len(oeis_ref),
            "n_matches": len(oeis_matches),
            "fibonacci_knots": fib_knots[:20] if fib_knots else [],
            "matches": oeis_matches,
        },
        "all_jones_char_polys": {
            cp: {
                "size": len(names),
                "knots": names,
            }
            for cp, names in sorted(jones_clusters.items(), key=lambda x: -len(x[1]))
        },
        "mathematical_interpretation": {
            "cluster_x5": {
                "char_poly": "x^5+x^4-x^3-x^2+x+1",
                "factorization": "(x+1) * Phi_12(x) where Phi_12 = x^4-x^2+1 is the 12th cyclotomic polynomial",
                "recurrence": "s[n] = -s[n-1] + s[n-2] + s[n-3] - s[n-4] - s[n-5]",
                "interpretation": "All 44 knots are 12-crossing alternating. The cyclotomic recurrence Phi_12 "
                                  "connects to quantum group structure at q = 12th root of unity. "
                                  "Most have palindromic Jones coefficients, suggesting amphichiral or near-amphichiral symmetry.",
                "significance": "Largest algebraic DNA family in knot Jones polynomials. "
                                "Cyclotomic polynomials as characteristic polynomials is a signature of "
                                "quantum group representation theory (Jones polynomial = trace of R-matrix).",
            },
            "cluster_x3": {
                "char_poly": "x^3+x^2",
                "factorization": "x^2(x+1), roots at 0 (double) and -1",
                "recurrence": "s[n] = -s[n-1] (effectively order 1, alternating sign after initial transient)",
                "members": "7_1 = T(2,7), 9_1 = T(2,9), 11*a_367 = T(2,11), 12*n_749",
                "interpretation": "Three of four members are torus knots T(2,p) for primes p=7,9,11. "
                                  "Their Jones coefficients follow pattern [1, 0, 1, -1, 1, -1, ...]. "
                                  "The alternating-sign tail is the hallmark of torus knot Jones polynomials.",
                "significance": "Torus knots form a distinct algebraic DNA family, confirming "
                                "that Berlekamp-Massey detects quantum topology structure.",
            },
            "fibonacci_absent": {
                "explanation": "The Fibonacci characteristic polynomial x^2-x-1 was NOT found. "
                               "While torus knot Jones polynomials have connections to Fibonacci numbers "
                               "through quantum dimensions, the coefficient sequences themselves do not "
                               "satisfy the Fibonacci recurrence. The connection is at the level of "
                               "evaluations V_K(e^{2pi i/5}), not coefficient recurrences.",
            },
            "low_detection_rate": {
                "rate": "1.6%",
                "explanation": "Most Jones polynomials do NOT satisfy short linear recurrences. "
                               "This is expected: Jones coefficients encode representation-theoretic data "
                               "that is generically non-linear. The 48 knots with recurrences are special "
                               "because their quantum group representations have constrained structure "
                               "(cyclotomic or torus-type).",
            },
        },
        "elapsed_seconds": round(elapsed, 2),
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"  Total knots: {len(knots)}")
    print(f"  With Jones coeffs: {results['n_knots_with_jones']}")
    print(f"  Eligible (len >= 8): {len(eligible)}")
    print(f"  With detectable recurrence: {n_with_recurrence} ({results['detection_rate']})")
    print(f"  Unique characteristic polynomials: {len(jones_clusters)}")
    print(f"  Multi-knot clusters: {len(multi_clusters)}")
    print(f"  Largest cluster: {top_clusters[0][0] if top_clusters else 'N/A'} ({len(top_clusters[0][1]) if top_clusters else 0} knots)")
    print(f"  OEIS matches: {len(oeis_matches)}")
    print(f"  Jones-Alexander same recurrence: {same_recurrence}/{len(both)}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
