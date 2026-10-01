"""Test (a): mutational neighbourhood of the P-FLIP plant at C1 cell 6f82f9c7 (d9cc).
k-field mutants (each chosen field resampled from the GA's own draw distribution, search._rand_instr),
plus offspring of search.mutate() with the cell's own SearchSpec. 4 fresh worlds (2 mirror pairs) each,
common to all genomes (CRN). Namespace 0x57324441 'W2DA'."""
from w2d_common import *
r, ph, env, sp = flip_cell()
ck = Clock()
plant = hp_plants.p_flip(ph)   # [1, 16, 5]
G, L, F = plant.shape
NW, NR = ph.n_write(), ph.n_read()
def reduced(x):
    return np.stack([x[..., 0] % 16, x[..., 1] % NW, x[..., 2] % NR, x[..., 3] % NR, x[..., 3] & 15, x[..., 4]], -1)
g = np.random.default_rng(0x57324441)
plan = [(1, 128), (2, 64), (4, 48), (8, 48), (16, 32), (32, 32)]
genomes, meta = [plant.copy()], [{"kind": "plant"}]
for k, n in plan:
    for _ in range(n):
        c = plant.copy()
        pos = g.choice(L * F, size=k, replace=False)
        fresh = search._rand_instr(g, (G, L))
        for p in pos:
            li, fi = divmod(int(p), F)
            c[0, li, fi] = fresh[0, li, fi]
        nchg = int((reduced(c) != reduced(plant)).any(-1).sum())
        genomes.append(c); meta.append({"kind": f"k{k}", "k": k, "pos": [int(p) for p in pos], "lines_changed": nchg})
for _ in range(64):
    c = search.mutate(g, plant, sp)
    nchg = int((reduced(c) != reduced(plant)).any(-1).sum())
    genomes.append(c); meta.append({"kind": "mutate_op", "lines_changed": nchg})
pop = np.stack(genomes)
seeds = assays.world_seeds(0x57324441, 4)
accs = []
for i in range(0, len(pop), 200):
    res = assays.evaluate(ph, pop[i:i+200], env, seeds, device="cpu")
    accs.append(res.mean())
acc = np.concatenate(accs)
for m, a in zip(meta, acc):
    m["acc"] = float(a)
summ = {}
for kind in ["plant"] + [f"k{k}" for k, _ in plan] + ["mutate_op"]:
    a = np.array([m["acc"] for m in meta if m["kind"] == kind])
    eff = np.array([m.get("lines_changed", 0) > 0 for m in meta if m["kind"] == kind])
    ae = a[eff] if eff.any() else a
    summ[kind] = {"n": int(a.size), "n_effective": int(eff.sum()), "mean": float(a.mean()),
                  "frac_ge_.90": float((a >= .90).mean()), "frac_.60_.90": float(((a >= .60) & (a < .90)).mean()),
                  "frac_lt_.60": float((a < .60).mean()),
                  "eff_frac_ge_.90": float((ae >= .90).mean()), "eff_frac_.60_.90": float(((ae >= .60) & (ae < .90)).mean()),
                  "quantiles": np.quantile(a, [0, .1, .25, .5, .75, .9, 1]).round(3).tolist()}
    print(kind, summ[kind])
# per-line sensitivity from k1 (effective only)
line = {}
for m in meta:
    if m["kind"] == "k1" and m["lines_changed"] > 0:
        li, fi = divmod(m["pos"][0], F)
        line.setdefault(li, []).append(m["acc"])
summ["k1_per_line_mean"] = {int(k): [round(float(np.mean(v)), 3), len(v)] for k, v in sorted(line.items())}
print(summ["k1_per_line_mean"])
out = {"cell": FLIP_CELL, "seeds_ns": "0x57324441", "M": 4, "summary": summ, "meta": meta, "compute": ck.done()}
print(out["compute"])
save("t_a_neighbourhood.json", out)
