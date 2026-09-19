"""P-G10 (anti-gravity, T-X16): PRICE DECOMPOSITION - {none, units only, registers only, both} x damage
{none, tape, tree} (f .1, separate rng) x rate .6 x 3 ids, 160 generations: the pruning signature and
TREE's dominance under each price component. TREE pays per node and nothing per register; TAPE pays both.
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
import run_PE06 as E6          # noqa: E402

W6 = E6.W6
PID, TID = "P-G10", "T-X16"
PRICES = {"none": (0.0, 0.0), "units_only": (0.01, 0.0), "registers_only": (0.0, 0.01), "both": (0.01, 0.01)}
DAMAGE, RATE, IDS, GENS, F0 = ("none", "tape", "tree"), 0.6, ["cw01-loop5-PG10-%d" % i for i in range(3)], 160, 0.1


def generation_w(pop, cfg, items, cross_ok, r, elite_frac):
    if E6.MODE["arm"] != "none":
        drng = np.random.Generator(np.random.PCG64(S.seed(E6.MODE["aid"], "damage|%d" % E6.MODE["gen"], 0)))
        E6.F = 0.1
        pop = E6.damage_pop(pop, drng, E6.MODE["arm"])
    E6.MODE["gen"] += 1
    return E6._orig_gen(pop, cfg, items, cross_ok, r, elite_frac)


W6.generation = generation_w


def job(j):
    aid, price, arm = j["aid"], j["price"], j["arm"]
    E6.MODE.update({"arm": arm, "aid": aid, "gen": 0})
    cfg = L.load_cfg("cw01-e06", aid)
    cfg["ecology"]["recombination_rate"] = RATE
    cfg["prices"]["per_structural_unit"], cfg["prices"]["per_live_register"] = PRICES[price]
    targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
    run = W6.evolve(cfg, "mixed_assortative", GENS, 96, S.seed, "%s|%s" % (aid, price), freq_first=F0, target=targets)
    h = run["history"]
    return {"aid": aid, "price": price, "arm": arm, "final": h[-1]["freq_TREE"], "coexist": W6.coexisting(run), "units_TREE": h[-1].get("structural_units_TREE"), "units_TAPE": h[-1].get("structural_units_TAPE"), "regs_TAPE": h[-1].get("live_registers_TAPE"),
            "traj": [round(x["freq_TREE"], 4) for x in h]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "economics-deformation", "prices": PRICES, "damage": DAMAGE, "rate": RATE, "ids": IDS, "generations": GENS, "f0": F0,
                         "price_assumptions": "per_item_attempted unchanged (.002); the structural and register components are varied", "readouts": "pruning signature (tree-damaged minus tape-damaged final TREE) and TREE dominance (none arm final TREE from .1) per price component",
                         "reading": "the component whose presence flips the signature's sign is named; REGISTER_ACCOUNTING if registers_only carries the .01 sign and units_only does not; STRUCTURAL_PRICE if units_only carries it; BOTH_NEEDED; NEITHER",
                         "material_rule": "the signature or TREE dominance differs between components by >= .2 (3 ids)", "continuation": ["register price dose"]})
    jobs = [{"aid": a, "price": p, "arm": d} for a in IDS for p in PRICES for d in DAMAGE]
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    by = {(x["aid"], x["price"], x["arm"]): x for x in rows}
    table = {}
    for p in PRICES:
        sig = [by[(a, p, "tree")]["final"] - by[(a, p, "tape")]["final"] for a in IDS]
        table[p] = {"signature_mean": float(np.mean(sig)), "signature_per_id": [round(s, 3) for s in sig], "tree_dominance_none": float(np.mean([by[(a, p, "none")]["final"] for a in IDS])),
                    "tape_damage_effect": float(np.mean([by[(a, p, "tape")]["final"] - by[(a, p, "none")]["final"] for a in IDS])), "tree_damage_effect": float(np.mean([by[(a, p, "tree")]["final"] - by[(a, p, "none")]["final"] for a in IDS])),
                    "coexist": sum(x["coexist"] for x in rows if x["price"] == p), "units": {d: (round(float(np.mean([by[(a, p, d)]["units_TREE"] or 0 for a in IDS])), 1), round(float(np.mean([by[(a, p, d)]["units_TAPE"] or 0 for a in IDS])), 1)) for d in DAMAGE}}
    s = {p: table[p]["signature_mean"] for p in PRICES}
    pos = {p: s[p] > 0.1 for p in PRICES}
    if pos["registers_only"] and not pos["units_only"]:
        reading = "REGISTER_ACCOUNTING"
    elif pos["units_only"] and not pos["registers_only"]:
        reading = "STRUCTURAL_PRICE"
    elif pos["both"] and not pos["units_only"] and not pos["registers_only"]:
        reading = "BOTH_NEEDED"
    elif pos["units_only"] and pos["registers_only"]:
        reading = "EITHER_COMPONENT"
    else:
        reading = "NEITHER"
    spread = max(s.values()) - min(s.values())
    dom = {p: table[p]["tree_dominance_none"] for p in PRICES}
    material = bool(spread >= 0.2 or max(dom.values()) - min(dom.values()) >= 0.2)
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "table": table, "signature_spread": spread, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "runs.json").write_text(json.dumps(rows, ensure_ascii=True, default=L.js), encoding="utf-8")
    L.append_evidence(TID, PID, "price decomposition at rate .6: reading %s; signature by component %s; TREE dominance %s; tape/tree damage effects %s" % (reading, {p: round(v, 3) for p, v in s.items()}, {p: round(v, 3) for p, v in dom.items()}, {p: (round(table[p]["tape_damage_effect"], 3), round(table[p]["tree_damage_effect"], 3)) for p in PRICES}), material, detail={"table": table})
    L.append_evidence("T-E06", PID, "cross: which price component sets TREE's dominance: %s" % {p: round(v, 3) for p, v in dom.items()}, material)
    print("DONE material=%s reading=%s (%.0f s) sig %s dom %s" % (material, reading, time.time() - t0, s, dom))


if __name__ == "__main__":
    main()
