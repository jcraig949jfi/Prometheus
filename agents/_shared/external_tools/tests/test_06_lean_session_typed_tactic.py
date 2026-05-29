"""test_06: LeanSession.apply_tactic() returns typed proof responses.

Workflow per the absorption doctrine:
  1. Submit a Command containing `by sorry` → response has `sorries: [...]`
  2. Take the sorry's `proofState` id, apply a tactic against it
  3. Verify typed response (ProofStepResponse / ProofFinished / etc.)
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
    ProofGivenUp,
    LeanError,
    SessionCrashed,
    Sorry,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPL_DIR = os.path.join(REPO_ROOT, "external_deps", "repl")
REPL_BIN = os.path.join(REPL_DIR, ".lake", "build", "bin", "repl.exe")


def _have_repl() -> bool:
    return os.path.isfile(REPL_BIN) or os.path.isfile(REPL_BIN.replace(".exe", ""))


def test_06a_command_with_sorry_emits_proof_state():
    """`by sorry` should produce a sorry entry with an integer proofState."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("example : 1 + 1 = 2 := by sorry")
        assert isinstance(r, CommandResponse)
        assert r.sorries, f"expected sorries from `by sorry`, got: {r!r}"
        s = r.sorries[0]
        assert isinstance(s, Sorry)
        assert isinstance(s.proof_state, int) and s.proof_state >= 0
        assert s.goal, f"sorry goal should be non-empty: {s!r}"


def test_06b_tactic_closes_goal_returns_proof_finished():
    """`rfl` against a sorry for `1+1=2` should close the goal."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("example : 1 + 1 = 2 := by sorry")
        assert isinstance(r, CommandResponse) and r.sorries
        ps_id = r.sorries[0].proof_state

        resp = lean.apply_tactic("rfl", proof_state=ps_id)
        assert isinstance(resp, (ProofFinished, ProofStepResponse)), \
            f"expected ProofFinished or empty-goals ProofStepResponse, got {type(resp).__name__}: {resp!r}"
        if isinstance(resp, ProofStepResponse):
            assert resp.is_finished, f"goals still open: {resp.goals!r}"


def test_06c_bad_tactic_keeps_proof_open():
    """A tactic that doesn't close the goal leaves goals remaining."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    with LeanSession.open(REPL_DIR) as lean:
        # Multi-step goal that one tactic won't close
        r = lean.command("example : ∀ n : Nat, n + 0 = n := by sorry")
        assert isinstance(r, CommandResponse) and r.sorries
        ps_id = r.sorries[0].proof_state

        # `intro n` doesn't close the goal, just opens the body
        resp = lean.apply_tactic("intro n", proof_state=ps_id)
        # Should be a ProofStepResponse with at least one goal remaining
        assert isinstance(resp, ProofStepResponse), \
            f"expected ProofStepResponse, got {type(resp).__name__}: {resp!r}"
        assert not resp.is_finished, f"unexpectedly finished: {resp!r}"
        assert resp.goals, "no goals returned"
