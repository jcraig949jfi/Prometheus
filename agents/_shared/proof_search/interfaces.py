"""Proof-search interfaces — proof-system-agnostic pluggable hooks."""
from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from agents._shared.proof_search.types import SearchNode, SearchState, SearchOutcome


# A CandidateGenerator returns up to K candidate tactic strings for a node.
# Stateless: takes the current SearchNode, returns ordered candidates.
# Implementations: random-tactic pool, premise-selector, LLM-prompted, etc.
CandidateGenerator = Callable[[SearchNode], list[str]]

# A Scorer returns a float — higher = more promising.
# Walk-Z plugs PRM v0 / sibling-ranker / per-kind here.
# If None, the engine treats all candidates as equally promising.
Scorer = Callable[[SearchNode, str], float]


@runtime_checkable
class ProofSystem(Protocol):
    """Adapter for any tactic-state-based proof system.

    LeanSession plugs in via LeanProofSystem. Future Isabelle/Coq/Z3 plug
    in via their own adapters — the engine itself stays proof-system-agnostic.
    """

    def apply_tactic(
        self, state: SearchState, tactic: str, timeout: float | None = None
    ) -> tuple[SearchOutcome, SearchState | None, str | None]:
        """Apply `tactic` against `state`.

        Returns (outcome, new_state_or_None, error_detail_or_None).
        new_state is None when outcome is REJECTED/GAVE_UP/CRASHED.
        error_detail carries the failure reason for human/log inspection.
        """
        ...

    def is_alive(self) -> bool:
        """Whether the underlying session is healthy enough to apply more tactics."""
        ...
