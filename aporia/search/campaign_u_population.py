"""CAMPAIGN U — one-pass campaign. Rebuild the neglected population from ALL
connectivity evidence, and report what it does to the 248 Campaign T survivors.

WHY THIS OUTRANKS WIDENING THE OPERATOR FAMILY: a contaminated population makes
every downstream count wrong. Adding operators to a wrong population produces more
wrong counts. Campaign S measured that 23.9% of its "unreferenced" targets name an
A-number in their own title, so the set is contaminated BY CONSTRUCTION.

THE DEFECT: Campaign S defined zero-connectivity from `oeis_crossrefs.jsonl` alone.
A sequence whose TITLE, FORMULA or PROGRAM text names another sequence is
referenced — the extraction simply did not capture it as an edge.

CORRECTED DEFINITION: a sequence is NEGLECTED only if it has no connectivity
evidence in ANY available source —
  * not a source or target of a cross-reference edge, AND
  * its own title / formulas / programs name no A-number (no outbound reference), AND
  * no other sequence's title / formulas / programs name it (no inbound reference).

PRE-STATED BRANCHES, COMMITTED BEFORE ANY COMPUTATION
-----------------------------------------------------
R = fraction of the 248 Campaign T survivor targets that remain in the corrected
neglected population.

    U1 DESTROYED   R < 0.20   the Campaign S/T result rested on a contaminated
                              population; this becomes the headline correction, not
                              a footnote.
    U2 WEAKENED    0.20 <= R < 0.70   materially reduced but survives in part.
    U3 SURVIVES    R >= 0.70   contamination did not drive the result.

PARTITION: R is a proportion in [0,1]; the three conditions are exhaustive and
mutually exclusive, verified by enumeration below.

POWER, STATED HONESTLY: this is a CENSUS of all 248 survivors, not a sample. There
is no sampling error; MDE is not the binding concept. Granularity is 1/248 =
0.0040, far finer than either cut, so both are resolvable. The 0.20/0.70 cuts are
MATERIALITY judgements and are labelled as such.

VERDICT-RULE NULL CHECK: if the correction removes nothing, R = 1 -> U3. If it
removes everything, R = 0 -> U1. The extremes map to distinct branches and neither
equals the middle, so the rule discriminates.

DIRECTION DECLARED IN ADVANCE: I expect this correction to SHRINK the neglected
population substantially, because most OEIS sequences mention another sequence
somewhere in their text. If R lands low, that is a result against my own two
previous campaigns and it goes in the headline.
"""
from __future__ import annotations

import gzip
import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'
CART = ROOT / 'cartography' / 'oeis' / 'data'
MIN_TERMS, MAX_TERMS = 25, 45
ANUM = re.compile(r'A\d{6}')

corpus = set()
with gzip.open(ROOT / 'prometheus_data/oeis/stripped.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        p = line.strip().rstrip(',').split(',')
        if len(p) >= MIN_TERMS + 1:
            corpus.add(p[0].strip())
print(f"corpus with >= {MIN_TERMS} terms: {len(corpus):,}", flush=True)

outbound, inbound = set(), set()

def absorb(sid, text):
    ms = ANUM.findall(text)
    if not ms:
        return
    others = [m for m in ms if m != sid]
    if others:
        outbound.add(sid)
        inbound.update(others)

# 1. cross-reference edges
xr_touch = set()
with (CART / 'oeis_crossrefs.jsonl').open('r', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get('source'): xr_touch.add(r['source'])
        if r.get('target'): xr_touch.add(r['target'])
print(f"crossref-touched: {len(xr_touch):,}", flush=True)

# 2. titles
n = 0
with gzip.open(ROOT / 'prometheus_data/oeis/names.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        pr = line.rstrip('\n').split(' ', 1)
        if len(pr) == 2:
            n += 1
            absorb(pr[0], pr[1])
print(f"titles scanned: {n:,} | outbound so far {len(outbound):,} | inbound {len(inbound):,}", flush=True)

# 3. formulas, 4. programs
for fname, key in (('oeis_formulas.jsonl', 'formula'), ('oeis_programs.jsonl', 'program')):
    n = 0
    with (CART / fname).open('r', encoding='utf-8', errors='replace') as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            n += 1
            sid = r.get('seq_id')
            if sid:
                absorb(sid, r.get(key, '') or '')
    print(f"{fname} scanned: {n:,} | outbound {len(outbound):,} | inbound {len(inbound):,}", flush=True)

connected = xr_touch | outbound | inbound
neglected = corpus - connected
print(f"\ntotal connectivity-touched: {len(connected):,}")
print(f"CORRECTED neglected population: {len(neglected):,}  (Campaign S used 31,189)")

surv = [json.loads(l) for l in (OUT / 'sb_candidates_formula_survivors.jsonl').open(encoding='utf-8') if l.strip()]
surv_tgt = {c['target'] for c in surv}
remain = surv_tgt & neglected
R = len(remain)/len(surv_tgt)

def fire(r):
    if r < 0.20: return 'U1', 'DESTROYED'
    if r < 0.70: return 'U2', 'WEAKENED'
    return 'U3', 'SURVIVES'

grid = [round(x/1000, 3) for x in range(0, 1001)]
cov = defaultdict(int); bad = 0
for g in grid:
    b = fire(g)
    if b is None: bad += 1
    cov[b[0]] += 1
print(f"\npartition: {len(grid)} points, unmapped {bad}, coverage {dict(cov)}")
print(f"  boundaries: 0.199->{fire(0.199)[0]} 0.200->{fire(0.200)[0]} "
      f"0.699->{fire(0.699)[0]} 0.700->{fire(0.700)[0]}")

br, term = fire(R)
print(f"\nCampaign T survivor targets: {len(surv_tgt)}")
print(f"  still neglected under the CORRECTED definition: {len(remain)}")
print(f"  R = {R:.4f}  ->  {br} {term}")

kept = [c for c in surv if c['target'] in remain]
with (OUT / 'sb_candidates_corrected_population.jsonl').open('w', encoding='utf-8') as fh:
    for c in sorted(kept, key=lambda x: (-x['exact_terms'], x['target'])):
        fh.write(json.dumps({**c,
            'status': 'CANDIDATE - verified exact; not in either title, formula or program text; '
                      'target neglected under the CORRECTED all-source definition',
            'population': 'corrected (crossrefs + titles + formulas + programs, inbound and outbound)'},
            ensure_ascii=False) + '\n')

res = {'corpus': len(corpus), 'crossref_touched': len(xr_touch),
       'text_outbound': len(outbound), 'text_inbound': len(inbound),
       'total_connected': len(connected),
       'neglected_corrected': len(neglected), 'neglected_campaign_S': 31189,
       'population_shrink_factor': round(31189/max(len(neglected), 1), 2),
       'survivor_targets': len(surv_tgt), 'survivors_still_neglected': len(remain),
       'R': round(R, 4), 'branch': br, 'TERMINAL': term,
       'surviving_records': len(kept),
       'partition': {'points': len(grid), 'unmapped': bad, 'coverage': dict(cov)},
       'census_not_sample': True, 'granularity': round(1/len(surv_tgt), 4),
       'thresholds': 'materiality judgements, not power-derived; census has no sampling error'}
(OUT / 'campaign_u_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\nartifact: sb_candidates_corrected_population.jsonl ({len(kept)} records)")
