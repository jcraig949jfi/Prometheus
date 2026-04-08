"""
Genocide Round 7 — Round 3 triage of overnight survivors.
==========================================================
13 hypotheses survived two rounds of triage. Kill them properly.
"""

import json
import math
import os
import sys
import numpy as np
from scipy import stats
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))

rng = np.random.RandomState(42)

kills = 0
survives_count = 0
results = []


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def permutation_p(real_stat, null_stats):
    na = np.array(null_stats)
    return (np.sum(na >= real_stat) + 1) / (len(null_stats) + 1)


def verdict(name, passed, detail=""):
    global kills, survives_count
    if passed:
        survives_count += 1
        print(f"  *** SURVIVES: {name}")
    else:
        kills += 1
        print(f"      KILLED:   {name}")
    if detail:
        print(f"                {detail}")
    results.append({"name": name, "survived": passed, "detail": detail})


def main():
    from search_engine import (
        _load_oeis, _oeis_cache, _load_oeis_names, _oeis_names_cache,
        _load_oeis_crossrefs, _oeis_xref_cache, _oeis_xref_reverse
    )

    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    print("=" * 70)
    print("  ROUND 3 GENOCIDE - 13 survivors from overnight run")
    print("=" * 70)

    knots = json.loads((ROOT / "cartography/knots/data/knots.json").read_text(encoding="utf-8"))
    antedb = json.loads((ROOT / "cartography/antedb/data/antedb_index.json").read_text(encoding="utf-8"))
    materials = json.loads((ROOT / "cartography/physics/data/materials_project_1000.json").read_text(encoding="utf-8"))

    bilbao_dir = ROOT / "cartography/physics/data/bilbao"
    sg_wyckoff = {}
    sg_pgorder = {}
    for sg_file in sorted(bilbao_dir.glob("sg_*.json")):
        try:
            sg = json.loads(sg_file.read_text(encoding="utf-8"))
            sgn = sg.get("space_group_number", 0)
            sg_wyckoff[sgn] = sg.get("num_wyckoff_positions", 0)
            sg_pgorder[sgn] = int(sg.get("point_group_order", 0))
        except:
            pass

    # ================================================================
    # S1: f-vector sums for 3D polytopes
    # ================================================================
    print("\n--- S1: Polytope f-vector structure ---")
    poly_dir = ROOT / "cartography/polytopes/data"
    fvecs_3d = []
    for jf in sorted(poly_dir.glob("*.json")):
        if jf.name == "manifest.json":
            continue
        try:
            entries = json.loads(jf.read_text(encoding="utf-8"))
            for e in entries:
                if isinstance(e, dict) and e.get("DIM") == 3 and e.get("F_VECTOR"):
                    try:
                        fvecs_3d.append([int(x) for x in e["F_VECTOR"]])
                    except (ValueError, TypeError):
                        pass
        except:
            pass

    if len(fvecs_3d) > 10:
        sums = [sum(fv) for fv in fvecs_3d]
        # Euler relation: V - E + F = 2. So sum = V + E + F = (E + 2) + E = 2E + 2
        # This means f-vector sums are ALWAYS even and >= 6. That is structure.
        all_even = all(s % 2 == 0 for s in sums)
        verdict("Polytope f-vector sums have non-trivial distribution",
                all_even,
                f"All even: {all_even} (Euler relation forces V+E+F = 2E+2). n={len(sums)}, range=[{min(sums)},{max(sums)}]. REDISCOVERY of Euler relation.")
    else:
        verdict("Polytope f-vector sums", False, "Insufficient 3D polytope data")

    # ================================================================
    # S2-3: Wildly ramified extensions ~ knot invariants
    # ================================================================
    print("\n--- S2-3: Ramification bridges ---")
    verdict("Wildly ramified Q3/S3 discriminants ~ knot invariants",
            False, "KILLED: Local field data is PARI/GP format, discriminants not parsed. Untestable.")
    verdict("Wildly ramified Q2 degree-6 valuations mod 3 ~ knot dets",
            False, "KILLED: Same data limitation.")

    # ================================================================
    # S4: Sleeper terms = zeta(n) for integer n
    # ================================================================
    print("\n--- S4: Sleeper terms contain zeta values ---")
    verdict("Sleeper terms = zeta(n) for integer n",
            False, "KILLED: zeta(n) for n>=2 are irrational. Integer sequences cannot contain them.")

    # ================================================================
    # S5-6: Crystal physics
    # ================================================================
    print("\n--- S5-6: Crystal physics ---")

    # Band gap ~ symmetry operations
    semi_ops = []
    other_ops = []
    for m in materials:
        if not isinstance(m, dict):
            continue
        bg = m.get("band_gap")
        sg_num = m.get("spacegroup", {}).get("number") if isinstance(m.get("spacegroup"), dict) else None
        if sg_num is None or bg is None:
            continue
        pgo = sg_pgorder.get(sg_num, 0)
        if pgo == 0:
            continue
        if 1.0 <= bg <= 2.0:
            semi_ops.append(pgo)
        elif bg > 2.0 or bg < 0.1:
            other_ops.append(pgo)

    if len(semi_ops) >= 10 and len(other_ops) >= 10:
        real_d = abs(np.mean(semi_ops) - np.mean(other_ops))
        combined = list(semi_ops) + list(other_ops)
        null_d = []
        for _ in range(2000):
            rng.shuffle(combined)
            null_d.append(abs(np.mean(combined[:len(semi_ops)]) - np.mean(combined[len(semi_ops):])))
        p = permutation_p(real_d, null_d)
        verdict("Band gap 1-2eV ~ SG symmetry operations",
                p < 0.01,
                f"semi={np.mean(semi_ops):.1f}, other={np.mean(other_ops):.1f}, p={p:.4f}, n={len(semi_ops)}+{len(other_ops)}")
    else:
        verdict("Band gap 1-2eV ~ SG symmetry operations",
                False, f"Insufficient data (semi={len(semi_ops)}, other={len(other_ops)})")

    # Cubic SG frequency in materials
    cubic_count = sum(1 for m in materials if isinstance(m, dict) and m.get("crystal_system") == "cubic")
    total_count = sum(1 for m in materials if isinstance(m, dict) and m.get("crystal_system"))
    cubic_rate = cubic_count / max(total_count, 1)
    # 36/230 = 15.7% of SGs are cubic. Is the material rate different?
    expected_rate = 36 / 230
    verdict("Cubic SG frequency ~ material properties",
            abs(cubic_rate - expected_rate) > 0.05,
            f"Cubic materials: {cubic_count}/{total_count} = {cubic_rate:.3f}. Expected from SG count: {expected_rate:.3f}. "
            f"{'SURVIVES: Materials prefer cubic (rock salt, diamond, perovskite).' if cubic_rate > expected_rate + 0.05 else 'KILLED: Rate matches SG base rate.'}")

    # ================================================================
    # S7-8: Dirichlet L-values
    # ================================================================
    print("\n--- S7-8: L-function values ---")
    verdict("Dirichlet L(1) for real quadratic chars in OEIS",
            False, "KILLED: L(1,chi) values are irrational (involve pi). Cannot be integer sequence terms.")
    verdict("Dirichlet L(2) distribution ~ crystal system frequencies",
            False, "KILLED: L(2,chi) values are irrational. Crystal frequencies are integers. Type mismatch.")

    # ================================================================
    # S9: Sleepers ~ ANTEDB bounds
    # ================================================================
    print("\n--- S9: Sleepers matching ANTEDB bounds ---")
    verdict("Sleeper terms match ANTEDB exponent bounds",
            False, "KILLED: ANTEDB exponents are fractions (0.5, 0.333...). Sleeper terms are integers.")

    # ================================================================
    # S10-11: Local fields ~ other domains
    # ================================================================
    print("\n--- S10-11: Local fields bridges ---")
    verdict("Local fields p=2 discriminants ~ EC conductors",
            False, "KILLED: Both involve powers of 2 by definition. Tautological.")
    verdict("Local fields p=5 prime factors subset of ANTEDB",
            False, "KILLED: Local fields at p=5 have 5 in discriminants. ANTEDB references all small primes. Trivial.")

    # ================================================================
    # S12: Knot det sequences and exponential growth
    # ================================================================
    print("\n--- S12: Growth classification of knot-det sequences ---")
    knot_dets = set(k.get("determinant", 0) for k in knots["knots"] if k.get("determinant"))

    contains_det = 0
    contains_det_exp = 0
    not_det = 0
    not_det_exp = 0

    for seq_id, terms in list(_oeis_cache.items())[:50000]:
        if len(terms) < 10:
            continue
        has_det = any(t in knot_dets for t in terms[:20] if isinstance(t, int))

        pos = [t for t in terms[:20] if isinstance(t, (int, float)) and t > 0]
        if len(pos) < 5:
            continue
        ratios = [pos[i + 1] / pos[i] for i in range(len(pos) - 1) if pos[i] > 0]
        if not ratios:
            continue
        avg_ratio = np.mean(ratios)
        is_exp = 1.5 < avg_ratio < 10

        if has_det:
            contains_det += 1
            if is_exp:
                contains_det_exp += 1
        else:
            not_det += 1
            if is_exp:
                not_det_exp += 1

    if contains_det > 20 and not_det > 20:
        rate_det = contains_det_exp / contains_det
        rate_nodet = not_det_exp / not_det
        real_diff = abs(rate_det - rate_nodet)
        # Permutation test
        all_exp_flags = ([1] * contains_det_exp + [0] * (contains_det - contains_det_exp) +
                         [1] * not_det_exp + [0] * (not_det - not_det_exp))
        all_group = [1] * contains_det + [0] * not_det
        null_diffs = []
        for _ in range(2000):
            rng.shuffle(all_group)
            g1 = [all_exp_flags[i] for i in range(len(all_group)) if all_group[i] == 1]
            g2 = [all_exp_flags[i] for i in range(len(all_group)) if all_group[i] == 0]
            if g1 and g2:
                null_diffs.append(abs(np.mean(g1) - np.mean(g2)))
        p = permutation_p(real_diff, null_diffs)
        verdict("Sequences with knot dets more often exponential",
                p < 0.01,
                f"det_rate={rate_det:.3f}, no_det_rate={rate_nodet:.3f}, diff={real_diff:.4f}, p={p:.4f}, n={contains_det}+{not_det}")
    else:
        verdict("Sequences with knot dets more often exponential", False, "Insufficient data")

    # ================================================================
    # S13: L(2) values = knot dets
    # ================================================================
    print("\n--- S13: L(2) values = knot dets ---")
    verdict("Dirichlet L(2) values subset of knot dets",
            False, "KILLED: L(2,chi) values are irrational. Knot dets are integers.")

    # ================================================================
    # SUMMARY
    # ================================================================
    print()
    print("=" * 70)
    print(f"  ROUND 3 COMPLETE: {kills} KILLED, {survives_count} SURVIVE out of {kills + survives_count}")
    print("=" * 70)
    print()
    for r in results:
        marker = "***" if r["survived"] else "   "
        tag = "SURVIVES" if r["survived"] else "KILLED"
        print(f"  {marker} {tag:8s} {r['name']}")

    out = ROOT / "cartography/convergence/data/genocide_r7_results.json"
    json.dump({"kills": kills, "survives": survives_count, "results": results}, open(out, "w"), indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
