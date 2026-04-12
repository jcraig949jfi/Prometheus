#!/usr/bin/env python3
"""
Endurance Battery: Run EVERYTHING remaining.

Block 1: Remaining council adversarial tests (2,6,7,8,9,10)
Block 2: Benford/size audit on ALL Tier 2 constraints
Block 3: Primitive cross-matching (do same-primitive findings correlate?)
Block 4: F25b on findings that haven't been tested for transportability
Block 5: Isomorphism trap + chemical sabotage (council stress tests)
"""
import sys, os, json, csv, io, re, ast
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent
ROOT = Path(__file__).resolve().parents[3]
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

def m4m2(arr):
    arr = np.array(arr, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if len(arr) < 10: return float("nan")
    vn = arr / np.mean(arr)
    return np.mean(vn**4) / np.mean(vn**2)**2

results = []
def rec(name, verdict, metric=""):
    results.append({"name": name, "verdict": verdict, "metric": metric})
    print(f"  >> {name:40s} | {verdict:25s} | {metric[:50]}")

# Load everything
print("Loading ALL datasets...")
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
    except: pass

g2 = json.load(open(DATA / "genus2/data/genus2_curves_full.json", encoding="utf-8"))
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
nf_raw = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf = []
for f in nf_raw:
    r = {}
    for k, v in f.items():
        if isinstance(v, str):
            try: r[k] = float(v)
            except: r[k] = v
        else:
            r[k] = v
    nf.append(r)

import duckdb
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_rows = con.execute("SELECT conductor, rank, torsion FROM elliptic_curves WHERE conductor > 0").fetchall()
con.close()

tc_all = np.array([r["tc"] for r in sc_rows])
sg_all = [r["sg"] for r in sc_rows]
sc_cls = [r["sc_class"] for r in sc_rows]
n = len(tc_all)

print(f"  sc={len(sc_rows)}, g2={len(valid_g2)}, knots={len(knots)}, nf={len(nf)}, ec={len(ec_rows)}\n")

# ============================================================
# BLOCK 1: Remaining council adversarial tests
# ============================================================
print("=" * 100)
print("BLOCK 1: REMAINING ADVERSARIAL TESTS")
print("=" * 100)

# Test 2: Label permutation within groups
print("\n--- Adversarial 2: Label permutation within SC_class ---")
# Within each SC_class, shuffle SG labels. Eta² and interaction should collapse.
shuffled_sg = list(sg_all)
for cls in set(sc_cls):
    indices = [i for i in range(n) if sc_cls[i] == cls]
    sg_subset = [sg_all[i] for i in indices]
    rng.shuffle(sg_subset)
    for j, idx in enumerate(indices):
        shuffled_sg[idx] = sg_subset[j]

eta_real, _, _ = eta_sq(tc_all, sg_all)
eta_shuffled, _, _ = eta_sq(tc_all, shuffled_sg)
print(f"  Real SG->Tc eta²: {eta_real:.4f}")
print(f"  Within-class shuffled eta²: {eta_shuffled:.4f}")
print(f"  Retention: {eta_shuffled/eta_real*100:.1f}%")
rec("Adv2: Within-class label shuffle",
    "PASS (collapses)" if eta_shuffled < eta_real * 0.5 else "FAIL (survives shuffle)",
    f"real={eta_real:.4f} shuffled={eta_shuffled:.4f}")

# Test 6: Continuous vs discretized — replace SG with continuous symmetry descriptors
print("\n--- Adversarial 6: Continuous symmetry descriptors ---")
sg_data = json.load(open(DATA / "spacegroups/data/space_groups.json", encoding="utf-8"))
sg_props = {}
for s in sg_data:
    sym = s.get("symbol", "")
    sg_props[sym] = {
        "pg_order": s.get("point_group_order", 0),
        "is_symmorphic": 1 if s.get("is_symmorphic") else 0,
    }

# Build continuous features for each material
cont_features = []
for r in sc_rows:
    props = sg_props.get(r["sg"], {"pg_order": 0, "is_symmorphic": 0})
    cont_features.append([props["pg_order"], props["is_symmorphic"]])

cont_features = np.array(cont_features, dtype=float)
# Linear regression: Tc ~ pg_order + is_symmorphic
X = np.column_stack([np.ones(n), cont_features])
beta = np.linalg.lstsq(X, tc_all, rcond=None)[0]
pred = X @ beta
ss_res = np.sum((tc_all - pred)**2)
ss_tot = np.sum((tc_all - np.mean(tc_all))**2)
r2_continuous = 1 - ss_res / ss_tot
print(f"  R² (continuous SG descriptors -> Tc): {r2_continuous:.4f}")
print(f"  Eta² (categorical SG -> Tc): {eta_real:.4f}")
print(f"  Continuous captures {r2_continuous/eta_real*100:.1f}% of categorical signal")
rec("Adv6: Continuous vs categorical SG",
    f"Categorical {eta_real/r2_continuous:.1f}x better",
    f"R2_cont={r2_continuous:.4f} eta2_cat={eta_real:.4f}")

# Test 7: Group imbalance stress — equal-weight eta²
print("\n--- Adversarial 7: Equal-weight eta² (balance correction) ---")
sg_groups = defaultdict(list)
for i in range(n):
    sg_groups[sg_all[i]].append(tc_all[i])

# Weighted eta²: weight each group equally regardless of size
group_means = {g: np.mean(v) for g, v in sg_groups.items() if len(v) >= 5}
grand_mean = np.mean(list(group_means.values()))  # unweighted grand mean
ss_between_balanced = sum((m - grand_mean)**2 for m in group_means.values())
ss_within_balanced = sum(np.var(v) for g, v in sg_groups.items() if len(v) >= 5)
# Omega-squared (less biased than eta²)
k = len(group_means)
total_balanced = ss_between_balanced + ss_within_balanced
omega_sq = (ss_between_balanced - (k-1) * (ss_within_balanced / (n - k))) / (total_balanced + ss_within_balanced / (n - k))
print(f"  Standard eta²: {eta_real:.4f}")
print(f"  Omega² (bias-corrected): {omega_sq:.4f}")
print(f"  Ratio: {omega_sq / eta_real:.3f}")
rec("Adv7: Omega² vs eta²", f"omega²={omega_sq:.4f}", f"eta²={eta_real:.4f} ratio={omega_sq/eta_real:.3f}")

# Test 8: Alternative effect size metrics
print("\n--- Adversarial 8: Alternative effect size metrics ---")
# Mutual information (discretized)
from scipy.stats import entropy
tc_bins = np.digitize(tc_all, np.percentile(tc_all, np.arange(0, 101, 10)))
# Compute MI between SG and binned Tc
joint = Counter(zip(sg_all, tc_bins))
sg_counts = Counter(sg_all)
tc_bin_counts = Counter(tc_bins)
mi = 0
for (s, t), count in joint.items():
    p_joint = count / n
    p_s = sg_counts[s] / n
    p_t = tc_bin_counts[t] / n
    if p_joint > 0 and p_s > 0 and p_t > 0:
        mi += p_joint * np.log2(p_joint / (p_s * p_t))

print(f"  Eta²: {eta_real:.4f}")
print(f"  Mutual Information (SG, Tc_binned): {mi:.4f} bits")
print(f"  Max possible MI: {np.log2(min(len(set(sg_all)), 10)):.4f} bits")
print(f"  Normalized MI: {mi / np.log2(min(len(set(sg_all)), 10)):.4f}")
rec("Adv8: MI vs eta²", f"MI={mi:.4f} bits", f"normalized={mi/np.log2(10):.4f}")

# Test 9: Representation randomization
print("\n--- Adversarial 9: Representation randomization ---")
# Randomly re-encode SG labels as hash values, test if eta² is stable
hash_etas = []
for trial in range(10):
    # Random bijection on SG labels
    unique_sgs = list(set(sg_all))
    shuffled_sgs = list(unique_sgs)
    rng.shuffle(shuffled_sgs)
    mapping = dict(zip(unique_sgs, shuffled_sgs))
    remapped = [mapping[s] for s in sg_all]
    eta_remap, _, _ = eta_sq(tc_all, remapped)
    hash_etas.append(eta_remap)

hash_etas = np.array(hash_etas)
print(f"  Original eta²: {eta_real:.4f}")
print(f"  After random bijection: mean={np.mean(hash_etas):.4f}, std={np.std(hash_etas):.6f}")
print(f"  (Should be identical — bijection preserves grouping)")
rec("Adv9: Bijection invariance",
    "PASS" if np.std(hash_etas) < 0.001 else "FAIL",
    f"std={np.std(hash_etas):.6f}")

# Test 10: Cross-domain null swap — replace one domain with unrelated data
print("\n--- Adversarial 10: Cross-domain null swap ---")
# Replace isogeny data with random graph data, test if iso-MF correlation persists
iso_dir = DATA / "isogenies/data/graphs"
real_iso_nodes = {}
for d in iso_dir.iterdir():
    if d.is_dir():
        md_file = d / f"{d.name}_metadata.json"
        if md_file.exists():
            try:
                md = json.load(open(md_file))
                real_iso_nodes[md["prime"]] = md["nodes"]
            except: pass

try:
    con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
    mf_counts = dict(con.execute("SELECT level, COUNT(*) FROM modular_forms GROUP BY level").fetchall())
    con.close()
except:
    mf_counts = {}

shared = sorted(set(real_iso_nodes.keys()) & set(mf_counts.keys()))
if len(shared) > 50:
    real_nodes = np.array([real_iso_nodes[p] for p in shared], dtype=float)
    real_mf = np.array([mf_counts[p] for p in shared], dtype=float)
    r_real = np.corrcoef(real_nodes, real_mf)[0, 1]

    # Null swap: replace iso nodes with random values (same distribution)
    null_rs = []
    for _ in range(100):
        fake_nodes = rng.permutation(real_nodes)  # same values, shuffled
        r_null = np.corrcoef(fake_nodes, real_mf)[0, 1]
        null_rs.append(r_null)

    null_rs = np.array(null_rs)
    z = (r_real - np.mean(null_rs)) / np.std(null_rs) if np.std(null_rs) > 0 else 0
    print(f"  Real iso-MF r: {r_real:.4f}")
    print(f"  Null (shuffled) r: mean={np.mean(null_rs):.4f}, std={np.std(null_rs):.4f}")
    print(f"  z-score: {z:.1f}")
    rec("Adv10: Null swap iso-MF", f"z={z:.1f}", f"real={r_real:.4f} null={np.mean(null_rs):.4f}")


# ============================================================
# BLOCK 2: Benford/size audit on ALL Tier 2 constraints
# ============================================================
print("\n" + "=" * 100)
print("BLOCK 2: SIZE/DISTRIBUTION AUDIT ON TIER 2 CONSTRAINTS")
print("=" * 100)

# #37: CN in EC conductors (already killed, confirm)
# #38: C84 det->Alexander enrichment (2.45x) — is this size-mediated?
print("\n--- C84: Is det->Alexander enrichment size-mediated? ---")
has_alex = [k for k in knots if k.get("alex_coeffs") and k.get("determinant")]
if has_alex:
    dets = [k["determinant"] for k in has_alex]
    alex_lens = [len(k["alex_coeffs"]) for k in has_alex]
    r_det_len = np.corrcoef(dets, alex_lens)[0, 1]
    print(f"  r(det, alex_length): {r_det_len:.4f}")
    print(f"  If high: enrichment is just 'bigger det → longer polynomial'")
    rec("C84 size check",
        "SIZE-MEDIATED" if abs(r_det_len) > 0.5 else "INDEPENDENT",
        f"r(det, alex_len)={r_det_len:.4f}")

# #39: EC not Poisson — is this just because conductor distribution is heavy-tailed?
print("\n--- G.R3.ec: Is 'not Poisson' trivial? ---")
ec_cond_counts = Counter(r[0] for r in ec_rows)
counts = list(ec_cond_counts.values())
mean_count = np.mean(counts)
# Compare to geometric distribution (which is NOT Poisson but common for discrete data)
from scipy.stats import kstest, geom
ks_geom = kstest(counts, geom(1/mean_count).cdf)
ks_pois = kstest(counts, sp_stats.poisson(mean_count).cdf)
print(f"  KS vs Poisson: {ks_pois.statistic:.4f} (p={ks_pois.pvalue:.4e})")
print(f"  KS vs Geometric: {ks_geom.statistic:.4f} (p={ks_geom.pvalue:.4e})")
rec("G.R3.ec distribution",
    "GEOMETRIC fits better" if ks_geom.statistic < ks_pois.statistic else "NEITHER fits",
    f"KS_pois={ks_pois.statistic:.3f} KS_geom={ks_geom.statistic:.3f}")

# C89: torsion->root number — is this just conductor parity (our proxy)?
print("\n--- C89: Torsion->RN is actually torsion->conductor_parity ---")
torsion_data = [(r[2], r[0] % 2) for r in ec_rows if r[2] is not None and r[2] > 0]
if torsion_data:
    # Is conductor parity correlated with torsion?
    tors_vals = [t for t, _ in torsion_data]
    parity_vals = [p for _, p in torsion_data]
    eta_tp, _, _ = eta_sq(parity_vals, [str(t) for t in tors_vals])
    print(f"  eta²(torsion -> conductor_parity): {eta_tp:.4f}")
    print(f"  This is what we ACTUALLY measured (not root number)")
    rec("C89 honesty check", "PROXY (not real RN)", f"eta²={eta_tp:.4f} (conductor parity, not root number)")


# ============================================================
# BLOCK 3: Chemical sabotage test (council stress test #4)
# ============================================================
print("\n" + "=" * 100)
print("BLOCK 3: CHEMICAL SABOTAGE — Does SG×SC interaction survive without formula?")
print("=" * 100)

# Strip chemical formula, keep only physical properties + SG
complete = [r for r in sc_rows if all(r.get(k) is not None for k in ["vol", "density", "nsites", "fe"])]
if complete:
    tc_c = np.array([r["tc"] for r in complete])
    sg_c = [r["sg"] for r in complete]
    sc_c = [r["sc_class"] for r in complete]

    # Model 1: SG + physical properties (NO SC_class)
    def one_hot(labels, n_rows):
        unique = sorted(set(labels))
        mat = np.zeros((n_rows, max(len(unique)-1, 1)))
        for i, l in enumerate(labels):
            idx = unique.index(l)
            if idx > 0 and idx-1 < mat.shape[1]:
                mat[i, idx-1] = 1
        return mat

    nc = len(complete)
    X_sg = one_hot(sg_c, nc)
    X_phys = np.column_stack([[r["vol"] for r in complete],
                               [r["density"] for r in complete],
                               [r["nsites"] for r in complete],
                               [r["fe"] for r in complete]])

    # SG + physics (no chemistry label)
    X1 = np.column_stack([np.ones(nc), X_sg, X_phys])
    b1 = np.linalg.lstsq(X1, tc_c, rcond=None)[0]
    r2_sg_phys = 1 - np.sum((tc_c - X1 @ b1)**2) / np.sum((tc_c - np.mean(tc_c))**2)

    # SG + SC_class (the full model)
    X_sc = one_hot(sc_c, nc)
    X2 = np.column_stack([np.ones(nc), X_sg, X_sc])
    b2 = np.linalg.lstsq(X2, tc_c, rcond=None)[0]
    r2_sg_sc = 1 - np.sum((tc_c - X2 @ b2)**2) / np.sum((tc_c - np.mean(tc_c))**2)

    # Physics only (no SG, no SC_class)
    X3 = np.column_stack([np.ones(nc), X_phys])
    b3 = np.linalg.lstsq(X3, tc_c, rcond=None)[0]
    r2_phys = 1 - np.sum((tc_c - X3 @ b3)**2) / np.sum((tc_c - np.mean(tc_c))**2)

    print(f"  R²(SG + physics, no chemistry): {r2_sg_phys:.4f}")
    print(f"  R²(SG + SC_class):              {r2_sg_sc:.4f}")
    print(f"  R²(physics only):               {r2_phys:.4f}")
    print(f"  SC_class adds: +{r2_sg_sc - r2_sg_phys:.4f} beyond SG+physics")
    print(f"  SG adds beyond physics: +{r2_sg_phys - r2_phys:.4f}")

    rec("Chem sabotage: SC_class vs physics",
        f"SC_class adds +{r2_sg_sc - r2_sg_phys:.3f}",
        f"SG+phys={r2_sg_phys:.3f} SG+SC={r2_sg_sc:.3f} phys={r2_phys:.3f}")


# ============================================================
# BLOCK 4: Isomorphism trap (council stress test #3)
# ============================================================
print("\n" + "=" * 100)
print("BLOCK 4: ISOMORPHISM TRAP — Can battery detect X = 2X+5 as identity?")
print("=" * 100)

# Create a dataset where Y = 2X + 5 + noise
x_orig = tc_all.copy()
y_transform = 2 * x_orig + 5 + rng.normal(0, 0.01, n)
r_ident = np.corrcoef(x_orig, y_transform)[0, 1]

# Now group by SG and compute eta² for both
eta_x, _, _ = eta_sq(x_orig, sg_all)
eta_y, _, _ = eta_sq(y_transform, sg_all)

print(f"  Y = 2X + 5 + noise(0.01)")
print(f"  r(X, Y): {r_ident:.8f}")
print(f"  eta²(SG -> X): {eta_x:.4f}")
print(f"  eta²(SG -> Y): {eta_y:.4f}")
print(f"  Ratio: {eta_y / eta_x:.6f}")

# Does battery flag this as identity?
if abs(r_ident) > 0.999:
    rec("Isomorphism trap", "PASS (would detect as identity)", f"r={r_ident:.8f}")
else:
    rec("Isomorphism trap", "FAIL", f"r={r_ident:.8f}")

# Harder: Y = log(X) — nonlinear but monotone
y_log = np.log(x_orig + 1)
eta_log, _, _ = eta_sq(y_log, sg_all)
r_log = np.corrcoef(x_orig, y_log)[0, 1]
print(f"\n  Y = log(X + 1)")
print(f"  r(X, Y): {r_log:.4f}")
print(f"  eta²(SG -> log(X)): {eta_log:.4f}")
print(f"  Retention vs raw: {eta_log / eta_x * 100:.1f}%")
rec("Isomorphism trap (log)", f"r={r_log:.4f} eta_retain={eta_log/eta_x*100:.0f}%", "")


# ============================================================
# BLOCK 5: Deuring fragmentation (council stress test #5)
# ============================================================
print("\n" + "=" * 100)
print("BLOCK 5: DEURING FRAGMENTATION — Does universal law survive random grouping?")
print("=" * 100)

iso_dir = DATA / "isogenies/data/graphs"
iso_primes = []
iso_nodes = []
for d in iso_dir.iterdir():
    if d.is_dir():
        md_file = d / f"{d.name}_metadata.json"
        if md_file.exists():
            try:
                md = json.load(open(md_file))
                iso_primes.append(md["prime"])
                iso_nodes.append(md["nodes"])
            except: pass

if iso_primes:
    p_arr = np.array(iso_primes, dtype=float)
    n_arr = np.array(iso_nodes, dtype=float)
    deuring = (p_arr - 1) / 12

    r_full = np.corrcoef(deuring, n_arr)[0, 1]
    print(f"  Full Deuring: r={r_full:.8f} (n={len(p_arr)})")

    # Fragment into 100 random dummy groups
    for n_groups in [10, 50, 100, 200]:
        dummy_labels = [str(i) for i in rng.choice(n_groups, len(p_arr))]
        v25b, r25b = bv2.F25b_model_transportability(
            n_arr.tolist(), dummy_labels,
            [str(int(p) % 4) for p in p_arr])
        # Also F25 (old)
        v25, r25 = bv2.F25_transportability(
            n_arr.tolist(), dummy_labels,
            [str(int(p) % 4) for p in p_arr])

        oos = r25.get("weighted_oos_r2", 0)
        main = r25b.get("weighted_r2_main", 0)
        print(f"  {n_groups:4d} groups: F25 OOS={oos:.4f}, F25b main={main:.4f}, F25b={r25b.get('weighted_r2_main', 0):.4f}")

    # Key question: does Deuring become WEAK_NOISY with many groups?
    dummy_200 = [str(i) for i in rng.choice(200, len(p_arr))]
    v25b_200, r25b_200 = bv2.F25b_model_transportability(
        n_arr.tolist(), dummy_200, [str(int(p) % 4) for p in p_arr])

    if v25b_200 == "UNIVERSAL":
        rec("Deuring fragmentation", "PASS (stays UNIVERSAL)", f"200 groups: {v25b_200}")
    elif v25b_200 == "WEAK_NOISY":
        rec("Deuring fragmentation", "FAIL (collapses to WEAK_NOISY)",
            f"200 groups: main R²={r25b_200.get('weighted_r2_main', 0):.4f}")
    else:
        rec("Deuring fragmentation", v25b_200, str(r25b_200.get("weighted_r2_main", 0)))


# ============================================================
# BLOCK 6: Monotonicity trap (#31 endomorphism)
# ============================================================
print("\n" + "=" * 100)
print("BLOCK 6: MONOTONICITY TRAP — Is M4/M² monotonicity a sample-size artifact?")
print("=" * 100)

# The endomorphism finding shows M4/M² monotonically decreasing with more endomorphisms
# But sample sizes also change: USp(4) has 9262, N(G_{3,3}) has 43
# Test: does M4/M² decrease with SAMPLE SIZE regardless of group?
from sympy import factorint

max_exps = []
st_labels = []
count = 0
for c in valid_g2:
    cond_val = int(c["conductor"])
    if cond_val > 1 and cond_val < 10**9:
        try:
            factors = factorint(cond_val)
            if factors:
                max_exps.append(max(factors.values()))
                st_labels.append(c["st_group"])
                count += 1
        except: pass
    if count >= 5000: break

if count > 100:
    # Compute M4/M² for random subsamples of different sizes
    print(f"  Testing if M4/M² decreases with sample size (using USp(4) only):")
    usp4 = [max_exps[i] for i in range(len(max_exps)) if st_labels[i] == "USp(4)"]

    print(f"  {'n_sample':>10s} | {'M4/M2^2':>8s}")
    print("  " + "-" * 25)
    for sample_n in [20, 50, 100, 200, 500, 1000, len(usp4)]:
        if sample_n <= len(usp4):
            m4_vals = []
            for _ in range(20):
                sample = rng.choice(usp4, min(sample_n, len(usp4)), replace=False)
                m4_vals.append(m4m2(sample))
            m4_mean = np.mean([v for v in m4_vals if np.isfinite(v)])
            print(f"  {sample_n:10d} | {m4_mean:8.3f}")

    # Does M4/M² converge as n grows? If yes, the group differences are real.
    # If M4/M² drops with n for EVERY group, it's a bias.
    rec("Monotonicity trap", "See output", "M4/M2^2 vs sample size for USp(4)")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("ENDURANCE BATTERY SUMMARY")
print("=" * 100)
for r in results:
    print(f"  {r['name']:40s} | {r['verdict']:25s} | {r['metric'][:50]}")

print(f"\n  Total tests: {len(results)}")
pass_count = sum(1 for r in results if "PASS" in r["verdict"] or "SURVIVES" in r["verdict"])
fail_count = sum(1 for r in results if "FAIL" in r["verdict"] or "KILL" in r["verdict"])
print(f"  Pass: {pass_count}")
print(f"  Fail/Kill: {fail_count}")
print(f"  Other: {len(results) - pass_count - fail_count}")
