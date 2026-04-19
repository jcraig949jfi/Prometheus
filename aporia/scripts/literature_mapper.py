"""
Aporia Literature Mapper — Maps papers to tensor (F, P) cells.
Produces literature_to_tensor_mapping.md and .json.
"""
import json
from pathlib import Path
from datetime import datetime

# Load papers
lit = json.loads(Path('aporia/data/literature_scan.json').read_text(encoding='utf-8'))
sweep_path = Path('aporia/data/frontier_sweep.json')
sweep = json.loads(sweep_path.read_text(encoding='utf-8')) if sweep_path.exists() else {'papers': []}

papers = []
for result in lit['results']:
    pid = result['problem_id']
    for p in result['recent_papers']:
        p['problem_id'] = pid
        papers.append(p)
    for p in result['classic_papers']:
        p['problem_id'] = pid
        papers.append(p)
for p in sweep.get('papers', []):
    p['problem_id'] = p.get('query', 'frontier')[:30]
    papers.append(p)

print(f'Papers to map: {len(papers)}')

PROBLEM_TO_CELLS = {
    'MATH-0062': [('F011', 'P020', '+1', 'Pair correlation predicts conductor-dependent deficit')],
    'MATH-0063': [
        ('F003', 'P023', '+2', 'BSD rank agreement confirmed at all ranks'),
        ('F003', 'P038', '+1', 'BSD Sha formula relates to Sha stratification'),
        ('F043', 'P101', 'UNKNOWN', 'BSD-Sha anticorrelation needs regulator test'),
    ],
    'MATH-0042': [('F014', 'P053', '+1', 'Lehmer spectrum near 1.176 via Mahler measure')],
    'MATH-0136': [
        ('F015', 'P020', '+1', 'abc/Szpiro monotone decrease with conductor'),
        ('F015', 'P021', '+1', 'Szpiro survives bad-prime stratification'),
        ('F015', 'P026', '+1', 'Szpiro differs by semistable vs additive'),
    ],
    'MATH-0130': [
        ('F001', 'P010', '+2', 'Langlands GL(2) perfect match via Galois label'),
        ('F001', 'P033', '+2', 'Is_Even parity splits proven vs open reps'),
    ],
    'MATH-0151': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Chowla autocorrelation not in current F-ids')],
    'MATH-0165': [
        ('F011', 'P020', '+1', 'Keating-Snaith predicts moment scaling with conductor'),
        ('F013', 'P023', '+1', 'Moments differ by rank family'),
    ],
    'MATH-0260': [
        ('F026', 'P102', '-2', 'Artin dim frontier killed as proof-boundary'),
        ('F026', 'P033', 'UNKNOWN', 'Even vs odd Artin split needs testing'),
    ],
    'MATH-0334': [
        ('F032', 'P053', 'UNKNOWN', 'Volume conjecture could break knot silence via Mahler'),
        ('OUT_OF_TENSOR', '', 'UNKNOWN', 'Suggests new F: hyperbolic volume fingerprint'),
    ],
    'MATH-0370': [('F011', 'P020', '+1', 'Density hypothesis constrains zero distribution')],
    'MATH-0492': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Zaremba CF not in F-ids; nf_cf domain exists')],
    'MATH-0501': [
        ('F032', 'P027', 'UNKNOWN', 'L-space conjecture: ADE type may break knot silence'),
        ('OUT_OF_TENSOR', '', 'UNKNOWN', 'Suggests new F: Alexander L-space classification'),
    ],
    'MATH-0508': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Selberg zeta not in F-ids')],
    'MATH-0518': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Greenberg Iwasawa not in F-ids')],
    'MATH-0522': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Poonen dynatomic not in tensor')],
    'MATH-0530': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Chromatic symmetric not in P-ids')],
    'MATH-0531': [
        ('F008', 'P020', '+1', 'Cohen-Lenstra predicts class group by conductor'),
        ('OUT_OF_TENSOR', '', 'UNKNOWN', 'Bartel-Lenstra needs Galois-type strat'),
    ],
    'MATH-0532': [
        ('F003', 'P024', '+1', 'BKLPR predicts Selmer by torsion'),
        ('F003', 'P036', '+1', 'Selmer split by root number predicts 50/50'),
    ],
    'MATH-0529': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Singularity type not in vocabulary')],
    'MATH-0537': [('OUT_OF_TENSOR', '', 'UNKNOWN', 'Spatial Moran not in tensor')],
}

live_specimens = {'F011', 'F013', 'F014', 'F015', 'F041a', 'F042', 'F043', 'F044', 'F045'}
mappings = []
out_of_tensor = []

for paper in papers:
    pid = paper.get('problem_id', '')
    title = paper.get('title', '')
    year = paper.get('year', '?')
    arxiv = paper.get('arxiv', '')
    citations = paper.get('citations', 0)
    key = f"{str(title)[:30].lower().replace(' ','_').replace('/','_')}_{year}"

    cells = PROBLEM_TO_CELLS.get(pid, [])
    if not cells:
        query = paper.get('query', str(title))
        if 'Langlands' in str(query) or 'Langlands' in str(title):
            cells = [('F001', 'P010', 'UNKNOWN', 'Langlands-related')]
        elif any(w in str(query).lower() for w in ['gue', 'random matrix', 'zero spacing']):
            cells = [('F011', 'P020', 'UNKNOWN', 'Zero statistics')]
        elif any(w in str(query).lower() for w in ['szpiro', 'abc']):
            cells = [('F015', 'P020', 'UNKNOWN', 'Szpiro/abc')]
        elif 'knot' in str(query).lower():
            cells = [('F032', 'P053', 'UNKNOWN', 'Knot-related')]
        else:
            cells = [('OUT_OF_TENSOR', '', 'UNKNOWN', f'No F/P mapping')]

    for f_id, p_id, verdict, reason in cells:
        entry = {
            'paper_key': key, 'title': str(title), 'year': year,
            'arxiv': arxiv, 'citations': citations, 'problem_id': pid,
            'F': f_id, 'P': p_id, 'verdict': verdict, 'reason': reason,
        }
        if f_id == 'OUT_OF_TENSOR':
            out_of_tensor.append(entry)
        else:
            mappings.append(entry)

# Score
for m in mappings:
    v_score = 1.0 if m['verdict'] in ('+1', '+2', '-1', '-2') else 0.5
    s_score = 1.0 if m['F'] in live_specimens else 0.3
    m['info_score'] = (m['citations'] + 1) * v_score * s_score

top10 = sorted(mappings, key=lambda x: -x['info_score'])[:10]

# Write MD
md = [
    '# Literature to Tensor Mapping',
    f'## Generated: {datetime.now().isoformat()[:19]}',
    f'## Mapped: {len(mappings)} cells, {len(out_of_tensor)} OUT_OF_TENSOR',
    '', '---', '',
    '## (a) Paper-to-Cell Table', '',
    '| Paper | Year | F | P | Verdict | Reason | Cites |',
    '|-------|------|---|---|---------|--------|-------|',
]
for m in sorted(mappings, key=lambda x: (x['F'], x['P'])):
    md.append(f"| {m['paper_key'][:35]} | {m['year']} | {m['F']} | {m['P']} | {m['verdict']} | {m['reason'][:50]} | {m['citations']} |")

md.extend(['', '---', '', '## (b) OUT_OF_TENSOR', '',
    '| Paper | Problem | Suggestion |', '|-------|---------|-----------|'])
for o in out_of_tensor[:30]:
    md.append(f"| {o['paper_key'][:35]} | {o['problem_id'][:15]} | {o['reason'][:55]} |")

md.extend(['', '---', '', '## (c) Top 10 Priorities', ''])
for i, m in enumerate(top10):
    md.extend([
        f'### Rank {i+1}',
        f'- **Paper**: {m["title"][:60]} ({m["year"]}, cites:{m["citations"]})',
        f'- **Cell**: {m["F"]} x {m["P"]}, verdict: {m["verdict"]}',
        f'- **Reason**: {m["reason"]}',
        f'- **Worker**: {"Gap-filler" if m["verdict"] in ("+1","+2") else "Re-auditor"}',
        '',
    ])

Path('cartography/docs/literature_to_tensor_mapping.md').write_text('\n'.join(md), encoding='utf-8')
Path('cartography/docs/literature_to_tensor_mapping.json').write_text(
    json.dumps({'generated': datetime.now().isoformat(), 'n_mapped': len(mappings),
                'n_out': len(out_of_tensor), 'mappings': mappings,
                'out_of_tensor': out_of_tensor, 'top10': top10}, indent=2), encoding='utf-8')

print(f'Mapped: {len(mappings)} cells, {len(out_of_tensor)} OUT_OF_TENSOR')
print(f'\nTOP 10:')
for i, m in enumerate(top10):
    print(f'  {i+1}. {m["F"]}x{m["P"]} [{m["verdict"]}] {m["title"][:50]} ({m["citations"]}c) score={m["info_score"]:.0f}')

print(f'\nOUT_OF_TENSOR suggestions:')
suggestions = set(o['reason'] for o in out_of_tensor)
for s in list(suggestions)[:8]:
    print(f'  - {s}')

print(f'\nLITERATURE_MAPPING_READY')
