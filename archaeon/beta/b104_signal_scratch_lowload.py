"""B104 -- does communication evolve FROM SCRATCH below the error threshold? (follow-up to B103)

B103/B103b: from one word away, at clone fraction .85, informative signalling re-evolves under SHARED reward 7/12 vs
INDIVIDUAL 0/12. B94: from random gen 0 at c=0, nothing evolves (not even scouting).
Here: random FOUNDRY_C2 gen 0, B97 high-headroom world, rotating scout, CMP3 N=200 G=300, c=0.85, seeds 10401-10406,
SHARED vs INDIVIDUAL.
Readout: the best genome's SIGNALS minus the best constant-signal twin (.011; B103c). Informative = margin > .05.
Also LISTENS and SELF.
PREDICTION (committed before running; deliberately modest): SHARED informative >= 1/6, and INDIVIDUAL 0/6.
Expected failure mode: cloning cuts exploration, and from scratch even scouting (argmax of 3 words) is far.
"""
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b97_signal_headroom import sw
from archaeon.beta.b99_mutation_load import make_descend
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B104_scratch_lowload"
CONST = .0107


def cell(job):
    w, s = sw(); arm = job["arm"]; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b104", foundry=FOUNDRY_C2,
                      descend_fn=make_descend(0.85, job["seed"]))
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b104.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        for a in range(0, len(idx), 4):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + 4]]
            rew = group_rot(grp, w, s, 8)
            vals = [sum(rew) / len(rew)] * len(rew) if arm == "SHARED" else rew
            for m, v in zip(grp, vals):
                cache[id(m)] = v
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    X = ev.scored[0][1]["manifest"]
    (OUT / ("best_%s_%d.json" % (arm, job["seed"]))).write_text(json.dumps(X), encoding="utf-8")
    sig, lis, slf = readouts(X, w, s)
    return {"arm": arm, "seed": job["seed"], "signals": sig, "margin_vs_constant": round(sig - CONST, 4), "listens": lis, "self_group": slf,
            "informative": sig - CONST > .05}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 10401 + i, "G": int(argv[0]) if argv else 300}): (a, i) for a in ("SHARED", "INDIVIDUAL") for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 10401 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B104_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("informative", False) for r in rows if r.get("arm") == a) for a in ("SHARED", "INDIVIDUAL")}
    summ["pred"] = summ["SHARED"] >= 1 and summ["INDIVIDUAL"] == 0
    print(json.dumps(summ))
    (OUT / "B104_result.json").write_text(json.dumps({"probe": "B104", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
