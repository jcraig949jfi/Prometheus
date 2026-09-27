"""Post-hoc diagnosis of the failed POS control (amendment A1): true single-edit improvement
rate from the 1-clobber genotype (12-op uniform, as probes), and the rate at which a neutral
frozen-weight step from the 2-clobber planted parent removes a clobber."""
import json, os, sys, collections as C
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4lib as L
eps = L.episodes(); exp = L.expected_vector(eps)
def sc(m): return L.score(L.answers(m, eps), exp)
out = {}
one = L.manifest_of(L.summit_genome(1)); two = L.manifest_of(L.summit_genome(2))
# (a) probes from the 1-clobber genotype
imp = app = 0; byop = C.Counter()
for op in L.OPS:
    for j in range(250):
        c, _ = L.one_edit(one, L.SplitMix64(L.seed_from("r4a001.diag", "one", op, j)), name=op)
        if c is None: continue
        app += 1
        if sc(c) > 0.53125 + L.BAND: imp += 1; byop[op] += 1
out["one_clobber_probe"] = {"applied": app, "improved": imp, "rate": imp / app, "by_op": dict(byop)}
# (b) neutral frozen-weight steps from 2-clobber: share that yield a 1-clobber-equivalent (i.e. a genotype with a one-edit fix)
rng = L.SplitMix64(L.seed_from("r4a001.diag", "two"))
neutral = removed = 0
for _ in range(3000):
    c, _r = L.one_edit(two, rng)
    if c is None: continue
    if abs(sc(c) - 0.53125) > L.BAND: continue
    neutral += 1
    # clobber removed iff restoring... test: does deleting the remaining clobber instruction exist? cheap proxy:
    # count LDC r9<-0 instructions that execute: count 'LDC 9 0' words patterns in genome
    g = c["genome"]; n = sum(1 for i in range(0, len(g), 4) if g[i] % 25 == 3 and g[i+1] % c["n_regs"] == 9 and g[i+2] == 0)
    if n < 2: removed += 1
out["two_clobber_neutral_steps"] = {"neutral": neutral, "clobber_pattern_lost": removed, "rate": removed / max(1, neutral)}
json.dump(out, open(os.path.join(L.HERE, "diag_pos.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
