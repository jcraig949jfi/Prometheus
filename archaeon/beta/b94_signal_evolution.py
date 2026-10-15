"""B94 -- does INFORMATIVE SIGNALLING evolve, and does it need SHARED reward? (communication lane)

B93b: in the non-rival static-pool world, a hand scout that signals the richest pool lifts 3 blind listeners
.869 -> 1.000 at no cost to itself.
Evolution: one role-agnostic genome type.
- Each generation the population is split into random 4-groups.
- In each group the SCOUT rotates by episode (scout = ep mod 4): it sees the pool words; the other three see them zeroed.
  Everyone sees the shared signal word (channel 3).
- E=8 per group, so every member scouts in 2 episodes.
Arms (CMP3 N=200, G=200, seeds 9401-9406):
  INDIVIDUAL  fitness = own reward
  SHARED      fitness = the group's mean reward
Readouts on the best final genome X (held-out world seeds s+1000..1003 x 16):
  SIGNALS  X as scout with 3 hand LISTENERs: listeners' mean minus the same with a hand SILENT scout
           (> .05 = informative signalling)
  LISTENS  X as listener (x3) with a hand SCOUT: their mean minus the same with a hand SILENT scout
  SELF     4 copies of X with a rotating scout: group mean (hand SCOUT+LISTENER reference 1.000; blind .869)
PREDICTION (committed before running):
- SHARED: SIGNALS > .05 in >= 4/6;
- INDIVIDUAL: SIGNALS > .05 in <= 2/6.
Signalling is free but brings the signaller nothing under individual reward.
"""
import copy
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
import archaeon.beta.b92_signal_ladder as B92
from archaeon.beta.b93b_nonrival_ladder import world_static
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B94_signal_evo"
R_ = 3


def group_rot(ms, w, seed, E, rng_seed=7, scout=None):
    """B92.group with the scout = ep mod len(ms) (or a fixed index when `scout` is given)."""
    inner = w.w; players = [Player(m) for m in ms]; tot = [0.0] * len(ms); mx = [0.0] * len(ms)
    for ep in range(E):
        sc = (ep % len(ms)) if scout is None else scout
        shared = {}; sts = [inner.reset(seed, ep, shared) for _ in ms]
        vms = [p.fresh_state() for p in players]
        rngs = [SplitMix64(seed_from("wse.vmrng", rng_seed, ep, i)) for i in range(len(ms))]
        t = 0
        while any(not w.done(st) for st in sts):
            order = list(range(len(ms))); order = order[t % len(ms):] + order[:t % len(ms)]
            for i in order:
                if w.done(sts[i]):
                    continue
                obs = w.observe(sts[i])
                if i != sc:
                    obs = [[0 if j < R_ else x for j, x in enumerate(ch)] for ch in obs]
                players[i].begin_tick(vms[i]); outs, status = players[i].run_tick(vms[i], obs, w.K, rngs[i])
                w.act(sts[i], outs)
                if status == "trap":
                    sts[i]["alive"] = False
            t += 1
        for i, st in enumerate(sts):
            tot[i] += max(0.0, st["reward"]); mx[i] += st["max_reward"]
    return [min(1.0, a / max(1e-9, b)) for a, b in zip(tot, mx)]


def readouts(X, w, s):
    S, Q, L = B92.man(B92.scout(True)), B92.man(B92.scout(False)), B92.man(B92.LISTENER)
    avg = lambda f: sum(f(s + 1000 + k) for k in range(4)) / 4
    lm = lambda ms, sc: avg(lambda ss: sum(r for i, r in enumerate(group_rot(ms, w, ss, 16, scout=sc)) if i != sc) / 3)
    signals = lm([X, L, L, L], 0) - lm([Q, L, L, L], 0)
    listens = lm([S, X, X, X], 0) - lm([Q, X, X, X], 0)
    self_ = avg(lambda ss: sum(group_rot([X] * 4, w, ss, 16)) / 4)
    return round(signals, 4), round(listens, 4), round(self_, 4)


def cell(job):
    w, s = world_static(); arm = job["arm"]; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b94", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b94.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
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
    return {"arm": arm, "seed": job["seed"], "signals": sig, "listens": lis, "self_group": slf, "informative": sig > .05}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "controls":
        w, s = world_static()
        print(json.dumps({k: readouts(B92.man(g), w, s) for k, g in (("hand_SCOUT", B92.scout(True)), ("hand_LISTENER", B92.LISTENER), ("BLIND", B92.BLIND))}))
        return 0
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 9401 + i, "G": int(argv[0]) if argv else 200}): (a, i) for a in ("INDIVIDUAL", "SHARED") for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 9401 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B94_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("informative", False) for r in rows if r.get("arm") == a) for a in ("INDIVIDUAL", "SHARED")}
    summ["pred"] = summ["SHARED"] >= 4 and summ["INDIVIDUAL"] <= 2
    print(json.dumps(summ))
    (OUT / "B94_result.json").write_text(json.dumps({"probe": "B94", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
