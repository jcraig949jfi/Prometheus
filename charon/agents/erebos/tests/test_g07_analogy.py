"""TDD tests for G07 Analogy."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g07_analogy import (
    ANALOGY_MAP,
    AnalogyGenerator,
    detect_domain,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row(text: str, rid: str = "r1") -> dict:
    return {
        "record_id": rid, "canonical_claim_text": text,
        "verdict": "PROMOTED", "kill_pattern": None,
        "kill_vector": None, "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {}, "extras": {},
    }


@pytest.fixture
def gen():
    return AnalogyGenerator()


def test_detect_domain_mahler():
    assert detect_domain("Lehmer Mahler measure test") == "mahler"


def test_detect_domain_knot():
    assert detect_domain("Knot crossing number analysis") == "knot"


def test_detect_domain_none():
    assert detect_domain("unrelated text") is None


def test_g07_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g07_not_applicable_without_recognizable_domain(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("nothing recognizable")]
    assert gen.applicable(state) is False


def test_g07_applicable_with_mahler_context(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("Salem polynomial Mahler test")]
    assert gen.applicable(state) is True


def test_g07_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("Mahler measure analysis")]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "metaphor_collapse"


def test_g07_metadata():
    g = AnalogyGenerator()
    assert g.id == "g07_analogy"
    assert g.feasibility_tier == "C"
    assert g.reasoning_tier == "R7"


def test_g07_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("Mahler degree test")]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G07-analogy_")
