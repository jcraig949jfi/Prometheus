"""TDD tests for G01 Intersection Composer.

Per DNA P3: input handling, transformation correctness, output
schema, falsification route validity, applicability gate.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g01_intersection import (
    IntersectionGenerator,
)
from charon.agents.erebos.tests._fixtures import (
    baseline_swarm_state,
    empty_swarm_state,
    sample_pollux_rows,
    sample_stygian_rows,
)


@pytest.fixture
def gen():
    return IntersectionGenerator()


# ---- Applicability gate ----------------------------------------------

def test_g01_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g01_not_applicable_with_only_stygian(gen):
    state = empty_swarm_state()
    state.stygian_substantive = sample_stygian_rows()
    assert gen.applicable(state) is False


def test_g01_not_applicable_with_only_pollux(gen):
    state = empty_swarm_state()
    state.pollux_substantive = sample_pollux_rows()
    assert gen.applicable(state) is False


def test_g01_applicable_with_both(gen):
    assert gen.applicable(baseline_swarm_state()) is True


def test_g01_not_applicable_when_all_pairs_tried(gen):
    state = baseline_swarm_state()
    # Mark every (S, P) pair as tried
    for s in state.stygian_substantive:
        for p in state.pollux_substantive:
            state.tried_pairs.add(
                f"{gen.id}|{s['record_id']}|{p['record_id']}"
            )
    assert gen.applicable(state) is False


# ---- Generation produces a well-formed claim --------------------------

def test_g01_generate_returns_composed_claim(gen):
    state = baseline_swarm_state()
    claim = gen.generate(state)
    assert claim is not None
    assert isinstance(claim, ComposedClaim)


def test_g01_six_field_spec_compliance(gen):
    """DNA P2: all six required spec fields present and non-empty."""
    state = baseline_swarm_state()
    claim = gen.generate(state)
    assert claim is not None
    assert claim.input_provenance, "input_provenance must be populated"
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()
    assert claim.expected_kill_pattern.strip()
    assert claim.loader_feasibility_note.strip()


def test_g01_expected_kill_pattern_is_base_rate_failure(gen):
    state = baseline_swarm_state()
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "base_rate_failure"


def test_g01_composed_id_starts_with_EREBOS_G01(gen):
    state = baseline_swarm_state()
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G01-")


def test_g01_plugin_id_correct(gen):
    state = baseline_swarm_state()
    claim = gen.generate(state)
    assert claim.plugin_id == "g01_intersection"


def test_g01_parent_record_ids_contain_both_parents(gen):
    state = baseline_swarm_state()
    claim = gen.generate(state)
    assert len(claim.parent_record_ids) == 2
    assert claim.parent_record_ids[0] in [
        r["record_id"] for r in state.stygian_substantive
    ]
    assert claim.parent_record_ids[1] in [
        r["record_id"] for r in state.pollux_substantive
    ]


def test_g01_picks_newest_pair_first(gen):
    """Generator picks highest-emitted_at (newest) S and P first."""
    state = baseline_swarm_state()
    claim = gen.generate(state)
    # newest stygian is stygian_test_002 (2026-05-26T00:01), newest
    # pollux is pollux_test_002 (2026-05-26T00:03)
    assert claim.parent_record_ids[0] == "stygian_test_002"
    assert claim.parent_record_ids[1] == "pollux_test_002"


def test_g01_returns_none_when_no_applicable_pair(gen):
    """If applicable() is False, generate() should also return None."""
    state = empty_swarm_state()
    assert gen.generate(state) is None


# ---- Metadata declarations (DNA P10) ---------------------------------

def test_g01_metadata():
    gen = IntersectionGenerator()
    assert gen.id == "g01_intersection"
    assert gen.name == "Intersection Composer"
    assert gen.spec_phase == 1
    assert gen.feasibility_tier == "S"


def test_g01_falsification_route_mentions_battery(gen):
    """DNA P2 field 4: falsification route must name a real
    falsification mechanism."""
    state = baseline_swarm_state()
    claim = gen.generate(state)
    fr = claim.falsification_route.lower()
    # Either references Stygian battery or the composition-aware
    # loader-pending status
    assert ("battery" in fr) or ("loader" in fr) or ("stygian" in fr)
