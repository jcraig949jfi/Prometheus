"""TDD tests for the §4 null battery + control #8 operator-artifact (Stage 0).

The null battery is the anti-artifact core of protocol v0.2: it decides whether an
observed non_gradient_mass exceeds what null procedures produce. The CENTRAL test
(composition) is the instrument distinguishing real planted structure from the
operator-induced floor:
  - planted-cycle (real curl)  BEATS the degree-preserving-rewire null  (low p)
  - no-cycle (no structure)     does NOT beat it                         (high p)
  - operator-artifact           does NOT beat the operator-label-shuffle null
                                (high p -> the floor; the menu didn't manufacture
                                 structure beyond itself)
"""
import numpy as np
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.controls import (
    no_cycle_graph,
    planted_cycle_graph,
    operator_artifact_graph,
)
from aporia.experiments.reasoning_steering.stage0.nulls import (
    null_pvalue,
    degree_preserving_rewire,
    operator_label_shuffle,
    run_null,
    NullResult,
)


# --------------------------------------------------------------------------
# 1. AUTHORITY — hand-computed p-values + the #8 multiset invariant.
# --------------------------------------------------------------------------
def test_authority_null_pvalue_hand_values():
    """Smoothed permutation p-value p = (#{null >= observed} + 1) / (n + 1).

    Hand: observed 0.5 vs nulls [0.1,0.2,0.3,0.4] -> 0 ge => (0+1)/5 = 0.2.
          observed 0.05 vs same                  -> 4 ge => (4+1)/5 = 1.0.
          observed 0.25 vs same                  -> 2 ge => (2+1)/5 = 0.6.
    Reference: standard Monte-Carlo permutation p-value (Davison & Hinkley 1997).
    """
    nulls = [0.1, 0.2, 0.3, 0.4]
    assert null_pvalue(0.5, nulls) == pytest.approx(0.2)
    assert null_pvalue(0.05, nulls) == pytest.approx(1.0)
    assert null_pvalue(0.25, nulls) == pytest.approx(0.6)


def test_authority_operator_artifact_preserves_label_multiset():
    """#8 builds the exact operator multiset on randomized topology."""
    counts = {"A": 3, "B": 2}
    cg = operator_artifact_graph(counts, n_nodes=6, seed=0)
    assert cg.G.number_of_edges() == 5
    got = {}
    for op in cg.edge_operators.values():
        got[op] = got.get(op, 0) + 1
    assert got == counts
    # valid decomposition
    d = hodge_decompose(cg.G, cg.flow)
    assert (d.gradient_mass + d.curl_mass + d.harmonic_mass) == pytest.approx(1.0, abs=1e-7)


# --------------------------------------------------------------------------
# 2. PROPERTY
# --------------------------------------------------------------------------
@settings(max_examples=50, deadline=None)
@given(
    obs=st.floats(min_value=0.0, max_value=1.0),
    nulls=st.lists(st.floats(0.0, 1.0), min_size=1, max_size=40),
)
def test_property_pvalue_in_unit_interval(obs, nulls):
    p = null_pvalue(obs, nulls)
    assert 0.0 < p <= 1.0


@settings(max_examples=30, deadline=None)
@given(seed=st.integers(0, 10_000))
def test_property_degree_preserving_rewire_keeps_degree_sequence(seed):
    cg = planted_cycle_graph(3, seed=seed)
    H = degree_preserving_rewire(cg.G, seed=seed)
    assert sorted(d for _, d in H.degree()) == sorted(d for _, d in cg.G.degree())
    assert H.number_of_edges() == cg.G.number_of_edges()


@settings(max_examples=30, deadline=None)
@given(seed=st.integers(0, 10_000))
def test_property_operator_label_shuffle_keeps_multiset_and_graph(seed):
    cg = operator_artifact_graph({"A": 4, "B": 3, "C": 2}, n_nodes=8, seed=seed)
    f = operator_label_shuffle(cg, seed=seed)
    assert set(f.keys()) == set(cg.flow.keys())            # same edges
    # flow values are signature values, so the multiset of values is preserved
    assert sorted(np.round(list(f.values()), 9)) == sorted(np.round(list(cg.flow.values()), 9))


# --------------------------------------------------------------------------
# 3. EDGE CASES
# --------------------------------------------------------------------------
def test_edge_cases():
    """Edges:
    - null_pvalue with empty null list: ValueError
    - run_null with n_samples<1: ValueError
    - operator_artifact empty counts / too many edges / tiny n_nodes: ValueError
    - operator_label_shuffle on a control with no edge_operators: ValueError
    """
    with pytest.raises(ValueError):
        null_pvalue(0.5, [])
    cg = planted_cycle_graph(2, seed=0)
    with pytest.raises(ValueError):
        run_null(cg, n_samples=0, seed=0)
    with pytest.raises(ValueError):
        operator_artifact_graph({}, n_nodes=5, seed=0)
    with pytest.raises(ValueError):
        operator_artifact_graph({"A": 100}, n_nodes=4, seed=0)  # > 6 possible edges
    with pytest.raises(ValueError):
        operator_label_shuffle(cg, seed=0)  # planted_cycle has no edge_operators


# --------------------------------------------------------------------------
# 4. COMPOSITION — the central anti-artifact test.
# --------------------------------------------------------------------------
def test_composition_planted_cycle_beats_rewire_null():
    """Real planted curl exceeds the degree-preserving-rewire null (low p)."""
    cg = planted_cycle_graph(4, seed=1)
    res = run_null(cg, n_samples=200, seed=2, kind="degree_preserving_rewire")
    assert isinstance(res, NullResult)
    assert res.observed > res.null_mean
    assert res.pvalue < 0.1


def test_composition_no_cycle_does_not_beat_null():
    """No structure: observed ~ 0 does not beat the rewire null (high p)."""
    cg = no_cycle_graph(12, seed=1)
    res = run_null(cg, n_samples=200, seed=2, kind="degree_preserving_rewire")
    assert res.pvalue > 0.1


def test_composition_operator_artifact_is_a_floor_not_signal():
    """Operator-structured flow on random topology does NOT beat the label-shuffle
    null: there is no structure beyond the operator menu (the false-positive floor).
    """
    cg = operator_artifact_graph({"A": 5, "B": 4, "C": 4, "D": 3}, n_nodes=10, seed=1)
    res = run_null(cg, n_samples=200, seed=2, kind="operator_label_shuffle")
    assert res.pvalue > 0.1
