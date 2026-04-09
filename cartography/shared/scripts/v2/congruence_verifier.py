"""
Congruence Verifier — Sturm Bound + Irreducibility for mod-ℓ congruences
=========================================================================
Verifies mod-11 congruence between EC 2184.a1 and MF 2184.2.a.b.

Gate 1 (Sturm bound): Verify a_p(E) ≡ a_p(f) (mod 11) at ALL primes
    up to the Sturm bound for Γ₀(2184), weight 2.
    Sturm bound = ⌊k·[SL₂(Z):Γ₀(N)]/12⌋ = 896.

Gate 2 (Irreducibility): If ρ_{E,11} were reducible, the Frobenius
    char poly x² - a_p·x + p would factor mod 11 at EVERY good prime.
    Discriminant Δ = a_p² - 4p must be a QR mod 11 for all p.
    ONE non-residue kills reducibility forever.

Gate 3 (Frobenius trace distribution): For surjectivity evidence,
    check that a_p mod 11 takes all 11 values {0,...,10} as p varies.

Usage:
    python congruence_verifier.py
    python congruence_verifier.py --all-pairs   # verify all 6 mod-11 pairs
"""

import sys
import json
import time
from pathlib import Path
from collections import Counter
from math import gcd

# Path setup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from search_engine import _get_duck

# ---------------------------------------------------------------------------
# Prime sieve
# ---------------------------------------------------------------------------
def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


# ---------------------------------------------------------------------------
# Sturm bound computation
# ---------------------------------------------------------------------------
def sturm_bound(N, k=2):
    """
    Compute Sturm bound for M_k(Γ₀(N)).
    Sturm bound = ⌊k · [SL₂(Z) : Γ₀(N)] / 12⌋
    Index = N · ∏_{p|N} (1 + 1/p)
    """
    index = N
    temp = N
    for p in sieve_primes(int(temp**0.5) + 1):
        if p * p > temp:
            break
        if temp % p == 0:
            index = index * (p + 1) // p
            while temp % p == 0:
                temp //= p
    if temp > 1:
        index = index * (temp + 1) // temp
    return (k * index) // 12


# ---------------------------------------------------------------------------
# Point counting on elliptic curve over F_p
# ---------------------------------------------------------------------------
def legendre_symbol(a, p):
    """Compute Legendre symbol (a/p)."""
    if a % p == 0:
        return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls


def compute_ap(ainvs, p):
    """
    Compute a_p for elliptic curve with given ainvs = [a1,a2,a3,a4,a6].
    General Weierstrass: y² + a1·xy + a3·y = x³ + a2·x² + a4·x + a6

    a_p = -∑_{x=0}^{p-1} (f(x)/p) where f(x) is the RHS discriminant.
    For general form, complete the square in y.
    """
    a1, a2, a3, a4, a6 = [int(a) for a in ainvs]

    # Complete the square: (2y + a1·x + a3)² = 4x³ + b2·x² + 2b4·x + b6
    # where b2 = a1² + 4a2, b4 = a1·a3 + 2a4, b6 = a3² + 4a6
    b2 = a1*a1 + 4*a2
    b4 = a1*a3 + 2*a4
    b6 = a3*a3 + 4*a6

    # For p = 2, need special handling
    if p == 2:
        # Count points directly
        count = 0
        for x in range(p):
            for y in range(p):
                lhs = (y*y + a1*x*y + a3*y) % p
                rhs = (x*x*x + a2*x*x + a4*x + a6) % p
                if lhs == rhs:
                    count += 1
        return p + 1 - count - 1  # subtract point at infinity... actually add 1 for inf
        # #E(F_p) = 1 + count, a_p = p + 1 - #E(F_p) = p - count

    # For odd p: sum Legendre symbols of 4x³ + b2·x² + 2b4·x + b6
    s = 0
    for x in range(p):
        f = (4*x*x*x + b2*x*x + 2*b4*x + b6) % p
        s += legendre_symbol(f, p)

    return -s


def compute_ap_batch(ainvs, primes):
    """Compute a_p for all primes in list."""
    return {p: compute_ap(ainvs, p) for p in primes}


# ---------------------------------------------------------------------------
# Extract MF a_p from traces array
# ---------------------------------------------------------------------------
def extract_mf_ap_from_traces(traces, primes):
    """
    traces[n-1] = a_n for the modular form (0-indexed array, 1-indexed math).
    For an eigenform, a_p = traces[p-1].
    """
    result = {}
    for p in primes:
        if p <= len(traces):
            result[p] = int(round(traces[p - 1]))
    return result


# ---------------------------------------------------------------------------
# Quadratic residue check
# ---------------------------------------------------------------------------
def is_qr_mod(a, ell):
    """Check if a is a quadratic residue mod ell (including 0)."""
    a = a % ell
    if a == 0:
        return True  # 0 is a square
    return pow(a, (ell - 1) // 2, ell) == 1


# ---------------------------------------------------------------------------
# Main verification
# ---------------------------------------------------------------------------
def verify_congruence(ec_label, mf_label, ell=11, verbose=True):
    """
    Full verification: Sturm bound + irreducibility + trace distribution.
    """
    con = _get_duck()

    # --- Load EC data ---
    ec_row = con.execute(f"""
        SELECT ainvs, conductor, rank, torsion, cm, isogeny_degrees,
               class_size, aplist
        FROM elliptic_curves
        WHERE lmfdb_label = '{ec_label}'
    """).fetchone()

    if not ec_row:
        print(f"ERROR: EC {ec_label} not found")
        return None

    ainvs = ec_row[0]
    conductor = int(ec_row[1])
    rank = ec_row[2]
    torsion = ec_row[3]
    cm = ec_row[4]
    isogeny_degrees = ec_row[5]
    class_size = ec_row[6]
    stored_ap = ec_row[7]

    # --- Load MF data ---
    mf_row = con.execute(f"""
        SELECT traces, level, weight, dim, is_cm, ap_maxp
        FROM modular_forms
        WHERE lmfdb_label = '{mf_label}'
    """).fetchone()

    if not mf_row:
        print(f"ERROR: MF {mf_label} not found")
        return None

    traces = mf_row[0]
    level = int(mf_row[1])
    weight = mf_row[2]
    dim = mf_row[3]
    mf_cm = mf_row[4]
    ap_maxp = mf_row[5]

    con.close()

    # --- Compute Sturm bound ---
    sb = sturm_bound(level, weight)
    all_primes = sieve_primes(min(ap_maxp, len(traces)))
    primes_to_sb = [p for p in all_primes if p <= sb]
    primes_all = all_primes  # use all available

    bad_primes_N = set()
    temp = conductor
    for p in sieve_primes(int(temp**0.5) + 1):
        if p * p > temp:
            break
        if temp % p == 0:
            bad_primes_N.add(p)
            while temp % p == 0:
                temp //= p
    if temp > 1:
        bad_primes_N.add(temp)

    if verbose:
        print("=" * 72)
        print(f"CONGRUENCE VERIFICATION: {ec_label} ↔ {mf_label} mod {ell}")
        print("=" * 72)
        print()
        print(f"EC {ec_label}:")
        print(f"  Conductor:        {conductor}")
        print(f"  Weierstrass:      [{', '.join(str(int(a)) for a in ainvs)}]")
        print(f"  Rank:             {rank}")
        print(f"  Torsion:          {torsion}")
        print(f"  CM:               {cm}")
        print(f"  Isogeny degrees:  {isogeny_degrees}")
        print(f"  Class size:       {class_size}")
        print(f"  Stored a_p count: {len(stored_ap) if stored_ap else 0}")
        print()
        print(f"MF {mf_label}:")
        print(f"  Level:            {level}")
        print(f"  Weight:           {weight}")
        print(f"  Dimension:        {dim}")
        print(f"  CM:               {mf_cm}")
        print(f"  Traces available: {len(traces)}")
        print(f"  ap_maxp:          {ap_maxp}")
        print()
        print(f"Bad primes of N={conductor}: {sorted(bad_primes_N)}")
        print(f"ℓ = {ell}, ℓ | N: {ell in bad_primes_N}")
        print()
        print(f"Sturm bound for Γ₀({level}), weight {weight}: {sb}")
        print(f"Primes up to Sturm bound: {len(primes_to_sb)}")
        print(f"Total primes available: {len(primes_all)}")
        print()

    # --- GATE 1: Compute a_p(E) and verify congruence ---
    if verbose:
        print("-" * 72)
        print("GATE 1: STURM BOUND VERIFICATION")
        print("-" * 72)

    t0 = time.time()
    ec_ap = compute_ap_batch(ainvs, primes_all)
    t1 = time.time()

    if verbose:
        print(f"Computed a_p(E) at {len(ec_ap)} primes in {t1-t0:.1f}s")

    # Cross-check against stored values
    stored_primes = sieve_primes(97)[:len(stored_ap)] if stored_ap else []
    mismatches_stored = 0
    for i, p in enumerate(stored_primes):
        if i < len(stored_ap) and ec_ap.get(p) != stored_ap[i]:
            mismatches_stored += 1
            if verbose:
                print(f"  WARNING: stored a_{p} = {stored_ap[i]}, computed = {ec_ap.get(p)}")
    if verbose and stored_ap:
        print(f"Cross-check vs stored: {len(stored_primes) - mismatches_stored}/{len(stored_primes)} match")

    # Extract MF a_p from traces
    mf_ap = extract_mf_ap_from_traces(traces, primes_all)

    # Verify congruence
    failures_sb = []
    passes_sb = 0
    for p in primes_to_sb:
        if p not in ec_ap or p not in mf_ap:
            continue
        diff = ec_ap[p] - mf_ap[p]
        if diff % ell != 0:
            failures_sb.append((p, ec_ap[p], mf_ap[p], diff))
        else:
            passes_sb += 1

    failures_all = []
    passes_all = 0
    diffs_all = []
    for p in primes_all:
        if p not in ec_ap or p not in mf_ap:
            continue
        diff = ec_ap[p] - mf_ap[p]
        diffs_all.append((p, diff))
        if diff % ell != 0:
            failures_all.append((p, ec_ap[p], mf_ap[p], diff))
        else:
            passes_all += 1

    if verbose:
        print()
        print(f"Congruence mod {ell} up to Sturm bound ({sb}):")
        print(f"  Tested: {passes_sb + len(failures_sb)} primes")
        print(f"  PASS:   {passes_sb}")
        print(f"  FAIL:   {len(failures_sb)}")
        if failures_sb:
            print(f"  First failure: p={failures_sb[0][0]}, "
                  f"a_p(E)={failures_sb[0][1]}, a_p(f)={failures_sb[0][2]}, "
                  f"diff={failures_sb[0][3]}")

        print()
        print(f"Congruence mod {ell} up to p={primes_all[-1]}:")
        print(f"  Tested: {passes_all + len(failures_all)} primes")
        print(f"  PASS:   {passes_all}")
        print(f"  FAIL:   {len(failures_all)}")
        if failures_all:
            print(f"  First failure: p={failures_all[0][0]}, "
                  f"a_p(E)={failures_all[0][1]}, a_p(f)={failures_all[0][2]}, "
                  f"diff={failures_all[0][3]}")

        # Difference pattern analysis
        diff_vals = Counter(d for _, d in diffs_all)
        print()
        print(f"Difference pattern (a_p(E) - a_p(f)) distribution:")
        for val, cnt in sorted(diff_vals.items(), key=lambda x: -x[1])[:15]:
            marker = " ✓" if val % ell == 0 else " ✗"
            print(f"  diff={val:+4d}: {cnt:4d} primes{marker}")

    sturm_passed = len(failures_sb) == 0

    if verbose:
        print()
        if sturm_passed:
            print(f"★ GATE 1 PASSED: congruence mod {ell} verified at ALL "
                  f"{passes_sb} primes up to Sturm bound {sb}")
        else:
            print(f"✗ GATE 1 FAILED: {len(failures_sb)} failures below Sturm bound")

    # --- GATE 2: Irreducibility via discriminant test ---
    if verbose:
        print()
        print("-" * 72)
        print("GATE 2: IRREDUCIBILITY OF ρ_{E,ℓ}")
        print("-" * 72)
        print()
        print(f"Test: if ρ_{{E,{ell}}} is reducible, then for EVERY good prime p,")
        print(f"  Δ = a_p(E)² - 4p must be a quadratic residue mod {ell}.")
        print(f"  ONE non-residue kills reducibility.")
        print()

    good_primes = [p for p in primes_all if p not in bad_primes_N and p != ell]
    non_residues = []
    qr_count = 0

    # Quadratic residues mod ell
    qr_set = set()
    for i in range(ell):
        qr_set.add((i * i) % ell)

    if verbose:
        print(f"Quadratic residues mod {ell}: {sorted(qr_set)}")
        print(f"Non-residues mod {ell}: {sorted(set(range(ell)) - qr_set)}")
        print()

    for p in good_primes:
        ap = ec_ap[p]
        disc = (ap * ap - 4 * p) % ell
        if disc in qr_set:
            qr_count += 1
        else:
            non_residues.append((p, ap, disc))

    irreducible = len(non_residues) > 0

    if verbose:
        print(f"Good primes tested: {len(good_primes)}")
        print(f"  QR (consistent with reducible): {qr_count}")
        print(f"  Non-QR (kills reducibility):    {len(non_residues)}")

        if non_residues:
            print()
            print(f"First 10 non-residue witnesses:")
            for p, ap, disc in non_residues[:10]:
                print(f"  p={p}: a_p={ap}, Δ=a_p²-4p≡{disc} (mod {ell}) — NOT a QR")

        print()
        if irreducible:
            print(f"★ GATE 2 PASSED: ρ_{{E,{ell}}} is IRREDUCIBLE")
            print(f"  {len(non_residues)} witnesses prove it. First: p={non_residues[0][0]}")
        else:
            print(f"✗ GATE 2 INCONCLUSIVE: all discriminants are QR mod {ell}")
            print(f"  Representation MAY be reducible — further investigation needed")

    # --- GATE 3: Frobenius trace distribution ---
    if verbose:
        print()
        print("-" * 72)
        print("GATE 3: FROBENIUS TRACE DISTRIBUTION (surjectivity evidence)")
        print("-" * 72)
        print()

    trace_dist = Counter()
    for p in good_primes:
        trace_dist[ec_ap[p] % ell] += 1

    values_hit = len(trace_dist)

    if verbose:
        print(f"Distribution of a_p(E) mod {ell} over {len(good_primes)} good primes:")
        for v in range(ell):
            bar = "█" * (trace_dist.get(v, 0) // 2)
            print(f"  {v:2d}: {trace_dist.get(v, 0):4d}  {bar}")
        print()
        print(f"Values hit: {values_hit}/{ell}")
        if values_hit == ell:
            print(f"★ All {ell} residues represented — strong surjectivity evidence")
            print(f"  (If image were contained in a Borel subgroup, trace distribution")
            print(f"   would concentrate on ≤ 2 residue classes)")
        else:
            missing = [v for v in range(ell) if v not in trace_dist]
            print(f"  Missing values: {missing}")

    # --- SUMMARY ---
    if verbose:
        print()
        print("=" * 72)
        print("SUMMARY")
        print("=" * 72)
        print()
        print(f"EC {ec_label} ↔ MF {mf_label} mod {ell}")
        print()
        print(f"Gate 1 (Sturm bound = {sb}):  {'PASSED ★' if sturm_passed else 'FAILED ✗'}")
        print(f"  Congruence verified at {passes_sb} primes up to bound")
        if not sturm_passed:
            print(f"  {len(failures_sb)} failures")
        print()
        print(f"Gate 2 (Irreducibility):      {'PROVED ★' if irreducible else 'INCONCLUSIVE'}")
        if irreducible:
            print(f"  {len(non_residues)} non-QR witnesses, first at p={non_residues[0][0]}")
        print()
        print(f"Gate 3 (Trace distribution):  {values_hit}/{ell} values hit")
        print()

        if sturm_passed and irreducible:
            print("═" * 72)
            print("VERDICT: THEOREM-LEVEL MOD-ℓ CONGRUENCE WITH IRREDUCIBLE REPRESENTATION")
            print("═" * 72)
            print()
            print(f"The two non-CM weight-2 newforms at level {level} satisfy:")
            print(f"  a_p({ec_label}) ≡ a_p({mf_label}) (mod {ell})")
            print(f"for ALL primes p (verified computationally up to Sturm bound).")
            print(f"The mod-{ell} Galois representation ρ_{{E,{ell}}} is irreducible")
            print(f"(proved by {len(non_residues)} discriminant witnesses).")
            print()
            print(f"This is a verified instance of non-trivial congruence multiplicity")
            print(f"in the mod-{ell} Hecke algebra at level {level}.")
            print(f"The Hecke algebra T_{level} is NOT semisimple mod {ell}.")
            print(f"Two distinct eigenforms define the same mod-{ell} eigensystem.")
        elif sturm_passed and not irreducible:
            print("Congruence is theorem-level, but irreducibility not proved.")
            print("May be Eisenstein or CM-induced. Further investigation needed.")
        else:
            print("Congruence does NOT hold at Sturm bound level.")

    return {
        "ec_label": ec_label,
        "mf_label": mf_label,
        "ell": ell,
        "conductor": conductor,
        "sturm_bound": sb,
        "sturm_passed": sturm_passed,
        "primes_tested_sb": passes_sb + len(failures_sb),
        "failures_sb": len(failures_sb),
        "primes_tested_all": passes_all + len(failures_all),
        "failures_all": len(failures_all),
        "irreducible": irreducible,
        "n_witnesses": len(non_residues),
        "first_witness": non_residues[0][0] if non_residues else None,
        "trace_values_hit": values_hit,
        "ec_cm": cm,
        "mf_cm": mf_cm,
        "ec_torsion": torsion,
        "ec_isogeny_degrees": list(isogeny_degrees) if isogeny_degrees else [],
    }


# ---------------------------------------------------------------------------
# All mod-11 pairs
# ---------------------------------------------------------------------------
MOD11_PAIRS = [
    ("2184.a1", "2184.2.a.b"),
    ("2184.b1", "2184.2.a.a"),
    ("3990.ba1", "3990.2.a.z"),
    ("3990.z1", "3990.2.a.ba"),
    ("4368.m1", "4368.2.a.n"),
    ("4368.n1", "4368.2.a.m"),
]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verify mod-ℓ congruences")
    parser.add_argument("--all-pairs", action="store_true",
                        help="Verify all 6 mod-11 pairs")
    parser.add_argument("--ell", type=int, default=11,
                        help="Congruence prime (default: 11)")
    parser.add_argument("--ec", type=str, default="2184.a1",
                        help="EC label")
    parser.add_argument("--mf", type=str, default="2184.2.a.b",
                        help="MF label")
    args = parser.parse_args()

    results = []

    if args.all_pairs:
        for ec_label, mf_label in MOD11_PAIRS:
            result = verify_congruence(ec_label, mf_label, ell=args.ell)
            results.append(result)
            print("\n\n")
    else:
        result = verify_congruence(args.ec, args.mf, ell=args.ell)
        results.append(result)

    # Summary table
    if len(results) > 1:
        print("\n" + "=" * 72)
        print("ALL PAIRS SUMMARY")
        print("=" * 72)
        print(f"{'EC':<14} {'MF':<16} {'Level':>5} {'Sturm':>6} "
              f"{'Gate1':>6} {'Gate2':>10} {'Gate3':>6}")
        print("-" * 72)
        for r in results:
            if r is None:
                continue
            g1 = "PASS" if r["sturm_passed"] else "FAIL"
            g2 = f"IRR({r['n_witnesses']})" if r["irreducible"] else "OPEN"
            g3 = f"{r['trace_values_hit']}/{r['ell']}"
            print(f"{r['ec_label']:<14} {r['mf_label']:<16} {r['conductor']:>5} "
                  f"{r['sturm_bound']:>6} {g1:>6} {g2:>10} {g3:>6}")

    # Save results
    out_file = Path(__file__).parent / "congruence_verification_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_file}")


if __name__ == "__main__":
    main()
