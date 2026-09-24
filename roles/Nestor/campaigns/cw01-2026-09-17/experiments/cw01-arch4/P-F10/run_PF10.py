"""P-F10 (serendipity / anti-gravity; T-X16 x T-ARCH4/M1 x T-X13 x T-X05): PRICE-MEDIATED PRUNING
TRANSPLANTED INTO PROTEUS. The Nestor evolver with fitness = reward - lambda * n_instr, lambda in
{0, 1/128, 1/32} x weather {off, on} x 2 seeds, 60 generations on W2_K2; sham at lambda 0 (harness
check). Does a price on length flip the sign of weather's effect on reward / length / state, as it
did for the damaged substrate in e06? Computational scope: integer programs on a bounded VM.
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

PID, TID = "P-F10", "T-X16"
LAMBDAS, SEEDS, TOP = (0.0, 1.0 / 128, 1.0 / 32), (1, 2), 32


def evo_job(j):
    r = EV.run(j["arm"], j["seed"], j["init"], price=j["lam"], label="nestor.pf10")
    return {"arm": j["arm"], "lam": j["lam"], "seed": j["seed"], "history": r["history"], "final": r["final"]}


def assay_job(j):
    r = EV.assay(j["m"], j["tag"])
    r.update({k: v for k, v in j.items() if k != "m"})
    return r


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-ARCH4/M1", "T-X13", "T-X05"], "scope": CM.SCOPE, "claim_type": "serendipity-cross",
                         "evolver": {"N": EV.N, "G": EV.G, "env": EV.ENV, "lambdas": LAMBDAS, "seeds": SEEDS, "weather": "p=.5, 2 instructions on the evaluated copy"},
                         "arms": "select (weather off) and weather at every lambda; sham at lambda 0 must equal select (harness)",
                         "readouts": "final-population reward (fixed W2_K2 episodes), length, persistent words; top-32 damage loss; weather - select at each lambda with relabel over the pooled top-32 (2 seeds)",
                         "predictions": {"CROSS_SUBSTRATE_PRUNING": "weather's effect on reward rises with lambda (cost at 0, neutral or beneficial at 1/32) as the damaged substrate gained in e06 under a price",
                                         "NOT_PORTABLE": "weather's effect does not depend on lambda", "REVERSED": "weather hurts more under a price"},
                         "material_rule": "the weather - select reward or length contrast changes sign or clears its band differently across lambdas", "continuation": ["price on persistent words", "tax x weather dose"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    init, _ = EV.init_population()
    jobs = [{"arm": arm, "lam": lam, "seed": s, "init": init} for lam in LAMBDAS for arm in ("select", "weather") for s in SEEDS] + [{"arm": "sham", "lam": 0.0, "seed": s, "init": init} for s in SEEDS]
    with A.pool(8) as ex:
        runs = list(ex.map(evo_job, jobs))
    by = {(r["arm"], r["lam"], r["seed"]): r for r in runs}
    sham_ok = all(json.dumps([x["m"] for x in by[("sham", 0.0, s)]["final"]], sort_keys=True) == json.dumps([x["m"] for x in by[("select", 0.0, s)]["final"]], sort_keys=True) for s in SEEDS)
    aj = []
    for r in runs:
        if r["arm"] == "sham":
            continue
        for i, x in enumerate(sorted(r["final"], key=lambda x: -x["reward"])[:TOP]):
            aj.append({"m": x["m"], "tag": "%s-%.4f-%d-%d" % (r["arm"], r["lam"], r["seed"], i), "arm": r["arm"], "lam": r["lam"], "seed": r["seed"], "reward": x["reward"]})
    with A.pool(8) as ex:
        rows = list(ex.map(assay_job, aj))
    M = EV.mean_or_none
    table, contrasts = {}, {}
    for lam in LAMBDAS:
        for arm in ("select", "weather"):
            rs = [r for r in rows if r["arm"] == arm and r["lam"] == lam]
            fin = [x for s in SEEDS for x in by[(arm, lam, s)]["final"]]
            table["%s|%.4f" % (arm, lam)] = {"pop_reward": float(np.mean([x["reward"] for x in fin])), "pop_len": float(np.mean([CM.n_instr(x["m"]) for x in fin])),
                                              "top_reward": M([r["reward"] for r in rs]), "top_loss": M([r["loss"] for r in rs]), "top_len": M([r["n_instr"] for r in rs]), "top_pw": M([r["persistent_words"] for r in rs])}
        S_ = [r for r in rows if r["arm"] == "select" and r["lam"] == lam]
        W_ = [r for r in rows if r["arm"] == "weather" and r["lam"] == lam]
        contrasts["%.4f" % lam] = {k: L.relabel_diff([r[k] for r in S_], [r[k] for r in W_]) for k in ("reward", "n_instr", "persistent_words")}
        contrasts["%.4f" % lam]["loss"] = L.relabel_diff([r["loss"] for r in S_ if r["loss"] is not None], [r["loss"] for r in W_ if r["loss"] is not None])
    eff = {lam: contrasts["%.4f" % lam]["reward"]["effect"] for lam in LAMBDAS}
    sig = {lam: (contrasts["%.4f" % lam]["reward"]["below_p05"], contrasts["%.4f" % lam]["reward"]["above_p95"]) for lam in LAMBDAS}
    signs = [np.sign(eff[l]) for l in LAMBDAS]
    if eff[LAMBDAS[-1]] > eff[0] and (sig[0][0] or sig[LAMBDAS[-1]][1]):
        reading = "CROSS_SUBSTRATE_PRUNING"
    elif eff[LAMBDAS[-1]] < eff[0] and sig[LAMBDAS[-1]][0]:
        reading = "REVERSED"
    elif not any(any(v) for v in sig.values()):
        reading = "NOT_PORTABLE"
    else:
        reading = "UNRESOLVED"
    material = bool(sham_ok and (len(set(signs)) > 1 or any(any(v) for v in sig.values())))
    out = {"perturbation_id": PID, "parent": TID, "sham_equals_select": sham_ok, "reading": reading if sham_ok else "INVALID_HARNESS", "table": table,
           "weather_minus_select": {k: {kk: {a: b for a, b in vv.items() if a in ("effect", "p05", "p95", "below_p05", "above_p95")} for kk, vv in v.items()} for k, v in contrasts.items()},
           "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "rows"} for r in rows], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "price x weather in Proteus (sham %s): reading %s; weather-select reward by lambda %s; length %s; persistent words %s; loss %s; table %s"
                      % (sham_ok, out["reading"], {k: (round(v["reward"]["effect"], 3), v["reward"]["below_p05"], v["reward"]["above_p95"]) for k, v in contrasts.items()},
                         {k: (round(v["n_instr"]["effect"], 2), v["n_instr"]["below_p05"], v["n_instr"]["above_p95"]) for k, v in contrasts.items()},
                         {k: (round(v["persistent_words"]["effect"], 1), v["persistent_words"]["below_p05"], v["persistent_words"]["above_p95"]) for k, v in contrasts.items()},
                         {k: (round(v["loss"]["effect"], 3), v["loss"]["below_p05"], v["loss"]["above_p95"]) for k, v in contrasts.items()},
                         {k: (round(v["pop_reward"], 3), round(v["pop_len"], 1)) for k, v in table.items()}), material, detail={"table": table})
    for tid in ("T-ARCH4/M1", "T-X13"):
        L.append_evidence(tid, PID, "cross: weather x length price in Proteus reads %s (reward effects by lambda %s)" % (out["reading"], {k: round(v["reward"]["effect"], 3) for k, v in contrasts.items()}), material)
    print("DONE material=%s reading=%s sham=%s (%.0f s) %s" % (material, out["reading"], sham_ok, time.time() - t0, {k: (round(v["pop_reward"], 3), round(v["pop_len"], 1)) for k, v in table.items()}))


if __name__ == "__main__":
    main()
