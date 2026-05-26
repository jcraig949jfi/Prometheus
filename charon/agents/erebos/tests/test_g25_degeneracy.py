"""TDD tests for G25 Degeneracy / Trivial-Case Generator."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim, SwarmState
from charon.agents.erebos.generators.g25_degeneracy import (
    DEGENERATE_REGISTRY,
    DegeneracyGenerator,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _erebos_row_for_problem(record_id: str, problem_id: str,
                            emitted_at: str = "2026-05-26T00:00:00+00:00") -> dict:
    return {
        "record_id": record_id,
        "canonical_claim_text": f"Erebos composition citing {problem_id}",
        "verdict": "UNVERIFIED",
        "kill_pattern": "erebos_g01_intersection_pending",
        "kill_vector": None,
        "generator_id": "erebos",
        "emitted_at": emitted_at,
        "claim_payload": {
            "plugin_id": "g01_intersection",
            "composed_id": f"EREBOS-G01-{problem_id}-x-test_pair",
        },
        "extras": {
            "input_provenance": {
                "stygian_problem_id": problem_id,
                "stygian_record_id": "fake_stygian_id",
                "pollux_record_id": "fake_pollux_id",
            },
            "composition_payload": {},
        },
    }


@pytest.fixture
def gen():
    return DegeneracyGenerator()


# ---- Registry sanity -----------------------------------------------

def test_registry_has_at_least_bl_c_001_and_002():
    assert "BL-C-001" in DEGENERATE_REGISTRY
    assert "BL-C-002" in DEGENERATE_REGISTRY


def test_registry_entries_have_required_fields():
    for problem_id, entry in DEGENERATE_REGISTRY.items():
        assert "name" in entry
        assert "description" in entry
        assert "state" in entry
        assert isinstance(entry["state"], dict)
        assert "trivial_holds_reason" in entry


# ---- Parent-problem extraction ------------------------------------

def test_extract_parent_problem_from_input_provenance(gen):
    row = _erebos_row_for_problem("e1", "BL-C-001")
    assert gen._extract_parent_problem_id(row) == "BL-C-001"


def test_extract_parent_problem_falls_back_to_composed_id(gen):
    row = {
        "record_id": "e1",
        "claim_payload": {"composed_id": "EREBOS-G01-BL-C-002-x-something"},
        "extras": {},
    }
    assert gen._extract_parent_problem_id(row) == "BL-C-002"


def test_extract_parent_problem_returns_none_when_absent(gen):
    row = {
        "record_id": "e1",
        "claim_payload": {"composed_id": "EREBOS-G01-OTHER"},
        "extras": {},
    }
    assert gen._extract_parent_problem_id(row) is None


# ---- Applicability gate -------------------------------------------

def test_g25_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g25_applicable_with_registered_problem(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    assert gen.applicable(state) is True


def test_g25_not_applicable_with_unregistered_problem(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-999"),  # unregistered
    ]
    assert gen.applicable(state) is False


def test_g25_not_applicable_when_tried(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    state.tried_pairs.add(f"{gen.id}|e1")
    assert gen.applicable(state) is False


# ---- Generation ---------------------------------------------------

def test_g25_generate_returns_composed_claim(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g25_picks_correct_degenerate_for_lehmer(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    claim = gen.generate(state)
    assert claim.composition_payload["degenerate_state_name"] == "degree_1_polynomial"
    assert claim.composition_payload["degenerate_state_dict"] == {
        "degree": 1, "salem_class": False, "cyclotomic": False,
    }


def test_g25_picks_correct_degenerate_for_bsd(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-002"),
    ]
    claim = gen.generate(state)
    assert claim.composition_payload["degenerate_state_name"] == "rank_0_curve"
    assert "rank" in claim.composition_payload["degenerate_state_dict"]


def test_g25_six_field_spec_compliance(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()
    assert claim.expected_kill_pattern.strip()
    assert claim.loader_feasibility_note.strip()


def test_g25_expected_kill_pattern_correct(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "division_by_zero_or_type_error"


def test_g25_composed_id_format(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G25-degenerate-")


def test_g25_returns_none_when_not_applicable(gen):
    assert gen.generate(empty_swarm_state()) is None


def test_g25_picks_newest_parent_first(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e_old", "BL-C-001",
                                emitted_at="2026-05-25T00:00:00+00:00"),
        _erebos_row_for_problem("e_new", "BL-C-002",
                                emitted_at="2026-05-26T00:00:00+00:00"),
    ]
    claim = gen.generate(state)
    assert claim.parent_record_ids == ["e_new"]


# ---- Metadata -----------------------------------------------------

def test_g25_metadata():
    gen = DegeneracyGenerator()
    assert gen.id == "g25_degeneracy"
    assert gen.name == "Degeneracy / Trivial-Case"
    assert gen.spec_phase == 5
    assert gen.feasibility_tier == "A"
    assert gen.reasoning_tier == "R6"


def test_g25_falsification_route_mentions_restricted_dataset(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row_for_problem("e1", "BL-C-001"),
    ]
    claim = gen.generate(state)
    fr = claim.falsification_route.lower()
    # Per DNA: route must name the restriction mechanism
    assert "degenerate" in fr or "restrict" in fr or "exclusively" in fr
