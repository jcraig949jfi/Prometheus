"""B12 -- LONG campaign: is the W2_K2 wall just time and population size? (Phase 2-B Beta, long-scale lane)

Every W2_K2 null so far (CMP1-3 0/60, B03 0/72, B07 0/36, B09/B10) used N=200 and G <= 400. B12 removes that excuse
at modest cost: BASE search (grammar v0.4, CMP3 evaluator, E0, FOUNDRY_C2), N=500, E=16, G=3000, 6 seeds. Each cell
appends a progress row every 100 generations to results/B12_progress.jsonl (best train, held-out of the elite,
jitter held-out of the elite = genuine memory vs delay line, genome length) so a long run is forensically
recoverable mid-flight.

PREDICTION (before running): 0/6 summits; the elite stays a one-slot memory (plain ~.55, jitter ~.55) after g ~200;
if any summit appears, its first-summit generation is > 1000 (a rare-event waiting time, not a ramp).
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SUMMIT, TARGET
from archaeon.beta.b08b_delay_line_check import jitter
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import episodes_for

OUT = Path(__file__).resolve().parent / "results"
PROG = OUT / "B12_progress.jsonl"


def cell(job):
    seed, G_, N = job["seed"], job["G"], job["N"]
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=16, branch="b12", foundry=FOUNDRY_C2)
    ho = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    hoj = jitter(ho, ("b12", seed))
    first = None
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        elite = ev.scored[0][1]["manifest"]
        hit = row["best_reward"] >= SUMMIT and evaluate(elite, ho, rng_seed=7)["reward"] >= SUMMIT
        if hit and first is None:
            first = g
        if g % 100 == 0 or g == G_ - 1 or hit:
            rec = {"seed": seed, "g": g, "best_train": round(row["best_reward"], 4),
                   "elite_heldout": round(evaluate(elite, ho, rng_seed=7)["reward"], 4),
                   "elite_jitter": round(evaluate(elite, hoj, rng_seed=7)["reward"], 4),
                   "elite_instr": len(elite["genome"]) // 4, "elite_persist": elite["persist"], "elite_n_regs": elite["n_regs"],
                   "first_summit_gen": first, "wall_s": round(time.time() - t0, 1)}
            with open(PROG, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
        if first is not None:
            break
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    return {"seed": seed, "N": N, "G": G_, "first_summit_gen": first, "elite_manifest": elite, "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 3000
    N = int(argv[1]) if len(argv) > 1 else 500
    workers = int(argv[2]) if len(argv) > 2 else 6
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for f in as_completed([ex.submit(cell, {"seed": s, "G": G_, "N": N}) for s in range(1201, 1207)]):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("seed", "first_summit_gen", "wall_s")}), flush=True)
    (OUT / "B12_result.json").write_text(json.dumps({"probe": "B12", "G": G_, "N": N, "rows": rows,
                                                      "summits": sum(r["first_summit_gen"] is not None for r in rows)}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
