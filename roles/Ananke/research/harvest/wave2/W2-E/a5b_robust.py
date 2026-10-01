"""A5b: 1-mutant robustness at M2 physics (small: 48 mutants x 8 worlds each)."""
from w2e_common import *
ck = Clock()
r = row("4ab2ba01", "evolve"); ph, env = spec_of(r); g_m2 = genome_of(r)
H2 = [("MULQ", "T0", "SENSE", "SENSE", 0), ("ADDI", "T0", "T0", 0, -100), ("SEL", "T0", "SENSE", "S0", 0),
      ("MOV", "S0", "T0", 0, 0)]
b = plants.assemble(ph, H2); g_h2 = np.broadcast_to(b, (ph.rules, *b.shape)).copy()
wl = json.load(open(ROOT / "roles/Ananke/research/workers/W-L/out/search_n0_s0.json"))
g_wl = np.asarray(wl["evolve"]["champion"])
def active_mutants(g0, n, seed):
    rg = np.random.default_rng(seed)
    act = [i for i in range(g0.shape[1]) if g0[0, i, 0] % 16 != 0]
    G = np.repeat(g0[None], n, 0).copy()
    for k in range(n):
        li, fi = act[rg.integers(len(act))], rg.integers(5)
        G[k, :, li, fi] = rg.integers(-128, 128) if fi == 4 else rg.integers(0, 256)
    return G
S8 = seeds(H_int(NS, 0xA5D), 8)
out = {}
for name, gg in [("H2_4line", g_h2), ("M2", g_m2), ("WL_integrator", g_wl)]:
    t = time.time()
    G = np.concatenate([gg[None], active_mutants(gg, 47, 1)])
    a = assays.evaluate(ph, G, env, S8, device="cpu", graph=False).mean()
    base = float(a[0]); m = a[1:]
    out[name] = {"base": base, "n_active_lines": int(sum(gg[0, i, 0] % 16 != 0 for i in range(gg.shape[1]))),
                 "frac_mut_within_.05": float((m >= base - .05).mean()), "frac_mut_above_.6": float((m > .6).mean()),
                 "frac_mut_at_chance_.5": float((np.abs(m - .5) < .02).mean()), "wall": round(time.time() - t, 1)}
    print(name, out[name], flush=True)
out["clock"] = ck.done(); save("a5b_robust.json", out)
