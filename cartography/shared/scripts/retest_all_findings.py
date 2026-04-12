#!/usr/bin/env python3
"""
Retest All Findings Through F1-F23 Unified Battery.

Runs the full battery on:
  - P1-P4 (Probable)
  - S1, S8 (Possible)
  - K1 (knot det SU(2) kill verification)
  - Isogeny diameter (Probable candidate)

Outputs structured logs + summary.
"""

import sys
import json
import numpy as np
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from battery_unified import UnifiedBattery, print_result

PYTHON = sys.executable
DATA_ROOT = Path(__file__).resolve().parent.parent.parent  # cartography/

ub = UnifiedBattery()


def load_json(relpath):
    fpath = DATA_ROOT / relpath
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)


def m4_m2_sq(values):
    v = np.array(values, dtype=float)
    v = v[np.isfinite(v) & (v != 0)]
    if len(v) < 10:
        return float("nan")
    vn = v / np.mean(v)
    m2 = np.mean(vn ** 2)
    m4 = np.mean(vn ** 4)
    return m4 / m2 ** 2 if m2 > 0 else float("nan")


# ============================================================
# P1: G2 conductor M4/M2^2 = USp(4) ≈ 3.0
# ============================================================
def test_P1():
    print("\n" + "=" * 70)
    print("P1: G2 conductor M4/M2^2 = USp(4)")
    print("=" * 70)

    g2 = load_json("genus2/data/genus2_curves_full.json")
    conductors = np.array([c["conductor"] for c in g2 if c.get("conductor")], dtype=float)
    conductors = conductors[conductors > 0]
    print(f"Loaded {len(conductors)} genus-2 conductors")

    # Filter to USp(4) Sato-Tate group only
    usp4_conds = np.array([c["conductor"] for c in g2
                           if c.get("st_group") == "USp(4)" and c.get("conductor")], dtype=float)
    usp4_conds = usp4_conds[usp4_conds > 0]
    print(f"USp(4) subset: {len(usp4_conds)} conductors")

    val = m4_m2_sq(usp4_conds) if len(usp4_conds) > 100 else m4_m2_sq(conductors)
    test_vals = usp4_conds if len(usp4_conds) > 100 else conductors
    print(f"M4/M2^2 = {val:.4f}")

    result = ub.test_distribution(
        finding_id="P1",
        claim="G2 USp(4) conductor M4/M2^2 = 3.0",
        values=test_vals,
        predicted_value=3.0,
        data_source=f"genus2_curves_full.json ({len(test_vals)} conductors)",
        domain_is_multiplicative=True,
        notes=f"M4/M2^2={val:.4f}",
    )
    print_result(result)
    return result


# ============================================================
# P2: Space group predicts Tc
# ============================================================
def test_P2():
    print("\n" + "=" * 70)
    print("P2: Space group predicts Tc (eta^2=0.45)")
    print("=" * 70)

    import csv
    csv_path = DATA_ROOT / "physics" / "data" / "superconductors" / "3DSC" / "superconductors_3D" / "data" / "final" / "MP" / "3DSC_MP.csv"
    if not csv_path.exists():
        print(f"SKIP: {csv_path} not found")
        return None

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        # Skip comment lines starting with #
        lines = []
        for line in f:
            if not line.startswith("#"):
                lines.append(line)
        import io
        reader = csv.DictReader(io.StringIO("".join(lines)))
        for row in reader:
            try:
                tc = float(row.get("tc", ""))
                sg = row.get("spacegroup_2", "")
                bg = row.get("band_gap_2", "")
                if tc > 0 and sg:
                    rows.append({"tc": tc, "sg": sg.strip(), "bg": float(bg) if bg else None})
            except (ValueError, TypeError):
                pass

    if len(rows) < 50:
        print(f"SKIP: only {len(rows)} valid rows")
        return None

    print(f"Loaded {len(rows)} superconductor records")

    # Eta-squared: SS_between / SS_total for Tc grouped by space group
    from collections import defaultdict
    sg_groups = defaultdict(list)
    for r in rows:
        sg_groups[r["sg"]].append(r["tc"])

    all_tc = [r["tc"] for r in rows]
    grand_mean = np.mean(all_tc)
    ss_total = sum((t - grand_mean) ** 2 for t in all_tc)
    ss_between = sum(len(vals) * (np.mean(vals) - grand_mean) ** 2
                     for vals in sg_groups.values() if len(vals) >= 2)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0
    print(f"Eta^2 (SG->Tc) = {eta_sq:.4f}")

    # Also check band gap
    bg_vals = [r for r in rows if r["bg"] is not None]
    if bg_vals:
        bg_groups = defaultdict(list)
        for r in bg_vals:
            bg_groups[r["sg"]].append(r["bg"])
        bg_all = [r["bg"] for r in bg_vals]
        bg_gm = np.mean(bg_all)
        bg_sst = sum((b - bg_gm) ** 2 for b in bg_all)
        bg_ssb = sum(len(v) * (np.mean(v) - bg_gm) ** 2 for v in bg_groups.values() if len(v) >= 2)
        bg_eta = bg_ssb / bg_sst if bg_sst > 0 else 0
        print(f"Eta^2 (SG->BandGap) = {bg_eta:.4f}")

    tc_array = np.array(all_tc)
    sg_labels = [r["sg"] for r in rows]
    # Encode string labels as integers for confound test
    unique_sgs = sorted(set(sg_labels))
    sg_map = {s: i for i, s in enumerate(unique_sgs)}
    sg_array = np.array([sg_map[s] for s in sg_labels])

    result = ub.test_distribution(
        finding_id="P2",
        claim="Space group predicts Tc (eta^2 large) but NOT band gap",
        values=tc_array,
        data_source=f"3DSC_MP.csv ({len(rows)} records)",
        group_labels=sg_labels,
        confound_values=np.log1p(np.abs(tc_array)),  # self-confound check
        notes=f"eta^2={eta_sq:.4f}",
    )
    print_result(result)
    return result


# ============================================================
# P4 + S8: Galois group enrichment on class numbers
# ============================================================
def test_P4_S8():
    print("\n" + "=" * 70)
    print("P4/S8: Galois enrichment on class number (MAX not multiplicative)")
    print("=" * 70)

    nf = load_json("number_fields/data/number_fields.json")
    print(f"Loaded {len(nf)} number fields")

    # Extract class numbers and Galois labels
    valid = [f for f in nf if f.get("class_number") and f.get("galois_label") and f.get("degree")]
    print(f"Valid (have class_number + galois + degree): {len(valid)}")

    from collections import defaultdict

    # Enrichment by Galois group
    galois_groups = defaultdict(list)
    for f in valid:
        galois_groups[f["galois_label"]].append(f["class_number"])

    all_cn = np.array([f["class_number"] for f in valid], dtype=float)

    # Compute within-group vs across-group distance
    rng = np.random.default_rng(42)
    within_dists, across_dists = [], []
    for label, vals in galois_groups.items():
        vals = np.array(vals, dtype=float)
        if len(vals) >= 3:
            for _ in range(min(50, len(vals))):
                i, j = rng.choice(len(vals), 2, replace=False)
                within_dists.append(abs(vals[i] - vals[j]))

    for _ in range(len(within_dists)):
        i, j = rng.choice(len(all_cn), 2, replace=False)
        across_dists.append(abs(all_cn[i] - all_cn[j]))

    enrichment = np.mean(across_dists) / np.mean(within_dists) if np.mean(within_dists) > 0 else 0
    print(f"Galois enrichment: {enrichment:.2f}x")

    # Also by degree
    degree_groups = defaultdict(list)
    for f in valid:
        degree_groups[f["degree"]].append(f["class_number"])

    deg_within = []
    for deg, vals in degree_groups.items():
        vals = np.array(vals, dtype=float)
        if len(vals) >= 3:
            for _ in range(min(50, len(vals))):
                i, j = rng.choice(len(vals), 2, replace=False)
                deg_within.append(abs(vals[i] - vals[j]))

    deg_enrichment = np.mean(across_dists) / np.mean(deg_within) if np.mean(deg_within) > 0 else 0
    print(f"Degree enrichment: {deg_enrichment:.2f}x")
    print(f"MAX test: Galois {enrichment:.2f}x vs Degree {deg_enrichment:.2f}x -> {'MAX holds' if abs(enrichment - max(enrichment, deg_enrichment)) < 0.1 else 'CHECK'}")

    # Use within/across as paired arrays for correlation test
    w = np.array(within_dists[:1000], dtype=float)
    a = np.array(across_dists[:1000], dtype=float)

    galois_labels = np.array([f["galois_label"] for f in valid])
    confound_degrees = np.array([f["degree"] for f in valid], dtype=float)

    result = ub.test_distribution(
        finding_id="P4_S8",
        claim=f"Galois enrichment {enrichment:.2f}x on class number, MAX not multiplicative",
        values=all_cn,
        data_source=f"number_fields.json ({len(valid)} fields)",
        group_labels=galois_labels,
        confound_values=confound_degrees,
        notes=f"galois={enrichment:.2f}x, degree={deg_enrichment:.2f}x",
    )
    print_result(result)
    return result


# ============================================================
# K1 / S1-related: Knot determinant M4/M2^2
# ============================================================
def test_knot_det():
    print("\n" + "=" * 70)
    print("K1: Knot determinant M4/M2^2 (SU(2)=2.0 kill verification)")
    print("=" * 70)

    knots_data = load_json("knots/data/knots.json")
    knots = knots_data["knots"]  # list of dicts inside "knots" key
    dets = np.array([k["determinant"] for k in knots if k.get("determinant")], dtype=float)
    dets = dets[dets > 0]
    print(f"Loaded {len(dets)} knot determinants")

    val = m4_m2_sq(dets)
    print(f"M4/M2^2 = {val:.4f}")

    result = ub.test_distribution(
        finding_id="K1",
        claim="Knot determinant M4/M2^2 ≈ SU(2) = 2.0",
        values=dets,
        predicted_value=2.0,
        data_source=f"knots.json ({len(dets)} determinants)",
        notes=f"M4/M2^2={val:.4f}, testing kill of SU(2) match",
    )
    print_result(result)
    return result


# ============================================================
# Isogeny diameter ~ 1.80·log(n)
# ============================================================
def test_isogeny():
    print("\n" + "=" * 70)
    print("ISOGENY: Diameter ~ 1.80·log(n) (Ramanujan expander)")
    print("=" * 70)

    iso_dir = DATA_ROOT / "isogenies" / "data" / "graphs"
    if not iso_dir.exists():
        print(f"SKIP: {iso_dir} not found")
        return None

    primes = []
    diameters = []
    nodes_list = []
    for pdir in sorted(iso_dir.iterdir()):
        if not pdir.is_dir():
            continue
        meta_file = pdir / f"{pdir.name}_metadata.json"
        if not meta_file.exists():
            continue
        try:
            with open(meta_file) as f:
                meta = json.load(f)
            p = int(pdir.name)
            # Get ell=2 diameter
            ell_data = meta.get("ell", meta.get("2", {}))
            if isinstance(ell_data, dict):
                d = ell_data.get("2", {}).get("diameter") if "2" in ell_data else ell_data.get("diameter")
            else:
                d = None
            n = meta.get("nodes") or meta.get("num_nodes") or meta.get("n_nodes")
            if d is not None and n is not None and n > 0:
                primes.append(p)
                diameters.append(d)
                nodes_list.append(n)
        except Exception:
            pass

    if len(primes) < 20:
        print(f"SKIP: only {len(primes)} primes with diameter data")
        return None

    primes = np.array(primes, dtype=float)
    diameters = np.array(diameters, dtype=float)
    nodes_arr = np.array(nodes_list, dtype=float)
    log_nodes = np.log(nodes_arr)

    from scipy.stats import linregress
    slope, intercept, r, p, se = linregress(log_nodes, diameters)
    print(f"Loaded {len(primes)} primes")
    print(f"diameter ~ {slope:.3f}·log(n) + {intercept:.3f}, R²={r**2:.3f}")

    result = ub.test_correlation(
        finding_id="ISOGENY",
        claim=f"Isogeny ell=2 diameter ~ {slope:.2f}·log(n), Ramanujan expander",
        values_a=log_nodes,
        values_b=diameters,
        data_source=f"isogeny graphs ({len(primes)} primes)",
        notes=f"slope={slope:.3f}, R²={r**2:.3f}",
    )
    print_result(result)
    return result


# ============================================================
# Run all
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("RETEST ALL FINDINGS — Full F1-F23 Battery")
    print("=" * 70)

    results = {}
    for name, fn in [
        ("P1", test_P1),
        ("P2", test_P2),
        ("P4_S8", test_P4_S8),
        ("K1_knot_det", test_knot_det),
        ("ISOGENY", test_isogeny),
    ]:
        try:
            results[name] = fn()
        except Exception as e:
            print(f"\n*** ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = None

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, r in results.items():
        if r is None:
            print(f"  {name:15s}: SKIPPED/ERROR")
        else:
            v = r["overall"]["verdict"]
            tier = r["overall"].get("tier", "?")
            kills = r["overall"].get("kills", [])
            print(f"  {name:15s}: {v:15s} (tier: {tier})" + (f" KILLED BY: {kills}" if kills else ""))

    # Log summary
    ub.logger.summary()
