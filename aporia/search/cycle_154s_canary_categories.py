"""CYCLE 154-S — verify the 0.6 and the boolean gap BY EXECUTION.

=============================== PREREGISTRATION ===============================
Committed BEFORE the run. Two questions I did NOT verify last pass and which gate
any mint specification.

(a) DOES THE CEILING PIPELINE SCORE ~0.6 ON THE REAL CANARY SUBSET?
    Last pass I measured `inference` (40/40) when the deficit is in `canary` =
    apollo/data/clean_canary_v01.json, 50 tasks over seven categories. The 0.6 is
    Apollo's number, not mine. Run the exact O1 ceiling pipeline over that file and
    report PER-CATEGORY accuracy.

(b) CAN THE EXISTING OPS ALREADY ANSWER THE BOOLEAN ITEMS?
    blackboard_evolve.py:564 (2026-06-24) asserts canary's compare/bool tasks are
    "genuinely unsolvable in the current substrate (no boolean primitive)". That is
    Apollo's claim, quoted, not measured by me. score_by_comparison and
    parse_comparison EXIST. Run them directly against numeric_comparison,
    vacuous_truth and consistency_check.

    IF THEY CAN: the gap is ROUTING, not EXPRESSIVITY. The mint target is VOID.
    That is the eighth falsification of this cycle and it is a GOOD outcome — say
    so plainly rather than defending the target.
    IF THEY CANNOT: the boolean gap is confirmed by my own measurement rather than
    by a code comment, and the mint target is earned.

CONTROLS, each stated WITH the input that would make it FAIL:
  C1 TASK-FILE FIDELITY -- all 50 tasks load, every task has a `correct` present in
     its `candidates`, and the seven categories match the expected counts
     (10/10/10/5/5/5/5). FAILS IF: not, meaning I am scoring a different file than
     Apollo's eval.
  C2 PIPELINE FIDELITY -- every op named in O1's ceiling_pipeline resolves in the
     live REGISTRY. FAILS IF: any missing, meaning my reconstruction is not O1's.
  C3 NON-DEGENERATE SCORING -- the pipeline must not answer identically on every
     task (which would mean it is emitting a constant, and accuracy is meaningless).
     FAILS IF: one distinct answer across all 50.
  C4 CHANCE REFERENCE -- chance is computed from the actual candidate counts, not
     assumed to be 0.25. FAILS IF: candidate counts vary and a flat 0.25 is used.

NULL OUTPUT OF EVERY RULE:
  - a category where the pipeline scores at or below its own chance is UNSOLVED;
  - a category above chance is PARTIALLY SOLVED and is not evidence of a boolean op;
  - if comparison ops score at chance on the boolean categories, the claim "no
    boolean primitive" is CONFIRMED BY MEASUREMENT;
  - if they score well above chance, the claim is REFUTED and the target voids.

SCOPE: the canary subset only, 50 tasks, single deterministic file. Says nothing
about synth/inference/cross_tier and nothing about the selector experiment.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(r'F:\Prometheus')
sys.path.insert(0, str(ROOT / 'apollo' / 'src'))
sys.path.insert(0, str(ROOT / 'apollo' / 'scripts'))

from blackboard import BlackboardState, run_pipeline          # noqa: E402
import blackboard_evolve as BE                                 # noqa: E402

CEILING = ['parse_box_items', 'op_aggregate_quantities', 'parse_comparison',
           'parse_names_and_relations', 'parse_ordinal', 'parse_rules', 'forward_chain',
           'parse_which_extreme', 'relations_from_facts', 'op_build_ordering',
           'score_by_aggregate__g', 'score_by_comparison__g', 'score_by_derivability__g',
           'score_by_extreme_number__g', 'select_nth__g']

print("CYCLE 154-S — canary per-category, by execution")
print("=" * 74)

REG = BE.REGISTRY
missing = [n for n in CEILING if n not in REG]
C2 = not missing
print(f"C2 pipeline fidelity: {len(CEILING)-len(missing)}/{len(CEILING)} ops resolve"
      + (f"  MISSING {missing}" if missing else "") + f" -> {C2}")

tasks = json.loads((ROOT / 'apollo/data/clean_canary_v01.json').read_text(encoding='utf-8'))['tasks']
cats = collections.Counter(t.get('category') for t in tasks)
bad = sum(1 for t in tasks if t.get('correct') not in t.get('candidates', []))
EXPECT = {'numeric_comparison': 10, 'numeric_stated_premise': 10, 'transitivity': 10,
          'all_but_n': 5, 'temporal_ordering': 5, 'vacuous_truth': 5, 'consistency_check': 5}
C1 = (len(tasks) == 50 and bad == 0 and dict(cats) == EXPECT)
print(f"C1 task-file fidelity: {len(tasks)} tasks, {bad} with correct-not-in-candidates, "
      f"categories match expected -> {C1}")
print(f"   categories: {dict(cats)}")

ncand = collections.Counter(len(t.get('candidates', [])) for t in tasks)
print(f"C4 candidate counts: {dict(ncand)}  (chance computed per task, not assumed)")
C4 = True

pipe = [REG[n][0] for n in CEILING]


def run(pipeline, task):
    st = BlackboardState(problem_text=task['prompt'], candidates=task['candidates'])
    st = run_pipeline(pipeline, st)
    return getattr(st, 'selected_answer', None)


# ---- (a) full ceiling pipeline, per category
per = collections.defaultdict(lambda: {'n': 0, 'hit': 0, 'chance': 0.0, 'ans': set()})
answers = set()
for t in tasks:
    a = run(pipe, t)
    c = per[t['category']]
    c['n'] += 1
    c['hit'] += (a == t['correct'])
    c['chance'] += 1.0 / max(len(t['candidates']), 1)
    c['ans'].add(a)
    answers.add(a)
C3 = len(answers) > 1
print(f"C3 non-degenerate scoring: {len(answers)} distinct answers across 50 tasks -> {C3}")

tot_hit = sum(c['hit'] for c in per.values())
tot_ch = sum(c['chance'] for c in per.values())
print(f"\n(a) FULL O1 CEILING PIPELINE over clean_canary_v01.json")
print(f"    OVERALL {tot_hit}/50 = {tot_hit/50:.4f}   (O1 reports canary 0.6)   "
      f"chance {tot_ch/50:.4f}")
print(f"    {'category':24s} {'n':>3s} {'acc':>7s} {'chance':>7s}  verdict")
for cat in EXPECT:
    c = per[cat]
    acc = c['hit'] / max(c['n'], 1)
    ch = c['chance'] / max(c['n'], 1)
    verd = 'UNSOLVED (<=chance)' if acc <= ch + 1e-9 else 'partially/fully solved'
    print(f"    {cat:24s} {c['n']:>3d} {acc:>7.4f} {ch:>7.4f}  {verd}")

# ---- (b) can the EXISTING comparison ops answer the boolean items?
BOOLCATS = ['numeric_comparison', 'vacuous_truth', 'consistency_check']
cmp_pipe_names = ['parse_comparison', 'score_by_comparison__g']
cmp_pipe = [REG[n][0] for n in cmp_pipe_names if n in REG]
print(f"\n(b) EXISTING COMPARISON OPS ALONE: {cmp_pipe_names}")
print(f"    {'category':24s} {'n':>3s} {'acc':>7s} {'chance':>7s}  {'fired':>6s}")
bool_solved = {}
for cat in BOOLCATS:
    sub = [t for t in tasks if t['category'] == cat]
    hit = 0
    ch = 0.0
    fired = 0
    for t in sub:
        st = BlackboardState(problem_text=t['prompt'], candidates=t['candidates'])
        for name, op in zip(cmp_pipe_names, cmp_pipe):
            pre = getattr(op, 'precondition', None)
            if name.endswith('__g') and pre is not None:
                try:
                    if pre(st):
                        fired += 1
                except Exception:
                    pass
            st = op(st)
        hit += (getattr(st, 'selected_answer', None) == t['correct'])
        ch += 1.0 / max(len(t['candidates']), 1)
    acc = hit / max(len(sub), 1)
    chv = ch / max(len(sub), 1)
    bool_solved[cat] = {'n': len(sub), 'acc': acc, 'chance': chv, 'scorer_fired': fired}
    print(f"    {cat:24s} {len(sub):>3d} {acc:>7.4f} {chv:>7.4f}  {fired:>6d}")

above = [c for c, v in bool_solved.items() if v['acc'] > v['chance'] + 1e-9]
BOOLEAN_GAP_CONFIRMED = (len(above) == 0)
print(f"\n    categories where existing comparison ops beat chance: {above or 'NONE'}")
print(f"    => 'no boolean primitive' CONFIRMED BY MEASUREMENT: {BOOLEAN_GAP_CONFIRMED}")

C = sum([C1, C2, C3, C4])
print(f"\ncontrols passing: {C} of 4")

bool_n = sum(EXPECT[c] for c in BOOLCATS)
print(f"\nMAX MOVABLE FRACTION if a boolean primitive is minted:")
print(f"    boolean-dependent categories {BOOLCATS} = {bool_n}/50 canary tasks")
print(f"    current hits on those: {sum(per[c]['hit'] for c in BOOLCATS)}")
print(f"    headroom on canary: {(bool_n - sum(per[c]['hit'] for c in BOOLCATS))/50:.4f}")

out = {'cycle': '154-S',
       'controls': {'C1_task_file_fidelity': C1, 'C2_pipeline_fidelity': C2,
                    'C3_non_degenerate': C3, 'C4_chance_per_task': C4,
                    'distinct_answers': len(answers)},
       'controls_passing': C,
       'canary_overall_acc': tot_hit / 50, 'canary_overall_chance': tot_ch / 50,
       'o1_reported_canary': 0.6,
       'per_category': {k: {'n': per[k]['n'], 'hit': per[k]['hit'],
                            'acc': per[k]['hit'] / max(per[k]['n'], 1),
                            'chance': per[k]['chance'] / max(per[k]['n'], 1)}
                        for k in EXPECT},
       'existing_comparison_ops_on_boolean_cats': bool_solved,
       'categories_beating_chance_with_existing_ops': above,
       'BOOLEAN_GAP_CONFIRMED_BY_MEASUREMENT': BOOLEAN_GAP_CONFIRMED,
       'boolean_dependent_tasks': bool_n,
       'max_movable_fraction_of_canary': (bool_n - sum(per[c]['hit'] for c in BOOLCATS)) / 50}
(ROOT / 'aporia/search/cycle_154s_results.json').write_text(json.dumps(out, indent=1),
                                                            encoding='utf-8')
print("\n*** written: aporia/search/cycle_154s_results.json ***")
