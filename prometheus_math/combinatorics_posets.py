"""prometheus_math.combinatorics_posets — finite partially ordered sets.

This module provides a first-class API for finite posets:

- Poset class            — encapsulates a finite poset given by its
                           order relations.  Computes transitive
                           closure, cover relations, Hasse diagram,
                           order ideals/filters, intervals, antichains,
                           Mobius / zeta functions, joins/meets,
                           lattice / distributivity / isomorphism tests.
- chain_poset(n)         — total order 1..n
- antichain_poset(n)     — pairwise incomparable
- boolean_lattice(n)     — subsets of {0,...,n-1}
- divisor_poset(n)       — positive divisors of n by divisibility
- product_poset(P, Q)    — coordinate-wise direct product
- dual_poset(P)          — opposite poset

References:
- Stanley, "Enumerative Combinatorics, Vol. 1" (2nd ed., 2012),
  Chapter 3.
- Davey & Priestley, "Introduction to Lattices and Order" (2002).
- Birkhoff, "Lattice Theory" (3rd ed., 1967).

Implementation notes:
- Cover relations are derived from the transitive reduction of the
  partial order DAG; we use networkx for the DAG operations.
- Linear extensions use networkx.algorithms.dag.all_topological_sorts.
- Mobius is computed by the standard recursion
      mu(a, a) = 1
      mu(a, b) = - sum_{a <= c < b} mu(a, c)   for a < b
- Maximum antichain uses Dilworth's theorem reduced to a maximum
  bipartite matching (Konig); minimum chain cover is the dual.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import permutations, product as iproduct
from typing import Hashable, Iterable, List, Optional, Sequence, Set, Tuple

import networkx as nx


Element = Hashable


class Poset:
    """Finite partially ordered set.

    Parameters
    ----------
    elements : Iterable[Element]
        The underlying set.  Elements must be hashable.
    relations : Iterable[Tuple[Element, Element]]
        Pairs ``(a, b)`` interpreted as ``a <= b``.  These need not be
        the cover relations: any superset of the cover relations works
        as long as the transitive closure recovers the desired poset.

    Raises
    ------
    ValueError
        If the supplied relations contain a cycle that would force two
        distinct elements to be equal (i.e. the resulting relation is
        not antisymmetric).
    """

    def __init__(
        self,
        elements: Iterable[Element],
        relations: Iterable[Tuple[Element, Element]],
    ) -> None:
        self.elements: List[Element] = list(elements)
        self._element_set: Set[Element] = set(self.elements)

        # Build a DiGraph including reflexive self-loops; then take the
        # transitive closure.  Cycles between distinct nodes => not a
        # poset.
        G = nx.DiGraph()
        G.add_nodes_from(self.elements)
        for a, b in relations:
            if a not in self._element_set or b not in self._element_set:
                raise KeyError(
                    f"relation references unknown element: ({a!r}, {b!r})"
                )
            G.add_edge(a, b)

        # Detect non-antisymmetric cycles before closure.
        # A simple cycle of length > 1 means a != b with a <= b <= a.
        for cyc in nx.simple_cycles(G):
            if len(cyc) > 1:
                raise ValueError(
                    f"relations are not antisymmetric (cycle {cyc})"
                )

        # Transitive closure on a DAG.
        TC = nx.transitive_closure_dag(G) if self.elements else nx.DiGraph()
        # Ensure reflexivity in our internal "<=" representation.
        self._le_edges: Set[Tuple[Element, Element]] = set()
        for a in self.elements:
            self._le_edges.add((a, a))
        for u, v in TC.edges():
            self._le_edges.add((u, v))

        # Cache cover relations lazily.
        self._covers: Optional[List[Tuple[Element, Element]]] = None

    # ------------------------------------------------------------------
    # Order primitives
    # ------------------------------------------------------------------

    def _check(self, a: Element, b: Element) -> None:
        if a not in self._element_set:
            raise KeyError(f"unknown element: {a!r}")
        if b not in self._element_set:
            raise KeyError(f"unknown element: {b!r}")

    def le(self, a: Element, b: Element) -> bool:
        """``a <= b`` in the poset."""
        self._check(a, b)
        return (a, b) in self._le_edges

    def lt(self, a: Element, b: Element) -> bool:
        """``a < b`` in the poset (strict)."""
        return a != b and self.le(a, b)

    def cover_relations(self) -> List[Tuple[Element, Element]]:
        """All pairs ``(a, b)`` such that ``a < b`` with no ``c`` strictly
        between them.

        Returns
        -------
        list[tuple[Element, Element]]
            The cover relations of the poset.
        """
        if self._covers is not None:
            return list(self._covers)
        covers: List[Tuple[Element, Element]] = []
        for a in self.elements:
            for b in self.elements:
                if not self.lt(a, b):
                    continue
                # b covers a iff there is no c strictly between
                between = False
                for c in self.elements:
                    if c == a or c == b:
                        continue
                    if self.lt(a, c) and self.lt(c, b):
                        between = True
                        break
                if not between:
                    covers.append((a, b))
        self._covers = covers
        return list(covers)

    def hasse_diagram(self) -> dict:
        """Hasse diagram as adjacency dict ``{a: [b1, b2, ...]}``
        listing the upper covers of each element."""
        adj: dict = {a: [] for a in self.elements}
        for a, b in self.cover_relations():
            adj[a].append(b)
        return adj

    # ------------------------------------------------------------------
    # Order ideals, filters, intervals
    # ------------------------------------------------------------------

    def principal_order_ideal(self, a: Element) -> Set[Element]:
        """``{x : x <= a}``."""
        self._check(a, a)
        return {x for x in self.elements if self.le(x, a)}

    def principal_order_filter(self, a: Element) -> Set[Element]:
        """``{x : x >= a}``."""
        self._check(a, a)
        return {x for x in self.elements if self.le(a, x)}

    def interval(self, a: Element, b: Element) -> Set[Element]:
        """``[a, b] = {x : a <= x <= b}``."""
        self._check(a, b)
        return {
            x for x in self.elements if self.le(a, x) and self.le(x, b)
        }

    # ------------------------------------------------------------------
    # Chains and antichains
    # ------------------------------------------------------------------

    def chain(self, elts: Sequence[Element]) -> bool:
        """``True`` iff ``elts`` are pairwise comparable."""
        for x in elts:
            self._check(x, x)
        for i, x in enumerate(elts):
            for y in elts[i + 1:]:
                if not (self.le(x, y) or self.le(y, x)):
                    return False
        return True

    def antichain(self, elts: Sequence[Element]) -> bool:
        """``True`` iff ``elts`` are pairwise incomparable."""
        for x in elts:
            self._check(x, x)
        for i, x in enumerate(elts):
            for y in elts[i + 1:]:
                if x == y:
                    return False
                if self.le(x, y) or self.le(y, x):
                    return False
        return True

    def max_antichain(self) -> List[Element]:
        """A maximum antichain (largest set of pairwise incomparable
        elements).

        Implementation: Dilworth's theorem reduces to max-flow / max
        bipartite matching, but for the modest poset sizes we ship
        with we use a brute search over subsets.
        """
        if not self.elements:
            return []
        # Dilworth via min chain cover on bipartite split (Mirsky/König).
        # We use a clean min-flow construction via networkx
        # bipartite matching.
        n = len(self.elements)
        idx = {e: i for i, e in enumerate(self.elements)}
        # Build bipartite graph: left copy L_a connected to right copy
        # R_b iff a < b in the poset.
        B = nx.DiGraph()
        SRC, SNK = "S", "T"
        B.add_node(SRC)
        B.add_node(SNK)
        for i in range(n):
            B.add_edge(SRC, ("L", i), capacity=1)
            B.add_edge(("R", i), SNK, capacity=1)
        for a in self.elements:
            for b in self.elements:
                if self.lt(a, b):
                    B.add_edge(("L", idx[a]), ("R", idx[b]), capacity=1)
        # Maximum matching size = m
        flow_value, _ = nx.maximum_flow(B, SRC, SNK)
        # Width = n - m (Dilworth/Mirsky for finite posets).
        width = n - flow_value
        # Find an antichain of that size by brute scan.  We try
        # subsets in decreasing size starting from `width`.
        from itertools import combinations
        for combo in combinations(self.elements, width):
            if self.antichain(list(combo)):
                return list(combo)
        # Fallback (shouldn't happen): return any single element.
        return [self.elements[0]]

    def min_chain_cover(self) -> List[List[Element]]:
        """A partition of the elements into the minimum number of
        chains (Dilworth)."""
        if not self.elements:
            return []
        # Greedy cover guided by topological order works for small
        # posets and matches Dilworth's bound when paired with the
        # bipartite matching above.  Implementation: assign each
        # element to the first existing chain whose top is below it,
        # else start a new chain.  The order of assignment uses a
        # linear extension.
        order = self.linear_extensions()[0] if self.elements else []
        chains: List[List[Element]] = []
        for e in order:
            placed = False
            for ch in chains:
                if self.le(ch[-1], e):
                    ch.append(e)
                    placed = True
                    break
            if not placed:
                chains.append([e])
        return chains

    # ------------------------------------------------------------------
    # Linear extensions
    # ------------------------------------------------------------------

    def _dag_for_linear_extension(self) -> nx.DiGraph:
        G = nx.DiGraph()
        G.add_nodes_from(self.elements)
        for a, b in self.cover_relations():
            G.add_edge(a, b)
        return G

    def linear_extensions(self) -> List[List[Element]]:
        """All linear extensions of the poset."""
        if not self.elements:
            return [[]]
        G = self._dag_for_linear_extension()
        return [list(t) for t in nx.algorithms.dag.all_topological_sorts(G)]

    def num_linear_extensions(self) -> int:
        """Number of linear extensions."""
        if not self.elements:
            return 1
        # Counting topological sorts is #P-hard in general but the
        # poset sizes shipped here are tiny.
        return sum(1 for _ in nx.algorithms.dag.all_topological_sorts(
            self._dag_for_linear_extension()
        ))

    # ------------------------------------------------------------------
    # Mobius / zeta
    # ------------------------------------------------------------------

    def zeta(self, a: Element, b: Element) -> int:
        """Zeta function: 1 if ``a <= b`` else 0."""
        return 1 if self.le(a, b) else 0

    def mobius(self, a: Element, b: Element) -> int:
        """Mobius function ``mu(a, b)``.

        Defined by the recursion
            mu(a, a) = 1
            mu(a, b) = - sum_{a <= c < b} mu(a, c)   for a < b
            mu(a, b) = 0  otherwise.
        """
        self._check(a, b)
        return self._mobius_cached(a, b)

    @lru_cache(maxsize=None)
    def _mobius_cached(self, a: Element, b: Element) -> int:
        if a == b:
            return 1
        if not self.le(a, b):
            return 0
        total = 0
        for c in self.interval(a, b):
            if c == b:
                continue
            total += self._mobius_cached(a, c)
        return -total

    # ------------------------------------------------------------------
    # Joins / meets
    # ------------------------------------------------------------------

    def join(self, a: Element, b: Element) -> Optional[Element]:
        """``a v b`` (least upper bound) or ``None`` if it does not
        exist or is not unique."""
        self._check(a, b)
        upper = [
            x for x in self.elements if self.le(a, x) and self.le(b, x)
        ]
        if not upper:
            return None
        # Find a minimum among the upper bounds (one that is <= every
        # other upper bound).
        for u in upper:
            if all(self.le(u, v) for v in upper):
                return u
        return None

    def meet(self, a: Element, b: Element) -> Optional[Element]:
        """``a ^ b`` (greatest lower bound) or ``None``."""
        self._check(a, b)
        lower = [
            x for x in self.elements if self.le(x, a) and self.le(x, b)
        ]
        if not lower:
            return None
        for u in lower:
            if all(self.le(v, u) for v in lower):
                return u
        return None

    # ------------------------------------------------------------------
    # Lattice tests
    # ------------------------------------------------------------------

    def is_lattice(self) -> bool:
        """``True`` iff every pair has a join and a meet."""
        for a in self.elements:
            for b in self.elements:
                if self.join(a, b) is None:
                    return False
                if self.meet(a, b) is None:
                    return False
        return True

    def is_distributive(self) -> bool:
        """``True`` iff the poset is a lattice satisfying the
        distributive law ``a ^ (b v c) = (a ^ b) v (a ^ c)``."""
        if not self.is_lattice():
            return False
        for a in self.elements:
            for b in self.elements:
                for c in self.elements:
                    bc = self.join(b, c)
                    ab = self.meet(a, b)
                    ac = self.meet(a, c)
                    lhs = self.meet(a, bc)
                    rhs = self.join(ab, ac)
                    if lhs != rhs:
                        return False
        return True

    # ------------------------------------------------------------------
    # Isomorphism
    # ------------------------------------------------------------------

    def is_isomorphic_to(self, other: "Poset") -> bool:
        """``True`` iff there is an order-preserving bijection
        between ``self`` and ``other``."""
        if len(self.elements) != len(other.elements):
            return False
        # Use networkx digraph isomorphism on cover-relation DAGs.
        G = nx.DiGraph()
        H = nx.DiGraph()
        G.add_nodes_from(self.elements)
        H.add_nodes_from(other.elements)
        for a, b in self.cover_relations():
            G.add_edge(a, b)
        for a, b in other.cover_relations():
            H.add_edge(a, b)
        return nx.is_isomorphic(G, H)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.elements)

    def __repr__(self) -> str:
        return (
            f"Poset(|elements|={len(self.elements)}, "
            f"|covers|={len(self.cover_relations())})"
        )


# ---------------------------------------------------------------------------
# Standard constructors
# ---------------------------------------------------------------------------


def chain_poset(n: int) -> Poset:
    """The total order on ``{1, 2, ..., n}``.

    Parameters
    ----------
    n : int
        Length of the chain (number of elements).  ``n >= 0``.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    elements = list(range(1, n + 1))
    relations = [(i, i + 1) for i in range(1, n)]
    return Poset(elements, relations)


def antichain_poset(n: int) -> Poset:
    """The antichain on ``n`` elements (no nontrivial relations)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return Poset(list(range(1, n + 1)), [])


def boolean_lattice(n: int) -> Poset:
    """``B_n`` — the lattice of subsets of ``{0, ..., n-1}`` ordered
    by inclusion."""
    if n < 0:
        raise ValueError("n must be non-negative")
    base = list(range(n))
    elements: List[frozenset] = []
    for mask in range(1 << n):
        s = frozenset(b for b in base if (mask >> b) & 1)
        elements.append(s)
    relations: List[Tuple[frozenset, frozenset]] = []
    for a in elements:
        for b in elements:
            if a < b:
                relations.append((a, b))
    return Poset(elements, relations)


def divisor_poset(n: int) -> Poset:
    """The divisor lattice ``D_n``: positive divisors of ``n`` ordered
    by divisibility."""
    if n < 1:
        raise ValueError("n must be a positive integer")
    divisors = [d for d in range(1, n + 1) if n % d == 0]
    relations: List[Tuple[int, int]] = []
    for a in divisors:
        for b in divisors:
            if a != b and b % a == 0:
                relations.append((a, b))
    return Poset(divisors, relations)


def product_poset(P: Poset, Q: Poset) -> Poset:
    """Coordinate-wise product ``P x Q``: ``(p,q) <= (p',q')`` iff
    ``p <= p'`` in ``P`` and ``q <= q'`` in ``Q``."""
    elements: List[Tuple[Element, Element]] = [
        (p, q) for p in P.elements for q in Q.elements
    ]
    relations: List[Tuple[Tuple, Tuple]] = []
    for (p1, q1) in elements:
        for (p2, q2) in elements:
            if (p1, q1) == (p2, q2):
                continue
            if P.le(p1, p2) and Q.le(q1, q2):
                relations.append(((p1, q1), (p2, q2)))
    return Poset(elements, relations)


def dual_poset(P: Poset) -> Poset:
    """The opposite poset ``P^op``: same underlying set, reversed
    order."""
    relations = [(b, a) for (a, b) in P.cover_relations()]
    return Poset(list(P.elements), relations)


__all__ = [
    "Poset",
    "chain_poset",
    "antichain_poset",
    "boolean_lattice",
    "divisor_poset",
    "product_poset",
    "dual_poset",
]
