"""OpenEvolve Problem Definition — initial program for evolving mathematical
search functions.

This file contains the seed search function with EVOLVE-BLOCK markers.
OpenEvolve will mutate the code inside the markers while preserving the
interface contract: ``search_function(values_a, values_b) -> dict``.

Run with OpenEvolve:
    from openevolve import run_evolution
    result = run_evolution(
        initial_program="openevolve_problem.py",
        evaluator="openevolve_evaluator.py",
        iterations=200,
    )
"""

import numpy as np
from scipy import stats


# EVOLVE-BLOCK-START
def search_function(values_a, values_b):
    """Search for structural connection between two numerical datasets.

    Args:
        values_a: First dataset (list or array of floats).
        values_b: Second dataset (list or array of floats).

    Returns:
        dict with keys:
            statistic   — float, the test statistic (higher = stronger signal)
            p_value     — float, probability under the null hypothesis
            description — str, human-readable summary of what was found
    """
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    n = min(len(a), len(b))

    if n < 10:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}

    a, b = a[:n], b[:n]

    # Pearson correlation as baseline signal detector
    r, p = stats.pearsonr(a, b)

    return {
        "statistic": float(r),
        "p_value": float(p),
        "description": f"Pearson r={r:.4f}, p={p:.2e}",
    }
# EVOLVE-BLOCK-END


if __name__ == "__main__":
    # Quick sanity check
    rng = np.random.RandomState(42)
    va = rng.randn(100)
    vb = 0.5 * va + 0.5 * rng.randn(100)
    result = search_function(va.tolist(), vb.tolist())
    print(f"Self-test: {result}")
