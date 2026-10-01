"""A2 intervention natural-experiment proxies. Read-only over comms_messages.json + gitlog.tsv.
All day buckets are America/New_York local (UTC-4 in Sep), matching most timestamps."""
import json, re, collections, statistics as st
from datetime import datetime, timedelta, timezone

D = __file__.rsplit('/', 1)[0] if '/' in __file__ else '.'
EDT = timezone(timedelta(hours=-4))
def ts(s):
    s = s.replace('Z', '+00:00')
    return datetime.fromisoformat(s).astimezone(EDT)

# ---------------- comms ----------------
M = json.load(open(f'{D}/comms_messages.json', encoding='utf-8'))
for x in M:
    x['t'] = ts(x['created_at']); x['day'] = x['t'].strftime('%m-%d')
    x['txt'] = (x['subject'] or '') + '\n' + (x['body'] or '')
byid = {x['id']: x for x in M}
days = sorted({x['day'] for x in M})

OVERHEAD = re.compile(r'\bHEARTBEAT\b|\bACK\b|\back(nowledg)?\b|\badopt(ed|ion|s)?\b|\bstatus\b|\bWORK_STATE\b|\bcensus\b|\bsync(ed)?\b', re.I)
def is_overhead(x):
    return x['kind'] == 'ack' or bool(OVERHEAD.search(x['subject'] or ''))
OPERATOR = re.compile(r'\bOPERATOR\b|operator[- ](ruling|directive|approved|decision|gate|prompt)|verbatim', re.I)
STALE = re.compile(r'\bstale\b|\bunadopted\b|not (yet )?(read|adopted|seen|synced)|\bsuperseded\b|out of date|behind origin|outdated|never (received|read|synced)', re.I)
FRICTION = {
    'lease/resource contention': r'lease (conflict|held|expired|lost)|contention|oversubscri|cpu8 (busy|held)|load average|starv',
    'git push/merge/rebase': r'non-fast-forward|push (was )?rejected|merge conflict|rebase (conflict|failed)|diverged',
    'DB/store unreachable': r'(postgres|EW_DB|store|database|db)[^.\n]{0,40}(unreachable|down|refused|timeout|timed out)|connection refused',
    'memory/OOM': r'\bOOM\b|out of memory|memory leak|swap(ping)?\b|killed by the kernel',
    'comms delivery/sync': r'(message|prompt|comms)[^.\n]{0,40}(not (received|delivered)|missed|lost|dropped)|sync (failed|error)',
    'disk/space': r'disk (full|space)|no space left|ENOSPC',
    'unowned/blocked waiting': r'waiting (for|on) (the )?operator|blocked on|awaiting (operator|ruling)',
}
FRICTION = {k: re.compile(v, re.I) for k, v in FRICTION.items()}

def day_table():
    rows = []
    for d in days:
        xs = [x for x in M if x['day'] == d]
        n = len(xs)
        rows.append(dict(day=d, n=n,
            senders=len({x['sender'] for x in xs}),
            overhead=sum(map(is_overhead, xs)),
            operator=sum(bool(OPERATOR.search(x['txt'])) for x in xs),
            stale=sum(bool(STALE.search(x['txt'])) for x in xs),
            q=sum(x['kind'] == 'question' for x in xs),
            threaded=sum(x['reply_to'] is not None for x in xs),
            friction=sum(any(p.search(x['txt']) for p in FRICTION.values()) for x in xs)))
    return rows

# reply-chain depth
def depth(x, seen=None):
    d = 0
    while x['reply_to'] is not None and x['reply_to'] in byid and d < 50:
        x = byid[x['reply_to']]; d += 1
    return d

# question -> resolution latency
def q_latency():
    out = []
    for q in [x for x in M if x['kind'] == 'question']:
        asker = q['sender']; rec = set(q['recipients'])
        # (a) explicit reply_to
        rep = [y for y in M if y['reply_to'] == q['id'] and y['t'] > q['t']]
        # (b) implicit: first ruling/report/delegation/prompt from a recipient (or Aporia/Archaeon) to the asker within 72h
        imp = [y for y in M if y['t'] > q['t'] and y['t'] - q['t'] < timedelta(hours=72)
               and asker in y['recipients'] and y['sender'] != asker
               and (y['sender'] in rec or '*' in rec)
               and y['kind'] in ('ruling', 'report', 'delegation', 'prompt', 'ack')]
        a = min((y['t'] for y in rep), default=None)
        b = min((y['t'] for y in imp), default=None)
        best = min([t for t in (a, b) if t], default=None)
        out.append(dict(id=q['id'], day=q['day'], t=q['t'], sender=asker,
                        explicit_h=(a - q['t']).total_seconds() / 3600 if a else None,
                        any_h=(best - q['t']).total_seconds() / 3600 if best else None))
    return out

# ---------------- git ----------------
G = []
for l in open(f'{D}/gitlog.tsv', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if len(p) < 4: continue
    G.append(dict(sha=p[0], t=ts(p[1]), author=p[2], s=p[3]))
SEATS = set(x['sender'] for x in M) | {'Ergon', 'Apollo', 'Charon', 'Mnemosyne'}
SEATMAP = {s.lower(): s for s in SEATS}
def seat_of(s):
    m = re.match(r'^([A-Za-z][\w\-]*)(\[[^\]]*\])?[:\s]', s)
    if not m: return None
    h = m.group(1); tag = m.group(2) or ''
    if re.fullmatch(r'[A-Z]', h) and tag.startswith('[m1-'): return 'Nestor'
    base = h.split('-')[0].lower()
    if base in SEATMAP: return SEATMAP[base]
    if base.upper() == 'ERGON': return 'Ergon'
    return None
AUTO = re.compile(r'^auto:|heartbeat|^WIP\b|portfolio update|^rows |\]: rows |\(\+1, \d+ total\)|\(close, \d+ total\)', re.I)
COORD = re.compile(r'WORK_STATE|\bSTATUS\b|journal|\badopt|\bACK\b|\bcomms\b|roster|\bqueue\b|census|\bMWO\b|\bCWO\b|handoff|NEXT_SESSION|publication record|verbatim|\bruling\b|\bsync\b|state (->|to|=)|boot|inbox|PUBLICATIONS', re.I)
SCI = re.compile(r'prereg|freez|frozen|verdict|result|receipt|\bKILL|\bPASS\b|\bFAIL|\bNULL\b|experiment|calibrat|control|holdout|blind|review packet|scorer|harness|probe|audit|replicat|falsif|baseline|gate|ablation|sweep|run\b|rows', re.I)
def cls(s):
    if AUTO.search(s): return 'auto'
    if COORD.search(s): return 'coord'
    if SCI.search(s): return 'sci'
    return 'other'
for g in G:
    g['seat'] = seat_of(g['s']); g['cls'] = cls(g['s']); g['day'] = g['t'].strftime('%m-%d')
    g['week'] = (g['t'] - timedelta(days=g['t'].weekday())).strftime('%m-%d')

VERDICT = re.compile(r'verdict|\bKILL|\bPASS\b|\bFAIL|\bNULL\b|\bresult|NEGATIVE|POSITIVE|decisive', re.I)
PREFZ = re.compile(r'prereg|freez|frozen', re.I)
AMEND = re.compile(r'amend', re.I)
POSCTL = re.compile(r'positive[- ]control|planted|\bplant\b|known[- ]answer|recover(y|s) (the )?(plant|truth)', re.I)
CHURN = re.compile(r'retract|invalidat|withdraw|supersed|correction|erratum|\brevert|re-?open|void', re.I)
REVIEW = re.compile(r'review[- ]packet|REVIEW_PACKET', re.I)
WIKI = re.compile(r'evidence[_ -]wiki|wiki (submit|claim|entry)|Mnemosyne', re.I)
BASE = re.compile(r'baseline|null model|trivial[- ]policy|floor', re.I)

def git_week_table(since='2026-07-27'):
    wk = collections.defaultdict(list)
    for g in G:
        if g['t'].strftime('%Y-%m-%d') >= since: wk[g['week']].append(g)
    rows = []
    for w in sorted(wk):
        xs = wk[w]; na = [g for g in xs if g['cls'] != 'auto']
        v = [g for g in na if VERDICT.search(g['s'])]
        # prereg-before-verdict: same seat had a prereg/freeze commit in the prior 7 days
        def prior(g):
            return any(h['seat'] == g['seat'] and PREFZ.search(h['s']) and timedelta(0) < g['t'] - h['t'] < timedelta(days=7) for h in G)
        vs = [g for g in v if g['seat']]
        rows.append(dict(week=w, all=len(xs), auto=len(xs) - len(na), nonauto=len(na),
            coord=sum(g['cls'] == 'coord' for g in na), sci=sum(g['cls'] == 'sci' for g in na),
            seats=len({g['seat'] for g in na if g['seat']}),
            verdicts=len(v), pf=sum(bool(PREFZ.search(g['s'])) for g in na),
            amend=sum(bool(AMEND.search(g['s'])) for g in na),
            v_prior_pf=(sum(map(prior, vs)) / len(vs)) if vs else None,
            v_posctl=sum(bool(POSCTL.search(g['s'])) for g in v),
            v_base=sum(bool(BASE.search(g['s'])) for g in v),
            churn=sum(bool(CHURN.search(g['s'])) for g in na),
            review=sum(bool(REVIEW.search(g['s'])) for g in na),
            wiki=sum(bool(WIKI.search(g['s'])) for g in na)))
    return rows

def git_day_table(since='2026-09-08'):
    dd = collections.defaultdict(list)
    for g in G:
        if g['t'].strftime('%Y-%m-%d') >= since: dd[g['day']].append(g)
    rows = []
    for d in sorted(dd):
        xs = dd[d]; na = [g for g in xs if g['cls'] != 'auto']
        rows.append(dict(day=d, all=len(xs), nonauto=len(na), coord=sum(g['cls'] == 'coord' for g in na),
                         sci=sum(g['cls'] == 'sci' for g in na), seats=len({g['seat'] for g in na if g['seat']}),
                         ws=sum('WORK_STATE' in g['s'] for g in na)))
    return rows

def md(rows, cols=None, fmt=None):
    cols = cols or list(rows[0])
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for r in rows:
        cells = []
        for c in cols:
            v = r[c]
            cells.append('-' if v is None else (f'{v:.2f}' if isinstance(v, float) else str(v)))
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)

def window(xs, key_t, a, b):
    return [x for x in xs if a <= key_t(x) < b]

if __name__ == '__main__':
    import sys
    T = lambda s: datetime.fromisoformat(s).replace(tzinfo=EDT)
    print('## comms per day\n'); dt = day_table()
    for r in dt:
        r['overhead_%'] = 100.0 * r['overhead'] / r['n']; r['operator_%'] = 100.0 * r['operator'] / r['n']
        r['threaded_%'] = 100.0 * r['threaded'] / r['n']
    print(md(dt, ['day', 'n', 'senders', 'overhead', 'overhead_%', 'operator', 'operator_%', 'stale', 'friction', 'q', 'threaded_%']))
    ql = q_latency()
    print('\n## question latency (hours) per window\n')
    WINDOWS = [('W0 comms bring-up 09-11..09-14', '2026-09-11', '2026-09-15'),
               ('W1 Opus5 steady 09-15..09-22', '2026-09-15', '2026-09-23'),
               ('W2 Opus5.5 pre-ops 09-23..09-26', '2026-09-23', '2026-09-27'),
               ('W3 ops pilot (TH/C/E ids) 09-27..09-28 17:00', '2026-09-27', '2026-09-28T17:00'),
               ('W4 Fabric lease + MWO + WORK_STATE 09-28 17:00..09-30 04:18', '2026-09-28T17:00', '2026-09-30T04:18'),
               ('W5 CWO A/B/C 09-30 04:18..', '2026-09-30T04:18', '2026-10-02')]
    wr = []
    for name, a, b in WINDOWS:
        A, B = T(a), T(b)
        qs = window(ql, lambda x: x['t'], A, B)
        ex = [q['explicit_h'] for q in qs if q['explicit_h'] is not None]
        an = [q['any_h'] for q in qs if q['any_h'] is not None]
        ms = window(M, lambda x: x['t'], A, B)
        deps = [depth(x) for x in ms]
        hrs = (min(B, max(x['t'] for x in M)) - A).total_seconds() / 3600
        wr.append(dict(window=name, msgs=len(ms), msgs_per_h=len(ms) / hrs if hrs > 0 else None,
            senders=len({x['sender'] for x in ms}),
            overhead_pct=100.0 * sum(map(is_overhead, ms)) / len(ms) if ms else None,
            operator_pct=100.0 * sum(bool(OPERATOR.search(x['txt'])) for x in ms) / len(ms) if ms else None,
            stale_pct=100.0 * sum(bool(STALE.search(x['txt'])) for x in ms) / len(ms) if ms else None,
            friction_pct=100.0 * sum(any(p.search(x['txt']) for p in FRICTION.values()) for x in ms) / len(ms) if ms else None,
            threaded_pct=100.0 * sum(x['reply_to'] is not None for x in ms) / len(ms) if ms else None,
            mean_depth=st.mean(deps) if deps else None, max_depth=max(deps) if deps else None,
            questions=len(qs), q_answered_pct=100.0 * len(an) / len(qs) if qs else None,
            q_med_h_any=st.median(an) if an else None, q_med_h_explicit=st.median(ex) if ex else None))
    print(md(wr))
    print('\n## friction categories: messages per window, distinct days with >=1 report\n')
    fr = []
    for k, p in FRICTION.items():
        r = dict(category=k)
        for name, a, b in WINDOWS:
            ms = window(M, lambda x: x['t'], T(a), T(b))
            r[name.split()[0]] = sum(bool(p.search(x['txt'])) for x in ms)
        hits = [x for x in M if p.search(x['txt'])]
        r['total'] = len(hits); r['days'] = len({x['day'] for x in hits}); r['seats'] = len({x['sender'] for x in hits})
        fr.append(r)
    print(md(fr))
    print('\n## kind mix per window (% of messages)\n')
    km = []
    for name, a, b in WINDOWS:
        ms = window(M, lambda x: x['t'], T(a), T(b)); c = collections.Counter(x['kind'] for x in ms)
        r = dict(window=name.split()[0])
        for k in ['report', 'delegation', 'ack', 'ruling', 'prompt', 'broadcast', 'question']:
            r[k] = 100.0 * c[k] / len(ms)
        km.append(r)
    print(md(km))
    print('\n## git weekly (week starting Monday, local)\n')
    gw = git_week_table()
    for r in gw:
        r['coord_%'] = 100.0 * r['coord'] / r['nonauto'] if r['nonauto'] else None
        r['sci_per_seat'] = r['sci'] / r['seats'] if r['seats'] else None
        r['amend_per_pf'] = r['amend'] / r['pf'] if r['pf'] else None
        r['posctl_%v'] = 100.0 * r['v_posctl'] / r['verdicts'] if r['verdicts'] else None
        r['base_%v'] = 100.0 * r['v_base'] / r['verdicts'] if r['verdicts'] else None
        r['churn_%'] = 100.0 * r['churn'] / r['nonauto'] if r['nonauto'] else None
    print(md(gw, ['week', 'all', 'auto', 'nonauto', 'seats', 'coord_%', 'sci', 'sci_per_seat', 'verdicts', 'v_prior_pf', 'pf', 'amend', 'amend_per_pf', 'posctl_%v', 'base_%v', 'churn_%', 'review', 'wiki']))
    print('\n## git daily 09-08..\n')
    gd = git_day_table()
    for r in gd:
        r['coord_%'] = 100.0 * r['coord'] / r['nonauto'] if r['nonauto'] else None
    print(md(gd, ['day', 'all', 'nonauto', 'seats', 'coord', 'coord_%', 'sci', 'ws']))
    # adoption speed of control-plane documents
    print('\n## adoption latency\n')
    for label, pat, t0 in [('MWO-0001 WORK_STATE adoption', r'adopt(s|ed)? MWO-0001|MWO-0001 adopted|WORK_STATE.*MWO-0001|MWO-0001.*WORK_STATE', '2026-09-28T21:48:58'),
                           ('CWO-B heartbeat reply', r'HEARTBEAT CWO-B', '2026-09-30T09:16:22')]:
        T0 = T(t0)
        cm = [(x['sender'], (x['t'] - T0).total_seconds() / 3600) for x in M if re.search(pat, x['subject'] or '') and x['t'] >= T0]
        gm = [(g['seat'], (g['t'] - T0).total_seconds() / 3600) for g in G if re.search(pat, g['s']) and g['t'] >= T0]
        first = {}
        for s, h in sorted(cm + gm, key=lambda z: z[1]):
            if s and s not in first: first[s] = h
        hs = sorted(first.values())
        print(f'{label}: seats={len(first)} median_h={st.median(hs) if hs else None:.2f} max_h={max(hs) if hs else 0:.2f} within1h={sum(h <= 1 for h in hs)}  {sorted(first.items(), key=lambda z: z[1])}')
    # seats per CWO census
    unattr = sum(1 for g in G if g['t'].strftime('%Y-%m') == '2026-09' and not g['seat'])
    print(f'\nSep commits unattributed to a seat: {unattr} of {sum(1 for g in G if g["t"].strftime("%Y-%m")=="2026-09")}')
    print('Sep class mix:', collections.Counter(g['cls'] for g in G if g['t'].strftime('%Y-%m') == '2026-09'))
