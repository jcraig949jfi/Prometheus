#!/usr/bin/env python3
"""
LAW Independence Analysis — How many independent axes control Tc?

For the 7 LAWS found by the re-audit, determine:
1. Partial eta² (each predictor controlling for each other)
2. Sequential variance decomposition (incremental R²)
3. Classification: Independent axes / Mediated / Redundant cluster

Case A (Independent): SG explains large variance after controlling for others
Case B (Mediated):    SG→Tc disappears after controlling for Volume/Density
Case C (Redundant):   All collapse into one latent variable
"""

import sys, json, csv, io, re, os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

DATA = Path(__file__).resolve().parent.parent.parent  # cartography/

# ============================================================
# Load superconductor data
# ============================================================
print("Loading superconductor data...")
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
                             ("fe", "formation_energy_per_atom_2"), ("bg", "band_gap_2")]:
                try: r[key] = float(row.get(col, ""))
                except: r[key] = None
            elements = set(re.findall(r'[A-Z][a-z]?', formula))
            r["n_elements"] = len(elements)
            sc_rows.append(r)
    except:
        pass

# Filter to complete cases (all continuous vars present)
complete = [r for r in sc_rows if all(r[k] is not None for k in ["vol", "density", "fe"])]
print(f"Total rows: {len(sc_rows)}, Complete cases (Tc + Vol + Den + FE): {len(complete)}")

# ============================================================
# Helper: eta² from one-way ANOVA
# ============================================================
def eta_squared(values, labels, min_group=5):
    """Compute eta² (proportion of variance explained by grouping)."""
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
    n = len(all_v)
    k = len(valid)
    return ss_between / ss_total if ss_total > 0 else 0, n, k


def partial_eta_categorical(outcome, focal_cat, control_cont):
    """
    Partial eta² for a categorical predictor after removing a continuous control.

    Method: regress outcome on control, take residuals, then compute eta²
    of focal_cat on those residuals.
    """
    outcome = np.array(outcome, dtype=float)
    control = np.array(control_cont, dtype=float)

    # Remove control effect via OLS residuals
    mask = np.isfinite(outcome) & np.isfinite(control)
    outcome = outcome[mask]
    control = control[mask]
    focal_cat_filtered = [focal_cat[i] for i in range(len(mask)) if mask[i]]

    # OLS: outcome ~ control
    X = np.column_stack([np.ones(len(control)), control])
    beta = np.linalg.lstsq(X, outcome, rcond=None)[0]
    residuals = outcome - X @ beta

    eta, n, k = eta_squared(residuals, focal_cat_filtered)
    return eta, n, k


def partial_eta_cat_cat(outcome, focal_cat, control_cat):
    """
    Partial eta² for a categorical predictor after removing another categorical control.

    Method: compute group means by control_cat, subtract, then eta² of focal on residuals.
    """
    outcome = np.array(outcome, dtype=float)

    # Compute control group means
    control_means = defaultdict(list)
    for v, c in zip(outcome, control_cat):
        control_means[c].append(v)
    control_means = {k: np.mean(v) for k, v in control_means.items()}

    # Residualize
    residuals = np.array([v - control_means[c] for v, c in zip(outcome, control_cat)])

    eta, n, k = eta_squared(residuals, focal_cat)
    return eta, n, k


def sequential_r2(outcome, predictors_ordered, predictor_names):
    """
    Sequential variance decomposition.

    For each predictor added in order, compute:
    - Total R² of model so far
    - Incremental R² added by this predictor

    Categorical predictors are one-hot encoded.
    """
    outcome = np.array(outcome, dtype=float)
    n = len(outcome)
    ss_total = np.sum((outcome - np.mean(outcome)) ** 2)

    X_cumulative = np.ones((n, 1))  # intercept
    results = []
    prev_r2 = 0.0

    for pred, name in zip(predictors_ordered, predictor_names):
        pred = np.array(pred)

        # Check if categorical
        try:
            pred_float = pred.astype(float)
            # Continuous: add as single column
            X_new = pred_float.reshape(-1, 1)
        except (ValueError, TypeError):
            # Categorical: one-hot encode
            unique_labels = sorted(set(pred))
            # Drop first for identifiability
            X_new = np.zeros((n, len(unique_labels) - 1))
            for j, label in enumerate(unique_labels[1:]):
                X_new[:, j] = (pred == label).astype(float)

        X_cumulative = np.hstack([X_cumulative, X_new])

        # OLS
        beta = np.linalg.lstsq(X_cumulative, outcome, rcond=None)[0]
        predicted = X_cumulative @ beta
        ss_residual = np.sum((outcome - predicted) ** 2)
        r2 = 1 - ss_residual / ss_total

        incremental = r2 - prev_r2
        results.append({
            "predictor": name,
            "cumulative_r2": r2,
            "incremental_r2": incremental,
            "n_params": X_cumulative.shape[1],
        })
        prev_r2 = r2

    return results


# ============================================================
# PART 1: Pairwise Partial eta²
# ============================================================
print()
print("=" * 100)
print("PART 1: PAIRWISE PARTIAL eta² — Does each LAW survive controlling for the others?")
print("=" * 100)

# Extract arrays from complete cases
tc = [r["tc"] for r in complete]
sg = [r["sg"] for r in complete]
sc_class = [r["sc_class"] for r in complete]
n_elem = [r["n_elements"] for r in complete]
vol = [r["vol"] for r in complete]
density = [r["density"] for r in complete]
fe = [r["fe"] for r in complete]
cs = [r["cs"] for r in complete]

# Baseline eta² (unconditional)
print()
print("Baseline (unconditional) eta²:")
print(f"  {'Predictor':30s} | {'eta²':>8s} | {'n':>6s} | {'groups':>6s}")
print("-" * 60)
for name, labels in [("SG → Tc", sg), ("SC_class → Tc", sc_class),
                      ("N_elements → Tc", n_elem), ("Crystal_system → Tc", cs)]:
    eta, n, k = eta_squared(tc, labels)
    print(f"  {name:30s} | {eta:8.4f} | {n:6d} | {k:6d}")

# Continuous predictors as "LAWs" - compute R² equivalent
print()
for name, vals in [("Volume → Tc", vol), ("Density → Tc", density), ("Form_energy → Tc", fe)]:
    tc_arr = np.array(tc)
    v_arr = np.array(vals)
    X = np.column_stack([np.ones(len(v_arr)), v_arr])
    beta = np.linalg.lstsq(X, tc_arr, rcond=None)[0]
    ss_res = np.sum((tc_arr - X @ beta) ** 2)
    ss_tot = np.sum((tc_arr - np.mean(tc_arr)) ** 2)
    r2 = 1 - ss_res / ss_tot
    print(f"  {name:30s} | R²={r2:8.4f} (linear)")

# Partial eta²: categorical predictors controlling for continuous ones
print()
print("Partial eta² — categorical predictors controlling for continuous variables:")
print(f"  {'Test':50s} | {'partial eta²':>12s}")
print("-" * 70)

cat_predictors = [("SG", sg), ("SC_class", sc_class), ("N_elements", n_elem), ("Crystal_system", cs)]
cont_controls = [("Volume", vol), ("Density", density), ("Form_energy", fe)]

for cat_name, cat_vals in cat_predictors:
    for cont_name, cont_vals in cont_controls:
        peta, n, k = partial_eta_categorical(tc, cat_vals, cont_vals)
        print(f"  eta²({cat_name:12s} → Tc | {cont_name:12s}) | {peta:12.4f}")
    print()

# Partial eta²: categorical controlling for categorical
print("Partial eta² — categorical predictors controlling for each other:")
print(f"  {'Test':50s} | {'partial eta²':>12s}")
print("-" * 70)

for i, (name_i, vals_i) in enumerate(cat_predictors):
    for j, (name_j, vals_j) in enumerate(cat_predictors):
        if i == j:
            continue
        peta, n, k = partial_eta_cat_cat(tc, vals_i, vals_j)
        print(f"  eta²({name_i:12s} → Tc | {name_j:12s}) | {peta:12.4f}")
    print()


# ============================================================
# PART 2: Sequential Variance Decomposition
# ============================================================
print()
print("=" * 100)
print("PART 2: SEQUENTIAL VARIANCE DECOMPOSITION — How much does each variable add?")
print("=" * 100)

# Multiple orderings to check for order dependence
orderings = [
    ("SC_class first", [sc_class, sg, n_elem, vol, density, fe],
     ["SC_class", "SG", "N_elements", "Volume", "Density", "Form_energy"]),
    ("SG first", [sg, sc_class, n_elem, vol, density, fe],
     ["SG", "SC_class", "N_elements", "Volume", "Density", "Form_energy"]),
    ("Continuous first", [vol, density, fe, sc_class, sg, n_elem],
     ["Volume", "Density", "Form_energy", "SC_class", "SG", "N_elements"]),
    ("N_elements first", [n_elem, sc_class, sg, vol, density, fe],
     ["N_elements", "SC_class", "SG", "Volume", "Density", "Form_energy"]),
]

for ordering_name, preds, names in orderings:
    print(f"\n  Ordering: {ordering_name}")
    print(f"  {'Step':5s} | {'Predictor':15s} | {'Cumul R²':>10s} | {'Incremental':>12s} | {'n_params':>8s}")
    print("  " + "-" * 65)

    seq = sequential_r2(tc, preds, names)
    for i, s in enumerate(seq):
        print(f"  {i+1:5d} | {s['predictor']:15s} | {s['cumulative_r2']:10.4f} | {s['incremental_r2']:12.4f} | {s['n_params']:8d}")

    print(f"  {'':5s} | {'TOTAL':15s} | {seq[-1]['cumulative_r2']:10.4f} |")


# ============================================================
# PART 3: The critical test — SG after everything else
# ============================================================
print()
print("=" * 100)
print("PART 3: THE CRITICAL TEST — What does SG add after all continuous controls?")
print("=" * 100)

# Model: Tc ~ Volume + Density + FE + SC_class + N_elements ... then add SG
critical_ordering = [vol, density, fe, sc_class, n_elem, sg]
critical_names = ["Volume", "Density", "Form_energy", "SC_class", "N_elements", "SG"]

print(f"\n  {'Step':5s} | {'Predictor':15s} | {'Cumul R²':>10s} | {'Incremental':>12s}")
print("  " + "-" * 55)

seq = sequential_r2(tc, critical_ordering, critical_names)
for i, s in enumerate(seq):
    marker = " ◀◀◀" if s["predictor"] == "SG" else ""
    print(f"  {i+1:5d} | {s['predictor']:15s} | {s['cumulative_r2']:10.4f} | {s['incremental_r2']:12.4f}{marker}")

sg_incremental = seq[-1]["incremental_r2"]
sc_class_incremental = seq[3]["incremental_r2"]

print()
print(f"  SG adds {sg_incremental:.4f} after everything else")
print(f"  SC_class adds {sc_class_incremental:.4f} after continuous controls")

# And the reverse: SG first, then everything else
print()
print("  Reverse: SG first, then everything else")
rev_ordering = [sg, vol, density, fe, sc_class, n_elem]
rev_names = ["SG", "Volume", "Density", "Form_energy", "SC_class", "N_elements"]

print(f"\n  {'Step':5s} | {'Predictor':15s} | {'Cumul R²':>10s} | {'Incremental':>12s}")
print("  " + "-" * 55)

seq_rev = sequential_r2(tc, rev_ordering, rev_names)
for i, s in enumerate(seq_rev):
    print(f"  {i+1:5d} | {s['predictor']:15s} | {s['cumulative_r2']:10.4f} | {s['incremental_r2']:12.4f}")


# ============================================================
# PART 4: Correlation between continuous LAW variables
# ============================================================
print()
print("=" * 100)
print("PART 4: CORRELATION MATRIX — Are the continuous variables redundant?")
print("=" * 100)

cont_names = ["Tc", "Volume", "Density", "Form_energy"]
cont_arrays = [np.array(tc), np.array(vol), np.array(density), np.array(fe)]

print(f"\n  {'':15s}", end="")
for name in cont_names:
    print(f" | {name:>12s}", end="")
print()
print("  " + "-" * 70)

for i, name_i in enumerate(cont_names):
    print(f"  {name_i:15s}", end="")
    for j, name_j in enumerate(cont_names):
        r = np.corrcoef(cont_arrays[i], cont_arrays[j])[0, 1]
        print(f" | {r:12.4f}", end="")
    print()

# VIF (Variance Inflation Factor) for the continuous variables
print()
print("  VIF (Variance Inflation Factors) for continuous predictors:")
cont_only = np.column_stack([np.array(vol), np.array(density), np.array(fe)])
for i, name in enumerate(["Volume", "Density", "Form_energy"]):
    y_i = cont_only[:, i]
    X_others = np.delete(cont_only, i, axis=1)
    X_others = np.column_stack([np.ones(len(y_i)), X_others])
    beta = np.linalg.lstsq(X_others, y_i, rcond=None)[0]
    ss_res = np.sum((y_i - X_others @ beta) ** 2)
    ss_tot = np.sum((y_i - np.mean(y_i)) ** 2)
    r2_i = 1 - ss_res / ss_tot
    vif = 1 / (1 - r2_i) if r2_i < 1 else float("inf")
    print(f"    {name:15s}: VIF = {vif:.2f} (R² with others = {r2_i:.4f})")


# ============================================================
# PART 5: Verdict
# ============================================================
print()
print("=" * 100)
print("PART 5: VERDICT — How many independent axes?")
print("=" * 100)

# Collect the key numbers
print()

# SG partial eta² after SC_class
sg_after_sc, _, _ = partial_eta_cat_cat(tc, sg, sc_class)
sc_after_sg, _, _ = partial_eta_cat_cat(tc, sc_class, sg)
sg_after_vol, _, _ = partial_eta_categorical(tc, sg, vol)
sg_after_den, _, _ = partial_eta_categorical(tc, sg, density)
sg_after_fe, _, _ = partial_eta_categorical(tc, sg, fe)

print("  Key partial eta² values:")
print(f"    SG → Tc (unconditional):      {eta_squared(tc, sg)[0]:.4f}")
print(f"    SG → Tc | Volume:             {sg_after_vol:.4f}")
print(f"    SG → Tc | Density:            {sg_after_den:.4f}")
print(f"    SG → Tc | Form_energy:        {sg_after_fe:.4f}")
print(f"    SG → Tc | SC_class:           {sg_after_sc:.4f}")
print(f"    SC_class → Tc | SG:           {sc_after_sg:.4f}")
print()

# Classification
print("  CLASSIFICATION:")
if sg_after_vol > 0.10 and sg_after_den > 0.10 and sg_after_fe > 0.10:
    print("    SG survives controlling for all continuous variables → NOT mediated by geometry/energy")
    if sg_after_sc > 0.10:
        print("    SG survives controlling for SC_class → INDEPENDENT of chemical family")
        print("    ▶ CASE A: SG is an INDEPENDENT axis of Tc control")
    elif sg_after_sc < 0.05:
        print("    SG collapses after controlling for SC_class → SC_class mediates")
        print("    ▶ CASE B: SG is MEDIATED by chemical family")
    else:
        print(f"    SG partially reduced by SC_class ({sg_after_sc:.4f}) → PARTIAL mediation")
        print("    ▶ CASE A/B: SG is partially independent, partially mediated")
else:
    low_controls = []
    if sg_after_vol < 0.10: low_controls.append("Volume")
    if sg_after_den < 0.10: low_controls.append("Density")
    if sg_after_fe < 0.10: low_controls.append("Form_energy")
    print(f"    SG weakened by: {', '.join(low_controls)}")
    print("    ▶ CASE B/C: SG is mediated or redundant")

print()
if sc_after_sg > 0.10:
    print("    SC_class survives after SG → INDEPENDENT of space group")
    print("    ▶ Chemical family adds information beyond crystal structure")
else:
    print("    SC_class collapses after SG → REDUNDANT with space group")

# Count independent axes
print()
print("  AXIS COUNT:")
axes = []
# SG: independent if survives all controls
if sg_after_vol > 0.05 and sg_after_den > 0.05 and sg_after_fe > 0.05:
    axes.append(("Crystal structure (SG)", eta_squared(tc, sg)[0]))
# SC_class: independent if survives SG
if sc_after_sg > 0.05:
    axes.append(("Chemical family (SC_class)", eta_squared(tc, sc_class)[0]))
# N_elements: check after SG + SC_class
ne_after_sg, _, _ = partial_eta_cat_cat(tc, n_elem, sg)
ne_after_sc, _, _ = partial_eta_cat_cat(tc, n_elem, sc_class)
print(f"    N_elements → Tc | SG:         {ne_after_sg:.4f}")
print(f"    N_elements → Tc | SC_class:   {ne_after_sc:.4f}")
if ne_after_sg > 0.05 and ne_after_sc > 0.05:
    axes.append(("Compositional complexity (N_elements)", eta_squared(tc, n_elem)[0]))

print()
print(f"  ═══════════════════════════════════════════")
print(f"  INDEPENDENT AXES CONTROLLING Tc: {len(axes)}")
print(f"  ═══════════════════════════════════════════")
for name, eta in axes:
    print(f"    • {name}: eta² = {eta:.4f}")
