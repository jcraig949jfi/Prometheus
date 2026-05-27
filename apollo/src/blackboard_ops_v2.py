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


# ── Registry (additive; v1 ops remain available) ─────────────────────


OP_REGISTRY_V2: dict[str, "BlackboardOp"] = {
    "evidence_updater": evidence_updater,
    "entity_counter": entity_counter,
    "distribution_reducer": distribution_reducer,
}
