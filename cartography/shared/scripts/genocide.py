"""
Hypothesis Genocide — Rapid-fire generation and killing of cross-domain hypotheses.
=====================================================================================
Generates specific, testable hypotheses and runs permutation nulls on each.
No LLM involved. Pure computation. Mass murder of bad science.
"""

import json
import math
import numpy as np
from scipy import stats
from pathlib import Path

rng = np.random.RandomState(42)

ROOT = Path(__file__).resolve().parents[3]
kills = 0
survives = 0
tests = []


def test_hypothesis(name, real_stat, null_stats, threshold=0.01):
    global kills, survives
    na = np.array(null_stats)
    p = (np.sum(na >= real_stat) + 1) / (len(null_stats) + 1)
    z = (real_stat - na.mean()) / na.std() if na.std() > 0 else 0
    survived = p < threshold
    if survived:
        survives += 1
        tag = "SURVIVES"
    else:
        kills += 1
        tag = "KILLED"
    tests.append({"name": name, "tag": tag, "p": round(p, 4), "z": round(z, 1),
                  "real": round(float(real_stat), 4), "null_mean": round(float(na.mean()), 4)})
    return survived, p, z


def permutation_test(group_a, group_b, n_perm=2000):
    """Permutation test for difference in means."""
    real_d = abs(np.mean(group_a) - np.mean(group_b))
    combined = list(group_a) + list(group_b)
    null_d = []
    for _ in range(n_perm):
        rng.shuffle(combined)
        null_d.append(abs(np.mean(combined[:len(group_a)]) - np.mean(combined[len(group_a):])))
    return real_d, null_d


def omega(n):
    """Count distinct prime factors."""
    if n <= 1: return 0
    count = 0
    d = 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0:
                n //= d
        d += 1
    if n > 1: count += 1
    return count


def is_squarefree(n):
    d = 2
    while d * d <= n:
        if n % (d * d) == 0: return False
        d += 1
    return True


def main():
    global kills, survives

    print("=" * 70)
    print("  HYPOTHESIS GENOCIDE — Rapid-fire cross-domain tests")
    print("=" * 70)
    print()

    # Load data
    knots = json.loads((ROOT / "cartography/knots/data/knots.json").read_text(encoding="utf-8"))
    fungrim = json.loads((ROOT / "cartography/fungrim/data/fungrim_index.json").read_text(encoding="utf-8"))
    antedb = json.loads((ROOT / "cartography/antedb/data/antedb_index.json").read_text(encoding="utf-8"))

    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from search_engine import _get_duck
    con = _get_duck()
    ec_rows = con.execute("""SELECT conductor, json_extract_string(properties, '$.rank') as rank
        FROM objects WHERE object_type = 'elliptic_curve' AND conductor <= 5000""").fetchall()
    con.close()
    conds_r0 = [r[0] for r in ec_rows if r[1] == "0"]
    conds_r1 = [r[0] for r in ec_rows if r[1] == "1"]

    # ==================== BATCH 1: Knot invariants ====================
    print("--- BATCH 1: Knot polynomial structure ---")

    # H1: Alexander degree correlates with determinant
    det_vals, alex_lens = [], []
    for k in knots["knots"]:
        if k.get("determinant") and k.get("alex_coeffs") and k["determinant"] > 0:
            det_vals.append(k["determinant"])
            alex_lens.append(len(k["alex_coeffs"]))
    if len(det_vals) > 30:
        real_r = abs(stats.spearmanr(det_vals, alex_lens)[0])
        null_r = [abs(stats.spearmanr(det_vals, rng.permutation(alex_lens))[0]) for _ in range(2000)]
        s, p, z = test_hypothesis("Determinant ~ Alexander polynomial length", real_r, null_r)
        print(f"  H1: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} r={real_r:.3f}")

    # H2: Jones coefficient sum differs by crossing parity
    even = [sum(abs(c) for c in k["jones_coeffs"]) for k in knots["knots"]
            if k.get("crossing_number", 0) % 2 == 0 and k.get("jones_coeffs")]
    odd = [sum(abs(c) for c in k["jones_coeffs"]) for k in knots["knots"]
           if k.get("crossing_number", 0) % 2 == 1 and k.get("jones_coeffs")]
    if even and odd:
        real_d, null_d = permutation_test(even, odd)
        s, p, z = test_hypothesis("Jones sum: even vs odd crossing", real_d, null_d)
        print(f"  H2: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f}")

    # H3: Max Alexander coeff ~ determinant
    max_alex = [max(abs(c) for c in k["alex_coeffs"]) for k in knots["knots"]
                if k.get("alex_coeffs") and k.get("determinant") and k["determinant"] > 0]
    det_for_alex = [k["determinant"] for k in knots["knots"]
                    if k.get("alex_coeffs") and k.get("determinant") and k["determinant"] > 0]
    if len(max_alex) > 30:
        real_r = abs(stats.spearmanr(det_for_alex, max_alex)[0])
        null_r = [abs(stats.spearmanr(det_for_alex, rng.permutation(max_alex))[0]) for _ in range(2000)]
        s, p, z = test_hypothesis("Determinant ~ max Alexander coefficient", real_r, null_r)
        print(f"  H3: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} r={real_r:.3f}")

    # ==================== BATCH 2: Conductor structure ====================
    print("\n--- BATCH 2: Conductor arithmetic ---")

    # H4: Rank-1 conductors have more prime factors
    omega_r0 = [omega(int(c)) for c in conds_r0[:5000]]
    omega_r1 = [omega(int(c)) for c in conds_r1[:5000]]
    real_d, null_d = permutation_test(omega_r0, omega_r1)
    s, p, z = test_hypothesis("omega(conductor): rank-0 vs rank-1", real_d, null_d)
    print(f"  H4: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} "
          f"r0={np.mean(omega_r0):.3f} r1={np.mean(omega_r1):.3f}")

    # H5: Squarefree rate differs
    sf_r0 = [int(is_squarefree(int(c))) for c in conds_r0[:5000]]
    sf_r1 = [int(is_squarefree(int(c))) for c in conds_r1[:5000]]
    real_d, null_d = permutation_test(sf_r0, sf_r1)
    s, p, z = test_hypothesis("Squarefree rate: rank-0 vs rank-1", real_d, null_d)
    print(f"  H5: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} "
          f"r0={np.mean(sf_r0):.3f} r1={np.mean(sf_r1):.3f}")

    # H6: Conductor mod 6 differs
    mod6_r0 = [int(c) % 6 for c in conds_r0[:5000]]
    mod6_r1 = [int(c) % 6 for c in conds_r1[:5000]]
    chi2, p_chi = stats.chi2_contingency([
        np.bincount(mod6_r0, minlength=6),
        np.bincount(mod6_r1, minlength=6)
    ])[:2]
    survived = p_chi < 0.01
    if survived: survives += 1
    else: kills += 1
    tests.append({"name": "Conductor mod 6: rank-0 vs rank-1", "tag": "SURVIVES" if survived else "KILLED",
                  "p": round(p_chi, 4), "z": 0})
    print(f"  H6: {'SURVIVES' if survived else 'KILLED':8s} p={p_chi:.4f} (chi2={chi2:.1f})")

    # H7: Conductor mod 12 differs
    mod12_r0 = [int(c) % 12 for c in conds_r0[:5000]]
    mod12_r1 = [int(c) % 12 for c in conds_r1[:5000]]
    chi2, p_chi = stats.chi2_contingency([
        np.bincount(mod12_r0, minlength=12),
        np.bincount(mod12_r1, minlength=12)
    ])[:2]
    survived = p_chi < 0.01
    if survived: survives += 1
    else: kills += 1
    tests.append({"name": "Conductor mod 12: rank-0 vs rank-1", "tag": "SURVIVES" if survived else "KILLED",
                  "p": round(p_chi, 4), "z": 0})
    print(f"  H7: {'SURVIVES' if survived else 'KILLED':8s} p={p_chi:.4f} (chi2={chi2:.1f})")

    # ==================== BATCH 3: Fungrim structure ====================
    print("\n--- BATCH 3: Fungrim formula structure ---")

    # H8: Equations have more symbols than definitions
    eqs = [f["n_symbols"] for f in fungrim["formulas"] if f["type"] == "equation"]
    defs = [f["n_symbols"] for f in fungrim["formulas"] if f["type"] == "definition"]
    if eqs and defs:
        real_d, null_d = permutation_test(eqs, defs)
        s, p, z = test_hypothesis("Symbol count: equations vs definitions", real_d, null_d)
        print(f"  H8: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} "
              f"eq={np.mean(eqs):.1f} def={np.mean(defs):.1f}")

    # H9: Module size correlates with bridge symbol count
    mod_stats = fungrim.get("module_stats", {})
    bridge_syms = fungrim.get("bridge_symbols", {})
    mod_bridges = {}
    for sym, mods in bridge_syms.items():
        for m in mods:
            mod_bridges[m] = mod_bridges.get(m, 0) + 1
    common_mods = [m for m in mod_stats if m in mod_bridges]
    if len(common_mods) > 10:
        sizes = [mod_stats[m] for m in common_mods]
        bridges = [mod_bridges[m] for m in common_mods]
        real_r = abs(stats.spearmanr(sizes, bridges)[0])
        null_r = [abs(stats.spearmanr(sizes, rng.permutation(bridges))[0]) for _ in range(2000)]
        s, p, z = test_hypothesis("Module size ~ bridge symbol count", real_r, null_r)
        print(f"  H9: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} r={real_r:.3f}")

    # ==================== BATCH 4: Cross-domain ====================
    print("\n--- BATCH 4: Cross-domain arithmetic ---")

    # H10: Knot determinants that are conductors have different crossing numbers
    cond_set = set(int(c) for c in conds_r0 + conds_r1)
    knots_in_cond = [k for k in knots["knots"] if k.get("determinant") in cond_set and k.get("crossing_number", 0) > 0]
    knots_not_cond = [k for k in knots["knots"] if k.get("determinant") not in cond_set and k.get("crossing_number", 0) > 0 and k.get("determinant")]
    if knots_in_cond and knots_not_cond:
        cross_in = [k["crossing_number"] for k in knots_in_cond]
        cross_out = [k["crossing_number"] for k in knots_not_cond]
        real_d, null_d = permutation_test(cross_in, cross_out)
        s, p, z = test_hypothesis("Crossing number: det-is-conductor vs det-is-not", real_d, null_d)
        print(f"  H10: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f}")

    # H11: ANTEDB chapters with "zero" in name have more bounds
    zero_ch = [len(t.get("numerical_values", [])) for ch in antedb["chapters"]
               for t in ch.get("theorems", []) if "zero" in ch["chapter"].lower()]
    non_zero_ch = [len(t.get("numerical_values", [])) for ch in antedb["chapters"]
                   for t in ch.get("theorems", []) if "zero" not in ch["chapter"].lower()]
    if zero_ch and non_zero_ch:
        real_d, null_d = permutation_test(zero_ch, non_zero_ch)
        s, p, z = test_hypothesis("ANTEDB: 'zero' chapters have more bounds", real_d, null_d)
        print(f"  H11: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f}")

    # H12: Conductor primality predicts rank
    prime_conds = [1 if all(int(c) % i != 0 for i in range(2, min(int(c), 100)))
                   else 0 for c in conds_r0[:5000]]
    prime_conds_r1 = [1 if all(int(c) % i != 0 for i in range(2, min(int(c), 100)))
                      else 0 for c in conds_r1[:5000]]
    real_d, null_d = permutation_test(prime_conds, prime_conds_r1)
    s, p, z = test_hypothesis("Prime conductor rate: rank-0 vs rank-1", real_d, null_d)
    print(f"  H12: {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} "
          f"r0={np.mean(prime_conds):.3f} r1={np.mean(prime_conds_r1):.3f}")

    # ==================== SUMMARY ====================
    print()
    print("=" * 70)
    print(f"  GENOCIDE COMPLETE: {kills} KILLED, {survives} SURVIVE out of {kills+survives}")
    print("=" * 70)
    print()
    for t in tests:
        marker = "***" if t["tag"] == "SURVIVES" else "   "
        print(f"  {marker} {t['tag']:8s} p={t['p']:.4f} z={t['z']:5.1f}  {t['name']}")

    # Save results
    out = ROOT / "cartography" / "convergence" / "data" / "genocide_results.json"
    json.dump({"kills": kills, "survives": survives, "tests": tests}, open(out, "w"), indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
