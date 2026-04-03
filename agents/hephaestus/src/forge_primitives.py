"""Forge Primitives — composable reasoning building blocks.

Small, single-purpose functions that forged tools can import and recombine.
The novelty in a forged tool comes from HOW these blocks are wired together,
not from the blocks themselves.

Usage in forged tools:
    from forge_primitives import bayesian_update, solve_sat, dag_traverse

All primitives use only numpy, sympy, networkx, scipy, and stdlib.
Each function does ONE thing, takes simple inputs, returns simple outputs.
"""

import re
import math
import itertools
from typing import Any
from collections import defaultdict

import numpy as np

# ---------------------------------------------------------------------------
# 1. LOGIC PRIMITIVES
# ---------------------------------------------------------------------------

def solve_sat(clauses: list[list[int]], n_vars: int) -> dict[int, bool] | None:
    """Brute-force SAT solver for small instances (up to ~20 variables).

    Args:
        clauses: CNF as list of lists of signed ints (e.g. [[1, -2], [2, 3]])
        n_vars: number of variables (1-indexed)

    Returns:
        Assignment dict {var: True/False} or None if unsatisfiable.
    """
    for bits in range(2 ** n_vars):
        assignment = {v: bool(bits & (1 << (v - 1))) for v in range(1, n_vars + 1)}
        if all(
            any((assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)])
                for lit in clause)
            for clause in clauses
        ):
            return assignment
    return None


def modus_ponens(premises: list[tuple[str, str]], facts: set[str]) -> set[str]:
    """Forward-chain modus ponens over implication rules.

    Args:
        premises: list of (antecedent, consequent) implication pairs
        facts: initial known facts

    Returns:
        Closure of all derivable facts.
    """
    facts = set(facts)
    changed = True
    while changed:
        changed = False
        for ante, cons in premises:
            if ante in facts and cons not in facts:
                facts.add(cons)
                changed = True
    return facts


def check_transitivity(relations: list[tuple[str, str]]) -> dict[str, set[str]]:
    """Compute transitive closure of a binary relation.

    Args:
        relations: list of (a, b) meaning a < b or a -> b

    Returns:
        Dict mapping each element to the set of all elements it transitively reaches.
    """
    # Build adjacency
    graph: dict[str, set[str]] = defaultdict(set)
    for a, b in relations:
        graph[a].add(b)

    # Warshall-style closure
    nodes = set()
    for a, b in relations:
        nodes.add(a)
        nodes.add(b)

    closure: dict[str, set[str]] = {n: set(graph[n]) for n in nodes}
    for k in nodes:
        for i in nodes:
            if k in closure.get(i, set()):
                closure.setdefault(i, set()).update(closure.get(k, set()))

    return closure


def negate(statement: str) -> str:
    """Simple logical negation of a natural-language statement.

    Returns the negation string. Handles 'not' insertion/removal.
    """
    s = statement.strip()
    if s.lower().startswith("not "):
        return s[4:]
    if " not " in s.lower():
        return re.sub(r'\bnot\b\s*', '', s, count=1, flags=re.IGNORECASE)
    return f"not {s}"


# ---------------------------------------------------------------------------
# 2. PROBABILISTIC PRIMITIVES
# ---------------------------------------------------------------------------

def bayesian_update(prior: float, likelihood: float,
                    false_positive: float = 0.0) -> float:
    """Single-step Bayes update. P(H|E) = P(E|H)*P(H) / P(E).

    Args:
        prior: P(H)
        likelihood: P(E|H)
        false_positive: P(E|~H)

    Returns:
        Posterior P(H|E), clamped to [0, 1].
    """
    p_e = likelihood * prior + false_positive * (1 - prior)
    if p_e == 0:
        return 0.0
    return max(0.0, min(1.0, (likelihood * prior) / p_e))


def expected_value(outcomes: list[tuple[float, float]]) -> float:
    """Compute expected value from (probability, value) pairs.

    Args:
        outcomes: list of (probability, value) tuples

    Returns:
        Sum of p * v for all outcomes.
    """
    return sum(p * v for p, v in outcomes)


def entropy(probs: list[float]) -> float:
    """Shannon entropy of a discrete distribution.

    Args:
        probs: list of probabilities (should sum to ~1)

    Returns:
        Entropy in bits.
    """
    return -sum(p * math.log2(p) for p in probs if p > 0)


def coin_flip_independence(n_flips: int, target_heads: int) -> float:
    """P(exactly k heads in n fair coin flips). Binomial coefficient.

    Args:
        n_flips: number of flips
        target_heads: target number of heads

    Returns:
        Probability as float.
    """
    return math.comb(n_flips, target_heads) / (2 ** n_flips)


# ---------------------------------------------------------------------------
# 3. GRAPH / CAUSAL PRIMITIVES
# ---------------------------------------------------------------------------

def dag_traverse(edges: list[tuple[str, str]], start: str) -> list[str]:
    """BFS traversal of a directed graph from a start node.

    Args:
        edges: list of (source, target) directed edges
        start: starting node

    Returns:
        List of reachable nodes in BFS order.
    """
    adj: dict[str, list[str]] = defaultdict(list)
    for s, t in edges:
        adj[s].append(t)

    visited = []
    queue = [start]
    seen = {start}
    while queue:
        node = queue.pop(0)
        visited.append(node)
        for neighbor in adj[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return visited


def topological_sort(edges: list[tuple[str, str]]) -> list[str] | None:
    """Kahn's algorithm for topological sort of a DAG.

    Args:
        edges: list of (source, target) directed edges

    Returns:
        Topologically sorted node list, or None if cycle detected.
    """
    adj: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = defaultdict(int)
    nodes: set[str] = set()

    for s, t in edges:
        adj[s].append(t)
        in_degree[t] = in_degree.get(t, 0) + 1
        in_degree.setdefault(s, 0)
        nodes.update([s, t])

    queue = [n for n in nodes if in_degree.get(n, 0) == 0]
    result = []
    while queue:
        queue.sort()  # deterministic
        node = queue.pop(0)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == len(nodes) else None


def counterfactual_intervention(edges: list[tuple[str, str]],
                                values: dict[str, float],
                                intervene_node: str,
                                intervene_value: float) -> dict[str, float]:
    """do-calculus: force a node to a value, propagate downstream.

    Cuts all incoming edges to intervene_node, sets its value,
    then propagates to descendants via topological order.
    Each child = mean of parent values (simple additive model).

    Args:
        edges: causal DAG edges
        values: current node values
        intervene_node: node to intervene on
        intervene_value: forced value

    Returns:
        Updated values dict after intervention.
    """
    # Cut incoming edges to intervention target
    cut_edges = [(s, t) for s, t in edges if t != intervene_node]

    result = dict(values)
    result[intervene_node] = intervene_value

    order = topological_sort(cut_edges)
    if order is None:
        return result

    # Build parent map from cut graph
    parents: dict[str, list[str]] = defaultdict(list)
    for s, t in cut_edges:
        parents[t].append(s)

    for node in order:
        if node == intervene_node:
            continue
        if parents[node]:
            result[node] = sum(result.get(p, 0) for p in parents[node]) / len(parents[node])

    return result


# ---------------------------------------------------------------------------
# 4. CONSTRAINT PRIMITIVES
# ---------------------------------------------------------------------------

def solve_constraints(variables: list[str], domains: dict[str, list],
                      constraints: list[tuple[list[str], callable]]) -> dict | None:
    """Backtracking constraint solver for small finite-domain problems.

    Args:
        variables: list of variable names to assign
        domains: {var: [possible_values]}
        constraints: list of (involved_vars, check_fn) where check_fn(**assigned) -> bool

    Returns:
        First satisfying assignment dict, or None.
    """
    def backtrack(assignment: dict, idx: int) -> dict | None:
        if idx == len(variables):
            return dict(assignment)
        var = variables[idx]
        for val in domains.get(var, []):
            assignment[var] = val
            # Check only constraints whose variables are all assigned
            ok = True
            for c_vars, c_fn in constraints:
                if all(v in assignment for v in c_vars):
                    try:
                        if not c_fn(**{v: assignment[v] for v in c_vars}):
                            ok = False
                            break
                    except Exception:
                        ok = False
                        break
            if ok:
                result = backtrack(assignment, idx + 1)
                if result is not None:
                    return result
            del assignment[var]
        return None

    return backtrack({}, 0)


def pigeonhole_check(items: int, containers: int) -> bool:
    """Pigeonhole principle: are there more items than containers?

    Returns True if at least one container must hold >1 item.
    """
    return items > containers


def fencepost_count(n_segments: int, include_both_ends: bool = True) -> int:
    """Fencepost counting: posts for n segments.

    Args:
        n_segments: number of segments/intervals
        include_both_ends: if True, returns n+1; if False, n-1

    Returns:
        Number of posts/points.
    """
    return n_segments + 1 if include_both_ends else n_segments - 1


# ---------------------------------------------------------------------------
# 5. ARITHMETIC / ALGEBRAIC PRIMITIVES
# ---------------------------------------------------------------------------

def bat_and_ball(total: float, difference: float) -> tuple[float, float]:
    """Classic bat-and-ball: X + Y = total, X - Y = difference.

    Returns (X, Y) — the larger and smaller items.
    """
    x = (total + difference) / 2
    y = total - x
    return (x, y)


def modular_arithmetic(a: int, b: int, mod: int) -> int:
    """(a + b) mod m, handling negative values correctly."""
    return (a + b) % mod


def all_but_n(total: int, n: int) -> int:
    """'All but N of T' = T - N."""
    return total - n


def solve_linear_system(A: list[list[float]], b: list[float]) -> list[float] | None:
    """Solve Ax = b for small linear systems.

    Args:
        A: coefficient matrix (list of rows)
        b: right-hand side vector

    Returns:
        Solution vector or None if singular.
    """
    try:
        A_arr = np.array(A, dtype=float)
        b_arr = np.array(b, dtype=float)
        return np.linalg.solve(A_arr, b_arr).tolist()
    except np.linalg.LinAlgError:
        return None


# ---------------------------------------------------------------------------
# 6. TEMPORAL PRIMITIVES
# ---------------------------------------------------------------------------

def temporal_order(events: list[tuple[str, str, str]]) -> list[str]:
    """Order events from before/after relations.

    Args:
        events: list of (event_a, relation, event_b) where relation is
                'before' or 'after'

    Returns:
        Events in chronological order (topological sort of temporal DAG).
    """
    edges = []
    for a, rel, b in events:
        rel_lower = rel.strip().lower()
        if rel_lower == "before":
            edges.append((a, b))
        elif rel_lower == "after":
            edges.append((b, a))
    result = topological_sort(edges)
    return result if result is not None else []


def direction_composition(directions: list[str]) -> str:
    """Compose compass directions into net direction.

    Args:
        directions: list of 'north', 'south', 'east', 'west'

    Returns:
        Net direction as string (e.g. 'north-east', 'south', 'origin').
    """
    dx, dy = 0, 0
    mapping = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}
    for d in directions:
        ddx, ddy = mapping.get(d.strip().lower(), (0, 0))
        dx += ddx
        dy += ddy

    parts = []
    if dy > 0:
        parts.append("north")
    elif dy < 0:
        parts.append("south")
    if dx > 0:
        parts.append("east")
    elif dx < 0:
        parts.append("west")

    return "-".join(parts) if parts else "origin"


# ---------------------------------------------------------------------------
# 7. BELIEF TRACKING PRIMITIVES
# ---------------------------------------------------------------------------

def track_beliefs(agents: list[str],
                  observations: list[tuple[str, str, bool]]) -> dict[str, set[str]]:
    """Track which agents believe which facts (simple ToM).

    Args:
        agents: list of agent names
        observations: list of (agent, fact, saw_it) — did the agent observe this fact?

    Returns:
        Dict mapping each agent to the set of facts they believe are true.
    """
    beliefs: dict[str, set[str]] = {a: set() for a in agents}
    for agent, fact, saw_it in observations:
        if agent in beliefs:
            if saw_it:
                beliefs[agent].add(fact)
            else:
                beliefs[agent].discard(fact)
    return beliefs


def sally_anne_test(who_moved: str, who_saw_move: set[str],
                    original_location: str,
                    new_location: str) -> dict[str, str]:
    """Sally-Anne false belief: where does each agent think the object is?

    Args:
        who_moved: agent who moved the object
        who_saw_move: set of agents who witnessed the move
        original_location: where the object was
        new_location: where it was moved to

    Returns:
        Dict mapping agent -> believed location.
    """
    # Everyone starts believing original location
    # Only those who saw the move update to new location
    beliefs = {}
    all_agents = who_saw_move | {who_moved}
    for agent in all_agents:
        if agent in who_saw_move or agent == who_moved:
            beliefs[agent] = new_location
        else:
            beliefs[agent] = original_location
    return beliefs


# ---------------------------------------------------------------------------
# 8. META / CALIBRATION PRIMITIVES
# ---------------------------------------------------------------------------

def confidence_from_agreement(scores: list[float]) -> float:
    """Confidence = 1 - normalized variance of multiple scorer outputs.

    High agreement among scorers -> high confidence.

    Args:
        scores: list of 0-1 scores from different methods

    Returns:
        Confidence 0-1 (1 = perfect agreement).
    """
    if not scores:
        return 0.0
    if len(scores) == 1:
        return scores[0]
    var = np.var(scores)
    # Max variance for [0,1] scores is 0.25
    return float(max(0.0, 1.0 - 4 * var))


def information_sufficiency(n_unknowns: int, n_constraints: int) -> str:
    """Check if a system is determined, underdetermined, or overconstrained.

    Args:
        n_unknowns: number of free variables
        n_constraints: number of independent constraints

    Returns:
        'determined', 'underdetermined', or 'overconstrained'
    """
    if n_constraints == n_unknowns:
        return "determined"
    elif n_constraints < n_unknowns:
        return "underdetermined"
    else:
        return "overconstrained"


def parity_check(numbers: list[int]) -> str:
    """Check parity of sum of integers.

    Returns 'even' or 'odd'.
    """
    return "even" if sum(numbers) % 2 == 0 else "odd"


# ---------------------------------------------------------------------------
# Catalog — for prompt introspection
# ---------------------------------------------------------------------------

PRIMITIVE_CATALOG = {
    "logic": ["solve_sat", "modus_ponens", "check_transitivity", "negate"],
    "probability": ["bayesian_update", "expected_value", "entropy", "coin_flip_independence"],
    "graph_causal": ["dag_traverse", "topological_sort", "counterfactual_intervention"],
    "constraints": ["solve_constraints", "pigeonhole_check", "fencepost_count"],
    "arithmetic": ["bat_and_ball", "modular_arithmetic", "all_but_n", "solve_linear_system"],
    "temporal": ["temporal_order", "direction_composition"],
    "belief_tracking": ["track_beliefs", "sally_anne_test"],
    "meta": ["confidence_from_agreement", "information_sufficiency", "parity_check"],
}
