#!/usr/bin/env python3
"""
Q29: Directional Persistence of Prime Runs on a 200x200 grid.

Map integers 1..40000 to a 200x200 grid (row-major).
For each of 8 directions, find all maximal runs of consecutive primes.
Compare run-length distributions to Bernoulli null model.
Test whether primes exhibit directional persistence.
"""

import json
import numpy as np
from collections import defaultdict
from pathlib import Path

# ── Sieve of Eratosthenes ──────────────────────────────────────────────
def sieve(n):
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

# ── Build grid ──────────────────────────────────────────────────────────
N = 40000
ROWS, COLS = 200, 200
assert ROWS * COLS == N

is_prime_arr = sieve(N)
# Map 1..40000 into 200x200 grid (row-major: cell (r,c) = r*200 + c + 1)
grid = np.zeros((ROWS, COLS), dtype=bool)
for r in range(ROWS):
    for c in range(COLS):
        val = r * COLS + c + 1  # 1-indexed
        grid[r, c] = is_prime_arr[val]

p_prime = grid.sum() / N
print(f"Grid: {ROWS}x{COLS}, total primes: {grid.sum()}, p = {p_prime:.6f}")
print(f"pi(40000) = {is_prime_arr[1:N+1].sum()}")

# ── Direction vectors ───────────────────────────────────────────────────
DIRECTIONS = {
    'N':  (-1,  0),
    'S':  ( 1,  0),
    'E':  ( 0,  1),
    'W':  ( 0, -1),
    'NE': (-1,  1),
    'NW': (-1, -1),
    'SE': ( 1,  1),
    'SW': ( 1, -1),
}

# ── Extract maximal runs ───────────────────────────────────────────────
def get_all_runs(grid, dr, dc):
    """
    Extract all maximal runs of consecutive primes along direction (dr, dc).
    We enumerate all 'lines' (maximal sequences of cells along that direction)
    and find runs of True within each line.
    """
    rows, cols = grid.shape
    visited = np.zeros_like(grid, dtype=bool)
    runs = []

    for r in range(rows):
        for c in range(cols):
            if visited[r, c]:
                continue
            # Check if (r, c) is a starting cell of a line:
            # It's a start if the previous cell (r-dr, c-dc) is out of bounds
            pr, pc = r - dr, c - dc
            if 0 <= pr < rows and 0 <= pc < cols:
                continue  # not a line start

            # Walk along the line
            line_cells = []
            cr, cc = r, c
            while 0 <= cr < rows and 0 <= cc < cols:
                visited[cr, cc] = True
                line_cells.append(grid[cr, cc])
                cr += dr
                cc += dc

            # Extract run lengths of consecutive True
            current_run = 0
            for val in line_cells:
                if val:
                    current_run += 1
                else:
                    if current_run > 0:
                        runs.append(current_run)
                    current_run = 0
            if current_run > 0:
                runs.append(current_run)

    return runs


# ── Bernoulli null model ────────────────────────────────────────────────
def bernoulli_expected_count(k, p, total_cells_in_lines):
    """
    Expected number of maximal runs of length exactly k in Bernoulli model.
    P(maximal run of length k) = p^k * (1-p)^2 for interior runs,
    but boundary effects matter. For a line of length L:
      E[# maximal runs of length k] involves boundary terms.

    Simpler: for a line of length L, the expected number of runs of length >= k
    is approximately (L - k + 1) * p^k * (1-p)^2 (interior) + boundary corrections.

    We'll use simulation for the null to be rigorous.
    """
    pass  # We'll use Monte Carlo instead


def monte_carlo_null(grid_shape, p, directions, n_trials=2000):
    """
    Generate random Bernoulli grids and compute run distributions.
    Returns mean and std of run counts per direction per length.
    """
    rows, cols = grid_shape
    all_results = {d: defaultdict(list) for d in directions}

    for t in range(n_trials):
        random_grid = np.random.random((rows, cols)) < p
        for dname, (dr, dc) in directions.items():
            runs = get_all_runs(random_grid, dr, dc)
            counts = defaultdict(int)
            for r in runs:
                counts[r] += 1
            # Record counts for each length up to some max
            for k in range(1, 30):
                all_results[dname][k].append(counts.get(k, 0))

    # Compute mean and std
    null_stats = {}
    for dname in directions:
        null_stats[dname] = {}
        for k in range(1, 30):
            vals = all_results[dname][k]
            null_stats[dname][k] = {
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals)),
            }
    return null_stats


# ── Conditional probability (persistence test) ─────────────────────────
def conditional_persistence(grid, dr, dc):
    """
    Given a cell is prime, what's the probability the next cell in direction
    (dr, dc) is also prime? Compare to unconditional p.
    """
    rows, cols = grid.shape
    prime_then_prime = 0
    prime_total = 0

    for r in range(rows):
        for c in range(cols):
            if not grid[r, c]:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                prime_total += 1
                if grid[nr, nc]:
                    prime_then_prime += 1

    if prime_total == 0:
        return 0.0, 0
    return prime_then_prime / prime_total, prime_total


# ── Main analysis ───────────────────────────────────────────────────────
print("\n=== Extracting runs for all 8 directions ===")
observed = {}
for dname, (dr, dc) in DIRECTIONS.items():
    runs = get_all_runs(grid, dr, dc)
    counts = defaultdict(int)
    for r in runs:
        counts[r] += 1
    observed[dname] = dict(counts)
    total_runs = len(runs)
    max_run = max(runs) if runs else 0
    mean_run = np.mean(runs) if runs else 0
    print(f"  {dname:2s}: {total_runs:5d} runs, max={max_run:2d}, mean={mean_run:.3f}")

# ── Conditional persistence ─────────────────────────────────────────────
print(f"\n=== Conditional persistence (baseline p = {p_prime:.6f}) ===")
persistence = {}
for dname, (dr, dc) in DIRECTIONS.items():
    cond_p, n_pairs = conditional_persistence(grid, dr, dc)
    # Z-test: (cond_p - p) / sqrt(p*(1-p)/n_pairs)
    se = np.sqrt(p_prime * (1 - p_prime) / n_pairs) if n_pairs > 0 else 1
    z = (cond_p - p_prime) / se
    persistence[dname] = {
        'conditional_p': round(cond_p, 6),
        'n_pairs': n_pairs,
        'z_score': round(z, 4),
        'excess_over_baseline': round(cond_p - p_prime, 6),
    }
    sig = " ***" if abs(z) > 3 else " *" if abs(z) > 2 else ""
    print(f"  {dname:2s}: P(next prime | prime) = {cond_p:.6f}, "
          f"excess = {cond_p - p_prime:+.6f}, z = {z:+.2f}{sig}")

# ── Monte Carlo null for run distributions ──────────────────────────────
print("\n=== Monte Carlo null (2000 trials) ===")
null_stats = monte_carlo_null((ROWS, COLS), p_prime, DIRECTIONS, n_trials=2000)

# ── Compare observed vs null ────────────────────────────────────────────
print("\n=== Run length distribution: observed vs Bernoulli null ===")
heavy_tail_evidence = {}
for dname in DIRECTIONS:
    print(f"\n  Direction {dname}:")
    dir_evidence = []
    for k in range(1, 20):
        obs = observed[dname].get(k, 0)
        null_mean = null_stats[dname][k]['mean']
        null_std = null_stats[dname][k]['std']
        z = (obs - null_mean) / null_std if null_std > 0 else 0
        if obs > 0 or null_mean > 1:
            sig = " ***" if abs(z) > 3 else " *" if abs(z) > 2 else ""
            print(f"    k={k:2d}: obs={obs:5d}, null={null_mean:7.1f}±{null_std:5.1f}, z={z:+.2f}{sig}")
        dir_evidence.append({
            'k': k,
            'observed': obs,
            'null_mean': round(null_mean, 2),
            'null_std': round(null_std, 2),
            'z_score': round(z, 4),
        })
    heavy_tail_evidence[dname] = dir_evidence

# ── Aggregate: is there any directional persistence? ────────────────────
print("\n=== Summary ===")
all_z_persist = [(d, persistence[d]['z_score']) for d in DIRECTIONS]
all_z_persist.sort(key=lambda x: abs(x[1]), reverse=True)
print("Persistence z-scores (sorted by |z|):")
for d, z in all_z_persist:
    print(f"  {d:2s}: z = {z:+.4f}")

# Check for heavy tails at k >= 4
print("\nHeavy-tail check (k >= 4, z > 2):")
heavy_tail_found = False
for dname in DIRECTIONS:
    for entry in heavy_tail_evidence[dname]:
        if entry['k'] >= 4 and entry['z_score'] > 2:
            heavy_tail_found = True
            print(f"  {dname} k={entry['k']}: obs={entry['observed']}, "
                  f"null={entry['null_mean']}±{entry['null_std']}, z={entry['z_score']:.2f}")

if not heavy_tail_found:
    print("  No significant heavy tails detected at k >= 4.")

# Pair opposite directions to check for anisotropy
print("\nAnisotropy check (opposite direction pairs):")
pairs = [('N', 'S'), ('E', 'W'), ('NE', 'SW'), ('NW', 'SE')]
for d1, d2 in pairs:
    z1 = persistence[d1]['z_score']
    z2 = persistence[d2]['z_score']
    diff = abs(z1 - z2)
    print(f"  {d1}/{d2}: z1={z1:+.4f}, z2={z2:+.4f}, |diff|={diff:.4f}")

# ── Verdict ─────────────────────────────────────────────────────────────
max_abs_z = max(abs(v['z_score']) for v in persistence.values())
verdict_persistence = (
    "YES: significant directional persistence detected"
    if max_abs_z > 3
    else "MARGINAL: some evidence of persistence"
    if max_abs_z > 2
    else "NO: primes show no directional persistence beyond Bernoulli expectation"
)

# Check heavy tails
max_heavy_z = 0
for dname in DIRECTIONS:
    for entry in heavy_tail_evidence[dname]:
        if entry['k'] >= 4 and entry['z_score'] > max_heavy_z:
            max_heavy_z = entry['z_score']

verdict_heavy_tail = (
    "YES: significant heavy-tailed runs detected"
    if max_heavy_z > 3
    else "MARGINAL: some evidence of heavy tails"
    if max_heavy_z > 2
    else "NO: run distributions consistent with Bernoulli null"
)

print(f"\nDirectional persistence: {verdict_persistence}")
print(f"Heavy-tailed runs: {verdict_heavy_tail}")

# ── Save results ────────────────────────────────────────────────────────
results = {
    'question': 'Q29: Directional Persistence of Prime Runs',
    'grid': {'rows': ROWS, 'cols': COLS, 'N': N},
    'prime_density': round(p_prime, 6),
    'total_primes': int(grid.sum()),
    'persistence_test': persistence,
    'run_distributions': {
        d: {
            'observed': {str(k): v for k, v in observed[d].items()},
            'max_run': max(observed[d].keys()) if observed[d] else 0,
            'total_runs': sum(observed[d].values()),
        }
        for d in DIRECTIONS
    },
    'heavy_tail_evidence': {
        d: [e for e in heavy_tail_evidence[d] if e['observed'] > 0 or e['null_mean'] > 0.5]
        for d in DIRECTIONS
    },
    'null_model': {
        'type': 'Bernoulli Monte Carlo',
        'n_trials': 2000,
        'p': round(p_prime, 6),
    },
    'verdicts': {
        'directional_persistence': verdict_persistence,
        'heavy_tailed_runs': verdict_heavy_tail,
        'max_persistence_z': round(max_abs_z, 4),
        'max_heavy_tail_z': round(max_heavy_z, 4),
    },
}

out_path = Path(__file__).parent / 'prime_run_persistence_results.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")
