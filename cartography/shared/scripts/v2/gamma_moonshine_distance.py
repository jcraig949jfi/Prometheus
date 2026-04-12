"""
ALL-054: Gamma Moonshine→NT Distance
=====================================
Compute Gamma-path geodesic distance from moonshine-adjacent Fungrim modules
to number-theory modules. Question: how far is moonshine from NT through the
Gamma wormhole?

Uses the Gamma distance matrix from gamma_wormhole_results.json.
Moonshine modules: dedekind_eta, eisenstein, jacobi_theta
NT modules: riemann_zeta, dirichlet, hurwitz_zeta
"""

import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
GAMMA_RESULTS = V2 / "gamma_wormhole_results.json"
OUT_PATH = V2 / "gamma_moonshine_distance_results.json"

MOONSHINE_MODULES = {"dedekind_eta", "eisenstein", "jacobi_theta"}
NT_MODULES = {"riemann_zeta", "dirichlet", "hurwitz_zeta"}
ANALYSIS_MODULES = {"gamma", "beta_function", "gauss_hypergeometric",
                    "confluent_hypergeometric", "bessel", "airy"}

def main():
    t0 = time.time()
    print("=== ALL-054: Gamma Moonshine→NT Distance ===\n")

    with open(GAMMA_RESULTS) as f:
        data = json.load(f)

    matrix_data = data["gamma_distance_matrix"]
    modules = matrix_data["modules"]
    dists = matrix_data["distances"]

    print(f"  Modules in Gamma matrix: {len(modules)}")
    moon_present = MOONSHINE_MODULES & set(modules)
    nt_present = NT_MODULES & set(modules)
    print(f"  Moonshine modules present: {sorted(moon_present)}")
    print(f"  NT modules present: {sorted(nt_present)}")

    # Direct distances: moonshine <-> NT
    direct = []
    for m in sorted(moon_present):
        for n in sorted(nt_present):
            d = dists[m][n]
            direct.append({"from": m, "to": n, "distance": d})
            print(f"    {m} → {n}: {d:.4f}")

    # Geodesic via Dijkstra on the full matrix
    print("\n  Computing shortest Gamma-geodesic paths...")
    n = len(modules)
    mod_idx = {m: i for i, m in enumerate(modules)}
    dist_matrix = np.ones((n, n))
    for i, ma in enumerate(modules):
        for j, mb in enumerate(modules):
            dist_matrix[i, j] = dists[ma][mb]

    # Floyd-Warshall for all-pairs shortest paths
    fw = dist_matrix.copy()
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if fw[i][k] + fw[k][j] < fw[i][j]:
                    fw[i][j] = fw[i][k] + fw[k][j]

    geodesic_results = []
    for m in sorted(moon_present):
        for nt in sorted(nt_present):
            i, j = mod_idx[m], mod_idx[nt]
            geo_d = fw[i][j]
            direct_d = dist_matrix[i][j]
            # Find the relay module
            best_relay = None
            best_relay_d = direct_d
            for k in range(n):
                if k == i or k == j:
                    continue
                via_d = dist_matrix[i][k] + dist_matrix[k][j]
                if via_d < best_relay_d:
                    best_relay_d = via_d
                    best_relay = modules[k]
            geodesic_results.append({
                "from": m, "to": nt,
                "direct_distance": round(direct_d, 6),
                "geodesic_distance": round(float(geo_d), 6),
                "shortcut_ratio": round(float(geo_d / direct_d), 4) if direct_d > 0 else 1.0,
                "best_relay": best_relay,
                "relay_distance": round(best_relay_d, 6) if best_relay else None,
            })
            print(f"    {m}→{nt}: direct={direct_d:.4f} geodesic={geo_d:.4f} "
                  f"relay={best_relay} ratio={geo_d/direct_d:.3f}" if direct_d > 0 else "")

    # Module centrality in Gamma space
    print("\n  Module centrality (mean distance to all others)...")
    centrality = {}
    for i, m in enumerate(modules):
        mean_d = float(np.mean([fw[i][j] for j in range(n) if j != i]))
        centrality[m] = round(mean_d, 6)
    for m in sorted(centrality, key=centrality.get):
        tag = " [MOON]" if m in MOONSHINE_MODULES else (" [NT]" if m in NT_MODULES else "")
        print(f"    {m}: {centrality[m]:.4f}{tag}")

    # Moonshine cluster coherence vs NT cluster coherence
    moon_list = sorted(moon_present)
    nt_list = sorted(nt_present)
    moon_intra = [dists[a][b] for a in moon_list for b in moon_list if a != b] if len(moon_list) > 1 else []
    nt_intra = [dists[a][b] for a in nt_list for b in nt_list if a != b] if len(nt_list) > 1 else []
    cross = [dists[a][b] for a in moon_list for b in nt_list]

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-054",
        "title": "Gamma Moonshine→NT Distance",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "modules_in_matrix": len(modules),
        "moonshine_modules": sorted(moon_present),
        "nt_modules": sorted(nt_present),
        "direct_distances": direct,
        "geodesic_paths": geodesic_results,
        "module_centrality": centrality,
        "cluster_coherence": {
            "moonshine_intra_mean": round(float(np.mean(moon_intra)), 4) if moon_intra else None,
            "nt_intra_mean": round(float(np.mean(nt_intra)), 4) if nt_intra else None,
            "cross_mean": round(float(np.mean(cross)), 4) if cross else None,
            "separation_ratio": round(float(np.mean(cross)) / float(np.mean(moon_intra + nt_intra)), 3) if (moon_intra or nt_intra) and cross else None,
        },
        "assessment": None,
    }

    # Assessment
    if cross:
        cross_mean = np.mean(cross)
        intra_mean = np.mean(moon_intra + nt_intra) if (moon_intra or nt_intra) else cross_mean
        if cross_mean < intra_mean * 1.1:
            output["assessment"] = f"CLOSE: moonshine↔NT cross-distance ({cross_mean:.3f}) ≈ intra-cluster ({intra_mean:.3f}) — Gamma connects them"
        elif cross_mean < 0.85:
            output["assessment"] = f"MODERATE: cross-distance={cross_mean:.3f}, below Gamma random baseline (0.88)"
        else:
            output["assessment"] = f"DISTANT: cross-distance={cross_mean:.3f}, near random baseline — Gamma does NOT shortcut moonshine→NT"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
