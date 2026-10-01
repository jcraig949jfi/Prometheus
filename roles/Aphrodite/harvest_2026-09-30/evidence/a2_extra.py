import re, collections, statistics as st
exec(open('a2_proxies.py', encoding='utf-8').read().split("if __name__")[0].replace('__file__', repr('./x')))
T = lambda s: datetime.fromisoformat(s).replace(tzinfo=EDT)
WINDOWS = [('W0','2026-09-11','2026-09-15'),('W1','2026-09-15','2026-09-23'),('W2','2026-09-23','2026-09-27'),
           ('W3','2026-09-27','2026-09-28T17:00'),('W4','2026-09-28T17:00','2026-09-30T04:18'),('W5','2026-09-30T04:18','2026-10-02')]
def norm(s): return re.sub(r'\([^)]*\)|\b(Aether|Ananke|Archaeon|Artemis|Bellerophon|Cosmos|Cyclops|Ensorain|Harmonia|Hecate|Nestor|Nyx|Odysseus|Techne|Theseus|Tyche|Aporia|Atlas)\b','',s or '')[:50]
OPSUBJ = re.compile(r'\bOPERATOR\b|operator[- ]ruling|operator[- ]directive|operator[- ]approved', re.I)
VERD = re.compile(r'verdict|\bKILL|\bPASS\b|\bFAIL|\bNULL\b|RESULT|decisive|NEGATIVE|POSITIVE', re.I)
POS = re.compile(r'positive[- ]control|planted|known[- ]answer', re.I)
LEASE = re.compile(r'\blease', re.I)
LEASEP = re.compile(r'lease[^.\n]{0,60}(conflict|refus|held by|collid|stale|expired|lost|contend|wait)|(conflict|refus|collid|contend)[^.\n]{0,40}lease', re.I)
BLINDV = re.compile(r'contaminat|peek|leak(ed|age)?\b|unblind|firewall breach|saw the (holdout|sealed)', re.I)
out = []
for name, a, b in WINDOWS:
    ms = [x for x in M if T(a) <= x['t'] < T(b)]
    seen = set(); ded = []
    for x in sorted(ms, key=lambda x: x['t']):
        k = (x['sender'], norm(x['subject']), x['t'].strftime('%m-%d %H'))
        if k in seen: continue
        seen.add(k); ded.append(x)
    v = [x for x in ms if x['kind'] == 'report' and VERD.search(x['subject'] or '')]
    out.append(dict(window=name, msgs=len(ms), dedup=len(ded), fanout_dupes=len(ms) - len(ded),
        overhead_pct_dedup=100.0 * sum(map(is_overhead, ded)) / len(ded),
        op_subject=sum(bool(OPSUBJ.search(x['subject'] or '')) for x in ded),
        verdict_reports=len(v), posctl_pct=100.0 * sum(bool(POS.search(x['txt'])) for x in v) / len(v) if v else None,
        lease_msgs=sum(bool(LEASE.search(x['txt'])) for x in ded), lease_problem=sum(bool(LEASEP.search(x['txt'])) for x in ded),
        blind_breach_terms=sum(bool(BLINDV.search(x['txt'])) for x in ded)))
print(md(out))
