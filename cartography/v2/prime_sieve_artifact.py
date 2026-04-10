#!/usr/bin/env python3
"""
Q10: The Simpler-Explanation Artifact Test (Prime Atmosphere in 2D)

Maps integers 1..10000 onto a 100x100 grid (row-major). Marks primes.
Computes clumping metric: mean nearest-neighbor distance between prime
positions vs uniformly random positions of the same count.

Then ABLATES by sieving:
  - Remove multiples of 2 → recompute clumping among survivors
  - Remove multiples of {2,3} → recompute
  - Remove multiples of {2,3,5} → recompute

If sieving survivors approach the prime clumping pattern, the 2D
structure is a NECESSARY consequence of excluding small factors.
If not, residual structure requires deeper explanation.

Verdict: compare the clumping ratio (observed/random) of primes vs
the sieved sets. Convergence = artifact. Divergence = real structure.
"""

import json
import numpy as np
from pathlib import Path
from scipy.spatial import cKDTree

OUT_FILE = Path(__file__).parent / "prime_sieve_artifact_results.json"

N = 10000
GRID_SIZE = 100
N_RANDOM_TRIALS = 200  # for null distribution


def is_prime_sieve(n):
    """Return boolean array where idx i is True if i is prime, for i in 0..n."""
    sieve = np.ones(n + 1, dtype=bool)
    sieve[0] = sieve[1] = False
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            sieve[p*p::p] = False
    return sieve


def int_to_grid(k):
    """Map integer k (1-indexed) to (row, col) on 100x100 grid, row-major."""
    idx = k - 1  # 0-indexed
    return (idx // GRID_SIZE, idx % GRID_SIZE)


def mean_nearest_neighbor(positions):
    """Mean nearest-neighbor Euclidean distance for a set of 2D positions."""
    if len(positions) < 2:
        return float('inf')
    tree = cKDTree(positions)
    dists, _ = tree.query(positions, k=2)  # k=2: self + nearest
    return float(np.mean(dists[:, 1]))


def random_mnn(n_points, n_trials=N_RANDOM_TRIALS):
    """Mean and std of MNN for n_points placed uniformly on 100x100 grid."""
    mnns = []
    for _ in range(n_trials):
        pts = np.column_stack([
            np.random.randint(0, GRID_SIZE, size=n_points),
            np.random.randint(0, GRID_SIZE, size=n_points)
        ]).astype(float)
        mnns.append(mean_nearest_neighbor(pts))
    return float(np.mean(mnns)), float(np.std(mnns))


def compute_clumping(label, integers):
    """
    Given a set of integers (subset of 1..10000), compute:
    - positions on grid
    - MNN of those positions
    - expected MNN for same count of random points
    - clumping ratio = observed_MNN / expected_MNN
      (< 1 means clumped, > 1 means dispersed, ~1 means random)
    """
    positions = np.array([int_to_grid(k) for k in integers], dtype=float)
    observed_mnn = mean_nearest_neighbor(positions)
    expected_mnn, expected_std = random_mnn(len(positions))
    ratio = observed_mnn / expected_mnn if expected_mnn > 0 else float('inf')
    z_score = (observed_mnn - expected_mnn) / expected_std if expected_std > 0 else 0.0

    return {
        "label": label,
        "count": len(integers),
        "observed_mnn": round(observed_mnn, 6),
        "expected_mnn_random": round(expected_mnn, 6),
        "expected_mnn_std": round(expected_std, 6),
        "clumping_ratio": round(ratio, 6),
        "z_score": round(z_score, 4),
        "interpretation": "clumped" if ratio < 0.98 else ("dispersed" if ratio > 1.02 else "random-like")
    }


def main():
    np.random.seed(42)

    # Build prime sieve
    primes_mask = is_prime_sieve(N)
    all_integers = np.arange(1, N + 1)
    primes = set(all_integers[primes_mask[1:]])  # primes in 1..10000

    # Sieve sets: integers NOT divisible by small primes
    survivors_no2 = set(k for k in all_integers if k % 2 != 0 or k == 2)
    survivors_no23 = set(k for k in all_integers if (k % 2 != 0 and k % 3 != 0) or k in (2, 3))
    survivors_no235 = set(k for k in all_integers if (k % 2 != 0 and k % 3 != 0 and k % 5 != 0) or k in (2, 3, 5))

    print(f"Primes in 1..{N}: {len(primes)}")
    print(f"Survivors (no mult of 2): {len(survivors_no2)}")
    print(f"Survivors (no mult of 2,3): {len(survivors_no23)}")
    print(f"Survivors (no mult of 2,3,5): {len(survivors_no235)}")

    results = {}
    stages = [
        ("primes", primes),
        ("sieve_remove_2", survivors_no2),
        ("sieve_remove_2_3", survivors_no23),
        ("sieve_remove_2_3_5", survivors_no235),
    ]

    for label, int_set in stages:
        print(f"\nComputing clumping for: {label} (n={len(int_set)})...")
        result = compute_clumping(label, sorted(int_set))
        results[label] = result
        print(f"  MNN observed: {result['observed_mnn']:.4f}")
        print(f"  MNN expected: {result['expected_mnn_random']:.4f}")
        print(f"  Ratio: {result['clumping_ratio']:.4f}")
        print(f"  z-score: {result['z_score']:.4f}")
        print(f"  Interpretation: {result['interpretation']}")

    # Convergence analysis: does sieving approach prime clumping?
    prime_ratio = results["primes"]["clumping_ratio"]
    sieve_ratios = {
        "remove_2": results["sieve_remove_2"]["clumping_ratio"],
        "remove_2_3": results["sieve_remove_2_3"]["clumping_ratio"],
        "remove_2_3_5": results["sieve_remove_2_3_5"]["clumping_ratio"],
    }

    # Measure convergence: how close does each sieve stage get to the prime ratio?
    convergence = {}
    for stage, ratio in sieve_ratios.items():
        gap = abs(ratio - prime_ratio)
        convergence[stage] = {
            "clumping_ratio": ratio,
            "gap_to_primes": round(gap, 6),
        }

    # Trend analysis
    gaps = [convergence[s]["gap_to_primes"] for s in ["remove_2", "remove_2_3", "remove_2_3_5"]]
    ratios_seq = [sieve_ratios[s] for s in ["remove_2", "remove_2_3", "remove_2_3_5"]]
    monotone_decreasing = all(gaps[i] >= gaps[i+1] for i in range(len(gaps)-1))
    min_gap = min(gaps)
    best_stage = ["remove_2", "remove_2_3", "remove_2_3_5"][gaps.index(min_gap)]

    # Check for crossover: does the sieve ratio pass through the prime ratio?
    # If it goes from above to below (or vice versa), that's a crossover.
    deviations = [r - prime_ratio for r in ratios_seq]
    crossover = any(deviations[i] * deviations[i+1] < 0 for i in range(len(deviations)-1))

    # The key insight: sieving creates REGULAR patterns (lattice-like), not random ones.
    # Removing mult-of-2 makes a checkerboard → hyper-dispersed.
    # Each additional sieve factor breaks the regularity toward randomness.
    # Primes live between "regular sieve" and "truly random."

    # Dispersal direction analysis
    all_dispersed = all(r > 1.0 for r in ratios_seq) and prime_ratio > 1.0
    approaching = abs(ratios_seq[-1] - prime_ratio) < abs(ratios_seq[0] - prime_ratio)

    # Final verdict
    final_gap = gaps[-1]
    if min_gap < 0.02:
        verdict = "ARTIFACT_CONFIRMED"
        explanation = (
            f"Sieving by the best stage ({best_stage}) produces a clumping ratio within "
            f"{min_gap:.4f} of the prime pattern. "
            "The 2D clumping of primes is a NECESSARY consequence of excluding "
            "small prime factors — no deeper geometric structure required."
        )
    elif crossover and min_gap < 0.05:
        verdict = "ARTIFACT_WITH_CROSSOVER"
        explanation = (
            f"Sieve clumping ratio CROSSES the prime value (gap at crossover < {min_gap:.4f}). "
            f"Best match at {best_stage} stage. The sieve trajectory passes through the "
            "prime clumping level, confirming it is an interpolation point on the sieve "
            "continuum. Structure is explained by factor exclusion; the non-monotonicity "
            "reflects the transition from lattice regularity to pseudo-random sieve residues."
        )
    elif approaching and final_gap < 0.15:
        verdict = "MOSTLY_ARTIFACT"
        explanation = (
            f"Sieve ratios approach prime clumping (gap shrinks from {gaps[0]:.4f} to "
            f"{final_gap:.4f}). The trend is correct but convergence is incomplete. "
            "Dominant structure is sieving; residual may come from higher primes."
        )
    else:
        verdict = "RESIDUAL_STRUCTURE"
        explanation = (
            f"Sieving does not adequately reproduce prime clumping (best gap={min_gap:.4f}). "
            "Significant residual structure exists beyond simple factor exclusion."
        )

    output = {
        "experiment": "Q10: Prime Sieve Artifact Test (2D Grid)",
        "description": (
            "Maps 1..10000 to 100x100 grid. Tests whether prime clumping is "
            "a necessary consequence of excluding small prime factors."
        ),
        "grid_size": GRID_SIZE,
        "N": N,
        "n_random_trials": N_RANDOM_TRIALS,
        "stages": results,
        "convergence": convergence,
        "convergence_monotone": monotone_decreasing,
        "convergence_crossover": crossover,
        "convergence_approaching": approaching,
        "best_match_stage": best_stage,
        "best_match_gap": round(min_gap, 6),
        "prime_clumping_ratio": prime_ratio,
        "final_sieve_gap": round(final_gap, 6),
        "verdict": verdict,
        "explanation": explanation,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"\nVERDICT: {verdict}")
    print(f"  {explanation}")


if __name__ == "__main__":
    main()
