"""B110 -- second-world replication of the KIN route (B106b in world 2).

B106b (world 1): in clonal groups at NORMAL mutation load (c=0, E=8), seeded signallers persist 4/4 and the signal
re-evolves from one word away 1/4.
World 2 (B107; B71 scan world 5). Training-set check (B107 controls, seed s5, E=8): clonal COMPLETE5 .995 vs MUTE5 .682,
so the signal has value in training.
Arms (c=0, CMP3 N=200, E=8, G=100), seeds 11001-11004:
  SEEDED  20% COMPLETE5 + 80% MUTE5
  MUTE    200 x MUTE5
Readout: world-2 readouts5; 'signalling' = >= 5 of the top 10 with SIGNALS > .05.
PREDICTION (committed before running; same as B106b): SEEDED >= 3/4 AND MUTE >= 1/4.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b94_signal_evolution import group_rot
import archaeon.beta.b107_comm_world2 as W2
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B110_kin_world2"


def cell(job):
    w, s = W2.world2(); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rc = G.organism_record(B92.man(list(W2.COMPLETE5)), None, 0); rm = G.organism_record(B92.man(list(W2.MUTE5)), None, 0)
    n_c = 40 if job["arm"] == "SEEDED" else 0
    pop = [copy.deepcopy(rc) for _ in range(n_c)] + [copy.deepcopy(rm) for _ in range(200 - n_c)]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b110", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "%d COMPLETE5 + %d MUTE5" % (n_c, 200 - n_c), "verified_common": True})
    for g in range(job["G"]):
        cache.clear()
        for o in ev.pop:
            m = o["manifest"]
            if id(m) not in cache:
                cache[id(m)] = sum(group_rot([m] * 4, w, s, 8)) / 4
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    tops = [z[1]["manifest"] for z in ev.scored[:10]]
    sigs = [W2.readouts5(m, w, s)[0] for m in tops]
    return {"arm": job["arm"], "seed": job["seed"], "top10_signalling": sum(x > .05 for x in sigs), "best_signals": sigs[0],
            "signalling": sum(x > .05 for x in sigs) >= 5}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 11001 + i, "G": int(argv[0]) if argv else 100}): (a, i) for a in ("SEEDED", "MUTE") for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 11001 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B110_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("signalling", False) for r in rows if r.get("arm") == a) for a in ("SEEDED", "MUTE")}
    summ["pred"] = summ["SEEDED"] >= 3 and summ["MUTE"] >= 1
    print(json.dumps(summ))
    (OUT / "B110_result.json").write_text(json.dumps({"probe": "B110", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
