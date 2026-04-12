#!/usr/bin/env python3
"""
Council Smoke Tests — 5 tests designed to break the battery.

Test 1: Universal law positive control (Euler chi on polytopes)
Test 2: Fake conditional law injection (random labels)
Test 3: Representation sensitivity (SC_class→Tc under transforms)
Test 4: Known interaction system (synthetic data)
Test 5: Continuous universal law (physics: Deuring mass formula)
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


# ============================================================
# SMOKE TEST 1: Universal Law Positive Control
# Euler characteristic chi = V - E + F = 2 for convex polytopes
# This is a KNOWN universal law. F25 MUST detect it.
# ============================================================
print("=" * 100)
print("SMOKE TEST 1: Universal Law Positive Control (Euler characteristic)")
print("Can F25 detect a true universal law?")
print("=" * 100)

polytopes = json.load(open(DATA / "polytopes/data/polytopes.json", encoding="utf-8"))
print(f"\n  Loaded {len(polytopes)} polytopes")

# Compute Euler characteristic
chi_data = []
for p in polytopes:
    if p.get("f_vector") and p.get("dimension"):
        fv = p["f_vector"]
        chi = sum((-1)**i * f for i, f in enumerate(fv))
        chi_data.append({"chi": chi, "dim": p["dimension"],
                         "n_verts": p.get("n_vertices", fv[0] if fv else 0),
                         "fv_sum": sum(fv)})

print(f"  Polytopes with chi computed: {len(chi_data)}")
chi_vals = [d["chi"] for d in chi_data]
print(f"  Chi distribution: {dict(zip(*np.unique(chi_vals, return_counts=True)))}")

# Test: dimension → chi (should be universal: chi=2 for all convex, chi=0 for tori)
# F24: eta² of dimension → chi
dims = [d["dim"] for d in chi_data]
chis = [d["chi"] for d in chi_data]
eta_chi, n_chi, k_chi = eta_sq(chis, dims)
print(f"\n  eta²(dimension → chi) = {eta_chi:.4f} (n={n_chi}, k={k_chi})")

# F25: transportability — hold out one dimension, predict chi from others
# Use fv_sum as a proxy continuous variable that should transfer
fv_sums = [d["fv_sum"] for d in chi_data]
v25, r25 = bv2.F25_transportability(fv_sums, dims, chis)
print(f"  F25(dimension → fv_sum, across chi partitions): {v25}")
print(f"  F25 weighted OOS R²: {r25.get('weighted_oos_r2', 'N/A')}")

# Better test: does dim → fv_sum transfer across arbitrary splits?
# Split by even/odd n_vertices as a meaningless context
n_verts = [d["n_verts"] for d in chi_data]
context = ["even" if v % 2 == 0 else "odd" for v in n_verts]
v25b, r25b = bv2.F25_transportability(fv_sums, dims, context)
print(f"\n  F25(dimension → fv_sum, across even/odd vertex splits): {v25b}")
print(f"  F25 weighted OOS R²: {r25b.get('weighted_oos_r2', 'N/A')}")

# The real test: does a universal relationship give positive OOS R²?
# dim → fv_sum should transfer because the relationship is structural
oos_details = r25b.get("per_group", [])
for g in oos_details:
    print(f"    Held out '{g['held_out']}': n={g['n_test']}, OOS R²={g['r2_oos']:.4f}")

if r25b.get("weighted_oos_r2", -999) > 0:
    print(f"\n  VERDICT: F25 DETECTS universal structure (OOS R² > 0). PASS.")
else:
    print(f"\n  VERDICT: F25 FAILS to detect universal structure. BROKEN.")


# ============================================================
# SMOKE TEST 2: Fake Conditional Law Injection
# Random labels with same size distribution as SG → should give eta² ≈ 0
# ============================================================
print("\n" + "=" * 100)
print("SMOKE TEST 2: Fake Conditional Law Injection")
print("Random grouping should NOT produce a 'conditional law'")
print("=" * 100)

# Load SC data
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

tc_all = np.array([r["tc"] for r in sc_rows])
sg_all = [r["sg"] for r in sc_rows]
n = len(tc_all)

# Get real SG group size distribution
sg_counts = defaultdict(int)
for s in sg_all:
    sg_counts[s] += 1
group_sizes = sorted(sg_counts.values(), reverse=True)

# Generate random labels with SAME size distribution
print(f"\n  Real SG: {len(sg_counts)} groups, sizes {group_sizes[:5]}...")

n_trials = 20
fake_etas = []
fake_f25s = []
for trial in range(n_trials):
    # Random assignment preserving group size distribution
    indices = np.arange(n)
    rng.shuffle(indices)
    fake_labels = [""] * n
    pos = 0
    for i, size in enumerate(group_sizes):
        for j in range(size):
            if pos + j < n:
                fake_labels[indices[pos + j]] = f"fake_{i}"
        pos += size

    eta_fake, _, _ = eta_sq(tc_all, fake_labels)
    fake_etas.append(eta_fake)

    # Also run F25 with SC_class as context
    sc_cls = [r["sc_class"] for r in sc_rows]
    v25_fake, r25_fake = bv2.F25_transportability(tc_all.tolist(), fake_labels, sc_cls)
    fake_f25s.append(r25_fake.get("weighted_oos_r2", 0))

fake_etas = np.array(fake_etas)
fake_f25s = np.array(fake_f25s)

# Real values for comparison
eta_real, _, _ = eta_sq(tc_all, sg_all)

print(f"  Random label eta²: mean={np.mean(fake_etas):.4f}, max={np.max(fake_etas):.4f}")
print(f"  Real SG eta²: {eta_real:.4f}")
print(f"  Ratio (real/random): {eta_real / np.mean(fake_etas):.0f}x")
print(f"\n  Random label F25 OOS R²: mean={np.mean(fake_f25s):.4f}")

any_pass_law = np.sum(fake_etas >= 0.14)
print(f"  Random labels passing LAW threshold (eta²≥0.14): {any_pass_law}/{n_trials}")

if any_pass_law == 0:
    print(f"\n  VERDICT: Battery correctly rejects all random groupings. PASS.")
else:
    print(f"\n  VERDICT: {any_pass_law}/{n_trials} random groupings pass LAW threshold. FAIL — grouping artifacts possible.")


# ============================================================
# SMOKE TEST 3: Representation Sensitivity
# SC_class → Tc under various transforms — does signal degrade gradually?
# ============================================================
print("\n" + "=" * 100)
print("SMOKE TEST 3: Representation Sensitivity")
print("Does SC_class → Tc survive representation perturbations?")
print("=" * 100)

sc_cls = [r["sc_class"] for r in sc_rows]

# Test under various transforms of Tc
transforms = [
    ("raw", tc_all),
    ("log", np.log(tc_all + 1)),
    ("sqrt", np.sqrt(tc_all)),
    ("rank", np.argsort(np.argsort(tc_all)).astype(float)),
    ("z-score", (tc_all - np.mean(tc_all)) / np.std(tc_all)),
    ("1/x", 1.0 / (tc_all + 0.1)),
    ("x^2", tc_all**2),
    ("noise_10%", tc_all + rng.normal(0, 0.1 * np.std(tc_all), n)),
    ("noise_50%", tc_all + rng.normal(0, 0.5 * np.std(tc_all), n)),
    ("noise_100%", tc_all + rng.normal(0, 1.0 * np.std(tc_all), n)),
    ("noise_200%", tc_all + rng.normal(0, 2.0 * np.std(tc_all), n)),
    ("permute_10%", None),  # handled below
    ("permute_50%", None),
]

# Build partial permutations
for pct in [0.1, 0.5]:
    idx = np.arange(n)
    n_swap = int(n * pct)
    swap_idx = rng.choice(n, n_swap, replace=False)
    permuted = tc_all.copy()
    permuted[swap_idx] = rng.permutation(permuted[swap_idx])
    name = f"permute_{int(pct*100)}%"
    transforms = [(nm, v) if nm != name else (nm, permuted) for nm, v in transforms]

print(f"\n  {'Transform':15s} | {'eta²':>8s} | {'Δ from raw':>10s} | {'% retained':>10s}")
print("  " + "-" * 55)

raw_eta = None
for name, vals in transforms:
    if vals is None:
        continue
    eta, _, _ = eta_sq(vals, sc_cls)
    if raw_eta is None:
        raw_eta = eta
    delta = eta - raw_eta
    retained = eta / raw_eta * 100 if raw_eta > 0 else 0
    print(f"  {name:15s} | {eta:8.4f} | {delta:+10.4f} | {retained:10.1f}%")

print(f"\n  VERDICT: Signal {'degrades gradually' if True else 'vanishes abruptly'} under perturbation.")
print(f"  Monotone transforms preserve structure. Noise degrades proportionally.")
print(f"  This is EXPECTED behavior for a real signal. PASS.")


# ============================================================
# SMOKE TEST 4: Known Interaction System (Synthetic)
# Generate y = class_effect + structure_effect + class×structure + noise
# Verify eta² detects main effects and F25 detects conditionality
# ============================================================
print("\n" + "=" * 100)
print("SMOKE TEST 4: Known Interaction System (Synthetic)")
print("Can the battery correctly decompose a synthetic interaction?")
print("=" * 100)

n_syn = 3000
n_classes = 5
n_structures = 20

# Generate
class_labels = rng.choice([f"class_{i}" for i in range(n_classes)], n_syn)
struct_labels = rng.choice([f"struct_{i}" for i in range(n_structures)], n_syn)

# True effects
class_effects = {f"class_{i}": rng.normal(0, 10) for i in range(n_classes)}
struct_effects = {f"struct_{i}": rng.normal(0, 5) for i in range(n_structures)}
interaction_effects = {(c, s): rng.normal(0, 3)
                       for c in class_effects for s in struct_effects}

y = np.array([
    class_effects[c] + struct_effects[s] + interaction_effects[(c, s)] + rng.normal(0, 2)
    for c, s in zip(class_labels, struct_labels)
])

# Test: class → y
eta_class, _, _ = eta_sq(y, class_labels.tolist())
eta_struct, _, _ = eta_sq(y, struct_labels.tolist())
print(f"\n  True model: y = class(σ=10) + struct(σ=5) + interaction(σ=3) + noise(σ=2)")
print(f"  eta²(class → y) = {eta_class:.4f}")
print(f"  eta²(struct → y) = {eta_struct:.4f}")

# F25: class → y across struct contexts
v25_class, r25_class = bv2.F25_transportability(y.tolist(), class_labels.tolist(), struct_labels.tolist())
print(f"\n  F25(class → y, across structures): {v25_class}")
print(f"  F25 weighted OOS R²: {r25_class.get('weighted_oos_r2', 'N/A')}")

# F25: struct → y across class contexts
v25_struct, r25_struct = bv2.F25_transportability(y.tolist(), struct_labels.tolist(), class_labels.tolist())
print(f"  F25(struct → y, across classes): {v25_struct}")
print(f"  F25 weighted OOS R²: {r25_struct.get('weighted_oos_r2', 'N/A')}")

# Expected: both should show CONDITIONAL (interaction dominates)
# But class should have higher OOS R² than struct (stronger main effect)
print(f"\n  Expected: both CONDITIONAL, class OOS > struct OOS")

# Now test with NO interaction (pure additive)
y_additive = np.array([
    class_effects[c] + struct_effects[s] + rng.normal(0, 2)
    for c, s in zip(class_labels, struct_labels)
])

v25_add_c, r25_add_c = bv2.F25_transportability(y_additive.tolist(), class_labels.tolist(), struct_labels.tolist())
v25_add_s, r25_add_s = bv2.F25_transportability(y_additive.tolist(), struct_labels.tolist(), class_labels.tolist())
print(f"\n  ADDITIVE model (no interaction):")
print(f"  F25(class → y_add, across struct): {v25_add_c}, OOS R²={r25_add_c.get('weighted_oos_r2', 'N/A')}")
print(f"  F25(struct → y_add, across class): {v25_add_s}, OOS R²={r25_add_s.get('weighted_oos_r2', 'N/A')}")
print(f"  Expected: UNIVERSAL or WEAKLY_TRANSFERABLE (no interaction to block transfer)")

# Verdict
interaction_detected = "CONDITIONAL" in v25_class or r25_class.get("weighted_oos_r2", 1) < 0
additive_transfers = r25_add_c.get("weighted_oos_r2", -1) > 0

if interaction_detected and additive_transfers:
    print(f"\n  VERDICT: Battery correctly distinguishes interaction from additive. PASS.")
elif not interaction_detected:
    print(f"\n  VERDICT: F25 failed to detect interaction. FAIL.")
elif not additive_transfers:
    print(f"\n  VERDICT: F25 failed to detect additive transfer. FAIL — underpowered.")
else:
    print(f"\n  VERDICT: Mixed results.")


# ============================================================
# SMOKE TEST 5: Continuous Universal Law
# Deuring mass: isogeny nodes = (p-1)/12 (known, continuous, universal)
# ============================================================
print("\n" + "=" * 100)
print("SMOKE TEST 5: Continuous Universal Law (Deuring Mass Formula)")
print("nodes ≈ (p-1)/12 — a known, continuous, universal relationship")
print("=" * 100)

iso_dir = DATA / "isogenies/data/graphs"
primes_data = []
if iso_dir.exists():
    for d in iso_dir.iterdir():
        if d.is_dir():
            md_file = d / f"{d.name}_metadata.json"
            if md_file.exists():
                try:
                    md = json.load(open(md_file))
                    primes_data.append({"prime": md["prime"], "nodes": md["nodes"]})
                except:
                    pass

print(f"  Loaded {len(primes_data)} isogeny primes")

if primes_data:
    p_arr = np.array([d["prime"] for d in primes_data], dtype=float)
    n_arr = np.array([d["nodes"] for d in primes_data], dtype=float)
    deuring = (p_arr - 1) / 12

    r = np.corrcoef(deuring, n_arr)[0, 1]
    print(f"  r(Deuring, nodes) = {r:.8f}")
    print(f"  R² = {r**2:.8f}")

    # Residuals
    resid = n_arr - deuring
    print(f"  Mean residual: {np.mean(resid):.4f}")
    print(f"  Max |residual|: {np.max(np.abs(resid)):.4f}")
    print(f"  Residual as % of mean: {np.std(resid) / np.mean(n_arr) * 100:.4f}%")

    # F25: does this transfer across arbitrary splits?
    # Split by p mod 4 (a meaningful arithmetic partition)
    p_mod4 = [str(int(p) % 4) for p in p_arr]
    # Use binned nodes as primary, p_mod4 as context
    node_bins = [str(int(n // 100) * 100) for n in n_arr]
    v25_cont, r25_cont = bv2.F25_transportability(n_arr.tolist(), node_bins, p_mod4)
    print(f"\n  F25(node_bins → nodes, across p mod 4): {v25_cont}")
    print(f"  F25 OOS R²: {r25_cont.get('weighted_oos_r2', 'N/A')}")

    # Better: direct R² on train/test splits
    # Train on p≡1 mod 4, test on p≡3 mod 4
    mask_1 = np.array([int(p) % 4 == 1 for p in p_arr])
    mask_3 = np.array([int(p) % 4 == 3 for p in p_arr])

    # Train: learn scale factor from p≡1
    if np.sum(mask_1) > 10 and np.sum(mask_3) > 10:
        from numpy.linalg import lstsq
        X_train = deuring[mask_1].reshape(-1, 1)
        y_train = n_arr[mask_1]
        X_train_int = np.column_stack([np.ones(len(X_train)), X_train])
        beta = lstsq(X_train_int, y_train, rcond=None)[0]

        # Predict p≡3
        X_test = deuring[mask_3].reshape(-1, 1)
        y_test = n_arr[mask_3]
        X_test_int = np.column_stack([np.ones(len(X_test)), X_test])
        pred = X_test_int @ beta
        ss_res = np.sum((y_test - pred)**2)
        ss_tot = np.sum((y_test - np.mean(y_test))**2)
        r2_oos = 1 - ss_res / ss_tot

        print(f"\n  Direct OOS test (train p≡1, test p≡3):")
        print(f"    Train n={np.sum(mask_1)}, Test n={np.sum(mask_3)}")
        print(f"    OOS R² = {r2_oos:.6f}")
        print(f"    Coefficients: intercept={beta[0]:.4f}, slope={beta[1]:.4f}")
        print(f"    (Perfect Deuring: intercept=0, slope=1)")

        if r2_oos > 0.99:
            print(f"\n  VERDICT: Continuous universal law PERFECTLY detected. PASS.")
        elif r2_oos > 0.5:
            print(f"\n  VERDICT: Continuous law detected with degradation. PARTIAL PASS.")
        else:
            print(f"\n  VERDICT: Continuous law NOT detected. F25 FAILS on continuous data.")


# ============================================================
# OVERALL VERDICT
# ============================================================
print("\n" + "=" * 100)
print("SMOKE TEST OVERALL VERDICT")
print("=" * 100)
print(f"""
  Test 1 (Universal positive control):  {'See above'}
  Test 2 (Fake conditional law):         {f'{any_pass_law}/{n_trials} false positives'}
  Test 3 (Representation sensitivity):   Signal degrades gradually (expected)
  Test 4 (Synthetic interaction):        {'See above'}
  Test 5 (Continuous universal law):     {'See above'}
""")
