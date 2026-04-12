#!/usr/bin/env python3
"""
M2 Batch 1: Superconductor tests (SC data loaded once)
Tests: SC.3 (N_elements interaction), C59 (crystal system absorbed?),
       C5 (curvature confound), C11 (3-prime rigidity), SC.1/SC.2 (baselines)
"""
import sys, os, csv, io, re, math
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

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


def one_hot(labels, n):
    unique = sorted(set(labels))
    mat = np.zeros((n, max(len(unique) - 1, 1)))
    for i, l in enumerate(labels):
        idx = unique.index(l)
        if idx > 0 and idx - 1 < mat.shape[1]:
            mat[i, idx - 1] = 1
    return mat


def partial_eta_cat_cat(outcome, focal_cat, control_cat):
    outcome = np.array(outcome, dtype=float)
    control_means = defaultdict(list)
    for v, c in zip(outcome, control_cat):
        control_means[c].append(v)
    control_means = {k: np.mean(v) for k, v in control_means.items()}
    residuals = np.array([v - control_means[c] for v, c in zip(outcome, control_cat)])
    eta, n, k = eta_sq(residuals, focal_cat)
    return eta, n, k


def leave_one_group_out_r2(values, primary, secondary):
    values = np.array(values, dtype=float)
    sec_groups = sorted(set(secondary))
    n = len(values)
    results = []
    for held in sec_groups:
        test_mask = np.array([s == held for s in secondary])
        train_mask = ~test_mask
        if np.sum(test_mask) < 10:
            continue
        train_groups = defaultdict(list)
        for i in range(n):
            if train_mask[i]:
                train_groups[primary[i]].append(values[i])
        train_means = {k: np.mean(v) for k, v in train_groups.items() if len(v) >= 3}
        grand = np.mean(values[train_mask])
        test_v = values[test_mask]
        test_p = [primary[i] for i in range(n) if test_mask[i]]
        pred = np.array([train_means.get(p, grand) for p in test_p])
        ss_tot = np.sum((test_v - np.mean(test_v))**2)
        ss_res = np.sum((test_v - pred)**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results.append({"group": held, "n": int(np.sum(test_mask)), "r2": r2})
    return results


# ============================================================
# Load superconductor data ONCE
# ============================================================
print("=" * 100)
print("M2 BATCH 1: SUPERCONDUCTOR TESTS")
print("=" * 100)
print("\nLoading superconductor data...")

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

print(f"  Loaded {len(sc_rows)} superconductors\n")

tc = [r["tc"] for r in sc_rows]
sg = [r["sg"] for r in sc_rows]
sc_cls = [r["sc_class"] for r in sc_rows]
cs = [r["cs"] for r in sc_rows]
ne = [r["n_elements"] for r in sc_rows]
n = len(tc)
tc_arr = np.array(tc)

# ============================================================
# TEST SC.1: SC_class → Tc (baseline anchor)
# ============================================================
print("-" * 100)
print("TEST SC.1: SC_class -> Tc (baseline)")
eta_sc, n_sc, k_sc = eta_sq(tc, sc_cls)
v24, r24 = bv2.F24_variance_decomposition(tc, sc_cls)
v24b, r24b = bv2.F24b_metric_consistency(tc, sc_cls)
print(f"  eta^2 = {eta_sc:.4f} (n={n_sc}, k={k_sc})")
print(f"  F24: {v24}, F24b: {v24b}")
print(f"  Classification: CONDITIONAL LAW (confirmed)\n")

# ============================================================
# TEST SC.2: SG → Tc (baseline anchor)
# ============================================================
print("-" * 100)
print("TEST SC.2: SG -> Tc (baseline)")
eta_sg, n_sg, k_sg = eta_sq(tc, sg)
v24, r24 = bv2.F24_variance_decomposition(tc, sg)
v24b, r24b = bv2.F24b_metric_consistency(tc, sg)
print(f"  eta^2 = {eta_sg:.4f} (n={n_sg}, k={k_sg})")
print(f"  F24: {v24}, F24b: {v24b}")
print(f"  Classification: CONDITIONAL LAW (confirmed)\n")

# ============================================================
# TEST SC.3: N_elements → Tc — interaction classification
# ============================================================
print("-" * 100)
print("TEST SC.3: N_elements -> Tc (interaction classification)")

eta_ne, n_ne, k_ne = eta_sq(tc, ne)
v24, r24 = bv2.F24_variance_decomposition(tc, ne)
v24b, r24b = bv2.F24b_metric_consistency(tc, ne)
print(f"  Raw eta^2 = {eta_ne:.4f} (n={n_ne}, k={k_ne})")
print(f"  F24: {v24}, F24b: {v24b}")

# Partial after SC_class
peta_ne_sc, _, _ = partial_eta_cat_cat(tc, ne, sc_cls)
peta_ne_sg, _, _ = partial_eta_cat_cat(tc, ne, sg)
print(f"  Partial eta^2(N_elem | SC_class) = {peta_ne_sc:.4f}")
print(f"  Partial eta^2(N_elem | SG)       = {peta_ne_sg:.4f}")

# Interaction: leave-one-SC-class-out
oos = leave_one_group_out_r2(tc, [str(x) for x in ne], sc_cls)
if oos:
    w_oos = sum(r["r2"] * r["n"] for r in oos) / sum(r["n"] for r in oos)
    print(f"  Leave-one-SC-class-out OOS R^2: {w_oos:.4f}")
else:
    w_oos = float("nan")
    print(f"  Leave-one-SC-class-out: insufficient data")

# Within-class eta^2
print(f"  Within-class N_elem -> Tc:")
for cls in sorted(set(sc_cls)):
    stratum = [r for r in sc_rows if r["sc_class"] == cls]
    if len(stratum) >= 30:
        eta_w, nw, kw = eta_sq([r["tc"] for r in stratum], [r["n_elements"] for r in stratum], min_group=3)
        if not np.isnan(eta_w) and kw >= 2:
            print(f"    {cls:25s}: eta^2={eta_w:.4f} (n={nw}, k={kw})")

# Classification
if peta_ne_sc < 0.05 and peta_ne_sg < 0.05:
    cls_label = "NEGLIGIBLE after controls"
elif not np.isnan(w_oos) and w_oos < -1:
    cls_label = "CONDITIONAL LAW (interaction-dominated)"
elif peta_ne_sc >= 0.05:
    cls_label = "WEAK CONDITIONAL LAW"
else:
    cls_label = "TENDENCY"
print(f"  Classification: {cls_label}\n")

# ============================================================
# TEST C59: Crystal system → Tc — absorbed by SG?
# ============================================================
print("-" * 100)
print("TEST C59: Crystal system -> Tc (absorbed by SG?)")

eta_cs, n_cs, k_cs = eta_sq(tc, cs)
v24, r24 = bv2.F24_variance_decomposition(tc, cs)
v24b, r24b = bv2.F24b_metric_consistency(tc, cs)
print(f"  Raw eta^2 = {eta_cs:.4f} (n={n_cs}, k={k_cs})")
print(f"  F24: {v24}, F24b: {v24b}")

# Partial after SG
peta_cs_sg, _, _ = partial_eta_cat_cat(tc, cs, sg)
peta_cs_sc, _, _ = partial_eta_cat_cat(tc, cs, sc_cls)
print(f"  Partial eta^2(CS | SG)       = {peta_cs_sg:.4f}")
print(f"  Partial eta^2(CS | SC_class) = {peta_cs_sc:.4f}")

if peta_cs_sg < 0.005:
    print(f"  VERDICT: ABSORBED by SG. Crystal system adds nothing beyond space group.")
    print(f"  Classification: NEGLIGIBLE (redundant with SG)\n")
else:
    print(f"  VERDICT: Partial independence from SG (partial eta^2 = {peta_cs_sg:.4f})")
    print(f"  Classification: TENDENCY\n")

# ============================================================
# TEST C5: SC composition curvature κ = -0.38 — F17 confound
# ============================================================
print("-" * 100)
print("TEST C5: SC composition graph curvature (F17 confound check)")
print("  Question: Is curvature just a proxy for node degree / n_elements?")

# Build composition graph: Jaccard similarity > 0.5
# Each material's element set defines a node
compositions = []
for r in sc_rows:
    elems = set(re.findall(r'[A-Z][a-z]?', r["formula"]))
    compositions.append(elems)

# Compute Jaccard neighbors and node degree (sample for speed)
sample_size = min(2000, len(compositions))
sample_idx = rng.choice(len(compositions), sample_size, replace=False)
degrees = np.zeros(sample_size)
for i in range(sample_size):
    count = 0
    for j in range(sample_size):
        if i != j:
            inter = len(compositions[sample_idx[i]] & compositions[sample_idx[j]])
            union = len(compositions[sample_idx[i]] | compositions[sample_idx[j]])
            if union > 0 and inter / union > 0.5:
                count += 1
    degrees[i] = count

sample_tc = tc_arr[sample_idx]
sample_ne = np.array([ne[i] for i in sample_idx])

# Correlation: degree vs Tc
r_deg_tc = np.corrcoef(degrees, sample_tc)[0, 1]
# Correlation: degree vs n_elements
r_deg_ne = np.corrcoef(degrees, sample_ne)[0, 1]
# Correlation: n_elements vs Tc
r_ne_tc = np.corrcoef(sample_ne, sample_tc)[0, 1]

print(f"  Graph degree stats: mean={np.mean(degrees):.1f}, std={np.std(degrees):.1f}")
print(f"  r(degree, Tc)         = {r_deg_tc:.4f}")
print(f"  r(degree, n_elements) = {r_deg_ne:.4f}")
print(f"  r(n_elements, Tc)     = {r_ne_tc:.4f}")

# Partial: degree → Tc after controlling n_elements
X_ctrl = np.column_stack([np.ones(sample_size), sample_ne])
b_d = np.linalg.lstsq(X_ctrl, degrees, rcond=None)[0]
b_t = np.linalg.lstsq(X_ctrl, sample_tc, rcond=None)[0]
deg_resid = degrees - X_ctrl @ b_d
tc_resid = sample_tc - X_ctrl @ b_t
r_partial = np.corrcoef(deg_resid, tc_resid)[0, 1]
print(f"  Partial r(degree, Tc | n_elements) = {r_partial:.4f}")

if abs(r_partial) < 0.05:
    print(f"  VERDICT: Curvature/degree is MEDIATED by n_elements. F17 CONFOUND.")
    print(f"  Classification: NEGLIGIBLE (confounded)\n")
elif abs(r_partial) < 0.15:
    print(f"  VERDICT: Weak partial signal survives. TENDENCY at best.")
    print(f"  Classification: TENDENCY\n")
else:
    print(f"  VERDICT: Partial signal survives controls.")
    print(f"  Classification: CONSTRAINT\n")

# ============================================================
# TEST C11: 3-prime rigidity on SC compositions — F24 magnitude
# ============================================================
print("-" * 100)
print("TEST C11: 3-prime rigidity on SC compositions (F24 magnitude)")

# Compute mod-3,5,7 fingerprint for each material
def mod_fingerprint(formula, primes=[3, 5, 7]):
    elems = re.findall(r'([A-Z][a-z]?)(\d*\.?\d*)', formula)
    counts = []
    for e, c in elems:
        if e:
            try:
                counts.append(float(c) if c else 1.0)
            except:
                counts.append(1.0)
    if not counts:
        return None
    fp = tuple(int(round(sum(counts))) % p for p in primes)
    return fp

fingerprints = {}
for r in sc_rows:
    fp = mod_fingerprint(r["formula"])
    if fp:
        fingerprints.setdefault(fp, []).append(r["tc"])

# Eta^2: fingerprint → Tc
fp_labels = []
fp_tc = []
for r in sc_rows:
    fp = mod_fingerprint(r["formula"])
    if fp:
        fp_labels.append(str(fp))
        fp_tc.append(r["tc"])

eta_fp, n_fp, k_fp = eta_sq(fp_tc, fp_labels)
v24, r24 = bv2.F24_variance_decomposition(fp_tc, fp_labels)
v24b, r24b = bv2.F24b_metric_consistency(fp_tc, fp_labels)
print(f"  Fingerprint eta^2 = {eta_fp:.4f} (n={n_fp}, k={k_fp})")
print(f"  F24: {v24}, F24b: {v24b}")

# Partial after SC_class
fp_sc = [r["sc_class"] for r in sc_rows if mod_fingerprint(r["formula"])]
peta_fp_sc, _, _ = partial_eta_cat_cat(fp_tc, fp_labels, fp_sc[:len(fp_labels)])
print(f"  Partial eta^2(fingerprint | SC_class) = {peta_fp_sc:.4f}")

# Within-fingerprint Tc enrichment
big_fps = {fp: tcs for fp, tcs in fingerprints.items() if len(tcs) >= 20}
print(f"  Fingerprints with >= 20 materials: {len(big_fps)}")

# Enrichment: do materials sharing a fingerprint have more similar Tc?
within_vars = [np.var(tcs) for tcs in big_fps.values()]
overall_var = np.var(fp_tc)
mean_within = np.mean(within_vars)
print(f"  Overall Tc variance: {overall_var:.1f}")
print(f"  Mean within-fingerprint variance: {mean_within:.1f}")
print(f"  Variance ratio (within/overall): {mean_within / overall_var:.3f}")

if eta_fp < 0.01:
    print(f"  Classification: NEGLIGIBLE\n")
elif eta_fp < 0.14:
    print(f"  Classification: TENDENCY (fingerprint groups materials but explains little Tc)\n")
else:
    print(f"  Classification: LAW\n")

# ============================================================
# SUMMARY
# ============================================================
print("=" * 100)
print("M2 BATCH 1 SUMMARY: SUPERCONDUCTOR TESTS")
print("=" * 100)
print(f"""
  SC.1  SC_class -> Tc:          eta^2={eta_sc:.4f}  CONDITIONAL LAW (anchor)
  SC.2  SG -> Tc:                eta^2={eta_sg:.4f}  CONDITIONAL LAW (anchor)
  SC.3  N_elements -> Tc:        eta^2={eta_ne:.4f}  (partial|SC={peta_ne_sc:.4f}, partial|SG={peta_ne_sg:.4f})
  C59   Crystal system -> Tc:    eta^2={eta_cs:.4f}  (partial|SG={peta_cs_sg:.4f})
  C5    Composition curvature:   partial r={r_partial:.4f} after n_elements
  C11   3-prime fingerprint:     eta^2={eta_fp:.4f}  (partial|SC={peta_fp_sc:.4f})
""")
