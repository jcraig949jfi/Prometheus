"""
Genus-2 c2 (b_p) Extension — FAST version using norm-based square detection
=============================================================================
Key optimization: z is a square in F_{p^2} iff N(z) = a^2 - g*b^2 is a square in F_p.
This replaces O(log p) F_{p^2} multiplications with 3 F_p multiplications per element.

Formula: c2 = (c1^2 + #C(F_{p^2}) - p^2 - 1) / 2

Usage:
    python genus2_c2_fast.py
    python genus2_c2_fast.py --max-prime 500
"""

import re
import time
import json
import argparse
from collections import defaultdict
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
# Fast F_{p^2} point counting using norm-based square detection
# ─────────────────────────────────────────────────────────────────────────────

def fp2_mul(a, b, p, g):
    """Multiply two F_{p^2} elements (tuples)."""
    return ((a[0]*b[0] + g*a[1]*b[1]) % p, (a[0]*b[1] + a[1]*b[0]) % p)


def fp2_add(a, b, p):
    return ((a[0]+b[0]) % p, (a[1]+b[1]) % p)


def fp2_pow_val(x, coeffs_items, p, g):
    """Evaluate polynomial with integer coefficients at x in F_{p^2}.
    coeffs_items: list of (power, coeff) pairs.
    """
    result = (0, 0)
    for power, coeff in coeffs_items:
        if coeff == 0:
            continue
        # x^power via repeated squaring
        if power == 0:
            xp = (1, 0)
        else:
            xp = (1, 0)
            base = x
            n = power
            while n > 0:
                if n & 1:
                    xp = fp2_mul(xp, base, p, g)
                base = fp2_mul(base, base, p, g)
                n >>= 1
        c_mod = coeff % p
        term = (c_mod * xp[0] % p, c_mod * xp[1] % p)
        result = fp2_add(result, term, p)
    return result


def eval_poly_fp2_fast(coeffs_dict, x, p, g):
    """Evaluate polynomial at x in F_{p^2} using Horner's method."""
    if not coeffs_dict:
        return (0, 0)
    max_deg = max(coeffs_dict.keys())
    # Horner: start from highest degree
    result = (coeffs_dict.get(max_deg, 0) % p, 0)
    for d in range(max_deg - 1, -1, -1):
        result = fp2_mul(result, x, p, g)
        c = coeffs_dict.get(d, 0) % p
        result = ((result[0] + c) % p, result[1])
    return result


def count_fp2_affine_fast(f_coeffs, h_coeffs, p, g):
    """
    Count affine points on y^2 + h(x)*y = f(x) over F_{p^2}.
    Uses norm trick: disc = (da, db) is a square in F_{p^2} iff
    N(disc) = da^2 - g*db^2 is a square in F_p.
    """
    count = 0
    # Precompute Legendre symbol table for F_p
    # ls[x] = 1 if x is QR, -1 if NQR, 0 if 0
    ls = [0] * p
    for x in range(1, p):
        ls[x] = 1 if pow(x, (p - 1) // 2, p) == 1 else -1

    for a in range(p):
        for b in range(p):
            x = (a, b)
            fv = eval_poly_fp2_fast(f_coeffs, x, p, g)
            hv = eval_poly_fp2_fast(h_coeffs, x, p, g)

            # disc = h^2 + 4f in F_{p^2}
            h2 = fp2_mul(hv, hv, p, g)
            f4 = ((4 * fv[0]) % p, (4 * fv[1]) % p)
            disc = fp2_add(h2, f4, p)

            da, db = disc
            if da == 0 and db == 0:
                count += 1  # disc = 0: one solution
            else:
                # Norm: N(disc) = da^2 - g*db^2 mod p
                norm = (da * da - g * db * db) % p
                if norm == 0:
                    # Norm is 0 but disc != 0 means disc is a zero divisor?
                    # No: in F_{p^2} there are no zero divisors. If norm=0
                    # and disc != 0, then... actually this can't happen.
                    # N(z) = z * z^p. If N(z) = 0, then z = 0.
                    # But we already checked z = 0. So this is an error.
                    pass
                elif ls[norm] == 1:
                    count += 2  # disc is a nonzero square: two solutions
                # else: disc is a non-square: zero solutions

    return count


def count_fp_affine(f_coeffs, h_coeffs, p):
    """Count affine points over F_p."""
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


def count_infinity(f_coeffs, h_coeffs, p):
    """Count points at infinity (same for F_p and F_{p^2})."""
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
    lv = lead_g_val % p
    if lv == 0:
        return 1
    if pow(lv, (p - 1) // 2, p) == 1:
        return 2
    return 0


def count_infinity_fp2(f_coeffs, h_coeffs, p, g):
    """Count points at infinity over F_{p^2}."""
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
    # Leading coeff is in F_p. Every nonzero element of F_p is a square in F_{p^2}
    # (since F_{p^2}* has order p^2-1 which is divisible by 2(p-1), and
    #  the embedding F_p* -> F_{p^2}* maps the index-2 subgroup into the
    #  index-2 subgroup)
    # Actually: a ∈ F_p* is a square in F_{p^2}* iff a^{(p^2-1)/2} = 1.
    # a^{(p^2-1)/2} = a^{(p-1)(p+1)/2}. If a^{p-1} = 1 (true for a ∈ F_p*),
    # then a^{(p-1)(p+1)/2} = (a^{p-1})^{(p+1)/2} = 1^{(p+1)/2} = 1.
    # So YES: every nonzero element of F_p is a square in F_{p^2}.
    lv = lead_g_val % p
    if lv == 0:
        return 1
    return 2  # Always a square in F_{p^2}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=500)
    parser.add_argument("--conductors", type=int, nargs="*", default=None)
    args = parser.parse_args()

    data_path = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"

    print("GENUS-2 c2 EXTENSION — FAST (norm-based square detection)")
    print("=" * 72)
    print(f"Max prime: {args.max_prime}")
    print(f"Optimization: N(z) = a^2 - g*b^2 square check replaces F_p^2 exponentiation")
    print()

    # Load curves
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

        # Find mod-3 congruent pair
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

        # Verify c2 at known primes
        verified = 0
        for p in good_known[:5]:
            if p in bad or p <= 2 or p == 3:
                continue
            g = find_non_residue(p)
            if g is None:
                continue

            c1_fp = count_fp_affine(f1, h1, p) + count_infinity(f1, h1, p) - p - 1
            c2_fp2 = count_fp2_affine_fast(f1, h1, p, g) + count_infinity_fp2(f1, h1, p, g)
            c2_comp = (c1_fp * c1_fp + c2_fp2 - p * p - 1) // 2
            c2_known = c1_curve["euler"][p][1]
            if c2_comp == c2_known:
                verified += 1

        if verified < 2:
            print(f"  *** N={cond}: c2 verification FAILED ({verified}/5). SKIP. ***")
            continue

        # Extend
        extended_primes = [p for p in all_primes if p not in bad and p != 3 and p > 97]

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

            # c1 for both curves (O(p))
            c1_1 = count_fp_affine(f1, h1, p) + count_infinity(f1, h1, p) - p - 1
            c1_2 = count_fp_affine(f2, h2, p) + count_infinity(f2, h2, p) - p - 1
            da_c1 = c1_1 - c1_2
            if da_c1 % ell != 0:
                fail_c1 += 1
                tested += 1
                continue
            pass_c1 += 1

            # c2 for both curves (O(p^2) but fast)
            n1_fp2 = count_fp2_affine_fast(f1, h1, p, g) + count_infinity_fp2(f1, h1, p, g)
            n2_fp2 = count_fp2_affine_fast(f2, h2, p, g) + count_infinity_fp2(f2, h2, p, g)
            c2_1 = (c1_1 * c1_1 + n1_fp2 - p * p - 1) // 2
            c2_2 = (c1_2 * c1_2 + n2_fp2 - p * p - 1) // 2

            # Check parity
            if (c1_1 * c1_1 + n1_fp2 - p * p - 1) % 2 != 0:
                fail_c2 += 1
                tested += 1
                continue

            da_c2 = c2_1 - c2_2
            if da_c2 % ell != 0:
                fail_c2 += 1
            else:
                pass_c2 += 1
            tested += 1

        t1 = time.time()
        total_primes = len(good_known) + tested

        c1_status = "PASS" if fail_c1 == 0 else f"FAIL({fail_c1})"
        c2_status = "PASS" if fail_c2 == 0 else f"FAIL({fail_c2})"
        combined = "PASS" if fail_c1 == 0 and fail_c2 == 0 else "FAIL"

        print(f"{ci+1:2d}. N={cond:<8} v={verified}/5  "
              f"c1:{pass_c1}/{tested} {c1_status}  "
              f"c2:{pass_c2}/{tested} {c2_status}  "
              f"total={total_primes}  {combined}  ({t1-t0:.1f}s)")

        results.append({
            "conductor": cond,
            "known_primes": len(good_known),
            "extended_tested": tested,
            "c1_pass": pass_c1,
            "c1_fail": fail_c1,
            "c2_pass": pass_c2,
            "c2_fail": fail_c2,
            "total_primes": total_primes,
            "time_seconds": round(t1 - t0, 1),
        })

    total_time = time.time() - total_start
    print()
    print("=" * 72)
    n_full = sum(1 for r in results if r["c1_fail"] == 0 and r["c2_fail"] == 0)
    print(f"SUMMARY: {n_full}/{len(results)} full pass (c1+c2)")
    print(f"Total time: {total_time:.0f}s ({total_time/60:.1f}min)")

    if n_full > 0:
        avg_c2 = sum(r["c2_pass"] for r in results if r["c2_fail"] == 0) / n_full
        avg_total = sum(r["total_primes"] for r in results if r["c2_fail"] == 0) / n_full
        print(f"Average c2 primes verified: {avg_c2:.0f}")
        print(f"Combined (c1+c2) at {avg_total:.0f} avg primes:")
        print(f"  Random prob: (1/9)^{avg_total:.0f} ~ 10^{-avg_total*0.954:.0f}")

    out_path = Path(__file__).parent / "genus2_c2_fast_results.json"
    with open(out_path, "w") as f:
        json.dump({"results": results, "total_time_s": round(total_time, 1)}, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
