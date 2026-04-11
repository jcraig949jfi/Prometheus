"""
Lattice Automorphism Group Size Distribution
=============================================
Measures |Aut(L)| distribution across 39K LMFDB lattices and correlates
with dim, det, kissing, class_number, and theta series structure.
"""

import json
import numpy as np
from collections import Counter
from scipy import stats
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ── Load data ──────────────────────────────────────────────────────────
with open(ROOT / "lmfdb_dump" / "lat_lattices.json", "r") as f:
    raw = json.load(f)

records = raw["records"]
print(f"Loaded {len(records)} lattice records")

# Parse fields
aut_orders = []
dims = []
dets = []
kissings = []
class_nums = []
theta_lengths = []
theta_nonzero_fracs = []
names = []
labels = []

for r in records:
    try:
        a = int(r["aut"])
    except (ValueError, TypeError):
        continue
    aut_orders.append(a)
    dims.append(r["dim"])
    dets.append(r["det"])
    kissings.append(r["kissing"])
    class_nums.append(r["class_number"])
    names.append(r.get("name", ""))
    labels.append(r.get("label", ""))

    ts = r.get("theta_series", [])
    theta_lengths.append(len(ts))
    if len(ts) > 0:
        theta_nonzero_fracs.append(sum(1 for x in ts if x != 0) / len(ts))
    else:
        theta_nonzero_fracs.append(0.0)

aut = np.array(aut_orders)
dim = np.array(dims)
det = np.array(dets)
kiss = np.array(kissings)
cn = np.array(class_nums)
theta_nz = np.array(theta_nonzero_fracs)

N = len(aut)
print(f"Valid records: {N}")

# ── 1. Distribution analysis ──────────────────────────────────────────
log_aut = np.log10(aut.astype(float))

# Basic stats
print(f"\n=== |Aut(L)| Distribution ===")
print(f"  min: {aut.min()}, max: {aut.max()}")
print(f"  median: {np.median(aut):.0f}")
print(f"  mean: {np.mean(aut):.2f}")
print(f"  log10 mean: {np.mean(log_aut):.3f}")
print(f"  log10 std: {np.std(log_aut):.3f}")

# Value counts (top 20)
aut_counts = Counter(aut_orders)
top20 = aut_counts.most_common(20)
print(f"\nTop 20 most common |Aut| values:")
for val, cnt in top20:
    print(f"  |Aut|={val}: {cnt} lattices ({100*cnt/N:.1f}%)")

# Test log-normality on log10(aut)
ks_stat, ks_p = stats.kstest(log_aut, 'norm', args=(np.mean(log_aut), np.std(log_aut)))
print(f"\nKS test for log-normality: stat={ks_stat:.4f}, p={ks_p:.2e}")

# Histogram of log10(|Aut|)
log_bins = np.arange(0, np.max(log_aut) + 0.5, 0.5)
log_hist, _ = np.histogram(log_aut, bins=log_bins)
log_hist_data = {f"{log_bins[i]:.1f}-{log_bins[i+1]:.1f}": int(log_hist[i])
                 for i in range(len(log_hist)) if log_hist[i] > 0}

# Power-of-2 analysis (many aut groups are powers of 2)
pow2_count = sum(1 for a in aut if a > 0 and (a & (a-1)) == 0)
print(f"\nPower-of-2 |Aut| values: {pow2_count}/{N} ({100*pow2_count/N:.1f}%)")

# Even values
even_count = sum(1 for a in aut if a % 2 == 0)
print(f"Even |Aut| values: {even_count}/{N} ({100*even_count/N:.1f}%)")

# ── 2. Correlations with invariants ───────────────────────────────────
print(f"\n=== Correlations (Spearman) ===")
correlations = {}
for name_inv, arr in [("dim", dim), ("det", det), ("kissing", kiss),
                       ("class_number", cn), ("theta_nonzero_frac", theta_nz)]:
    mask = np.isfinite(arr.astype(float)) & np.isfinite(log_aut)
    rho, p = stats.spearmanr(log_aut[mask], arr[mask])
    correlations[name_inv] = {"rho": round(float(rho), 4), "p": float(f"{p:.2e}")}
    print(f"  log10|Aut| vs {name_inv}: rho={rho:.4f}, p={p:.2e}")

# ── 3. |Aut| by dimension ─────────────────────────────────────────────
print(f"\n=== |Aut| by Dimension ===")
aut_by_dim = {}
unique_dims = sorted(set(dims))
for d in unique_dims:
    mask_d = dim == d
    vals = aut[mask_d]
    aut_by_dim[str(d)] = {
        "count": int(np.sum(mask_d)),
        "median_aut": float(np.median(vals)),
        "max_aut": int(np.max(vals)),
        "mean_log10_aut": round(float(np.mean(np.log10(vals.astype(float)))), 3),
    }
    print(f"  dim={d}: n={np.sum(mask_d)}, median|Aut|={np.median(vals):.0f}, max|Aut|={np.max(vals)}")

# ── 4. Theta series structure vs |Aut| ────────────────────────────────
print(f"\n=== Theta Series vs |Aut| ===")
# Bin by log10(|Aut|) quartiles
quartiles = np.percentile(log_aut, [25, 50, 75])
q_labels = ["Q1 (low)", "Q2", "Q3", "Q4 (high)"]
q_bounds = [(-np.inf, quartiles[0]), (quartiles[0], quartiles[1]),
            (quartiles[1], quartiles[2]), (quartiles[2], np.inf)]

theta_by_aut_quartile = {}
# Distribution is extremely concentrated (81% at |Aut|=2 or 4).
# Use meaningful bins based on actual value boundaries.
aut_bins = [
    ("|Aut|=2", aut == 2),
    ("|Aut|=4", aut == 4),
    ("|Aut|=8", aut == 8),
    ("|Aut|=12-48", (aut >= 12) & (aut <= 48)),
    ("|Aut|>48", aut > 48),
]
for ql, mask_q in aut_bins:
    nz_vals = theta_nz[mask_q]
    n_q = int(np.sum(mask_q))
    theta_by_aut_quartile[ql] = {
        "n": n_q,
        "mean_nonzero_frac": round(float(np.mean(nz_vals)), 4) if n_q > 0 else None,
        "std_nonzero_frac": round(float(np.std(nz_vals)), 4) if n_q > 0 else None,
    }
    mean_str = f"{np.mean(nz_vals):.4f}" if n_q > 0 else "N/A"
    print(f"  {ql}: n={n_q}, mean theta nonzero frac={mean_str}")

# For records with theta series, check if high-symmetry lattices have
# more structured (sparser) theta series
print(f"\n  Interpretation: Higher |Aut| -> {'sparser' if correlations['theta_nonzero_frac']['rho'] < 0 else 'denser'} theta series")

# ── 5. Most symmetric lattices ─────────────────────────────────────────
print(f"\n=== Top 20 Most Symmetric Lattices ===")
sorted_idx = np.argsort(-aut)
top_symmetric = []
for i in sorted_idx[:20]:
    entry = {
        "label": labels[i],
        "name": names[i],
        "dim": int(dim[i]),
        "det": int(det[i]),
        "aut": int(aut[i]),
        "log10_aut": round(float(log_aut[i]), 3),
        "kissing": int(kiss[i]),
        "class_number": int(cn[i]),
    }
    top_symmetric.append(entry)
    nm = names[i] if names[i] else labels[i]
    print(f"  {nm}: dim={dim[i]}, |Aut|={aut[i]}, kissing={kiss[i]}, det={det[i]}")

# Check for famous lattices
famous = {"E8": None, "Leech": None, "D4": None, "A2": None, "BW16": None}
for i in range(N):
    raw_name = names[i]
    n = str(raw_name).strip() if raw_name else ""
    for f in famous:
        if f.lower() in n.lower() or (f == "BW16" and "Barnes-Wall" in n):
            if famous[f] is None or aut[i] > famous[f]["aut"]:
                famous[f] = {"name": n, "label": labels[i], "dim": int(dim[i]),
                             "aut": int(aut[i]), "kissing": int(kiss[i])}

print(f"\n=== Famous Lattice Check ===")
for f, info in famous.items():
    if info:
        print(f"  {f}: {info}")
    else:
        print(f"  {f}: not found by name")

# ── 6. Does |Aut| predict kissing number? ─────────────────────────────
# Within fixed dimension
print(f"\n=== |Aut| as Kissing Number Predictor (within dim) ===")
kissing_pred = {}
for d in unique_dims:
    mask_d = dim == d
    if np.sum(mask_d) < 10:
        continue
    rho_k, p_k = stats.spearmanr(log_aut[mask_d], kiss[mask_d])
    kissing_pred[str(d)] = {"rho": round(float(rho_k), 4),
                            "p": float(f"{p_k:.2e}"), "n": int(np.sum(mask_d))}
    if p_k < 0.01:
        print(f"  dim={d}: rho={rho_k:.4f}, p={p_k:.2e}, n={np.sum(mask_d)}")

# ── Assemble results ──────────────────────────────────────────────────
results = {
    "experiment": "lattice_automorphism_group_distribution",
    "data_source": "LMFDB lat_lattices (39K records)",
    "n_records": N,
    "distribution": {
        "min": int(aut.min()),
        "max": int(aut.max()),
        "median": float(np.median(aut)),
        "mean_log10": round(float(np.mean(log_aut)), 3),
        "std_log10": round(float(np.std(log_aut)), 3),
        "ks_lognormal": {"statistic": round(ks_stat, 4), "p_value": float(f"{ks_p:.2e}")},
        "power_of_2_fraction": round(pow2_count / N, 4),
        "even_fraction": round(even_count / N, 4),
        "log10_histogram": log_hist_data,
        "top20_values": [{"aut": v, "count": c, "frac": round(c/N, 4)} for v, c in top20],
    },
    "correlations_spearman": correlations,
    "aut_by_dimension": aut_by_dim,
    "theta_vs_aut": {
        "quartile_analysis": theta_by_aut_quartile,
        "direction": "sparser" if correlations["theta_nonzero_frac"]["rho"] < 0 else "denser",
    },
    "top20_most_symmetric": top_symmetric,
    "kissing_prediction_within_dim": kissing_pred,
    "findings": [],
}

# Generate findings
findings = []

# Distribution shape
if ks_p < 0.01:
    findings.append("log10|Aut| is NOT log-normal (KS p={:.2e}); heavy right tail from famous lattices".format(ks_p))
else:
    findings.append("log10|Aut| is approximately log-normal")

if results["distribution"]["power_of_2_fraction"] > 0.3:
    findings.append(f"{100*results['distribution']['power_of_2_fraction']:.0f}% of |Aut| values are powers of 2 — reflects hyperoctahedral/reflection group dominance")

# Correlations
for inv, d in correlations.items():
    if abs(d["rho"]) > 0.3 and d["p"] < 1e-10:
        findings.append(f"Strong correlation: log10|Aut| vs {inv} (rho={d['rho']:.3f})")

# Top symmetric
top_name = top_symmetric[0]["name"] or top_symmetric[0]["label"]
findings.append(f"Most symmetric lattice: {top_name} with |Aut|={top_symmetric[0]['aut']} (dim={top_symmetric[0]['dim']})")

# Kissing prediction
strong_kiss = {d: v for d, v in kissing_pred.items() if abs(v["rho"]) > 0.5}
if strong_kiss:
    dims_str = ", ".join(strong_kiss.keys())
    findings.append(f"|Aut| strongly predicts kissing number within dimensions: {dims_str}")

results["findings"] = findings

for f in findings:
    print(f"\nFINDING: {f}")

# ── Save ──────────────────────────────────────────────────────────────
out_path = pathlib.Path(__file__).resolve().parent / "lattice_automorphism_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
