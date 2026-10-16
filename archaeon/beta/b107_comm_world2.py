"""B107 -- SECOND-WORLD replication of evolved communication (ensemble invariance for Finding 5; B103 in world 5).

B103/B103b (world = B71 minimal ecology): below the error threshold (clone fraction .85), an informative signal
re-evolves from one word away under SHARED reward 7/12 vs INDIVIDUAL 0/12.
World 2 = B71 scan world 5. Its features (resources, objects, coupling, channels; M=1 cell word) and pool layouts
differ. Made non-rival: locality off, static pools rescaled 0.1-3.1 once per shared pool list. Observation
[pool0, pool1, pool2, cell0, signal]. Training set (seed s5, E=8): the richest pool per episode is 2,2,1,0,2,2,2,0.
World-5 programs: COMPLETE5 / MUTE5 / LISTENER5 read one extra word (the cell) before the signal.
Arms: gen 0 = 200 x MUTE5; rotating scout; CMP3 N=200 E=8 G=300; c=.85; SHARED vs INDIVIDUAL; seeds 10701-10706.
Readout: the best genome's SIGNALS (world-5 readouts) minus the best constant-signal twin; informative = margin > .05.
PREDICTION (committed before running): SHARED informative >= 2/6 AND INDIVIDUAL <= 1/6.
B107 RESULT: SHARED 1/6, INDIVIDUAL 0/6 (FAILED on SHARED). B107b (argv[2]=b): 6 more SHARED seeds (10711-10716).
PREDICTION (committed before the B107b run): the new seeds give SHARED >= 1/6, AND the pooled world-2 SHARED rate (12 runs)
is not significantly below world 1 (7/12; Fisher one-sided p > .05).
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
from archaeon.beta.b94_signal_evolution import group_rot
from archaeon.beta.b97_signal_headroom import Spread
from archaeon.beta.b99_mutation_load import make_descend
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B107_comm_world2"
ADD, SUB, OR, LT = 7, 8, 11, 17


def world2():
    from archaeon.beta.b25_noclock_world import NoClock
    from archaeon.beta.b32_world_distribution import family_world
    from archaeon.campaign6.worlds.runtime import ComposedWorld
    w5, s5 = family_world(("b71", 5, 0)); p = copy.deepcopy(w5.w.params)
    p["locality"] = {"on": False}; p["resources"] = dict(p["resources"], deplete=0.0, regen=0.0); p["coupling"] = {"on": True}
    return NoClock(Spread(ComposedWorld(p))), s5


COMPLETE5 = _prog([
    (IN, 1, 0), (IN, 2, 0), (IN, 3, 0), (IN, 9, 0), (IN, 9, 0),          # 0-4  pools r1-r3; cell (discarded), signal -> r9
    (OR, 6, 1, 2), (OR, 6, 6, 3), (JZ, 6, 17),                           # 5-7  all pools zero -> listener (24)
    (LDC, 4, 0), (MOV, 5, 1), (LT, 6, 5, 2), (JZ, 6, 3), (MOV, 5, 2), (LDC, 4, 1),
    (LT, 6, 5, 3), (JZ, 6, 3), (MOV, 5, 3), (LDC, 4, 2),
    (OUT_, 4, 0), (LDC, 7, 1), (ADD, 8, 4, 7), (LDC, 6, 3), (OUT_, 8, 6), (HALT,),   # 18-23; the signal OUT is instruction 22
    (JZ, 9, 5), (LDC, 7, 1), (SUB, 8, 9, 7), (OUT_, 8, 0), (HALT,),      # 24-28 listener
    (OUT_, 0, 0), (HALT,)])
MUTE5 = list(COMPLETE5); MUTE5[22 * 4] = 0                              # opcode word of the signal OUT -> NOP
LISTENER5 = _prog([(IN, 1, 0)] * 5 + [(JZ, 1, 5), (LDC, 2, 1), (SUB, 3, 1, 2), (OUT_, 3, 0), (HALT,), (OUT_, 0, 0), (HALT,)])


def readouts5(X, w, s):
    """B94 readouts with the world-5 hand LISTENER (the hand SCOUT reads only the first three words, so it is valid)."""
    S, Q, L = B92.man(B92.scout(True)), B92.man(B92.scout(False)), B92.man(LISTENER5)
    avg = lambda f: sum(f(s + 1000 + k) for k in range(4)) / 4
    lm = lambda ms, sc: avg(lambda ss: sum(r for i, r in enumerate(group_rot(ms, w, ss, 16, scout=sc)) if i != sc) / 3)
    signals = lm([X, L, L, L], 0) - lm([Q, L, L, L], 0)
    listens = lm([S, X, X, X], 0) - lm([Q, X, X, X], 0)
    self_ = avg(lambda ss: sum(group_rot([X] * 4, w, ss, 16)) / 4)
    return round(signals, 4), round(listens, 4), round(self_, 4)


def const_scout(v):
    body = [(IN, 1, 0), (IN, 2, 0), (IN, 3, 0), (LDC, 4, 0), (MOV, 5, 1), (LT, 6, 5, 2), (JZ, 6, 3), (MOV, 5, 2), (LDC, 4, 1),
            (LT, 6, 5, 3), (JZ, 6, 3), (MOV, 5, 3), (LDC, 4, 2), (OUT_, 4, 0), (LDC, 8, v), (LDC, 9, 3), (OUT_, 8, 9), (HALT,)]
    return B92.man(_prog(body))


def cell(job):
    w, s = world2(); arm = job["arm"]; cache = {}; const = job["const"]

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rec = G.organism_record(B92.man(list(MUTE5)), None, 0); rec["origins"] = ["gen0_MUTE5"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b107", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x MUTE5", "verified_common": True},
                      descend_fn=make_descend(0.85, job["seed"]))
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b107.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
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
    sig, lis, slf = readouts5(X, w, s)
    return {"arm": arm, "seed": job["seed"], "signals": sig, "margin": round(sig - const, 4), "listens": lis, "self_group": slf, "informative": sig - const > .05}


def controls():
    w, s = world2()
    C, M = B92.man(list(COMPLETE5)), B92.man(list(MUTE5))
    ctl = {"COMPLETE5": readouts5(C, w, s), "MUTE5": readouts5(M, w, s)}
    ctl["const"] = {v: readouts5(const_scout(v), w, s)[0] for v in (1, 2, 3)}
    ctl["train_clonal"] = {"COMPLETE5": round(sum(group_rot([C] * 4, w, s, 8)) / 4, 4), "MUTE5": round(sum(group_rot([M] * 4, w, s, 8)) / 4, 4)}
    ctl["train_1C3M_vs_4M"] = [round(sum(group_rot([C, M, M, M], w, s, 8)) / 4, 4), round(sum(group_rot([M] * 4, w, s, 8)) / 4, 4)]
    return ctl


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    if argv and argv[0] == "controls":
        return 0
    const = max(ctl["const"].values()); rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        b = len(argv) > 2 and argv[2] == "b"; base = 10711 if b else 10701; arms = ("SHARED",) if b else ("SHARED", "INDIVIDUAL")
        futs = {ex.submit(cell, {"arm": a, "seed": base + i, "G": int(argv[0]) if argv else 300, "const": const}): (a, i) for a in arms for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[fu]; r = {"arm": a, "seed": 10701 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / ("B107b_cells.jsonl" if b else "B107_cells.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("informative", False) for r in rows if r.get("arm") == a) for a in arms}
    summ["pred"] = (summ["SHARED"] >= 1) if b else (summ["SHARED"] >= 2 and summ["INDIVIDUAL"] <= 1)
    print(json.dumps(summ))
    (OUT / ("B107b_result.json" if b else "B107_result.json")).write_text(json.dumps({"probe": "B107", "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
