"""
Genus-2 Mod-3 Irreducibility Sweep
====================================
For each of the 42 mod-3 coprime USp(4) congruence candidates,
check the Frobenius characteristic polynomial mod 3 at all good primes.

The char poly is: x^4 - a_p*x^3 + b_p*x^2 - a_p*p*x + p^2

If this polynomial is IRREDUCIBLE mod 3 at ANY prime, the mod-3
Galois representation is irreducible (not a product of GL_2 reps).
One irreducible char poly = kill shot against reducibility.
"""

import re
from collections import defaultdict, Counter
from math import sqrt


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


def parse_good_lfactors(s):
    result = {}
    matches = re.findall(r'\[(-?\d+),(-?\d+),(-?\d+)\]', s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


def poly_eval_mod(coeffs, x, ell):
    """Evaluate polynomial at x mod ell. coeffs[i] = coeff of x^i."""
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % ell
        xpow = (xpow * x) % ell
    return val


def poly_divmod(num, den, ell):
    """Polynomial division mod ell. Returns (quotient, remainder)."""
    num = [c % ell for c in num]
    den = [c % ell for c in den]
    degd = len(den) - 1
    degn = len(num) - 1
    if degn < degd:
        return [], num

    lead_inv = pow(den[-1], ell - 2, ell)
    quot = [0] * (degn - degd + 1)
    work = list(num)

    for i in range(degn - degd, -1, -1):
        quot[i] = (work[i + degd] * lead_inv) % ell
        for j in range(degd + 1):
            work[i + j] = (work[i + j] - quot[i] * den[j]) % ell

    rem = [work[i] % ell for i in range(degd)]
    return quot, rem


def factor_type_mod3(a_p, b_p, p):
    """
    Factor the Frobenius char poly mod 3.
    Poly: x^4 - a_p*x^3 + b_p*x^2 - a_p*p*x + p^2
    Coefficients in ascending order: [p^2, -a_p*p, b_p, -a_p, 1]
    """
    ell = 3
    coeffs = [
        (p * p) % ell,
        (-(a_p * p)) % ell,
        b_p % ell,
        (-a_p) % ell,
        1
    ]

    # Find linear factors (roots mod 3)
    roots = []
    for x in range(ell):
        if poly_eval_mod(coeffs, x, ell) == 0:
            roots.append(x)

    if len(roots) == 0:
        # No roots. Either irreducible (4) or two irreducible quadratics (2,2)
        # Try all monic quadratics x^2 + ax + b mod 3 (9 possibilities)
        for a1 in range(ell):
            for b1 in range(ell):
                q1 = [b1, a1, 1]
                quot, rem = poly_divmod(coeffs, q1, ell)
                if all(r == 0 for r in rem):
                    return "2+2"
        return "irreducible"

    elif len(roots) == 1:
        # Factor out (x - root)
        q1 = [(-roots[0]) % ell, 1]
        quot, rem = poly_divmod(coeffs, q1, ell)
        # Check cubic for more roots
        cubic_roots = sum(1 for x in range(ell)
                         if poly_eval_mod(quot, x, ell) == 0)
        if cubic_roots == 0:
            return "1+3"
        elif cubic_roots == 1:
            return "1+1+2"
        else:
            return "1+1+1+1"

    elif len(roots) == 2:
        # Factor out both linear factors, check remainder
        return "1+1+2"

    else:
        return "1+1+1+1"


# ===================================================================
# Load and find candidates
# ===================================================================
def main():
    print("GENUS-2 MOD-3 IRREDUCIBILITY SWEEP")
    print("=" * 72)

    curves = []
    with open("cartography/genus2/data/g2c-data/gce_1000000_lmfdb.txt", "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            conductor = int(parts[1])
            st_group = parts[8]
            euler = parse_good_lfactors(parts[16])
            if euler:
                curves.append({"conductor": conductor, "st": st_group, "euler": euler})

    print(f"Loaded {len(curves)} curves")

    # Deduplicate by isogeny class
    by_conductor = defaultdict(list)
    for c in curves:
        by_conductor[c["conductor"]].append(c)

    conductor_classes = {}
    for cond, crvs in by_conductor.items():
        classes = defaultdict(list)
        common_primes = sorted(set.intersection(*[set(c["euler"].keys()) for c in crvs]))
        for i, c in enumerate(crvs):
            fp = tuple((c["euler"][p][0], c["euler"][p][1]) for p in common_primes)
            classes[fp].append(i)
        reps = []
        for fp, indices in classes.items():
            c = crvs[indices[0]]
            reps.append({"euler": c["euler"], "st": c["st"]})
        conductor_classes[cond] = reps

    # Find mod-3 coprime USp(4) candidates
    candidates = []
    for cond, reps in conductor_classes.items():
        if len(reps) < 2 or cond % 3 == 0:
            continue
        bad = prime_factors(cond)
        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                if reps[i]["st"] != "USp(4)" or reps[j]["st"] != "USp(4)":
                    continue
                e1 = reps[i]["euler"]
                e2 = reps[j]["euler"]
                common = sorted(set(e1.keys()) & set(e2.keys()))
                good = [p for p in common if p not in bad]
                if len(good) < 10:
                    continue
                all_cong = True
                has_nonzero = False
                for p in good:
                    da = e1[p][0] - e2[p][0]
                    db = e1[p][1] - e2[p][1]
                    if da % 3 != 0 or db % 3 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nonzero = True
                if all_cong and has_nonzero:
                    candidates.append({
                        "cond": cond,
                        "euler1": e1,
                        "euler2": e2,
                        "good_primes": good,
                    })

    print(f"Found {len(candidates)} mod-3 coprime USp(4) candidates")
    print()

    # ===================================================================
    # FACTORIZATION SWEEP
    # ===================================================================
    print("FACTORIZATION SWEEP")
    print("-" * 72)
    print()
    print("Checking Frobenius char poly mod 3 at all good primes.")
    print("ONE irreducible char poly = kill shot against reducibility.")
    print()

    n_both_irred = 0
    n_one_irred = 0
    n_both_red = 0
    results = []

    for idx, cand in enumerate(candidates):
        cond = cand["cond"]
        good = cand["good_primes"]

        types_1 = Counter()
        types_2 = Counter()
        irred_w1 = []
        irred_w2 = []

        for p in good:
            a1, b1 = cand["euler1"][p]
            a2, b2 = cand["euler2"][p]

            ft1 = factor_type_mod3(a1, b1, p)
            ft2 = factor_type_mod3(a2, b2, p)

            types_1[ft1] += 1
            types_2[ft2] += 1

            if ft1 == "irreducible":
                irred_w1.append(p)
            if ft2 == "irreducible":
                irred_w2.append(p)

        c1_irred = len(irred_w1) > 0
        c2_irred = len(irred_w2) > 0

        if c1_irred and c2_irred:
            n_both_irred += 1
            status = "BOTH IRREDUCIBLE"
        elif c1_irred or c2_irred:
            n_one_irred += 1
            status = "ONE IRREDUCIBLE"
        else:
            n_both_red += 1
            status = "BOTH REDUCIBLE"

        results.append({
            "cond": cond, "status": status,
            "w1": len(irred_w1), "w2": len(irred_w2),
            "first1": irred_w1[0] if irred_w1 else None,
            "first2": irred_w2[0] if irred_w2 else None,
            "types1": dict(types_1), "types2": dict(types_2),
        })

        w1_str = f"witnesses={len(irred_w1)}" + (f" first=p={irred_w1[0]}" if irred_w1 else "")
        w2_str = f"witnesses={len(irred_w2)}" + (f" first=p={irred_w2[0]}" if irred_w2 else "")
        print(f"{idx+1:2d}. N={cond:<8} {status}")
        print(f"    Curve 1: {dict(types_1)}  {w1_str}")
        print(f"    Curve 2: {dict(types_2)}  {w2_str}")

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"Both curves irreducible mod 3:  {n_both_irred}/42")
    print(f"One curve irreducible:          {n_one_irred}/42")
    print(f"Both curves reducible:          {n_both_red}/42")
    print()
    if n_both_irred > 0:
        print(f"*** {n_both_irred} CANDIDATES HAVE IRREDUCIBLE 4D REPRESENTATIONS ***")
        print("These are genuinely new GSp_4 structure, not GL_2 shadows.")
    if n_both_red > 0:
        print(f"*** {n_both_red} candidates may be GL_2 products (2+2 reducible) ***")
        print("These need further investigation to determine if they are trivial.")


if __name__ == "__main__":
    main()
