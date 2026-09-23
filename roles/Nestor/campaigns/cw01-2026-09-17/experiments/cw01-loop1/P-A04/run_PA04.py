"""P-A04 (anti-gravity): does training breadth restore held-out competence on w13?

Parent T-X02 (<- e08/e09). Delta: e08's CONTROL arm (no tax, sham) with train seed sets of
8, 32 and 128 seeds (9100..); 4 / 4 / 3 lineages; 200 generations. Assay: top-8 by train
fitness scored on held64 (30000..30063); competent representative = held64 > 166.47;
competent lineage = >= 4 competent representatives. Unchanged: e08 organism (ragged TT at
R_max 5, read mask), world w13, selection, mutation, assay. Descriptive with the exact
relabelling band between the 8-seed and 128-seed groups on the per-lineage competent count.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402

W8 = L.import_world("cw01-e08", "world_e08")
PID, TID, AID = "P-A04", "T-X02", "cw01-loop1-PA04"
BREADTH = {8: 4, 32: 4, 128: 3}
G = 200


def main():
    t0 = time.time()
    base = L.load_cfg("cw01-e08", AID)
    spec = W8.world_spec(base)
    floor = base["assay"]["competence_floor_held64"]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "search-boundary-descriptive",
                         "delta": "train seed set size 8 / 32 / 128 for the e08 CONTROL arm", "lineages": BREADTH, "generations": G,
                         "unchanged": "organism, world, selection, mutation, assay seeds and competence floor",
                         "attacks": "the assumption that train8 fitness tracks held64 capability (D065, D069)",
                         "statistic": "per lineage: competent reps (of 8) and mean held64; 8-seed vs 128-seed by exact relabelling",
                         "decision": "descriptive; a relabelling-clearing rise in competent reps with breadth is material"})
    runs = {}
    for n_seeds, n_lin in BREADTH.items():
        cfg = copy.deepcopy(base)
        cfg["world"]["train_seeds"] = [9100, 9100 + n_seeds - 1]
        runs[n_seeds] = []
        for li in range(n_lin):
            t1 = time.time()
            ev = W8.evolve(cfg, spec, AID + "|n%d" % n_seeds, "CONTROL", li, G, lam=0.0, g_amp=None, history_every=0)
            reps, _ = W8.representatives(ev["pop"], ev["fit"], 8)
            hs = W8.held_seeds(cfg)
            held = W8.rollout(spec, reps, hs)["fit"] / len(hs)
            B = W8.burden(reps, cfg, spec)
            rec = {"lineage": li, "n_seeds": n_seeds, "competent_reps": int((held > floor).sum()), "held64_mean": float(held.mean()),
                   "held64_max": float(held.max()), "train_fit_max_per_seed": float(ev["fit"].max() / n_seeds),
                   "scalar_mean": float(W8.scalar_burden(B, cfg, spec).mean()), "wall_s": round(time.time() - t1, 1)}
            runs[n_seeds].append(rec)
            print("   seeds %3d L%d  train/seed %.1f  held64 mean %.1f max %.1f  competent %d/8  (%.0f s)"
                  % (n_seeds, li, rec["train_fit_max_per_seed"], rec["held64_mean"], rec["held64_max"], rec["competent_reps"], rec["wall_s"]), flush=True)
    c8, c128 = [r["competent_reps"] for r in runs[8]], [r["competent_reps"] for r in runs[128]]
    h8, h128 = [r["held64_mean"] for r in runs[8]], [r["held64_mean"] for r in runs[128]]
    contrast = L.relabel_diff(c8, c128)
    hcon = L.relabel_diff(h8, h128)
    material = bool(contrast["above_p95"] or hcon["above_p95"])
    res = {"perturbation_id": PID, "parent": TID, "runs": runs,
           "means": {n: {"competent_reps": float(np.mean([r["competent_reps"] for r in v])), "held64": float(np.mean([r["held64_mean"] for r in v]))}
                     for n, v in runs.items()},
           "contrast_128_minus_8_competent": contrast, "contrast_128_minus_8_held64": hcon, "material": material,
           "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "training breadth 8/32/128: competent reps %.2f/%.2f/%.2f, held64 %.1f/%.1f/%.1f; 128-8 competent effect %.2f [%.2f, %.2f]"
                      % (res["means"][8]["competent_reps"], res["means"][32]["competent_reps"], res["means"][128]["competent_reps"],
                         res["means"][8]["held64"], res["means"][32]["held64"], res["means"][128]["held64"],
                         contrast["effect"], contrast["p05"], contrast["p95"]), material, detail=res["means"],
                      state="ACTIVE", state_reason="screening axis measured; next: rotating seed schedules")
    L.append_evidence("T-E08", PID, "breadth screen bears on e08's eligibility surface: %s" % res["means"], material)
    print("DONE material=%s (%.0f s)" % (material, time.time() - t0))


if __name__ == "__main__":
    main()
