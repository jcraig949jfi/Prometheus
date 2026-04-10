#!/usr/bin/env python3
"""
Q27 — Residue Class Interference Lattices

Map integers 1..40000 onto a 200x200 grid. For each small prime l in {2,3,5,7},
mark positions where the integer ≡ 0 mod l. These form regular sublattices.
The "sieve survivors" are positions coprime to 210 = 2*3*5*7.

Questions answered:
  1. Fraction of primes that are sieve survivors (should be ~100% minus {2,3,5,7}).
  2. Spatial overlap between sieve survivors and actual primes.
  3. Excess clustering of primes WITHIN the sieve-survivor sublattice vs random.

Core question: once you account for the sieve lattice, is the sieve the COMPLETE
explanation for prime spatial structure, or do primes show residual clustering?
"""

import json
import math
import numpy as np
from collections import defaultdict
from pathlib import Path

# ── Setup ──────────────────────────────────────────────────────────────────
N = 40000
ROWS, COLS = 200, 200
SMALL_PRIMES = [2, 3, 5, 7]
PRIMORIAL = 2 * 3 * 5 * 7  # 210

def sieve_of_eratosthenes(limit):
    """Return boolean array where is_prime[i] is True if i is prime."""
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for p in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[p]:
            is_prime[p*p::p] = False
    return is_prime

def int_to_grid(n):
    """Map integer n (1-indexed) to (row, col) on 200x200 grid."""
    idx = n - 1  # 0-indexed
    return idx // COLS, idx % COLS

def grid_to_int(r, c):
    """Map (row, col) back to integer (1-indexed)."""
    return r * COLS + c + 1

# ── Build arrays ───────────────────────────────────────────────────────────
is_prime = sieve_of_eratosthenes(N)
primes_set = set(np.where(is_prime)[0])

# Grid arrays
grid_values = np.arange(1, N + 1).reshape(ROWS, COLS)

# Sieve survivor mask: coprime to 210
sieve_survivor = np.ones((ROWS, COLS), dtype=bool)
for p in SMALL_PRIMES:
    sieve_survivor &= (grid_values % p != 0)

# Prime mask on grid
prime_grid = np.zeros((ROWS, COLS), dtype=bool)
for p in primes_set:
    if 1 <= p <= N:
        r, c = int_to_grid(p)
        prime_grid[r, c] = True

# ── Q1: Fraction of primes that are sieve survivors ───────────────────────
total_primes = int(prime_grid.sum())
primes_that_are_survivors = int((prime_grid & sieve_survivor).sum())
primes_that_are_small = len({2, 3, 5, 7} & primes_set)
fraction_primes_survivors = primes_that_are_survivors / total_primes

# ── Q2: Spatial overlap ──────────────────────────────────────────────────
n_survivors = int(sieve_survivor.sum())
n_primes_on_survivors = primes_that_are_survivors
# Expected if primes were placed uniformly at random on grid
survivor_fraction = n_survivors / N
expected_primes_on_survivors = total_primes * survivor_fraction
overlap_ratio = n_primes_on_survivors / expected_primes_on_survivors if expected_primes_on_survivors > 0 else 0

# ── Q3: Clustering analysis within sieve-survivor sublattice ─────────────
# Extract the sieve-survivor positions and check which are prime
survivor_coords = np.argwhere(sieve_survivor)  # (n_survivors, 2)
prime_on_survivor_coords = np.argwhere(prime_grid & sieve_survivor)

# Nearest-neighbor distances for primes within the survivor sublattice
# Compare to random placement of the same number of points on the same sublattice

def nearest_neighbor_distances(points, reference_points=None):
    """Compute nearest-neighbor distance from each point to reference set.
    If reference_points is None, compute within-set NN (excluding self)."""
    if len(points) == 0:
        return np.array([])
    if reference_points is None:
        reference_points = points
        exclude_self = True
    else:
        exclude_self = False

    dists = []
    # Chunked to avoid memory blowup
    chunk_size = 500
    for i in range(0, len(points), chunk_size):
        chunk = points[i:i+chunk_size]
        # Euclidean distance
        diff = chunk[:, np.newaxis, :] - reference_points[np.newaxis, :, :]
        d = np.sqrt((diff ** 2).sum(axis=2))
        if exclude_self:
            # Set diagonal-block to inf
            for j in range(len(chunk)):
                global_idx = i + j
                if global_idx < len(reference_points):
                    d[j, global_idx] = np.inf
        dists.append(d.min(axis=1))
    return np.concatenate(dists)

# Actual prime NN distances within survivor sublattice
prime_nn = nearest_neighbor_distances(prime_on_survivor_coords)

# Monte Carlo: random placement on survivor sublattice
n_trials = 500
random_nn_means = []
random_nn_stds = []
rng = np.random.default_rng(42)
n_prime_survivors = len(prime_on_survivor_coords)

for _ in range(n_trials):
    # Random subset of survivor positions, same count as actual primes on survivors
    idx = rng.choice(len(survivor_coords), size=n_prime_survivors, replace=False)
    random_pts = survivor_coords[idx]
    rnn = nearest_neighbor_distances(random_pts)
    random_nn_means.append(rnn.mean())
    random_nn_stds.append(rnn.std())

actual_nn_mean = float(prime_nn.mean())
actual_nn_std = float(prime_nn.std())
random_nn_mean_avg = float(np.mean(random_nn_means))
random_nn_std_avg = float(np.mean(random_nn_stds))
random_nn_mean_std = float(np.std(random_nn_means))  # uncertainty on the mean

# Z-score: how many sigma is actual mean from random expectation
z_clustering = (actual_nn_mean - random_nn_mean_avg) / random_nn_mean_std if random_nn_mean_std > 0 else 0.0

# ── Q3b: Quadrat analysis (chi-squared) ─────────────────────────────────
# Divide the 200x200 grid into 10x10 blocks (20x20 = 400 blocks)
BLOCK = 10
n_blocks_r = ROWS // BLOCK
n_blocks_c = COLS // BLOCK

def quadrat_chi2(point_grid, survivor_mask):
    """Chi-squared test for uniformity of points on survivor sublattice across blocks."""
    observed = []
    expected = []
    total_points = int((point_grid & survivor_mask).sum())
    total_survivors = int(survivor_mask.sum())

    for br in range(n_blocks_r):
        for bc in range(n_blocks_c):
            r0, r1 = br * BLOCK, (br + 1) * BLOCK
            c0, c1 = bc * BLOCK, (bc + 1) * BLOCK
            block_survivors = int(survivor_mask[r0:r1, c0:c1].sum())
            block_primes = int((point_grid & survivor_mask)[r0:r1, c0:c1].sum())
            observed.append(block_primes)
            # Expected = total_points * (block_survivors / total_survivors)
            exp = total_points * (block_survivors / total_survivors) if total_survivors > 0 else 0
            expected.append(exp)

    observed = np.array(observed, dtype=float)
    expected = np.array(expected, dtype=float)
    # Filter out zero-expected blocks
    mask = expected > 0
    chi2 = float(((observed[mask] - expected[mask]) ** 2 / expected[mask]).sum())
    dof = int(mask.sum()) - 1
    return chi2, dof, observed, expected

chi2_primes, dof_primes, obs_primes, exp_primes = quadrat_chi2(prime_grid, sieve_survivor)

# Same for random placements
chi2_randoms = []
for _ in range(200):
    fake_grid = np.zeros((ROWS, COLS), dtype=bool)
    idx = rng.choice(len(survivor_coords), size=n_prime_survivors, replace=False)
    for i in idx:
        fake_grid[survivor_coords[i, 0], survivor_coords[i, 1]] = True
    c2, _, _, _ = quadrat_chi2(fake_grid, sieve_survivor)
    chi2_randoms.append(c2)

chi2_random_mean = float(np.mean(chi2_randoms))
chi2_random_std = float(np.std(chi2_randoms))
chi2_z = (chi2_primes - chi2_random_mean) / chi2_random_std if chi2_random_std > 0 else 0.0

# ── Q3c: Row-by-row density variance ────────────────────────────────────
# Primes thin out as numbers grow (PNT). Within the sieve sublattice, is the
# thinning exactly what PNT predicts, or is there residual structure?

row_prime_density = []
row_expected_density = []
for r in range(ROWS):
    n_surv_row = int(sieve_survivor[r].sum())
    n_prime_surv_row = int((prime_grid[r] & sieve_survivor[r]).sum())
    if n_surv_row > 0:
        row_prime_density.append(n_prime_surv_row / n_surv_row)
        # PNT expectation: for integers in this row, average 1/ln(n)
        row_start = r * COLS + 1
        row_end = (r + 1) * COLS
        # Average 1/ln(n) over survivor positions in this row
        row_vals = grid_values[r][sieve_survivor[r]].astype(float)
        row_vals = row_vals[row_vals > 1]  # exclude 1 where log(1)=0
        if len(row_vals) == 0:
            row_prime_density.pop()  # undo the append above
            continue
        pnt_density = float(np.mean(1.0 / np.log(row_vals)))
        # Scale by euler_phi(210)/210 to get density among survivors
        # Actually, PNT says pi(x) ~ x/ln(x), so density among ALL integers ~ 1/ln(n)
        # Density among survivors = density_all / survivor_fraction = (1/ln(n)) / (phi(210)/210)
        # But we're measuring density among survivors directly, so expected = 1/ln(n) / (phi(210)/210)
        # Wait: if fraction phi(210)/210 of integers are survivors, and fraction 1/ln(n) are prime,
        # then density of primes among survivors ≈ (1/ln(n)) / (phi(210)/210)
        # phi(210) = 210 * (1-1/2)(1-1/3)(1-1/5)(1-1/7) = 48
        phi_ratio = 48.0 / 210.0  # ≈ 0.2286
        pnt_among_survivors = pnt_density / phi_ratio
        row_expected_density.append(pnt_among_survivors)

row_prime_density = np.array(row_prime_density)
row_expected_density = np.array(row_expected_density)
residual = row_prime_density - row_expected_density

residual_mean = float(residual.mean())
residual_std = float(residual.std())
residual_max = float(np.max(np.abs(residual)))

# ── Sublattice structure for each small prime ────────────────────────────
sublattice_info = {}
for p in SMALL_PRIMES:
    mask = (grid_values % p == 0)
    count = int(mask.sum())
    sublattice_info[str(p)] = {
        "positions_marked": count,
        "fraction_of_grid": round(count / N, 6),
        "theoretical_fraction": round(1.0 / p, 6)
    }

# ── Assemble results ────────────────────────────────────────────────────
results = {
    "metadata": {
        "grid_size": [ROWS, COLS],
        "N": N,
        "small_primes": SMALL_PRIMES,
        "primorial": PRIMORIAL,
        "euler_phi_210": 48,
        "survivor_fraction_theoretical": round(48 / 210, 6),
        "monte_carlo_trials_nn": 500,
        "monte_carlo_trials_chi2": 200,
        "quadrat_block_size": BLOCK
    },
    "sublattice_structure": sublattice_info,
    "Q1_primes_as_survivors": {
        "total_primes_in_range": total_primes,
        "primes_that_are_sieve_survivors": primes_that_are_survivors,
        "primes_excluded_by_sieve": total_primes - primes_that_are_survivors,
        "excluded_primes_are": [2, 3, 5, 7],
        "fraction_primes_that_are_survivors": round(fraction_primes_survivors, 8),
        "interpretation": "All primes except {2,3,5,7} are coprime to 210, so ~99.9% are survivors"
    },
    "Q2_spatial_overlap": {
        "total_sieve_survivors": n_survivors,
        "survivor_fraction_of_grid": round(n_survivors / N, 6),
        "primes_on_survivor_positions": n_primes_on_survivors,
        "expected_if_uniform": round(expected_primes_on_survivors, 2),
        "overlap_enrichment_ratio": round(overlap_ratio, 6),
        "interpretation": (
            "Enrichment ratio >> 1 means primes are heavily concentrated on survivor positions. "
            "This is trivially expected since primes > 7 MUST be coprime to 210."
        )
    },
    "Q3_clustering_within_survivor_sublattice": {
        "nearest_neighbor_analysis": {
            "actual_prime_nn_mean": round(actual_nn_mean, 4),
            "actual_prime_nn_std": round(actual_nn_std, 4),
            "random_placement_nn_mean": round(random_nn_mean_avg, 4),
            "random_placement_nn_std": round(random_nn_std_avg, 4),
            "z_score_clustering": round(z_clustering, 4),
            "interpretation": (
                "z < -2 would mean primes are MORE clustered than random on the survivor sublattice. "
                "z > 2 would mean primes are MORE spread out (repulsion). "
                "|z| < 2 means no significant deviation."
            )
        },
        "quadrat_chi2_analysis": {
            "chi2_primes": round(chi2_primes, 2),
            "dof": dof_primes,
            "chi2_random_mean": round(chi2_random_mean, 2),
            "chi2_random_std": round(chi2_random_std, 2),
            "chi2_z_score": round(chi2_z, 4),
            "interpretation": (
                "chi2_z >> 2 means primes show excess spatial variation beyond what random "
                "placement on the survivor lattice produces. This captures density gradients."
            )
        },
        "row_density_pnt_residual": {
            "residual_mean": round(residual_mean, 6),
            "residual_std": round(residual_std, 6),
            "residual_max_abs": round(residual_max, 6),
            "interpretation": (
                "Residual after subtracting PNT-predicted density among survivors. "
                "Small residual_std means PNT + sieve explains nearly all row-to-row variation."
            )
        }
    },
    "verdict": {
        "sieve_explains_spatial_structure": None,  # filled below
        "residual_clustering_detected": None,
        "residual_density_gradient_detected": None,
        "summary": None
    }
}

# Fill verdict
nn_significant = abs(z_clustering) > 2.0
chi2_significant = abs(chi2_z) > 2.0

results["verdict"]["residual_clustering_detected"] = bool(nn_significant)
results["verdict"]["residual_density_gradient_detected"] = bool(chi2_significant)

if not nn_significant and not chi2_significant:
    results["verdict"]["sieve_explains_spatial_structure"] = True
    results["verdict"]["summary"] = (
        "The sieve lattice is the COMPLETE explanation for prime spatial structure on this grid. "
        "Once you condition on the survivor sublattice, primes show no excess clustering "
        f"(NN z={z_clustering:.2f}) and no excess density variation (chi2 z={chi2_z:.2f}). "
        "All apparent 'structure' of primes on the 200x200 grid is fully accounted for by "
        "the mod-2, mod-3, mod-5, mod-7 exclusion pattern."
    )
elif chi2_significant and not nn_significant:
    results["verdict"]["sieve_explains_spatial_structure"] = False
    results["verdict"]["summary"] = (
        f"The sieve lattice does NOT fully explain prime spatial structure. "
        f"NN clustering is insignificant (z={z_clustering:.2f}), but density gradients "
        f"are significant (chi2 z={chi2_z:.2f}). This is the PNT gradient: primes thin "
        "toward the bottom of the grid (larger integers). The sieve removes mod-p structure "
        "but cannot remove the 1/ln(n) density decay. The residual structure is PNT, not "
        "any mysterious additional pattern."
    )
else:
    results["verdict"]["sieve_explains_spatial_structure"] = False
    results["verdict"]["summary"] = (
        f"Residual structure detected beyond sieve. NN z={z_clustering:.2f}, "
        f"chi2 z={chi2_z:.2f}. Investigate whether this is PNT density gradient "
        "or genuine higher-order prime correlation."
    )

# ── Save ─────────────────────────────────────────────────────────────────
out_dir = Path(__file__).parent
out_path = out_dir / "residue_interference_lattice_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"Results saved to {out_path}")
print(f"\n=== Q27: Residue Class Interference Lattices ===")
print(f"Grid: {ROWS}x{COLS} = {N} integers")
print(f"Sieve survivors (coprime to 210): {n_survivors} ({n_survivors/N:.4f} of grid, theory={48/210:.4f})")
print(f"\nQ1: {primes_that_are_survivors}/{total_primes} primes are sieve survivors ({fraction_primes_survivors:.6f})")
print(f"    Only {2},{3},{5},{7} excluded = {total_primes - primes_that_are_survivors} primes")
print(f"\nQ2: Overlap enrichment = {overlap_ratio:.4f}x")
print(f"    (Primes on {survivor_fraction:.4f} of grid, but {n_primes_on_survivors}/{total_primes} land there)")
print(f"\nQ3: Clustering WITHIN survivor sublattice:")
print(f"    NN mean:  actual={actual_nn_mean:.4f}, random={random_nn_mean_avg:.4f}, z={z_clustering:.4f}")
print(f"    Chi2:     actual={chi2_primes:.1f}, random={chi2_random_mean:.1f}±{chi2_random_std:.1f}, z={chi2_z:.4f}")
print(f"    PNT residual: mean={residual_mean:.6f}, std={residual_std:.6f}")
print(f"\nVERDICT: {results['verdict']['summary']}")
