"""Scour base class. A scour is a vacuum cleaner for one source of
tensor-related content. Each scour subclasses Scour and implements
discover() (and optionally lineage())."""
from __future__ import annotations

from typing import Any
from ..tensor import CandidateCell, LineageEdge


class Scour:
    """Abstract base. Concrete scours register in scours/__init__.REGISTRY."""

    name: str = "abstract_scour"
    interval_hint_sec: int = 1800       # daemon respects this when rotating
    min_seconds_between_runs: int = 60  # rate-limit politeness

    def discover(self, state: dict) -> list[CandidateCell]:
        """Pull from the source. Return candidate cells. The integrator
        will compute cell_ids and merge/append.

        `state` is the scour's persistent state — a dict the daemon
        passes in and saves whatever you write back to it (under
        state['scour_state'][self.name]). Use it for cursors, last-fetched
        timestamps, etc.
        """
        raise NotImplementedError

    def lineage(self, candidates: list[CandidateCell]) -> list[LineageEdge]:
        """Optional: emit lineage edges. Default = none.

        Note: lineage edges reference cell_ids, but cell_ids aren't
        computed until integrate-time. If you want to emit edges, the
        usual pattern is to emit them in a follow-up tick after the
        cells you're connecting are already in the tensor.
        """
        return []
