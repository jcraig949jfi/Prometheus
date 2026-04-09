"""
Genus-2 c2 (b_p) Extension via F_{p^2} Point Counting
=======================================================
Extends b_p verification from ~24 primes (LMFDB stored) to ~95 primes (up to p=500).

Key formula:
  #C(F_{p^2}) = p^2 + 1 - sum(alpha_i^2)
  sum(alpha_i^2) = c1^2 - 2*c2
  => c2 = (c1^2 - #C(F_{p^2}) + p^2 + 1) / 2

Where c1 = #C(F_p) - p - 1 (already verified at 166 primes).

F_{p^2} arithmetic: represent elements as (a, b) with a + b*omega,
where omega^2 = g for some non-residue g mod p.

Usage:
    python genus2_c2_extend.py
    python genus2_c2_extend.py --max-prime 300
    python genus2_c2_extend.py --conductors 1844 2348
"""

import re
import sys
import time
import json
import argparse
from collections import defaultdict
from math import sqrt
from pathlib import Path


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


def find_non_residue(p):
    """Find the smallest quadratic non-residue mod p."""
    for g in range(2, p):
        if pow(g, (p - 1) // 2, p) != 1:
            return g
    return None


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


# ─────────────────────────────────────────────────────────────────────────────
# F_{p^2} arithmetic
# ─────────────────────────────────────────────────────────────────────────────

class Fp2:
    """Element of F_{p^2} = F_p[omega] / (omega^2 - g) where g is a non-residue."""
    __slots__ = ('a', 'b', 'p', 'g')

    def __init__(self, a, b, p, g):
        self.a = a % p
        self.b = b % p
        self.p = p
        self.g = g

    def __add__(self, other):
        return Fp2((self.a + other.a) % self.p, (self.b + other.b) % self.p, self.p, self.g)

    def __sub__(self, other):
        return Fp2((self.a - other.a) % self.p, (self.b - other.b) % self.p, self.p, self.g)

    def __mul__(self, other):
        # (a1 + b1*w)(a2 + b2*w) = (a1*a2 + g*b1*b2) + (a1*b2 + a2*b1)*w
        p = self.p
        return Fp2(
            (self.a * other.a + self.g * self.b * other.b) % p,
            (self.a * other.b + self.b * other.a) % p,
            p, self.g
        )

    def __pow__(self, n):
        if n == 0:
            return Fp2(1, 0, self.p, self.g)
        if n == 1:
            return self
        result = Fp2(1, 0, self.p, self.g)
        base = self
        while n > 0:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1
        return result

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def is_square(self):
        """Check if element is a square in F_{p^2}. Uses Euler criterion."""
        if self.is_zero():
            return True
        # Element z is a square in F_{p^2}* iff z^{(p^2-1)/2} = 1
        exp = (self.p * self.p - 1) // 2
        result = self ** exp
        return result.a == 1 and result.b == 0

    def norm(self):
        """Norm to F_p: N(a + b*w) = a^2 - g*b^2."""
        return (self.a * self.a - self.g * self.b * self.b) % self.p


def eval_poly_fp2(coeffs_dict, x, p, g):
    """Evaluate polynomial at x in F_{p^2}."""
    if not coeffs_dict:
        return Fp2(0, 0, p, g)
    result = Fp2(0, 0, p, g)
    for power, coeff in coeffs_dict.items():
        c_fp2 = Fp2(coeff % p, 0, p, g)
        x_pow = x ** power
        result = result + c_fp2 * x_pow
    return result


def count_fp2_points(f_coeffs, h_coeffs, p, g):
    """
    Count points on y^2 + h(x)*y = f(x) over F_{p^2}.

    For each x in F_{p^2}, compute disc = h(x)^2 + 4*f(x).
    If disc = 0: 1 solution for y
    If disc is a nonzero square: 2 solutions for y
    If disc is a non-square: 0 solutions for y

    Returns total affine points.
    """
    count = 0
    four = Fp2(4, 0, p, g)

    # Iterate over all x in F_{p^2}
    for a in range(p):
        for b in range(p):
            x = Fp2(a, b, p, g)
            fv = eval_poly_fp2(f_coeffs, x, p, g)
            hv = eval_poly_fp2(h_coeffs, x, p, g)
            disc = hv * hv + four * fv

            if disc.is_zero():
                count += 1
            elif disc.is_square():
                count += 2

    return count


def count_fp2_infinity(f_coeffs, h_coeffs, p, g):
    """Count points at infinity over F_{p^2}."""
    deg_f = max(f_coeffs.keys()) if f_coeffs else 0
    deg_h = max(h_coeffs.keys()) if h_coeffs else 0
    eff_deg = max(deg_f, 2 * deg_h)

    if eff_deg % 2 == 1:
        return 1

    # Leading coefficient of 4f + h^2 at degree eff_deg
    lead_4f = 4 * f_coeffs.get(eff_deg, 0)
    lead_h2 = 0
    for i, ci in h_coeffs.items():
        j = eff_deg - i
        if j in h_coeffs:
            lead_h2 += ci * h_coeffs[j]
    lead_g_val = lead_4f + lead_h2

    if lead_g_val == 0:
        return 0

    # Check if leading coeff is a square in F_{p^2}
    lv = Fp2(lead_g_val % p, 0, p, g)
    if lv.is_zero():
        return 1
    elif lv.is_square():
        return 2
    else:
        return 0


def count_fp_points(f_coeffs, h_coeffs, p):
    """Count affine points over F_p (fast, no F_{p^2} needed)."""
    count = 0
    for x in range(p):
        fv = 0
        for power, coeff in f_coeffs.items():
            fv = (fv + coeff * pow(x, power, p)) % p
        hv = 0
        for power, coeff in h_coeffs.items():
            hv = (hv + coeff * pow(x, power, p)) % p
        disc = (hv * hv + 4 * fv) % p
        if disc == 0:
            count += 1
        elif pow(disc, (p - 1) // 2, p) == 1:
            count += 2
    return count


def count_fp_infinity(f_coeffs, h_coeffs, p):
    deg_f = max(f_coeffs.keys()) if f_coeffs else 0
    deg_h = max(h_coeffs.keys()) if h_coeffs else 0
    eff_deg = max(deg_f, 2 * deg_h)
    if eff_deg % 2 == 1:
        return 1
    lead_4f = 4 * f_coeffs.get(eff_deg, 0)
    lead_h2 = 0
    for i, ci in h_coeffs.items():
        j = eff_deg - i
        if j in h_coeffs:
            lead_h2 += ci * h_coeffs[j]
    lead_g_val = lead_4f + lead_h2
    if lead_g_val == 0:
        return 0
    if p == 2:
        return 2
    ls = pow(lead_g_val % p, (p - 1) // 2, p) if lead_g_val % p != 0 else 0
    if ls == 0:
        return 1
    elif ls == 1:
        return 2
    else:
        return 0


def compute_c1(f_coeffs, h_coeffs, p):
    """c1 = #C(F_p) - p - 1"""
    affine = count_fp_points(f_coeffs, h_coeffs, p)
    inf = count_fp_infinity(f_coeffs, h_coeffs, p)
    return affine + inf - p - 1


def compute_c2_from_fp2(f_coeffs, h_coeffs, p, g, c1):
    """
    Compute c2 from F_{p^2} point count.

    c2 = (c1^2 - #C(F_{p^2}) + p^2 + 1) / 2
    """
    affine_fp2 = count_fp2_points(f_coeffs, h_coeffs, p, g)
    inf_fp2 = count_fp2_infinity(f_coeffs, h_coeffs, p, g)
    n_fp2 = affine_fp2 + inf_fp2

    numerator = c1 * c1 + n_fp2 - p * p - 1
    if numerator % 2 != 0:
        return None, n_fp2  # Error: should always be even
    c2 = numerator // 2
    return c2, n_fp2


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=500,
                        help="Maximum prime for F_{p^2} computation")
    parser.add_argument("--conductors", type=int, nargs="*", default=None,
                        help="Specific conductors to test (default: all 37)")
    parser.add_argument("--verify-first", type=int, default=5,
                        help="Number of known primes to verify before extending")
    args = parser.parse_args()

    data_path = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"

    print("GENUS-2 c2 (b_p) EXTENSION VIA F_{p^2} POINT COUNTING")
    print("=" * 72)
    print(f"Max prime: {args.max_prime}")
    print(f"Formula: c2 = (c1^2 - #C(F_p^2) + p^2 + 1) / 2")
    print()

    # Load ALL curves with equations
    all_data = []
    with open(data_path, "r") as f:
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

    irred_conds = [
        1844, 2348, 3572, 4304, 5497, 7945, 9664, 14155, 19201, 20432,
        20560, 21611, 31312, 32119, 32575, 36265, 43276, 50173, 50608,
        69422, 77608, 83776, 88765, 96347, 114437, 124712, 141538, 142265,
        155305, 173936, 195337, 216677, 232912, 235237, 342871, 600953, 745517,
    ]

    if args.conductors:
        irred_conds = [c for c in irred_conds if c in args.conductors]

    all_primes = sieve_primes(args.max_prime)
    ell = 3

    print(f"Testing {len(irred_conds)} conductors at primes up to {args.max_prime}")
    print(f"F_{{p^2}} computation: O(p^2) per prime")
    print()

    results = []
    total_start = time.time()

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
        found_pair = None
        for i in range(len(class_list)):
            if found_pair:
                break
            for j in range(i + 1, len(class_list)):
                c1_curve = class_list[i][0]
                c2_curve = class_list[j][0]
                common = sorted(set(c1_curve["euler"].keys()) & set(c2_curve["euler"].keys()))
                good_known = [p for p in common if p not in bad and p != 3]

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

                if all_cong and has_nz:
                    found_pair = (c1_curve, c2_curve, good_known)
                    break

        if not found_pair:
            continue

        c1_curve, c2_curve, good_known = found_pair
        f1 = parse_poly(c1_curve["f_str"])
        h1 = parse_poly(c1_curve["h_str"])
        f2 = parse_poly(c2_curve["f_str"])
        h2 = parse_poly(c2_curve["h_str"])

        # Step 1: Verify c1 and c2 at known primes
        verified_c1 = 0
        verified_c2 = 0
        for p in good_known[:args.verify_first]:
            if p in bad or p == 2 or p == 3:
                continue

            g = find_non_residue(p)
            if g is None:
                continue

            # Verify c1
            c1_comp = compute_c1(f1, h1, p)
            c1_known = c1_curve["euler"][p][0]
            if c1_comp == c1_known:
                verified_c1 += 1

            # Verify c2
            c2_comp, _ = compute_c2_from_fp2(f1, h1, p, g, c1_comp)
            c2_known = c1_curve["euler"][p][1]
            if c2_comp == c2_known:
                verified_c2 += 1

        if verified_c2 < 2:
            print(f"  *** N={cond}: c2 verification FAILED "
                  f"(only {verified_c2}/{args.verify_first} match). SKIPPING. ***")
            continue

        # Step 2: Extend to new primes
        extended_primes = [p for p in all_primes
                           if p not in bad and p != 3 and p > 97]

        t0 = time.time()
        pass_c1 = 0
        pass_c2 = 0
        fail_c1 = 0
        fail_c2 = 0
        tested = 0

        for p in extended_primes:
            g = find_non_residue(p)
            if g is None:
                continue

            # c1 for both curves (fast, O(p))
            c1_1 = compute_c1(f1, h1, p)
            c1_2 = compute_c1(f2, h2, p)
            da_c1 = c1_1 - c1_2

            if da_c1 % ell != 0:
                fail_c1 += 1
                tested += 1
                continue
            pass_c1 += 1

            # c2 for both curves (slow, O(p^2))
            c2_1, _ = compute_c2_from_fp2(f1, h1, p, g, c1_1)
            c2_2, _ = compute_c2_from_fp2(f2, h2, p, g, c1_2)

            if c2_1 is None or c2_2 is None:
                fail_c2 += 1
                tested += 1
                continue

            da_c2 = c2_1 - c2_2
            if da_c2 % ell != 0:
                fail_c2 += 1
            else:
                pass_c2 += 1
            tested += 1

            # Progress for slow primes
            if p > 200 and tested % 10 == 0:
                elapsed = time.time() - t0
                print(f"    N={cond}: p={p}, tested={tested}, "
                      f"c1_pass={pass_c1}, c2_pass={pass_c2}, "
                      f"c2_fail={fail_c2}, {elapsed:.1f}s", flush=True)

        t1 = time.time()
        total_primes = len(good_known) + tested

        c1_status = "PASS" if fail_c1 == 0 else f"FAIL({fail_c1})"
        c2_status = "PASS" if fail_c2 == 0 else f"FAIL({fail_c2})"
        combined = "PASS" if fail_c1 == 0 and fail_c2 == 0 else "FAIL"

        print(f"{ci+1:2d}. N={cond:<8} verified_c2={verified_c2}/{args.verify_first}  "
              f"c1: {pass_c1}/{tested} {c1_status}  "
              f"c2: {pass_c2}/{tested} {c2_status}  "
              f"total={total_primes}  {combined}  ({t1-t0:.1f}s)")

        prob_c1 = tested * 0.477 if fail_c1 == 0 else 0
        prob_c2 = pass_c2 * 0.477 if fail_c2 == 0 else 0

        results.append({
            "conductor": cond,
            "known_primes": len(good_known),
            "extended_tested": tested,
            "c1_pass": pass_c1,
            "c1_fail": fail_c1,
            "c2_pass": pass_c2,
            "c2_fail": fail_c2,
            "total_primes": total_primes,
            "time_seconds": t1 - t0,
            "random_prob_c1": f"10^-{prob_c1:.0f}",
            "random_prob_c2": f"10^-{prob_c2:.0f}",
        })

    total_time = time.time() - total_start
    print()
    print("=" * 72)
    n_full_pass = sum(1 for r in results if r["c1_fail"] == 0 and r["c2_fail"] == 0)
    n_c1_fail = sum(1 for r in results if r["c1_fail"] > 0)
    n_c2_fail = sum(1 for r in results if r["c2_fail"] > 0)
    print(f"SUMMARY: {n_full_pass} full pass (c1+c2), "
          f"{n_c1_fail} c1 fail, {n_c2_fail} c2 fail")
    print(f"Total time: {total_time:.0f}s ({total_time/60:.1f}min)")

    if n_full_pass > 0:
        avg_c2 = sum(r["c2_pass"] for r in results if r["c2_fail"] == 0) / n_full_pass
        print(f"Average c2 primes verified: {avg_c2:.0f}")
        print(f"Random probability (c2 only): (1/3)^{avg_c2:.0f} ~ 10^{-avg_c2*0.477:.0f}")
        avg_total = sum(r["total_primes"] for r in results if r["c2_fail"] == 0) / n_full_pass
        print(f"Combined (c1+c2) at {avg_total:.0f} avg primes: "
              f"(1/9)^{avg_total:.0f} ~ 10^{-avg_total*0.954:.0f}")

    # Save
    out_path = Path(__file__).parent / "genus2_c2_extend_results.json"
    with open(out_path, "w") as f:
        json.dump({"results": results, "total_time_s": total_time}, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
