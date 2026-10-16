"""B111 -- can communication arise FROM SCRATCH under the KIN route? (B104 analogue for clonal groups)

B104: from random gen 0, group reward + low load gives 0/12 (not even scouting).
B106b/B110: kin (clonal) groups at NORMAL load hold seeded signallers 8/8 and restore the signal from one word away 2/8.
Here: random FOUNDRY_C2 gen 0, world 1 (B97 world), clonal groups, c=0, CMP3 N=200 E=8 G=300, seeds 11101-11106.
Readout: the best genome's SIGNALS minus the constant twin (.011); informative = margin > .05. Also SELF and LISTENS.
PREDICTION (committed before running; deliberately modest): informative >= 1/6.
Expected failure mode: scouting plus a listener branch are many coupled instructions from random -- the distance wall.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b97_signal_headroom import sw
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B111_kin_scratch"
CONST = .0107


def cell(job):
    w, s = sw(); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b111", foundry=FOUNDRY_C2)
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
    sig, lis, slf = readouts(X, w, s)
    return {"seed": job["seed"], "signals": sig, "margin": round(sig - CONST, 4), "listens": lis, "self_group": slf, "informative": sig - CONST > .05}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 6) as ex:
        futs = {ex.submit(cell, {"seed": 11101 + i, "G": int(argv[0]) if argv else 300}): i for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 11101 + futs[fu], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B111_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("informative", False) for r in rows); summ = {"informative": k, "n": len(rows), "pred": k >= 1}
    print(json.dumps(summ))
    (OUT / "B111_result.json").write_text(json.dumps({"probe": "B111", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
