"""CAMPAIGN T — one-pass campaign. Does the OEIS FORMULA field already state the
259 candidate relations?

ONE-PASS IS PRECEDENTED: Campaign B (void audit, P107) completed in a single pass
to terminal ADVANCE. A campaign is three passes at most, not at least, and this is
a single decisive measurement on data already in hand.

PRE-STATED READINGS, COMMITTED HERE BEFORE ANY COMPUTATION RUNS
---------------------------------------------------------------
Campaign S's headline — 93.2% of its hits are "genuine unstated" — was measured
against OEIS TITLES only, and its terminal artifact recorded that as an UPPER
BOUND because comment and formula fields were not on disk. They are:
`cartography/oeis/data/oeis_formulas.jsonl`, 523,463 formula lines. That file
answers the one question deciding whether the candidate set is worth a human's
time.

MEASURABLE: F = fraction of the 259 distinct genuine-unstated targets whose
relation to its partner IS stated in an OEIS formula field of either sequence.

    T1 KILL-THE-SET   F >= 0.80   overwhelmingly rediscovery; the set is not worth
                                  triage as a discovery set. The METHOD claim from
                                  Campaign S survives untouched — this kills the
                                  artifact's value, not the sweep's validity.
    T2 REDESIGN       0.30 <= F < 0.80   substantially contaminated; the set needs
                                  filtering before a human should be handed it.
    T3 ADVANCE        F < 0.30    the set survives its strongest available check
                                  and is worth triage.

PARTITION: F is a proportion in [0,1]; the three conditions are exhaustive and
mutually exclusive by construction, verified by enumeration below.

ON POWER, STATED HONESTLY: this is a CENSUS of all 259 targets, not a sample, so
there is NO sampling error and MDE is not the binding concept. Granularity is
1/259 = 0.0039, far finer than either threshold, so both are resolvable. The
0.30/0.80 cuts are materiality judgements and are labelled as such rather than
dressed up as power-derived.

VERDICT-RULE NULL CHECK: if formulas state nothing, F = 0 -> T3. If they state
everything, F = 1 -> T1. The two extremes map to distinct branches and neither is
the same as the middle, so the rule discriminates.

DETECTION: a relation counts as STATED if either partner's formula text names the
other's A-number. That is deliberately generous toward T1 — it counts any formula
mentioning the partner, not only formulas expressing this exact operator — so the
resulting F is an UPPER bound on statedness, which biases against the candidate
set surviving. Bias direction declared before the number exists.
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'

cands = [json.loads(l) for l in (OUT / 'sb_candidate_relations.jsonl').open(encoding='utf-8') if l.strip()]
targets = {c['target'] for c in cands}
print(f"candidate records {len(cands)} | distinct targets {len(targets)}", flush=True)

need = set()
for c in cands:
    need.add(c['source']); need.add(c['target'])

formulas = defaultdict(list)
n_lines = 0
with open(ROOT / 'cartography/oeis/data/oeis_formulas.jsonl', 'r', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if not line.strip():
            continue
        n_lines += 1
        try:
            r = json.loads(line)
        except Exception:
            continue
        sid = r.get('seq_id')
        if sid in need:
            formulas[sid].append(r.get('formula', ''))
print(f"formula lines scanned {n_lines:,} | with formulas for {len(formulas):,} of {len(need):,} involved sequences", flush=True)

ANUM = re.compile(r'A\d{6}')
stated_recs, unstated_recs = [], []
for c in cands:
    s, t = c['source'], c['target']
    ftxt = ' || '.join(formulas.get(t, [])) + ' || ' + ' || '.join(formulas.get(s, []))
    hits = set(ANUM.findall(ftxt))
    if s in hits or t in hits:
        stated_recs.append({**c, 'stated_via': 'formula names partner'})
    else:
        unstated_recs.append(c)

stated_tgt = {c['target'] for c in stated_recs}
survive_tgt = targets - stated_tgt
F = len(stated_tgt)/len(targets)

def fire(f):
    if f >= 0.80: return 'T1', 'KILL-THE-SET'
    if f >= 0.30: return 'T2', 'REDESIGN'
    return 'T3', 'ADVANCE'

grid = [round(x/1000, 3) for x in range(0, 1001)]
cov = defaultdict(int); bad = 0
for g in grid:
    r = fire(g)
    if r is None: bad += 1
    cov[r[0]] += 1
print(f"\npartition enumeration over F in [0,1]: {len(grid)} points, unmapped {bad}, coverage {dict(cov)}")
print(f"  boundaries: F=0.299 -> {fire(0.299)[0]} | F=0.300 -> {fire(0.300)[0]} | "
      f"F=0.799 -> {fire(0.799)[0]} | F=0.800 -> {fire(0.800)[0]}")

br, term = fire(F)
print(f"\nRECORDS: stated {len(stated_recs)}/{len(cands)} = {len(stated_recs)/len(cands):.4f}")
print(f"TARGETS: stated {len(stated_tgt)}/{len(targets)} = {F:.4f}  -> surviving {len(survive_tgt)}")
print(f"\nBRANCH {br} -> TERMINAL {term}")

with (OUT / 'sb_candidates_formula_survivors.jsonl').open('w', encoding='utf-8') as fh:
    for c in sorted(unstated_recs, key=lambda x: (-x['exact_terms'], x['target'])):
        fh.write(json.dumps({**c,
            'status': 'CANDIDATE - verified exact; not in either title; not in either FORMULA field',
            'checked_fields': 'OEIS name + formula (comments and examples still unchecked)'},
            ensure_ascii=False) + '\n')

res = {'candidate_records': len(cands), 'distinct_targets': len(targets),
       'formula_lines_scanned': n_lines, 'sequences_with_formulas': len(formulas),
       'stated_records': len(stated_recs), 'stated_targets': len(stated_tgt),
       'F_fraction_of_targets_stated_in_formulas': round(F, 4),
       'surviving_targets': len(survive_tgt), 'surviving_records': len(unstated_recs),
       'branch': br, 'TERMINAL': term,
       'partition': {'points': len(grid), 'unmapped': bad, 'coverage': dict(cov)},
       'census_not_sample': True,
       'granularity': round(1/len(targets), 4),
       'detection_bias': 'generous toward T1: any formula naming the partner counts as stated, '
                         'so F is an UPPER bound on statedness and biases against the set surviving',
       'still_unchecked': 'OEIS comment and example fields are not on disk'}
(OUT / 'campaign_t_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\nsurvivor artifact: sb_candidates_formula_survivors.jsonl ({len(unstated_recs)} records)")
