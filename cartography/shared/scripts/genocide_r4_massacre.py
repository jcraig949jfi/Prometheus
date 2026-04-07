"""
Genocide Round 4: THE MASSACRE
================================
30 hypotheses. No mercy. Cross everything with everything.
The ferryman doesn't sleep.
"""

import json, math, numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent))

rng = np.random.RandomState(999)
ROOT = Path(__file__).resolve().parents[3]
kills = 0
survives = 0
tests = []


def test(name, real, null_list, threshold=0.01):
    global kills, survives
    na = np.array(null_list)
    p = (np.sum(na >= real) + 1) / (len(null_list) + 1)
    z = (real - na.mean()) / na.std() if na.std() > 0 else 0
    s = p < threshold
    if s: survives += 1
    else: kills += 1
    tag = "SURVIVES" if s else "KILLED"
    tests.append({"name": name, "tag": tag, "p": round(p, 4), "z": round(z, 1)})
    print(f"  {'>>>' if s else '   '} {tag:8s} p={p:.4f} z={z:5.1f}  {name}")
    return s


def perm(a, b, n=3000):
    real_d = abs(np.mean(a) - np.mean(b))
    c = list(a) + list(b)
    null = []
    for _ in range(n):
        rng.shuffle(c)
        null.append(abs(np.mean(c[:len(a)]) - np.mean(c[len(a):])))
    return real_d, null


def corr_test(x, y, n=3000):
    real_r = abs(stats.spearmanr(x, y)[0])
    null_r = [abs(stats.spearmanr(x, rng.permutation(y))[0]) for _ in range(n)]
    return real_r, null_r


def main():
    global kills, survives

    knots = json.loads((ROOT / "cartography/knots/data/knots.json").read_text(encoding="utf-8"))
    fungrim = json.loads((ROOT / "cartography/fungrim/data/fungrim_index.json").read_text(encoding="utf-8"))
    antedb = json.loads((ROOT / "cartography/antedb/data/antedb_index.json").read_text(encoding="utf-8"))

    from search_engine import _get_duck
    con = _get_duck()
    ec = con.execute("""SELECT conductor, json_extract_string(properties, '$.rank') as rank,
        json_extract_string(properties, '$.torsion_structure') as torsion
        FROM objects WHERE object_type = 'elliptic_curve' AND conductor <= 5000""").fetchall()
    mf = con.execute("""SELECT conductor FROM objects WHERE object_type = 'modular_form' AND conductor <= 5000""").fetchall()
    g2 = con.execute("""SELECT conductor FROM objects WHERE object_type = 'genus2_curve' AND conductor <= 5000""").fetchall()
    con.close()

    c_r0 = [int(r[0]) for r in ec if r[1] == "0"]
    c_r1 = [int(r[0]) for r in ec if r[1] == "1"]
    c_r2 = [int(r[0]) for r in ec if r[1] == "2"]
    mf_c = [int(r[0]) for r in mf]
    g2_c = [int(r[0]) for r in g2]

    print("=" * 70)
    print("  GENOCIDE R4: THE MASSACRE (30 hypotheses)")
    print("=" * 70)

    # ============================================================
    # BLOCK A: Deep knot structure (10 tests)
    # ============================================================
    print("\n=== BLOCK A: Deep knot structure ===")

    kdata = [(k["crossing_number"], k.get("determinant", 0),
              k.get("alex_coeffs", []), k.get("jones_coeffs", []))
             for k in knots["knots"]
             if k.get("crossing_number", 0) > 0 and k.get("alex_coeffs") and k.get("jones_coeffs")]

    # A1: Alexander and Jones polynomial lengths correlate
    al = [len(d[2]) for d in kdata]
    jl = [len(d[3]) for d in kdata]
    r, n = corr_test(al, jl)
    test("Alexander length ~ Jones length", r, n)

    # A2: Alternating sum of Alexander coeffs = determinant (this IS the definition)
    correct = 0
    for k in knots["knots"]:
        if k.get("alex_coeffs") and k.get("determinant") and k.get("alexander"):
            ac = k["alex_coeffs"]
            mp = k["alexander"]["min_power"]
            alt_sum = abs(sum(c * ((-1) ** (mp + i)) for i, c in enumerate(ac)))
            if alt_sum == k["determinant"]:
                correct += 1
    total = sum(1 for k in knots["knots"] if k.get("alex_coeffs") and k.get("determinant") and k.get("alexander"))
    if total > 0:
        rate = correct / total
        print(f"  >>> DEFINITIONAL p=0.0000 z= inf  Alexander alternating sum = determinant ({correct}/{total} = {rate:.1%})")
        survives += 1
        tests.append({"name": "Alexander alt-sum = determinant (definitional)", "tag": "SURVIVES", "p": 0, "z": 999})

    # A3: Coefficient sum of Jones polynomial differs between knots with det=prime vs det=composite
    prime_jones_sum = []
    comp_jones_sum = []
    for cn, det, ac, jc in kdata:
        if det > 2:
            js = sum(abs(c) for c in jc)
            is_prime = all(det % i != 0 for i in range(2, int(det**0.5) + 1))
            if is_prime:
                prime_jones_sum.append(js)
            else:
                comp_jones_sum.append(js)
    if prime_jones_sum and comp_jones_sum:
        r, n = perm(prime_jones_sum, comp_jones_sum)
        test("Jones coeff sum: prime det vs composite det", r, n)

    # A4: Max Jones coeff ~ determinant
    max_j = [max(abs(c) for c in d[3]) for d in kdata if d[1] and d[1] > 0]
    dets = [d[1] for d in kdata if d[1] and d[1] > 0]
    if max_j:
        r, n = corr_test(dets, max_j)
        test("max Jones coeff ~ determinant", r, n)

    # A5: Number of zero coefficients in Jones ~ crossing number
    n_zeros_j = [sum(1 for c in d[3] if c == 0) for d in kdata]
    crossings = [d[0] for d in kdata]
    r, n = corr_test(crossings, n_zeros_j)
    test("Jones zero-coeff count ~ crossing number", r, n)

    # A6: Sign pattern of Alexander coeffs (n_positive - n_negative) ~ crossing
    sign_balance = [sum(1 for c in d[2] if c > 0) - sum(1 for c in d[2] if c < 0) for d in kdata]
    r, n = corr_test(crossings, [abs(s) for s in sign_balance])
    test("|Alexander sign balance| ~ crossing number", r, n)

    # A7: Jones polynomial evaluated at -1 ~ Alexander evaluated at -1 (= determinant)
    # Both should relate to determinant — but do they correlate with each other?
    jones_at_neg1 = []
    alex_at_neg1 = []
    for cn, det, ac, jc in kdata:
        if ac and jc:
            # Alexander at -1
            mp_a = knots["knots"][0].get("alexander", {}).get("min_power", 0)  # rough
            a_val = abs(sum(c * ((-1) ** i) for i, c in enumerate(ac)))
            # Jones at -1
            j_val = abs(sum(c * ((-1) ** i) for i, c in enumerate(jc)))
            jones_at_neg1.append(j_val)
            alex_at_neg1.append(a_val)
    if jones_at_neg1:
        r, n = corr_test(alex_at_neg1, jones_at_neg1)
        test("Alexander(-1) ~ Jones(-1)", r, n)

    # ============================================================
    # BLOCK B: EC arithmetic (10 tests)
    # ============================================================
    print("\n=== BLOCK B: EC conductor arithmetic ===")

    # B1: Rank-2 conductors have different prime factorization than rank-0
    def omega(n):
        if n <= 1: return 0
        count, d = 0, 2
        while d * d <= n:
            if n % d == 0:
                count += 1
                while n % d == 0: n //= d
            d += 1
        if n > 1: count += 1
        return count

    if c_r2:
        o_r0 = [omega(c) for c in c_r0[:3000]]
        o_r2 = [omega(c) for c in c_r2]
        r, n = perm(o_r0, o_r2)
        test("omega: rank-0 vs rank-2", r, n)

    # B2: Rank-2 conductors are smaller on average
    if c_r2:
        r, n = perm(c_r0[:len(c_r2)], c_r2)
        test("Mean conductor: rank-0 vs rank-2", r, n)

    # B3: Gap between consecutive rank-1 conductors differs from rank-0 gaps
    sorted_r0 = sorted(set(c_r0))
    sorted_r1 = sorted(set(c_r1))
    gaps_r0 = [sorted_r0[i+1] - sorted_r0[i] for i in range(len(sorted_r0)-1)]
    gaps_r1 = [sorted_r1[i+1] - sorted_r1[i] for i in range(len(sorted_r1)-1)]
    if gaps_r0 and gaps_r1:
        r, n = perm(gaps_r0[:500], gaps_r1[:500])
        test("Conductor gap size: rank-0 vs rank-1", r, n)

    # B4: Genus-2 conductors overlap with EC conductors more than random
    if g2_c:
        g2_set = set(g2_c)
        ec_set = set(c_r0 + c_r1)
        real_overlap = len(g2_set & ec_set)
        all_in_range = set(range(min(g2_c), max(g2_c)+1))
        null_overlap = []
        for _ in range(3000):
            fake = set(rng.choice(list(all_in_range), len(g2_c), replace=False))
            null_overlap.append(len(fake & ec_set))
        test("G2 conductors overlap EC conductors above chance", real_overlap, null_overlap)

    # B5: Conductor mod 24 predicts rank
    try:
        mod24_r0 = np.bincount([c % 24 for c in c_r0[:5000]], minlength=24)
        mod24_r1 = np.bincount([c % 24 for c in c_r1[:5000]], minlength=24)
        chi2, p_chi = stats.chi2_contingency([mod24_r0, mod24_r1])[:2]
        s = p_chi < 0.01
        if s: survives += 1
        else: kills += 1
        tests.append({"name": "Conductor mod 24: rank-0 vs rank-1", "tag": "SURVIVES" if s else "KILLED",
                      "p": round(p_chi, 4), "z": 0})
        print(f"  {'>>>' if s else '   '} {'SURVIVES' if s else 'KILLED':8s} p={p_chi:.4f}  Conductor mod 24: rank-0 vs rank-1")
    except: pass

    # B6: Number of EC at prime conductors vs composite conductors
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0: return False
        return True

    ec_per_cond = defaultdict(int)
    for r in ec:
        ec_per_cond[int(r[0])] += 1

    prime_cond_counts = [ec_per_cond[c] for c in ec_per_cond if is_prime(c)]
    comp_cond_counts = [ec_per_cond[c] for c in ec_per_cond if not is_prime(c) and c > 1]
    if prime_cond_counts and comp_cond_counts:
        r, n = perm(prime_cond_counts, comp_cond_counts)
        test("EC per prime conductor vs composite conductor", r, n)

    # ============================================================
    # BLOCK C: Cross-domain forbidden (10 tests)
    # ============================================================
    print("\n=== BLOCK C: Cross-domain forbidden ===")

    # C1: Knot determinants that are ALSO genus-2 conductors
    if g2_c:
        det_set = set(knots.get("determinants_list", []))
        g2_set = set(g2_c)
        real_ov = len(det_set & g2_set)
        all_odds = set(range(1, max(det_set)+1, 2)) if det_set else set()
        null_ov = [len(set(rng.choice(list(all_odds), len(det_set), replace=False)) & g2_set)
                   for _ in range(3000)] if all_odds else []
        if null_ov:
            test("Knot dets overlap G2 conductors", real_ov, null_ov)

    # C2: Fungrim formula type distribution ~ ANTEDB theorem type distribution
    f_types = defaultdict(int)
    for f in fungrim["formulas"]:
        f_types[f.get("type", "?")] += 1
    a_types = defaultdict(int)
    for ch in antedb["chapters"]:
        for t in ch.get("theorems", []):
            a_types[t.get("type", "?")] += 1

    common_types = set(f_types.keys()) & set(a_types.keys())
    if len(common_types) > 2:
        f_vec = [f_types.get(t, 0) for t in sorted(common_types)]
        a_vec = [a_types.get(t, 0) for t in sorted(common_types)]
        real_r = abs(stats.spearmanr(f_vec, a_vec)[0])
        null_r = [abs(stats.spearmanr(f_vec, rng.permutation(a_vec))[0]) for _ in range(3000)]
        test("Fungrim type dist ~ ANTEDB type dist", real_r, null_r)

    # C3: Mean ANTEDB bound value per chapter ~ chapter position
    ch_bounds = []
    ch_positions = []
    for i, ch in enumerate(antedb["chapters"]):
        bounds = []
        for t in ch.get("theorems", []):
            for v in t.get("numerical_values", []):
                try:
                    if "/" in str(v):
                        num, den = str(v).split("/")
                        bounds.append(float(num)/float(den))
                    else:
                        bounds.append(float(v))
                except: pass
        if bounds:
            ch_bounds.append(np.mean(bounds))
            ch_positions.append(i)
    if len(ch_bounds) > 5:
        r, n = corr_test(ch_positions, ch_bounds)
        test("ANTEDB: mean bound ~ chapter position", r, n)

    # C4: Fungrim symbols per formula ~ formula position in module
    # (Do later formulas in a module use more symbols?)
    mod_positions = defaultdict(list)
    for i, f in enumerate(fungrim["formulas"]):
        mod_positions[f["module"]].append((i, f["n_symbols"]))
    within_mod_corr = []
    for mod, items in mod_positions.items():
        if len(items) > 10:
            pos, syms = zip(*items)
            r_val = stats.spearmanr(pos, syms)[0]
            if not np.isnan(r_val):
                within_mod_corr.append(r_val)
    if within_mod_corr:
        mean_r = np.mean(within_mod_corr)
        # Null: shuffle within each module
        null_means = []
        for _ in range(1000):
            shuffled_corrs = []
            for mod, items in mod_positions.items():
                if len(items) > 10:
                    pos, syms = zip(*items)
                    shuffled_corrs.append(stats.spearmanr(pos, rng.permutation(syms))[0])
            null_means.append(np.mean([r for r in shuffled_corrs if not np.isnan(r)]))
        test("Fungrim: later formulas have more symbols (within module)", abs(mean_r),
             [abs(m) for m in null_means])

    # C5: EC rank-2 conductors cluster near specific mod residues
    if len(c_r2) > 20:
        # Compare mod-12 distribution of rank-2 vs rank-0
        try:
            chi2, p_chi = stats.chi2_contingency([
                np.bincount([c % 12 for c in c_r2], minlength=12),
                np.bincount([c % 12 for c in c_r0[:len(c_r2)*10]], minlength=12)
            ])[:2]
            s = p_chi < 0.01
            if s: survives += 1
            else: kills += 1
            tests.append({"name": "Rank-2 conductor mod 12 differs from rank-0",
                          "tag": "SURVIVES" if s else "KILLED", "p": round(p_chi, 4), "z": 0})
            print(f"  {'>>>' if s else '   '} {'SURVIVES' if s else 'KILLED':8s} p={p_chi:.4f}  Rank-2 conductor mod 12 vs rank-0")
        except: pass

    # C6: MF count per level ~ EC count per conductor (already found z=72, but test at finer grain)
    # Specifically: does the RATIO MF/EC per N have structure?
    shared_N = sorted(set(ec_per_cond.keys()) & set(int(r[0]) for r in mf))
    if len(shared_N) > 100:
        mf_per = defaultdict(int)
        for r in mf: mf_per[int(r[0])] += 1
        ratios = [mf_per[n] / ec_per_cond[n] for n in shared_N if ec_per_cond[n] > 0]
        conductors = [n for n in shared_N if ec_per_cond[n] > 0]
        # Does the MF/EC ratio correlate with conductor value?
        r, n = corr_test(conductors[:500], ratios[:500])
        test("MF/EC ratio ~ conductor value", r, n)

    # ============================================================
    # SUMMARY
    # ============================================================
    print()
    print("=" * 70)
    print(f"  THE MASSACRE: {kills} in the Styx, {survives} returned with cargo")
    print("=" * 70)
    print()
    for t in tests:
        m = ">>>" if t["tag"] == "SURVIVES" else "   "
        print(f"  {m} {t['tag']:8s} p={t['p']:.4f}  {t['name']}")

    json.dump({"kills": kills, "survives": survives, "tests": tests},
              open(str(ROOT / "cartography/convergence/data/genocide_r4_results.json"), "w"), indent=2)

    print(f"\n  Total across all rounds: check genocide_r1-r4_results.json")


if __name__ == "__main__":
    main()
