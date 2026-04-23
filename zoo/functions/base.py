"""Zoo function protocol: any function we want to approximate becomes a dense tensor on a grid."""
from dataclasses import dataclass
from typing import Callable
import numpy as np


@dataclass
class ZooFunction:
    label: str
    tier: str  # "calibration_low" | "calibration_high" | "frontier"
    shape: tuple[int, ...]
    sampler: Callable[[], np.ndarray]
    expected_tt_rank: int | None = None  # None = unknown / frontier
    notes: str = ""

    def sample(self) -> np.ndarray:
        arr = self.sampler()
        if arr.shape != self.shape:
            raise ValueError(f"{self.label}: sampler returned {arr.shape}, expected {self.shape}")
        return arr

    @property
    def dense_size(self) -> int:
        return int(np.prod(self.shape))
