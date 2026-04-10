"""
Recurrence Stability Under Prime Reduction (M10)
=================================================
Metrology challenge: If an OEIS sequence satisfies a linear recurrence over Z,
does it still satisfy that recurrence over F_p?

Pipeline:
1. Load 1000+ OEIS sequences with verified BM recurrences (from S33 cache).
2. For each: reduce coefficients and terms mod p, check if recurrence holds.
3. Test at p = 2, 3, 5, 7, 11, 13.
4. Compute stability spectrum (how many primes stable).
5. Cross-reference with C08 cluster families.
6. Identify which primes cause instability and why.

Key insight: A recurrence a(n) = sum c_i * a(n-i) over Z is p-stable iff
reducing mod p gives a valid recurrence in F_p. Non-integer coefficients
(truly rational) are definitionally unstable at primes dividing denominator.

Usage:
    python recurrence_stability.py
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
S33_FILE = ROOT / "cartography" / "convergence" / "data" / "recursion_operator_signatures.jsonl"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
C08_RESULTS = Path(__file__).resolve().parent / "recurrence_euler_factor_results.json"
OUT_FILE = Path(__file__).resolve().parent / "recurrence_stability_results.json"

PRIMES = [2, 3, 5, 7, 11, 13]

# ---------------------------------------------------------------------------
# Load S33 recurrences
# ---------------------------------------------------------------------------

def load_s33_recurrences(max_seqs=None):
    """Load BM-extracted recurrences from S33 cache."""
    results = {}
    if not S33_FILE.exists():
        print(f"  ERROR: S33 file not found at {S33_FILE}")
        return results
    with open(S33_FILE, "r") as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("is_linear_recurrence") and obj.get("characteristic_coeffs"):
                deg = obj["recurrence_degree"]
                coeffs = obj["characteristic_coeffs"]
                if deg >= 1 and len(coeffs) == deg:
                    results[obj["seq_id"]] = {
                        "degree": deg,
                        "coeffs": coeffs,  # floats from BM
                    }
            if max_seqs and len(results) >= max_seqs:
                break
    return results


# ---------------------------------------------------------------------------
# Load OEIS sequence terms
# ---------------------------------------------------------------------------

def load_oeis_terms(seq_ids):
    """Load raw integer terms from stripped_new.txt for given sequence IDs."""
    needed = set(seq_ids)
    terms = {}
    with open(OEIS_STRIPPED, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: A000001 ,1,2,3,...
            space_idx = line.find(" ")
            if space_idx < 0:
                continue
            sid = line[:space_idx].strip()
            if sid not in needed:
                continue
            rest = line[space_idx:].strip().strip(",")
            try:
                vals = [int(t) for t in rest.split(",") if t.strip()]
            except ValueError:
                continue
            if vals:
                terms[sid] = vals
    return terms


# ---------------------------------------------------------------------------
# Coefficient integrality check
# ---------------------------------------------------------------------------

def classify_coefficient(c_float):
    """Classify a BM coefficient as integer or rational.

    Returns (int_value, is_integer, denominator_if_rational).
    We round to nearest integer. If the float is more than 0.01 away
    from the nearest integer, it's truly rational.
    """
    rounded = round(c_float)
    residual = abs(c_float - rounded)
    if residual < 0.01:
        return rounded, True, 1
    else:
        # Try to find a small-denominator rational approximation
        frac = Fraction(c_float).limit_denominator(1000)
        return None, False, frac.denominator


def integralize_coefficients(coeffs_float):
    """Round BM coefficients to integers.

    Returns (int_coeffs, is_all_integer, problematic_denominators).
    """
    int_coeffs = []
    all_integer = True
    denominators = []
    for c in coeffs_float:
        rounded, is_int, denom = classify_coefficient(c)
        if is_int:
            int_coeffs.append(rounded)
        else:
            all_integer = False
            denominators.append(denom)
            # Still round for testing purposes
            int_coeffs.append(round(c))
    return int_coeffs, all_integer, denominators


# ---------------------------------------------------------------------------
# Mod-p recurrence verification
# ---------------------------------------------------------------------------

def verify_recurrence_mod_p(terms, coeffs_int, degree, p):
    """Check if reduced recurrence holds in F_p.

    Recurrence: a(n) = -c_1*a(n-1) - c_2*a(n-2) - ... - c_k*a(n-k)
    (BM convention: characteristic polynomial x^k + c_1*x^{k-1} + ... + c_k)

    So predicted = -sum(coeffs[j] * terms[i-j-1]) for j in 0..degree-1.

    Returns (n_checks, n_mismatches).
    """
    n = len(terms)
    if degree >= n:
        return 0, 0

    # Reduce coefficients mod p
    coeffs_mod = [c % p for c in coeffs_int]
    terms_mod = [t % p for t in terms]

    n_checks = 0
    n_mismatches = 0

    # Check from position degree to end
    check_end = min(n, degree + max(50, n))  # check all available terms
    for i in range(degree, check_end):
        predicted = 0
        for j in range(degree):
            predicted += (-coeffs_mod[j]) * terms_mod[i - j - 1]
        predicted = predicted % p
        actual = terms_mod[i]
        n_checks += 1
        if predicted != actual:
            n_mismatches += 1

    return n_checks, n_mismatches


def verify_recurrence_over_Z(terms, coeffs_int, degree):
    """Quick check that the integer recurrence actually works over Z.

    Returns True if it works for at least 80% of checkable positions.
    """
    n = len(terms)
    if degree >= n:
        return False

    n_checks = 0
    n_ok = 0
    check_end = min(n, degree + max(30, n))
    for i in range(degree, check_end):
        predicted = 0
        for j in range(degree):
            predicted += (-coeffs_int[j]) * terms[i - j - 1]
        if predicted == terms[i]:
            n_ok += 1
        n_checks += 1

    if n_checks == 0:
        return False
    return n_ok / n_checks >= 0.95


# ---------------------------------------------------------------------------
# Load C08 clusters for cross-referencing
# ---------------------------------------------------------------------------

def load_c08_clusters():
    """Load polynomial clusters from C08 results.

    Returns:
        seq_to_cluster: {seq_id: cluster_index}
        clusters: list of cluster dicts
    """
    seq_to_cluster = {}
    clusters = []
    if not C08_RESULTS.exists():
        return seq_to_cluster, clusters

    with open(C08_RESULTS) as f:
        data = json.load(f)

    if "polynomial_clusters" in data:
        clusters = data["polynomial_clusters"].get("top_clusters", [])
        for i, cl in enumerate(clusters):
            for sid in cl.get("sequences", []):
                seq_to_cluster[sid] = i

    return seq_to_cluster, clusters


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def char_poly_factors_mod_p(coeffs_int, p):
    """Check if the characteristic polynomial factors mod p.

    Characteristic poly: x^k + c_1*x^{k-1} + ... + c_k
    where coeffs_int = [c_1, c_2, ..., c_k] (BM convention).

    Returns: (has_root, roots_mod_p, disc_mod_p_zero)
    """
    deg = len(coeffs_int)
    if deg == 0:
        return False, [], False

    # Evaluate char poly at each x in F_p
    roots = []
    for x in range(p):
        val = pow(x, deg, p)
        for j, c in enumerate(coeffs_int):
            val = (val + (c % p) * pow(x, deg - 1 - j, p)) % p
        if val % p == 0:
            roots.append(x)

    return len(roots) > 0, roots, None


def berlekamp_massey_mod_p(seq_mod_p, p, max_deg=20):
    """Run Berlekamp-Massey over F_p to find minimal recurrence mod p.

    Returns (coeffs_mod_p, degree) or (None, 0) if no recurrence found.
    """
    n = len(seq_mod_p)
    if n == 0:
        return None, 0

    s = [x % p for x in seq_mod_p]

    # Extended GCD for modular inverse
    def modinv(a, m):
        if a == 0:
            return None
        g, x, _ = extended_gcd(a % m, m)
        if g != 1:
            return None
        return x % m

    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x

    b = [1]
    c = [1]
    l_deg = 0
    m = 1
    d = 1

    for i in range(n):
        disc = s[i]
        for j in range(1, l_deg + 1):
            if j < len(c):
                disc = (disc + c[j] * s[i - j]) % p

        if disc % p == 0:
            m += 1
        elif 2 * l_deg <= i:
            t = list(c)
            inv_d = modinv(d, p)
            if inv_d is None:
                return None, 0
            coef = ((-disc) * inv_d) % p
            while len(c) < len(b) + m:
                c.append(0)
            for j in range(len(b)):
                c[j + m] = (c[j + m] + coef * b[j]) % p
            l_deg = i + 1 - l_deg
            b = t
            d = disc
            m = 1
        else:
            inv_d = modinv(d, p)
            if inv_d is None:
                return None, 0
            coef = ((-disc) * inv_d) % p
            while len(c) < len(b) + m:
                c.append(0)
            for j in range(len(b)):
                c[j + m] = (c[j + m] + coef * b[j]) % p
            m += 1

        if l_deg > max_deg:
            return None, 0

    coeffs = [c[j] % p for j in range(1, l_deg + 1)]
    return coeffs, l_deg


def main():
    t0 = time.time()
    print("=" * 70)
    print("M10: Recurrence Stability Under Prime Reduction")
    print("=" * 70)

    # 1. Load recurrences
    print("\n[1] Loading S33 recurrences...")
    rec_data = load_s33_recurrences()
    print(f"    Loaded {len(rec_data)} recurrences")

    # Filter to degree 1-10 for tractability (higher degrees are rare and noisy)
    rec_data = {sid: r for sid, r in rec_data.items() if 1 <= r["degree"] <= 10}
    print(f"    After degree filter (1-10): {len(rec_data)}")

    # 2. Load OEIS terms
    print("\n[2] Loading OEIS terms...")
    terms_data = load_oeis_terms(list(rec_data.keys()))
    print(f"    Loaded terms for {len(terms_data)} sequences")

    # 3. Integralize coefficients and verify over Z
    print("\n[3] Integralizing coefficients and verifying over Z...")
    valid_sequences = {}
    non_integer_count = 0
    z_fail_count = 0

    for sid, rec in rec_data.items():
        if sid not in terms_data:
            continue
        terms = terms_data[sid]
        int_coeffs, all_integer, denoms = integralize_coefficients(rec["coeffs"])

        if not all_integer:
            non_integer_count += 1

        # Verify the integer recurrence works over Z
        if not verify_recurrence_over_Z(terms, int_coeffs, rec["degree"]):
            z_fail_count += 1
            continue

        valid_sequences[sid] = {
            "degree": rec["degree"],
            "coeffs_float": rec["coeffs"],
            "coeffs_int": int_coeffs,
            "all_integer": all_integer,
            "problematic_denoms": denoms if not all_integer else [],
            "n_terms": len(terms),
        }

    print(f"    Non-integer coefficients: {non_integer_count}")
    print(f"    Failed Z-verification: {z_fail_count}")
    print(f"    Valid sequences for stability testing: {len(valid_sequences)}")

    # Cap at 2000 for reasonable runtime (take all if fewer)
    if len(valid_sequences) > 2000:
        # Prioritize: take a diverse sample across degrees
        by_degree = defaultdict(list)
        for sid, v in valid_sequences.items():
            by_degree[v["degree"]].append(sid)
        selected = set()
        # Round-robin across degrees
        while len(selected) < 2000:
            added = False
            for deg in sorted(by_degree.keys()):
                if by_degree[deg] and len(selected) < 2000:
                    selected.add(by_degree[deg].pop(0))
                    added = True
            if not added:
                break
        valid_sequences = {sid: valid_sequences[sid] for sid in selected}
        print(f"    Sampled to {len(valid_sequences)} sequences")

    # 4. Test stability at each prime
    print(f"\n[4] Testing stability at primes {PRIMES}...")

    stability_results = {}

    for sid, info in valid_sequences.items():
        terms = terms_data[sid]
        deg = info["degree"]
        int_coeffs = info["coeffs_int"]

        prime_results = {}
        stable_count = 0

        for p in PRIMES:
            n_checks, n_mismatches = verify_recurrence_mod_p(terms, int_coeffs, deg, p)
            is_stable = (n_mismatches == 0) and (n_checks > 0)
            prime_results[str(p)] = {
                "stable": is_stable,
                "checks": n_checks,
                "mismatches": n_mismatches,
            }
            if is_stable:
                stable_count += 1

        # Check for denominator-induced instability
        denom_unstable_primes = []
        if not info["all_integer"]:
            for d in info["problematic_denoms"]:
                for p in PRIMES:
                    if d % p == 0:
                        denom_unstable_primes.append(p)

        stability_results[sid] = {
            "degree": deg,
            "coeffs_int": int_coeffs,
            "all_integer": info["all_integer"],
            "prime_results": prime_results,
            "n_stable": stable_count,
            "n_primes_tested": len(PRIMES),
            "stability_spectrum": stable_count,  # 0-6
            "denom_unstable_primes": sorted(set(denom_unstable_primes)),
        }

    print(f"    Tested {len(stability_results)} sequences")

    # 5. Compute stability spectrum distribution
    print("\n[5] Computing stability spectrum...")
    spectrum_dist = Counter()
    for sid, sr in stability_results.items():
        spectrum_dist[sr["stability_spectrum"]] += 1

    print(f"    Spectrum distribution (n_stable_primes: count):")
    for k in sorted(spectrum_dist.keys()):
        pct = 100.0 * spectrum_dist[k] / len(stability_results)
        bar = "#" * int(pct / 2)
        print(f"      {k}/6: {spectrum_dist[k]:5d} ({pct:5.1f}%) {bar}")

    # 6. Per-prime instability rates
    print("\n[6] Per-prime instability rates:")
    prime_instability = {}
    for p in PRIMES:
        unstable_at_p = sum(
            1 for sr in stability_results.values()
            if not sr["prime_results"][str(p)]["stable"]
        )
        rate = unstable_at_p / len(stability_results) if stability_results else 0
        prime_instability[str(p)] = {
            "unstable_count": unstable_at_p,
            "total": len(stability_results),
            "rate": round(rate, 4),
        }
        print(f"    p={p:2d}: {unstable_at_p:5d}/{len(stability_results)} unstable ({100*rate:.1f}%)")

    # 7. Stability vs degree
    print("\n[7] Stability vs recurrence degree:")
    degree_stability = defaultdict(lambda: {"total": 0, "spectrum_sum": 0, "fully_stable": 0})
    for sid, sr in stability_results.items():
        deg = sr["degree"]
        degree_stability[deg]["total"] += 1
        degree_stability[deg]["spectrum_sum"] += sr["stability_spectrum"]
        if sr["stability_spectrum"] == 6:
            degree_stability[deg]["fully_stable"] += 1

    degree_stats = {}
    for deg in sorted(degree_stability.keys()):
        ds = degree_stability[deg]
        avg = ds["spectrum_sum"] / ds["total"] if ds["total"] > 0 else 0
        fs_rate = ds["fully_stable"] / ds["total"] if ds["total"] > 0 else 0
        degree_stats[str(deg)] = {
            "total": ds["total"],
            "avg_spectrum": round(avg, 2),
            "fully_stable_rate": round(fs_rate, 4),
            "fully_stable_count": ds["fully_stable"],
        }
        print(f"    deg {deg}: n={ds['total']:4d}, avg_spectrum={avg:.2f}, fully_stable={100*fs_rate:.1f}%")

    # 8. Cross-reference with C08 clusters
    print("\n[8] Cross-referencing with C08 polynomial clusters...")
    seq_to_cluster, clusters = load_c08_clusters()

    cluster_stability = defaultdict(lambda: {"total": 0, "spectrum_sum": 0, "fully_stable": 0})
    in_cluster_count = 0
    out_cluster_count = 0
    in_cluster_spectra = []
    out_cluster_spectra = []

    for sid, sr in stability_results.items():
        if sid in seq_to_cluster:
            ci = seq_to_cluster[sid]
            cluster_stability[ci]["total"] += 1
            cluster_stability[ci]["spectrum_sum"] += sr["stability_spectrum"]
            if sr["stability_spectrum"] == 6:
                cluster_stability[ci]["fully_stable"] += 1
            in_cluster_count += 1
            in_cluster_spectra.append(sr["stability_spectrum"])
        else:
            out_cluster_count += 1
            out_cluster_spectra.append(sr["stability_spectrum"])

    print(f"    In C08 clusters: {in_cluster_count}")
    print(f"    Not in clusters: {out_cluster_count}")

    if in_cluster_spectra:
        avg_in = sum(in_cluster_spectra) / len(in_cluster_spectra)
        print(f"    Avg spectrum (in cluster): {avg_in:.2f}")
    if out_cluster_spectra:
        avg_out = sum(out_cluster_spectra) / len(out_cluster_spectra)
        print(f"    Avg spectrum (not in cluster): {avg_out:.2f}")

    # Per-cluster stability
    cluster_results = []
    for ci in sorted(cluster_stability.keys()):
        cs = cluster_stability[ci]
        if cs["total"] == 0:
            continue
        cl = clusters[ci] if ci < len(clusters) else {}
        avg = cs["spectrum_sum"] / cs["total"]
        cluster_results.append({
            "cluster_index": ci,
            "char_poly_coeffs": cl.get("char_poly_coeffs", []),
            "degree": cl.get("degree", 0),
            "cluster_size": cl.get("n_sequences", 0),
            "tested": cs["total"],
            "avg_spectrum": round(avg, 2),
            "fully_stable_count": cs["fully_stable"],
            "fully_stable_rate": round(cs["fully_stable"] / cs["total"], 4),
        })

    # Sort by avg spectrum
    cluster_results.sort(key=lambda x: x["avg_spectrum"])

    print("\n    Top unstable clusters (low avg spectrum):")
    for cr in cluster_results[:10]:
        print(f"      coeffs={cr['char_poly_coeffs']}, deg={cr['degree']}, "
              f"size={cr['cluster_size']}, avg_spec={cr['avg_spectrum']:.2f}, "
              f"fully_stable={cr['fully_stable_rate']*100:.0f}%")

    print("\n    Top stable clusters (high avg spectrum):")
    for cr in cluster_results[-10:]:
        print(f"      coeffs={cr['char_poly_coeffs']}, deg={cr['degree']}, "
              f"size={cr['cluster_size']}, avg_spec={cr['avg_spectrum']:.2f}, "
              f"fully_stable={cr['fully_stable_rate']*100:.0f}%")

    # 9. Stability vs cluster size correlation
    print("\n[9] Stability vs cluster size:")
    if cluster_results:
        sizes = [cr["cluster_size"] for cr in cluster_results]
        avgs = [cr["avg_spectrum"] for cr in cluster_results]
        # Spearman-like: rank correlation
        n_cr = len(cluster_results)
        if n_cr >= 3:
            # Simple Pearson on ranks
            size_ranks = _rank(sizes)
            avg_ranks = _rank(avgs)
            corr = _pearson(size_ranks, avg_ranks)
            print(f"    Rank correlation (cluster_size vs avg_spectrum): {corr:.3f}")
        else:
            corr = None
            print(f"    Too few clusters for correlation")

    # 10. Identify most unstable sequences and their fragile primes
    print("\n[10] Most unstable sequences (spectrum=0):")
    completely_unstable = [
        (sid, sr) for sid, sr in stability_results.items()
        if sr["stability_spectrum"] == 0
    ]
    print(f"    Count: {len(completely_unstable)}")
    for sid, sr in completely_unstable[:10]:
        print(f"      {sid}: deg={sr['degree']}, coeffs={sr['coeffs_int']}")

    # 11. Fragile prime distribution among partially unstable
    print("\n[11] Which primes break recurrences (among unstable sequences)?")
    fragile_prime_dist = Counter()
    for sid, sr in stability_results.items():
        for p in PRIMES:
            if not sr["prime_results"][str(p)]["stable"]:
                fragile_prime_dist[p] += 1

    total_tested = len(stability_results)
    for p in PRIMES:
        count = fragile_prime_dist.get(p, 0)
        print(f"    p={p:2d}: breaks {count:5d}/{total_tested} = {100*count/total_tested:.1f}%")

    # 12. Conditional: among sequences unstable at exactly 1 prime, which prime?
    print("\n[12] Sequences with exactly one fragile prime:")
    one_fragile = defaultdict(int)
    one_fragile_total = 0
    for sid, sr in stability_results.items():
        if sr["stability_spectrum"] == 5:
            one_fragile_total += 1
            for p in PRIMES:
                if not sr["prime_results"][str(p)]["stable"]:
                    one_fragile[p] += 1

    print(f"    Total with spectrum=5: {one_fragile_total}")
    for p in PRIMES:
        c = one_fragile.get(p, 0)
        pct = 100 * c / one_fragile_total if one_fragile_total else 0
        print(f"    Fragile at p={p:2d}: {c:4d} ({pct:.1f}%)")

    # 13. Char poly discriminant and root analysis
    print("\n[13] Characteristic polynomial root analysis:")
    deg2_disc_analysis = defaultdict(lambda: {"stable": 0, "unstable": 0})
    for sid, sr in stability_results.items():
        if sr["degree"] != 2:
            continue
        c1, c2 = sr["coeffs_int"]
        disc = c1 * c1 - 4 * c2
        for p in PRIMES:
            has_double_root = (disc % p == 0)
            is_stable = sr["prime_results"][str(p)]["stable"]
            key = (p, has_double_root)
            if is_stable:
                deg2_disc_analysis[key]["stable"] += 1
            else:
                deg2_disc_analysis[key]["unstable"] += 1

    print("    Degree-2: discriminant mod p distribution:")
    for p in PRIMES:
        for has_dr in [False, True]:
            key = (p, has_dr)
            s = deg2_disc_analysis[key]["stable"]
            u = deg2_disc_analysis[key]["unstable"]
            total = s + u
            if total > 0:
                rate = u / total
                dr_label = "disc=0" if has_dr else "disc!=0"
                print(f"    p={p:2d}, {dr_label:8s}: {u:4d}/{total:4d} unstable ({100*rate:.1f}%)")

    # 14. DEGREE REDUCTION: char poly factorization mod p
    # This is the real finding: recurrences are STABLE (hold mod p),
    # but the char poly may FACTOR mod p, yielding a SHORTER recurrence.
    # This is the algebraically interesting invariant.
    print("\n[14] Degree reduction analysis (char poly factorization mod p)...")
    print("    For each sequence, run BM mod p to find minimal recurrence degree in F_p.")
    print("    If deg_p < deg_Z, the char poly factors mod p (degree reduction).")

    degree_reduction = {}
    reduction_count_per_prime = {p: 0 for p in PRIMES}
    reduction_spectrum = Counter()  # how many primes reduce degree
    sample_count = min(1000, len(stability_results))

    # Sample sequences for BM-mod-p (it's more expensive)
    sampled_sids = list(stability_results.keys())[:sample_count]

    for idx, sid in enumerate(sampled_sids):
        if (idx + 1) % 200 == 0:
            print(f"    ... {idx+1}/{sample_count}")
        sr = stability_results[sid]
        deg_z = sr["degree"]
        terms = terms_data[sid]
        n_terms = len(terms)

        prime_deg = {}
        n_reduced = 0

        for p in PRIMES:
            terms_mod = [t % p for t in terms]
            # Run BM mod p
            bm_coeffs, bm_deg = berlekamp_massey_mod_p(terms_mod, p, max_deg=deg_z + 2)

            if bm_coeffs is not None and bm_deg > 0 and bm_deg < deg_z:
                # Verify the reduced recurrence
                ok = True
                for i in range(bm_deg, min(n_terms, bm_deg + 50)):
                    pred = 0
                    for j in range(bm_deg):
                        pred = (pred + ((-bm_coeffs[j]) % p) * terms_mod[i - j - 1]) % p
                    if pred != terms_mod[i]:
                        ok = False
                        break
                if ok:
                    prime_deg[p] = bm_deg
                    reduction_count_per_prime[p] += 1
                    n_reduced += 1
                else:
                    prime_deg[p] = deg_z  # BM failed verification
            else:
                prime_deg[p] = bm_deg if (bm_coeffs is not None and bm_deg > 0) else deg_z

        # Also check char poly roots mod p
        has_root_at = {}
        for p in PRIMES:
            has_root, roots, _ = char_poly_factors_mod_p(sr["coeffs_int"], p)
            has_root_at[p] = roots

        reduction_spectrum[n_reduced] += 1

        degree_reduction[sid] = {
            "deg_z": deg_z,
            "deg_mod_p": {str(p): prime_deg[p] for p in PRIMES},
            "reduced_at": [p for p in PRIMES if prime_deg[p] < deg_z],
            "n_reduced": n_reduced,
            "char_poly_roots": {str(p): has_root_at[p] for p in PRIMES},
        }

    print(f"\n    Degree reduction spectrum (n_primes_with_reduction: count):")
    for k in sorted(reduction_spectrum.keys()):
        pct = 100.0 * reduction_spectrum[k] / sample_count
        bar = "#" * int(pct / 2)
        print(f"      {k}/6: {reduction_spectrum[k]:5d} ({pct:5.1f}%) {bar}")

    print(f"\n    Per-prime degree reduction rates:")
    for p in PRIMES:
        c = reduction_count_per_prime[p]
        print(f"    p={p:2d}: {c:4d}/{sample_count} reduced ({100*c/sample_count:.1f}%)")

    # Degree reduction vs original degree
    print(f"\n    Degree reduction vs original degree:")
    deg_red_by_degree = defaultdict(lambda: {"total": 0, "any_reduced": 0, "avg_n_reduced": 0})
    for sid, dr in degree_reduction.items():
        deg = dr["deg_z"]
        deg_red_by_degree[deg]["total"] += 1
        if dr["n_reduced"] > 0:
            deg_red_by_degree[deg]["any_reduced"] += 1
        deg_red_by_degree[deg]["avg_n_reduced"] += dr["n_reduced"]
    for deg in sorted(deg_red_by_degree.keys()):
        dd = deg_red_by_degree[deg]
        if dd["total"] == 0:
            continue
        rate = dd["any_reduced"] / dd["total"]
        avg = dd["avg_n_reduced"] / dd["total"]
        print(f"    deg {deg}: {dd['any_reduced']:4d}/{dd['total']:4d} have reduction ({100*rate:.1f}%), avg_primes_reduced={avg:.2f}")

    # Interesting: sequences that reduce at exactly one prime
    print(f"\n    Sequences with reduction at exactly one prime:")
    single_reduction = Counter()
    for sid, dr in degree_reduction.items():
        if dr["n_reduced"] == 1:
            single_reduction[dr["reduced_at"][0]] += 1
    for p in PRIMES:
        print(f"    p={p:2d}: {single_reduction.get(p, 0)}")

    # Examples of degree reduction
    print(f"\n    Example degree reductions:")
    examples_shown = 0
    for sid, dr in degree_reduction.items():
        if dr["n_reduced"] > 0 and examples_shown < 10:
            sr = stability_results[sid]
            print(f"      {sid}: deg_Z={dr['deg_z']}, coeffs={sr['coeffs_int']}")
            for p in dr["reduced_at"]:
                print(f"        mod {p}: deg={dr['deg_mod_p'][str(p)]}, roots={dr['char_poly_roots'][str(p)]}")
            examples_shown += 1

    # Degree-1 sequences (geometric): which are "periodic mod p" (root = 0 mod p)?
    print(f"\n    Degree-1 sequences with trivial reduction (a(n) = c*a(n-1), c=0 mod p):")
    deg1_trivial = Counter()
    for sid, dr in degree_reduction.items():
        if dr["deg_z"] == 1:
            sr = stability_results[sid]
            c = sr["coeffs_int"][0]
            for p in PRIMES:
                if c % p == 0:
                    deg1_trivial[p] += 1
    for p in PRIMES:
        print(f"    p={p:2d}: {deg1_trivial.get(p, 0)}")

    # Cross-reference: char poly has root mod p <=> degree reduces mod p
    print(f"\n    Cross-check: char poly root mod p vs degree reduction:")
    root_vs_red = {"root_and_red": 0, "root_no_red": 0, "no_root_red": 0, "no_root_no_red": 0}
    for sid, dr in degree_reduction.items():
        for p in PRIMES:
            has_root = len(dr["char_poly_roots"][str(p)]) > 0
            is_reduced = (p in dr["reduced_at"])
            if has_root and is_reduced:
                root_vs_red["root_and_red"] += 1
            elif has_root and not is_reduced:
                root_vs_red["root_no_red"] += 1
            elif not has_root and is_reduced:
                root_vs_red["no_root_red"] += 1
            else:
                root_vs_red["no_root_no_red"] += 1
    total_pairs = sum(root_vs_red.values())
    for k, v in root_vs_red.items():
        print(f"    {k:20s}: {v:6d} ({100*v/total_pairs:.1f}%)")

    # 15. Build output
    print("\n[15] Building results JSON...")

    # Collect example sequences at each spectrum level
    spectrum_examples = defaultdict(list)
    for sid, sr in stability_results.items():
        spec = sr["stability_spectrum"]
        if len(spectrum_examples[spec]) < 20:
            spectrum_examples[spec].append({
                "seq_id": sid,
                "degree": sr["degree"],
                "coeffs_int": sr["coeffs_int"],
                "unstable_at": [p for p in PRIMES if not sr["prime_results"][str(p)]["stable"]],
            })

    elapsed = time.time() - t0

    output = {
        "challenge": "M10",
        "title": "Recurrence Stability Under Prime Reduction",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_seconds": round(elapsed, 1),
        "parameters": {
            "primes_tested": PRIMES,
            "max_degree": 10,
            "source": "S33 BM recurrences + OEIS stripped_new.txt",
        },
        "coverage": {
            "s33_recurrences_loaded": len(rec_data),
            "terms_loaded": len(terms_data),
            "non_integer_coefficients": non_integer_count,
            "z_verification_failures": z_fail_count,
            "sequences_tested": len(stability_results),
        },
        "stability_spectrum": {
            str(k): {
                "count": spectrum_dist[k],
                "fraction": round(spectrum_dist[k] / len(stability_results), 4) if stability_results else 0,
                "examples": spectrum_examples.get(k, []),
            }
            for k in range(7)
        },
        "per_prime_instability": prime_instability,
        "stability_vs_degree": degree_stats,
        "c08_cross_reference": {
            "in_cluster_count": in_cluster_count,
            "out_cluster_count": out_cluster_count,
            "avg_spectrum_in_cluster": round(sum(in_cluster_spectra) / len(in_cluster_spectra), 3) if in_cluster_spectra else None,
            "avg_spectrum_out_cluster": round(sum(out_cluster_spectra) / len(out_cluster_spectra), 3) if out_cluster_spectra else None,
            "cluster_details": cluster_results,
            "size_spectrum_rank_correlation": round(corr, 4) if cluster_results and len(cluster_results) >= 3 else None,
        },
        "fragile_prime_distribution": {
            "overall": {str(p): fragile_prime_dist.get(p, 0) for p in PRIMES},
            "single_fragile": {str(p): one_fragile.get(p, 0) for p in PRIMES},
            "single_fragile_total": one_fragile_total,
        },
        "discriminant_analysis": {
            f"p={p}": {
                "disc_zero_unstable": deg2_disc_analysis[(p, True)]["unstable"],
                "disc_zero_stable": deg2_disc_analysis[(p, True)]["stable"],
                "disc_nonzero_unstable": deg2_disc_analysis[(p, False)]["unstable"],
                "disc_nonzero_stable": deg2_disc_analysis[(p, False)]["stable"],
            }
            for p in PRIMES
        },
        "completely_unstable": {
            "count": len(completely_unstable),
            "examples": [
                {"seq_id": sid, "degree": sr["degree"], "coeffs_int": sr["coeffs_int"]}
                for sid, sr in completely_unstable[:30]
            ],
        },
        "maximally_stable": {
            "count": spectrum_dist.get(6, 0),
            "fraction": round(spectrum_dist.get(6, 0) / len(stability_results), 4) if stability_results else 0,
        },
        "degree_reduction": {
            "description": "Char poly factorization mod p: minimal recurrence degree in F_p may be smaller than over Z",
            "sequences_tested": sample_count,
            "reduction_spectrum": {
                str(k): {
                    "count": reduction_spectrum[k],
                    "fraction": round(reduction_spectrum[k] / sample_count, 4),
                }
                for k in range(7)
            },
            "per_prime_reduction_rate": {
                str(p): {
                    "reduced_count": reduction_count_per_prime[p],
                    "rate": round(reduction_count_per_prime[p] / sample_count, 4),
                }
                for p in PRIMES
            },
            "reduction_by_degree": {
                str(deg): {
                    "total": dd["total"],
                    "any_reduced": dd["any_reduced"],
                    "rate": round(dd["any_reduced"] / dd["total"], 4) if dd["total"] > 0 else 0,
                    "avg_primes_reduced": round(dd["avg_n_reduced"] / dd["total"], 3) if dd["total"] > 0 else 0,
                }
                for deg, dd in sorted(deg_red_by_degree.items())
            },
            "single_prime_reduction": {str(p): single_reduction.get(p, 0) for p in PRIMES},
            "root_vs_reduction_contingency": root_vs_red,
            "examples": [
                {
                    "seq_id": sid,
                    "deg_z": dr["deg_z"],
                    "coeffs_int": stability_results[sid]["coeffs_int"],
                    "deg_mod_p": dr["deg_mod_p"],
                    "reduced_at": dr["reduced_at"],
                    "char_poly_roots": {k: v for k, v in dr["char_poly_roots"].items() if v},
                }
                for sid, dr in list(degree_reduction.items())[:50]
                if dr["n_reduced"] > 0
            ],
        },
        "key_finding": "Linear recurrences over Z are universally p-stable (ring homomorphism Z->F_p preserves equalities). "
                       "The interesting invariant is DEGREE REDUCTION: the char poly may factor mod p, "
                       "yielding a shorter recurrence in F_p. This maps the prime sensitivity of each recurrence's algebraic structure.",
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n    Results saved to {OUT_FILE}")
    print(f"    Total runtime: {elapsed:.1f}s")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    n = len(stability_results)
    ms = spectrum_dist.get(6, 0)
    cu = len(completely_unstable)
    print(f"  Sequences tested: {n}")
    print(f"  p-STABILITY: {ms}/{n} ({100*ms/n:.1f}%) are stable at all 6 primes")
    print(f"  (This is expected: Z->F_p ring homomorphism preserves exact equalities)")
    print(f"  Completely unstable (0/6): {cu}")
    n_any_red = sum(1 for dr in degree_reduction.values() if dr["n_reduced"] > 0)
    print(f"  DEGREE REDUCTION: {n_any_red}/{sample_count} ({100*n_any_red/sample_count:.1f}%) have shorter recurrence mod some p")
    for p in PRIMES:
        c = reduction_count_per_prime[p]
        print(f"    p={p:2d}: {c:4d} reductions ({100*c/sample_count:.1f}%)")
    if in_cluster_spectra and out_cluster_spectra:
        avg_in = sum(in_cluster_spectra) / len(in_cluster_spectra)
        avg_out = sum(out_cluster_spectra) / len(out_cluster_spectra)
        print(f"  In-cluster avg spectrum: {avg_in:.2f} vs out-cluster: {avg_out:.2f}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rank(vals):
    """Simple ranking (average rank for ties)."""
    n = len(vals)
    indexed = sorted(range(n), key=lambda i: vals[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and vals[indexed[j + 1]] == vals[indexed[j]]:
            j += 1
        avg_rank = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def _pearson(x, y):
    """Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    sx = sum((xi - mx) ** 2 for xi in x) ** 0.5
    sy = sum((yi - my) ** 2 for yi in y) ** 0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (sx * sy)


if __name__ == "__main__":
    main()
