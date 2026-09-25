"""P-E03 [deformation A, T-ARCH4/M1]: SELECTED TOPS vs THEIR OWN ANCESTORS vs DRIFT.

The Nestor evolver (evolver.py) runs 60 generations from the depth-16 walkers of every viable
parent under (i) tournament-3 selection and (ii) drift, 2 seeds each. The P-D01 damage assay is
then applied to the selected top-32, a drift sample of 32, the ancestor walker of each and the
original parent of each ancestor, paired by ancestor. Reading rules preregistered below. Lineage
survival (distinct ancestors per generation) is recorded in both arms (T-X01's floor, free).
Computational scope: integer programs on a bounded VM.
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

PID, TID = "P-E03", "T-ARCH4/M1"
SEEDS, TOP = (1, 2), 32


def evo_job(j):
    return EV.run(j["arm"], j["seed"], j["init"])


def assay_job(j):
    r = EV.assay(j["m"], j["tag"])
    r.update({k: v for k, v in j.items() if k not in ("m",)})
    return r


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "A", "scope": CM.SCOPE, "claim_type": "required-comparison",
                         "evolver": {"N": EV.N, "G": EV.G, "tournament": EV.K_T, "env": EV.ENV, "episodes_per_generation": "fresh (index 1000+g)", "births": "one grammar op, mutation only", "seeds": SEEDS},
                         "arms": ["select", "drift"], "groups": ["selected top-32 by final W2_K2 reward", "drift sample 32 (seeded uniform)", "ancestor walker of each (paired)", "original parent of each ancestor"],
                         "assay": {"cells": EV.ASSAY_CELLS, "draws": 4, "decode": "modulo", "loss_env": EV.ENV, "held": "W1_d1"},
                         "reading_rules": {"SELECTED": "tops - ancestors sign-flip below p05 AND tops - drift relabel below p05",
                                           "INHERITED": "tops - ancestors inside its band (robustness was already in the walkers)",
                                           "DRIFT_ASSOCIATED": "tops - ancestors below p05 AND drift - ancestors below p05 AND tops - drift inside band",
                                           "NONE": "otherwise; a length covariate regression is reported alongside"},
                         "material_rule": "any paired or relabelled contrast outside its band, or the reading is not NONE",
                         "continuation": ["selection on W0 / W1_d4", "generation dose", "n_ops 2 births"], "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    init, parent_m = EV.init_population()
    with A.pool(4) as ex:
        runs = list(ex.map(evo_job, [{"arm": arm, "seed": s, "init": init} for arm in ("select", "drift") for s in SEEDS]))
    jobs = []
    rng = A.SplitMix64(A.seed_from("nestor.pe03.sample", A.LOOP_SEED))
    for r in runs:
        fin = r["final"]
        if r["arm"] == "select":
            chosen = sorted(fin, key=lambda x: -x["reward"])[:TOP]
        else:
            idx = sorted(set(int(rng.next_u32() % len(fin)) for _ in range(TOP * 3)))[:TOP]
            chosen = [fin[i] for i in idx]
        for i, x in enumerate(chosen):
            jobs.append({"m": x["m"], "tag": "%s-%d-top-%d" % (r["arm"], r["seed"], i), "group": "top_" + r["arm"], "arm": r["arm"], "seed": r["seed"], "anc": x["anc"], "anc_parent": x["anc_parent"], "reward": x["reward"]})
    ancs = sorted({j["anc"] for j in jobs})
    for a in ancs:
        jobs.append({"m": init[a]["m"], "tag": "anc-%d" % a, "group": "ancestor", "arm": None, "seed": None, "anc": a, "anc_parent": init[a]["anc_parent"], "reward": None})
    for pid in sorted({init[a]["anc_parent"] for a in ancs}):
        jobs.append({"m": parent_m[pid], "tag": "parent-" + pid, "group": "parent", "arm": None, "seed": None, "anc": None, "anc_parent": pid, "reward": None})
    with A.pool(8) as ex:
        rows = list(ex.map(assay_job, jobs))
    anc_loss = {r["anc"]: r["loss"] for r in rows if r["group"] == "ancestor"}
    par_loss = {r["anc_parent"]: r["loss"] for r in rows if r["group"] == "parent"}

    def grp(g):
        return [r for r in rows if r["group"] == g and r["loss"] is not None]
    tops_s, tops_d = grp("top_select"), grp("top_drift")
    M = EV.mean_or_none
    means = {g: {"loss": M([r["loss"] for r in grp(g)]), "n": len(grp(g)), "degenerate": sum(r["degenerate"] for r in rows if r["group"] == g),
                 "len": M([r["n_instr"] for r in grp(g)]), "held_delta": M([r["held_delta"] for r in grp(g)]),
                 "persistent_words": M([r["persistent_words"] for r in grp(g)])} for g in ("top_select", "top_drift", "ancestor", "parent")}
    sf_sel_anc = CM.paired_signflip([r["loss"] - anc_loss[r["anc"]] for r in tops_s if anc_loss.get(r["anc"]) is not None])
    sf_drf_anc = CM.paired_signflip([r["loss"] - anc_loss[r["anc"]] for r in tops_d if anc_loss.get(r["anc"]) is not None])
    sf_anc_par = CM.paired_signflip([anc_loss[a] - par_loss[init[a]["anc_parent"]] for a in ancs if anc_loss.get(a) is not None and par_loss.get(init[a]["anc_parent"]) is not None])
    rl_sel_drf = L.relabel_diff([r["loss"] for r in tops_d], [r["loss"] for r in tops_s])
    # length covariate: loss ~ 1 + log len + [select] on tops of both arms
    X = np.column_stack([np.ones(len(tops_s) + len(tops_d)), np.log([r["n_instr"] for r in tops_s + tops_d]), [1.0] * len(tops_s) + [0.0] * len(tops_d)])
    y = np.array([r["loss"] for r in tops_s + tops_d])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    sel_below = bool(sf_sel_anc and sf_sel_anc["below_p05"])
    drf_below = bool(sf_drf_anc and sf_drf_anc["below_p05"])
    sd_below = bool(rl_sel_drf["below_p05"])
    sd_inside = not (rl_sel_drf["below_p05"] or rl_sel_drf["above_p95"])
    if sel_below and sd_below:
        reading = "SELECTED"
    elif sf_sel_anc and not (sf_sel_anc["below_p05"] or sf_sel_anc["above_p95"]):
        reading = "INHERITED"
    elif sel_below and drf_below and sd_inside:
        reading = "DRIFT_ASSOCIATED"
    else:
        reading = "NONE"
    lineage = {r["arm"] + "-" + str(r["seed"]): [h["n_ancestors"] for h in r["history"]] for r in runs}
    traj = {r["arm"] + "-" + str(r["seed"]): {k: [h[k] for h in r["history"]] for k in ("reward_mean", "len_mean", "persistent_words", "tape_writes")} for r in runs}
    material = bool(reading != "NONE" or sd_below or rl_sel_drf["above_p95"] or (sf_anc_par and (sf_anc_par["below_p05"] or sf_anc_par["above_p95"])))
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "group_means": means,
           "contrasts": {"top_select_minus_ancestor": sf_sel_anc, "top_drift_minus_ancestor": sf_drf_anc, "ancestor_minus_parent": sf_anc_par, "select_minus_drift_relabel": rl_sel_drf},
           "length_regression": {"intercept": float(beta[0]), "log_len": float(beta[1]), "select": float(beta[2])},
           "lineage_survival": lineage, "trajectories": traj, "n_rows": len(rows), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "rows"} for r in rows], ensure_ascii=True, default=CM.js), encoding="utf-8")
    (HERE / "runs.json").write_text(json.dumps([{"arm": r["arm"], "seed": r["seed"], "history": r["history"], "final": [{k: v for k, v in x.items() if k != "m"} for x in r["final"]]} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "tops vs ancestors vs drift: reading %s; loss top_select %s top_drift %s ancestor %s parent %s; top-anc %s; drift-anc %s; select-drift %s; log-len coef %+.3f select coef %+.3f; ancestors surviving at G60 select %s drift %s"
                      % (reading, means["top_select"]["loss"], means["top_drift"]["loss"], means["ancestor"]["loss"], means["parent"]["loss"],
                         (round(sf_sel_anc["mean_diff"], 3), sf_sel_anc["below_p05"]) if sf_sel_anc else None, (round(sf_drf_anc["mean_diff"], 3), sf_drf_anc["below_p05"]) if sf_drf_anc else None,
                         (round(rl_sel_drf["effect"], 3), rl_sel_drf["below_p05"], rl_sel_drf["above_p95"]), beta[1], beta[2],
                         [lineage[k][-1] for k in lineage if k.startswith("select")], [lineage[k][-1] for k in lineage if k.startswith("drift")]),
                      material, detail={"means": means, "contrasts": out["contrasts"], "lineage_final": {k: v[-1] for k, v in lineage.items()}})
    print("DONE material=%s reading=%s (%.0f s) %s | %s" % (material, reading, time.time() - t0, {g: v["loss"] for g, v in means.items()}, {k: v[-1] for k, v in lineage.items()}))


if __name__ == "__main__":
    main()
