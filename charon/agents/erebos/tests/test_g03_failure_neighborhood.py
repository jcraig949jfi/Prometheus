"""TDD tests for G03 Failure-Neighborhood."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g03_failure_neighborhood import (
    ARITHMETIC_LADDER,
    FailureNeighborhoodGenerator,
    arith_below,
    find_strictest_arith,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row(text: str, rid: str = "r1", verdict: str = "REJECTED") -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": text,
        "verdict": verdict,
        "kill_pattern": "stygian_some_kill",
        "kill_vector": {"tests": {"F15": {"verdict": "FAIL"}}},
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return FailureNeighborhoodGenerator()


def test_ladder_ranks_descend():
    ranks = [t["rank"] for t in ARITHMETIC_LADDER]
    assert ranks == sorted(ranks, reverse=True)


def test_find_strictest_returns_highest_rank():
    text = "A = B and A is bounded by K"  # = is rank 5, bounded is rank 2
    tier = find_strictest_arith(text)
    assert tier is not None
    assert tier["name"] == "arith_equality"


def test_find_strictest_returns_none_when_no_arith():
    assert find_strictest_arith("no math operators here") is None


def test_arith_below_returns_one_weaker():
    eq = next(t for t in ARITHMETIC_LADDER if t["name"] == "arith_equality")
    below = arith_below(eq)
    assert below is not None
    assert below["rank"] == eq["rank"] - 1


def test_g03_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g03_not_applicable_with_only_promoted(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("A = B", verdict="PROMOTED")]
    assert gen.applicable(state) is False


def test_g03_applicable_with_rejected_arith(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("A = B")]
    assert gen.applicable(state) is True


def test_g03_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("A = B")]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "boundary_collapse"


def test_g03_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("A = B")]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G03-weaken_")


def test_g03_six_field_compliance(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("A = B")]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g03_metadata():
    g = FailureNeighborhoodGenerator()
    assert g.id == "g03_failure_neighborhood"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R3"
