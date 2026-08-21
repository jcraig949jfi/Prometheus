"""R8: representation shift — CONSTRUCT a task-relevant representation-changing map.

Round 5, item 11.3, adopted verbatim as the design: if both representations are supplied and
the system merely chooses, that is R4 wearing R8 clothing. To force R8 the useful
representation must be INSTANCE-DERIVED and absent beforehand.

Their family, implemented: a graph whose nodes fall into equivalence classes by identical
neighbourhood structure. Raw search over nodes exceeds budget; the quotient graph has a
handful of nodes and answers immediately. Node names and class sizes are randomised per
episode, and **the partition is never supplied** — it must be inferred. A precomputed
two-view selector cannot help, because the useful representation is one of exponentially many
possible partitions (Bell number of |V|).

Their sharper twin, also implemented: the SAME object with two goals requiring INCOMPATIBLE
quotients, so a generic canonicaliser is insufficient and the map must be goal-conditioned,
phi_{x,G} : X -> Z.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

Graph = Dict[str, Set[str]]  # adjacency


# ---- instance generation --------------------------------------------------------------------

# ---- the representation-CONSTRUCTING circuit ------------------------------------------------

def infer_partition(g: Graph, rounds: int = 4) -> Dict[str, int]:
    """Colour refinement (1-WL): infer the equivalence classes from neighbourhood structure.

    This is the constructed map. Nothing about the partition was supplied; it is derived from
    THIS instance. The number of possible partitions is the Bell number of |V|, so no
    precomputed catalogue of representations can contain it."""
    colour: Dict[str, int] = {n: 0 for n in g}
    for _ in range(rounds):
        sig: Dict[str, Tuple] = {}
        for n in g:
            sig[n] = (colour[n], tuple(sorted(colour[m] for m in g[n])))
        buckets = {s: i for i, s in enumerate(sorted(set(sig.values())))}
        new = {n: buckets[sig[n]] for n in g}
        if new == colour:
            break
        colour = new
    return colour


def quotient(g: Graph, colour: Dict[str, int]) -> Graph:
    """Build the quotient graph on the inferred classes — the new representation."""
    q: Graph = {}
    for n, nbrs in g.items():
        cu = f"c{colour[n]}"
        q.setdefault(cu, set())
        for m in nbrs:
            cv = f"c{colour[m]}"
            if cv != cu:
                q[cu].add(cv)
    return q



def make_class_graph(rng: random.Random, class_sizes: List[int],
                     attempts: int = 60) -> Tuple[Graph, Dict[str, int]]:
    """A graph on sum(class_sizes) nodes whose classes are recoverable from STRUCTURE alone.

    SELF-VALIDATING, and it has to be: the first draft used a ring over classes, which makes
    the graph complete multipartite — every node then has the identical neighbour-colour
    multiset and colour refinement collapses to ONE class. Not every class structure is
    1-WL-recoverable, so the generator samples a random symmetric class-adjacency (self-
    adjacency allowed) and REJECTS any instance whose inferred partition does not match the
    planted one. A probe generator that cannot certify its own ground truth is not a probe
    generator.
    """
    k = len(class_sizes)
    for _ in range(attempts):
        names: List[str] = []
        truth: Dict[str, int] = {}
        for ci, size in enumerate(class_sizes):
            for _ in range(size):
                n = f"n{rng.randrange(10**9)}"
                while n in truth:
                    n = f"n{rng.randrange(10**9)}"
                names.append(n)
                truth[n] = ci
        adj = [[False] * k for _ in range(k)]
        for i in range(k):
            for j in range(i, k):
                adj[i][j] = adj[j][i] = bool(rng.getrandbits(1))
        g: Graph = {n: set() for n in names}
        for u in names:
            for v in names:
                if u != v and adj[truth[u]][truth[v]]:
                    g[u].add(v)
        rng.shuffle(names)
        g = {n: g[n] for n in names}
        colour = infer_partition(g)
        groups: Dict[int, Set[int]] = {}
        for n, c in colour.items():
            groups.setdefault(c, set()).add(truth[n])
        if len(groups) == k and all(len(v) == 1 for v in groups.values()):
            return g, truth
    raise RuntimeError(f"could not sample a 1-WL-recoverable instance for sizes {class_sizes}")


@dataclass
class RepresentationShifter:
    """R8: infers the partition, builds the quotient, and answers there. Work is counted in
    the representation it actually searched, so the budget separation is measurable."""

    work: int = 0

    def solve(self, g: Graph, budget: int) -> Optional[int]:
        colour = infer_partition(g)
        q = quotient(g, colour)
        self.work = len(q)                     # searched the quotient, not the raw graph
        if self.work > budget:
            return None
        return len(q)                          # the answer: number of structural classes


@dataclass
class RawSearcher:
    """R7-and-below signature: stays in the given representation and exceeds the budget."""

    work: int = 0

    def solve(self, g: Graph, budget: int) -> Optional[int]:
        self.work = len(g)                     # must touch every node in the raw view
        if self.work > budget:
            return None
        return len({frozenset(v) for v in g.values()})


@dataclass
class PrecomputedViewSelector:
    """The R4-in-R8-clothing trap: holds a FIXED catalogue of representations and picks one.
    It cannot contain the instance's partition because the partition is instance-derived."""

    catalogue: List[Dict[str, int]] = field(default_factory=list)
    work: int = 0

    def solve(self, g: Graph, budget: int) -> Optional[int]:
        for colour in self.catalogue:
            if set(colour) == set(g):          # a view that even applies to this instance
                q = quotient(g, colour)
                self.work = len(q)
                if self.work <= budget:
                    return len(q)
        self.work = len(g)
        return None


# ---- goal-conditioned representation (their sharper twin) -----------------------------------

@dataclass
class TwoGoalObject:
    """One object, two goals whose useful quotients are INCOMPATIBLE.

    items carry two independent attributes; goal 'parity' needs the quotient by a % 2, goal
    'residue3' needs the quotient by b % 3. Neither refines the other, so no single canonical
    form serves both — the map must be conditioned on the goal."""

    items: List[Tuple[int, int]]

    def quotient_for(self, goal: str) -> Dict[Tuple[int, int], int]:
        if goal == "parity":
            return {it: it[0] % 2 for it in self.items}
        if goal == "residue3":
            return {it: it[1] % 3 for it in self.items}
        raise ValueError(goal)

    def classes_for(self, goal: str) -> int:
        return len(set(self.quotient_for(goal).values()))


def generic_canonical_form(obj: TwoGoalObject) -> Dict[Tuple[int, int], int]:
    """A goal-BLIND canonicaliser: one fixed quotient (by the first attribute's parity).
    Correct for one goal, wrong for the other — the point of the twin."""
    return {it: it[0] % 2 for it in obj.items}
