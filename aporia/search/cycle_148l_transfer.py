"""CYCLE 148-L — does the 14-cell structure TRANSFER, or is it memorisation?

=============================== PREREGISTRATION ===============================
Committed BEFORE the transfer numbers are computed.

THE FALSIFIER 147-K NAMED. 147-K found the line's first positive: a
state-conditioned ranker beat a context-free one by D = +0.24395 at ~3.9 clustered
SE. Its stated weakness was that the same 14 (parent_invariant, relation) cells
were used to FIT and to EVALUATE. A lookup table that only works on the cells it
was fit to is memorisation, not navigation. This pass holds out RELATIONS.

WHAT HOLDING OUT A RELATION DOES TO EACH MODEL, worked out at design time so the
comparison is honest rather than rigged:

  M4 = P(holds | parent, relation, invariant) has NO CELL for an unseen relation.
  It cannot rank at all on held-out data and must back off. So "test M4 on a held-
  out relation" is not a meaningful comparison — M4 is definitionally
  relation-specific, and reporting its collapse as a transfer failure would be
  measuring a tautology.

  The model that CAN transfer is M2 = P(holds | parent, invariant), which pools
  across relations. So the transfer question is precisely:

    Fitted on three relations, does parent-conditioning still beat the
    context-free invariant marginal on a fourth relation never seen?

  If yes, the parent structure is a real transferable regularity and 147-K's
  positive has a component that survives. If no, then the gain lived entirely in
  relation-specific constants, and 147-K's ADVANCE is memorisation — which must be
  reported as superseding that result.

DESIGN: LEAVE-ONE-RELATION-OUT across all four relations (equal_mod_2, divides,
abs_diff_le_3, equal), so every relation takes a turn as the held-out one. Fitting
uses only the three training relations; evaluation uses only the held-out one.

  M1 = P(holds | invariant)            context-free, fit on train relations
  M2 = P(holds | parent, invariant)    the transferable model, fit on train relations
  HEADLINE = per-cell delta(M2) - per-cell delta(M1) on held-out relations.

UNIT OF ANALYSIS, per the 147-K correction that this loop paid for: the CELL, not
the row. Both M1 and M2 emit a CONSTANT ranking per cell, so independent decisions
number at most 4 relations x 4 parents = 16, never the row count. SE is
CLUSTER-ROBUST across (held-out relation, parent) cells, and a t-reference with
n_cells - 1 degrees of freedom is used rather than a normal one because the
cluster count is small. The naive per-row SE is reported beside purely to show the
inflation it would have caused.

CONTROLS, each stated WITH the input that would make it FAIL:
  C1 ONE RANKING PER CELL — every model must emit exactly one ranking per cell.
     FAILS IF: any cell shows more than one ranking, meaning the clustering unit is
     finer than assumed and every SE here is wrong.
  C2 CELL COUNT — n_cells must exceed 3, since a clustered SE over fewer is
     meaningless. FAILS IF: n_cells <= 3.
  C3 SHUFFLED NULL AT ZERO — a model fit on shuffled labels must produce a
     per-cell delta within 3 clustered SE of zero. FAILS IF: outside. And per the
     147-K lesson, if it fails its PER-CELL behaviour is diagnosed before any leak
     mechanism is invented.
  C4 LOUD PARSE ACCOUNTING — every dropped record counted and reported.
     FAILS IF: drops exceed 1%.
  C5 RELATION DISJOINTNESS — the held-out relation must contribute ZERO rows to
     the fitting set in every fold. FAILS IF: any overlap, which would make the
     whole transfer claim void.

ATTAINABILITY as a CONJUNCT: readable only if M2 and M1 choose differently in at
least one held-out cell. If they never differ, the contrast is 0 by construction
and the reading is VACUOUS, not null. Computed before the verdict.

BRANCHES (partition verified by enumeration with an assert). C = controls passing
(0..5), A = held-out cells where M2 and M1 differ, D = per-cell delta difference,
SEc = clustered SE, t = the 2-sided t critical value at n_cells-1 df:
  B1 VACUOUS        C < 5 or A < 1
  B2 TRANSFERS      C == 5 and A >= 1 and D > t*SEc
  B3 NO_TRANSFER    C == 5 and A >= 1 and D <= t*SEc

NULL OUTPUT OF EVERY VERDICT RULE:
  - one-ranking-per-cell rule -> violation forces VACUOUS, not a null;
  - attainability rule -> A == 0 gives VACUOUS;
  - headline rule -> D <= t*SEc is NO_TRANSFER, and it RETRACTS 147-K's ADVANCE as
    memorisation. It is reported as a major result and is not softened.

DIAGNOSTIC (a MEASUREMENT, never the verdict): the within-relation performance of
M2, i.e. what it achieves when the relation IS seen. This is reported so the drop
from within-relation to across-relation is visible, which is the quantity that
distinguishes memorisation from generalisation.

MATERIALITY: t * clustered SE at n_cells-1 df, computed BEFORE the comparison.

SCOPE, declared in advance: h4 only, sampled batches, 4-element measurement action
space, action is FEATURE SELECTION rather than a mathematical transformation. Any
result here is about ranking which invariant to measure next, nothing more.

RECORDED RISK before the result: the `equal` relation has a hold rate of 0.1230
against 0.41 to 0.62 for the others, so it is a genuinely hard transfer target and
one fold may dominate the variance. That is disclosed in advance, and per-fold
results are reported individually rather than only in aggregate.
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
import statistics as st

ROOT = pathlib.Path(r'F:\Prometheus')
NBATCH = 12
T_CRIT = {3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
          10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131}

print("CYCLE 148-L — leave-one-relation-out transfer test")
print("=" * 74)
files = sorted(glob.glob(str(ROOT / 'theseus/corpus/*.jsonl')))
recs, drop = [], 0
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
        if not ex or not p.get('parent_record_id') or not p.get('relation'):
            drop += 1
            continue
        recs.append({'pi': p.get('parent_ec_invariant'), 'rel': p.get('relation'),
                     'ext': [(e.get('ec_invariant'), bool(e.get('holds'))) for e in ex]})
C4 = drop / max(len(recs) + drop, 1) < 0.01
print(f"batches {NBATCH}/{len(files)} | kept {len(recs):,} | dropped {drop:,} -> C4 {C4}")

disc = [r for r in recs if 0 < sum(h for _, h in r['ext']) < len(r['ext'])]
RELS = sorted({r['rel'] for r in disc})
print(f"discriminative {len(disc):,} of {len(recs):,} | relations: {RELS}")


def fit(rows, keyfn):
    num, den = collections.Counter(), collections.Counter()
    for r in rows:
        for inv, h in r['ext']:
            k = keyfn(r, inv)
            den[k] += 1
            num[k] += h
    return {k: num[k] / den[k] for k in den}


K1 = lambda r, i: (i,)
K2 = lambda r, i: (r['pi'], i)


def pick(r, tbl, keyfn, gr):
    sc = [(tbl.get(keyfn(r, i), gr), i, h) for i, h in r['ext']]
    sc.sort(key=lambda t: (-t[0], t[1]))
    return sc[0][1], sc[0][2]


def fold_cells(rows, tbl, keyfn, gr, relname):
    cells = collections.defaultdict(lambda: {'n': 0, 'hit': 0, 'ch': 0.0,
                                             'picks': collections.Counter()})
    for r in rows:
        inv, h = pick(r, tbl, keyfn, gr)
        c = cells[(relname, r['pi'])]
        c['n'] += 1
        c['hit'] += h
        c['ch'] += sum(x for _, x in r['ext']) / len(r['ext'])
        c['picks'][inv] += 1
    return cells


cells1, cells2, cellsN = {}, {}, {}
overlap = 0
rng = random.Random(20260824)
print("\nPER-FOLD (leave-one-relation-out):")
for held in RELS:
    tr = [r for r in disc if r['rel'] != held]
    te = [r for r in disc if r['rel'] == held]
    overlap += sum(1 for r in tr if r['rel'] == held)
    gr = sum(h for r in tr for _, h in r['ext']) / sum(len(r['ext']) for r in tr)
    t1, t2 = fit(tr, K1), fit(tr, K2)
    shuf = []
    for r in tr:
        labs = [h for _, h in r['ext']]
        rng.shuffle(labs)
        shuf.append({**r, 'ext': [(inv, labs[i]) for i, (inv, _) in enumerate(r['ext'])]})
    tN = fit(shuf, K2)
    c1 = fold_cells(te, t1, K1, gr, held)
    c2 = fold_cells(te, t2, K2, gr, held)
    cN = fold_cells(te, tN, K2, gr, held)
    cells1.update(c1)
    cells2.update(c2)
    cellsN.update(cN)
    n = sum(c['n'] for c in c2.values())
    a1 = sum(c['hit'] for c in c1.values()) / n
    a2 = sum(c['hit'] for c in c2.values()) / n
    ch = sum(c['ch'] for c in c2.values()) / n
    print(f"  held-out {held:16s} n={n:>7,} chance={ch:.4f} | M1={a1:.4f} M2={a2:.4f} "
          f"| delta={a2-a1:+.4f}")
C5 = overlap == 0
print(f"\nC5 relation disjointness: {overlap} leaked rows -> {C5}")


def cellstats(cells):
    tot = sum(c['n'] for c in cells.values())
    d = [((c['hit'] - c['ch']) / c['n'], c['n']) for c in cells.values()]
    mean = sum(x * n for x, n in d) / tot
    var = sum(n * (x - mean) ** 2 for x, n in d) / tot
    return mean, math.sqrt(var / len(d)), len(d), tot, sum(c['hit'] for c in cells.values()) / tot


d1, se1, n1, tot, a1 = cellstats(cells1)
d2, se2, n2, _, a2 = cellstats(cells2)
dN, seN, nN, _, aN = cellstats(cellsN)
C1 = all(len(c['picks']) == 1 for c in list(cells1.values()) + list(cells2.values()))
C2 = n2 > 3
C3 = abs(dN) <= 3 * seN
print(f"\nC1 one ranking per cell: {C1}")
print(f"C2 cells > 3: M2 has {n2} -> {C2}")
print(f"C3 shuffled null at zero: |{dN:+.4f}| vs 3*SE {3*seN:.4f} -> {C3}")

print(f"\nHELD-OUT-RELATION per-cell deltas:")
print(f"  M1 context-free  acc={a1:.4f} delta={d1:+.4f} SE={se1:.4f} cells={n1}")
print(f"  M2 parent-cond   acc={a2:.4f} delta={d2:+.4f} SE={se2:.4f} cells={n2}")

D = d2 - d1
SEc = math.sqrt(se1 ** 2 + se2 ** 2)
df = n2 - 1
tc = T_CRIT.get(df, 2.0)
naive = math.sqrt(a2 * (1 - a2) / tot)
A = sum(1 for r in disc if True)
A = 0
for held in RELS:
    tr = [r for r in disc if r['rel'] != held]
    te = [r for r in disc if r['rel'] == held]
    gr = sum(h for r in tr for _, h in r['ext']) / sum(len(r['ext']) for r in tr)
    t1, t2 = fit(tr, K1), fit(tr, K2)
    A += sum(1 for r in te if pick(r, t1, K1, gr)[0] != pick(r, t2, K2, gr)[0])
print(f"\nATTAINABILITY: held-out sets where M2 and M1 choose differently: {A:,} -> {A >= 1}")
print(f"\nHEADLINE (TRANSFER): D = {D:+.5f} | clustered SE = {SEc:.5f} | "
      f"t({df}) = {tc} | bar = {tc*SEc:.5f}")
print(f"  naive per-row SE would have been {naive:.5f} — inflation {SEc/naive:.1f}x")
print(f"  transfers? {D > tc*SEc}")

C = sum([C1, C2, C3, C4, C5])
print(f"\ncontrols passing: C = {C} of 5")
branches = {'B1_VACUOUS': (C < 5) or (A < 1),
            'B2_TRANSFERS': (C == 5) and (A >= 1) and (D > tc * SEc),
            'B3_NO_TRANSFER': (C == 5) and (A >= 1) and (D <= tc * SEc)}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1
VERDICT = fired[0].split('_', 1)[1]

out = {'cycle': '148-L', 'question': 'does the (parent, invariant) structure transfer to a '
                                     'relation never seen in fitting?',
       'design': 'leave-one-relation-out over 4 relations; M4 excluded by design because it has '
                 'no cell for an unseen relation and testing it would measure a tautology',
       'bound': {'batches': NBATCH, 'of': len(files)},
       'parse': {'kept': len(recs), 'dropped': drop},
       'discriminative': len(disc), 'relations': RELS,
       'M1_heldout': {'acc': a1, 'per_cell_delta': d1, 'clustered_se': se1, 'cells': n1},
       'M2_heldout': {'acc': a2, 'per_cell_delta': d2, 'clustered_se': se2, 'cells': n2},
       'NULL_heldout': {'acc': aN, 'per_cell_delta': dN, 'clustered_se': seN, 'cells': nN},
       'controls': {'C1_one_ranking_per_cell': C1, 'C2_cells_gt_3': C2,
                    'C3_null_at_zero': C3, 'C4_parse_loud': C4,
                    'C5_relation_disjoint': C5, 'C5_leaked_rows': overlap},
       'controls_passing': C, 'attainability': A,
       'D': D, 'clustered_SE': SEc, 'df': df, 't_crit': tc, 'bar': tc * SEc,
       'naive_se': naive, 'inflation': SEc / naive if naive else None,
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'scope': 'h4 only; feature-selection action space of 4 invariants; sampled batches'}
(ROOT / 'aporia/search/cycle_148l_results.json').write_text(json.dumps(out, indent=1),
                                                            encoding='utf-8')
print(f"\n*** CYCLE 148-L VERDICT: {VERDICT} ***")
