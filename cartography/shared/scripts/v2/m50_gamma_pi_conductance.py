"""
M50: Gamma-Pi wormhole conductance
=====================================
Given that pi (not Gamma) is the true hub (M22/M29), compute the
effective conductance of the Gamma↔Pi edge specifically.
Is this edge a high-conductance superhighway or a narrow bridge?

Also: compute the Fiedler vector (second eigenvector of Laplacian) to
find the natural graph bisection. Does the cut separate moonshine from NT?
"""
import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
GAMMA = V2 / "gamma_wormhole_results.json"
OUT = V2 / "m50_gamma_pi_conductance_results.json"

def main():
    t0 = time.time()
    print("=== M50: Gamma-Pi wormhole conductance ===\n")

    with open(GAMMA) as f:
        data = json.load(f)

    matrix = data["gamma_distance_matrix"]
    modules = matrix["modules"]
    dists = matrix["distances"]
    n = len(modules)
    mod_idx = {m: i for i, m in enumerate(modules)}

    D = np.zeros((n, n))
    W = np.zeros((n, n))
    for i, mi in enumerate(modules):
        for j, mj in enumerate(modules):
            D[i, j] = dists[mi][mj]
            if i != j and D[i, j] > 0:
                W[i, j] = 1.0 / D[i, j]

    # Laplacian
    deg = W.sum(axis=1)
    L = np.diag(deg) - W

    # Fiedler vector (second smallest eigenvalue)
    print("[1] Computing Fiedler vector...")
    eigvals, eigvecs = np.linalg.eigh(L)
    fiedler_val = float(eigvals[1])
    fiedler_vec = eigvecs[:, 1]

    # Natural bisection: sign of Fiedler vector
    partition_A = [modules[i] for i in range(n) if fiedler_vec[i] >= 0]
    partition_B = [modules[i] for i in range(n) if fiedler_vec[i] < 0]

    MOON = {"dedekind_eta", "eisenstein", "jacobi_theta"}
    NT = {"riemann_zeta", "dirichlet", "hurwitz_zeta"}

    moon_in_A = MOON & set(partition_A)
    moon_in_B = MOON & set(partition_B)
    nt_in_A = NT & set(partition_A)
    nt_in_B = NT & set(partition_B)

    print(f"  Fiedler eigenvalue (algebraic connectivity): {fiedler_val:.6f}")
    print(f"  Partition A ({len(partition_A)}): {sorted(partition_A)}")
    print(f"  Partition B ({len(partition_B)}): {sorted(partition_B)}")
    print(f"  Moonshine: {len(moon_in_A)} in A, {len(moon_in_B)} in B")
    print(f"  NT: {len(nt_in_A)} in A, {len(nt_in_B)} in B")

    # Does the bisection separate moonshine from NT?
    moon_separated = (len(moon_in_A) == len(MOON & set(modules)) and len(nt_in_B) == len(NT & set(modules))) or \
                     (len(moon_in_B) == len(MOON & set(modules)) and len(nt_in_A) == len(NT & set(modules)))

    # Gamma-Pi conductance
    gi = mod_idx.get("gamma")
    pi_i = mod_idx.get("pi")
    if gi is not None and pi_i is not None:
        gamma_pi_weight = W[gi, pi_i]
        gamma_pi_dist = D[gi, pi_i]
        # Effective conductance via pseudoinverse of L
        L_pinv = np.linalg.pinv(L)
        eff_resist = float(L_pinv[gi, gi] + L_pinv[pi_i, pi_i] - 2 * L_pinv[gi, pi_i])
        eff_cond = 1.0 / eff_resist if eff_resist > 0 else float('inf')

        # Compare to mean edge conductance
        all_resistances = []
        for i in range(n):
            for j in range(i+1, n):
                r = float(L_pinv[i, i] + L_pinv[j, j] - 2 * L_pinv[i, j])
                all_resistances.append(r)
        mean_resist = float(np.mean(all_resistances))
        mean_cond = 1.0 / mean_resist if mean_resist > 0 else 0

        cond_ratio = eff_cond / mean_cond if mean_cond > 0 else 0

        print(f"\n[2] Gamma↔Pi edge:")
        print(f"  Distance: {gamma_pi_dist:.4f}")
        print(f"  Direct weight: {gamma_pi_weight:.4f}")
        print(f"  Effective resistance: {eff_resist:.6f}")
        print(f"  Effective conductance: {eff_cond:.2f}")
        print(f"  Mean conductance: {mean_cond:.2f}")
        print(f"  Conductance ratio: {cond_ratio:.3f}")
    else:
        eff_cond = 0; cond_ratio = 0; eff_resist = 0; gamma_pi_dist = 0

    # Cheeger constant (edge expansion)
    cut_weight = sum(W[i, j] for i in range(n) if fiedler_vec[i] >= 0
                     for j in range(n) if fiedler_vec[j] < 0)
    vol_A = sum(deg[i] for i in range(n) if fiedler_vec[i] >= 0)
    vol_B = sum(deg[i] for i in range(n) if fiedler_vec[i] < 0)
    cheeger = float(cut_weight / min(vol_A, vol_B)) if min(vol_A, vol_B) > 0 else 0
    print(f"\n  Cheeger constant (edge expansion): {cheeger:.4f}")

    elapsed = time.time() - t0
    output = {
        "probe": "M50", "title": "Gamma-Pi wormhole conductance",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_modules": n,
        "fiedler_eigenvalue": round(fiedler_val, 6),
        "graph_bisection": {
            "partition_A": sorted(partition_A),
            "partition_B": sorted(partition_B),
            "moonshine_separated": moon_separated,
            "moon_A": sorted(moon_in_A), "moon_B": sorted(moon_in_B),
            "nt_A": sorted(nt_in_A), "nt_B": sorted(nt_in_B),
        },
        "gamma_pi_edge": {
            "distance": round(gamma_pi_dist, 6),
            "effective_resistance": round(eff_resist, 6),
            "effective_conductance": round(eff_cond, 2),
            "conductance_ratio_vs_mean": round(cond_ratio, 4),
        },
        "cheeger_constant": round(cheeger, 4),
        "assessment": None,
    }

    parts = []
    if moon_separated:
        parts.append("FIEDLER SEPARATES moonshine from NT — spectral bisection confirms domain boundary")
    else:
        parts.append("Fiedler does NOT separate moonshine from NT — domains are interleaved")
    if cond_ratio > 1.5:
        parts.append(f"Gamma↔Pi is a SUPERHIGHWAY ({cond_ratio:.1f}x mean conductance)")
    elif cond_ratio > 0.8:
        parts.append(f"Gamma↔Pi is AVERAGE ({cond_ratio:.2f}x)")
    else:
        parts.append(f"Gamma↔Pi is a BOTTLENECK ({cond_ratio:.2f}x)")
    output["assessment"] = ". ".join(parts)

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
