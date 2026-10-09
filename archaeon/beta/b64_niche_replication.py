"""B64 -- replication of the B60/B62/B63 niche-partitioning result on a SECOND world (ensemble-invariance attack).

World: B-scatter.T000.d_horizon, NoClock (R=5 pools, L=5, 24 ticks; non-lethal hazards, hidden rich pool, history,
regime). The B60 evaluator is generalised for the REGIME feature. Agents' acts run on a copy of the world without
'regime'; once per tick, after all agents act:
- regeneration;
- every `every` ticks: regen *= factor, the shared pool list is reversed, and each agent's pool_node is reversed.
Teeth check first: at k=1 this must equal evaluate_world on the original world, and 4 identical foragers must earn less
each than solo.
Arms CONC / SOLO / SHAM, seeds 6401-6406, G=200: B62's cell, with this world and this evaluator. Then B63's
rare-advantage test on the final populations.
PREDICTION (before running), all three must hold for the replication to count:
- CONC entropy > SHAM by >= .2 bits in >= 4/6;
- CONC HET > HOM in >= 4/6;
- rare-type advantage in BOTH compositions CONC >= 4/6, with SOLO and SHAM fewer.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

import archaeon.beta.b60_concurrent_niches as B60
import archaeon.beta.b62_niche_attack as B62
import archaeon.beta.b63_rare_advantage as B63
from archaeon.beta.b25_noclock_world import NoClock, content_manifest
from archaeon.beta.b27_noclock_generality import load_world
from archaeon.campaign6.worlds.runtime import evaluate_world

WORLD = "B-scatter.T000.d_horizon"
OUT = Path(__file__).resolve().parent / "results" / "B64_bscatter"
_W = {}


def load():
    if "w" not in _W:
        w, s = load_world(WORLD)[:2]; _W["w"] = (w, s, None)
    return _W["w"]


def group_rewards(ms, w, seed, E, rng_seed=7, log=None):
    inner = w.w if isinstance(w, NoClock) else w
    agent_w = copy.copy(inner); agent_w.features = [f for f in inner.features if f != "regime"]
    aw = NoClock(agent_w) if isinstance(w, NoClock) else agent_w
    reg = inner.params.get("regime", {}) if "regime" in inner.features else None
    players = [Player(m) for m in ms]; tot = [0.0] * len(ms); mx = [0.0] * len(ms)
    for ep in range(E):
        shared = {}
        sts = [inner.reset(seed, ep, shared) for _ in ms]
        regen = sts[0]["regen"]
        for st in sts:
            st["regen"] = 0.0
        vms = [p.fresh_state() for p in players]
        rngs = [SplitMix64(seed_from("wse.vmrng", rng_seed, ep, i)) for i in range(len(ms))]
        t = 0
        while any(not aw.done(st) for st in sts):
            order = list(range(len(ms))); order = order[t % len(ms):] + order[:t % len(ms)]
            picks = []
            for i in order:
                if aw.done(sts[i]):
                    continue
                players[i].begin_tick(vms[i])
                outs, status = players[i].run_tick(vms[i], aw.observe(sts[i]), aw.K, rngs[i])
                if outs and outs[0] and sts[i]["pools"]:
                    picks.append(outs[0][0] % len(sts[i]["pools"]))
                aw.act(sts[i], outs)
                if status == "trap":
                    sts[i]["alive"] = False
            if log is not None and len(picks) > 1:
                log["ticks"] += 1; log["collide"] += len(picks) - len(set(picks))
            pools = sts[0]["pools"]
            for j, a in enumerate(pools):
                pools[j] = min(3.0, a + regen)
            if reg is not None:
                every = reg.get("every", 8)
                if every and t and t % every == 0:
                    regen = regen * reg.get("regen_factor", 0.5)
                    if pools:
                        pools.reverse()
                        for st in sts:
                            st["pool_node"].reverse()
            t += 1
        for i, st in enumerate(sts):
            tot[i] += max(0.0, st["reward"]); mx[i] += st["max_reward"]
    return [min(1.0, a / max(1e-9, b)) for a, b in zip(tot, mx)]


def _patch():
    B60.group_rewards = group_rewards; B62.group_rewards = group_rewards; B63.group_rewards = group_rewards
    B62.load = load; B62.OUT = OUT; B63.OUT = OUT


def teeth():
    _patch(); world, s, _ = load(); w = NoClock(world); m = content_manifest()
    return {"solo_k1": round(group_rewards([m], w, s, 8)[0], 4), "evaluate_world": round(evaluate_world(m, w, s, 8, rng_seed=7)["reward"], 4),
            "k4_identical": [round(x, 4) for x in group_rewards([m] * 4, w, s, 8)]}


def cell(job):
    _patch(); return B62.cell(job)


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "teeth":
        print(json.dumps(teeth())); return 0
    if argv and argv[0] == "rare":
        _patch(); world, s, _ = load(); w = NoClock(world); rows = []
        for arm in ("CONC", "SOLO", "SHAM"):
            for sd in range(6401, 6407):
                f = OUT / ("B62_pop_%s_%d.json" % (arm, sd))
                if f.exists():
                    r = {"arm": arm, "seed": sd, **B63.test(json.loads(f.read_text(encoding="utf-8")), w, s, world.R, sd)}
                    rows.append(r); print(json.dumps(r), flush=True)
        summ = {a: sum(r.get("rare_wins_both", False) for r in rows if r["arm"] == a) for a in ("CONC", "SOLO", "SHAM")}
        print(json.dumps(summ)); (OUT / "B64_rare.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")
        return 0
    G_ = int(argv[0]) if argv else 200
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 6401 + i, "G": G_}): (a, i) for i in range(6) for a in ("CONC", "SOLO", "SHAM")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 6401 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B64_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    (OUT / "B64_result.json").write_text(json.dumps({"probe": "B64", "world": WORLD, "G": G_, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
