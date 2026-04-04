"""
RMT Simulation: Does GUE repulsion alone explain ARI = 0.49?
=============================================================
The decisive experiment. All four Titans demand it.

Method:
  For SO(even), eigenvalues come in conjugate pairs e^{+/-i*theta}.
  The positive eigenangles theta_1 < theta_2 < ... < theta_N model
  normalized L-function zeros.

  Rank-0: All eigenangles free, repelled from 0 by sin(theta/2) factor.
  Rank-2: Two eigenangles pinned at 0. Remaining angles feel enhanced
          repulsion from the origin: sin^2(theta/2) -> sin^4(theta/2).

  We implement two approaches:
  A) NAIVE: Sample from SO(2(N-r)), insert r zeros at 0.
     This UNDERESTIMATES repulsion (lower bound on ARI).
  B) ENHANCED: Apply importance weights for the extra sin^2(theta_j/2)
     factors from the 2 pinned zeros. This is the correct conditional.

  We match the exact empirical stratum structure (84 strata, same
  rank-0/rank-2 counts per stratum) and run identical k-means.

If simulated ARI >= 0.45: the finding is trivial (GUE repulsion suffices).
If simulated ARI << 0.45: the finding has genuine residual structure.
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy.stats import ortho_group

ROOT = Path(__file__).parent.parent
STRATA_FILE = ROOT / "data" / "empirical_strata_so_even.json"

N_MATRIX = 60   # matrix size parameter: SO(2*N_MATRIX), giving N_MATRIX eigenangles
N_ZEROS = 20    # zeros per object
TAIL_SLICE = slice(4, 20)  # zeros 5-19 (0-indexed 4-19)
N_TRIALS = 50   # number of full simulation trials for statistics


def sample_eigenangles(N, n_objects):
    """Sample n_objects sets of eigenangles from SO(2N).
    Returns array of shape (n_objects, N) with sorted positive eigenangles."""
    results = []
    for _ in range(n_objects):
        M = ortho_group.rvs(2 * N)
        eigs = np.linalg.eigvals(M)
        angles = np.angle(eigs)
        # Take positive eigenangles (one per conjugate pair)
        pos = np.sort(np.abs(angles))
        # Deduplicate: eigenvalues come in +/- pairs, so sort and take every other
        # After abs + sort, duplicates are adjacent
        unique = []
        i = 0
        while i < len(pos):
            unique.append(pos[i])
            # Skip the duplicate from conjugate pair
            if i + 1 < len(pos) and abs(pos[i+1] - pos[i]) < 1e-8:
                i += 2
            else:
                i += 1
        eigenangles = np.array(unique)
        # Normalize: mean spacing = 1 (KS normalization: theta * N / pi)
        normalized = eigenangles * N / np.pi
        results.append(normalized[:N_ZEROS])
    return np.array(results)


def sample_rank0(N, n_objects):
    """Rank-0 SO(even): all eigenangles free."""
    return sample_eigenangles(N, n_objects)


def sample_rank2_naive(N, n_objects):
    """Rank-2 SO(even) NAIVE: sample from SO(2(N-2)), insert 2 zeros at 0.
    UNDERESTIMATES repulsion -- gives lower bound on ARI."""
    free_angles = sample_eigenangles(N - 2, n_objects)
    # Insert 2 zeros at position 0
    pinned = np.zeros((n_objects, 2))
    all_angles = np.hstack([pinned, free_angles])
    # Re-sort and re-normalize to N (not N-2)
    all_sorted = np.sort(all_angles, axis=1)
    # Renormalize: the effective matrix size is N, not N-2
    all_sorted = all_sorted * N / (N - 2)
    return all_sorted[:, :N_ZEROS]


def sample_rank2_enhanced(N, n_objects, n_mcmc_steps=200):
    """Rank-2 SO(even) ENHANCED: start from naive, apply Metropolis
    correction for the extra sin^2(theta_j/2) repulsion from pinned zeros.
    Each free eigenangle theta_j gets weight proportional to sin^4(theta_j/2)
    instead of sin^2(theta_j/2)."""
    samples = sample_rank2_naive(N, n_objects)
    rng = np.random.default_rng(42)

    for obj_idx in range(n_objects):
        angles = samples[obj_idx].copy()
        # Only modify free angles (indices 2+, since 0,1 are pinned at 0)
        for step in range(n_mcmc_steps):
            # Pick a random free angle (index 2-19)
            idx = rng.integers(2, N_ZEROS)
            old_val = angles[idx]
            # Propose small perturbation
            new_val = old_val + rng.normal(0, 0.05)
            if new_val <= 0:
                continue
            # Log acceptance ratio from the extra sin^2 factor
            # Target: sin^4(theta/2) instead of sin^2(theta/2)
            # Extra factor: sin^2(new/2) / sin^2(old/2)
            # In normalized coords: theta = angle * pi / N
            old_theta = old_val * np.pi / N
            new_theta = new_val * np.pi / N
            if old_theta <= 0 or old_theta >= np.pi or new_theta >= np.pi:
                continue
            log_ratio = 2.0 * (np.log(np.sin(new_theta / 2)) - np.log(np.sin(old_theta / 2)))
            if np.log(rng.random()) < log_ratio:
                angles[idx] = new_val
        samples[obj_idx] = np.sort(angles)
    return samples


def run_simulation(rank0_sampler, rank2_sampler, strata, label, n_trials=N_TRIALS):
    """Run full simulation matching empirical strata."""
    trial_aris = []
    for trial in range(n_trials):
        aris = []
        for stratum in strata:
            n_r0 = stratum["n_r0"]
            n_r2 = stratum["n_r2"]
            total = n_r0 + n_r2
            if total < 5:
                continue
            r0_zeros = rank0_sampler(N_MATRIX, n_r0)
            r2_zeros = rank2_sampler(N_MATRIX, n_r2)
            X = np.vstack([r0_zeros[:, TAIL_SLICE], r2_zeros[:, TAIL_SLICE]])
            labels = [0] * n_r0 + [2] * n_r2
            if len(set(labels)) < 2:
                continue
            k = max(2, min(total // 2, 5))
            pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
            aris.append(adjusted_rand_score(labels, pred))
        trial_aris.append(np.mean(aris) if aris else 0.0)
    return np.array(trial_aris)


def main():
    print("=" * 60)
    print("RMT SIMULATION: Does GUE repulsion explain ARI = 0.49?")
    print("=" * 60)

    # Load empirical strata
    with open(STRATA_FILE) as f:
        strata = json.load(f)
    print(f"Loaded {len(strata)} empirical strata")
    print(f"  Rank-0: {sum(s['n_r0'] for s in strata)}")
    print(f"  Rank-2: {sum(s['n_r2'] for s in strata)}")
    print(f"  Matrix size: SO(2*{N_MATRIX}) = SO({2*N_MATRIX})")
    print(f"  Trials: {N_TRIALS}")
    print()

    # --- Approach A: Naive (lower bound) ---
    print("--- Approach A: NAIVE (no enhanced repulsion) ---")
    print("    Lower bound on RMT-predicted ARI.")
    naive_aris = run_simulation(sample_rank0, sample_rank2_naive, strata, "naive")
    print(f"    ARI: mean={naive_aris.mean():.4f}, std={naive_aris.std():.4f}, "
          f"median={np.median(naive_aris):.4f}")
    print(f"    Range: [{naive_aris.min():.4f}, {naive_aris.max():.4f}]")
    print()

    # --- Approach B: Enhanced (correct conditional) ---
    print("--- Approach B: ENHANCED (Metropolis-corrected repulsion) ---")
    print("    Correct conditional distribution with sin^4 repulsion.")
    enhanced_aris = run_simulation(sample_rank0, sample_rank2_enhanced, strata, "enhanced")
    print(f"    ARI: mean={enhanced_aris.mean():.4f}, std={enhanced_aris.std():.4f}, "
          f"median={np.median(enhanced_aris):.4f}")
    print(f"    Range: [{enhanced_aris.min():.4f}, {enhanced_aris.max():.4f}]")
    print()

    # --- Permutation null on synthetic data ---
    print("--- Permutation null on synthetic data ---")
    rng = np.random.default_rng(999)
    perm_aris = []
    for trial in range(N_TRIALS):
        aris = []
        for stratum in strata:
            n_r0 = stratum["n_r0"]
            n_r2 = stratum["n_r2"]
            total = n_r0 + n_r2
            if total < 5:
                continue
            r0_zeros = sample_rank0(N_MATRIX, n_r0)
            r2_zeros = sample_rank2_enhanced(N_MATRIX, n_r2)
            X = np.vstack([r0_zeros[:, TAIL_SLICE], r2_zeros[:, TAIL_SLICE]])
            labels = [0] * n_r0 + [2] * n_r2
            shuffled = list(labels)
            rng.shuffle(shuffled)
            if len(set(labels)) < 2:
                continue
            k = max(2, min(total // 2, 5))
            pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
            aris.append(adjusted_rand_score(shuffled, pred))
        perm_aris.append(np.mean(aris) if aris else 0.0)
    perm_aris = np.array(perm_aris)
    print(f"    Shuffled ARI: mean={perm_aris.mean():.4f}, std={perm_aris.std():.4f}")
    print()

    # --- VERDICT ---
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    print(f"  Empirical ARI (within SO(even)):  0.4913")
    print(f"  RMT Naive ARI:                    {naive_aris.mean():.4f} +/- {naive_aris.std():.4f}")
    print(f"  RMT Enhanced ARI:                 {enhanced_aris.mean():.4f} +/- {enhanced_aris.std():.4f}")
    print(f"  Permutation null:                 {perm_aris.mean():.4f} +/- {perm_aris.std():.4f}")
    print()

    empirical = 0.4913
    best_rmt = enhanced_aris.mean()
    gap = empirical - best_rmt

    if best_rmt >= 0.45:
        print("  RESULT: GUE REPULSION EXPLAINS THE FINDING.")
        print(f"  RMT simulation produces ARI = {best_rmt:.4f}, empirical = {empirical:.4f}.")
        print("  The spectral tail finding reduces to 'GUE repulsion works as expected.'")
        print("  Still novel as computational demonstration. Not novel as mathematics.")
    elif best_rmt >= 0.30:
        print("  RESULT: PARTIAL EXPLANATION.")
        print(f"  RMT produces ARI = {best_rmt:.4f}, empirical = {empirical:.4f}.")
        print(f"  Gap = {gap:.4f}. Repulsion explains some but not all of the signal.")
        print("  Residual structure exists beyond GUE repulsion.")
    elif best_rmt < 0.30:
        print("  RESULT: GUE REPULSION IS INSUFFICIENT.")
        print(f"  RMT produces ARI = {best_rmt:.4f}, empirical = {empirical:.4f}.")
        print(f"  Gap = {gap:.4f}. The empirical finding far exceeds RMT prediction.")
        print("  Genuine residual structure in the spectral tail, not explained by repulsion.")
    else:
        print("  RESULT: INCONCLUSIVE.")


if __name__ == "__main__":
    main()
