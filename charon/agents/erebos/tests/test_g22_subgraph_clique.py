"""TDD tests for G22 Subgraph / Clique."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g22_subgraph_clique import (
    MIN_CLIQUE_SIZE,
    MIN_JACCARD,
    SubgraphCliqueGenerator,
    _find_greedy_clique,
    _jaccard,
    _payload_keys,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _erebos_row(record_id: str, payload_keys: list[str],
                plugin_id: str = "g01_intersection",
                emitted_at: str = "2026-05-27T00:00:00+00:00") -> dict:
    """Make a fixture Erebos row with a payload containing exactly
    the given keys. Values are 1.0 placeholders."""
    payload = {k: 1.0 for k in payload_keys}
    return {
        "record_id": record_id,
        "canonical_claim_text": f"composition {record_id}",
        "verdict": "UNVERIFIED",
        "kill_pattern": "erebos_pending",
        "kill_vector": None,
        "generator_id": "erebos",
        "emitted_at": emitted_at,
        "claim_payload": {
            "plugin_id": plugin_id,
            "composed_id": f"EREBOS-X-{record_id}",
        },
        "extras": {"composition_payload": payload},
    }


@pytest.fixture
def gen():
    return SubgraphCliqueGenerator()


# ---- Helpers ----------------------------------------------------

def test_jaccard_identical_sets_is_one():
    a = frozenset(["x", "y", "z"])
    assert _jaccard(a, a) == 1.0


def test_jaccard_disjoint_sets_is_zero():
    assert _jaccard(frozenset(["a"]), frozenset(["b"])) == 0.0


def test_jaccard_half_overlap():
    a = frozenset(["x", "y"])
    b = frozenset(["x", "z"])
    # intersection={x}, union={x,y,z} → 1/3
    assert abs(_jaccard(a, b) - 1/3) < 1e-9


def test_payload_keys_extracts_correctly():
    row = _erebos_row("r1", ["alpha", "beta"])
    assert _payload_keys(row) == frozenset(["alpha", "beta"])


# ---- Greedy clique detection -----------------------------------

def test_find_greedy_clique_returns_empty_when_too_few_rows():
    rows = [_erebos_row("r1", ["x"])]
    assert _find_greedy_clique(rows, min_size=3, min_jaccard=0.4) == []


def test_find_greedy_clique_finds_obvious_clique():
    # 3 rows with identical payload keys → clique of 3
    rows = [
        _erebos_row("r1", ["x", "y", "z"]),
        _erebos_row("r2", ["x", "y", "z"]),
        _erebos_row("r3", ["x", "y", "z"]),
    ]
    clique = _find_greedy_clique(rows, min_size=3, min_jaccard=0.4)
    assert len(clique) == 3


def test_find_greedy_clique_excludes_disconnected():
    rows = [
        _erebos_row("r1", ["x", "y"]),
        _erebos_row("r2", ["x", "y"]),
        _erebos_row("r3", ["x", "y"]),
        _erebos_row("disconnected", ["completely", "different"]),
    ]
    clique = _find_greedy_clique(rows, min_size=3, min_jaccard=0.4)
    assert len(clique) == 3
    assert "disconnected" not in [r["record_id"] for r in clique]


def test_find_greedy_clique_below_jaccard_threshold():
    # Pairs with too little overlap
    rows = [
        _erebos_row("r1", ["a", "x", "y", "z"]),
        _erebos_row("r2", ["b", "x", "y", "z"]),
        _erebos_row("r3", ["c", "p", "q", "r"]),
    ]
    # r1+r2 jaccard = 3/5 = 0.6 (above 0.4)
    # but r3 has zero overlap → can't form 3-clique
    clique = _find_greedy_clique(rows, min_size=3, min_jaccard=0.4)
    assert clique == []


# ---- Plugin gate + generation ----------------------------------

def test_g22_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g22_not_applicable_below_clique_size(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("r1", ["x", "y"]),
        _erebos_row("r2", ["x", "y"]),
    ]
    assert gen.applicable(state) is False


def test_g22_applicable_with_three_overlapping_rows(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("r1", ["a", "b", "c"]),
        _erebos_row("r2", ["a", "b", "c"]),
        _erebos_row("r3", ["a", "b", "c"]),
    ]
    assert gen.applicable(state) is True


def test_g22_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("r1", ["a", "b", "c"]),
        _erebos_row("r2", ["a", "b", "c"]),
        _erebos_row("r3", ["a", "b", "c"]),
    ]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g22_master_property_is_intersection(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("r1", ["common1", "common2", "r1only"]),
        _erebos_row("r2", ["common1", "common2", "r2only"]),
        _erebos_row("r3", ["common1", "common2", "r3only"]),
    ]
    claim = gen.generate(state)
    master = claim.composition_payload["master_property_keys"]
    assert set(master) == {"common1", "common2"}


def test_g22_six_field_compliance(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row(f"r{i}", ["x", "y", "z"]) for i in range(3)
    ]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g22_expected_kill_pattern_correct(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row(f"r{i}", ["x", "y", "z"]) for i in range(3)
    ]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "counterexample_breaks_master_unification"


def test_g22_records_all_clique_parents(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("r1", ["x", "y", "z"]),
        _erebos_row("r2", ["x", "y", "z"]),
        _erebos_row("r3", ["x", "y", "z"]),
    ]
    claim = gen.generate(state)
    assert len(claim.parent_record_ids) >= 3


def test_g22_metadata():
    gen = SubgraphCliqueGenerator()
    assert gen.id == "g22_subgraph_clique"
    assert gen.spec_phase == 5
    assert gen.feasibility_tier == "A"
    assert gen.reasoning_tier == "R3"


def test_g22_returns_none_when_not_applicable(gen):
    assert gen.generate(empty_swarm_state()) is None
