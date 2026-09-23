"""P-F07 [T-X13, bounded; cycle-4 candidate]: WEATHER DOSE in Proteus - damage probability {.25, .5, .75} x
generations {60, 120} x 2 seeds, sham at each; assay on the top-32 with the QUALIFIED scattered ruler
(f .10; the recorded delta's fixed-k / contiguous cells are superseded by T-R01) plus persistent words
and length. Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import evolver as EV           # noqa: E402
import scatter as SC           # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-F07", "T-X13"
PS, GS, SEEDS = (0.25, 0.5, 0.75), (60, 120), (1, 2)


def evo_job(j):
    EV.WEATHER_P = j["p"]
    r = EV.run(j["arm"], j["seed"], j["init"], G_=j["G"], label="nestor.pf07")
    eps = A.episodes(EV.ENV)
    tops = sorted(r["final"], key=lambda x: -x["reward"])[:32]
    rows = []
    for i, x in enumerate(tops):
        a = SC.assay(A.canonical(x["m"]), EV.ENV, eps, 0.10, 4, "delete", "%s-%.2f-%d-%d-%d" % (j["arm"], j["p"], j["G"], j["seed"], i))
        if not a.get("degenerate"):
            rows.append({"loss": a["loss"], "dreward": a["dreward"], "pw": a["persistent_words"], "n": a["n_instr"], "reward": x["reward"]})
    return {"arm": j["arm"], "p": j["p"], "G": j["G"], "seed": j["seed"], "loss": float(np.mean([r["loss"] for r in rows])), "pw": float(np.mean([r["pw"] for r in rows])), "len": float(np.mean([r["n"] for r in rows])), "reward": float(np.mean([r["reward"] for r in rows])), "n": len(rows)}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "parameterized-dose", "ps": PS, "Gs": GS, "seeds": SEEDS, "arms": ["weather", "sham"], "ruler": SC.PROVENANCE,
                         "note": "the candidate's fixed-k / fraction-matched cells are superseded by the qualified scattered ruler (T-R01)", "readouts": "top-32 loss (scattered f .10), persistent words, length, reward; weather - sham per dose",
                         "material_rule": "weather - sham loss below its band at any dose (pooled seeds, relabel over tops not available here: descriptive with 2 seeds; material if the difference exceeds .10 at >= 2 doses)", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    init, _ = EV.init_population()
    jobs = [{"arm": arm, "p": p, "G": G, "seed": s, "init": init} for p in PS for G in GS for s in SEEDS for arm in ("weather", "sham")]
    with A.pool(8) as ex:
        runs = list(ex.map(evo_job, jobs))
    table = {}
    for p in PS:
        for G in GS:
            w = [r for r in runs if r["arm"] == "weather" and r["p"] == p and r["G"] == G]
            s = [r for r in runs if r["arm"] == "sham" and r["p"] == p and r["G"] == G]
            table["p%.2f|G%d" % (p, G)] = {k: (float(np.mean([r[k] for r in w])), float(np.mean([r[k] for r in s]))) for k in ("loss", "pw", "len", "reward")}
    diffs = [v["loss"][0] - v["loss"][1] for v in table.values()]
    material = sum(1 for d in diffs if d <= -0.10) >= 2
    out = {"perturbation_id": PID, "parent": TID, "table": table, "loss_weather_minus_sham": {k: round(v["loss"][0] - v["loss"][1], 3) for k, v in table.items()}, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "weather dose (scattered ruler): loss weather-sham %s; pw (weather, sham) %s; len %s" % (out["loss_weather_minus_sham"], {k: (round(v["pw"][0], 0), round(v["pw"][1], 0)) for k, v in table.items()}, {k: (round(v["len"][0], 1), round(v["len"][1], 1)) for k, v in table.items()}), material, detail=table)
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, out["loss_weather_minus_sham"]))


if __name__ == "__main__":
    main()
