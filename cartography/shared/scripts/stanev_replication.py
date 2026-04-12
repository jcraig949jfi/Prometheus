#!/usr/bin/env python3
"""
Stanev Replication + Leave-One-Class-Out Cross-Validation for SG -> Tc

Two independent replication strategies:

Strategy A: Match Stanev formulas (NOT in main dataset) to MP structures.
            Test SG -> Tc on these independently-sourced materials.

Strategy B: Leave-one-SC-class-out CV on the main dataset.
            Train SG means on all classes EXCEPT one, predict that class.
            Much stronger than random 80/20 splits.

Strategy C: Permutation null — shuffle SG labels, confirm eta^2 collapses.

The claim to replicate: SG -> Tc, eta^2 ~ 0.45, independent of chemical family,
irreducible, 2.8% CV shrinkage.
"""

import sys, os, csv, io, re, ast
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


def normalize_formula(f):
    """Normalize chemical formula for matching: strip spaces, sort elements."""
    f = f.strip().replace(" ", "")
    # Extract element-count pairs
    pairs = re.findall(r'([A-Z][a-z]?)(\d*\.?\d*)', f)
    if not pairs:
        return f
    # Sort by element
    normed = []
    for elem, count in sorted(pairs):
        if elem:
            normed.append(f"{elem}{count}")
    return "".join(normed)


def eta_squared(values, labels, min_group=5):
    values = np.array(values, dtype=float)
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= min_group}
    if len(valid) < 2:
        return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm) ** 2)
    ss_between = sum(len(v) * (np.mean(v) - gm) ** 2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)


# ============================================================
# Load main dataset
# ============================================================
print("Loading main dataset (3DSC_MP)...")
csv_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
sc_rows = []
main_formulas = set()
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
            elements = set(re.findall(r'[A-Z][a-z]?', formula))
            r["n_elements"] = len(elements)
            sc_rows.append(r)
            main_formulas.add(formula)
            main_formulas.add(normalize_formula(formula))
    except:
        pass

print(f"  Main dataset: {len(sc_rows)} rows, {len(set(r['sg'] for r in sc_rows))} SGs")

# ============================================================
# Strategy A: Match Stanev to MP structures
# ============================================================
print()
print("=" * 100)
print("STRATEGY A: Match Stanev formulas to MP structures (non-overlapping)")
print("=" * 100)

# Build MP formula -> SG map
print("\n  Loading MP_subset for structure lookup...")
mp_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/source/MP/raw/MP_subset.csv"
mp_sg = {}  # normalized formula -> (sg_symbol, sg_number)
with open(mp_path, encoding="utf-8") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    sg_raw = row.get("spacegroup", "")
    formula = row.get("pretty_formula", "").strip()
    full_formula = row.get("full_formula", "").strip()
    if sg_raw and formula:
        try:
            sg_dict = ast.literal_eval(sg_raw)
            if isinstance(sg_dict, dict):
                symbol = sg_dict.get("symbol", "")
                number = sg_dict.get("number", 0)
                if symbol:
                    mp_sg[formula] = symbol
                    mp_sg[normalize_formula(formula)] = symbol
                    if full_formula:
                        mp_sg[full_formula] = symbol
                        mp_sg[normalize_formula(full_formula)] = symbol
        except:
            pass

print(f"  MP structure map: {len(mp_sg)} entries")

# Load Stanev
stanev_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/source/SuperCon/raw/Supercon_data_by_2018_Stanev.csv"
stanev = []
with open(stanev_path) as f:
    for row in csv.DictReader(f):
        name = row.get("name", "").strip()
        tc = row.get("Tc", "")
        try:
            tc = float(tc)
            if tc > 0:
                stanev.append({"name": name, "tc": tc})
        except:
            pass

print(f"  Stanev: {len(stanev)} materials with Tc > 0")

# Match: Stanev formula -> MP structure, EXCLUDING main dataset overlap
matched = []
for s in stanev:
    name = s["name"]
    normed = normalize_formula(name)
    # Skip if in main dataset
    if name in main_formulas or normed in main_formulas:
        continue
    # Try to find in MP
    sg = mp_sg.get(name) or mp_sg.get(normed)
    if sg:
        matched.append({"tc": s["tc"], "sg": sg, "formula": name})

print(f"  Matched (non-overlapping): {len(matched)}")

if matched:
    sg_counts = defaultdict(int)
    for m in matched:
        sg_counts[m["sg"]] += 1
    valid_sgs = sum(1 for s, c in sg_counts.items() if c >= 5)
    print(f"  Unique SGs: {len(sg_counts)}, SGs with >= 5 members: {valid_sgs}")

    if valid_sgs >= 2:
        eta_a, n_a, k_a = eta_squared(
            [m["tc"] for m in matched],
            [m["sg"] for m in matched]
        )
        print(f"\n  RESULT: eta^2(SG -> Tc) on Stanev non-overlap = {eta_a:.4f}")
        print(f"          n={n_a}, groups={k_a}")
        print(f"          Main dataset eta^2 = 0.4565")
        print(f"          Ratio: {eta_a / 0.4565:.2f}")

        # F24 + F24b
        v24, r24 = bv2.F24_variance_decomposition(
            [m["tc"] for m in matched], [m["sg"] for m in matched])
        v24b, r24b = bv2.F24b_metric_consistency(
            [m["tc"] for m in matched], [m["sg"] for m in matched])
        print(f"          F24: {v24}")
        print(f"          F24b: {v24b}")
    else:
        print(f"\n  INSUFFICIENT: Only {valid_sgs} SGs with >= 5 members. Cannot compute eta^2.")
        print("  Stanev formula format doesn't match MP pretty_formula well enough.")
else:
    print(f"\n  NO MATCHES: Stanev formula format is incompatible with MP pretty_formula.")

# Show match failure analysis
unmatched_examples = []
for s in stanev[:100]:
    name = s["name"]
    normed = normalize_formula(name)
    if name not in main_formulas and normed not in main_formulas:
        if not (mp_sg.get(name) or mp_sg.get(normed)):
            unmatched_examples.append(name)
if unmatched_examples:
    print(f"\n  Example unmatched Stanev formulas: {unmatched_examples[:10]}")

# ============================================================
# Strategy B: Leave-One-SC-Class-Out Cross-Validation
# ============================================================
print()
print("=" * 100)
print("STRATEGY B: Leave-One-SC-Class-Out Cross-Validation")
print("This is the STRONGEST replication test: can SG means learned from")
print("OTHER chemical families predict Tc in the held-out family?")
print("=" * 100)

tc_all = np.array([r["tc"] for r in sc_rows])
sg_all = [r["sg"] for r in sc_rows]
sc_class_all = [r["sc_class"] for r in sc_rows]
classes = sorted(set(sc_class_all))
n_total = len(tc_all)

print(f"\n  {'Held-out class':25s} | {'n_test':>6s} | {'n_train':>7s} | {'OOS R^2':>8s} | {'eta^2 test':>10s} | {'Verdict'}")
print("  " + "-" * 85)

loocv_results = []
for held_out in classes:
    test_mask = np.array([sc == held_out for sc in sc_class_all])
    train_mask = ~test_mask
    n_test = np.sum(test_mask)
    n_train = np.sum(train_mask)

    if n_test < 20:
        print(f"  {held_out:25s} | {n_test:6d} | {n_train:7d} | {'skip':>8s} | {'skip':>10s} | too small")
        continue

    # Learn SG group means from TRAINING set only
    train_groups = defaultdict(list)
    for i in range(n_total):
        if train_mask[i]:
            train_groups[sg_all[i]].append(tc_all[i])
    train_means = {k: np.mean(v) for k, v in train_groups.items() if len(v) >= 3}
    grand_mean_train = np.mean(tc_all[train_mask])

    # Predict test set
    test_tc = tc_all[test_mask]
    test_sg = [sg_all[i] for i in range(n_total) if test_mask[i]]
    predicted = np.array([train_means.get(s, grand_mean_train) for s in test_sg])

    # Out-of-sample R^2
    ss_total_test = np.sum((test_tc - np.mean(test_tc)) ** 2)
    ss_resid = np.sum((test_tc - predicted) ** 2)
    r2_oos = 1 - ss_resid / ss_total_test if ss_total_test > 0 else 0

    # In-sample eta^2 on test set alone
    eta_test, n_eta, k_eta = eta_squared(test_tc, test_sg, min_group=3)

    verdict = "REPLICATES" if r2_oos > 0.15 else "WEAK" if r2_oos > 0.05 else "FAILS"
    print(f"  {held_out:25s} | {n_test:6d} | {n_train:7d} | {r2_oos:8.4f} | {eta_test:10.4f} | {verdict}")

    loocv_results.append({"class": held_out, "n_test": int(n_test), "r2_oos": r2_oos,
                           "eta2_within": eta_test})

# Summary
if loocv_results:
    r2_values = [r["r2_oos"] for r in loocv_results]
    weighted_r2 = sum(r["r2_oos"] * r["n_test"] for r in loocv_results) / sum(r["n_test"] for r in loocv_results)
    print(f"\n  LEAVE-ONE-CLASS-OUT SUMMARY:")
    print(f"    Mean OOS R^2:       {np.mean(r2_values):.4f}")
    print(f"    Weighted OOS R^2:   {weighted_r2:.4f}")
    print(f"    Min OOS R^2:        {np.min(r2_values):.4f}")
    print(f"    Max OOS R^2:        {np.max(r2_values):.4f}")
    print(f"    Classes replicating: {sum(1 for r in r2_values if r > 0.15)}/{len(r2_values)}")
    print(f"    In-sample eta^2:    0.4565")


# ============================================================
# Strategy C: Permutation Null (sanity check)
# ============================================================
print()
print("=" * 100)
print("STRATEGY C: Permutation Null — does shuffling SG labels kill the signal?")
print("=" * 100)

real_eta, _, _ = eta_squared(tc_all, sg_all)
print(f"\n  Real eta^2: {real_eta:.4f}")

null_etas = []
sg_array = np.array(sg_all)
for i in range(1000):
    shuffled = sg_array.copy()
    rng.shuffle(shuffled)
    null_eta, _, _ = eta_squared(tc_all, shuffled.tolist())
    null_etas.append(null_eta)

null_etas = np.array(null_etas)
p_value = (np.sum(null_etas >= real_eta) + 1) / (len(null_etas) + 1)
z_score = (real_eta - np.mean(null_etas)) / np.std(null_etas) if np.std(null_etas) > 0 else 0

print(f"  Null distribution: mean={np.mean(null_etas):.4f}, std={np.std(null_etas):.4f}")
print(f"  Null max: {np.max(null_etas):.4f}")
print(f"  Real eta^2 / null mean: {real_eta / np.mean(null_etas):.1f}x")
print(f"  z-score: {z_score:.1f}")
print(f"  p-value: {p_value:.6f}")

if p_value < 0.001:
    print(f"  VERDICT: Signal is {real_eta / np.mean(null_etas):.0f}x above permutation null. NOT an artifact.")
else:
    print(f"  WARNING: Signal does not clearly exceed permutation null.")


# ============================================================
# Strategy D: Temporal/Source Split (if available)
# ============================================================
print()
print("=" * 100)
print("STRATEGY D: Within-class SG effect — does SG add to SC_class?")
print("=" * 100)

# This is the minimal model test the user requested:
# Tc ~ SG only vs Tc ~ SC_class only vs Tc ~ SG + SC_class

# Model 1: Tc ~ SG
eta_sg, n_sg, k_sg = eta_squared(tc_all, sg_all)

# Model 2: Tc ~ SC_class
eta_sc, n_sc, k_sc = eta_squared(tc_all, sc_class_all)

# Model 3: Tc ~ SG + SC_class (sequential R^2)
def one_hot(labels, n):
    unique = sorted(set(labels))
    if len(unique) < 2:
        return np.zeros((n, 0))
    mat = np.zeros((n, len(unique) - 1))
    for i, l in enumerate(labels):
        idx = unique.index(l)
        if idx > 0:
            mat[i, idx - 1] = 1
    return mat

X_sg = one_hot(sg_all, n_total)
X_sc = one_hot(sc_class_all, n_total)

# SG only
X1 = np.column_stack([np.ones(n_total), X_sg])
b1 = np.linalg.lstsq(X1, tc_all, rcond=None)[0]
r2_sg_only = 1 - np.sum((tc_all - X1 @ b1)**2) / np.sum((tc_all - np.mean(tc_all))**2)

# SC_class only
X2 = np.column_stack([np.ones(n_total), X_sc])
b2 = np.linalg.lstsq(X2, tc_all, rcond=None)[0]
r2_sc_only = 1 - np.sum((tc_all - X2 @ b2)**2) / np.sum((tc_all - np.mean(tc_all))**2)

# SG + SC_class
X3 = np.column_stack([np.ones(n_total), X_sc, X_sg])
b3 = np.linalg.lstsq(X3, tc_all, rcond=None)[0]
r2_both = 1 - np.sum((tc_all - X3 @ b3)**2) / np.sum((tc_all - np.mean(tc_all))**2)

print(f"\n  Model comparison:")
print(f"    Tc ~ SG only:           R^2 = {r2_sg_only:.4f}  (eta^2 = {eta_sg:.4f})")
print(f"    Tc ~ SC_class only:     R^2 = {r2_sc_only:.4f}  (eta^2 = {eta_sc:.4f})")
print(f"    Tc ~ SC_class + SG:     R^2 = {r2_both:.4f}")
print(f"    SG incremental:         +{r2_both - r2_sc_only:.4f} after SC_class")
print(f"    SC_class incremental:   +{r2_both - r2_sg_only:.4f} after SG")
print(f"    Shared variance:        {r2_sg_only + r2_sc_only - r2_both:.4f}")

print(f"\n  Interpretation:")
if r2_both - r2_sc_only > 0.10:
    print(f"    SG adds {r2_both - r2_sc_only:.1%} of variance beyond chemical family.")
    print(f"    This is INDEPENDENT STRUCTURE, not a proxy.")
elif r2_both - r2_sc_only > 0.03:
    print(f"    SG adds moderate variance ({r2_both - r2_sc_only:.1%}) beyond chemical family.")
else:
    print(f"    SG adds minimal variance beyond chemical family. Possible proxy.")


# ============================================================
# Strategy E: Random SG subsample stability
# ============================================================
print()
print("=" * 100)
print("STRATEGY E: Subsample stability — is eta^2 stable across random 50% splits?")
print("=" * 100)

split_etas = []
for i in range(20):
    idx = np.arange(n_total)
    rng.shuffle(idx)
    half = idx[:n_total // 2]
    eta_half, _, _ = eta_squared(tc_all[half], [sg_all[j] for j in half])
    split_etas.append(eta_half)

split_etas = np.array(split_etas)
print(f"  20 random 50% splits:")
print(f"    Mean eta^2:  {np.mean(split_etas):.4f}")
print(f"    Std:         {np.std(split_etas):.4f}")
print(f"    CV:          {np.std(split_etas) / np.mean(split_etas):.4f}")
print(f"    Min:         {np.min(split_etas):.4f}")
print(f"    Max:         {np.max(split_etas):.4f}")
print(f"    Full-sample: 0.4565")


# ============================================================
# FINAL VERDICT
# ============================================================
print()
print("=" * 100)
print("FINAL REPLICATION VERDICT")
print("=" * 100)

print(f"""
  CLAIM: SG -> Tc, eta^2 = 0.457, independent of chemical family, irreducible

  EVIDENCE:
    A. Stanev cross-match:       {'eta^2 = ' + f'{eta_a:.4f}' if matched and valid_sgs >= 2 else 'Insufficient formula matches (format incompatibility)'}
    B. Leave-one-class-out OOS:  {'weighted R^2 = ' + f'{weighted_r2:.4f}' if loocv_results else 'N/A'}
    C. Permutation null:         z = {z_score:.1f}, p = {p_value:.6f} ({real_eta / np.mean(null_etas):.0f}x above null)
    D. SG incremental after SC:  +{r2_both - r2_sc_only:.4f}
    E. Subsample stability:      CV = {np.std(split_etas) / np.mean(split_etas):.4f}

  OVERALL:""")

# Tally
passes = 0
tests_run = 0

if matched and valid_sgs >= 2:
    tests_run += 1
    if eta_a > 0.20: passes += 1

if loocv_results:
    tests_run += 1
    if weighted_r2 > 0.10: passes += 1

tests_run += 1  # permutation always runs
if p_value < 0.001: passes += 1

tests_run += 1  # incremental
if r2_both - r2_sc_only > 0.05: passes += 1

tests_run += 1  # subsample
if np.std(split_etas) / np.mean(split_etas) < 0.10: passes += 1

print(f"    {passes}/{tests_run} replication tests passed")
if passes >= tests_run - 1:
    print(f"    VERDICT: SG -> Tc REPLICATES. This is a robust, independent phenomenon.")
elif passes >= tests_run // 2:
    print(f"    VERDICT: SG -> Tc PARTIALLY REPLICATES. Some tests show weakness.")
else:
    print(f"    VERDICT: SG -> Tc FAILS REPLICATION. Likely a dataset-specific artifact.")
