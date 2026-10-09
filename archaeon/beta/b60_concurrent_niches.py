"""B60 -- niche partitioning under CONCURRENT ecological coupling (repair of B59).

B59's sequential coupling had no teeth: pools regenerate to the in-episode equilibrium before the next organism is
evaluated (teeth check: .2948 then .2895 x19). Repair: k organisms act in the SAME episode.
- Shared: pools, cells and signal (C6 coupling, one shared dict per group x episode, so every episode keeps its own layout).
- Each organism keeps its own pos, reward and alive.
- Regeneration is applied ONCE per tick after all agents act.
- Acting order rotates by tick.
Arms on the P-boom NoClock world, CMP3 search, N=200, E=8, G=200, 6 seeds each:
  CONC   each generation the population is randomly partitioned into groups of k=4; fitness = own concurrent reward
  SOLO   same evaluator with k=1 (only coupling differs between arms)
Readouts on the final population:
  entropy of dominant harvest indices (solo, 32 episodes, as B59);
  mean group reward (k=4 groups of final organisms) vs mean solo reward;
  same-pool collision share in groups.
PREDICTION (before running): CONC entropy > SOLO by >= .2 bits in >= 4/6 seed pairs, AND CONC final organisms earn more
in groups than SOLO final organisms do in groups (adaptation to competition) in >= 4/6 pairs.
"""
import json
import math
import random
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock, content_manifest, load
from archaeon.beta.b59_coupling_niches import dominant_index, entropy
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"


def group_rewards(ms, w, seed, E, rng_seed=7, log=None):
    """Concurrent evaluation of the manifests ms in one group; returns each one's normalised reward."""
    players = [Player(m) for m in ms]; tot = [0.0] * len(ms); mx = [0.0] * len(ms)
    for ep in range(E):
        shared = {}
        sts = [w.reset(seed, ep, shared) for _ in ms]
        regen = sts[0]["regen"]
        for st in sts:
            st["regen"] = 0.0
        vms = [p.fresh_state() for p in players]
        rngs = [SplitMix64(seed_from("wse.vmrng", rng_seed, ep, i)) for i in range(len(ms))]
        t = 0
        while any(not w.done(st) for st in sts):
            order = list(range(len(ms))); order = order[t % len(ms):] + order[:t % len(ms)]
            picks = []
            for i in order:
                if w.done(sts[i]):
                    continue
                players[i].begin_tick(vms[i])
                outs, status = players[i].run_tick(vms[i], w.observe(sts[i]), w.K, rngs[i])
                if outs and outs[0] and sts[i]["pools"]:
                    picks.append(outs[0][0] % len(sts[i]["pools"]))
                w.act(sts[i], outs)
                if status == "trap":
                    sts[i]["alive"] = False
            if log is not None and len(picks) > 1:
                log["ticks"] += 1; log["collide"] += len(picks) - len(set(picks))
            pools = sts[0]["pools"]
            for j, a in enumerate(pools):
                pools[j] = min(3.0, a + regen)
            t += 1
        for i, st in enumerate(sts):
            tot[i] += max(0.0, st["reward"]); mx[i] += st["max_reward"]
    return [min(1.0, a / max(1e-9, b)) for a, b in zip(tot, mx)]


def teeth():
    world, s, _ = load(); w = NoClock(world); m = content_manifest()
    return {"solo_k1": round(group_rewards([m], w, s, 8)[0], 4), "k4_identical": [round(x, 4) for x in group_rewards([m] * 4, w, s, 8)],
            "evaluate_world_uncoupled": round(evaluate_world(m, w, s, 8, rng_seed=7)["reward"], 4)}


def mean_group(pop, w, s, k, seed, n_groups=12):
    r = random.Random(seed); out = []; log = {"ticks": 0, "collide": 0}
    for _ in range(n_groups):
        out += group_rewards(r.sample(pop, k), w, s, 8, log=log)
    return round(sum(out) / len(out), 4), round(log["collide"] / max(1, log["ticks"]), 4)


def cell(job):
    world, s, _ = load(); w = NoClock(world); k = 4 if job["arm"] == "CONC" else 1
    cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b60", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b60.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        for a in range(0, len(idx), k):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + k]]
            for m, x in zip(grp, group_rewards(grp, w, s, 8)):
                cache[id(m)] = x
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    pop = [o["manifest"] for o in ev.pop]
    dom = [dominant_index(m, w, s, world.R) for m in pop]
    solo = [group_rewards([m], w, s, 8)[0] for m in pop[:50]]
    g4, coll = mean_group(pop, w, s, 4, job["seed"])
    return {"arm": job["arm"], "seed": job["seed"], "entropy": round(entropy(dom), 4), "dominant_counts": {str(a): b for a, b in Counter(dom).items()},
            "mean_solo_top50": round(sum(solo) / len(solo), 4), "mean_group4": g4, "collision_share": coll}


def main(argv):
    if argv and argv[0] == "teeth":
        print(json.dumps(teeth())); return 0
    G_ = int(argv[0]) if argv else 200
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 6001 + i, "G": G_}): (a, i) for i in range(6) for a in ("CONC", "SOLO")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 6001 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B60_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    pairs = {}
    for r in rows:
        pairs.setdefault(r["seed"], {})[r["arm"]] = r
    ok = [v for v in pairs.values() if "entropy" in v.get("CONC", {}) and "entropy" in v.get("SOLO", {})]
    summ = {"pairs": len(ok), "entropy_conc_higher_by_.2": sum(v["CONC"]["entropy"] - v["SOLO"]["entropy"] >= .2 for v in ok),
            "group4_conc_higher": sum(v["CONC"]["mean_group4"] > v["SOLO"]["mean_group4"] for v in ok),
            "mean_entropy_diff": round(sum(v["CONC"]["entropy"] - v["SOLO"]["entropy"] for v in ok) / max(1, len(ok)), 4)}
    print(json.dumps(summ), flush=True)
    (OUT / "B60_result.json").write_text(json.dumps({"probe": "B60", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
