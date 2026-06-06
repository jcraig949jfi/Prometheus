"""§4 null battery (Stage 0, protocol v0.2).

Decides whether an observed non_gradient_mass exceeds what null procedures produce.
The point is the operator-vs-state-curl distinction: if the observed non-gradient
structure dies under these nulls, the operator menu (or chance topology) manufactured
it; if it survives, the state landscape carries it.

Nulls implemented here:
  - degree_preserving_rewire : randomise topology keeping the degree sequence, then
    reassign the flow-value multiset (does the flow's alignment with THIS topology
    matter beyond chance?).
  - operator_label_shuffle   : keep the graph, permute operator labels across edges
    and rebuild flow from the per-operator signature (does structure survive when
    operators are reassigned?).

p-value is the smoothed Monte-Carlo permutation value (Davison & Hinkley 1997):
    p = (#{null >= observed} + 1) / (n_samples + 1)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import networkx as nx

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose

__all__ = [
    "NullResult",
    "null_pvalue",
    "degree_preserving_rewire",
    "operator_label_shuffle",
    "run_null",
]


@dataclass(frozen=True)
class NullResult:
    observed: float
    null_masses: list
    pvalue: float
    null_mean: float
    null_std: float
    kind: str


def _canon(u, v):
    return (u, v) if u <= v else (v, u)


def null_pvalue(observed: float, null_masses) -> float:
    """Smoothed right-tailed permutation p-value."""
    arr = np.asarray(list(null_masses), dtype=float)
    if arr.size == 0:
        raise ValueError("null_masses is empty")
    return float((arr >= observed).sum() + 1) / (arr.size + 1)


def degree_preserving_rewire(G: nx.Graph, seed: int, n_swaps: int | None = None) -> nx.Graph:
    """Degree-preserving double-edge-swap rewiring; returns a fresh graph.

    Falls back to a copy of G if the graph has too few edges to swap.
    """
    H = G.copy()
    if H.number_of_edges() < 2:
        return H
    swaps = n_swaps if n_swaps is not None else 10 * H.number_of_edges()
    try:
        nx.double_edge_swap(H, nswap=swaps, max_tries=swaps * 20, seed=seed)
    except nx.NetworkXError:
        pass  # could not satisfy the swap target; partial/!no rewiring is acceptable
    return H


def _reassign_flow_multiset(G_new: nx.Graph, flow_values, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    edges = sorted(_canon(u, v) for u, v in G_new.edges())
    vals = list(flow_values)
    rng.shuffle(vals)
    return {e: vals[i] for i, e in enumerate(edges)}


def operator_label_shuffle(cg, seed: int) -> dict:
    """Permute operator labels across edges, rebuild flow from the signature."""
    if not cg.edge_operators:
        raise ValueError("control has no edge_operators to shuffle")
    signature = cg.meta["signature"]
    rng = np.random.default_rng(seed)
    edges = sorted(cg.edge_operators.keys())
    ops = [cg.edge_operators[e] for e in edges]
    rng.shuffle(ops)
    return {e: signature[ops[i]] for i, e in enumerate(edges)}


def run_null(cg, n_samples: int, seed: int, kind: str = "degree_preserving_rewire") -> NullResult:
    """Build a null distribution of non_gradient_mass and compare the observed value."""
    if n_samples < 1:
        raise ValueError("n_samples must be >= 1")
    observed = hodge_decompose(cg.G, cg.flow).non_gradient_mass
    flow_values = list(cg.flow.values())
    rng = np.random.default_rng(seed)
    masses = []
    for _ in range(n_samples):
        ss = int(rng.integers(0, 2**31 - 1))
        if kind == "degree_preserving_rewire":
            H = degree_preserving_rewire(cg.G, seed=ss)
            f = _reassign_flow_multiset(H, flow_values, seed=ss)
            masses.append(hodge_decompose(H, f).non_gradient_mass)
        elif kind == "operator_label_shuffle":
            f = operator_label_shuffle(cg, seed=ss)
            masses.append(hodge_decompose(cg.G, f).non_gradient_mass)
        else:
            raise ValueError(f"unknown null kind {kind!r}")
    return NullResult(
        observed=observed,
        null_masses=masses,
        pvalue=null_pvalue(observed, masses),
        null_mean=float(np.mean(masses)),
        null_std=float(np.std(masses)),
        kind=kind,
    )
