"""B19 -- is generation 0's CONFIGURATION a hidden gate on keyed memory? (Phase 2-B Beta)

2026-10-07 ~07:00Z correction: an 11-instruction v0 program that stores each value at tape[tag] and reads tape[tag]
on ASK solves jittered L4 and W2_K2 at 1.000 and K=3/4/6 at ~1.000 -- GENERAL keyed memory with no loop, no slots,
no composition (the B05 "GENERAL needs a loop" assumption was wrong; "composition wall" names the wrong thing). It
needs a large persistent tape: with tape_words 256 it scores .73-.92 (tags land in the read-only code region),
with 4096 ~1.0. FOUNDRY_C2 (every campaign's gen 0) draws tape_words from {16..256} and persist uniformly over
{none, regs, tape, all}; tape_words reaches 4096 only by config_perturbation steps.

Arms (jittered W2_K2 = B08J L6, CMP3 search N=200, E=16, E0, G=300, 4 seeds each, 2 procs, light rule):
  C2    FOUNDRY_C2 unchanged (= B08J L6 replication; B08J: 0/8)
  BIG   FOUNDRY_C2 with tape_words_choices [4096] and persist_weights [0, 0, 1, 1] (tape or all)
Readout: solved (held-out >= .90); elite mechanism by B11-style jitter check and executed LD/ST count.
PREDICTION (before running): BIG >= 1/4; C2 0/4. If BIG = 0/4, configuration is not the gate and the coupled
write/read pair (ST[tag] + LD[tag] + reading the tag on both paths, ~3 silent edits) is.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, REGIMES, TARGET
from archaeon.beta.b08j_jittered_ladder import jittered
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.wse.evolve import Evolution, evaluate

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
FOUNDRY_BIG = dict(FOUNDRY_C2, tape_words_choices=[4096], persist_weights=[0, 0, 1, 1])


def cell(job):
    B.eps_for = jittered
    arm, seed, G_ = job["arm"], job["seed"], job["G"]
    fm = FOUNDRY_BIG if arm == "BIG" else FOUNDRY_C2
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b19", foundry=fm)
    ho = B.eps_for("L6_w2k2", "heldout", seed, 48)
    solved, best = None, []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=B.eps_for("L6_w2k2", "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= SOLVED and evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"] >= SOLVED:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    g_ = elite["genome"]
    return {"arm": arm, "seed": seed, "solved_gen": solved, "max_train": max(best),
            "final_heldout": round(evaluate(elite, ho, rng_seed=7)["reward"], 4), "elite_persist": elite["persist"],
            "elite_tape": elite["tape_words"], "elite_ST": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == 6),
            "elite_LD": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == 5), "elite_manifest": elite}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 2) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 1901 + s, "G": G_}): (a, s) for s in range(4) for a in ("BIG", "C2")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, s = futs[f]; r = {"arm": a, "seed": 1901 + s, "solved_gen": None, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B19_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {a: sum(r["arm"] == a and r["solved_gen"] is not None for r in rows) for a in ("BIG", "C2")}
    print(json.dumps(summ), flush=True)
    (OUT / "B19_result.json").write_text(json.dumps({"probe": "B19", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
