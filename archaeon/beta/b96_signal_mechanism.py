"""B96 -- test the Finding 5 mechanism: DILUTION (rotating scout) and DECAY (unused listener half).

B95b: from 200 x MUTE_OP (one word from full communication) the signal is never restored under SHARED reward, and the
listener half decays. Proposed mechanism:
(i) a signal mutant scouts in only 2/8 episodes (rotating scout), so its benefit is diluted;
(ii) listening is neutral when nobody signals and drifts away before a signal mutation is selected.
Arms (SHARED reward, gen 0 = 200 x MUTE_OP, B94 world/groups, CMP3 N=200 G=200, seeds 9601-9606):
  FIXED  the scout is the FIRST member of each random group in all 8 episodes (removes dilution)
  IMM    rotating scout; 20 fresh MUTE_OP immigrants per generation into non-elite slots (keeps listeners)
  BOTH   fixed scout + immigration
Readout: the best final genome's SIGNALS (> .05 = restored).
PREDICTION (committed before running): BOTH restores >= 3/6, AND at least one of FIXED / IMM restores >= 2/6.
If BOTH is 0/6, the mechanism is wrong or incomplete.
"""
import copy
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b93b_nonrival_ladder import world_static
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b95_signal_restore import MUTE_OP
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B96_signal_mech"
IMM = 20


def cell(job):
    w, s = world_static(); arm = job["arm"]; fixed = arm in ("FIXED", "BOTH"); imm = arm in ("IMM", "BOTH"); cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rec = G.organism_record(B92.man(list(MUTE_OP)), None, 0); rec["origins"] = ["gen0_MUTE_OP"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b96", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x MUTE_OP", "verified_common": True})
    rng = SplitMix64(seed_from("b96.imm", job["seed"]))
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b96.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        for a in range(0, len(idx), 4):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + 4]]
            rew = group_rot(grp, w, s, 8, scout=0 if fixed else None)
            mean = sum(rew) / len(rew)
            for m in grp:
                cache[id(m)] = mean
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
            if imm:
                ids = list(range(ev.elitism, len(ev.pop)))
                for _ in range(IMM):
                    k = ids.pop(rng.randbelow(len(ids))); im = copy.deepcopy(rec); im["origins"] = ["immigrant"]; ev.pop[k] = im
    X = ev.scored[0][1]["manifest"]
    sig, lis, slf = readouts(X, w, s)
    return {"arm": arm, "seed": job["seed"], "signals": sig, "listens": lis, "self_group": slf, "restored": sig > .05}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 9601 + i, "G": int(argv[0]) if argv else 200}): (a, i) for a in ("FIXED", "IMM", "BOTH") for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 9601 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B96_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("restored", False) for r in rows if r.get("arm") == a) for a in ("FIXED", "IMM", "BOTH")}
    summ["pred"] = summ["BOTH"] >= 3 and max(summ["FIXED"], summ["IMM"]) >= 2
    print(json.dumps(summ))
    (OUT / "B96_result.json").write_text(json.dumps({"probe": "B96", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
