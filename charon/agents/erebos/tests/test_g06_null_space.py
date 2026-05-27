"""TDD tests for G06 Null-Space."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g06_null_space import (
    KILL_PATTERN_UNIVERSE,
    MIN_DENSE_COUNT,
    NullSpaceGenerator,
    _identify_void_and_dense,
    _kill_pattern_counts,
    _pick_promoted_anchor,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _erebos_rejected(rid: str, kp: str) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"erebos {rid}",
        "verdict": "REJECTED",
        "kill_pattern": kp,
        "kill_vector": None,
        "generator_id": "erebos",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {},
        "extras": {},
    }


def _promoted(rid: str) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"PROMOTED anchor {rid}",
        "verdict": "PROMOTED",
        "kill_pattern": None,
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return NullSpaceGenerator()


def test_kill_pattern_counts_skips_non_rejected():
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_rejected("r1", "permutation_null"),
        _promoted("r2"),  # PROMOTED, should be skipped
    ]
    counts = _kill_pattern_counts(state)
    assert counts["permutation_null"] == 1
    assert sum(counts.values()) == 1


def test_identify_void_and_dense_needs_enough_kills(gen):
    """Below MIN_DENSE_COUNT, no dense pattern exists."""
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_rejected("r1", "permutation_null")]
    assert _identify_void_and_dense(state) is None


def test_identify_void_and_dense_returns_modal_and_void():
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_rejected("r1", "permutation_null"),
        _erebos_rejected("r2", "permutation_null"),
        _erebos_rejected("r3", "permutation_null"),
    ]
    out = _identify_void_and_dense(state)
    assert out is not None
    assert out["dense_kp"] == "permutation_null"
    assert out["dense_count"] == 3
    # Void must be in universe, absent from counts
    assert out["void_kp"] in KILL_PATTERN_UNIVERSE
    assert out["void_kp"] != "permutation_null"


def test_pick_promoted_anchor_returns_promoted():
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("anchor1")]
    a = _pick_promoted_anchor(state)
    assert a is not None
    assert a["record_id"] == "anchor1"


def test_g06_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g06_not_applicable_without_anchor(gen):
    """Ledger has kills but no PROMOTED anchor exists."""
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_rejected("r1", "permutation_null"),
        _erebos_rejected("r2", "permutation_null"),
    ]
    assert gen.applicable(state) is False


def test_g06_not_applicable_without_dense_region(gen):
    """Anchor exists but no kill is dense enough."""
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("anchor1")]
    state.erebos_self_ledger = [_erebos_rejected("r1", "permutation_null")]
    assert gen.applicable(state) is False


def test_g06_applicable_with_full_setup(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("anchor1")]
    state.erebos_self_ledger = [
        _erebos_rejected("r1", "permutation_null"),
        _erebos_rejected("r2", "permutation_null"),
    ]
    assert gen.applicable(state) is True


def test_g06_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("anchor1")]
    state.erebos_self_ledger = [
        _erebos_rejected("r1", "permutation_null"),
        _erebos_rejected("r2", "permutation_null"),
    ]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "universal_rejection"
    assert claim.composition_payload["dense_kill_pattern"] == "permutation_null"


def test_g06_metadata():
    g = NullSpaceGenerator()
    assert g.id == "g06_null_space"
    assert g.feasibility_tier == "C"
    assert g.reasoning_tier == "R6"


def test_g06_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("anchor1")]
    state.erebos_self_ledger = [
        _erebos_rejected("r1", "permutation_null"),
        _erebos_rejected("r2", "permutation_null"),
    ]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G06-null_space_")
