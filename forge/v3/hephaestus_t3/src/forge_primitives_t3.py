"""Forge Primitives Tier 3 -- higher-order reasoning compositions.

These primitives build on T1 and T2 building blocks to provide
sophisticated reasoning patterns: recursive self-consistent solving,
multi-perspective deliberation, abstraction mapping, constraint cascading,
game-tree backward induction, insufficiency detection, and cognitive
bias detection.

Usage in forged tools:
    from forge_primitives_t3 import recursive_solve, bias_detect, constraint_cascade

All T1 and T2 primitives are also re-exported here for convenience.
"""

import re
import sys
from pathlib import Path
from typing import Any, Callable
from collections import defaultdict

# ---------------------------------------------------------------------------
# Re-export all Tier 1 and Tier 2 primitives
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hephaestus_t2" / "src"))
from forge_primitives_t2 import *  # noqa: F401,F403
from forge_primitives_t2 import (
    PRIMITIVE_CATALOG,
    PRIMITIVE_CATALOG_T2,
    confidence_from_agreement,
    information_sufficiency,
    self_critique,
    deliberate,
    solve_sat,
    modus_ponens,
    check_transitivity,
    solve_constraints,
    topological_sort,
)


# ---------------------------------------------------------------------------
# 1. RECURSIVE SOLVE
# ---------------------------------------------------------------------------

def recursive_solve(solver: Callable, prompt: str, candidates: list[str],
                    max_depth: int = 5) -> list[dict]:
    """Apply solver, check self-consistency; re-solve with partial answer if not.

    For problems where the answer depends on itself (e.g., self-referential
    logic, fixed-point equations, Nash equilibria).

    Args:
        solver: callable(prompt, candidates) -> list[dict] with 'candidate', 'score'
        prompt: the problem statement
        candidates: candidate answers
        max_depth: maximum recursion depth

    Returns:
        List of {'candidate', 'score', 'depth', 'stable'} dicts, sorted by score.
    """
    current_prompt = prompt
    prev_top = None

    for depth in range(1, max_depth + 1):
        results = solver(current_prompt, candidates)
        if not results:
            return []

        results_sorted = sorted(results, key=lambda r: r.get("score", 0.0),
                                reverse=True)
        top = results_sorted[0]["candidate"]

        # Check stability: did the top answer change?
        if top == prev_top:
            # Self-consistent -- annotate and return
            return [
                {
                    "candidate": r["candidate"],
                    "score": r.get("score", 0.0),
                    "depth": depth,
                    "stable": r["candidate"] == top,
                }
                for r in results_sorted
            ]

        # Not yet stable -- inject partial answer into prompt
        prev_top = top
        current_prompt = (
            f"{prompt}\n[Partial answer from depth {depth}: {top}. "
            f"Re-evaluate for self-consistency.]"
        )

    # Exhausted depth -- return last results marked unstable
    return [
        {
            "candidate": r["candidate"],
            "score": r.get("score", 0.0),
            "depth": max_depth,
            "stable": False,
        }
        for r in results_sorted
    ]


# ---------------------------------------------------------------------------
# 2. MULTI-PERSPECTIVE DELIBERATE
# ---------------------------------------------------------------------------

def multi_perspective_deliberate(
    prompt: str,
    candidates: list[str],
    perspectives: list[dict],
) -> list[dict]:
    """Evaluate from multiple perspectives, aggregate weighted results.

    Each perspective is {name, belief_transform_fn, weight} where
    belief_transform_fn(prompt) -> transformed_prompt reshapes the problem
    from that perspective's viewpoint.

    Useful for Theory of Mind, deception detection, and multi-stakeholder
    reasoning.

    Args:
        prompt: the problem statement
        candidates: candidate answers
        perspectives: list of {name: str, belief_transform_fn: Callable, weight: float}

    Returns:
        List of {'candidate', 'weighted_score', 'perspective_scores'} dicts.
    """
    tally: dict[str, float] = defaultdict(float)
    per_perspective: dict[str, dict[str, float]] = defaultdict(dict)
    total_weight = sum(p.get("weight", 1.0) for p in perspectives) or 1.0

    for persp in perspectives:
        name = persp["name"]
        transform = persp["belief_transform_fn"]
        weight = persp.get("weight", 1.0)

        transformed = transform(prompt)

        # Score each candidate under this perspective using keyword heuristic
        prompt_words = set(re.findall(r'\w+', transformed.lower()))
        for cand in candidates:
            cand_words = set(re.findall(r'\w+', cand.lower()))
            overlap = len(prompt_words & cand_words)
            # Normalize to 0-1
            score = min(overlap / max(len(cand_words), 1), 1.0)
            tally[cand] += score * weight
            per_perspective[cand][name] = score

    output = []
    for cand in candidates:
        output.append({
            "candidate": cand,
            "weighted_score": round(tally.get(cand, 0.0) / total_weight, 4),
            "perspective_scores": per_perspective.get(cand, {}),
        })
    return sorted(output, key=lambda x: x["weighted_score"], reverse=True)


# ---------------------------------------------------------------------------
# 3. ABSTRACTION MAP
# ---------------------------------------------------------------------------

def abstraction_map(source_problem: dict, target_problem: dict,
                    mapping: dict) -> dict:
    """Map structural elements from a solved problem to an unsolved one.

    Takes a source problem (with known solution) and a target problem,
    plus a mapping of structural roles, and returns the mapped solution.

    Args:
        source_problem: {description: str, elements: dict, solution: str}
        target_problem: {description: str, elements: dict}
        mapping: {source_element_key: target_element_key, ...}

    Returns:
        Dict with 'mapped_solution', 'unmapped_elements', 'confidence'.
    """
    source_elements = source_problem.get("elements", {})
    target_elements = target_problem.get("elements", {})
    solution = source_problem.get("solution", "")

    # Apply mapping to solution string
    mapped_solution = solution
    unmapped = []
    for src_key, tgt_key in mapping.items():
        src_val = str(source_elements.get(src_key, src_key))
        tgt_val = str(target_elements.get(tgt_key, tgt_key))
        if src_val in mapped_solution:
            mapped_solution = mapped_solution.replace(src_val, tgt_val)
        else:
            unmapped.append(src_key)

    # Check for source elements not covered by mapping
    for key in source_elements:
        if key not in mapping:
            unmapped.append(key)

    coverage = (len(mapping) - len(unmapped)) / max(len(source_elements), 1)
    confidence = max(0.0, min(1.0, coverage))

    return {
        "mapped_solution": mapped_solution,
        "unmapped_elements": unmapped,
        "confidence": round(confidence, 3),
    }


# ---------------------------------------------------------------------------
# 4. CONSTRAINT CASCADE
# ---------------------------------------------------------------------------

def constraint_cascade(constraints: list, initial_knowns: dict) -> dict:
    """Iteratively apply constraints until fixed-point (no new deductions).

    For cascading inference problems like Einstein riddles where each
    deduction enables further deductions.

    Each constraint is a callable(knowns: dict) -> dict returning any
    new facts deduced, or a (key, relation, value) tuple for simple
    equality propagation.

    Args:
        constraints: list of callables or (key, relation, value) tuples
        initial_knowns: starting known facts {key: value}

    Returns:
        Dict with 'knowns' (final state), 'steps' (deduction trace),
        'converged' (bool).
    """
    knowns = dict(initial_knowns)
    steps: list[str] = []
    max_iterations = 100

    for iteration in range(max_iterations):
        new_facts: dict = {}

        for constraint in constraints:
            if callable(constraint):
                deduced = constraint(knowns)
                if isinstance(deduced, dict):
                    for k, v in deduced.items():
                        if k not in knowns:
                            new_facts[k] = v
            elif isinstance(constraint, (list, tuple)) and len(constraint) == 3:
                key, rel, value = constraint
                if rel == "==" and key not in knowns:
                    # Check if value refers to a known
                    if value in knowns:
                        new_facts[key] = knowns[value]
                    else:
                        new_facts[key] = value
                elif rel == "!=" and key in knowns and knowns[key] == value:
                    steps.append(
                        f"Contradiction: {key}={knowns[key]} but {key}!={value}"
                    )

        if not new_facts:
            # Fixed-point reached
            return {"knowns": knowns, "steps": steps, "converged": True}

        for k, v in new_facts.items():
            knowns[k] = v
            steps.append(f"Step {iteration+1}: deduced {k} = {v}")

    return {"knowns": knowns, "steps": steps, "converged": False}


# ---------------------------------------------------------------------------
# 5. GAME TREE SOLVE
# ---------------------------------------------------------------------------

def game_tree_solve(tree: dict, rationality: dict) -> str:
    """Backward induction on a game tree with heterogeneous player types.

    Args:
        tree: nested dict representing the game tree. Each node is either:
              - A leaf: {"payoff": {player: value, ...}}
              - A decision: {"player": str, "choices": {action: subtree, ...}}
        rationality: {player: "rational" | "greedy"} mapping.
                     "rational" = backward induction (minimax-style).
                     "greedy" = pick highest immediate payoff if leaf,
                                else pick highest expected payoff.

    Returns:
        The action label chosen at the root node.
    """
    def _evaluate(node: dict) -> dict:
        """Return payoff dict for the subtree."""
        if "payoff" in node:
            return node["payoff"]

        player = node["player"]
        choices = node.get("choices", {})
        if not choices:
            return {}

        # Evaluate all children
        child_payoffs = {}
        for action, subtree in choices.items():
            child_payoffs[action] = _evaluate(subtree)

        player_type = rationality.get(player, "rational")

        # Pick action that maximizes this player's payoff
        best_action = None
        best_value = float("-inf")

        for action, payoffs in child_payoffs.items():
            value = payoffs.get(player, 0)
            if value > best_value:
                best_value = value
                best_action = action

        return child_payoffs.get(best_action, {})

    # Find the root action (not just the payoff)
    if "choices" not in tree:
        return ""

    player = tree["player"]
    player_type = rationality.get(player, "rational")
    best_action = None
    best_value = float("-inf")

    for action, subtree in tree["choices"].items():
        payoffs = _evaluate(subtree)
        value = payoffs.get(player, 0)
        if value > best_value:
            best_value = value
            best_action = action

    return best_action or ""


# ---------------------------------------------------------------------------
# 6. DETECT INSUFFICIENCY
# ---------------------------------------------------------------------------

def detect_insufficiency(prompt: str, parsed_vars: list[str],
                         parsed_constraints: list) -> tuple[bool, str]:
    """Check if a problem has enough information to solve.

    Uses information_sufficiency from T1 primitives plus structural
    analysis of constraints vs unknowns.

    Args:
        prompt: the problem statement
        parsed_vars: list of unknown variable names
        parsed_constraints: list of constraints (tuples or callables)

    Returns:
        (is_solvable, missing_info) tuple.
    """
    n_unknowns = len(parsed_vars)
    n_constraints = len(parsed_constraints)

    # Use T1's information_sufficiency check
    sufficiency = information_sufficiency(n_unknowns, n_constraints)

    if sufficiency == "underdetermined":
        deficit = n_unknowns - n_constraints
        return (
            False,
            f"Underdetermined: {n_unknowns} unknowns but only "
            f"{n_constraints} constraints (need {deficit} more).",
        )

    if sufficiency == "overdetermined":
        # Could still be solvable, but may have contradictions
        return (
            True,
            f"Overdetermined: {n_constraints} constraints for "
            f"{n_unknowns} unknowns. Check for contradictions.",
        )

    # Check for unconstrained variables
    constrained_vars = set()
    for c in parsed_constraints:
        if isinstance(c, (list, tuple)):
            for element in c:
                if isinstance(element, str):
                    constrained_vars.add(element)

    unconstrained = [v for v in parsed_vars if v not in constrained_vars]
    if unconstrained:
        return (
            False,
            f"Variables not referenced by any constraint: "
            f"{', '.join(unconstrained)}",
        )

    return (True, "Problem appears fully determined.")


# ---------------------------------------------------------------------------
# 7. BIAS DETECT
# ---------------------------------------------------------------------------

# Known cognitive bias patterns
_BIAS_PATTERNS: dict[str, dict[str, Any]] = {
    "base_rate_neglect": {
        "triggers": [
            r"\d+%\s+of\s+(?:people|population|cases)",
            r"test\s+(?:is\s+)?\d+%\s+accurate",
            r"prevalence.*rare",
            r"false\s+positive",
        ],
        "description": (
            "Problem provides base rate information that is typically "
            "ignored in favor of case-specific evidence."
        ),
    },
    "conjunction_fallacy": {
        "triggers": [
            r"which\s+is\s+more\s+(?:likely|probable)",
            r"(?:and|also)\s+(?:is\s+)?(?:a\s+)?(?:feminist|activist|liberal)",
            r"rank\s+(?:the\s+)?(?:following\s+)?(?:statements|options)\s+by\s+"
            r"(?:probability|likelihood)",
        ],
        "description": (
            "Problem tempts the conjunction fallacy: judging A-and-B as "
            "more probable than A alone due to representativeness."
        ),
    },
    "anchoring": {
        "triggers": [
            r"(?:starts?\s+at|initial(?:ly)?|original(?:ly)?)\s+\$?\d+",
            r"(?:was|were)\s+\$?\d+.*(?:now|currently|today)",
            r"(?:increased|decreased|changed)\s+by\s+\d+%",
        ],
        "description": (
            "Problem contains an anchor value that may bias numerical "
            "estimates toward the anchor."
        ),
    },
    "framing_effect": {
        "triggers": [
            r"(?:save|rescue|survive)\s+\d+",
            r"(?:lose|die|kill)\s+\d+",
            r"(?:90%\s+(?:chance|probability)\s+of\s+(?:success|survival))"
            r"|(?:10%\s+(?:chance|probability)\s+of\s+(?:failure|death))",
            r"glass\s+(?:half\s+)?(?:full|empty)",
        ],
        "description": (
            "Problem frames identical outcomes differently (gain vs loss) "
            "which typically shifts risk preferences."
        ),
    },
}


def bias_detect(prompt: str, candidates: list[str]) -> tuple[str, float]:
    """Detect if the problem framing triggers a known cognitive bias.

    Scans the prompt for linguistic patterns associated with common
    cognitive biases.

    Args:
        prompt: the problem statement
        candidates: candidate answers (used for conjunction check)

    Returns:
        (bias_name, confidence) tuple. bias_name is "" if no bias detected.
    """
    best_bias = ""
    best_confidence = 0.0
    combined = prompt + " " + " ".join(candidates)

    for bias_name, spec in _BIAS_PATTERNS.items():
        match_count = 0
        total_patterns = len(spec["triggers"])

        for pattern in spec["triggers"]:
            if re.search(pattern, combined, re.IGNORECASE):
                match_count += 1

        if match_count > 0:
            confidence = match_count / total_patterns
            # Boost if multiple patterns hit
            if match_count >= 2:
                confidence = min(confidence * 1.3, 1.0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_bias = bias_name

    return (best_bias, round(best_confidence, 3))


# ---------------------------------------------------------------------------
# Catalog -- Tier 3 primitives by category
# ---------------------------------------------------------------------------

PRIMITIVE_CATALOG_T3 = {
    "recursive": ["recursive_solve"],
    "perspective": ["multi_perspective_deliberate"],
    "analogy": ["abstraction_map"],
    "constraint": ["constraint_cascade"],
    "game_theory": ["game_tree_solve"],
    "meta": ["detect_insufficiency", "bias_detect"],
    # Include T2 catalog (which already includes T1)
    "t2": PRIMITIVE_CATALOG_T2,
    "t1": PRIMITIVE_CATALOG,
}
