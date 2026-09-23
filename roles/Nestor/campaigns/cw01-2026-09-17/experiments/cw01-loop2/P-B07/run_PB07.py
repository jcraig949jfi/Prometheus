"""P-B07 (serendipity): e08's representational tax laid over e03's activation policy.

Parent T-E03 (x T-E08). Selection fitness sel = score - lambda * (share of weights with |w| > 0.05)
with lambda in {0, H/4, H/2, H}, H = the measured headroom of e03 (treatment final mean minus
non-conditional control final mean, computed in this run at lambda 0 on a disjoint attempt id);
4 attempt ids per lambda; a Nestor copy of e03's evolve loop with the tax in selection only.
Measures at the end: MI excess (mi_with_null) of latent class vs activation pattern, sparsity,
non-zero-weight share, recorded score. Does representational burden pressure change coalition
conditionality or only behavioural sparsity?
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import infometrics as IM       # noqa: E402

W3 = L.import_world("cw01-e03", "world_e03")
PID, TID = "P-B07", "T-E03"
G, N, THR = 60, 64, 0.05


def nz_share(g):
    return float((np.abs(g["w"]) > THR).mean())


def evolve_taxed(cfg, lam, mk, structure, centres):
    aid = cfg["attempt_id"]
    rng = np.random.Generator(np.random.PCG64(mk(aid, "evo|treatment", 0)))
    pop = [W3.seed_genome(cfg, rng) for _ in range(N)]
    elite_n = max(2, int(N * cfg["population"]["elite_fraction"]))
    sigma = cfg["population"]["mutation_sigma"]
    for gen in range(G):
        res = [W3.run_episode(p, cfg, "treatment", mk(aid, "stream|g%d" % gen, i), structure=structure, centres=centres) for i, p in enumerate(pop)]
        sc = np.array([r["score"] for r in res])
        sel = sc - lam * np.array([nz_share(p) for p in pop])
        if gen == G - 1:
            break
        elite = [pop[i] for i in np.argsort(-sel)[:elite_n]]
        pop = [W3.mutate(elite[i % len(elite)], cfg, rng, sigma) for i in range(N)]
    return pop, res


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "serendipity-descriptive",
                         "delta": "sel = score - lambda * nonzero-weight share; lambda in {0, H/4, H/2, H} with H measured at lambda 0 on a disjoint id",
                         "unchanged": "e03 world, organism, mutation, elitism, 60 generations, MI ruler", "attacks": "burden vs behavioural sparsity vs conditionality",
                         "continuation": ["tax on bias magnitude", "tax x activation cost", "held-out structure transfer (I4)"]})
    # headroom on a disjoint id
    cfg0 = L.load_cfg("cw01-e03", "cw01-loop2-PB07-H")
    st0, ce0 = W3.attempt_structure(cfg0, S.seed), W3.attempt_centres(cfg0, S.seed)
    tr = W3.evolve(cfg0, "treatment", G, N, S.seed, structure=st0, centres=ce0)["history"][-1]["mean"]
    ct = W3.evolve(cfg0, "control_no_conditionality", G, N, S.seed, structure=st0, centres=ce0)["history"][-1]["mean"]
    H = max(tr - ct, 1e-6)
    lams = {"0": 0.0, "H/4": H / 4, "H/2": H / 2, "H": H}
    print("   headroom H = %.4f (treatment %.4f, control %.4f)" % (H, tr, ct), flush=True)
    rows = []
    for name, lam in lams.items():
        for i in range(4):
            cfg = L.load_cfg("cw01-e03", "cw01-loop2-PB07-%d" % i)
            st, ce = W3.attempt_structure(cfg, S.seed), W3.attempt_centres(cfg, S.seed)
            pop, res = evolve_taxed(cfg, lam, S.seed, st, ce)
            cls, pat = [], []
            for j in range(16):
                r = W3.run_episode(pop[j % len(pop)], cfg, "treatment", S.seed(cfg["attempt_id"], "stream|iv", j), structure=st, centres=ce, collect_patterns=True)
                cls += r["_classes"]
                pat += r["_patterns"]
            mi = IM.mi_with_null(cls, pat, n_shuffles=200, seed=17)
            rec = {"lambda": name, "aid": i, "score": float(np.mean([r["score"] for r in res])), "sparsity": float(np.mean([r["sparsity"] for r in res])),
                   "nz_share": float(np.mean([nz_share(p) for p in pop])), "mi_excess": mi["excess_bits"], "mi_significant": mi["significant"],
                   "precision": float(np.mean([r["routing_precision"] for r in res])), "coverage": float(np.mean([r["coverage_mean"] for r in res]))}
            rows.append(rec)
            print("   lambda %-4s id %d score %.3f sparsity %.3f nz %.3f MI excess %.3f sig %s" % (name, i, rec["score"], rec["sparsity"], rec["nz_share"], rec["mi_excess"], rec["mi_significant"]), flush=True)
    summ = {n: {k: float(np.mean([r[k] for r in rows if r["lambda"] == n])) for k in ("score", "sparsity", "nz_share", "mi_excess", "precision", "coverage")} for n in lams}
    for n in lams:
        summ[n]["mi_significant"] = sum(1 for r in rows if r["lambda"] == n and r["mi_significant"])
    c_nz = L.relabel_diff([r["nz_share"] for r in rows if r["lambda"] == "0"], [r["nz_share"] for r in rows if r["lambda"] == "H"])
    c_mi = L.relabel_diff([r["mi_excess"] for r in rows if r["lambda"] == "0"], [r["mi_excess"] for r in rows if r["lambda"] == "H"])
    material = bool(c_nz["below_p05"] and not c_mi["below_p05"]) or bool(c_mi["below_p05"])
    out = {"perturbation_id": PID, "parent": TID, "H": H, "summary": summ, "nz_H_minus_0": c_nz, "mi_H_minus_0": c_mi, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "representational tax on e03: %s" % {n: (round(v["nz_share"], 3), round(v["sparsity"], 3), round(v["mi_excess"], 3), v["mi_significant"]) for n, v in summ.items()}, material, detail=summ)
    print("DONE material=%s (%.0f s)" % (material, time.time() - t0))


if __name__ == "__main__":
    main()
