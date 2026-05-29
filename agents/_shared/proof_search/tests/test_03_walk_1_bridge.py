"""test_03: walk_1 record parsing and candidate-pool construction.

Structural tests only — runs without mathlib4. The full end-to-end Lean
integration (engine drives a search over a real walk_1 theorem with mathlib4
imports) is test_04 and requires Gap 1 to complete.
"""
from __future__ import annotations

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.proof_search.walk_1_bridge import (
    Walk1Record,
    load_records,
    imports_for_theorem,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
WALK_1_FILE = os.path.join(
    REPO_ROOT,
    "ergon",
    "learner",
    "corpus",
    "v1_0_tier_pending",
    "by_file",
    "daedalus",
    "walk_1",
    "records_2026-05-24T165042Z.jsonl",
)


def _have_walk_1() -> bool:
    return os.path.isfile(WALK_1_FILE)


def test_03a_load_walk_1_records():
    if not _have_walk_1():
        pytest.skip("walk_1 jsonl missing")
    records = load_records(WALK_1_FILE)
    assert len(records) > 0
    r = records[0]
    assert r.theorem_full_name
    assert r.file_path.endswith(".lean")
    assert r.decomposition
    assert isinstance(r.decomposition[0], dict)


def test_03b_candidate_pool_construction():
    if not _have_walk_1():
        pytest.skip("walk_1 jsonl missing")
    records = load_records(WALK_1_FILE)
    r = records[0]

    # Step 0 candidates: winning tactic + siblings, deduped
    step0_cands = r.candidates_at_step(0)
    assert step0_cands, "step 0 should have candidates"
    assert step0_cands[0] == r.decomposition[0]["tactic"], \
        "winning tactic should be first"
    # No duplicates
    assert len(step0_cands) == len(set(step0_cands))

    # Total pool: union across all steps
    pool = r.total_candidate_pool
    assert pool, "total pool should be non-empty"
    assert len(pool) >= len(step0_cands)
    # Original winning sequence is a subset of the pool
    for tac in r.winning_tactic_sequence:
        assert tac in pool, f"winning tactic {tac!r} missing from pool"


def test_03c_imports_from_file_path():
    """`Mathlib/Combinatorics/Quiver/Path.lean` → `import Mathlib.Combinatorics.Quiver.Path`"""
    fake = Walk1Record(
        problem_id="x",
        theorem_full_name="X.theorem",
        file_path="Mathlib/Combinatorics/Quiver/Path.lean",
        decomposition=[],
        raw={},
    )
    imps = imports_for_theorem(fake)
    assert imps == ["import Mathlib.Combinatorics.Quiver.Path"]


def test_03d_winning_sequence_extraction():
    if not _have_walk_1():
        pytest.skip("walk_1 jsonl missing")
    records = load_records(WALK_1_FILE)
    r = records[0]
    seq = r.winning_tactic_sequence
    assert len(seq) == len(r.decomposition)
    assert all(isinstance(t, str) for t in seq)
