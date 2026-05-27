"""TDD tests for G21 Isomorphism / Functor."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g21_isomorphism_functor import (
    IsomorphismFunctorGenerator,
    _battery_signature,
    _is_promoted,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _promoted_row(rid: str, text: str, kp: str = None, tier: str = None) -> dict:
    kv = None
    if tier:
        kv = {"overall": {"tier": tier}}
    return {
        "record_id": rid, "canonical_claim_text": text,
        "verdict": "PROMOTED", "kill_pattern": kp,
        "kill_vector": kv, "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {}, "extras": {},
    }


@pytest.fixture
def gen():
    return IsomorphismFunctorGenerator()


def test_battery_signature_from_kill_pattern():
    assert _battery_signature({"kill_pattern": "f17_failed"}) == "kp:f17_failed"


def test_battery_signature_from_tier():
    row = {"kill_vector": {"overall": {"tier": "A"}}}
    assert _battery_signature(row) == "tier:A"


def test_battery_signature_none():
    assert _battery_signature({"kill_pattern": None}) is None


def test_is_promoted():
    assert _is_promoted({"verdict": "PROMOTED"}) is True
    assert _is_promoted({"verdict": "REJECTED"}) is False


def test_g21_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g21_not_applicable_with_single_promoted(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _promoted_row("r1", "Mahler measure test", tier="A"),
    ]
    assert gen.applicable(state) is False


def test_g21_not_applicable_same_domain(gen):
    """Two PROMOTED from the SAME domain don't qualify (need cross-
    domain functor)."""
    state = empty_swarm_state()
    state.stygian_substantive = [
        _promoted_row("r1", "Mahler measure A", tier="A"),
        _promoted_row("r2", "Lehmer test B", tier="A"),
    ]
    assert gen.applicable(state) is False


def test_g21_not_applicable_no_shared_signature(gen):
    """Two cross-domain PROMOTED without shared battery signature
    don't qualify."""
    state = empty_swarm_state()
    state.stygian_substantive = [
        _promoted_row("r1", "Mahler measure", tier="A"),
        _promoted_row("r2", "Knot crossing number", tier="B"),
    ]
    assert gen.applicable(state) is False


def test_g21_applicable_cross_domain_shared_signature(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _promoted_row("r1", "Mahler measure A", tier="A"),
        _promoted_row("r2", "Knot Jones polynomial", tier="A"),
    ]
    assert gen.applicable(state) is True


def test_g21_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _promoted_row("r1", "Mahler measure structure", tier="A"),
        _promoted_row("r2", "BSD elliptic curve conductor", tier="A"),
    ]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "functor_breaks"
    assert claim.composition_payload["shared_battery_signature"] == "tier:A"


def test_g21_metadata():
    g = IsomorphismFunctorGenerator()
    assert g.id == "g21_isomorphism_functor"
    assert g.feasibility_tier == "C"
    assert g.reasoning_tier == "R7"


def test_g21_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _promoted_row("r1", "Mahler test", tier="A"),
        _promoted_row("r2", "Knot alexander", tier="A"),
    ]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G21-functor_")


def test_g21_parent_record_ids_includes_both(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _promoted_row("r1", "Mahler", tier="A"),
        _promoted_row("r2", "Knot", tier="A"),
    ]
    claim = gen.generate(state)
    assert "r1" in claim.parent_record_ids
    assert "r2" in claim.parent_record_ids
