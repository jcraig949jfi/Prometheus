"""Proof-search state types — proof-system-agnostic."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SearchOutcome(str, Enum):
    """Terminal state of a search node."""
    FINISHED = "finished"        # closed the goal
    PROGRESS = "progress"        # tactic worked, goals remain
    REJECTED = "rejected"        # tactic failed / error
    GAVE_UP = "gave_up"          # explicit admit / sorry
    CRASHED = "crashed"          # session died
    PENDING = "pending"          # not yet evaluated


@dataclass
class SearchState:
    """Opaque proof-system state. `state_id` is interpreted by the ProofSystem.

    For Lean, state_id is the lean-repl integer proofState.
    For other systems, it could be a hash, a serialized term, etc.
    """
    state_id: object
    goals: list[str] = field(default_factory=list)

    @property
    def is_closed(self) -> bool:
        return len(self.goals) == 0


@dataclass
class SearchNode:
    """One node in the search tree."""
    state: SearchState
    depth: int
    outcome: SearchOutcome = SearchOutcome.PENDING
    tactic_from_parent: Optional[str] = None
    parent: Optional["SearchNode"] = None
    children: list["SearchNode"] = field(default_factory=list)
    score: float = 0.0
    error_detail: Optional[str] = None

    @property
    def tactic_path(self) -> list[str]:
        """Reconstruct full tactic chain from root to this node."""
        path: list[str] = []
        node: Optional[SearchNode] = self
        while node is not None and node.tactic_from_parent is not None:
            path.append(node.tactic_from_parent)
            node = node.parent
        return list(reversed(path))


@dataclass
class SearchResult:
    """Outcome of a ProofSearchEngine.search() call."""
    finished: bool
    closing_tactic_sequence: Optional[list[str]]
    explored_nodes: int
    elapsed_seconds: float
    final_node: Optional[SearchNode]
    reason: str = ""  # "closed" / "budget_exhausted" / "session_crashed" / etc.
