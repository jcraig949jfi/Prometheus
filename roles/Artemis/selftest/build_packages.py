"""Build blind worker packages for the Artemis self-test (PREREG amendment 2, A2.1/A2.4).
Reads ONLY the frozen commit a9d5f5f23 via `git show`. Writes packages + the secret
run->thread mapping to OUT (outside the repo); prints the mapping's sha256 for commit-reveal.
usage: python3 build_packages.py OUTDIR
"""
import hashlib, json, random, re, subprocess, sys, pathlib
FROZEN = 'a9d5f5f23'
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
def show(p):
    r = subprocess.run(['git', 'show', f'{FROZEN}:{p}'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None
prereg = show('roles/Artemis/challenge/prospective/PREREG.md').encode()
seed = hashlib.sha256(prereg.replace(b'\r\n', b'\n')).hexdigest()
coh = json.loads(show('roles/Artemis/challenge/prospective/COHORTS.json'))
A_RUN = {'FR-011', 'FR-101'}                      # A2.0: S side executed by Artemis
runs = []
for p in coh['pairs']:
    if p['S'] not in A_RUN: runs.append(dict(fr=p['S'], cohort='S', pair=p['S']))
    runs.append(dict(fr=p['B'], cohort='B', pair=p['S'], paired=p['S'] not in A_RUN))
for r in runs: r.setdefault('paired', True)
rng = random.Random(seed); rng.shuffle(runs)
for i, r in enumerate(runs, 1): r['run'] = f'R-{i:02d}'
index = show('roles/Artemis/backlog/INDEX.md')
harvest = ''.join(show(f'roles/Artemis/backlog/harvest/{f}') or '' for f in
                  ['D1_program.md', 'D2_replication.md', 'D3_new_lenses.md', 'D4_sfe_era.md', 'D5_older_lines.md'])
blocks = {m.group(1): m.group(0) for m in re.finditer(r'### (H-D\d-\d+).*?(?=\n### H-|\n## |\Z)', harvest, re.S)}
def sanitize(t, run):
    t = re.sub(r'\bFR-\d+\b', '[thread]', t)
    t = re.sub(r'\b(SHARPENED|MATURE|RAW)\b', '', t)
    t = re.sub(r'roles/Artemis/[^\s)`\'"]*', '[curator file, not provided]', t)
    t = re.sub(r'\bArtemis\b', 'the curator', t)
    t = '\n'.join(l for l in t.split('\n') if not re.match(r'\s*(State|Last reviewed):', l))
    return t
for r in runs:
    fr = r['fr']
    if r['cohort'] == 'S':
        body = show(f'roles/Artemis/backlog/threads/{fr}.md') or ''
        chop = show(f'roles/Artemis/backlog/chops/{fr}.md')
        pkg = body + ('\n\n---- work sketch ----\n\n' + chop if chop else '')
    else:
        row = [l for l in index.split('\n') if l.startswith(f'| {fr} |')][0]
        c = [x.strip() for x in row.strip().strip('|').split(' | ')]
        srcs = re.findall(r'H-D\d-\d+', c[3])
        pkg = (f'# {c[1]}\n\nRelations: {c[4]}\nHost hint: {c[5].strip(" |")}\n\n'
               f'Source material (verbatim harvest entries):\n\n' +
               '\n\n'.join(blocks.get(s, f'[{s} not found]') for s in srcs))
    (OUT / f"{r['run']}.package.md").write_text(f"# Run {r['run']} -- question package\n\n" + sanitize(pkg, r['run']))
mapping = json.dumps(dict(seed=seed, frozen=FROZEN, runs=runs), indent=1, sort_keys=True)
(OUT / 'MAPPING_SECRET.json').write_text(mapping)
print('runs', len(runs), 'paired', sum(r['paired'] for r in runs), 'mapping_sha256', hashlib.sha256(mapping.encode()).hexdigest())
