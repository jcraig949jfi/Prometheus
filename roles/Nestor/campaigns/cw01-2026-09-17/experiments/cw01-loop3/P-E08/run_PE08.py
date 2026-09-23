"""P-E08 (T-E03 stasis escape, anti-gravity): a ZEROING mutation makes the L0 burden coordinate attainable?

Phase 1, ATTAINABILITY (mandatory before any pressure is frozen): 30 generations of selection-free
drift, 4 attempt ids, with the zeroing operator (each weight set to exactly 0 with probability .05
per birth, after the clipped Gaussian) and with the plain operator; the non-zero share must move by
>= .10 under zeroing or the candidate closes INSTRUMENT_UNATTAINABLE. Phase 2 (only if attainable):
e03 treatment with sel = score - lambda * nz_share, lambda in {0, H}, 4 ids each, MI excess /
sparsity / precision / coverage as in P-B07.
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
PID, TID = "P-E08", "T-E03"
G, N, THR, PZ, G_DRIFT = 60, 64, 0.05, 0.05, 30


def nz_share(g):
    return float((np.abs(g["w"]) > THR).mean())


def mutate_z(g, cfg, rng, sigma, zero):
    h = W3.mutate(g, cfg, rng, sigma)
    mask = rng.random(h["w"].shape) < PZ            # drawn in BOTH operators
    if zero:
        h["w"] = np.where(mask, 0.0, h["w"])
    return h


def drift(cfg, mk, zero):
    aid = cfg["attempt_id"]
    rng = np.random.Generator(np.random.PCG64(mk(aid, "drift|zero%d" % int(zero), 0)))
    pop = [W3.seed_genome(cfg, rng) for _ in range(N)]
    sigma = cfg["population"]["mutation_sigma"]
    start = float(np.mean([nz_share(p) for p in pop]))
    for gen in range(G_DRIFT):
        pop = [mutate_z(pop[int(rng.integers(0, N))], cfg, rng, sigma, zero) for _ in range(N)]
    return start, float(np.mean([nz_share(p) for p in pop]))


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
        pop = [mutate_z(elite[i % len(elite)], cfg, rng, sigma, True) for i in range(N)]
    return pop, res


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "escapes_stasis": "a mutation operator that can zero a weight (T-E03's recorded escape)", "claim_type": "stasis-escape",
                         "phase1": {"drift_generations": G_DRIFT, "ids": 4, "operators": ["zeroing p=%.2f" % PZ, "plain (same draws)"], "attainable_if": "mean(start - end) of nz_share under zeroing >= .10"},
                         "phase2": {"lambdas": ["0", "H"], "ids": 4, "generations": G, "n": N, "measures": ["nz_share", "sparsity", "mi_excess", "precision", "coverage", "score"]},
                         "unchanged": "e03 world, organism, elitism, MI ruler (P-B07's harness)",
                         "material_rule": "phase 2 only: nz_share(H) - nz_share(0) below p05 AND (mi_excess or precision differs outside its band) -> burden pressure changes conditionality; nz below only -> behavioural sparsity only; phase 1 failure -> INSTRUMENT_UNATTAINABLE (not material, instrument fact)",
                         "continuation": ["zeroing probability dose", "magnitude-based burden", "tax x activation cost"]})
    phase1 = []
    for i in range(4):
        cfg = L.load_cfg("cw01-e03", "cw01-loop3-PE08-d%d" % i)
        s0, e0 = drift(cfg, S.seed, False)
        s1, e1 = drift(cfg, S.seed, True)
        phase1.append({"id": i, "plain": {"start": s0, "end": e0}, "zeroing": {"start": s1, "end": e1}})
        print("   drift id %d plain %.3f->%.3f zeroing %.3f->%.3f" % (i, s0, e0, s1, e1), flush=True)
    drop = float(np.mean([p["zeroing"]["start"] - p["zeroing"]["end"] for p in phase1]))
    drop_plain = float(np.mean([p["plain"]["start"] - p["plain"]["end"] for p in phase1]))
    attainable = drop >= 0.10
    out = {"perturbation_id": PID, "parent": TID, "phase1": phase1, "nz_drop_zeroing": drop, "nz_drop_plain": drop_plain, "attainable": attainable}
    if not attainable:
        out.update({"disposition": "INSTRUMENT_UNATTAINABLE", "material": False, "elapsed_s": round(time.time() - t0, 1)})
        L.result(HERE, out, ph)
        L.append_evidence(TID, PID, "zeroing operator: nz_share drop under drift %.3f (plain %.3f) - coordinate still unattainable; INSTRUMENT_UNATTAINABLE" % (drop, drop_plain), False, detail=out["phase1"])
        print("DONE INSTRUMENT_UNATTAINABLE drop %.3f" % drop)
        return
    cfg0 = L.load_cfg("cw01-e03", "cw01-loop3-PE08-H")
    st0, ce0 = W3.attempt_structure(cfg0, S.seed), W3.attempt_centres(cfg0, S.seed)
    tr = W3.evolve(cfg0, "treatment", G, N, S.seed, structure=st0, centres=ce0)["history"][-1]["mean"]
    ct = W3.evolve(cfg0, "control_no_conditionality", G, N, S.seed, structure=st0, centres=ce0)["history"][-1]["mean"]
    H = max(tr - ct, 1e-6)
    rows = []
    for name, lam in (("0", 0.0), ("H", H)):
        for i in range(4):
            cfg = L.load_cfg("cw01-e03", "cw01-loop3-PE08-%d" % i)
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
            print("   lambda %-2s id %d score %.3f sparsity %.3f nz %.3f MI %.3f sig %s prec %.3f" % (name, i, rec["score"], rec["sparsity"], rec["nz_share"], rec["mi_excess"], rec["mi_significant"], rec["precision"]), flush=True)
    summ = {n: {k: float(np.mean([r[k] for r in rows if r["lambda"] == n])) for k in ("score", "sparsity", "nz_share", "mi_excess", "precision", "coverage")} for n in ("0", "H")}
    c = {k: L.relabel_diff([r[k] for r in rows if r["lambda"] == "0"], [r[k] for r in rows if r["lambda"] == "H"]) for k in ("nz_share", "mi_excess", "precision", "sparsity", "score")}
    cond = c["mi_excess"]["below_p05"] or c["mi_excess"]["above_p95"] or c["precision"]["below_p05"] or c["precision"]["above_p95"]
    reading = ("BURDEN_CHANGES_CONDITIONALITY" if (c["nz_share"]["below_p05"] and cond) else "SPARSITY_ONLY" if c["nz_share"]["below_p05"] else "TAX_INERT")
    material = bool(c["nz_share"]["below_p05"] and cond)
    out.update({"H": H, "summary": summ, "contrasts": c, "reading": reading, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)})
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "zeroing operator attainable (drift drop %.3f); tax at H: %s; contrasts %s; reading %s" % (drop, {n: {k: round(v, 3) for k, v in s.items()} for n, s in summ.items()}, {k: (round(v["effect"], 3), v["below_p05"], v["above_p95"]) for k, v in c.items()}, reading), material, detail=summ,
                      state="ACTIVE" if c["nz_share"]["below_p05"] else None, state_reason="the burden coordinate moves under the zeroing operator; T-E03's stasis scope is escaped" if c["nz_share"]["below_p05"] else None)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, reading, time.time() - t0, summ))


if __name__ == "__main__":
    main()
