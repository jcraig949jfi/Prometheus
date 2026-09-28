"""Review 6, step 2 driver: v4 identification, flip coverage, Q8c, Q4, Q-homology, Q2/P2 on r025144's 92 births."""
import json, os, random, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r6_v4 import *  # noqa

P = json.load(open(os.path.join(HERE, "r6_births_pre.json")))
rng = random.Random(606)
K = 8
out = []
for bi, p in enumerate(P):
    wt = bytes.fromhex(p['writer_tape']); ot = bytes.fromhex(p['occ_tape']) if p['occ_tape'] else None; inp = p['inputs']
    mem0 = build_mem(wt, ot, inp)
    r = run(mem0, inp, ot is not None)
    assert born(r, ot) and bytes(r['mem'][L:2 * L]).hex() == p['child'], bi
    child = r['mem'][L:2 * L]
    loci = []
    for j in range(L):
        q = r['rec'][j]; d = q['data']
        dent = ent(d[1]) if d[0] == 'M' else None
        pent = ent(d[1]) if False else (ent(q['perf'][1]) if q['perf'][0] == 'M' else None)
        allowed = {dent, pent} - {None}
        def ok(sets):
            u = set().union(*sets)
            return not any(b[0] in ('INPUT', 'OTHER', 'ENV') for b in u) and not any(ent(b) and ent(b) not in allowed for b in u)
        rid_len = dent is not None and ok([q['ctrl_store'], q['addr'], q['exec_store']])
        rid_str = dent is not None and ok([r['ctrl_end'], q['addr'], r['exec_end']])
        # why not identified (lenient)
        why = []
        if dent is None: why.append('data:' + (d[1][1] if d[0] == 'M' else {'X': 'COMPUTED', 'CF': 'COMPUTED_FROM'}[d[0]]))
        for nm, s in (('ctrl', q['ctrl_store']), ('addr', q['addr']), ('exec', q['exec_store'])):
            if any(b[0] == 'INPUT' for b in s): why.append(nm + ':INPUT')
            if any(ent(b) and ent(b) not in allowed for b in s): why.append(nm + ':foreign_entity')
        src = d[1] if dent else None
        loci.append({'j': j, 'dent': dent, 'src': src, 'perf': pent, 'rid_len': rid_len, 'rid_str': rid_str, 'why': why,
                     'kind': d[0] if d[0] != 'M' else ('M-' + (dent or d[1][1]))})
    # ---- s4.1 path-preserving flip test on rule-identified (lenient) entity-MOVE loci
    base_fetch = r['fetch']; base_st = r['stores']
    for lc in loci:
        if not lc['rid_len']:
            lc['flip'] = None; continue
        e, i = lc['src']; addr = i if e == 'W' else L + i
        app = fail = 0
        for bit in range(8):
            m = bytearray(mem0); m[addr] ^= 1 << bit
            rr = run(m, inp, ot is not None, want_labels=False)
            if rr['fetch'] != base_fetch or rr['stores'] != base_st:
                continue
            app += 1
            if rr['mem'][L + lc['j']] != (mem0[addr] ^ (1 << bit)):
                fail += 1
        lc['flip'] = 'FAILED' if fail else ('CONFIRMED' if app else 'INAPPLICABLE')
    # ---- Q8c: per written locus, randomise each ENTITY other than the data-label entity, K draws
    ents = ['W'] + (['O'] if ot is not None else [])
    cache = {}
    for e in ents:
        res = []
        for k in range(K):
            m = bytearray(mem0)
            rnd = bytes(rng.randrange(256) for _ in range(L))
            if e == 'W': m[:L] = rnd; occ = ot
            else: m[L:2 * L] = rnd; occ = rnd
            rr = run(m, inp, ot is not None, want_labels=False)
            res.append((born(rr, occ), rr['mem'][L:2 * L], {a - L for a in rr['writes'] if L <= a < 2 * L}))
        cache[e] = res
    for lc in loci:
        arms = [e for e in ents if e != lc['dent']]
        ch = []
        for e in arms:
            for (b, ch_mem, wr) in cache[e]:
                ch.append(1 if (not b or lc['j'] not in wr or ch_mem[lc['j']] != child[lc['j']]) else 0)
        lc['q8c'] = sum(ch) / len(ch) if ch else 0.0
        lc['q8c_n'] = len(ch)
    q8c_whether = {e: sum(1 for (b, _, _) in cache[e] if not b) / K for e in ents}
    # ---- Q4 capability of the child in isolation: 8 random occupants x 40 random inputs
    ninp = len(inp); cap = 0; r4 = random.Random(bi)
    for o8 in range(8):
        occ = bytes(r4.randrange(256) for _ in range(L))
        for i40 in range(40):
            ii = [r4.randrange(256) for _ in range(ninp)]
            m = build_mem(bytes(child), occ, ii)
            mm, tr = frozen(m, ii)
            wr = {a - L for a in tr.writes if L <= a < 2 * L}
            cap += (len(wr) == L and bytes(mm[L:2 * L]) == bytes(child))
    out.append({'bi': bi, 'tick': p['tick'], 'native': p['row'][6], 'empty': ot is None, 'loci': loci, 'q8c_whether': q8c_whether,
                'cap': cap / 320, 'budget_end': r['budget_end'], 'halted': r['halted'], 'n_steps': len(r['fetch']),
                'ctrl_end_n': len(r['ctrl_end']), 'ctrl_end_input': any(b[0] == 'INPUT' for b in r['ctrl_end']),
                'exec_end_has_O': any(b[0] == 'O' for b in r['exec_end']), 'exec_end_input': any(b[0] == 'INPUT' for b in r['exec_end'])})
    print(bi, end=' ', flush=True)
print()


def ser(o):
    if isinstance(o, (set, frozenset, tuple)): return list(o)
    raise TypeError(o)


json.dump(out, open(os.path.join(HERE, "r6_results.json"), "w"), default=ser)
print("done")
