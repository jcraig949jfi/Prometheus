"""TDD tests for G20 Instrument-Disagreement."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g20_instrument_disagreement import (
    InstrumentDisagreementGenerator,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _lethe_row(rid: str, text: str) -> dict:
    return {
        "record_id": rid, "canonical_claim_text": text,
        "verdict": "REJECTED",
        "kill_pattern": "lethe_anti_anchor_candidate",
        "kill_vector": None,
        "generator_id": "lethe",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {}, "extras": {},
    }


def _stygian_rejected(rid: str, text: str) -> dict:
    return {
        "record_id": rid, "canonical_claim_text": text,
        "verdict": "REJECTED",
        "kill_pattern": "stygian_f17_failed",
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {}, "extras": {},
    }


@pytest.fixture
def gen():
    return InstrumentDisagreementGenerator()


def test_g20_vacuous_with_no_lethe_emissions(gen):
    """Current state: Lethe doesn't fire false-form-candidates
    against modern frontier models. G20 should be applicable=False
    until Lethe v2."""
    state = empty_swarm_state()
    state.stygian_substantive = [_stygian_rejected("s1", "Lehmer test")]
    assert gen.applicable(state) is False


def test_g20_applicable_with_clash(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _lethe_row("l1", "twin primes conjecture analysis"),  # in stygian pool
        _stygian_rejected("s1", "twin primes empirical disagreement"),
    ]
    assert gen.applicable(state) is True


def test_g20_topic_overlap_detection():
    # static method via class
    cls = InstrumentDisagreementGenerator
    assert cls._topic_overlap("conductor analysis", "elliptic conductor") is True
    assert cls._topic_overlap("alpha beta", "gamma delta") is False


def test_g20_generates_composed_claim_with_concept_k(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _lethe_row("l1", "ternary goldbach test"),
        _stygian_rejected("s1", "ternary something different"),
    ]
    claim = gen.generate(state)
    assert claim is not None
    assert "ternary" in claim.composition_payload["concept_k_candidate"]


def test_g20_expected_kill_pattern(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _lethe_row("l1", "schinzel zassenhaus polynomial"),
        _stygian_rejected("s1", "schinzel test rejected"),
    ]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "instrument_clash_detected"


def test_g20_metadata():
    g = InstrumentDisagreementGenerator()
    assert g.id == "g20_instrument_disagreement"
    assert g.feasibility_tier == "S"
    assert g.reasoning_tier == "R6"
