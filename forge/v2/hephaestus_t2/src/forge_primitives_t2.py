"""Forge Primitives Tier 2 — higher-order reasoning compositions.

These primitives COMPOSE Tier 1 building blocks into richer reasoning
patterns: deliberation, perspective-shifting, self-critique, analogy,
ensemble voting, error correction, causal chains, temporal reasoning,
and multi-hop inference.

Usage in forged tools:
    from forge_primitives_t2 import deliberate, causal_reason, multi_hop_reason

All T1 primitives are also re-exported here for convenience.
"""

import re
import sys
from pathlib import Path
from typing import Any
from collections import defaultdict

# ---------------------------------------------------------------------------
# Re-export all Tier 1 primitives
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agents" / "hephaestus" / "src"))
from forge_primitives import *  # noqa: F401,F403
from forge_primitives import (
    confidence_from_agreement,
    track_beliefs,
    sally_anne_test,
    modus_ponens,
    check_transitivity,
    topological_sort,
    counterfactual_intervention,
    dag_traverse,
    temporal_order,
    PRIMITIVE_CATALOG,
)


# ---------------------------------------------------------------------------
# 1. DELIBERATION
# ---------------------------------------------------------------------------

def deliberate(solvers: list, prompt: str, candidates: list[str],
               max_rounds: int = 3) -> list[dict]:
    """Run multiple solvers, re-run on disagreement until consensus.

    Each solver is a callable(prompt, candidates) -> list[dict] where each
    dict has keys 'candidate' and 'score' (0-1).

    Args:
        solvers: list of solver callables
        prompt: the problem statement
        candidates: candidate answers
        max_rounds: maximum deliberation rounds

    Returns:
        List of {'candidate', 'score', 'confidence'} dicts, sorted by score.
    """
    context = prompt
    for _round in range(max_rounds):
        all_scores: dict[str, list[float]] = defaultdict(list)
        for solver in solvers:
            results = solver(context, candidates)
            for r in results:
                all_scores[r["candidate"]].append(r["score"])

        confidence = confidence_from_agreement(
            [s for scores in all_scores.values() for s in scores]
        )
        if confidence > 0.8:
            break
        # Refine context with disagreement info for next round
        disagreements = [c for c, s in all_scores.items() if max(s) - min(s) > 0.3]
        context = f"{prompt}\n[Contested: {', '.join(disagreements)}]"

    output = []
    for cand, scores in all_scores.items():
        avg = sum(scores) / len(scores) if scores else 0.0
        conf = confidence_from_agreement(scores)
        output.append({"candidate": cand, "score": avg, "confidence": conf})
    return sorted(output, key=lambda x: x["score"], reverse=True)


# ---------------------------------------------------------------------------
# 2. PERSPECTIVE SHIFT
# ---------------------------------------------------------------------------

def perspective_shift(prompt: str, viewpoints: list[str]) -> list[dict]:
    """Reframe a scenario from multiple agent viewpoints.

    Extracts entities and their knowledge states by simulating who
    observed what from each viewpoint.

    Args:
        prompt: scenario description
        viewpoints: list of perspective labels (e.g. 'the liar', 'observer')

    Returns:
        List of {'viewpoint', 'believed_facts'} dicts.
    """
    # Extract simple factual sentences from prompt
    sentences = [s.strip() for s in re.split(r'[.!?]', prompt) if s.strip()]
    agents = viewpoints
    # Build observations: assume each viewpoint sees all facts by default
    observations = []
    for agent in agents:
        for fact in sentences:
            # If the fact mentions the agent, they know it; otherwise uncertain
            saw = agent.lower() in fact.lower() or "everyone" in fact.lower()
            observations.append((agent, fact, saw))

    beliefs = track_beliefs(agents, observations)
    return [{"viewpoint": vp, "believed_facts": list(beliefs.get(vp, set()))}
            for vp in viewpoints]


# ---------------------------------------------------------------------------
# 3. SELF-CRITIQUE
# ---------------------------------------------------------------------------

def self_critique(answer: str, prompt: str,
                  parsed_constraints: list) -> tuple[bool, str]:
    """Check if an answer is logically consistent with constraints.

    Each constraint is a (antecedent, consequent) implication or a
    (a, relation, b) transitivity triple.

    Args:
        answer: proposed answer string
        prompt: original problem
        parsed_constraints: list of constraint tuples

    Returns:
        (is_consistent, reason) tuple.
    """
    implications = [c for c in parsed_constraints if len(c) == 2]
    relations = [c for c in parsed_constraints if len(c) >= 2]

    # Check forward-chaining consistency
    facts = {answer}
    derived = modus_ponens(implications, facts)

    # Check for contradictions via transitivity
    closure = check_transitivity([(a, b) for a, b in relations[:50]])
    for node, reachable in closure.items():
        if node in reachable:
            return False, f"Cycle detected involving '{node}'"

    # Check if the answer contradicts any derived fact
    neg_answer = f"not {answer}"
    if neg_answer in derived:
        return False, f"Answer '{answer}' contradicts derived fact '{neg_answer}'"

    return True, "Answer is consistent with all parsed constraints"


# ---------------------------------------------------------------------------
# 4. ANALOGIZE
# ---------------------------------------------------------------------------

def analogize(prompt: str,
              templates: dict[str, Any]) -> tuple[str, float]:
    """Map a prompt to the nearest known problem template by keyword matching.

    Each template key is a name; its value is a callable or descriptor.
    Matching uses structural keywords extracted from the prompt.

    Args:
        prompt: the problem statement
        templates: {template_name: callable_or_descriptor}

    Returns:
        (best_template_name, match_confidence) tuple.
    """
    keyword_sets: dict[str, set[str]] = {
        "constraint_satisfaction": {"constraint", "assign", "satisfy", "domain", "variable"},
        "graph_traversal": {"path", "route", "connect", "node", "edge", "graph", "network"},
        "probability": {"chance", "likely", "probability", "odds", "random", "expect"},
        "temporal": {"before", "after", "when", "time", "order", "sequence", "first", "last"},
        "causal": {"cause", "effect", "because", "leads", "intervention", "if", "then"},
        "belief": {"think", "believe", "know", "sees", "hidden", "perspective"},
        "arithmetic": {"sum", "total", "cost", "price", "count", "number", "many"},
    }
    prompt_words = set(re.findall(r'\w+', prompt.lower()))
    best_name, best_score = "", 0.0

    for tname in templates:
        keywords = keyword_sets.get(tname, set(re.findall(r'\w+', tname.lower())))
        if not keywords:
            continue
        overlap = len(prompt_words & keywords) / len(keywords)
        if overlap > best_score:
            best_score = overlap
            best_name = tname

    return best_name, min(best_score, 1.0)


# ---------------------------------------------------------------------------
# 5. ENSEMBLE VOTE
# ---------------------------------------------------------------------------

def ensemble_vote(solvers: list, prompt: str,
                  candidates: list[str]) -> list[dict]:
    """Weighted majority vote across multiple solvers.

    Each solver is a callable(prompt, candidates) -> list[dict] with
    'candidate' and 'score' keys. Weight = solver's mean confidence.

    Args:
        solvers: list of solver callables
        prompt: the problem statement
        candidates: candidate answers

    Returns:
        List of {'candidate', 'weighted_score', 'agreement'} dicts.
    """
    tally: dict[str, float] = defaultdict(float)
    counts: dict[str, list[float]] = defaultdict(list)

    for solver in solvers:
        results = solver(prompt, candidates)
        scores = [r.get("score", 0.0) for r in results]
        weight = confidence_from_agreement(scores) if scores else 0.5
        for r in results:
            cand = r["candidate"]
            tally[cand] += r["score"] * weight
            counts[cand].append(r["score"])

    output = []
    for cand in candidates:
        agreement = confidence_from_agreement(counts.get(cand, []))
        output.append({
            "candidate": cand,
            "weighted_score": tally.get(cand, 0.0),
            "agreement": agreement,
        })
    return sorted(output, key=lambda x: x["weighted_score"], reverse=True)


# ---------------------------------------------------------------------------
# 6. ERROR CORRECT
# ---------------------------------------------------------------------------

def error_correct(solvers: list, prompt: str, candidates: list[str],
                  min_agreement: int = 2) -> list[dict]:
    """ECC-style reasoning: use min_agreement-of-N majority to filter noise.

    Args:
        solvers: list of solver callables(prompt, candidates) -> list[dict]
        prompt: the problem statement
        candidates: candidate answers
        min_agreement: minimum solvers that must agree for a candidate to pass

    Returns:
        List of {'candidate', 'score', 'n_agree'} dicts for passing candidates.
    """
    votes: dict[str, list[float]] = defaultdict(list)
    for solver in solvers:
        results = solver(prompt, candidates)
        if not results:
            continue
        # Each solver's top pick gets a vote
        top = max(results, key=lambda r: r.get("score", 0.0))
        votes[top["candidate"]].append(top.get("score", 1.0))

    output = []
    for cand, scores in votes.items():
        if len(scores) >= min_agreement:
            output.append({
                "candidate": cand,
                "score": sum(scores) / len(scores),
                "n_agree": len(scores),
            })
    return sorted(output, key=lambda x: x["score"], reverse=True)


# ---------------------------------------------------------------------------
# 7. CAUSAL REASON
# ---------------------------------------------------------------------------

def causal_reason(edges: list[tuple], observations: dict,
                  intervention: tuple = None) -> dict:
    """Higher-level causal reasoning over a DAG.

    Chains dag_traverse, counterfactual_intervention, and topological_sort
    to answer "what if X were different?" questions.

    Args:
        edges: list of (cause, effect) edges
        observations: {node: observed_value} dict
        intervention: optional (node, forced_value) tuple for do-calculus

    Returns:
        Dict with 'order', 'reachable', 'values' keys.
    """
    order = topological_sort(edges) or []
    values = dict(observations)

    if intervention is not None:
        node, forced = intervention
        values = counterfactual_intervention(edges, values, node, forced)
        reachable = dag_traverse(edges, node)
    else:
        reachable = []
        if order:
            reachable = dag_traverse(edges, order[0])

    return {"order": order, "reachable": reachable, "values": values}


# ---------------------------------------------------------------------------
# 8. TEMPORAL REASON
# ---------------------------------------------------------------------------

def temporal_reason(events: list, constraints: list) -> dict:
    """Higher-level temporal reasoning: build timeline, detect conflicts.

    Args:
        events: list of event names
        constraints: list of (event_a, relation, event_b) where relation
                     is 'before', 'after', 'simultaneous', or 'during'

    Returns:
        Dict with 'timeline', 'simultaneous_groups', 'has_conflict' keys.
    """
    # Separate ordering constraints from simultaneity
    ordering = [(a, rel, b) for a, rel, b in constraints
                if rel.lower() in ("before", "after")]
    simultaneous = [(a, b) for a, rel, b in constraints
                    if rel.lower() in ("simultaneous", "during")]

    timeline = temporal_order(ordering)

    # Build simultaneity groups via union-find
    parent: dict[str, str] = {}
    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in simultaneous:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    groups: dict[str, list[str]] = defaultdict(list)
    for e in events:
        groups[find(e)].append(e)
    sim_groups = [g for g in groups.values() if len(g) > 1]

    # Detect conflict: simultaneous events that also have before/after
    has_conflict = False
    for a, b in simultaneous:
        edges = [(x, y) for x, rel, y in ordering if rel.lower() == "before"]
        closure = check_transitivity(edges)
        if b in closure.get(a, set()) or a in closure.get(b, set()):
            has_conflict = True
            break

    return {
        "timeline": timeline,
        "simultaneous_groups": sim_groups,
        "has_conflict": has_conflict,
    }


# ---------------------------------------------------------------------------
# 9. MULTI-HOP REASON
# ---------------------------------------------------------------------------

def multi_hop_reason(premises: list[tuple[str, str]],
                     query: str) -> tuple[str, list[str]]:
    """Chain modus ponens steps to reach a conclusion, tracking derivation.

    Args:
        premises: list of (antecedent, consequent) implication rules
        query: the target fact to derive

    Returns:
        (conclusion, derivation_path) where derivation_path lists each
        step as 'from A derived B'. Returns ('', []) if underivable.
    """
    facts: set[str] = set()
    path: list[str] = []
    # Seed with facts that appear as antecedents with no own antecedent
    all_consequents = {c for _, c in premises}
    all_antecedents = {a for a, _ in premises}
    axioms = all_antecedents - all_consequents
    facts.update(axioms)

    # Iterative forward chaining with path tracking
    changed = True
    while changed:
        changed = False
        for ante, cons in premises:
            if ante in facts and cons not in facts:
                facts.add(cons)
                path.append(f"from '{ante}' derived '{cons}'")
                changed = True
                if cons == query:
                    return query, path

    # Also check transitivity for ordering queries
    closure = check_transitivity(premises)
    for node, reachable in closure.items():
        if query in reachable and node in axioms:
            return query, path + [f"by transitivity: '{node}' reaches '{query}'"]

    if query in facts:
        return query, path
    return "", path


# ---------------------------------------------------------------------------
# Catalog — Tier 2 primitives by category
# ---------------------------------------------------------------------------

PRIMITIVE_CATALOG_T2 = {
    "deliberation": ["deliberate"],
    "perspective": ["perspective_shift"],
    "critique": ["self_critique"],
    "analogy": ["analogize"],
    "ensemble": ["ensemble_vote", "error_correct"],
    "causal": ["causal_reason"],
    "temporal": ["temporal_reason"],
    "multi_hop": ["multi_hop_reason"],
    # Include T1 catalog for full reference
    "t1": PRIMITIVE_CATALOG,
}
