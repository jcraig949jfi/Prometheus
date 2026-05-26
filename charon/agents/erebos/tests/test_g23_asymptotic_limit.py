"""TDD tests for G23 Asymptotic Limit."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g23_asymptotic_limit import (
    AsymptoticLimitGenerator,
    COMPLEXITY_FIELDS,
    _pick_complexity_field,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _erebos_row(rid: str, verdict: str, payload: dict) -> dict:
    return {
        "record_id": rid, "canonical_claim_text": f"comp {rid}",
        "verdict": verdict, "kill_pattern": None,
        "kill_vector": None, "generator_id": "erebos",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {}, "extras": {"composition_payload": payload},
    }


@pytest.fixture
def gen():
    return AsymptoticLimitGenerator()


def test_pick_complexity_field_finds_conductor():
    out = _pick_complexity_field({"conductor": 100, "junk": "x"})
    assert out == ("conductor", 100.0)


def test_pick_complexity_field_skips_zero():
    """0-valued complexity fields are degenerate; should be skipped."""
    assert _pick_complexity_field({"degree": 0}) is None


def test_g23_not_applicable_with_promoted_only(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row("r1", "PROMOTED", {"degree": 5})]
    assert gen.applicable(state) is False


def test_g23_applicable_with_unverified_and_complexity(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row("r1", "UNVERIFIED", {"degree": 12})]
    assert gen.applicable(state) is True


def test_g23_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row("r1", "REJECTED", {"degree": 8})]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "error_term_does_not_decay"


def test_g23_metadata():
    g = AsymptoticLimitGenerator()
    assert g.id == "g23_asymptotic_limit"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R3"


def test_g23_composed_id_format(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_row("r1", "UNVERIFIED", {"n_paired": 50})]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G23-asymptotic_O_1_over_")
