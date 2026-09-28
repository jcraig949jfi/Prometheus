"""WTP-LM01 CAMPAIGN runner (PREREG s4-s10). Computes every per-world reading. Launch only through launch_gate.

Per world (stratum = family x level x generator; frozen arms from FROZEN_SELECTION.json):
  L-K (always; the F-B strict test), the frozen LOSSLESS choice, and converged L-R rank 3 (the headline endpoint, #693)
  SELECTIVE capacity LADDER (6.2): the frozen substrate at caps cells/16 x 2^k, up to the frozen LOSSLESS arm's
    persistent bytes / 8. INCOMPATIBLE caps are recorded, not skipped silently.
  frozen HYBRID + the R1e index-ablation gap (6.4)
  RESERVOIR ladder (6.1): random and the frozen eviction candidate at rungs c/8..2c and the full store, with HR2 /
    HR2_signal / R / dist / bytes / ALS iterations. The rung scale is RUNG_SCALE (pending the F5 ruling, #719).
  dual matching (6.3) at c/4 and c, 3 random seeds; per-stratum eviction positive control (E6)
Every arm carries its measured resource meter (G2). Rows are written from Python, one file per stratum.
The DRY RUN (dev seeds only) gives the resource estimate (G5) and never touches campaign seeds."""
import json
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np

from .margins import (_feed, _ac_cells, _AC, _iters, _build, RANK, DUAL_AT, HERE)

RUNG_SCALE = "real_cells"         # operator ruling 2026-09-26 item 3 (governing); "all_cells" = the old dev-v1 interpretation
OUTROOT = os.path.join(HERE, "campaign")


def _cells(w):
    d = w["dims"]
    if RUNG_SCALE == "real_cells" and w["family"] == "F5_nuisance":
        d = d[:-1]
    return int(np.prod(d))


def _rungs(w, n):
    c = _cells(w)
    r = {"c/8": c // 8, "c/4": c // 4, "c/2": c // 2, "c": c, "2c": 2 * c, "full": n}
    return {k: v for k, v in r.items() if v <= n or k == "full"}   # same rule as margins.py


def selective_ladder(w, label, segs, T, truth, max_bytes):
    from .arms import Selective
    from .select_arms import SELECTIVE_GRID
    kind, recipe = dict(SELECTIVE_GRID)[label]
    cells = int(np.prod(w["dims"]))
    out, cap = {}, max(16, cells // 16)
    while cap * 8 <= max_bytes:
        try:
            arm = _feed(Selective(kind, w["dims"], cap=cap, recipe=recipe), segs)
            out[str(cap)] = dict(AC=_AC(_ac_cells(arm.predict(T), truth)), meter=arm.meter.as_dict())
        except ValueError as ex:
            out[str(cap)] = dict(status=f"INCOMPATIBLE: {ex}")
        cap *= 2
    return out


def job(a):
    import psutil
    if psutil.virtual_memory().available < 6 * 2 ** 30:
        return dict(a, status="STOP_RAM")
    from .ablation import ablation_gap
    from .arms import BufferALS, LosslessR, LosslessK
    from .families import make_world
    from .recover import recoverability
    from .select_arms import HEADLINE_SEL
    t0 = time.time()
    f, l, g, sd, ch = a["family"], a["level"], a["gen"], a["seed"], a["choices"]
    w = make_world(f, l, sd, gen=g)
    T, truth = w["tests"][HEADLINE_SEL[f]]
    segs = w["train"]
    A_all = np.concatenate([s[0] for s in segs])
    y_all = np.concatenate([s[1] for s in segs])
    s_all = np.concatenate([s[2] for s in segs])
    n = len(y_all)
    out = {k: a[k] for k in ("family", "level", "gen", "seed")}
    out.update(n_test=int(len(T)), n_unseen=w["n_unseen"], coverage=w["coverage"], visits_per_cell=n / _cells(w),
               rung_scale=RUNG_SCALE)
    if len(T) < 8:
        return dict(out, status="TOO_FEW_TEST", wall=time.time() - t0)
    out["N1"] = max(_AC(_ac_cells(np.full(len(T), y_all.mean()), truth)),
                    _AC(_ac_cells(np.full(len(T), y_all[-n // 4:].mean()), truth)))
    arms = {}
    lk = _feed(LosslessK(w["dims"]), segs)
    arms["L-K"] = dict(AC=_AC(_ac_cells(lk.predict(T), truth)), meter=lk.meter.as_dict())
    for fam in ("LOSSLESS", "HYBRID"):
        lab = ch.get(fam)
        if lab is None:
            continue
        arm = _feed(_build(fam, lab, w["dims"], 0), segs)
        rec = dict(label=lab, AC=_AC(_ac_cells(arm.predict(T), truth)), meter=arm.meter.as_dict(), iters=_iters(arm))
        if fam == "HYBRID":
            rec["ablation"] = ablation_gap(arm, T, truth, seed=sd)
        arms[fam] = rec
    lmax = arms.get("LOSSLESS", arms["L-K"])["meter"]["peak_persistent"]
    if ch.get("SELECTIVE"):
        arms["SELECTIVE_LADDER"] = dict(label=ch["SELECTIVE"],
                                        ladder=selective_ladder(w, ch["SELECTIVE"], segs, T, truth, lmax))
    out["arms"] = arms
    rr = lambda arm: recoverability(arm, A_all, y_all, 0.1, np.random.default_rng(sd + 1), signal=s_all)
    lad = {}
    ev = ch.get("RESERVOIR_EVICT_POLICY")
    for rung, B in _rungs(w, n).items():
        for pol in ("random", ev):
            if pol is None:
                continue
            arm = _feed(BufferALS(w["dims"], RANK, max(1, B), evict=pol), segs)
            r = rr(arm)
            lad[f"{pol}|{rung}"] = dict(B=int(B), AC=_AC(_ac_cells(arm.predict(T), truth)), HR2=r["HR2"],
                                        HR2_signal=r["HR2_signal"], R=r["R"], dist=r["dist"],
                                        meter=arm.meter.as_dict(), iters=_iters(arm))
    lr = _feed(LosslessR(w["dims"], rank=RANK), segs)
    lad["L-R|full"] = dict(B=n, AC=_AC(_ac_cells(lr.predict(T), truth)), meter=lr.meter.as_dict(), iters=_iters(lr))
    out["ladder"] = lad
    dual = {}
    if ev is not None:
        rB = sorted((v["HR2"], v["B"]) for k, v in lad.items() if k.startswith("random|"))
        hs, bs = np.array([x[0] for x in rB]), np.array([x[1] for x in rB])
        for rung in DUAL_AT:
            key = f"{ev}|{rung}"
            if key not in lad:
                continue
            Bm = int(np.clip(np.interp(lad[key]["HR2"], hs, bs), 1, n))
            runs = []
            for k in range(3):
                arm = _feed(BufferALS(w["dims"], RANK, Bm, evict="random", seed=100 + k), segs)
                r = rr(arm)
                runs.append(dict(AC=_AC(_ac_cells(arm.predict(T), truth)), HR2=r["HR2"], bytes=arm.meter.peak_persistent))
            dual[rung] = dict(target_HR2=lad[key]["HR2"], B_random=Bm, runs=runs)
    out["dual"] = dual
    d0 = w["dims"][0]
    prng = np.random.default_rng(sd + 5)
    csegs = [(A, y + (A[:, 0] < d0 // 2) * prng.normal(0, 3.0, len(y)), s) for A, y, s in segs]
    keep = T[:, 0] >= d0 // 2
    pc = {}
    if keep.sum() >= 8:
        Bp = max(1, _cells(w) // 2)
        for pol in ("random", "oracle"):
            arm = _feed(BufferALS(w["dims"], RANK, Bp, evict=pol, oracle_keep=lambda X, d0=d0: X[:, 0] >= d0 // 2), csegs)
            pc[pol] = _AC(_ac_cells(arm.predict(T[keep]), truth[keep]))
    out["posctl"] = pc
    return dict(out, status="OK", wall=time.time() - t0)


def jobs(seed_map):
    from .margins import jobs_from_frozen
    base = {(j["family"], j["level"], j["gen"]): j["choices"] for j in jobs_from_frozen()}
    return [dict(family=f, level=l, gen=g, seed=s, choices=base[(f, l, g)])
            for (f, l, g), seeds in seed_map.items() for s in seeds]


def dry_run(n_per_stratum=1, seed0=9_600_000, strata=None):
    """G5 resource estimate on DEV seeds (9_600_000..): wall + peak bytes per world per stratum."""
    from .margins import jobs_from_frozen
    keys = sorted({(j["family"], j["level"], j["gen"]) for j in jobs_from_frozen()})
    keys = [k for k in keys if strata is None or k in strata]
    res = {}
    for i, k in enumerate(keys):
        J = jobs({k: [seed0 + i * 10 + r for r in range(n_per_stratum)]})
        rows = [job(j) for j in J]
        res["|".join(k)] = [dict(status=r["status"], wall=r.get("wall")) for r in rows]
    return res


if __name__ == "__main__":
    print("LM01 campaign runner: launch only via launch_gate.campaign_seeds(release_id, ...); use dry_run() on dev seeds.")
    sys.exit(0)
