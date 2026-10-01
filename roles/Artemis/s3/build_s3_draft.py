"""S3 workload DRAFT (principal Artemis). Eligibility and draw fixed in this file before running.
Reads only committed content via `git show <BASE>:path`. No ranking: a seeded draw from an eligible set.
usage: python3 build_s3_draft.py BASE_SHA OUTDIR
"""
import hashlib, json, random, re, subprocess, sys, pathlib
BASE = sys.argv[1]; OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
def show(p):
    r = subprocess.run(['git', 'show', f'{BASE}:{p}'], capture_output=True, text=True)
    assert r.returncode == 0, p
    return r.stdout
# Seed: sha256 of the S3 protocol as published by Odysseus (external to Artemis's choice).
proto = show('roles/Odysseus/fabric_pilot/s3/S3_PROTOCOL.md').encode()
seed = hashlib.sha256(proto).hexdigest()
N = 10
EXCLUDED_CLUSTERS = {'D', 'H', 'Z'}   # D memory/SI-adjacent; H holdouts/custody; Z answered
GUARD = re.compile(r'LM01|SI01|irreversib|forget|evict|retention|retain|erasure|erase|reversible|selective|holdout|sealed', re.I)
coh = json.loads(show('roles/Artemis/challenge/prospective/COHORTS.json'))
used = {p['S'] for p in coh['pairs']} | {p['B'] for p in coh['pairs']}
index = show('roles/Artemis/backlog/INDEX.md')
cluster = None; elig = []; excl = []
for line in index.split('\n'):
    m = re.match(r'## ([A-Z])\. ', line)
    if m: cluster = m.group(1); continue
    if not line.startswith('| FR-'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    fr, title, state, host = c[0], c[1], c[2], c[-1].strip(' |')
    why = []
    if state != 'RAW': why.append('state=' + state)
    if host != 'L': why.append('host=' + host)
    if fr in used: why.append('self-test cohort')
    if cluster in EXCLUDED_CLUSTERS: why.append('cluster ' + cluster)
    if GUARD.search(title): why.append('guard term')
    (excl if why else elig).append(dict(fr=fr, cluster=cluster, title=title, why=why, line=line))
elig.sort(key=lambda r: r['fr'])
draw = random.Random(seed).sample(elig, N)
harvest = ''.join(show(f'roles/Artemis/backlog/harvest/{f}') for f in
                  ['D1_program.md', 'D2_replication.md', 'D3_new_lenses.md', 'D4_sfe_era.md', 'D5_older_lines.md'])
blocks = {m.group(1): m.group(0) for m in re.finditer(r'### (H-D\d-\d+).*?(?=\n### H-|\n## |\Z)', harvest, re.S)}
def sanitize(t):
    t = re.sub(r'\bFR-\d+\b', '[thread]', t)
    t = re.sub(r'\b(SHARPENED|MATURE|RAW)\b', '', t)
    t = re.sub(r'roles/Artemis/[^\s)`\'"]*', '[curator file, not provided]', t)
    return re.sub(r'\bArtemis\b', 'the curator', t)
TAIL = """

---- deliverables (S3_PROTOCOL s3) ----
Answer the question above from committed repository content (read-only).
Write REPORT.md: question, method, evidence with path:line or <commit>:<path>
citations, result, limits, and what would change the conclusion. Write
claims.json: every load-bearing claim with evidence pointers and confidence.
You cannot run code. If a computation is needed, write it as out/analysis.py
(stdlib/numpy, inputs named by repo path@sha) and say what result would
decide the question; do not guess its output.
"""
for i, r in enumerate(draw, 1):
    c = [x.strip() for x in r['line'].strip().strip('|').split(' | ')]
    srcs = re.findall(r'H-D\d-\d+', c[3])
    pkg = (f'# {c[1]}\n\nRelations: {c[4]}\n\nSource material (verbatim harvest entries):\n\n' +
           '\n\n'.join(blocks.get(s, f'[{s} not found]') for s in srcs))
    r['id'] = f'Q{i}'
    (OUT / f"Q{i}.package.md").write_text(f"# S3 package Q{i}\n\n" + sanitize(pkg) + TAIL)
json.dump(dict(base=BASE, seed=seed, n_eligible=len(elig), n_excluded=len(excl),
               draw=[dict(id=r['id'], fr=r['fr'], cluster=r['cluster'], title=r['title']) for r in draw],
               excluded=[dict(fr=r['fr'], why=r['why']) for r in excl]), open(OUT / 'DRAW.json', 'w'), indent=1)
print('eligible', len(elig), 'excluded', len(excl), 'seed', seed[:16])
for r in draw: print(r['id'], r['fr'], r['cluster'], r['title'][:90])
