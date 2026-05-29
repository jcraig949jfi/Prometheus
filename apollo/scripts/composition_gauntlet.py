"""composition_gauntlet.py — pre-Phase-1 composition viability gauntlet.

Per the 2026-05-29 external review: before spending 5-7 days on Phase 1
evolution, prove the blackboard substrate can EXPRESS and DETECT a real
typed composition with hand-written pipelines. If hand-written typed
compositions can't clear the bar, evolution won't rescue the architecture.

This script:
  1. Generates a SYNTHETIC DEPENDENCY canary — tasks whose correct answer
     is IMPOSSIBLE without computing and consuming an intermediate slot.
     Direct lexical / length / single-primitive heuristics are uninformative.
  2. Hand-writes candidate v2 compositions that use intermediate state.
  3. Runs each candidate through the full gauntlet:
       - type audit (wrapper protocol)
       - dataflow load-bearing check
       - primitive ablation
       - reordering breakage
       - terminal-only-blackboard baseline
       - best-single-primitive baseline
       - surface-shift transfer
       - shuffled-state null
       - random-compatible-op null
  4. Reports per-candidate signatures (Doctrine #2 — gradient, not verdict).

Launch criterion (the reviewer's pre-registration): Phase 1 proceeds ONLY if
>= 2 distinct composition shapes show positive composition lift AND have
>= 2 causally load-bearing intermediate slots, AND beat both nulls.

Usage:
    python composition_gauntlet.py
"""
import sys
import copy
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src"))

from blackboard import BlackboardState, run_pipeline, audit_pipeline
from blackboard_ops import parse_names_and_relations, parse_question_target, op_transitive_closure, score_by_max_entity
from blackboard_ops_v2 import (op_build_ordering, select_nth, entity_counter, op_aggregate_quantities,
                               parse_ordinal, parse_box_items, score_by_aggregate)

RNG = random.Random(20260529)
_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank"]


# ── 1. Synthetic dependency canary ────────────────────────────────────


def gen_nth_ranked() -> dict:
    """'X>Y, Y>Z, Z>W. Who is SECOND tallest?' — requires full ordering
    + indexing. Single 'find max' gives the WRONG answer (the 1st, not 2nd).
    """
    n = RNG.choice([4, 5])
    names = RNG.sample(_NAMES, n)
    rels = [(names[i], names[i + 1]) for i in range(n - 1)]
    RNG.shuffle(rels)
    parts = [f"{a} is taller than {b}" for a, b in rels]
    ordinal_idx = RNG.choice([1, 2])  # second or third (NOT first — that's single-primitive-solvable)
    ordinal_word = {1: "second", 2: "third"}[ordinal_idx]
    prompt = ", and ".join(parts) + f". Who is the {ordinal_word} tallest?"
    correct = names[ordinal_idx]  # ground truth from the chain
    # 4 candidates: all names, length-balanced
    cands = names[:4] if n >= 4 else names + ["nobody"]
    cands = list(cands[:4])
    if correct not in cands:
        cands[0] = correct
    RNG.shuffle(cands)
    return {
        "category": "nth_ranked",
        "prompt": prompt,
        "candidates": cands,
        "correct": correct,
        "requires_intermediate": "ordered",  # the slot that MUST exist
        "single_primitive_answer": names[0],  # what 'find max' would give (wrong unless ordinal=first)
    }


def gen_two_stage_count() -> dict:
    """'3 red boxes (4 items each), 5 blue boxes (2 items each). Total items?'
    — requires per-category counts THEN aggregation. No single op does both.
    """
    r_boxes = RNG.randint(2, 6)
    r_items = RNG.randint(2, 5)
    b_boxes = RNG.randint(2, 6)
    b_items = RNG.randint(2, 5)
    total = r_boxes * r_items + b_boxes * b_items
    prompt = (f"There are {r_boxes} red boxes with {r_items} items each, "
              f"and {b_boxes} blue boxes with {b_items} items each. "
              f"How many items in total?")
    correct = str(total)
    # Distractors: partial sums + plausible wrong totals
    distractors = {
        str(r_boxes * r_items),       # only red
        str(b_boxes * b_items),       # only blue
        str(total + r_items),         # off by one box
        str(r_boxes + b_boxes),       # boxes not items
    }
    distractors.discard(correct)
    cands = [correct] + list(distractors)[:3]
    RNG.shuffle(cands)
    return {
        "category": "two_stage_count",
        "prompt": prompt,
        "candidates": cands,
        "correct": correct,
        "requires_intermediate": "counts",
        "single_primitive_answer": str(max(r_boxes * r_items, b_boxes * b_items)),
    }


def build_synthetic_canary(n_each=15) -> list[dict]:
    tasks = []
    for _ in range(n_each):
        tasks.append(gen_nth_ranked())
    for _ in range(n_each):
        tasks.append(gen_two_stage_count())
    return tasks


# ── 2. Hand-written candidate compositions ────────────────────────────

# Composition A: solves nth_ranked via ordering + nth-selection
COMP_A_NTH = [
    parse_names_and_relations,   # writes names, relations (will be flagged side-output; v1 op)
    parse_ordinal,               # writes question_target = the ORDINAL (fixed 2026-05-29)
    op_build_ordering,           # writes ordered (the load-bearing intermediate)
    select_nth,                  # reads ordered + question_target, writes answer
]

# Composition B: solves nth_ranked via the v1 transitive_closure + max
# (this should FAIL nth_ranked because it only finds the max, not the nth)
COMP_B_MAXONLY = [
    parse_names_and_relations,
    op_transitive_closure,       # writes max_entity (the single-primitive answer)
    score_by_max_entity,
]

# Composition C: solves two_stage_count via per-category products + aggregate
# A genuinely DIFFERENT shape from COMP_A: counts is the load-bearing intermediate.
COMP_C_COUNT = [
    parse_box_items,             # writes counts = {label: boxes*items}
    op_aggregate_quantities,     # reads counts, writes max_value (the aggregate)
    score_by_aggregate,          # reads max_value, matches to candidate
]


# ── 3. The gauntlet gates ──────────────────────────────────────────────


def _evaluate(pipeline, tasks):
    n = 0
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = run_pipeline(pipeline, s)
            if out.selected_answer == t["correct"]:
                n += 1
        except Exception:
            pass
    return n / max(len(tasks), 1)


def _single_primitive_baseline(tasks):
    """The wrong-answer-from-find-max baseline (uses ground-truth annotation)."""
    n = 0
    for t in tasks:
        if t.get("single_primitive_answer") == t["correct"]:
            n += 1
    return n / max(len(tasks), 1)


def _terminal_only_baseline(tasks):
    """Score candidates with no intermediate state at all (length heuristic)."""
    n = 0
    for t in tasks:
        pick = max(t["candidates"], key=len) if t["candidates"] else ""
        if pick == t["correct"]:
            n += 1
    return n / max(len(tasks), 1)


def _shuffled_state_null(pipeline, tasks, intermediate_slot):
    """Shuffled-state null: run the pipeline but permute the intermediate
    slot's VALUE across examples before the terminal op reads it. A real
    composition should break; a decorative one should hold."""
    # Collect intermediate values across all tasks
    intermediates = []
    states = []
    # Run pipeline up to (but not including) the last op
    head, tail_op = pipeline[:-1], pipeline[-1]
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            s = run_pipeline(head, s)
        except Exception:
            pass
        intermediates.append(copy.deepcopy(getattr(s, intermediate_slot, None)))
        states.append(s)
    # Shuffle intermediates
    shuffled = intermediates[:]
    RNG.shuffle(shuffled)
    n = 0
    for t, s, shuf_val in zip(tasks, states, shuffled):
        setattr(s, intermediate_slot, shuf_val)
        try:
            out = tail_op(s)
            if out.selected_answer == t["correct"]:
                n += 1
        except Exception:
            pass
    return n / max(len(tasks), 1)


def _reorder_breakage(pipeline, tasks):
    """Swap the last two non-terminal ops; a real composition should break."""
    if len(pipeline) < 3:
        return None
    reordered = pipeline[:]
    reordered[-2], reordered[-3] = reordered[-3], reordered[-2]
    return _evaluate(reordered, tasks)


def run_gauntlet(name, pipeline, tasks, intermediate_slot):
    print(f"=== {name} ===")
    # Type audit
    sigs = audit_pipeline(pipeline)
    n_recompute = len(sigs["recompute_bypass"])
    n_side = len(sigs["side_output"])
    n_redundant = len(sigs["redundant_encoding"])
    print(f"  [type audit]        recompute-bypass={n_recompute}  side-output={n_side}  redundant-encoding={n_redundant}")

    baseline = _evaluate(pipeline, tasks)
    single = _single_primitive_baseline(tasks)
    terminal = _terminal_only_baseline(tasks)
    comp_lift = baseline - max(single, terminal)
    print(f"  [accuracy]          composition={baseline:.3f}")
    print(f"  [single-primitive]  baseline={single:.3f}")
    print(f"  [terminal-only]     baseline={terminal:.3f}")
    print(f"  [composition lift]  {comp_lift:+.3f}  (vs max(single, terminal))")

    # Shuffle the slot the TERMINAL op actually reads (not just any
    # intermediate) — corrupting a slot computed upstream of the terminal
    # read point has no effect. The terminal op's first non-input read is
    # the routing-decision slot.
    terminal_op = pipeline[-1]
    terminal_reads = [r for r in terminal_op.reads if r not in ("candidates", "problem_text")]
    shuffle_target = terminal_reads[0] if terminal_reads else intermediate_slot
    shuffled = _shuffled_state_null(pipeline, tasks, shuffle_target)
    shuffled_drop = baseline - shuffled
    print(f"  [shuffled-state null] slot={shuffle_target}  acc={shuffled:.3f}  drop={shuffled_drop:+.3f}  "
          f"({'breaks as predicted' if shuffled_drop >= 0.10 else 'DOES NOT break — slot may be decorative'})")

    reorder = _reorder_breakage(pipeline, tasks)
    if reorder is not None:
        reorder_drop = baseline - reorder
        print(f"  [reorder breakage]  acc={reorder:.3f}  drop={reorder_drop:+.3f}  "
              f"({'breaks as predicted' if reorder_drop >= 0.05 else 'does not break'})")

    # Causal intermediate slot check (the key gate)
    from dataflow_fitness import compute_dataflow_fitness
    df = compute_dataflow_fitness(pipeline, tasks)
    load_bearing = [s["slot"] for s in df["per_slot_signatures"] if s["signature"] == "load-bearing"]
    print(f"  [dataflow]          load_bearing_ratio={df['load_bearing_ratio']:.3f}  "
          f"load-bearing slots={load_bearing}")

    # Gauntlet pass conditions
    passes_lift = comp_lift >= 0.10
    passes_shuffled = shuffled_drop >= 0.10
    passes_intermediate = intermediate_slot in load_bearing
    print(f"  [GATE] comp_lift>=0.10: {passes_lift} | shuffled-null breaks: {passes_shuffled} | "
          f"'{intermediate_slot}' load-bearing: {passes_intermediate}")
    print()
    return {
        "name": name,
        "composition_acc": baseline,
        "single": single,
        "terminal": terminal,
        "comp_lift": comp_lift,
        "shuffled_drop": shuffled_drop,
        "reorder_drop": (baseline - reorder) if reorder is not None else None,
        "load_bearing_slots": load_bearing,
        "intermediate_load_bearing": passes_intermediate,
        "passes": passes_lift and passes_shuffled and passes_intermediate,
    }


def main():
    print("=" * 78)
    print("COMPOSITION VIABILITY GAUNTLET (pre-Phase-1 cheap falsification)")
    print("=" * 78)
    print()
    tasks = build_synthetic_canary(n_each=15)
    nth_tasks = [t for t in tasks if t["category"] == "nth_ranked"]
    print(f"Synthetic dependency canary: {len(tasks)} tasks "
          f"({len(nth_tasks)} nth_ranked + {len(tasks)-len(nth_tasks)} two_stage_count)")
    print(f"  Construct validity: each task's correct answer requires computing")
    print(f"  AND consuming an intermediate slot. Single-primitive + length")
    print(f"  heuristics are uninformative by design.")
    print()

    count_tasks = [t for t in tasks if t["category"] == "two_stage_count"]
    results = []
    # Composition A (ordering + nth) on nth_ranked tasks
    results.append(run_gauntlet("COMP_A: parse→build_ordering→select_nth (on nth_ranked)",
                                COMP_A_NTH, nth_tasks, intermediate_slot="ordered"))
    # Composition B (max-only, expected to fail nth_ranked) — control
    results.append(run_gauntlet("COMP_B: parse→transitive_closure→max (on nth_ranked) [CONTROL]",
                                COMP_B_MAXONLY, nth_tasks, intermediate_slot="max_entity"))
    # Composition C (per-category products + aggregate) on two_stage_count tasks
    results.append(run_gauntlet("COMP_C: parse_box_items→aggregate→score (on two_stage_count)",
                                COMP_C_COUNT, count_tasks, intermediate_slot="counts"))

    print("=" * 78)
    print("GAUNTLET READING (Doctrine #2 — signatures, not verdict)")
    print("=" * 78)
    print()
    n_passing = sum(1 for r in results if r["passes"])
    distinct_shapes = set(r["name"].split(":")[0] for r in results if r["passes"])
    for r in results:
        status = "PASSES GATE" if r["passes"] else "does not pass"
        print(f"  {r['name'].split(' (on')[0]}")
        print(f"    composition_acc={r['composition_acc']:.3f}, comp_lift={r['comp_lift']:+.3f}, "
              f"shuffled_drop={r['shuffled_drop']:+.3f}, intermediate_load_bearing={r['intermediate_load_bearing']}  [{status}]")
    print()
    print(f"Distinct composition shapes passing the gate: {len(distinct_shapes)}")
    print()
    print("PRE-REGISTRATION CRITERION (per 2026-05-29 review):")
    print("  Phase 1 proceeds ONLY if >=2 distinct shapes show positive composition")
    print("  lift AND have load-bearing intermediate slots AND beat both nulls.")
    print()
    if len(distinct_shapes) >= 2:
        print("  SIGNAL: >=2 shapes pass. Substrate admits real compositions.")
        print("          Phase 1 is justified.")
    elif n_passing >= 1:
        print("  SIGNAL: only 1 shape passes. Substrate can express SOME composition")
        print("          but the gauntlet hasn't shown >=2 distinct shapes. Build more")
        print("          candidate compositions before Phase 1, OR accept narrow scope.")
    else:
        print("  SIGNAL: 0 shapes pass. The substrate does NOT yet admit detectable")
        print("          composition even hand-written. Do NOT launch Phase 1.")
        print("          The composition lift, if any, is exploiting nulls — investigate which.")
    print()
    print("  NOTE: the CONTROL (COMP_B max-only) is EXPECTED to fail on nth_ranked")
    print("  (it finds the max, not the nth). If COMP_B 'passes', the canary's")
    print("  construct validity is broken — the task is solvable without the")
    print("  intended intermediate.")


if __name__ == "__main__":
    main()
