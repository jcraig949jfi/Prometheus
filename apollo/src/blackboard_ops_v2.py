"""blackboard_ops_v2.py — rewritten primitives as state transformers.

Per the 2026-05-25 reviewer convergence (Gemini, ChatGPT, DeepSeek): three
Frame H primitives are "answer-producing heuristics" by nature, not typed
state transformations. Wrapping them in @blackboard_op declarations doesn't
fix the semantics. They must be REWRITTEN.

Rewritten in this module:
  - evidence_updater          (was: bayesian_update)
  - entity_counter            (was: fencepost_count)
  - distribution_reducer      (was: expected_value)

Each rewrite reads a typed-state COLLECTION and writes a typed-state
COLLECTION — never a scalar answer. The whole point is that downstream
operators consume the updated collection, not a precomputed answer.

These are new ops; the v1 wrappers in blackboard_ops.py remain available
for backward compatibility but should be quarantined to terminal-scorer
roles per ChatGPT's primitive-classification scheme.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blackboard import blackboard_op, BlackboardState

# Make Frame H originals importable for arithmetic kernels
_HEPH_SRC = str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src")
if _HEPH_SRC not in sys.path:
    sys.path.insert(0, _HEPH_SRC)

import forge_primitives as fp  # noqa: E402


# ── evidence_updater (rewrite of bayesian_update) ────────────────────


@blackboard_op(
    reads=["hypotheses", "evidence", "probabilities"],
    writes=["probabilities", "confidence"],
    precondition=lambda s: bool(s.hypotheses) and bool(s.evidence),
)
def evidence_updater(state: BlackboardState) -> BlackboardState:
    """Update the entire hypothesis lattice from observed evidence.

    Difference from bayesian_update v1 (which took 3 scalars and emitted
    a scalar posterior): this operates on the NAMED HYPOTHESIS LATTICE.
    Each evidence record updates every matching hypothesis's posterior.
    The op is composable because downstream operators see the full
    updated `probabilities` dict, not a single point-estimate.

    Reads:
      hypotheses        — list of named hypotheses still under consideration
      evidence          — list of {hypothesis, likelihood, false_positive, source}
      probabilities     — current named priors (dict name -> p in [0,1])

    Writes:
      probabilities     — updated posteriors (same dict, mutated)
      confidence        — max posterior across hypotheses still in play
    """
    for ev in state.evidence:
        hyp = ev.get("hypothesis", "")
        if hyp not in state.hypotheses:
            continue
        prior = float(state.probabilities.get(hyp, 0.5))
        lik = float(ev.get("likelihood", 0.5))
        fp_ = float(ev.get("false_positive", 0.5))
        posterior = fp.bayesian_update(prior=prior, likelihood=lik, false_positive=fp_)
        state.probabilities[hyp] = posterior
    if state.probabilities:
        state.confidence = max(p for h, p in state.probabilities.items() if h in state.hypotheses)
    return state


# ── entity_counter (rewrite of fencepost_count) ──────────────────────


@blackboard_op(
    reads=["names", "relations", "quantities"],
    writes=["counts", "evidence"],
    precondition=lambda s: bool(s.names) or bool(s.relations) or bool(s.quantities),
)
def entity_counter(state: BlackboardState) -> BlackboardState:
    """Build a typed count dict with provenance per category.

    Difference from fencepost_count v1 (which took an int and returned
    an int): this reads the FULL parsed state (entities, relations, named
    quantities) and writes a structured counts dict keyed by category.
    Each count carries its provenance — which slot it was derived from,
    and via which counting rule (fencepost-included-both-ends vs not).

    Downstream ops can use the counts as evidence in a Bayesian update,
    or as constraint inputs, or as candidate features. The count is no
    longer a bare answer-producer.
    """
    out = dict(state.counts) if state.counts else {}
    new_evidence = list(state.evidence) if state.evidence else []

    if state.names:
        out["names"] = {
            "count": len(state.names),
            "provenance": "len(names)",
            "fencepost_adjusted": fp.fencepost_count(n_segments=len(state.names), include_both_ends=True),
        }
        new_evidence.append({"source": "entity_counter", "category": "names",
                             "count": len(state.names)})

    if state.relations:
        out["relations"] = {
            "count": len(state.relations),
            "provenance": "len(relations)",
            "fencepost_adjusted": fp.fencepost_count(n_segments=len(state.relations), include_both_ends=False),
        }
        new_evidence.append({"source": "entity_counter", "category": "relations",
                             "count": len(state.relations)})

    if state.quantities:
        for k, v in state.quantities.items():
            try:
                n = int(v)
            except (TypeError, ValueError):
                continue
            out[f"quantity_{k}"] = {
                "count": n,
                "provenance": f"quantities[{k}]",
                "fencepost_adjusted": fp.fencepost_count(n_segments=n, include_both_ends=True),
            }

    state.counts = out
    state.evidence = new_evidence
    return state


# ── distribution_reducer (rewrite of expected_value) ─────────────────


@blackboard_op(
    reads=["probabilities", "evidence"],
    writes=["evidence", "confidence"],
    precondition=lambda s: bool(s.probabilities),
)
def distribution_reducer(state: BlackboardState) -> BlackboardState:
    """Reduce the probability distribution to summary statistics, keeping
    the distribution as a first-class object accessible downstream.

    Difference from expected_value v1 (which collapsed a list of
    (probability, value) tuples to a scalar expectation): this preserves
    the full distribution in state.probabilities AND writes mean/variance/
    mode summary statistics as new evidence records. Downstream ops see
    both the underlying distribution and its summary.
    """
    if not state.probabilities:
        return state
    items = [(h, p) for h, p in state.probabilities.items()]
    weights = [p for _, p in items]
    total = sum(weights)
    if total <= 0:
        return state
    norm = [w / total for w in weights]
    # Mean position (assigning ordinal positions to hypothesis names)
    positions = list(range(len(items)))
    mean_pos = sum(p * pos for p, pos in zip(norm, positions))
    variance = sum(p * (pos - mean_pos) ** 2 for p, pos in zip(norm, positions))
    mode_h, mode_p = max(items, key=lambda kv: kv[1])

    summary = {
        "source": "distribution_reducer",
        "n_hypotheses": len(items),
        "total_mass": total,
        "mean_position": mean_pos,
        "variance": variance,
        "mode_hypothesis": mode_h,
        "mode_probability": mode_p,
        "entropy": -sum(p * math.log(p + 1e-12) for p in norm),
    }
    if state.evidence is None:
        state.evidence = []
    state.evidence.append(summary)
    # Confidence: how peaked is the distribution
    state.confidence = mode_p
    return state


# ── Composing ops for synthetic-dependency tasks (2026-05-29) ────────
# These exist to test whether the substrate can EXPRESS a genuinely
# two-stage composition where an intermediate slot is causally necessary.
# Each writes ONE slot (no side-output), reads canonical slots only.


import re as _re


@blackboard_op(
    reads=["problem_text"],
    writes=["question_target"],
)
def parse_ordinal(state: BlackboardState) -> BlackboardState:
    """Extract the ORDINAL ('first'/'second'/'third'/...) the question asks for.

    Distinct from parse_question_target (which grabs the superlative keyword
    like 'tallest'). The 2026-05-29 gauntlet caught that conflating these
    two made select_nth read the wrong index. This op writes the ordinal
    word canonically into question_target so select_nth indexes correctly.
    """
    text = state.problem_text.lower()
    for word in ("first", "second", "third", "fourth", "fifth"):
        if word in text:
            state.question_target = word
            return state
    # No explicit ordinal — fall back to superlative => first
    for word in ("tallest", "largest", "biggest", "shortest", "smallest"):
        if word in text:
            state.question_target = "first" if word in ("tallest", "largest", "biggest") else "last"
            return state
    return state


@blackboard_op(
    reads=["relations"],
    writes=["ordered"],
    precondition=lambda s: bool(s.relations),
)
def op_build_ordering(state: BlackboardState) -> BlackboardState:
    """Build a full ranking from pairwise 'a > b' relations.

    Single-output (writes only `ordered`). The ordering is a genuine
    intermediate: a downstream nth-selector cannot work without it, and
    no single primitive produces it.
    """
    nodes = set()
    for a, b in state.relations:
        nodes.add(a); nodes.add(b)
    # Count how many others each node dominates (transitively)
    reach = {n: set() for n in nodes}
    for a, b in state.relations:
        reach[a].add(b)
    changed = True
    while changed:
        changed = False
        for n in list(reach):
            for m in list(reach[n]):
                for p in reach.get(m, set()):
                    if p not in reach[n]:
                        reach[n].add(p); changed = True
    # Rank by domination count descending (the top dominates the most)
    state.ordered = sorted(nodes, key=lambda n: -len(reach[n]))
    return state


@blackboard_op(
    reads=["ordered", "question_target"],
    writes=["selected_answer", "candidate_scores"],
    name="select_nth",  # terminal scorer role: writing answer + scores together is OK
)
def select_nth(state: BlackboardState) -> BlackboardState:
    """Select the nth-ranked entity from `ordered`, matched to a candidate.

    Reads the ordinal from question_target ('first'/'second'/'third'/...).
    This op is CAUSALLY DEPENDENT on `ordered` — corrupt that slot and
    the answer is wrong. That is the dependency the gauntlet tests.
    """
    if not state.candidates:
        return state
    ordinal_map = {"first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
                   "tallest": 0, "largest": 0, "biggest": 0,
                   "shortest": -1, "smallest": -1}
    idx = None
    for word, i in ordinal_map.items():
        if word in state.question_target.lower():
            idx = i
            break
    if idx is None or not state.ordered:
        # No ordering or no ordinal — fall back to first candidate
        state.candidate_scores = [0.0] * len(state.candidates)
        state.selected_answer = state.candidates[0]
        return state
    try:
        target_entity = state.ordered[idx]
    except IndexError:
        target_entity = state.ordered[0]
    scores = []
    for c in state.candidates:
        if target_entity and (c == target_entity or c.lower() == target_entity.lower()
                              or target_entity in c):
            scores.append(1.0)
        else:
            scores.append(0.0)
    state.candidate_scores = scores
    idx_best = max(range(len(scores)), key=lambda i: scores[i])
    state.selected_answer = state.candidates[idx_best]
    return state


@blackboard_op(
    reads=["problem_text"],
    writes=["counts"],
)
def parse_box_items(state: BlackboardState) -> BlackboardState:
    """Parse 'N <label> boxes with M items each' patterns into per-category
    products. Writes counts = {label: N*M, ...}. The product is the genuine
    per-category intermediate that op_aggregate_quantities then sums."""
    out = dict(state.counts) if state.counts else {}
    pattern = _re.compile(r'(\d+)\s+(\w+)\s+boxes?\s+with\s+(\d+)\s+items?\s+each')
    for m in pattern.finditer(state.problem_text):
        n_boxes = int(m.group(1))
        label = m.group(2)
        items_each = int(m.group(3))
        out[label] = {"count": n_boxes * items_each, "provenance": f"{n_boxes}x{items_each}"}
    state.counts = out
    return state


@blackboard_op(
    reads=["max_value", "candidates"],
    writes=["selected_answer", "candidate_scores"],
    name="score_by_aggregate",  # terminal scorer role
)
def score_by_aggregate(state: BlackboardState) -> BlackboardState:
    """Match the aggregate value (max_value) to a numeric candidate.

    Reads max_value (the load-bearing aggregate). Corrupt it and the
    answer is wrong — the dependency the gauntlet tests."""
    if not state.candidates:
        return state
    if state.max_value is None:
        state.candidate_scores = [0.0] * len(state.candidates)
        state.selected_answer = state.candidates[0]
        return state
    target = state.max_value
    scores = []
    for c in state.candidates:
        m = _re.search(r'-?\d+(?:\.\d+)?', c)
        if m and abs(float(m.group(0)) - target) < 1e-6:
            scores.append(1.0)
        else:
            scores.append(0.0)
    state.candidate_scores = scores
    idx = max(range(len(scores)), key=lambda i: scores[i])
    state.selected_answer = state.candidates[idx]
    return state


@blackboard_op(
    reads=["counts"],
    writes=["max_value"],
    precondition=lambda s: bool(s.counts),
)
def op_aggregate_quantities(state: BlackboardState) -> BlackboardState:
    """Sum the per-category counts into a single aggregate.

    Reads the typed counts dict, writes a single aggregate to max_value.
    A genuine two-stage dependency: the per-category counts must exist
    (written by entity_counter) before this op can aggregate them.
    """
    total = 0
    for k, v in state.counts.items():
        if isinstance(v, dict) and "count" in v:
            total += v["count"]
        elif isinstance(v, (int, float)):
            total += v
    state.max_value = float(total)
    return state


# ── Registry (additive; v1 ops remain available) ─────────────────────


OP_REGISTRY_V2: dict[str, "BlackboardOp"] = {
    "evidence_updater": evidence_updater,
    "entity_counter": entity_counter,
    "distribution_reducer": distribution_reducer,
    "op_build_ordering": op_build_ordering,
    "select_nth": select_nth,
    "op_aggregate_quantities": op_aggregate_quantities,
}
