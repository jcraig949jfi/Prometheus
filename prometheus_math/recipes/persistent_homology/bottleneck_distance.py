"""Recipe 5: Bottleneck distance between persistence diagrams.

The bottleneck distance is the L-infinity earth-mover distance between two
persistence diagrams, with the unit diagonal added as a "free sink".  It is
the most-used stability metric in TDA: small perturbations of the input
imply small bottleneck perturbation of the diagram (Cohen-Steiner et al.).

This recipe demonstrates the metric on the canonical pair: a noisy circle
versus an ideal circle.

Mathematical reference
----------------------
Cohen-Steiner, Edelsbrunner & Harer, "Stability of persistence diagrams",
Discrete & Computational Geometry 37 (2007).
"""

from __future__ import annotations

import math

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def _ideal_circle(n: int = 100) -> np.ndarray:
    theta = 2 * np.pi * np.linspace(0.0, 1.0, n, endpoint=False)
    return np.stack([np.cos(theta), np.sin(theta)], axis=1)


def _noisy_circle(n: int, noise: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pts = _ideal_circle(n)
    return pts + rng.normal(scale=noise, size=pts.shape)


def main(n: int = 100, noise: float = 0.05, seed: int = 0) -> dict:
    """Run the bottleneck-distance recipe on the circle pair."""
    pts_ideal = _ideal_circle(n)
    pts_noisy = _noisy_circle(n, noise, seed)

    diag_ideal = pha.rips_persistence(pts_ideal, max_dim=1, max_edge_length=2.5)
    diag_noisy = pha.rips_persistence(pts_noisy, max_dim=1, max_edge_length=2.5)

    bn_h0 = pha.bottleneck_distance(diag_ideal, diag_noisy, dim=0)
    bn_h1 = pha.bottleneck_distance(diag_ideal, diag_noisy, dim=1)

    # Self-distances are zero; useful sanity check.
    bn_self = pha.bottleneck_distance(diag_ideal, diag_ideal, dim=1)

    # Cohen-Steiner stability says bottleneck <= 2 * Hausdorff distance of inputs.
    haus = float(
        max(
            np.min(np.linalg.norm(pts_ideal[:, None, :] - pts_noisy[None, :, :], axis=-1), axis=1).max(),
            np.min(np.linalg.norm(pts_noisy[:, None, :] - pts_ideal[None, :, :], axis=-1), axis=1).max(),
        )
    )

    print("bottleneck_distance.py -- noisy vs ideal circle")
    print(f"  n                     = {n}")
    print(f"  noise sigma           = {noise}")
    print(f"  bottleneck H_0        = {bn_h0:.6f}")
    print(f"  bottleneck H_1        = {bn_h1:.6f}")
    print(f"  bottleneck self       = {bn_self:.6f}")
    print(f"  hausdorff (data)      = {haus:.6f}")
    print(f"  stability check       = bn(H_1) <= 2 * Hausdorff -> {bn_h1 <= 2*haus + 1e-9}")

    assert bn_self < 1e-6, "bottleneck(d, d) should be ~0"

    return {
        "bn_h0": float(bn_h0),
        "bn_h1": float(bn_h1),
        "bn_self": float(bn_self),
        "hausdorff": haus,
    }


if __name__ == "__main__":
    main()
