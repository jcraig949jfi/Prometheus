"""TDD tests for G14 Relation-Strengthening."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators._predicate_lattice import (
    find_weakest_predicate,
    tier_above,
)
from charon.agents.erebos.generators.g14_relation_strengthening import (
    RelationStrengtheningGenerator,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row_with_text(text: str, record_id: str = "r1") -> dict:
    return {
        "record_id": record_id,
        "canonical_claim_text": text,
        "verdict": "PROMOTED",
        "kill_pattern": None,
        "kill_vector": {"corr_raw": 0.9, "corr_norm": 0.85},
        "generator_id": "pollux",
        "emitted_at": "2026-05-27T00:00:00+00:00",
        "claim_payload": {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return RelationStrengtheningGenerator()


# ---- Lattice helpers --------------------------------------------

def test_find_weakest_returns_lowest_rank():
    text = "A equals B but at minimum they have same sign"
    tier = find_weakest_predicate(text)
    assert tier is not None
    assert tier.canonical_name == "sign_equality"  # rank 1


def test_tier_above_at_top_returns_none():
    from charon.agents.erebos.generators._predicate_lattice import PREDICATE_LATTICE
    strongest = max(PREDICATE_LATTICE, key=lambda t: t.rank)
    assert tier_above(strongest) is None


# ---- Applicability ---------------------------------------------

def test_g14_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g14_applicable_with_sign_equality(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_text("sign(A) = sign(B)")]
    assert gen.applicable(state) is True


def test_g14_not_applicable_when_already_strongest(gen):
    """G14 walks UP. If text uses the strongest predicate,
    nothing stronger is available."""
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_text("A equals B exactly")]
    assert gen.applicable(state) is False


# ---- Generation ------------------------------------------------

def test_g14_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_text("sign(A) = sign(B)")]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g14_six_field_compliance(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_text("divides B")]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g14_expected_kill_pattern_correct(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_text("divides B")]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "predicate_strengthened_past_truth"


def test_g14_composed_id_format(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_text("divides B")]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G14-strengthen_")


def test_g14_metadata():
    gen = RelationStrengtheningGenerator()
    assert gen.id == "g14_relation_strengthening"
    assert gen.spec_phase == 3
    assert gen.feasibility_tier == "A"
    assert gen.reasoning_tier == "R8"


def test_g14_returns_none_when_not_applicable(gen):
    assert gen.generate(empty_swarm_state()) is None
