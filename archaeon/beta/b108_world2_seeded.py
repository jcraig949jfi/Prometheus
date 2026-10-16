"""B108 -- diagnose B107's low world-2 rate: can SEEDED signallers HOLD in world 2 below the threshold?

B107: world 2 SHARED 1/6 vs world 1 7/12, although the world-2 training gain is larger (+.07 vs +.035).
Separating test (B99 design in world 2): gen 0 = 20% COMPLETE5 + 80% MUTE5, SHARED, rotating scout, c=.85, G=100,
seeds 10801-10804. 'Holds' = >= 5 of the final top 10 with SIGNALS above the constant twin by > .05.
- If seeded signallers sweep, world 2's deficit is about ARISING (supply / path availability).
- If they cannot hold, world 2's error threshold is higher.
PREDICTION (committed before running): holds in >= 3/4.
"""
import copy
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.prng import seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b94_signal_evolution import group_rot
from archaeon.beta.b99_mutation_load import make_descend
import archaeon.beta.b107_comm_world2 as W2
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B108_world2_seeded"


def cell(job):
    w, s = W2.world2(); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rc = G.organism_record(B92.man(list(W2.COMPLETE5)), None, 0); rm = G.organism_record(B92.man(list(W2.MUTE5)), None, 0)
    pop = [copy.deepcopy(rc) for _ in range(40)] + [copy.deepcopy(rm) for _ in range(160)]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b108", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "40 COMPLETE5 + 160 MUTE5", "verified_common": True},
                      descend_fn=make_descend(0.85, job["seed"]))
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b108.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        for a in range(0, len(idx), 4):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + 4]]
            rew = group_rot(grp, w, s, 8); mean = sum(rew) / len(rew)
            for m in grp:
                cache[id(m)] = mean
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    tops = [z[1]["manifest"] for z in ev.scored[:10]]
    sigs = [W2.readouts5(m, w, s)[0] for m in tops]
    return {"seed": job["seed"], "top10_signalling": sum(x > .05 for x in sigs), "best_signals": sigs[0], "holds": sum(x > .05 for x in sigs) >= 5}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 4) as ex:
        futs = {ex.submit(cell, {"seed": 10801 + i, "G": int(argv[0]) if argv else 100}): i for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 10801 + futs[fu], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B108_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("holds", False) for r in rows); summ = {"holds": k, "n": len(rows), "pred": k >= 3}
    print(json.dumps(summ))
    (OUT / "B108_result.json").write_text(json.dumps({"probe": "B108", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
