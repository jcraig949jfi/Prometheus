"""TDD tests for G13 Relation-Weakening."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators._predicate_lattice import (
    PREDICATE_LATTICE,
    find_strongest_predicate,
    tier_below,
)
from charon.agents.erebos.generators.g13_relation_weakening import (
    RelationWeakeningGenerator,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row_with_text(text: str, record_id: str = "r1",
                   verdict: str = "REJECTED",
                   generator_id: str = "stygian") -> dict:
    return {
        "record_id": record_id,
        "canonical_claim_text": text,
        "verdict": verdict,
        "kill_pattern": "stygian_some_failure",
        "kill_vector": {"tests": {"F15": {"verdict": "FAIL"}}},
        "generator_id": generator_id,
        "emitted_at": "2026-05-27T00:00:00+00:00",
        "claim_payload": {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return RelationWeakeningGenerator()


# ---- Predicate lattice helpers ---------------------------------

def test_lattice_ranks_descend():
    ranks = [t.rank for t in PREDICATE_LATTICE]
    assert ranks == sorted(ranks, reverse=True)


def test_find_strongest_returns_highest_rank_when_multiple_match():
    text = "A equals B and they also have same sign"
    tier = find_strongest_predicate(text)
    assert tier is not None
    assert tier.canonical_name == "exact_equality"


def test_find_strongest_returns_none_when_no_match():
    assert find_strongest_predicate("nothing relevant here") is None


def test_tier_below_returns_one_step_weaker():
    eq = next(t for t in PREDICATE_LATTICE if t.canonical_name == "exact_equality")
    below = tier_below(eq)
    assert below is not None
    assert below.rank == eq.rank - 1


def test_tier_below_at_bottom_returns_none():
    weakest = min(PREDICATE_LATTICE, key=lambda t: t.rank)
    assert tier_below(weakest) is None


# ---- Applicability ---------------------------------------------

def test_g13_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g13_not_applicable_without_predicate_in_text(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("no predicates here")]
    assert gen.applicable(state) is False


def test_g13_applicable_with_equality_in_text(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("M(P) equals M_Lehmer")]
    assert gen.applicable(state) is True


def test_g13_not_applicable_when_already_weakest(gen):
    """If text uses the weakest predicate, no further weakening
    is possible."""
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("sign(A) = sign(B) holds")]
    assert gen.applicable(state) is False


# ---- Generation ------------------------------------------------

def test_g13_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("M(P) equals M_Lehmer")]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g13_six_field_compliance(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("M = M_target")]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()
    assert claim.expected_kill_pattern.strip()
    assert claim.loader_feasibility_note.strip()


def test_g13_expected_kill_pattern_correct(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("M equals target")]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "predicate_weakened_to_triviality"


def test_g13_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("M equals target")]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G13-weaken_")


def test_g13_metadata():
    gen = RelationWeakeningGenerator()
    assert gen.id == "g13_relation_weakening"
    assert gen.spec_phase == 3
    assert gen.feasibility_tier == "A"
    assert gen.reasoning_tier == "R3"


def test_g13_returns_none_when_not_applicable(gen):
    assert gen.generate(empty_swarm_state()) is None
