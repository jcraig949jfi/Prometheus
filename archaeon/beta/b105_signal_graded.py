"""B105 -- GRADED distance for communication below the error threshold (the analogue of B87 for keyed memory).

B103/B103b: from MUTE_OP (one opcode WORD from COMPLETE), at clone fraction .85 under SHARED reward, an informative
signal re-evolves in 7/12 runs. B104: from random gen 0, 0/6.
Here: precursors W1/W2/W3 = COMPLETE with the opcode words of instruction 21 (signal OUT), 21+20 (+ channel LDC),
21+20+19 (+ ADD) NOPed. All three are verified to sit on the SAME plateau (SIGNALS 0, LISTENS .328, own group .754),
so only distance differs. B97 world, rotating scout, SHARED, c=.85, G=300, seeds 10501-10506 per arm.
Readout: the best genome's SIGNALS minus the constant twin (.011); informative = margin > .05.
PREDICTION (committed before running):
- informative rates monotone non-increasing W1 >= W2 >= W3;
- W1 >= 2/6 (replicating B103);
- W3 <= 1/6.
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
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b95_signal_restore import COMPLETE
from archaeon.beta.b97_signal_headroom import sw
from archaeon.beta.b99_mutation_load import make_descend
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B105_signal_graded"
CONST = .0107
SETS = {"W1": [21], "W2": [21, 20], "W3": [21, 20, 19]}


def precursor(k):
    g = list(COMPLETE)
    for i in SETS[k]:
        g[4 * i] = 0
    return g


def cell(job):
    w, s = sw(); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rec = G.organism_record(B92.man(precursor(job["arm"])), None, 0); rec["origins"] = ["gen0_" + job["arm"]]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b105", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x " + job["arm"], "verified_common": True},
                      descend_fn=make_descend(0.85, job["seed"]))
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b105.groups", job["seed"], job["arm"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        for a in range(0, len(idx), 4):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + 4]]
            rew = group_rot(grp, w, s, 8); mean = sum(rew) / len(rew)
            for m in grp:
                cache[id(m)] = mean
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    X = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (job["arm"], job["seed"]))).write_text(json.dumps(X), encoding="utf-8")
    sig = readouts(X, w, s)[0]
    return {"arm": job["arm"], "seed": job["seed"], "signals": sig, "margin": round(sig - CONST, 4), "informative": sig - CONST > .05}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": k, "seed": 10501 + i, "G": int(argv[0]) if argv else 300}): (k, i) for k in SETS for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                k, i = futs[fu]; r = {"arm": k, "seed": 10501 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B105_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {k: sum(r.get("informative", False) for r in rows if r.get("arm") == k) for k in SETS}
    summ["pred"] = summ["W1"] >= summ["W2"] >= summ["W3"] and summ["W1"] >= 2 and summ["W3"] <= 1
    print(json.dumps(summ))
    (OUT / "B105_result.json").write_text(json.dumps({"probe": "B105", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
