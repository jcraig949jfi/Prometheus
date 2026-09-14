"""Name-blind matching over the catalogue's behavioural axes (Nyx, 2026-09-12).

A QUERY is a partial point in the classification space: any subset of the signature axes
plus optional geometry alternatives. It never contains a name, a lineage or free text -- the
matcher cannot read them, by construction. This is the tool the directive imagines: an organism
produced something that SELECTs from a SET under a TOTAL order with EXTERNAL state; which known
bits do that?

Scoring is deliberately dumb and inspectable: each specified axis contributes 1.0 on exact match,
a vocabulary-declared partial credit for near values (e.g. ORDER PARTIAL vs TOTAL = 0.5), 0
otherwise. Score = matched / specified. Ties are broken by grade (T1 first) and then by id, so
runs are reproducible. The point is not cleverness; it is that a query with k axes finds the
bits that agree on k axes, and the caller can see WHICH axes disagreed.

    python -m nyx.catalog.search verb=SELECT in_geometry=MAP order_req=TOTAL
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from nyx.catalog.schema import GRADES, SIGNATURE_FIELDS, load_all

NEAR = {  # partial credit between vocabulary values on the same axis
    ("order_req", "PARTIAL", "TOTAL"): 0.5, ("order_req", "TOTAL", "WELL_FOUNDED"): 0.5,
    ("metric_req", "DISTANCE", "SIMILARITY"): 0.5, ("metric_req", "EQUALITY", "DISTANCE"): 0.25,
    ("state_req", "LOCAL", "GLOBAL"): 0.5, ("state_req", "GLOBAL", "EXTERNAL"): 0.5,
    ("guarantee", "LOCAL_OPTIMUM", "OPTIMAL"): 0.5, ("guarantee", "SOUND", "EXACT"): 0.5,
    ("guarantee", "APPROXIMATE", "PROBABILISTIC_BOUND"): 0.5,
    ("in_geometry", "SEQUENCE", "STRING"): 0.5, ("in_geometry", "SEQUENCE", "STREAM"): 0.5,
    ("in_geometry", "SET", "MULTISET"): 0.75, ("in_geometry", "TREE", "DAG"): 0.5, ("in_geometry", "DAG", "GRAPH"): 0.5,
    ("in_geometry", "MATRIX", "TENSOR"): 0.75, ("in_geometry", "MAP", "RECORD"): 0.5,
    ("out_geometry", "SEQUENCE", "STRING"): 0.5, ("out_geometry", "SET", "MULTISET"): 0.75,
    ("out_geometry", "TREE", "DAG"): 0.5, ("out_geometry", "DAG", "GRAPH"): 0.5, ("out_geometry", "MATRIX", "TENSOR"): 0.75,
    ("verb", "SEARCH", "SELECT"): 0.25, ("verb", "ORDER", "SELECT"): 0.25, ("verb", "REPAIR", "CORRECT"): 0.5,
    ("verb", "REMEMBER", "RESUME"): 0.25, ("verb", "PARTITION", "COMPRESS"): 0.25, ("verb", "VERIFY", "DETECT"): 0.5,
    ("verb", "COMPARE", "DETECT"): 0.25, ("verb", "COMPARE", "PREDICT"): 0.25,
    # strategy (v0.2): near values are ways of organising work that a naive observer would confuse
    ("strategy", "DIVIDE_CONQUER", "DYNAMIC_PROGRAMMING"): 0.5, ("strategy", "INCREMENTAL", "GREEDY"): 0.5,
    ("strategy", "DIVIDE_CONQUER", "PARTITION_BY_VALUE"): 0.5,
    ("strategy", "INCREMENTAL", "STREAMING"): 0.5, ("strategy", "EXCHANGE", "FIXPOINT_ITERATION"): 0.5,
    ("strategy", "BACKTRACKING", "BRANCH_AND_BOUND"): 0.5, ("strategy", "DISTRIBUTION", "PRECOMPUTED_TABLE"): 0.25,
    ("strategy", "DIRECT", "PRECOMPUTED_TABLE"): 0.25, ("strategy", "RANDOMIZED", "DIRECT"): 0.25,
    # iteration (v0.4)
    ("iteration", "FIFO", "PARALLEL_ROUNDS"): 0.5, ("iteration", "PRIORITY", "SORTED_GLOBAL"): 0.5,
    ("iteration", "LIFO", "PRIORITY"): 0.25, ("iteration", "SWEEP", "FIFO"): 0.25, ("iteration", "RANDOM", "NONE"): 0.25,
}
FORBIDDEN_QUERY_KEYS = {"name", "lineage", "sources", "mechanism", "id", "instances"}


def axis_score(axis: str, want: str, have: str) -> float:
    if want == have:
        return 1.0
    return NEAR.get((axis, want, have), NEAR.get((axis, have, want), 0.0))


def match(query: Dict[str, Any], bits: List[Dict[str, Any]]) -> List[Tuple[float, Dict[str, Any], Dict[str, float]]]:
    bad = FORBIDDEN_QUERY_KEYS & set(query)
    if bad:
        raise ValueError(f"query may not contain provenance/name fields: {sorted(bad)} -- the matcher is name-blind by construction")
    axes = [k for k in SIGNATURE_FIELDS if k in query]
    if not axes:
        raise ValueError("query specifies no behavioural axis")
    ranked = []
    for b in bits:
        per = {}
        for k in axes:
            wants = query[k] if isinstance(query[k], list) else [query[k]]
            per[k] = max(axis_score(k, w, str(b.get(k))) for w in wants)
        score = sum(per.values()) / len(axes)
        ranked.append((score, b, per))
    ranked.sort(key=lambda t: (-t[0], GRADES.index(t[1].get("grade", "unknown")) if t[1].get("grade") in GRADES else 99, t[1]["id"]))
    return ranked


def explain(ranked, top: int = 5) -> str:
    lines = []
    for score, b, per in ranked[:top]:
        miss = [f"{k}:{b.get(k)}" for k, v in per.items() if v < 1.0]
        lines.append(f"{score:.2f}  {b['id']}  [{b.get('grade')}]  " + (f"disagrees on {', '.join(miss)}" if miss else "exact on all queried axes"))
    return "\n".join(lines)


def main(argv: List[str]) -> int:
    root = Path("nyx/catalog/bits")
    q: Dict[str, Any] = {}
    for a in argv[1:]:
        k, _, v = a.partition("=")
        q[k] = v.split("|") if "|" in v else v
    ranked = match(q, load_all(root))
    print(explain(ranked, top=10))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
