"""INV_E: induction vs coverage in the alien-lawful pilot (Claude).
Read-only over hecate/alien data + runs. Run from the worktree root:
    python roles/Hecate/harvest_w2/INV_E_induction_vs_coverage.py > out.txt
Witness = set of rule-table entries (taint-tracked through the interpreter) that a
next-state COMPONENT depends on (A systems); for K systems (no tables) and as a
family-agnostic second notion, RF = (component, values of its receptive field).
Covered = every witness key of that component was consulted at some observed source.
"""
import json, sys, itertools, pickle, os
from collections import defaultdict
import numpy as np
sys.path.insert(0, '.')
from hecate.alien.systems import parse_state, dims_of, all_states, step, trajectory, clamp_run
from hecate.alien.baselines import fit_localtab, pred_localtab, _transitions
from hecate.alien import sandbox as SB

K = json.load(open('hecate/alien/data/answer_key.json'))
PUB = {e['id']: e for e in json.load(open('hecate/alien/data/public.json'))}
def jl(t): return {json.loads(l)['sid']: json.loads(l) for l in open(f'hecate/alien/runs/claude/{t}.jsonl', encoding='utf-8') if l.strip()}
BL, AC, RV = jl('blind'), jl('active'), jl('reveal')

# ---------------- taint-tracked witnesses (per output component) ----------------
def W_base(p, s):
    x = list(s); n = len(x); k = p.get('kind'); f = p['family']
    if f == 'tab' and k == 'tab_local':
        keys = [('D', i, x[i], x[p['nb'][i]]) for i in range(n)]
        out = [{keys[i]} for i in range(n)]
        if p.get('mode') in ('lin', 'cyc'):
            c = p['comp']; out[c] = {keys[j] for j in range(n) if j != c and p['w'][j]}
        return out
    if f == 'tab' and k == 'tab_rev':
        t = [set() for _ in x]
        for i in p['order']:
            nb = p['nb'][i]; t[i] = t[i] | t[nb] | {('U', i, x[nb])}
            x[i] = (x[i] + p['D'][i][x[nb]]) % 5
        return t
    if f == 'graph' and k == 'graph_attr':
        nbrs = [[] for _ in x]
        for u, v in p['edges']: nbrs[u].append(v); nbrs[v].append(u)
        return [{('G', x[i], sum(x[j] for j in nbrs[i]) % 4)} for i in range(n)]
    if f == 'graph' and k == 'graph_flow':
        t = [set() for _ in x]
        for u, v in p['edges']:
            key = ('F', x[u], x[v]); tt = t[u] | t[v] | {key}; t[u] = tt; t[v] = set(tt)
            d = p['F'][x[u]][x[v]]
            if 0 <= x[u] + d <= 3 and 0 <= x[v] - d <= 3: x[u] += d; x[v] -= d
        return t
    if f == 'rewrite':
        ks = set()
        for pos in range(n - 1):
            ks.add(('R', x[pos], x[pos + 1]))
            if any(x[pos] == a and x[pos + 1] == b for (a, b), _ in p['rules']): break
        return [set(ks) for _ in x]
    if f == 'vm':
        c, r = x[0], x[1:]; ins = p['program'][c]; op = ins[0]; P = ('P', c)
        out = [{P} for _ in x]
        if op == 'mix':
            _, a, b, z, *_ = ins; key = ('g', c, r[b]); out[1 + a] |= {key}; out[1 + z] |= {key}
        elif op == 'aff':
            _, a, b, z, *_ = ins; out[1 + a] |= {('aff', c, r[b], r[z])}
        elif op == 'tab':
            _, a, b, _T = ins; out[1 + a] |= {('T', c, r[b])}
        elif op in ('jz', 'jnz'):
            out[0] |= {('J', c, r[ins[1]])}
        return out
    if f == 'map' and k == 'shear':
        X, Y = x; x2 = (X + sum(cc * pow(Y, i, 31) for i, j, cc in p['h1'])) % 31
        return [{('h1', Y)}, {('h1', Y), ('h2', x2)}]
    if f == 'map' and k == 'poly_sym':
        X, Y = x; return [{('g', X, Y)}, {('g', Y, X)}]
    return None

def W(p, s):
    if p.get('wrap') == 'linmix':
        z = tuple(int(v) for v in (np.array(p['Minv']) @ np.array(s)) % p['mod'])
        wb = W_base(p['base'], z)
        if wb is None: return None
        M = p['M']
        return [set().union(*[wb[kk] for kk in range(len(z)) if M[j][kk] % p['mod']]) for j in range(len(s))]
    return W_base(p, s)

# ---------------- OCD: oracle architecture + seen entries + "nothing happens" default ----------------
def OCD_base(p, s, sw):
    x = list(s); n = len(x); k = p.get('kind'); f = p['family']
    if f == 'tab' and k == 'tab_local':
        d = [p['D'][i][x[i]][x[p['nb'][i]]] if ('D', i, x[i], x[p['nb'][i]]) in sw else 0 for i in range(n)]
        if p.get('mode') in ('lin', 'cyc'):
            c, w = p['comp'], p['w']; tot = sum(w[i] * d[i] for i in range(n) if i != c)
            d[c] = (((0 if p['mode'] == 'lin' else 1) - tot) * pow(w[c], -1, 5)) % 5
        return tuple((x[i] + d[i]) % 5 for i in range(n))
    if f == 'tab' and k == 'tab_rev':
        for i in p['order']:
            nb = p['nb'][i]; x[i] = (x[i] + (p['D'][i][x[nb]] if ('U', i, x[nb]) in sw else 0)) % 5
        return tuple(x)
    if f == 'graph' and k == 'graph_attr':
        nbrs = [[] for _ in x]
        for u, v in p['edges']: nbrs[u].append(v); nbrs[v].append(u)
        out = []
        for i in range(n):
            S = sum(x[j] for j in nbrs[i]) % 4
            out.append(p['G'][x[i]][S] if ('G', x[i], S) in sw else x[i])
        return tuple(out)
    if f == 'graph' and k == 'graph_flow':
        for u, v in p['edges']:
            d = p['F'][x[u]][x[v]] if ('F', x[u], x[v]) in sw else 0
            if 0 <= x[u] + d <= 3 and 0 <= x[v] - d <= 3: x[u] += d; x[v] -= d
        return tuple(x)
    if f == 'rewrite':
        for pos in range(n - 1):
            if ('R', x[pos], x[pos + 1]) not in sw: continue
            for (a, b), (c, d) in p['rules']:
                if x[pos] == a and x[pos + 1] == b:
                    x[pos], x[pos + 1] = c, d; return tuple(x)
        return tuple(x)
    if f == 'vm':
        c, r = x[0], x[1:]
        if ('P', c) not in sw: return tuple([(c + 1) % 6] + r)
        ins = p['program'][c]; op = ins[0]; nxt = (c + 1) % 6
        if op == 'mix':
            _, a, b, z, g, kk, kz = ins; gv = g[r[b]] if ('g', c, r[b]) in sw else 0
            r[a] = (r[a] + kk * gv) % 7; r[z] = (r[z] - kz * gv) % 7
        elif op == 'aff':
            _, a, b, z, k1, k2, e = ins
            if ('aff', c, r[b], r[z]) in sw: r[a] = (k1 * r[b] + k2 * r[z] + e) % 7
        elif op == 'tab':
            _, a, b, T = ins
            if ('T', c, r[b]) in sw: r[a] = T[r[b]]
        elif op in ('jz', 'jnz'):
            if ('J', c, r[ins[1]]) in sw:
                z = r[ins[1]] == 0
                nxt = ins[2] if (z if op == 'jz' else not z) else nxt
        elif op == 'jmp':
            nxt = ins[1]
        return tuple([nxt] + r)
    if f == 'map' and k == 'shear':
        from hecate.alien.systems import _poly
        X, Y = x; X2 = (X + (_poly(p['h1'], Y, 0, 31) if ('h1', Y) in sw else 0)) % 31
        Y2 = (Y + (_poly(p['h2'], X2, 0, 31) if ('h2', X2) in sw else 0)) % 31
        return (X2, Y2)
    if f == 'map' and k == 'poly_sym':
        from hecate.alien.systems import _poly
        X, Y = x
        return (_poly(p['g'], X, Y, 31) if ('g', X, Y) in sw else X, _poly(p['g'], Y, X, 31) if ('g', Y, X) in sw else Y)
    return None

def OCD(p, s, sw):
    if p.get('wrap') == 'linmix':
        z = tuple(int(v) for v in (np.array(p['Minv']) @ np.array(s)) % p['mod'])
        gz = OCD_base(p['base'], z, sw)
        return tuple(int(v) for v in (np.array(p['M']) @ np.array(gz)) % p['mod'])
    return OCD_base(p, s, sw)

# ---------------- receptive fields (exhaustive) ----------------
RFC = 'C:/Users/jcrai/AppData/Local/Temp/claude/F--prometheus/dd0c3882-b7cd-448c-8a58-3c002b4bbbc8/scratchpad/rf_cache.pkl'
RF = pickle.load(open(RFC, 'rb')) if os.path.exists(RFC) else {}
def rf(sid, p):
    if sid in RF: return RF[sid]
    dims = dims_of(p); n = len(dims); dep = [set() for _ in range(n)]
    sts = all_states(dims); nx = {s: step(p, s) for s in sts}
    for s in sts:
        for j in range(n):
            for v in range(dims[j]):
                if v == s[j]: continue
                s2 = list(s); s2[j] = v; t2 = nx[tuple(s2)]
                for i in range(n):
                    if t2[i] != nx[s][i]: dep[i].add(j)
            if all(len(d) == n for d in dep): break
    RF[sid] = [sorted(d) for d in dep]; return RF[sid]

def rfkey(R, s): return [(i, tuple(s[j] for j in R[i])) for i in range(len(R))]

# ---------------- subject code ----------------
def run_code(src, states):
    out = SB.run(src, 'step', states)
    if isinstance(out, dict) and 'call' in out.get('error', ''):   # prior side finding: local lambda rejected
        B = {k: __builtins__[k] if isinstance(__builtins__, dict) else getattr(__builtins__, k) for k in SB.SAFE_CALLS if k not in ('step', 'g', 'q')}
        env = {'__builtins__': B}; exec(src, env); out = []
        for s in states:
            try: out.append([int(v) for v in env['step'](list(s))])
            except Exception: out.append(None)
        return out, 'UNSANDBOXED'
    if isinstance(out, dict): return None, out['error']
    return out, 'OK'

def comp_correct(pred, truth, n):
    if pred is None or len(pred) != n: return [False] * n
    return [int(a) == int(b) for a, b in zip(pred, truth)]

def obs_sources(p, trajs):
    src = []
    for t in trajs:
        st = [parse_state(p, s) for s in t]; src += st[:-1]
    return src

def active_sources(p, pub, row):
    src = obs_sources(p, pub['observations'][:2]); ts = _transitions(p, {'observations': pub['observations'][:2]})
    for h in row['history']:
        q = h['query']
        try:
            st = parse_state(p, q['start']); steps = max(1, min(6, int(q.get('steps', 6))))
            if q['query'] == 'run':
                tr = trajectory(p, st, steps); src += tr[:-1]; ts += list(zip(tr[:-1], tr[1:]))
            elif q['query'] == 'clamp':
                s0 = list(st); s0[int(q['position'])] = int(q['value']); tr = [tuple(s0)] + clamp_run(p, st, int(q['position']), int(q['value']), steps)
                src += tr[:-1]   # clamp transitions: sources seen, but pair is not a pure step -> not added to baseline ts
        except Exception:
            pass
    return src, ts

def seen_sets(sid, p, srcs):
    R = rf(sid, p); sw, sr = set(), set()
    for s in srcs:
        w = W(p, s)
        if w: [sw.update(x) for x in w]
        sr.update(rfkey(R, s))
    return sw, sr

def classify(sid, p, s, sw, sr):
    w = W(p, s); R = rf(sid, p)
    tab = [None if w is None else (wi <= sw) for wi in w] if w else [None] * len(s)
    rfc = [k in sr for k in rfkey(R, s)]
    return tab, rfc

LAWFUL = [sid for sid, e in K.items() if e['class'] in ('ALIEN_LAWFUL', 'KNOWN_LAWFUL')]
def label(e):
    p = e['params']; base = p.get('base', p)
    kind = base.get('kind') or base['family']
    return ('K' if e['class'] == 'KNOWN_LAWFUL' else 'A'), e['family'], (('linmix:' + kind) if p.get('wrap') == 'linmix' else kind)

def per_component(sid, srcs, ts, code, states, truths, t2preds=None):
    e = K[sid]; p = e['params']; dims = dims_of(p); n = len(dims)
    sw, sr = seen_sets(sid, p, srcs); lt = fit_localtab(ts, dims)
    out, status = (run_code(code, states) if code else (None, 'NO_CODE'))
    recs = []
    for k, (s, t) in enumerate(zip(states, truths)):
        tab, rfc = classify(sid, p, s, sw, sr)
        cl = comp_correct(None if out is None else out[k], t, n)
        bl = comp_correct(pred_localtab(lt, s, dims), t, n)
        idn = comp_correct(s, t, n)
        for i in range(n):
            recs.append(dict(sid=sid, st=k, i=i, tab=tab[i], rf=rfc[i], cl=cl[i], bl=bl[i], idn=idn[i],
                             pred=None if out is None else out[k], src=s, truth=t))
    return recs, status

if __name__ == '__main__':
    res = {'blind': {}, 'blind_t2': {}, 'active': {}, 'active_blindcov': {}, 'reveal_t2': {}, 'status': {}}
    for sid in sorted(LAWFUL):
        e = K[sid]; p = e['params']; pub = PUB[sid]; ans = e['answers']
        ev = [tuple(s) for s in ans['eval_states']]; evn = [tuple(s) for s in ans['eval_next']]
        srcs = obs_sources(p, pub['observations']); ts = _transitions(p, pub)
        code = (BL[sid]['parsed'] or {}).get('t5', {}).get('code')
        res['blind'][sid], res['status'][sid] = per_component(sid, srcs, ts, code, ev, evn)
        # T2: predictions as 'code output'
        q2 = [tuple(s) for s in ans['q2_states']]; a2 = [tuple(s) for s in ans['t2']]
        sw, sr = seen_sets(sid, p, srcs); lt = fit_localtab(ts, dims_of(p)); n = len(dims_of(p))
        def t2recs(preds):
            rr = []
            for k, (s, t) in enumerate(zip(q2, a2)):
                try: pr = parse_state(p, preds[k])
                except Exception: pr = None
                tab, rfc = classify(sid, p, s, sw, sr)
                cl = comp_correct(pr, t, n); bl = comp_correct(pred_localtab(lt, s, dims_of(p)), t, n)
                for i in range(n): rr.append(dict(sid=sid, i=i, tab=tab[i], rf=rfc[i], cl=cl[i], bl=bl[i], idn=s[i] == t[i], pred=pr, src=s, truth=t))
            return rr
        res['blind_t2'][sid] = t2recs(((BL[sid]['parsed'] or {}).get('t2') or {}).get('predictions') or [])
        if sid in RV and RV[sid]['parsed']:
            res['reveal_t2'][sid] = t2recs((RV[sid]['parsed'].get('t2') or {}).get('predictions') or [])
        if sid in AC:
            asrc, ats = active_sources(p, pub, AC[sid])
            acode = (AC[sid]['parsed'] or {}).get('t5', {}).get('code')
            res['active'][sid], _ = per_component(sid, asrc, ats, acode, ev, evn)
            res['active_blindcov'][sid], _ = per_component(sid, srcs, ts, acode, ev, evn)
        print(sid, label(e), res['status'][sid], file=sys.stderr)
    pickle.dump(RF, open(RFC, 'wb'))
    pickle.dump(res, open(RFC.replace('rf_cache', 'inv_e_res'), 'wb'))
