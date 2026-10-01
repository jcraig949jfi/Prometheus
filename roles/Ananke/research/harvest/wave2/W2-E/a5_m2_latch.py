"""A5: M2 (4ab2ba01) physics. (i) Do the 4-line latch (W-H H2) and hold_latch
score ~1.0 there? (ii) Random-genome census at M2 physics: how often is a
random 16-line program above .55, and is it comm-using (echo-like) or local?
(iii) 1-mutant robustness of M2 champion vs the H2 latch vs W-L integrator."""
from w2e_common import *
ck = Clock()
r = row("4ab2ba01", "evolve"); ph, env = spec_of(r); g_m2 = genome_of(r)
H2 = [("MULQ", "T0", "SENSE", "SENSE", 0), ("ADDI", "T0", "T0", 0, -100), ("SEL", "T0", "SENSE", "S0", 0),
      ("MOV", "S0", "T0", 0, 0)]
b = plants.assemble(ph, H2); g_h2 = np.broadcast_to(b, (ph.rules, *b.shape)).copy()
g_hl = plants.plant("hold_latch", ph)
wl = json.load(open(ROOT / "roles/Ananke/research/workers/W-L/out/search_n0_s0.json"))
g_wl = np.asarray(wl["evolve"]["champion"])
S = seeds(H_int(NS, 0xA5), 64)
out = {"latches": {}}
for name, gg in [("H2_4line", g_h2), ("hold_latch_9line", g_hl), ("M2", g_m2), ("WL_integrator", g_wl)]:
    acc, *_ = run(ph, gg, env, S); out["latches"][name] = ci(pairs(acc))
print(out, flush=True)

def batch_eval(G, SS, ctrl=None):
    return assays.evaluate(ph, G, env, SS, ctrl=ctrl, device="cpu", graph=False).mean()

# (ii) random census
from prometheus.ananke.search import random_genomes
rg = np.random.default_rng(0xA5)
S8 = seeds(H_int(NS, 0xA5C), 8)
accs, zcs = [], []
for chunk in range(8):
    G = random_genomes(rg, 128, ph)
    a = batch_eval(G, S8); accs.append(a)
    idx = np.flatnonzero(a > 0.55)
    z = np.full(len(a), np.nan)
    if len(idx):
        z[idx] = batch_eval(G[idx], S8, Controls(zero_comm=True))
    zcs.append(z)
accs = np.concatenate(accs); zcs = np.concatenate(zcs)
hit = accs > 0.55
out["census"] = {"n": int(len(accs)), "n_above_.55": int(hit.sum()), "n_above_.65": int((accs > .65).sum()),
                 "comm_using_above_.55": int((hit & (zcs < accs - 0.05)).sum()),
                 "local_above_.55": int((hit & (zcs >= accs - 0.05)).sum()),
                 "max": float(accs.max())}
print(out["census"], flush=True)

# (iii) 1-mutant robustness: every single-field resample (one draw per field) of the active body
def mutants(g0, n=192, seed=1):
    rg = np.random.default_rng(seed)
    G = np.repeat(g0[None], n, 0).copy()
    for i in range(n):
        L = g0.shape[1]
        li, fi = rg.integers(L), rg.integers(5)
        G[i, :, li, fi] = rg.integers(-128, 128) if fi == 4 else rg.integers(0, 256)
    return G
S16 = seeds(H_int(NS, 0xA5D), 16)
rob = {}
for name, gg in [("H2_4line", g_h2), ("M2", g_m2), ("WL_integrator", g_wl)]:
    base = float(batch_eval(gg[None], S16)[0])
    a = batch_eval(mutants(gg), S16)
    rob[name] = {"base": base, "frac_within_.05": float((a >= base - .05).mean()),
                 "frac_above_.6": float((a > .6).mean()), "mean": float(a.mean())}
out["robustness_1mut"] = rob
out["clock"] = ck.done(); save("a5_m2_latch.json", out); print(json.dumps(out, indent=1))
