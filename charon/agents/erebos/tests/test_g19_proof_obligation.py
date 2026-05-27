"""TDD tests for G19 Proof-Obligation."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g19_proof_obligation import (
    MIN_PARENTS,
    ProofObligationGenerator,
    _erebos_row_with_parents,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _erebos_composed(rid: str, parents: list[str], emitted: str = "2026-05-26T00:00:00+00:00") -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"composed {rid}",
        "verdict": "UNVERIFIED",
        "kill_pattern": None,
        "kill_vector": None,
        "generator_id": "erebos",
        "emitted_at": emitted,
        "claim_payload": {},
        "extras": {
            "parent_record_ids": parents,
            "composition_payload": {"parent_record_ids": parents},
        },
    }


def _stygian_row(rid: str, verdict: str) -> dict:
    return {
        "record_id": rid, "canonical_claim_text": f"parent {rid}",
        "verdict": verdict, "kill_pattern": "stygian_f17_failed" if verdict == "REJECTED" else None,
        "kill_vector": None, "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {}, "extras": {},
    }


@pytest.fixture
def gen():
    return ProofObligationGenerator()


def test_erebos_row_with_parents_returns_distinct():
    row = _erebos_composed("c1", ["p1", "p2", "p1"])
    assert _erebos_row_with_parents(row) == ["p1", "p2"]


def test_erebos_row_with_parents_rejects_below_min():
    row = _erebos_composed("c1", ["p1"])
    assert _erebos_row_with_parents(row) is None


def test_g19_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g19_not_applicable_with_single_parent(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_composed("c1", ["p1"])]
    assert gen.applicable(state) is False


def test_g19_applicable_with_multi_parent(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_composed("c1", ["p1", "p2"])]
    assert gen.applicable(state) is True


def test_g19_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_composed("c1", ["p1", "p2", "p3"])]
    state.stygian_substantive = [
        _stygian_row("p1", "PROMOTED"),
        _stygian_row("p2", "REJECTED"),
        _stygian_row("p3", "PROMOTED"),
    ]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "sub_claim_falsified"
    assert claim.composition_payload["n_obligations"] == 3
    assert claim.composition_payload["n_already_falsified"] == 1


def test_g19_detects_already_falsified_sub_obligation(gen):
    """If a parent is already REJECTED in the live ledger, G19 should
    flag it in the claim text."""
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_composed("c1", ["p1", "p2"])]
    state.stygian_substantive = [
        _stygian_row("p1", "PROMOTED"),
        _stygian_row("p2", "REJECTED"),
    ]
    claim = gen.generate(state)
    assert "ALREADY REJECTED" in claim.output_claim_text


def test_g19_no_already_falsified_when_all_promoted(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_composed("c1", ["p1", "p2"])]
    state.stygian_substantive = [
        _stygian_row("p1", "PROMOTED"),
        _stygian_row("p2", "PROMOTED"),
    ]
    claim = gen.generate(state)
    assert claim.composition_payload["n_already_falsified"] == 0


def test_g19_metadata():
    g = ProofObligationGenerator()
    assert g.id == "g19_proof_obligation"
    assert g.feasibility_tier == "C"
    assert g.reasoning_tier == "R8"


def test_g19_composed_id_format(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_composed("c1", ["p1", "p2"])]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G19-proof_obligation_")
    assert "n2" in claim.composed_id


def test_g19_parent_record_ids_includes_obligation_parents(gen):
    """The composed claim's parent_record_ids should include both the
    direct parent (the composed source) and the obligation parents."""
    state = empty_swarm_state()
    state.erebos_self_ledger = [_erebos_composed("c1", ["p1", "p2"])]
    claim = gen.generate(state)
    assert "c1" in claim.parent_record_ids
    assert "p1" in claim.parent_record_ids
    assert "p2" in claim.parent_record_ids
