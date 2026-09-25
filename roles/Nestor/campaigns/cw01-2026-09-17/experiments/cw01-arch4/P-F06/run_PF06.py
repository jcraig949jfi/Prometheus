"""P-F06 [T-ARCH4/M1, deformation A]: P-E03 REPLICATED over 6 seeds with a NEUTRAL-BAND DRIFT control
and a generation dose (archives at G 20 / 40 / 60). Computational scope: integer programs on a bounded VM.
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
A, L = CM.A, CM.L

PID, TID = "P-F06", "T-ARCH4/M1"
SEEDS, TOP, ARCHS = (1, 2, 3, 4, 5, 6), 32, (19, 39, 59)


def evo_job(j):
    r = EV.run(j["arm"], j["seed"], j["init"], archive_gens=ARCHS, label="nestor.pf06")
    return {"arm": r["arm"], "seed": r["seed"], "history": r["history"], "archive": r["archive"], "final": r["final"]}


def assay_job(j):
    r = EV.assay(j["m"], j["tag"])
    r.update({k: v for k, v in j.items() if k != "m"})
    return r


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "A", "scope": CM.SCOPE, "claim_type": "replication-confirmatory",
                         "evolver": {"N": EV.N, "G": EV.G, "tournament": EV.K_T, "env": EV.ENV, "seeds": SEEDS, "archives": [g + 1 for g in ARCHS]},
                         "arms": {"select": "tournament 3", "ndrift": "uniform parent; child kept only if |r_child - r_parent| <= band (competence retained, no fitness ordering)"},
                         "assay": {"cells": EV.ASSAY_CELLS, "draws": 4, "loss_env": EV.ENV, "held": "W1_d1"}, "samples": "top-32 (select) / 32-sample (ndrift) at each archive; ancestor walker of each",
                         "promotion_rule": "per seed at G60: (top_select - ancestor) sign-flip below p05 AND (select - ndrift) relabel below p05; promote only if >= 4/6 seeds",
                         "material_rule": "the promotion rule holds, or the ndrift arm itself moves loss vs ancestors outside its band, or the generation dose is monotone",
                         "continuation": ["selection on W0 / W1_d4", "n_ops 2", "band width of the control"], "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    init, parent_m = EV.init_population()
    with A.pool(6) as ex:
        runs = list(ex.map(evo_job, [{"arm": arm, "seed": s, "init": init} for arm in ("select", "ndrift") for s in SEEDS]))
    jobs = []
    for r in runs:
        for g, pop in list(r["archive"].items()):                 # archives 20/40/60 (the 'final' offspring are not re-assayed)
            rng = A.SplitMix64(A.seed_from("nestor.pf06.sample", A.LOOP_SEED, r["arm"], r["seed"], str(g)))
            if r["arm"] == "select":
                chosen = sorted(pop, key=lambda x: -x["reward"])[:TOP]
            else:
                idx = sorted(set(int(rng.next_u32() % len(pop)) for _ in range(TOP * 3)))[:TOP]
                chosen = [pop[i] for i in idx]
            for i, x in enumerate(chosen):
                jobs.append({"m": x["m"], "tag": "%s-%d-%s-%d" % (r["arm"], r["seed"], g, i), "group": r["arm"], "seed": r["seed"], "gen": (int(g) + 1 if g != "final" else EV.G), "anc": x["anc"], "reward": x["reward"]})
    ancs = sorted({j["anc"] for j in jobs})
    for a in ancs:
        jobs.append({"m": init[a]["m"], "tag": "anc-%d" % a, "group": "ancestor", "seed": None, "gen": 0, "anc": a, "reward": None})
    with A.pool(8) as ex:
        rows = list(ex.map(assay_job, jobs))
    anc_loss = {r["anc"]: r["loss"] for r in rows if r["group"] == "ancestor"}
    M = EV.mean_or_none
    per_seed, dose = {}, {}
    for s in SEEDS:
        per_seed[s] = {}
        for g in sorted({r["gen"] for r in rows if r["seed"] == s}):
            S_ = [r for r in rows if r["group"] == "select" and r["seed"] == s and r["gen"] == g and r["loss"] is not None]
            D_ = [r for r in rows if r["group"] == "ndrift" and r["seed"] == s and r["gen"] == g and r["loss"] is not None]
            sf_s = CM.paired_signflip([r["loss"] - anc_loss[r["anc"]] for r in S_ if anc_loss.get(r["anc"]) is not None])
            sf_d = CM.paired_signflip([r["loss"] - anc_loss[r["anc"]] for r in D_ if anc_loss.get(r["anc"]) is not None])
            rl = L.relabel_diff([r["loss"] for r in D_], [r["loss"] for r in S_]) if S_ and D_ else None
            per_seed[s][g] = {"loss_select": M([r["loss"] for r in S_]), "loss_ndrift": M([r["loss"] for r in D_]), "degenerate_ndrift": sum(r["degenerate"] for r in rows if r["group"] == "ndrift" and r["seed"] == s and r["gen"] == g),
                              "select_minus_anc": sf_s, "ndrift_minus_anc": sf_d, "select_minus_ndrift": rl,
                              "len_select": M([r["n_instr"] for r in S_]), "len_ndrift": M([r["n_instr"] for r in D_]), "pw_select": M([r["persistent_words"] for r in S_]), "pw_ndrift": M([r["persistent_words"] for r in D_])}
    g60 = EV.G
    hold = [s for s in SEEDS if per_seed[s].get(g60) and per_seed[s][g60]["select_minus_anc"] and per_seed[s][g60]["select_minus_anc"]["below_p05"] and per_seed[s][g60]["select_minus_ndrift"] and per_seed[s][g60]["select_minus_ndrift"]["below_p05"]]
    promoted = len(hold) >= 4
    for g in sorted({r["gen"] for r in rows if r["gen"] > 0}):
        dose[g] = {"loss_select": M([per_seed[s][g]["loss_select"] for s in SEEDS if g in per_seed[s]]), "loss_ndrift": M([per_seed[s][g]["loss_ndrift"] for s in SEEDS if g in per_seed[s]]),
                   "seeds_select_below_anc": sum(1 for s in SEEDS if g in per_seed[s] and per_seed[s][g]["select_minus_anc"] and per_seed[s][g]["select_minus_anc"]["below_p05"]),
                   "seeds_ndrift_below_anc": sum(1 for s in SEEDS if g in per_seed[s] and per_seed[s][g]["ndrift_minus_anc"] and per_seed[s][g]["ndrift_minus_anc"]["below_p05"])}
    ndrift_moves = sum(1 for s in SEEDS if per_seed[s].get(g60) and per_seed[s][g60]["ndrift_minus_anc"] and (per_seed[s][g60]["ndrift_minus_anc"]["below_p05"] or per_seed[s][g60]["ndrift_minus_anc"]["above_p95"]))
    lineage = {"%s-%d" % (r["arm"], r["seed"]): [h["n_ancestors"] for h in r["history"]][-1] for r in runs}
    competent = {"%s-%d" % (r["arm"], r["seed"]): r["history"][-1]["reward_mean"] for r in runs}
    material = bool(promoted or ndrift_moves >= 3)
    out = {"perturbation_id": PID, "parent": TID, "reading": "SELECTED_REPLICATED" if promoted else "NOT_PROMOTED", "seeds_holding": hold, "per_seed": {str(s): {str(g): v for g, v in d.items()} for s, d in per_seed.items()},
           "generation_dose": {str(g): v for g, v in dose.items()}, "ndrift_moves_vs_ancestor_seeds": ndrift_moves, "final_reward_mean": competent, "ancestors_surviving": lineage,
           "anc_loss_mean": M(list(anc_loss.values())), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "rows"} for r in rows], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "P-E03 replication (6 seeds, neutral-band drift control competent: final reward %s): %s, seeds holding %s; dose %s; ndrift moves vs ancestors in %d seeds; ancestors surviving %s"
                      % ({k: round(v, 2) for k, v in competent.items()}, out["reading"], hold, {g: (round(v["loss_select"], 3) if v["loss_select"] is not None else None, round(v["loss_ndrift"], 3) if v["loss_ndrift"] is not None else None, v["seeds_select_below_anc"], v["seeds_ndrift_below_anc"]) for g, v in dose.items()}, ndrift_moves, lineage),
                      material, detail={"dose": dose, "seeds_holding": hold})
    print("DONE material=%s %s holding %s (%.0f s) dose %s competent %s" % (material, out["reading"], hold, time.time() - t0, dose, competent))


if __name__ == "__main__":
    main()
