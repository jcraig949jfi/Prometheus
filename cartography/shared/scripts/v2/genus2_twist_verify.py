"""
Genus-2 Quadratic Twist Verification
======================================
For the 3 mod-2 anomalies with b_p = 0 at all primes (N=4293, 7173, 9459),
determine the twist discriminant and confirm the quadratic twist relationship.

Genus-2 quadratic twist by d:
  a_p(C_d) = chi_d(p) * a_p(C)   where chi_d = Kronecker symbol (d/.)
  b_p(C_d) = b_p(C)              (invariant)

So if b_p differences are all zero and a_p(C2) = +/- a_p(C1) with the sign
matching a Kronecker symbol, we have a twist.

Usage:
    python genus2_twist_verify.py
"""

import re
import json
from collections import defaultdict, Counter
from pathlib import Path
from math import gcd


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


def kronecker_symbol(a, p):
    """Kronecker symbol (a/p) for odd prime p."""
    a = a % p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def is_squarefree(n):
    """Check if n is squarefree."""
    if n == 0:
        return False
    n = abs(n)
    for p in range(2, int(n**0.5) + 1):
        if n % (p * p) == 0:
            return False
    return True


def parse_igusa_clebsch(s):
    s = s.strip("[]")
    parts = s.split(",")
    if len(parts) == 4:
        return [int(x.strip()) for x in parts]
    return None


def main():
    data_path = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"

    print("GENUS-2 QUADRATIC TWIST VERIFICATION")
    print("=" * 72)
    print()

    target_conds = [4293, 7173, 9459]

    # Load curves for target conductors
    curves_by_cond = defaultdict(list)
    with open(data_path, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            cond = int(parts[1])
            if cond not in target_conds:
                continue
            st = parts[8]
            eqn = parts[3]
            ic_raw = parts[5]
            disc = int(parts[0])
            euler_matches = re.findall(r"\[(-?\d+),(-?\d+),(-?\d+)\]", parts[16])
            euler = {int(m[0]): (int(m[1]), int(m[2])) for m in euler_matches}

            curves_by_cond[cond].append({
                "st": st, "eqn": eqn, "disc": disc,
                "ic": parse_igusa_clebsch(ic_raw),
                "euler": euler,
            })

    for cond in target_conds:
        print(f"\n{'='*72}")
        print(f"CONDUCTOR N = {cond}")
        print(f"{'='*72}")

        curves = curves_by_cond[cond]
        usp4 = [c for c in curves if c["st"] == "USp(4)"]
        print(f"Total curves: {len(curves)}, USp(4): {len(usp4)}")

        # Deduplicate by isogeny class
        classes = defaultdict(list)
        for c in usp4:
            primes_avail = sorted(c["euler"].keys())
            fp = tuple(c["euler"][p] for p in primes_avail[:20])
            classes[fp].append(c)

        class_list = list(classes.values())
        print(f"Distinct isogeny classes: {len(class_list)}")

        bad = prime_factors(cond)

        # Check all pairs for mod-2 congruence with b_p = 0
        for i in range(len(class_list)):
            for j in range(i + 1, len(class_list)):
                c1 = class_list[i][0]
                c2 = class_list[j][0]
                common = sorted(set(c1["euler"].keys()) & set(c2["euler"].keys()))
                good = [p for p in common if p not in bad and p != 2]

                # Check b_p exact match
                b_match = True
                a_diffs = []
                for p in good:
                    a1, b1 = c1["euler"][p]
                    a2, b2 = c2["euler"][p]
                    if b1 != b2:
                        b_match = False
                        break
                    a_diffs.append((p, a1, a2, a1 - a2))

                if not b_match:
                    continue

                has_nz = any(d[3] != 0 for d in a_diffs)
                if not has_nz:
                    continue

                print(f"\n  PAIR: b_p EXACT MATCH at all {len(good)} primes")
                print(f"  Curve 1: {c1['eqn'][:60]}")
                print(f"  Curve 2: {c2['eqn'][:60]}")

                # Check IC match
                if c1["ic"] and c2["ic"]:
                    ic_match = (c1["ic"] == c2["ic"])
                    print(f"  IC match: {'IDENTICAL' if ic_match else 'DIFFER'}")
                    if ic_match:
                        print(f"    IC = {c1['ic']}")
                    else:
                        print(f"    IC1 = {c1['ic']}")
                        print(f"    IC2 = {c2['ic']}")

                # Determine the sign pattern
                print(f"\n  a_p comparison:")
                sign_pattern = []
                for p, a1, a2, da in a_diffs[:30]:
                    if a1 == 0 and a2 == 0:
                        sign = 0
                    elif a1 != 0 and a2 == -a1:
                        sign = -1
                    elif a1 != 0 and a2 == a1:
                        sign = 1
                    else:
                        sign = None  # Not a simple twist
                    sign_pattern.append((p, sign))
                    if len(a_diffs) <= 30 or p <= 47:
                        marker = {1: "+", -1: "-", 0: "0", None: "?"}[sign]
                        print(f"    p={p:>3}: a1={a1:>4}, a2={a2:>4}, "
                              f"da={da:>4}, sign={marker}")

                # Check if sign pattern matches a Kronecker symbol
                # Extract the sign at each prime
                target_signs = {}
                for p, sign in sign_pattern:
                    if sign is not None and sign != 0:
                        target_signs[p] = sign

                if not target_signs:
                    print("\n  No non-trivial a_p to determine twist character")
                    continue

                # If all signs are +1, it's the trivial character (not a twist)
                if all(s == 1 for s in target_signs.values()):
                    print("\n  All signs +1: trivial character (identical a_p)")
                    continue

                # If all signs are -1, twist by d with chi(d/p) = -1 for all p
                # This means d < 0 (negative fundamental discriminant)
                all_neg = all(s == -1 for s in target_signs.values())
                if all_neg:
                    print(f"\n  ALL signs -1 at {len(target_signs)} primes")
                    print("  Looking for twist discriminant d with (d/p) = -1 for all p...")

                # Search for the twist discriminant
                print("\n  Twist discriminant search:")
                found_twist = False
                for d in range(-200, 201):
                    if d == 0 or not is_squarefree(d):
                        continue
                    # Check if (d/p) matches target_signs at all primes
                    match = True
                    for p, expected in target_signs.items():
                        if p == 2:
                            continue
                        ks = kronecker_symbol(d, p)
                        if ks != expected:
                            match = False
                            break
                    if match:
                        # Verify at ALL primes (including ones where a_p = 0)
                        full_match = True
                        for p, a1, a2, da in a_diffs:
                            if p == 2:
                                continue
                            ks = kronecker_symbol(d, p)
                            if a2 != ks * a1:
                                full_match = False
                                break

                        status = "EXACT TWIST" if full_match else "PARTIAL (fails full check)"
                        print(f"    d = {d:>4}: {status}")
                        if full_match:
                            found_twist = True
                            # Show the Kronecker symbol values
                            print(f"    Verified: a_p(C2) = (d/p) * a_p(C1) at all {len(good)} primes")
                            print(f"    b_p(C2) = b_p(C1) at all {len(good)} primes")

                            # Factor d
                            if d < 0:
                                print(f"    d = {d} = -1 * {abs(d)}")
                            pfact = prime_factors(abs(d))
                            print(f"    |d| prime factors: {sorted(pfact)}")

                            # Check if d divides the conductor
                            print(f"    d divides N? {cond % abs(d) == 0 if d != 0 else 'N/A'}")

                            # Conductor relationship
                            print(f"    N = {cond}, factored: ", end="")
                            n = cond
                            factors = []
                            d2 = 2
                            while d2 * d2 <= n:
                                while n % d2 == 0:
                                    factors.append(d2)
                                    n //= d2
                                d2 += 1
                            if n > 1:
                                factors.append(n)
                            print(" * ".join(str(f) for f in factors))

                if not found_twist:
                    print("    No squarefree d in [-200, 200] matches the sign pattern")
                    print("    This may indicate a non-quadratic twist or a deeper symmetry")

                    # Analyze the sign pattern more carefully
                    neg_primes = [p for p, s in target_signs.items() if s == -1]
                    pos_primes = [p for p, s in target_signs.items() if s == 1]
                    print(f"\n    Primes with sign -1: {neg_primes[:20]}")
                    print(f"    Primes with sign +1: {pos_primes[:20]}")
                    print(f"    Ratio: {len(neg_primes)}/{len(neg_primes)+len(pos_primes)}")

    print(f"\n{'='*72}")
    print("SUMMARY")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()
