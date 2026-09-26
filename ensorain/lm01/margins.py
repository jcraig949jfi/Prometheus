"""WTP-LM01 DEV MARGIN SWEEP on the FROZEN arms (checklist A4, B9, C1, C3, C4, E4, E5, E6, E9, H1).
Dev margin seeds 9_500_000-9_500_015 (16 per stratum), 75 strata, envelope v2.

Per world (a stratum = family x level x generator):
  arms       the frozen SELECTIVE / LOSSLESS / HYBRID choice (FROZEN_SELECTION.json), each run TWICE: replicate a (learner
             seed 0, the full headline test set) and replicate b (learner seed 1, a bootstrap resample of the same test
             cells). |a - b| over worlds -> the per-stratum equivalence MARGIN (97.5th percentile, pooled over families).
  n1         the better of the global and recent constants (gate reference, E5)
  ci         the bootstrap SD of each arm's replicate-a AC at test sizes 16/32/64/128/256/all -> the CI half-width vs n
             -> the derived MIN ELIGIBLE COUNT (E4: half-width <= margin/2)
  ladder     RESERVOIR-REFIT (rank 3) with random eviction and with the stratum's frozen eviction candidate, at
             B in {c/8, c/4, c/2, c, 2c, full}: AC, HR2, HR2_signal, R, dist, persistent bytes, ALS iterations, and
             cap-hit fraction (B9). Plus converged L-R rank 3, the curve's full-store end.
  dual       C4-ii at B in {c/4, c}: the random B' whose HR2 matches the eviction arm's (interpolated on the random
             ladder), 3 random seeds, with the extra bytes charged.
  posctl     E6: the stratum's world with a corrupted half (mode-0 < d0/2 observations get extra noise SD 3), scored on
             the clean half; oracle vs random eviction at B = c/2, at the stratum's own revisit density.
Writes dev/margins/<stratum>.jsonl rows (one per world) from Python; start/end go to DEV_SWEEP_LOG.jsonl.
The per-stratum reductions (margin, min count, X, B*, positive-control pass) are computed by margins_reduce.py (committed
separately) BEFORE the prereg freezes."""
import json
import os
import sys
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np

HERE = os.path.dirname(__file__)
OUTDIR = os.path.join(HERE, "dev", "margins")
LOG = os.path.join(HERE, "DEV_SWEEP_LOG.jsonl")
SEEDS = range(9_500_000, 9_500_016)
CI_SIZES = (16, 32, 64, 128, 256)
RANK = 3
DUAL_AT = ("c/4", "c")
N_BOOT = 200


def _feed(arm, segs):
    for A, y, _ in segs:
        for i in range(0, len(y), 50):
            arm.observe(A[i:i + 50], y[i:i + 50])
    return arm


def _ac_cells(pred, truth):
    return (np.nan_to_num(pred, nan=0.0, posinf=1e6, neginf=-1e6) - truth) ** 2


def _AC(e):
    return float(np.clip(-np.log10(max(float(np.mean(e)), 1e-12)), -3, 6))


def _ci(e, rng):
    out = {}
    for n in CI_SIZES + (len(e),):
        if n > len(e):
            continue
        acs = [_AC(e[rng.integers(0, len(e), n)]) for _ in range(N_BOOT)]
        out[str(n)] = float(np.std(acs))
    return out


def _spec(family, label):
    from .select_arms import SELECTIVE_GRID, LOSSLESS_GRID, HYBRID_GRID, EVICT_GRID
    grid = dict(SELECTIVE=SELECTIVE_GRID, LOSSLESS=LOSSLESS_GRID, HYBRID=HYBRID_GRID, RESERVOIR_EVICT=EVICT_GRID)[family]
    return dict(grid)[label]


def _build(family, label, dims, seed):
    from .arms import Selective, LosslessK, LosslessKRec, LosslessR, LosslessRRec, Hybrid, HybridRec
    spec = _spec(family, label)
    cells = int(np.prod(dims))
    if family == "SELECTIVE":
        kind, recipe = spec
        return Selective(kind, dims, cap=max(160, cells // 4), seed=seed, recipe=recipe)
    if family == "LOSSLESS":
        kind, p = spec
        if kind == "K":
            return LosslessK(dims) if p is None else LosslessKRec(dims, half_life=p)
        r, h = p
        return LosslessR(dims, rank=r, seed=seed) if h is None else LosslessRRec(dims, half_life=h, rank=r, seed=seed)
    div, k, h = spec
    cap = max(160, cells // div)
    return Hybrid(dims, cap=cap, k=k, seed=seed) if h is None else HybridRec(dims, cap=cap, half_life=h, k=k, seed=seed)


def _iters(arm):
    it = getattr(arm, "als_iters", None) or getattr(arm.meter, "als_iters", [])
    return dict(n_fits=len(it), median=float(np.median(it)) if it else None,
                cap_frac=float(np.mean(np.array(it) >= 80)) if it else None)


def _cellcount(dims, family, scale):
    """Operator ruling 2026-09-26 item 3: for F5 under scale "real_cells" the nuisance mode is excluded from the capacity
    denominator. "all_cells" is the original (dev v1) definition."""
    d = dims[:-1] if (scale == "real_cells" and family == "F5_nuisance") else dims
    return int(np.prod(d))


def _rungs(dims, n, family=None, scale="all_cells"):
    c = _cellcount(dims, family, scale)
    r = {"c/8": c // 8, "c/4": c // 4, "c/2": c // 2, "c": c, "2c": 2 * c, "full": n}
    return {k: v for k, v in r.items() if v <= n or k == "full"}


def job(a):
    import psutil
    if psutil.virtual_memory().available < 6 * 2 ** 30:
        return dict(a, status="STOP_RAM")
    from .arms import BufferALS, LosslessR
    from .families import make_world
    from .recover import recoverability
    from .select_arms import HEADLINE_SEL
    t0 = time.time()
    f, l, g, sd = a["family"], a["level"], a["gen"], a["seed"]
    ch = a["choices"]
    w = make_world(f, l, sd, gen=g)
    T, truth = w["tests"][HEADLINE_SEL[f]]
    out = dict(a, n_test=int(len(T)), n_unseen=w["n_unseen"], coverage=w["coverage"])
    out.pop("choices")
    segs = w["train"]
    A_all = np.concatenate([s[0] for s in segs])
    y_all = np.concatenate([s[1] for s in segs])
    s_all = np.concatenate([s[2] for s in segs])
    n = len(y_all)
    out["visits_per_cell"] = n / float(_cellcount(w["dims"], f, a.get("scale", "all_cells")))
    if len(T) < 8:
        return dict(out, status="TOO_FEW_TEST", wall=time.time() - t0)
    rng = np.random.default_rng(sd + 77)
    boot = rng.integers(0, len(T), len(T))
    n1 = max(_AC(_ac_cells(np.full(len(T), y_all.mean()), truth)),
             _AC(_ac_cells(np.full(len(T), y_all[-n // 4:].mean()), truth)))
    out["N1"] = n1
    arms = {}
    for fam in ("SELECTIVE", "LOSSLESS", "HYBRID"):
        lab = ch.get(fam)
        if lab is None:
            continue
        ea = _ac_cells(_feed(_build(fam, lab, w["dims"], 0), segs).predict(T), truth)
        armb = _feed(_build(fam, lab, w["dims"], 1), segs)
        eb = _ac_cells(armb.predict(T[boot]), truth[boot])
        arms[fam] = dict(label=lab, AC_a=_AC(ea), AC_b=_AC(eb), ci_sd=_ci(ea, rng), meter=armb.meter.as_dict(),
                         iters=_iters(armb))
    out["arms"] = arms
    tau = 0.1
    rr = lambda arm: recoverability(arm, A_all, y_all, tau, np.random.default_rng(sd + 1), signal=s_all)
    lad = {}
    scale = a.get("scale", "all_cells")
    out["rung_scale"] = scale
    for rung, B in _rungs(w["dims"], n, f, scale).items():
        for ev in ("random", ch.get("RESERVOIR_EVICT_POLICY")):
            if ev is None:
                continue
            arm = _feed(BufferALS(w["dims"], RANK, max(1, B), evict=ev), segs)
            rec = rr(arm)
            lad[f"{ev}|{rung}"] = dict(B=int(B), AC=_AC(_ac_cells(arm.predict(T), truth)), HR2=rec["HR2"],
                                       HR2_signal=rec["HR2_signal"], R=rec["R"], dist=rec["dist"],
                                       bytes=arm.meter.peak_persistent, iters=_iters(arm))
    lr = _feed(LosslessR(w["dims"], rank=RANK), segs)
    lad["L-R|full"] = dict(B=n, AC=_AC(_ac_cells(lr.predict(T), truth)), bytes=lr.meter.peak_persistent,
                           iters=_iters(lr))
    out["ladder"] = lad
    ev = ch.get("RESERVOIR_EVICT_POLICY")
    dual = {}
    if ev is not None:
        rB = sorted([(v["HR2"], v["B"]) for k, v in lad.items() if k.startswith("random|")])
        for rung in DUAL_AT:
            key = f"{ev}|{rung}"
            if key not in lad:
                continue
            target = lad[key]["HR2"]
            hs, bs = np.array([x[0] for x in rB]), np.array([x[1] for x in rB])
            Bm = int(np.clip(np.interp(target, hs, bs), 1, n))
            res = []
            for k in range(3):
                arm = _feed(BufferALS(w["dims"], RANK, Bm, evict="random", seed=100 + k), segs)
                rec = rr(arm)
                res.append(dict(AC=_AC(_ac_cells(arm.predict(T), truth)), HR2=rec["HR2"], bytes=arm.meter.peak_persistent))
            dual[rung] = dict(target_HR2=target, B_random=Bm, runs=res)
    out["dual"] = dual
    d0 = w["dims"][0]
    prng = np.random.default_rng(sd + 5)
    csegs = [(A, y + (A[:, 0] < d0 // 2) * prng.normal(0, 3.0, len(y)), s) for A, y, s in segs]
    keep = T[:, 0] >= d0 // 2
    pc = {}
    if keep.sum() >= 8:
        Bp = max(1, _cellcount(w["dims"], f, scale) // 2)
        for evp in ("random", "oracle"):
            arm = _feed(BufferALS(w["dims"], RANK, Bp, evict=evp, oracle_keep=lambda X, d0=d0: X[:, 0] >= d0 // 2), csegs)
            pc[evp] = _AC(_ac_cells(arm.predict(T[keep]), truth[keep]))
        pc["n_test"] = int(keep.sum())
    out["posctl"] = pc
    return dict(out, status="OK", wall=time.time() - t0)


def jobs_from_frozen():
    from .select_arms import EVICT_GRID
    fz = json.load(open(os.path.join(HERE, "FROZEN_SELECTION.json")))["choices"]
    evmap = dict(EVICT_GRID)
    J = []
    for key, c in fz.items():
        f, l, g = key.split("|")
        ch = {fam: c.get(fam) for fam in ("SELECTIVE", "LOSSLESS", "HYBRID")}
        ch["RESERVOIR_EVICT_POLICY"] = evmap.get(c.get("RESERVOIR_EVICT")) if c.get("RESERVOIR_EVICT") else None
        for sd in SEEDS:
            J.append(dict(family=f, level=l, gen=g, seed=sd, choices=ch))
    return J


def main(workers=8):
    from .learn_probe import _init
    J = jobs_from_frozen()
    order = {"L3": 0, "L2": 1, "L1": 2}                         # heaviest first for load balance
    J.sort(key=lambda j: order[j["level"]])
    os.makedirs(OUTDIR, exist_ok=True)
    t = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="start", sweep="lm01_margins_v1", t=t(), workers=workers, priority="BELOW_NORMAL",
                                 seeds=f"{SEEDS.start}-{SEEDS.stop - 1}", n_jobs=len(J))) + "\n")
    t0 = time.time()
    n_stop = 0
    with Pool(workers, initializer=_init) as p:
        for r in p.imap_unordered(job, J, chunksize=1):
            n_stop += r["status"] == "STOP_RAM"
            fn = os.path.join(OUTDIR, f"{r['family']}__{r['level']}__{r['gen']}.jsonl")
            with open(fn, "a") as fh:
                fh.write(json.dumps(r) + "\n")
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="end", sweep="lm01_margins_v1", t=t(), workers=workers, n_jobs=len(J),
                                 n_stop_ram=n_stop, wall_s=round(time.time() - t0, 1))) + "\n")
    print("done", len(J), "stop_ram", n_stop, "wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 8))
