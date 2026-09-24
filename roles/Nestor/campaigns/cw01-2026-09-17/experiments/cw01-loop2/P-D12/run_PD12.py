"""P-D12 (anti-gravity): amputation ALONE on w13 - does structural pressure raise held-out capability?

Parent T-X05 (<- e08). Arms: no pressure (CONTROL) and AMP with g_amp in {2, 5, 10, 20}; no tax;
4 lineages each; 200 generations; representatives = top-8 by train fitness (as e08); assay held64,
burden vector, competent count. Descriptive with the exact relabelling band (control vs each
interval) on lineage mean held64.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402

W8 = L.import_world("cw01-e08", "world_e08")
PID, TID, AID = "P-D12", "T-X05", "cw01-loop2-PD12"
INTERVALS, N_LIN, G = (None, 2, 5, 10, 20), 4, 200


def main():
    t0 = time.time()
    cfg = L.load_cfg("cw01-e08", AID)
    spec = W8.world_spec(cfg)
    floor = cfg["assay"]["competence_floor_held64"]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "exploratory-dose", "delta": "amputation interval g_amp in %s (None = control), no tax" % (INTERVALS,),
                         "unchanged": "e08 organism, world, selection, assay, train-selected representatives", "attacks": "TAX+AMP had the highest held64 (171) and the lowest burden in e08",
                         "measures": "per lineage: held64 mean of top-8, competent reps, scalar burden; relabelling band control vs each interval",
                         "continuation": ["amputation severity (slices per event)", "mask amputation", "held-out selection", "tax x interval"]})
    lines = []
    for gi in INTERVALS:
        arm = "CONTROL" if gi is None else "AMP"
        for li in range(N_LIN):
            r = W8.evolve(cfg, spec, AID + "|g%s" % gi, arm, li, G, lam=0.0, g_amp=gi, history_every=0)
            reps, _ = W8.representatives(r["pop"], r["fit"], 8)
            hs = W8.held_seeds(cfg)
            held = W8.rollout(spec, reps, hs)["fit"] / len(hs)
            B = W8.burden(reps, cfg, spec)
            rec = {"g_amp": gi, "lineage": li, "held64": float(held.mean()), "held64_max": float(held.max()), "competent": int((held > floor).sum()),
                   "scalar": float(W8.scalar_burden(B, cfg, spec).mean()), "params": float(B["params"].mean()), "train_fit_max": float(r["fit"].max())}
            lines.append(rec)
            print("   g_amp %-4s L%d held64 %.1f (max %.1f) competent %d/8 scalar %.3f params %.0f" % (gi, li, rec["held64"], rec["held64_max"], rec["competent"], rec["scalar"], rec["params"]), flush=True)
    ctl = [x["held64"] for x in lines if x["g_amp"] is None]
    summ, contrasts = {}, {}
    for gi in INTERVALS:
        v = [x for x in lines if x["g_amp"] == gi]
        summ[str(gi)] = {"held64": float(np.mean([x["held64"] for x in v])), "competent": float(np.mean([x["competent"] for x in v])), "scalar": float(np.mean([x["scalar"] for x in v]))}
        if gi is not None:
            contrasts[str(gi)] = L.relabel_diff(ctl, [x["held64"] for x in v])
    material = any(c["above_p95"] for c in contrasts.values())
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "contrasts_vs_control": contrasts, "lineages": lines, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "amputation-only dose: held64 %s; scalar %s" % ({k: round(v["held64"], 1) for k, v in summ.items()}, {k: round(v["scalar"], 3) for k, v in summ.items()}), material, detail={"summary": summ, "contrasts": contrasts})
    L.append_evidence("T-E08", PID, "structural pressure alone on w13: %s" % {k: round(v["held64"], 1) for k, v in summ.items()}, material)
    print("DONE material=%s %s (%.0f s)" % (material, {k: (round(v["held64"], 1), round(v["scalar"], 3)) for k, v in summ.items()}, time.time() - t0))


if __name__ == "__main__":
    main()
