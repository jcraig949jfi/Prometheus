"""Frontier functions: genuinely unknown TT-compressibility. The zoo's discovery targets."""
import numpy as np
from .base import ZooFunction


def _grid(shape: tuple[int, ...], lo: float = -1.0, hi: float = 1.0) -> list[np.ndarray]:
    return [np.linspace(lo, hi, n) for n in shape]


def pairwise_tanh(shape: tuple[int, ...] = (16,) * 6) -> ZooFunction:
    """f(x) = tanh(x_1*x_2 + x_3*x_4 + x_5*x_6).

    Pairwise products summed inside a nonlinearity. Not separable, not algebraically
    forced low-rank. Expected non-trivial TT rank — the interesting question is
    how fast it decays with bond dimension.
    """
    assert len(shape) % 2 == 0, "pairwise_tanh expects an even number of axes"

    def sampler() -> np.ndarray:
        axes = _grid(shape)
        grids = np.meshgrid(*axes, indexing="ij")
        s = np.zeros(shape, dtype=np.float64)
        for i in range(0, len(grids), 2):
            s += grids[i] * grids[i + 1]
        return np.tanh(s)

    return ZooFunction(
        label="pairwise_tanh",
        tier="frontier",
        shape=shape,
        sampler=sampler,
        expected_tt_rank=None,
        notes="tanh(sum of disjoint pairwise products). Frontier: unknown compressibility.",
    )


def runge_dim(shape: tuple[int, ...] = (16,) * 6, c: float = 25.0) -> ZooFunction:
    """Generalized d-dim Runge function: f(x) = 1 / (1 + c * sum_i x_i^2).

    Smooth, non-separable (the denominator couples all coordinates through
    the sum-of-squares inside a rational), sharply peaked at the origin
    and decaying toward the grid boundary.

    Expected TT behavior: non-trivial finite rank with controllable decay
    rate via c. Distinct from pairwise_tanh by construction — pairwise_tanh
    couples coordinates in disjoint pairs, Runge couples all d coordinates
    symmetrically.
    """
    def sampler() -> np.ndarray:
        axes = _grid(shape)
        grids = np.meshgrid(*axes, indexing="ij")
        s = np.zeros(shape, dtype=np.float64)
        for g in grids:
            s += g ** 2
        return 1.0 / (1.0 + c * s)

    return ZooFunction(
        label="runge_dim",
        tier="frontier",
        shape=shape,
        sampler=sampler,
        expected_tt_rank=None,
        notes=f"1/(1 + {c} * sum x_i^2). Smooth, symmetric-in-all-coords, non-separable.",
    )


def heat_smoothed_paraboloid(shape: tuple[int, ...] = (12,) * 6,
                             t: float = 0.02) -> ZooFunction:
    """Non-separable paraboloid^2 initial condition, heat-smoothed via FFT.

    u_0(x) = max(0, 1 - sum(x_i^2))^2 on [-1, 1]^d. This is a smooth
    compact bump that is NOT separable (the ||x||^2 inside the clamp
    couples all coordinates).

    Evolved under the heat equation to time t: multiply the Fourier
    transform by exp(-t * sum k_i^2) and invert. The parameter t
    controls spectral tail behavior — small t preserves the sharp
    structure (high effective rank); large t smooths toward a
    Gaussian-like limit (effective rank approaches 1).

    This provides a controllable spectral stress-test for the archive.
    """
    def sampler() -> np.ndarray:
        axes = _grid(shape)
        grids = np.meshgrid(*axes, indexing="ij")
        r_sq = np.zeros(shape, dtype=np.float64)
        for g in grids:
            r_sq += g ** 2
        u0 = np.maximum(0.0, 1.0 - r_sq) ** 2
        # Heat smoothing via FFT
        u_hat = np.fft.fftn(u0)
        k_axes = [np.fft.fftfreq(n, d=2.0 / (n - 1)) * 2 * np.pi for n in shape]
        k_grids = np.meshgrid(*k_axes, indexing="ij")
        k_sq = np.zeros(shape, dtype=np.float64)
        for kg in k_grids:
            k_sq += kg ** 2
        u_hat *= np.exp(-t * k_sq)
        u = np.real(np.fft.ifftn(u_hat))
        return u

    return ZooFunction(
        label="heat_smoothed",
        tier="frontier",
        shape=shape,
        sampler=sampler,
        expected_tt_rank=None,
        notes=f"max(0, 1 - ||x||^2)^2 heat-smoothed at t={t}. Controllable spectral decay.",
    )
