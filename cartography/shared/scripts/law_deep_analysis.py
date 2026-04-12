#!/usr/bin/env python3
"""
Priority 3: Deep LAW analysis.

1. Test SG -> Tc WITHIN each SC class stratum separately.
   If SG still predicts Tc within cuprates, within iron-based, etc.,
   then it's truly independent (not just a proxy for chemical family).

2. Check if crossing_number -> determinant is trivially structural.
   Determinant = |Alexander(-1)|. Alexander polynomial degree ~ crossing number.
   So is this just "bigger knots have bigger polynomials"?

3. Look for SuperCon/Stanev replication data.
"""

import sys, os, csv, io, re, json
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

# ============================================================
# Load data
# ============================================================
print("Loading data...")

# Superconductors
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
        formula = row.get("formula_sc", "").strip()
        if tc > 0 and sg:
            r = {"tc": tc, "sg": sg, "cs": cs, "sc_class": sc_class, "formula": formula}
            for key, col in [("vol", "cell_volume_2"), ("density", "density_2"),
                             ("fe", "formation_energy_per_atom_2")]:
                try: r[key] = float(row.get(col, ""))
                except: r[key] = None
            elements = set(re.findall(r'[A-Z][a-z]?', formula))
            r["n_elements"] = len(elements)
            sc_rows.append(r)
    except:
        pass

# Knots
knots_data = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))
knots = knots_data["knots"]

print(f"Loaded: sc={len(sc_rows)}, knots={len(knots)}")


# ============================================================
# PART 1: SG -> Tc WITHIN each SC class stratum
# ============================================================
print()
print("=" * 100)
print("PART 1: SG -> Tc WITHIN each SC class stratum")
print("If SG predicts Tc within each chemical family, it's truly independent.")
print("=" * 100)

sc_classes = sorted(set(r["sc_class"] for r in sc_rows if r["sc_class"]))

print(f"\n  SC classes: {sc_classes}")
print(f"\n  {'SC Class':25s} | {'n':>5s} | {'n_SGs':>5s} | {'eta^2':>8s} | {'F24 verdict':15s} | {'F24b':20s}")
print("  " + "-" * 95)

stratum_results = []
for cls in sc_classes:
    stratum = [r for r in sc_rows if r["sc_class"] == cls]
    if len(stratum) < 30:
        print(f"  {cls:25s} | {len(stratum):5d} | {'--':>5s} | {'skip':>8s} | too small")
        continue

    tc_s = [r["tc"] for r in stratum]
    sg_s = [r["sg"] for r in stratum]

    # Count valid SGs
    sg_counts = defaultdict(int)
    for s in sg_s:
        sg_counts[s] += 1
    n_valid_sg = sum(1 for s, c in sg_counts.items() if c >= 5)

    if n_valid_sg < 2:
        print(f"  {cls:25s} | {len(stratum):5d} | {n_valid_sg:5d} | {'skip':>8s} | <2 valid SGs")
        continue

    v24, r24 = bv2.F24_variance_decomposition(tc_s, sg_s)
    v24b, r24b = bv2.F24b_metric_consistency(tc_s, sg_s)

    eta = r24.get("eta_squared", float("nan"))
    n_total = r24.get("n_total", len(stratum))
    n_groups = r24.get("n_groups", 0)

    print(f"  {cls:25s} | {n_total:5d} | {n_groups:5d} | {eta:8.4f} | {v24:15s} | {v24b}")

    stratum_results.append({"class": cls, "n": n_total, "n_sg": n_groups, "eta2": eta, "f24": v24})

# Summary
print()
surviving = [r for r in stratum_results if r["eta2"] > 0.14]
partial = [r for r in stratum_results if 0.01 < r["eta2"] <= 0.14]
negligible_s = [r for r in stratum_results if r["eta2"] <= 0.01]

print(f"  WITHIN-STRATUM SUMMARY:")
print(f"    LAW-level (eta^2 > 0.14): {len(surviving)} strata")
for r in surviving:
    print(f"      {r['class']:25s}: eta^2 = {r['eta2']:.4f}")
print(f"    TENDENCY-level (0.01 < eta^2 < 0.14): {len(partial)} strata")
for r in partial:
    print(f"      {r['class']:25s}: eta^2 = {r['eta2']:.4f}")
print(f"    NEGLIGIBLE (eta^2 < 0.01): {len(negligible_s)} strata")

if surviving:
    print(f"\n  VERDICT: SG -> Tc is INDEPENDENT of chemical family.")
    print(f"  SG still explains substantial Tc variance WITHIN {len(surviving)} chemical families.")
else:
    print(f"\n  VERDICT: SG -> Tc may be MEDIATED by chemical family.")
    print(f"  No stratum shows LAW-level SG effect.")


# ============================================================
# PART 2: Is crossing_number -> determinant trivially structural?
# ============================================================
print()
print("=" * 100)
print("PART 2: Is crossing_number -> determinant trivially structural?")
print("=" * 100)

valid_knots = [k for k in knots if k.get("determinant") and k.get("crossing_number") and k.get("alexander_coeffs")]

print(f"\n  Valid knots with determinant + crossing_number + Alexander: {len(valid_knots)}")

# Test 1: Raw correlation
cn = np.array([k["crossing_number"] for k in valid_knots])
det = np.array([k["determinant"] for k in valid_knots])
r = np.corrcoef(cn, det)[0, 1]
print(f"\n  Raw: r(crossing, determinant) = {r:.4f}, R^2 = {r**2:.4f}")

# Test 2: Alexander length ~ crossing number (polynomial degree grows with crossing)
alex_len = np.array([len(k["alexander_coeffs"]) for k in valid_knots])
r_al_cn = np.corrcoef(cn, alex_len)[0, 1]
print(f"  r(crossing, alexander_length) = {r_al_cn:.4f}")

# Test 3: Determinant ~ Alexander length (bigger poly -> bigger determinant)
r_det_al = np.corrcoef(det, alex_len)[0, 1]
print(f"  r(determinant, alexander_length) = {r_det_al:.4f}")

# Test 4: PARTIAL — crossing -> determinant AFTER controlling for Alexander length
X = np.column_stack([np.ones(len(cn)), alex_len])
beta = np.linalg.lstsq(X, det, rcond=None)[0]
det_resid = det - X @ beta

beta2 = np.linalg.lstsq(X, cn, rcond=None)[0]
cn_resid = cn - X @ beta2

r_partial = np.corrcoef(cn_resid, det_resid)[0, 1]
print(f"\n  PARTIAL: r(crossing, determinant | alexander_length) = {r_partial:.4f}, R^2 = {r_partial**2:.4f}")

# Test 5: PARTIAL — crossing -> determinant AFTER controlling for max Alexander coeff
max_alex = np.array([max(abs(c) for c in k["alexander_coeffs"]) for k in valid_knots])
X2 = np.column_stack([np.ones(len(cn)), alex_len, max_alex])
beta_d = np.linalg.lstsq(X2, det, rcond=None)[0]
det_resid2 = det - X2 @ beta_d
beta_c = np.linalg.lstsq(X2, cn, rcond=None)[0]
cn_resid2 = cn - X2 @ beta_c
r_partial2 = np.corrcoef(cn_resid2, det_resid2)[0, 1]
print(f"  PARTIAL: r(crossing, determinant | alex_len + max_alex) = {r_partial2:.4f}, R^2 = {r_partial2**2:.4f}")

# Test 6: Eta^2 by crossing number as categorical
v24, r24 = bv2.F24_variance_decomposition(det, cn)
v24b, r24b = bv2.F24b_metric_consistency(det, cn)
eta = r24.get("eta_squared", float("nan"))
print(f"\n  Eta^2(crossing -> determinant) = {eta:.4f}")
print(f"  F24b: {v24b}")

# Test 7: WITHIN-crossing-number variance
print(f"\n  Within-crossing-number determinant statistics:")
print(f"  {'CN':>4s} | {'n':>5s} | {'mean det':>10s} | {'std det':>10s} | {'CV':>8s} | {'min':>8s} | {'max':>8s}")
print("  " + "-" * 70)
cn_groups = defaultdict(list)
for k in valid_knots:
    cn_groups[k["crossing_number"]].append(k["determinant"])
for c in sorted(cn_groups.keys()):
    vals = cn_groups[c]
    if len(vals) >= 5:
        arr = np.array(vals, dtype=float)
        cv = np.std(arr) / np.mean(arr) if np.mean(arr) > 0 else 0
        print(f"  {c:4d} | {len(vals):5d} | {np.mean(arr):10.1f} | {np.std(arr):10.1f} | {cv:8.3f} | {np.min(arr):8.0f} | {np.max(arr):8.0f}")

# Verdict
print()
if r_partial**2 < 0.01:
    print("  VERDICT: Crossing -> determinant is almost ENTIRELY mediated by Alexander polynomial.")
    print("  After controlling for Alexander length, the partial R^2 is negligible.")
    print("  This LAW is TRIVIALLY STRUCTURAL: bigger knots -> bigger polynomials -> bigger determinants.")
elif r_partial**2 < 0.05:
    print("  VERDICT: Crossing -> determinant is MOSTLY mediated by Alexander polynomial.")
    print(f"  Partial R^2 = {r_partial**2:.4f} — a small residual signal remains.")
else:
    print("  VERDICT: Crossing -> determinant has INDEPENDENT structure beyond Alexander polynomial.")
    print(f"  Partial R^2 = {r_partial**2:.4f} — crossing number carries additional information.")


# ============================================================
# PART 3: Cross-validate SG -> Tc on train/test splits
# ============================================================
print()
print("=" * 100)
print("PART 3: Cross-validation of SG -> Tc (is eta^2 = 0.46 an overfit?)")
print("=" * 100)

rng = np.random.default_rng(42)
tc_all = np.array([r["tc"] for r in sc_rows])
sg_all = [r["sg"] for r in sc_rows]
n_total = len(tc_all)

cv_etas = []
for fold in range(10):
    idx = np.arange(n_total)
    rng.shuffle(idx)
    test_idx = idx[:n_total // 5]
    train_idx = idx[n_total // 5:]

    # Compute eta^2 on TEST set using TRAIN group means
    train_groups = defaultdict(list)
    for i in train_idx:
        train_groups[sg_all[i]].append(tc_all[i])
    train_means = {k: np.mean(v) for k, v in train_groups.items() if len(v) >= 5}

    # Predict test Tc using train means
    test_tc = tc_all[test_idx]
    test_sg = [sg_all[i] for i in test_idx]
    grand_mean = np.mean(tc_all[train_idx])

    predicted = np.array([train_means.get(s, grand_mean) for s in test_sg])
    ss_total = np.sum((test_tc - np.mean(test_tc)) ** 2)
    ss_model = np.sum((predicted - np.mean(test_tc)) ** 2)
    # Out-of-sample R^2
    ss_resid = np.sum((test_tc - predicted) ** 2)
    r2_oos = 1 - ss_resid / ss_total

    cv_etas.append(r2_oos)

print(f"\n  10-fold cross-validated R^2 (out-of-sample SG -> Tc):")
print(f"    Mean:  {np.mean(cv_etas):.4f}")
print(f"    Std:   {np.std(cv_etas):.4f}")
print(f"    Min:   {np.min(cv_etas):.4f}")
print(f"    Max:   {np.max(cv_etas):.4f}")
print(f"    In-sample eta^2: 0.4565")
print(f"    Shrinkage: {(0.4565 - np.mean(cv_etas)) / 0.4565 * 100:.1f}%")

if np.mean(cv_etas) > 0.30:
    print(f"\n  VERDICT: SG -> Tc is ROBUST out of sample. Not an overfit.")
elif np.mean(cv_etas) > 0.15:
    print(f"\n  VERDICT: SG -> Tc has MODERATE shrinkage but survives cross-validation.")
else:
    print(f"\n  VERDICT: SG -> Tc shows LARGE shrinkage — possible overfit with 77 groups.")


# ============================================================
# PART 4: SuperCon/Stanev replication check
# ============================================================
print()
print("=" * 100)
print("PART 4: Replication dataset check")
print("=" * 100)

# Check for alternative superconductor datasets
stanev_path = DATA / "physics/data/superconductors"
print(f"\n  Checking for alternative datasets in {stanev_path}...")

import glob
alt_files = []
for pattern in ["**/*.csv", "**/*.json", "**/*.xlsx"]:
    alt_files.extend(glob.glob(str(stanev_path / pattern), recursive=True))

csv_main = str(csv_path)
alt_files = [f for f in alt_files if f != csv_main]

print(f"  Found {len(alt_files)} files besides the main CSV:")
for f in alt_files[:15]:
    print(f"    {os.path.relpath(f, str(stanev_path))}")

# Try to find and load Stanev if it exists
stanev_files = [f for f in alt_files if "stanev" in f.lower() or "supercon" in f.lower() or "unique" in f.lower()]
if stanev_files:
    print(f"\n  Potential replication datasets: {stanev_files}")
else:
    print(f"\n  No Stanev/SuperCon replication dataset found in current data.")
    print(f"  To replicate: download SuperCon from NIMS or Stanev et al. (2018) dataset.")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 100)
print("SUMMARY")
print("=" * 100)

print(f"""
  1. SG -> Tc WITHIN strata: {len(surviving)} chemical families show LAW-level SG effect
     {'INDEPENDENT' if surviving else 'MEDIATED'}: SG encodes Tc information beyond chemical family

  2. Crossing -> determinant: partial R^2 = {r_partial**2:.4f} after Alexander control
     {'TRIVIALLY STRUCTURAL' if r_partial**2 < 0.01 else 'PARTIALLY STRUCTURAL' if r_partial**2 < 0.05 else 'INDEPENDENTLY STRUCTURAL'}

  3. SG -> Tc cross-validation: OOS R^2 = {np.mean(cv_etas):.4f} (shrinkage {(0.4565 - np.mean(cv_etas)) / 0.4565 * 100:.1f}%)
     {'ROBUST' if np.mean(cv_etas) > 0.30 else 'MODERATE' if np.mean(cv_etas) > 0.15 else 'WEAK'}

  4. Replication: {'Found alternative datasets' if stanev_files else 'No replication dataset available'}
""")
