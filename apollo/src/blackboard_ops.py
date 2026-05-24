"""blackboard_ops.py — wrapped Frame H primitives + parsing operators.

Each op has explicit reads/writes/preconditions. The wrappers reuse the
underlying Frame H primitive implementations from forge_primitives.

Bound to Branch C blackboard genome. See blackboard.py.
"""
from __future__ import annotations
import re
import math
import sys
from pathlib import Path

from blackboard import blackboard_op, BlackboardState

# Make Frame H primitives importable
_HEPH_SRC = str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src")
if _HEPH_SRC not in sys.path:
    sys.path.insert(0, _HEPH_SRC)

import forge_primitives as fp  # noqa: E402


# ── Parsing operators (state-only; do not call Frame H) ─────────────


@blackboard_op(
    reads=["problem_text"],
    writes=["numbers"],
)
def parse_numbers(state: BlackboardState) -> BlackboardState:
    """Extract numeric literals from problem_text into typed slot `numbers`."""
    state.numbers = [float(m) for m in re.findall(r"-?\d+(?:\.\d+)?", state.problem_text)]
    return state


_REL_PATTERN = re.compile(
    r"(\b[A-Z][a-z]+)\s+is\s+"
    r"(?:taller|bigger|larger|greater|older|faster|heavier|smarter|stronger|richer)"
    r"\s+than\s+(\b[A-Z][a-z]+)"
)


@blackboard_op(
    reads=["problem_text"],
    writes=["names", "relations"],
)
def parse_names_and_relations(state: BlackboardState) -> BlackboardState:
    """Parse 'X is GREATER than Y' patterns into names + ordered pairs (a > b)."""
    matches = _REL_PATTERN.findall(state.problem_text)
    names = set()
    rels = []
    for a, b in matches:
        names.add(a); names.add(b)
        rels.append((a, b))
    state.names = sorted(names)
    state.relations = rels
    return state


_QUESTION_KEYWORDS = (
    "tallest", "shortest", "biggest", "smallest", "largest", "oldest",
    "youngest", "fastest", "slowest", "richest", "poorest",
    "larger", "smaller", "greater", "less",
)


@blackboard_op(
    reads=["problem_text"],
    writes=["question_target"],
)
def parse_question_target(state: BlackboardState) -> BlackboardState:
    """Pick a single keyword from the question that names what to find."""
    lower = state.problem_text.lower()
    for kw in _QUESTION_KEYWORDS:
        if kw in lower:
            state.question_target = kw
            return state
    return state


# ── Frame H wrappers ─────────────────────────────────────────────────


@blackboard_op(
    reads=["names", "relations"],
    writes=["transitive_closure", "ordered", "max_entity"],
    precondition=lambda s: bool(s.relations),
)
def op_transitive_closure(state: BlackboardState) -> BlackboardState:
    """Wrap check_transitivity-style closure; pick the dominating entity."""
    # We construct a directed graph A -> B meaning "A greater than B"
    graph: dict[str, set[str]] = {n: set() for n in state.names}
    for a, b in state.relations:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set())
    changed = True
    while changed:
        changed = False
        for n in list(graph.keys()):
            for m in list(graph[n]):
                for p in graph.get(m, set()):
                    if p not in graph[n]:
                        graph[n].add(p); changed = True
    state.transitive_closure = graph
    if graph:
        ranked = sorted(graph.items(), key=lambda kv: -len(kv[1]))
        state.ordered = [n for n, _ in ranked]
        state.max_entity = ranked[0][0] if ranked[0][1] else ""
    return state


@blackboard_op(
    reads=["numbers"],
    writes=["max_value"],
    precondition=lambda s: len(s.numbers) > 0,
)
def op_numeric_argmax(state: BlackboardState) -> BlackboardState:
    """Pure max() over the typed numbers slot."""
    state.max_value = max(state.numbers)
    return state


@blackboard_op(
    reads=["probabilities", "evidence"],
    writes=["confidence"],
    precondition=lambda s: bool(s.probabilities) and bool(s.evidence),
)
def op_bayesian_update(state: BlackboardState) -> BlackboardState:
    """Wrap fp.bayesian_update with a typed-slot interface.

    The current state has `probabilities` (named priors) and `evidence`
    (list of {hypothesis, likelihood, false_positive}). Update each
    matching prior. Result aggregated into state.confidence as the
    max posterior across known hypotheses.
    """
    posteriors = []
    for e in state.evidence:
        hyp = e.get("hypothesis", "")
        if hyp in state.probabilities:
            prior = state.probabilities[hyp]
            lik = float(e.get("likelihood", 0.5))
            fp_ = float(e.get("false_positive", 0.5))
            post = fp.bayesian_update(prior=prior, likelihood=lik, false_positive=fp_)
            state.probabilities[hyp] = post
            posteriors.append(post)
    if posteriors:
        state.confidence = max(posteriors)
    return state


@blackboard_op(
    reads=["quantities"],
    writes=["evidence"],
    precondition=lambda s: bool(s.quantities),
)
def op_fencepost(state: BlackboardState) -> BlackboardState:
    """Wrap fp.fencepost_count over a named quantity. Writes one
    evidence record per quantity entry. Reads quantities[k] as
    n_segments; appends fencepost-adjusted count to evidence."""
    for k, n in state.quantities.items():
        adjusted = fp.fencepost_count(n_segments=int(n), include_both_ends=True)
        state.evidence.append({"source": "fencepost", "key": k, "count": adjusted})
    return state


# ── Scoring operators (terminal) ─────────────────────────────────────


@blackboard_op(
    reads=["candidates", "max_entity"],
    writes=["candidate_scores", "selected_answer"],
    # Terminal scoring ops MUST always produce a selected_answer (default
    # to candidates[0] when state is incomplete). We removed the
    # precondition so this op never "skips" — that was the 2026-05-24
    # POC regression.
)
def score_by_max_entity(state: BlackboardState) -> BlackboardState:
    if not state.candidates:
        return state
    target = state.max_entity
    scores = []
    for c in state.candidates:
        if target and (c == target or c.lower() == target.lower()):
            scores.append(1.0)
        elif target and (target in c or c in target):
            scores.append(0.5)
        else:
            scores.append(0.0)
    state.candidate_scores = scores
    idx = max(range(len(scores)), key=lambda i: scores[i])
    state.selected_answer = state.candidates[idx]
    return state


@blackboard_op(
    reads=["candidates", "numbers", "question_target"],
    writes=["candidate_scores", "selected_answer"],
    # Same discipline: scoring ops never skip; they always produce an answer.
)
def score_by_max_value(state: BlackboardState) -> BlackboardState:
    if not state.candidates:
        return state

    # No numbers parsed: fall back to first candidate (preserves prototype's
    # defensive behavior; never leave selected_answer empty).
    if not state.numbers:
        state.candidate_scores = [0.0] * len(state.candidates)
        state.selected_answer = state.candidates[0]
        return state

    is_larger = any(k in state.question_target for k in ("larg", "great", "bigg", "tall"))
    target_val = max(state.numbers) if is_larger else min(state.numbers)

    scores = [0.0] * len(state.candidates)
    for i, c in enumerate(state.candidates):
        m = re.search(r"-?\d+(?:\.\d+)?", c)
        if m and math.isclose(float(m.group(0)), target_val, abs_tol=1e-6):
            scores[i] = 1.0

    # Yes/No fallback when candidates don't contain numbers
    if not any(scores) and state.candidates and state.candidates[0] in ("Yes", "No"):
        if len(state.numbers) >= 2:
            answer_is_yes = state.numbers[0] > state.numbers[1]
            for i, c in enumerate(state.candidates):
                if (c == "Yes" and answer_is_yes) or (c == "No" and not answer_is_yes):
                    scores[i] = 1.0

    state.candidate_scores = scores
    idx = max(range(len(scores)), key=lambda i: scores[i])
    state.selected_answer = state.candidates[idx]
    return state


# Convenience: registry of named ops for genome construction
OP_REGISTRY: dict[str, "BlackboardOp"] = {
    "parse_numbers": parse_numbers,
    "parse_names_and_relations": parse_names_and_relations,
    "parse_question_target": parse_question_target,
    "op_transitive_closure": op_transitive_closure,
    "op_numeric_argmax": op_numeric_argmax,
    "op_bayesian_update": op_bayesian_update,
    "op_fencepost": op_fencepost,
    "score_by_max_entity": score_by_max_entity,
    "score_by_max_value": score_by_max_value,
}
