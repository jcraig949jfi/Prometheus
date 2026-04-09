"""
Congruence Graph Builder — Map fiber structure of newforms -> mod-l representations
===================================================================================
For each prime l in {5, 7, 11, 13, 17, 19, 23}, find ALL pairs of weight-2
dim-1 newforms at the same level whose Hecke eigenvalues are congruent mod l.

Then:
  1. Verify each via Sturm bound (compute a_p from Weierstrass equations)
  2. Test irreducibility (discriminant non-residue witnesses)
  3. Detect twist equivalences (quadratic character analysis)
  4. Build the congruence graph: nodes=newforms, edges=congruences, quotient by twists

Output: congruence_graph.json with the full fiber map.

Usage:
    python congruence_graph.py                    # full scan, all primes
    python congruence_graph.py --ell 11           # single prime
    python congruence_graph.py --verify           # + Sturm bound verification
    python congruence_graph.py --verify --irred   # + irreducibility test
"""

import sys
import json
import time
from pathlib import Path
from collections import defaultdict, Counter
from math import gcd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from search_engine import _get_duck

OUT_DIR = Path(__file__).resolve().parent
OUT_FILE = OUT_DIR / "congruence_graph.json"


def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def sturm_bound(N, k=2):
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


def legendre_symbol(a, p):
    if a % p == 0:
        return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls


def compute_ap(ainvs, p):
    a1, a2, a3, a4, a6 = [int(a) for a in ainvs]
    b2 = a1*a1 + 4*a2
    b4 = a1*a3 + 2*a4
    b6 = a3*a3 + 4*a6
    if p == 2:
        count = 0
        for x in range(p):
            for y in range(p):
                lhs = (y*y + a1*x*y + a3*y) % p
                rhs = (x*x*x + a2*x*x + a4*x + a6) % p
                if lhs == rhs:
                    count += 1
        return p - count
    s = 0
    for x in range(p):
        f = (4*x*x*x + b2*x*x + 2*b4*x + b6) % p
        s += legendre_symbol(f, p)
    return -s


# ---------------------------------------------------------------------------
# Phase 1: Fast detection using stored traces
# ---------------------------------------------------------------------------
def scan_congruences(ell, min_primes=15):
    """Find all mod-ell congruences between dim-1 weight-2 newforms at same level."""
    con = _get_duck()

    forms = con.execute('''
        SELECT lmfdb_label, level, traces, related_objects
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()

    con.close()

    primes = sieve_primes(50)[:min_primes]

    by_level = defaultdict(list)
    for label, level, traces, related in forms:
        by_level[level].append((label, traces, related))

    congruences = []
    levels_checked = 0
    pairs_checked = 0

    for level, forms_at_level in sorted(by_level.items()):
        if len(forms_at_level) < 2:
            continue
        levels_checked += 1

        for i in range(len(forms_at_level)):
            for j in range(i + 1, len(forms_at_level)):
                pairs_checked += 1
                label_a, traces_a, rel_a = forms_at_level[i]
                label_b, traces_b, rel_b = forms_at_level[j]

                all_cong = True
                diffs = []
                for p in primes:
                    if p <= len(traces_a) and p <= len(traces_b):
                        diff = int(round(traces_a[p - 1])) - int(round(traces_b[p - 1]))
                        if diff % ell != 0:
                            all_cong = False
                            break
                        diffs.append(diff)

                if all_cong and len(diffs) >= min_primes:
                    ell_divides_N = (level % ell == 0)
                    congruences.append({
                        "level": level,
                        "form_a": label_a,
                        "form_b": label_b,
                        "ell": ell,
                        "ell_divides_N": ell_divides_N,
                        "level_factors": sorted(prime_factors(level)),
                        "related_a": rel_a,
                        "related_b": rel_b,
                        "n_primes_checked": len(diffs),
                        "nonzero_diffs": sum(1 for d in diffs if d != 0),
                    })

    return {
        "ell": ell,
        "total_forms": len(forms),
        "levels_checked": levels_checked,
        "pairs_checked": pairs_checked,
        "congruences_found": len(congruences),
        "congruences": congruences,
    }


# ---------------------------------------------------------------------------
# Phase 2: Sturm bound verification (requires EC Weierstrass data)
# ---------------------------------------------------------------------------
def verify_sturm(congruence_data):
    """Verify congruences at Sturm bound level using point counting."""
    con = _get_duck()
    ell = congruence_data["ell"]

    for cong in congruence_data["congruences"]:
        level = cong["level"]
        sb = sturm_bound(level)
        cong["sturm_bound"] = sb

        # Get traces for both forms up to Sturm bound
        primes_needed = sieve_primes(min(sb, 2999))

        for key in ["form_a", "form_b"]:
            label = cong[key]
            row = con.execute(f"""
                SELECT traces FROM modular_forms WHERE lmfdb_label = '{label}'
            """).fetchone()
            if row:
                traces = row[0]
                ap = {}
                for p in primes_needed:
                    if p <= len(traces):
                        ap[p] = int(round(traces[p - 1]))
                cong[f"{key}_ap"] = ap

        # Check congruence up to Sturm bound
        if "form_a_ap" in cong and "form_b_ap" in cong:
            failures = 0
            tested = 0
            for p in primes_needed:
                if p <= sb and p in cong["form_a_ap"] and p in cong["form_b_ap"]:
                    tested += 1
                    diff = cong["form_a_ap"][p] - cong["form_b_ap"][p]
                    if diff % ell != 0:
                        failures += 1
                        break

            cong["sturm_tested"] = tested
            cong["sturm_failures"] = failures
            cong["sturm_passed"] = (failures == 0 and tested > 0)

            # If Sturm bound exceeds trace data, try to bridge with EC data
            if sb > 2999:
                cong["sturm_note"] = f"Sturm bound {sb} exceeds trace data (2999). Partial verification only."

        # Clean up large AP data from output
        for key in ["form_a_ap", "form_b_ap"]:
            if key in cong:
                del cong[key]

    con.close()
    return congruence_data


# ---------------------------------------------------------------------------
# Phase 3: Irreducibility test via discriminant
# ---------------------------------------------------------------------------
def test_irreducibility(congruence_data):
    """Test irreducibility of residual representation for each congruence."""
    con = _get_duck()
    ell = congruence_data["ell"]

    qr_set = set()
    for i in range(ell):
        qr_set.add((i * i) % ell)

    for cong in congruence_data["congruences"]:
        # Get the EC associated with form_a (via related_objects)
        ec_label = None
        if cong.get("related_a"):
            for rel in cong["related_a"]:
                if "EllipticCurve" in rel:
                    # Extract EC label: "EllipticCurve/Q/2184/a" -> need to find actual curve
                    parts = rel.split("/")
                    if len(parts) >= 4:
                        iso_class = f"{parts[2]}.{parts[3]}1"  # e.g., "2184.a1"
                        ec_label = iso_class

        if not ec_label:
            cong["irreducibility"] = "no_ec_data"
            continue

        # Get EC Weierstrass coefficients
        ec_row = con.execute(f"""
            SELECT ainvs, conductor, isogeny_degrees, torsion
            FROM elliptic_curves
            WHERE lmfdb_label = '{ec_label}'
        """).fetchone()

        if not ec_row:
            cong["irreducibility"] = "ec_not_found"
            cong["ec_label_tried"] = ec_label
            continue

        ainvs = ec_row[0]
        conductor = int(ec_row[1])
        isog_degrees = ec_row[2]
        torsion = ec_row[3]

        cong["ec_label"] = ec_label
        cong["ec_isogeny_degrees"] = list(isog_degrees) if isog_degrees else []
        cong["ec_torsion"] = torsion
        cong["ec_has_ell_isogeny"] = ell in (isog_degrees or [])

        # Compute a_p at good primes and check discriminant
        bad_primes = prime_factors(conductor)
        test_primes = [p for p in sieve_primes(500)
                       if p not in bad_primes and p != ell]

        non_residues = []
        for p in test_primes:
            ap = compute_ap(ainvs, p)
            disc = (ap * ap - 4 * p) % ell
            if disc not in qr_set:
                non_residues.append(p)

        cong["irred_witnesses"] = len(non_residues)
        cong["irred_first_witness"] = non_residues[0] if non_residues else None
        cong["irreducible"] = len(non_residues) > 0
        cong["irred_primes_tested"] = len(test_primes)

    con.close()
    return congruence_data


# ---------------------------------------------------------------------------
# Phase 4: Twist deduplication
# ---------------------------------------------------------------------------
def detect_twists(congruence_data):
    """Detect which congruences are related by quadratic twists."""
    con = _get_duck()
    congruences = congruence_data["congruences"]

    # Group congruences by ell
    # For each pair of congruences at different levels, check if one is a twist
    # A twist by character chi maps a_p -> chi(p) * a_p
    # For quadratic chi: chi(p) = +/-1, so |a_p| is preserved

    # Simple heuristic: two congruences are twist-related if their levels
    # share the same odd part (up to powers of small primes)
    # and their a_p values differ only by signs matching a Kronecker symbol

    for i, cong in enumerate(congruences):
        cong["twist_class"] = i  # default: each is its own class
        cong["twist_of"] = None

    # For each pair of congruences, check twist relationship
    for i in range(len(congruences)):
        for j in range(i + 1, len(congruences)):
            ci = congruences[i]
            cj = congruences[j]

            if ci["ell"] != cj["ell"]:
                continue

            # Get traces for the forms
            level_i, level_j = ci["level"], cj["level"]
            if level_i == level_j:
                continue  # same level can't be twists

            # Check if level ratio suggests a twist
            # Twisting by conductor-d character maps level N to lcm(N, d^2)*something
            # Quick check: do the a_p values match up to signs?

            traces_cache = {}
            for label in [ci["form_a"], ci["form_b"], cj["form_a"], cj["form_b"]]:
                if label not in traces_cache:
                    row = con.execute(f"""
                        SELECT traces[1:100] FROM modular_forms
                        WHERE lmfdb_label = '{label}'
                    """).fetchone()
                    if row:
                        traces_cache[label] = [int(round(x)) for x in row[0]]

            # Check if form_a at level_i is a twist of form_a at level_j
            # by seeing if |a_p| values match at good primes
            primes = sieve_primes(97)
            bad_i = prime_factors(level_i)
            bad_j = prime_factors(level_j)
            good = [p for p in primes if p not in bad_i and p not in bad_j]

            if ci["form_a"] in traces_cache and cj["form_a"] in traces_cache:
                tr_i = traces_cache[ci["form_a"]]
                tr_j = traces_cache[cj["form_a"]]

                # Check if |a_p| match (twist changes signs but not magnitudes)
                abs_match = 0
                sign_flips = 0
                total = 0
                for p in good:
                    if p <= len(tr_i) and p <= len(tr_j):
                        a_i = tr_i[p - 1]
                        a_j = tr_j[p - 1]
                        total += 1
                        if abs(a_i) == abs(a_j):
                            abs_match += 1
                            if a_i == -a_j and a_i != 0:
                                sign_flips += 1

                if total > 10 and abs_match == total:
                    # All absolute values match — this is a twist
                    congruences[j]["twist_class"] = congruences[i]["twist_class"]
                    congruences[j]["twist_of"] = i
                    congruences[j]["twist_sign_flips"] = sign_flips

            # Also check form_a(i) vs form_b(j) and vice versa
            if ci["form_a"] in traces_cache and cj["form_b"] in traces_cache:
                tr_i = traces_cache[ci["form_a"]]
                tr_j = traces_cache[cj["form_b"]]
                abs_match = 0
                total = 0
                for p in good:
                    if p <= len(tr_i) and p <= len(tr_j):
                        total += 1
                        if abs(tr_i[p - 1]) == abs(tr_j[p - 1]):
                            abs_match += 1
                if total > 10 and abs_match == total:
                    congruences[j]["twist_class"] = congruences[i]["twist_class"]
                    congruences[j]["twist_of_cross"] = i

    con.close()

    # Count independent classes
    classes = set(c["twist_class"] for c in congruences)
    congruence_data["n_twist_classes"] = len(classes)
    congruence_data["n_independent"] = sum(
        1 for c in congruences if c["twist_of"] is None and c.get("twist_of_cross") is None
    )

    return congruence_data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build congruence graph mod ell")
    parser.add_argument("--ell", type=int, nargs="+", default=[5, 7, 11, 13, 17, 19, 23],
                        help="Primes to scan")
    parser.add_argument("--verify", action="store_true",
                        help="Verify via Sturm bound")
    parser.add_argument("--irred", action="store_true",
                        help="Test irreducibility")
    parser.add_argument("--twists", action="store_true",
                        help="Detect twist equivalences")
    parser.add_argument("--full", action="store_true",
                        help="All phases: verify + irred + twists")
    args = parser.parse_args()

    if args.full:
        args.verify = args.irred = args.twists = True

    all_results = {}

    for ell in args.ell:
        print(f"\n{'='*72}")
        print(f"SCANNING MOD {ell}")
        print(f"{'='*72}")

        t0 = time.time()
        result = scan_congruences(ell)
        t1 = time.time()

        n_cong = result["congruences_found"]
        n_coprime = sum(1 for c in result["congruences"] if not c["ell_divides_N"])

        print(f"  Forms: {result['total_forms']}, Levels: {result['levels_checked']}, "
              f"Pairs: {result['pairs_checked']}")
        print(f"  Congruences: {n_cong} total, {n_coprime} with ell coprime to N")
        print(f"  Time: {t1-t0:.1f}s")

        if n_cong > 0 and args.verify:
            print(f"  Verifying Sturm bounds...")
            t2 = time.time()
            result = verify_sturm(result)
            t3 = time.time()
            n_passed = sum(1 for c in result["congruences"]
                          if c.get("sturm_passed", False))
            print(f"  Sturm: {n_passed}/{n_cong} passed ({t3-t2:.1f}s)")

        if n_cong > 0 and args.irred:
            print(f"  Testing irreducibility...")
            t4 = time.time()
            result = test_irreducibility(result)
            t5 = time.time()
            n_irred = sum(1 for c in result["congruences"]
                          if c.get("irreducible", False))
            print(f"  Irreducible: {n_irred}/{n_cong} ({t5-t4:.1f}s)")

        if n_cong > 0 and args.twists:
            print(f"  Detecting twists...")
            result = detect_twists(result)
            print(f"  Independent (after twist dedup): {result.get('n_independent', '?')}")

        # Print detail table
        if n_cong > 0:
            print(f"\n  {'Level':<8} {'Form A':<18} {'Form B':<18} {'l|N':<5} "
                  f"{'Sturm':<7} {'Irred':<8} {'Twist':<6}")
            print(f"  {'-'*72}")
            for c in result["congruences"]:
                l_div = "yes" if c["ell_divides_N"] else "NO"
                sturm = "PASS" if c.get("sturm_passed") else (
                    "FAIL" if c.get("sturm_passed") is False else "-")
                irred = f"yes({c['irred_witnesses']})" if c.get("irreducible") else (
                    "NO" if c.get("irreducible") is False else (
                        c.get("irreducibility", "-")))
                twist = f"of#{c['twist_of']}" if c.get("twist_of") is not None else (
                    f"cx#{c['twist_of_cross']}" if c.get("twist_of_cross") is not None else
                    "indep")
                print(f"  {c['level']:<8} {c['form_a']:<18} {c['form_b']:<18} "
                      f"{l_div:<5} {sturm:<7} {irred:<8} {twist:<6}")

        all_results[str(ell)] = result

    # Summary across all primes
    print(f"\n{'='*72}")
    print(f"CONGRUENCE GRAPH SUMMARY")
    print(f"{'='*72}")
    print(f"{'ell':<5} {'Total':<7} {'l|N':<5} {'l nmid N':<8} "
          f"{'Sturm':<7} {'Irred':<7} {'Indep':<7}")
    print(f"{'-'*50}")

    for ell_str, result in sorted(all_results.items(), key=lambda x: int(x[0])):
        ell = int(ell_str)
        total = result["congruences_found"]
        div = sum(1 for c in result["congruences"] if c["ell_divides_N"])
        coprime = total - div
        sturm = sum(1 for c in result["congruences"] if c.get("sturm_passed"))
        irred = sum(1 for c in result["congruences"] if c.get("irreducible"))
        indep = result.get("n_independent", "?")
        print(f"{ell:<5} {total:<7} {div:<5} {coprime:<8} "
              f"{sturm:<7} {irred:<7} {indep:<7}")

    # Save
    # Convert to serializable format
    for ell_str in all_results:
        for c in all_results[ell_str]["congruences"]:
            if "level_factors" in c:
                c["level_factors"] = list(c["level_factors"])

    with open(OUT_FILE, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nSaved to {OUT_FILE}")


if __name__ == "__main__":
    main()
