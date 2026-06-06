"""TDD tests for the remaining two §4 nulls (Stage 0, protocol v0.2 §4 #2, #4).

  endpoint_permutation   : keep the operator-label multiset, randomise which vertex
                           pair each edge connects (destroy topology). For an
                           operator-artifact this stays a floor.
  emitter_family_holdout : drop ALL edges of one operator family and recompute -- the
                           "generalises beyond the generators" clause. If removing a
                           single family collapses the non_gradient_mass, that family
                           manufactured the signal.
"""
import numpy as np
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.controls import (
    ControlGraph,
    operator_artifact_graph,
)
from aporia.experiments.reasoning_steering.stage0.nulls import (
    endpoint_permutation,
    emitter_family_holdout,
    run_emitter_holdout,
    run_null,
)


def _labelled_triangle_plus_bridge():
    """Triangle 0-1-2 (circulation, family 'C') + bridge 2-3 (family 'B').

    Removing family C destroys the only curl => non_gradient_mass -> 0.
    Removing family B leaves the pure triangle curl => non_gradient_mass -> 1.
    """
    G = nx.Graph([(0, 1), (1, 2), (0, 2), (2, 3)])
    flow = {(0, 1): 1.0, (1, 2): 1.0, (0, 2): -1.0, (2, 3): 0.5}
    edge_ops = {(0, 1): "C", (1, 2): "C", (0, 2): "C", (2, 3): "B"}
    return ControlGraph(
        G=G, flow=flow, kind="manual", expected={}, seed=0,
        edge_operators=edge_ops, meta={},
    )


# --------------------------------------------------------------------------
# 1. AUTHORITY
# --------------------------------------------------------------------------
def test_authority_endpoint_permutation_keeps_multiset_and_counts():
    cg = operator_artifact_graph({"A": 3, "B": 2}, n_nodes=6, seed=0)
    G2, flow2 = endpoint_permutation(cg, seed=1)
    assert G2.number_of_edges() == cg.G.number_of_edges()
    assert G2.number_of_nodes() == cg.G.number_of_nodes()
    assert not any(u == v for u, v in G2.edges())            # no self-loops
    # operator-value multiset preserved (flow values are signature values)
    assert sorted(np.round(list(flow2.values()), 9)) == sorted(np.round(list(cg.flow.values()), 9))


def test_authority_emitter_holdout_collapses_on_load_bearing_family():
    """Hand example: family 'C' carries all the curl."""
    cg = _labelled_triangle_plus_bridge()
    full = hodge_decompose(cg.G, cg.flow).non_gradient_mass
    G_noC, f_noC = emitter_family_holdout(cg, "C")
    assert "C" not in set(
        cg.edge_operators[e] for e in (tuple(sorted(x)) for x in G_noC.edges())
    )
    # removing C leaves only the bridge (a tree) => zero non-gradient mass
    assert hodge_decompose(G_noC, f_noC).non_gradient_mass == pytest.approx(0.0, abs=1e-9)
    # removing B leaves the pure triangle curl
    G_noB, f_noB = emitter_family_holdout(cg, "B")
    assert hodge_decompose(G_noB, f_noB).non_gradient_mass == pytest.approx(1.0, abs=1e-9)
    assert 0.0 < full < 1.0


# --------------------------------------------------------------------------
# 2. PROPERTY
# --------------------------------------------------------------------------
@settings(max_examples=30, deadline=None)
@given(seed=st.integers(0, 10_000))
def test_property_endpoint_permutation_preserves_operator_value_multiset(seed):
    cg = operator_artifact_graph({"A": 4, "B": 3, "C": 2}, n_nodes=8, seed=seed)
    _, flow2 = endpoint_permutation(cg, seed=seed)
    assert sorted(np.round(list(flow2.values()), 9)) == sorted(np.round(list(cg.flow.values()), 9))


@settings(max_examples=30, deadline=None)
@given(seed=st.integers(0, 10_000))
def test_property_emitter_holdout_reduces_edge_count_by_family_size(seed):
    cg = operator_artifact_graph({"A": 4, "B": 3, "C": 3}, n_nodes=8, seed=seed)
    G2, _ = emitter_family_holdout(cg, "A")
    n_A = sum(1 for op in cg.edge_operators.values() if op == "A")
    assert G2.number_of_edges() == cg.G.number_of_edges() - n_A


# --------------------------------------------------------------------------
# 3. EDGE CASES
# --------------------------------------------------------------------------
def test_edge_cases():
    """Edges:
    - endpoint_permutation on a control with no edge_operators: ValueError
    - emitter_family_holdout of a family not present: ValueError
    - emitter_family_holdout that removes EVERY edge: ValueError
    """
    plain = ControlGraph(
        G=nx.Graph([(0, 1), (1, 2)]), flow={(0, 1): 1.0, (1, 2): 1.0},
        kind="plain", expected={}, seed=0, edge_operators=None, meta={},
    )
    with pytest.raises(ValueError):
        endpoint_permutation(plain, seed=0)

    cg = _labelled_triangle_plus_bridge()
    with pytest.raises(ValueError):
        emitter_family_holdout(cg, "Z")  # not present

    all_one = ControlGraph(
        G=nx.Graph([(0, 1), (1, 2), (0, 2)]),
        flow={(0, 1): 1.0, (1, 2): 1.0, (0, 2): -1.0},
        kind="manual", expected={}, seed=0,
        edge_operators={(0, 1): "C", (1, 2): "C", (0, 2): "C"}, meta={},
    )
    with pytest.raises(ValueError):
        emitter_family_holdout(all_one, "C")  # removes everything


# --------------------------------------------------------------------------
# 4. COMPOSITION
# --------------------------------------------------------------------------
def test_composition_operator_artifact_floor_under_endpoint_permutation():
    """Operator-artifact does not beat the endpoint-permutation null (floor)."""
    cg = operator_artifact_graph({"A": 5, "B": 4, "C": 4, "D": 3}, n_nodes=10, seed=1)
    res = run_null(cg, n_samples=200, seed=2, kind="endpoint_permutation")
    assert res.pvalue > 0.1


def test_composition_run_emitter_holdout_flags_load_bearing_family():
    """run_emitter_holdout reports per-family non_gradient_mass; the load-bearing
    family's removal collapses it while another family's removal does not."""
    cg = _labelled_triangle_plus_bridge()
    res = run_emitter_holdout(cg)
    assert res["_full"] > res["C"]                 # removing C drops the mass
    assert res["C"] == pytest.approx(0.0, abs=1e-9)
    assert res["B"] == pytest.approx(1.0, abs=1e-9)
