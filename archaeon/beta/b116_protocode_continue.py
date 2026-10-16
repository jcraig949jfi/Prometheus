"""B116 -- does B112-NL 11214's sub-threshold proto-code SHARPEN under continued kin selection?

11214 (kin from scratch, jittered world, G=300): B115 info .046, ablation .049. It emits 0 mostly when pool 0 is
richest and 1 when pool 1/2 is (index-like, not a lattice hash).
Design: gen 0 = 200 clones of best_11214 (the population was not saved, so this is a restart from the best genome,
not a true lineage continuation). Kin clonal groups, c=0, E=8, G=300, jittered world (b114.jw). Seeds 11601-11602,
2 processes (memory: host reaped B112-NL at 18:35Z; 16.6 GB free at 19:00Z).
Readout: B115 info on the final best (held-out jittered 4 x 16); also the info of best_11214 re-scored as baseline.
PREDICTION (committed before running), local-optimum hypothesis: the code does NOT sharpen -- final info < .10 in
both seeds. A seed reaching info >= .10 falsifies it (the proto-code is a stepping stone kin selection can climb).
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b94_signal_evolution import group_rot
from archaeon.beta.b114_nolattice import jw
from archaeon.beta.b115_info_readout import info
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "B116_protocode"
SRC = HERE / "results" / "B112NL_kin_scratch_nolattice" / "best_11214.json"


def cell(job):
    w, s = jw(); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rec = G.organism_record(json.loads(SRC.read_text(encoding="utf-8")), None, 0); rec["origins"] = ["gen0_B112NL_11214"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b116", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x best_11214", "verified_common": True})
    for g in range(job["G"]):
        cache.clear()
        for o in ev.pop:
            m = o["manifest"]
            if id(m) not in cache:
                cache[id(m)] = sum(group_rot([m] * 4, w, s, 8)) / 4
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    X = ev.scored[0][1]["manifest"]
    (OUT / ("best_%d.json" % job["seed"])).write_text(json.dumps(X), encoding="utf-8")
    r = info(X, w, s); r.update({"seed": job["seed"], "sharpened": r["info"] >= .10})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    w, s = jw(); base = info(json.loads(SRC.read_text(encoding="utf-8")), w, s); print("baseline_11214", json.dumps(base), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(cell, {"seed": 11601 + i, "G": int(argv[0]) if argv else 300}): i for i in range(2)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 11601 + futs[fu], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B116_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("sharpened", False) for r in rows); summ = {"sharpened": k, "n": len(rows), "pred": k == 0, "baseline": base}
    print(json.dumps(summ))
    (OUT / "B116_result.json").write_text(json.dumps({"probe": "B116", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
