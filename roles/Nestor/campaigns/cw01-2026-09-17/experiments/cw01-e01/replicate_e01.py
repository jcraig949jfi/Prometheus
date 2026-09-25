"""cw01-e01 REPLICATION — the clause the first EXECUTE driver failed to implement.

PREREGISTRATION.md defines COMPLETE as an advantage that "replicates and is
intervention-sensitive in the pre-registered direction". execute_e01.py checked
intervention-sensitivity, beats-control, mechanism-in-use and the backend swap —
but never replication, so it could award COMPLETE from a single attempt seed
(CW01-D016). This runs independent replicates and applies the full rule.

Independence: each replicate derives every draw from its own attempt_id, so the
world stream, the policy coins and the evolutionary trajectory are all distinct.
Nothing is shared but the world's declared economics.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[3]
for p in (str(REPO), str(BASE / "lib"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import world_e01 as W                       # noqa: E402
import seeds as S                           # noqa: E402

REPLICATES = ["cw01-e01-a01", "cw01-e01-r02", "cw01-e01-r03", "cw01-e01-r04", "cw01-e01-r05"]
N_IV = 32
GENERATIONS = 40
N_ORG = 64


def load_cfg(attempt_id):
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    cfg["attempt_id"] = attempt_id
    return cfg


def one_replicate(attempt_id):
    cfg = load_cfg(attempt_id)
    mk = S.seed

    def ep(g, arm, tag, i, **kw):
        return W.run_episode(g, cfg, arm, mk(attempt_id, f"stream|{tag}", i),
                             policy_seed=mk(attempt_id, f"policy|{tag}", i), **kw)

    evo = {a: W.evolve(cfg, a, GENERATIONS, N_ORG, mkseed=mk)
           for a in ("treatment", "control_no_retention")}

    # ancestor contrast, paired on identical streams
    anc = [ep(g, "treatment", "contrast", i) for i, g in enumerate(evo["treatment"]["ancestor_pop"])]
    fin = [ep(g, "treatment", "contrast", i) for i, g in enumerate(evo["treatment"]["final_pop"])]
    a_m = float(np.mean([r["score"] for r in anc]))
    f_m = float(np.mean([r["score"] for r in fin]))

    # interventions on the EVOLVED population
    pop = evo["treatment"]["final_pop"]
    sc = {}
    for name, arg in (("I1_sham", "I1_sham"), ("I1_erase", "I1_erase")):
        sc[name] = np.array([ep(pop[i % len(pop)], "treatment", "iv", i, intervention=arg)["score"]
                             for i in range(N_IV)])
    paired = sc["I1_erase"] - sc["I1_sham"]

    tr_final = evo["treatment"]["history"][-1]
    ct_final = evo["control_no_retention"]["history"][-1]
    return {
        "attempt_id": attempt_id,
        "treatment_final": tr_final["mean"],
        "control_final": ct_final["mean"],
        "beats_control": tr_final["mean"] > ct_final["mean"],
        "ancestor_relative_pct": 100 * (f_m - a_m) / a_m,
        "evolved_reentries": tr_final["mean_reentries"],
        "evolved_p_write": tr_final["mean_p_write"],
        "evolved_p_reenter": tr_final["mean_p_reenter"],
        "evolved_persist": tr_final["mean_persist"],
        "dependence_pct": float(100 * (sc["I1_erase"].mean() - sc["I1_sham"].mean()) / sc["I1_sham"].mean()),
        "paired_mean": float(paired.mean()),
        "paired_negative_in": f"{int((paired < 0).sum())}/{N_IV}",
        "dependence_holds": bool(paired.mean() < 0 and (paired < 0).sum() >= 0.75 * N_IV),
        "mechanism_in_use": bool(tr_final["mean_reentries"] > 1.0),
    }


def main():
    t0 = time.time()
    reps = []
    for aid in REPLICATES:
        r = one_replicate(aid)
        reps.append(r)
        print(f"  {aid}: treat {r['treatment_final']:.5f} vs ctl {r['control_final']:.5f} "
              f"| anc-rel {r['ancestor_relative_pct']:+6.2f}% | reent {r['evolved_reentries']:5.2f} "
              f"| dep {r['dependence_pct']:+6.2f}% ({r['paired_negative_in']}) "
              f"| {'OK' if r['beats_control'] and r['dependence_holds'] and r['mechanism_in_use'] else 'FAIL'}")

    n = len(reps)
    n_beats = sum(r["beats_control"] for r in reps)
    n_dep = sum(r["dependence_holds"] for r in reps)
    n_mech = sum(r["mechanism_in_use"] for r in reps)
    replicated = (n_beats == n and n_dep == n and n_mech == n)

    out = {
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e01",
        "kind": "REPLICATION", "n_replicates": n, "replicates": reps,
        "summary": {
            "beats_control": f"{n_beats}/{n}", "dependence_holds": f"{n_dep}/{n}",
            "mechanism_in_use": f"{n_mech}/{n}",
            "ancestor_relative_pct_mean": float(np.mean([r["ancestor_relative_pct"] for r in reps])),
            "ancestor_relative_pct_min": float(np.min([r["ancestor_relative_pct"] for r in reps])),
            "dependence_pct_mean": float(np.mean([r["dependence_pct"] for r in reps])),
            "dependence_pct_max": float(np.max([r["dependence_pct"] for r in reps])),
            "evolved_reentries_mean": float(np.mean([r["evolved_reentries"] for r in reps])),
        },
        "replicated": replicated,
        "rule": "PREREGISTRATION.md: COMPLETE requires the advantage to REPLICATE and be "
                "intervention-sensitive. Replication = every replicate must beat its matched control, "
                "show intervention dependence, and actually use the mechanism. One failure blocks COMPLETE.",
        "wall_s": round(time.time() - t0, 1),
    }
    (HERE / "REPLICATION.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n  beats_control {n_beats}/{n} | dependence {n_dep}/{n} | mechanism {n_mech}/{n}")
    print(f"  REPLICATED: {replicated}")
    print(f"  wall {out['wall_s']}s")
    return out


if __name__ == "__main__":
    main()
