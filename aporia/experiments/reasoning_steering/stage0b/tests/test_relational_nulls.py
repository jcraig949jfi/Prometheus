"""TDD tests for the relational null battery (Stage 0b v0.3, §5).

Load-bearing authority test: under the falsifier-column-shuffle null, a Condorcet
cycle BEATS the null (genuine non-transitivity), while a transitive ordering does NOT
(its non_gradient_mass is the saturation baseline the null reproduces). This is what
makes the relational H-R1 verdict meaningful.
"""
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0b.flow import relational_flow
from aporia.experiments.reasoning_steering.stage0b.relational_nulls import (
    vectors_from_records, falsifier_column_shuffle, sign_permutation,
    falsifier_family_holdout, run_relational_null, run_relational_family_holdout,
)

# Condorcet cycle (3 falsifiers, 3 states) and a transitive ordering.
CONDORCET = [
    {"margins": {"f1": 3, "f2": 1, "f3": 2}},
    {"margins": {"f1": 2, "f2": 3, "f3": 1}},
    {"margins": {"f1": 1, "f2": 2, "f3": 3}},
]
TRANSITIVE = [
    {"margins": {"f1": 3, "f2": 3, "f3": 3}},
    {"margins": {"f1": 2, "f2": 2, "f3": 2}},
    {"margins": {"f1": 1, "f2": 1, "f3": 1}},
]


# 1. AUTHORITY — the null isolates genuine non-transitivity from the saturation floor.
def test_authority_condorcet_separates_from_column_shuffle_null():
    """The column-shuffle null separates genuine non-transitivity from the saturation
    floor: Condorcet observed sits far above its null mean and its p-value is far below
    the transitive case's.

    NOTE: a 3-state toy is UNDERPOWERED for a hard p<0.05 (a random shuffle re-creates a
    Condorcet cycle ~6% of the time -> p~0.06); that is exactly why the v0.3 guard
    requires >= 8 states. The hard p-threshold applies to the real >=21-state run; here
    we assert the separation, which is robust.
    """
    res_c = run_relational_null(CONDORCET, "falsifier_column_shuffle", n_samples=300, seed=1)
    res_t = run_relational_null(TRANSITIVE, "falsifier_column_shuffle", n_samples=300, seed=1)
    assert res_c.observed == pytest.approx(1.0, abs=1e-9)   # Condorcet = pure curl
    assert res_c.observed > res_c.null_mean + 2 * res_c.null_std   # far above null
    assert res_c.pvalue < res_t.pvalue                     # ... and separates from transitive
    assert res_t.observed < 0.2                            # transitive ~ saturation floor


# 2. PROPERTY
@settings(max_examples=20, deadline=None)
@given(seed=st.integers(0, 10_000))
def test_property_column_shuffle_preserves_per_falsifier_multiset(seed):
    vectors = vectors_from_records(CONDORCET)
    shuffled = falsifier_column_shuffle(vectors, seed)
    for k in ("f1", "f2", "f3"):
        assert sorted(v[k] for v in shuffled) == sorted(v[k] for v in vectors)


def test_property_sign_permutation_preserves_abs_values():
    _, flow = relational_flow(vectors_from_records(CONDORCET))
    flipped = sign_permutation(flow, seed=3)
    assert sorted(abs(v) for v in flipped.values()) == sorted(abs(v) for v in flow.values())


# 3. EDGE CASES
def test_edge_cases():
    with pytest.raises(ValueError):
        run_relational_null(CONDORCET, "falsifier_column_shuffle", n_samples=0, seed=0)
    with pytest.raises(ValueError):
        run_relational_null(CONDORCET, "bogus_kind", n_samples=5, seed=0)
    # holding out a family that carries the cycle reduces non-gradient mass
    held = falsifier_family_holdout(vectors_from_records(CONDORCET), "f1")
    assert all("f1" not in v for v in held)


# 4. COMPOSITION — family holdout reports per-falsifier non_gradient_mass.
def test_composition_family_holdout_map():
    res = run_relational_family_holdout(CONDORCET)
    assert res["_full"] == pytest.approx(1.0, abs=1e-9)
    # removing any single falsifier from a 3-falsifier Condorcet cycle breaks it
    for fam in ("f1", "f2", "f3"):
        assert res[fam] < res["_full"]
