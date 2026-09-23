"""P-E09 (serendipity cross, T-X13 x T-ARCH4/M1): WEATHER IN A SUBSTRATE THAT CAN REPRESENT PROTECTION.

The Nestor evolver with arms 'static' (= selection), 'sham' (weather draws made, nothing applied)
and 'weather' (each birth evaluated on a copy that lost 2 random instructions with probability .5),
2 seeds; the P-D01 damage assay on each arm's top-32 and on their ancestors (paired); state-use
descriptors (persist policy shares, persistent words, tape writes, length) by arm and generation.
Reading rules preregistered. Computational scope: integer programs on a bounded VM.
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

PID, TID = "P-E09", "T-X13"
SEEDS, TOP = (1, 2), 32
ARMS = ("select", "sham", "weather")


def evo_job(j):
    return EV.run(j["arm"], j["seed"], j["init"])


def assay_job(j):
    r = EV.assay(j["m"], j["tag"])
    r.update({k: v for k, v in j.items() if k != "m"})
    return r


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-ARCH4/M1", "T-E07"], "scope": CM.SCOPE, "claim_type": "serendipity-cross",
                         "evolver": {"N": EV.N, "G": EV.G, "tournament": EV.K_T, "env": EV.ENV, "weather": "blind deletion of 2 instructions on the evaluated copy with probability .5 per birth; genome inherited intact", "seeds": SEEDS},
                         "arms": list(ARMS), "harness_check": "sham arm's final population must equal the select arm's (same draws, nothing applied) - a difference voids the run",
                         "assay": {"cells": EV.ASSAY_CELLS, "draws": 4, "decode": "modulo", "loss_env": EV.ENV, "held": "W1_d1"},
                         "reading_rules": {"PROTECTION": "weather tops' loss below select tops' (relabel below p05) AND persistent words / length not lower (relabel not below p05)",
                                           "AVOIDANCE": "weather tops' persistent words or tape writes below select tops' (below p05) AND loss not below",
                                           "BOTH": "loss below AND state use below", "NEITHER": "otherwise"},
                         "material_rule": "any relabelled contrast between weather and select tops outside its band (loss, persistent words, tape writes, length), or ancestor-paired loss under weather below p05",
                         "continuation": ["damage probability dose", "operand damage during evolution", "persist frozen per arm"], "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    init, parent_m = EV.init_population()
    with A.pool(6) as ex:
        runs = list(ex.map(evo_job, [{"arm": arm, "seed": s, "init": init} for arm in ARMS for s in SEEDS]))
    by = {(r["arm"], r["seed"]): r for r in runs}
    sham_ok = all(json.dumps([x["m"] for x in by[("sham", s)]["final"]], sort_keys=True) == json.dumps([x["m"] for x in by[("select", s)]["final"]], sort_keys=True) for s in SEEDS)
    jobs = []
    for r in runs:
        chosen = sorted(r["final"], key=lambda x: -x["reward"])[:TOP]
        for i, x in enumerate(chosen):
            jobs.append({"m": x["m"], "tag": "%s-%d-top-%d" % (r["arm"], r["seed"], i), "group": r["arm"], "seed": r["seed"], "anc": x["anc"], "reward": x["reward"]})
    ancs = sorted({j["anc"] for j in jobs})
    for a in ancs:
        jobs.append({"m": init[a]["m"], "tag": "anc-%d" % a, "group": "ancestor", "seed": None, "anc": a, "reward": None})
    with A.pool(8) as ex:
        rows = list(ex.map(assay_job, jobs))
    anc_loss = {r["anc"]: r["loss"] for r in rows if r["group"] == "ancestor"}

    def grp(g):
        return [r for r in rows if r["group"] == g and r["loss"] is not None]
    M = EV.mean_or_none
    means = {g: {"loss": M([r["loss"] for r in grp(g)]), "n": len(grp(g)), "len": M([r["n_instr"] for r in grp(g)]),
                 "persistent_words": M([r["persistent_words"] for r in grp(g)]), "tape_writes": M([r["tape_writes"] for r in grp(g)]),
                 "persist_none_share": M([float(r["persist"] == "none") for r in grp(g)]), "held_delta": M([r["held_delta"] for r in grp(g)])} for g in ARMS + ("ancestor",)}
    W, S_ = grp("weather"), grp("select")
    rl = {k: L.relabel_diff([r[k] for r in S_], [r[k] for r in W]) for k in ("loss", "persistent_words", "tape_writes", "n_instr")}
    sf_w_anc = CM.paired_signflip([r["loss"] - anc_loss[r["anc"]] for r in W if anc_loss.get(r["anc"]) is not None])
    sf_s_anc = CM.paired_signflip([r["loss"] - anc_loss[r["anc"]] for r in S_ if anc_loss.get(r["anc"]) is not None])
    loss_below = rl["loss"]["below_p05"]
    state_below = rl["persistent_words"]["below_p05"] or rl["tape_writes"]["below_p05"]
    state_not_lower = not (rl["persistent_words"]["below_p05"] or rl["n_instr"]["below_p05"])
    if loss_below and state_not_lower:
        reading = "PROTECTION"
    elif state_below and not loss_below:
        reading = "AVOIDANCE"
    elif loss_below and state_below:
        reading = "BOTH"
    else:
        reading = "NEITHER"
    traj = {r["arm"] + "-" + str(r["seed"]): {k: [h[k] for h in r["history"]] for k in ("reward_mean", "len_mean", "persistent_words", "tape_writes", "occupancy", "n_ancestors")} | {"persist_none": [h["persist"]["none"] for h in r["history"]]} for r in runs}
    material = bool(sham_ok and (any(v["below_p05"] or v["above_p95"] for v in rl.values()) or (sf_w_anc and sf_w_anc["below_p05"])))
    out = {"perturbation_id": PID, "parent": TID, "sham_equals_select": sham_ok, "reading": reading if sham_ok else "INVALID_HARNESS", "group_means": means,
           "weather_minus_select_relabel": rl, "weather_minus_ancestor": sf_w_anc, "select_minus_ancestor": sf_s_anc, "trajectories": traj, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "rows"} for r in rows], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "weather in Proteus (sham==select %s): reading %s; loss weather %s select %s ancestor %s; persistent words %s vs %s; tape writes %s vs %s; len %s vs %s; relabel %s"
                      % (sham_ok, out["reading"], means["weather"]["loss"], means["select"]["loss"], means["ancestor"]["loss"], means["weather"]["persistent_words"], means["select"]["persistent_words"],
                         means["weather"]["tape_writes"], means["select"]["tape_writes"], means["weather"]["len"], means["select"]["len"],
                         {k: (round(v["effect"], 3), v["below_p05"], v["above_p95"]) for k, v in rl.items()}), material, detail={"means": means, "relabel": rl})
    print("DONE material=%s reading=%s sham_ok=%s (%.0f s) %s" % (material, out["reading"], sham_ok, time.time() - t0, {g: (v["loss"], v["persistent_words"], v["len"]) for g, v in means.items()}))


if __name__ == "__main__":
    main()
