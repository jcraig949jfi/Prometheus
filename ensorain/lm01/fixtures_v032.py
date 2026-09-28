"""v0.3.2 fixtures read by the frozen analysis (dev seeds only; the output dev/fixtures_v032.json is frozen with the prereg).

headline_pc[level]: HEADLINE POSITIVE CONTROL (review F5/F15a). Planted F2 lowrank worlds (rank <= 3 = the readout's
  class) with HIGH observation noise (SD 1.0, declared), life 4x, dev seeds 9_890_000-007. The world is built so that every
  additional exact record lowers the estimation error of the rank-3 fit. EXACT_RETENTION_PAYS "should" fire if the rung
  grid and the analysis can see retention paying at all.
  PASS iff analysis.headline() returns LOSSLESS_TRANSIENT_CONTRACTION or COUNTERMODEL_SIGNAL.
  A level that fails has a headline that CANNOT FIRE (the analysis then reads UNRESOLVED_INSTRUMENT_CANNOT_FIRE).
ablation_pc: the R1e oracle-key HYBRID positive control (ablation.positive_control), PASS iff median gap > DELTA."""
import json
import os
import sys
import time

import numpy as np

from .margins_reduce_v2 import DELTA

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "dev", "fixtures_v032.json")
SEEDS = range(9_890_000, 9_890_008)
NOISE = 1.0


def _world_rows(level, seed):
    from .campaign import _feed, _rungs, RANK
    from .arms import BufferALS, LosslessR
    from .families import make_world
    from .margins import _ac_cells, _AC
    w = make_world("F2_latent", level, seed, gen="lowrank", noise=NOISE)
    T, truth = w["tests"]["never_seen"]
    if len(T) < 8:
        return None
    y = np.concatenate([s[1] for s in w["train"]])
    n = len(y)
    lad = {}
    for rung, B in _rungs(w, n).items():
        arm = _feed(BufferALS(w["dims"], RANK, max(1, B), evict="random"), w["train"]).finalize()
        lad[f"random|{rung}"] = dict(AC=_AC(_ac_cells(arm.predict(T), truth)))
    lr = _feed(LosslessR(w["dims"], rank=RANK), w["train"])
    lad["L-R|full"] = dict(AC=_AC(_ac_cells(lr.predict(T), truth)))
    N1 = max(_AC(_ac_cells(np.full(len(T), y.mean()), truth)), _AC(_ac_cells(np.full(len(T), y[-n // 4:].mean()), truth)))
    return dict(status="OK", level=level, N1=N1, ladder=lad, arms={"L-K": dict(AC=N1)})


def main():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    from .analysis import headline
    from .ablation import positive_control
    t0 = time.time()
    hpc, detail, all_rows = {}, {}, {}
    for level in ("L1", "L2", "L3"):
        rows = [r for r in (_world_rows(level, s) for s in SEEDS) if r]
        all_rows[level] = rows
        h = headline(rows, DELTA, True) if len(rows) >= 3 else dict(label="TOO_FEW_WORLDS")
        hpc[level] = h["label"] in ("LOSSLESS_TRANSIENT_CONTRACTION", "COUNTERMODEL_SIGNAL")
        detail[level] = dict(n=len(rows), label=h["label"],
                             LR_minus_rung={g: (None if c is None else {k: round(c[k], 3) for k in ("mean", "lo", "hi")})
                                            for g, c in h.get("LR_minus_rung", {}).items()},
                             G1=h.get("G1_LR_minus_N1"))
    apc = positive_control()
    out = dict(headline_pc=hpc, headline_pc_detail=detail, noise=NOISE, seeds=[SEEDS.start, SEEDS.stop - 1],
               rows={lv: r for lv, r in all_rows.items()},
               ablation_pc=bool(apc["median_gap"] > DELTA), ablation_pc_median_gap=apc["median_gap"],
               wall_s=round(time.time() - t0, 1))
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "headline_pc_detail"}), json.dumps(detail, indent=1)[:3000])


if __name__ == "__main__":
    sys.exit(main())
