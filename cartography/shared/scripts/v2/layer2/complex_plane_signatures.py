"""
Complex Plane Signature Extractor (S1) — pole/zero landscape from formula trees.
==================================================================================
Evaluates single-variable formulas on a 50x50 grid in the complex plane and
extracts a topological signature: pole count, zero count, phase winding number,
symmetry under conjugation and negation, and modulus statistics.

    exp(z)       -> n_poles=0, n_zeros=0, winding=0, conj_sym=True
    1/(z^2 + 1)  -> n_poles=2, n_zeros=0, winding=-2, conj_sym=True

Usage:
    python complex_plane_signatures.py                        # full run (10K)
    python complex_plane_signatures.py --max-formulas 1000    # cap input
"""

import argparse
import json
import math
import sys
import time
import warnings
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from formula_to_executable import tree_to_callable

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "complex_plane_signatures.jsonl"

# Grid parameters
GRID_N = 50
GRID_RANGE = 5.0
POLE_THRESHOLD = 1e6
ZERO_THRESHOLD = 1e-6

try:
    import orjson as _json
    def _loads(s):
        return _json.loads(s)
except ImportError:
    _json = json
    _loads = json.loads


# ---------------------------------------------------------------------------
# Complex plane evaluation
# ---------------------------------------------------------------------------

def _build_grid():
    """Build a 50x50 complex grid on [-5,5] x [-5,5]."""
    x = np.linspace(-GRID_RANGE, GRID_RANGE, GRID_N, dtype=np.float32)
    y = np.linspace(-GRID_RANGE, GRID_RANGE, GRID_N, dtype=np.float32)
    xg, yg = np.meshgrid(x, y, indexing='xy')
    z_grid = xg.astype(np.complex64) + 1j * yg.astype(np.complex64)
    return z_grid, x, y


def _evaluate_on_grid(func, variables, z_grid):
    """
    Evaluate func on the complex grid. Returns complex result array.
    The first variable name is mapped to z_grid.
    """
    if not variables:
        return None

    var_name = variables[0]
    var_dict = {var_name: z_grid}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            result = func(var_dict)
        except Exception:
            return None

    # Ensure result is array
    if np.isscalar(result):
        result = np.full_like(z_grid, result)
    else:
        result = np.asarray(result, dtype=np.complex64)

    return result


def _phase_winding(result, z_grid):
    """
    Compute phase winding number around the boundary of the grid.
    Walk the boundary counterclockwise, sum the phase increments.
    """
    n = GRID_N
    # Boundary indices: bottom row, right col, top row reversed, left col reversed
    boundary_idx = []
    # Bottom row (j=0, i=0..n-1)
    for i in range(n):
        boundary_idx.append((0, i))
    # Right col (i=n-1, j=1..n-1)
    for j in range(1, n):
        boundary_idx.append((j, n - 1))
    # Top row reversed (j=n-1, i=n-2..0)
    for i in range(n - 2, -1, -1):
        boundary_idx.append((n - 1, i))
    # Left col reversed (i=0, j=n-2..1)
    for j in range(n - 2, 0, -1):
        boundary_idx.append((j, 0))

    # Extract boundary values
    boundary_vals = []
    for j, i in boundary_idx:
        v = result[j, i]
        if not np.isfinite(v) or abs(v) < 1e-30 or abs(v) > 1e10:
            return float('nan')  # can't compute winding reliably
        boundary_vals.append(v)

    # Compute total phase change
    phases = np.angle(np.array(boundary_vals, dtype=np.complex128))
    dphases = np.diff(phases)

    # Unwrap jumps > pi
    dphases = np.where(dphases > np.pi, dphases - 2 * np.pi, dphases)
    dphases = np.where(dphases < -np.pi, dphases + 2 * np.pi, dphases)

    total_winding = np.sum(dphases) / (2 * np.pi)
    return float(np.round(total_winding))


def _check_symmetry(result, z_grid):
    """
    Check conjugation symmetry f(conj(z)) = conj(f(z)) and
    negation symmetry f(-z) = f(z) or f(-z) = -f(z).
    """
    n = GRID_N
    modulus = np.abs(result)

    # Conjugation: f(conj(z)) vs conj(f(z))
    # conj(z) means flipping y -> -y, i.e. flipping rows
    result_conj_z = result[::-1, :]  # f evaluated at conj(z)
    conj_result = np.conj(result)    # conj(f(z))

    # Mask out poles/zeros for comparison
    good = np.isfinite(result) & np.isfinite(result_conj_z) & (modulus < POLE_THRESHOLD) & (modulus > ZERO_THRESHOLD)
    if np.sum(good) > 100:
        diff_conj = np.abs(result_conj_z[good] - conj_result[good])
        scale = np.abs(result[good]) + 1e-10
        rel_err = np.median(diff_conj / scale)
        has_conj_sym = bool(rel_err < 0.01)
    else:
        has_conj_sym = False

    # Negation: f(-z) vs f(z)
    result_neg_z = result[::-1, ::-1]  # f evaluated at -z (flip both axes)

    if np.sum(good) > 100:
        # Even symmetry: f(-z) = f(z)
        diff_even = np.abs(result_neg_z[good] - result[good])
        rel_even = np.median(diff_even / scale)
        # Odd symmetry: f(-z) = -f(z)
        diff_odd = np.abs(result_neg_z[good] + result[good])
        rel_odd = np.median(diff_odd / scale)
        has_neg_sym = bool(rel_even < 0.01 or rel_odd < 0.01)
    else:
        has_neg_sym = False

    return has_conj_sym, has_neg_sym


def complex_plane_signature(tree, func, variables):
    """
    Extract complex plane signature from a callable formula.
    Returns dict with all signature components, or None.
    """
    z_grid, _, _ = _build_grid()

    result = _evaluate_on_grid(func, variables, z_grid)
    if result is None:
        return None

    # Ensure correct shape
    if result.shape != z_grid.shape:
        try:
            result = np.broadcast_to(result, z_grid.shape).copy()
        except Exception:
            return None

    modulus = np.abs(result)

    # Handle non-finite values
    finite_mask = np.isfinite(modulus)
    if np.sum(finite_mask) < 10:
        return None  # too degenerate

    # Pole count: |f(z)| > threshold
    n_poles = int(np.sum(finite_mask & (modulus > POLE_THRESHOLD)))

    # Zero count: |f(z)| < threshold
    n_zeros = int(np.sum(finite_mask & (modulus < ZERO_THRESHOLD)))

    # Max modulus (excluding poles)
    non_pole = finite_mask & (modulus <= POLE_THRESHOLD)
    if np.any(non_pole):
        max_mod = float(np.max(modulus[non_pole]))
        max_mod_log = float(np.log10(max_mod + 1e-30))
    else:
        max_mod_log = float('nan')

    # Phase winding
    winding = _phase_winding(result, z_grid)

    # Mean phase (excluding poles/zeros)
    good = finite_mask & (modulus > ZERO_THRESHOLD) & (modulus < POLE_THRESHOLD)
    if np.sum(good) > 10:
        phases = np.angle(result[good].astype(np.complex128))
        mean_phase = float(np.mean(phases))
    else:
        mean_phase = float('nan')

    # Symmetry checks
    has_conj_sym, has_neg_sym = _check_symmetry(result, z_grid)

    return {
        "hash": tree.get("hash", ""),
        "n_poles": n_poles,
        "n_zeros": n_zeros,
        "phase_winding": winding if not math.isnan(winding) else None,
        "max_modulus_log": round(max_mod_log, 4) if not math.isnan(max_mod_log) else None,
        "has_conjugate_symmetry": has_conj_sym,
        "has_negation_symmetry": has_neg_sym,
        "mean_phase": round(mean_phase, 6) if not math.isnan(mean_phase) else None,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="S1: Complex plane signature extraction for formula trees"
    )
    parser.add_argument("--max-formulas", type=int, default=10000,
                        help="Max single-variable formulas to process (default: 10000)")
    args = parser.parse_args()

    print("=" * 70)
    print("S1: Complex Plane Signatures")
    print("=" * 70)

    if not TREES_FILE.exists():
        print(f"  ERROR: formula trees not found at {TREES_FILE}")
        return

    t0 = time.time()
    n_total = 0
    n_single_var = 0
    n_converted = 0
    n_ok = 0
    n_fail = 0
    n_multi_var = 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(TREES_FILE, "r", encoding="utf-8") as fin, \
         open(OUT_FILE, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_total += 1

            # Progress
            if n_total % 10000 == 0 or n_total == 1:
                elapsed = time.time() - t0
                rate = n_total / elapsed if elapsed > 0 else 0
                print(f"  [scanned {n_total:>8}] "
                      f"single_var={n_single_var} converted={n_converted} "
                      f"sigs={n_ok} fail={n_fail} ({rate:.0f} trees/s)")

            # Stop if we have enough signatures
            if n_ok >= args.max_formulas:
                break

            try:
                tree = _loads(line)
            except (json.JSONDecodeError, ValueError):
                continue

            # Quick filter: check n_variables if present in metadata
            n_vars_meta = tree.get("n_variables")
            if n_vars_meta is not None and n_vars_meta != 1:
                n_multi_var += 1
                continue

            # Convert to callable
            try:
                func, variables, success = tree_to_callable(tree)
            except Exception:
                continue

            if not success or func is None:
                continue

            n_converted += 1

            # Filter: single variable only
            if len(variables) != 1:
                n_multi_var += 1
                continue

            n_single_var += 1

            # Extract signature
            try:
                sig = complex_plane_signature(tree, func, variables)
                if sig is not None:
                    fout.write(json.dumps(sig) + "\n")
                    n_ok += 1
                else:
                    n_fail += 1
            except Exception:
                n_fail += 1

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")
    print(f"  Trees scanned: {n_total:,}")
    print(f"  Single-variable: {n_single_var:,}, multi-variable skipped: {n_multi_var:,}")
    print(f"  Successfully converted: {n_converted:,}")
    print(f"  Signatures: {n_ok:,} ok, {n_fail:,} failed")
    print(f"  Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
