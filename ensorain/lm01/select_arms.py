"""WTP-LM01 arm-formation SELECTION procedure (#656/#657 JOINT, option b). DEV seeds only.

Each family (SELECTIVE, LOSSLESS, HYBRID) gets the SAME selection budget: 8 declared configurations, listed below
before any selection row. The criterion is the median headline AC over 16 dev selection seeds per stratum
(family x level x generator); ties go to grid order. The choice is frozen per stratum in dev/selection.json and reported
for every family. Never per world; never on campaign rows. The IM arms are constructed (rate-matched), not selected.

Selection seeds 9_400_000..9_400_015 are disjoint from the margin seeds (9_500_000..) and the fixture seeds (9_3xx_xxx).
SELECTIVE reference capacity = cells // 4, the middle of the R2 capacity ladder; the ladder is applied to the chosen
substrate afterwards."""
import json
import os
import sys
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "dev", "selection.json")
LOG = os.path.join(HERE, "DEV_SWEEP_LOG.jsonl")
SEL_SEEDS = range(9_400_000, 9_400_016)
BUDGET = 8
HEADLINE_SEL = {"F1_episodic": "exact_hit", "F2_latent": "never_seen", "F3_switch": "never_seen",
                "F4_transfer": "fresh_field", "F5_nuisance": "ood_never_seen"}

# (label, constructor spec) -- declared before any selection row; exactly BUDGET per family
SELECTIVE_GRID = [("S-lowrank", ("lowrank", None)), ("S-cp", ("cp", None)), ("S-tt", ("tt", None)),
                  ("S-dct", ("dct", None)), ("S-additive", ("additive", None)), ("S-hybrid_al", ("hybrid_al", None)),
                  ("S-lowrank-lr.03", ("lowrank", ("sgd", 0.03, 3))), ("S-lowrank-lr.3", ("lowrank", ("sgd", 0.3, 3)))]
LOSSLESS_GRID = [("L-K", ("K", None)), ("L-K-rec.1", ("K", 0.1)), ("L-K-rec.3", ("K", 0.3)),
                 ("L-R-r1", ("R", (1, None))), ("L-R-r2", ("R", (2, None))), ("L-R-r3", ("R", (3, None))),
                 ("L-R-r2-rec.1", ("R", (2, 0.1))), ("L-R-r2-rec.3", ("R", (2, 0.3)))]
HYBRID_GRID = [("H-c4-k4", (4, 4, None)), ("H-c4-k8", (4, 8, None)), ("H-c4-k16", (4, 16, None)),
               ("H-c4-k32", (4, 32, None)), ("H-c8-k8", (8, 8, None)), ("H-c2-k8", (2, 8, None)),
               ("H-c4-k8-rec.1", (4, 8, 0.1)), ("H-c4-k8-rec.3", (4, 8, 0.3))]
assert len(SELECTIVE_GRID) == len(LOSSLESS_GRID) == len(HYBRID_GRID) == BUDGET


def build(family, spec, dims):
    from .arms import Selective, LosslessK, LosslessKRec, LosslessR, LosslessRRec, Hybrid, HybridRec
    cells = int(np.prod(dims))
    if family == "SELECTIVE":
        kind, recipe = spec
        return Selective(kind, dims, cap=max(160, cells // 4), recipe=recipe)
    if family == "LOSSLESS":
        kind, p = spec
        if kind == "K":
            return LosslessK(dims) if p is None else LosslessKRec(dims, half_life=p)
        r, h = p
        return LosslessR(dims, rank=r) if h is None else LosslessRRec(dims, half_life=h, rank=r)
    div, k, h = spec
    cap = max(160, cells // div)
    return Hybrid(dims, cap=cap, k=k) if h is None else HybridRec(dims, cap=cap, half_life=h, k=k)


def job(a):
    import psutil
    if psutil.virtual_memory().available < 6 * 2 ** 30:
        return dict(a, status="STOP_RAM")
    from ensorain.wtp3.world3 import AC
    from .families import make_world
    w = make_world(a["family"], a["level"], a["seed"], gen=a["gen"])
    T, truth = w["tests"][HEADLINE_SEL[a["family"]]]
    if len(T) < 8:
        return dict(a, status="TOO_FEW_TEST", n_test=int(len(T)))
    res = {}
    for fam, grid in (("SELECTIVE", SELECTIVE_GRID), ("LOSSLESS", LOSSLESS_GRID), ("HYBRID", HYBRID_GRID)):
        for label, spec in grid:
            try:
                arm = build(fam, spec, w["dims"])
            except ValueError as ex:
                res[label] = None
                continue
            for A, y, _ in w["train"]:
                for i in range(0, len(y), 50):
                    arm.observe(A[i:i + 50], y[i:i + 50])
            res[label] = AC(arm.predict(T), truth, 1.0)
    return dict(a, status="OK", n_test=int(len(T)), AC=res)


def strata():
    from .families import FAMILIES, LEVELS, LATENT_GENS
    for f in FAMILIES:
        for l in LEVELS:
            for g in (("random",) if f == "F1_episodic" else LATENT_GENS):
                yield f, l, g


def choose(rows):
    out = {}
    for f, l, g in strata():
        rs = [r for r in rows if (r["family"], r["level"], r["gen"]) == (f, l, g) and r["status"] == "OK"]
        entry = dict(n_worlds=len(rs))
        for fam, grid in (("SELECTIVE", SELECTIVE_GRID), ("LOSSLESS", LOSSLESS_GRID), ("HYBRID", HYBRID_GRID)):
            med = {}
            for label, _ in grid:
                v = [r["AC"][label] for r in rs if r["AC"].get(label) is not None]
                med[label] = float(np.median(v)) if v else None
            ok = {k: v for k, v in med.items() if v is not None}
            best = max(ok, key=lambda k: (ok[k], -[x for x, _ in grid].index(k))) if ok else None
            entry[fam] = dict(choice=best, median_AC=med)
        out[f"{f}|{l}|{g}"] = entry
    return out


def main(workers=8):
    jobs = [dict(family=f, level=l, gen=g, seed=s) for f, l, g in strata() for s in SEL_SEEDS]
    t = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="start", sweep="lm01_arm_selection_v1", t=t(), workers=workers,
                                 priority="BELOW_NORMAL", seeds=f"{SEL_SEEDS.start}-{SEL_SEEDS.stop - 1}",
                                 n_jobs=len(jobs))) + "\n")
    t0 = time.time()
    from .learn_probe import _init
    with Pool(workers, initializer=_init) as p:
        rows = p.map(job, jobs, chunksize=2)
    sel = choose(rows)
    with open(OUT, "w") as fh:
        json.dump(dict(sweep="lm01_arm_selection_v1", seeds=[SEL_SEEDS.start, SEL_SEEDS.stop - 1], budget=BUDGET,
                       grids=dict(SELECTIVE=[x for x, _ in SELECTIVE_GRID], LOSSLESS=[x for x, _ in LOSSLESS_GRID],
                                  HYBRID=[x for x, _ in HYBRID_GRID]), selection=sel, rows=rows), fh)
    stops = sum(r["status"] == "STOP_RAM" for r in rows)
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="end", sweep="lm01_arm_selection_v1", t=t(), workers=workers, n_jobs=len(jobs),
                                 n_stop_ram=stops, wall_s=round(time.time() - t0, 1))) + "\n")
    print("done", len(rows), "stop_ram", stops, "wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 8))
