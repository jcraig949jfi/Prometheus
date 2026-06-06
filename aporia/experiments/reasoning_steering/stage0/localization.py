"""H-R2 localization with the LOCALIZATION FREEZE (Stage 0, protocol v0.2).

Per-well local rank on FIXED graph-distance balls B_r(w), r in {1,2,3}. No radius is
selected post hoc; all three are reported. curl_rank and harmonic_rank are estimated
SEPARATELY at each radius (they mean different things: curl = local path-dependence,
harmonic = a hole). A nonzero rank is declarable only if the same value appears at
two adjacent radii with non-gradient mass above floor at both; a nonzero rank that
appears at only one radius is UNSTABLE_LOCALIZATION and cannot support H-R2.

Spectral localization is deliberately rejected for v0.2 (it adds eigenvalue-cutoff /
bandwidth / diffusion-time knobs -- exactly where artifacts hide).
"""
from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose

__all__ = ["LocalRank", "ball_nodes", "local_decompose", "localized_rank"]


@dataclass(frozen=True)
class LocalRank:
    well: object
    radii: tuple
    curl_rank_by_r: dict
    harmonic_rank_by_r: dict
    non_gradient_mass_by_r: dict
    curl_rank: int | None        # declared stable value, or None if unstable
    harmonic_rank: int | None
    status: str                  # "STABLE" or "UNSTABLE_LOCALIZATION"


def _canon(u, v):
    return (u, v) if u <= v else (v, u)


def ball_nodes(G: nx.Graph, well, r: int) -> set:
    """Nodes within graph distance r of ``well`` (inclusive)."""
    return set(nx.single_source_shortest_path_length(G, well, cutoff=r).keys())


def local_decompose(G: nx.Graph, flow: dict, well, r: int):
    """Local Hodge ranks on the induced subgraph B_r(w).

    Returns (curl_rank, harmonic_rank, non_gradient_mass); (0, 0, 0.0) if the ball
    has no internal edges.
    """
    sub = nx.ego_graph(G, well, radius=r)
    if sub.number_of_edges() == 0:
        return 0, 0, 0.0
    subflow = {_canon(u, v): flow[_canon(u, v)] for u, v in sub.edges()}
    # a sub-ball whose restricted flow is exactly zero has no decomposition
    if all(val == 0.0 for val in subflow.values()):
        return 0, 0, 0.0
    d = hodge_decompose(sub, subflow)
    return d.curl_rank, d.harmonic_rank, d.non_gradient_mass


def _declare(ranks_by_r: dict, radii: tuple, mass_by_r: dict, mass_floor: float):
    """Two-adjacent-radii rule. Returns (declared_value, 'stable'|'unstable')."""
    pairs = [(radii[i], radii[i + 1]) for i in range(len(radii) - 1)]
    for a, b in pairs:
        if ranks_by_r[a] == ranks_by_r[b] and ranks_by_r[a] > 0:
            if mass_by_r[a] > mass_floor and mass_by_r[b] > mass_floor:
                return ranks_by_r[a], "stable"
    if all(ranks_by_r[r] == 0 for r in radii):
        return 0, "stable"
    return None, "unstable"          # a nonzero rank with no adjacent agreement


def localized_rank(
    G: nx.Graph, flow: dict, well, radii: tuple = (1, 2, 3), mass_floor: float = 1e-9
) -> LocalRank:
    if well not in G:
        raise ValueError(f"well {well!r} is not a node of the graph")
    if any(r <= 0 for r in radii) or list(radii) != sorted(radii) or len(set(radii)) != len(radii):
        raise ValueError(f"radii must be strictly increasing positive ints, got {radii}")

    curl_by_r, harm_by_r, mass_by_r = {}, {}, {}
    for r in radii:
        cr, hr, m = local_decompose(G, flow, well, r)
        curl_by_r[r], harm_by_r[r], mass_by_r[r] = cr, hr, m

    curl_val, curl_status = _declare(curl_by_r, radii, mass_by_r, mass_floor)
    harm_val, harm_status = _declare(harm_by_r, radii, mass_by_r, mass_floor)
    status = "STABLE" if (curl_status == "stable" and harm_status == "stable") else "UNSTABLE_LOCALIZATION"

    return LocalRank(
        well=well,
        radii=tuple(radii),
        curl_rank_by_r=curl_by_r,
        harmonic_rank_by_r=harm_by_r,
        non_gradient_mass_by_r=mass_by_r,
        curl_rank=curl_val,
        harmonic_rank=harm_val,
        status=status,
    )
