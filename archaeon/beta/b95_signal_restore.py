"""B95 -- does selection RESTORE a one-edit-lost signal, and only under SHARED reward? (follow-up to B94)

B94: from random gen 0, neither signalling nor listening evolves (0/6 in both arms; own-group mean = the blind .869).
Following the distance law, here the population starts ONE EDIT from full communication.
Hand programs:
  COMPLETE  if any pool word is non-zero (scout): harvest the richest and signal its index+1; else (listener): follow
            the signal (default pool 0)
  MUTE      COMPLETE with the signal OUT NOPed (one edit): scouts harvest the richest silently; listeners default to 0
Gen 0 = 200 x MUTE. B94 world and groups (rotating scout, non-rival static pools), CMP3 N=200 G=200, seeds 9501-9506.
Arms:
  SHARED      fitness = group mean -- restoring the signal raises the group mean ~+.10
  INDIVIDUAL  fitness = own reward -- a signal helps only OTHERS, so restoring it is neutral for the signaller
Readout: the best final genome's SIGNALS score (B94 readout; COMPLETE +.131, MUTE 0).
PREDICTION (committed before running): SHARED restores the signal (SIGNALS > .05) in >= 4/6; INDIVIDUAL in <= 2/6.
"""
import copy
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.prng import seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, HALT, IN, JZ, LDC, MOV, OUT_, REGIMES, TARGET, _prog
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b93b_nonrival_ladder import world_static
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B95_signal_restore"
ADD, SUB, OR, LT = 7, 8, 11, 17
COMPLETE = _prog([
    (IN, 1, 0), (IN, 2, 0), (IN, 3, 0), (IN, 9, 0),                       # 0-3  pools r1-r3, signal r9
    (OR, 6, 1, 2), (OR, 6, 6, 3), (JZ, 6, 17),                           # 4-6  all pools zero -> listener (23)
    (LDC, 4, 0), (MOV, 5, 1), (LT, 6, 5, 2), (JZ, 6, 3), (MOV, 5, 2), (LDC, 4, 1),   # 7-12
    (LT, 6, 5, 3), (JZ, 6, 3), (MOV, 5, 3), (LDC, 4, 2),                 # 13-16 argmax -> r4
    (OUT_, 4, 0), (LDC, 7, 1), (ADD, 8, 4, 7), (LDC, 6, 3), (OUT_, 8, 6), (HALT,),   # 17-22 harvest r4, signal r4+1
    (JZ, 9, 5), (LDC, 7, 1), (SUB, 8, 9, 7), (OUT_, 8, 0), (HALT,),      # 23-27 listener: harvest signal-1
    (OUT_, 0, 0), (HALT,)])                                               # 28-29 default pool 0
MUTE = list(COMPLETE); MUTE[21 * 4:22 * 4] = [0, 0, 0, 0]


def cell(job):
    w, s = world_static(); arm = job["arm"]; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rec = G.organism_record(B92.man(list(MUTE)), None, 0); rec["origins"] = ["gen0_MUTE"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b95", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x MUTE", "verified_common": True})
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b95.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
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
    return {"arm": arm, "seed": job["seed"], "signals": sig, "listens": lis, "self_group": slf, "restored": sig > .05}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        w, s = world_static(); print(json.dumps({"COMPLETE": readouts(B92.man(list(COMPLETE)), w, s), "MUTE": readouts(B92.man(list(MUTE)), w, s)})); return 0
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 9501 + i, "G": int(argv[0]) if argv else 200}): (a, i) for a in ("SHARED", "INDIVIDUAL") for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 9501 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B95_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("restored", False) for r in rows if r.get("arm") == a) for a in ("SHARED", "INDIVIDUAL")}
    summ["pred"] = summ["SHARED"] >= 4 and summ["INDIVIDUAL"] <= 2
    print(json.dumps(summ))
    (OUT / "B95_result.json").write_text(json.dumps({"probe": "B95", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
