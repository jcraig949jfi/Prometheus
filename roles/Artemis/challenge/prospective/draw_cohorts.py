"""Seeded, rule-based cohort draw for the Artemis prospective test (2026-09-28).
S = every SHARPENED/MATURE thread in backlog/INDEX.md at the frozen commit (no selection).
B = for each S thread, one RAW thread from the same cluster (letter) and host class,
    excluding BLOCKED-*, ANSWERED, SUPERSEDED and ops-owned rows; drawn without
    replacement by a PRNG seeded with sha256 of the committed challenge directive.
    If the cluster has no eligible RAW thread left, draw from the same host class
    in any cluster (recorded as 'fallback')."""
import hashlib, random, re, json, sys
IDX = 'roles/Artemis/backlog/INDEX.md'
DIR = 'roles/Artemis/prompts/2026-09-28_operator_challenge/01_OPERATOR_CHALLENGE_verbatim.md'
seed = hashlib.sha256(open(DIR, 'rb').read().replace(b'\r\n', b'\n')).hexdigest()
rng = random.Random(seed)
rows, cluster = [], None
for line in open(IDX):
    m = re.match(r'## ([A-Z])\. ', line)
    if m: cluster = m.group(1)
    if line.startswith('| FR-'):
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        host = c[5].strip(' |') if len(c) > 5 else ''
        hc = 'L' if host == 'L' else ('M2' if 'M2' in host else ('S' if 'S' in host or 'G' in host else host))
        rows.append(dict(fr=c[0], title=c[1], state=c[2], cluster=cluster, host=host, hclass=hc))
S = [r for r in rows if r['state'].startswith(('SHARPENED', 'MATURE'))]
elig = [r for r in rows if r['state'] == 'RAW' and r['cluster'] not in ('Z',)]
elig = [r for r in elig if 'owned in ops' not in r['state']]
elig.sort(key=lambda r: int(r['fr'][3:]))
pairs = []
for s in sorted(S, key=lambda r: int(r['fr'][3:])):
    pool = [r for r in elig if r['cluster'] == s['cluster'] and r['hclass'] == s['hclass']]
    how = 'cluster+host'
    if not pool:
        pool = [r for r in elig if r['hclass'] == s['hclass']]; how = 'fallback-host'
    b = rng.choice(pool); elig.remove(b)
    pairs.append(dict(S=s['fr'], S_title=s['title'], B=b['fr'], B_title=b['title'], cluster=s['cluster'], host=s['hclass'], match=how))
print(json.dumps(dict(seed=seed, n=len(pairs), pairs=pairs), indent=1))
