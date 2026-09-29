"""Standing bounded dispatch (MWO-0001 s10 ARTEMIS; MWO-0004). Seeded draw of raw eligible threads, packaged
verbatim (no rewriting, no ranking). Eligibility = the S3 rule (roles/Artemis/s3/build_s3_draft.py), minus
threads already dispatched. The seed is sha256 of a named committed file that Artemis did not write.
usage: python3 build_dispatch.py BATCH BASE_SHA SEED_PATH@SEED_COMMIT N OUTDIR EXCLUDE_JSON...
"""
import hashlib, json, random, re, subprocess, sys, pathlib
BATCH, BASE, SEEDSPEC, N, OUT = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), pathlib.Path(sys.argv[5])
EXCL_FILES = sys.argv[6:]
OUT.mkdir(parents=True, exist_ok=True)
def show(rev, p):
    r = subprocess.run(['git', 'show', f'{rev}:{p}'], capture_output=True, text=True); assert r.returncode == 0, p
    return r.stdout
sp, sc = SEEDSPEC.split('@')
seed = hashlib.sha256(show(sc, sp).encode()).hexdigest()
EXCLUDED_CLUSTERS = {'D', 'H', 'Z'}
GUARD = re.compile(r'LM01|SI01|irreversib|forget|evict|retention|retain|erasure|erase|reversible|selective|holdout|sealed', re.I)
coh = json.loads(show(BASE, 'roles/Artemis/challenge/prospective/COHORTS.json'))
used = {p['S'] for p in coh['pairs']} | {p['B'] for p in coh['pairs']}
for f in EXCL_FILES:
    used |= {r['fr'] for r in json.load(open(f))['draw']}
ids = json.loads(show(BASE, 'roles/Artemis/challenge/identity/ARTEMIS_FR_IDS.json'))
index = show(BASE, 'roles/Artemis/backlog/INDEX.md')
cluster = None; elig = []
for line in index.split('\n'):
    m = re.match(r'## ([A-Z])\. ', line)
    if m: cluster = m.group(1); continue
    if not line.startswith('| FR-'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    fr, title, state, host = c[0], c[1], c[2], c[-1].strip(' |')
    if state == 'RAW' and host == 'L' and fr not in used and cluster not in EXCLUDED_CLUSTERS and not GUARD.search(title):
        elig.append(dict(fr=fr, cluster=cluster, title=title, line=line))
elig.sort(key=lambda r: r['fr'])
draw = random.Random(seed).sample(elig, min(N, len(elig)))
harvest = ''.join(show(BASE, f'roles/Artemis/backlog/harvest/{f}') for f in
                  ['D1_program.md', 'D2_replication.md', 'D3_new_lenses.md', 'D4_sfe_era.md', 'D5_older_lines.md'])
blocks = {m.group(1): m.group(0) for m in re.finditer(r'### (H-D\d-\d+).*?(?=\n### H-|\n## |\Z)', harvest, re.S)}
def sanitize(t):
    t = re.sub(r'\bFR-\d+\b', '[thread]', t); t = re.sub(r'\b(SHARPENED|MATURE|RAW)\b', '', t)
    t = re.sub(r'roles/Artemis/[^\s)`\'"]*', '[curator file, not provided]', t)
    return re.sub(r'\bArtemis\b', 'the curator', t)
TAIL = """

---- deliverables ----
Answer the question above from committed repository content (read-only).
The harvest's status notes ("later evidence", "never built", counts) were
written earlier and are UNVERIFIED: establish current status yourself.
Write out/REPORT.md: question, method, evidence with path:line or <commit>:<path>
citations, result, limits, and what would change the conclusion. Write
out/claims.json: every load-bearing claim with evidence pointers and confidence.
You cannot run code. If a computation is needed, write it as out/analysis.py
(stdlib/numpy, inputs named by repo path@sha) and say what result would
decide the question; do not guess its output.
"""
for i, r in enumerate(draw, 1):
    c = [x.strip() for x in r['line'].strip().strip('|').split(' | ')]
    srcs = re.findall(r'H-D\d-\d+', c[3])
    pkg = (f'# {c[1]}\n\nRelations: {c[4]}\n\nSource material (verbatim harvest entries):\n\n' +
           '\n\n'.join(blocks.get(s, f'[{s} not found]') for s in srcs))
    r['id'] = f'{BATCH}-{i:02d}'; r['thread'] = ids.get(r['fr'], {}).get('id')
    (OUT / f"{r['id']}.package.md").write_text(f"# Package {r['id']}\n\n" + sanitize(pkg) + TAIL)
json.dump(dict(batch=BATCH, base=BASE, seed_source=SEEDSPEC, seed=seed, n_eligible=len(elig),
               draw=[{k: r[k] for k in ('id', 'fr', 'thread', 'cluster', 'title')} for r in draw]),
          open(OUT / 'DRAW.json', 'w'), indent=1)
print('eligible', len(elig), 'seed', seed[:16])
for r in draw: print(r['id'], r['fr'], r['thread'], r['cluster'], r['title'][:80])
