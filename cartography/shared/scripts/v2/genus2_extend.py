"""
Genus-2 Extended Point Counting — Push congruence verification from 24 to 300+ primes
=======================================================================================
For each of the 37 irreducible mod-3 candidates, compute a_p (= c1) at extended
primes via direct point counting on the curve equation.

Convention: LMFDB stores c1 = #C(F_p) - p - 1 (negative trace of Frobenius).
"""

import re
import time
from collections import defaultdict
from math import sqrt


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
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def parse_poly(s):
    s = s.strip()
    if not s or s == "0":
        return {}
    coeffs = {}
    s = s.replace("-", "+-")
    terms = [t.strip() for t in s.split("+") if t.strip()]
    for term in terms:
        term = term.strip()
        if "x" not in term:
            coeffs[0] = coeffs.get(0, 0) + int(term)
        elif "^" in term:
            base, exp_str = term.split("^")
            power = int(exp_str)
            base = base.rstrip("x").rstrip("*").strip()
            if base in ("", "+"):
                coeff = 1
            elif base == "-":
                coeff = -1
            else:
                coeff = int(base)
            coeffs[power] = coeffs.get(power, 0) + coeff
        else:
            base = term.rstrip("x").rstrip("*").strip()
            if base in ("", "+"):
                coeff = 1
            elif base == "-":
                coeff = -1
            else:
                coeff = int(base)
            coeffs[1] = coeffs.get(1, 0) + coeff
    return coeffs


def eval_poly_mod(coeffs, x, p):
    val = 0
    for power, coeff in coeffs.items():
        val = (val + coeff * pow(x, power, p)) % p
    return val


def count_affine_points(f_coeffs, h_coeffs, p):
    """Count affine points on y^2 + h(x)*y = f(x) over F_p."""
    if p == 2:
        count = 0
        for x in range(p):
            fv = eval_poly_mod(f_coeffs, x, p)
            hv = eval_poly_mod(h_coeffs, x, p)
            for y in range(p):
                if (y * y + hv * y - fv) % p == 0:
                    count += 1
        return count

    count = 0
    for x in range(p):
        fv = eval_poly_mod(f_coeffs, x, p)
        hv = eval_poly_mod(h_coeffs, x, p)
        disc = (hv * hv + 4 * fv) % p
        if disc == 0:
            count += 1
        else:
            ls = pow(disc, (p - 1) // 2, p)
            if ls == 1:
                count += 2
    return count


def count_infinity_points(f_coeffs, h_coeffs, p):
    """Count points at infinity on the smooth projective model over F_p."""
    deg_f = max(f_coeffs.keys()) if f_coeffs else 0
    deg_h = max(h_coeffs.keys()) if h_coeffs else 0
    eff_deg = max(deg_f, 2 * deg_h)

    if eff_deg % 2 == 1:
        return 1  # Odd degree: one point at infinity (Weierstrass)

    # Even degree: depends on whether leading coeff of 4f + h^2 is a square
    # Compute leading coefficient of g(x) = 4*f(x) + h(x)^2 at degree eff_deg
    # For most curves in our dataset, this is a perfect square -> 2 points
    # Compute exactly:
    lead_4f = 4 * f_coeffs.get(eff_deg, 0)
    # h^2 at degree eff_deg: sum h_i * h_j where i+j = eff_deg
    lead_h2 = 0
    for i, ci in h_coeffs.items():
        j = eff_deg - i
        if j in h_coeffs:
            lead_h2 += ci * h_coeffs[j]

    lead_g = lead_4f + lead_h2
    if lead_g == 0:
        return 0  # Degenerate case

    if p == 2:
        # Special handling
        return 2 if lead_g % 2 == 0 or True else 0  # Simplified

    ls = pow(lead_g % p, (p - 1) // 2, p) if lead_g % p != 0 else 0
    if ls == 0:
        return 1  # Tangent at infinity
    elif ls == 1:
        return 2
    else:
        return 0


def compute_c1(f_coeffs, h_coeffs, p):
    """Compute c1 = #C(F_p) - p - 1 (LMFDB convention)."""
    affine = count_affine_points(f_coeffs, h_coeffs, p)
    inf = count_infinity_points(f_coeffs, h_coeffs, p)
    return affine + inf - p - 1


def main():
    print("GENUS-2 EXTENDED POINT COUNTING")
    print("=" * 72)

    # Load ALL curves with equations
    all_data = []
    with open("cartography/genus2/data/g2c-data/gce_1000000_lmfdb.txt", "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            conductor = int(parts[1])
            st = parts[8]
            eqn_inner = parts[3].strip("[]")
            eqn_parts = eqn_inner.split(",")
            f_str = eqn_parts[0].strip()
            h_str = eqn_parts[1].strip() if len(eqn_parts) > 1 else "0"
            euler_matches = re.findall(r"\[(-?\d+),(-?\d+),(-?\d+)\]", parts[16])
            euler = {int(m[0]): (int(m[1]), int(m[2])) for m in euler_matches}

            all_data.append({
                "conductor": conductor, "st": st,
                "f_str": f_str, "h_str": h_str, "euler": euler,
            })

    print(f"Loaded {len(all_data)} curves")

    by_cond = defaultdict(list)
    for d in all_data:
        by_cond[d["conductor"]].append(d)

    # The 37 irreducible conductors
    irred_conds = [
        1844, 2348, 3572, 4304, 5497, 7945, 9664, 14155, 19201, 20432,
        20560, 21611, 31312, 32119, 32575, 36265, 43276, 50173, 50608,
        69422, 77608, 83776, 88765, 96347, 114437, 124712, 141538, 142265,
        155305, 173936, 195337, 216677, 232912, 235237, 342871, 600953, 745517,
    ]

    primes_extended = sieve_primes(1000)
    ell = 3

    print(f"\nExtending c1 verification to {len(primes_extended)} primes (up to 1000)")
    print(f"Checking mod-{ell} congruence on a_p component")
    print()

    results = []

    for ci, cond in enumerate(irred_conds):
        curves = [d for d in by_cond[cond] if d["st"] == "USp(4)"]
        bad = prime_factors(cond)
        if cond % 3 == 0:
            continue

        # Deduplicate by Euler fingerprint
        classes = defaultdict(list)
        for curve in curves:
            primes_avail = sorted(curve["euler"].keys())
            fp = tuple(curve["euler"][p] for p in primes_avail[:20])
            classes[fp].append(curve)

        class_list = list(classes.values())
        if len(class_list) < 2:
            continue

        # Find the mod-3 congruent pair
        for i in range(len(class_list)):
            for j in range(i + 1, len(class_list)):
                c1_curve = class_list[i][0]
                c2_curve = class_list[j][0]
                common = sorted(set(c1_curve["euler"].keys()) & set(c2_curve["euler"].keys()))
                good_known = [p for p in common if p not in bad]

                all_cong = True
                has_nz = False
                for p in good_known:
                    da = c1_curve["euler"][p][0] - c2_curve["euler"][p][0]
                    db = c1_curve["euler"][p][1] - c2_curve["euler"][p][1]
                    if da % 3 != 0 or db % 3 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True

                if not (all_cong and has_nz):
                    continue

                # Parse curve equations
                f1 = parse_poly(c1_curve["f_str"])
                h1 = parse_poly(c1_curve["h_str"])
                f2 = parse_poly(c2_curve["f_str"])
                h2 = parse_poly(c2_curve["h_str"])

                # Verify known c1 values
                verified = 0
                for p in good_known[:5]:
                    if p in bad or p == 2:
                        continue
                    c1_comp = compute_c1(f1, h1, p)
                    c1_known = c1_curve["euler"][p][0]
                    if c1_comp == c1_known:
                        verified += 1

                # Extended check: primes beyond stored data
                extended_primes = [p for p in primes_extended
                                   if p not in bad and p != 3 and p > 97]

                t0 = time.time()
                pass_c = 0
                fail_c = 0
                for p in extended_primes:
                    c1_1 = compute_c1(f1, h1, p)
                    c1_2 = compute_c1(f2, h2, p)
                    da = c1_1 - c1_2
                    if da % ell != 0:
                        fail_c += 1
                    else:
                        pass_c += 1
                t1 = time.time()

                total_ext = pass_c + fail_c
                total_all = len(good_known) + total_ext
                status = "PASS" if fail_c == 0 else f"FAIL({fail_c})"

                print(f"{ci+1:2d}. N={cond:<8} known={len(good_known)} "
                      f"verified={verified}/5  "
                      f"extended={pass_c}/{total_ext} {status}  "
                      f"total_primes={total_all}  "
                      f"({t1-t0:.1f}s)")

                results.append({
                    "cond": cond,
                    "known_primes": len(good_known),
                    "extended_primes": total_ext,
                    "extended_pass": pass_c,
                    "extended_fail": fail_c,
                    "total_primes": total_all,
                    "time": t1 - t0,
                })
                break
            else:
                continue
            break

    print()
    print("=" * 72)
    n_pass = sum(1 for r in results if r["extended_fail"] == 0)
    n_fail = sum(1 for r in results if r["extended_fail"] > 0)
    print(f"SUMMARY: {n_pass} pass extended c1 check, {n_fail} fail")
    if n_pass > 0:
        avg_primes = sum(r["total_primes"] for r in results if r["extended_fail"] == 0) / n_pass
        print(f"Average total primes verified: {avg_primes:.0f}")
        print(f"Random probability at {avg_primes:.0f} primes (c1 only): "
              f"(1/3)^{avg_primes:.0f} ~ 10^{-avg_primes*0.477:.0f}")


if __name__ == "__main__":
    main()
