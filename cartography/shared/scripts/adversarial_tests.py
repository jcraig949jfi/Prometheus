#!/usr/bin/env python3
"""
Adversarial Tests — Council Round 2
5 tests designed to break the battery and flagship results.

Test 1: Subsample scaling curve (resolves core ambiguity)
Test 2: Target leakage test (validates coarsening claim)
Test 3: Synthetic ground truth injection (validates classification)
Test 4: Synthetic junk calibration (overfitting check)
Test 5: Benford distributional control (numerology trap)
"""
import sys, os, json, csv, io, re
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
    if len(valid) < 2: return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)

# Load SC data once
print("Loading superconductor data...")
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
            r = {"tc": tc, "sg": sg, "sc_class": sc_class}
            for key, col in [("vol", "cell_volume_2"), ("density", "density_2"),
                             ("nsites", "nsites_2"), ("fe", "formation_energy_per_atom_2")]:
                try: r[key] = float(row.get(col, ""))
                except: r[key] = None
            sc_rows.append(r)
    except:
        pass
print(f"  {len(sc_rows)} superconductors\n")

tc_all = np.array([r["tc"] for r in sc_rows])
sg_all = [r["sg"] for r in sc_rows]
sc_cls = [r["sc_class"] for r in sc_rows]
n = len(tc_all)


# ============================================================
# TEST 1: SUBSAMPLE SCALING CURVE
# ============================================================
print("=" * 100)
print("TEST 1: SUBSAMPLE SCALING — Does transfer improve with n per group?")
print("If yes → noise-limited. If no → genuine non-stationarity.")
print("=" * 100)

# For each subsample size, randomly thin groups to max n per cell
sample_sizes = [5, 10, 20, 50, 100, 200, 500]

print(f"\n  {'n/group':>8s} | {'eta2':>8s} | {'F25b main R2':>12s} | {'F25b inter R2':>13s} | {'F25b verdict':>15s}")
print("  " + "-" * 70)

for max_n in sample_sizes:
    # Subsample: for each (SG, SC_class) cell, take at most max_n
    cells = defaultdict(list)
    for i, r in enumerate(sc_rows):
        cells[(r["sg"], r["sc_class"])].append(i)

    sampled_idx = []
    for cell, indices in cells.items():
        if len(indices) <= max_n:
            sampled_idx.extend(indices)
        else:
            sampled_idx.extend(rng.choice(indices, max_n, replace=False).tolist())

    sub_tc = [sc_rows[i]["tc"] for i in sampled_idx]
    sub_sg = [sc_rows[i]["sg"] for i in sampled_idx]
    sub_sc = [sc_rows[i]["sc_class"] for i in sampled_idx]

    eta, _, _ = eta_sq(sub_tc, sub_sg)
    v25b, r25b = bv2.F25b_model_transportability(sub_tc, sub_sg, sub_sc)
    main_r2 = r25b.get("weighted_r2_main", float("nan"))
    inter_r2 = r25b.get("weighted_r2_interaction", float("nan"))
    print(f"  {max_n:8d} | {eta:8.4f} | {main_r2:12.4f} | {inter_r2:13.4f} | {v25b:>15s}")

print(f"\n  If main R2 improves monotonically with n → NOISE-LIMITED")
print(f"  If main R2 stays negative regardless of n → GENUINE NON-STATIONARITY")


# ============================================================
# TEST 2: TARGET LEAKAGE — Does coarsening work without Tc?
# ============================================================
print("\n" + "=" * 100)
print("TEST 2: TARGET LEAKAGE — Does structure-only grouping transfer?")
print("Groupings using ONLY structural features, no Tc.")
print("=" * 100)

# Structural-only groupings (no Tc information)
complete = [r for r in sc_rows if all(r.get(k) is not None for k in ["vol", "density", "nsites"])]
if len(complete) > 100:
    # k-means on structural features (NOT Tc)
    from scipy.cluster.vq import kmeans2
    features = np.column_stack([
        np.log([r["vol"] + 1 for r in complete]),
        np.log([r["density"] + 1 for r in complete]),
        [r["nsites"] for r in complete],
    ])
    # Normalize
    features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-10)

    tc_comp = [r["tc"] for r in complete]
    sc_comp = [r["sc_class"] for r in complete]

    print(f"\n  {'Grouping':30s} | {'k':>4s} | {'eta2':>8s} | {'F25b':>15s} | {'main R2':>8s}")
    print("  " + "-" * 75)

    for k in [3, 5, 10, 20]:
        try:
            centroids, labels = kmeans2(features, k, minit="points", seed=42)
            str_labels = [str(l) for l in labels]
            eta, _, _ = eta_sq(tc_comp, str_labels)
            v25b, r25b = bv2.F25b_model_transportability(tc_comp, str_labels, sc_comp)
            main_r2 = r25b.get("weighted_r2_main", float("nan"))
            print(f"  {'struct k-means':30s} | {k:4d} | {eta:8.4f} | {v25b:>15s} | {main_r2:8.4f}")
        except:
            print(f"  {'struct k-means':30s} | {k:4d} | ERROR")

    # Comparison: k-means on Tc (the tautological control)
    tc_arr_comp = np.array(tc_comp)
    for k in [5, 10]:
        centroids, labels = kmeans2(tc_arr_comp, k, minit="points", seed=42)
        str_labels = [str(l) for l in labels]
        eta, _, _ = eta_sq(tc_comp, str_labels)
        v25b, r25b = bv2.F25b_model_transportability(tc_comp, str_labels, sc_comp)
        main_r2 = r25b.get("weighted_r2_main", float("nan"))
        print(f"  {'Tc k-means (tautological)':30s} | {k:4d} | {eta:8.4f} | {v25b:>15s} | {main_r2:8.4f}")

    # SG for comparison
    eta_sg, _, _ = eta_sq(tc_comp, [r["sg"] for r in complete])
    v25b_sg, r25b_sg = bv2.F25b_model_transportability(tc_comp, [r["sg"] for r in complete], sc_comp)
    print(f"  {'SG (reference)':30s} | {'77':>4s} | {eta_sg:8.4f} | {v25b_sg:>15s} | {r25b_sg.get('weighted_r2_main', 0):8.4f}")


# ============================================================
# TEST 3: SYNTHETIC GROUND TRUTH INJECTION
# ============================================================
print("\n" + "=" * 100)
print("TEST 3: SYNTHETIC INJECTION — Can battery recover known structure?")
print("Inject Tc' = Tc + alpha*f(SG) + beta*interaction(SG,class)")
print("=" * 100)

# Get SG group means and class means
sg_means = defaultdict(list)
for r in sc_rows:
    sg_means[r["sg"]].append(r["tc"])
sg_means = {k: np.mean(v) for k, v in sg_means.items() if len(v) >= 5}
grand_mean = np.mean(tc_all)

# Create f(SG) = centered SG mean
def f_sg(sg):
    return sg_means.get(sg, grand_mean) - grand_mean

# Create interaction: SG×class cell mean deviation from additive
cell_means = defaultdict(list)
for r in sc_rows:
    cell_means[(r["sg"], r["sc_class"])].append(r["tc"])
cls_means = defaultdict(list)
for r in sc_rows:
    cls_means[r["sc_class"]].append(r["tc"])
cls_means = {k: np.mean(v) for k, v in cls_means.items()}

def interaction(sg, cls):
    cell = cell_means.get((sg, cls), [grand_mean])
    additive = sg_means.get(sg, grand_mean) + cls_means.get(cls, grand_mean) - grand_mean
    return np.mean(cell) - additive

configs = [
    ("alpha=0, beta=0 (pure noise)", 0, 0),
    ("alpha=10, beta=0 (universal SG)", 10, 0),
    ("alpha=10, beta=5 (conditional)", 10, 5),
    ("alpha=0, beta=10 (pure interaction)", 0, 10),
]

noise_std = np.std(tc_all) * 0.5

print(f"\n  {'Config':40s} | {'eta2':>8s} | {'F25b':>15s} | {'main R2':>8s} | {'Expected'}")
print("  " + "-" * 100)

for config_name, alpha, beta in configs:
    y_synth = np.array([
        alpha * f_sg(r["sg"]) + beta * interaction(r["sg"], r["sc_class"]) + rng.normal(0, noise_std)
        for r in sc_rows
    ])
    eta, _, _ = eta_sq(y_synth, sg_all)
    v25b, r25b = bv2.F25b_model_transportability(y_synth.tolist(), sg_all, sc_cls)
    main_r2 = r25b.get("weighted_r2_main", float("nan"))

    if alpha > 0 and beta == 0:
        expected = "UNIVERSAL"
    elif beta > 0:
        expected = "CONDITIONAL"
    else:
        expected = "WEAK_NOISY"

    match = "OK" if v25b == expected else f"MISMATCH (got {v25b})"
    print(f"  {config_name:40s} | {eta:8.4f} | {v25b:>15s} | {main_r2:8.4f} | {expected:15s} {match}")


# ============================================================
# TEST 4: SYNTHETIC JUNK CALIBRATION
# ============================================================
print("\n" + "=" * 100)
print("TEST 4: SYNTHETIC JUNK — Does battery find structure in pure noise?")
print("=" * 100)

n_junk = 4000
n_groups = 50

junk_values = rng.normal(0, 1, n_junk)
junk_labels = [f"NonAbelianTrace_{i}" for i in rng.choice(n_groups, n_junk)]
junk_context = [f"AdelicVolume_{i}" for i in rng.choice(8, n_junk)]

eta_junk, n_j, k_j = eta_sq(junk_values, junk_labels)
v24_junk, r24_junk = bv2.F24_variance_decomposition(junk_values.tolist(), junk_labels)
v25b_junk, r25b_junk = bv2.F25b_model_transportability(junk_values.tolist(), junk_labels, junk_context)

print(f"\n  Junk dataset: {n_junk} samples, {n_groups} groups, pure Gaussian noise")
print(f"  eta² = {eta_junk:.4f}")
print(f"  F24: {v24_junk}")
print(f"  F25b: {v25b_junk} (main R²={r25b_junk.get('weighted_r2_main', 0):.4f})")

# Run 20 trials
junk_etas = []
junk_tier2 = 0
for trial in range(20):
    jv = rng.normal(0, 1, n_junk)
    jl = [f"group_{i}" for i in rng.choice(n_groups, n_junk)]
    eta_t, _, _ = eta_sq(jv, jl)
    junk_etas.append(eta_t)
    if eta_t >= 0.011:  # Tier 2 threshold from report
        junk_tier2 += 1

print(f"\n  20 trials: mean eta²={np.mean(junk_etas):.4f}, max={np.max(junk_etas):.4f}")
print(f"  Trials reaching Tier 2 (eta²≥0.011): {junk_tier2}/20")

if junk_tier2 == 0:
    print(f"  VERDICT: Battery correctly rejects junk data. PASS.")
else:
    print(f"  VERDICT: {junk_tier2}/20 junk datasets reach Tier 2. Battery thresholds too permissive. FAIL.")


# ============================================================
# TEST 5: BENFORD DISTRIBUTIONAL CONTROL
# ============================================================
print("\n" + "=" * 100)
print("TEST 5: BENFORD CONTROL — Is cross-domain overlap just shared distributions?")
print("=" * 100)

# Generate two unrelated datasets with similar integer distributions
# Set A: "city populations" (log-normal integers)
set_a = np.round(np.exp(rng.normal(10, 2, 5000))).astype(int)
set_a = set(int(x) for x in set_a if x > 0)

# Set B: "prime factors of random integers"
set_b = set()
for _ in range(5000):
    n = rng.integers(2, 100000)
    d = 2
    while d * d <= n:
        if n % d == 0:
            set_b.add(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        set_b.add(int(n))

overlap_fake = len(set_a & set_b)
union_fake = len(set_a | set_b)
print(f"\n  Set A ('populations'): {len(set_a)} unique integers")
print(f"  Set B ('prime factors'): {len(set_b)} unique integers")
print(f"  Overlap: {overlap_fake} ({overlap_fake/min(len(set_a), len(set_b))*100:.1f}%)")

# Compare to real cross-domain overlaps
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
knot_dets = set(k["determinant"] for k in knots if k.get("determinant") and k["determinant"] > 1)
try:
    sg_data = json.load(open(DATA / "spacegroups/data/space_groups.json", encoding="utf-8"))
    sg_numbers = set(s.get("number", 0) for s in sg_data if s.get("number"))
except:
    sg_numbers = set(range(1, 231))

overlap_real = len(knot_dets & sg_numbers)
print(f"\n  Knot dets: {len(knot_dets)} unique")
print(f"  SG numbers: {len(sg_numbers)} unique")
print(f"  Real overlap: {overlap_real} ({overlap_real/min(len(knot_dets), len(sg_numbers))*100:.1f}%)")

# Expected overlap under uniform random: hypergeometric
max_val = max(max(knot_dets), max(sg_numbers))
expected_overlap = len(knot_dets) * len(sg_numbers) / max_val
print(f"  Expected overlap (uniform): {expected_overlap:.1f}")
print(f"  Enrichment: {overlap_real / expected_overlap:.2f}x" if expected_overlap > 0 else "")

if overlap_real / expected_overlap < 2.0 if expected_overlap > 0 else True:
    print(f"\n  VERDICT: Cross-domain overlap (#56) is NOT enriched above chance.")
    print(f"  It's a Benford/distribution artifact. KILL Finding #56.")
else:
    print(f"\n  VERDICT: Overlap exceeds distribution expectation. Possibly real.")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("ADVERSARIAL TEST SUMMARY")
print("=" * 100)
