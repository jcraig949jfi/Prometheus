"""TDD tests for G10 Boundary."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g10_boundary import (
    SIZE_LIKE_FIELDS,
    BoundaryGenerator,
    _pick_size_field,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _erebos_row_with_payload(rid: str, payload: dict) -> dict:
    return {
        "record_id": rid, "canonical_claim_text": f"comp {rid}",
        "verdict": "UNVERIFIED", "kill_pattern": "erebos_pending",
        "kill_vector": None, "generator_id": "erebos",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {}, "extras": {"composition_payload": payload},
    }


@pytest.fixture
def gen():
    return BoundaryGenerator()


def test_pick_size_field_finds_degree():
    out = _pick_size_field({"degree": 10, "other": "x"})
    assert out == ("degree", 10.0)


def test_pick_size_field_returns_none_when_no_size_field():
    assert _pick_size_field({"random_field": 42}) is None


def test_g10_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g10_applicable_with_size_field(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row_with_payload("r1", {"degree": 12})]
    assert gen.applicable(state) is True


def test_g10_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row_with_payload("r1", {"n_paired": 50})]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "smooth_degradation"


def test_g10_six_field_compliance(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row_with_payload("r1", {"degree": 8})]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g10_metadata():
    g = BoundaryGenerator()
    assert g.id == "g10_boundary"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R3"


def test_g10_composed_id_format(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row_with_payload("r1", {"degree": 10})]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G10-boundary_")
