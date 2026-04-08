"""
Hypothesis Genocide Round 5 — Expansion Pack
=============================================
Tests cross-domain hypotheses involving the 7 new datasets:
Number Fields, Isogenies, Space Groups, Local Fields, Polytopes, pi-Base, MMLKG.

No LLM. Pure computation. The Styx claims its own.
"""

import json
import math
import numpy as np
from scipy import stats
from pathlib import Path

rng = np.random.RandomState(2026)

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
    count, d = 0, 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0: n //= d
        d += 1
    if n > 1: count += 1
    return count


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def main():
    global kills, survives
    print("=" * 70)
    print("  HYPOTHESIS GENOCIDE R5 — Expansion Pack (7 new datasets)")
    print("=" * 70)
    print()

    # Load data
    nf = json.loads((ROOT / "cartography/number_fields/data/number_fields.json").read_text(encoding="utf-8"))
    knots = json.loads((ROOT / "cartography/knots/data/knots.json").read_text(encoding="utf-8"))

    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from search_engine import _get_duck
    con = _get_duck()
    ec_rows = con.execute("""SELECT conductor, json_extract_string(properties, '$.rank') as rank
        FROM objects WHERE object_type = 'elliptic_curve' AND conductor <= 5000""").fetchall()
    con.close()
    conds_r0 = [r[0] for r in ec_rows if r[1] == "0"]
    conds_r1 = [r[0] for r in ec_rows if r[1] == "1"]

    # Load isogeny data
    iso_dir = ROOT / "cartography/isogenies/data/graphs"
    iso_primes = []
    iso_node_counts = {}
    for pdir in sorted(iso_dir.iterdir()):
        if not pdir.is_dir(): continue
        try:
            p = int(pdir.name)
        except ValueError:
            continue
        iso_primes.append(p)
        npz_files = list(pdir.glob("*.npz"))
        if npz_files:
            try:
                adj = np.load(str(npz_files[0]))
                for key in adj.files:
                    iso_node_counts[p] = adj[key].shape[0]
                    break
            except Exception:
                pass

    # Load space groups
    bilbao_dir = ROOT / "cartography/physics/data/bilbao"
    spacegroups = []
    for sg_file in sorted(bilbao_dir.glob("sg_*.json")):
        try:
            sg = json.loads(sg_file.read_text(encoding="utf-8"))
            spacegroups.append(sg)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    # Load polytopes
    poly_dir = ROOT / "cartography/polytopes/data"
    polytopes = []
    for jf in sorted(poly_dir.glob("*.json")):
        if jf.name == "manifest.json": continue
        try:
            entries = json.loads(jf.read_text(encoding="utf-8"))
            if isinstance(entries, list):
                polytopes.extend([e for e in entries if isinstance(e, dict) and e])
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    print(f"Loaded: {len(nf)} number fields, {len(iso_primes)} isogeny primes, "
          f"{len(spacegroups)} space groups, {len(polytopes)} polytopes")
    print()

    # ==================== BATCH 1: Number Fields ====================
    print("--- BATCH 1: Number Fields structure ---")

    # H1: Class number distribution differs by degree (2 vs 3)
    cn_d2 = [int(f["class_number"]) for f in nf if f.get("degree") == 2 and f.get("class_number")]
    cn_d3 = [int(f["class_number"]) for f in nf if f.get("degree") == 3 and f.get("class_number")]
    if cn_d2 and cn_d3:
        real_d, null_d = permutation_test(cn_d2[:2000], cn_d3[:2000])
        s, p, z = test_hypothesis("Class number: degree-2 vs degree-3 fields", real_d, null_d)
        print(f"  H1:  {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} "
              f"d2={np.mean(cn_d2[:2000]):.2f} d3={np.mean(cn_d3[:2000]):.2f}")

    # H2: Class number 1 fields have smaller discriminants than others (known: Stark conjecture related)
    cn1_disc = [abs(int(f["disc_abs"])) for f in nf if f.get("class_number") == "1" and f.get("disc_abs")]
    cn_other_disc = [abs(int(f["disc_abs"])) for f in nf if f.get("class_number") and f["class_number"] != "1" and f.get("disc_abs")]
    if cn1_disc and cn_other_disc:
        real_d, null_d = permutation_test(
            np.log1p(cn1_disc[:2000]).tolist(),
            np.log1p(cn_other_disc[:2000]).tolist()
        )
        s, p, z = test_hypothesis("log(disc): class-number-1 vs others (Stark-adjacent)", real_d, null_d)
        print(f"  H2:  {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f}")

    # H3: Galois group label encodes class number structure
    galois_cn = {}
    for f in nf:
        g = f.get("galois_label", "")
        cn = f.get("class_number")
        if g and cn:
            galois_cn.setdefault(g, []).append(int(cn))
    # Compare two most common Galois groups
    galois_sorted = sorted(galois_cn.keys(), key=lambda g: -len(galois_cn[g]))
    if len(galois_sorted) >= 2:
        g1, g2 = galois_sorted[0], galois_sorted[1]
        real_d, null_d = permutation_test(galois_cn[g1][:2000], galois_cn[g2][:2000])
        s, p, z = test_hypothesis(f"Class number: {g1} vs {g2} Galois groups", real_d, null_d)
        print(f"  H3:  {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} "
              f"{g1}={np.mean(galois_cn[g1][:2000]):.2f} {g2}={np.mean(galois_cn[g2][:2000]):.2f}")

    # ==================== BATCH 2: Number Fields vs Elliptic Curves ====================
    print("\n--- BATCH 2: Number Fields vs Elliptic Curves ---")

    # H4: Discriminants of class-number-1 quadratic fields overlap conductors more than chance
    cn1_quad_disc = set(abs(int(f["disc_abs"])) for f in nf
                        if f.get("degree") == 2 and f.get("class_number") == "1" and f.get("disc_abs"))
    all_conds = set(int(c) for c in conds_r0 + conds_r1 if int(c) > 0)
    real_overlap = len(cn1_quad_disc & all_conds) / max(len(cn1_quad_disc), 1)
    null_overlaps = []
    disc_list = list(cn1_quad_disc)
    for _ in range(2000):
        fake_discs = set(rng.choice(range(1, max(disc_list) + 1), size=len(disc_list), replace=False))
        null_overlaps.append(len(fake_discs & all_conds) / max(len(fake_discs), 1))
    s, p, z = test_hypothesis("CN=1 quad disc overlap with EC conductors", real_overlap, null_overlaps)
    print(f"  H4:  {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} "
          f"overlap={real_overlap:.3f} null={np.mean(null_overlaps):.3f}")

    # H5: Number field regulators correlate with conductor density
    # (Regulator encodes arithmetic complexity → does it predict EC density?)
    regs = [(float(f["regulator"]), abs(int(f["disc_abs"])))
            for f in nf if f.get("regulator") and f.get("disc_abs")
            and float(f["regulator"]) > 0 and abs(int(f["disc_abs"])) <= 5000]
    if len(regs) > 30:
        reg_vals = [r[0] for r in regs]
        disc_vals = [r[1] for r in regs]
        # How many EC conductors fall near each discriminant?
        ec_density = [sum(1 for c in all_conds if abs(c - d) < 50) for d in disc_vals]
        real_r = abs(stats.spearmanr(reg_vals, ec_density)[0])
        null_r = [abs(stats.spearmanr(reg_vals, rng.permutation(ec_density))[0]) for _ in range(2000)]
        s, p, z = test_hypothesis("NF regulator ~ EC conductor density", real_r, null_r)
        print(f"  H5:  {'SURVIVES' if s else 'KILLED':8s} p={p:.4f} z={z:.1f} r={real_r:.3f}")

    # ==================== BATCH 3: Isogeny graphs ====================
    print("\n--- BATCH 3: Isogeny graph structure ---")

    # H6: Supersingular node count grows with floor((p-1)/12) (known: Deuring/Eichler)
    iso_with_nodes = [(p, n) for p, n in iso_node_counts.items() if p > 5]
    if len(iso_with_nodes) > 50:
        primes_list = [x[0] for x in iso_with_nodes]
        nodes_list = [x[1] for x in iso_with_nodes]
        predicted = [math.floor((p - 1) / 12) + 1 for p in primes_list]
        real_r = abs(stats.spearmanr(nodes_list, predicted)[0])
        null_r = [abs(stats.spearmanr(nodes_list, rng.permutation(predicted))[0]) for _ in range(2000)]
        s, p_val, z = test_hypothesis("Isogeny nodes ~ (p-1)/12 (Deuring mass formula)", real_r, null_r)
        print(f"  H6:  {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f} r={real_r:.3f}")

    # H7: Isogeny primes that are also knot determinants have different node counts
    knot_dets = set(k.get("determinant", 0) for k in knots["knots"] if k.get("determinant"))
    iso_in_knot = [iso_node_counts[p] for p in iso_primes if p in knot_dets and p in iso_node_counts]
    iso_not_knot = [iso_node_counts[p] for p in iso_primes if p not in knot_dets and p in iso_node_counts]
    if len(iso_in_knot) > 20 and len(iso_not_knot) > 20:
        real_d, null_d = permutation_test(iso_in_knot, iso_not_knot)
        s, p_val, z = test_hypothesis("Isogeny nodes: prime-is-knot-det vs not", real_d, null_d)
        print(f"  H7:  {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f}")

    # H8: Isogeny node count mod 2 correlates with p mod 4
    if len(iso_with_nodes) > 50:
        nodes_mod2 = [n % 2 for _, n in iso_with_nodes]
        primes_mod4 = [1 if p % 4 == 1 else 0 for p, _ in iso_with_nodes]
        real_r = abs(stats.spearmanr(nodes_mod2, primes_mod4)[0])
        null_r = [abs(stats.spearmanr(nodes_mod2, rng.permutation(primes_mod4))[0]) for _ in range(2000)]
        s, p_val, z = test_hypothesis("Isogeny nodes mod 2 ~ p mod 4", real_r, null_r)
        print(f"  H8:  {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f} r={real_r:.3f}")

    # ==================== BATCH 4: Space Groups vs Number Theory ====================
    print("\n--- BATCH 4: Space Groups vs Number Theory ---")

    # H9: Point group order distribution matches number field degree distribution
    pg_orders = [sg.get("point_group_order", 0) for sg in spacegroups if sg.get("point_group_order")]
    nf_degrees = [f.get("degree", 0) for f in nf if f.get("degree")]
    # KS test on distributions
    if pg_orders and nf_degrees:
        # Normalize both to CDFs and compare
        ks_stat, ks_p = stats.ks_2samp(pg_orders, nf_degrees[:1000])
        survived = ks_p < 0.01
        if survived: survives += 1
        else: kills += 1
        tag = "SURVIVES" if survived else "KILLED"
        tests.append({"name": "SG point group order ~ NF degree (KS)", "tag": tag,
                      "p": round(ks_p, 4), "z": 0, "real": round(ks_stat, 4), "null_mean": 0})
        print(f"  H9:  {tag:8s} p={ks_p:.4f} KS={ks_stat:.3f}")

    # H10: Wyckoff position count correlates with space group number
    wyckoff_counts = [(sg["space_group_number"], sg["num_wyckoff_positions"])
                      for sg in spacegroups
                      if sg.get("num_wyckoff_positions") and sg.get("space_group_number")]
    if len(wyckoff_counts) > 20:
        sg_nums = [x[0] for x in wyckoff_counts]
        wy_counts = [x[1] for x in wyckoff_counts]
        real_r = abs(stats.spearmanr(sg_nums, wy_counts)[0])
        null_r = [abs(stats.spearmanr(sg_nums, rng.permutation(wy_counts))[0]) for _ in range(2000)]
        s, p_val, z = test_hypothesis("SG number ~ Wyckoff position count", real_r, null_r)
        print(f"  H10: {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f} r={real_r:.3f}")

    # ==================== BATCH 5: Polytopes ====================
    print("\n--- BATCH 5: Polytope structure ---")

    # H11: Polytope f-vector entries correlate with dimension (Euler relation: should survive)
    poly_dim_fv = [(p.get("DIM", 0), p.get("F_VECTOR", []))
                   for p in polytopes if p.get("DIM") and p.get("F_VECTOR")]
    if len(poly_dim_fv) > 20:
        dims = [x[0] for x in poly_dim_fv]
        fv_sums = [sum(int(v) for v in x[1] if str(v).lstrip('-').isdigit()) for x in poly_dim_fv]
        real_r = abs(stats.spearmanr(dims, fv_sums)[0])
        null_r = [abs(stats.spearmanr(dims, rng.permutation(fv_sums))[0]) for _ in range(2000)]
        s, p_val, z = test_hypothesis("Polytope dim ~ f-vector sum (Euler relation)", real_r, null_r)
        print(f"  H11: {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f} r={real_r:.3f}")

    # H12: Euler characteristic from f-vector (alternating sum) = expected value
    euler_chars = []
    for p_data in polytopes:
        fv = p_data.get("F_VECTOR", [])
        if fv:
            try:
                chi = sum((-1)**i * int(v) for i, v in enumerate(fv) if str(v).lstrip('-').isdigit())
                euler_chars.append(chi)
            except (ValueError, TypeError):
                pass
    if euler_chars:
        # For convex polytopes, Euler char should be 0 or 2 depending on convention
        # Test: is the distribution non-uniform?
        unique_vals, counts = np.unique(euler_chars, return_counts=True)
        chi2_stat = stats.chisquare(counts)[0]
        # Null: uniform across observed values
        null_chi2 = []
        for _ in range(2000):
            fake = rng.choice(unique_vals, size=len(euler_chars))
            _, fc = np.unique(fake, return_counts=True)
            if len(fc) == len(counts):
                null_chi2.append(stats.chisquare(fc)[0])
            else:
                null_chi2.append(0)
        null_chi2 = [x for x in null_chi2 if x > 0]
        if null_chi2:
            s, p_val, z = test_hypothesis("Polytope Euler characteristic non-uniform", chi2_stat, null_chi2)
            print(f"  H12: {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f} "
                  f"chi2={chi2_stat:.1f} unique_chi={list(unique_vals[:5])}")

    # ==================== BATCH 6: Cross-domain wild shots ====================
    print("\n--- BATCH 6: Cross-domain wild shots ---")

    # H13: Number fields with class number = knot determinant have unusual discriminants
    knot_dets_small = set(k.get("determinant", 0) for k in knots["knots"]
                          if k.get("determinant") and 0 < k["determinant"] < 100)
    nf_cn_is_det = [abs(int(f["disc_abs"])) for f in nf
                    if f.get("class_number") and int(f["class_number"]) in knot_dets_small and f.get("disc_abs")]
    nf_cn_not_det = [abs(int(f["disc_abs"])) for f in nf
                     if f.get("class_number") and int(f["class_number"]) not in knot_dets_small and f.get("disc_abs")]
    if nf_cn_is_det and nf_cn_not_det:
        real_d, null_d = permutation_test(
            np.log1p(nf_cn_is_det[:2000]).tolist(),
            np.log1p(nf_cn_not_det[:2000]).tolist()
        )
        s, p_val, z = test_hypothesis("NF disc: class_number in knot_dets vs not", real_d, null_d)
        print(f"  H13: {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f}")

    # H14: Space group point group orders match number field class group orders
    pg_order_set = set(sg.get("point_group_order", 0) for sg in spacegroups)
    nf_cn_in_pg = [abs(int(f["disc_abs"])) for f in nf
                   if f.get("class_number") and int(f["class_number"]) in pg_order_set and f.get("disc_abs")]
    nf_cn_not_pg = [abs(int(f["disc_abs"])) for f in nf
                    if f.get("class_number") and int(f["class_number"]) not in pg_order_set and f.get("disc_abs")]
    if nf_cn_in_pg and nf_cn_not_pg:
        real_d, null_d = permutation_test(
            np.log1p(nf_cn_in_pg[:2000]).tolist(),
            np.log1p(nf_cn_not_pg[:2000]).tolist()
        )
        s, p_val, z = test_hypothesis("NF disc: class_num in SG point_group_orders vs not", real_d, null_d)
        print(f"  H14: {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f}")

    # H15: Polytope vertex counts appear in OEIS-linked knot determinants
    poly_verts = set(p.get("N_VERTICES", 0) for p in polytopes if p.get("N_VERTICES"))
    knots_vert = [k["crossing_number"] for k in knots["knots"]
                  if k.get("determinant") in poly_verts and k.get("crossing_number")]
    knots_no_vert = [k["crossing_number"] for k in knots["knots"]
                     if k.get("determinant") not in poly_verts and k.get("crossing_number") and k.get("determinant")]
    if len(knots_vert) > 10 and len(knots_no_vert) > 10:
        real_d, null_d = permutation_test(knots_vert, knots_no_vert)
        s, p_val, z = test_hypothesis("Crossing: det in polytope_verts vs not", real_d, null_d)
        print(f"  H15: {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f}")

    # H16: MMLKG hub articles reference number-theoretic vs algebraic topics differently
    from search_engine import MMLKG_REFS
    import csv
    article_refs = {}
    with open(MMLKG_REFS, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 1:
                src = row[0]
                article_refs[src] = article_refs.get(src, 0) + 1
    # Split into high-ref and low-ref articles
    ref_counts = list(article_refs.values())
    if ref_counts:
        median_refs = np.median(ref_counts)
        hub_counts = [v for v in ref_counts if v > median_refs]
        leaf_counts = [v for v in ref_counts if v <= median_refs]
        real_d, null_d = permutation_test(hub_counts[:1000], leaf_counts[:1000])
        s, p_val, z = test_hypothesis("MMLKG: hub vs leaf reference density", real_d, null_d)
        print(f"  H16: {'SURVIVES' if s else 'KILLED':8s} p={p_val:.4f} z={z:.1f}")

    # ==================== SUMMARY ====================
    print()
    print("=" * 70)
    print(f"  GENOCIDE R5 COMPLETE: {kills} KILLED, {survives} SURVIVE out of {kills+survives}")
    print("=" * 70)
    print()
    for t in tests:
        marker = "***" if t["tag"] == "SURVIVES" else "   "
        print(f"  {marker} {t['tag']:8s} p={t['p']:.4f} z={t['z']:5.1f}  {t['name']}")

    # Classify survivors
    rediscoveries = [t for t in tests if t["tag"] == "SURVIVES" and any(
        kw in t["name"].lower() for kw in ["euler", "deuring", "stark", "known"])]
    novel = [t for t in tests if t["tag"] == "SURVIVES" and t not in rediscoveries]

    if rediscoveries:
        print(f"\n  Known math rediscoveries: {len(rediscoveries)}")
        for t in rediscoveries:
            print(f"    - {t['name']} (z={t['z']})")
    if novel:
        print(f"\n  Potentially novel survivors: {len(novel)}")
        for t in novel:
            print(f"    - {t['name']} (z={t['z']})")

    out = ROOT / "cartography" / "convergence" / "data" / "genocide_r5_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"kills": kills, "survives": survives, "tests": tests,
               "rediscoveries": len(rediscoveries), "novel": len(novel)},
              open(out, "w"), indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
