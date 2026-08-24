"""CYCLE 153-S — verify the guard-collision hypothesis BY EXECUTION.

=============================== PREREGISTRATION ===============================
Committed BEFORE the run.

CLAIM UNDER TEST, structurally identified last pass and NOT yet executed:
  score_by_derivability__g carries precondition
      (len(derived_facts) > 0 or len(facts) > 0) and len(ordered) == 0
  so it SKIPS whenever `ordered` is non-empty. The O1 ceiling pipeline runs
  relations_from_facts then op_build_ordering BEFORE all five scorers. If those
  populate `ordered` on a canary task, the derivability guard fails and
  select_nth__g (guard len(ordered) > 0) fires instead, answering the wrong
  question on a task whose solver is present in the pipeline.

  IF TRUE: canary's 0.6 is a GUARD-COLLISION ARTIFACT — a routing-order defect —
  NOT an expressivity gap. The target is VOIDED and the assay survives.

THREE HYPOTHESES ALREADY FALSIFIED BY READING (not to be re-tested):
  forward_chain depth bound      -- FALSE, genuine `while changed:` fixpoint
  multi-premise rules needed     -- FALSE, canary emits single-premise chains only
  conditional dispatch missing   -- FALSE, __g scorers ARE guarded and ARE a dispatcher

MEASUREMENT: build N canary tasks from inference_canary.gen_inference_chain (the
production generator, not a reimplementation). Run the exact O1 ceiling_pipeline
via run_pipeline, one op at a time, recording after each op which slots changed.
For each guarded scorer record whether its precondition held at the moment it ran.

CONTROLS, each stated WITH the input that would make it FAIL:
  C1 GENERATOR FIDELITY -- every generated task must have exactly one derivable
     candidate among 4, and correct must be in candidates.
     FAILS IF: not, meaning the harness is not testing the real canary.
  C2 SOLVER-PATH PRESENT -- parse_rules, forward_chain and score_by_derivability__g
     must all be in the ceiling pipeline as named in RESULT.json.
     FAILS IF: absent, meaning the premise of the whole hypothesis is wrong.
  C3 POSITIVE CONTROL -- the three-op pipeline parse_rules -> forward_chain ->
     score_by_derivability (UNGUARDED base op) must score near 1.0 on canary.
     FAILS IF: below ~0.9, meaning canary is NOT solvable by that path and the
     deficit really is expressivity, which refutes the hypothesis outright.
  C4 SKIP DETECTION -- a skipped op must be distinguishable from an op that ran and
     wrote nothing. Detected by evaluating the precondition directly, not by
     inferring from slot deltas.
     FAILS IF: preconditions are not introspectable, in which case the mechanism
     is reported as unverified rather than confirmed.

NULL OUTPUT OF EVERY RULE:
  - if derivability's precondition HOLDS at its position and it still scores wrong,
    the mechanism is elsewhere and the hypothesis is REFUTED, reported as such;
  - if `ordered` is empty at that point, the collision does not occur and the
    hypothesis is REFUTED;
  - C3 failing refutes the hypothesis and RESTORES the expressivity reading.

SCOPE: canary subset only, one generator, seed stated. This says nothing about the
other three subsets and nothing about the 0.8333 ceiling until the consequence is
measured separately.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

ROOT = pathlib.Path(r'F:\Prometheus')
sys.path.insert(0, str(ROOT / 'apollo' / 'src'))
sys.path.insert(0, str(ROOT / 'apollo' / 'scripts'))

from blackboard import BlackboardState, run_pipeline            # noqa: E402
import blackboard_evolve as BE                                   # noqa: E402
from inference_canary import gen_inference_chain                 # noqa: E402

CEILING = ['parse_box_items', 'op_aggregate_quantities', 'parse_comparison',
           'parse_names_and_relations', 'parse_ordinal', 'parse_rules', 'forward_chain',
           'parse_which_extreme', 'relations_from_facts', 'op_build_ordering',
           'score_by_aggregate__g', 'score_by_comparison__g', 'score_by_derivability__g',
           'score_by_extreme_number__g', 'select_nth__g']

SLOTS = ['numbers', 'names', 'relations', 'quantities', 'question_target',
         'transitive_closure', 'ordered', 'counts', 'rules', 'facts', 'derived_facts',
         'candidate_scores', 'selected_answer', 'max_entity', 'comparison']

print("CYCLE 153-S — canary trace, by execution")
print("=" * 74)

REG = BE.REGISTRY
missing = [n for n in CEILING if n not in REG]
print(f"ceiling pipeline ops resolved: {len(CEILING) - len(missing)}/{len(CEILING)}"
      + (f"  MISSING {missing}" if missing else ""))
C2 = all(n in REG for n in ('parse_rules', 'forward_chain', 'score_by_derivability__g'))
print(f"C2 solver path present in ceiling pipeline: {C2}")


def snap(s):
    out = {}
    for k in SLOTS:
        v = getattr(s, k, None)
        if v is None:
            out[k] = None
        elif isinstance(v, (list, set, dict, str)):
            out[k] = len(v)
        else:
            out[k] = v
    return out


rng = random.Random(20260824)
tasks = [gen_inference_chain(rng) for _ in range(40)]
c1_bad = sum(1 for t in tasks
             if t['correct'] not in t['candidates'] or len(t['candidates']) != 4)
C1 = (c1_bad == 0)
print(f"C1 generator fidelity: {len(tasks)} tasks, {c1_bad} malformed -> {C1}")

# ---- C3 POSITIVE CONTROL: the bare solver path, unguarded
base_pipe = [REG[n][0] for n in ('parse_rules', 'forward_chain')]
deriv_base = REG['score_by_derivability__g'][0]
# reach the unguarded base op through the guarded wrapper's fn
import blackboard_ops_r2 as R2                                    # noqa: E402
solver = [REG['parse_rules'][0], REG['forward_chain'][0],
          R2.REGISTRY['score_by_derivability'][0] if hasattr(R2, 'REGISTRY')
          else deriv_base]
hit = 0
for t in tasks:
    st = BlackboardState(problem_text=t['prompt'], candidates=t['candidates'])
    st = run_pipeline(solver, st)
    if getattr(st, 'selected_answer', None) == t['correct']:
        hit += 1
c3_acc = hit / len(tasks)
C3 = c3_acc >= 0.9
print(f"C3 positive control (parse_rules->forward_chain->derivability): "
      f"{hit}/{len(tasks)} = {c3_acc:.4f} -> {C3}")

# ---- THE TRACE: full ceiling pipeline, per-op, with precondition introspection
pipe = [REG[n][0] for n in CEILING]
guard_fired = {n: 0 for n in CEILING}
guard_present = {n: 0 for n in CEILING}
ceiling_hit = 0
ordered_at_deriv = []
first_trace = None

for ti, t in enumerate(tasks):
    st = BlackboardState(problem_text=t['prompt'], candidates=t['candidates'])
    trace = []
    for name, op in zip(CEILING, pipe):
        before = snap(st)
        pre = getattr(op, 'precondition', None)
        holds = None
        if pre is not None:
            guard_present[name] += 1
            try:
                holds = bool(pre(st))
            except Exception:
                holds = None
            if holds:
                guard_fired[name] += 1
        if name == 'score_by_derivability__g':
            ordered_at_deriv.append(len(getattr(st, 'ordered', [])))
        st = op(st)
        after = snap(st)
        changed = {k: (before[k], after[k]) for k in SLOTS if before[k] != after[k]}
        trace.append((name, holds, changed))
    if getattr(st, 'selected_answer', None) == t['correct']:
        ceiling_hit += 1
    if first_trace is None:
        first_trace = trace

ceil_acc = ceiling_hit / len(tasks)
print(f"\nFULL CEILING PIPELINE on canary: {ceiling_hit}/{len(tasks)} = {ceil_acc:.4f}")
print(f"  (O1 RESULT.json reports canary 0.6)")

print("\nGUARD BEHAVIOUR across all tasks:")
for n in CEILING:
    if guard_present[n]:
        print(f"  {n:26s} precondition HELD in {guard_fired[n]:>3}/{guard_present[n]:>3} tasks")
C4 = any(guard_present[n] for n in CEILING)
print(f"C4 skip detection available (preconditions introspectable): {C4}")

import statistics as _st
print(f"\n`ordered` length at the moment derivability's guard is evaluated: "
      f"median {_st.median(ordered_at_deriv) if ordered_at_deriv else 'n/a'} "
      f"| max {max(ordered_at_deriv) if ordered_at_deriv else 'n/a'} "
      f"| zero in {sum(1 for x in ordered_at_deriv if x == 0)}/{len(ordered_at_deriv)}")

print("\nPER-OP TRACE, task 0 (slots that changed):")
for name, holds, changed in first_trace:
    g = '' if holds is None else ('  guard=HELD' if holds else '  guard=SKIP')
    if changed:
        print(f"  {name:26s}{g}  {changed}")
    else:
        print(f"  {name:26s}{g}  (no slot change)")

deriv_skipped = guard_present['score_by_derivability__g'] - guard_fired['score_by_derivability__g']
CONFIRMED = (C1 and C2 and C3 and C4
             and deriv_skipped > 0
             and ceil_acc < c3_acc)
print(f"\nHYPOTHESIS (guard collision voids the target): "
      f"{'CONFIRMED' if CONFIRMED else 'NOT CONFIRMED'}")
print(f"  derivability skipped in {deriv_skipped}/{len(tasks)} tasks; "
      f"solver-alone {c3_acc:.4f} vs full pipeline {ceil_acc:.4f}")

out = {'cycle': '153-S', 'n_tasks': len(tasks), 'seed': 20260824,
       'controls': {'C1_generator_fidelity': C1, 'C1_malformed': c1_bad,
                    'C2_solver_path_present': C2,
                    'C3_positive_control_acc': c3_acc, 'C3': C3,
                    'C4_preconditions_introspectable': C4},
       'solver_alone_acc': c3_acc, 'full_ceiling_pipeline_acc': ceil_acc,
       'o1_reported_canary': 0.6,
       'guard_held_counts': {n: [guard_fired[n], guard_present[n]]
                             for n in CEILING if guard_present[n]},
       'derivability_skipped_in': deriv_skipped,
       'ordered_len_at_derivability_guard': {
           'median': _st.median(ordered_at_deriv) if ordered_at_deriv else None,
           'max': max(ordered_at_deriv) if ordered_at_deriv else None,
           'zero_count': sum(1 for x in ordered_at_deriv if x == 0)},
       'HYPOTHESIS_CONFIRMED': CONFIRMED}
(ROOT / 'aporia/search/cycle_153s_results.json').write_text(json.dumps(out, indent=1),
                                                            encoding='utf-8')
print(f"\n*** written: aporia/search/cycle_153s_results.json ***")
