"""TDD tests for G12 Invariant-Substitution Generator."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim, SwarmState
from charon.agents.erebos.generators.g12_invariant_substitution import (
    KNOWN_INVARIANTS,
    InvariantSubstitutionGenerator,
    _SIM_RAW,
    _sim,
    find_invariants_in_text,
    pick_best_substitution,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row_with_text(text: str, record_id: str = "test_1",
                   generator_id: str = "stygian",
                   emitted_at: str = "2026-05-26T00:00:00+00:00") -> dict:
    return {
        "record_id": record_id,
        "canonical_claim_text": text,
        "verdict": "UNVERIFIED",
        "kill_pattern": None,
        "kill_vector": {"tests": {"F15": {"verdict": "DEVIATES"}}},
        "generator_id": generator_id,
        "emitted_at": emitted_at,
        "claim_payload": {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return InvariantSubstitutionGenerator()


# ---- Similarity helpers --------------------------------------------

def test_sim_diagonal_is_one():
    for inv in KNOWN_INVARIANTS:
        assert _sim(inv, inv) == 1.0


def test_sim_symmetric():
    for (a, b), v in _SIM_RAW.items():
        assert _sim(a, b) == v
        assert _sim(b, a) == v


def test_sim_unknown_pair_returns_zero():
    assert _sim("mahler_measure", "rank") == 0.0  # cross-domain, not registered


def test_sim_known_bsd_pairs():
    assert _sim("rank", "regulator") == 0.70
    assert _sim("rank", "L1") == 0.70
    assert _sim("rank", "tamagawa_product") == 0.20


# ---- Invariant detection in claim text -----------------------------

def test_find_invariants_picks_known_terms():
    text = "M(P) >= M_Lehmer where mahler_measure is the invariant"
    found = find_invariants_in_text(text)
    assert "mahler_measure" in found


def test_find_invariants_ignores_unknown_terms():
    text = "this_is_not_an_invariant"
    assert find_invariants_in_text(text) == set()


def test_find_invariants_whole_word_only():
    text = "regulator-like behavior"  # should match
    assert "regulator" in find_invariants_in_text(text)
    text2 = "premature optimization"
    assert "rank" not in find_invariants_in_text(text2)


def test_find_invariants_case_insensitive():
    text = "RANK distribution test"
    assert "rank" in find_invariants_in_text(text)


# ---- pick_best_substitution -----------------------------------------

def test_pick_best_substitution_returns_max_similarity():
    # For 'rank', best targets are 'regulator' and 'L1' both at 0.70
    pick = pick_best_substitution("rank", tried_targets=set())
    assert pick is not None
    target, sim = pick
    assert target in ("regulator", "L1")  # tie
    assert sim == 0.70


def test_pick_best_substitution_skips_tried():
    # Exclude both 0.70 candidates; next best is cm_flag/cm/sha_an at 0.50
    pick = pick_best_substitution(
        "rank", tried_targets={"regulator", "L1"}
    )
    assert pick is not None
    target, sim = pick
    assert target in ("cm_flag", "cm", "sha_an")
    assert sim == 0.50


def test_pick_best_substitution_none_when_all_tried():
    pick = pick_best_substitution(
        "n_paired", tried_targets={"corr_raw", "corr_norm"}
    )
    # n_paired has registered similarity only with corr_raw + corr_norm
    assert pick is None


def test_pick_best_substitution_never_returns_self():
    pick = pick_best_substitution("rank", tried_targets=set())
    target, _ = pick
    assert target != "rank"


# ---- Applicability gate --------------------------------------------

def test_g12_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g12_not_applicable_with_text_lacking_invariants(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("nothing in here matches")]
    assert gen.applicable(state) is False


def test_g12_applicable_with_text_containing_invariant(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _row_with_text("BSD rank distribution test"),
    ]
    assert gen.applicable(state) is True


def test_g12_not_applicable_when_all_substitutions_tried(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("rank distribution", "rec1")]
    # Mark every possible target for 'rank' as tried
    rank_targets = [
        t for t in KNOWN_INVARIANTS
        if t != "rank" and _sim("rank", t) > 0
    ]
    for t in rank_targets:
        state.tried_pairs.add(f"{gen.id}|rec1|rank|{t}")
    assert gen.applicable(state) is False


# ---- Generation ----------------------------------------------------

def test_g12_generate_returns_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("rank distribution test")]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g12_substitution_uses_best_similarity(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("rank distribution")]
    claim = gen.generate(state)
    # original = rank; best target = regulator OR L1 (both 0.70)
    assert claim.input_provenance["original_invariant"] == "rank"
    assert claim.input_provenance["substituted_invariant"] in ("regulator", "L1")
    assert claim.input_provenance["similarity_score"] == 0.70


def test_g12_six_field_spec_compliance(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("rank claim")]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()
    assert claim.expected_kill_pattern.strip()
    assert claim.loader_feasibility_note.strip()


def test_g12_expected_kill_pattern_correct(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("rank claim")]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "syntactic_or_semantic_failure"


def test_g12_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("rank claim")]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G12-sub_")


def test_g12_picks_newest_parent_first(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [
        _row_with_text("rank old", "old", emitted_at="2026-05-25T00:00:00+00:00"),
        _row_with_text("rank new", "new", emitted_at="2026-05-26T00:00:00+00:00"),
    ]
    claim = gen.generate(state)
    assert claim.parent_record_ids == ["new"]


def test_g12_returns_none_when_not_applicable(gen):
    assert gen.generate(empty_swarm_state()) is None


def test_g12_works_across_all_pools(gen):
    """G12 should pick from Stygian, Pollux, or Erebos pools."""
    state = empty_swarm_state()
    state.pollux_substantive = [
        _row_with_text("corr_raw analysis", "p1", "pollux"),
    ]
    claim = gen.generate(state)
    assert claim is not None
    assert claim.parent_record_ids == ["p1"]


# ---- Metadata ------------------------------------------------------

def test_g12_metadata():
    gen = InvariantSubstitutionGenerator()
    assert gen.id == "g12_invariant_substitution"
    assert gen.name == "Invariant Substitution"
    assert gen.spec_phase == 3
    assert gen.feasibility_tier == "A"
    assert gen.reasoning_tier == "R3"


def test_g12_falsification_route_mentions_battery(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row_with_text("rank claim")]
    claim = gen.generate(state)
    fr = claim.falsification_route.lower()
    assert "battery" in fr or "stygian" in fr
