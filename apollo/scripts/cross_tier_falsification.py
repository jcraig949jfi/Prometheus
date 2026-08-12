"""cross_tier_falsification.py — does a genuine MULTI-TIER organism exist?

After R2 Run 1 (pivot/r2_run1_findings_2026-06-10.md) showed R2 stranded as an
isolated specialist, two fixes were made: the bridge op `relations_from_facts`
(R2 output -> R1 input) and a cross-tier canary (tasks that need R2 inference
THEN R1 ordering). This experiment falsifies the claim that the fixes work.

Question: *Is the cross-tier pipeline the UNIQUE solver — solving the canary with
every link load-bearing, while no single-tier shape can?*

  YES -> cross-tier composition is now expressible AND rewarded; a future
         --mode llm run has a real gradient toward multi-tier organisms.
  NO  -> either the canary isn't construct-valid (a single-tier shape solves it)
         or a link isn't load-bearing; fix before any long run.

Falsification-first — we try to make the multi-tier organism look unnecessary:
  - run R0-R1-only and R2-only controls on the SAME canary
  - run a no-inference null (forward_chain -> copy_facts): keeps the full
    cross-tier STRUCTURE but removes the inference; if it still solves the task,
    the inference wasn't load-bearing
  - null-slot ablation across every slot (is each link causal?)
  - shuffled-state null on the ordering the terminal reads

Writes a JSON artifact for re-audit.

Usage:
    python cross_tier_falsification.py
"""
import sys
import copy
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blackboard import BlackboardState, blackboard_op, run_pipeline, audit_pipeline
from dataflow_fitness import compute_dataflow_fitness
from blackboard_ops_r2 import (parse_rules, forward_chain, relations_from_facts,
                               score_by_derivability)
from blackboard_ops_v2 import parse_ordinal, op_build_ordering, select_nth
from blackboard_ops import parse_names_and_relations, op_transitive_closure, score_by_max_entity
from cross_tier_canary import build_cross_tier_canary


# ── pipelines under test ──────────────────────────────────────────────

# The candidate multi-tier organism (R1 parse + R2 inference + bridge + R1 order)
CROSS_TIER = [parse_rules, parse_ordinal, forward_chain, relations_from_facts,
              op_build_ordering, select_nth]

# Controls
R01_ONLY = [parse_names_and_relations, parse_ordinal, op_build_ordering, select_nth]
R01_TRANSITIVE = [parse_names_and_relations, op_transitive_closure, score_by_max_entity]
R2_ONLY = [parse_rules, forward_chain, score_by_derivability]


# no-inference null: keep the structure, replace the inference with a copy
@blackboard_op(reads=["facts"], writes=["derived_facts"], name="copy_facts_null")
def copy_facts_null(state):
    state.derived_facts = set(state.facts)
    return state

NO_INFERENCE_NULL = [parse_rules, parse_ordinal, copy_facts_null, relations_from_facts,
                     op_build_ordering, select_nth]


# ── gates ──────────────────────────────────────────────────────────────

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


def _shuffled_state_null(pipeline, tasks, slot, seed=20260610):
    import random
    rng = random.Random(seed)
    head, tail_op = pipeline[:-1], pipeline[-1]
    vals, states = [], []
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            s = run_pipeline(head, s)
        except Exception:
            pass
        vals.append(copy.deepcopy(getattr(s, slot, None)))
        states.append(s)
    shuffled = vals[:]
    rng.shuffle(shuffled)
    n = 0
    for t, s, v in zip(tasks, states, shuffled):
        setattr(s, slot, v)
        try:
            out = tail_op(s)
            if out.selected_answer == t["correct"]:
                n += 1
        except Exception:
            pass
    return n / max(len(tasks), 1)


def main():
    print("=" * 78)
    print("CROSS-TIER FALSIFICATION — is the multi-tier organism the unique solver?")
    print("=" * 78)
    tasks = build_cross_tier_canary(30)
    chance = _chance(tasks)
    print(f"Cross-tier canary: {len(tasks)} derive-then-order tasks. Chance={chance:.3f}")
    print(f"  Solver must: parse rules -> infer hidden link (R2) -> bridge to")
    print(f"  relations -> order (R1) -> select nth. Single tiers structurally can't.")
    print()

    # type audit
    sigs = audit_pipeline(CROSS_TIER)
    print(f"--- candidate: {' -> '.join(o.name for o in CROSS_TIER)} ---")
    print(f"  [type audit]  recompute-bypass={len(sigs['recompute_bypass'])} "
          f"side-output={len(sigs['side_output'])} compile-errors={len(sigs['compile_check_errors'])}")

    ct_acc = _evaluate(CROSS_TIER, tasks)
    single = _single_primitive_baseline(tasks)
    terminal = _terminal_only_baseline(tasks)
    comp_lift = ct_acc - max(single, terminal, chance)
    print(f"  [accuracy]            cross-tier = {ct_acc:.3f}")
    print(f"  [single-primitive]    baseline   = {single:.3f}")
    print(f"  [terminal-only]       baseline   = {terminal:.3f}")
    print(f"  [composition lift]    {comp_lift:+.3f}")

    df = compute_dataflow_fitness(CROSS_TIER, tasks)
    lb = [s["slot"] for s in df["per_slot_signatures"] if s["signature"] == "load-bearing"]
    print(f"  [dataflow]            load-bearing slots = {lb}")
    for s in df["per_slot_signatures"]:
        print(f"      slot={s['slot']:<16} sig={s['signature']:<28} delta={s['delta']:+.3f}")
    # the cross-tier chain's two pivotal intermediates:
    derived_lb = "derived_facts" in lb
    relations_lb = "relations" in lb

    shuffled = _shuffled_state_null(CROSS_TIER, tasks, "ordered")
    shuffled_drop = ct_acc - shuffled
    print(f"  [shuffled-state null] ordered shuffled -> acc={shuffled:.3f} "
          f"drop={shuffled_drop:+.3f}  ({'breaks' if shuffled_drop >= 0.10 else 'DOES NOT break'})")

    ni_acc = _evaluate(NO_INFERENCE_NULL, tasks)
    ni_drop = ct_acc - ni_acc
    print(f"  [no-inference null]   forward_chain->copy_facts -> acc={ni_acc:.3f} "
          f"drop={ni_drop:+.3f}  ({'inference load-bearing' if ni_drop >= 0.10 else 'inference NOT load-bearing'})")

    print()
    print("--- single-tier controls on the SAME canary ---")
    controls = {
        "R0-R1 only (parse_rel->ordinal->ordering->select_nth)": R01_ONLY,
        "R0-R1 transitive->max": R01_TRANSITIVE,
        "R2 only (parse_rules->forward_chain->derivability)": R2_ONLY,
    }
    ctrl_results = {}
    for name, pipe in controls.items():
        acc = _evaluate(pipe, tasks)
        ctrl_results[name] = acc
        print(f"  {acc:.3f}  {name}")
    ctrl_best = max(ctrl_results.values())
    print(f"  -> best single-tier control = {ctrl_best:.3f}  (chance={chance:.3f})")

    # ── verdict ────────────────────────────────────────────────────────
    ct_passes = (comp_lift >= 0.10 and derived_lb and relations_lb
                 and shuffled_drop >= 0.10 and ni_drop >= 0.10)
    controls_fail = ctrl_best <= chance + 0.05
    unique_solver = ct_passes and controls_fail

    print()
    print("=" * 78)
    print(f"  cross-tier passes load-bearing gauntlet : {ct_passes}")
    print(f"    comp_lift>=0.10={comp_lift >= 0.10} | derived_facts LB={derived_lb} "
          f"| relations LB={relations_lb} | ordered shuffle breaks={shuffled_drop >= 0.10} "
          f"| inference LB={ni_drop >= 0.10}")
    print(f"  single-tier controls all fail (<=chance+0.05): {controls_fail} "
          f"(best={ctrl_best:.3f})")
    print()
    if unique_solver:
        print("  RESULT = YES. The cross-tier organism is the UNIQUE solver. Both")
        print("  fixes work: R2->R1 composition is expressible (bridge) AND rewarded")
        print("  (canary). A --mode llm run now has a real gradient toward multi-tier")
        print("  organisms — the novelty Run 1 lacked.")
    elif ct_passes and not controls_fail:
        print("  RESULT = NO (canary construct-invalid). A single-tier shape solves it;")
        print("  the task does not actually require crossing tiers. Harden the canary.")
    else:
        print("  RESULT = NO. The cross-tier composition did not clear the bar; inspect")
        print("  the failing gate (a link may not be load-bearing through the bridge).")

    out = {
        "experiment": "cross_tier_falsification",
        "date": "2026-06-10",
        "n_tasks": len(tasks),
        "chance": chance,
        "cross_tier": {
            "pipeline": [o.name for o in CROSS_TIER],
            "accuracy": ct_acc, "single": single, "terminal": terminal,
            "comp_lift": comp_lift,
            "load_bearing_slots": lb,
            "derived_facts_load_bearing": derived_lb,
            "relations_load_bearing": relations_lb,
            "dataflow_signatures": df["per_slot_signatures"],
            "shuffled_ordered_acc": shuffled, "shuffled_drop": shuffled_drop,
            "no_inference_null_acc": ni_acc, "no_inference_drop": ni_drop,
            "type_audit": {k: len(v) for k, v in sigs.items()},
            "passes_gauntlet": ct_passes,
        },
        "single_tier_controls": {"results": ctrl_results, "best": ctrl_best,
                                 "all_fail": controls_fail},
        "unique_solver": unique_solver,
    }
    art = ROOT / "pivot" / "cross_tier_falsification_result_2026-06-10.json"
    with open(art, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print()
    print(f"  artifact -> {art}")
    return unique_solver


if __name__ == "__main__":
    main()
