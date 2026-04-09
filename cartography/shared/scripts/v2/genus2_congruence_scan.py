"""
Genus-2 Congruence Scanner — Probing the Paramodular Hecke Algebra
===================================================================
Scans genus-2 curves for mod-ell congruences on degree-4 L-functions.

For genus-2 curve C, the Euler factor at good prime p is:
  L_p(T) = 1 - a_p*T + b_p*T^2 - a_p*p*T^3 + p^2*T^4

Two curves C1, C2 at the same conductor are congruent mod ell if:
  a_p(C1) = a_p(C2) (mod ell) AND b_p(C1) = b_p(C2) (mod ell)
at all good primes.

This probes the structure of the paramodular Hecke algebra mod ell.
Two conditions per prime (vs one for GL_2) makes congruences much rarer.

Usage:
    python genus2_congruence_scan.py
    python genus2_congruence_scan.py --ell 5 7 11
    python genus2_congruence_scan.py --max-conductor 10000
"""

import sys
import json
import time
import re
from pathlib import Path
from collections import defaultdict, Counter
from math import sqrt

def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


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


# ---------------------------------------------------------------------------
# Parse genus-2 LMFDB data
# ---------------------------------------------------------------------------
def parse_good_lfactors(s):
    """Parse good_lfactors field: [[p, a_p, b_p], ...]"""
    # Format: [[2,3,5],[3,2,1],[5,0,-7],...]
    result = {}
    # Find all [p,a,b] triples
    matches = re.findall(r'\[(-?\d+),(-?\d+),(-?\d+)\]', s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


def load_genus2_data(filepath, max_conductor=None):
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
            if max_conductor and conductor > max_conductor:
                continue

            # Parse fields
            disc = int(parts[0])
            disc_sign = int(parts[4])
            st_group = parts[8]
            good_lfactors_str = parts[16] if len(parts) > 16 else ""

            # Parse Euler factors
            euler = parse_good_lfactors(good_lfactors_str)
            if not euler:
                continue

            # Parse equation for label
            min_eqn = parts[3]

            curves.append({
                "conductor": conductor,
                "disc": disc,
                "disc_sign": disc_sign,
                "st_group": st_group,
                "min_eqn": min_eqn,
                "euler": euler,  # {p: (a_p, b_p)}
                "n_primes": len(euler),
            })

    return curves


# ---------------------------------------------------------------------------
# Congruence scan
# ---------------------------------------------------------------------------
def scan_genus2_congruences(curves, ell_list, min_primes=10):
    """Scan for mod-ell congruences between genus-2 curves at same conductor."""

    # Group by conductor
    by_conductor = defaultdict(list)
    for i, c in enumerate(curves):
        by_conductor[c["conductor"]].append(i)

    results = {}

    for ell in ell_list:
        congruences = []
        n_pairs = 0
        n_conductors = 0

        for cond, indices in sorted(by_conductor.items()):
            if len(indices) < 2:
                continue
            n_conductors += 1

            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    n_pairs += 1
                    c1 = curves[indices[i]]
                    c2 = curves[indices[j]]

                    # Find common good primes
                    common_primes = sorted(set(c1["euler"].keys()) & set(c2["euler"].keys()))

                    # Filter out primes dividing conductor (bad primes)
                    bad = prime_factors(cond)
                    good_primes = [p for p in common_primes if p not in bad]

                    if len(good_primes) < min_primes:
                        continue

                    # Check congruence: both a_p and b_p must be congruent mod ell
                    all_cong = True
                    diffs_a = []
                    diffs_b = []
                    for p in good_primes:
                        a1, b1 = c1["euler"][p]
                        a2, b2 = c2["euler"][p]
                        da = a1 - a2
                        db = b1 - b2
                        if da % ell != 0 or db % ell != 0:
                            all_cong = False
                            break
                        diffs_a.append(da)
                        diffs_b.append(db)

                    if all_cong:
                        ell_div_cond = (cond % ell == 0)
                        congruences.append({
                            "conductor": cond,
                            "ell": ell,
                            "ell_divides_N": ell_div_cond,
                            "curve1_st": c1["st_group"],
                            "curve2_st": c2["st_group"],
                            "curve1_eqn": c1["min_eqn"][:60],
                            "curve2_eqn": c2["min_eqn"][:60],
                            "n_good_primes": len(good_primes),
                            "nonzero_da": sum(1 for d in diffs_a if d != 0),
                            "nonzero_db": sum(1 for d in diffs_b if d != 0),
                            "diffs_a_sample": diffs_a[:10],
                            "diffs_b_sample": diffs_b[:10],
                            "both_USp4": c1["st_group"] == "USp(4)" and c2["st_group"] == "USp(4)",
                        })

        n_coprime = sum(1 for c in congruences if not c["ell_divides_N"])
        n_usp4 = sum(1 for c in congruences if c["both_USp4"])

        results[ell] = {
            "ell": ell,
            "total_congruences": len(congruences),
            "coprime_to_N": n_coprime,
            "both_USp4": n_usp4,
            "pairs_checked": n_pairs,
            "conductors_checked": n_conductors,
            "congruences": congruences,
        }

    return results


# ---------------------------------------------------------------------------
# Hasse squeeze analysis for genus-2
# ---------------------------------------------------------------------------
def hasse_squeeze_genus2(ell_list):
    """Compute the Hasse squeeze for genus-2 degree-4 L-functions."""
    primes = sieve_primes(100)[:20]

    print("\nHASSE SQUEEZE FOR GENUS-2 (degree-4 L-functions)")
    print("=" * 60)
    print()
    print("Two conditions per prime: a_p AND b_p must both be = 0 mod ell.")
    print("Bounds: |a_p| <= 4*sqrt(p), |b_p| <= 6*p (Weil bounds)")
    print()

    for ell in ell_list:
        forced_a = 0  # primes where da forced to 0
        forced_b = 0  # primes where db forced to 0
        forced_both = 0  # primes where BOTH forced to 0

        for p in primes[:15]:
            # a_p bound: |da| <= 2*floor(4*sqrt(p)) (difference of two)
            Ha = int(4 * sqrt(p))
            Da = 2 * Ha
            a_forced = (Da < ell)

            # b_p bound: |db| <= 2*6*p = 12*p
            # Actually the Weil bound on b_p is tighter: b_p = (a_p^2 - a_{p^2})/2
            # but conservatively |b_p| <= 6p
            Hb = 6 * p
            Db = 2 * Hb
            b_forced = (Db < ell)

            if a_forced:
                forced_a += 1
            if b_forced:
                forced_b += 1
            if a_forced and b_forced:
                forced_both += 1

        print(f"ell={ell:2d}: a_p forced to 0 at {forced_a} primes, "
              f"b_p forced to 0 at {forced_b} primes, "
              f"both forced at {forced_both} primes")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ell", type=int, nargs="+", default=[5, 7, 11, 13])
    parser.add_argument("--max-conductor", type=int, default=None)
    parser.add_argument("--data", type=str,
                        default=str(Path(__file__).resolve().parents[3] /
                                    "genus2" / "data" / "g2c-data" /
                                    "gce_1000000_lmfdb.txt"))
    args = parser.parse_args()

    print("GENUS-2 CONGRUENCE SCANNER")
    print("=" * 60)
    print(f"Data: {args.data}")
    print(f"Primes: {args.ell}")
    print(f"Max conductor: {args.max_conductor or 'all'}")
    print()

    # Load data
    t0 = time.time()
    print("Loading genus-2 curves...")
    curves = load_genus2_data(args.data, max_conductor=args.max_conductor)
    t1 = time.time()
    print(f"Loaded {len(curves)} curves in {t1-t0:.1f}s")

    # Stats
    conductors = Counter(c["conductor"] for c in curves)
    st_groups = Counter(c["st_group"] for c in curves)
    n_usp4 = st_groups.get("USp(4)", 0)
    multi_cond = {k: v for k, v in conductors.items() if v >= 2}

    print(f"Distinct conductors: {len(conductors)}")
    print(f"Conductors with 2+ curves: {len(multi_cond)}")
    print(f"USp(4) curves: {n_usp4} ({100*n_usp4/len(curves):.1f}%)")
    print(f"Primes per curve: {min(c['n_primes'] for c in curves)}-"
          f"{max(c['n_primes'] for c in curves)}")
    print()

    # Sato-Tate distribution
    print("Sato-Tate groups (top 5):")
    for st, cnt in st_groups.most_common(5):
        print(f"  {st}: {cnt}")
    print()

    # Scan
    t2 = time.time()
    results = scan_genus2_congruences(curves, args.ell)
    t3 = time.time()
    print(f"Scan completed in {t3-t2:.1f}s")
    print()

    # Results table
    print("RESULTS")
    print("=" * 60)
    print(f"{'ell':<5} {'Total':<7} {'l coprime N':<12} {'Both USp(4)':<12} "
          f"{'Pairs':<8}")
    print("-" * 50)

    for ell in args.ell:
        r = results[ell]
        print(f"{ell:<5} {r['total_congruences']:<7} {r['coprime_to_N']:<12} "
              f"{r['both_USp4']:<12} {r['pairs_checked']:<8}")

    # Details
    for ell in args.ell:
        r = results[ell]
        if r["total_congruences"] > 0:
            print(f"\n--- Mod {ell} congruences ---")
            for c in r["congruences"]:
                div = "l|N" if c["ell_divides_N"] else "l coprime"
                usp = "USp4" if c["both_USp4"] else c["curve1_st"] + "/" + c["curve2_st"]
                print(f"  N={c['conductor']:<8} {div:<10} {usp:<20} "
                      f"primes={c['n_good_primes']:<3} "
                      f"da_nonzero={c['nonzero_da']}/{c['n_good_primes']} "
                      f"db_nonzero={c['nonzero_db']}/{c['n_good_primes']}")
                if c["diffs_a_sample"]:
                    print(f"    da: {c['diffs_a_sample']}")
                    print(f"    db: {c['diffs_b_sample']}")

    # Hasse squeeze
    hasse_squeeze_genus2(args.ell)

    # Save results
    out_file = Path(__file__).parent / "genus2_congruence_results.json"
    serializable = {}
    for ell in args.ell:
        serializable[str(ell)] = {k: v for k, v in results[ell].items()
                                   if k != "congruences"}
        serializable[str(ell)]["congruences"] = results[ell]["congruences"]
    with open(out_file, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"\nResults saved to {out_file}")


if __name__ == "__main__":
    main()
