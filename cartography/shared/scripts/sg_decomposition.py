#!/usr/bin/env python3
"""Decompose space group into components and test each on Tc."""

import sys, csv, io, numpy as np, re
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2
bv2 = BatteryV2()

csv_path = Path(__file__).resolve().parent.parent.parent / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
with open(csv_path, "r") as f:
    lines = [l for l in f if not l.startswith("#")]

rows = []
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        if tc <= 0 or not sg:
            continue
        pg = row.get("point_group_2", "").strip()
        cs = row.get("crystal_system_2", "").strip()
        sg_num = int(float(row.get("exchange_symmetry_2", "0")))
        sc_class = row.get("sc_class", "").strip()
        n_elem = len(set(re.findall(r"[A-Z][a-z]?", row.get("formula_sc", ""))))

        lattice = sg[0] if sg else "?"
        has_inversion = "-" in pg or "/" in pg
        has_screw = bool(re.search(r"[2-6][1-5]", sg))
        has_glide = bool(re.search(r"[abcdn]", sg.lower().replace(lattice, "", 1)))
        symmorphic = not (has_screw or has_glide)
        rotation_orders = re.findall(r"[2-6]", pg)
        max_rotation = max(int(x) for x in rotation_orders) if rotation_orders else 1

        rows.append({
            "tc": tc, "sg": sg, "pg": pg, "cs": cs, "sg_num": sg_num,
            "sc_class": sc_class, "n_elem": n_elem, "lattice": lattice,
            "has_inversion": has_inversion, "symmorphic": symmorphic,
            "max_rotation": max_rotation,
        })
    except Exception:
        pass

print(f"{len(rows)} materials with all SG components")
print()
print("Component distributions:")
print(f"  Lattice: {Counter(r['lattice'] for r in rows).most_common()}")
print(f"  Inversion: {Counter(r['has_inversion'] for r in rows)}")
print(f"  Symmorphic: {Counter(r['symmorphic'] for r in rows)}")
print(f"  Max rotation: {Counter(r['max_rotation'] for r in rows).most_common()}")

tc_arr = np.array([r["tc"] for r in rows], dtype=float)

components = [
    ("sc_class",      "SC class (chemical family)",  [r["sc_class"] for r in rows]),
    ("sg",            "Full space group",            [r["sg"] for r in rows]),
    ("pg",            "Point group",                 [r["pg"] for r in rows]),
    ("cs",            "Crystal system",              [r["cs"] for r in rows]),
    ("lattice",       "Lattice type (P/I/F/C/R)",    [r["lattice"] for r in rows]),
    ("has_inversion", "Has inversion symmetry",      [r["has_inversion"] for r in rows]),
    ("symmorphic",    "Symmorphic (no screw/glide)", [r["symmorphic"] for r in rows]),
    ("max_rotation",  "Max rotation order",          [r["max_rotation"] for r in rows]),
    ("n_elem",        "Number of elements",          [r["n_elem"] for r in rows]),
]

# STEP 1
print()
print("=" * 80)
print("STEP 1: Raw eta^2 for each component on Tc")
print("=" * 80)
print()
print(f"{'Component':<35s} | {'eta^2':>8s} | {'F':>8s} | {'groups':>6s} | Type")
print("-" * 75)
for _, desc, labels in components:
    v, r = bv2.F24_variance_decomposition(tc_arr, labels)
    eta = r.get("eta_squared", 0)
    f_stat = r.get("f_statistic", 0)
    n_g = r.get("n_groups", 0)
    ftype = "LAW" if eta >= 0.14 else "TENDENCY" if eta >= 0.06 else "small" if eta >= 0.01 else "negl"
    print(f"{desc:<35s} | {eta:8.4f} | {f_stat:8.1f} | {n_g:6d} | {ftype}")

# STEP 2: After removing SC_class
print()
print("=" * 80)
print("STEP 2: Residual eta^2 after removing SC_class")
print("=" * 80)
print()

sc_groups = defaultdict(list)
for i, r in enumerate(rows):
    sc_groups[r["sc_class"]].append(i)
tc_resid1 = np.copy(tc_arr)
for cls, indices in sc_groups.items():
    if len(indices) >= 5:
        cls_mean = np.mean(tc_arr[indices])
        for i in indices:
            tc_resid1[i] = tc_arr[i] - cls_mean

print(f"{'Component':<35s} | {'raw':>8s} | {'after SC':>8s} | {'retained':>8s}")
print("-" * 70)
for cname, desc, labels in components:
    if cname == "sc_class":
        continue
    _, r_raw = bv2.F24_variance_decomposition(tc_arr, labels)
    _, r_res = bv2.F24_variance_decomposition(tc_resid1, labels)
    eta_raw = r_raw.get("eta_squared", 0)
    eta_res = r_res.get("eta_squared", 0)
    ret = eta_res / eta_raw if eta_raw > 0 else 0
    print(f"{desc:<35s} | {eta_raw:8.4f} | {eta_res:8.4f} | {ret:7.0%}")

# STEP 3: After SC_class + crystal_system + n_elements
print()
print("=" * 80)
print("STEP 3: Residual after SC_class + crystal_system + n_elements")
print("=" * 80)
print()

n_elem_arr = np.array([r["n_elem"] for r in rows])
n_elem_bin = ["simple" if n <= 2 else "medium" if n <= 4 else "complex" for n in n_elem_arr]
strata = defaultdict(list)
for i, r in enumerate(rows):
    strata[(r["sc_class"], r["cs"], n_elem_bin[i])].append(i)
tc_resid3 = np.copy(tc_arr)
for key, indices in strata.items():
    if len(indices) >= 3:
        m = np.mean(tc_arr[indices])
        for i in indices:
            tc_resid3[i] = tc_arr[i] - m

print(f"{'SG Component':<35s} | {'raw':>8s} | {'-SC_cls':>8s} | {'-all 3':>8s}")
print("-" * 70)
for cname, desc, labels in components:
    if cname in ("sc_class", "cs", "n_elem"):
        continue
    _, r_raw = bv2.F24_variance_decomposition(tc_arr, labels)
    _, r_sc = bv2.F24_variance_decomposition(tc_resid1, labels)
    _, r_deep = bv2.F24_variance_decomposition(tc_resid3, labels)
    eta_raw = r_raw.get("eta_squared", 0)
    eta_sc = r_sc.get("eta_squared", 0)
    eta_deep = r_deep.get("eta_squared", 0)
    print(f"{desc:<35s} | {eta_raw:8.4f} | {eta_sc:8.4f} | {eta_deep:8.4f}")

print()
print("INTERPRETATION: 'after all 3' = controlling for chemical family + crystal system + complexity.")
print("Whatever survives is the PURE SG contribution — symmetry constraints on Tc beyond")
print("what chemical class, crystal system, and compositional complexity explain.")
