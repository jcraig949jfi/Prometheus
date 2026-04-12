"""
M37: Gamma curvature (discrete Ollivier-Ricci)
=================================================
Compute discrete Ollivier-Ricci curvature on the Fungrim module graph.
Positive curvature = cluster-like. Negative = tree-like / bottleneck.
Which edges are positively curved? Which are negatively curved?
Does Gamma sit on a negatively-curved bottleneck edge?
"""
import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
GAMMA = V2 / "gamma_wormhole_results.json"
OUT = V2 / "m37_gamma_curvature_results.json"

def ollivier_ricci(W, i, j):
    """Approximate Ollivier-Ricci curvature κ(i,j) via Wasserstein-1."""
    n = W.shape[0]
    # Probability distributions: uniform over neighbors
    di = W[i].copy(); di[i] = 0
    s = di.sum()
    if s > 0: di /= s
    else: return 0.0

    dj = W[j].copy(); dj[j] = 0
    s = dj.sum()
    if s > 0: dj /= s
    else: return 0.0

    # W1 distance approximation: use L1 of distributions
    # (exact W1 needs LP, but L1 gives lower bound)
    w1 = float(np.sum(np.abs(di - dj)))
    d_ij = 1.0 / W[i, j] if W[i, j] > 0 else 1.0
    kappa = 1.0 - w1 / (2.0)  # Simplified: κ ≈ 1 - W1/d
    return float(kappa)

def main():
    t0 = time.time()
    print("=== M37: Gamma curvature (discrete Ollivier-Ricci) ===\n")

    with open(GAMMA) as f:
        data = json.load(f)

    matrix = data["gamma_distance_matrix"]
    modules = matrix["modules"]
    dists = matrix["distances"]
    n = len(modules)

    # Build weight matrix (closer = stronger connection)
    D = np.zeros((n, n))
    W = np.zeros((n, n))
    for i, mi in enumerate(modules):
        for j, mj in enumerate(modules):
            D[i, j] = dists[mi][mj]
            if i != j and D[i, j] > 0:
                W[i, j] = 1.0 / D[i, j]

    # Compute curvature for all edges
    print("  Computing Ollivier-Ricci curvature for all module pairs...")
    curvatures = []
    for i in range(n):
        for j in range(i + 1, n):
            if W[i, j] < 0.01:  # Skip very weak edges
                continue
            kappa = ollivier_ricci(W, i, j)
            curvatures.append({
                "from": modules[i], "to": modules[j],
                "curvature": round(kappa, 6),
                "distance": round(D[i, j], 6),
                "weight": round(W[i, j], 4),
            })

    curvatures.sort(key=lambda x: x["curvature"])
    print(f"  {len(curvatures)} edges computed")

    # Most negatively curved (bottleneck edges)
    print("\n  Most NEGATIVELY curved edges (bottlenecks):")
    for c in curvatures[:10]:
        print(f"    {c['from']}↔{c['to']}: κ={c['curvature']:.4f}")

    # Most positively curved (cluster edges)
    print("\n  Most POSITIVELY curved edges (clusters):")
    for c in curvatures[-10:]:
        print(f"    {c['from']}↔{c['to']}: κ={c['curvature']:.4f}")

    # Per-module mean curvature
    mod_curv = {}
    for m in modules:
        edges = [c for c in curvatures if c["from"] == m or c["to"] == m]
        if edges:
            mod_curv[m] = round(float(np.mean([c["curvature"] for c in edges])), 6)
    sorted_mc = sorted(mod_curv.items(), key=lambda x: x[1])

    print("\n  Per-module mean curvature:")
    for m, k in sorted_mc:
        tag = " ← GAMMA" if m == "gamma" else (" ← PI" if m == "pi" else "")
        print(f"    {m}: κ_mean={k:.4f}{tag}")

    # Gamma-specific
    gamma_curv = mod_curv.get("gamma")
    pi_curv = mod_curv.get("pi")
    gamma_rank = next((i+1 for i, (m, _) in enumerate(sorted_mc) if m == "gamma"), n)

    # Global statistics
    all_k = [c["curvature"] for c in curvatures]
    global_mean = float(np.mean(all_k))
    global_std = float(np.std(all_k))
    n_positive = sum(1 for k in all_k if k > 0)
    n_negative = sum(1 for k in all_k if k < 0)

    print(f"\n  Global: mean κ={global_mean:.4f}, std={global_std:.4f}")
    print(f"  Positive: {n_positive}, Negative: {n_negative}, Zero: {len(all_k)-n_positive-n_negative}")

    elapsed = time.time() - t0
    output = {
        "probe": "M37", "title": "Gamma curvature (Ollivier-Ricci)",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_modules": n,
        "n_edges_computed": len(curvatures),
        "global_curvature": {"mean": round(global_mean, 6), "std": round(global_std, 6),
                            "n_positive": n_positive, "n_negative": n_negative},
        "most_negative": curvatures[:10],
        "most_positive": curvatures[-10:],
        "per_module_curvature": dict(sorted_mc),
        "gamma_curvature": gamma_curv,
        "gamma_rank": gamma_rank,
        "pi_curvature": pi_curv,
        "assessment": None,
    }

    if gamma_curv is not None and gamma_curv < global_mean - global_std:
        output["assessment"] = f"GAMMA IS BOTTLENECK: κ_gamma={gamma_curv:.4f} < mean-σ ({global_mean-global_std:.4f}). Negative curvature = tree-like, NOT cluster hub"
    elif gamma_curv is not None and gamma_curv > global_mean + global_std:
        output["assessment"] = f"GAMMA IS CLUSTER: κ_gamma={gamma_curv:.4f} > mean+σ. Positive curvature = well-connected cluster"
    elif gamma_curv is not None:
        output["assessment"] = f"GAMMA IS AVERAGE: κ_gamma={gamma_curv:.4f} ≈ mean ({global_mean:.4f}). No special geometric role. Rank {gamma_rank}/{n}"
    else:
        output["assessment"] = "GAMMA MODULE NOT FOUND in distance matrix"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
