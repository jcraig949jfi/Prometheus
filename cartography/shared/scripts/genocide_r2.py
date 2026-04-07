"""Genocide Round 2: 20 more hypotheses targeting untested territory."""

import json, math, numpy as np
from scipy import stats
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

rng = np.random.RandomState(123)
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
    print(f"  {'***' if s else '   '} {tag:8s} p={p:.4f} z={z:.1f}  {name}")
    return s


def perm(a, b, n=3000):
    real_d = abs(np.mean(a) - np.mean(b))
    c = list(a) + list(b)
    null = []
    for _ in range(n):
        rng.shuffle(c)
        null.append(abs(np.mean(c[:len(a)]) - np.mean(c[len(a):])))
    return real_d, null


def main():
    global kills, survives
    knots = json.loads((ROOT / "cartography/knots/data/knots.json").read_text(encoding="utf-8"))
    fungrim = json.loads((ROOT / "cartography/fungrim/data/fungrim_index.json").read_text(encoding="utf-8"))
    antedb = json.loads((ROOT / "cartography/antedb/data/antedb_index.json").read_text(encoding="utf-8"))

    from search_engine import _get_duck
    con = _get_duck()
    ec_rows = con.execute("""SELECT conductor, json_extract_string(properties, '$.rank') as rank,
        json_extract_string(properties, '$.torsion_structure') as torsion
        FROM objects WHERE object_type = 'elliptic_curve' AND conductor <= 5000""").fetchall()
    con.close()

    print("=" * 70)
    print("  GENOCIDE ROUND 2")
    print("=" * 70)

    # G1: Jones length ~ crossing number
    print("\n--- Knot structure ---")
    jl = [(k["crossing_number"], len(k["jones_coeffs"])) for k in knots["knots"]
          if k.get("jones_coeffs") and k.get("crossing_number", 0) > 0]
    if jl:
        cn, jlen = zip(*jl)
        real_r = abs(stats.spearmanr(cn, jlen)[0])
        null_r = [abs(stats.spearmanr(cn, rng.permutation(jlen))[0]) for _ in range(3000)]
        test("Jones length ~ crossing number", real_r, null_r)

    # G2: Alexander coeff variance ~ crossing number
    av = [(k["crossing_number"], np.var(k["alex_coeffs"])) for k in knots["knots"]
          if k.get("alex_coeffs") and len(k["alex_coeffs"]) > 1 and k.get("crossing_number", 0) > 0]
    if av:
        cn, var = zip(*av)
        real_r = abs(stats.spearmanr(cn, var)[0])
        null_r = [abs(stats.spearmanr(cn, rng.permutation(var))[0]) for _ in range(3000)]
        test("Alexander variance ~ crossing number", real_r, null_r)

    # G3: Knots with prime determinant have different Jones sums
    prime_j = [sum(abs(c) for c in k["jones_coeffs"]) for k in knots["knots"]
               if k.get("jones_coeffs") and k.get("determinant", 0) > 2
               and all(k["determinant"] % i != 0 for i in range(2, int(k["determinant"]**0.5)+1))]
    comp_j = [sum(abs(c) for c in k["jones_coeffs"]) for k in knots["knots"]
              if k.get("jones_coeffs") and k.get("determinant", 0) > 2
              and not all(k["determinant"] % i != 0 for i in range(2, int(k["determinant"]**0.5)+1))]
    if prime_j and comp_j:
        r, n = perm(prime_j, comp_j)
        test("Jones sum: prime vs composite determinant", r, n)

    # EC torsion
    print("\n--- EC torsion & conductor ---")
    torsion_map = {}
    for row in ec_rows:
        t = row[2] if row[2] else "trivial"
        torsion_map.setdefault(t, []).append(int(row[0]))

    # G4-G7: Torsion predicts conductor mod p
    trivial_conds = torsion_map.get("trivial", [])
    for tg in ["[2]", "[3]", "[2, 2]", "[4]"]:
        if tg in torsion_map and len(torsion_map[tg]) > 30 and trivial_conds:
            for mod in [3, 4, 6]:
                a = [c % mod for c in torsion_map[tg]]
                b = [c % mod for c in trivial_conds[:len(torsion_map[tg])]]
                try:
                    chi2, p_chi = stats.chi2_contingency([
                        np.bincount(a, minlength=mod),
                        np.bincount(b, minlength=mod)
                    ])[:2]
                    s = p_chi < 0.01
                    if s:
                        global survives, kills
                        survives += 1
                    else: kills += 1
                    tag = "SURVIVES" if s else "KILLED"
                    tests.append({"name": f"Torsion {tg} ~ conductor mod {mod}", "tag": tag, "p": round(p_chi, 4), "z": 0})
                    print(f"  {'***' if s else '   '} {tag:8s} p={p_chi:.4f}  Torsion {tg} ~ conductor mod {mod}")
                except:
                    pass

    # Conductor div by small primes
    print("\n--- Conductor prime divisibility ---")
    for p_val in [2, 3, 5, 7, 11, 13]:
        d_r0 = [1 if int(r[0]) % p_val == 0 else 0 for r in ec_rows if r[1] == "0"]
        d_r1 = [1 if int(r[0]) % p_val == 0 else 0 for r in ec_rows if r[1] == "1"]
        if d_r0 and d_r1:
            r, n = perm(d_r0, d_r1)
            test(f"Div by {p_val}: rank-0 vs rank-1", r, n)

    # Fungrim
    print("\n--- Fungrim ---")

    # G: Zeta formulas concentrated in fewer modules
    zeta_forms = [f for f in fungrim["formulas"] if any("Zeta" in s for s in f.get("symbols", []))]
    zeta_mods = set(f["module"] for f in zeta_forms)
    all_mods = [f["module"] for f in fungrim["formulas"]]
    null_conc = [len(set(rng.choice(all_mods, len(zeta_forms), replace=False))) for _ in range(3000)]
    na = np.array(null_conc)
    p = (np.sum(na <= len(zeta_mods)) + 1) / (len(null_conc) + 1)
    z = (len(zeta_mods) - na.mean()) / na.std() if na.std() > 0 else 0
    s = p < 0.01
    if s: survives += 1
    else: kills += 1
    tests.append({"name": "Zeta concentrated in fewer modules", "tag": "SURVIVES" if s else "KILLED",
                  "p": round(p, 4), "z": round(z, 1)})
    print(f"  {'***' if s else '   '} {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f}  Zeta concentrated ({len(zeta_mods)} vs {na.mean():.0f} expected)")

    # G: Pi formulas have more symbols
    pi_syms = [f["n_symbols"] for f in fungrim["formulas"] if "Pi" in f.get("symbols", [])]
    non_pi = [f["n_symbols"] for f in fungrim["formulas"] if "Pi" not in f.get("symbols", [])]
    if pi_syms:
        r, n = perm(pi_syms, non_pi)
        test("Pi formulas have more symbols", r, n)

    # Zipf test
    mod_sizes = sorted(fungrim["module_stats"].values(), reverse=True)
    ranks = np.arange(1, len(mod_sizes) + 1, dtype=float)
    slope, _, r_val, p_val, _ = stats.linregress(np.log(ranks), np.log(np.array(mod_sizes, dtype=float) + 0.1))
    s = r_val**2 > 0.85 and p_val < 0.01
    if s: survives += 1
    else: kills += 1
    tests.append({"name": "Module sizes follow Zipf", "tag": "SURVIVES" if s else "KILLED",
                  "p": round(p_val, 6), "z": 0})
    print(f"  {'***' if s else '   '} {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4e}  Zipf: slope={slope:.2f} R2={r_val**2:.3f}")

    # Summary
    print()
    print("=" * 70)
    print(f"  GENOCIDE R2: {kills} KILLED, {survives} SURVIVE out of {kills + survives}")
    print("=" * 70)
    print()
    for t in tests:
        m = "***" if t["tag"] == "SURVIVES" else "   "
        print(f"  {m} {t['tag']:8s} p={t['p']:.4f}  {t['name']}")

    json.dump({"kills": kills, "survives": survives, "tests": tests},
              open(str(ROOT / "cartography/convergence/data/genocide_r2_results.json"), "w"), indent=2)
    print(f"\nSaved. Total body count: {kills} killed, {survives} survived.")


if __name__ == "__main__":
    main()
