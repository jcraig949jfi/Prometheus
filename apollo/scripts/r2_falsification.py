"""r2_falsification.py — the 2026-05-29 handoff's one-experiment falsification.

Question (forge handoff §8): *Does a single R2 transformer produce a
genuinely load-bearing composition the R0-R1 set provably couldn't?*

  YES -> the tier-monoculture diagnosis holds; the forge typed-transformer
         pivot is justified; coordinate the contract.
  NO  -> the bottleneck is NOT primitive tier; we learned it for an
         afternoon's work and look elsewhere.

Method (falsification-first — try hard to make the R2 op look unnecessary):
  1. Build a constraint-tracking canary whose answer is reachable ONLY by
     multi-hop forward chaining (never stated; no ordering/counting/length
     structure to exploit).
  2. Run the R2 composition (parse_rules -> forward_chain -> score_by_derivability)
     through the load-bearing gauntlet:
       - composition accuracy vs single-primitive / terminal-only / chance
       - derived_facts load-bearing (null-slot ablation)
       - shuffled-state null (permute the closure across tasks)
       - inference null (replace forward_chain with copy-facts: proves the
         *inference* is load-bearing, not merely the slot's existence)
       - reorder breakage
  3. Run the R0-R1 set on the SAME canary (the decisive comparison): the
     best evolved pipeline + three hand-written R0-R1 shapes. If any solves
     it, tier is not the bottleneck.

Doctrine #2: report signatures, not just a verdict line. Writes a JSON
artifact with every gate value for re-audit.

Usage:
    python r2_falsification.py
"""
import sys
import copy
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "agents" / "hephaestus" / "src"))

from blackboard import BlackboardState, BlackboardOp, blackboard_op, run_pipeline, audit_pipeline
from dataflow_fitness import compute_dataflow_fitness
from blackboard_ops_r2 import parse_rules, forward_chain, score_by_derivability
# R0-R1 set (the existing substrate)
from blackboard_ops import (parse_names_and_relations, parse_question_target,
                            op_transitive_closure, score_by_max_entity)
from blackboard_ops_v2 import (op_build_ordering, select_nth, parse_ordinal,
                               parse_box_items, op_aggregate_quantities, score_by_aggregate)

RNG = random.Random(20260609)
_ATOMS = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
          "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
          "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]


# ── 1. Constraint-tracking canary ─────────────────────────────────────


def gen_inference_chain() -> dict:
    """Multi-hop forward-chaining task.

    Chain  a0 -> a1 -> ... -> a(L-1); base fact a0 is true. Correct answer
    is a derived atom at depth >= 2 (requires chaining; NOT the asserted
    fact, NOT a single hop). Distractors are atoms that appear in rules but
    are unreachable (no asserted fact triggers them), plus an unmentioned
    atom. Exactly one candidate is in the closure.
    """
    pool = RNG.sample(_ATOMS, 12)
    L = RNG.choice([4, 5])
    chain = pool[:L]
    rules = [(chain[i], chain[i + 1]) for i in range(L - 1)]

    # distractor rule cluster, unreachable (no asserted fact triggers it)
    d_pool = pool[L:L + 3]
    distractor_rules = [(d_pool[0], d_pool[1])]  # d0 -> d1, never fired
    unmentioned = d_pool[2]

    all_rules = rules + distractor_rules
    RNG.shuffle(all_rules)
    rule_text = ". ".join(f"If {a} then {b}" for a, b in all_rules)

    depth = RNG.randint(2, L - 1)        # correct answer is >= 2 hops deep
    correct = chain[depth]
    base_fact = chain[0]

    prompt = f"{rule_text}. {base_fact} is true. Which of the following can be derived?"

    # candidates: correct (derivable) + 3 non-derivable distractors
    distractors = [d_pool[0], d_pool[1], unmentioned]  # none reachable from base_fact
    cands = [correct] + distractors
    RNG.shuffle(cands)
    return {
        "category": "inference_chain",
        "prompt": prompt,
        "candidates": cands,
        "correct": correct,
        "requires_intermediate": "derived_facts",
        # what surface extraction of "the stated fact" would yield (the base fact):
        "single_primitive_answer": base_fact,
    }


def build_canary(n=30) -> list[dict]:
    return [gen_inference_chain() for _ in range(n)]


# ── 2. Compositions under test ────────────────────────────────────────

R2_COMP = [parse_rules, forward_chain, score_by_derivability]

# R0-R1 set: the best evolved pipeline (gen-50 elite) + hand-written shapes.
R01_BEST_EVOLVED = [parse_names_and_relations, parse_ordinal, op_build_ordering, select_nth]
R01_TRANSITIVE = [parse_names_and_relations, op_transitive_closure, score_by_max_entity]
R01_COUNT = [parse_box_items, op_aggregate_quantities, score_by_aggregate]
R01_SET = {
    "best_evolved (parse_rel->ordinal->ordering->select_nth)": R01_BEST_EVOLVED,
    "transitive_closure->max": R01_TRANSITIVE,
    "box_items->aggregate->score": R01_COUNT,
}


# Inference null: writes derived_facts = facts (no chaining). If the R2
# composition still solves the canary with this swapped in, the INFERENCE
# (not the slot) was not load-bearing.
@blackboard_op(reads=["facts"], writes=["derived_facts"], name="copy_facts_null")
def copy_facts_null(state: BlackboardState) -> BlackboardState:
    state.derived_facts = set(state.facts)
    return state

R2_INFERENCE_NULL = [parse_rules, copy_facts_null, score_by_derivability]


# ── 3. Gates ───────────────────────────────────────────────────────────


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
    n = sum(1 for t in tasks if t.get("single_primitive_answer") == t["correct"])
    return n / max(len(tasks), 1)


def _terminal_only_baseline(tasks):
    n = 0
    for t in tasks:
        pick = max(t["candidates"], key=len) if t["candidates"] else ""
        if pick == t["correct"]:
            n += 1
    return n / max(len(tasks), 1)


def _chance(tasks):
    return sum(1.0 / max(len(t["candidates"]), 1) for t in tasks) / max(len(tasks), 1)


def _shuffled_state_null(pipeline, tasks, slot):
    head, tail_op = pipeline[:-1], pipeline[-1]
    intermediates, states = [], []
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            s = run_pipeline(head, s)
        except Exception:
            pass
        intermediates.append(copy.deepcopy(getattr(s, slot, None)))
        states.append(s)
    shuffled = intermediates[:]
    RNG.shuffle(shuffled)
    n = 0
    for t, s, val in zip(tasks, states, shuffled):
        setattr(s, slot, val)
        try:
            out = tail_op(s)
            if out.selected_answer == t["correct"]:
                n += 1
        except Exception:
            pass
    return n / max(len(tasks), 1)


def _reorder_breakage(pipeline, tasks):
    if len(pipeline) < 3:
        return None
    r = pipeline[:]
    r[-2], r[-3] = r[-3], r[-2]
    return _evaluate(r, tasks)


def main():
    print("=" * 78)
    print("R2 FALSIFICATION — does ONE R2 transformer beat the R0-R1 ceiling?")
    print("=" * 78)
    tasks = build_canary(30)
    chance = _chance(tasks)
    print(f"Constraint-tracking canary: {len(tasks)} multi-hop forward-chaining tasks")
    print(f"  Correct answer is >=2 hops deep; never stated; no ordering/count/length")
    print(f"  structure. Chance (random candidate) = {chance:.3f}")
    print()

    # ── R2 composition gates ───────────────────────────────────────────
    print("--- R2 composition: parse_rules -> forward_chain -> score_by_derivability ---")
    sigs = audit_pipeline(R2_COMP)
    print(f"  [type audit]  recompute-bypass={len(sigs['recompute_bypass'])} "
          f"side-output={len(sigs['side_output'])} "
          f"redundant-encoding={len(sigs['redundant_encoding'])} "
          f"compile-errors={len(sigs['compile_check_errors'])}")

    r2_acc = _evaluate(R2_COMP, tasks)
    single = _single_primitive_baseline(tasks)
    terminal = _terminal_only_baseline(tasks)
    comp_lift = r2_acc - max(single, terminal, chance)
    print(f"  [accuracy]            R2 composition = {r2_acc:.3f}")
    print(f"  [single-primitive]    baseline       = {single:.3f}")
    print(f"  [terminal-only]       baseline       = {terminal:.3f}")
    print(f"  [composition lift]    {comp_lift:+.3f}  (vs max(single, terminal, chance))")

    df = compute_dataflow_fitness(R2_COMP, tasks)
    lb_slots = [s["slot"] for s in df["per_slot_signatures"] if s["signature"] == "load-bearing"]
    derived_lb = "derived_facts" in lb_slots
    print(f"  [dataflow]            load-bearing slots = {lb_slots}")
    for s in df["per_slot_signatures"]:
        print(f"      slot={s['slot']:<16} sig={s['signature']:<28} delta={s['delta']:+.3f}")

    shuffled = _shuffled_state_null(R2_COMP, tasks, "derived_facts")
    shuffled_drop = r2_acc - shuffled
    print(f"  [shuffled-state null] derived_facts shuffled -> acc={shuffled:.3f} "
          f"drop={shuffled_drop:+.3f}  ({'breaks' if shuffled_drop >= 0.10 else 'DOES NOT break'})")

    inf_null_acc = _evaluate(R2_INFERENCE_NULL, tasks)
    inf_null_drop = r2_acc - inf_null_acc
    print(f"  [inference null]      forward_chain -> copy_facts -> acc={inf_null_acc:.3f} "
          f"drop={inf_null_drop:+.3f}  ({'inference is load-bearing' if inf_null_drop >= 0.10 else 'inference NOT load-bearing'})")

    reorder = _reorder_breakage(R2_COMP, tasks)
    reorder_drop = (r2_acc - reorder) if reorder is not None else None
    if reorder_drop is not None:
        print(f"  [reorder breakage]    acc={reorder:.3f} drop={reorder_drop:+.3f} "
              f"({'breaks' if reorder_drop >= 0.05 else 'does not break'})")

    # ── R0-R1 set on the SAME canary (decisive comparison) ─────────────
    print()
    print("--- R0-R1 set on the SAME canary (can the existing substrate solve it?) ---")
    r01_results = {}
    for name, pipe in R01_SET.items():
        acc = _evaluate(pipe, tasks)
        r01_results[name] = acc
        print(f"  {acc:.3f}  {name}")
    r01_best = max(r01_results.values())
    print(f"  -> best R0-R1 = {r01_best:.3f}  (chance = {chance:.3f})")

    # ── Verdict ────────────────────────────────────────────────────────
    r2_passes = (comp_lift >= 0.10 and derived_lb and shuffled_drop >= 0.10
                 and inf_null_drop >= 0.10)
    r01_fails = r01_best <= chance + 0.05
    keystone = r2_passes and r01_fails

    print()
    print("=" * 78)
    print("READING (Doctrine #2 — signatures above; verdict below)")
    print("=" * 78)
    print(f"  R2 composition passes load-bearing gauntlet : {r2_passes}")
    print(f"    comp_lift>=0.10={comp_lift >= 0.10} | derived_facts load-bearing={derived_lb} "
          f"| shuffled breaks={shuffled_drop >= 0.10} | inference load-bearing={inf_null_drop >= 0.10}")
    print(f"  R0-R1 set fails the canary (<= chance+0.05)  : {r01_fails}  "
          f"(best={r01_best:.3f}, chance={chance:.3f})")
    print()
    if keystone:
        print("  KEYSTONE QUESTION = YES.")
        print("  A single R2 transformer (forward_chain) produces a load-bearing")
        print("  composition the R0-R1 set provably cannot. The tier-monoculture")
        print("  diagnosis holds; the forge typed-transformer pivot is justified.")
    elif r2_passes and not r01_fails:
        print("  KEYSTONE QUESTION = NO (canary construct-invalid).")
        print("  R2 passes, but an R0-R1 shape also solves the canary -> the task did")
        print("  not actually require R2. Harden the canary before concluding.")
    else:
        print("  KEYSTONE QUESTION = NO.")
        print("  The R2 composition did not clear the load-bearing bar. Tier is not")
        print("  obviously the bottleneck; investigate the failing gate above.")

    # ── Artifact ───────────────────────────────────────────────────────
    out = {
        "experiment": "r2_falsification",
        "date": "2026-06-09",
        "seed": 20260609,
        "n_tasks": len(tasks),
        "chance": chance,
        "r2_composition": {
            "pipeline": [o.name for o in R2_COMP],
            "accuracy": r2_acc,
            "single_primitive_baseline": single,
            "terminal_only_baseline": terminal,
            "comp_lift": comp_lift,
            "derived_facts_load_bearing": derived_lb,
            "load_bearing_slots": lb_slots,
            "dataflow_signatures": df["per_slot_signatures"],
            "shuffled_state_null_acc": shuffled,
            "shuffled_drop": shuffled_drop,
            "inference_null_acc": inf_null_acc,
            "inference_null_drop": inf_null_drop,
            "reorder_acc": reorder,
            "reorder_drop": reorder_drop,
            "type_audit": {k: len(v) for k, v in sigs.items()},
            "passes_gauntlet": r2_passes,
        },
        "r01_set": {
            "results": r01_results,
            "best": r01_best,
            "fails_canary": r01_fails,
        },
        "keystone_question_yes": keystone,
    }
    art = ROOT / "pivot" / "r2_falsification_result_2026-06-09.json"
    with open(art, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print()
    print(f"  artifact -> {art}")
    return keystone


if __name__ == "__main__":
    main()
