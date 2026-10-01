"""Check eval_full == assays.evaluate (acc, sens_act, sens_any) and time it."""
from r_common import *
ck = Clock()
E = [r for r in rows() if r["kind"] == "evolve"]
out = []
for r in [E[0], E[100], E[400]]:
    ph, env = spec_of(r); g = genome_of(r)
    s = seeds(H_int(NS, 0xBE), 8)
    t0 = time.process_time()
    a = eval_full(ph, g, env, s)
    t1 = time.process_time()
    b = assays.evaluate(ph, g[None], env, s, device="cpu", graph=False)
    t2 = time.process_time()
    out.append({"cell": r["cell_id"], "T": env.T(), "N": ph.n_sites,
                "acc_eq": bool(np.allclose(a["acc"], b.acc[0])), "sa": [a["sens_act"], float(b.sens_act[0])],
                "sy": [a["sens_any"], float(b.sens_any[0])], "cpu_full": round(t1 - t0, 2), "cpu_assay": round(t2 - t1, 2)})
    print(out[-1], flush=True)
print(ck.done())
