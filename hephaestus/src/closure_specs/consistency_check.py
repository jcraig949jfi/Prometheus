"""MINT-0004 consistency_check -- semantic specification (the second specimen; Addendum 3).

Apollo's canary: "A > B and B > C and C > A. Consistent?" -- a set of strict-order relations is
consistent iff its directed graph has no cycle. Semantic state: the relation set as a tuple of
(a, b) pairs over a small universe. Target (bool): acyclic. The target is DEFINED INDEPENDENTLY
here by a plain depth-first search that shares no code with the frozen primitives.

SEARCH points: all 64 digraphs on 3 nodes without self-loops (edge subsets of the 6 ordered pairs).
VERIFY points: all 4096 digraphs on 4 nodes without self-loops -- exhaustive, disjoint, larger.
Single route key (no quantifier), so A0 == A1 here: routing is not a resource this wall needs.
"""
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))
import forge_primitives as fp  # noqa: E402

NOTES = "consistency_check: is a set of strict-order relations acyclic? Independent DFS target; frozen primitives take edge lists."
REPRESENTATION_DEBT = ("Moderate: parse 'A > B and B > C and C > A' into (a,b) pairs. Apollo's REGISTRY already has "
                       "parse_names_and_relations / relations_from_facts writing the `relations` slot; the missing piece "
                       "was never the parse, it was that no op turns `relations` into a consistency verdict.")
ROUTE_KEYS = ["consistent"]
TARGET_TYPE = "bool"


def _digraphs(n):
    pairs = [(a, b) for a in range(n) for b in range(n) if a != b]
    for r in range(len(pairs) + 1):
        for sub in itertools.combinations(pairs, r):
            yield tuple(sub)


SEARCH_POINTS = list(_digraphs(3))
# VERIFY_EXHAUSTIVE_SMALL: all 4,096 digraphs on 4 nodes.
VERIFY_POINTS = list(_digraphs(4))
# VERIFY_STRUCTURAL_SHIFT (Addendum 4, Q5): 5- and 6-node digraphs sampled deterministically, half of
# them with DUPLICATE edges (rels is a tuple, so duplicates are representable) and with node labels
# drawn from a larger universe (isolated nodes are NOT representable by an edge set alone -- a
# representation-semantics fact this spec records rather than hides).
import random as _random
_rng = _random.Random(20260901)
def _shift():
    pts = []
    for n in (5, 6):
        pairs = [(a, b) for a in range(n) for b in range(n) if a != b]
        for _ in range(150):
            k = _rng.randint(0, len(pairs))
            edges = _rng.sample(pairs, k)
            if _rng.random() < 0.5 and edges:
                edges = edges + _rng.sample(edges, max(1, len(edges) // 3))   # duplicates
            off = _rng.choice([0, 10, 100])                                    # larger label universe
            pts.append(tuple((a + off, b + off) for a, b in edges))
    return pts
VERIFY_SHIFT_DESCRIPTION = "300 sampled 5/6-node digraphs, half with duplicate edges, labels offset into a larger universe"
VERIFY_SHIFT_POINTS = _shift()


def _acyclic(edges):
    """Independent target: DFS three-colour cycle detection. Shares nothing with forge_primitives."""
    nodes = {x for e in edges for x in e}
    adj = {x: [] for x in nodes}
    for a, b in edges:
        adj[a].append(b)
    WHITE, GREY, BLACK = 0, 1, 2
    color = {x: WHITE for x in nodes}
    def visit(u):
        color[u] = GREY
        for v in adj[u]:
            if color[v] == GREY or (color[v] == WHITE and not visit(v)):
                return False
        color[u] = BLACK
        return True
    return all(visit(x) for x in nodes if color[x] == WHITE)


def target(_key, edges):
    return _acyclic(edges)


# Relation lists are the only typed terminal; small int constants for generic ops.
TERMINALS = {
    "rels": ("edges", lambda pt: [tuple(e) for e in pt]),
    "0": ("int", lambda pt: 0),
    "1": ("int", lambda pt: 1),
}

def _topo(edges):
    return fp.topological_sort([list(e) for e in edges])

def _closure(edges):
    return fp.check_transitivity([tuple(e) for e in edges])

FROZEN_OPS = {
    # declared return types as observed: topological_sort -> list | None ; check_transitivity -> dict
    "topological_sort":   (("edges",), "opt_list", _topo),
    "check_transitivity": (("edges",), "dict",     _closure),
    "pigeonhole_check":   (("int", "int"), "bool", lambda a, b: fp.pigeonhole_check(a, b)),
    "all_but_n":          (("int", "int"), "int",  lambda a, b: fp.all_but_n(a, b)),
}
# A2 uses the FROZEN global basis (closure_specs/generic_basis.py). The per-spec `self_reach` op that
# produced the first MINT-0004 witness is GONE (Addendum 4, Q2): that op was tuned to this wall.
B_OPS = {
    "has_cycle_dfs": (("edges",), "bool", lambda e: not _acyclic(e)),   # the generic control: any small program can
    "not":           (("bool",), "bool", lambda a: not a),
    "eq":            (("int", "int"), "bool", lambda a, b: a == b),
    "len_edges":     (("edges",), "int", lambda e: len(e)),
}
