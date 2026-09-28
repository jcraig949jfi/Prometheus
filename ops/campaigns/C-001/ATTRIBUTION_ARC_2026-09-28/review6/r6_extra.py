"""Review 6 extra checks:
 (a) precision arm vs the 'exec_deps = all memory' over-taint mutant (names W and O on every locus): does it pass?
 (b) Q8c amended: randomise only entities NOT in {data-label entity, performer entity}.
 (c) whole-execution ctrl scope on the frozen vm's own textbook hybrids (copy-then-task, task-then-copy), COND_MULTI inputs.
 (d) mechanism census: births whose window stores come from an LDIR entered with C==0 (256-byte wrap sweep)."""
import json, os, random, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from r6_v4 import *  # noqa
P = json.load(open(os.path.join(HERE, "r6_births_pre.json"))); R = json.load(open(os.path.join(HERE, "r6_results.json")))
rng = random.Random(808); K = 8
mut_named = mut_changed = 0; amended = []; per_birth_amended = []
for bi, p in enumerate(P):
    wt = bytes.fromhex(p['writer_tape']); ot = bytes.fromhex(p['occ_tape']) if p['occ_tape'] else None; inp = p['inputs']
    mem0 = build_mem(wt, ot, inp); r = run(mem0, inp, ot is not None); child = r['mem'][L:2 * L]
    arms = {}
    for e in (['W', 'O'] if ot is not None else ['W']):
        res = []
        for k in range(K):
            m = bytearray(mem0); rnd = bytes(rng.randrange(256) for _ in range(L))
            if e == 'W': m[:L] = rnd; occ = ot
            else: m[L:2 * L] = rnd; occ = rnd
            rr = run(m, inp, ot is not None, want_labels=False)
            res.append((born(rr, occ), rr['mem'][L:2 * L], {a - L for a in rr['writes'] if L <= a < 2 * L}))
        arms[e] = res
    ch = lambda res, j: [int((not b) or (j not in wr) or cm[j] != child[j]) for b, cm, wr in res]
    bq = []
    for l in R[bi]['loci']:
        j = l['j']
        for e in arms:                      # over-taint mutant names every entity
            mut_named += 1; mut_changed += any(ch(arms[e], j))
        other = [e for e in arms if e not in {l['dent'], l['perf']}]
        v = [x for e in other for x in ch(arms[e], j)]
        if v: amended.append(sum(v) / len(v)); bq.append(sum(v) / len(v))
    per_birth_amended.append(bq)
print("(a) over-taint mutant (exec_deps = all memory) precision share: %d/%d = %.3f  (v4 fails a class only below 0.20)" % (
    mut_changed, mut_named, mut_changed / mut_named))
n_arm = len(amended)
print("(b) amended Q8c (exclude data entity AND performer): loci with >=1 arm %d of %d; mean over them %.3f" % (
    n_arm, 64 * len(P), sum(amended) / max(1, n_arm)))
print("    births with >=1 armed locus:", sum(1 for b in per_birth_amended if b))

# (c) textbook hybrids on the frozen vm, SHARED, occupied window, COND_MULTI-style 1-input tasks
rep = V.replicator_copyall(L); task = V.witness_cond_multi()
copy_then_task = V.hybrid(rep, task)
# task-then-copy: IN; CP 128; JC over the edit; edit; out: OUT; then the copier
task_body = task[:-1]                                     # drop HALT, fall into copier
task_then_copy = task_body + rep
for nm, tape in (('copy-then-task', copy_then_task), ('task-then-copy', task_then_copy)):
    t = bytearray(L); t[:len(tape)] = tape
    res = collections.Counter()
    for trial in range(40):
        occ = bytes(rng.randrange(256) for _ in range(L)); inp = [rng.randrange(256)]
        rr = run(build_mem(bytes(t), occ, inp), inp, True)
        ok_len = ok_str = 0
        for j in range(L):
            q = rr['rec'][j]
            f = lambda S: not any(b[0] == 'INPUT' or b[0] == 'O' for b in S)
            ok_len += q['data'] == ('M', ('W', j)) and f(q['ctrl_store']) and f(q['exec_store']) and f(q['addr'])
            ok_str += q['data'] == ('M', ('W', j)) and f(rr['ctrl_end']) and f(rr['exec_end']) and f(q['addr'])
        res['born'] += born(rr, occ); res['len_ident'] += ok_len; res['str_ident'] += ok_str; res['loci'] += L
    print("(c) %-15s births %d/40; identified loci: at-store scope %d/%d, whole-execution scope %d/%d" % (
        nm, res['born'], res['len_ident'], res['loci'], res['str_ident'], res['loci']))

# (d) mechanism census
sweep = 0; srcwin = 0
for bi, p in enumerate(P):
    wt = bytes.fromhex(p['writer_tape']); ot = bytes.fromhex(p['occ_tape']) if p['occ_tape'] else None; inp = p['inputs']
    mem = build_mem(wt, ot, inp); r = shadow(mem, inp, ot is not None, want_labels=False)
    # re-walk to find LDIR entries with C==0: count stores > 128 as a wrap sweep proxy
    sweep += len(r['stores']) >= 128
    srcs = [l['src'] for l in R[bi]['loci'] if l['src']]
    srcwin += (sum(1 for s in srcs if s[0] == 'O') + sum(1 for l in R[bi]['loci'] if l['kind'] == 'M-empty')) >= 32
print("(d) births with >=128 stores in one interaction (wrap sweep):", sweep, "of", len(P),
      "; births whose majority window value came from the window itself (O or EMPTY):", srcwin)
