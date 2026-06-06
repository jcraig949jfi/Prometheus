"""TDD tests for the combinatorial Hodge decomposer (Stage 0 core).

The decomposer splits an edge-flow f on a graph into three orthogonal parts:

    f = grad(phi)  +  curl_adjoint(psi)  +  harmonic(h)

per combinatorial Hodge theory / HodgeRank
(Jiang, Lim, Yao, Ye, "Statistical ranking and combinatorial Hodge theory",
Math. Program. 127 (2011) 203-244). Triangles (3-cliques) are filled as 2-cells,
so closed flows around a filled triangle are CURL, while closed flows around an
unfilled longer cycle (a hole) are HARMONIC. That distinction is the whole point
of protocol v0.2 controls #6 (planted-cycle) vs #7 (planted-hole).

Four math-tdd categories: authority / property / edge / composition.
"""
import math
import numpy as np
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _canon(u, v):
    return (u, v) if u <= v else (v, u)


def _circulation(cycle):
    """Unit flow circulating around an ordered cycle [v0, v1, ..., v0-implied].

    Returns a flow dict in canonical edge orientation. Going v_i -> v_{i+1}
    contributes +1 if (v_i < v_{i+1}) else -1 (because canonical orientation is
    the sorted pair).
    """
    flow = {}
    n = len(cycle)
    for i in range(n):
        a, b = cycle[i], cycle[(i + 1) % n]
        e = _canon(a, b)
        flow[e] = 1.0 if (a, b) == e else -1.0
    return flow


# --------------------------------------------------------------------------
# 1. AUTHORITY
# --------------------------------------------------------------------------
def test_authority_triangle_circulation_is_pure_curl():
    """A unit circulation on a filled triangle is PURE CURL.

    Hand computation (orientation = sorted pairs, edges [(0,1),(0,2),(1,2)]):
    circulating 0->1->2->0 gives f = [f(0,1), f(0,2), f(1,2)] = [+1, -1, +1].
    The triangle 2-cell {0,1,2} has boundary d2 = (1,2) - (0,2) + (0,1) = [+1,-1,+1],
    so im(curl_adjoint) = span([1,-1,1]) contains f exactly => grad=0, harmonic=0.
    Reference: HodgeRank (Jiang et al. 2011), Sec. 3 (the curl space im(delta_1)).
    """
    G = nx.complete_graph(3)  # 3-clique => triangle is filled
    f = _circulation([0, 1, 2])
    d = hodge_decompose(G, f)
    assert d.curl_mass == pytest.approx(1.0, abs=1e-9)
    assert d.gradient_mass == pytest.approx(0.0, abs=1e-9)
    assert d.harmonic_mass == pytest.approx(0.0, abs=1e-9)
    assert d.curl_rank == 1
    assert d.harmonic_rank == 0


def test_authority_square_circulation_is_pure_harmonic():
    """A unit circulation on a chordless 4-cycle is PURE HARMONIC.

    The 4-cycle 0-1-2-3-0 has NO 3-cliques, so no triangle is filled and the
    curl operator is zero. The circulating flow is not a gradient (its integral
    around the loop is 4 != 0), so it lands entirely in the harmonic subspace.
    First Betti number of a single 4-cycle = |E|-|V|+c = 4-4+1 = 1.
    Reference: HodgeRank (Jiang et al. 2011); harmonic = ker(L1), dim = b1.
    """
    G = nx.cycle_graph(4)
    f = _circulation([0, 1, 2, 3])
    d = hodge_decompose(G, f)
    assert d.harmonic_mass == pytest.approx(1.0, abs=1e-9)
    assert d.curl_mass == pytest.approx(0.0, abs=1e-9)
    assert d.gradient_mass == pytest.approx(0.0, abs=1e-9)
    assert d.curl_rank == 0
    assert d.harmonic_rank == 1


def test_authority_path_flow_is_pure_gradient():
    """Any flow on a tree (path) is PURE GRADIENT: no cycles => no curl/harmonic.

    Reference: a tree has cycle space dimension 0 (|E|-|V|+1 = 0), so the edge
    space equals im(grad). HodgeRank (Jiang et al. 2011), Sec. 2.
    """
    G = nx.path_graph(4)  # edges (0,1),(1,2),(2,3); a tree
    f = {(0, 1): 2.0, (1, 2): -3.0, (2, 3): 5.0}
    d = hodge_decompose(G, f)
    assert d.gradient_mass == pytest.approx(1.0, abs=1e-9)
    assert d.non_gradient_mass == pytest.approx(0.0, abs=1e-9)
    assert d.harmonic_rank == 0
    assert d.curl_rank == 0


# --------------------------------------------------------------------------
# 2. PROPERTY (Hypothesis)
# --------------------------------------------------------------------------
@settings(max_examples=60, deadline=None)
@given(
    n=st.integers(min_value=2, max_value=9),
    p=st.floats(min_value=0.2, max_value=1.0),
    seed=st.integers(min_value=0, max_value=10_000),
)
def test_property_pythagorean_and_orthogonality(n, p, seed):
    """Masses are a partition of unity and the three parts are orthogonal.

    ||f||^2 = ||grad||^2 + ||curl||^2 + ||h||^2  (Pythagoras), so the three
    masses are non-negative and sum to 1; and the components are pairwise
    orthogonal (im grad _|_ im curl_adjoint _|_ harmonic), the defining property
    of the Hodge decomposition.
    """
    G = nx.gnp_random_graph(n, p, seed=seed)
    if G.number_of_edges() == 0:
        return
    rng = np.random.default_rng(seed)
    f = {_canon(u, v): float(rng.standard_normal()) for u, v in G.edges()}
    if all(v == 0.0 for v in f.values()):
        return
    d = hodge_decompose(G, f)
    for m in (d.gradient_mass, d.curl_mass, d.harmonic_mass):
        assert m >= -1e-9
    assert (d.gradient_mass + d.curl_mass + d.harmonic_mass) == pytest.approx(1.0, abs=1e-7)
    assert d.non_gradient_mass == pytest.approx(d.curl_mass + d.harmonic_mass, abs=1e-9)
    # pairwise orthogonality of the raw component vectors
    g, c, h = d.gradient, d.curl, d.harmonic
    assert float(g @ c) == pytest.approx(0.0, abs=1e-6)
    assert float(g @ h) == pytest.approx(0.0, abs=1e-6)
    assert float(c @ h) == pytest.approx(0.0, abs=1e-6)


@settings(max_examples=40, deadline=None)
@given(
    n=st.integers(min_value=2, max_value=9),
    p=st.floats(min_value=0.2, max_value=1.0),
    seed=st.integers(min_value=0, max_value=10_000),
)
def test_property_gradient_of_potential_has_zero_non_gradient_mass(n, p, seed):
    """A flow constructed AS a gradient (f = grad(phi)) is pure gradient."""
    G = nx.gnp_random_graph(n, p, seed=seed)
    if G.number_of_edges() == 0:
        return
    rng = np.random.default_rng(seed + 1)
    phi = {v: float(rng.standard_normal()) for v in G.nodes()}
    f = {_canon(u, v): phi[max(u, v)] - phi[min(u, v)] for u, v in G.edges()}
    if all(v == 0.0 for v in f.values()):
        return
    d = hodge_decompose(G, f)
    assert d.gradient_mass == pytest.approx(1.0, abs=1e-6)
    assert d.non_gradient_mass == pytest.approx(0.0, abs=1e-6)


# --------------------------------------------------------------------------
# 3. EDGE CASES
# --------------------------------------------------------------------------
def test_edge_cases():
    """Documented edges:
    - empty graph (no edges): ValueError (nothing to decompose)
    - single isolated node, no edges: ValueError
    - single edge: pure gradient (no cycle possible), curl_rank=harmonic_rank=0
    - self-loop: ValueError (1-cells must be between distinct vertices)
    - flow missing an edge value: ValueError
    """
    with pytest.raises(ValueError):
        hodge_decompose(nx.empty_graph(0), {})
    with pytest.raises(ValueError):
        hodge_decompose(nx.empty_graph(1), {})

    G1 = nx.Graph([(0, 1)])
    d = hodge_decompose(G1, {(0, 1): 7.0})
    assert d.gradient_mass == pytest.approx(1.0, abs=1e-9)
    assert d.curl_rank == 0 and d.harmonic_rank == 0

    Gloop = nx.Graph()
    Gloop.add_edge(0, 0)
    with pytest.raises(ValueError):
        hodge_decompose(Gloop, {(0, 0): 1.0})

    G2 = nx.path_graph(3)
    with pytest.raises(ValueError):
        hodge_decompose(G2, {(0, 1): 1.0})  # missing (1,2)


def test_edge_disconnected_graph():
    """Disconnected graph: decomposition still valid; b1 counts per-component."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (0, 2)])        # filled triangle, component A
    G.add_edges_from([(3, 4), (4, 5), (5, 6), (3, 6)])  # chordless 4-cycle, comp B
    f = {}
    f.update(_circulation([0, 1, 2]))
    f.update(_circulation([3, 4, 5, 6]))
    d = hodge_decompose(G, f)
    assert d.curl_rank == 1       # one filled triangle
    assert d.harmonic_rank == 1   # one hole (the 4-cycle)


# --------------------------------------------------------------------------
# 4. COMPOSITION (cross-check against networkx, an independent tool)
# --------------------------------------------------------------------------
@settings(max_examples=40, deadline=None)
@given(
    n=st.integers(min_value=2, max_value=9),
    p=st.floats(min_value=0.2, max_value=1.0),
    seed=st.integers(min_value=0, max_value=10_000),
)
def test_composition_rank_identity_vs_networkx(n, p, seed):
    """curl_rank + harmonic_rank == graph cycle rank (|E|-|V|+components).

    Independent reference: networkx number_connected_components and basic counts.
    This pins the rank bookkeeping: the non-gradient subspace dimension equals the
    cycle space dimension, split by whether each cycle is triangle-filled (curl)
    or a hole (harmonic).
    """
    G = nx.gnp_random_graph(n, p, seed=seed)
    if G.number_of_edges() == 0:
        return
    rng = np.random.default_rng(seed)
    f = {_canon(u, v): float(rng.standard_normal()) for u, v in G.edges()}
    d = hodge_decompose(G, f)
    cycle_rank = (
        G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)
    )
    assert d.curl_rank + d.harmonic_rank == cycle_rank


def test_composition_triangle_free_harmonic_rank_equals_cycle_basis():
    """On a triangle-free graph, curl_rank=0 so harmonic_rank == len(cycle_basis).

    Cross-check against networkx.cycle_basis on the 4x4 grid (triangle-free).
    """
    G = nx.grid_2d_graph(4, 4)
    G = nx.convert_node_labels_to_integers(G)
    rng = np.random.default_rng(0)
    f = {_canon(u, v): float(rng.standard_normal()) for u, v in G.edges()}
    d = hodge_decompose(G, f)
    assert d.curl_rank == 0
    assert d.harmonic_rank == len(nx.cycle_basis(G))
