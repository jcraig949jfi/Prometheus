"""MAP-Elites behavior-descriptor grid.

Phase 4: generalized to arbitrary 2D descriptor placement.

An AxisSpec binds a named descriptor to a bin range. Cell lookup pulls
the named descriptor from the Elite's `extras` dict (or from a small
fixed set of core Elite fields: n_params, rel_error).

Backward compatibility: GridSpec() with no arguments yields the Phase 2/3
(log_params, log_error) grid.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import numpy as np


def _log_params(elite) -> float:
    return float(np.log10(max(1, elite.n_params)))


def _log_error(elite, floor: float = 1e-12) -> float:
    return float(np.log10(max(floor, elite.rel_error)))


def _from_extras(name: str):
    def reader(elite):
        v = (elite.extras or {}).get(name)
        return float(v) if v is not None else 0.0
    return reader


def _log_from_extras(name: str, floor: float = 1e-12):
    def reader(elite):
        v = (elite.extras or {}).get(name)
        if v is None:
            return float(np.log10(floor))
        return float(np.log10(max(floor, abs(v))))
    return reader


@dataclass(frozen=True)
class AxisSpec:
    name: str                                   # descriptor name (user-facing)
    reader: Callable[[Any], float]              # extract axis value from an Elite
    lo: float
    hi: float
    n_bins: int = 20

    def bin(self, elite) -> int:
        x = self.reader(elite)
        idx = int(np.floor((x - self.lo) / (self.hi - self.lo) * self.n_bins))
        return max(0, min(self.n_bins - 1, idx))


@dataclass(frozen=True)
class GridSpec:
    """Generic 2D placement grid. Defaults to (log_params, log_error)."""
    x: AxisSpec = field(default_factory=lambda: AxisSpec(
        "log_params", _log_params, 0.0, 7.0, 20,
    ))
    y: AxisSpec = field(default_factory=lambda: AxisSpec(
        "log_error", _log_error, -10.0, 0.5, 20,
    ))

    @property
    def params_bins(self) -> int:
        return self.x.n_bins

    @property
    def error_bins(self) -> int:
        return self.y.n_bins

    @property
    def params_range(self) -> tuple[float, float]:
        return (self.x.lo, self.x.hi)

    @property
    def error_range(self) -> tuple[float, float]:
        return (self.y.lo, self.y.hi)

    @property
    def error_floor(self) -> float:
        return 1e-12

    def axis_names(self) -> tuple[str, str]:
        return (self.x.name, self.y.name)

    def cell_from_elite(self, elite) -> tuple[int, int]:
        return (self.x.bin(elite), self.y.bin(elite))

    # Legacy (Phase 1/2/3) convenience — compute cell from raw (n_params, rel_error)
    # without going through an Elite. Preserved for backward compatibility.
    def cell(self, n_params: int, rel_error: float) -> tuple[int, int]:
        class _Mock:
            pass
        e = _Mock()
        e.n_params = n_params
        e.rel_error = rel_error
        e.extras = None
        return self.cell_from_elite(e)

    def params_bin(self, n_params: int) -> int:
        return self.cell(n_params, 1.0)[0]

    def error_bin(self, rel_error: float) -> int:
        return self.cell(1, rel_error)[1]


def grid_params_entropy() -> GridSpec:
    """Phase 4 Branch-A grid: (log_params, rank_entropy).

    rank_entropy naturally lives in [0, log(d-1)]. For d = 6 that is
    [0, log(5)] ~ [0, 1.609]. Use that range with 20 bins.
    """
    return GridSpec(
        x=AxisSpec("log_params", _log_params, 0.0, 7.0, 20),
        y=AxisSpec("rank_entropy", _from_extras("rank_entropy"), 0.0, 1.61, 20),
    )


def grid_params_concentration() -> GridSpec:
    """Alternate Branch-A grid: (log_params, rank_concentration).

    rank_concentration = max/mean is >= 1. Use log to spread values; range
    [0, log10(max_bond)] covers the useful regime."""
    return GridSpec(
        x=AxisSpec("log_params", _log_params, 0.0, 7.0, 20),
        y=AxisSpec("rank_concentration",
                   lambda e: float((e.extras or {}).get("rank_concentration", 1.0)),
                   1.0, 16.0, 20),
    )


@dataclass
class Elite:
    function_label: str
    ranks: tuple[int, ...]
    n_params: int
    rel_error: float
    cell: tuple[int, int]
    generation: int
    extras: dict | None = None


@dataclass
class Archive:
    function_label: str
    spec: GridSpec
    cells: dict[tuple[int, int], Elite] = field(default_factory=dict)
    history: list[Elite] = field(default_factory=list)

    def try_place(self, candidate: Elite) -> bool:
        """Place candidate in its cell if empty, or if strictly better by
        rel_error. Within-cell tie-breaker favors lower error (accuracy).
        """
        self.history.append(candidate)
        occupant = self.cells.get(candidate.cell)
        if occupant is None or candidate.rel_error < occupant.rel_error:
            self.cells[candidate.cell] = candidate
            return True
        return False

    def pareto_front(self) -> list[Elite]:
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
            "axis_names": list(self.spec.axis_names()),
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
