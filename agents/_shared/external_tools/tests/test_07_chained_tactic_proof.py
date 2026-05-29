"""test_07: chained tactics — multi-step proof under apply_tactic.

This is the Walk-Z BFS pattern: a proof_state from one apply_tactic becomes
the input proof_state of the next. Validates that:

  - proof_state ids thread correctly across multiple tactic applications
  - intermediate ProofStepResponse.proof_state is valid for the next step
  - ProofFinished surfaces when the goal closes
"""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.lean_runtime import (
    LeanSession,
    CommandResponse,
    ProofStepResponse,
    ProofFinished,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPL_DIR = os.path.join(REPO_ROOT, "external_deps", "repl")
REPL_BIN = os.path.join(REPL_DIR, ".lake", "build", "bin", "repl.exe")


def _have_repl() -> bool:
    return os.path.isfile(REPL_BIN) or os.path.isfile(REPL_BIN.replace(".exe", ""))


def test_07a_two_step_proof():
    """`intro n; rfl` closes ∀ n, n + 0 = n in two tactics."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    with LeanSession.open(REPL_DIR) as lean:
        # Goal: ∀ n : Nat, n + 0 = n
        r = lean.command("example : ∀ n : Nat, n + 0 = n := by sorry")
        assert isinstance(r, CommandResponse) and r.sorries
        ps0 = r.sorries[0].proof_state

        # Step 1: intro n — opens goal `n + 0 = n` (closed by definitional eq)
        step1 = lean.apply_tactic("intro n", proof_state=ps0)
        # Could already close to ProofFinished if Lean unfolds + by rfl after intro,
        # but in general we expect a ProofStepResponse with the next state
        if isinstance(step1, ProofFinished):
            return  # Lean closed it earlier than expected — still a pass
        assert isinstance(step1, ProofStepResponse), \
            f"expected ProofStepResponse, got {type(step1).__name__}: {step1!r}"
        assert not step1.has_errors
        ps1 = step1.proof_state

        # Step 2: rfl — should close (n + 0 = n by defeq)
        step2 = lean.apply_tactic("rfl", proof_state=ps1)
        assert isinstance(step2, (ProofFinished, ProofStepResponse)), \
            f"expected closure, got {type(step2).__name__}: {step2!r}"
        if isinstance(step2, ProofStepResponse):
            assert step2.is_finished, f"goals not closed: {step2.goals!r}"


def test_07b_branching_proof_states_are_independent():
    """Two tactic applications on the same proof_state produce independent next states.

    Critical for BFS: a parent state must remain usable for trying alternative
    tactics. apply_tactic must not mutate the source proof_state.
    """
    if not _have_repl():
        pytest.skip("lean-repl not built")

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("example : ∀ n : Nat, n + 0 = n := by sorry")
        assert isinstance(r, CommandResponse) and r.sorries
        ps0 = r.sorries[0].proof_state

        # Branch A: intro n
        branch_a = lean.apply_tactic("intro n", proof_state=ps0)
        # Branch B: also intro n, but on the SAME ps0 (re-using parent)
        branch_b = lean.apply_tactic("intro n", proof_state=ps0)

        # Both should succeed; lean-repl issues fresh proof_state ids
        assert isinstance(branch_a, (ProofStepResponse, ProofFinished))
        assert isinstance(branch_b, (ProofStepResponse, ProofFinished))

        # If both are ProofStepResponse, their proof_state ids should differ
        if isinstance(branch_a, ProofStepResponse) and isinstance(branch_b, ProofStepResponse):
            assert branch_a.proof_state != branch_b.proof_state, \
                "lean-repl reused proof_state id — backtracking would alias states"
