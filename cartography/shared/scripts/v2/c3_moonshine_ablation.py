"""
Challenge 3: Break the Moonshine Rank-1 Tensor
=================================================
The enrichment matrix M[partition, prime] is rank-1 with spectral gap 6.7,
dominated by Mock Theta. Ablate (remove) Mock Theta and recompute SVD.
What is the new spectral gap? Which partition becomes the new driver?
Also: ablate each partition in turn — full ablation analysis.
"""
import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
MOON = V2 / "moonshine_scaling_results.json"
OUT = V2 / "c3_moonshine_ablation_results.json"

def svd_analysis(M, part_names, primes, label):
    """Compute SVD and return structured analysis."""
    if M.shape[0] < 2 or M.shape[1] < 2:
        return {"label": label, "error": "Matrix too small"}
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    total_var = np.sum(S**2)
    cum_var = np.cumsum(S**2) / total_var if total_var > 0 else np.zeros(len(S))
    gap = float(S[0] / S[1]) if len(S) > 1 and S[1] > 0 else float('inf')

    return {
        "label": label,
        "shape": list(M.shape),
        "singular_values": [round(float(s), 4) for s in S],
        "cumulative_variance": [round(float(c), 4) for c in cum_var],
        "spectral_gap": round(gap, 4),
        "rank1_variance": round(float(cum_var[0]), 4),
        "partition_loadings": {name: round(float(U[i, 0]), 4) for i, name in enumerate(part_names)},
        "prime_loadings": {str(p): round(float(Vt[0, j]), 4) for j, p in enumerate(primes)},
        "dominant_partition": part_names[int(np.argmax(np.abs(U[:, 0])))],
        "dominant_prime": str(primes[int(np.argmax(np.abs(Vt[0])))]),
    }

def main():
    t0 = time.time()
    print("=== Challenge 3: Break the Moonshine Rank-1 Tensor ===\n")

    with open(MOON) as f:
        data = json.load(f)

    partitions = data["enrichment_by_partition"]
    all_primes = set()
    for name, info in partitions.items():
        all_primes.update(int(p) for p in info["enrichments_by_prime"].keys())
    primes = sorted(all_primes)
    part_names = sorted(partitions.keys())

    # Build full matrix
    M_full = np.zeros((len(part_names), len(primes)))
    for i, name in enumerate(part_names):
        ep = partitions[name]["enrichments_by_prime"]
        for j, p in enumerate(primes):
            M_full[i, j] = ep.get(str(p), 0)

    print(f"  Full matrix: {M_full.shape}")
    full_svd = svd_analysis(M_full, part_names, primes, "FULL")
    print(f"  Spectral gap: {full_svd['spectral_gap']}")
    print(f"  Rank-1 variance: {full_svd['rank1_variance']:.1%}")
    print(f"  Dominant: {full_svd['dominant_partition']} × {full_svd['dominant_prime']}")

    # Ablation study: remove each partition in turn
    print("\n  === ABLATION STUDY ===")
    ablations = {}
    for remove_idx, remove_name in enumerate(part_names):
        keep_idx = [i for i in range(len(part_names)) if i != remove_idx]
        keep_names = [part_names[i] for i in keep_idx]
        M_ablated = M_full[keep_idx]

        result = svd_analysis(M_ablated, keep_names, primes, f"without_{remove_name}")
        ablations[remove_name] = result

        print(f"\n  Remove {remove_name}:")
        print(f"    New spectral gap: {result['spectral_gap']}")
        print(f"    Rank-1 variance: {result['rank1_variance']:.1%}")
        print(f"    New dominant: {result['dominant_partition']} × {result['dominant_prime']}")
        print(f"    SVs: {result['singular_values']}")

    # Also ablate each prime
    print("\n  === PRIME ABLATION ===")
    prime_ablations = {}
    for remove_j, remove_p in enumerate(primes):
        keep_j = [j for j in range(len(primes)) if j != remove_j]
        keep_primes = [primes[j] for j in keep_j]
        M_ablated = M_full[:, keep_j]

        result = svd_analysis(M_ablated, part_names, keep_primes, f"without_p{remove_p}")
        prime_ablations[str(remove_p)] = result

        print(f"\n  Remove p={remove_p}:")
        print(f"    New spectral gap: {result['spectral_gap']}")
        print(f"    Rank-1 variance: {result['rank1_variance']:.1%}")
        print(f"    New dominant: {result['dominant_partition']} × {result['dominant_prime']}")

    # Find which ablation has the biggest impact
    gap_changes = {name: full_svd['spectral_gap'] - abl['spectral_gap']
                   for name, abl in ablations.items()}
    most_impactful = max(gap_changes.items(), key=lambda x: abs(x[1]))

    prime_gap_changes = {p: full_svd['spectral_gap'] - abl['spectral_gap']
                        for p, abl in prime_ablations.items()}
    most_impactful_prime = max(prime_gap_changes.items(), key=lambda x: abs(x[1]))

    print(f"\n  Most impactful partition ablation: {most_impactful[0]} (gap change: {most_impactful[1]:.2f})")
    print(f"  Most impactful prime ablation: p={most_impactful_prime[0]} (gap change: {most_impactful_prime[1]:.2f})")

    # What happens when Mock Theta is removed specifically?
    mock_result = ablations.get("mock_theta", {})
    print(f"\n  === MOCK THETA REMOVAL ===")
    print(f"  New spectral gap: {mock_result.get('spectral_gap', 'N/A')}")
    print(f"  New dominant partition: {mock_result.get('dominant_partition', 'N/A')}")
    print(f"  New rank-1 variance: {mock_result.get('rank1_variance', 'N/A')}")
    print(f"  Was rank-1? Now: {'YES' if mock_result.get('rank1_variance', 0) > 0.9 else 'NO'}")

    elapsed = time.time() - t0
    output = {
        "challenge": "C3", "title": "Break the Moonshine Rank-1 Tensor",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "full_matrix": full_svd,
        "partition_ablations": ablations,
        "prime_ablations": prime_ablations,
        "gap_changes_partition": {k: round(v, 4) for k, v in gap_changes.items()},
        "gap_changes_prime": {k: round(v, 4) for k, v in prime_gap_changes.items()},
        "most_impactful_partition": most_impactful[0],
        "most_impactful_prime": f"p={most_impactful_prime[0]}",
        "mock_theta_removal": mock_result,
        "assessment": None,
    }

    mt_gap = mock_result.get('spectral_gap', 0)
    mt_var = mock_result.get('rank1_variance', 0)
    mt_dom = mock_result.get('dominant_partition', 'unknown')
    if mt_gap < 2:
        output["assessment"] = (
            f"TENSOR BROKEN: removing Mock Theta collapses spectral gap from {full_svd['spectral_gap']:.1f} "
            f"to {mt_gap:.1f}. Rank-1 structure destroyed. New dominant: {mt_dom}. "
            f"Mock Theta IS the fundamental frequency — without it, moonshine has no single mode.")
    elif mt_var < 0.7:
        output["assessment"] = (
            f"TENSOR WEAKENED: gap {full_svd['spectral_gap']:.1f}→{mt_gap:.1f}. "
            f"Rank-1 variance drops to {mt_var:.0%}. New dominant: {mt_dom}. "
            f"Mock Theta was the primary but not sole contributor.")
    else:
        output["assessment"] = (
            f"TENSOR SURVIVES: gap {full_svd['spectral_gap']:.1f}→{mt_gap:.1f}. "
            f"Still rank-1 ({mt_var:.0%}). New dominant: {mt_dom}. "
            f"Moonshine rank-1 structure is ROBUST to Mock Theta removal — the mode is deeper than any single partition.")

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
