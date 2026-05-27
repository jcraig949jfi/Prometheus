"""TDD tests for G08 Dimensional-Lift."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g08_dimensional_lift import (
    DimensionalLiftGenerator,
    MIN_JOINT_DIMS,
    _is_borderline_scalar,
    _numeric_coords,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row_with_coords(rid: str, verdict: str, kv: dict, payload: dict = None) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"parent {rid}",
        "verdict": verdict,
        "kill_pattern": None,
        "kill_vector": kv,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": payload or {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return DimensionalLiftGenerator()


def test_numeric_coords_skips_bools():
    """Booleans should NOT be treated as numeric coordinates."""
    row = {
        "kill_vector": {"a": 1.5, "b": True, "c": 2},
        "extras": {}, "claim_payload": {},
    }
    coords = _numeric_coords(row)
    assert "kv.a" in coords
    assert "kv.c" in coords
    assert "kv.b" not in coords


def test_is_borderline_unverified():
    assert _is_borderline_scalar({"verdict": "UNVERIFIED"}) is True


def test_is_borderline_pollux_midrange():
    assert _is_borderline_scalar({"kill_vector": {"corr_raw": 0.5}}) is True


def test_is_borderline_strong_corr_rejected():
    """|corr|=0.95 is NOT borderline; the strong signal speaks for itself."""
    row = {"verdict": "REJECTED", "kill_vector": {"corr_raw": 0.95}}
    assert _is_borderline_scalar(row) is False


def test_g08_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g08_not_applicable_below_min_dims(gen):
    """Borderline but only 2 numeric coords → cannot lift."""
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_coords(
        "r1", "UNVERIFIED", {"a": 1.0, "b": 2.0},
    )]
    assert gen.applicable(state) is False


def test_g08_applicable_with_enough_dims(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_coords(
        "r1", "UNVERIFIED", {"a": 1.0, "b": 2.0, "c": 3.0},
    )]
    assert gen.applicable(state) is True


def test_g08_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_coords(
        "r1", "UNVERIFIED",
        {"degree": 12, "discriminant": -7.5, "conductor": 1000.0,
         "torsion": 4},
    )]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "overfitting_goodharting"
    assert len(claim.composition_payload["selected_keys"]) >= MIN_JOINT_DIMS


def test_g08_metadata():
    g = DimensionalLiftGenerator()
    assert g.id == "g08_dimensional_lift"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R6"


def test_g08_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_coords(
        "r1", "POSSIBLE",
        {"x": 1.0, "y": 2.0, "z": 3.0, "w": 4.0},
    )]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G08-lift_")
    assert "dim" in claim.composed_id


def test_g08_skips_tried_pair(gen):
    state = empty_swarm_state()
    row = _row_with_coords(
        "r1", "UNVERIFIED",
        {"a": 1.0, "b": 2.0, "c": 3.0},
    )
    state.stygian_substantive = [row]
    # Force the candidate key into tried_pairs to simulate already-emitted
    state.tried_pairs.add(f"g08_dimensional_lift|r1|kv.a,kv.b,kv.c")
    assert gen.applicable(state) is False
