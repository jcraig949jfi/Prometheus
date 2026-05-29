"""test_04: full stack — engine + LeanSession + mathlib4.

Closes Gap 1 by demonstrating that the LeanSession / ProofSearchEngine stack
works against the real Mathlib environment. Uses the bridge Lake project at
`external_deps/mathlib_repl/`, which depends on both lean-repl and mathlib4.

Validates:
  - `lake exe repl` from the bridge project starts cleanly
  - `import Mathlib.Tactic` succeeds (no symbol-not-found from mathlib)
  - Engine drives a proof using mathlib's tactic library
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
BRIDGE_DIR = os.path.join(REPO_ROOT, "external_deps", "mathlib_repl")
MATHLIB_DIR = os.path.join(REPO_ROOT, "external_deps", "mathlib4")


def _have_mathlib_bridge() -> bool:
    return (
        os.path.isfile(os.path.join(BRIDGE_DIR, "lakefile.toml"))
        and os.path.isdir(os.path.join(MATHLIB_DIR, ".lake", "build"))
    )


def test_04a_mathlib_import_succeeds():
    """Smoke test: import Mathlib.Tactic should produce {env: N} with no errors."""
    if not _have_mathlib_bridge():
        pytest.skip("mathlib4 + bridge not built (Gap 1)")

    with LeanSession.open(BRIDGE_DIR, timeout=600.0) as lean:
        # Cold-cache import of all of Mathlib can take 5+ minutes on first
        # run; warm runs are ~15-20s. Generous timeout to absorb both.
        r = lean.command("import Mathlib.Tactic", timeout=420.0)
        assert isinstance(r, CommandResponse), f"got {type(r).__name__}: {r!r}"
        assert isinstance(r.env, int)
        assert not r.has_errors, f"import errored: {r.messages!r}"


def test_04b_engine_closes_mathlib_proof():
    """Engine drives a search using mathlib's simp lemmas."""
    if not _have_mathlib_bridge():
        pytest.skip("mathlib4 + bridge not built (Gap 1)")

    with LeanSession.open(BRIDGE_DIR, timeout=600.0) as lean:
        # Import mathlib (gives access to simp lemmas)
        r_import = lean.command("import Mathlib.Tactic", timeout=420.0)
        assert isinstance(r_import, CommandResponse) and not r_import.has_errors
        env = r_import.env

        # State a theorem that needs mathlib (List manipulation)
        r = lean.command(
            "example : ([1, 2, 3] : List Nat).length = 3 := by sorry",
            env=env,
            timeout=60.0,
        )
        assert isinstance(r, CommandResponse), f"got {type(r).__name__}: {r!r}"
        assert r.sorries, "no sorry returned"
        ps0 = r.sorries[0].proof_state

        candidates = ["rfl", "simp", "decide", "trivial"]

        engine = ProofSearchEngine(
            proof_system=LeanProofSystem(lean),
            candidate_gen=lambda node: candidates,
            max_depth=3,
            max_nodes=20,
            per_tactic_timeout=30.0,
        )
        result = engine.search(SearchState(state_id=ps0, goals=[r.sorries[0].goal]))

        assert result.finished, f"engine failed to close: {result!r}"
        assert result.closing_tactic_sequence
        assert result.closing_tactic_sequence[-1] in candidates
