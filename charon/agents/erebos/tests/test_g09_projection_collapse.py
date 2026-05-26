"""TDD tests for G09 Projection-Collapse Generator."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim, SwarmState
from charon.agents.erebos.generators.g09_projection_collapse import (
    CAPTURE_THRESHOLD,
    MIN_PAYLOAD_COORDS,
    ProjectionCollapseGenerator,
    _extract_numeric_fields,
)
from charon.agents.erebos.tests._fixtures import (
    baseline_swarm_state,
    empty_swarm_state,
)


def _erebos_row(record_id: str, payload: dict, emitted_at: str = "2026-05-26T00:00:00+00:00") -> dict:
    """Construct a fixture Erebos kill_ledger row with the given
    composition_payload nested inside extras (mirrors the actual
    daemon emission shape)."""
    return {
        "record_id": record_id,
        "canonical_claim_text": f"Erebos composition {record_id}",
        "verdict": "UNVERIFIED",
        "kill_pattern": "erebos_g01_intersection_pending",
        "kill_vector": None,
        "generator_id": "erebos",
        "emitted_at": emitted_at,
        "claim_payload": {
            "plugin_id": "g01_intersection",
            "composed_id": f"EREBOS-G01-test-{record_id}",
        },
        "extras": {"composition_payload": payload},
    }


def _multi_coord_payload(**numeric_kw) -> dict:
    return numeric_kw


@pytest.fixture
def gen():
    return ProjectionCollapseGenerator()


# ---- _extract_numeric_fields helper --------------------------------

def test_extract_numeric_strips_bools():
    out = _extract_numeric_fields({"a": 1, "b": True, "c": 2.5})
    assert "b" not in out
    assert out == {"a": 1.0, "c": 2.5}


def test_extract_numeric_strips_strings():
    out = _extract_numeric_fields({"a": 1, "name": "foo"})
    assert out == {"a": 1.0}


def test_extract_numeric_empty_payload():
    assert _extract_numeric_fields({}) == {}


def test_extract_numeric_none_payload():
    assert _extract_numeric_fields(None) == {}


# ---- Applicability gate --------------------------------------------

def test_g09_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g09_not_applicable_with_only_baseline_state(gen):
    """baseline_swarm_state has empty erebos_self_ledger."""
    assert gen.applicable(baseline_swarm_state()) is False


def test_g09_not_applicable_with_single_coord_payload(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"only_field": 1.0}),
    ]
    assert gen.applicable(state) is False


def test_g09_applicable_with_multi_coord_payload(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 2.0, "c": 3.0}),
    ]
    assert gen.applicable(state) is True


def test_g09_not_applicable_when_tried(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 2.0}),
    ]
    state.tried_pairs.add(f"{gen.id}|e1")
    assert gen.applicable(state) is False


# ---- Generation -----------------------------------------------------

def test_g09_generate_returns_composed_claim(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 100.0, "c": 3.0}),
    ]
    claim = gen.generate(state)
    assert claim is not None
    assert isinstance(claim, ComposedClaim)


def test_g09_picks_max_absolute_magnitude(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"small": 0.5, "huge": 1000.0, "medium": 5.0}),
    ]
    claim = gen.generate(state)
    assert claim.composition_payload["chosen_coord"] == "huge"
    assert claim.composition_payload["chosen_value"] == 1000.0


def test_g09_picks_max_by_absolute_value_not_signed(gen):
    """Negative-large should beat positive-small."""
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 0.3, "b": -10.0, "c": 1.0}),
    ]
    claim = gen.generate(state)
    assert claim.composition_payload["chosen_coord"] == "b"


def test_g09_six_field_spec_compliance(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 2.0}),
    ]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()
    assert claim.expected_kill_pattern.strip()
    assert claim.loader_feasibility_note.strip()


def test_g09_expected_kill_pattern_correct(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 2.0}),
    ]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "residual_survival"


def test_g09_composed_id_format(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 2.0}),
    ]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G09-collapse_to-")


def test_g09_picks_newest_parent_first(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e_old", {"a": 1.0, "b": 2.0},
                    emitted_at="2026-05-25T00:00:00+00:00"),
        _erebos_row("e_new", {"a": 1.0, "b": 2.0},
                    emitted_at="2026-05-26T00:00:00+00:00"),
    ]
    claim = gen.generate(state)
    assert claim.parent_record_ids == ["e_new"]


def test_g09_skips_payloads_with_only_bools_or_strings(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a_flag": True, "b_flag": False, "name": "x"}),
    ]
    # No numeric fields at all -> not applicable
    assert gen.applicable(state) is False


def test_g09_returns_none_when_not_applicable(gen):
    assert gen.generate(empty_swarm_state()) is None


# ---- Metadata + DNA conformance ------------------------------------

def test_g09_metadata():
    gen = ProjectionCollapseGenerator()
    assert gen.id == "g09_projection_collapse"
    assert gen.name == "Projection-Collapse"
    assert gen.spec_phase == 2
    assert gen.feasibility_tier == "S"
    assert gen.reasoning_tier == "R3"


def test_g09_falsification_route_mentions_ablation(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 2.0}),
    ]
    claim = gen.generate(state)
    fr = claim.falsification_route.lower()
    assert "ablation" in fr or "drop" in fr or "omit" in fr


def test_g09_capture_threshold_in_output_text(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("e1", {"a": 1.0, "b": 2.0}),
    ]
    claim = gen.generate(state)
    # Output text should mention the predicted capture percentage
    assert str(int(CAPTURE_THRESHOLD * 100)) in claim.output_claim_text
