"""blackboard_prototype.py — test ChatGPT's representational critique.

Hypothesis (from external review 2026-05-24): Apollo's primitives are
"answer-producing heuristics" wired together at the OUTPUT level. That
representation makes composition semantically ill-defined — e.g., wiring
fencepost_count's int output into bayesian_update's probability input.
The dominant gen-3551 recipe is type-broken from the start.

ChatGPT's proposed alternative: evolve organisms over a SHARED TYPED
STATE (blackboard). Each step reads typed slots and writes typed slots.
Compositions become pipelines of state transformations, not output->input
wiring.

This prototype tests whether the representation matters by hand-writing
three small blackboard compositions and comparing them to:
  (a) Apollo's gen-3551 elite (the dominant Goodhart recipe)
  (b) the best single primitive on the same tasks
  (c) NCD baseline

If hand-written blackboard compositions beat (a), (b), and (c) by a
meaningful margin on Apollo's actual trap battery, the representation
matters and Branch C should be on the new genome shape.

Usage:
    python blackboard_prototype.py [n_per_category=3]
"""
import sys
import re
import math
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src"))

# ── Blackboard state ───────────────────────────────────────────────────


@dataclass
class BlackboardState:
    """Typed shared state. Each primitive reads/writes named slots.

    Slots are explicit semantic types — not raw Python types. The
    distinction is the entire point of the experiment.
    """
    # Input
    problem_text: str = ""
    candidates: list[str] = field(default_factory=list)

    # Parsed entities (filled by parsing steps)
    numbers: list[float] = field(default_factory=list)        # parsed numeric values
    names: list[str] = field(default_factory=list)            # parsed proper names
    relations: list[tuple[str, str]] = field(default_factory=list)  # (a, b) means a > b in some ordering
    question_target: str = ""                                 # what the question asks for

    # Derived
    transitive_closure: dict[str, set[str]] = field(default_factory=dict)
    ordered: list[str] = field(default_factory=list)          # entities in order
    max_value: Optional[float] = None
    max_entity: str = ""

    # Output
    candidate_scores: list[float] = field(default_factory=list)
    selected_answer: str = ""


# ── Blackboard-aware primitive wrappers ────────────────────────────────


def parse_numbers(state: BlackboardState) -> BlackboardState:
    """Read: problem_text. Write: numbers."""
    state.numbers = [float(m) for m in re.findall(r'-?\d+(?:\.\d+)?', state.problem_text)]
    return state


def parse_names_and_relations(state: BlackboardState) -> BlackboardState:
    """Read: problem_text. Write: names, relations (a > b form).

    Matches patterns like "X is taller than Y" or "X is greater than Y"
    or "X is bigger/larger than Y".
    """
    text = state.problem_text
    # Match "X is [taller/bigger/larger/greater/...] than Y"
    pattern = r'(\b[A-Z][a-z]+)\s+is\s+(?:taller|bigger|larger|greater|older|faster|heavier|smarter|stronger|richer)\s+than\s+(\b[A-Z][a-z]+)'
    matches = re.findall(pattern, text)
    names = set()
    relations = []
    for a, b in matches:
        names.add(a); names.add(b)
        relations.append((a, b))  # a > b
    state.names = sorted(names)
    state.relations = relations
    return state


def parse_question_target(state: BlackboardState) -> BlackboardState:
    """Read: problem_text. Write: question_target (e.g., 'tallest', 'larger')."""
    text = state.problem_text.lower()
    for keyword in ('tallest', 'shortest', 'biggest', 'smallest', 'largest',
                    'oldest', 'youngest', 'fastest', 'slowest', 'richest', 'poorest',
                    'larger', 'smaller', 'greater', 'less'):
        if keyword in text:
            state.question_target = keyword
            return state
    state.question_target = ''
    return state


def transitive_close(state: BlackboardState) -> BlackboardState:
    """Read: relations. Write: transitive_closure, ordered, max_entity.

    Wraps the Frame H primitive check_transitivity (more or less).
    """
    graph: dict[str, set[str]] = {n: set() for n in state.names}
    for a, b in state.relations:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set())
    # Floyd-Warshall-ish closure
    changed = True
    while changed:
        changed = False
        for n in list(graph.keys()):
            for m in list(graph[n]):
                for p in graph.get(m, set()):
                    if p not in graph[n]:
                        graph[n].add(p)
                        changed = True
    state.transitive_closure = graph
    # The "max" entity is the one that dominates the most others
    if graph:
        ranked = sorted(graph.items(), key=lambda kv: -len(kv[1]))
        state.ordered = [n for n, _ in ranked]
        state.max_entity = ranked[0][0] if ranked[0][1] else ''  # only if has reach
    return state


def numeric_argmax(state: BlackboardState) -> BlackboardState:
    """Read: numbers. Write: max_value."""
    state.max_value = max(state.numbers) if state.numbers else None
    return state


def score_candidates_by_max_entity(state: BlackboardState) -> BlackboardState:
    """Read: candidates, max_entity. Write: candidate_scores, selected_answer."""
    scores = []
    target = state.max_entity
    for c in state.candidates:
        if not target:
            scores.append(0.0)
        elif c == target or c.lower() == target.lower():
            scores.append(1.0)
        elif target in c or c in target:
            scores.append(0.5)
        else:
            scores.append(0.0)
    state.candidate_scores = scores
    if scores:
        idx = max(range(len(scores)), key=lambda i: scores[i])
        state.selected_answer = state.candidates[idx]
    return state


def score_candidates_by_max_value(state: BlackboardState) -> BlackboardState:
    """Read: candidates, max_value, question_target. Write: candidate_scores, selected_answer."""
    scores = []
    if state.max_value is None or not state.numbers:
        state.candidate_scores = [0.0] * len(state.candidates)
        state.selected_answer = state.candidates[0] if state.candidates else ''
        return state
    # If question is "larger / greater / bigger / largest" pick max; else min
    is_larger_question = any(k in state.question_target for k in ('larg', 'great', 'bigg', 'tall'))
    target_val = max(state.numbers) if is_larger_question else min(state.numbers)
    for c in state.candidates:
        # Try to parse candidate as a number
        m = re.search(r'-?\d+(?:\.\d+)?', c)
        if m:
            cv = float(m.group(0))
            if math.isclose(cv, target_val, abs_tol=1e-6):
                scores.append(1.0)
            else:
                scores.append(0.0)
        else:
            # Yes/No question — if max IS the first or second number mentioned, decide
            scores.append(0.0)
    if not any(scores) and state.candidates and state.candidates[0] in ('Yes', 'No'):
        # Yes/No comparison: extract two numbers from prompt, check first > second
        if len(state.numbers) >= 2:
            answer_is_yes = state.numbers[0] > state.numbers[1]
            for c in state.candidates:
                scores_idx = 1.0 if (c == 'Yes' and answer_is_yes) or (c == 'No' and not answer_is_yes) else 0.0
                scores[state.candidates.index(c)] = scores_idx
    state.candidate_scores = scores
    if scores:
        idx = max(range(len(scores)), key=lambda i: scores[i])
        state.selected_answer = state.candidates[idx]
    return state


# ── Hand-written compositions (pipelines over the blackboard) ──────────


def composition_numeric(state: BlackboardState) -> BlackboardState:
    """parse_numbers -> parse_question_target -> numeric_argmax -> score_candidates_by_max_value"""
    state = parse_numbers(state)
    state = parse_question_target(state)
    state = numeric_argmax(state)
    state = score_candidates_by_max_value(state)
    return state


def composition_transitivity(state: BlackboardState) -> BlackboardState:
    """parse_names_and_relations -> transitive_close -> score_candidates_by_max_entity"""
    state = parse_names_and_relations(state)
    state = transitive_close(state)
    state = score_candidates_by_max_entity(state)
    return state


def composition_dispatch(state: BlackboardState) -> BlackboardState:
    """Try transitivity if relations are present; else try numeric.

    This is the "meta-composition" — the blackboard organism that
    decides which pipeline to run based on what it parses.
    """
    s2 = parse_names_and_relations(BlackboardState(
        problem_text=state.problem_text, candidates=state.candidates))
    if s2.relations:
        return composition_transitivity(state)
    return composition_numeric(state)


# ── Single-primitive baseline (for comparison) ─────────────────────────


def single_primitive_random(state: BlackboardState) -> BlackboardState:
    """Pick first candidate (deterministic baseline)."""
    state.selected_answer = state.candidates[0] if state.candidates else ''
    return state


def single_primitive_longest_candidate(state: BlackboardState) -> BlackboardState:
    """Pick the longest candidate string (a common dumb heuristic)."""
    if not state.candidates:
        state.selected_answer = ''
        return state
    state.selected_answer = max(state.candidates, key=len)
    return state


def single_primitive_numeric_only(state: BlackboardState) -> BlackboardState:
    """Just parse numbers and pick max — no question parsing, no transitivity."""
    state = parse_numbers(state)
    state = numeric_argmax(state)
    if state.max_value is None or not state.candidates:
        state.selected_answer = state.candidates[0] if state.candidates else ''
        return state
    for c in state.candidates:
        m = re.search(r'-?\d+(?:\.\d+)?', c)
        if m and math.isclose(float(m.group(0)), state.max_value, abs_tol=1e-6):
            state.selected_answer = c
            return state
    state.selected_answer = state.candidates[0]
    return state


# ── Evaluation harness ─────────────────────────────────────────────────


def evaluate(composition_fn, tasks: list[dict]) -> dict:
    """Run a composition on each task; return accuracy + per-category breakdown."""
    n_correct = 0
    by_cat: dict[str, list[int]] = {}
    for t in tasks:
        state = BlackboardState(problem_text=t['prompt'], candidates=t['candidates'])
        try:
            out = composition_fn(state)
            correct = (out.selected_answer == t['correct'])
        except Exception:
            correct = False
        cat = t.get('category', 'unknown')
        by_cat.setdefault(cat, []).append(1 if correct else 0)
        if correct:
            n_correct += 1
    return {
        'accuracy': n_correct / max(len(tasks), 1),
        'n_correct': n_correct,
        'n_tasks': len(tasks),
        'by_category': {c: f"{sum(v)}/{len(v)}" for c, v in by_cat.items()},
    }


def main():
    from trap_generator import generate_trap_battery
    n_per = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    tasks = generate_trap_battery(n_per_category=n_per, seed=42)
    print(f"Loaded {len(tasks)} trap-battery tasks ({n_per} per category)")
    print()

    candidates = [
        ('B1 baseline: first candidate', single_primitive_random),
        ('B2 baseline: longest candidate', single_primitive_longest_candidate),
        ('B3 baseline: numbers-only argmax', single_primitive_numeric_only),
        ('C1 blackboard: numeric pipeline', composition_numeric),
        ('C2 blackboard: transitivity pipeline', composition_transitivity),
        ('C3 blackboard: meta-dispatch', composition_dispatch),
    ]

    print(f"{'composition':45s} {'accuracy':>10s}  {'n':>5s}")
    print("-" * 75)
    results = []
    for name, fn in candidates:
        r = evaluate(fn, tasks)
        results.append((name, r))
        print(f"{name:45s} {r['accuracy']:>10.3f}  {r['n_correct']:>3d}/{r['n_tasks']:<3d}")

    # Show per-category breakdown for the best blackboard composition
    print()
    print("=" * 75)
    print("Per-category breakdown for meta-dispatch composition:")
    print("=" * 75)
    meta_r = results[-1][1]
    for cat, ratio in sorted(meta_r['by_category'].items()):
        print(f"  {cat:40s} {ratio}")

    # Verdict
    print()
    print("=" * 75)
    best_baseline = max(r['accuracy'] for _, r in results[:3])
    best_blackboard = max(r['accuracy'] for _, r in results[3:])
    lift = best_blackboard - best_baseline
    print(f"Best single-primitive baseline:    {best_baseline:.3f}")
    print(f"Best blackboard composition:       {best_blackboard:.3f}")
    print(f"Blackboard lift over baseline:     {lift:+.3f}")
    print()
    apollo_elite_estimate = 0.36  # from gen-3551 baseline_matrix.py result
    print(f"For comparison, Apollo elite (gen 2960):  ~{apollo_elite_estimate:.3f}")
    if best_blackboard > apollo_elite_estimate + 0.05:
        print()
        print("VERDICT: Blackboard composition beats Apollo elite by >5pp.")
        print("         Representation matters. Branch C should be on blackboard.")
    elif best_blackboard > best_baseline + 0.05:
        print()
        print("VERDICT: Blackboard composition beats single-primitive baseline")
        print("         but not Apollo elite by much. Representation helps but")
        print("         isn't the main blocker.")
    else:
        print()
        print("VERDICT: No meaningful lift from blackboard representation.")
        print("         The current representation is not the bottleneck.")


if __name__ == "__main__":
    main()
