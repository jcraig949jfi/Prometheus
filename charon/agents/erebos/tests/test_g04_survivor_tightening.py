"""TDD tests for G04 Survivor-Tightening."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g04_survivor_tightening import (
    FIELD_TO_LADDER,
    TIGHTENING_LADDER,
    SurvivorTighteningGenerator,
    _next_tighter,
    _pick_field_and_value,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row_with_payload(payload: dict, record_id: str = "r1",
                      verdict: str = "PROMOTED",
                      generator_id: str = "pollux") -> dict:
    return {
        "record_id": record_id,
        "canonical_claim_text": f"claim {record_id}",
        "verdict": verdict,
        "kill_pattern": None,
        "kill_vector": payload,
        "generator_id": generator_id,
        "emitted_at": "2026-05-27T00:00:00+00:00",
        "claim_payload": {},
        "extras": {"composition_payload": {}},
    }


@pytest.fixture
def gen():
    return SurvivorTighteningGenerator()


# ---- Ladder helpers ---------------------------------------------

def test_next_tighter_correlation_ascending():
    # Ascending ladder: tighter = larger
    assert _next_tighter(TIGHTENING_LADDER["correlation"], 0.6) == 0.7


def test_next_tighter_p_value_descending():
    # Descending ladder: tighter = smaller
    assert _next_tighter(TIGHTENING_LADDER["p_value"], 0.05) == 0.01


def test_next_tighter_at_extreme_returns_none():
    # correlation observed already above all ladder rungs
    assert _next_tighter(TIGHTENING_LADDER["correlation"], 1.0) is None
    # p_value observed already below all ladder rungs
    assert _next_tighter(TIGHTENING_LADDER["p_value"], 0.000001) is None


def test_pick_field_picks_known_ladder_field():
    row = _row_with_payload({"corr_raw": 0.85, "n_paired": 100})
    picked = _pick_field_and_value(row)
    assert picked is not None
    field, observed, ladder = picked
    # 'n_paired' is NOT in FIELD_TO_LADDER, so corr_raw must be chosen
    assert field == "corr_raw"
    assert ladder == "correlation"


def test_pick_field_picks_max_magnitude_among_candidates():
    row = _row_with_payload({"corr_raw": 0.50, "corr_norm": 0.90})
    picked = _pick_field_and_value(row)
    field, observed, _ = picked
    assert field == "corr_norm"
    assert observed == 0.90


def test_pick_field_returns_none_when_no_known_field():
    row = _row_with_payload({"unknown_metric": 0.99})
    assert _pick_field_and_value(row) is None


# ---- Applicability ----------------------------------------------

def test_g04_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g04_applicable_with_pollux_promoted_correlation(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"corr_raw": 0.85})]
    assert gen.applicable(state) is True


def test_g04_not_applicable_without_tightenable_field(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"unknown": 1.0})]
    assert gen.applicable(state) is False


def test_g04_not_applicable_when_at_ladder_top(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"corr_raw": 1.0})]
    assert gen.applicable(state) is False


# ---- Generation -------------------------------------------------

def test_g04_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"corr_raw": 0.85})]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g04_tightens_correctly(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"corr_raw": 0.85})]
    claim = gen.generate(state)
    assert claim.composition_payload["tightened_value"] == 0.90
    assert claim.composition_payload["observed_value"] == 0.85


def test_g04_six_field_compliance(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"corr_raw": 0.85})]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g04_expected_kill_pattern_correct(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"corr_raw": 0.85})]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "strict_threshold_violation"


def test_g04_composed_id_format(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_row_with_payload({"corr_raw": 0.85})]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G04-tighten_")


def test_g04_metadata():
    gen = SurvivorTighteningGenerator()
    assert gen.id == "g04_survivor_tightening"
    assert gen.spec_phase == 1
    assert gen.feasibility_tier == "B"
    assert gen.reasoning_tier == "R6"


def test_g04_returns_none_when_not_applicable(gen):
    assert gen.generate(empty_swarm_state()) is None
