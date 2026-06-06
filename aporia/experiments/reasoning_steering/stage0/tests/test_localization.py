"""TDD tests for H-R2 localization with the v0.2 LOCALIZATION FREEZE (Stage 0).

Per-well local rank is computed on fixed graph-distance balls B_r(w), r in {1,2,3}.
curl_rank and harmonic_rank are estimated SEPARATELY at each radius. A nonzero rank
is declarable only if the SAME value appears at two adjacent radii (with non-gradient
mass above floor at both); a nonzero rank that appears at only one radius is
UNSTABLE_LOCALIZATION and cannot support H-R2.

The freeze does real work here: a chordless 4-cycle's hole closes inside the r=2 ball
and persists at r=3 (stable harmonic 1), but a 6-cycle's hole only closes at r=3 --
a single radius -- so it is correctly rejected as UNSTABLE_LOCALIZATION even though
the GLOBAL decomposition sees harmonic_rank 1. Localization is stricter than global,
on purpose.
"""
import networkx as nx
import pytest
from hypothesis import given, settings, strategies as st

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.controls import (
    planted_cycle_graph,
    planted_hole_graph,
)
from aporia.experiments.reasoning_steering.stage0.localization import (
    ball_nodes,
    localized_rank,
    LocalRank,
)


# 1. AUTHORITY
def test_authority_triangle_well_stable_curl_rank_1():
    """A well on an isolated filled triangle: curl_rank 1 at every radius => STABLE."""
    cg = planted_cycle_graph(1, seed=0)            # single triangle 0,1,2
    lr = localized_rank(cg.G, cg.flow, well=0)
    assert lr.curl_rank == 1
    assert lr.harmonic_rank == 0
    assert lr.status == "STABLE"


def test_authority_four_cycle_well_stable_harmonic_rank_1():
    """A well on a chordless 4-cycle: hole appears at radii {2,3} => STABLE harmonic 1."""
    cg = planted_hole_graph(1, hole_len=4, seed=0)
    lr = localized_rank(cg.G, cg.flow, well=0)
    assert lr.harmonic_rank == 1
    assert lr.curl_rank == 0
    assert lr.status == "STABLE"
    # hole is absent at r=1, present at r=2 and r=3
    assert lr.harmonic_rank_by_r[1] == 0
    assert lr.harmonic_rank_by_r[2] == 1
    assert lr.harmonic_rank_by_r[3] == 1


def test_authority_six_cycle_well_is_unstable_localization():
    """A well on a 6-cycle: hole only closes at r=3 (single radius) => rejected."""
    cg = planted_hole_graph(1, hole_len=6, seed=0)
    lr = localized_rank(cg.G, cg.flow, well=0)
    assert lr.harmonic_rank_by_r[1] == 0
    assert lr.harmonic_rank_by_r[2] == 0
    assert lr.harmonic_rank_by_r[3] == 1            # appears at only one radius
    assert lr.harmonic_rank is None                 # cannot be declared
    assert lr.status == "UNSTABLE_LOCALIZATION"


# 2. PROPERTY
@settings(max_examples=30, deadline=None)
@given(seed=st.integers(0, 10_000))
def test_property_radii_keys_and_triangle_curl_stable(seed):
    cg = planted_cycle_graph(1, seed=seed)
    lr = localized_rank(cg.G, cg.flow, well=0)
    assert set(lr.curl_rank_by_r) == {1, 2, 3}
    assert set(lr.harmonic_rank_by_r) == {1, 2, 3}
    assert set(lr.non_gradient_mass_by_r) == {1, 2, 3}
    assert lr.curl_rank == 1 and lr.status == "STABLE"


# 3. EDGE CASES
def test_edge_cases():
    """Edges:
    - well not in graph: ValueError
    - isolated well (degree 0): all balls empty => curl/harmonic 0, STABLE (no crash)
    - non-increasing/zero radii: ValueError
    """
    cg = planted_cycle_graph(1, seed=0)
    with pytest.raises(ValueError):
        localized_rank(cg.G, cg.flow, well=999)
    with pytest.raises(ValueError):
        localized_rank(cg.G, cg.flow, well=0, radii=(2, 1, 3))
    with pytest.raises(ValueError):
        localized_rank(cg.G, cg.flow, well=0, radii=(0, 1, 2))

    G = nx.Graph()
    G.add_node(42)                                  # isolated well
    G.add_edges_from([(0, 1), (1, 2), (0, 2)])
    flow = {(0, 1): 1.0, (1, 2): 1.0, (0, 2): -1.0}
    lr = localized_rank(G, flow, well=42)
    assert lr.curl_rank == 0 and lr.harmonic_rank == 0
    assert lr.status == "STABLE"


# 4. COMPOSITION — localization is stricter than global (the freeze doing work)
def test_composition_ball_nodes_match_networkx_ego():
    cg = planted_hole_graph(1, hole_len=6, seed=0)
    for r in (1, 2, 3):
        assert ball_nodes(cg.G, 0, r) == set(nx.ego_graph(cg.G, 0, radius=r).nodes())


def test_composition_localization_rejects_what_global_accepts():
    """Global decomposition accepts the 6-cycle hole (harmonic_rank 1); localized at
    a single well it is UNSTABLE_LOCALIZATION. Localization is the stricter gate."""
    cg = planted_hole_graph(1, hole_len=6, seed=0)
    assert hodge_decompose(cg.G, cg.flow).harmonic_rank == 1   # global accepts
    lr = localized_rank(cg.G, cg.flow, well=0)
    assert isinstance(lr, LocalRank)
    assert lr.status == "UNSTABLE_LOCALIZATION"                # local rejects
