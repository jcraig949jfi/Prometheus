"""test_09: end-to-end multi-step BFS over a Lean proof.

This is the contract Walk-Z proof-search needs from lean_runtime:
  - Open a session
  - Declare a theorem with `by sorry`
  - Explore K candidate tactics from the initial proof_state
  - For successful candidates, recurse one level deeper
  - Detect when the goal closes

Uses Mathlib-free Lean (the bare lean-repl project). Mathlib-dependent
theorems (e.g. real walk_1 records like `Quiver.Path.toList_injective`)
require a separate mathlib4 build — tracked as follow-up work.
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
    LeanError,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPL_DIR = os.path.join(REPO_ROOT, "external_deps", "repl")
REPL_BIN = os.path.join(REPL_DIR, ".lake", "build", "bin", "repl.exe")


def _have_repl() -> bool:
    return os.path.isfile(REPL_BIN) or os.path.isfile(REPL_BIN.replace(".exe", ""))


def test_09_walk_z_bfs_one_level_branching():
    """Simulate Walk-Z's one-step lookahead: 3 candidates, score by success."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    # Goal: ∀ n : Nat, n + 0 = n. Candidates: rfl (wrong-level), intro (right),
    # simp (right but heavier), exact rfl (wrong-level).
    candidates = ["rfl", "intro n", "simp", "exact rfl"]

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("example : ∀ n : Nat, n + 0 = n := by sorry")
        assert isinstance(r, CommandResponse)
        assert r.sorries, "no sorry returned"
        ps0 = r.sorries[0].proof_state

        results = []
        for tac in candidates:
            outcome = lean.apply_tactic(tac, proof_state=ps0)
            if isinstance(outcome, ProofFinished):
                kind = "finished"
            elif isinstance(outcome, LeanError):
                kind = "error"  # top-level lean-repl error = tactic rejected outright
            elif isinstance(outcome, ProofStepResponse):
                if outcome.has_errors:
                    kind = "error"
                elif outcome.is_finished:
                    kind = "finished"
                else:
                    kind = "progress"
            else:
                kind = type(outcome).__name__.lower()
            results.append((tac, kind))

        # At least one candidate should make progress (intro n) and at least
        # one should error (rfl on the universal quantifier)
        progresses = [t for t, k in results if k in ("progress", "finished")]
        errors = [t for t, k in results if k == "error"]
        assert progresses, f"no candidate made progress: {results!r}"
        assert errors, f"no candidate errored (rfl should fail on ∀): {results!r}"


def test_09b_two_level_search_to_closure():
    """One step then close: simulate depth-2 BFS to ProofFinished."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("example : ∀ n : Nat, n + 0 = n := by sorry")
        assert isinstance(r, CommandResponse) and r.sorries
        ps0 = r.sorries[0].proof_state

        # Depth 1: intro n
        d1 = lean.apply_tactic("intro n", proof_state=ps0)
        if isinstance(d1, ProofFinished):
            return  # closed at depth 1 (Lean's defeq machinery may handle this)
        assert isinstance(d1, ProofStepResponse) and not d1.has_errors
        ps1 = d1.proof_state

        # Depth 2: rfl should close
        d2 = lean.apply_tactic("rfl", proof_state=ps1)
        assert isinstance(d2, (ProofFinished, ProofStepResponse))
        if isinstance(d2, ProofStepResponse):
            assert d2.is_finished, f"proof not closed at depth 2: {d2!r}"
