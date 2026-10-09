"""B59 -- does ECOLOGICAL COUPLING produce niche partitioning? (first coordination / division-of-labour probe)

C6 coupling (archaeon/campaign6/worlds/runtime.py reset(shared=...)): organisms evaluated with the same `shared`
dict draw on ONE pool list -- each harvest depletes what the next organism sees. Every Beta run so far scored
organisms independently, so frequency-dependent selection was never on.
Arms on the P-boom NoClock world (coupling feature on in its params), CMP3 search, N=200, E=8, G=200, 6 seeds each:
  COUPLED    one shared dict per GENERATION (reset when the generation advances); organisms in population order
  UNCOUPLED  no shared state (B25 condition)
Readout (final population, each organism evaluated UNCOUPLED, 32 episodes): its DOMINANT harvest index (most frequent
channel-0 value mod R when a pool is local); population entropy of dominant indices (bits); also mean reward.
Caveat recorded up front: under coupling, evaluation order matters (elites are evaluated first and see full pools).
PREDICTION (before running): dominant-index entropy COUPLED > UNCOUPLED by >= .2 bits in >= 4/6 seed pairs.
"""
import json
import math
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"


def dominant_index(m, w, seed, R, E=32):
    p = Player(m); c = Counter()
    for ep in range(E):
        st = w.reset(seed, ep, None); vm = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep))
        while not w.done(st):
            obs = w.observe(st); outs, _ = p.run_tick(vm, obs, w.K, rng)
            if outs and outs[0]:
                c[outs[0][0] % R] += 1
            w.act(st, outs)
    return c.most_common(1)[0][0] if c else None


def entropy(vals):
    c = Counter(v for v in vals if v is not None); n = sum(c.values())
    return -sum(k / n * math.log2(k / n) for k in c.values()) if n else 0.0


def cell(job):
    world, s, _ = load(); w = NoClock(world); R = world.R
    state = {"g": -1, "shared": None}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        if job["arm"] == "COUPLED":
            return evaluate_world(m, w, s, 8, rng_seed=7, shared=state["shared"])
        return evaluate_world(m, w, s, 8, rng_seed=7)

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b59", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        state["shared"] = {}                      # fresh shared pools each generation
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    pop = [o["manifest"] for o in ev.pop]
    dom = [dominant_index(m, w, s, R) for m in pop]
    rewards = [evaluate_world(m, w, s, 8, rng_seed=7)["reward"] for m in pop[:50]]
    return {"arm": job["arm"], "seed": job["seed"], "entropy": round(entropy(dom), 4), "dominant_counts": dict(Counter(dom)),
            "mean_reward_top50_uncoupled": round(sum(rewards) / len(rewards), 4)}


def main(argv):
    G_ = int(argv[0]) if argv else 200
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 5901 + i, "G": G_}): (a, i) for i in range(6) for a in ("COUPLED", "UNCOUPLED")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 5901 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B59_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    pairs = {}
    for r in rows:
        pairs.setdefault(r["seed"], {})[r["arm"]] = r.get("entropy")
    diffs = [v["COUPLED"] - v["UNCOUPLED"] for v in pairs.values() if None not in (v.get("COUPLED"), v.get("UNCOUPLED"))]
    summ = {"pairs": len(diffs), "coupled_higher_by_.2": sum(d >= .2 for d in diffs), "mean_diff_bits": round(sum(diffs) / max(1, len(diffs)), 4)}
    print(json.dumps(summ), flush=True)
    (OUT / "B59_result.json").write_text(json.dumps({"probe": "B59", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
