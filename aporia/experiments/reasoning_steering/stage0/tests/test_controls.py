"""TDD tests for synthetic control generators (Stage 0, protocol v0.2 §4 #5-#8).

Controls are (graph, flow) pairs with KNOWN Hodge structure, used to calibrate the
decomposer before it touches real data (protocol §5 step 0a):

  #5 no-cycle/no-void  -> decomposer must read non_gradient_mass ~ 0  (sees nothing)
  #6 planted-cycle     -> decomposer must read curl_mass > 0, curl_rank = #triangles
  #7 planted-hole      -> harmonic_rank = #holes                     (iter 3)
  #8 operator-artifact -> false-positive floor                       (iter 3)

Each generator declares its `expected` Hodge structure; the COMPOSITION tests below
verify the decomposer recovers exactly that (planted == recovered). Independent
anchors (networkx is_tree / triangle count / Betti) guard against circularity with
the decomposer being calibrated.
"""
import numpy as np
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.controls import (
    no_cycle_graph,
    planted_cycle_graph,
)


# --------------------------------------------------------------------------
# 1. AUTHORITY — specific configs with structure verified independently of the
#    decomposer (networkx), then confirmed through it.
# --------------------------------------------------------------------------
def test_authority_no_cycle_is_a_tree_with_zero_non_gradient_mass():
    """no_cycle_graph(8, seed=0) is a TREE (independent: nx.is_tree) and the
    decomposer reads non_gradient_mass ~ 0 (a tree has empty cycle space).
    Reference: tree cycle-space dimension |E|-|V|+1 = 0.
    """
    cg = no_cycle_graph(8, seed=0)
    assert nx.is_tree(cg.G)                       # independent structural anchor
    assert cg.G.number_of_nodes() == 8
    d = hodge_decompose(cg.G, cg.flow)
    assert d.non_gradient_mass == pytest.approx(0.0, abs=1e-9)
    assert d.curl_rank == 0 and d.harmonic_rank == 0


def test_authority_planted_cycle_three_triangles():
    """planted_cycle_graph(3, seed=0): exactly 3 filled triangles, no holes.
    Independent anchor: networkx counts 3 three-cliques. The decomposer must read
    curl_rank == 3, harmonic_rank == 0, curl_mass > 0.
    """
    cg = planted_cycle_graph(3, seed=0)
    n_triangles = sum(1 for c in nx.enumerate_all_cliques(cg.G) if len(c) == 3)
    assert n_triangles == 3                       # independent anchor
    d = hodge_decompose(cg.G, cg.flow)
    assert d.curl_rank == 3
    assert d.harmonic_rank == 0
    assert d.curl_mass > 0.0


# --------------------------------------------------------------------------
# 2. PROPERTY — hold across seeds / sizes.
# --------------------------------------------------------------------------
@settings(max_examples=40, deadline=None)
@given(n=st.integers(min_value=2, max_value=20), seed=st.integers(0, 10_000))
def test_property_no_cycle_always_zero_non_gradient(n, seed):
    cg = no_cycle_graph(n, seed=seed)
    assert nx.is_forest(cg.G)
    d = hodge_decompose(cg.G, cg.flow)
    assert d.non_gradient_mass == pytest.approx(0.0, abs=1e-9)


@settings(max_examples=40, deadline=None)
@given(k=st.integers(min_value=1, max_value=6), seed=st.integers(0, 10_000))
def test_property_planted_cycle_curl_rank_equals_triangles(k, seed):
    cg = planted_cycle_graph(k, seed=seed)
    d = hodge_decompose(cg.G, cg.flow)
    assert d.curl_rank == k
    assert d.harmonic_rank == 0
    assert d.curl_mass > 0.0


# --------------------------------------------------------------------------
# 3. EDGE CASES
# --------------------------------------------------------------------------
def test_edge_cases():
    """Generator edges:
    - no_cycle_graph(n<2): ValueError (a tree needs >=1 edge)
    - planted_cycle_graph(0): ValueError (nothing to plant)
    - planted_cycle_graph(-1): ValueError
    """
    with pytest.raises(ValueError):
        no_cycle_graph(1, seed=0)
    with pytest.raises(ValueError):
        planted_cycle_graph(0, seed=0)
    with pytest.raises(ValueError):
        planted_cycle_graph(-1, seed=0)


# --------------------------------------------------------------------------
# 4. COMPOSITION — control declares `expected`; decomposer must recover it.
#    This IS protocol step 0a: the instrument sees nothing in no-structure data
#    and recovers planted structure where it exists.
# --------------------------------------------------------------------------
@settings(max_examples=30, deadline=None)
@given(k=st.integers(min_value=1, max_value=6), seed=st.integers(0, 10_000))
def test_composition_planted_cycle_recovered_matches_declared(k, seed):
    cg = planted_cycle_graph(k, seed=seed)
    d = hodge_decompose(cg.G, cg.flow)
    assert d.curl_rank == cg.expected["curl_rank"]
    assert d.harmonic_rank == cg.expected["harmonic_rank"]
    assert (d.non_gradient_mass > 0.0) == (cg.expected["non_gradient_mass"] == "positive")


def test_composition_no_cycle_recovered_matches_declared():
    cg = no_cycle_graph(10, seed=3)
    d = hodge_decompose(cg.G, cg.flow)
    assert d.curl_rank == cg.expected["curl_rank"] == 0
    assert d.harmonic_rank == cg.expected["harmonic_rank"] == 0
    assert cg.expected["non_gradient_mass"] == "zero"
    assert d.non_gradient_mass == pytest.approx(0.0, abs=1e-9)
