"""Recipe 3: Vietoris-Rips on a torus, recovering Betti numbers (1, 2, 1).

The 2-torus T^2 has Betti numbers beta_0 = 1, beta_1 = 2, beta_2 = 1.
We sample T^2 as the surface of revolution {((R + r cos v) cos u,
(R + r cos v) sin u, r sin v)} in R^3, run Vietoris-Rips up to H_2, and
identify the two long H_1 bars and the one long H_2 bar.

Mathematical reference
----------------------
Hatcher, *Algebraic Topology* (CUP 2002), Example 2.41 (Betti numbers of
T^n).  See also Adams & Tausz, "JavaPlex Tutorial" (Stanford 2014),
Section 8 -- the standard "torus test" example for persistent homology.
"""

from __future__ import annotations

import math

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def sample_torus(n: int, R: float = 2.0, r: float = 1.0, seed: int = 1) -> np.ndarray:
    """Quasi-uniform sample on a torus surface in R^3.

    Uses rejection on the area Jacobian ``R + r cos v`` to avoid the
    over-sampling artefact that uniform (u, v) gives.  Returns an (n, 3)
    array of points on the torus.
    """
    rng = np.random.default_rng(seed)
    out = np.empty((n, 3), dtype=float)
    M = R + r  # max of jacobian (when cos v = 1)
    i = 0
    while i < n:
        u = rng.uniform(0.0, 2 * np.pi)
        v = rng.uniform(0.0, 2 * np.pi)
        if rng.uniform(0.0, M) <= R + r * np.cos(v):
            out[i, 0] = (R + r * np.cos(v)) * np.cos(u)
            out[i, 1] = (R + r * np.cos(v)) * np.sin(u)
            out[i, 2] = r * np.sin(v)
            i += 1
    return out


def main(n: int = 300, seed: int = 1) -> dict:
    """Run the torus Betti recipe.

    Note: full H_2 on a torus needs a few hundred points; we use 300 by
    default.  The Rips edge-length is bounded so the simplex tree stays
    manageable.
    """
    pts = sample_torus(n, seed=seed)
    diag = pha.rips_persistence(pts, max_dim=2, max_edge_length=2.0)

    # Buckets per dimension, sorted by persistence descending.
    def by_dim(d):
        bars = [(b, x) for dd, (b, x) in diag if dd == d and not math.isinf(x)]
        bars.sort(key=lambda bx: -(bx[1] - bx[0]))
        return bars

    h0 = by_dim(0)
    h1 = by_dim(1)
    h2 = by_dim(2)

    # On a torus we expect: 1 long H_0 (infinite, not in `h0`), 2 long H_1, 1 long H_2.
    threshold = 0.5
    n_h1_long = sum(1 for b, x in h1 if (x - b) > threshold)
    n_h2_long = sum(1 for b, x in h2 if (x - b) > threshold)

    betti = pha.betti_numbers_from_diagram(diag)

    print("rip_torus.py -- Vietoris-Rips on a sampled torus")
    print(f"  n_points              = {n}")
    print(f"  betti numbers (full)  = {betti}")
    print(f"  top 3 H1 bars         = {h1[:3]}")
    print(f"  top 3 H2 bars         = {h2[:3]}")
    print(f"  H1 bars > {threshold} pers = {n_h1_long}")
    print(f"  H2 bars > {threshold} pers = {n_h2_long}")

    return {
        "diagram": diag,
        "betti": betti,
        "n_h1_long": int(n_h1_long),
        "n_h2_long": int(n_h2_long),
        "top_h1": h1[:3],
        "top_h2": h2[:3],
    }


if __name__ == "__main__":
    main()
