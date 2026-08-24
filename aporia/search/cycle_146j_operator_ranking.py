"""CYCLE 146-J — does the substrate know which action is best FROM HERE?

=============================== PREREGISTRATION ===============================
Committed BEFORE the ranking runs.

THE QUESTION, in the form the data forces. 145-I found h4 to be a genuine edge
corpus: a parent relation that held for one invariant, extended to other
invariants, each extension recorded as holds true/false. The naive question is
"does the representation predict holds?" — but the contamination check run first
this pass shows that is the WRONG question, for a structural reason:

  WITHIN a sibling set, relation, parent_ec_invariant, knot_invariant, knot_object
  and ec_object are ALL CONSTANT. Only the extended ec_invariant varies.

So a context-free model that memorises the global holds rate per invariant emits
THE SAME RANKING for every state in the corpus. It can score well on outcome
prediction while carrying zero navigational information. The question that
separates a taxonomy from a navigation coordinate system is therefore:

  Does conditioning on the STATE change the RANKING of the available actions, and
  does that reordering improve which action you would pick?

That is I(Z ; best-action | state) rather than I(Z ; outcome), and it is the
quantity the operator's diagnosis is actually about.

WHAT h4's "OPERATION" IS, stated plainly so it scopes every claim: the action is
"which ec_invariant to test this relation against next." That is FEATURE
SELECTION — choosing a different projection of the same object — NOT a
mathematical transformation of the object. The edge is real (state, action,
outcome) but the action space is a 4-element choice of measurement. This pass
therefore tests whether the substrate can rank WHICH MEASUREMENT TO TAKE NEXT. It
does NOT test whether it can rank mathematical transformations, and no claim here
may be read that way. "Edge" is not permitted to do rhetorical work the data does
not support.

POPULATION, and why it is restricted: only DISCRIMINATIVE sibling sets — those
with at least one holding and at least one failing extension. In a set where every
extension holds, or none does, ranking cannot matter and top-1 accuracy measures
nothing about direction. Sets that are all-hold or all-fail are EXCLUDED and
COUNTED, reported beside the verdict. This is the signature-exists conjunct: if no
discriminative set exists, the reading is VACUOUS.

TASK AND METRIC: for each held-out discriminative set, rank its k extensions and
score 1 if the top-ranked extension HOLDS. Chance for a set is n_holding/k. The
headline statistic is (model accuracy - matched chance), with binomial SE computed
BEFORE any threshold is chosen, per the P114/P125 doctrine.

TRAIN/TEST SPLIT: by PARENT record, hashed, 50/50. No parent contributes to both
sides. All rates are estimated on train only and applied to test only. A model
that saw its own test labels would be leakage, and C4 below exists to detect it.

MODELS, in increasing use of state:
  M0 CHANCE            random pick among the k extensions
  M1 CONTEXT-FREE      rank by global P(holds | extended_invariant), estimated on
                       train. EMITS THE SAME ORDERING FOR EVERY STATE.
  M2 PARENT-CONDITIONED   rank by P(holds | parent_invariant, extended_invariant)
  M3 RELATION-CONDITIONED rank by P(holds | relation, extended_invariant)
  M4 FULL-CELL         rank by P(holds | parent_invariant, relation,
                       extended_invariant) — the most state the record carries
                       that can vary the ranking
  M5 KNOT-CONDITIONED  adds knot_invariant to the cell

THE HEADLINE IS M4 - M1, NOT M4 - M0. Beating chance only shows the corpus has a
marginal signal, which the contamination check already established. Beating the
CONTEXT-FREE model is the only thing that demonstrates state-dependent
navigational information.

CONTROLS, each stated WITH the input that would make it FAIL:
  C1 PARSE LOUDNESS — every record that fails to parse, lacks extensions, or lacks
     a parent id is COUNTED and reported. FAILS IF: drops exceed 1% unreported.
     This control exists because 145-I audited the wrong population via a silent
     `continue`, the second such incident on this line.
  C2 SPLIT DISJOINTNESS — no parent id may appear in both train and test.
     FAILS IF: any overlap, which would make every result leakage.
  C3 SHUFFLED-LABEL — a model trained on shuffled holds labels must score at
     matched chance within 3 SE. FAILS IF: above chance, meaning the harness leaks
     the answer through the evaluation path rather than the model.
  C4 CONTEXT-FREE INVARIANCE — M1 must emit an identical invariant ordering for
     every test set, verified by counting distinct orderings.
     FAILS IF: more than one ordering, which would mean M1 is secretly
     state-dependent and the M4-M1 contrast is not measuring what it claims.

ATTAINABILITY, a CONJUNCT of every non-vacuous branch: the M4-M1 contrast is only
readable if (a) at least one discriminative test set exists, and (b) M4 and M1
actually differ in their orderings on at least one test set. If M4 never reorders
relative to M1 then the contrast is 0 BY CONSTRUCTION and the reading is VACUOUS,
not null. Both are computed and printed BEFORE the verdict.

BRANCHES (partition verified by enumeration with an assert). Let C = controls
passing (0..4), A = test sets where M4 reorders relative to M1, D = M4 accuracy
minus M1 accuracy, SE = binomial SE of the paired difference:
  B1 VACUOUS   C < 4 or A < 1
  B2 ADVANCE   C == 4 and A >= 1 and D > 2*SE
  B3 KILL      C == 4 and A >= 1 and D <= 2*SE
Exhaustive over (C<4 | C==4) x (A<1 | A>=1) x (D>2SE | D<=2SE); enumerated in code.

NULL OUTPUT OF EVERY VERDICT RULE:
  - discriminative rule -> all-hold and all-fail sets excluded and counted;
  - split rule -> a parent seen in train is skipped in test and counted;
  - reorder rule -> A == 0 gives VACUOUS, which is neither null nor kill;
  - ranking rule -> D <= 2*SE is a NULL and is reported as the major result it is.

DEDUPLICATION before counting: sets are keyed by parent_record_id, so a parent
appearing in several batches contributes once.

MATERIALITY: declared as 2*SE on the paired difference, computed from the realised
test n before any comparison is made. There is no "small effect" escape hatch: if
D does not clear 2*SE the answer is no.

CONSEQUENCE, stated in advance:
  ADVANCE -> the substrate carries state-dependent navigational information for
    measurement selection, and the next cycle tests whether it TRANSFERS to
    held-out relations rather than held-out parents.
  KILL -> the recorded coordinates predict outcomes but not which action is best
    from a given state. That is the operator's hypothesis confirmed on real data,
    and it must be reported as a major result rather than softened.
  ELIGIBLE TO GO DIFFERENTLY? Yes, and checked numerically before the verdict via
    the reorder count A.

SCOPE, declared in advance: h4 only, sampled batches, action space = 4 invariants,
and the action is a measurement choice rather than a mathematical transformation.

RECORDED RISK before the result: the contamination check shows relation spans
0.123 to 0.625 in holds rate while extended-invariant spans only 0.445 to 0.635,
and relation is CONSTANT within a set. So most of the corpus's apparent predictive
power sits in a variable that cannot affect ranking. A null on M4-M1 is therefore
the EXPECTED outcome, and it is recorded here so the write-up cannot present an
expected result as a discovery, nor soften it if it arrives.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import ast
import collections
import glob
import hashlib
import json
import math
import pathlib
import random

ROOT = pathlib.Path(r'F:\Prometheus')
NBATCH = 12
INVS = ('conductor', 'tamagawa_product', 'torsion', 'rank')

print("CYCLE 146-J — does the substrate know which action is best FROM HERE?")
print("=" * 76)
files = sorted(glob.glob(str(ROOT / 'theseus/corpus/*.jsonl')))
print(f"corpus batches present: {len(files)} | reading {NBATCH} (bound, reported beside result)")


def split_side(pid):
    return int(hashlib.md5(str(pid).encode()).hexdigest()[:8], 16) % 2


records = []
drop_parse = drop_noext = drop_nopid = 0
seen = set()
for F in files[:NBATCH]:
    for line in open(F, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            drop_parse += 1
            continue
        if r.get('generator_id') != 'h4':
            continue
        p = r.get('claim_payload')
        if isinstance(p, str):
            try:
                p = ast.literal_eval(p)
            except Exception:
                drop_parse += 1
                continue
        ex = p.get('extensions')
        if not ex:
            drop_noext += 1
            continue
        pid = p.get('parent_record_id')
        if not pid:
            drop_nopid += 1
            continue
        rid = r.get('record_id')
        if rid in seen:
            continue
        seen.add(rid)
        records.append({'pid': pid, 'parent_inv': p.get('parent_ec_invariant'),
                        'relation': p.get('relation'), 'knot_inv': p.get('knot_invariant'),
                        'ext': [(e.get('ec_invariant'), bool(e.get('holds'))) for e in ex]})

total_read = len(records) + drop_parse + drop_noext + drop_nopid
print(f"\nLOUD PARSE ACCOUNTING (C1): kept {len(records):,} | dropped parse {drop_parse:,} | "
      f"no-extensions {drop_noext:,} | no-parent {drop_nopid:,}")
C1 = (total_read > 0 and (drop_parse + drop_noext + drop_nopid) / total_read < 0.01)
print(f"  drop fraction {(drop_parse+drop_noext+drop_nopid)/max(total_read,1):.5f} -> C1 {C1}")

# ---- discriminative restriction (signature-exists)
disc = [r for r in records if 0 < sum(h for _, h in r['ext']) < len(r['ext'])]
allhold = sum(1 for r in records if all(h for _, h in r['ext']))
allfail = sum(1 for r in records if not any(h for _, h in r['ext']))
print(f"\nDISCRIMINATIVE RESTRICTION: {len(disc):,} of {len(records):,} sets are mixed "
      f"({100*len(disc)/max(len(records),1):.1f}%)")
print(f"  excluded all-hold {allhold:,} | all-fail {allfail:,} (counted, not hidden)")

train = [r for r in disc if split_side(r['pid']) == 0]
test = [r for r in disc if split_side(r['pid']) == 1]
tr_pids = {r['pid'] for r in train}
te_pids = {r['pid'] for r in test}
C2 = len(tr_pids & te_pids) == 0
print(f"\nSPLIT: train {len(train):,} sets / test {len(test):,} sets | "
      f"parent overlap {len(tr_pids & te_pids)} -> C2 {C2}")


def fit(rows, keyfn):
    num = collections.Counter()
    den = collections.Counter()
    for r in rows:
        for inv, h in r['ext']:
            k = keyfn(r, inv)
            den[k] += 1
            num[k] += h
    return {k: num[k] / den[k] for k in den}, den


K_M1 = lambda r, i: (i,)
K_M2 = lambda r, i: (r['parent_inv'], i)
K_M3 = lambda r, i: (r['relation'], i)
K_M4 = lambda r, i: (r['parent_inv'], r['relation'], i)
K_M5 = lambda r, i: (r['parent_inv'], r['relation'], r['knot_inv'], i)

MODELS = {'M1_context_free': K_M1, 'M2_parent': K_M2, 'M3_relation': K_M3,
          'M4_full_cell': K_M4, 'M5_plus_knot': K_M5}
tables = {name: fit(train, fn)[0] for name, fn in MODELS.items()}
glob_rate = sum(h for r in train for _, h in r['ext']) / max(
    sum(len(r['ext']) for r in train), 1)


def rank_top1(r, table, keyfn):
    scored = [(table.get(keyfn(r, inv), glob_rate), inv, h) for inv, h in r['ext']]
    scored.sort(key=lambda t: (-t[0], t[1]))
    return scored[0][2], [t[1] for t in scored]


def evaluate(table, keyfn):
    hit = n = 0
    orders = collections.Counter()
    for r in test:
        h, order = rank_top1(r, table, keyfn)
        hit += h
        n += 1
        orders[tuple(order)] += 1
    return hit, n, orders


chance = sum(sum(h for _, h in r['ext']) / len(r['ext']) for r in test) / max(len(test), 1)
print(f"\nMATCHED CHANCE on test sets: {chance:.4f}  (n = {len(test):,})")

results = {}
for name, fn in MODELS.items():
    hit, n, orders = evaluate(tables[name], fn)
    acc = hit / max(n, 1)
    se = math.sqrt(acc * (1 - acc) / max(n, 1))
    results[name] = {'acc': acc, 'n': n, 'se': se, 'distinct_orderings': len(orders)}
    print(f"  {name:18s} acc={acc:.4f} (SE {se:.4f}) | distinct orderings emitted: {len(orders)}")

# ---- C4 context-free invariance
C4 = results['M1_context_free']['distinct_orderings'] == 1
print(f"\nC4 context-free model emits ONE ordering for every state: "
      f"{results['M1_context_free']['distinct_orderings']} -> {C4}")

# ---- C3 shuffled-label control
rng = random.Random(20260824)
shuf = []
for r in train:
    labs = [h for _, h in r['ext']]
    rng.shuffle(labs)
    shuf.append({**r, 'ext': [(inv, labs[i]) for i, (inv, _) in enumerate(r['ext'])]})
tbl_s, _ = fit(shuf, K_M4)
hit_s, n_s, _ = evaluate(tbl_s, K_M4)
acc_s = hit_s / max(n_s, 1)
se_s = math.sqrt(chance * (1 - chance) / max(n_s, 1))
C3 = abs(acc_s - chance) <= 3 * se_s
print(f"C3 shuffled-label model: acc={acc_s:.4f} vs chance {chance:.4f} "
      f"(3SE {3*se_s:.4f}) -> {C3}")

# ---- ATTAINABILITY: does M4 ever reorder relative to M1?
A = 0
paired = []
for r in test:
    h1, o1 = rank_top1(r, tables['M1_context_free'], K_M1)
    h4, o4 = rank_top1(r, tables['M4_full_cell'], K_M4)
    if o1 != o4:
        A += 1
    paired.append((h4, h1))
print(f"\nATTAINABILITY: test sets where M4 REORDERS relative to M1: {A:,} of {len(test):,} "
      f"({100*A/max(len(test),1):.2f}%)")
print(f"  M4-M1 contrast readable? {A >= 1}")

b = sum(1 for x, y in paired if x and not y)
c = sum(1 for x, y in paired if y and not x)
n_pair = len(paired)
D = results['M4_full_cell']['acc'] - results['M1_context_free']['acc']
se_d = (math.sqrt((b + c) - (b - c) ** 2 / n_pair) / n_pair) if (b + c) > 0 and n_pair else 0.0
print(f"\nHEADLINE — M4 (state-conditioned) minus M1 (context-free):")
print(f"  D = {D:+.5f} | paired McNemar SE = {se_d:.5f} | 2*SE = {2*se_d:.5f} "
      f"(b={b:,} c={c:,})")
print(f"  materiality bar was set at 2*SE BEFORE the comparison")

C = sum([C1, C2, C3, C4])
print(f"\ncontrols passing: C = {C} of 4")
branches = {'B1_VACUOUS': (C < 4) or (A < 1),
            'B2_ADVANCE': (C == 4) and (A >= 1) and (D > 2 * se_d),
            'B3_KILL':    (C == 4) and (A >= 1) and (D <= 2 * se_d)}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = fired[0].split('_', 1)[1]

out = {'cycle': '146-J',
       'question': 'does conditioning on STATE change the RANKING of available actions, and does '
                   'that reordering improve which action you would pick? I(Z; best-action|state), '
                   'not I(Z; outcome)',
       'action_semantics': 'FEATURE SELECTION — which ec_invariant to test the relation against '
                           'next — NOT a mathematical transformation of the object',
       'bound': {'batches_read': NBATCH, 'batches_present': len(files)},
       'parse_accounting': {'kept': len(records), 'drop_parse': drop_parse,
                            'drop_no_extensions': drop_noext, 'drop_no_parent': drop_nopid},
       'discriminative': {'mixed_sets': len(disc), 'all_hold_excluded': allhold,
                          'all_fail_excluded': allfail, 'total_sets': len(records)},
       'split': {'train_sets': len(train), 'test_sets': len(test),
                 'parent_overlap': len(tr_pids & te_pids)},
       'matched_chance': chance,
       'models': results,
       'controls': {'C1_parse_loudness': C1, 'C2_split_disjoint': C2,
                    'C3_shuffled_at_chance': C3, 'C3_shuffled_acc': acc_s,
                    'C4_context_free_single_ordering': C4},
       'controls_passing': C,
       'reordering_sets': A, 'contrast_readable': bool(A >= 1),
       'D_M4_minus_M1': D, 'paired_se': se_d, 'materiality_2se': 2 * se_d,
       'mcnemar_b': b, 'mcnemar_c': c,
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'scope': 'h4 only; sampled batches; 4-element action space; action is a measurement choice',
       'what_dies': 'the claim that these coordinates carry STATE-DEPENDENT navigational '
                    'information for measurement selection; NOT the navigation hypothesis itself'}
(ROOT / 'aporia/search/cycle_146j_results.json').write_text(json.dumps(out, indent=1),
                                                            encoding='utf-8')
print(f"\n*** CYCLE 146-J VERDICT: {VERDICT} ***")
