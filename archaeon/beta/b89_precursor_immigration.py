"""B89 -- direct test of BASIN CAPTURE: keep the precursor basin occupied by IMMIGRATION. (follow-up to B88)

B87/B88: keyed reach from a precursor with d instructions missing (pooled d2 9/16, d4 4/16, d6 0/16, d8 0/8). Every
success comes in the first ~40 generations, and none appears late even at G=900. Reading: the population leaves the
precursor's basin for the shelf plateau, and the solver is then lost.
Intervention: after every reproduce(), replace 20 random NON-ELITE members with fresh copies of the precursor (10% of
N=200 each generation), so the basin never empties.
Arms (stock VM, CMP3 N=200 E=16 G=300, wide-jitter training, held-out 64 x 4, keyed >= .9), seeds 8901-8908:
  d4_IMM, d6_IMM
Controls: B87+B88 without immigration (d4 4/16, d6 0/16).
PREDICTION (committed before running), basin capture:
- d6_IMM keyed >= 2/8 (vs 0/16 without immigration);
- d4_IMM keyed >= 4/8 (vs 4/16).
If d6_IMM stays at 0/8, keeping the basin occupied does not help, and basin capture is not the mechanism.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET, manifest
from archaeon.beta.b55_chain_length import train_eps
from archaeon.beta.b86_keyed_distance import heldout
from archaeon.beta.b87_keyed_graded_distance import genome
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B89_immigration"
IMM = 20


def cell(job):
    d = job["arm"].split("_")[0]
    rec = G.organism_record(manifest(genome(d)), None, 0); rec["origins"] = ["gen0_" + d]
    pop = [copy.deepcopy(rec) for _ in range(200)]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b89", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "200 x " + d, "verified_common": True})
    rng = SplitMix64(seed_from("b89.imm", job["seed"])); first = None
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        if first is None and row["best_reward"] >= .9:
            first = g
        if g < job["G"] - 1:
            ev.reproduce()
            n = len(ev.pop); idx = list(range(ev.elitism, n))
            for _ in range(IMM):
                if not idx:
                    break
                k = idx.pop(rng.randbelow(len(idx)))
                im = copy.deepcopy(rec); im["origins"] = ["immigrant_" + d]; ev.pop[k] = im
    tops = [z[1]["manifest"] for z in ev.scored[:10]]
    scores = [heldout(m) for m in tops]
    return {"arm": job["arm"], "seed": job["seed"], "best_heldout": max(scores), "keyed": max(scores) >= .9, "first_train_ge_.9": first}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 8901 + i, "G": int(argv[0]) if argv else 300}): (a, i) for a in ("d4_IMM", "d6_IMM") for i in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 8901 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B89_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("keyed", False) for r in rows if r.get("arm") == a) for a in ("d4_IMM", "d6_IMM")}
    summ["pred"] = summ["d6_IMM"] >= 2 and summ["d4_IMM"] >= 4
    print(json.dumps(summ))
    (OUT / "B89_result.json").write_text(json.dumps({"probe": "B89", "imm_per_gen": IMM, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
