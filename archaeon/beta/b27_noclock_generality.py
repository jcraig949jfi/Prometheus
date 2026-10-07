"""B27 -- does NO-CLOCK content sensing evolve beyond one world? (generality of B25/B26)

Four other composed worlds from the frontier record, each with resources + locality (different families):
B-pressure.T2 (delayed, hidden, regime), B-scatter.T000.d_horizon (hidden, history, coupling, regime),
C6-unable.T3 (delayed, history), W-artifacts_w50053_persist (objects, hazards, coupling).
NOCLOCK only (B25 wrapper), CMP3 search, E=8, G=200, 3 seeds per world, 2 procs (light rule). Readout per elite:
elite reward, BLIND twin (all observation words zeroed -- the primary control after B26), words SENSED (zeroing one
word drops reward >= .05).
PREDICTION (before running): content sensing (blind drop >= .05 AND >= 1 pool word sensed) in >= 1/3 seeds in at
least 3 of the 4 worlds. Delayed worlds (actions act d ticks later) are expected to be hardest.
"""
import gzip
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b23b_composed_world_audit import RUNS, score
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.campaign6.segment import resolve_world
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
WORLDS = ["B-pressure.T2", "B-scatter.T000.d_horizon", "C6-unable.T3", "W-artifacts_w50053_persist"]


def load_world(name):
    exp = [f / name for f in RUNS.iterdir() if (f / name).is_dir()][0]
    c = json.load(gzip.open(sorted(exp.glob("chunk_*.json.gz"))[-1]))
    return resolve_world(c["spec"]["world"]), c["spec"].get("provenance", {}).get("seed", 0) or 0


def cell(job):
    world, seed = load_world(job["world"])
    w = NoClock(world)
    EV.evaluate = lambda m, eps, intervention=None, rng_seed=0, reward_mode="per_ask": evaluate_world(m, w, seed, 8, rng_seed=7)
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b27", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    base = score(m, w, seed)
    n_words = len(w.observe(w.reset(seed, 0, None))[0])
    names = ["pool%d" % i for i in range(len(world.reset(seed, 0, None)["pools"]))]
    drops = {}
    for i in range(n_words):
        drops[names[i] if i < len(names) else "w%d" % i] = round(base - score(m, Ablate(w, i), seed), 4)
    blind = score(m, Ablate(w, "all"), seed)
    sensed = [k for k, v in drops.items() if v >= .05]
    return {"world": job["world"], "seed": job["seed"], "features": world.features, "elite": round(base, 4), "blind": round(blind, 4),
            "sensed": sensed, "content_sensing": (base - blind >= .05) and any(k.startswith("pool") for k in sensed),
            "drops": drops, "elite_manifest": m}


def main(argv):
    G_ = int(argv[0]) if argv else 200
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 2) as ex:
        futs = {ex.submit(cell, {"world": w, "seed": 2701 + s, "G": G_}): (w, s) for s in range(3) for w in WORLDS}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                w, s = futs[f]; r = {"world": w, "seed": 2701 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B27_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {w: sum(1 for r in rows if r.get("world") == w and r.get("content_sensing")) for w in WORLDS}
    print(json.dumps(summ), flush=True)
    (OUT / "B27_result.json").write_text(json.dumps({"probe": "B27", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
