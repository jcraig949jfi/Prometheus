"""Layer 2: substrate-wide proof-search engine.

Generic BFS / beam search over proof states. Wires:
  - Layer 1 LeanSession (Lean today; Isabelle/Coq/Z3 tomorrow via the same
    pattern) for tactic application
  - Pluggable CandidateGenerator (random / model-based / pretrained / Walk-Z PRM)
  - Pluggable Scorer (Walk-Z PRM v0, sibling-ranker, per-kind, or constant 1.0)

Designed for hundreds-of-agents future: every agent that wants to do
proof-search inherits this. Walk-Z is the first caller; the next agent
doing Isabelle or Coq plugs in a different Session implementation.
"""
from agents._shared.proof_search.types import (
    SearchNode,
    SearchState,
    SearchResult,
    SearchOutcome,
)
from agents._shared.proof_search.interfaces import (
    CandidateGenerator,
    Scorer,
    ProofSystem,
)
from agents._shared.proof_search.engine import ProofSearchEngine
from agents._shared.proof_search.lean_adapter import LeanProofSystem

__all__ = [
    "SearchNode",
    "SearchState",
    "SearchResult",
    "SearchOutcome",
    "CandidateGenerator",
    "Scorer",
    "ProofSystem",
    "ProofSearchEngine",
    "LeanProofSystem",
]
