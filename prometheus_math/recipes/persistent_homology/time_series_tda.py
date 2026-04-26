"""Recipe 8: Time-series TDA via sliding-window embeddings.

Periodicity in a 1D time series shows up as a *loop* in its sliding-window
(Takens) embedding.  Persistent homology of the embedded point cloud
detects this loop as a single long-lived H_1 bar -- a topology-based
periodicity test.

This recipe samples a noisy sine wave, embeds it, runs Vietoris-Rips, and
prints the longest H_1 bar.  A pure sine wave should produce a bar with
persistence near sqrt(2) when ``dim = 2`` and ``tau`` matches the period.

Mathematical reference
----------------------
Perea & Harer, "Sliding Windows and Persistence: An Application of
Topological Methods to Signal Analysis", Foundations of Computational
Mathematics 15 (2015), Section 3.
"""

from __future__ import annotations

import math

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def main(length: int = 200, period: int = 20, noise: float = 0.1,
         emb_dim: int = 5, tau: int = 5, seed: int = 0) -> dict:
    """Run sliding-window PH on a noisy sine.

    Defaults give an embedding of length ~180 in R^5, where the noisy sine
    traces out a simple loop.  The H_1 diagram contains exactly one long
    bar.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(length, dtype=float)
    ts = np.sin(2 * np.pi * t / period) + rng.normal(scale=noise, size=length)

    cloud = pha.sliding_window_embed(ts, dim=emb_dim, tau=tau)
    diag = pha.rips_persistence(cloud, max_dim=1, max_edge_length=4.0)

    h1 = [(b, x) for d, (b, x) in diag if d == 1 and not math.isinf(x)]
    h1.sort(key=lambda bx: -(bx[1] - bx[0]))

    if not h1:
        raise RuntimeError("no H_1 bar found; try larger emb_dim or smaller noise")
    top_birth, top_death = h1[0]
    top_pers = top_death - top_birth

    n_long = sum(1 for b, x in h1 if (x - b) > 0.5)

    print("time_series_tda.py -- sliding-window PH of a noisy sine")
    print(f"  length, period        = {length}, {period}")
    print(f"  embedding (dim, tau)  = ({emb_dim}, {tau})")
    print(f"  cloud shape           = {cloud.shape}")
    print(f"  top H_1 bar           = ({top_birth:.4f}, {top_death:.4f})")
    print(f"  top H_1 persistence   = {top_pers:.4f}")
    print(f"  H_1 bars > 0.5 pers   = {n_long}")

    assert n_long >= 1, "expected at least one persistent loop in the embedding"

    return {
        "diagram": diag,
        "cloud_shape": cloud.shape,
        "top_H1": (top_birth, top_death),
        "top_H1_persistence": float(top_pers),
        "n_long_loops": int(n_long),
    }


if __name__ == "__main__":
    main()
