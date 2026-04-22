"""
gen_07 execution: process Aporia paper cache; produce classified diff log.
"""
import os, json, datetime as dt
from pathlib import Path
os.environ.setdefault('AGORA_REDIS_HOST', '192.168.1.176')
os.environ.setdefault('AGORA_REDIS_PASSWORD', 'prometheus')
from agora.tensor import features, feature_meta

lit = json.loads(Path('aporia/data/literature_scan.json').read_text(encoding='utf-8'))
papers = []
for result in lit['results']:
    pid = result['problem_id']
    for p in result['recent_papers']:
        p['problem_id'] = pid
        p['vintage'] = 'recent'
        papers.append(p)
    for p in result['classic_papers']:
        p['problem_id'] = pid
        p['vintage'] = 'classic'
        papers.append(p)
print('Papers loaded: {}'.format(len(papers)))

PROBLEM_TO_FIDS = {
    'MATH-0062': ['F011'],
    'MATH-0063': ['F003', 'F043'],
    'MATH-0042': ['F014'],
    'MATH-0136': ['F015'],
    'MATH-0130': ['F001'],
    'MATH-0165': ['F011', 'F013'],
    'MATH-0151': [],
    'MATH-0080': ['F011', 'F013'],
    'MATH-0141': ['F002', 'F009'],
    'MATH-0170': ['F008'],
    'MATH-0173': ['F045'],
    'MATH-0181': ['F011', 'F041a'],
    'MATH-0205': ['F044'],
    'MATH-0211': ['F011'],
    'MATH-0218': ['F010', 'F022'],
    'MATH-0234': ['F015', 'F041a'],
    'MATH-0240': ['F004'],
    'MATH-0256': ['F014'],
    'MATH-0268': ['F042'],
    'MATH-0275': ['F043'],
}


def classify_diff(paper, f_id, f_meta):
    text = '{} {}'.format(paper.get('title', ''), paper.get('tldr', '')).lower()
    tier = f_meta.get('tier', '')

    if f_id == 'F043' and tier == 'killed':
        return ('RETRACTION_CROSS_CHECK', 0.9,
                'F043 retracted as algebraic coupling; paper may be relevant to re-examining claim structure')

    if tier == 'calibration':
        return ('REPRODUCTION', 0.7,
                'F-ID is calibration anchor; default to reproduction unless paper claims violation')

    if tier == 'killed':
        return ('KILL_REINFORCEMENT_CANDIDATE', 0.6,
                'F-ID already killed; paper may reinforce kill or propose resurrection')

    if tier == 'live_specimen' or 'live' in tier:
        if any(w in text for w in ['deficit', 'residual', 'anomal', 'divergence']):
            return ('DIVERGENCE_NUMERICAL', 0.5,
                    'Paper describes a deviation; requires numerical diff vs measured value')
        if any(w in text for w in ['rigor', 'proof', 'theorem', 'bound', 'inequality']):
            return ('REPRODUCTION', 0.6,
                    'Paper appears to establish theorem / bound; expect reproduction')
        return ('DIVERGENCE_STRUCTURAL', 0.4,
                'Paper touches this F-ID via different framing; structural comparison needed')

    return ('CANDIDATE_NEW_F_ID', 0.3,
            'F-ID match weak; paper may describe a structure not yet registered')


features_set = set(features())

diff_log = []
for p in papers:
    pid = p['problem_id']
    matched_f_ids = PROBLEM_TO_FIDS.get(pid, [])
    if not matched_f_ids:
        diff_log.append({
            'paper_title': p.get('title', '')[:120],
            'paper_year': p.get('year'),
            'paper_url': p.get('url'),
            'problem_id': pid,
            'matched_f_ids': [],
            'classification': 'CANDIDATE_NEW_F_ID',
            'confidence': 0.3,
            'rationale': 'No existing F-ID for this problem; paper may motivate a new one',
        })
        continue
    for fid in matched_f_ids:
        m = feature_meta(fid) if fid in features_set else {'tier': 'unknown'}
        cat, conf, why = classify_diff(p, fid, m)
        diff_log.append({
            'paper_title': p.get('title', '')[:120],
            'paper_year': p.get('year'),
            'paper_authors': (p.get('authors') or [''])[:2],
            'paper_url': p.get('url'),
            'paper_arxiv': p.get('arxiv'),
            'paper_tldr': (p.get('tldr') or '')[:200],
            'problem_id': pid,
            'matched_f_ids': [fid],
            'f_id': fid,
            'f_tier': m.get('tier', ''),
            'classification': cat,
            'confidence': conf,
            'rationale': why,
        })

from collections import Counter
cat_counts = Counter(d['classification'] for d in diff_log)
print('Diff entries: {}'.format(len(diff_log)))
for c, n in cat_counts.most_common():
    print('  {:30s} {}'.format(c, n))

Path('harmonia/memory').mkdir(exist_ok=True)
with open('harmonia/memory/literature_diff_entries.json', 'w', encoding='utf-8') as fh:
    json.dump({'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'source': 'aporia/data/literature_scan.json',
               'n_papers': len(papers),
               'n_diff_entries': len(diff_log),
               'classification_counts': dict(cat_counts),
               'entries': diff_log}, fh, indent=2)
print('Wrote harmonia/memory/literature_diff_entries.json')
