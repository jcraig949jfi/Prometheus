"""P-H03 [T-ARCH4/W1 x T-X17, deformation W]: NONSTATIONARY LIFETIME WORLDS. The Nestor evolver on W0 with
the generation's 16 episodes carrying PHASE SWITCH / MOVING WINDOW / ALTERNATING delays (an idle tick
before the ask = delay 1) or a PRICE SWITCH at generation 30, against STATIONARY-0 and STATIONARY-1;
60 generations, 2 seeds. Read: tops' reward on held-out delay-0 / 1 / 2 sets, the share solving both
0 and 1 (a switch), reward on unseen delay 2, persistent words, full curves. Computational scope:
integer programs on a bounded VM.
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
import ticks as TK             # noqa: E402
import manifold as MF          # noqa: E402
import evolver as EV           # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-H03", "T-ARCH4/W1"
REGIMES = ("stationary0", "stationary1", "phase_switch", "moving", "alternating", "price_switch")
SEEDS, G = (1, 2), 60
FLOOR = A.C1.FLOOR


def delayed(ep, n):
    return TK.insert(ep, TK.ask_ticks(ep)[0], [[]] * n) if n > 0 else TK.clone(ep)


def transform(regime):
    def f(eps, g):
        rng = A.SplitMix64(A.seed_from("nestor.ph03", A.LOOP_SEED, regime, g))
        if regime in ("stationary0", "price_switch"):
            return [TK.clone(e) for e in eps]
        if regime == "stationary1":
            return [delayed(e, 1) for e in eps]
        if regime == "phase_switch":
            k = 4 + rng.randbelow(9)
            return [delayed(e, 0 if i < k else 1) for i, e in enumerate(eps)]
        if regime == "moving":
            return [delayed(e, rng.randbelow(3)) for e in eps]
        if regime == "alternating":
            return [delayed(e, i % 2) for i, e in enumerate(eps)]
        raise ValueError(regime)
    return f


def held_sets():
    eps = A.episodes_for(A.ENVS["W0"], A.CAMPAIGN_SEED, "train", 2, A.C1.E)
    return {"d0": [delayed(e, 0) for e in eps], "d1": [delayed(e, 1) for e in eps], "d2": [delayed(e, 2) for e in eps], "mixed": [delayed(e, i % 2) for i, e in enumerate(eps)]}


def job(j):
    init, _ = EV.init_population()
    price = (lambda g: 0.0 if g < 30 else 1.0 / 64) if j["regime"] == "price_switch" else 0.0
    r = EV.run("select", j["seed"], init, G_=G, env="W0", ep_transform=transform(j["regime"]), price=price, label="nestor.ph03|" + j["regime"])
    tops = sorted(r["final"], key=lambda x: -x["reward"])[:16]
    H = held_sets()
    rows = []
    for x in tops:
        m = x["m"]
        rw = {k: A.evaluate(m, e, rng_seed=0, reward_mode="per_ask") for k, e in H.items()}
        rows.append({"rewards": {k: v["reward_per_ask"] for k, v in rw.items()}, "switch": bool(rw["d0"]["reward_per_ask"] >= FLOOR and rw["d1"]["reward_per_ask"] >= FLOOR), "pw": rw["d0"]["meter"].get("persistent_state_words", 0), "n_instr": CM.n_instr(m), "curve": MF.curve(m)[0], "m": m})
    return {"regime": j["regime"], "seed": j["seed"], "history_reward": [h["reward_mean"] for h in r["history"]], "len_final": r["history"][-1]["len_mean"], "tops": rows}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X17", "T-X12"], "deformation": "W", "scope": CM.SCOPE, "claim_type": "world-deformation", "regimes": REGIMES, "seeds": SEEDS, "generations": G,
                         "delay": "an idle (empty) tick before the ask; delay n = n ticks", "held_out": "episode family index 2: d0, d1, d2, mixed (alternating)", "price_switch": "fitness = reward - price * n_instr with price 0 before generation 30 and 1/64 after",
                         "readouts": ["tops' reward on d0 / d1 / d2 / mixed", "share of tops solving both d0 and d1 above floor (SWITCH)", "reward on unseen d2 (generalisation)", "persistent words, length", "curve set of the tops"],
                         "reading": "named from the regime x readout table only; a regime whose tops solve both phases above floor in >= 1/2 of tops while the stationary regimes do not is a SWITCHING transition; reward on d2 above floor from regimes that never saw d2 is PREDICTION",
                         "material_rule": "a regime differs from both stationary regimes on the switch share by >= .25 or on d2 reward by >= floor", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    with A.pool(8) as ex:
        runs = list(ex.map(job, [{"regime": rg, "seed": s} for rg in REGIMES for s in SEEDS]))
    table = {}
    for rg in REGIMES:
        ts = [t for r in runs if r["regime"] == rg for t in r["tops"]]
        cents = np.nanmean(np.array([t["curve"] for t in ts], float), axis=0).tolist()
        table[rg] = {"n_tops": len(ts), "reward": {k: float(np.mean([t["rewards"][k] for t in ts])) for k in ("d0", "d1", "d2", "mixed")}, "switch_share": float(np.mean([t["switch"] for t in ts])),
                     "d2_above_floor": float(np.mean([t["rewards"]["d2"] >= FLOOR for t in ts])), "pw": float(np.mean([t["pw"] for t in ts])), "n_instr": float(np.mean([t["n_instr"] for t in ts])),
                     "final_train_reward": float(np.mean([r["history_reward"][-1] for r in runs if r["regime"] == rg])), "centroid": cents, "nearest_known": MF.nearest(cents)[0] if all(x == x for x in cents) else None}
    st = max(table["stationary0"]["switch_share"], table["stationary1"]["switch_share"])
    st_d2 = max(table["stationary0"]["reward"]["d2"], table["stationary1"]["reward"]["d2"])
    transitions = {rg: {"switching": bool(v["switch_share"] - st >= 0.25 and v["switch_share"] >= 0.5), "prediction": bool(v["d2_above_floor"] >= 0.5 and v["reward"]["d2"] - st_d2 >= FLOOR)} for rg, v in table.items() if rg not in ("stationary0", "stationary1")}
    material = bool(any(v["switching"] or v["prediction"] for v in transitions.values()) or any(abs(table[rg]["reward"]["d2"] - st_d2) >= FLOOR for rg in transitions))
    out = {"perturbation_id": PID, "parent": TID, "table": {k: {kk: vv for kk, vv in v.items() if kk != "centroid"} for k, v in table.items()}, "centroids": {k: v["centroid"] for k, v in table.items()}, "transitions": transitions, "keys": MF.KEYS, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "tops.json").write_text(json.dumps([{"regime": r["regime"], "seed": r["seed"], "tops": [{k: v for k, v in t.items()} for t in r["tops"]]} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "nonstationary lifetime worlds: %s; transitions %s" % ({rg: (round(v["reward"]["d0"], 2), round(v["reward"]["d1"], 2), round(v["reward"]["d2"], 2), round(v["switch_share"], 2), round(v["pw"], 0), v["nearest_known"]) for rg, v in table.items()}, transitions), material, detail={"table": out["table"], "transitions": transitions})
    for tid in ("T-X17", "T-X12"):
        L.append_evidence(tid, PID, "cross: switch share by regime %s; nearest known shape of tops %s" % ({rg: round(v["switch_share"], 2) for rg, v in table.items()}, {rg: v["nearest_known"] for rg, v in table.items()}), material)
    print("DONE material=%s (%.0f s) %s %s" % (material, time.time() - t0, {rg: (round(v["reward"]["d0"], 2), round(v["reward"]["d1"], 2), round(v["reward"]["d2"], 2), round(v["switch_share"], 2)) for rg, v in table.items()}, transitions))


if __name__ == "__main__":
    main()
