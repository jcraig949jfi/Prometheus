"""B04 -- H-EROSION: does neutral drift erase the near-solver structure within ~10 generations? (Phase 2-B Beta)

B01b: 6/12 plateau neighbours of the W2_K2 solver were rescued by the CMP3 GA, all by generation 10, none later.
H-EROSION: the plateau lineage takes over fast, then neutral drift moves it away from the solver, closing the
reversal window. Test: replay the SAME 12 cells (same neighbours, same cell seeds, deterministic) and record per
generation the population's minimum and median instruction-level edit distance to the solver (Levenshtein over
4-word instructions), and the count of organisms at distance <= 1.

PREDICTION (before running): in the 6 unrescued cells the count at distance <= 1 falls to 0 by generation 15 in
>= 5/6; in rescued cells the summit appears while that count is > 0. Replay check: the summit generations match
B01b exactly (deterministic CRN), else the replay itself is the finding.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SOLVER, SUMMIT, TARGET
from archaeon.wse.evolve import Evolution, common_fill, evaluate
from archaeon.wse.worlds import episodes_for

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
SOL = [tuple(SOLVER[i:i + 4]) for i in range(0, len(SOLVER), 4)]


def ins(g):
    return [tuple(g[i:i + 4]) for i in range(0, len(g), 4)]


def lev(a, b, cap=12):
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, y in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y))
        prev = cur
    return prev[-1]


def cell(job):
    m = job["manifest"]
    init, prov = common_fill(CAMPAIGN_SEED, job["cell_seed"], 200, [m] * 4, tag="plateau", foundry=FOUNDRY_C2)
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["cell_seed"], N=200, E=16, branch="b01b",
                   foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov)
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", job["cell_seed"], 48)
    first, trace = None, []
    for g in range(60):
        dists = sorted(lev(ins(o["manifest"]["genome"]), SOL) for o in ev.pop)
        row = ev.evaluate_generation(last=(g == 59))
        trace.append({"g": g, "min": dists[0], "median": dists[len(dists) // 2], "n_le1": sum(d <= 1 for d in dists),
                      "n_le3": sum(d <= 3 for d in dists), "best": round(row["best_reward"], 4)})
        if first is None and row["best_reward"] >= SUMMIT and evaluate(ev.scored[0][1]["manifest"], eps, rng_seed=7)["reward"] >= SUMMIT:
            first = g
            break
        if g < 59:
            ev.reproduce()
    return {"i": job["i"], "first_summit_gen": first, "b01b_first_summit_gen": job["b01b_first"], "trace": trace}


def main(argv):
    OUT.mkdir(exist_ok=True)
    b = json.loads((OUT / "B01b_result.json").read_text(encoding="utf-8"))
    jobs = [{"i": r["i"], "manifest": b["neighbour_manifests"][r["i"]], "cell_seed": 201 + r["i"], "b01b_first": r["first_summit_gen"]}
            for r in b["rows"]]
    with ProcessPoolExecutor(max_workers=12) as ex:
        rows = list(ex.map(cell, jobs))
    for r in rows:
        t = r["trace"]
        zero_at = next((x["g"] for x in t if x["n_le1"] == 0), None)
        r["n_le1_zero_at"] = zero_at
        print(json.dumps({"i": r["i"], "summit": r["first_summit_gen"], "b01b": r["b01b_first_summit_gen"], "n_le1_zero_at": zero_at,
                          "n_le1": [x["n_le1"] for x in t[:16]], "min": [x["min"] for x in t[:16]]}), flush=True)
    (OUT / "B04_result.json").write_text(json.dumps({"probe": "B04", "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
