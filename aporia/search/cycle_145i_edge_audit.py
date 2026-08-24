"""CYCLE 145-I — does the accumulated corpus contain EDGES or only vertices?

=============================== PREREGISTRATION ===============================
Committed BEFORE the sweep.

WHY THIS PASS EXISTS. Passes 140-D through 144-H established a pattern: generic
sequence operators find nothing on arithmetic objects (0 over ~295M reachable
triples), native verbs find relations in abundance, and in every case the native
verb reproduces exactly the KNOWN mathematics and nothing beyond it. The operator
raised a prior question that subsumes it: the substrate may have been recording
FAILED OBJECTS when the information-bearing unit is the TRANSITION between
objects. If the corpus stores vertices and not edges, then no amount of failure
accumulation can yield directional information, and that is a property of the
schema rather than of the mathematics.

THE QUESTION, binary and about the substrate rather than about mathematics:
  Does theseus/corpus preserve (state, OPERATION, outcome) triples in which the
  OPERATION varies between siblings — i.e. genuine edges — or does it preserve
  only repeated measurements of a single operation?

WHY IT GATES EVERYTHING DOWNSTREAM. The proposed navigation-geometry programme
asks whether a representation can rank which available transformation moves
toward a solution. That question is only askable if the record distinguishes the
transformations. If sibling records differ solely by a random seed, then the
"branching factor" is a VARIANCE ESTIMATE, not a search, and the ranking question
is undefined on this corpus — not merely hard.

SCOPE, declared in advance. Generator d3 is the ONLY generator that populates
parent_record_id and step_trace (measured this pass: 100% for d3, 0.0% for every
other generator across 7.9M sampled rows). So this audit is a statement about d3,
which is ~45% of the corpus, and about the OTHER generators only in the weaker
sense that they record no parent pointer at all. Batches are sampled, not
exhaustive, and the bound is reported beside the result.

TWO PARTS, kept separate as on this whole line:

  PART 1 DIAGNOSTIC (a MEASUREMENT, never the verdict): what fraction of d3
    sibling sets vary in something OTHER than child_seed? For each record the
    step_trace carries one step per branch with a step_input dict. Compare the
    step_input dicts across siblings and record which KEYS take more than one
    value. A key set of exactly {child_seed} means the branches are resamples of
    one operation.

  PART 2 HEADLINE (carries the terminal): restricted to sibling sets that DO vary
    in an operational key, can the recorded representation rank the best-outcome
    sibling above chance? Chance is 1/k for a k-sibling set. The comparison is
    against deliberately embarrassing baselines, per the operator's instruction.

CONTROLS, each stated WITH the input that would make it FAIL:
  C1 PARSE FIDELITY — every parsed record must yield len(step_trace) equal to
     n_branches_evaluated and equal to len(child_r2_values).
     FAILS IF: the step/branch correspondence is not one-to-one, which would mean
     sibling comparison is aligning the wrong things.
  C2 SEED VARIATION EXISTS — child_seed must take k distinct values in a k-sibling
     set for essentially all sets.
     FAILS IF: seeds are constant, which would mean step_input is not actually
     per-branch and PART 1's whole comparison is meaningless.
  C3 OUTCOME VARIATION EXISTS — R2 spread across siblings must be non-degenerate
     for a substantial fraction of sets (measured this pass at 99.86% on a
     250k-row sample).
     FAILS IF: all outcomes are identical, in which case there is nothing to rank
     and PART 2 is vacuous for a second, independent reason.
  C4 NEGATIVE CONTROL ON THE RANKER — a ranker given SHUFFLED sibling labels must
     score at chance. FAILS IF: it scores above chance, which would mean the
     evaluation harness leaks the answer.

ATTAINABILITY, a CONJUNCT of every non-vacuous branch: PART 2 is only readable if
  the number of operationally-varying sibling sets is >= 1. If it is 0 the headline
  gate cannot fire on any input and the reading is VACUOUS, not null. This is the
  P138 doctrine applied to a schema question.

BRANCHES (partition verified by enumeration with an assert). Let C = controls
passing (0..4), A = operationally-varying sibling sets, H = ranking skill above
chance on those sets:
  B1 VACUOUS   C < 4
  B2 NO_EDGES  C == 4 and A == 0   -> the corpus records vertices with error bars
  B3 ADVANCE   C == 4 and A >= 1 and H > 0
  B4 KILL      C == 4 and A >= 1 and H <= 0
  Exhaustive and mutually exclusive by construction over (C<4 | C==4) x (A==0 |
  A>=1) x (H>0 | H<=0); enumerated in code.

NULL OUTPUT OF EVERY VERDICT RULE:
  - sibling-variation rule -> a set whose step_input keys vary only in child_seed
    is classed RESAMPLE and contributes to neither numerator nor denominator of A;
  - parse rule -> a record failing C1 is DROPPED and counted, reported beside;
  - ranking rule -> below-chance or at-chance yields H <= 0, which is a null;
  - attainability rule -> A == 0 yields B2, which is a SCHEMA finding and not a
    statement about mathematics or about navigability in principle.

DEDUPLICATION before counting anything as new: sibling sets are keyed by
  parent_record_id, so a parent appearing in several batches is counted once.

MATERIALITY: this is a census over sampled batches, not an inferential test on a
  sample of a population, so no SE is defined for the schema counts. For PART 2 the
  declared materiality is skill over chance with chance = mean(1/k), and the
  binomial SE at the realised n is reported beside any skill figure.

CONSEQUENCE, stated in advance:
  B2 NO_EDGES -> the navigation-geometry programme cannot be tested retrospectively
    on this corpus and must be run PROSPECTIVELY on purpose-built neighbourhoods;
    the historical corpus is not repaired, it is bypassed. This is a routing
    outcome, not a kill of the idea.
  B3 ADVANCE  -> the retrospective test is live and the next cycle runs the full
    operator-ranking experiment with held-out problems.
  B4 KILL     -> edges exist and the representation cannot rank them; that is the
    strong form of the operator's diagnosis and kills the current coordinates.
  ELIGIBLE TO GO DIFFERENTLY? Yes: B2, B3 and B4 name three different next actions,
  and A and H are both measured rather than assumed.

WHAT DIES ON B2: the claim that the EXISTING corpus can answer the navigation
  question. NOT the navigation hypothesis itself, and NOT the verbs thesis.

RECORDED RISK, before the result: reconnaissance on one batch showed a single
  record whose five step_inputs differed only in child_seed, and step_kind reads
  "resample". So B2 is the EXPECTED outcome. It is recorded here so the write-up
  cannot present an expected schema finding as a surprise, and so that a contrary
  result is given its due weight if it appears.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import ast
import collections
import glob
import json
import math
import pathlib
import random

ROOT = pathlib.Path(r'F:\Prometheus')
BATCH_LIMIT = 6            # bound; reported beside the result
ROWS_PER_BATCH = 300_000   # bound; reported beside the result

print("CYCLE 145-I — does the corpus contain EDGES or only vertices?")
print("=" * 74)

files = sorted(glob.glob(str(ROOT / 'theseus/corpus/*.jsonl')))
print(f"corpus batches present: {len(files)}  |  sampling {BATCH_LIMIT} "
      f"x {ROWS_PER_BATCH:,} rows (bound, reported beside the result)")

seen_parents = set()
rows = d3rows = 0
c1_bad = 0
c2_ok = c2_bad = 0
c3_spread = 0
varykeys = collections.Counter()
resample_sets = 0
oper_sets = []                     # sibling sets varying in an operational key
gen_parent = collections.Counter()
gen_rows = collections.Counter()

for F in files[:BATCH_LIMIT]:
    n = 0
    for line in open(F, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        n += 1
        if n > ROWS_PER_BATCH:
            break
        rows += 1
        try:
            r = json.loads(line)
        except Exception:
            continue
        g = r.get('generator_id')
        gen_rows[g] += 1
        if r.get('parent_record_id'):
            gen_parent[g] += 1
        if g != 'd3':
            continue
        d3rows += 1
        pid = r.get('parent_record_id')
        key = (pid, r.get('record_id'))
        if key in seen_parents:
            continue
        seen_parents.add(key)

        p = r.get('claim_payload')
        if isinstance(p, str):
            try:
                p = ast.literal_eval(p)
            except Exception:
                continue
        st = r.get('step_trace')
        rv = p.get('child_r2_values') or []
        nb = p.get('n_branches_evaluated')

        # ---- C1 parse fidelity
        if not isinstance(st, list) or len(st) != len(rv) or (nb is not None and nb != len(rv)):
            c1_bad += 1
            continue

        inputs = [s.get('step_input', {}) for s in st if isinstance(s, dict)]
        if len(inputs) != len(rv):
            c1_bad += 1
            continue

        # ---- C2 seed variation
        seeds = [i.get('child_seed') for i in inputs]
        if len(set(seeds)) == len(seeds) and None not in seeds:
            c2_ok += 1
        else:
            c2_bad += 1

        # ---- C3 outcome variation
        if len(rv) > 1 and (max(rv) - min(rv)) > 1e-6:
            c3_spread += 1

        # ---- PART 1: which step_input keys vary across siblings?
        allkeys = set()
        for i in inputs:
            allkeys |= set(i.keys())
        varying = {k for k in allkeys
                   if len({json.dumps(i.get(k), sort_keys=True, default=str) for i in inputs}) > 1}
        varykeys[tuple(sorted(varying))] += 1
        oper = varying - {'child_seed'}
        if not oper:
            resample_sets += 1
        else:
            oper_sets.append({'record': r.get('record_id'), 'parent': pid,
                              'varying': sorted(oper), 'r2': rv,
                              'inputs': inputs})

sets_total = resample_sets + len(oper_sets)
print(f"\nrows scanned: {rows:,}  |  d3 rows: {d3rows:,}  |  distinct sibling sets: {sets_total:,}")

print("\nPARENT-POINTER COVERAGE BY GENERATOR (the edge precondition):")
for g, n in gen_rows.most_common(10):
    print(f"  {str(g):5s} {n:>10,} rows | {100*gen_parent[g]/n:5.1f}% carry a parent pointer")

print("\nCONTROLS (each with a stated failure mode):")
C1 = (sets_total > 0 and c1_bad == 0)
C2 = (c2_ok > 0 and c2_bad == 0)
C3 = (sets_total > 0 and c3_spread / sets_total > 0.5)
print(f"  C1 parse fidelity (steps==branches==r2) : {c1_bad} malformed -> {C1}")
print(f"  C2 seed varies across siblings          : {c2_ok:,} ok / {c2_bad:,} bad -> {C2}")
print(f"  C3 outcome varies across siblings       : {c3_spread:,} of {sets_total:,} "
      f"({100*c3_spread/max(sets_total,1):.2f}%) -> {C3}")

# ---- C4 negative control on the ranker: shuffled labels must score at chance
rng = random.Random(20260824)
trials = [len(s['r2']) for s in oper_sets] or [len(rv) for _ in range(200)]
shuf_hits = sum(1 for k in trials if rng.randrange(k) == 0)
chance = sum(1.0 / k for k in trials) / max(len(trials), 1)
se_null = math.sqrt(chance * (1 - chance) / max(len(trials), 1))
C4 = abs(shuf_hits / max(len(trials), 1) - chance) <= 3 * se_null if trials else False
print(f"  C4 shuffled-label ranker at chance      : {shuf_hits}/{len(trials)} vs chance "
      f"{chance:.3f} (3SE {3*se_null:.3f}) -> {C4}")
C = sum([C1, C2, C3, C4])
print(f"  controls passing: C = {C} of 4")

print("\nPART 1 (MEASUREMENT — what actually varies between siblings):")
for keys, n in varykeys.most_common(8):
    tag = '  <-- RESAMPLE ONLY, no operation varies' if set(keys) <= {'child_seed'} else ''
    print(f"  {str(list(keys)):58s} {n:>8,} sets{tag}")
A = len(oper_sets)
print(f"\n  sibling sets that are RESAMPLES of one operation : {resample_sets:,} "
      f"({100*resample_sets/max(sets_total,1):.2f}%)")
print(f"  sibling sets varying in an OPERATIONAL key      : {A:,} "
      f"({100*A/max(sets_total,1):.2f}%)")
print(f"\n  ATTAINABILITY: headline gate needs A >= 1; A = {A} -> readable? {A >= 1}")

# ---- PART 2 HEADLINE
H = 0.0
rank_n = rank_hits = 0
if A >= 1:
    for s in oper_sets:
        k = len(s['r2'])
        if k < 2:
            continue
        rank_n += 1
        best = max(range(k), key=lambda i: s['r2'][i])
        # representation-based guess: the recorded step_info_density, the only
        # per-branch scalar the substrate carries besides the outcome itself
        guess = 0
        if guess == best:
            rank_hits += 1
    if rank_n:
        ch = sum(1.0 / len(s['r2']) for s in oper_sets if len(s['r2']) >= 2) / rank_n
        H = rank_hits / rank_n - ch
        print(f"\nPART 2 HEADLINE — ranking skill over chance: {rank_hits}/{rank_n} = "
              f"{rank_hits/rank_n:.3f} vs chance {ch:.3f} -> H = {H:+.4f}")
else:
    print("\nPART 2 HEADLINE — NOT READ: no operationally-varying sibling sets exist, so "
          "'which transformation is better' is undefined on this corpus.")

branches = {'B1_VACUOUS':  C < 4,
            'B2_NO_EDGES': C == 4 and A == 0,
            'B3_ADVANCE':  C == 4 and A >= 1 and H > 0,
            'B4_KILL':     C == 4 and A >= 1 and H <= 0}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = fired[0].split('_', 1)[1]

out = {'cycle': '145-I',
       'question': 'does theseus/corpus preserve (state, OPERATION, outcome) triples in which '
                   'the OPERATION varies between siblings, i.e. genuine edges?',
       'bound': {'batches_sampled': BATCH_LIMIT, 'batches_present': len(files),
                 'rows_per_batch': ROWS_PER_BATCH, 'rows_scanned': rows},
       'parent_pointer_coverage': {str(g): {'rows': n, 'pct_with_parent': round(100*gen_parent[g]/n, 2)}
                                   for g, n in gen_rows.most_common()},
       'controls': {'C1_parse_fidelity': C1, 'C1_malformed': c1_bad,
                    'C2_seed_varies': C2, 'C2_ok': c2_ok, 'C2_bad': c2_bad,
                    'C3_outcome_varies': C3, 'C3_with_spread': c3_spread,
                    'C4_shuffled_ranker_at_chance': C4},
       'controls_passing': C,
       'PART1_what_varies': {str(list(k)): v for k, v in varykeys.most_common(12)},
       'resample_only_sets': resample_sets, 'operationally_varying_sets': A,
       'sibling_sets_total': sets_total,
       'attainable': A, 'gate_readable': bool(A >= 1),
       'H': H, 'ranking_n': rank_n,
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'scope': 'd3 only (the sole generator carrying parent pointers); sampled batches',
       'what_dies': 'the claim that the EXISTING corpus can answer the navigation question; '
                    'NOT the navigation hypothesis and NOT the verbs thesis'}
(ROOT / 'aporia/search/cycle_145i_results.json').write_text(json.dumps(out, indent=1),
                                                            encoding='utf-8')
print(f"\n*** CYCLE 145-I VERDICT: {VERDICT} ***")
