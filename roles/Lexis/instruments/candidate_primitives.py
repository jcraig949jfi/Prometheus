"""Candidate primitives for the G5 redundancy gate.

PROVENANCE, STATED FIRST AND HONESTLY. These three are **LLM-authored** -- written by
Lexis (Claude Opus 5) after reading the four blocked task categories in
`STEP1_CEILING_CLOSED_2026-08-25.md` section 5. They are therefore the **LLM arm** of the
STEP 3 comparison, not the symbolic arm. Nothing here was produced by repeated-subgraph
compression, anti-unification, or CEGIS. Labelling them otherwise would corrupt the one
comparison STEP 3 exists to make.

They live in `roles/Lexis/`, are never imported by `apollo/`, and modify nothing there.
They exist to be pushed through the gate stack, and they are expected to fail parts of it.

Each is a `BlackboardOp` so the closure machinery treats it exactly like a registry
operator -- same wrapper, same precondition/skip semantics, same provenance.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "apollo" / "src"))

from blackboard import BlackboardState, blackboard_op   # noqa: E402


# ── C1 ── generalized order-relation parser ────────────────────────────────────
# Apollo's `_REL_PATTERN` requires `[A-Z][a-z]+` on both sides and one of ten hard-coded
# comparatives. It encodes a general verb -- "read a strict partial order out of text" --
# and then welds it to capitalised multi-letter proper nouns and an English adjective list.
# This one keeps the verb and drops the nouns: any token either side, and a relation
# vocabulary that includes temporal precedence. Direction is normalised so the written pair
# is always (greater, lesser) / (earlier, later), matching Apollo's own convention.
_GEN_GREATER = re.compile(
    r"(\b[A-Za-z][A-Za-z]*)\s+is\s+"
    r"(?:taller|bigger|larger|greater|older|faster|heavier|smarter|stronger|richer)"
    r"\s+than\s+(\b[A-Za-z][A-Za-z]*)")
_GEN_BEFORE = re.compile(
    r"(\b[A-Za-z][A-Za-z]*)\s+(?:happened\s+)?before\s+(\b[A-Za-z][A-Za-z]*)")


@blackboard_op(reads=["problem_text"], writes=["names", "relations"],
               name="lexis_parse_relations_general")
def parse_relations_general(state: BlackboardState) -> BlackboardState:
    """Same verb as parse_names_and_relations, decoupled from capitalised proper nouns
    and from the closed comparative list. 'X before Y' is emitted as (Y, X) so that the
    slot's ordering convention -- first element dominates -- means 'earliest'."""
    rels = list(_GEN_GREATER.findall(state.problem_text))
    rels += [(b, a) for a, b in _GEN_BEFORE.findall(state.problem_text)]
    if not rels:
        return state
    state.relations = rels
    state.names = sorted({x for pair in rels for x in pair})
    return state


# ── C2 ── integer remainder after removal ──────────────────────────────────────
# The `all_but_n` category is "There were N items. K were removed. How many remain?"
# Apollo parses numbers but has no operator that combines two of them arithmetically into
# a value a scorer can match against a candidate.
@blackboard_op(reads=["numbers"], writes=["max_value"],
               precondition=lambda s: len(s.numbers) >= 2,
               name="lexis_op_subtract")
def op_subtract(state: BlackboardState) -> BlackboardState:
    """Write the difference of the two largest parsed numbers into max_value, so the
    existing score_by_max_value can route it. Deliberately reuses an existing slot rather
    than adding one: adding a slot would change the substrate, not the vocabulary."""
    ns = sorted(state.numbers, reverse=True)
    state.max_value = ns[0] - ns[1]
    return state


# ── C3 ── order-consistency (cycle detection) ──────────────────────────────────
# `consistency_check` is "A > B, B > C, C > A. Are these consistent?" The relations are a
# directed graph; the answer is whether it is acyclic. Apollo has op_build_ordering and a
# quarantined op_transitive_closure but nothing that reports acyclicity as a boolean.
@blackboard_op(reads=["relations"], writes=["comparison"],
               precondition=lambda s: len(s.relations) > 0,
               name="lexis_op_order_consistent")
def op_order_consistent(state: BlackboardState) -> BlackboardState:
    """comparison := True iff the relation graph is acyclic. Writes the existing boolean
    slot so the existing score_by_comparison__g can route it."""
    adj: dict[str, list[str]] = {}
    for a, b in state.relations:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, [])
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in adj}

    def has_cycle(u):
        colour[u] = GREY
        for v in adj[u]:
            if colour[v] == GREY:
                return True
            if colour[v] == WHITE and has_cycle(v):
                return True
        colour[u] = BLACK
        return False

    state.comparison = not any(colour[n] == WHITE and has_cycle(n) for n in list(adj))
    return state


CANDIDATES = {
    "lexis_parse_relations_general": parse_relations_general,
    "lexis_op_subtract": op_subtract,
    "lexis_op_order_consistent": op_order_consistent,
}
