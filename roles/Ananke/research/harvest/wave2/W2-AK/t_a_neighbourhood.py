"""Test (a): mutational neighbourhood of the cell's plant (W2-D t_a_neighbourhood.py adapted).
k-field mutants (positions drawn over the WHOLE genome G x L x 5, each field resampled from search._rand_instr,
the GA's own draw), plus search.mutate() offspring with the cell's SearchSpec. Common worlds (CRN) for all
genomes, namespace 0x57324B41 'W2KA'. usage: python t_a_neighbourhood.py 8743|f29c NW"""
from ak_common import *
p = sys.argv[1]; NWLD = int(sys.argv[2]) if len(sys.argv) > 2 else 8
r, ph, env, sp = cell(p)
ck = Clock()
pl = plant(p, ph)
G, L, F = pl.shape
NW, NR = ph.n_write(), ph.n_read()
def reduced(x):
    return np.stack([x[..., 0] % 16, x[..., 1] % NW, x[..., 2] % NR, x[..., 3] % NR, x[..., 3] & 15, x[..., 4]], -1)
def nchg(c):
    return int((reduced(c) != reduced(pl)).any(-1).sum())
g = np.random.default_rng(0x57324B41)
plan = [(1, 96), (2, 48), (4, 48), (8, 24)] if len(sys.argv) < 4 else [(1, 64), (2, 32), (4, 32), (8, 16)]
NMUT = 64 if len(sys.argv) < 4 else 48
genomes, meta = [pl.copy(), pl.copy()], [{"kind": "plant"}, {"kind": "plant_dup"}]
champ = np.asarray(r["result"]["champion"]); genomes.append(champ); meta.append({"kind": "champion"})
for k, n in plan:
    for _ in range(n):
        c = pl.copy()
        pos = g.choice(G * L * F, size=k, replace=False)
        fresh = search._rand_instr(g, (G, L))
        for q in pos:
            gi, rem = divmod(int(q), L * F); li, fi = divmod(rem, F)
            c[gi, li, fi] = fresh[gi, li, fi]
        genomes.append(c); meta.append({"kind": f"k{k}", "k": k, "pos": [int(q) for q in pos], "lines_changed": nchg(c)})
for _ in range(NMUT):
    c = search.mutate(g, pl, sp)
    genomes.append(c); meta.append({"kind": "mutate_op", "lines_changed": nchg(c)})
pop = np.stack(genomes)
seeds = assays.world_seeds(0x57324B41, NWLD)
accs = []
for i in range(0, len(pop), 96):
    accs.append(ev(ph, pop[i:i+96], env, seeds).mean()); print("chunk", i, ck.done(), flush=True)
acc = np.concatenate(accs)
for m, a in zip(meta, acc):
    m["acc"] = float(a)
pa = float(acc[0]); assert abs(acc[0] - acc[1]) < 1e-12, "batch-position dependence"
summ = {"plant_acc": pa, "champion_acc_same_worlds": float(acc[2])}
for kind in [f"k{k}" for k, _ in plan] + ["mutate_op"]:
    a = np.array([m["acc"] for m in meta if m["kind"] == kind])
    eff = np.array([m["lines_changed"] > 0 for m in meta if m["kind"] == kind])
    ae = a[eff]
    summ[kind] = {"n": int(a.size), "n_effective": int(eff.sum()), "mean": float(a.mean()),
                  "frac_ge_plant-.05": float((a >= pa - .05).mean()), "frac_.60_to_plant-.05": float(((a >= .60) & (a < pa - .05)).mean()),
                  "frac_lt_.60": float((a < .60).mean()), "frac_ge_.55": float((a >= .55).mean()),
                  "eff_frac_ge_plant-.05": float((ae >= pa - .05).mean()) if ae.size else None,
                  "eff_frac_lt_.60": float((ae < .60).mean()) if ae.size else None,
                  "quantiles": np.quantile(a, [0, .1, .25, .5, .75, .9, 1]).round(3).tolist()}
    print(kind, summ[kind], flush=True)
line = {}
for m in meta:
    if m["kind"] == "k1" and m["lines_changed"] > 0:
        gi, rem = divmod(m["pos"][0], L * F); li, fi = divmod(rem, F)
        line.setdefault(li, []).append(m["acc"])
summ["k1_eff_per_line_mean"] = {int(k): [round(float(np.mean(v)), 3), len(v)] for k, v in sorted(line.items())}
print(summ["k1_eff_per_line_mean"])
out = {"cell": r["cell_id"], "seeds_ns": "0x57324B41", "M": NWLD, "G": G, "L": L, "summary": summ, "meta": meta, "compute": ck.done()}
print(out["compute"]); save(f"t_a_neighbourhood_{p}.json", out)
