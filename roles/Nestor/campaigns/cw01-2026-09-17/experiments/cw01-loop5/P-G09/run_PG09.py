"""P-G09 (serendipity / anti-gravity; T-X18 x T-X01 x T-E06): IS DELETERIOUS LOAD AN ORGANISM PROPERTY OR A
POPULATION ARTEFACT? e06 solo arms (solo_tape / solo_tree), rates .5 / 1.0, 3 ids, sharing ON and OFF,
populations at generations 0 / 20 / 40 / 80 (deterministic prefixes): absolute score change under
ONE-unit blind deletion (4 draws, fixed probe items) for the ELITE (top 5 percent by fitness), the
population and random members.
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
sys.path.insert(0, str(HERE.parents[1] / "cw01-loop4" / "P-F09"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import run_PF09 as F9          # noqa: E402  (damage_tape / damage_tree / W6)

W6 = F9.W6
PID, TID = "P-G09", "T-X18"
IDS, RATES, GENS = ["cw01-loop5-PG09-%d" % i for i in range(3)], (0.5, 1.0), (0, 20, 40, 80)


def job(j):
    aid, rate, sharing = j["aid"], j["rate"], j["sharing"]
    cfg = L.load_cfg("cw01-e06", aid)
    cfg["ecology"]["recombination_rate"] = rate
    cfg["sharing"]["enabled"] = sharing
    targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
    irng = np.random.Generator(np.random.PCG64(S.seed(aid, "probe-items", 0)))
    items = W6.make_items(cfg, irng, targets)
    out = []
    for arm, sub in (("solo_tape", "TAPE"), ("solo_tree", "TREE")):
        for g in GENS:
            if g == 0:
                r = np.random.Generator(np.random.PCG64(S.seed(aid, "evo|" + arm, 0)))
                pop = W6.initial_population(cfg, arm, r, 96, 1.0)
            else:
                pop = W6.evolve(cfg, arm, g, 96, S.seed, "%s|%s|r%.1f|sh%d" % (aid, arm, rate, int(sharing)), freq_first=1.0, target=targets)["final_pop"]
            ev = W6.evaluate_population(pop, cfg, items)
            fit = np.array([e["fitness"] for e in ev])
            order = np.argsort(-fit)
            elite = set(int(i) for i in order[:5])
            prng = np.random.Generator(np.random.PCG64(S.seed(aid, "probe|%s|%d|%d" % (arm, g, int(sharing)), 0)))
            sample = set(int(i) for i in prng.choice(len(pop), 24, replace=False)) | elite
            for i in sorted(sample):
                gnm = pop[i]
                s0 = W6.evaluate(gnm, cfg, items)["score"]
                ds = []
                for d in range(4):
                    r = np.random.Generator(np.random.PCG64(S.seed(aid, "dmg|%s|%d|%d|%d" % (arm, g, i, d), int(sharing))))
                    dv = dict(gnm, body=(F9.damage_tape(gnm["body"], 1, r) if sub == "TAPE" else F9.damage_tree(gnm["body"], 1, r)))
                    ds.append(W6.evaluate(dv, cfg, items)["score"] - s0)
                out.append({"aid": aid, "rate": rate, "sharing": sharing, "substrate": sub, "gen": g, "i": i, "elite": i in elite, "score0": s0, "fitness": float(fit[i]), "size": W6.structural_units(gnm),
                            "dscore": float(np.mean(ds)), "rises": bool(np.mean(ds) > 0)})
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X01", "T-E06"], "claim_type": "serendipity-cross", "ids": IDS, "rates": RATES, "generations": GENS, "sharing": [True, False],
                         "ruler": {"family": "blind structural damage", "geometry": "one unit (TAPE instruction / TREE internal-node contraction)", "sampling_law": "uniform over units", "normalisation": "ABSOLUTE score change on fixed probe items", "denominator": "4 draws", "price_assumptions": "score only (no price in the ruler)", "viability_floor": "none", "alters_baseline_function": "no", "qualification": "absolute change; no ratio (D086)"},
                         "readouts": "mean dscore and share rising for elite (top 5 by fitness) vs population sample, by substrate x generation x sharing",
                         "reading": "POPULATION_ARTEFACT if the population's share rising exceeds the elite's by >= .15 with the elite's share <= .2 in >= 3/4 generations > 0; ORGANISM_PROPERTY if the elite's share rising >= .3 in >= 2 generations; MIXED otherwise; NO_LOAD if shares <= .1 everywhere",
                         "material_rule": "the reading is not NO_LOAD, or sharing changes the share rising by >= .15", "continuation": ["load vs recombination rate", "price 0"]})
    jobs = [{"aid": a, "rate": r, "sharing": sh} for a in IDS for r in RATES for sh in (True, False)]
    with ProcessPoolExecutor(max_workers=6) as ex:
        rows = [x for rs in ex.map(job, jobs) for x in rs]
    table = {}
    for sub in ("TAPE", "TREE"):
        for sh in (True, False):
            for g in GENS:
                rs = [r for r in rows if r["substrate"] == sub and r["sharing"] == sh and r["gen"] == g]
                el = [r for r in rs if r["elite"]]
                po = [r for r in rs if not r["elite"]]
                table["%s|sh%d|G%d" % (sub, int(sh), g)] = {"n": len(rs), "pop_share_rises": float(np.mean([r["rises"] for r in po])) if po else None, "pop_mean_dscore": float(np.mean([r["dscore"] for r in po])) if po else None,
                                                             "elite_share_rises": float(np.mean([r["rises"] for r in el])) if el else None, "elite_mean_dscore": float(np.mean([r["dscore"] for r in el])) if el else None,
                                                             "mean_score0": float(np.mean([r["score0"] for r in rs])), "mean_size": float(np.mean([r["size"] for r in rs]))}
    later = [v for k, v in table.items() if not k.endswith("G0")]
    art = sum(1 for v in later if v["pop_share_rises"] is not None and v["elite_share_rises"] is not None and v["pop_share_rises"] - v["elite_share_rises"] >= 0.15 and v["elite_share_rises"] <= 0.2)
    org = sum(1 for v in later if v["elite_share_rises"] is not None and v["elite_share_rises"] >= 0.3)
    no_load = all((v["pop_share_rises"] or 0) <= 0.1 and (v["elite_share_rises"] or 0) <= 0.1 for v in later)
    reading = "NO_LOAD" if no_load else "ORGANISM_PROPERTY" if org >= 2 else "POPULATION_ARTEFACT" if art >= 3 else "MIXED"
    sh_eff = {sub: float(np.mean([table["%s|sh1|G%d" % (sub, g)]["pop_share_rises"] or 0 for g in GENS[1:]]) - np.mean([table["%s|sh0|G%d" % (sub, g)]["pop_share_rises"] or 0 for g in GENS[1:]])) for sub in ("TAPE", "TREE")}
    material = bool(reading != "NO_LOAD" or any(abs(v) >= 0.15 for v in sh_eff.values()))
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "table": table, "sharing_effect_on_pop_share": sh_eff, "counts": {"artefact_cells": art, "organism_cells": org, "later_cells": len(later)}, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=L.js), encoding="utf-8")
    L.append_evidence(TID, PID, "load: organism vs population: reading %s; %s; sharing effect %s" % (reading, {k: (round(v["pop_share_rises"], 2) if v["pop_share_rises"] is not None else None, round(v["elite_share_rises"], 2) if v["elite_share_rises"] is not None else None, round(v["mean_score0"], 3)) for k, v in table.items()}, {k: round(v, 3) for k, v in sh_eff.items()}), material, detail={"table": table, "sharing": sh_eff})
    L.append_evidence("T-X01", PID, "cross: elite vs population load %s" % reading, material)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, reading, time.time() - t0, {k: (v["pop_share_rises"], v["elite_share_rises"]) for k, v in table.items()}))


if __name__ == "__main__":
    main()
