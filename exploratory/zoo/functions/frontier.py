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
