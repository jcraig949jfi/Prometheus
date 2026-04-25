"""Recipe 4: Vietoris-Rips persistence directly from a distance matrix.

Many real-world inputs come not as point coordinates but as a precomputed
pairwise dissimilarity matrix: graph distances, edit distances, dynamic
time-warping distances, correlation-based distances on time series, ...

This recipe demonstrates that the Vietoris-Rips persistence is fully
specified by such a matrix -- no ambient embedding required.

Mathematical reference
----------------------
de Silva & Ghrist, "Coverage in sensor networks via persistent homology",
Algebraic & Geometric Topology 7 (2007), Section 2.1 -- Rips complex
directly on a metric space.
"""

from __future__ import annotations

import math

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def graph_metric_cycle(n: int) -> np.ndarray:
    """Distance matrix of the n-cycle graph (vertices ``0..n-1``).

    Edges connect ``i`` to ``i+1 mod n`` with unit weight, so
    ``D[i, j] = min(|i - j|, n - |i - j|)``.  The cycle has H_0 = 1 and
    H_1 = 1, so we expect one infinite H_0 bar and one significant H_1 bar.
    """
    idx = np.arange(n)
    diff = np.abs(idx[:, None] - idx[None, :])
    return np.minimum(diff, n - diff).astype(float)


def main(n: int = 24) -> dict:
    """Run Rips persistence on the cycle-graph distance matrix."""
    D = graph_metric_cycle(n)

    # Sanity: symmetric, non-negative, zero diagonal.
    assert np.allclose(D, D.T)
    assert np.all(D >= 0)
    assert np.all(np.diag(D) == 0)

    # max_edge_length = n/2 ensures the loop closes (longest cycle distance).
    diag = pha.persistence_diagram_from_distmat(
        D, max_dim=1, max_edge_length=float(n)
    )

    h1 = [(b, x) for d, (b, x) in diag if d == 1 and not math.isinf(x)]
    h1.sort(key=lambda bx: -(bx[1] - bx[0]))
    betti = pha.betti_numbers_from_diagram(diag)

    print("distance_matrix_to_diagram.py -- Rips on cycle-graph distances")
    print(f"  n_vertices            = {n}")
    print(f"  betti numbers         = {betti}")
    print(f"  top H1 bar            = {h1[0] if h1 else 'none'}")
    print(f"  number H1 bars        = {len(h1)}")

    # The cycle graph has exactly one persistent H_1 class.
    assert betti.get(0, 0) == 1, "expected beta_0 = 1 for connected graph"

    return {
        "diagram": diag,
        "betti": betti,
        "top_H1": h1[0] if h1 else None,
        "n_H1_bars": len(h1),
    }


if __name__ == "__main__":
    main()
