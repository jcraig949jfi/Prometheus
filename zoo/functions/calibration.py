"""Calibration anchors: functions with known TT-compressibility verdicts.

These are load-bearing. If the archive fails to place these correctly, the
instrument is broken, not the frontier functions.
"""
import numpy as np
from .base import ZooFunction


def _grid(shape: tuple[int, ...], lo: float = -1.0, hi: float = 1.0) -> list[np.ndarray]:
    """1D axis grids used to build separable tensor functions."""
    return [np.linspace(lo, hi, n) for n in shape]


def product_of_coords(shape: tuple[int, ...] = (16,) * 6) -> ZooFunction:
    """f(x_1, ..., x_d) = prod_i x_i. Exact TT rank 1. Near-trivial compression."""
    def sampler() -> np.ndarray:
        axes = _grid(shape)
        grids = np.meshgrid(*axes, indexing="ij")
        out = np.ones(shape, dtype=np.float64)
        for g in grids:
            out *= g
        return out

    return ZooFunction(
        label="prod_x",
        tier="calibration_low",
        shape=shape,
        sampler=sampler,
        expected_tt_rank=1,
        notes="Exact TT rank 1. Storage at r=1 is d*n*1*1 = d*n scalars.",
    )


def sum_of_squares(shape: tuple[int, ...] = (16,) * 6) -> ZooFunction:
    """f(x_1, ..., x_d) = sum_i x_i^2. Exact TT rank 2.

    Geometric anchor between prod_of_coords (multiplicative separability, rank 1)
    and random_gaussian (no separability). The unfolding M_k = f_left(.) * 1 + 1 *
    f_right(.) has matrix rank 2; therefore TT rank is 2 at every bond.

    Storage at r=2: d cores of shape ~(2, n, 2). Roughly 4*d*n - 2*n params.
    """
    def sampler() -> np.ndarray:
        axes = _grid(shape)
        grids = np.meshgrid(*axes, indexing="ij")
        out = np.zeros(shape, dtype=np.float64)
        for g in grids:
            out += g ** 2
        return out

    return ZooFunction(
        label="sum_of_squares",
        tier="calibration_low",
        shape=shape,
        sampler=sampler,
        expected_tt_rank=2,
        notes="Additive separability. Sum of d rank-1 terms. TT rank exactly 2.",
    )


def random_gaussian(shape: tuple[int, ...] = (16,) * 6, seed: int = 20260424) -> ZooFunction:
    """Random i.i.d. Gaussian tensor. Full TT rank by construction. Incompressible."""
    def sampler() -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.standard_normal(shape)

    return ZooFunction(
        label="random_gaussian",
        tier="calibration_high",
        shape=shape,
        sampler=sampler,
        expected_tt_rank=None,  # full-rank; ceiling = min(left_size, right_size) at each bond
        notes="i.i.d. Gaussian. Should resist compression: any low-rank TT misses most energy.",
    )
