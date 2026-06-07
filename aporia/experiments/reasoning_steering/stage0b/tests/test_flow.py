"""TDD tests for the relational comparison-flow builder (Stage 0b, v0.3).

The keystone authority test: a Condorcet 3-cycle (non-transitive pairwise comparison)
MUST decompose to nonzero curl -- proving the relational flow CAN be non-conservative,
the entire point of the v0.3 correction. The contrast: a transitive comparison is a
pure gradient (non_gradient_mass ~ 0).
"""
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0b.flow import relational_flow


# 1. AUTHORITY
def test_authority_condorcet_cycle_has_nonzero_curl():
    """Classic Condorcet cycle over 3 states (A,B,C) and 3 falsifiers (f1,f2,f3):
        f1: A>B>C,  f2: B>C>A,  f3: C>A>B
    Pairwise majority gives A≻B, B≻C, C≻A — non-transitive. On the filled triangle
    this circulation is PURE CURL. Reference: Condorcet paradox / HodgeRank (Jiang
    et al. 2011).
    """
    A = {"f1": 3, "f2": 1, "f3": 2}
    B = {"f1": 2, "f2": 3, "f3": 1}
    C = {"f1": 1, "f2": 2, "f3": 3}
    G, flow = relational_flow([A, B, C])
    d = hodge_decompose(G, flow)
    assert d.curl_mass > 0.0           # the cycle shows up as curl
    assert d.non_gradient_mass > 0.5   # in fact it is dominated by curl
    assert d.harmonic_rank == 0        # a single filled triangle has no hole


def test_authority_transitive_is_gradient_dominated_below_condorcet():
    """All falsifiers agree A>B>C (transitive) => GRADIENT-DOMINATED, and strictly less
    non-gradient than a Condorcet cycle.

    NOTE (important): sign-aggregation is NOT path-additive (it saturates), so even a
    perfectly consistent ordering leaves a small SATURATION-CURL baseline
    (non_gradient_mass ~ 0.11 here, gradient ~ 0.89) -- it is NOT exactly 0. Therefore
    H-R1's verdict must be 'non_gradient_mass BEATS THE NULL', never 'non_gradient_mass
    > 0' (the null battery carries the same saturation baseline and subtracts it).
    """
    A = {"f1": 3, "f2": 3, "f3": 3}
    B = {"f1": 2, "f2": 2, "f3": 2}
    C = {"f1": 1, "f2": 1, "f3": 1}
    _, flow_t = relational_flow([A, B, C])
    d_t = hodge_decompose(nx.complete_graph(3), flow_t)
    assert d_t.gradient_mass > 0.5                       # gradient-dominated

    A2 = {"f1": 3, "f2": 1, "f3": 2}
    B2 = {"f1": 2, "f2": 3, "f3": 1}
    C2 = {"f1": 1, "f2": 2, "f3": 3}
    _, flow_c = relational_flow([A2, B2, C2])
    d_c = hodge_decompose(nx.complete_graph(3), flow_c)
    assert d_c.non_gradient_mass > d_t.non_gradient_mass  # Condorcet >> transitive


# 2. PROPERTY
@settings(max_examples=40, deadline=None)
@given(
    n=st.integers(min_value=2, max_value=8),
    seed=st.integers(0, 10_000),
)
def test_property_flow_is_bounded_integer_and_complete(n, seed):
    import random
    rng = random.Random(seed)
    fals = ["f1", "f2", "f3", "f4"]
    vectors = [{f: rng.randint(-3, 3) for f in fals} for _ in range(n)]
    G, flow = relational_flow(vectors)
    assert G.number_of_edges() == n * (n - 1) // 2          # complete graph
    for (i, j), val in flow.items():
        assert i < j
        assert abs(val) <= len(fals)                        # |sum of signs| <= #falsifiers
        assert val == int(val)


# 3. EDGE CASES
def test_edge_cases():
    """Edges: <2 states -> ValueError; states with no shared falsifiers -> 0 flow."""
    with pytest.raises(ValueError):
        relational_flow([{"f1": 1.0}])
    G, flow = relational_flow([{"f1": 1.0}, {"f2": 2.0}])   # disjoint falsifiers
    assert flow[(0, 1)] == 0.0


# 4. COMPOSITION — feeds the validated decomposer; masses partition.
def test_composition_decomposes_to_unit_mass():
    A = {"f1": 3, "f2": 1, "f3": 2}
    B = {"f1": 2, "f2": 3, "f3": 1}
    C = {"f1": 1, "f2": 2, "f3": 3}
    D = {"f1": 0, "f2": 0, "f3": 5}
    G, flow = relational_flow([A, B, C, D])
    d = hodge_decompose(G, flow)
    assert (d.gradient_mass + d.curl_mass + d.harmonic_mass) == pytest.approx(1.0, abs=1e-7)
