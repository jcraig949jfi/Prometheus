"""
Lattice Genus Theory Verification for dim=2 binary quadratic forms.

For a lattice with Gram matrix [[a,b],[b,c]], the associated quadratic form is
Q(x,y) = ax^2 + 2bxy + cy^2, with discriminant D = 4b^2 - 4ac = -4*det(Gram).

Genus theory (Gauss): for fundamental discriminant D0 < 0,
  number_of_genera = 2^{omega(|D0|) - 1}
where omega counts the number of distinct prime divisors of |D0|.

The class number h(D0) must be divisible by the number of genera.
Equivalently, the 2-rank of the class group >= omega(|D0|) - 1.

This script:
1. Loads dim=2 lattices from LMFDB
2. Computes primitive and fundamental discriminants from Gram matrices
3. Groups forms by fundamental discriminant
4. Verifies divisibility: h(D) mod 2^{omega-1} = 0
5. Computes genus characters to count genera independently
6. Compares predicted vs actual 2-rank
"""

import json
import math
from collections import defaultdict, Counter
from pathlib import Path


def factorize(n):
    """Return dict of {prime: exponent} for positive integer n."""
    if n <= 0:
        raise ValueError(f"factorize expects positive int, got {n}")
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = 1
    return factors


def omega(n):
    """Number of distinct prime divisors of n."""
    return len(factorize(n))


def is_squarefree(n):
    """Check if n is squarefree."""
    return all(e == 1 for e in factorize(n).values())


def _is_fundamental_disc(D):
    """Check if D < 0 is a fundamental discriminant."""
    if D >= 0:
        return False
    abs_D = abs(D)
    if abs_D % 4 == 3:
        return is_squarefree(abs_D)
    elif abs_D % 4 == 0:
        m = abs_D // 4
        if not is_squarefree(m):
            return False
        return m % 4 in [1, 2]
    return False


def fundamental_discriminant(D):
    """
    Given negative discriminant D, return (D0, f) where D0 is fundamental
    and D = D0 * f^2.
    """
    abs_D = abs(D)
    for ff in range(int(math.isqrt(abs_D)), 0, -1):
        if abs_D % (ff * ff) != 0:
            continue
        cand = -(abs_D // (ff * ff))
        if _is_fundamental_disc(cand):
            return cand, ff
    return D, 1


def v2(n):
    """2-adic valuation of n."""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    return count


def kronecker_symbol(a, p):
    """Compute the Kronecker/Legendre symbol (a/p) for odd prime p."""
    a = a % p
    if a == 0:
        return 0
    if p == 2:
        return 0  # shouldn't be called with p=2
    # Euler's criterion
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1


def genus_characters(gram, D):
    """
    Compute the genus character vector for a binary quadratic form.
    The form Q(x,y) = ax^2 + 2bxy + cy^2 with Gram [[a,b],[b,c]].

    For discriminant D < 0, the genus characters are determined by
    which values coprime to D the form represents.

    Returns a tuple of +1/-1 values (one per odd prime dividing D,
    plus 2-adic characters if needed).
    """
    a, b, c = gram[0][0], gram[0][1], gram[1][1]
    abs_D = abs(D)
    primes = sorted(factorize(abs_D).keys())

    # Find a value n represented by the form, coprime to D
    # Q(x,y) = ax^2 + 2bxy + cy^2
    n = None
    for x in range(100):
        for y in range(100):
            if x == 0 and y == 0:
                continue
            val = a * x * x + 2 * b * x * y + c * y * y
            if val > 0 and math.gcd(val, abs_D) == 1:
                n = val
                break
        if n is not None:
            break

    if n is None:
        return None  # shouldn't happen for small forms

    # Compute Kronecker symbols (D/n) but we want (n/p) for each p|D
    chars = []
    for p in primes:
        if p == 2:
            # 2-adic character: (-1)^((n^2-1)/8) or (-1)^((n-1)/2) depending
            # For D divisible by 4: character is (-1)^((n-1)/2) if 4||D,
            # or both (-1)^((n-1)/2) and (-1)^((n^2-1)/8) if 8|D
            v = v2(abs_D)
            if v == 2:
                # One character: (-1)^((n-1)/2)
                chars.append((-1) ** ((n - 1) // 2))
            elif v == 3:
                # One character: (-1)^((n^2-1)/8)
                chars.append((-1) ** ((n * n - 1) // 8))
            elif v >= 4:
                # Two characters
                chars.append((-1) ** ((n - 1) // 2))
                chars.append((-1) ** ((n * n - 1) // 8))
        else:
            chars.append(kronecker_symbol(n, p))

    return tuple(chars)


def compute_disc_from_gram(gram):
    """From Gram matrix [[a,b],[b,c]], compute discriminant and primitive disc."""
    a, b, c = gram[0][0], gram[0][1], gram[1][1]
    D = 4 * b * b - 4 * a * c
    content = math.gcd(math.gcd(a, 2 * abs(b)), c)
    D_prim = D // (content * content)
    return D, content, D_prim


def main():
    data_path = Path("F:/Prometheus/cartography/lmfdb_dump/lat_lattices.json")
    with open(data_path) as f:
        data = json.load(f)

    records = data["records"]
    dim2 = [r for r in records if r["dim"] == 2]
    print(f"Total dim=2 lattices: {len(dim2)}")

    # Compute discriminants and group by fundamental discriminant
    fund_disc_records = defaultdict(list)

    for r in dim2:
        D, content, D_prim = compute_disc_from_gram(r["gram"])
        D0, conductor = fundamental_discriminant(D_prim)
        r["_D"] = D
        r["_content"] = content
        r["_D_prim"] = D_prim
        r["_D0"] = D0
        r["_conductor"] = conductor
        if conductor == 1:  # Only fundamental discriminants for clean genus theory
            fund_disc_records[D0].append(r)

    print(f"Distinct fundamental discriminants with lattice data: {len(fund_disc_records)}")

    # For each fundamental discriminant, verify genus theory
    results = []
    pass_div = 0
    fail_div = 0
    incomplete = 0
    pass_genera_exact = 0
    fail_genera_exact = 0
    violations = []

    for D0 in sorted(fund_disc_records.keys(), key=lambda x: abs(x)):
        entries = fund_disc_records[D0]
        h_obs = len(entries)
        abs_D0 = abs(D0)
        t = omega(abs_D0)
        predicted_genera = 2 ** (t - 1) if t > 0 else 1

        # Compute genus characters for each form to count actual genera
        genus_char_set = set()
        for e in entries:
            gc = genus_characters(e["gram"], D0)
            if gc is not None:
                genus_char_set.add(gc)

        computed_genera = len(genus_char_set)

        # Check divisibility
        is_complete = h_obs >= predicted_genera
        div_ok = (h_obs % predicted_genera == 0)
        gen_exact = (computed_genera == predicted_genera)

        if div_ok:
            pass_div += 1
        else:
            fail_div += 1
            if not is_complete:
                incomplete += 1

        if gen_exact:
            pass_genera_exact += 1
        else:
            fail_genera_exact += 1

        predicted_2rank = max(t - 1, 0)
        actual_2rank = v2(h_obs) if h_obs > 0 else 0

        result = {
            "D0": D0,
            "abs_D0": abs_D0,
            "omega": t,
            "predicted_genera": predicted_genera,
            "computed_genera_from_chars": computed_genera,
            "h_observed": h_obs,
            "divisibility_pass": div_ok,
            "genera_exact_match": gen_exact,
            "predicted_2rank_lb": predicted_2rank,
            "actual_2rank_h": actual_2rank,
            "bound_satisfied": actual_2rank >= predicted_2rank,
            "likely_incomplete": not is_complete
        }
        results.append(result)

        if is_complete and not div_ok:
            violations.append(result)

    total = len(results)
    complete = [r for r in results if not r["likely_incomplete"]]
    n_complete = len(complete)

    div_rate_all = pass_div / total if total > 0 else 0
    complete_div_pass = sum(1 for r in complete if r["divisibility_pass"])
    complete_div_rate = complete_div_pass / n_complete if n_complete > 0 else 0

    complete_gen_pass = sum(1 for r in complete if r["genera_exact_match"])
    complete_gen_rate = complete_gen_pass / n_complete if n_complete > 0 else 0

    complete_bound_pass = sum(1 for r in complete if r["bound_satisfied"])
    complete_bound_rate = complete_bound_pass / n_complete if n_complete > 0 else 0

    # 2-rank excess distribution (complete only)
    rank_diff = Counter()
    for r in complete:
        diff = r["actual_2rank_h"] - r["predicted_2rank_lb"]
        rank_diff[diff] += 1

    # Genera distribution
    pred_gen_dist = Counter(r["predicted_genera"] for r in results)

    # Print
    print(f"\n{'='*65}")
    print(f"GENUS THEORY VERIFICATION (dim=2, fundamental discriminants)")
    print(f"{'='*65}")
    print(f"Total fundamental discriminants: {total}")
    print(f"LMFDB-complete (h_obs >= predicted genera): {n_complete}")
    print(f"LMFDB-incomplete (partial coverage): {total - n_complete}")

    print(f"\n--- DIVISIBILITY: h(D) mod 2^(omega-1) = 0 ---")
    print(f"  All discriminants:  {pass_div}/{total} pass ({div_rate_all:.2%})")
    print(f"  Complete only:      {complete_div_pass}/{n_complete} pass ({complete_div_rate:.2%})")

    print(f"\n--- GENERA COUNT: computed genera == 2^(omega-1) ---")
    print(f"  All discriminants:  {pass_genera_exact}/{total} pass")
    print(f"  Complete only:      {complete_gen_pass}/{n_complete} pass ({complete_gen_rate:.2%})")

    print(f"\n--- 2-RANK BOUND: v_2(h) >= omega-1 ---")
    print(f"  All discriminants:  {sum(1 for r in results if r['bound_satisfied'])}/{total}")
    print(f"  Complete only:      {complete_bound_pass}/{n_complete} pass ({complete_bound_rate:.2%})")

    print(f"\n--- 2-RANK EXCESS (complete entries) ---")
    for diff, count in sorted(rank_diff.items()):
        pct = count / n_complete * 100 if n_complete else 0
        print(f"  excess={diff}: {count} ({pct:.1f}%)")

    print(f"\n--- PREDICTED GENERA DISTRIBUTION ---")
    for g, count in sorted(pred_gen_dist.items()):
        print(f"  2^{int(math.log2(g))} = {g} genera: {count} discriminants")

    if violations:
        print(f"\n--- VIOLATIONS (complete, failing divisibility) ---")
        for v in violations[:10]:
            print(f"  D0={v['D0']}: h={v['h_observed']}, genera={v['predicted_genera']}, "
                  f"h mod genera = {v['h_observed'] % v['predicted_genera']}")
    else:
        print(f"\n*** ZERO VIOLATIONS: Genus theory holds for all {n_complete} complete entries ***")

    # Show interesting examples
    print(f"\n--- SAMPLE RESULTS (complete, h > 1) ---")
    interesting = [r for r in complete if r["h_observed"] > 1]
    for r in interesting[:20]:
        print(f"  D0={r['D0']}: omega={r['omega']}, genera(pred)={r['predicted_genera']}, "
              f"genera(char)={r['computed_genera_from_chars']}, h={r['h_observed']}, "
              f"2-rank={r['actual_2rank_h']}>={r['predicted_2rank_lb']}")

    # Save
    summary = {
        "dataset": "LMFDB lat_lattices, dim=2",
        "total_dim2_lattices": len(dim2),
        "distinct_fundamental_discriminants": total,
        "lmfdb_complete": n_complete,
        "lmfdb_incomplete": total - n_complete,
        "formula": "genera = 2^{omega(|D0|) - 1}, D0 = fundamental discriminant",
        "divisibility_test": {
            "description": "h(D0) divisible by 2^{omega(|D0|)-1}",
            "all_pass": pass_div,
            "all_total": total,
            "all_rate": round(div_rate_all, 6),
            "complete_pass": complete_div_pass,
            "complete_total": n_complete,
            "complete_rate": round(complete_div_rate, 6)
        },
        "genera_exact_test": {
            "description": "Number of distinct genus characters == predicted genera",
            "complete_pass": complete_gen_pass,
            "complete_total": n_complete,
            "complete_rate": round(complete_gen_rate, 6)
        },
        "two_rank_bound_test": {
            "description": "v_2(h) >= omega(|D0|) - 1",
            "complete_pass": complete_bound_pass,
            "complete_total": n_complete,
            "complete_rate": round(complete_bound_rate, 6)
        },
        "two_rank_excess_distribution": {
            str(k): v for k, v in sorted(rank_diff.items())
        },
        "predicted_genera_distribution": {
            str(k): v for k, v in sorted(pred_gen_dist.items())
        },
        "violations": [
            {"D0": v["D0"], "h": v["h_observed"], "predicted_genera": v["predicted_genera"]}
            for v in violations
        ],
        "all_results": results
    }

    out_path = Path("F:/Prometheus/cartography/v2/lattice_genus_theory_results.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
