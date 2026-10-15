"""B98 -- direct fixation test: does a SEEDED signaller establish, and at what starting frequency? (F5 packet S3)

F5: a restored signaller has s ~ .046 (B97 high-headroom world) but arises in only ~1e-4 of offspring. The
supply x selection account ASSUMED a fixation chance of ~2s. Here establishment is measured directly: gen 0 =
f% COMPLETE (signalling) + (100-f)% MUTE_OP, SHARED reward, rotating scout, B97 world, CMP3 N=200, G=100.
f in {1, 5, 20}%, seeds 9801-9804.
Readout: number of the final population's top-10 genomes with SIGNALS > .05, and the best genome's SIGNALS.
A run 'establishes' if >= 5 of the top 10 signal.
PREDICTION (committed before running):
- establishment is monotone in f;
- f=20% establishes in >= 3/4;
- f=1% (2 founders) in <= 1/4.
If even f=20% fails, a signaller cannot hold its ground, and the barrier is not only supply.
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
from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
from archaeon.beta.b97_signal_headroom import sw
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B98_fixation"


def cell(job):
    w, s = sw(); f = job["f"]; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    n_c = max(1, round(200 * f / 100))
    rc = G.organism_record(B92.man(list(COMPLETE)), None, 0); rc["origins"] = ["gen0_COMPLETE"]
    rm = G.organism_record(B92.man(list(MUTE_OP)), None, 0); rm["origins"] = ["gen0_MUTE_OP"]
    pop = [copy.deepcopy(rc) for _ in range(n_c)] + [copy.deepcopy(rm) for _ in range(200 - n_c)]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b98", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "%d COMPLETE + %d MUTE_OP" % (n_c, 200 - n_c), "verified_common": True})
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b98.groups", job["seed"], f, g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        for a in range(0, len(idx), 4):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + 4]]
            rew = group_rot(grp, w, s, 8); mean = sum(rew) / len(rew)
            for m in grp:
                cache[id(m)] = mean
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    tops = [z[1]["manifest"] for z in ev.scored[:10]]
    sigs = [readouts(m, w, s)[0] for m in tops]
    return {"f": f, "seed": job["seed"], "n_founders": n_c, "top10_signalling": sum(x > .05 for x in sigs), "best_signals": sigs[0],
            "established": sum(x > .05 for x in sigs) >= 5}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"f": f, "seed": 9801 + i, "G": int(argv[0]) if argv else 100}): (f, i) for f in (1, 5, 20) for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                f, i = futs[fu]; r = {"f": f, "seed": 9801 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B98_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {str(f): sum(r.get("established", False) for r in rows if r.get("f") == f) for f in (1, 5, 20)}
    summ["pred"] = summ["20"] >= 3 and summ["1"] <= 1 and summ["1"] <= summ["5"] <= summ["20"]
    print(json.dumps(summ))
    (OUT / "B98_result.json").write_text(json.dumps({"probe": "B98", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
