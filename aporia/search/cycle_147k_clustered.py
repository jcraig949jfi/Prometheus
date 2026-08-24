"""CYCLE 147-K — the effect was an SE artifact. Corrected unit of analysis.

=============================== PREREGISTRATION ===============================
Committed BEFORE the corrected numbers are computed.

WHAT THIS PASS WAS SENT TO DO, and why it changed. 146-J terminated REDESIGN with
a shuffled-label null at 0.5903 against chance 0.5029, and diagnosed the cause as
an availability confound. This pass was to replace the null with a stratified
conditional permutation and re-read the headline.

THE DIAGNOSIS WAS WRONG, and verifying it before implementing the fix is what
this pass actually did. Three checks, in order:

  1. The 146-J story said ties would break alphabetically toward `conductor`.
     MEASURED: the shuffled model picks `rank` most often (48,612 of 132,009) and
     within-set score spread is nonzero (median 0.006). Alphabetical tie-breaking
     is NOT what happens.
  2. The 146-J story said the shuffle failed to equalise cells. MEASURED: it
     equalised them correctly — shuffled marginal rates 0.4846 to 0.5150, and
     within-group spreads of 0.0053 to 0.0083, which is sampling noise.
  3. So where does +0.087 come from? MEASURED per group: the shuffled model picks
     ONE invariant for EVERY set in a group, in 14 of 14 groups, and per-group
     deltas are large and bidirectional — ('torsion','abs_diff_le_3') picks rank
     and scores 0.9601 against 0.4635 chance; ('rank','abs_diff_le_3') picks
     conductor and scores 0.0000 against 0.4668.

THE ACTUAL DEFECT, which is methodological rather than a leak: every model here
emits a CONSTANT RANKING PER CELL. M1 emits 4 distinct orderings (one per
availability subset), M4 emits 9 to 14. So the number of independent decisions the
model makes is the number of CELLS, not the number of test sets. Scoring 132,009
sets and computing a binomial SE as if they were independent trials inflates
apparent precision by roughly sqrt(132009/14) ~ 97x.

That is the same error class as this loop's own doctrine on measuring over the
wrong population, applied to the variance rather than the mean.

THE QUESTION THIS PASS NOW ANSWERS: under a CLUSTERED unit of analysis — the cell
being the independent decision — does the state-conditioned model still beat the
context-free one by more than 2 clustered SE?

PREREGISTERED ANALYSIS, fixed before the numbers are seen:
  - unit of analysis = CELL, defined as the (parent_invariant, relation) group for
    M4 and the availability subset for M1. Each cell contributes ONE decision.
  - per-cell statistic = accuracy of that cell's chosen invariant on held-out sets
    in that cell, minus that cell's matched chance.
  - headline = weighted mean of the per-cell deltas, with a CLUSTER-ROBUST SE
    computed across cells: SE = sd(per-cell delta, weighted) / sqrt(n_cells).
  - materiality bar = 2 * clustered SE, computed BEFORE the comparison.
  - the naive per-set SE is also reported, beside, purely to show the inflation.

CONTROLS, each stated WITH the input that would make it FAIL:
  C1 CONSTANT-PER-CELL — every model must be verified to emit one ranking per cell.
     FAILS IF: any cell shows more than one distinct ranking, which would mean the
     clustering unit is wrong and the SE must be recomputed at a finer grain.
  C2 CELL COUNT — the number of cells must be reported and must exceed 3, since a
     clustered SE over fewer is meaningless.
     FAILS IF: n_cells <= 3.
  C3 NULL AT CHANCE UNDER THE CORRECT UNIT — the shuffled-label null's mean
     per-cell delta must be within 3 clustered SE of zero.
     FAILS IF: outside, meaning a genuine leak remains on top of the SE artifact.
  C4 LOUD PARSE ACCOUNTING — every dropped record counted and reported.
     FAILS IF: drops exceed 1%.

ATTAINABILITY as a CONJUNCT: the contrast is readable only if M4 and M1 differ in
at least one cell's chosen invariant. Computed before the verdict.

BRANCHES (partition verified by enumeration with an assert). C = controls passing
(0..4), A = cells where M4 and M1 choose differently, D = weighted mean per-cell
delta of M4 minus M1, SEc = clustered SE:
  B1 VACUOUS  C < 4 or A < 1
  B2 ADVANCE  C == 4 and A >= 1 and D > 2*SEc
  B3 KILL     C == 4 and A >= 1 and D <= 2*SEc

NULL OUTPUT OF EVERY VERDICT RULE:
  - constant-per-cell rule -> a violating cell forces VACUOUS, not a null;
  - attainability rule -> A == 0 gives VACUOUS;
  - headline rule -> D <= 2*SEc is a NULL and is the major result it appears to be.

WHAT A NULL MEANS HERE, stated in advance so it cannot be softened: a model that
emits one ranking per (parent, relation) cell is a 14-entry lookup table. If its
advantage does not survive a clustered SE, then the recorded coordinates carry a
handful of constants rather than state-dependent navigational knowledge. That is
the operator's hypothesis, confirmed, and it must be reported as such.

SCOPE: h4 only, sampled batches, 4-element measurement action space, action is
feature selection rather than mathematical transformation.
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

print("CYCLE 147-K — corrected unit of analysis")
print("=" * 74)
files = sorted(glob.glob(str(ROOT / 'theseus/corpus/*.jsonl')))
recs = []
drop = 0
for F in files[:NBATCH]:
    for line in open(F, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            drop += 1
            continue
        if r.get('generator_id') != 'h4':
            continue
        p = r.get('claim_payload')
        if isinstance(p, str):
            try:
                p = ast.literal_eval(p)
            except Exception:
                drop += 1
                continue
        ex = p.get('extensions') or []
        if not ex or not p.get('parent_record_id'):
            drop += 1
            continue
        recs.append({'pid': p['parent_record_id'], 'pi': p.get('parent_ec_invariant'),
                     'rel': p.get('relation'),
                     'ext': [(e.get('ec_invariant'), bool(e.get('holds'))) for e in ex]})
C4 = drop / max(len(recs) + drop, 1) < 0.01
print(f"batches {NBATCH}/{len(files)} | kept {len(recs):,} | dropped {drop:,} -> C4 {C4}")

disc = [r for r in recs if 0 < sum(h for _, h in r['ext']) < len(r['ext'])]
side = lambda pid: int(hashlib.md5(str(pid).encode()).hexdigest()[:8], 16) % 2
train = [r for r in disc if side(r['pid']) == 0]
test = [r for r in disc if side(r['pid']) == 1]
print(f"discriminative {len(disc):,} of {len(recs):,} | train {len(train):,} test {len(test):,}")


def fit(rows, keyfn):
    num, den = collections.Counter(), collections.Counter()
    for r in rows:
        for inv, h in r['ext']:
            k = keyfn(r, inv)
            den[k] += 1
            num[k] += h
    return {k: num[k] / den[k] for k in den}


K1 = lambda r, i: (i,)
K4 = lambda r, i: (r['pi'], r['rel'], i)
CELL1 = lambda r: tuple(sorted(i for i, _ in r['ext']))     # availability subset
CELL4 = lambda r: (r['pi'], r['rel'])

t1, t4 = fit(train, K1), fit(train, K4)
gr = sum(h for r in train for _, h in r['ext']) / sum(len(r['ext']) for r in train)


def pick(r, tbl, keyfn):
    sc = [(tbl.get(keyfn(r, i), gr), i, h) for i, h in r['ext']]
    sc.sort(key=lambda t: (-t[0], t[1]))
    return sc[0][1], sc[0][2]


def cellstats(tbl, keyfn, cellfn):
    cells = collections.defaultdict(lambda: {'n': 0, 'hit': 0, 'ch': 0.0,
                                             'picks': collections.Counter()})
    for r in test:
        inv, h = pick(r, tbl, keyfn)
        c = cells[cellfn(r)]
        c['n'] += 1
        c['hit'] += h
        c['ch'] += sum(x for _, x in r['ext']) / len(r['ext'])
        c['picks'][inv] += 1
    return cells


cA = cellstats(t4, K4, CELL4)
cB = cellstats(t1, K1, CELL1)
C1 = all(len(c['picks']) == 1 for c in cA.values()) and all(len(c['picks']) == 1 for c in cB.values())
print(f"\nC1 one ranking per cell: M4 cells {len(cA)} | M1 cells {len(cB)} -> {C1}")
C2 = len(cA) > 3
print(f"C2 cell count > 3: M4 has {len(cA)} -> {C2}")


def summarise(cells, label):
    tot = sum(c['n'] for c in cells.values())
    deltas = [((c['hit'] - c['ch']) / c['n'], c['n']) for c in cells.values()]
    mean = sum(d * n for d, n in deltas) / tot
    var = sum(n * (d - mean) ** 2 for d, n in deltas) / tot
    se = math.sqrt(var / len(deltas))
    acc = sum(c['hit'] for c in cells.values()) / tot
    ch = sum(c['ch'] for c in cells.values()) / tot
    print(f"  {label:24s} acc={acc:.4f} chance={ch:.4f} delta={mean:+.4f} "
          f"| clustered SE={se:.4f} over {len(deltas)} cells")
    return mean, se, acc, ch, len(deltas), tot


print("\nPER-CELL SUMMARY (the corrected unit):")
d4, se4, a4, ch4, n4, tot = summarise(cA, 'M4 state-conditioned')
d1, se1, a1, ch1, n1, _ = summarise(cB, 'M1 context-free')

# --- C3 null under the correct unit
rng = random.Random(20260824)
shuf = []
for r in train:
    labs = [h for _, h in r['ext']]
    rng.shuffle(labs)
    shuf.append({**r, 'ext': [(inv, labs[i]) for i, (inv, _) in enumerate(r['ext'])]})
cN = cellstats(fit(shuf, K4), K4, CELL4)
dN, seN, aN, chN, nN, _ = summarise(cN, 'NULL shuffled')
C3 = abs(dN) <= 3 * seN
print(f"C3 null within 3 clustered SE of zero: |{dN:+.4f}| vs {3*seN:.4f} -> {C3}")

# --- attainability and headline
A = 0
for cell, c in cA.items():
    pa = c['picks'].most_common(1)[0][0]
    match = [cb for k, cb in cB.items() if True]
    A += 1 if True else 0
A = sum(1 for r in test if pick(r, t4, K4)[0] != pick(r, t1, K1)[0])
print(f"\nATTAINABILITY: test sets where M4 and M1 choose differently: {A:,} -> readable {A >= 1}")

D = d4 - d1
SEc = math.sqrt(se4 ** 2 + se1 ** 2)
naive_se = math.sqrt(a4 * (1 - a4) / tot)
print(f"\nHEADLINE under the CORRECTED unit:")
print(f"  D = M4 - M1 = {D:+.5f} | clustered SE = {SEc:.5f} | bar 2*SEc = {2*SEc:.5f}")
print(f"  naive per-set SE would have been {naive_se:.5f} — inflation factor "
      f"{SEc/naive_se:.1f}x")
print(f"  clears the bar? {D > 2*SEc}")

C = sum([C1, C2, C3, C4])
print(f"\ncontrols passing: C = {C} of 4")
branches = {'B1_VACUOUS': (C < 4) or (A < 1),
            'B2_ADVANCE': (C == 4) and (A >= 1) and (D > 2 * SEc),
            'B3_KILL':    (C == 4) and (A >= 1) and (D <= 2 * SEc)}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1
VERDICT = fired[0].split('_', 1)[1]

out = {'cycle': '147-K',
       'what_146J_got_wrong': 'the leak diagnosis (alphabetical tie-breaking / failed shuffle) '
                              'was falsified: the shuffle equalised cells correctly (marginals '
                              '0.4846-0.5150, within-group spreads 0.0053-0.0083) and the model '
                              'picks rank most, not conductor',
       'actual_defect': 'every model emits a CONSTANT RANKING PER CELL, so the number of '
                        'independent decisions is the cell count, not the test-set count; a '
                        'binomial SE over 132,009 sets inflates precision by ~97x',
       'bound': {'batches': NBATCH, 'of': len(files)},
       'parse': {'kept': len(recs), 'dropped': drop},
       'discriminative': len(disc), 'train': len(train), 'test': len(test),
       'M4': {'acc': a4, 'chance': ch4, 'per_cell_delta': d4, 'clustered_se': se4, 'cells': n4},
       'M1': {'acc': a1, 'chance': ch1, 'per_cell_delta': d1, 'clustered_se': se1, 'cells': n1},
       'NULL': {'acc': aN, 'per_cell_delta': dN, 'clustered_se': seN, 'cells': nN},
       'controls': {'C1_one_ranking_per_cell': C1, 'C2_cells_gt_3': C2,
                    'C3_null_at_zero_clustered': C3, 'C4_parse_loud': C4},
       'controls_passing': C,
       'attainability_sets_differing': A,
       'D': D, 'clustered_SE': SEc, 'bar_2SE': 2 * SEc, 'naive_se': naive_se,
       'inflation_factor': SEc / naive_se if naive_se else None,
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'scope': 'h4 only; sampled batches; action is feature selection over 4 invariants'}
(ROOT / 'aporia/search/cycle_147k_results.json').write_text(json.dumps(out, indent=1),
                                                            encoding='utf-8')
print(f"\n*** CYCLE 147-K VERDICT: {VERDICT} ***")
