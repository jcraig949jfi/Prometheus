"""
Genocide Round 3: WILD EDITION
================================
The ferryman ferries hypotheses across the Styx.
Most don't come back. The ones that do are real.

This round: weird cross-domain tests, forbidden combinations,
things nobody would think to test. Let Charon get creative.
"""

import json, math, numpy as np
from scipy import stats
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

rng = np.random.RandomState(777)
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
    print(f"  {'***' if s else '   '} {tag:8s} p={p:.4f} z={z:5.1f}  {name}")
    return s


def perm(a, b, n=3000):
    real_d = abs(np.mean(a) - np.mean(b))
    c = list(a) + list(b)
    null = [];
    for _ in range(n):
        rng.shuffle(c)
        null.append(abs(np.mean(c[:len(a)]) - np.mean(c[len(a):])))
    return real_d, null


def main():
    global kills, survives

    knots = json.loads((ROOT / "cartography/knots/data/knots.json").read_text(encoding="utf-8"))
    fungrim = json.loads((ROOT / "cartography/fungrim/data/fungrim_index.json").read_text(encoding="utf-8"))
    antedb = json.loads((ROOT / "cartography/antedb/data/antedb_index.json").read_text(encoding="utf-8"))

    from search_engine import _get_duck, _load_mathlib, _mathlib_graph, MATHLIB_GRAPH
    con = _get_duck()
    ec_rows = con.execute("""SELECT conductor, json_extract_string(properties, '$.rank') as rank
        FROM objects WHERE object_type = 'elliptic_curve' AND conductor <= 5000""").fetchall()
    mf_rows = con.execute("""SELECT conductor FROM objects WHERE object_type = 'modular_form' AND conductor <= 5000""").fetchall()
    con.close()

    _load_mathlib()
    from collections import defaultdict
    adj = defaultdict(set)
    for edge in _mathlib_graph.get("edges", []):
        if isinstance(edge, (list, tuple)) and len(edge) >= 2:
            adj[str(edge[0])].add(str(edge[1]))
            adj[str(edge[1])].add(str(edge[0]))

    conds_r0 = [int(r[0]) for r in ec_rows if r[1] == "0"]
    conds_r1 = [int(r[0]) for r in ec_rows if r[1] == "1"]
    mf_conds = [int(r[0]) for r in mf_rows]

    print("=" * 70)
    print("  GENOCIDE R3: WILD EDITION")
    print("  The ferryman ferries hypotheses across the Styx.")
    print("  Most don't come back.")
    print("=" * 70)

    # ============================================================
    # SECTION 1: FORBIDDEN CROSS-DOMAIN (the weird ones)
    # ============================================================
    print("\n--- FORBIDDEN CROSS-DOMAIN ---")

    # W1: Do knot determinants that are ALSO modular form levels behave differently?
    mf_cond_set = set(mf_conds)
    knots_in_mf = [k for k in knots["knots"] if k.get("determinant") in mf_cond_set and k.get("alex_coeffs")]
    knots_not_mf = [k for k in knots["knots"] if k.get("determinant") and k["determinant"] not in mf_cond_set
                    and k.get("alex_coeffs") and k["determinant"] >= 11]
    if knots_in_mf and knots_not_mf:
        alex_in = [len(k["alex_coeffs"]) for k in knots_in_mf]
        alex_out = [len(k["alex_coeffs"]) for k in knots_not_mf]
        r, n = perm(alex_in, alex_out)
        test("Alex poly length: det-is-MF-level vs not", r, n)

    # W2: Fungrim formula count per topic correlates with ANTEDB theorem count per topic
    fungrim_topics = fungrim.get("module_stats", {})
    antedb_topics = {ch["chapter"]: ch["n_theorems"] for ch in antedb["chapters"]}
    # Find overlapping topic words
    shared_topics = []
    for ft, fc in fungrim_topics.items():
        for at, ac in antedb_topics.items():
            if ft.lower() in at.lower() or at.lower() in ft.lower():
                shared_topics.append((fc, ac))
    if len(shared_topics) > 5:
        f_counts, a_counts = zip(*shared_topics)
        real_r = abs(stats.spearmanr(f_counts, a_counts)[0])
        null_r = [abs(stats.spearmanr(f_counts, rng.permutation(a_counts))[0]) for _ in range(3000)]
        test("Fungrim module size ~ ANTEDB chapter size (shared topics)", real_r, null_r)
    else:
        print(f"   SKIP  Fungrim~ANTEDB topic correlation (only {len(shared_topics)} shared topics)")

    # W3: mathlib degree distribution exponent ~ Fungrim module size distribution exponent
    degrees = [len(adj[n]) for n in adj if len(adj[n]) > 0]
    mod_sizes = sorted(fungrim["module_stats"].values(), reverse=True)
    if degrees and mod_sizes:
        # Both should follow power laws — do they have the same exponent?
        from scipy.optimize import curve_fit
        def power(x, a, b): return a * np.power(x, b)

        # Degree distribution
        deg_counts = np.bincount(degrees)[1:]  # skip 0
        deg_x = np.arange(1, len(deg_counts)+1, dtype=float)
        deg_y = deg_counts.astype(float)
        mask_d = deg_y > 0
        if mask_d.sum() > 3:
            slope_d = np.polyfit(np.log(deg_x[mask_d]), np.log(deg_y[mask_d]), 1)[0]
        else:
            slope_d = 0

        # Module size distribution
        ranks_m = np.arange(1, len(mod_sizes)+1, dtype=float)
        slope_m = np.polyfit(np.log(ranks_m), np.log(np.array(mod_sizes, dtype=float)+0.1), 1)[0]

        print(f"   INFO  mathlib degree slope={slope_d:.2f}, Fungrim module slope={slope_m:.2f}, diff={abs(slope_d-slope_m):.2f}")
        # Null: is the difference smaller than random?
        null_diffs = []
        for _ in range(1000):
            rng.shuffle(degrees)
            dc = np.bincount(degrees[:len(degrees)//2])[1:]
            dx = np.arange(1, len(dc)+1, dtype=float)
            dy = dc.astype(float)
            m = dy > 0
            if m.sum() > 3:
                s_null = np.polyfit(np.log(dx[m]), np.log(dy[m]), 1)[0]
                null_diffs.append(abs(slope_d - s_null))
        if null_diffs:
            real_diff = abs(slope_d - slope_m)
            test("mathlib~Fungrim power-law exponent similarity", -real_diff, [-d for d in null_diffs])

    # ============================================================
    # SECTION 2: NUMERICAL COINCIDENCES (test them properly)
    # ============================================================
    print("\n--- NUMERICAL COINCIDENCES ---")

    # W4: Is the number of knots per crossing number a known OEIS sequence?
    crossing_counts = {}
    for k in knots["knots"]:
        c = k.get("crossing_number", 0)
        if c > 0:
            crossing_counts[c] = crossing_counts.get(c, 0) + 1
    cc_seq = [crossing_counts.get(i, 0) for i in range(3, 13)]
    print(f"   INFO  Knots per crossing (3-12): {cc_seq}")
    # This IS a known OEIS sequence (A002863 etc.) — checking is validation

    # W5: EC count per conductor follows Poisson?
    ec_per_cond = defaultdict(int)
    for r in ec_rows:
        ec_per_cond[int(r[0])] += 1
    counts = list(ec_per_cond.values())
    # Poisson test: is the variance/mean ratio near 1?
    vm_ratio = np.var(counts) / np.mean(counts)
    print(f"   INFO  EC per conductor: mean={np.mean(counts):.2f}, var={np.var(counts):.2f}, var/mean={vm_ratio:.2f}")
    # If Poisson, var/mean ≈ 1. If clustered, var/mean > 1.
    # Chi-squared test for Poisson
    expected_poisson = [stats.poisson.pmf(k, np.mean(counts)) * len(counts) for k in range(max(counts)+1)]
    observed = np.bincount(counts, minlength=max(counts)+1)
    # Truncate to where expected > 5
    valid = np.array(expected_poisson) > 5
    if valid.sum() > 3:
        # Scale expected to match observed sum
        exp_arr = np.array(expected_poisson)[valid]
        obs_arr = observed[valid].astype(float)
        exp_arr = exp_arr * obs_arr.sum() / exp_arr.sum()
        chi2, p_chi = stats.chisquare(obs_arr, exp_arr)
        s = p_chi < 0.01
        if s: survives += 1
        else: kills += 1
        tests.append({"name": "EC per conductor is NOT Poisson", "tag": "SURVIVES" if s else "KILLED",
                      "p": round(p_chi, 4), "z": 0})
        print(f"  {'***' if s else '   '} {'SURVIVES' if s else 'KILLED':8s} p={p_chi:.4f}  EC per conductor is NOT Poisson (var/mean={vm_ratio:.2f})")

    # ============================================================
    # SECTION 3: INFORMATION-THEORETIC (entropy-based)
    # ============================================================
    print("\n--- INFORMATION-THEORETIC ---")

    # W6: Shannon entropy of Alexander polynomial coefficients differs by crossing number
    for cn in [7, 8, 9, 10]:
        coeffs_cn = []
        for k in knots["knots"]:
            if k.get("crossing_number") == cn and k.get("alex_coeffs"):
                # Normalize coefficients to probability distribution
                ac = np.array(k["alex_coeffs"], dtype=float)
                ac_abs = np.abs(ac) + 0.01
                p_dist = ac_abs / ac_abs.sum()
                entropy = -np.sum(p_dist * np.log2(p_dist))
                coeffs_cn.append(entropy)

        other_cn = []
        for k in knots["knots"]:
            if k.get("crossing_number") != cn and k.get("crossing_number", 0) > 0 and k.get("alex_coeffs"):
                ac = np.array(k["alex_coeffs"], dtype=float)
                ac_abs = np.abs(ac) + 0.01
                p_dist = ac_abs / ac_abs.sum()
                entropy = -np.sum(p_dist * np.log2(p_dist))
                other_cn.append(entropy)

        if len(coeffs_cn) > 5 and other_cn:
            r, n = perm(coeffs_cn, other_cn)
            test(f"Alexander entropy differs for crossing={cn}", r, n)

    # W7: Conductor entropy differs by rank
    # Treat digits of conductor as a distribution
    def digit_entropy(n):
        digits = [int(d) for d in str(abs(int(n))) if d.isdigit()]
        if not digits: return 0
        counts = np.bincount(digits, minlength=10).astype(float)
        counts += 0.01
        p = counts / counts.sum()
        return -np.sum(p * np.log2(p))

    ent_r0 = [digit_entropy(c) for c in conds_r0[:3000]]
    ent_r1 = [digit_entropy(c) for c in conds_r1[:3000]]
    r, n = perm(ent_r0, ent_r1)
    test("Conductor digit entropy: rank-0 vs rank-1", r, n)

    # ============================================================
    # SECTION 4: GRAPH-THEORETIC (mathlib structure)
    # ============================================================
    print("\n--- GRAPH-THEORETIC ---")

    # W8: NumberTheory modules have higher clustering coefficient than average
    nodes = list(adj.keys())
    nt_nodes = [n for n in nodes if "numbertheory" in n.lower()]
    other_nodes = [n for n in nodes if "numbertheory" not in n.lower() and len(adj[n]) > 1]

    def local_clustering(node):
        neighbors = list(adj[node])
        if len(neighbors) < 2: return 0
        edges = sum(1 for i in range(len(neighbors)) for j in range(i+1, len(neighbors))
                    if neighbors[j] in adj[neighbors[i]])
        return 2 * edges / (len(neighbors) * (len(neighbors) - 1))

    nt_cc = [local_clustering(n) for n in nt_nodes if len(adj[n]) > 1]
    ot_cc = [local_clustering(n) for n in other_nodes[:200]]
    if nt_cc and ot_cc:
        r, n = perm(nt_cc, ot_cc)
        test("NumberTheory has higher clustering coefficient", r, n)

    # W9: Hub degree in mathlib correlates with Fungrim module size
    # Top mathlib hubs → do their topic names match Fungrim's biggest modules?
    top_hubs = sorted(adj.keys(), key=lambda x: -len(adj[x]))[:20]
    hub_topics = []
    for h in top_hubs:
        parts = h.split(".")
        topic = parts[-1].lower() if parts else ""
        hub_topics.append(topic)
    # Check if any hub topics are also Fungrim module names
    fungrim_mods = set(fungrim["module_stats"].keys())
    overlap = sum(1 for t in hub_topics if t in fungrim_mods)
    # Null: random mathlib modules
    null_overlap = []
    all_nodes = list(adj.keys())
    for _ in range(3000):
        random_hubs = rng.choice(all_nodes, 20, replace=False)
        random_topics = [h.split(".")[-1].lower() for h in random_hubs]
        null_overlap.append(sum(1 for t in random_topics if t in fungrim_mods))
    test("mathlib hub topics match Fungrim modules", overlap, null_overlap)

    # ============================================================
    # SECTION 5: THE TRULY WILD (cross-everything)
    # ============================================================
    print("\n--- THE TRULY WILD ---")

    # W10: Sum of digits of knot determinant correlates with Alexander poly length
    dig_sums = []
    alex_lens = []
    for k in knots["knots"]:
        if k.get("determinant") and k["determinant"] > 0 and k.get("alex_coeffs"):
            dig_sums.append(sum(int(d) for d in str(k["determinant"])))
            alex_lens.append(len(k["alex_coeffs"]))
    if dig_sums:
        real_r = abs(stats.spearmanr(dig_sums, alex_lens)[0])
        null_r = [abs(stats.spearmanr(dig_sums, rng.permutation(alex_lens))[0]) for _ in range(3000)]
        test("Digit sum of determinant ~ Alexander length", real_r, null_r)

    # W11: Number of EC with conductor N correlates with number of MF with level N
    shared_N = set(ec_per_cond.keys()) & set(int(r[0]) for r in mf_rows)
    if len(shared_N) > 50:
        ec_counts = [ec_per_cond[n] for n in sorted(shared_N)]
        mf_per_level = defaultdict(int)
        for r in mf_rows:
            mf_per_level[int(r[0])] += 1
        mf_counts = [mf_per_level[n] for n in sorted(shared_N)]
        real_r = abs(stats.spearmanr(ec_counts, mf_counts)[0])
        null_r = [abs(stats.spearmanr(ec_counts, rng.permutation(mf_counts))[0]) for _ in range(3000)]
        test("EC count per N ~ MF count per N", real_r, null_r)

    # W12: ANTEDB theorem count per chapter correlates with chapter name length
    ch_lens = [len(ch["chapter"]) for ch in antedb["chapters"] if ch["n_theorems"] > 0]
    ch_thms = [ch["n_theorems"] for ch in antedb["chapters"] if ch["n_theorems"] > 0]
    if len(ch_lens) > 5:
        real_r = abs(stats.spearmanr(ch_lens, ch_thms)[0])
        null_r = [abs(stats.spearmanr(ch_lens, rng.permutation(ch_thms))[0]) for _ in range(3000)]
        test("ANTEDB: chapter name length ~ theorem count", real_r, null_r)

    # W13: Knot determinant mod 3 predicts whether Alexander poly has even or odd number of terms
    det_mod3 = []
    alex_parity = []
    for k in knots["knots"]:
        if k.get("determinant") and k["determinant"] > 0 and k.get("alex_coeffs"):
            det_mod3.append(k["determinant"] % 3)
            alex_parity.append(len(k["alex_coeffs"]) % 2)
    if det_mod3:
        try:
            chi2, p_chi = stats.chi2_contingency([
                [sum(1 for d, a in zip(det_mod3, alex_parity) if d == dm and a == ap)
                 for ap in [0, 1]]
                for dm in [0, 1, 2]
            ])[:2]
            s = p_chi < 0.01
            if s: survives += 1
            else: kills += 1
            tests.append({"name": "det mod 3 ~ Alex parity", "tag": "SURVIVES" if s else "KILLED",
                          "p": round(p_chi, 4), "z": 0})
            print(f"  {'***' if s else '   '} {'SURVIVES' if s else 'KILLED':8s} p={p_chi:.4f}  det mod 3 predicts Alexander parity")
        except:
            print("   SKIP  det mod 3 ~ Alex parity (contingency table issue)")

    # ============================================================
    # SUMMARY
    # ============================================================
    print()
    print("=" * 70)
    print(f"  CHARON'S FERRY: {kills} didn't make it back, {survives} survived the crossing")
    print("=" * 70)
    print()
    for t in tests:
        m = "***" if t["tag"] == "SURVIVES" else "   "
        print(f"  {m} {t['tag']:8s} p={t['p']:.4f}  {t['name']}")

    json.dump({"kills": kills, "survives": survives, "tests": tests},
              open(str(ROOT / "cartography/convergence/data/genocide_r3_results.json"), "w"), indent=2)

    print(f"\n  Total ferried: {kills + survives}")
    print(f"  Lost in the Styx: {kills}")
    print(f"  Returned with cargo: {survives}")


if __name__ == "__main__":
    main()
