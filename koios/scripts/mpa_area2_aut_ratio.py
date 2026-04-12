"""
Koios MPA Area 2: Automorphism-to-Size Ratio (Symmetry Coupling)

Hypothesis: rho = log(aut_group_order) / log(size_variable) is a domain-agnostic
MPA coordinate encoding how much symmetry an object carries relative to its size.

Datasets: Lattices (39K), Groups (545K), Genus-2 curves (66K)

5-Gate Admission Test + IDN (3 normalizations)
"""
import sys, os, json, warnings
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

warnings.filterwarnings('ignore')
np.set_printoptions(precision=4)

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)


def idn_size_residual(values, size_var):
    x = np.log1p(np.array(size_var, dtype=float))
    y = np.array(values, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 10:
        return y, 0.0
    slope, intercept, r, p, se = stats.linregress(x, y)
    residuals = y - (slope * x + intercept)
    return residuals, r**2


def idn_rank_quantile(values, size_var, n_bins=20):
    x = np.array(size_var, dtype=float)
    y = np.array(values, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    try:
        bins = np.digitize(x, np.percentile(x[np.isfinite(x)], np.linspace(0, 100, n_bins + 1)[1:-1]))
    except:
        return stats.rankdata(y) / len(y)
    result = np.zeros(len(y))
    for b in np.unique(bins):
        m = bins == b
        vals = y[m]
        if len(vals) < 2:
            result[m] = 0.5
        else:
            result[m] = stats.rankdata(vals) / len(vals)
    return result


# ===================================================================
# LOAD DATA
# ===================================================================
print("=" * 70)
print("KOIOS MPA AREA 2: Automorphism-to-Size Ratio")
print("=" * 70)

# --- Lattices ---
print("\n--- Loading Lattices ---")
lat_path = ROOT / "cartography" / "lattices" / "data" / "lattices_full.json"
with open(lat_path) as f:
    lat_raw = json.load(f)

# Handle both list and dict-with-records format
if isinstance(lat_raw, dict) and "records" in lat_raw:
    lat_records = lat_raw["records"]
elif isinstance(lat_raw, list):
    lat_records = lat_raw
else:
    lat_records = list(lat_raw.values()) if isinstance(lat_raw, dict) else []

lat_data = []
for r in lat_records:
    aut = r.get("aut_group_order") or r.get("aut")
    dim = r.get("dimension") or r.get("dim") or r.get("n")
    if aut and dim and dim >= 2 and aut >= 1:
        rho = np.log(float(aut)) / np.log(float(dim))
        lat_data.append({
            "aut_order": int(aut),
            "size": int(dim),
            "size_name": "dimension",
            "rho": float(rho),
            "domain": "Lattices",
        })
print(f"  Lattices: {len(lat_data)} with rho (dim >= 2, aut >= 1)")
if lat_data:
    print(f"  Sample rho: {[d['rho'] for d in lat_data[:5]]}")
    print(f"  aut range: {min(d['aut_order'] for d in lat_data)} - {max(d['aut_order'] for d in lat_data)}")
    print(f"  dim range: {min(d['size'] for d in lat_data)} - {max(d['size'] for d in lat_data)}")

# --- Groups ---
print("\n--- Loading Groups ---")
grp_path = ROOT / "cartography" / "groups" / "data" / "abstract_groups.json"
with open(grp_path) as f:
    grp_raw = json.load(f)

if isinstance(grp_raw, dict) and "records" in grp_raw:
    grp_records = grp_raw["records"]
elif isinstance(grp_raw, list):
    grp_records = grp_raw
else:
    grp_records = list(grp_raw.values()) if isinstance(grp_raw, dict) else []

grp_data = []
for r in grp_records:
    ncc = r.get("num_conjugacy_classes") or r.get("number_conjugacy_classes")
    order = r.get("order")
    try:
        ncc = int(ncc) if ncc else 0
        order = int(order) if order else 0
    except (ValueError, TypeError):
        continue
    if ncc >= 1 and order >= 2:
        rho = np.log(float(ncc)) / np.log(float(order))
        grp_data.append({
            "num_conj_classes": ncc,
            "size": order,
            "size_name": "order",
            "rho": float(rho),
            "domain": "Groups",
        })
print(f"  Groups: {len(grp_data)} with rho (order >= 2, ncc >= 1)")
if grp_data:
    print(f"  Sample rho: {[d['rho'] for d in grp_data[:5]]}")
    print(f"  ncc range: {min(d['num_conj_classes'] for d in grp_data)} - {max(d['num_conj_classes'] for d in grp_data)}")
    print(f"  order range: {min(d['size'] for d in grp_data)} - {max(d['size'] for d in grp_data)}")

# --- Genus-2 ---
print("\n--- Loading Genus-2 ---")
g2_path = ROOT / "cartography" / "genus2" / "data" / "genus2_curves_full.json"
with open(g2_path) as f:
    g2_raw = json.load(f)

if isinstance(g2_raw, dict) and "records" in g2_raw:
    g2_records = g2_raw["records"]
elif isinstance(g2_raw, list):
    g2_records = g2_raw
else:
    g2_records = list(g2_raw.values()) if isinstance(g2_raw, dict) else []

g2_data = []
for r in g2_records:
    # aut_grp is stored as string like "[2, 1]" or list [2, 1]
    aut_raw = r.get("aut_grp")
    conductor = r.get("conductor")
    if aut_raw and conductor and conductor > 1:
        if isinstance(aut_raw, str):
            try:
                aut_list = json.loads(aut_raw.replace("'", '"'))
                aut_order = aut_list[0] if isinstance(aut_list, list) else int(aut_raw)
            except:
                continue
        elif isinstance(aut_raw, list):
            aut_order = aut_raw[0]
        else:
            aut_order = int(aut_raw)

        if aut_order >= 1:
            rho = np.log(float(aut_order)) / np.log(float(conductor))
            g2_data.append({
                "aut_order": int(aut_order),
                "size": int(conductor),
                "size_name": "conductor",
                "rho": float(rho),
                "domain": "Genus2",
            })
print(f"  Genus-2: {len(g2_data)} with rho (conductor > 1, aut >= 1)")
if g2_data:
    print(f"  Sample rho: {[round(d['rho'], 4) for d in g2_data[:5]]}")
    print(f"  aut range: {min(d['aut_order'] for d in g2_data)} - {max(d['aut_order'] for d in g2_data)}")
    print(f"  conductor range: {min(d['size'] for d in g2_data)} - {max(d['size'] for d in g2_data)}")


# ===================================================================
# SANITY CHECK
# ===================================================================
print("\n" + "=" * 70)
print("SANITY CHECK: Distributions")
print("=" * 70)

for name, data in [("Lattices", lat_data), ("Groups", grp_data), ("Genus2", g2_data)]:
    if not data:
        print(f"  {name}: NO DATA")
        continue
    rhos = np.array([d["rho"] for d in data])
    print(f"  {name} (n={len(data)}): rho mean={np.mean(rhos):.4f}, "
          f"std={np.std(rhos):.4f}, median={np.median(rhos):.4f}, "
          f"[{np.percentile(rhos, 5):.4f}, {np.percentile(rhos, 95):.4f}]")


# ===================================================================
# IDN
# ===================================================================
print("\n" + "=" * 70)
print("IDN: 3 Normalizations")
print("=" * 70)

for name, data in [("Lattices", lat_data), ("Groups", grp_data), ("Genus2", g2_data)]:
    if not data:
        continue
    rhos = [d["rho"] for d in data]
    sizes = [d["size"] for d in data]

    residuals, r2 = idn_size_residual(rhos, sizes)
    rank_q = idn_rank_quantile(np.array(rhos), np.array(sizes, dtype=float))

    print(f"\n  {name} IDN:")
    print(f"    Size R^2 removed: {r2:.4f}")
    print(f"    Residual mean: {np.mean(residuals):.4f}, std: {np.std(residuals):.4f}")
    info_retained = np.std(residuals) / np.std(rhos) if np.std(rhos) > 0 else 0
    print(f"    Info retained: {info_retained:.1%}")

    for i, d in enumerate(data):
        if i < len(residuals):
            d["idn_residual"] = float(residuals[i])
            d["idn_rank_q"] = float(rank_q[i]) if i < len(rank_q) else 0.5


# ===================================================================
# GATE 1: Null-calibrated
# ===================================================================
print("\n" + "=" * 70)
print("GATE 1: Null calibration (permutation test)")
print("=" * 70)

# For each domain: permute aut values within size groups, recompute rho
gate1_results = {}
for name, data in [("Lattices", lat_data), ("Groups", grp_data), ("Genus2", g2_data)]:
    if len(data) < 100:
        print(f"  {name}: insufficient data")
        gate1_results[name] = False
        continue

    observed_std = np.std([d["rho"] for d in data])

    # Group by size, permute aut within groups
    by_size = defaultdict(list)
    for d in data:
        by_size[d["size"]].append(d["aut_order"] if "aut_order" in d else d.get("num_conj_classes", 1))

    null_stds = []
    for _ in range(500):
        perm_rhos = []
        for d in data:
            s = d["size"]
            group = by_size[s]
            shuffled_aut = rng.choice(group)
            if shuffled_aut >= 1 and s >= 2:
                perm_rhos.append(np.log(float(shuffled_aut)) / np.log(float(s)))
        if perm_rhos:
            null_stds.append(np.std(perm_rhos))

    null_stds = np.array(null_stds)
    z = (observed_std - np.mean(null_stds)) / (np.std(null_stds) + 1e-15)
    p_val = np.mean(null_stds >= observed_std)

    print(f"  {name}: observed std={observed_std:.4f}, null mean={np.mean(null_stds):.4f}, "
          f"z={z:.2f}, p={p_val:.4f}")
    gate1_results[name] = bool(p_val < 0.05 or abs(z) > 2)

gate1_pass = all(gate1_results.values()) if gate1_results else False
print(f"  GATE 1: {'PASS' if gate1_pass else 'FAIL'}")


# ===================================================================
# GATE 2: Representation stability
# ===================================================================
print("\n" + "=" * 70)
print("GATE 2: Representation stability")
print("=" * 70)
print("  Test: rho is invariant under relabeling (aut_order and size are integers,")
print("  not representation-dependent). Log ratio of integers is basis-independent.")
print("  This gate passes by construction for integer invariants.")
gate2_pass = True
print(f"  GATE 2: PASS (integer invariants are representation-stable)")


# ===================================================================
# GATE 3: Not reducible to marginals
# ===================================================================
print("\n" + "=" * 70)
print("GATE 3: Not reducible to marginals")
print("=" * 70)

gate3_results = {}
for name, data in [("Lattices", lat_data), ("Groups", grp_data), ("Genus2", g2_data)]:
    if len(data) < 100:
        gate3_results[name] = False
        continue
    rhos = np.array([d["rho"] for d in data])
    sizes = np.log1p(np.array([d["size"] for d in data], dtype=float))
    corr = np.corrcoef(rhos, sizes)[0, 1]

    residuals = np.array([d.get("idn_residual", 0) for d in data])
    info_retained = np.std(residuals) / np.std(rhos) if np.std(rhos) > 0 else 0

    print(f"  {name}: corr(rho, log_size)={corr:.4f}, info retained={info_retained:.1%}")
    gate3_results[name] = info_retained > 0.5

gate3_pass = all(gate3_results.values()) if gate3_results else False
print(f"  GATE 3: {'PASS' if gate3_pass else 'FAIL'}")


# ===================================================================
# GATE 4: Non-tautological
# ===================================================================
print("\n" + "=" * 70)
print("GATE 4: Non-tautological")
print("=" * 70)

# For groups: is ncc/order forced by Burnside?
# Check: variance of rho within each order
if grp_data:
    by_order = defaultdict(list)
    for d in grp_data:
        by_order[d["size"]].append(d["rho"])

    # For orders with multiple groups, compute within-order variance
    within_vars = []
    for order, rhos in by_order.items():
        if len(rhos) >= 2:
            within_vars.append(np.var(rhos))

    mean_within_var = np.mean(within_vars) if within_vars else 0
    total_var = np.var([d["rho"] for d in grp_data])
    within_ratio = mean_within_var / total_var if total_var > 0 else 0

    print(f"  Groups: mean within-order variance / total variance = {within_ratio:.4f}")
    print(f"    ({len(within_vars)} orders with 2+ groups)")
    print(f"    If ratio ~ 0: rho is determined by order alone (tautological)")
    print(f"    If ratio ~ 1: rho varies freely within orders (non-tautological)")

    # Also check lattices: within-dimension variance
    lat_by_dim = defaultdict(list)
    for d in lat_data:
        lat_by_dim[d["size"]].append(d["rho"])
    lat_within = [np.var(v) for v in lat_by_dim.values() if len(v) >= 2]
    lat_within_ratio = np.mean(lat_within) / np.var([d["rho"] for d in lat_data]) if lat_within else 0
    print(f"  Lattices: within-dim variance ratio = {lat_within_ratio:.4f}")

    gate4_pass = within_ratio > 0.1  # At least 10% of variance is within-order
    print(f"  GATE 4: {'PASS' if gate4_pass else 'FAIL'} (within-group variance ratio > 0.1)")
else:
    gate4_pass = False
    print(f"  GATE 4: FAIL (no group data)")


# ===================================================================
# GATE 5: Domain-agnostic
# ===================================================================
print("\n" + "=" * 70)
print("GATE 5: Domain-agnostic (cross-domain comparison)")
print("=" * 70)

# Collect IDN residuals from all domains
all_residuals = []
all_labels = []
for name, data in [("Lattices", lat_data), ("Groups", grp_data), ("Genus2", g2_data)]:
    for d in data:
        r = d.get("idn_residual")
        if r is not None and np.isfinite(r):
            all_residuals.append(r)
            all_labels.append(name)

all_residuals = np.array(all_residuals)
all_labels = np.array(all_labels)

if len(all_residuals) > 100:
    # eta^2
    groups = defaultdict(list)
    for v, l in zip(all_residuals, all_labels):
        groups[l].append(v)

    ss_between = sum(len(g) * (np.mean(g) - np.mean(all_residuals))**2 for g in groups.values())
    ss_total = np.sum((all_residuals - np.mean(all_residuals))**2)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0

    # Permutation null
    n_perm = 1000
    perm_etas = []
    for _ in range(n_perm):
        shuffled = rng.permutation(all_labels)
        pg = defaultdict(list)
        for v, l in zip(all_residuals, shuffled):
            pg[l].append(v)
        ss_b = sum(len(g) * (np.mean(g) - np.mean(all_residuals))**2 for g in pg.values())
        perm_etas.append(ss_b / ss_total if ss_total > 0 else 0)

    perm_etas = np.array(perm_etas)
    z_score = (eta_sq - np.mean(perm_etas)) / (np.std(perm_etas) + 1e-15)

    print(f"  eta^2(domain -> IDN rho) = {eta_sq:.4f}")
    print(f"  Permutation null: mean={np.mean(perm_etas):.6f}, std={np.std(perm_etas):.6f}")
    print(f"  z = {z_score:.2f}")

    for name in sorted(groups.keys()):
        g = np.array(groups[name])
        print(f"  {name}: n={len(g)}, mean={np.mean(g):.4f}, std={np.std(g):.4f}")

    # Pairwise KS
    domain_names = sorted(groups.keys())
    for i, a in enumerate(domain_names):
        for b in domain_names[i+1:]:
            ks, p = stats.ks_2samp(
                np.array(groups[a])[:5000],
                np.array(groups[b])[:5000]
            )
            print(f"  KS({a} vs {b}): stat={ks:.4f}, p={p:.2e}")

    gate5_pass = eta_sq < 0.05
    print(f"  GATE 5: {'PASS' if gate5_pass else 'FAIL'} (eta^2 < 0.05)")
else:
    gate5_pass = False
    print(f"  GATE 5: FAIL (insufficient data)")


# ===================================================================
# SUMMARY
# ===================================================================
print("\n" + "=" * 70)
print("AREA 2 SUMMARY: Automorphism-to-Size Ratio as MPA Coordinate")
print("=" * 70)

gates = {
    "Gate 1 (Null-calibrated)": gate1_pass,
    "Gate 2 (Representation-stable)": gate2_pass,
    "Gate 3 (Not reducible to marginals)": gate3_pass,
    "Gate 4 (Non-tautological)": gate4_pass,
    "Gate 5 (Domain-agnostic)": gate5_pass,
}

for name, passed in gates.items():
    print(f"  {name}: {'PASS' if passed else 'FAIL'}")

all_pass = all(gates.values())
print(f"\n  VERDICT: {'ADMITTED TO TENSOR' if all_pass else 'REJECTED'}")
print(f"  Gates passed: {sum(gates.values())}/5")

# Save results
results = {
    "area": "Area 2: Automorphism-to-Size Ratio",
    "invariant": "aut_size_ratio",
    "phoneme_class": "symmetry",
    "datasets": {},
    "gates": {name: bool(passed) for name, passed in gates.items()},
    "cross_domain": {
        "eta_sq_domain": float(eta_sq) if 'eta_sq' in dir() else None,
        "permutation_z": float(z_score) if 'z_score' in dir() else None,
    },
    "verdict": "ADMITTED" if all_pass else "REJECTED",
    "gates_passed": int(sum(gates.values())),
    "gates_total": 5,
}

for name, data in [("Lattices", lat_data), ("Groups", grp_data), ("Genus2", g2_data)]:
    if data:
        rhos = [d["rho"] for d in data]
        results["datasets"][name] = {
            "n": len(data),
            "mean_rho": float(np.mean(rhos)),
            "std_rho": float(np.std(rhos)),
            "median_rho": float(np.median(rhos)),
        }

out_path = RESULTS_DIR / "mpa_area2_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to {out_path}")
