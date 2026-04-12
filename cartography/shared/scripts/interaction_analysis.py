#!/usr/bin/env python3
"""
Interaction Analysis: SG x SC_class -> Tc

Priority 1: Map the interaction surface (SG rankings per class, consistency)
Priority 2: Quantify interaction strength (eta^2 of interaction term)
Priority 3: Within-class PCA (is irreducibility global or local?)
Priority 4: SG distribution bias (compositional skew)
"""

import sys, os, csv, io, re
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

# ============================================================
# Load data
# ============================================================
print("Loading data...")
csv_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
sc_rows = []
with open(csv_path, "r") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        sc_class = row.get("sc_class", "").strip()
        if tc > 0 and sg and sc_class:
            sc_rows.append({"tc": tc, "sg": sg, "sc_class": sc_class})
    except:
        pass

print(f"Loaded {len(sc_rows)} rows")

tc_all = np.array([r["tc"] for r in sc_rows])
sg_all = [r["sg"] for r in sc_rows]
sc_all = [r["sc_class"] for r in sc_rows]
n = len(tc_all)

classes = sorted(set(sc_all))
all_sgs = sorted(set(sg_all))

# ============================================================
# PRIORITY 1: Map the interaction surface
# ============================================================
print()
print("=" * 110)
print("PRIORITY 1: INTERACTION SURFACE — SG rankings per class")
print("=" * 110)

# For each class, compute mean Tc per SG (min 5 members)
class_sg_means = {}  # class -> {sg: (mean_tc, n)}
for cls in classes:
    sg_groups = defaultdict(list)
    for r in sc_rows:
        if r["sc_class"] == cls:
            sg_groups[r["sg"]].append(r["tc"])
    class_sg_means[cls] = {}
    for sg, tcs in sg_groups.items():
        if len(tcs) >= 3:
            class_sg_means[cls][sg] = (np.mean(tcs), len(tcs))

# Find SGs that appear in multiple classes
sg_class_count = defaultdict(set)
for cls, sg_dict in class_sg_means.items():
    for sg in sg_dict:
        sg_class_count[sg].add(cls)

multi_class_sgs = {sg: classes for sg, classes in sg_class_count.items() if len(classes) >= 2}
print(f"\n  SGs appearing in >= 2 classes (min 3 per class): {len(multi_class_sgs)}")

# Print the interaction surface for multi-class SGs
print(f"\n  {'SG':20s}", end="")
for cls in classes:
    if sum(1 for sg in multi_class_sgs if cls in multi_class_sgs[sg]) > 0:
        print(f" | {cls[:10]:>10s}", end="")
active_classes = [cls for cls in classes if sum(1 for sg in multi_class_sgs if cls in multi_class_sgs[sg]) > 0]
print()
print("  " + "-" * (22 + 13 * len(active_classes)))

for sg in sorted(multi_class_sgs.keys(), key=lambda s: -len(multi_class_sgs[s])):
    print(f"  {sg:20s}", end="")
    vals = []
    for cls in active_classes:
        if cls in class_sg_means and sg in class_sg_means[cls]:
            mean_tc, cnt = class_sg_means[cls][sg]
            print(f" | {mean_tc:7.1f}({cnt:2d})", end="")
            vals.append((cls, mean_tc))
        else:
            print(f" | {'':>10s}", end="")
    print()

# Rank consistency analysis
print(f"\n  RANK CONSISTENCY: Do SGs rank the same way across classes?")
print(f"  For each pair of classes sharing >= 3 SGs, compute Spearman rank correlation")
print()

from scipy.stats import spearmanr

rank_pairs = []
print(f"  {'Class A':15s} vs {'Class B':15s} | {'shared SGs':>10s} | {'Spearman r':>10s} | {'p':>8s} | Pattern")
print("  " + "-" * 80)

for i, cls_a in enumerate(active_classes):
    for cls_b in active_classes[i+1:]:
        shared = set(class_sg_means.get(cls_a, {}).keys()) & set(class_sg_means.get(cls_b, {}).keys())
        if len(shared) >= 3:
            ranks_a = [class_sg_means[cls_a][sg][0] for sg in sorted(shared)]
            ranks_b = [class_sg_means[cls_b][sg][0] for sg in sorted(shared)]
            if len(set(ranks_a)) > 1 and len(set(ranks_b)) > 1:
                rho, p = spearmanr(ranks_a, ranks_b)
            else:
                rho, p = 0, 1
            pattern = "CONSISTENT" if rho > 0.5 else "INVERTED" if rho < -0.3 else "INDEPENDENT"
            print(f"  {cls_a:15s} vs {cls_b:15s} | {len(shared):10d} | {rho:10.3f} | {p:8.4f} | {pattern}")
            rank_pairs.append({"a": cls_a, "b": cls_b, "n": len(shared), "rho": rho, "p": p})

if rank_pairs:
    mean_rho = np.mean([r["rho"] for r in rank_pairs])
    print(f"\n  Mean Spearman rho: {mean_rho:.3f}")
    if mean_rho > 0.3:
        print(f"  Pattern: PARTIAL UNIVERSALITY — SG rankings weakly consistent across classes")
    elif mean_rho < -0.1:
        print(f"  Pattern: INVERTED — same SGs predict opposite Tc in different classes")
    else:
        print(f"  Pattern: INDEPENDENT — SG rankings unrelated across classes (pure interaction)")


# ============================================================
# PRIORITY 2: Quantify interaction strength
# ============================================================
print()
print("=" * 110)
print("PRIORITY 2: INTERACTION STRENGTH — Tc ~ SC_class + SG + SC_class x SG")
print("=" * 110)

def one_hot(labels):
    unique = sorted(set(labels))
    mat = np.zeros((len(labels), len(unique) - 1))
    for i, l in enumerate(labels):
        idx = unique.index(l)
        if idx > 0:
            mat[i, idx - 1] = 1
    return mat, unique

# Main effects
X_sg, sg_cats = one_hot(sg_all)
X_sc, sc_cats = one_hot(sc_all)

# Interaction terms: for each (sc_class, sg) pair with enough data
# Use cell means approach: create indicator for each (class, sg) cell
cell_labels = [f"{r['sc_class']}|{r['sg']}" for r in sc_rows]
cell_counts = defaultdict(int)
for cl in cell_labels:
    cell_counts[cl] += 1

# Model 1: Tc ~ SC_class (main effect only)
X1 = np.column_stack([np.ones(n), X_sc])
b1 = np.linalg.lstsq(X1, tc_all, rcond=None)[0]
ss_res1 = np.sum((tc_all - X1 @ b1)**2)
ss_total = np.sum((tc_all - np.mean(tc_all))**2)
r2_sc = 1 - ss_res1 / ss_total

# Model 2: Tc ~ SC_class + SG (additive)
X2 = np.column_stack([np.ones(n), X_sc, X_sg])
b2 = np.linalg.lstsq(X2, tc_all, rcond=None)[0]
ss_res2 = np.sum((tc_all - X2 @ b2)**2)
r2_additive = 1 - ss_res2 / ss_total

# Model 3: Tc ~ cell means (full interaction = saturated within cells)
# This is equivalent to fitting a separate mean for each (class, sg) combination
valid_cells = {cl for cl, cnt in cell_counts.items() if cnt >= 2}
cell_label_arr = np.array(cell_labels)
# For each observation, predict with its cell mean
cell_means_map = {}
for cl in valid_cells:
    mask = cell_label_arr == cl
    cell_means_map[cl] = np.mean(tc_all[mask])

# For observations in valid cells, use cell mean; others use additive prediction
pred_interaction = X2 @ b2  # default to additive
for i, cl in enumerate(cell_labels):
    if cl in cell_means_map:
        pred_interaction[i] = cell_means_map[cl]

ss_res3 = np.sum((tc_all - pred_interaction)**2)
r2_interaction = 1 - ss_res3 / ss_total

# Decomposition
r2_sc_main = r2_sc
r2_sg_given_sc = r2_additive - r2_sc
r2_interaction_term = r2_interaction - r2_additive
r2_residual = 1 - r2_interaction

print(f"\n  VARIANCE DECOMPOSITION:")
print(f"    {'Component':30s} | {'R^2':>8s} | {'% of total':>10s}")
print("    " + "-" * 55)
print(f"    {'SC_class (main)':30s} | {r2_sc_main:8.4f} | {r2_sc_main*100:10.1f}%")
print(f"    {'SG (main, after SC_class)':30s} | {r2_sg_given_sc:8.4f} | {r2_sg_given_sc*100:10.1f}%")
print(f"    {'SC_class x SG (interaction)':30s} | {r2_interaction_term:8.4f} | {r2_interaction_term*100:10.1f}%")
print(f"    {'Residual':30s} | {r2_residual:8.4f} | {r2_residual*100:10.1f}%")
print(f"    {'TOTAL':30s} | {1.0:8.4f} | {100.0:10.1f}%")

print(f"\n  KEY RATIOS:")
print(f"    Interaction / SG main effect: {r2_interaction_term / r2_sg_given_sc:.2f}x")
print(f"    Interaction / SC_class main:  {r2_interaction_term / r2_sc_main:.2f}x")
total_sg_related = r2_sg_given_sc + r2_interaction_term
print(f"    Total SG-related (main+inter): {total_sg_related:.4f} ({total_sg_related*100:.1f}%)")
print(f"    Of which interaction:          {r2_interaction_term / total_sg_related * 100:.0f}%")

if r2_interaction_term > r2_sg_given_sc:
    print(f"\n  VERDICT: INTERACTION DOMINATES. The SC_class x SG term ({r2_interaction_term:.4f})")
    print(f"  is larger than the additive SG term ({r2_sg_given_sc:.4f}).")
    print(f"  Space group's meaning changes across chemical families.")
elif r2_interaction_term > 0.05:
    print(f"\n  VERDICT: STRONG INTERACTION. Both main and interaction contribute.")
else:
    print(f"\n  VERDICT: ADDITIVE DOMINATES. SG effect is mostly consistent across classes.")


# ============================================================
# PRIORITY 3: Within-class PCA — is irreducibility global or local?
# ============================================================
print()
print("=" * 110)
print("PRIORITY 3: WITHIN-CLASS PCA — is the SG signal reducible WITHIN classes?")
print("=" * 110)

for cls in classes:
    stratum = [r for r in sc_rows if r["sc_class"] == cls]
    if len(stratum) < 50:
        continue

    tc_s = np.array([r["tc"] for r in stratum])
    sg_s = [r["sg"] for r in stratum]
    n_s = len(tc_s)

    # SGs with >= 3 members in this class
    sg_counts_s = defaultdict(int)
    for s in sg_s:
        sg_counts_s[s] += 1
    valid_sgs_s = sorted([s for s, c in sg_counts_s.items() if c >= 3])

    if len(valid_sgs_s) < 3:
        print(f"\n  {cls}: only {len(valid_sgs_s)} valid SGs, skipping PCA")
        continue

    # One-hot encode SGs for this class
    X_sg_s = np.zeros((n_s, len(valid_sgs_s) - 1))
    for i, label in enumerate(sg_s):
        if label in valid_sgs_s:
            idx = valid_sgs_s.index(label)
            if idx > 0:
                X_sg_s[i, idx - 1] = 1

    # Center Tc
    tc_centered = tc_s - np.mean(tc_s)

    # SVD of SG encoding
    U, S, Vt = np.linalg.svd(X_sg_s, full_matrices=False)

    # Cumulative R^2 of top k PCs predicting Tc
    max_k = min(len(S), 30)
    cumul_r2 = []
    for k in range(1, max_k + 1):
        X_pcs = np.column_stack([np.ones(n_s), U[:, :k]])
        beta = np.linalg.lstsq(X_pcs, tc_centered, rcond=None)[0]
        pred = X_pcs @ beta
        ss_res = np.sum((tc_centered - pred)**2)
        r2 = 1 - ss_res / np.sum(tc_centered**2)
        cumul_r2.append(r2)

    max_r2 = cumul_r2[-1] if cumul_r2 else 0

    # Find k for 50%, 90%
    k_50 = next((k+1 for k, r2 in enumerate(cumul_r2) if r2 >= 0.50 * max_r2), max_k)
    k_90 = next((k+1 for k, r2 in enumerate(cumul_r2) if r2 >= 0.90 * max_r2), max_k)

    # Participation ratio
    pc_r2_indiv = []
    for k in range(max_k):
        r_single = np.corrcoef(U[:, k], tc_centered)[0, 1] if np.std(U[:, k]) > 0 else 0
        pc_r2_indiv.append(r_single**2)
    pc_r2_arr = np.array(pc_r2_indiv)
    pr = (np.sum(pc_r2_arr))**2 / np.sum(pc_r2_arr**2) if np.sum(pc_r2_arr**2) > 0 else 0

    verdict = "REDUCIBLE" if k_90 <= 3 else "PARTIALLY" if k_90 <= 8 else "IRREDUCIBLE"

    print(f"\n  {cls} (n={n_s}, valid_SGs={len(valid_sgs_s)}):")
    print(f"    Max R^2 (all PCs): {max_r2:.4f}")
    print(f"    PCs for 50% signal: {k_50}")
    print(f"    PCs for 90% signal: {k_90}")
    print(f"    Participation ratio: {pr:.1f}")
    print(f"    VERDICT: {verdict}")

    # Show top 3 PCs
    for k in range(min(5, len(cumul_r2))):
        incr = cumul_r2[k] - (cumul_r2[k-1] if k > 0 else 0)
        print(f"      PC{k+1}: cumul R^2={cumul_r2[k]:.4f}, incr={incr:.4f}")


# ============================================================
# PRIORITY 4: SG distribution bias
# ============================================================
print()
print("=" * 110)
print("PRIORITY 4: SG DISTRIBUTION BIAS — how skewed is SG usage across classes?")
print("=" * 110)

# For each SG, what fraction of its members are in each class?
sg_class_dist = defaultdict(lambda: defaultdict(int))
for r in sc_rows:
    sg_class_dist[r["sg"]][r["sc_class"]] += 1

# Entropy of class distribution per SG
print(f"\n  {'SG':20s} | {'n':>5s} | {'n_classes':>9s} | {'entropy':>7s} | {'dominant class':25s} | {'dom %':>5s}")
print("  " + "-" * 85)

sg_entropies = []
for sg in sorted(all_sgs, key=lambda s: -sum(sg_class_dist[s].values())):
    total = sum(sg_class_dist[sg].values())
    if total < 10:
        continue
    dist = sg_class_dist[sg]
    n_classes = len(dist)
    probs = np.array([v / total for v in dist.values()])
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    max_entropy = np.log2(len(classes))
    dominant = max(dist, key=dist.get)
    dom_frac = dist[dominant] / total

    sg_entropies.append(entropy / max_entropy)
    print(f"  {sg:20s} | {total:5d} | {n_classes:9d} | {entropy:7.3f} | {dominant:25s} | {dom_frac:5.0%}")

if sg_entropies:
    print(f"\n  Mean normalized entropy: {np.mean(sg_entropies):.3f}")
    print(f"  SGs with >90% in one class: {sum(1 for e in sg_entropies if e < 0.15)}/{len(sg_entropies)}")
    print(f"  SGs with even spread (H > 0.5): {sum(1 for e in sg_entropies if e > 0.5)}/{len(sg_entropies)}")

    if np.mean(sg_entropies) < 0.3:
        print(f"\n  VERDICT: HIGHLY SKEWED. Most SGs are concentrated in one class.")
        print(f"  A large part of global eta^2 is compositional bias, not pure SG effect.")
    elif np.mean(sg_entropies) < 0.5:
        print(f"\n  VERDICT: MODERATELY SKEWED. Some SGs span classes, many don't.")
    else:
        print(f"\n  VERDICT: WELL-DISTRIBUTED. SGs span multiple classes.")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 110)
print("INTEGRATED SUMMARY")
print("=" * 110)

print(f"""
  VARIANCE DECOMPOSITION of Tc:
    SC_class main effect:       {r2_sc_main*100:.1f}%
    SG main effect (after SC):  {r2_sg_given_sc*100:.1f}%
    SC_class x SG interaction:  {r2_interaction_term*100:.1f}%
    Residual:                   {r2_residual*100:.1f}%

  INTERACTION ANALYSIS:
    Interaction / SG main:      {r2_interaction_term / r2_sg_given_sc:.2f}x
    Mean rank correlation:      {np.mean([r['rho'] for r in rank_pairs]) if rank_pairs else 'N/A':.3f}

  REVISED ONTOLOGY:
    SG -> Tc:                   CONDITIONAL LAW (interaction-dominated)
    SC_class -> Tc:             UNIVERSAL LAW (transfers across structures)
    SG x SC_class -> Tc:        The dominant mechanism

  INTERPRETATION:
    Space group defines the constraint language.
    Chemical family defines the constraint semantics.
    The same symmetry imposes different Tc constraints in different electronic environments.
""")
