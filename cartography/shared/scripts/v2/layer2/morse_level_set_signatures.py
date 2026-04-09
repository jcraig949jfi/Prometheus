"""
Morse / Level Set Signatures — topological invariants from function sweeps.
============================================================================
Strategy S8: for evaluable single-variable formulas, sweep a threshold and
track topology changes (connected components where f(x) >= c).

The "Betti curve" records n_components as a function of threshold, giving a
topological fingerprint of the function's landscape.

Usage:
    python morse_level_set_signatures.py
    python morse_level_set_signatures.py --max-formulas 50000
    python morse_level_set_signatures.py --sample 10000
"""

import argparse
import json
import random
import sys
import time
import warnings
import numpy as np
from math import isfinite, log2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from formula_to_executable import tree_to_callable

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "morse_level_set_signatures.jsonl"

N_GRID = 200
N_THRESHOLDS = 20


# ── Level set topology analysis ───────────────────────────────────────────

def count_components_above(vals, threshold):
    """Count connected intervals where vals >= threshold.
    vals is a 1D array of function evaluations on a uniform grid.
    """
    above = vals >= threshold
    if not np.any(above):
        return 0
    # Count transitions from False->True (start of a connected component)
    changes = np.diff(above.astype(int))
    n_starts = np.sum(changes == 1)
    # If the first point is above, that's an extra component start
    if above[0]:
        n_starts += 1
    return int(n_starts)


def compute_morse_signature(f_vals, thresholds):
    """Compute the Betti curve and derived invariants.

    f_vals: 1D array of function evaluations
    thresholds: array of threshold values to sweep

    Returns dict with signature or None.
    """
    betti_curve = []
    for c in thresholds:
        nc = count_components_above(f_vals, c)
        betti_curve.append(nc)

    betti_arr = np.array(betti_curve)

    max_components = int(np.max(betti_arr))
    if max_components == 0:
        return None

    # Threshold at which max components is achieved (first occurrence)
    max_idx = int(np.argmax(betti_arr))
    threshold_at_max = float(thresholds[max_idx])

    # Betti curve entropy: treat normalized betti curve as a distribution
    betti_pos = betti_arr[betti_arr > 0].astype(float)
    if len(betti_pos) > 0:
        betti_norm = betti_pos / betti_pos.sum()
        entropy = float(-np.sum(betti_norm * np.log2(betti_norm + 1e-30)))
    else:
        entropy = 0.0

    # Critical values: thresholds where n_components changes
    changes = np.diff(betti_arr)
    critical_indices = np.where(changes != 0)[0]
    n_critical = len(critical_indices)

    return {
        "max_components": max_components,
        "threshold_at_max": threshold_at_max,
        "betti_curve_entropy": entropy,
        "n_critical_values": int(n_critical),
        "betti_curve": betti_arr.tolist(),
    }


# ── JSON encoder ──────────────────────────────────────────────────────────

class _Enc(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, cls=_Enc) + "\n")
    print(f"  Wrote {len(records):,} records -> {path}")


# ── Main ──────────────────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("Morse / Level Set Signatures (S8)")
    print("=" * 70)

    print(f"\n  Loading formula trees from {TREES_FILE.name} ...")
    if not TREES_FILE.exists():
        print(f"  ERROR: {TREES_FILE} not found")
        return

    trees = []
    with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                trees.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if max_formulas and len(trees) >= max_formulas:
                break
    print(f"  Loaded {len(trees):,} formula trees")

    if sample_n and sample_n < len(trees):
        random.seed(42)
        trees = random.sample(trees, sample_n)
        print(f"  Sampled {len(trees):,} trees")

    x_grid = np.linspace(-10, 10, N_GRID)
    results = []
    n_evaluable = 0
    n_sig = 0
    n_err = 0

    for i, tree in enumerate(trees):
        if (i + 1) % 50000 == 0:
            elapsed = time.time() - t0
            print(f"  ... {i+1:,}/{len(trees):,} processed, "
                  f"{n_evaluable} evaluable, {n_sig} sigs  ({elapsed:.1f}s)")

        h = tree.get("hash", "")

        # Convert to callable
        fn, variables, ok = tree_to_callable(tree)
        if not ok or fn is None:
            continue

        # Only single-variable formulas
        if len(variables) != 1:
            continue

        var_name = variables[0]
        n_evaluable += 1

        # Evaluate on grid
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                f_vals = np.array([
                    fn({var_name: float(x)}) for x in x_grid
                ], dtype=np.float64)
        except Exception:
            n_err += 1
            continue

        # Check for valid values
        finite_mask = np.isfinite(f_vals)
        if np.sum(finite_mask) < N_GRID // 2:
            continue

        # Replace non-finite with NaN for threshold sweep
        f_clean = np.where(finite_mask, f_vals, np.nan)
        f_min = float(np.nanmin(f_clean))
        f_max = float(np.nanmax(f_clean))

        if not isfinite(f_min) or not isfinite(f_max):
            continue
        if abs(f_max - f_min) < 1e-15:
            continue  # constant function

        # Replace NaN with f_min - 1 so they don't count as above threshold
        f_for_sweep = np.where(finite_mask, f_vals, f_min - 1.0)

        thresholds = np.linspace(f_min, f_max, N_THRESHOLDS)
        sig = compute_morse_signature(f_for_sweep, thresholds)
        if sig is None:
            continue

        n_sig += 1
        results.append({
            "id": h,
            "source": "formula",
            "variable": var_name,
            "f_range": [f_min, f_max],
            **sig,
        })

    write_jsonl(OUT_SIGS, results)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Total trees:   {len(trees):,}")
    print(f"  Evaluable:     {n_evaluable:,}")
    print(f"  Eval errors:   {n_err:,}")
    print(f"  Signatures:    {n_sig:,}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description="S8: Morse / level set signatures from single-variable formulas"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
