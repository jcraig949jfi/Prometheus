"""TDD tests for G05 Confound-Swap."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g05_confound_swap import (
    ConfoundSwapGenerator,
    MIN_COORDS,
    _harvest_numeric_coords,
    _is_promoted,
    _pick_target_and_confound,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _promoted(rid: str, payload: dict) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"PROMOTED {rid}",
        "verdict": "PROMOTED",
        "kill_pattern": None,
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": payload,
        "extras": {},
    }


def _rejected(rid: str, payload: dict) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"REJECTED {rid}",
        "verdict": "REJECTED",
        "kill_pattern": "f17_failed",
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": payload,
        "extras": {},
    }


@pytest.fixture
def gen():
    return ConfoundSwapGenerator()


def test_harvest_skips_bools():
    row = {"claim_payload": {"degree": 12, "is_cm": True}, "extras": {}}
    c = _harvest_numeric_coords(row)
    assert "pl.degree" in c
    assert "pl.is_cm" not in c


def test_pick_target_and_confound_ranks_by_magnitude():
    coords = {"a": 1.0, "b": -100.0, "c": 5.0}
    pick = _pick_target_and_confound(coords)
    # Highest magnitude = b (|-100|=100); second = c (|5|=5)
    assert pick["confound_key"] == "b"
    assert pick["target_key"] == "c"


def test_pick_target_and_confound_rejects_below_min():
    assert _pick_target_and_confound({"only_one": 1.0}) is None


def test_is_promoted():
    assert _is_promoted({"verdict": "PROMOTED"}) is True
    assert _is_promoted({"verdict": "REJECTED"}) is False


def test_g05_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g05_not_applicable_when_only_rejected(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_rejected("r1", {"a": 1.0, "b": 2.0})]
    assert gen.applicable(state) is False


def test_g05_not_applicable_below_min_coords(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"only": 1.0})]
    assert gen.applicable(state) is False


def test_g05_applicable_with_promoted_and_enough_coords(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"a": 1.0, "b": 2.0})]
    assert gen.applicable(state) is True


def test_g05_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted(
        "r1", {"target": 5.0, "confound": 100.0},
    )]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "complete_signal_collapse"
    assert claim.composition_payload["candidate_confound_key"] == "pl.confound"
    assert claim.composition_payload["target_key"] == "pl.target"


def test_g05_metadata():
    g = ConfoundSwapGenerator()
    assert g.id == "g05_confound_swap"
    assert g.feasibility_tier == "C"
    assert g.reasoning_tier == "R5"


def test_g05_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"x": 1.0, "y": 2.0})]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G05-confound_swap_")


def test_g05_skips_tried_pair(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"a": 1.0, "b": 2.0})]
    # Pre-populate tried_pairs with the expected key
    state.tried_pairs.add("g05_confound_swap|r1|pl.b|pl.a")
    assert gen.applicable(state) is False
