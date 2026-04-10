"""
GSp_4 Berlekamp-Massey — Linear Recurrence Discovery in Congruence Quotients
=============================================================================
For each of 37 mod-3 congruence pairs of genus-2 curves, compute:
    d_a(p) = (a_p(C1) - a_p(C2)) / 3
    d_b(p) = (b_p(C1) - b_p(C2)) / 3
indexed by good primes p, then apply Berlekamp-Massey to find minimal
linear recurrences. Cluster pairs by shared characteristic polynomial.

Usage:
    python gsp4_berlekamp_massey.py
"""

import re
import json
import time
from collections import defaultdict, Counter
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= abs(n):
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if abs(n) > 1:
        factors.add(abs(n))
    return factors


def parse_good_lfactors(s):
    """Parse good_lfactors field: [[p, a_p, b_p], ...]"""
    result = {}
    matches = re.findall(r'\[(-?\d+),(-?\d+),(-?\d+)\]', s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


def load_genus2_curves(filepath):
    """Load genus-2 curves from LMFDB raw dump."""
    curves = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            if len(parts) < 17:
                continue

            conductor = int(parts[1])
            disc = int(parts[0])
            st_group = parts[8]
            euler = parse_good_lfactors(parts[16] if len(parts) > 16 else "")
            if not euler:
                continue

            eqn = parts[3]
            curves.append({
                "conductor": conductor,
                "disc": disc,
                "st_group": st_group,
                "eqn": eqn,
                "euler": euler,
                "n_primes": len(euler),
            })
    return curves


# ─────────────────────────────────────────────────────────────────────────────
# Berlekamp-Massey Algorithm
# ─────────────────────────────────────────────────────────────────────────────

def berlekamp_massey_rational(seq, max_order=8):
    """
    Berlekamp-Massey over Q (integers). Find minimal linear recurrence
    c[0]*s[n] + c[1]*s[n-1] + ... + c[L]*s[n-L] = 0
    where c[0] = 1 (monic).

    Returns (order, coefficients) where coefficients = [c_1, ..., c_L]
    such that s[n] = c_1*s[n-1] + c_2*s[n-2] + ... + c_L*s[n-L]

    Uses the standard BM approach adapted for rationals:
    Try each order L from 1..max_order, solve the Toeplitz system,
    verify on remaining data.
    """
    n = len(seq)
    if n < 3:
        return None

    for L in range(1, min(max_order + 1, n // 2)):
        # Build system: for i = L, L+1, ..., 2L-1 (need L equations)
        # s[i] = c_1*s[i-1] + c_2*s[i-2] + ... + c_L*s[i-L]
        if 2 * L > n:
            break

        # Build matrix A and vector b
        A = []
        b = []
        for i in range(L, 2 * L):
            row = [seq[i - j - 1] for j in range(L)]
            A.append(row)
            b.append(seq[i])

        # Solve via Gaussian elimination with exact rational arithmetic
        # Use fractions to keep exact
        coeffs = solve_exact(A, b, L)
        if coeffs is None:
            continue

        # Verify on ALL remaining data points
        valid = True
        max_err = 0
        for i in range(L, n):
            predicted = sum(coeffs[j] * seq[i - j - 1] for j in range(L))
            err = abs(seq[i] - predicted)
            max_err = max(max_err, err)
            if err > 1e-10:  # Allow tiny floating point errors
                valid = False
                break

        if valid:
            # Check coefficients are rational (integer or simple fraction)
            int_coeffs = []
            all_int = True
            for c in coeffs:
                if isinstance(c, float):
                    if abs(c - round(c)) < 1e-9:
                        int_coeffs.append(round(c))
                    else:
                        all_int = False
                        int_coeffs.append(c)
                else:
                    int_coeffs.append(c)

            return {
                "order": L,
                "coefficients": int_coeffs,
                "all_integer": all_int,
                "verified_length": n,
                "max_residual": max_err,
            }

    return None


def berlekamp_massey_gf(seq, p, max_order=8):
    """
    Classic Berlekamp-Massey over GF(p).
    Returns minimal LFSR (linear recurrence) or None if order > max_order.

    The algorithm maintains connection polynomial C(x) such that
    C produces all observed bits.
    """
    n = len(seq)
    if n < 3:
        return None

    # Work in GF(p)
    s = [x % p for x in seq]

    # Standard BM algorithm
    C = [1]  # Current connection polynomial
    B = [1]  # Previous connection polynomial
    L = 0    # Current LFSR length
    m = 1    # Shift counter
    b_val = 1  # Previous discrepancy

    for i in range(n):
        # Compute discrepancy
        d = s[i]
        for j in range(1, len(C)):
            if i - j >= 0:
                d = (d + C[j] * s[i - j]) % p

        if d == 0:
            m += 1
        elif 2 * L <= i:
            # Need to update
            T = list(C)
            # C(x) = C(x) - (d/b) * x^m * B(x)
            db_inv = (d * pow(b_val, p - 2, p)) % p
            # Pad C if needed
            needed = m + len(B)
            while len(C) < needed:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - db_inv * B[j]) % p

            L = i + 1 - L
            B = T
            b_val = d
            m = 1

            if L > max_order:
                return None
        else:
            # Just update C
            db_inv = (d * pow(b_val, p - 2, p)) % p
            needed = m + len(B)
            while len(C) < needed:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - db_inv * B[j]) % p
            m += 1

    if L == 0 or L > max_order:
        return None

    # Verify: the LFSR of length L with connection poly C should
    # predict all elements from index L onward
    for i in range(L, n):
        val = 0
        for j in range(1, len(C)):
            if i - j >= 0:
                val = (val + C[j] * s[i - j]) % p
        predicted = (p - val) % p
        if predicted != s[i]:
            return None

    # Convert connection poly to recurrence coefficients
    # C[0]=1, C[1], ..., C[L] means s[n] = -C[1]*s[n-1] - ... - C[L]*s[n-L] mod p
    rec_coeffs = [(p - C[j]) % p for j in range(1, L + 1)]

    return {
        "order": L,
        "coefficients": rec_coeffs,
        "char_poly": [1] + [C[j] for j in range(1, L + 1)],
        "modulus": p,
        "verified_length": n,
    }


def solve_exact(A, b, n):
    """Solve n x n system Ax = b using Gaussian elimination with fractions."""
    from fractions import Fraction

    # Convert to fractions
    M = [[Fraction(A[i][j]) for j in range(n)] for i in range(n)]
    rhs = [Fraction(b[i]) for i in range(n)]

    # Forward elimination
    for col in range(n):
        # Find pivot
        pivot = None
        for row in range(col, n):
            if M[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return None  # Singular

        # Swap
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            rhs[col], rhs[pivot] = rhs[pivot], rhs[col]

        # Eliminate
        for row in range(col + 1, n):
            if M[row][col] != 0:
                factor = M[row][col] / M[col][col]
                for j in range(col, n):
                    M[row][j] -= factor * M[col][j]
                rhs[row] -= factor * rhs[col]

    # Back substitution
    x = [Fraction(0)] * n
    for i in range(n - 1, -1, -1):
        if M[i][i] == 0:
            return None
        s = rhs[i]
        for j in range(i + 1, n):
            s -= M[i][j] * x[j]
        x[i] = s / M[i][i]

    # Convert back: try to keep as integers or floats
    result = []
    for xi in x:
        if xi.denominator == 1:
            result.append(int(xi))
        else:
            result.append(float(xi))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Characteristic polynomial analysis
# ─────────────────────────────────────────────────────────────────────────────

def char_poly_from_recurrence(coeffs):
    """
    Given recurrence s[n] = c_1*s[n-1] + ... + c_L*s[n-L],
    characteristic polynomial is x^L - c_1*x^{L-1} - ... - c_L.
    Returns as list [1, -c_1, -c_2, ..., -c_L] (coefficient of x^L first).
    """
    L = len(coeffs)
    poly = [1] + [-c for c in coeffs]
    return poly


def check_euler_factor_form(char_poly, primes_used):
    """
    Check if characteristic polynomial matches known Euler factor forms.
    Returns description of match or None.
    """
    L = len(char_poly) - 1  # degree

    if L == 2:
        # x^2 + a*x + b
        # EC Euler factor: x^2 - a_p*x + p  (for a specific p)
        # But our recurrence is over the sequence indexed by primes,
        # so the char poly is a property of the sequence, not a single Euler factor
        a, b = -char_poly[1], -char_poly[2]
        return {
            "degree": 2,
            "trace": a,
            "det": -b,
            "form": f"x^2 - ({a})*x + ({-b})",
        }

    elif L == 4:
        # Check genus-2 Euler factor form: x^4 - a*x^3 + b*x^2 - a*p*x + p^2
        # As a recurrence this would mean specific symmetry
        a1 = -char_poly[1]
        a2 = -char_poly[2]
        a3 = -char_poly[3]
        a4 = -char_poly[4]

        # Check functional equation symmetry: a3 = a1 * a4 / a4_sqrt?
        # Actually x^4 + c1*x^3 + c2*x^2 + c3*x + c4
        # genus-2 form requires c3 = c1 * sqrt(c4) and c4 = p^2
        # Let's just report the coefficients
        return {
            "degree": 4,
            "coefficients": [a1, a2, a3, a4],
            "form": f"x^4 - ({a1})*x^3 + ({a2})*x^2 - ({a3})*x + ({a4})",
        }

    return {"degree": L, "form": f"degree-{L} polynomial"}


def describe_char_poly(char_poly):
    """Return a hashable string description of the characteristic polynomial."""
    return str(char_poly)


# ─────────────────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    script_dir = Path(__file__).parent

    # Load raw LMFDB data
    data_path = script_dir.parent.parent.parent / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
    if not data_path.exists():
        print(f"ERROR: Data file not found: {data_path}")
        return

    print("Loading genus-2 curves...")
    curves = load_genus2_curves(str(data_path))
    print(f"  Loaded {len(curves)} curves in {time.time()-t0:.1f}s")

    # The 37 irreducible mod-3 conductors
    irred_conds = [
        1844, 2348, 3572, 4304, 5497, 7945, 9664, 14155, 19201, 20432,
        20560, 21611, 31312, 32119, 32575, 36265, 43276, 50173, 50608,
        69422, 77608, 83776, 88765, 96347, 114437, 124712, 141538, 142265,
        155305, 173936, 195337, 216677, 232912, 235237, 342871, 600953, 745517,
    ]

    by_cond = defaultdict(list)
    for c in curves:
        by_cond[c["conductor"]].append(c)

    # ─── Recover the 37 pairs ───
    print("\nRecovering 37 mod-3 congruence pairs...")
    pairs = []
    for cond in irred_conds:
        cond_curves = [c for c in by_cond[cond] if c["st_group"] == "USp(4)"]
        if cond % 3 == 0:
            continue

        # Dedup by Euler fingerprint (isogeny classes)
        classes = defaultdict(list)
        for c in cond_curves:
            primes_avail = sorted(c["euler"].keys())
            fp = tuple(c["euler"][p] for p in primes_avail[:20])
            classes[fp].append(c)

        class_list = list(classes.values())
        if len(class_list) < 2:
            continue

        # Find the mod-3 congruent pair
        found = False
        for i in range(len(class_list)):
            if found:
                break
            for j in range(i + 1, len(class_list)):
                c1 = class_list[i][0]
                c2 = class_list[j][0]
                bad = prime_factors(cond)
                common = sorted(set(c1["euler"].keys()) & set(c2["euler"].keys()))
                good = [p for p in common if p not in bad and p != 3]

                all_cong = True
                has_nz = False
                for p in good:
                    da = c1["euler"][p][0] - c2["euler"][p][0]
                    db = c1["euler"][p][1] - c2["euler"][p][1]
                    if da % 3 != 0 or db % 3 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True

                if all_cong and has_nz:
                    pairs.append({
                        "conductor": cond,
                        "c1_eqn": c1["eqn"],
                        "c2_eqn": c2["eqn"],
                        "c1_euler": c1["euler"],
                        "c2_euler": c2["euler"],
                        "good_primes": good,
                    })
                    found = True
                    break

    print(f"  Recovered {len(pairs)} pairs")

    # ─── Compute difference sequences ───
    print("\nComputing difference sequences d_a(p) and d_b(p)...")
    for pair in pairs:
        good = pair["good_primes"]
        d_a = []
        d_b = []
        primes_used = []
        for p in good:
            a1, b1 = pair["c1_euler"][p]
            a2, b2 = pair["c2_euler"][p]
            da = (a1 - a2) // 3
            db = (b1 - b2) // 3
            d_a.append(da)
            d_b.append(db)
            primes_used.append(p)
        pair["d_a"] = d_a
        pair["d_b"] = d_b
        pair["primes_used"] = primes_used

    # ─── Berlekamp-Massey on each sequence ───
    print("\nRunning Berlekamp-Massey (max order 8)...")
    print("=" * 72)

    bm_results = []
    for idx, pair in enumerate(pairs):
        cond = pair["conductor"]
        n_primes = len(pair["primes_used"])

        # Run BM on d_a sequence
        bm_a = berlekamp_massey_rational(pair["d_a"], max_order=8)
        # Run BM on d_b sequence
        bm_b = berlekamp_massey_rational(pair["d_b"], max_order=8)

        result = {
            "conductor": cond,
            "c1_eqn": pair["c1_eqn"],
            "c2_eqn": pair["c2_eqn"],
            "n_good_primes": n_primes,
            "d_a_sample": pair["d_a"][:15],
            "d_b_sample": pair["d_b"][:15],
            "bm_d_a": None,
            "bm_d_b": None,
        }

        tag_a = "NO RECURRENCE"
        tag_b = "NO RECURRENCE"

        if bm_a is not None:
            cp_a = char_poly_from_recurrence(bm_a["coefficients"])
            ef_a = check_euler_factor_form(cp_a, pair["primes_used"])
            bm_a["char_poly"] = cp_a
            bm_a["euler_form"] = ef_a
            result["bm_d_a"] = bm_a
            tag_a = f"order {bm_a['order']}, char_poly={cp_a}"

        if bm_b is not None:
            cp_b = char_poly_from_recurrence(bm_b["coefficients"])
            ef_b = check_euler_factor_form(cp_b, pair["primes_used"])
            bm_b["char_poly"] = cp_b
            bm_b["euler_form"] = ef_b
            result["bm_d_b"] = bm_b
            tag_b = f"order {bm_b['order']}, char_poly={cp_b}"

        bm_results.append(result)

        # Print summary
        print(f"\nPair {idx+1:2d} | N={cond:>7d} | {n_primes} primes")
        print(f"  d_a: {tag_a}")
        print(f"  d_b: {tag_b}")
        if pair["d_a"][:8]:
            print(f"  d_a[:8] = {pair['d_a'][:8]}")
        if pair["d_b"][:8]:
            print(f"  d_b[:8] = {pair['d_b'][:8]}")

    # ─── Clustering by characteristic polynomial ───
    print("\n" + "=" * 72)
    print("CLUSTERING BY CHARACTERISTIC POLYNOMIAL")
    print("=" * 72)

    # Cluster d_a recurrences
    clusters_a = defaultdict(list)
    no_recurrence_a = []
    for r in bm_results:
        if r["bm_d_a"] is not None:
            key = str(r["bm_d_a"]["char_poly"])
            clusters_a[key].append(r["conductor"])
        else:
            no_recurrence_a.append(r["conductor"])

    # Cluster d_b recurrences
    clusters_b = defaultdict(list)
    no_recurrence_b = []
    for r in bm_results:
        if r["bm_d_b"] is not None:
            key = str(r["bm_d_b"]["char_poly"])
            clusters_b[key].append(r["conductor"])
        else:
            no_recurrence_b.append(r["conductor"])

    print(f"\n--- d_a clusters ---")
    print(f"  Pairs with recurrence: {len(bm_results) - len(no_recurrence_a)}")
    print(f"  Pairs without recurrence: {len(no_recurrence_a)}")
    for poly, conds in sorted(clusters_a.items(), key=lambda x: -len(x[1])):
        print(f"  char_poly = {poly}: {len(conds)} pairs — N = {conds}")

    print(f"\n--- d_b clusters ---")
    print(f"  Pairs with recurrence: {len(bm_results) - len(no_recurrence_b)}")
    print(f"  Pairs without recurrence: {len(no_recurrence_b)}")
    for poly, conds in sorted(clusters_b.items(), key=lambda x: -len(x[1])):
        print(f"  char_poly = {poly}: {len(conds)} pairs — N = {conds}")

    # ─── Check for Euler factor forms ───
    print("\n" + "=" * 72)
    print("EULER FACTOR FORM CHECK")
    print("=" * 72)
    for r in bm_results:
        if r["bm_d_a"] is not None and r["bm_d_a"]["order"] in (2, 3, 4):
            ef = r["bm_d_a"]["euler_form"]
            print(f"\n  N={r['conductor']}: d_a recurrence order {r['bm_d_a']['order']}")
            print(f"    {ef['form']}")
            if ef["degree"] == 2:
                print(f"    EC-like? trace={ef['trace']}, det={ef['det']}")
        if r["bm_d_b"] is not None and r["bm_d_b"]["order"] in (2, 3, 4):
            ef = r["bm_d_b"]["euler_form"]
            print(f"\n  N={r['conductor']}: d_b recurrence order {r['bm_d_b']['order']}")
            print(f"    {ef['form']}")

    # ─── Combined analysis: pairs where BOTH d_a and d_b have recurrences ───
    print("\n" + "=" * 72)
    print("PAIRS WITH RECURRENCES IN BOTH d_a AND d_b")
    print("=" * 72)
    both_count = 0
    for r in bm_results:
        if r["bm_d_a"] is not None and r["bm_d_b"] is not None:
            both_count += 1
            print(f"\n  N={r['conductor']}:")
            print(f"    d_a: order {r['bm_d_a']['order']}, "
                  f"char_poly = {r['bm_d_a']['char_poly']}")
            print(f"    d_b: order {r['bm_d_b']['order']}, "
                  f"char_poly = {r['bm_d_b']['char_poly']}")
    if both_count == 0:
        print("  None found.")
    print(f"\n  Total: {both_count} / {len(bm_results)} pairs")

    # ─── BM over finite fields (mod q) ───
    print("\n" + "=" * 72)
    print("BERLEKAMP-MASSEY OVER FINITE FIELDS (mod q)")
    print("=" * 72)
    print("Reducing d_a and d_b mod q, then running BM over GF(q).")
    print("This is the natural setting for BM and may reveal hidden structure.")

    modular_results = {}
    for q in [2, 5, 7, 11, 13]:
        print(f"\n--- mod {q} ---")
        n_a_found = 0
        n_b_found = 0
        mod_clusters_a = defaultdict(list)
        mod_clusters_b = defaultdict(list)

        for idx, pair in enumerate(pairs):
            d_a_mod = [x % q for x in pair["d_a"]]
            d_b_mod = [x % q for x in pair["d_b"]]

            bm_a_q = berlekamp_massey_gf(d_a_mod, q, max_order=8)
            bm_b_q = berlekamp_massey_gf(d_b_mod, q, max_order=8)

            if bm_a_q is not None:
                n_a_found += 1
                key = str(bm_a_q["char_poly"])
                mod_clusters_a[key].append(pair["conductor"])
            if bm_b_q is not None:
                n_b_found += 1
                key = str(bm_b_q["char_poly"])
                mod_clusters_b[key].append(pair["conductor"])

        print(f"  d_a recurrences: {n_a_found}/37")
        print(f"  d_b recurrences: {n_b_found}/37")
        if mod_clusters_a:
            print(f"  d_a clusters ({len(mod_clusters_a)} distinct):")
            for poly, conds in sorted(mod_clusters_a.items(), key=lambda x: -len(x[1])):
                print(f"    {poly}: {len(conds)} pairs")
        if mod_clusters_b:
            print(f"  d_b clusters ({len(mod_clusters_b)} distinct):")
            for poly, conds in sorted(mod_clusters_b.items(), key=lambda x: -len(x[1])):
                print(f"    {poly}: {len(conds)} pairs")

        modular_results[q] = {
            "n_a_recurrences": n_a_found,
            "n_b_recurrences": n_b_found,
            "d_a_clusters": {k: v for k, v in mod_clusters_a.items()},
            "d_b_clusters": {k: v for k, v in mod_clusters_b.items()},
        }

    # ─── Statistics ───
    print("\n" + "=" * 72)
    print("SUMMARY STATISTICS")
    print("=" * 72)

    n_total = len(bm_results)
    n_a_rec = sum(1 for r in bm_results if r["bm_d_a"] is not None)
    n_b_rec = sum(1 for r in bm_results if r["bm_d_b"] is not None)
    n_both = sum(1 for r in bm_results
                 if r["bm_d_a"] is not None and r["bm_d_b"] is not None)

    # Order distribution
    orders_a = Counter(r["bm_d_a"]["order"] for r in bm_results if r["bm_d_a"])
    orders_b = Counter(r["bm_d_b"]["order"] for r in bm_results if r["bm_d_b"])

    print(f"  Total pairs analyzed: {n_total}")
    print(f"  d_a recurrences found: {n_a_rec} ({100*n_a_rec/max(n_total,1):.0f}%)")
    print(f"  d_b recurrences found: {n_b_rec} ({100*n_b_rec/max(n_total,1):.0f}%)")
    print(f"  Both: {n_both}")
    print(f"  d_a order distribution: {dict(orders_a)}")
    print(f"  d_b order distribution: {dict(orders_b)}")
    print(f"  Distinct d_a char polys: {len(clusters_a)}")
    print(f"  Distinct d_b char polys: {len(clusters_b)}")

    # Check for all-zero sequences (trivial — isomorphic L-functions)
    n_zero_a = sum(1 for p in pairs if all(x == 0 for x in p["d_a"]))
    n_zero_b = sum(1 for p in pairs if all(x == 0 for x in p["d_b"]))
    print(f"  All-zero d_a sequences: {n_zero_a}")
    print(f"  All-zero d_b sequences: {n_zero_b}")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")

    # ─── Save results ───
    out_path = script_dir / "gsp4_bm_results.json"

    # Make results JSON-serializable
    save_results = {
        "description": "Berlekamp-Massey analysis of mod-3 GSp_4 congruence quotients",
        "n_pairs": n_total,
        "n_d_a_recurrences": n_a_rec,
        "n_d_b_recurrences": n_b_rec,
        "n_both_recurrences": n_both,
        "d_a_order_distribution": dict(orders_a),
        "d_b_order_distribution": dict(orders_b),
        "d_a_clusters": {k: v for k, v in clusters_a.items()},
        "d_b_clusters": {k: v for k, v in clusters_b.items()},
        "no_recurrence_d_a": no_recurrence_a,
        "no_recurrence_d_b": no_recurrence_b,
        "modular_bm": {str(k): v for k, v in modular_results.items()},
        "pairs": [],
    }

    for r in bm_results:
        entry = {
            "conductor": r["conductor"],
            "c1_eqn": r["c1_eqn"],
            "c2_eqn": r["c2_eqn"],
            "n_good_primes": r["n_good_primes"],
            "d_a_sample": r["d_a_sample"],
            "d_b_sample": r["d_b_sample"],
        }
        if r["bm_d_a"]:
            entry["bm_d_a"] = {
                "order": r["bm_d_a"]["order"],
                "coefficients": r["bm_d_a"]["coefficients"],
                "char_poly": r["bm_d_a"]["char_poly"],
                "all_integer": r["bm_d_a"]["all_integer"],
                "euler_form": r["bm_d_a"].get("euler_form"),
            }
        if r["bm_d_b"]:
            entry["bm_d_b"] = {
                "order": r["bm_d_b"]["order"],
                "coefficients": r["bm_d_b"]["coefficients"],
                "char_poly": r["bm_d_b"]["char_poly"],
                "all_integer": r["bm_d_b"]["all_integer"],
                "euler_form": r["bm_d_b"].get("euler_form"),
            }
        save_results["pairs"].append(entry)

    with open(out_path, 'w') as f:
        json.dump(save_results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
