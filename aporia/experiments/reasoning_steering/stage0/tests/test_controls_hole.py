"""TDD tests for control #7 planted-hole (Stage 0, protocol v0.2 §4 #7).

A planted hole is a CHORDLESS cycle of length >= 4 (no triangle fill), so a
circulation around it is PURE HARMONIC: harmonic_rank == #holes, curl_rank == 0.
This is the harmonic counterpart to control #6 (planted-cycle = pure curl), and the
distinction is exactly what protocol v0.2 §2 hangs on (curl = local path-dependence;
harmonic = a hole / global obstruction). Independent anchor: triangle-free graphs
have curl_rank 0 and harmonic_rank == len(networkx.cycle_basis).
"""
import numpy as np
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.controls import planted_hole_graph


# 1. AUTHORITY
def test_authority_planted_hole_two_chordless_squares():
    """planted_hole_graph(2, hole_len=4, seed=0): two chordless 4-cycles, no fill.
    Independent anchors: zero 3-cliques (=> curl_rank 0) and first Betti number 2.
    Decomposer must read harmonic_rank == 2, curl_rank == 0, harmonic_mass > 0.
    """
    cg = planted_hole_graph(2, hole_len=4, seed=0)
    n_triangles = sum(1 for c in nx.enumerate_all_cliques(cg.G) if len(c) == 3)
    assert n_triangles == 0
    betti1 = cg.G.number_of_edges() - cg.G.number_of_nodes() + nx.number_connected_components(cg.G)
    assert betti1 == 2
    d = hodge_decompose(cg.G, cg.flow)
    assert d.harmonic_rank == 2
    assert d.curl_rank == 0
    assert d.harmonic_mass > 0.0


# 2. PROPERTY
@settings(max_examples=40, deadline=None)
@given(
    k=st.integers(min_value=1, max_value=5),
    hole_len=st.integers(min_value=4, max_value=7),
    seed=st.integers(0, 10_000),
)
def test_property_planted_hole_harmonic_rank_equals_holes(k, hole_len, seed):
    cg = planted_hole_graph(k, hole_len=hole_len, seed=seed)
    d = hodge_decompose(cg.G, cg.flow)
    assert d.curl_rank == 0
    assert d.harmonic_rank == k
    assert d.harmonic_mass > 0.0


# 3. EDGE CASES
def test_edge_cases():
    """Edges:
    - n_holes=0: ValueError (nothing to plant)
    - hole_len=3: ValueError (a 3-cycle is a triangle = curl, not a hole)
    - hole_len<3: ValueError
    """
    with pytest.raises(ValueError):
        planted_hole_graph(0, hole_len=4, seed=0)
    with pytest.raises(ValueError):
        planted_hole_graph(2, hole_len=3, seed=0)
    with pytest.raises(ValueError):
        planted_hole_graph(2, hole_len=2, seed=0)


# 4. COMPOSITION (cross-check vs networkx cycle_basis; recovered == declared)
@settings(max_examples=30, deadline=None)
@given(k=st.integers(min_value=1, max_value=5), seed=st.integers(0, 10_000))
def test_composition_harmonic_rank_matches_cycle_basis(k, seed):
    cg = planted_hole_graph(k, hole_len=4, seed=seed)
    d = hodge_decompose(cg.G, cg.flow)
    assert d.curl_rank == 0
    assert d.harmonic_rank == len(nx.cycle_basis(cg.G))   # triangle-free => equal
    assert d.harmonic_rank == cg.expected["harmonic_rank"] == k
    assert cg.expected["non_gradient_mass"] == "positive"
