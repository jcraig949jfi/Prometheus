#!/usr/bin/env python3
"""
Q4: Permutation Null Test on Diagonal Prime Clustering.

Maps integers 1..N^2 to a 2D grid (row-major and Ulam spiral),
marks prime positions, and tests whether diagonal/line clustering
is significant via permutation null (10,000 shuffles).

Tests:
  1. Row-major grid: main diagonals (slope=1, slope=-1)
  2. Row-major grid: specific slopes (2, 1/2, 3, 1/3)
  3. Ulam spiral: line clustering along rows, cols, diagonals
"""

import json
import numpy as np
from sympy import isprime
from pathlib import Path
from collections import defaultdict

SEED = 42
N = 100
N_PERM = 10_000


def make_prime_mask(mapping):
    """Given a mapping from grid positions to integers, return boolean mask of primes."""
    mask = np.zeros((N, N), dtype=bool)
    for (r, c), val in mapping.items():
        if isprime(val):
            mask[r, c] = True
    return mask


def rowmajor_mapping():
    """Integer k -> (row=k//N, col=k%N) for k in 1..N^2."""
    m = {}
    for k in range(1, N * N + 1):
        r, c = (k - 1) // N, (k - 1) % N
        m[(r, c)] = k
    return m


def ulam_spiral_mapping():
    """Map integers 1..N^2 via Ulam spiral from center."""
    grid = {}
    cx, cy = N // 2, N // 2
    x, y = cx, cy
    grid[(y, x)] = 1
    num = 2
    step = 1
    while num <= N * N:
        for dx, dy, count in [(1, 0, step), (0, -1, step),
                               (-1, 0, step + 1), (0, 1, step + 1)]:
            for _ in range(count):
                x += dx
                y += dy
                if 0 <= x < N and 0 <= y < N and num <= N * N:
                    grid[(y, x)] = num
                num += 1
                if num > N * N:
                    break
            if num > N * N:
                break
        step += 2
    return grid


def get_diagonal_sets(N):
    """Return dict of diagonal-name -> set of (r,c) positions."""
    diags = {}

    # Main diagonal slope=1: r == c
    diags["slope_1"] = {(i, i) for i in range(N)}

    # Anti-diagonal slope=-1: r + c == N-1
    diags["slope_-1"] = {(i, N - 1 - i) for i in range(N)}

    # All slope=1 diagonals (parallel to main)
    s1 = set()
    for d in range(-(N - 1), N):
        for i in range(N):
            j = i - d
            if 0 <= j < N:
                s1.add((i, j))
    diags["all_slope_1"] = s1

    # All slope=-1 diagonals
    sm1 = set()
    for s in range(2 * N - 1):
        for i in range(N):
            j = s - i
            if 0 <= j < N:
                sm1.add((i, j))
    diags["all_slope_-1"] = sm1

    return diags


def get_slope_sets(N, slope):
    """
    For a rational slope p/q, collect all grid positions on lines
    with that slope. Line: r = (p/q)*c + b for varying b.
    We discretize: for each starting column, step by (q, p).
    """
    from fractions import Fraction
    f = Fraction(slope).limit_denominator(100)
    p, q = f.numerator, f.denominator
    positions = set()
    # Start from every possible origin
    for r0 in range(N):
        for c0 in range(N):
            # Check if (r0, c0) is on a line of this slope
            # Walk the line through (r0,c0)
            r, c = r0, c0
            on_line = []
            while 0 <= r < N and 0 <= c < N:
                on_line.append((r, c))
                r += p
                c += q
            if len(on_line) >= 2:
                for pos in on_line:
                    positions.add(pos)
    return positions


def get_line_positions_ulam(N):
    """For Ulam spiral, return positions on rows, columns, and both diagonals."""
    lines = {}
    # Rows
    row_pos = set()
    for r in range(N):
        for c in range(N):
            row_pos.add((r, c))
    lines["rows"] = row_pos  # trivially all, but we test line-by-line

    # For Ulam, the interesting thing is specific lines through center
    cx, cy = N // 2, N // 2

    # Horizontal line through center
    lines["center_row"] = {(cy, c) for c in range(N)}
    # Vertical line through center
    lines["center_col"] = {(r, cx) for r in range(N)}
    # Main diagonal through center
    lines["center_diag1"] = set()
    for d in range(-(N - 1), N):
        r, c = cy + d, cx + d
        if 0 <= r < N and 0 <= c < N:
            lines["center_diag1"].add((r, c))
    # Anti-diagonal through center
    lines["center_diag2"] = set()
    for d in range(-(N - 1), N):
        r, c = cy + d, cx - d
        if 0 <= r < N and 0 <= c < N:
            lines["center_diag2"].add((r, c))

    # All diagonals (slope=1 and slope=-1)
    lines["all_diag1"] = {(i, j) for i in range(N) for j in range(N) if True}  # placeholder
    # Better: collect by diagonal index
    d1 = set()
    for i in range(N):
        for j in range(N):
            d1.add((i, j))
    # That's everything. Instead, let's do lines of length >= 5
    # For Ulam, we test specific geometric lines
    return lines


def fraction_on_positions(mask, positions):
    """Fraction of primes that fall on given positions."""
    total_primes = mask.sum()
    if total_primes == 0:
        return 0.0
    on_count = sum(1 for (r, c) in positions if mask[r, c])
    return on_count / total_primes


def fraction_on_positions_vs_expected(mask, positions):
    """Return (observed_fraction, expected_fraction_by_area)."""
    total_primes = int(mask.sum())
    total_cells = N * N
    n_on = sum(1 for (r, c) in positions if mask[r, c])
    n_positions = len(positions)
    obs_frac = n_on / total_primes if total_primes > 0 else 0
    exp_frac = n_positions / total_cells
    return obs_frac, exp_frac, n_on, total_primes


def permutation_test(mask, positions, n_perm, rng):
    """
    Shuffle prime/composite labels on the grid, recompute fraction on positions.
    Return array of null fractions.
    """
    flat = mask.flatten().copy()
    total_primes = flat.sum()
    n_pos = len(positions)
    pos_indices = np.array([r * N + c for (r, c) in positions])

    null_counts = np.zeros(n_perm)
    for i in range(n_perm):
        rng.shuffle(flat)
        null_counts[i] = flat[pos_indices].sum()

    null_fracs = null_counts / total_primes
    return null_fracs


def compute_z(obs, null_dist):
    """Z-score of observation vs null distribution."""
    mu = null_dist.mean()
    sigma = null_dist.std()
    if sigma == 0:
        return 0.0
    return (obs - mu) / sigma


def run_rowmajor_tests(rng):
    """Run all row-major grid tests."""
    print("=== Row-Major Grid Tests ===")
    mapping = rowmajor_mapping()
    mask = make_prime_mask(mapping)
    total_primes = int(mask.sum())
    print(f"  Grid: {N}x{N}, Total primes in 1..{N*N}: {total_primes}")

    results = {"grid": "row_major", "N": N, "total_primes": total_primes, "tests": {}}

    # Test 1: Main diagonals
    diag_sets = get_diagonal_sets(N)

    for name in ["slope_1", "slope_-1"]:
        positions = diag_sets[name]
        obs_frac, exp_frac, n_on, _ = fraction_on_positions_vs_expected(mask, positions)
        null_fracs = permutation_test(mask, positions, N_PERM, rng)
        z = compute_z(obs_frac, null_fracs)
        p_val = (null_fracs >= obs_frac).mean()

        print(f"\n  {name}: {n_on}/{total_primes} primes on {len(positions)} cells")
        print(f"    Observed fraction: {obs_frac:.6f}, Expected: {exp_frac:.6f}")
        print(f"    z={z:.2f}, p={p_val:.4f}")

        results["tests"][name] = {
            "n_positions": len(positions),
            "primes_on_line": n_on,
            "obs_fraction": round(obs_frac, 6),
            "exp_fraction": round(exp_frac, 6),
            "enrichment": round(obs_frac / exp_frac, 4) if exp_frac > 0 else None,
            "z_score": round(z, 4),
            "p_value": round(float(p_val), 6),
            "significant": abs(z) > 3
        }

    # Test 2: Specific slopes
    for slope, label in [(2, "slope_2"), (0.5, "slope_1over2"), (3, "slope_3"), (1/3, "slope_1over3")]:
        slope_name = label
        positions = get_slope_sets(N, slope)
        if not positions:
            print(f"\n  {slope_name}: no positions found, skipping")
            continue
        obs_frac, exp_frac, n_on, _ = fraction_on_positions_vs_expected(mask, positions)
        null_fracs = permutation_test(mask, positions, N_PERM, rng)
        z = compute_z(obs_frac, null_fracs)
        p_val = (null_fracs >= obs_frac).mean()

        print(f"\n  {slope_name}: {n_on}/{total_primes} primes on {len(positions)} cells")
        print(f"    Observed fraction: {obs_frac:.6f}, Expected: {exp_frac:.6f}")
        print(f"    z={z:.2f}, p={p_val:.4f}")

        results["tests"][slope_name] = {
            "n_positions": len(positions),
            "primes_on_line": n_on,
            "obs_fraction": round(obs_frac, 6),
            "exp_fraction": round(exp_frac, 6),
            "enrichment": round(obs_frac / exp_frac, 4) if exp_frac > 0 else None,
            "z_score": round(z, 4),
            "p_value": round(float(p_val), 6),
            "significant": abs(z) > 3
        }

    return results


def run_ulam_tests(rng):
    """Run Ulam spiral grid tests."""
    print("\n=== Ulam Spiral Grid Tests ===")
    mapping = ulam_spiral_mapping()
    mask = make_prime_mask(mapping)
    total_primes = int(mask.sum())
    print(f"  Grid: {N}x{N}, Total primes mapped: {total_primes}")

    results = {"grid": "ulam_spiral", "N": N, "total_primes": total_primes, "tests": {}}

    # Test lines through center
    cx, cy = N // 2, N // 2
    line_defs = {
        "center_row": [(cy, c) for c in range(N)],
        "center_col": [(r, cx) for r in range(N)],
        "center_diag_slope1": [(cy + d, cx + d) for d in range(-(N-1), N) if 0 <= cy+d < N and 0 <= cx+d < N],
        "center_diag_slope-1": [(cy + d, cx - d) for d in range(-(N-1), N) if 0 <= cy+d < N and 0 <= cx-d < N],
    }

    # Also test ALL diagonals (not just center)
    all_diag1_pos = set()
    for offset in range(-(N-1), N):
        line = [(i, i + offset) for i in range(N) if 0 <= i + offset < N]
        if len(line) >= 3:
            all_diag1_pos.update(line)

    all_diag_m1_pos = set()
    for s in range(2 * N - 1):
        line = [(i, s - i) for i in range(N) if 0 <= s - i < N]
        if len(line) >= 3:
            all_diag_m1_pos.update(line)

    line_defs["all_slope1_diags"] = list(all_diag1_pos)
    line_defs["all_slope-1_diags"] = list(all_diag_m1_pos)

    for name, pos_list in line_defs.items():
        positions = set(pos_list)
        if not positions:
            continue
        obs_frac, exp_frac, n_on, _ = fraction_on_positions_vs_expected(mask, positions)
        null_fracs = permutation_test(mask, positions, N_PERM, rng)
        z = compute_z(obs_frac, null_fracs)
        p_val = (null_fracs >= obs_frac).mean()

        print(f"\n  {name}: {n_on}/{total_primes} primes on {len(positions)} cells")
        print(f"    Observed fraction: {obs_frac:.6f}, Expected: {exp_frac:.6f}")
        print(f"    z={z:.2f}, p={p_val:.4f}")

        results["tests"][name] = {
            "n_positions": len(positions),
            "primes_on_line": n_on,
            "obs_fraction": round(obs_frac, 6),
            "exp_fraction": round(exp_frac, 6),
            "enrichment": round(obs_frac / exp_frac, 4) if exp_frac > 0 else None,
            "z_score": round(z, 4),
            "p_value": round(float(p_val), 6),
            "significant": abs(z) > 3
        }

    # Ulam-specific: test along specific polynomial lines
    # Euler's n^2+n+41 — find which cells these primes land on
    euler_primes = set()
    for n in range(0, 100):
        val = n * n + n + 41
        if val <= N * N and isprime(val):
            euler_primes.add(val)

    # Find grid positions of these primes
    inv_map = {v: k for k, v in mapping.items()}
    euler_positions = set()
    for val in euler_primes:
        if val in inv_map:
            euler_positions.add(inv_map[val])

    if euler_positions:
        obs_frac, exp_frac, n_on, _ = fraction_on_positions_vs_expected(mask, euler_positions)
        # For this special set, the null is: pick len(euler_positions) random cells,
        # how many are prime?
        null_fracs = permutation_test(mask, euler_positions, N_PERM, rng)
        z = compute_z(obs_frac, null_fracs)
        p_val = (null_fracs >= obs_frac).mean()

        name = "euler_n2_n_41"
        print(f"\n  {name}: {n_on}/{total_primes} primes on {len(euler_positions)} cells")
        print(f"    Observed fraction: {obs_frac:.6f}, Expected: {exp_frac:.6f}")
        print(f"    z={z:.2f}, p={p_val:.4f}")

        results["tests"][name] = {
            "n_positions": len(euler_positions),
            "primes_on_line": n_on,
            "obs_fraction": round(obs_frac, 6),
            "exp_fraction": round(exp_frac, 6),
            "enrichment": round(obs_frac / exp_frac, 4) if exp_frac > 0 else None,
            "z_score": round(z, 4),
            "p_value": round(float(p_val), 6),
            "significant": abs(z) > 3,
            "note": "Euler prime-generating polynomial positions in Ulam grid"
        }

    return results


def summarize(rowmajor_results, ulam_results):
    """Build final summary."""
    all_tests = {}
    for res in [rowmajor_results, ulam_results]:
        grid = res["grid"]
        for name, data in res["tests"].items():
            all_tests[f"{grid}/{name}"] = data

    n_sig = sum(1 for v in all_tests.values() if v.get("significant"))
    n_total = len(all_tests)

    verdict = "ARTIFACT" if n_sig == 0 else "MIXED" if n_sig < n_total else "SIGNIFICANT"
    if n_sig > 0:
        sig_names = [k for k, v in all_tests.items() if v.get("significant")]
        # Check if ALL significant ones have enrichment near 1.0
        enrichments = [all_tests[k]["enrichment"] for k in sig_names if all_tests[k]["enrichment"]]
        if all(0.95 <= e <= 1.05 for e in enrichments):
            verdict = "ARTIFACT (significant but no enrichment)"

    summary = {
        "verdict": verdict,
        "n_tests": n_total,
        "n_significant_z3": n_sig,
        "significant_tests": [k for k, v in all_tests.items() if v.get("significant")],
        "interpretation": (
            "Diagonal clustering on row-major grids is an artifact of integer growth rates — "
            "primes thin out as integers grow, creating non-uniform density that mimics geometric "
            "structure. The permutation null (which preserves prime count but destroys spatial "
            "correlation with integer value) is the correct control."
            if verdict.startswith("ARTIFACT") else
            "Some geometric lines show significant prime clustering beyond the permutation null. "
            "Check enrichment values to distinguish real structure from density artifacts."
        )
    }

    return summary


def main():
    rng = np.random.default_rng(SEED)

    rowmajor_results = run_rowmajor_tests(rng)
    ulam_results = run_ulam_tests(rng)
    summary = summarize(rowmajor_results, ulam_results)

    print("\n=== SUMMARY ===")
    print(f"  Verdict: {summary['verdict']}")
    print(f"  Tests: {summary['n_tests']}, Significant (|z|>3): {summary['n_significant_z3']}")
    if summary['significant_tests']:
        print(f"  Significant: {summary['significant_tests']}")
    print(f"  Interpretation: {summary['interpretation']}")

    output = {
        "experiment": "Q4_diagonal_prime_clustering_permutation_null",
        "parameters": {"N": N, "n_permutations": N_PERM, "seed": SEED},
        "row_major": rowmajor_results,
        "ulam_spiral": ulam_results,
        "summary": summary
    }

    out_path = Path(__file__).parent / "grid_prime_null_results.json"

    def convert(obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} not serializable")

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=convert)
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
