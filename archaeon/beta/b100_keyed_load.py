"""B100 -- does lowering the MUTATION LOAD move the keyed d6 wall? (B99 cross-lane hypothesis)

B99: with a fraction c of offspring cloned, seeded signallers sweep instead of going extinct (error threshold). The
keyed precursor with 6 instructions missing (d6) has never been reached: 0/32 across G=300, G=900, immigration, and
immigration + G=900.
Hypothesis: partial keyed structures are broken faster than they are selected.
Counter-pressure: cloning ALSO cuts exploration (fewer mutants per generation), so the outcome is genuinely open.
Arms: d6 precursor, B87 setup (stock VM, W2_K2 wide jitter, CMP3 N=200 E=16 G=300), clone fraction c in {0.5, 0.8},
seeds 10001-10006.
PREDICTION (committed before running), error-threshold-on-memory hypothesis: keyed reach >= 2/12 across the two arms
(vs 0/32 at c = 0).
If 0/12, the keyed d6 wall is not (only) an error threshold, or lower load costs as much exploration as it saves.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET, manifest
from archaeon.beta.b55_chain_length import train_eps
from archaeon.beta.b86_keyed_distance import heldout
from archaeon.beta.b87_keyed_graded_distance import genome
from archaeon.beta.b99_mutation_load import make_descend
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B100_keyed_load"


def cell(job):
    rec = G.organism_record(manifest(genome("d6")), None, 0); rec["origins"] = ["gen0_d6"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b100", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x d6", "verified_common": True},
                      descend_fn=make_descend(job["c"], job["seed"]))
    first = None
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        if first is None and row["best_reward"] >= .9:
            first = g
        if g < job["G"] - 1:
            ev.reproduce()
    scores = [heldout(z[1]["manifest"]) for z in ev.scored[:10]]
    return {"c": job["c"], "seed": job["seed"], "best_heldout": max(scores), "keyed": max(scores) >= .9, "first_train_ge_.9": first}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"c": c, "seed": 10001 + i, "G": int(argv[0]) if argv else 300}): (c, i) for c in (0.5, 0.8) for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                c, i = futs[fu]; r = {"c": c, "seed": 10001 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B100_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {str(c): sum(r.get("keyed", False) for r in rows if r.get("c") == c) for c in (0.5, 0.8)}
    summ["total"] = summ["0.5"] + summ["0.8"]; summ["pred"] = summ["total"] >= 2
    print(json.dumps(summ))
    (OUT / "B100_result.json").write_text(json.dumps({"probe": "B100", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
