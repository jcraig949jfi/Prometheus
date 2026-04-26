"""Recipe 6: Wasserstein-2 distance between persistence diagrams.

The p-Wasserstein distance generalises the bottleneck distance: rather than
the worst-case matching cost, it sums the matching costs to the p-th power.
Wasserstein-2 (p = 2) is widely used in machine learning on diagrams.

This recipe contrasts Wasserstein-2 against bottleneck on the same noisy-vs-
ideal circle pair from recipe 5, illustrating the canonical inequality
``W_p >= bottleneck`` (since bottleneck is the limit p -> infinity).

Mathematical reference
----------------------
Cohen-Steiner, Edelsbrunner, Harer & Mileyko, "Lipschitz functions have
L_p-stable persistence", Foundations of Computational Mathematics 10
(2010), Theorem 4.2.
"""

from __future__ import annotations

import math

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def main(n: int = 100, noise: float = 0.05, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    theta = 2 * np.pi * np.linspace(0, 1, n, endpoint=False)
    ideal = np.stack([np.cos(theta), np.sin(theta)], axis=1)
    noisy = ideal + rng.normal(scale=noise, size=ideal.shape)

    diag_a = pha.rips_persistence(ideal, max_dim=1, max_edge_length=2.5)
    diag_b = pha.rips_persistence(noisy, max_dim=1, max_edge_length=2.5)

    w2_h1 = pha.wasserstein_distance(diag_a, diag_b, p=2.0, dim=1)
    w1_h1 = pha.wasserstein_distance(diag_a, diag_b, p=1.0, dim=1)
    bn_h1 = pha.bottleneck_distance(diag_a, diag_b, dim=1)

    # Self-distance.
    w2_self = pha.wasserstein_distance(diag_a, diag_a, p=2.0, dim=1)

    print("wasserstein_distance.py -- noisy vs ideal circle")
    print(f"  n                     = {n}")
    print(f"  noise sigma           = {noise}")
    print(f"  W_2(H_1)              = {w2_h1:.6f}")
    print(f"  W_1(H_1)              = {w1_h1:.6f}")
    print(f"  bottleneck(H_1)       = {bn_h1:.6f}")
    print(f"  W_2 >= bottleneck     = {w2_h1 + 1e-9 >= bn_h1}")
    print(f"  W_2 self-distance     = {w2_self:.6f}")

    assert w2_self < 1e-6, "W_2(d, d) should be ~0"
    # In general W_p >= bottleneck (with equality at p = infinity).
    assert w2_h1 + 1e-9 >= bn_h1, "W_2 should be at least bottleneck"

    return {
        "w2_h1": float(w2_h1),
        "w1_h1": float(w1_h1),
        "bn_h1": float(bn_h1),
        "w2_self": float(w2_self),
    }


if __name__ == "__main__":
    main()
