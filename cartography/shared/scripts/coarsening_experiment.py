#!/usr/bin/env python3
"""
Coarsening Experiment: Find the resolution limit where F25b flips.

Merge SGs into progressively coarser groupings and test when
transportability becomes detectable.

Levels:
  L0: Full SG (77 valid groups) — WEAK_NOISY (known)
  L1: Point group family (~26 groups)
  L2: Crystal system (7 groups)
  L3: Lattice type (6 groups: P, I, F, C, R, A)
  L4: Has inversion (2 groups)
  L5: k-means on Tc (k=3,5,10,20)

For each level: compute min cell size, run F25b, report verdict.
"""
import sys, os, json, csv, io, re
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)


def eta_sq(values, labels, min_group=5):
    values = np.array(values, dtype=float)
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= min_group}
    if len(valid) < 2:
        return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)


# Load data
print("Loading data...")
csv_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
sc_rows = []
with open(csv_path, "r") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        cs = row.get("crystal_system_2", "").strip()
        sc_class = row.get("sc_class", "").strip()
        if tc > 0 and sg and sc_class:
            sc_rows.append({"tc": tc, "sg": sg, "cs": cs, "sc_class": sc_class})
    except:
        pass

# Load space group metadata for coarsening
sg_meta = {}
sg_path = DATA / "spacegroups/data/space_groups.json"
if sg_path.exists():
    sg_data = json.load(open(sg_path, encoding="utf-8"))
    for s in sg_data:
        symbol = s.get("symbol", s.get("international_full", ""))
        sg_meta[symbol] = {
            "pg": s.get("point_group", "unknown"),
            "cs": s.get("crystal_system", "unknown"),
            "lattice": s.get("lattice_type", symbol[0] if symbol else "?"),
            "symmorphic": s.get("is_symmorphic", False),
            "pg_order": s.get("point_group_order", 0),
        }

# Derive lattice type from SG symbol (first letter) as fallback
def get_lattice(sg_symbol):
    if sg_symbol in sg_meta:
        return sg_meta[sg_symbol].get("lattice", sg_symbol[0])
    return sg_symbol.split()[0][0] if sg_symbol else "?"

def get_pg(sg_symbol):
    if sg_symbol in sg_meta:
        return sg_meta[sg_symbol].get("pg", "unknown")
    return "unknown"

def get_inversion(sg_symbol):
    if sg_symbol in sg_meta:
        return "centro" if sg_meta[sg_symbol].get("pg_order", 0) > 0 and "-" in sg_symbol else "non-centro"
    return "centro" if "-" in sg_symbol else "non-centro"

tc = [r["tc"] for r in sc_rows]
sc_cls = [r["sc_class"] for r in sc_rows]
n = len(tc)

print(f"  {n} superconductors, {len(sg_meta)} SG metadata entries\n")

# ============================================================
# Build coarsening levels
# ============================================================
print("=" * 110)
print("COARSENING EXPERIMENT: SG granularity vs F25b transportability")
print("=" * 110)

levels = []

# L0: Full SG
levels.append(("L0: Full SG", [r["sg"] for r in sc_rows]))

# L1: Point group
levels.append(("L1: Point group", [get_pg(r["sg"]) for r in sc_rows]))

# L2: Crystal system
levels.append(("L2: Crystal system", [r["cs"] for r in sc_rows]))

# L3: Lattice type
levels.append(("L3: Lattice type", [get_lattice(r["sg"]) for r in sc_rows]))

# L4: Has inversion
levels.append(("L4: Centro/non-centro", [get_inversion(r["sg"]) for r in sc_rows]))

# L5: k-means on Tc (data-driven grouping)
from scipy.cluster.vq import kmeans2
tc_arr = np.array(tc)
for k in [20, 10, 5, 3]:
    centroids, labels = kmeans2(tc_arr, k, minit="points", seed=42)
    levels.append((f"L5: Tc k-means k={k}", [str(l) for l in labels]))

# L6: SC_class itself (the context variable — sanity check)
levels.append(("L6: SC_class (self)", sc_cls))

print(f"\n  {'Level':30s} | {'n_groups':>8s} | {'min_cell':>8s} | {'med_cell':>8s} | {'eta2':>8s} | {'F25b':>15s} | {'main R2':>8s} | {'inter R2':>8s}")
print("  " + "-" * 120)

results = []
for name, grouping in levels:
    # Group stats
    group_counts = defaultdict(int)
    for g in grouping:
        group_counts[g] += 1
    n_groups = len(group_counts)
    min_cell = min(group_counts.values()) if group_counts else 0
    med_cell = int(np.median(list(group_counts.values()))) if group_counts else 0

    # Cell sizes (grouping × SC_class)
    cell_counts = defaultdict(int)
    for g, c in zip(grouping, sc_cls):
        cell_counts[(g, c)] += 1
    min_cell_cross = min(cell_counts.values()) if cell_counts else 0
    n_cells = len(cell_counts)

    # eta²
    eta, _, _ = eta_sq(tc, grouping)

    # F25b
    v25b, r25b = bv2.F25b_model_transportability(tc, grouping, sc_cls)
    main_r2 = r25b.get("weighted_r2_main", float("nan"))
    inter_r2 = r25b.get("weighted_r2_interaction", float("nan"))

    print(f"  {name:30s} | {n_groups:8d} | {min_cell:8d} | {med_cell:8d} | {eta:8.4f} | {v25b:>15s} | {main_r2:8.4f} | {inter_r2:8.4f}")

    results.append({
        "name": name, "n_groups": n_groups, "min_cell": min_cell,
        "med_cell": med_cell, "n_cells": n_cells, "min_cell_cross": min_cell_cross,
        "eta2": eta, "f25b": v25b, "main_r2": main_r2, "inter_r2": inter_r2
    })

# ============================================================
# Analysis: find the transition
# ============================================================
print("\n" + "=" * 110)
print("RESOLUTION LIMIT ANALYSIS")
print("=" * 110)

flipped = [r for r in results if r["f25b"] != "WEAK_NOISY"]
still_noisy = [r for r in results if r["f25b"] == "WEAK_NOISY"]

if flipped:
    print(f"\n  FLIPPED to non-WEAK_NOISY:")
    for r in flipped:
        print(f"    {r['name']:30s}: {r['f25b']:15s} (n_groups={r['n_groups']}, min_cell={r['min_cell']}, main R2={r['main_r2']:.4f})")

    # Find transition point
    first_flip = flipped[0]
    print(f"\n  TRANSITION POINT: {first_flip['name']}")
    print(f"    Groups: {first_flip['n_groups']}")
    print(f"    Min cell size: {first_flip['min_cell']}")
    print(f"    Min cross-cell: {first_flip['min_cell_cross']}")
    print(f"    F25b: {first_flip['f25b']}")
else:
    print(f"\n  NO TRANSITION: All levels remain WEAK_NOISY")
    print(f"  Even the coarsest grouping (2 groups) doesn't achieve transfer.")
    print(f"  This suggests the issue is NOT just cell size — it may be")
    print(f"  genuine non-stationarity of the SG-Tc mapping across SC classes.")

# Best main R² achieved
best = max(results, key=lambda r: r["main_r2"])
print(f"\n  Best main R²: {best['main_r2']:.4f} at {best['name']} ({best['n_groups']} groups)")

# Plot-like output: groups vs main R²
print(f"\n  Resolution curve (n_groups vs main OOS R²):")
for r in sorted(results, key=lambda x: x["n_groups"]):
    bar = "#" * max(0, int((r["main_r2"] + 20) * 2))
    print(f"    {r['n_groups']:3d} groups | R²={r['main_r2']:8.4f} | {bar}")
