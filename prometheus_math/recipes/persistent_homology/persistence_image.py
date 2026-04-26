"""Recipe 7: Persistence images -- vectorising a diagram for ML.

A persistence diagram is an unordered multiset of points; most ML pipelines
need fixed-length vectors.  The persistence image (Adams et al., JMLR 2017)
maps a diagram to a 2D grayscale image by:

1.  Replacing each (birth, death) point with a Gaussian centred at
    (birth, death - birth) -- the "birth, persistence" coordinate.
2.  Weighting by a function of persistence so that the diagonal has zero
    contribution (stability).
3.  Sampling on a regular grid.

The result is a fixed-length vector that is stable under bottleneck
perturbation and feeds directly into sklearn / torch.

Mathematical reference
----------------------
Adams, Emerson, Kirby, Neville, Peterson, Shipman, Chepushtanova, Hanson,
Motta & Ziegelmeier, "Persistence Images: A Stable Vector Representation
of Persistent Homology", JMLR 18 (2017).
"""

from __future__ import annotations

import os

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def _outputs_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "outputs")
    os.makedirs(out, exist_ok=True)
    return out


def main(n: int = 100, noise: float = 0.05, seed: int = 0,
         resolution: int = 20, sigma: float = 0.1,
         save_artifact: bool = False) -> dict:
    """Build a persistence image from a noisy-circle H_1 diagram."""
    rng = np.random.default_rng(seed)
    theta = 2 * np.pi * np.linspace(0, 1, n, endpoint=False)
    pts = np.stack([np.cos(theta), np.sin(theta)], axis=1)
    pts += rng.normal(scale=noise, size=pts.shape)

    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5)

    img = pha.persistence_image(diag, dim=1, resolution=resolution, sigma=sigma)

    # Total mass should approximately track the total H_1 persistence.
    total_mass = float(img.sum())
    h1_total_pers = float(sum(
        x - b for d, (b, x) in diag if d == 1 and x != float("inf")
    ))

    print("persistence_image.py -- vectorise diagram for ML")
    print(f"  diagram size          = {len(diag)}")
    print(f"  image shape           = {img.shape}")
    print(f"  image min / max       = {img.min():.6f} / {img.max():.6f}")
    print(f"  image total mass      = {total_mass:.6f}")
    print(f"  H_1 total persistence = {h1_total_pers:.6f}")

    # Sanity assertions: non-negative, finite.
    assert (img >= 0).all(), "persistence image should be non-negative"
    assert np.isfinite(img).all(), "persistence image should be finite"

    artifact = None
    if save_artifact:
        path = os.path.join(_outputs_dir(), "persistence_image.npy")
        np.save(path, img)
        artifact = path

    return {
        "image": img,
        "total_mass": total_mass,
        "h1_total_persistence": h1_total_pers,
        "artifact": artifact,
    }


if __name__ == "__main__":
    main(save_artifact=True)
