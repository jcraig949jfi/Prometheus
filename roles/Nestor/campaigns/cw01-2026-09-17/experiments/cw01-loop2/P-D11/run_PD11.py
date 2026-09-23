"""P-D11: two material single-axis results crossed - tournament size 2 (P-A10) x recombination 1.0
(P-A07) - in e06's mixed ecology.

Parent T-X01 (x T-E06). Conditions: (t3, r0.5) as e06 ran; (t2, r0.5); (t3, r1.0); (t2, r1.0).
Mixed assortative arm seeded at 0.5, 80 generations, 4 attempt ids. Measures: coexistence at 80
(both labels > 5%), final TREE frequency, growth advantage (TREE vs TAPE), lineage survival.
Descriptive with the count of coexisting runs per condition.
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

W6 = L.import_world("cw01-e06", "world_e06")
PID, TID = "P-D11", "T-X01"


def growth(run, a, b):
    """world_e06.growth_advantage's formula without its latent crash (len() on an int; CW01-D074)."""
    import math
    h = run["history"]
    res = 1.0 / max(2.0, sum(h[0].get("n_" + lab, 0) for lab in run["labels"]))

    def odds(rec):
        x = min(max(rec.get("freq_" + a, 0.0), res), 1 - res)
        y = min(max(rec.get("freq_" + b, 0.0), res), 1 - res)
        return x / y
    return float((math.log(odds(h[-1])) - math.log(odds(h[0]))) / max(1, len(h) - 1))
CONDS = (("t3_r0.5", 3, 0.5), ("t2_r0.5", 2, 0.5), ("t3_r1.0", 3, 1.0), ("t2_r1.0", 2, 1.0))
IDS = ["cw01-loop2-PD11-%d" % i for i in range(4)]


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "cross-material-descriptive",
                         "delta": "tournament size {3,2} x recombination rate {0.5,1.0} in the mixed_assortative arm, seeded .5, 80 generations, 4 attempt ids",
                         "unchanged": "e06 world, sharing, prices, mutation", "attacks": "whether weaker selection and crossover-heavy variation compose into coexistence (e06's original question)",
                         "measures": "coexisting at 80, final TREE frequency, growth advantage, lineage survival; count of coexisting runs per condition",
                         "continuation": ["tournament 1", "rate 0.75", "seeded-frequency grid", "240 generations"]})
    rows = []
    for aid in IDS:
        for name, ts, rate in CONDS:
            cfg = L.load_cfg("cw01-e06", aid)
            cfg["ecology"]["tournament_size"] = ts
            cfg["ecology"]["recombination_rate"] = rate
            targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
            run = W6.evolve(cfg, "mixed_assortative", 80, 96, S.seed, "%s|%s" % (aid, name), freq_first=0.5, target=targets)
            rec = {"aid": aid, "cond": name, "coexist": W6.coexisting(run), "final_TREE": W6.final_frequency(run, "TREE"),
                   "growth_TREE_vs_TAPE": growth(run, "TREE", "TAPE"), "lineage_survival": run["lineage_survival"],
                   "extinct": run["extinction_generation"]}
            rows.append(rec)
            print("   %s %-8s coexist %s  TREE %.3f  growth %+.4f  surv %.2f  extinct %s" % (aid[-1], name, rec["coexist"], rec["final_TREE"], rec["growth_TREE_vs_TAPE"], rec["lineage_survival"], rec["extinct"]), flush=True)
    summ = {name: {"coexist": sum(1 for r in rows if r["cond"] == name and r["coexist"]), "final_TREE_mean": float(np.mean([r["final_TREE"] for r in rows if r["cond"] == name])),
                   "growth_mean": float(np.mean([r["growth_TREE_vs_TAPE"] for r in rows if r["cond"] == name]))} for name, _, _ in CONDS}
    material = bool(summ["t2_r1.0"]["coexist"] >= 2 and summ["t3_r0.5"]["coexist"] == 0)
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "tournament x recombination cross: coexistence counts %s; final TREE %s" % ({k: v["coexist"] for k, v in summ.items()}, {k: round(v["final_TREE_mean"], 3) for k, v in summ.items()}), material, detail=summ)
    L.append_evidence("T-E06", PID, "coexistence attempt under (t2, r1.0): %d/4 coexisting" % summ["t2_r1.0"]["coexist"], material)
    print("DONE material=%s %s (%.0f s)" % (material, summ, time.time() - t0))


if __name__ == "__main__":
    main()
