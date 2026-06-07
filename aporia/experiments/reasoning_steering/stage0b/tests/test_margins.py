"""TDD tests for the per-falsifier MARGIN VECTOR (Stage 0b relational, v0.3).

The relational flow needs each state's vector of per-falsifier margins
v(s) = {falsifier_name: margin}, extracted from the KillVector components. The pure
extraction (margins_from_kill_vector) is tested fast with mock components; one slow
authority test confirms it on Lehmer's polynomial through the real pipeline.
"""
import math
from dataclasses import dataclass

import pytest

from aporia.experiments.reasoning_steering.stage0b.damage import (
    margins_from_kill_vector,
    Axis2DamageScorer,
)

LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.1762808182599175


@dataclass
class _C:                       # duck-typed KillComponent stand-in
    falsifier_name: str
    margin: float | None


class _KV:
    def __init__(self, comps):
        self.components = comps


# 1. AUTHORITY
def test_authority_extraction_hand_example():
    """margins_from_kill_vector keeps named float margins, drops None margins."""
    kv = _KV([
        _C("reciprocity", 0.5),
        _C("irreducibility", -1.25),
        _C("F1_permutation_null", 0.0),
        _C("catalog:OEIS", None),         # None margin -> dropped
    ])
    v = margins_from_kill_vector(kv)
    assert v == {"reciprocity": 0.5, "irreducibility": -1.25, "F1_permutation_null": 0.0}


@pytest.mark.slow
def test_authority_lehmer_margin_vector_real_pipeline():
    """Lehmer through the real pipeline exposes the expected falsifier names as a
    float-valued margin vector (reference: Lehmer 1933; in-band so full battery runs)."""
    s = Axis2DamageScorer()
    v = s.margin_vector(LEHMER, LEHMER_M)
    assert all(isinstance(x, float) for x in v.values())
    # the structural falsifiers that run in-band should appear
    assert any(name.startswith("out_of_band") for name in v)
    assert len(v) >= 4


# 2. PROPERTY
def test_property_values_float_keys_named_none_dropped():
    kv = _KV([_C("a", 1.0), _C("b", None), _C("c", -3.0), _C("d", float("nan"))])
    v = margins_from_kill_vector(kv)
    assert set(v) == {"a", "c"}              # None and NaN dropped
    assert all(isinstance(x, float) and math.isfinite(x) for x in v.values())


# 3. EDGE CASES
def test_edge_cases():
    """Edges: no components -> empty dict; all-None margins -> empty dict; missing
    components attribute -> ValueError."""
    assert margins_from_kill_vector(_KV([])) == {}
    assert margins_from_kill_vector(_KV([_C("x", None)])) == {}
    with pytest.raises(ValueError):
        margins_from_kill_vector(object())     # no .components


# 4. COMPOSITION — extraction names align with the Axis-2 passed/failed names.
def test_composition_names_are_falsifier_names():
    """The margin-vector keys are exactly the component falsifier names (the same
    namespace Axis-2 uses for passed/failed), so the two views are consistent."""
    kv = _KV([_C("reciprocity", 0.1), _C("F6_base_rate", -0.2)])
    v = margins_from_kill_vector(kv)
    assert set(v) == {"reciprocity", "F6_base_rate"}
