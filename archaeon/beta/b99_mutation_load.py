"""B99 -- direct test of the MUTATIONAL-LOAD mechanism (Finding 5 revision). Lower the load: do seeded signallers persist?

B98: COMPLETE signallers seeded at 20% in MUTE_OP go extinct (0/4). B98b: their one-step children break the signal
31% of the time, against s ~ .046.
Intervention: wrap CMP3's mutation operator so that a fraction c of offspring are EXACT clones of their parent; the
rest use lineage.descend as before. The effective per-offspring break rate becomes ~.31 x (1 - c).
B98 setup otherwise: f = 20% COMPLETE + 80% MUTE_OP, SHARED, rotating scout, B97 high-headroom world, N=200, G=100,
seeds 9901-9904.
Arms: c = 0 (B98 replication), c = 0.8 (break ~.06), c = 0.95 (break ~.016 < s).
Readout: top-10 signalling; established = >= 5 of the top 10 signal.
PREDICTION (committed before running), mutational-load hypothesis:
- c=0.95 establishes in >= 3/4;
- c=0 in <= 1/4;
- monotone in c.
"""
import copy
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
from archaeon.beta.b97_signal_headroom import sw
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B99_mutation_load"


def make_descend(c, seed):
    rng = SplitMix64(seed_from("b99.clone", seed))

    def d(parent, s, mate=None):
        if rng.randbelow(1000) < int(c * 1000):
            return copy.deepcopy(parent), None
        return descend(parent, s, mate=mate)
    return d


def cell(job):
    w, s = sw(); c = job["c"]; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rc = G.organism_record(B92.man(list(COMPLETE)), None, 0); rc["origins"] = ["gen0_COMPLETE"]
    rm = G.organism_record(B92.man(list(MUTE_OP)), None, 0); rm["origins"] = ["gen0_MUTE_OP"]
    pop = [copy.deepcopy(rc) for _ in range(40)] + [copy.deepcopy(rm) for _ in range(160)]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b99", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "40 COMPLETE + 160 MUTE_OP", "verified_common": True},
                      descend_fn=make_descend(c, job["seed"]))
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b99.groups", job["seed"], c, g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
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
    return {"c": c, "seed": job["seed"], "top10_signalling": sum(x > .05 for x in sigs), "best_signals": sigs[0], "established": sum(x > .05 for x in sigs) >= 5}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"c": c, "seed": 9901 + i, "G": int(argv[0]) if argv else 100}): (c, i) for c in (0.0, 0.8, 0.95) for i in range(4)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                c, i = futs[fu]; r = {"c": c, "seed": 9901 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B99_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {str(c): sum(r.get("established", False) for r in rows if r.get("c") == c) for c in (0.0, 0.8, 0.95)}
    summ["pred"] = summ["0.95"] >= 3 and summ["0.0"] <= 1 and summ["0.0"] <= summ["0.8"] <= summ["0.95"]
    print(json.dumps(summ))
    (OUT / "B99_result.json").write_text(json.dumps({"probe": "B99", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
