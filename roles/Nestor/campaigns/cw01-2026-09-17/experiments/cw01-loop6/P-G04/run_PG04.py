"""P-G04 [T-X16 x T-X18 x T-E06; bounded]: PRICE DOSE x damage x LOAD over generations. Price {0, .0025, .005,
.01, .02} x damage {none, tape, tree, both} (f .1, separate rng) x rate {.6, 1.0} x 3 ids, 160
generations; per generation and label: structural units, a deleterious-load probe (16 sampled bodies:
absolute score change under deletion of one unit on that generation's items), raw score, share,
lineages; final coexistence. Absolute ruler throughout.
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
sys.path.insert(0, str(HERE.parents[1] / "cw01-loop4" / "P-F09"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import run_PE06 as E6          # noqa: E402
import run_PF09 as F9          # noqa: E402

W6 = E6.W6
PID, TID = "P-G04", "T-X16"
PRICES, DAMAGE, RATES, IDS, GENS = (0.0, 0.0025, 0.005, 0.01, 0.02), ("none", "tape", "tree", "both"), (0.6, 1.0), ["cw01-loop6-PG04-%d" % i for i in range(3)], 160
PROBE = {"log": [], "cfg": None}


def generation_w(pop, cfg, items, cross_ok, r, elite_frac):
    g = E6.MODE["gen"]
    prng = np.random.Generator(np.random.PCG64(S.seed(E6.MODE["aid"], "loadprobe|%d" % g, 0)))
    idx = prng.choice(len(pop), min(16, len(pop)), replace=False)
    rec = {"gen": g}
    for lab in ("TREE", "TAPE"):
        ds = []
        for i in idx:
            gnm = pop[int(i)]
            if gnm["label"] != lab:
                continue
            s0 = W6.evaluate(gnm, cfg, items)["score"]
            rr = np.random.Generator(np.random.PCG64(S.seed(E6.MODE["aid"], "loaddmg|%d|%d" % (g, int(i)), 0)))
            dv = dict(gnm, body=(F9.damage_tape(gnm["body"], 1, rr) if gnm["substrate"] == "TAPE" else F9.damage_tree(gnm["body"], 1, rr)))
            ds.append(W6.evaluate(dv, cfg, items)["score"] - s0)
        rec["load_" + lab] = float(np.mean(ds)) if ds else None
        rec["rise_" + lab] = float(np.mean([d > 0 for d in ds])) if ds else None
    PROBE["log"].append(rec)
    if E6.MODE["arm"] != "none":
        drng = np.random.Generator(np.random.PCG64(S.seed(E6.MODE["aid"], "damage|%d" % g, 0)))
        E6.F = 0.1
        pop = E6.damage_pop(pop, drng, E6.MODE["arm"])
    E6.MODE["gen"] += 1
    return E6._orig_gen(pop, cfg, items, cross_ok, r, elite_frac)


W6.generation = generation_w


def job(j):
    aid, price, arm, rate = j["aid"], j["price"], j["arm"], j["rate"]
    E6.MODE.update({"arm": arm, "aid": aid, "gen": 0})
    PROBE["log"] = []
    cfg = L.load_cfg("cw01-e06", aid)
    cfg["ecology"]["recombination_rate"] = rate
    cfg["prices"]["per_structural_unit"] = price
    cfg["prices"]["per_live_register"] = price
    targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
    run = W6.evolve(cfg, "mixed_assortative", GENS, 96, S.seed, "%s|r%.1f|p%.4f" % (aid, rate, price), freq_first=0.5, target=targets)
    h = run["history"]
    keep = lambda k: [round(float(x.get(k, 0.0)), 4) for x in h]   # noqa: E731
    return {"aid": aid, "price": price, "arm": arm, "rate": rate, "final": h[-1]["freq_TREE"], "coexist": W6.coexisting(run), "units_TREE": keep("structural_units_TREE"), "units_TAPE": keep("structural_units_TAPE"),
            "score_TREE": keep("score_TREE"), "score_TAPE": keep("score_TAPE"), "freq_TREE": keep("freq_TREE"), "lineages": [x.get("lineages_TREE", 0) + x.get("lineages_TAPE", 0) for x in h],
            "load": PROBE["log"]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X18", "T-E06"], "claim_type": "parameterized-dose", "factors": {"price": PRICES, "damage": DAMAGE, "rate": RATES, "ids": IDS, "generations": GENS, "f0": 0.5, "f": 0.1},
                         "ruler": {"family": "blind structural damage (probe)", "geometry": "one unit", "sampling_law": "uniform over units", "normalisation": "ABSOLUTE score change on the generation's items", "denominator": "16 sampled bodies per generation", "price_assumptions": "the price is the factor", "viability_floor": "none", "alters_baseline_function": "no (probe on copies)", "qualification": "absolute change (D086)"},
                         "readouts": ["load (mean dscore, share rising) by label x price x generation band (early 0-40, mid 40-100, late 100-160)", "structural units by label x price", "pruning signature (tree-damaged minus tape-damaged final TREE) by price", "coexistence by price"],
                         "reading": "load TRACKS_PRICE if the late-band share rising is monotone in price with a range >= .2; GROWS_WITH_GENERATIONS if late - early >= .15 at every price; representation-dependent if TREE and TAPE differ by >= .2; the pruning signature's price dose named from its sign per price",
                         "material_rule": "any of the three load readings, or the signature changes sign inside the dose", "bounded": "runs once; no follow-up this cycle"})
    jobs = [{"aid": a, "price": p, "arm": d, "rate": r} for a in IDS for p in PRICES for d in DAMAGE for r in RATES]
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(job, jobs, chunksize=3))
    by = {(x["aid"], x["price"], x["arm"], x["rate"]): x for x in rows}
    bands = {"early": (0, 40), "mid": (40, 100), "late": (100, 160)}
    load = {}
    for p in PRICES:
        load["%.4f" % p] = {}
        for lab in ("TREE", "TAPE"):
            for bn, (a, b) in bands.items():
                vals = [x["rise_" + lab] for r in rows if r["price"] == p and r["arm"] == "none" for x in r["load"][a:b] if x.get("rise_" + lab) is not None]
                dsc = [x["load_" + lab] for r in rows if r["price"] == p and r["arm"] == "none" for x in r["load"][a:b] if x.get("load_" + lab) is not None]
                load["%.4f" % p]["%s|%s" % (lab, bn)] = {"rise": float(np.mean(vals)) if vals else None, "dscore": float(np.mean(dsc)) if dsc else None, "n": len(vals)}
        load["%.4f" % p]["units_final"] = {lab: float(np.mean([r["units_" + lab][-1] for r in rows if r["price"] == p and r["arm"] == "none"])) for lab in ("TREE", "TAPE")}
        sig = [by[(a, p, "tree", rt)]["final"] - by[(a, p, "tape", rt)]["final"] for a in IDS for rt in RATES]
        load["%.4f" % p]["signature"] = float(np.mean(sig))
        load["%.4f" % p]["coexist"] = {d: sum(x["coexist"] for x in rows if x["price"] == p and x["arm"] == d) for d in DAMAGE}
        load["%.4f" % p]["final_TREE_none"] = float(np.mean([r["final"] for r in rows if r["price"] == p and r["arm"] == "none"]))
    late = {p: np.nanmean([load[p]["TREE|late"]["rise"] or np.nan, load[p]["TAPE|late"]["rise"] or np.nan]) for p in load}
    vals = [late[p] for p in sorted(late)]
    tracks = bool(max(vals) - min(vals) >= 0.2 and (all(np.diff(vals) >= -0.02) or all(np.diff(vals) <= 0.02)))
    grows = all((load[p]["TREE|late"]["rise"] or 0) - (load[p]["TREE|early"]["rise"] or 0) >= 0.15 or (load[p]["TAPE|late"]["rise"] or 0) - (load[p]["TAPE|early"]["rise"] or 0) >= 0.15 for p in load)
    repdep = any(abs((load[p]["TREE|late"]["rise"] or 0) - (load[p]["TAPE|late"]["rise"] or 0)) >= 0.2 for p in load)
    signs = [np.sign(load[p]["signature"]) for p in sorted(load)]
    material = bool(tracks or grows or repdep or len(set(signs)) > 1)
    out = {"perturbation_id": PID, "parent": TID, "readings": {"tracks_price": tracks, "grows_with_generations": grows, "representation_dependent": repdep, "signature_by_price": {p: round(load[p]["signature"], 3) for p in load}}, "load": load, "n_runs": len(rows), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "runs.json").write_text(json.dumps(rows, ensure_ascii=True, default=L.js), encoding="utf-8")
    L.append_evidence(TID, PID, "price dose x damage x load: readings %s; late-band share rising by price %s; units final %s; coexist %s" % (out["readings"], {p: (round(v["TREE|late"]["rise"], 2) if v["TREE|late"]["rise"] is not None else None, round(v["TAPE|late"]["rise"], 2) if v["TAPE|late"]["rise"] is not None else None) for p, v in load.items()}, {p: v["units_final"] for p, v in load.items()}, {p: v["coexist"] for p, v in load.items()}), material, detail=out["readings"])
    L.append_evidence("T-X18", PID, "cross: load vs price and generation band: %s" % {p: {k: round(v[k]["rise"], 2) for k in ("TREE|early", "TREE|late", "TAPE|early", "TAPE|late") if v[k]["rise"] is not None} for p, v in load.items()}, material)
    print("DONE material=%s %s (%.0f s)" % (material, out["readings"], time.time() - t0))


if __name__ == "__main__":
    main()
