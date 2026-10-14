"""B86 -- is the KEYED-memory wall also a distance wall? (memory-law revision, keyed class; stock Proteus v0 VM)

Finding 3 (revised): update-on-condition (RESET) is unreachable from random gen 0 but reached 6/6 from a write-once
latch. The keyed class (two-slot recall, W2_K2) has never been reached on the stock VM from random or evolved starts
(B49-B53: 0/8). Here two hand precursors are seeded:
- equal fitness under 0-7 wide jitter, held-out 64 x 4;
- different DISTANCE to the hand keyed SOLVER (1.000).
Arms (stock VM, CMP3 N=200 E=16 G=300, wide-jitter training episodes (b55.train_eps), seeds 8601-8608):
  SLOT_A  gen 0 = 200 x SOLVER with slot B's two fill instructions NOPed (two edits from SOLVER); held-out .531
  SHELF   gen 0 = 200 x SHELF (one-value 'remember the last value' store; far from SOLVER);           held-out .535
Readout: the best genome's held-out W2_K2 reward (64 x 4, wide jitter). 'Keyed' = >= .9.
PREDICTION (committed before running), distance hypothesis: SLOT_A keyed in >= 4/8 AND SHELF keyed in <= 1/8.
If both are <= 1/8, a two-edit precursor with no fitness gradient does not help (the update result does not carry over
to keyed memory).
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SHELF, SOLVER, TARGET, manifest
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.beta.b55_chain_length import train_eps
from archaeon.wse import evolve as EV
from archaeon.wse.worlds import episodes_for

OUT = Path(__file__).resolve().parent / "results" / "B86_keyed_distance"
SLOT_A = list(SOLVER); SLOT_A[40:48] = [0] * 8
GENOMES = {"SLOT_A": SLOT_A, "SHELF": SHELF}


def heldout(m):
    return round(sum(EV.evaluate(m, wide(episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 7 + s, 64), ("b86", s)), rng_seed=7)["reward"] for s in range(4)) / 4, 4)


def cell(job):
    rec = G.organism_record(manifest(list(GENOMES[job["arm"]])), None, 0); rec["origins"] = ["gen0_" + job["arm"]]
    pop = [copy.deepcopy(rec) for _ in range(200)]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b86", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "200 x " + job["arm"], "verified_common": True})
    first = None
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        if first is None and row["best_reward"] >= .9:
            first = g
        if g < job["G"] - 1:
            ev.reproduce()
    tops = [z[1]["manifest"] for z in ev.scored[:10]]
    scores = [heldout(m) for m in tops]
    return {"arm": job["arm"], "seed": job["seed"], "best_heldout": max(scores), "keyed": max(scores) >= .9, "first_train_ge_.9": first}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        print(json.dumps({k: heldout(manifest(list(g))) for k, g in [("SOLVER", SOLVER)] + list(GENOMES.items())})); return 0
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 8601 + i, "G": int(argv[0]) if argv else 300}): (a, i) for a in GENOMES for i in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 8601 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B86_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("keyed", False) for r in rows if r.get("arm") == a) for a in GENOMES}
    print(json.dumps(summ))
    (OUT / "B86_result.json").write_text(json.dumps({"probe": "B86", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
