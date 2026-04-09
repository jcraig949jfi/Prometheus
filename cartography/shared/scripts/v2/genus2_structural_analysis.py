"""
Genus-2 Structural Analysis — Twist Dedup, Geometric Cases, Mod-2 Scan
========================================================================
Three analyses on the 37 irreducible mod-3 GSp_4 congruences + new mod-2 scan.

1. Twist deduplication: check if any pairs are related by quadratic character twists
2. Geometric deep dive: Igusa-Clebsch invariants mod 3 for the 7 geometric cases
3. Mod-2 congruence scan: Hasse squeeze weakest at ell=2, expect many more candidates

Usage:
    python genus2_structural_analysis.py
"""

import re
import json
import time
from collections import defaultdict, Counter
from math import sqrt, gcd
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

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
    """Compute Kronecker symbol (a/p) for odd prime p."""
    a = a % p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def parse_good_lfactors(s):
    result = {}
    matches = re.findall(r'\[(-?\d+),(-?\d+),(-?\d+)\]', s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


def parse_igusa_clebsch(s):
    """Parse Igusa-Clebsch invariants [I2, I4, I6, I10]."""
    s = s.strip("[]")
    parts = s.split(",")
    if len(parts) == 4:
        return [int(x.strip()) for x in parts]
    return None


def poly_eval_mod(coeffs, x, ell):
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % ell
        xpow = (xpow * x) % ell
    return val


def is_irreducible_mod(poly_coeffs, ell):
    """Check if polynomial is irreducible mod ell by checking for roots."""
    # For degree 4: irreducible if no roots AND no degree-2 factors
    deg = len(poly_coeffs) - 1
    if deg <= 0:
        return False

    # Check for roots
    for x in range(ell):
        if poly_eval_mod(poly_coeffs, x, ell) == 0:
            return False

    if deg <= 3:
        return True  # No roots + degree <= 3 => irreducible

    # Degree 4: also need to check for degree-2 factors
    # Enumerate all monic degree-2 polys mod ell: x^2 + ax + b
    lead = poly_coeffs[deg] % ell
    if lead == 0:
        return False
    # Normalize to monic
    lead_inv = pow(lead, ell - 2, ell)
    monic = [(c * lead_inv) % ell for c in poly_coeffs]

    for a in range(ell):
        for b in range(ell):
            # Try dividing monic by (x^2 + ax + b)
            # If quotient is also degree 2, then it factors
            # Polynomial long division of degree-4 monic by (x^2 + ax + b)
            r = list(monic)  # copy
            # r[4] = 1 (monic), divide by x^2 + ax + b
            q1 = r[4]  # = 1
            r[3] -= q1 * a
            r[2] -= q1 * b
            q0 = r[3] % ell
            r[2] = (r[2] - q0 * a) % ell
            r[1] = (r[1] - q0 * b) % ell
            if r[2] % ell == 0 and r[1] % ell == 0 and r[0] % ell == 0:
                return False  # Factors as (x^2 + q1*x + q0)(x^2 + a*x + b)

    return True


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_all_curves(filepath):
    """Load all genus-2 curves with full metadata."""
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
            disc = int(parts[0])
            disc_sign = int(parts[4])
            ic_raw = parts[5]
            st_group = parts[8]
            euler = parse_good_lfactors(parts[16] if len(parts) > 16 else "")
            if not euler:
                continue

            ic = parse_igusa_clebsch(ic_raw)
            eqn = parts[3]

            curves.append({
                "conductor": conductor,
                "disc": disc,
                "disc_sign": disc_sign,
                "igusa_clebsch": ic,  # [I2, I4, I6, I10]
                "st_group": st_group,
                "eqn": eqn,
                "euler": euler,
                "n_primes": len(euler),
            })
    return curves


# ─────────────────────────────────────────────────────────────────────────────
# Part 1: Twist deduplication
# ─────────────────────────────────────────────────────────────────────────────

def check_twist_relationship(euler1, euler2, bad_primes, ell=3):
    """
    Check if two curves are related by a quadratic twist.

    Twist signature for genus-2:
      a_p(C_twist) = chi(p) * a_p(C) where chi is a quadratic character
      b_p(C_twist) = b_p(C)  (unchanged under quadratic twist)

    So mod ell: if b_p differences are all 0 mod ell, and a_p ratio matches
    a Kronecker symbol, it's a twist.
    """
    common = sorted(set(euler1.keys()) & set(euler2.keys()))
    good = [p for p in common if p not in bad_primes and p != ell]

    if len(good) < 5:
        return None

    # Check b_p: under quadratic twist, b_p is unchanged
    # So if db = 0 at all primes, twist is possible
    b_exact_match = True
    b_mod_ell_match = True
    a_diffs = []
    b_diffs = []

    for p in good:
        a1, b1 = euler1[p]
        a2, b2 = euler2[p]
        da = a1 - a2
        db = b1 - b2
        a_diffs.append((p, da))
        b_diffs.append((p, db))
        if db != 0:
            b_exact_match = False
        if db % ell != 0:
            b_mod_ell_match = False

    # Check if a_p ratio matches a quadratic character
    # For twist by d: a_p(C2) = (d/p) * a_p(C1)
    # So a_p(C1) - (d/p)*a_p(C1) = a_p(C1)*(1 - (d/p))
    # When (d/p) = 1: da = 0
    # When (d/p) = -1: da = 2*a_p(C1)

    # Try small discriminants for the twist character
    # MUST be squarefree — perfect squares give trivial character (d/p)=1
    twist_candidates = []
    for d in range(-50, 51):
        if d == 0:
            continue
        abs_d = abs(d)
        # Filter: must be squarefree (no p^2 divides d)
        is_sqfree = True
        for p in range(2, int(abs_d**0.5) + 1):
            if abs_d % (p * p) == 0:
                is_sqfree = False
                break
        if not is_sqfree:
            continue

        match_count = 0
        total = 0
        for p in good:
            if p == 2:
                continue
            a1, b1 = euler1[p]
            a2, b2 = euler2[p]
            chi = kronecker_symbol(d, p)
            if chi == 0:
                continue
            total += 1
            if a2 == chi * a1 and b2 == b1:
                match_count += 1

        if total > 0 and match_count == total:
            twist_candidates.append({
                "d": d,
                "primes_checked": total,
                "exact_match": True,
            })
        elif total > 0 and match_count > total * 0.8:
            twist_candidates.append({
                "d": d,
                "primes_checked": total,
                "match_rate": match_count / total,
                "exact_match": False,
            })

    # Check for mod-ell twist: a_p(C1) = chi(p)*a_p(C2) mod ell
    mod_twist_candidates = []
    for d in range(-50, 51):
        if d == 0:
            continue
        abs_d = abs(d)
        is_sqfree = True
        for p2 in range(2, int(abs_d**0.5) + 1):
            if abs_d % (p2 * p2) == 0:
                is_sqfree = False
                break
        if not is_sqfree:
            continue
        match_count = 0
        total = 0
        for p in good:
            if p == 2:
                continue
            a1, b1 = euler1[p]
            a2, b2 = euler2[p]
            chi = kronecker_symbol(d, p)
            if chi == 0:
                continue
            total += 1
            if (a1 - chi * a2) % ell == 0 and (b1 - b2) % ell == 0:
                match_count += 1

        if total > 0 and match_count == total:
            mod_twist_candidates.append({
                "d": d,
                "primes_checked": total,
                "mod_ell": ell,
            })

    return {
        "b_exact_match": b_exact_match,
        "b_mod_ell_match": b_mod_ell_match,
        "n_good_primes": len(good),
        "exact_twists": twist_candidates,
        "mod_ell_twists": mod_twist_candidates,
        "a_diffs_sample": a_diffs[:10],
        "b_diffs_sample": b_diffs[:10],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Geometric cases deep dive
# ─────────────────────────────────────────────────────────────────────────────

def analyze_geometric_cases(ic1, ic2, ell=3):
    """
    Compare Igusa-Clebsch invariants mod ell.

    IC = [I2, I4, I6, I10]
    If all match mod ell, the curves have isomorphic Jacobians over F̄_ell.

    Further: compute absolute Igusa invariants j1, j2, j3 to check
    isomorphism class over the base field.
    """
    if ic1 is None or ic2 is None:
        return {"status": "missing_data"}

    # Raw comparison mod ell
    ic_mod = []
    all_match = True
    for i, (v1, v2) in enumerate(zip(ic1, ic2)):
        m1 = v1 % ell
        m2 = v2 % ell
        match = (m1 == m2)
        if not match:
            all_match = False
        ic_mod.append({
            "index": i,
            "name": ["I2", "I4", "I6", "I10"][i],
            "val1": v1,
            "val2": v2,
            "mod1": m1,
            "mod2": m2,
            "match": match,
        })

    # Check if I10 ≡ 0 mod ell (degenerate reduction)
    i10_degen = (ic1[3] % ell == 0) or (ic2[3] % ell == 0)

    # Absolute Igusa invariants (when I2 ≠ 0):
    # j1 = I4 * I10 / I2^5, j2 = I2^2 * I4 / I10, j3 = I2^5 / I10
    # These determine the isomorphism class over the algebraic closure
    abs_inv = {}
    if ic1[0] != 0 and ic2[0] != 0 and ic1[3] != 0 and ic2[3] != 0:
        # Compute ratios — we only care about mod ell comparison
        # j1 = I4 * I10 / I2^5
        # For mod-ell comparison, use modular arithmetic
        if ell > 2:
            for label, ic in [("curve1", ic1), ("curve2", ic2)]:
                I2, I4, I6, I10 = [x % ell for x in ic]
                if I2 != 0 and I10 != 0:
                    I2_inv = pow(I2, ell - 2, ell)
                    I10_inv = pow(I10, ell - 2, ell)
                    j1 = (I4 * I10 * pow(I2_inv, 5, ell)) % ell
                    j2 = (I2 * I2 * I4 * I10_inv) % ell
                    j3 = (pow(I2, 5, ell) * I10_inv) % ell
                    abs_inv[label] = {"j1": j1, "j2": j2, "j3": j3}

    return {
        "all_match_mod_ell": all_match,
        "ell": ell,
        "ic_details": ic_mod,
        "i10_degenerate": i10_degen,
        "absolute_invariants": abs_inv,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Part 3: Mod-2 scan with irreducibility
# ─────────────────────────────────────────────────────────────────────────────

def scan_mod2(curves, min_primes=10):
    """
    Scan for mod-2 congruences. At ell=2, the Hasse squeeze is weakest:
    |a_p| <= 4*sqrt(p) forces a_p even for p < (ell/8)^2 = 1/16 (never forced).
    But mod 2 is special: a_p mod 2 = #C(F_p) + p + 1 mod 2 = #C(F_p) mod 2 (if p odd).

    For each pair of distinct-class curves at the same conductor:
    Check a_p ≡ a_p' (mod 2) AND b_p ≡ b_p' (mod 2) at all good primes.
    """
    ell = 2

    by_conductor = defaultdict(list)
    for i, c in enumerate(curves):
        by_conductor[c["conductor"]].append(i)

    # Deduplicate by isogeny class (Euler fingerprint)
    by_cond_deduped = {}
    for cond, indices in by_conductor.items():
        if len(indices) < 2:
            continue
        classes = defaultdict(list)
        for idx in indices:
            c = curves[idx]
            primes_avail = sorted(c["euler"].keys())
            fp = tuple(c["euler"][p] for p in primes_avail[:20])
            classes[fp].append(idx)
        class_reps = [v[0] for v in classes.values()]
        if len(class_reps) >= 2:
            by_cond_deduped[cond] = class_reps

    congruences = []
    n_pairs = 0

    for cond, reps in sorted(by_cond_deduped.items()):
        bad = prime_factors(cond)

        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                n_pairs += 1
                c1 = curves[reps[i]]
                c2 = curves[reps[j]]

                common = sorted(set(c1["euler"].keys()) & set(c2["euler"].keys()))
                good = [p for p in common if p not in bad and p != 2]

                if len(good) < min_primes:
                    continue

                all_cong = True
                has_nonzero = False
                diffs_a = []
                diffs_b = []
                for p in good:
                    a1, b1 = c1["euler"][p]
                    a2, b2 = c2["euler"][p]
                    da = a1 - a2
                    db = b1 - b2
                    if da % ell != 0 or db % ell != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nonzero = True
                    diffs_a.append(da)
                    diffs_b.append(db)

                if not all_cong:
                    continue
                if not has_nonzero:
                    continue  # Same isogeny class ghost

                coprime = (cond % ell != 0)
                both_usp4 = c1["st_group"] == "USp(4)" and c2["st_group"] == "USp(4)"

                # Irreducibility check: char poly mod 2
                # x^4 - a_p*x^3 + b_p*x^2 - a_p*p*x + p^2
                irred_witnesses = 0
                for p in good:
                    a1, b1 = c1["euler"][p]
                    a2, b2 = c2["euler"][p]
                    # Check both curves' char polys mod 2
                    for ap, bp in [(a1, b1), (a2, b2)]:
                        coeffs = [
                            (p * p) % ell,
                            (-ap * p) % ell,
                            bp % ell,
                            (-ap) % ell,
                            1,
                        ]
                        if is_irreducible_mod(coeffs, ell):
                            irred_witnesses += 1
                            break
                    if irred_witnesses > 0:
                        break

                congruences.append({
                    "conductor": cond,
                    "coprime": coprime,
                    "both_USp4": both_usp4,
                    "n_good_primes": len(good),
                    "nonzero_da": sum(1 for d in diffs_a if d != 0),
                    "nonzero_db": sum(1 for d in diffs_b if d != 0),
                    "diffs_a_sample": diffs_a[:10],
                    "diffs_b_sample": diffs_b[:10],
                    "irred_witnesses": irred_witnesses,
                    "st1": c1["st_group"],
                    "st2": c2["st_group"],
                    "eqn1": c1["eqn"][:60],
                    "eqn2": c2["eqn"][:60],
                    "ic1": c1["igusa_clebsch"],
                    "ic2": c2["igusa_clebsch"],
                })

    return congruences, n_pairs


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    data_path = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"

    print("GENUS-2 STRUCTURAL ANALYSIS")
    print("=" * 72)
    print(f"Data: {data_path}")
    print()

    t0 = time.time()
    curves = load_all_curves(str(data_path))
    print(f"Loaded {len(curves)} curves in {time.time()-t0:.1f}s")

    # ─── Identify the 37 irreducible mod-3 candidates ───
    irred_conds = [
        1844, 2348, 3572, 4304, 5497, 7945, 9664, 14155, 19201, 20432,
        20560, 21611, 31312, 32119, 32575, 36265, 43276, 50173, 50608,
        69422, 77608, 83776, 88765, 96347, 114437, 124712, 141538, 142265,
        155305, 173936, 195337, 216677, 232912, 235237, 342871, 600953, 745517,
    ]

    by_cond = defaultdict(list)
    for c in curves:
        by_cond[c["conductor"]].append(c)

    # Build the 37 pairs (deduplicate by isogeny class, find the congruent pair)
    pairs_37 = []
    for cond in irred_conds:
        cond_curves = [c for c in by_cond[cond] if c["st_group"] == "USp(4)"]
        if cond % 3 == 0:
            continue
        # Dedup by Euler fingerprint
        classes = defaultdict(list)
        for c in cond_curves:
            primes_avail = sorted(c["euler"].keys())
            fp = tuple(c["euler"][p] for p in primes_avail[:20])
            classes[fp].append(c)

        class_list = list(classes.values())
        if len(class_list) < 2:
            continue

        # Find the mod-3 congruent pair
        found = False
        for i in range(len(class_list)):
            if found:
                break
            for j in range(i + 1, len(class_list)):
                c1 = class_list[i][0]
                c2 = class_list[j][0]
                bad = prime_factors(cond)
                common = sorted(set(c1["euler"].keys()) & set(c2["euler"].keys()))
                good = [p for p in common if p not in bad and p != 3]

                all_cong = True
                has_nz = False
                for p in good:
                    da = c1["euler"][p][0] - c2["euler"][p][0]
                    db = c1["euler"][p][1] - c2["euler"][p][1]
                    if da % 3 != 0 or db % 3 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True

                if all_cong and has_nz:
                    pairs_37.append((cond, c1, c2))
                    found = True
                    break

    print(f"Recovered {len(pairs_37)} / 37 irreducible mod-3 pairs")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # PART 1: TWIST DEDUPLICATION
    # ═══════════════════════════════════════════════════════════════════════
    print("=" * 72)
    print("PART 1: TWIST DEDUPLICATION")
    print("=" * 72)
    print()
    print("For genus-2 quadratic twist by d:")
    print("  a_p(C_twist) = (d/p) * a_p(C)")
    print("  b_p(C_twist) = b_p(C)")
    print()

    twist_results = []
    for cond, c1, c2 in pairs_37:
        bad = prime_factors(cond)
        result = check_twist_relationship(c1["euler"], c2["euler"], bad, ell=3)
        result["conductor"] = cond
        twist_results.append(result)

        # Report
        exact = result["exact_twists"]
        mod_tw = result["mod_ell_twists"]
        b_exact = result["b_exact_match"]
        b_mod = result["b_mod_ell_match"]

        flags = []
        if b_exact:
            flags.append("b_p EXACT MATCH")
        if exact:
            flags.append(f"EXACT TWIST(d={exact[0]['d']})")
        if mod_tw:
            mod_ds = [t["d"] for t in mod_tw]
            flags.append(f"MOD-3 TWIST(d={mod_ds})")

        status = " | ".join(flags) if flags else "no twist"
        print(f"  N={cond:<8} primes={result['n_good_primes']:>3}  {status}")

    n_exact = sum(1 for r in twist_results if r["exact_twists"])
    n_mod = sum(1 for r in twist_results if r["mod_ell_twists"])
    n_b_exact = sum(1 for r in twist_results if r["b_exact_match"])
    print()
    print(f"  SUMMARY: {n_exact} exact twists, {n_mod} mod-3 twists, "
          f"{n_b_exact} with b_p exact match")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # PART 2: GEOMETRIC CASES DEEP DIVE
    # ═══════════════════════════════════════════════════════════════════════
    print("=" * 72)
    print("PART 2: GEOMETRIC CASES (Igusa-Clebsch mod 3)")
    print("=" * 72)
    print()

    geometric_results = []
    n_geometric = 0
    n_rep_theoretic = 0

    for cond, c1, c2 in pairs_37:
        geo = analyze_geometric_cases(c1["igusa_clebsch"], c2["igusa_clebsch"], ell=3)
        geo["conductor"] = cond

        if geo.get("all_match_mod_ell"):
            n_geometric += 1
            tag = "GEOMETRIC"
        else:
            n_rep_theoretic += 1
            tag = "REP-THEORETIC"

        geometric_results.append(geo)

        # Detailed output
        if geo.get("ic_details"):
            ic_str = "  ".join(
                f"{d['name']}:{'=' if d['match'] else '!='}({d['mod1']},{d['mod2']})"
                for d in geo["ic_details"]
            )
        else:
            ic_str = "no IC data"

        abs_match = ""
        if geo.get("absolute_invariants"):
            ai = geo["absolute_invariants"]
            if "curve1" in ai and "curve2" in ai:
                j_match = all(
                    ai["curve1"][k] == ai["curve2"][k]
                    for k in ["j1", "j2", "j3"]
                )
                abs_match = " | abs_j: MATCH" if j_match else " | abs_j: DIFFER"

        degen = " | I10≡0!" if geo.get("i10_degenerate") else ""
        print(f"  N={cond:<8} {tag:<15} {ic_str}{abs_match}{degen}")

    print()
    print(f"  SUMMARY: {n_geometric} geometric, {n_rep_theoretic} representation-theoretic")

    # Deep dive on geometric cases
    print()
    print("  --- Geometric cases detail ---")
    for geo in geometric_results:
        if not geo.get("all_match_mod_ell"):
            continue
        cond = geo["conductor"]
        print(f"\n  N={cond}:")
        if geo.get("ic_details"):
            for d in geo["ic_details"]:
                print(f"    {d['name']}: {d['val1']} vs {d['val2']}  "
                      f"(mod 3: {d['mod1']} vs {d['mod2']})")
        if geo.get("absolute_invariants"):
            ai = geo["absolute_invariants"]
            for label in ["curve1", "curve2"]:
                if label in ai:
                    print(f"    {label} abs Igusa: j1={ai[label]['j1']}, "
                          f"j2={ai[label]['j2']}, j3={ai[label]['j3']}")
        if geo.get("i10_degenerate"):
            print(f"    *** I10 ≡ 0 mod 3 — degenerate reduction! ***")
            print(f"    Jacobian has bad reduction mod 3, invariants unreliable")

    print()

    # ═══════════════════════════════════════════════════════════════════════
    # PART 3: MOD-2 SCAN
    # ═══════════════════════════════════════════════════════════════════════
    print("=" * 72)
    print("PART 3: MOD-2 CONGRUENCE SCAN")
    print("=" * 72)
    print()
    print("Hasse squeeze at ell=2: |a_p| <= 4*sqrt(p), so |da| <= 8*sqrt(p).")
    print("da forced even iff 8*sqrt(p) < 2, i.e., p < 1/16. Never forced.")
    print("Config space per prime: (1/4) for (a,b) both even.")
    print()

    t2 = time.time()
    mod2_congs, n_pairs = scan_mod2(curves)
    t3 = time.time()
    print(f"Scanned {n_pairs} pairs in {t3-t2:.1f}s")
    print()

    # Filter
    coprime = [c for c in mod2_congs if c["coprime"]]
    usp4_coprime = [c for c in coprime if c["both_USp4"]]
    irred = [c for c in usp4_coprime if c["irred_witnesses"] > 0]

    print(f"Total mod-2 congruences: {len(mod2_congs)}")
    print(f"Coprime to conductor:    {len(coprime)}")
    print(f"Both USp(4) + coprime:   {len(usp4_coprime)}")
    print(f"Irreducible (4D):        {len(irred)}")
    print()

    # Detailed output for irreducible cases
    if irred:
        print("--- Irreducible mod-2 congruences ---")
        for c in irred[:50]:
            print(f"  N={c['conductor']:<8} primes={c['n_good_primes']:>3}  "
                  f"da_nz={c['nonzero_da']}/{c['n_good_primes']}  "
                  f"db_nz={c['nonzero_db']}/{c['n_good_primes']}  "
                  f"irred_wit={c['irred_witnesses']}")
        if len(irred) > 50:
            print(f"  ... and {len(irred) - 50} more")
        print()

    # Compare with mod-3 landscape
    print("--- Comparison with mod-3 landscape ---")
    print(f"  mod-3 coprime USp(4) irreducible: 37")
    print(f"  mod-2 coprime USp(4) irreducible: {len(irred)}")
    if len(irred) > 0:
        ratio = len(irred) / 37
        print(f"  Ratio: {ratio:.1f}x (Hasse squeeze prediction: ~9x for ell=2 vs ell=3)")
    print()

    # IC analysis for mod-2 irreducible
    if irred:
        n_geo_mod2 = 0
        n_rep_mod2 = 0
        for c in irred:
            if c["ic1"] and c["ic2"]:
                match = all((v1 - v2) % 2 == 0 for v1, v2 in zip(c["ic1"], c["ic2"]))
                if match:
                    n_geo_mod2 += 1
                else:
                    n_rep_mod2 += 1
        print(f"  IC mod-2: {n_geo_mod2} geometric, {n_rep_mod2} rep-theoretic "
              f"(of {len(irred)} total)")

    # ═══════════════════════════════════════════════════════════════════════
    # Save results
    # ═══════════════════════════════════════════════════════════════════════
    out = {
        "twist_analysis": {
            "n_exact_twists": n_exact,
            "n_mod3_twists": n_mod,
            "n_b_exact_match": n_b_exact,
            "details": [{
                "conductor": r["conductor"],
                "b_exact_match": r["b_exact_match"],
                "exact_twists": r["exact_twists"],
                "mod_ell_twists": r["mod_ell_twists"],
            } for r in twist_results],
        },
        "geometric_analysis": {
            "n_geometric": n_geometric,
            "n_rep_theoretic": n_rep_theoretic,
            "details": geometric_results,
        },
        "mod2_scan": {
            "total": len(mod2_congs),
            "coprime": len(coprime),
            "usp4_coprime": len(usp4_coprime),
            "irreducible": len(irred),
            "pairs_checked": n_pairs,
            "congruences": mod2_congs[:100],  # Top 100
        },
    }

    out_path = Path(__file__).parent / "genus2_structural_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
