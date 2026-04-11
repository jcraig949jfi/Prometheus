"""
Lattice Root System Detection from Theta Series
-------------------------------------------------
Detects root system type (A_n, D_n, E_n) signatures from theta series.
Key idea: (dim, min_norm, kissing_number) clusters should separate root system types.
"""

import json
from collections import defaultdict

DATA = "F:/Prometheus/cartography/lmfdb_dump/lat_lattices.json"
OUT  = "F:/Prometheus/cartography/v2/lattice_root_system_results.json"

# Load
with open(DATA) as f:
    raw = json.load(f)
records = raw["records"]
print(f"Loaded {len(records)} lattices")

# ── Step 1-4: Extract (dim, min_norm, kissing) and group ──

clusters = defaultdict(list)

for r in records:
    theta = r.get("theta_series")
    dim = r.get("dim")
    kissing = r.get("kissing")
    minimum = r.get("minimum")
    label = r.get("label", "?")
    name = r.get("name", "")

    if not theta or dim is None:
        continue

    # Find first nonzero coeff after index 0 (index 0 is always 1)
    min_norm = None
    kiss_from_theta = None
    for i in range(1, len(theta)):
        if theta[i] > 0:
            min_norm = i
            kiss_from_theta = theta[i]
            break

    if min_norm is None:
        continue

    key = (dim, min_norm, kiss_from_theta)
    clusters[key].append({
        "label": label,
        "name": name,
        "theta": theta,
        "det": r.get("det"),
        "level": r.get("level"),
    })

print(f"\n── Step 5: {len(clusters)} distinct (dim, min_norm, kissing) clusters ──")

# ── Step 6-7: Within-cluster theta divergence ──

results = {}
for key, members in sorted(clusters.items(), key=lambda x: (-len(x[1]), x[0])):
    dim, mn, kiss = key
    cluster_key = f"d{dim}_m{mn}_k{kiss}"
    n = len(members)

    # Find first divergence position
    if n == 1:
        first_diff = None
        all_identical = True
    else:
        # Compare all theta series pairwise
        ref = members[0]["theta"]
        all_identical = True
        first_diff = None
        for m in members[1:]:
            other = m["theta"]
            min_len = min(len(ref), len(other))
            for i in range(min_len):
                if ref[i] != other[i]:
                    if first_diff is None or i < first_diff:
                        first_diff = i
                    all_identical = False
                    break
            if len(ref) != len(other):
                all_identical = False
                if first_diff is None:
                    first_diff = min_len

    # Collect sample names
    named = []
    for m in members:
        nm = m["name"]
        if nm:
            named.append(nm if isinstance(nm, str) else str(nm))
    sample_labels = [m["label"] for m in members[:5]]

    results[cluster_key] = {
        "dim": dim,
        "min_norm": mn,
        "kissing": kiss,
        "count": n,
        "theta_identical": all_identical,
        "first_divergence_pos": first_diff,
        "named_members": named[:10],
        "sample_labels": sample_labels,
    }

# ── Print summary ──

# Sort by count descending
sorted_results = dict(sorted(results.items(), key=lambda x: -x[1]["count"]))

print(f"\nTop 30 clusters by size:")
print(f"{'cluster':<20} {'count':>6} {'identical':>9} {'div_pos':>8} {'names'}")
for k, v in list(sorted_results.items())[:30]:
    names_str = ", ".join(v["named_members"][:3]) if v["named_members"] else ""
    print(f"{k:<20} {v['count']:>6} {str(v['theta_identical']):>9} {str(v['first_divergence_pos']):>8} {names_str[:50]}")

# ── Root system signature table ──
# Known root lattices: A_n kissing=n(n+1), D_n kissing=2n(n-1), E_6=72, E_7=126, E_8=240
# All root lattices have min_norm=2

print(f"\n── Root system candidates (min_norm=2) ──")
root_sigs = {
    (2, 2, 4): "A_2 (=hex)", (3, 2, 12): "A_3 (=D_3=fcc)",
    (4, 2, 20): "A_4", (4, 2, 24): "D_4",
    (5, 2, 30): "A_5", (5, 2, 40): "D_5",
    (6, 2, 42): "A_6", (6, 2, 60): "D_6", (6, 2, 72): "E_6",
    (7, 2, 56): "A_7", (7, 2, 84): "D_7", (7, 2, 126): "E_7",
    (8, 2, 72): "A_8", (8, 2, 112): "D_8", (8, 2, 240): "E_8",
    (2, 2, 6): "A_2* (hex dual)", (1, 2, 2): "A_1 (=Z)",
}

print(f"{'signature':<22} {'root_type':<15} {'count':>6} {'identical':>9} {'div_pos':>8}")
for key in sorted(clusters.keys()):
    dim, mn, kiss = key
    if mn != 2:
        continue
    rt = root_sigs.get(key, "?")
    ck = f"d{dim}_m{mn}_k{kiss}"
    r = results[ck]
    print(f"({dim},{mn},{kiss}){'':<12} {rt:<15} {r['count']:>6} {str(r['theta_identical']):>9} {str(r['first_divergence_pos']):>8}")

# ── Dimension distribution ──
dim_counts = defaultdict(int)
for r in records:
    d = r.get("dim")
    if d is not None:
        dim_counts[d] += 1
print(f"\nDimension distribution:")
for d in sorted(dim_counts):
    print(f"  dim={d}: {dim_counts[d]}")

# ── Stats ──
n_identical = sum(1 for v in results.values() if v["theta_identical"])
n_divergent = sum(1 for v in results.values() if not v["theta_identical"])
n_singleton = sum(1 for v in results.values() if v["count"] == 1)
n_multi = sum(1 for v in results.values() if v["count"] > 1)

# Divergence position histogram for non-identical clusters
div_positions = [v["first_divergence_pos"] for v in results.values()
                 if v["first_divergence_pos"] is not None]
if div_positions:
    avg_div = sum(div_positions) / len(div_positions)
    min_div = min(div_positions)
    max_div = max(div_positions)
else:
    avg_div = min_div = max_div = None

summary = {
    "total_lattices": len(records),
    "lattices_with_theta": sum(1 for r in records if r.get("theta_series")),
    "total_clusters": len(clusters),
    "singleton_clusters": n_singleton,
    "multi_member_clusters": n_multi,
    "all_identical_theta": n_identical,
    "divergent_theta": n_divergent,
    "divergence_stats": {
        "mean_position": round(avg_div, 2) if avg_div else None,
        "min_position": min_div,
        "max_position": max_div,
        "count": len(div_positions),
    },
    "root_system_signatures": {str(k): v for k, v in root_sigs.items()},
}

print(f"\n── Summary ──")
print(f"Total clusters: {len(clusters)}")
print(f"Singletons: {n_singleton}, Multi-member: {n_multi}")
print(f"Identical theta within cluster: {n_identical}")
print(f"Divergent theta within cluster: {n_divergent}")
if div_positions:
    print(f"Divergence position: mean={avg_div:.1f}, min={min_div}, max={max_div}")

# ── Save ──
output = {
    "summary": summary,
    "clusters": sorted_results,
}

with open(OUT, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to {OUT}")
