"""TDD tests for score-and-cache orchestration (Stage 0b v0.3) -- mock scorer, fast."""
from dataclasses import dataclass

import pytest

from aporia.experiments.reasoning_steering.stage0b.cache import (
    score_states, write_cache, load_cache,
)


@dataclass
class _S:                       # InBandState stand-in
    coeffs: tuple
    mahler_measure: float
    name: str


class _MockScorer:
    """Deterministic fake: margin = coeff sum offset by falsifier index."""
    def margin_vector(self, coeffs, mahler):
        base = float(sum(coeffs))
        return {"fA": base, "fB": base + 1.0}


# 1. AUTHORITY
def test_authority_score_states_uses_scorer():
    states = [_S((1, 1), 1.05, "x"), _S((1, 2, 1), 1.10, "y")]
    recs = score_states(states, _MockScorer())
    assert len(recs) == 2
    assert recs[0]["margins"] == {"fA": 2.0, "fB": 3.0}     # sum([1,1])=2
    assert recs[1]["name"] == "y"
    assert recs[1]["mahler_measure"] == 1.10


# 2. PROPERTY
def test_property_records_are_jsonable_and_complete():
    states = [_S((1, -1), 1.02, "a")]
    recs = score_states(states, _MockScorer())
    for r in recs:
        assert set(r) == {"coeffs", "mahler_measure", "name", "margins"}
        assert isinstance(r["coeffs"], list)
        assert all(isinstance(v, float) for v in r["margins"].values())


# 3. EDGE CASES
def test_edge_empty_states():
    assert score_states([], _MockScorer()) == []


# 4. COMPOSITION — write/load round-trip preserves records.
def test_composition_cache_roundtrip(tmp_path):
    states = [_S((1, 1), 1.05, "x"), _S((1, 0, 1), 1.12, "z")]
    recs = score_states(states, _MockScorer())
    p = write_cache(recs, tmp_path / "c.json")
    assert load_cache(p) == recs
