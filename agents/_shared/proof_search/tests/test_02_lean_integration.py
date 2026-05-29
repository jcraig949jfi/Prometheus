"""test_02: ProofSearchEngine driving a real LeanSession.

Bridges Layer 2 to Layer 1: open a Lean session, declare a theorem with
`by sorry`, point the engine at the resulting proof state, watch the
engine close the goal.

This is the full Walk-Z BFS contract end-to-end.
"""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.lean_runtime import (
    LeanSession,
    CommandResponse,
)
from agents._shared.proof_search import (
    ProofSearchEngine,
    LeanProofSystem,
    SearchState,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPL_DIR = os.path.join(REPO_ROOT, "external_deps", "repl")
REPL_BIN = os.path.join(REPL_DIR, ".lake", "build", "bin", "repl.exe")


def _have_repl() -> bool:
    return os.path.isfile(REPL_BIN) or os.path.isfile(REPL_BIN.replace(".exe", ""))


def test_02a_engine_closes_forall_n_plus_zero():
    """Engine finds and applies `simp` (one-step closure) for ∀ n, n + 0 = n."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    candidates = ["rfl", "intro n", "simp", "exact rfl", "trivial"]

    with LeanSession.open(REPL_DIR) as lean:
        # Set up the theorem and grab its proof state
        r = lean.command("example : ∀ n : Nat, n + 0 = n := by sorry")
        assert isinstance(r, CommandResponse) and r.sorries
        ps0 = r.sorries[0].proof_state
        initial_goal = r.sorries[0].goal

        ps = LeanProofSystem(lean)
        engine = ProofSearchEngine(
            proof_system=ps,
            candidate_gen=lambda node: candidates,
            max_depth=3,
            max_nodes=20,
        )
        result = engine.search(SearchState(state_id=ps0, goals=[initial_goal]))

        assert result.finished, f"engine failed to close: {result!r}"
        assert result.closing_tactic_sequence is not None
        assert len(result.closing_tactic_sequence) <= 3, \
            f"closing path too long: {result.closing_tactic_sequence}"
        # `simp` is in our candidate list and closes in one step — engine
        # should find it at depth 1
        assert result.closing_tactic_sequence[-1] in candidates


def test_02b_scorer_routes_to_efficient_proof():
    """Scoring `simp` higher than `intro n` should let the engine close at depth 1."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    candidates = ["intro n", "simp", "rfl"]

    def scorer(node, tac):
        # Prefer one-step closers
        return {"simp": 1.0, "intro n": 0.5, "rfl": -1.0}.get(tac, 0.0)

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("example : ∀ n : Nat, n + 0 = n := by sorry")
        assert isinstance(r, CommandResponse) and r.sorries
        ps0 = r.sorries[0].proof_state

        engine = ProofSearchEngine(
            proof_system=LeanProofSystem(lean),
            candidate_gen=lambda node: candidates,
            scorer=scorer,
            max_depth=3,
            max_nodes=10,
        )
        result = engine.search(SearchState(state_id=ps0, goals=[r.sorries[0].goal]))

        assert result.finished, f"engine failed: {result!r}"
        # Should close in 1 step via simp (the highest-scored option)
        assert result.closing_tactic_sequence == ["simp"], \
            f"expected ['simp'], got {result.closing_tactic_sequence}"
