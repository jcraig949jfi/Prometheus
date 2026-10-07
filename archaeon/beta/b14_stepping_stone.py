"""B14 -- composition wall, stepping-stone test: does starting FROM a guard organism make two stored values reachable?

B08J: the write-once guard (L2) is reachable (5/8) and one overwrite store is reachable (L3 8/8) under timing jitter,
but two stored values (L4) are not (0/8). If the wall is "discovering both pieces at once", seeding L4 with organisms
that already HAVE the guard should cross it; if it persists, the composition step itself is the barrier.

Seeds: the B08J L2_first solvers that are genuine state (held-out L2 >= .90 under jitter: all B08J solves are under
jitter by construction). Each L4 cell's generation 0 = 4 copies of ONE such solver + the common CMP3 fill; arms:
  FROM_GUARD   4 copies of a B08J L2 solver
  FROM_STORE   4 copies of a B08J L3 solver (overwrite store, no guard)       -- control stepping stone
  FRESH        no seeding                                                     -- B08J replication
Jittered L4_order train and held-out, CMP3 search (N=200, E=16, E0, FOUNDRY_C2), G=300; one cell per seed organism
(up to 5 per arm) plus 5 FRESH cells.

PREDICTION (before running): FROM_GUARD >= 2/5; FROM_STORE <= 1/5; FRESH 0/5.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b08j_jittered_ladder import jittered
from archaeon.wse.evolve import Evolution, common_fill, evaluate

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90


def cell(job):
    B.eps_for = jittered
    seed, G_ = job["seed"], job["G"]
    if job.get("manifest"):
        init, prov = common_fill(CAMPAIGN_SEED, seed, 200, [job["manifest"]] * 4, tag=job["arm"], foundry=FOUNDRY_C2)
        ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b14", foundry=FOUNDRY_C2,
                       init_pop=init, gen0_provenance=prov)
    else:
        ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b14", foundry=FOUNDRY_C2)
    ho = B.eps_for("L4_order", "heldout", seed, 48)
    solved, best = None, []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=B.eps_for("L4_order", "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= SOLVED and evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"] >= SOLVED:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    seed_l4 = round(evaluate(job["manifest"], ho, rng_seed=7)["reward"], 4) if job.get("manifest") else None
    return {"arm": job["arm"], "seed": seed, "seed_organism_L4": seed_l4, "solved_gen": solved, "max_train": max(best),
            "final_heldout": round(evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"], 4),
            "elite_manifest": ev.scored[0][1]["manifest"]}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    j = json.loads((OUT / "B08J_result.json").read_text(encoding="utf-8"))
    guards = [r["elite_manifest"] for r in j["rows"] if r["rung"] == "L2_first" and r["solved_gen"] is not None][:5]
    stores = [r["elite_manifest"] for r in j["rows"] if r["rung"] == "L3_last" and r["solved_gen"] is not None][:5]
    jobs = ([{"arm": "FROM_GUARD", "seed": 1401 + i, "G": G_, "manifest": m} for i, m in enumerate(guards)] +
            [{"arm": "FROM_STORE", "seed": 1411 + i, "G": G_, "manifest": m} for i, m in enumerate(stores)] +
            [{"arm": "FRESH", "seed": 1421 + i, "G": G_} for i in range(5)])
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 15) as ex:
        for f in as_completed([ex.submit(cell, x) for x in jobs]):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("arm", "seed", "seed_organism_L4", "solved_gen", "final_heldout", "max_train")}), flush=True)
    summ = {a: {"n": sum(r["arm"] == a for r in rows), "solved": sum(r["arm"] == a and r["solved_gen"] is not None for r in rows)}
            for a in ("FROM_GUARD", "FROM_STORE", "FRESH")}
    print(json.dumps(summ), flush=True)
    (OUT / "B14_result.json").write_text(json.dumps({"probe": "B14", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
