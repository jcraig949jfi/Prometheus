"""TDD tests for the genus-2 corpus loader (Stage 0b relational expansion)."""
import pytest

from aporia.experiments.reasoning_steering.stage0b.g2c_corpus import (
    load_g2c_states, EXCLUDED_FIELDS,
)


# 1. AUTHORITY
def test_authority_loads_states_with_known_invariants():
    """Genus-2 records expose the expected heterogeneous numeric invariants as the
    criteria vector (reference: LMFDB g2c_curves columns)."""
    states = load_g2c_states(12)
    assert len(states) == 12
    crit = states[0]["margins"]
    for inv in ("cond", "abs_disc", "analytic_rank", "torsion_order"):
        assert inv in crit
    assert "id" not in crit                       # row id excluded
    assert all(isinstance(v, float) for v in crit.values())


# 2. PROPERTY
def test_property_deterministic_and_stratified():
    a = load_g2c_states(20)
    b = load_g2c_states(20)
    assert [s["label"] for s in a] == [s["label"] for s in b]      # deterministic
    assert len({s["label"] for s in a}) == 20                       # distinct (stratified)


# 3. EDGE CASES
def test_edge_cases():
    with pytest.raises(ValueError):
        load_g2c_states(1)
    with pytest.raises(ValueError):
        load_g2c_states(10_000_000)


# 4. COMPOSITION — the loaded states carry enough varying criteria for H-R1.
def test_composition_has_varying_criteria():
    states = load_g2c_states(30)
    names = set().union(*[set(s["margins"]) for s in states])
    varying = sum(1 for k in names
                  if len({round(s["margins"][k], 9) for s in states if k in s["margins"]}) >= 2)
    assert varying >= 3                            # passes the criteria-adequacy guard
