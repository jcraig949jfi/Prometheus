"""MAP-Elites behavior-descriptor grid.

Phase 1 uses two descriptors: log10(n_params), log10(L2_relative_error).
Cells are indexed by (log_params_bin, log_error_bin).
"""
from dataclasses import dataclass, field
from typing import Any
import numpy as np


@dataclass(frozen=True)
class GridSpec:
    params_range: tuple[float, float] = (0.0, 7.0)    # log10(params)
    params_bins: int = 20
    error_range: tuple[float, float] = (-10.0, 0.5)   # log10(relative L2 error)
    error_bins: int = 20
    error_floor: float = 1e-12  # clip to avoid log(0) when reconstruction is exact

    def params_bin(self, n_params: int) -> int:
        x = np.log10(max(1, n_params))
        lo, hi = self.params_range
        idx = int(np.floor((x - lo) / (hi - lo) * self.params_bins))
        return max(0, min(self.params_bins - 1, idx))

    def error_bin(self, rel_error: float) -> int:
        x = np.log10(max(self.error_floor, rel_error))
        lo, hi = self.error_range
        idx = int(np.floor((x - lo) / (hi - lo) * self.error_bins))
        return max(0, min(self.error_bins - 1, idx))

    def cell(self, n_params: int, rel_error: float) -> tuple[int, int]:
        return (self.params_bin(n_params), self.error_bin(rel_error))


@dataclass
class Elite:
    function_label: str
    ranks: tuple[int, ...]
    n_params: int
    rel_error: float
    cell: tuple[int, int]
    generation: int
    extras: dict | None = None  # P2: rel_error_before_refine, refinement_gain, etc.


@dataclass
class Archive:
    """Per-function archive. Cells map (params_bin, error_bin) -> Elite."""
    function_label: str
    spec: GridSpec
    cells: dict[tuple[int, int], Elite] = field(default_factory=dict)
    history: list[Elite] = field(default_factory=list)

    def try_place(self, candidate: Elite) -> bool:
        """Place candidate in its cell if empty, or if lower rel_error than occupant.

        Within-cell tie-breaker favors lower error (accuracy). Phase 2 can switch
        to a proper elitism strategy.
        """
        self.history.append(candidate)
        occupant = self.cells.get(candidate.cell)
        if occupant is None or candidate.rel_error < occupant.rel_error:
            self.cells[candidate.cell] = candidate
            return True
        return False

    def pareto_front(self) -> list[Elite]:
        """Return non-dominated elites across (n_params, rel_error)."""
        items = list(self.cells.values())
        front = []
        for a in items:
            dominated = False
            for b in items:
                if b is a:
                    continue
                if b.n_params <= a.n_params and b.rel_error <= a.rel_error and (
                    b.n_params < a.n_params or b.rel_error < a.rel_error
                ):
                    dominated = True
                    break
            if not dominated:
                front.append(a)
        front.sort(key=lambda e: e.n_params)
        return front

    def summary(self) -> dict[str, Any]:
        if not self.cells:
            return {
                "function_label": self.function_label,
                "n_cells_occupied": 0,
                "n_evaluations": len(self.history),
            }
        elites = list(self.cells.values())
        return {
            "function_label": self.function_label,
            "n_cells_occupied": len(self.cells),
            "n_evaluations": len(self.history),
            "min_error": min(e.rel_error for e in elites),
            "min_params": min(e.n_params for e in elites),
            "min_params_at_low_error": min(
                (e.n_params for e in elites if e.rel_error < 1e-4),
                default=None,
            ),
            "pareto_front_size": len(self.pareto_front()),
        }
