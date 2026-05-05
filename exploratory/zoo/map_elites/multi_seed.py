"""Multi-seed harness: run MAP-Elites with N different seeds, aggregate with
median + IQR. Single-seed results are indefensible; this is the cheapest
robustness upgrade available.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import numpy as np

from ..functions.base import ZooFunction
from .grid import Archive, GridSpec
from .loop import LoopConfig, run


@dataclass
class MultiSeedResult:
    function_label: str
    archives: list[Archive] = field(default_factory=list)
    seeds: list[int] = field(default_factory=list)

    def pooled_history(self) -> list:
        out = []
        for arc in self.archives:
            out.extend(arc.history)
        return out

    def aggregate_summary(self) -> dict[str, Any]:
        """Median + IQR across seeds of each summary field."""
        if not self.archives:
            return {"function_label": self.function_label, "n_seeds": 0}
        per_seed = [a.summary() for a in self.archives]

        def _col(key):
            xs = [s.get(key) for s in per_seed if s.get(key) is not None]
            return xs

        def _stats(xs):
            if not xs:
                return None
            xs = np.asarray(xs, dtype=np.float64)
            return {
                "median": float(np.median(xs)),
                "q25": float(np.percentile(xs, 25)),
                "q75": float(np.percentile(xs, 75)),
                "min": float(np.min(xs)),
                "max": float(np.max(xs)),
                "n_seeds": int(len(xs)),
            }

        return {
            "function_label": self.function_label,
            "n_seeds": len(self.archives),
            "seeds": list(self.seeds),
            "n_cells_occupied": _stats(_col("n_cells_occupied")),
            "min_error": _stats(_col("min_error")),
            "min_params": _stats(_col("min_params")),
            "pareto_front_size": _stats(_col("pareto_front_size")),
        }


def run_multi_seed(func: ZooFunction, config: LoopConfig, spec: GridSpec,
                   seeds: list[int]) -> MultiSeedResult:
    """Run the same LoopConfig once per seed.

    BUG-FIX 2026-04-25: previously this constructor only forwarded a subset
    of LoopConfig fields (n_generations, n_initial, max_bond, seed, als_sweeps).
    It silently dropped dmrg_sweeps, dmrg_rel_tol, mutation, and seed_strategy,
    causing Phase 4's "DMRG ON" run to actually execute with dmrg_sweeps=0 and
    Phase 5's diversified-seed config to be silently ignored.

    The fix uses dataclasses.replace to override only the seed field, preserving
    every other field exactly as configured by the caller.
    """
    from dataclasses import replace as _replace
    archives = []
    for s in seeds:
        cfg_s = _replace(config, seed=s)
        arc = run(func, config=cfg_s, spec=spec)
        archives.append(arc)
    return MultiSeedResult(
        function_label=func.label,
        archives=archives,
        seeds=list(seeds),
    )
