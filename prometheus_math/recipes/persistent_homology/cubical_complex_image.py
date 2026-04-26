"""Recipe 9: Sublevel-set persistence of a 2D image (cubical complex).

For a 2D scalar field ``f``, the sublevel sets ``{f <= t}`` give a
filtration of the image grid.  Persistent homology of this filtration
counts dark blobs (H_0) and bright holes (H_1) and tracks how they merge
or fill in as ``t`` rises.

This recipe builds a small synthetic image with three Gaussian "dark
blobs", runs cubical persistence, and prints the number of significant
H_0 bars (which should be 3).

Mathematical reference
----------------------
Edelsbrunner & Harer, *Computational Topology*, Chapter VI.4 (cubical
complexes); Carriere & Bauer, "On the metric distortion of embedding
persistence diagrams into Hilbert spaces", JCSS 105 (2019), Section 2 for
the formal definition of cubical sublevel-set PH.
"""

from __future__ import annotations

import math

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def _gaussian_blob(grid_x: np.ndarray, grid_y: np.ndarray,
                   cx: float, cy: float, sigma: float) -> np.ndarray:
    return np.exp(-((grid_x - cx) ** 2 + (grid_y - cy) ** 2) / (2 * sigma ** 2))


def make_three_blob_image(size: int = 60) -> np.ndarray:
    """Return a (size, size) image with three dark Gaussian blobs."""
    xs = np.linspace(-1.0, 1.0, size)
    ys = np.linspace(-1.0, 1.0, size)
    gx, gy = np.meshgrid(xs, ys)
    bg = np.ones_like(gx)
    blobs = (
        _gaussian_blob(gx, gy, -0.5, -0.3, 0.15) +
        _gaussian_blob(gx, gy, +0.5, -0.3, 0.15) +
        _gaussian_blob(gx, gy, +0.0, +0.5, 0.15)
    )
    # Dark blobs = LOW values (sublevel sets fill in early).
    return bg - blobs


def main(size: int = 60, threshold_pers: float = 0.2) -> dict:
    """Run sublevel-set PH on a 3-blob synthetic image."""
    img = make_three_blob_image(size)
    diag = pha.cubical_persistence(img)

    h0 = [(b, x) for d, (b, x) in diag if d == 0 and not math.isinf(x)]
    h0.sort(key=lambda bx: -(bx[1] - bx[0]))

    # Significant H_0 bars (excluding the one infinite bar -- the global one).
    n_h0_long = sum(1 for b, x in h0 if (x - b) > threshold_pers)
    # Plus the single infinite H_0 component:
    total_h0 = n_h0_long + 1

    betti = pha.betti_numbers_from_diagram(diag)

    print("cubical_complex_image.py -- sublevel-set PH on a 3-blob image")
    print(f"  image shape           = {img.shape}")
    print(f"  total H_0 bars        = {sum(1 for d, _ in diag if d == 0)}")
    print(f"  H_0 bars > {threshold_pers} pers = {n_h0_long} (+ 1 infinite = {total_h0})")
    print(f"  betti                 = {betti}")
    print(f"  top H_0 finite bars   = {h0[:5]}")

    assert total_h0 == 3, f"expected 3 dark blobs, found {total_h0}"

    return {
        "diagram": diag,
        "image_shape": img.shape,
        "n_significant_blobs": int(total_h0),
        "betti": betti,
    }


if __name__ == "__main__":
    main()
