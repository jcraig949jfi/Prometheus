"""TDD tests for G18 Minimal-Counterexample."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g18_minimal_counterexample import (
    MIN_PRIOR_KILLS,
    MinimalCounterexampleGenerator,
    _is_unverified_pending,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _stygian_pending(rid: str = "r1", problem_id: str = "BL-C-005") -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"Stygian attempted attack on {problem_id}",
        "verdict": "UNVERIFIED",
        "kill_pattern": "stygian_no_loader_registered",
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {"problem_id": problem_id},
        "extras": {},
    }


def _erebos_rejected(rid: str, kp: str) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"composition {rid}",
        "verdict": "REJECTED",
        "kill_pattern": kp,
        "kill_vector": None,
        "generator_id": "erebos",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return MinimalCounterexampleGenerator()


def test_is_unverified_pending_true_for_short_circuits():
    row = {
        "verdict": "UNVERIFIED",
        "kill_pattern": "stygian_no_loader_registered",
    }
    assert _is_unverified_pending(row) is True


def test_is_unverified_pending_false_for_real_unverified():
    row = {
        "verdict": "UNVERIFIED",
        "kill_pattern": None,
    }
    assert _is_unverified_pending(row) is False


def test_g18_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g18_not_applicable_without_pending_parents(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_rejected(f"e{i}", "kp_alpha") for i in range(5)
    ]
    assert gen.applicable(state) is False


def test_g18_not_applicable_with_insufficient_gradient(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_stygian_pending()]
    state.erebos_self_ledger = [
        _erebos_rejected("e1", "kp_alpha"),
        _erebos_rejected("e2", "kp_alpha"),
    ]  # only 2 < MIN_PRIOR_KILLS=3
    assert gen.applicable(state) is False


def test_g18_applicable_with_pending_and_gradient(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_stygian_pending()]
    state.erebos_self_ledger = [
        _erebos_rejected(f"e{i}", "kp_modal") for i in range(3)
    ] + [_erebos_rejected("e4", "kp_other")]
    assert gen.applicable(state) is True


def test_g18_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_stygian_pending()]
    state.erebos_self_ledger = [
        _erebos_rejected(f"e{i}", "kp_modal") for i in range(5)
    ]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g18_predicts_modal_kill_pattern_as_region(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_stygian_pending()]
    state.erebos_self_ledger = [
        _erebos_rejected(f"a{i}", "kp_modal") for i in range(5)
    ] + [_erebos_rejected("b1", "kp_minor")]
    claim = gen.generate(state)
    assert claim.composition_payload["predicted_region"] == "kp_modal"


def test_g18_expected_kill_pattern(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_stygian_pending()]
    state.erebos_self_ledger = [
        _erebos_rejected(f"e{i}", "kp_x") for i in range(3)
    ]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "region_R_exhausted_without_counterexample"


def test_g18_metadata():
    g = MinimalCounterexampleGenerator()
    assert g.id == "g18_minimal_counterexample"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R4"
