"""P-F08 (T-E03 stasis escape, anti-gravity): a heritable MASK GENE (effective weight = w * mask; mask
bits flip with probability .02 per birth) makes the L0 burden coordinate attainable? Attainability
check first (30 drift generations, 4 ids; effective non-zero share must move by >= .10), then the
tax at lambda {0, H} as P-B07 / P-E08.
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
PID, TID = "P-F08", "T-E03"
G, N, THR, PFLIP, G_DRIFT = 60, 64, 0.05, 0.02, 30


def seed(cfg, rng):
    g = W3.seed_genome(cfg, rng)
    g["mask"] = np.ones(g["w"].shape)
    return g


def effective(g):
    return {"bias": g["bias"], "w": g["w"] * g["mask"], "neutral_a": g["neutral_a"], "neutral_b": g["neutral_b"]}


def nz_share(g):
    return float((np.abs(g["w"] * g["mask"]) > THR).mean())


def mutate(g, cfg, rng, sigma):
    h = W3.mutate(g, cfg, rng, sigma)
    flip = rng.random(g["mask"].shape) < PFLIP
    h["mask"] = np.where(flip, 1.0 - g["mask"], g["mask"])
    return h


def drift(cfg, mk):
    aid = cfg["attempt_id"]
    rng = np.random.Generator(np.random.PCG64(mk(aid, "drift|mask", 0)))
    pop = [seed(cfg, rng) for _ in range(N)]
    sigma = cfg["population"]["mutation_sigma"]
    start = float(np.mean([nz_share(p) for p in pop]))
    for gen in range(G_DRIFT):
        pop = [mutate(pop[int(rng.integers(0, N))], cfg, rng, sigma) for _ in range(N)]
    return start, float(np.mean([nz_share(p) for p in pop]))


def evolve_taxed(cfg, lam, mk, structure, centres):
    aid = cfg["attempt_id"]
    rng = np.random.Generator(np.random.PCG64(mk(aid, "evo|treatment", 0)))
    pop = [seed(cfg, rng) for _ in range(N)]
    elite_n = max(2, int(N * cfg["population"]["elite_fraction"]))
    sigma = cfg["population"]["mutation_sigma"]
    for gen in range(G):
        res = [W3.run_episode(effective(p), cfg, "treatment", mk(aid, "stream|g%d" % gen, i), structure=structure, centres=centres) for i, p in enumerate(pop)]
        sc = np.array([r["score"] for r in res])
        sel = sc - lam * np.array([nz_share(p) for p in pop])
        if gen == G - 1:
            break
        elite = [pop[i] for i in np.argsort(-sel)[:elite_n]]
        pop = [mutate(elite[i % len(elite)], cfg, rng, sigma) for i in range(N)]
    return pop, res


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "escapes_stasis": "a heritable binary mask gene: zeros persist across births (T-E03's refined escape)", "claim_type": "stasis-escape",
                         "phase1": {"drift_generations": G_DRIFT, "ids": 4, "flip_p": PFLIP, "attainable_if": "mean(start - end) of effective nz_share >= .10"},
                         "phase2": {"lambdas": ["0", "H"], "ids": 4, "generations": G, "n": N}, "unchanged": "e03 world, organism otherwise, elitism, MI ruler",
                         "material_rule": "phase 2: nz_share(H) - nz_share(0) below p05 AND (mi_excess or precision outside its band) -> BURDEN_CHANGES_CONDITIONALITY; nz below only -> SPARSITY_ONLY; phase 1 failure -> INSTRUMENT_UNATTAINABLE",
                         "continuation": ["flip dose", "magnitude burden"]})
    phase1 = []
    for i in range(4):
        cfg = L.load_cfg("cw01-e03", "cw01-loop4-PF08-d%d" % i)
        s, e = drift(cfg, S.seed)
        phase1.append({"id": i, "start": s, "end": e})
        print("   drift id %d mask %.3f -> %.3f" % (i, s, e), flush=True)
    drop = float(np.mean([p["start"] - p["end"] for p in phase1]))
    attainable = drop >= 0.10
    out = {"perturbation_id": PID, "parent": TID, "phase1": phase1, "nz_drop": drop, "attainable": attainable}
    if not attainable:
        out.update({"disposition": "INSTRUMENT_UNATTAINABLE", "material": False, "elapsed_s": round(time.time() - t0, 1)})
        L.result(HERE, out, ph)
        L.append_evidence(TID, PID, "mask gene: nz_share drop under drift %.3f < .10; INSTRUMENT_UNATTAINABLE" % drop, False, detail=phase1)
        print("DONE INSTRUMENT_UNATTAINABLE drop %.3f" % drop)
        return
    cfg0 = L.load_cfg("cw01-e03", "cw01-loop4-PF08-H")
    st0, ce0 = W3.attempt_structure(cfg0, S.seed), W3.attempt_centres(cfg0, S.seed)
    tr = W3.evolve(cfg0, "treatment", G, N, S.seed, structure=st0, centres=ce0)["history"][-1]["mean"]
    ct = W3.evolve(cfg0, "control_no_conditionality", G, N, S.seed, structure=st0, centres=ce0)["history"][-1]["mean"]
    H = max(tr - ct, 1e-6)
    rows = []
    for name, lam in (("0", 0.0), ("H", H)):
        for i in range(4):
            cfg = L.load_cfg("cw01-e03", "cw01-loop4-PF08-%d" % i)
            st, ce = W3.attempt_structure(cfg, S.seed), W3.attempt_centres(cfg, S.seed)
            pop, res = evolve_taxed(cfg, lam, S.seed, st, ce)
            cls, pat = [], []
            for j in range(16):
                r = W3.run_episode(effective(pop[j % len(pop)]), cfg, "treatment", S.seed(cfg["attempt_id"], "stream|iv", j), structure=st, centres=ce, collect_patterns=True)
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
    L.append_evidence(TID, PID, "mask gene attainable (drift drop %.3f); tax at H: %s; contrasts %s; reading %s" % (drop, {n: {k: round(v, 3) for k, v in s.items()} for n, s in summ.items()}, {k: (round(v["effect"], 3), v["below_p05"], v["above_p95"]) for k, v in c.items()}, reading), material, detail=summ,
                      state="ACTIVE" if c["nz_share"]["below_p05"] else None, state_reason="the burden coordinate moves under a heritable mask; the stasis scope is escaped" if c["nz_share"]["below_p05"] else None)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, reading, time.time() - t0, summ))


if __name__ == "__main__":
    main()
