"""Review 6: summarise r6_results.json into the numbers v4's verdict logic needs."""
import json, os, collections, random
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "r6_results.json")))
N = len(R)


def pclass(b):
    c = collections.Counter(l['perf'] or 'nonentity' for l in b['loci'])
    top = c.most_common(1)[0][0]
    return {'W': 'self-performed', 'O': 'occupant-performed'}.get(top, 'INPUT/scratch-performed')


def grp(b):
    return ('EMPTY' if b['empty'] else 'OCCUPIED') + '/' + b['native']


print("births", N, collections.Counter(grp(b) for b in R))
print("birth class (majority performer):", collections.Counter((pclass(b), grp(b)) for b in R))
allL = [l for b in R for l in b['loci']]
print("written loci", len(allL))
print("data-label kinds:", collections.Counter(l['kind'] for l in allL))
print("data-label kinds by group:")
for g in sorted({grp(b) for b in R}):
    print("  ", g, collections.Counter(l['kind'] for b in R if grp(b) == g for l in b['loci']))
print("not-identified reasons (lenient):", collections.Counter(w for l in allL for w in l['why']).most_common())
for mode in ('rid_len', 'rid_str'):
    ri = [l for l in allL if l[mode]]
    per_birth = [sum(l[mode] for l in b['loci']) / 64 for b in R]
    print("%s: rule-identified loci %d/%d (%.1f%%); births with >=90%% identified: %d/%d (%.1f%%)" % (
        mode, len(ri), len(allL), 100 * len(ri) / len(allL), sum(x >= 0.9 for x in per_birth), N, 100 * sum(x >= 0.9 for x in per_birth) / N))
ri = [l for l in allL if l['rid_len']]
fc = collections.Counter(l['flip'] for l in ri)
cov = (fc['CONFIRMED'] + fc['FAILED']) / max(1, len(ri))
print("flip (lenient-identified loci):", dict(fc), "coverage %.3f" % cov)
for g in sorted({grp(b) for b in R}):
    rr = [l for b in R if grp(b) == g for l in b['loci'] if l['rid_len']]
    c = collections.Counter(l['flip'] for l in rr)
    print("   ", g, dict(c), "coverage %.3f" % ((c['CONFIRMED'] + c['FAILED']) / max(1, len(rr))))
print("identified births (lenient) detail:")
for b in R:
    n = sum(l['rid_len'] for l in b['loci'])
    if n:
        print("   birth", b['bi'], grp(b), "identified", n, "flip", dict(collections.Counter(l['flip'] for l in b['loci'] if l['rid_len'])),
              "src==own index", sum(1 for l in b['loci'] if l['rid_len'] and l['src'][1] == l['j']))
# Q8c
q = [sum(l['q8c'] for l in b['loci']) / 64 for b in R]
est = sum(l['q8c'] for l in allL) / len(allL)
rng = random.Random(1)
bs = sorted(sum(q[rng.randrange(N)] for _ in range(N)) / N for _ in range(2000))
print("Q8c (all written loci): mean %.3f, birth-clustered bootstrap 95%% [%.3f, %.3f]" % (est, bs[50], bs[1949]))
print("  Q8c by data kind:", {k: round(sum(l['q8c'] for l in allL if l['kind'] == k) / max(1, sum(1 for l in allL if l['kind'] == k)), 3)
                               for k in sorted({l['kind'] for l in allL})})
print("  Q8c loci with zero arms (q8c_n==0):", sum(1 for l in allL if l['q8c_n'] == 0))
for g in sorted({grp(b) for b in R}):
    qq = [q[i] for i, b in enumerate(R) if grp(b) == g]
    print("   Q8c", g, "n=%d mean %.3f" % (len(qq), sum(qq) / len(qq)))
ent_loci = [l for l in allL if l['dent']]
print("  Q8c over ENTITY-data loci only: %.3f (n=%d)" % (sum(l['q8c'] for l in ent_loci) / max(1, len(ent_loci)), len(ent_loci)))
print("Q8c-whether (birth suppression rate by arm):", {e: round(sum(b['q8c_whether'].get(e, 0) for b in R if e in b['q8c_whether']) /
      max(1, sum(1 for b in R if e in b['q8c_whether'])), 3) for e in ('W', 'O')})
print("Q4 capable children (>=50% of 320):", sum(b['cap'] >= 0.5 for b in R), "; any success:", sum(b['cap'] > 0 for b in R),
      "; max rate", max(b['cap'] for b in R))
print("budget-ended interactions:", sum(b['budget_end'] for b in R), "halted:", sum(b['halted'] for b in R))
print("whole-interaction ctrl contains INPUT:", sum(b['ctrl_end_input'] for b in R), "; exec contains O:", sum(b['exec_end_has_O'] for b in R),
      "; exec contains INPUT:", sum(b['exec_end_input'] for b in R))
# Q-homology / P1 over identified ENTITY loci; also over all ENTITY-data loci
for nm, sel in (('identified', lambda l: l['rid_len']), ('entity-data', lambda l: l['dent'])):
    s = [l for l in allL if sel(l)]
    print("Q-homology (%s): n=%d, source index == own index: %d" % (nm, len(s), sum(1 for l in s if l['src'][1] == l['j'])))
# Q2 / P2 on native 'target' births: copy-descent majority donor over all written loci
def majority(b, sel):
    c = collections.Counter(l['dent'] for l in b['loci'] if sel(l) and l['dent'])
    if not c: return 'NONE'
    mc = c.most_common()
    return 'TIED' if len(mc) > 1 and mc[0][1] == mc[1][1] else {'W': 'writer', 'O': 'target'}[mc[0][0]]
for nm, sel in (('all written', lambda l: True), ('identified', lambda l: l['rid_len'])):
    t = [b for b in R if b['native'] == 'target']
    dis = sum(1 for b in t if majority(b, sel) != 'target')
    print("P2 (%s): native 'target' births %d, copy-descent majority != target: %d; majority donors %s" % (
        nm, len(t), dis, dict(collections.Counter(majority(b, sel) for b in t))))
    print("   all births majority donor vs native:", dict(collections.Counter((b['native'], majority(b, sel)) for b in R)))
