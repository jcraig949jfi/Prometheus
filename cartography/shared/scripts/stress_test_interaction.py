#!/usr/bin/env python3
"""
Stress Test 3: Interaction classification for ALL categorical findings.

For every categorical -> continuous finding in the re-audit:
- Compute main effect eta^2
- Compute interaction eta^2 (where a secondary grouping exists)
- Compute transferability (leave-one-group-out OOS R^2)
- Classify: UNIVERSAL / CONDITIONAL / PURE_INTERACTION / CONTEXT_LOCKED
"""

import sys, os, json, csv, io, re
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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


def leave_one_group_out(values, primary_labels, secondary_labels):
    """Leave-one-secondary-group-out OOS R^2 for primary -> values."""
    values = np.array(values, dtype=float)
    sec_groups = sorted(set(secondary_labels))
    n = len(values)

    results = []
    for held_out in sec_groups:
        test_mask = np.array([s == held_out for s in secondary_labels])
        train_mask = ~test_mask
        n_test = np.sum(test_mask)
        if n_test < 10:
            continue

        # Learn primary group means from training
        train_groups = defaultdict(list)
        for i in range(n):
            if train_mask[i]:
                train_groups[primary_labels[i]].append(values[i])
        train_means = {k: np.mean(v) for k, v in train_groups.items() if len(v) >= 3}
        grand_mean = np.mean(values[train_mask])

        # Predict test
        test_vals = values[test_mask]
        test_primary = [primary_labels[i] for i in range(n) if test_mask[i]]
        predicted = np.array([train_means.get(p, grand_mean) for p in test_primary])

        ss_total_test = np.sum((test_vals - np.mean(test_vals))**2)
        ss_resid = np.sum((test_vals - predicted)**2)
        r2_oos = 1 - ss_resid / ss_total_test if ss_total_test > 0 else 0

        results.append({"group": held_out, "n": int(n_test), "r2_oos": r2_oos})

    return results


# ============================================================
# Load all datasets
# ============================================================
print("Loading datasets...")

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
        if tc > 0 and sg and sc_class:
            elements = set(re.findall(r'[A-Z][a-z]?', formula))
            sc_rows.append({"tc": tc, "sg": sg, "cs": cs, "sc_class": sc_class,
                           "n_elements": len(elements)})
    except:
        pass

# Genus-2
g2 = json.load(open(DATA / "genus2/data/genus2_curves_full.json", encoding="utf-8"))
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]

# Number fields
nf = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))

print(f"  sc={len(sc_rows)}, g2={len(valid_g2)}, nf={len(nf)}")

# ============================================================
# Build finding list with interaction structure
# ============================================================
print()
print("=" * 110)
print("INTERACTION CLASSIFICATION: All categorical findings")
print(f"{'ID':>6s} | {'eta^2':>8s} | {'OOS R^2':>8s} | {'interact':>8s} | {'Type':15s} | claim")
print("-" * 110)

findings = []

def classify_finding(name, values, primary_labels, secondary_labels=None, claim=""):
    """Full interaction classification for one finding."""
    eta, n, k = eta_sq(values, primary_labels)
    if np.isnan(eta):
        return

    # Leave-one-group-out (if secondary grouping exists)
    oos_results = []
    interaction_r2 = float("nan")
    if secondary_labels is not None:
        oos_results = leave_one_group_out(values, primary_labels, secondary_labels)

    if oos_results:
        weighted_oos = sum(r["r2_oos"] * r["n"] for r in oos_results) / sum(r["n"] for r in oos_results)

        # Interaction: fit additive vs cell-means model
        vals = np.array(values, dtype=float)
        n_total = len(vals)

        def one_hot(labels):
            unique = sorted(set(labels))
            mat = np.zeros((len(labels), max(len(unique) - 1, 1)))
            for i, l in enumerate(labels):
                idx = unique.index(l)
                if idx > 0 and idx - 1 < mat.shape[1]:
                    mat[i, idx - 1] = 1
            return mat

        X_p = one_hot(primary_labels)
        X_s = one_hot(secondary_labels)

        # Additive model
        X_add = np.column_stack([np.ones(n_total), X_p, X_s])
        b_add = np.linalg.lstsq(X_add, vals, rcond=None)[0]
        ss_res_add = np.sum((vals - X_add @ b_add)**2)
        ss_tot = np.sum((vals - np.mean(vals))**2)
        r2_add = 1 - ss_res_add / ss_tot

        # Cell-means model
        cell_labels = [f"{p}|{s}" for p, s in zip(primary_labels, secondary_labels)]
        cell_groups = defaultdict(list)
        for v, cl in zip(vals, cell_labels):
            cell_groups[cl].append(v)
        cell_means = {cl: np.mean(v) for cl, v in cell_groups.items() if len(v) >= 2}
        pred_cell = np.array([cell_means.get(cl, np.mean(vals)) for cl in cell_labels])
        ss_res_cell = np.sum((vals - pred_cell)**2)
        r2_cell = 1 - ss_res_cell / ss_tot

        interaction_r2 = r2_cell - r2_add
    else:
        weighted_oos = float("nan")

    # Classify
    if np.isnan(weighted_oos):
        if eta >= 0.14:
            ftype = "UNIVERSAL_LAW"
        elif eta >= 0.01:
            ftype = "TENDENCY"
        else:
            ftype = "NEGLIGIBLE"
    elif weighted_oos > 0.15:
        ftype = "UNIVERSAL_LAW"
    elif weighted_oos > 0.0 and eta >= 0.14:
        ftype = "CONDITIONAL_LAW"
    elif weighted_oos < -1.0:
        ftype = "CONTEXT_LOCKED"
    elif not np.isnan(interaction_r2) and interaction_r2 > eta * 0.5:
        ftype = "PURE_INTERACTION"
    elif eta >= 0.14:
        ftype = "CONDITIONAL_LAW"
    elif eta >= 0.01:
        ftype = "TENDENCY"
    else:
        ftype = "NEGLIGIBLE"

    oos_str = f"{weighted_oos:8.4f}" if not np.isnan(weighted_oos) else "    N/A "
    int_str = f"{interaction_r2:8.4f}" if not np.isnan(interaction_r2) else "    N/A "
    print(f"  {name:>4s} | {eta:8.4f} | {oos_str} | {int_str} | {ftype:15s} | {claim[:50]}")

    findings.append({"name": name, "eta2": eta, "oos_r2": weighted_oos,
                      "interaction_r2": interaction_r2, "type": ftype, "claim": claim})

# ============================================================
# Run all findings
# ============================================================

# Superconductor findings
sc_tc = [r["tc"] for r in sc_rows]
sc_sg = [r["sg"] for r in sc_rows]
sc_cls = [r["sc_class"] for r in sc_rows]
sc_cs = [r["cs"] for r in sc_rows]
sc_ne = [r["n_elements"] for r in sc_rows]

classify_finding("SC.1", sc_tc, sc_cls, sc_sg, "SC_class -> Tc")
classify_finding("SC.2", sc_tc, sc_sg, sc_cls, "SG -> Tc")
classify_finding("SC.3", sc_tc, sc_ne, sc_cls, "N_elements -> Tc")
classify_finding("SC.4", sc_tc, sc_cs, sc_cls, "Crystal system -> Tc")

# Number field findings
valid_nf_gal = [f for f in nf if f.get("class_number") and f.get("galois_label") and f.get("degree")]
if valid_nf_gal:
    nf_cn = [f["class_number"] for f in valid_nf_gal]
    nf_gal = [f["galois_label"] for f in valid_nf_gal]
    nf_deg = [str(f["degree"]) for f in valid_nf_gal]
    classify_finding("NF.1", nf_cn, nf_gal, nf_deg, "Galois group -> class number")
    classify_finding("NF.2", nf_cn, nf_deg, nf_gal, "Degree -> class number")

# Genus-2 findings
g2_cond = [c["conductor"] for c in valid_g2]
g2_st = [c["st_group"] for c in valid_g2]
classify_finding("G2.1", g2_cond, g2_st, claim="ST group -> conductor")

g2_disc = [abs(c["discriminant"]) for c in valid_g2 if c.get("discriminant", 0) != 0]
g2_st_disc = [c["st_group"] for c in valid_g2 if c.get("discriminant", 0) != 0]
classify_finding("G2.2", g2_disc, g2_st_disc, claim="ST group -> |discriminant|")

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 110)
print("INTERACTION CLASSIFICATION SUMMARY")
print("=" * 110)

types = defaultdict(list)
for f in findings:
    types[f["type"]].append(f)

for t in ["UNIVERSAL_LAW", "CONDITIONAL_LAW", "PURE_INTERACTION", "CONTEXT_LOCKED", "TENDENCY", "NEGLIGIBLE"]:
    items = types.get(t, [])
    if items:
        print(f"\n  {t} ({len(items)}):")
        for f in items:
            oos = f"OOS={f['oos_r2']:.3f}" if not np.isnan(f['oos_r2']) else "OOS=N/A"
            print(f"    {f['name']:6s}: eta^2={f['eta2']:.4f}, {oos} | {f['claim']}")
