"""
M29: Gamma metric prediction — removal experiment
=====================================================
Remove Gamma from the Fungrim distance matrix and measure how much
inter-module distances increase. If Gamma is a genuine hub, removing it
should increase mean distance significantly. If it's just one of many
paths, removal should have minimal effect.

Also: remove each module in turn, compute the mean distance increase.
Rank modules by their "removal impact" — this is the indispensability score.
"""
import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
GAMMA = V2 / "gamma_wormhole_results.json"
OUT = V2 / "m29_gamma_removal_results.json"

def floyd_warshall(D):
    n = D.shape[0]
    fw = D.copy()
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if fw[i][k] + fw[k][j] < fw[i][j]:
                    fw[i][j] = fw[i][k] + fw[k][j]
    return fw

def mean_distance(fw, exclude=None):
    n = fw.shape[0]
    total = 0; count = 0
    for i in range(n):
        if i == exclude: continue
        for j in range(i+1, n):
            if j == exclude: continue
            total += fw[i][j]; count += 1
    return total / count if count > 0 else 0

def main():
    t0 = time.time()
    print("=== M29: Gamma metric prediction — removal experiment ===\n")
    with open(GAMMA) as f:
        data = json.load(f)

    matrix = data["gamma_distance_matrix"]
    modules = matrix["modules"]
    dists = matrix["distances"]
    n = len(modules)
    mod_idx = {m: i for i, m in enumerate(modules)}

    D = np.zeros((n, n))
    for i, mi in enumerate(modules):
        for j, mj in enumerate(modules):
            D[i, j] = dists[mi][mj]

    # Baseline: Floyd-Warshall on full graph
    fw_full = floyd_warshall(D)
    baseline_mean = mean_distance(fw_full)
    print(f"  Baseline mean geodesic distance: {baseline_mean:.6f}")

    # Remove each module and measure impact
    print("\n  Module removal impact analysis...")
    removal_impacts = {}
    for k, mod in enumerate(modules):
        # Create reduced matrix
        idx = list(range(n))
        idx.remove(k)
        D_reduced = D[np.ix_(idx, idx)]
        fw_reduced = floyd_warshall(D_reduced)
        reduced_mean = mean_distance(fw_reduced)
        impact = (reduced_mean - baseline_mean) / baseline_mean
        removal_impacts[mod] = {
            "mean_distance_after_removal": round(float(reduced_mean), 6),
            "absolute_increase": round(float(reduced_mean - baseline_mean), 6),
            "relative_increase": round(float(impact), 6),
        }

    # Sort by impact
    sorted_impacts = sorted(removal_impacts.items(), key=lambda x: -x[1]["relative_increase"])
    print("\n  Ranked by removal impact (indispensability):")
    for mod, imp in sorted_impacts:
        tag = " ← GAMMA" if mod == "gamma" else ""
        print(f"    {mod}: Δ={imp['relative_increase']:.4%}{tag}")

    # Gamma-specific
    gamma_impact = removal_impacts.get("gamma", {})
    gamma_rank = next((i+1 for i, (m, _) in enumerate(sorted_impacts) if m == "gamma"), n)
    top_module = sorted_impacts[0][0] if sorted_impacts else "?"
    top_impact = sorted_impacts[0][1]["relative_increase"] if sorted_impacts else 0

    # Diameter analysis
    fw_diameter = float(fw_full.max())
    print(f"\n  Full graph diameter: {fw_diameter:.4f}")

    elapsed = time.time() - t0
    output = {
        "probe": "M29", "title": "Gamma metric prediction — removal",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_modules": n,
        "baseline_mean_distance": round(baseline_mean, 6),
        "graph_diameter": round(fw_diameter, 6),
        "removal_impacts": {m: v for m, v in sorted_impacts},
        "gamma_specific": {
            "rank": gamma_rank,
            "impact": gamma_impact,
        },
        "most_indispensable": top_module,
        "most_indispensable_impact": round(top_impact, 6),
        "assessment": None,
    }

    if gamma_rank == 1:
        output["assessment"] = f"GAMMA IS MOST INDISPENSABLE: removing it increases mean distance by {gamma_impact.get('relative_increase', 0):.2%} — maximum of all modules"
    elif gamma_rank <= 3:
        output["assessment"] = f"GAMMA IS TOP-{gamma_rank}: impact={gamma_impact.get('relative_increase', 0):.2%}. Most indispensable is {top_module} ({top_impact:.2%})"
    else:
        output["assessment"] = f"GAMMA IS RANK-{gamma_rank}/{n}: impact={gamma_impact.get('relative_increase', 0):.2%}. Gamma is NOT structurally special — {top_module} matters more"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
