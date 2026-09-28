"""Review 6: v4 s4.2 completeness and precision arms, and per-class flip coverage (v4 s2.1 classes by performer)."""
import json, os, random, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from r6_v4 import *  # noqa
P = json.load(open(os.path.join(HERE, "r6_births_pre.json"))); R = json.load(open(os.path.join(HERE, "r6_results.json")))
rng = random.Random(707); K = 8
prec = collections.Counter(); comp_ok = collections.Counter(); comp_n = collections.Counter(); input_changes = 0
for bi, p in enumerate(P):
    wt = bytes.fromhex(p['writer_tape']); ot = bytes.fromhex(p['occ_tape']) if p['occ_tape'] else None; inp = p['inputs']
    mem0 = build_mem(wt, ot, inp); r = run(mem0, inp, ot is not None); child = r['mem'][L:2 * L]
    executed = {pc for pc, op in r['fetch']} | {(pc + 1) & 0xFF for pc, op in r['fetch'] if V.OPLEN.get(op, 0)}
    def arm(addrs, occ_rand=False):
        res = []
        for k in range(K):
            m = bytearray(mem0)
            for a in addrs: m[a] = rng.randrange(256)
            occ = bytes(m[L:2 * L]) if (ot is not None) else None
            rr = run(m, inp, ot is not None, want_labels=False)
            wr = {a - L for a in rr['writes'] if L <= a < 2 * L}
            res.append((born(rr, occ), rr['mem'][L:2 * L], wr))
        return res
    def changed(res, j):
        return any((not b) or (j not in wr) or cm[j] != child[j] for b, cm, wr in res)
    ents = {'W': range(0, L)}
    if ot is not None: ents['O'] = range(L, 2 * L)
    whole = {e: arm(list(a)) for e, a in ents.items()}
    split = {}
    for e, a in ents.items():
        split[(e, 'exec')] = arm([x for x in a if x in executed])
        split[(e, 'nonexec')] = arm([x for x in a if x not in executed])
    split[('INPUT', 'all')] = arm([IN_BASE + k for k in range(len(inp))])
    cls = collections.Counter(l['perf'] or 'x' for l in R[bi]['loci']).most_common(1)[0][0]
    cls = {'W': 'self', 'O': 'occupant'}.get(cls, 'input/scratch')
    rec = r['rec']
    for j in range(L):
        q = rec[j]; named = set()
        for s in (q['addr'], q['ctrl_store'], q['exec_store'], {q['data'][1]} if q['data'][0] == 'M' else set(q['data'][1])):
            for b in s:
                if ent(b): named.add(ent(b))
                if b[0] == 'INPUT': named.add('INPUT')
        for e in named & set(ents):
            prec[(cls, 'named')] += 1; prec[(cls, 'changes')] += changed(whole[e], j)
        for (e, part), res in split.items():
            if changed(res, j):
                comp_n[cls] += 1; comp_ok[cls] += (e in named)
                if e == 'INPUT': input_changes += 1
print("precision arm (share of named ENTITY dependences whose randomisation ever changes value/write/birth):")
for c in sorted({k[0] for k in prec}):
    print("   %s: %d/%d = %.3f" % (c, prec[(c, 'changes')], prec[(c, 'named')], prec[(c, 'changes')] / prec[(c, 'named')]))
print("completeness arm (changed loci-arms naming the randomised source):", {c: "%d/%d" % (comp_ok[c], comp_n[c]) for c in comp_n})
print("INPUT-arm changed loci:", input_changes)
# per-class flip coverage with v4 s2.1 classes
cov = collections.defaultdict(collections.Counter); births = collections.Counter(); ident = collections.Counter()
for b in R:
    cls = collections.Counter(l['perf'] or 'x' for l in b['loci']).most_common(1)[0][0]
    cls = {'W': 'self', 'O': 'occupant'}.get(cls, 'input/scratch')
    births[cls] += 1; ident[cls] += sum(l['rid_len'] for l in b['loci']) >= 0.9 * 64
    for l in b['loci']:
        if l['rid_len']: cov[cls][l['flip']] += 1
for c in births:
    cc = cov[c]; n = sum(cc.values())
    print("class %-9s births %3d identifiable %3d (%.0f%%) rule-identified loci %4d flip %s coverage %s" % (
        c, births[c], ident[c], 100 * ident[c] / births[c], n, dict(cc), "%.3f" % ((cc['CONFIRMED'] + cc['FAILED']) / n) if n else "0/0"))
