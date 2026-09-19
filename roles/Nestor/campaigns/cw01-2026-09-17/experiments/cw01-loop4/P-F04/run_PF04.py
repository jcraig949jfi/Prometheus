"""P-F04 (T-X16 x T-E06 x T-E07): DAMAGE_EFFECT vs PRICE_MEDIATED_PRUNING.

Structural price {0.01, 0} x damage {none, tape, tree, both} x fraction {.05, .1, .2} x rate {.55, .6,
.65, .7, .75} x f0 .1 x 3 attempt ids, 240 generations. Damage draws from a separate rng keyed
(attempt, generation) - draw-matched by construction; a sham at fraction .1 / price .01 retains the
none == sham check. Pruning signature = final TREE(tree-damaged) - final TREE(tape-damaged): positive
under pruning. If it clears its band at price .01 and not at price 0 -> PRICE_MEDIATED_PRUNING; both
-> DAMAGE_EFFECT; reversed sign at 0 -> REVERSED.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
sys.path.insert(0, str(HERE.parents[1] / "cw01-loop3" / "P-E06"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import run_PE06 as E6          # noqa: E402  (its W6 patch and damage_pop are reused; F is read from MODE)

W6 = E6.W6
PID, TID = "P-F04", "T-X16"
PRICES, DAMAGE, FRACS, RATES, F0, IDS, GENS = (0.01, 0.0), ("tape", "tree", "both"), (0.05, 0.1, 0.2), (0.55, 0.6, 0.65, 0.7, 0.75), 0.1, ["cw01-loop4-PF04-%d" % i for i in range(3)], 240


def generation_w(pop, cfg, items, cross_ok, r, elite_frac):
    if E6.MODE["arm"] != "none":
        drng = np.random.Generator(np.random.PCG64(S.seed(E6.MODE["aid"], "damage|%d" % E6.MODE["gen"], 0)))
        E6.F = E6.MODE.get("f", 0.1)
        pop = E6.damage_pop(pop, drng, E6.MODE["arm"])
    E6.MODE["gen"] += 1
    return E6._orig_gen(pop, cfg, items, cross_ok, r, elite_frac)


W6.generation = generation_w


def job(j):
    aid, rate, arm, f, price = j["aid"], j["rate"], j["arm"], j["f"], j["price"]
    E6.MODE.update({"arm": arm, "aid": aid, "gen": 0, "f": f})
    cfg = L.load_cfg("cw01-e06", aid)
    cfg["ecology"]["recombination_rate"] = rate
    cfg["prices"]["per_structural_unit"] = price
    cfg["prices"]["per_live_register"] = price
    targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
    run = W6.evolve(cfg, "mixed_assortative", GENS, 96, S.seed, "%s|r%.2f|p%.3f" % (aid, rate, price), freq_first=F0, target=targets)
    h = run["history"]
    return {"aid": aid, "rate": rate, "arm": arm, "f": f, "price": price, "final160": h[159]["freq_TREE"], "final240": h[-1]["freq_TREE"],
            "coexist240": W6.coexisting(run), "extinct": run["extinction_generation"], "units_TREE": h[-1].get("structural_units_TREE"), "units_TAPE": h[-1].get("structural_units_TAPE"),
            "traj": [round(x["freq_TREE"], 4) for x in h]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-E06", "T-E07"], "claim_type": "economics-reversal",
                         "factors": {"price": PRICES, "damage": ("none",) + DAMAGE, "fraction": FRACS, "rate": RATES, "f0": F0, "ids": IDS, "generations": GENS},
                         "harness_check": "none == sham (fraction .1, price .01) on every trajectory",
                         "signature": "pruning = final240 TREE(tree-damaged) - final240 TREE(tape-damaged), paired by (id, rate, fraction); relabel/sign-flip band",
                         "decision": {"PRICE_MEDIATED_PRUNING": "signature above p95 at price .01 and inside band at price 0", "DAMAGE_EFFECT": "above p95 at both prices", "REVERSED": "below p05 at price 0", "UNRESOLVED": "otherwise"},
                         "also": "damage-vs-none effects per price and fraction; the rate window (signs of final240 - f0 at each rate) per price; coexistence at 240",
                         "material_rule": "the decision is not UNRESOLVED, or a damage-vs-none effect clears its band at either price, or the window signs differ between prices",
                         "continuation": ["price dose", "registers-only vs nodes-only damage", "non-heritable damage"]})
    jobs = []
    for a in IDS:
        for r in RATES:
            for p in PRICES:
                jobs.append({"aid": a, "rate": r, "arm": "none", "f": 0.1, "price": p})
                for d in DAMAGE:
                    for f in FRACS:
                        jobs.append({"aid": a, "rate": r, "arm": d, "f": f, "price": p})
            jobs.append({"aid": a, "rate": r, "arm": "sham", "f": 0.1, "price": 0.01})
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(job, jobs, chunksize=3))
    by = {(x["aid"], x["rate"], x["arm"], x["f"], x["price"]): x for x in rows}
    sham_ok = all(by[(a, r, "none", 0.1, 0.01)]["traj"] == by[(a, r, "sham", 0.1, 0.01)]["traj"] for a in IDS for r in RATES)
    sig, eff, window, coex = {}, {}, {}, {}
    for p in PRICES:
        diffs = [by[(a, r, "tree", f, p)]["final240"] - by[(a, r, "tape", f, p)]["final240"] for a in IDS for r in RATES for f in FRACS]
        d = np.array(diffs)
        rng = np.random.Generator(np.random.PCG64(0))
        null = np.array([(d * rng.choice([-1.0, 1.0], size=len(d))).mean() for _ in range(5000)])
        sig["%.3f" % p] = {"mean": float(d.mean()), "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)), "n": len(d), "above_p95": bool(d.mean() > np.percentile(null, 95)), "below_p05": bool(d.mean() < np.percentile(null, 5))}
        eff["%.3f" % p] = {}
        for dmg in DAMAGE:
            for f in FRACS:
                dd = np.array([by[(a, r, dmg, f, p)]["final240"] - by[(a, r, "none", 0.1, p)]["final240"] for a in IDS for r in RATES])
                null = np.array([(dd * rng.choice([-1.0, 1.0], size=len(dd))).mean() for _ in range(3000)])
                eff["%.3f" % p]["%s|f%.2f" % (dmg, f)] = {"mean": float(dd.mean()), "above_p95": bool(dd.mean() > np.percentile(null, 95)), "below_p05": bool(dd.mean() < np.percentile(null, 5)),
                                                          "units_TREE": float(np.mean([by[(a, r, dmg, f, p)]["units_TREE"] or 0 for a in IDS for r in RATES])), "units_TAPE": float(np.mean([by[(a, r, dmg, f, p)]["units_TAPE"] or 0 for a in IDS for r in RATES]))}
        window["%.3f" % p] = {"%.2f" % r: int(np.sign(np.mean([by[(a, r, "none", 0.1, p)]["final240"] for a in IDS]) - F0)) for r in RATES}
        window["%.3f" % p]["finals"] = {"%.2f" % r: round(float(np.mean([by[(a, r, "none", 0.1, p)]["final240"] for a in IDS])), 3) for r in RATES}
        coex["%.3f" % p] = {dmg: sum(x["coexist240"] for x in rows if x["price"] == p and x["arm"] == dmg) for dmg in ("none",) + DAMAGE}
    s1, s0 = sig["0.010"], sig["0.000"]
    if s1["above_p95"] and not (s0["above_p95"] or s0["below_p05"]):
        decision = "PRICE_MEDIATED_PRUNING"
    elif s1["above_p95"] and s0["above_p95"]:
        decision = "DAMAGE_EFFECT"
    elif s0["below_p05"]:
        decision = "REVERSED"
    else:
        decision = "UNRESOLVED"
    material = bool(sham_ok and (decision != "UNRESOLVED" or any(v["above_p95"] or v["below_p05"] for p in eff.values() for v in p.values()) or window["0.010"] != window["0.000"]))
    out = {"perturbation_id": PID, "parent": TID, "harness_none_equals_sham": sham_ok, "decision": decision if sham_ok else "INVALID_HARNESS", "pruning_signature": sig, "damage_minus_none": eff,
           "window_signs_none": window, "coexist240": coex, "n_runs": len(rows), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "runs.json").write_text(json.dumps(rows, ensure_ascii=True, default=L.js), encoding="utf-8")
    L.append_evidence(TID, PID, "price x damage (none==sham %s): decision %s; pruning signature tree-tape at price .01 %s / 0 %s; damage-none %s; window signs (none) %s; coexist240 %s"
                      % (sham_ok, out["decision"], (round(s1["mean"], 3), s1["above_p95"]), (round(s0["mean"], 3), s0["above_p95"], s0["below_p05"]),
                         {p: {k: (round(v["mean"], 3), v["above_p95"], v["below_p05"]) for k, v in e.items()} for p, e in eff.items()}, window, coex), material, detail={"decision": out["decision"], "signature": sig, "effects": eff, "window": window})
    for tid in ("T-E06", "T-E07"):
        L.append_evidence(tid, PID, "cross: damage under price 0 reads %s (signature %s at .01, %s at 0)" % (out["decision"], round(s1["mean"], 3), round(s0["mean"], 3)), material)
    print("DONE material=%s decision=%s sham=%s (%.0f s) sig %s | window %s | coex %s" % (material, out["decision"], sham_ok, time.time() - t0, {k: round(v["mean"], 3) for k, v in sig.items()}, window, coex))


if __name__ == "__main__":
    main()
