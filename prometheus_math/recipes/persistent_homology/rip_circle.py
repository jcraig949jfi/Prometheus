"""Recipe 2: Vietoris-Rips on a noisy circle, demonstrating H_1 = 1.

Samples a noisy unit circle, builds the Vietoris-Rips filtration up to
dimension 1, and verifies that exactly one long-lived H_1 bar shows up --
the loop that gives a circle its non-trivial first Betti number.

Mathematical reference
----------------------
Carlsson, "Topology and Data", Bull. AMS 46 (2009), Section 5 (the
"circle test").  H_1(S^1) = Z, so the persistence diagram of a sufficiently
dense, sufficiently low-noise sample of S^1 must contain exactly one bar
of large persistence in dimension 1.
"""

from __future__ import annotations

import math
import os

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def sample_noisy_circle(n: int, noise: float, seed: int) -> np.ndarray:
    """Return ``n`` points sampled uniformly on the unit circle, plus noise."""
    rng = np.random.default_rng(seed)
    theta = 2.0 * np.pi * rng.uniform(0.0, 1.0, size=n)
    pts = np.stack([np.cos(theta), np.sin(theta)], axis=1)
    return pts + rng.normal(scale=noise, size=pts.shape)


def main(n: int = 100, noise: float = 0.05, seed: int = 0) -> dict:
    """Run the noisy-circle recipe.

    Returns the diagram and the persistence (death - birth) of the longest
    H_1 bar.  Asserts that this exceeds 0.5 -- the canonical Carlsson test.
    """
    pts = sample_noisy_circle(n, noise, seed)
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5)

    # Pick the longest H_1 bar (the "true" loop).
    h1 = [(b, x) for d, (b, x) in diag if d == 1 and not math.isinf(x)]
    h1.sort(key=lambda bx: -(bx[1] - bx[0]))

    if not h1:
        raise RuntimeError(
            "no finite H_1 bar found; check noise / max_edge_length"
        )
    top_birth, top_death = h1[0]
    top_persistence = top_death - top_birth

    # Number of "clearly significant" loops at a 0.5 persistence threshold.
    n_significant_loops = sum(1 for b, x in h1 if (x - b) > 0.5)

    betti = pha.betti_numbers_from_diagram(diag)

    print("rip_circle.py -- noisy unit circle")
    print(f"  n_points              = {n}")
    print(f"  noise sigma           = {noise}")
    print(f"  betti numbers         = {betti}")
    print(f"  top H1 bar            = ({top_birth:.4f}, {top_death:.4f})")
    print(f"  top H1 persistence    = {top_persistence:.4f}")
    print(f"  loops above 0.5 pers  = {n_significant_loops}")

    # Sanity assertion: noisy S^1 must have exactly one significant loop.
    assert n_significant_loops == 1, (
        f"expected 1 significant H_1 loop, found {n_significant_loops}"
    )

    return {
        "diagram": diag,
        "betti": betti,
        "top_H1": (top_birth, top_death),
        "top_H1_persistence": float(top_persistence),
        "n_significant_loops": int(n_significant_loops),
    }


if __name__ == "__main__":
    main()
