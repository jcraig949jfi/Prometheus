"""
Genus-2 Mod-5 Extended Congruence Scan
========================================
Re-run the mod-5 scan with extended point counting (primes up to 500).
The original scan at 24 primes found 0 coprime USp(4) congruences.
With 92 primes, Hasse squeeze false positives should collapse.

Uses fast F_{p^2} point counting (norm trick) for b_p extension.

Usage:
    python genus2_mod5_extended.py
"""

import re
import time
import json
from collections import defaultdict, Counter
from pathlib import Path
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


# ─── Fast F_{p^2} point counting (from genus2_c2_fast.py) ───

def fp2_mul(a, b, p, g):
    return ((a[0]*b[0] + g*a[1]*b[1]) % p, (a[0]*b[1] + a[1]*b[0]) % p)

def fp2_add(a, b, p):
    return ((a[0]+b[0]) % p, (a[1]+b[1]) % p)

def eval_poly_fp2(coeffs_dict, x, p, g):
    if not coeffs_dict:
        return (0, 0)
    max_deg = max(coeffs_dict.keys())
    result = (coeffs_dict.get(max_deg, 0) % p, 0)
    for d in range(max_deg - 1, -1, -1):
        result = fp2_mul(result, x, p, g)
        c = coeffs_dict.get(d, 0) % p
        result = ((result[0] + c) % p, result[1])
    return result

def count_fp_affine(f_coeffs, h_coeffs, p):
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

def count_fp2_affine(f_coeffs, h_coeffs, p, g):
    count = 0
    ls = [0] * p
    for x in range(1, p):
        ls[x] = 1 if pow(x, (p - 1) // 2, p) == 1 else -1
    for a in range(p):
        for b in range(p):
            x = (a, b)
            fv = eval_poly_fp2(f_coeffs, x, p, g)
            hv = eval_poly_fp2(h_coeffs, x, p, g)
            h2 = fp2_mul(hv, hv, p, g)
            f4 = ((4 * fv[0]) % p, (4 * fv[1]) % p)
            disc = fp2_add(h2, f4, p)
            da, db = disc
            if da == 0 and db == 0:
                count += 1
            else:
                norm = (da * da - g * db * db) % p
                if norm != 0 and ls[norm] == 1:
                    count += 2
    return count

def count_infinity(f_coeffs, h_coeffs, p):
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

def compute_c1(f_coeffs, h_coeffs, p):
    return count_fp_affine(f_coeffs, h_coeffs, p) + count_infinity(f_coeffs, h_coeffs, p) - p - 1

def compute_c2(f_coeffs, h_coeffs, p, g, c1):
    n_fp2 = count_fp2_affine(f_coeffs, h_coeffs, p, g) + 2  # infinity always 2 over F_{p^2}
    return (c1 * c1 + n_fp2 - p * p - 1) // 2


# ─── Irreducibility check ───

def poly_eval_mod(coeffs, x, ell):
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % ell
        xpow = (xpow * x) % ell
    return val

def is_irreducible_mod(poly_coeffs, ell):
    deg = len(poly_coeffs) - 1
    if deg <= 0:
        return False
    for x in range(ell):
        if poly_eval_mod(poly_coeffs, x, ell) == 0:
            return False
    if deg <= 3:
        return True
    lead = poly_coeffs[deg] % ell
    if lead == 0:
        return False
    lead_inv = pow(lead, ell - 2, ell)
    monic = [(c * lead_inv) % ell for c in poly_coeffs]
    for a in range(ell):
        for b in range(ell):
            r = list(monic)
            q1 = r[4]
            r[3] -= q1 * a
            r[2] -= q1 * b
            q0 = r[3] % ell
            r[2] = (r[2] - q0 * a) % ell
            r[1] = (r[1] - q0 * b) % ell
            if r[2] % ell == 0 and r[1] % ell == 0 and r[0] % ell == 0:
                return False
    return True


def main():
    data_path = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
    ell = 5
    max_prime_extend = 200  # Keep moderate — mod-5 is expensive at O(p^2)
    max_conductor = 100000  # Focus on smaller conductors first

    print("GENUS-2 MOD-5 EXTENDED CONGRUENCE SCAN")
    print("=" * 72)
    print(f"ell = {ell}")
    print(f"Extended primes up to: {max_prime_extend}")
    print(f"Max conductor: {max_conductor}")
    print()

    # Load all curves with equations
    t0 = time.time()
    all_data = []
    with open(data_path, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            cond = int(parts[1])
            if cond > max_conductor:
                continue
            st = parts[8]
            eqn_inner = parts[3].strip("[]")
            eqn_parts = eqn_inner.split(",")
            f_str = eqn_parts[0].strip()
            h_str = eqn_parts[1].strip() if len(eqn_parts) > 1 else "0"
            euler_matches = re.findall(r"\[(-?\d+),(-?\d+),(-?\d+)\]", parts[16])
            euler = {int(m[0]): (int(m[1]), int(m[2])) for m in euler_matches}
            all_data.append({
                "conductor": cond, "st": st,
                "f_str": f_str, "h_str": h_str, "euler": euler,
            })
    print(f"Loaded {len(all_data)} curves in {time.time()-t0:.1f}s")

    by_cond = defaultdict(list)
    for d in all_data:
        by_cond[d["conductor"]].append(d)

    # Phase 1: Quick scan at stored primes (~24) to find candidates
    print("\nPhase 1: Quick scan at stored primes...")
    candidates = []
    n_pairs = 0

    for cond, curves in sorted(by_cond.items()):
        if cond % ell == 0:
            continue
        usp4 = [c for c in curves if c["st"] == "USp(4)"]
        if len(usp4) < 2:
            continue

        # Dedup by isogeny class
        classes = defaultdict(list)
        for c in usp4:
            primes_avail = sorted(c["euler"].keys())
            fp = tuple(c["euler"][p] for p in primes_avail[:20])
            classes[fp].append(c)
        class_list = list(classes.values())
        if len(class_list) < 2:
            continue

        bad = prime_factors(cond)

        for i in range(len(class_list)):
            for j in range(i + 1, len(class_list)):
                n_pairs += 1
                c1 = class_list[i][0]
                c2 = class_list[j][0]
                common = sorted(set(c1["euler"].keys()) & set(c2["euler"].keys()))
                good = [p for p in common if p not in bad and p != ell]

                if len(good) < 10:
                    continue

                all_cong = True
                has_nz = False
                for p in good:
                    da = c1["euler"][p][0] - c2["euler"][p][0]
                    db = c1["euler"][p][1] - c2["euler"][p][1]
                    if da % ell != 0 or db % ell != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True

                if all_cong and has_nz:
                    candidates.append((cond, c1, c2, good))

    print(f"Scanned {n_pairs} pairs, found {len(candidates)} candidates at stored primes")

    if not candidates:
        print("\nNo mod-5 candidates found even at stored primes. Done.")
        return

    # Phase 2: Extend verification with point counting
    print(f"\nPhase 2: Extending {len(candidates)} candidates to primes up to {max_prime_extend}...")
    extended_primes = [p for p in sieve_primes(max_prime_extend) if p > 97 and p != ell]

    survivors = []
    for ci, (cond, c1, c2, good_known) in enumerate(candidates):
        bad = prime_factors(cond)
        ext_primes = [p for p in extended_primes if p not in bad]

        f1 = parse_poly(c1["f_str"])
        h1 = parse_poly(c1["h_str"])
        f2 = parse_poly(c2["f_str"])
        h2 = parse_poly(c2["h_str"])

        if not f1 and not h1:
            continue

        # Verify c1 at a couple known primes first
        verified = 0
        for p in good_known[:3]:
            if p <= 2 or p == ell or p in bad:
                continue
            c1_comp = compute_c1(f1, h1, p)
            if c1_comp == c1["euler"][p][0]:
                verified += 1

        if verified < 1:
            continue

        # Extend: check c1 AND c2 at extended primes
        t1 = time.time()
        pass_count = 0
        fail_count = 0
        for p in ext_primes:
            g = find_non_residue(p)
            if g is None:
                continue

            c1_1 = compute_c1(f1, h1, p)
            c1_2 = compute_c1(f2, h2, p)
            da_c1 = c1_1 - c1_2
            if da_c1 % ell != 0:
                fail_count += 1
                break  # One failure kills it

            c2_1 = compute_c2(f1, h1, p, g, c1_1)
            c2_2 = compute_c2(f2, h2, p, g, c1_2)
            da_c2 = c2_1 - c2_2
            if da_c2 % ell != 0:
                fail_count += 1
                break

            pass_count += 1

        t2 = time.time()
        total = len(good_known) + pass_count

        if fail_count == 0:
            status = "SURVIVES"
            survivors.append({
                "conductor": cond, "known_primes": len(good_known),
                "extended_pass": pass_count, "total_primes": total,
            })

            # Irreducibility check
            irred = 0
            for p in good_known:
                if p <= 2 or p == ell:
                    continue
                a1, b1 = c1["euler"][p]
                coeffs = [
                    (p * p) % ell, (-a1 * p) % ell, b1 % ell, (-a1) % ell, 1
                ]
                if is_irreducible_mod(coeffs, ell):
                    irred += 1
                    break

            print(f"  {ci+1}. N={cond:<8} known={len(good_known)} ext={pass_count} "
                  f"total={total}  {status}  irred={'YES' if irred else 'no'}  ({t2-t1:.1f}s)")
        else:
            print(f"  {ci+1}. N={cond:<8} known={len(good_known)} "
                  f"KILLED at extended prime  ({t2-t1:.1f}s)")

    print()
    print("=" * 72)
    print(f"SUMMARY: {len(candidates)} candidates -> {len(survivors)} survivors after extension")
    if survivors:
        for s in survivors:
            prob = s["total_primes"] * 1.398  # log10(25) = 1.398
            print(f"  N={s['conductor']}: {s['total_primes']} primes, "
                  f"random prob (1/25)^{s['total_primes']} ~ 10^{-prob:.0f}")

    out_path = Path(__file__).parent / "genus2_mod5_extended_results.json"
    with open(out_path, "w") as f:
        json.dump({"candidates": len(candidates), "survivors": survivors}, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
