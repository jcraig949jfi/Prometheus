"""B62 -- attack on B60 (CONC entropy > SOLO). Two kill paths.

K1 NOISE: random group composition makes CONC fitness noisy, and noisy selection alone keeps populations diverse.
  Arm SHAM:
  - each generation compute solo reward s_i and concurrent reward x_i (as CONC);
  - least-squares x = a*s + e;
  - fitness_i = a*s_i + e_pi(i) for a random permutation pi.
  The distribution of the competition-dependent residual is kept, but it is detached from the organism's own strategy.
  If SHAM entropy ~ CONC entropy, B60's diversity is selection noise, not partitioning.
K2 FUNCTION: higher entropy is not a niche unless MIXED groups do better than SAME-niche groups from the same
  population. On each final population, per-capita concurrent reward of:
  - HOMOGENEOUS groups (4 organisms sharing a dominant index);
  - HETEROGENEOUS groups (4 organisms covering >= 3 dominant indices).
Arms CONC / SOLO / SHAM; seeds 6001-6006, so CONC and SOLO re-run B60's seeds: their summaries must reproduce B60
exactly (a determinism check). Final populations are dumped to results/B62_pop_<arm>_<seed>.json.
PREDICTION (before running, written as the B60 claim's defender):
- CONC entropy > SHAM by >= .2 bits in >= 4/6 pairs;
- in CONC finals, HET per-capita > HOM per-capita in >= 4/6;
- in SOLO finals, HET - HOM is smaller than in CONC in >= 4/6.
"""
import json
import random
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b59_coupling_niches import dominant_index, entropy
from archaeon.beta.b60_concurrent_niches import group_rewards, mean_group
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"


def het_hom(pop, dom, w, s, seed, n=12):
    r = random.Random(seed); by = defaultdict(list)
    for m, d in zip(pop, dom):
        if d is not None:
            by[d].append(m)
    hom = []; het = []
    big = [d for d, ms in by.items() if len(ms) >= 4]
    for _ in range(n):
        if big:
            hom += group_rewards(r.sample(by[r.choice(big)], 4), w, s, 8)
        keys = [d for d in by if by[d]]
        if len(keys) >= 3:
            ks = r.sample(keys, 3); grp = [r.choice(by[k]) for k in ks] + [r.choice(by[r.choice(ks)])]
            het += group_rewards(grp, w, s, 8)
    f = lambda v: round(sum(v) / len(v), 4) if v else None
    return {"hom": f(hom), "het": f(het), "n_niches_ge4": len(big), "n_niches": len(by)}


def cell(job):
    world, s, _ = load(); w = NoClock(world); arm = job["arm"]; k = 1 if arm == "SOLO" else job.get("k", 4)
    cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b60", foundry=FOUNDRY_C2)
    slopes = []
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b60.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
        x = {}
        for a in range(0, len(idx), k):
            grp = [ev.pop[i]["manifest"] for i in idx[a:a + k]]
            for m, v in zip(grp, group_rewards(grp, w, s, 8)):
                x[id(m)] = v
        if arm == "SHAM":
            ids = list(x); sv = {i: group_rewards([m], w, s, 8)[0] for i, m in ((id(o["manifest"]), o["manifest"]) for o in ev.pop)}
            ss = sum(sv[i] ** 2 for i in ids); a_ = sum(sv[i] * x[i] for i in ids) / ss if ss else 0.0
            res = [x[i] - a_ * sv[i] for i in ids]; random.Random(seed_from("b62.sham", job["seed"], g)).shuffle(res)
            x = {i: a_ * sv[i] + e for i, e in zip(ids, res)}; slopes.append(round(a_, 4))
        cache.update(x)
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    pop = [o["manifest"] for o in ev.pop]
    (OUT / ("B62_pop_%s_%d.json" % (arm, job["seed"]))).write_text(json.dumps(pop), encoding="utf-8")
    dom = [dominant_index(m, w, s, world.R) for m in pop]
    solo = [group_rewards([m], w, s, 8)[0] for m in pop[:50]]
    g4, coll = mean_group(pop, w, s, 4, job["seed"])
    return {"arm": arm, "seed": job["seed"], "entropy": round(entropy(dom), 4), "dominant_counts": {str(a): b for a, b in Counter(dom).items()},
            "mean_solo_top50": round(sum(solo) / len(solo), 4), "mean_group4": g4, "collision_share": coll,
            "het_hom": het_hom(pop, dom, w, s, job["seed"]), "sham_slope_mean": round(sum(slopes) / len(slopes), 4) if slopes else None}


def main(argv):
    G_ = int(argv[0]) if argv else 200
    arms = argv[2].split(",") if len(argv) > 2 else ["CONC", "SOLO", "SHAM"]
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 6001 + i, "G": G_}): (a, i) for i in range(6) for a in arms}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 6001 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B62_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    (OUT / "B62_result.json").write_text(json.dumps({"probe": "B62", "G": G_, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
