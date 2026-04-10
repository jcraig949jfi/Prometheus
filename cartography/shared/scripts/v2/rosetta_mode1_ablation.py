"""
Rosetta Stone Mode 1 Ablation
==============================
Load the 60x60 cross-module connectivity matrix from operadic_dynamics_results.json.
Run SVD to identify top 3 principal components.
Ablate Component 1 (universal vocabulary, ~57% variance).
Reconstruct the matrix. Identify module pairs that GAIN connectivity
(lower distance = stronger connection) after ablation.
Determine which Fungrim symbols/operators become load-bearing in Mode 2.

Saves results to rosetta_mode1_ablation_results.json.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).resolve().parent

# ── Load data ──────────────────────────────────────────────────────────────────
with open(HERE / "operadic_dynamics_results.json") as f:
    operadic = json.load(f)

with open(HERE / "gamma_wormhole_results.json") as f:
    gamma = json.load(f)

modules = operadic["distance_matrix"]["modules"]  # 60 modules
raw_matrix = np.array(operadic["distance_matrix"]["matrix"], dtype=np.float64)
n = len(modules)
mod_idx = {m: i for i, m in enumerate(modules)}

print(f"Loaded {n}x{n} distance matrix across {n} Fungrim modules")

# ── Convert distance to connectivity ───────────────────────────────────────────
# Connectivity = 1 - distance (distance 0 = max connectivity 1)
connectivity = 1.0 - raw_matrix

# Zero out diagonal (self-connections are trivial)
np.fill_diagonal(connectivity, 0.0)

print(f"Connectivity range: [{connectivity.min():.4f}, {connectivity.max():.4f}]")
print(f"Mean off-diagonal connectivity: {connectivity[~np.eye(n, dtype=bool)].mean():.4f}")

# ── SVD decomposition ─────────────────────────────────────────────────────────
# Center the matrix (subtract mean of each row)
row_means = connectivity.mean(axis=1, keepdims=True)
centered = connectivity - row_means

U, S, Vt = np.linalg.svd(centered, full_matrices=False)

total_var = (S ** 2).sum()
explained = (S ** 2) / total_var
cumulative = np.cumsum(explained)

print(f"\n=== SVD Components ===")
for i in range(min(10, n)):
    print(f"  Component {i+1}: {explained[i]*100:.2f}% variance "
          f"(cumulative: {cumulative[i]*100:.2f}%)")

# ── Identify top 3 components ─────────────────────────────────────────────────
comp1_var = explained[0] * 100
comp2_var = explained[1] * 100
comp3_var = explained[2] * 100

print(f"\nMode 1 (universal vocabulary): {comp1_var:.1f}%")
print(f"Mode 2 (NT<->algebra axis):     {comp2_var:.1f}%")
print(f"Mode 3 (continuous<->discrete):  {comp3_var:.1f}%")

# ── Analyze component loadings ─────────────────────────────────────────────────
# U columns = left singular vectors = module loadings on each component
loadings_1 = U[:, 0]
loadings_2 = U[:, 1]
loadings_3 = U[:, 2]

# Mode 1: modules sorted by |loading| (universal vocabulary)
mode1_order = np.argsort(-np.abs(loadings_1))
print(f"\n=== Mode 1 (Universal Vocabulary) Top Modules ===")
for i in mode1_order[:15]:
    print(f"  {modules[i]:35s} loading={loadings_1[i]:+.4f}")

# Mode 2: NT<->algebra axis
mode2_order = np.argsort(-np.abs(loadings_2))
print(f"\n=== Mode 2 (NT<->Algebra Axis) Top Modules ===")
for i in mode2_order[:15]:
    print(f"  {modules[i]:35s} loading={loadings_2[i]:+.4f}")

# Identify the two poles of Mode 2
pos_pole = [(modules[i], loadings_2[i]) for i in range(n) if loadings_2[i] > 0]
neg_pole = [(modules[i], loadings_2[i]) for i in range(n) if loadings_2[i] < 0]
pos_pole.sort(key=lambda x: -x[1])
neg_pole.sort(key=lambda x: x[1])

print(f"\n  Mode 2 positive pole (NT?): {[p[0] for p in pos_pole[:8]]}")
print(f"  Mode 2 negative pole (Algebra?): {[p[0] for p in neg_pole[:8]]}")

# Mode 3: continuous<->discrete
mode3_order = np.argsort(-np.abs(loadings_3))
print(f"\n=== Mode 3 (Continuous<->Discrete) Top Modules ===")
for i in mode3_order[:15]:
    print(f"  {modules[i]:35s} loading={loadings_3[i]:+.4f}")

# ── ABLATION: Set Component 1 to Zero ─────────────────────────────────────────
print(f"\n{'='*60}")
print(f"ABLATING MODE 1 (universal vocabulary, {comp1_var:.1f}% variance)")
print(f"{'='*60}")

# Reconstruct without component 1
# centered = U @ diag(S) @ Vt
# ablated = U[:,1:] @ diag(S[1:]) @ Vt[1:,:] + row_means
S_ablated = S.copy()
S_ablated[0] = 0.0  # zero out mode 1

reconstructed_centered = U @ np.diag(S_ablated) @ Vt
reconstructed = reconstructed_centered + row_means

# The ablated connectivity matrix
ablated_connectivity = reconstructed.copy()

# ── Compare: what GAINS connectivity? ──────────────────────────────────────────
# delta = ablated - original.  Positive delta = gained connectivity after ablation.
# But this needs interpretation: removing universal vocabulary might shift baselines.
# We care about RELATIVE ranking changes.

delta = ablated_connectivity - connectivity

# For each module pair, compute gain
gains = []
for i in range(n):
    for j in range(i + 1, n):
        gains.append({
            "module_a": modules[i],
            "module_b": modules[j],
            "original_connectivity": float(connectivity[i, j]),
            "ablated_connectivity": float(ablated_connectivity[i, j]),
            "delta": float(delta[i, j]),
            "original_distance": float(raw_matrix[i, j]),
        })

gains.sort(key=lambda x: -x["delta"])

print(f"\n=== Top 30 Module Pairs GAINING Connectivity After Mode 1 Ablation ===")
print(f"{'Module A':30s} {'Module B':30s} {'Orig':>8s} {'Ablated':>8s} {'Delta':>8s}")
for g in gains[:30]:
    print(f"{g['module_a']:30s} {g['module_b']:30s} "
          f"{g['original_connectivity']:8.4f} {g['ablated_connectivity']:8.4f} "
          f"{g['delta']:+8.4f}")

print(f"\n=== Top 30 Module Pairs LOSING Connectivity After Mode 1 Ablation ===")
for g in gains[-30:]:
    print(f"{g['module_a']:30s} {g['module_b']:30s} "
          f"{g['original_connectivity']:8.4f} {g['ablated_connectivity']:8.4f} "
          f"{g['delta']:+8.4f}")

# ── Identify Mode 2 load-bearing symbols ──────────────────────────────────────
# After ablation, Mode 2 becomes the dominant component.
# Which symbols drive Mode 2 connectivity?

# Use the cross_domain_bridges from operadic data to map symbols to module pairs
bridges = operadic["cross_domain_bridges"]

# Also use conserved patterns
conserved = operadic["conserved_patterns"]
universal_ops = set(conserved["universal_operators"])  # Equal, For, And, Set
bridge_fns = conserved["bridge_functions"]

# Build symbol-to-module mapping from bridges
symbol_module_map = {}  # symbol -> set of modules it appears in
for b in bridges:
    for sym in b["symbols_a"]:
        symbol_module_map.setdefault(sym, set()).add(b["module_a"])
    for sym in b["symbols_b"]:
        symbol_module_map.setdefault(sym, set()).add(b["module_b"])

# Enrich with bridge cargo from gamma data
bridge_cargo = gamma["companion_analysis"]["bridge_cargo"]
for cargo in bridge_cargo:
    ma, mb = cargo["module_a"], cargo["module_b"]
    for sym in cargo["shared_companions"]:
        symbol_module_map.setdefault(sym, set()).add(ma)
        symbol_module_map.setdefault(sym, set()).add(mb)

# Universal companions from gamma data
universal_companions = gamma["companion_analysis"]["universal_companions"]

# ── Compute symbol centrality in the ablated network ───────────────────────────
# For each symbol, compute its "centrality gain" = sum of delta for module pairs
# where the symbol co-occurs.

# We need per-module symbol sets. Extract from the full bridge data.
# Use bridge_fns + cargo to build richer symbol-module mapping.

# For each symbol, compute:
# 1) which modules it connects
# 2) sum of delta for those module pairs
# 3) classify as "universal" (Mode 1) vs "domain-specific" (Mode 2+)

symbol_delta_scores = {}
symbol_pair_count = {}

for sym, mods in symbol_module_map.items():
    mods_list = sorted(mods)
    total_delta = 0.0
    pair_count = 0
    for ii in range(len(mods_list)):
        for jj in range(ii + 1, len(mods_list)):
            ma, mb = mods_list[ii], mods_list[jj]
            if ma in mod_idx and mb in mod_idx:
                ia, ib = mod_idx[ma], mod_idx[mb]
                total_delta += delta[ia, ib]
                pair_count += 1
    if pair_count > 0:
        symbol_delta_scores[sym] = total_delta / pair_count
        symbol_pair_count[sym] = pair_count

# Sort symbols by centrality gain after ablation
symbol_gain_ranking = sorted(symbol_delta_scores.items(), key=lambda x: -x[1])

print(f"\n=== Symbols GAINING Centrality After Mode 1 Ablation ===")
print(f"(These become load-bearing when universal vocabulary is removed)")
print(f"{'Symbol':35s} {'Avg Delta':>8s} {'#Pairs':>8s} {'Universal?':>10s}")
for sym, avg_d in symbol_gain_ranking[:30]:
    is_univ = sym in universal_ops or sym in universal_companions
    print(f"{sym:35s} {avg_d:+8.4f} {symbol_pair_count[sym]:8d} "
          f"{'YES' if is_univ else 'no':>10s}")

print(f"\n=== Symbols LOSING Centrality After Mode 1 Ablation ===")
for sym, avg_d in symbol_gain_ranking[-20:]:
    is_univ = sym in universal_ops or sym in universal_companions
    print(f"{sym:35s} {avg_d:+8.4f} {symbol_pair_count[sym]:8d} "
          f"{'YES' if is_univ else 'no':>10s}")

# ── Mode 2 load-bearing analysis ──────────────────────────────────────────────
# After ablating Mode 1, Mode 2 IS the dominant structure.
# The symbols that gain centrality in module pairs with high Mode 2 loading
# are the load-bearing operators of the NT<->algebra axis.

# Compute Mode 2 projection strength for each module pair
mode2_strength = {}
for i in range(n):
    for j in range(i + 1, n):
        # Mode 2 contribution = outer product of Mode 2 loadings * S[1]
        strength = abs(loadings_2[i] * loadings_2[j]) * S[1]
        key = (modules[i], modules[j])
        mode2_strength[key] = strength

# For each gaining symbol, compute its overlap with Mode 2
symbol_mode2_load = {}
for sym, mods in symbol_module_map.items():
    mods_list = sorted(mods)
    total_mode2 = 0.0
    count = 0
    for ii in range(len(mods_list)):
        for jj in range(ii + 1, len(mods_list)):
            key = (mods_list[ii], mods_list[jj])
            rev_key = (mods_list[jj], mods_list[ii])
            if key in mode2_strength:
                total_mode2 += mode2_strength[key]
                count += 1
            elif rev_key in mode2_strength:
                total_mode2 += mode2_strength[rev_key]
                count += 1
    if count > 0:
        symbol_mode2_load[sym] = total_mode2 / count

# Combined score: symbols that both GAIN centrality AND load on Mode 2
combined_scores = {}
for sym in symbol_delta_scores:
    if sym in symbol_mode2_load:
        # Normalize both to [0,1] range
        gain = symbol_delta_scores[sym]
        mode2 = symbol_mode2_load[sym]
        combined_scores[sym] = gain * mode2  # product favors both high

combined_ranking = sorted(combined_scores.items(), key=lambda x: -x[1])

print(f"\n{'='*60}")
print(f"MODE 2 LOAD-BEARING SYMBOLS (after Mode 1 ablation)")
print(f"Symbols that gain centrality AND load on NT<->algebra axis")
print(f"{'='*60}")
print(f"{'Symbol':35s} {'Gain':>8s} {'Mode2':>8s} {'Combined':>10s}")
for sym, score in combined_ranking[:25]:
    gain = symbol_delta_scores[sym]
    mode2 = symbol_mode2_load[sym]
    is_univ = sym in universal_ops
    marker = " [UNIV]" if is_univ else ""
    print(f"{sym:35s} {gain:+8.4f} {mode2:8.4f} {score:10.6f}{marker}")

# ── Module centrality shift analysis ──────────────────────────────────────────
# Compute degree centrality in original vs ablated network

threshold_orig = np.percentile(connectivity[connectivity > 0], 75)
threshold_ablated = np.percentile(ablated_connectivity[ablated_connectivity > 0], 75)

orig_degree = {}
ablated_degree = {}
for i in range(n):
    orig_deg = sum(1 for j in range(n) if j != i and connectivity[i, j] > threshold_orig)
    abl_deg = sum(1 for j in range(n) if j != i and ablated_connectivity[i, j] > threshold_ablated)
    orig_degree[modules[i]] = orig_deg
    ablated_degree[modules[i]] = abl_deg

degree_delta = {m: ablated_degree[m] - orig_degree[m] for m in modules}
degree_ranking = sorted(degree_delta.items(), key=lambda x: -x[1])

print(f"\n=== Module Degree Centrality Shift ===")
print(f"{'Module':35s} {'Orig Deg':>10s} {'Ablated Deg':>12s} {'Delta':>8s}")
for m, dd in degree_ranking[:15]:
    print(f"{m:35s} {orig_degree[m]:10d} {ablated_degree[m]:12d} {dd:+8d}")
print(f"  ...")
for m, dd in degree_ranking[-10:]:
    print(f"{m:35s} {orig_degree[m]:10d} {ablated_degree[m]:12d} {dd:+8d}")

# ── Build results ──────────────────────────────────────────────────────────────
results = {
    "meta": {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "n_modules": n,
        "method": "SVD on connectivity matrix (1 - distance), ablate component 1",
        "source_files": [
            "operadic_dynamics_results.json",
            "gamma_wormhole_results.json"
        ]
    },
    "svd_components": {
        "explained_variance_pct": [float(e * 100) for e in explained[:10]],
        "cumulative_variance_pct": [float(c * 100) for c in cumulative[:10]],
        "mode1_variance_pct": float(comp1_var),
        "mode2_variance_pct": float(comp2_var),
        "mode3_variance_pct": float(comp3_var),
    },
    "mode1_top_modules": [
        {"module": modules[i], "loading": float(loadings_1[i])}
        for i in mode1_order[:20]
    ],
    "mode2_top_modules": [
        {"module": modules[i], "loading": float(loadings_2[i])}
        for i in mode2_order[:20]
    ],
    "mode2_positive_pole": [{"module": m, "loading": float(l)} for m, l in pos_pole[:10]],
    "mode2_negative_pole": [{"module": m, "loading": float(l)} for m, l in neg_pole[:10]],
    "mode3_top_modules": [
        {"module": modules[i], "loading": float(loadings_3[i])}
        for i in mode3_order[:20]
    ],
    "ablation_gains_top30": gains[:30],
    "ablation_losses_top30": gains[-30:],
    "mode2_loadbearing_symbols": [
        {
            "symbol": sym,
            "centrality_gain": float(symbol_delta_scores[sym]),
            "mode2_load": float(symbol_mode2_load.get(sym, 0)),
            "combined_score": float(score),
            "n_module_pairs": int(symbol_pair_count.get(sym, 0)),
            "is_universal_operator": sym in universal_ops,
            "is_universal_companion": sym in universal_companions,
        }
        for sym, score in combined_ranking[:30]
    ],
    "symbol_centrality_gainers": [
        {
            "symbol": sym,
            "avg_delta": float(avg_d),
            "n_pairs": int(symbol_pair_count[sym]),
            "is_universal": sym in universal_ops or sym in universal_companions,
        }
        for sym, avg_d in symbol_gain_ranking[:30]
    ],
    "symbol_centrality_losers": [
        {
            "symbol": sym,
            "avg_delta": float(avg_d),
            "n_pairs": int(symbol_pair_count[sym]),
            "is_universal": sym in universal_ops or sym in universal_companions,
        }
        for sym, avg_d in symbol_gain_ranking[-20:]
    ],
    "module_degree_shift": [
        {
            "module": m,
            "original_degree": int(orig_degree[m]),
            "ablated_degree": int(ablated_degree[m]),
            "delta": int(dd),
        }
        for m, dd in degree_ranking
    ],
}

out_path = HERE / "rosetta_mode1_ablation_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path}")
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Mode 1 captured {comp1_var:.1f}% of variance (universal vocabulary)")
print(f"Mode 2 captured {comp2_var:.1f}% of variance (NT<->algebra axis)")
print(f"Mode 3 captured {comp3_var:.1f}% of variance (continuous<->discrete)")
print(f"Top gaining pair after ablation: "
      f"{gains[0]['module_a']} <-> {gains[0]['module_b']} (Delta={gains[0]['delta']:+.4f})")
print(f"Top Mode 2 load-bearing symbol: {combined_ranking[0][0]} "
      f"(combined={combined_ranking[0][1]:.6f})")
n_gaining = sum(1 for g in gains if g["delta"] > 0)
print(f"Module pairs gaining connectivity: {n_gaining}/{len(gains)}")
