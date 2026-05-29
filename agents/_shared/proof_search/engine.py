"""ProofSearchEngine — proof-system-agnostic BFS/beam search.

The engine itself is generic over proof system, candidate generator, and
scorer. It owns: frontier, budget, search tree, terminal detection.

Walk-Z's first use:
  - ProofSystem = LeanProofSystem
  - CandidateGenerator = static pool (initial) → PRM-aware (later)
  - Scorer = None initially → PRM v0 → sibling-ranker → per-kind

Walk-Z's later use: replace CandidateGenerator with an LLM call returning
ranked tactic candidates; replace Scorer with the trained model head.
"""
from __future__ import annotations

import heapq
import time
from typing import Optional

from agents._shared.proof_search.interfaces import (
    CandidateGenerator,
    Scorer,
    ProofSystem,
)
from agents._shared.proof_search.types import (
    SearchNode,
    SearchState,
    SearchResult,
    SearchOutcome,
)


class ProofSearchEngine:
    """BFS/beam search engine over a ProofSystem.

    Frontier semantics: best-first by score (descending). If `scorer` is None,
    falls back to plain BFS by depth (FIFO).
    """

    def __init__(
        self,
        proof_system: ProofSystem,
        candidate_gen: CandidateGenerator,
        scorer: Optional[Scorer] = None,
        max_depth: int = 10,
        max_nodes: int = 1000,
        beam_width: int | None = None,
        per_tactic_timeout: float | None = None,
    ):
        self.ps = proof_system
        self.candidate_gen = candidate_gen
        self.scorer = scorer
        self.max_depth = int(max_depth)
        self.max_nodes = int(max_nodes)
        self.beam_width = beam_width  # None = unlimited per-node expansion
        self.per_tactic_timeout = per_tactic_timeout

    def search(self, initial_state: SearchState) -> SearchResult:
        t0 = time.monotonic()
        root = SearchNode(
            state=initial_state,
            depth=0,
            outcome=SearchOutcome.PROGRESS if not initial_state.is_closed else SearchOutcome.FINISHED,
        )

        # If the initial state is already closed, return immediately
        if initial_state.is_closed:
            return SearchResult(
                finished=True,
                closing_tactic_sequence=[],
                explored_nodes=1,
                elapsed_seconds=time.monotonic() - t0,
                final_node=root,
                reason="initial_state_closed",
            )

        # Frontier as a max-heap of (neg_score, node_id, node)
        # neg_score ensures highest score pops first; node_id breaks score ties
        frontier: list[tuple[float, int, SearchNode]] = []
        next_id = 0
        heapq.heappush(frontier, (-root.score, next_id, root))
        next_id += 1

        explored = 0
        while frontier:
            if explored >= self.max_nodes:
                return SearchResult(
                    finished=False,
                    closing_tactic_sequence=None,
                    explored_nodes=explored,
                    elapsed_seconds=time.monotonic() - t0,
                    final_node=None,
                    reason="max_nodes_exhausted",
                )

            if not self.ps.is_alive():
                return SearchResult(
                    finished=False,
                    closing_tactic_sequence=None,
                    explored_nodes=explored,
                    elapsed_seconds=time.monotonic() - t0,
                    final_node=None,
                    reason="session_crashed",
                )

            _neg, _id, node = heapq.heappop(frontier)
            explored += 1

            if node.depth >= self.max_depth:
                continue

            # Generate candidates for this node
            candidates = self.candidate_gen(node)
            if self.beam_width is not None:
                candidates = candidates[: self.beam_width]

            for tac in candidates:
                outcome, new_state, err = self.ps.apply_tactic(
                    node.state, tac, timeout=self.per_tactic_timeout
                )

                child = SearchNode(
                    state=new_state if new_state is not None else SearchState(state_id=-1),
                    depth=node.depth + 1,
                    outcome=outcome,
                    tactic_from_parent=tac,
                    parent=node,
                    error_detail=err,
                )

                if outcome == SearchOutcome.FINISHED:
                    return SearchResult(
                        finished=True,
                        closing_tactic_sequence=child.tactic_path,
                        explored_nodes=explored,
                        elapsed_seconds=time.monotonic() - t0,
                        final_node=child,
                        reason="closed",
                    )

                if outcome == SearchOutcome.CRASHED:
                    return SearchResult(
                        finished=False,
                        closing_tactic_sequence=None,
                        explored_nodes=explored,
                        elapsed_seconds=time.monotonic() - t0,
                        final_node=child,
                        reason=f"session_crashed: {err}",
                    )

                # Skip dead branches
                if outcome in (SearchOutcome.REJECTED, SearchOutcome.GAVE_UP):
                    node.children.append(child)
                    continue

                # PROGRESS — score and push to frontier
                if self.scorer is not None:
                    child.score = self.scorer(node, tac)
                else:
                    # Depth-based heuristic: shallower = higher (BFS-like)
                    child.score = -float(child.depth)

                node.children.append(child)
                heapq.heappush(frontier, (-child.score, next_id, child))
                next_id += 1

        return SearchResult(
            finished=False,
            closing_tactic_sequence=None,
            explored_nodes=explored,
            elapsed_seconds=time.monotonic() - t0,
            final_node=None,
            reason="frontier_empty",
        )
