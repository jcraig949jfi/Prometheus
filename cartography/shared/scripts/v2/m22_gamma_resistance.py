"""
M22: Network resistance of Γ hub
===================================
Treat the Gamma wormhole distance matrix as a weighted graph.
Compute the effective resistance (commute time) between key module pairs.
Identify bottleneck edges. Compare resistance to geodesic distance.
Is Γ a bottleneck or a superhighway?
"""
import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
GAMMA = V2 / "gamma_wormhole_results.json"
OUT = V2 / "m22_gamma_resistance_results.json"

def effective_resistance(L_pinv, i, j):
    """Effective resistance between i,j from pseudoinverse of Laplacian."""
    return float(L_pinv[i, i] + L_pinv[j, j] - 2 * L_pinv[i, j])

def main():
    t0 = time.time()
    print("=== M22: Network resistance of Γ hub ===\n")
    with open(GAMMA) as f:
        data = json.load(f)

    matrix = data["gamma_distance_matrix"]
    modules = matrix["modules"]
    dists = matrix["distances"]
    n = len(modules)
    print(f"  {n} modules in Gamma distance matrix")

    # Build distance matrix
    D = np.zeros((n, n))
    for i, mi in enumerate(modules):
        for j, mj in enumerate(modules):
            D[i, j] = dists[mi][mj]

    # Build weight matrix W = 1/D (with diagonal = 0)
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j and D[i, j] > 0:
                W[i, j] = 1.0 / D[i, j]

    # Laplacian L = diag(W*1) - W
    deg = W.sum(axis=1)
    L = np.diag(deg) - W

    # Pseudoinverse of Laplacian
    L_pinv = np.linalg.pinv(L)

    # Compute effective resistance for all pairs
    print("\n  Computing effective resistance for all pairs...")
    resist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            resist[i, j] = effective_resistance(L_pinv, i, j)

    # Key pairs: moonshine <-> NT
    MOON = {"dedekind_eta", "eisenstein", "jacobi_theta"}
    NT = {"riemann_zeta", "dirichlet", "hurwitz_zeta"}
    ANALYSIS = {"gamma", "beta_function", "gauss_hypergeometric"}
    mod_idx = {m: i for i, m in enumerate(modules)}

    print("\n  Key resistances:")
    key_pairs = []
    for m in sorted(MOON & set(modules)):
        for nt in sorted(NT & set(modules)):
            i, j = mod_idx[m], mod_idx[nt]
            r = resist[i, j]
            d = D[i, j]
            ratio = r / d if d > 0 else 0
            key_pairs.append({"from": m, "to": nt, "resistance": round(r, 6),
                             "distance": round(d, 6), "R_over_D": round(ratio, 4)})
            print(f"    {m}→{nt}: R={r:.4f} D={d:.4f} R/D={ratio:.3f}")

    # Gamma hub centrality by resistance
    print("\n  Hub resistance centrality (mean R to all others):")
    centrality = {}
    for i, m in enumerate(modules):
        mean_r = float(np.mean([resist[i, j] for j in range(n) if j != i]))
        centrality[m] = round(mean_r, 6)
    for m in sorted(centrality, key=centrality.get):
        tag = " [MOON]" if m in MOON else (" [NT]" if m in NT else (" [γ]" if m in ANALYSIS else ""))
        print(f"    {m}: R_mean={centrality[m]:.4f}{tag}")

    # Bottleneck: edge with highest betweenness (approximated by resistance ratio)
    print("\n  Bottleneck analysis:")
    max_r = 0; bottleneck = None
    for i in range(n):
        for j in range(i+1, n):
            if resist[i, j] > max_r:
                max_r = resist[i, j]
                bottleneck = (modules[i], modules[j])
    if bottleneck:
        print(f"    Max resistance: {bottleneck[0]}↔{bottleneck[1]} R={max_r:.4f}")

    # Total network resistance (Kirchhoff index)
    kirchhoff = float(np.sum(resist) / 2)
    print(f"\n  Kirchhoff index (total resistance): {kirchhoff:.2f}")

    # Is Gamma superhighway or bottleneck?
    gamma_idx = mod_idx.get("gamma")
    if gamma_idx is not None:
        gamma_centrality = centrality["gamma"]
        mean_centrality = float(np.mean(list(centrality.values())))
        gamma_ratio = gamma_centrality / mean_centrality
        print(f"  Gamma centrality ratio: {gamma_ratio:.3f} (< 1 = hub, > 1 = bottleneck)")

    elapsed = time.time() - t0
    output = {
        "probe": "M22", "title": "Network resistance of Γ hub",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_modules": n,
        "key_pair_resistances": key_pairs,
        "resistance_centrality": centrality,
        "bottleneck": {"pair": list(bottleneck) if bottleneck else None, "resistance": round(max_r, 6)},
        "kirchhoff_index": round(kirchhoff, 2),
        "gamma_centrality_ratio": round(gamma_ratio, 4) if gamma_idx is not None else None,
        "assessment": None,
    }

    if gamma_idx is not None and gamma_ratio < 0.8:
        output["assessment"] = f"SUPERHIGHWAY: Gamma has centrality ratio {gamma_ratio:.3f} — it is a hub, NOT a bottleneck"
    elif gamma_idx is not None and gamma_ratio < 1.0:
        output["assessment"] = f"MODERATE HUB: Gamma centrality ratio {gamma_ratio:.3f} — slightly better than average"
    else:
        output["assessment"] = f"BOTTLENECK: Gamma centrality ratio {gamma_ratio:.3f} — Gamma is NOT a special hub"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
