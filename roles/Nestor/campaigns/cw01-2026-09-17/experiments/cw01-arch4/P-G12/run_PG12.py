"""P-G12 (serendipity, T-X18 in Proteus; requires P-G01): DELETERIOUS LOAD in the P-F06 populations (select
and ndrift, seeds 1-2, regenerated) at G20 / G40 / G60: absolute reward change under scattered deletion
f .05 (2 draws) for every individual; share whose reward RISES; elite (top 5 by reward) vs population.
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
import scatter as SC           # noqa: E402
import evolver as EV           # noqa: E402
import gate                    # noqa: E402
A, L = CM.A, CM.L

PID, TID, F = "P-G12", "T-X18", 0.05
ARCHS = (19, 39, 59)


def evo_job(j):
    r = EV.run(j["arm"], j["seed"], j["init"], archive_gens=ARCHS, label="nestor.pf06")
    return {"arm": r["arm"], "seed": r["seed"], "archive": r["archive"]}


def load_job(j):
    eps = A.episodes(EV.ENV)
    out = []
    for i, x in enumerate(j["pop"]):
        pm = A.canonical(x["m"])
        n = CM.n_instr(pm)
        r0 = A.evaluate(pm, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
        drs = []
        for d in (1, 2):
            key = ("%s-%d-%d-%d" % (j["arm"], j["seed"], j["gen"], i), "load", F, d)
            c = SC.apply(pm, SC.mask(n, F, key), "delete", key)
            drs.append(A.evaluate(c, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"] - r0)
        out.append({"arm": j["arm"], "seed": j["seed"], "gen": j["gen"], "i": i, "r0": r0, "n_instr": n, "dreward": float(np.mean(drs)), "rises": bool(np.mean(drs) > 0), "any_rise": bool(max(drs) > 0)})
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-ARCH4/M1", "T-X15"], "requires": ["P-G01"], "scope": CM.SCOPE, "claim_type": "serendipity-cross",
                         "populations": "P-F06 select / ndrift seeds 1-2 regenerated (label nestor.pf06), archives G20/40/60", "ruler": SC.PROVENANCE, "f": F, "draws": 2,
                         "readouts": "per arm x generation: mean absolute reward change, share of individuals whose reward rises, elite (top 5 by reward) vs population; load vs generation",
                         "reading": "LOAD_PRESENT if the share rising exceeds the sham expectation (a rise requires the deletion to remove a harmful instruction: share > 0 with Wilson lower bound > .05) in the population; ELITE_LOADED if the elite also rises in >= 1/3 of cases; else NO_LOAD",
                         "material_rule": "LOAD_PRESENT or ELITE_LOADED", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    gate.require_qualified(HERE, PID, TID, ph)
    init, _ = EV.init_population()
    with A.pool(4) as ex:
        runs = list(ex.map(evo_job, [{"arm": arm, "seed": s, "init": init} for arm in ("select", "ndrift") for s in (1, 2)]))
    jobs = [{"arm": r["arm"], "seed": r["seed"], "gen": g + 1, "pop": pop} for r in runs for g, pop in r["archive"].items()]
    with A.pool(8) as ex:
        rows = [x for rs in ex.map(load_job, jobs) for x in rs]

    def wilson(k, n, z=1.96):
        if n == 0:
            return (0.0, 0.0)
        p = k / n
        den = 1 + z * z / n
        c = (p + z * z / (2 * n)) / den
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        return (float(c - h), float(c + h))
    table = {}
    for arm in ("select", "ndrift"):
        for g in (20, 40, 60):
            rs = [r for r in rows if r["arm"] == arm and r["gen"] == g]
            elite = sorted(rs, key=lambda r: -r["r0"])[:10]
            table["%s|G%d" % (arm, g)] = {"n": len(rs), "mean_dreward": float(np.mean([r["dreward"] for r in rs])), "share_rises": float(np.mean([r["rises"] for r in rs])), "wilson": wilson(sum(r["rises"] for r in rs), len(rs)),
                                          "share_any_rise": float(np.mean([r["any_rise"] for r in rs])), "elite_share_rises": float(np.mean([r["rises"] for r in elite])), "elite_mean_dreward": float(np.mean([r["dreward"] for r in elite])),
                                          "mean_r0": float(np.mean([r["r0"] for r in rs])), "mean_len": float(np.mean([r["n_instr"] for r in rs]))}
    present = any(v["wilson"][0] > 0.05 for v in table.values())
    elite = any(v["elite_share_rises"] >= 1 / 3 for v in table.values())
    reading = "ELITE_LOADED" if elite else "LOAD_PRESENT" if present else "NO_LOAD"
    material = bool(present or elite)
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "deleterious load in Proteus (scattered f .05): reading %s; %s" % (reading, {k: (round(v["mean_dreward"], 4), round(v["share_rises"], 3), round(v["elite_share_rises"], 2), round(v["mean_r0"], 3), round(v["mean_len"], 1)) for k, v in table.items()}), material, detail=table)
    L.append_evidence("T-ARCH4/M1", PID, "cross: share of evolved programs whose reward RISES under blind scattered deletion: %s" % {k: round(v["share_rises"], 3) for k, v in table.items()}, material)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, reading, time.time() - t0, {k: (round(v["mean_dreward"], 4), round(v["share_rises"], 3)) for k, v in table.items()}))


if __name__ == "__main__":
    main()
