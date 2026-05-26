"""TDD tests for G02 Contrast Generator.

Per DNA P3: input handling, transformation correctness, output
schema, falsification route validity, applicability gate.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g02_contrast import (
    ContrastGenerator,
    GENERIC_BINARY_SPLIT,
    PROBLEM_BINARY_SPLITS,
    _is_substantive_for_contrast,
)
from charon.agents.erebos.tests._fixtures import (
    baseline_swarm_state,
    empty_swarm_state,
    sample_stygian_rows,
)


@pytest.fixture
def gen():
    return ContrastGenerator()


# ---- Helper logic ----------------------------------------------------

def test_substantive_filter_accepts_rejected_with_tests():
    row = sample_stygian_rows()[1]  # REJECTED with tests
    assert _is_substantive_for_contrast(row) is True


def test_substantive_filter_accepts_unverified_with_tests():
    row = sample_stygian_rows()[0]  # UNVERIFIED with tests
    assert _is_substantive_for_contrast(row) is True


def test_substantive_filter_rejects_pending_short_circuit():
    row = {
        "verdict": "UNVERIFIED",
        "kill_pattern": "stygian_no_loader_registered",
        "kill_vector": None,
    }
    assert _is_substantive_for_contrast(row) is False


def test_substantive_filter_rejects_missing_kill_vector():
    row = {
        "verdict": "UNVERIFIED",
        "kill_pattern": None,
        "kill_vector": None,
    }
    assert _is_substantive_for_contrast(row) is False


def test_substantive_filter_rejects_empty_tests():
    row = {
        "verdict": "REJECTED",
        "kill_pattern": "stygian_something",
        "kill_vector": {"tests": {}},  # empty
    }
    assert _is_substantive_for_contrast(row) is False


# ---- Applicability gate ----------------------------------------------

def test_g02_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g02_applicable_with_substantive_stygian(gen):
    state = empty_swarm_state()
    state.stygian_substantive = sample_stygian_rows()
    assert gen.applicable(state) is True


def test_g02_not_applicable_when_all_tried(gen):
    state = empty_swarm_state()
    state.stygian_substantive = sample_stygian_rows()
    for r in state.stygian_substantive:
        state.tried_pairs.add(f"{gen.id}|{r['record_id']}")
    assert gen.applicable(state) is False


# ---- Generation ------------------------------------------------------

def test_g02_generate_returns_composed_claim(gen):
    claim = gen.generate(baseline_swarm_state())
    assert claim is not None
    assert isinstance(claim, ComposedClaim)


def test_g02_six_field_spec_compliance(gen):
    claim = gen.generate(baseline_swarm_state())
    assert claim is not None
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()
    assert claim.expected_kill_pattern.strip()
    assert claim.loader_feasibility_note.strip()


def test_g02_expected_kill_pattern_is_permutation_null(gen):
    claim = gen.generate(baseline_swarm_state())
    assert claim.expected_kill_pattern == "permutation_null"


def test_g02_composed_id_format(gen):
    claim = gen.generate(baseline_swarm_state())
    assert claim.composed_id.startswith("EREBOS-G02-")


def test_g02_uses_problem_specific_split_when_registered(gen):
    """For BL-C-002 (registered), uses cm_vs_non_cm not generic."""
    claim = gen.generate(baseline_swarm_state())
    # Fixture's first chosen row is BL-C-002 REJECTED (newest)
    # → cm_vs_non_cm split
    assert "cm_vs_non_cm" in claim.composed_id
    assert claim.input_provenance.get("split_name") == "cm_vs_non_cm"
    assert claim.input_provenance.get("is_generic_split") is False


def test_g02_falls_back_to_generic_split_for_unknown_problem(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        {
            "record_id": "stygian_unknown_001",
            "canonical_claim_text": "BL-C-UNREGISTERED test",
            "verdict": "REJECTED",
            "kill_pattern": "stygian_some_failure",
            "kill_vector": {"tests": {"F15": {"verdict": "FAIL"}}},
            "generator_id": "stygian",
            "emitted_at": "2026-05-26T00:00:00+00:00",
            "claim_payload": {"problem_id": "BL-C-UNREGISTERED"},
            "extras": {},
        },
    ]
    claim = gen.generate(state)
    assert claim is not None
    assert claim.input_provenance.get("is_generic_split") is True
    assert claim.input_provenance.get("split_name") == GENERIC_BINARY_SPLIT["split_name"]


def test_g02_plugin_id_correct(gen):
    claim = gen.generate(baseline_swarm_state())
    assert claim.plugin_id == "g02_contrast"


def test_g02_parent_record_id_is_single_stygian(gen):
    claim = gen.generate(baseline_swarm_state())
    # G02 takes ONE Stygian row (not a pair)
    assert len(claim.parent_record_ids) == 1


def test_g02_returns_none_when_no_substantive(gen):
    assert gen.generate(empty_swarm_state()) is None


# ---- Metadata ---------------------------------------------------------

def test_g02_metadata():
    gen = ContrastGenerator()
    assert gen.id == "g02_contrast"
    assert gen.name == "Contrast Generator"
    assert gen.spec_phase == 1
    assert gen.feasibility_tier == "S"


def test_g02_falsification_route_mentions_permutation(gen):
    """DNA P2 field 4: route names the specific permutation
    mechanism."""
    claim = gen.generate(baseline_swarm_state())
    fr = claim.falsification_route.lower()
    assert "permutation" in fr
    assert "1000" in fr or "shuffle" in fr


def test_g02_known_problem_splits_present():
    """Sanity: PROBLEM_BINARY_SPLITS has registered entries for the
    Stygian loaders that exist (BL-C-001 + BL-C-002)."""
    assert "BL-C-001" in PROBLEM_BINARY_SPLITS
    assert "BL-C-002" in PROBLEM_BINARY_SPLITS
