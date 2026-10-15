"""B97 -- does a LARGER SELECTION COEFFICIENT let signalling be restored? (follow-up to B96)

B96: neither a fixed scout nor listener immigration (nor both) restores the one-word-lost signal (0/6 x 3).
B96b measured the selection coefficient of a restored signaller in a MUTE_OP population: expected group-mean gain
s ~ .019 under both the rotating and the fixed scout. Fixing the scout only concentrates the gain; it does not change
its expectation, so the 'dilution' story was wrong. The constraint is a weak s, because blind listeners already score
.869 (headroom .13).
Here pool values are rescaled so information matters more: each episode's static pools (1.0-1.75) are mapped linearly
onto 0.1-3.1 (max 3.0). Blind foraging is poor; the richest pool is worth up to ~30x the poorest. The shared pool list
is rescaled ONCE per (group, episode), when the first agent creates it.
Steps:
- controls + s (evaluation);
- evolution from 200 x MUTE_OP, SHARED (rotating scout) and INDIVIDUAL, CMP3 N=200 G=200, seeds 9701-9706.
PREDICTION (committed before running), weak-selection hypothesis:
- s in the rescaled world >= 3x the B96b value (.019);
- SHARED restores the signal (SIGNALS > .05) in >= 3/6;
- INDIVIDUAL in <= 1/6.
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
from archaeon.beta.b93b_nonrival_ladder import world_static
from archaeon.beta.b94_signal_evolution import group_rot, readouts
from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B97_headroom"


class Spread:
    """Wraps the static ComposedWorld (inside NoClock): rescales the episode's pools (1.0-1.75) to 0.1-3.1, ONCE per
    shared pool list (the first agent's reset)."""

    def __init__(self, cw):
        self.w = cw; self.K = cw.K; self.features = cw.features

    def __getattr__(self, k):
        return getattr(self.w, k)

    def reset(self, seed, ep, shared=None):
        first = shared is None or "pools" not in shared
        st = self.w.reset(seed, ep, shared)
        if first:
            st["pools"][:] = [min(3.0, .1 + 3.0 * (a - 1.0) / .75) for a in st["pools"]]
        st["max_reward"] = max(1e-9, self.w.ticks * max(st["pools"]))
        return st


def sw():
    from archaeon.beta.b25_noclock_world import NoClock
    w, s = world_static(); return NoClock(Spread(w.w)), s


def s_coeff(w, s):
    C, M = B92.man(list(COMPLETE)), B92.man(list(MUTE_OP)); out = []
    for pos in range(4):
        grp = [M] * 4; grp[pos] = C
        out.append(sum(sum(group_rot(grp, w, s + k, 8)) / 4 - sum(group_rot([M] * 4, w, s + k, 8)) / 4 for k in range(4)) / 4)
    return round(sum(out) / 4, 4)


def cell(job):
    w, s = sw(); arm = job["arm"]; cache = {}

    def ev_fn(m, eps, intervention=None, rng_seed=0, reward_mode="per_ask"):
        ev = evaluate_world(m, w, s, 8, rng_seed=7)
        if id(m) in cache:
            ev["reward"] = ev["reward_per_ask"] = cache[id(m)]
        return ev

    EV.evaluate = ev_fn
    rec = G.organism_record(B92.man(list(MUTE_OP)), None, 0); rec["origins"] = ["gen0_MUTE_OP"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=8, branch="b97", foundry=FOUNDRY_C2,
                      init_pop=[copy.deepcopy(rec) for _ in range(200)], gen0_provenance={"fill": "200 x MUTE_OP", "verified_common": True})
    for g in range(job["G"]):
        cache.clear(); r = random.Random(seed_from("b97.groups", job["seed"], g)); idx = list(range(len(ev.pop))); r.shuffle(idx)
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
    sig, lis, slf = readouts(X, w, s)
    return {"arm": arm, "seed": job["seed"], "signals": sig, "listens": lis, "self_group": slf, "restored": sig > .05}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    w, s = sw()
    ctl = {k: readouts(B92.man(list(g)), w, s) for k, g in (("COMPLETE", COMPLETE), ("MUTE_OP", MUTE_OP), ("BLIND", B92.BLIND))}
    sc = s_coeff(w, s); print("controls", json.dumps(ctl), "s", sc, flush=True)
    if argv and argv[0] == "controls":
        return 0
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 9701 + i, "G": int(argv[0]) if argv else 200}): (a, i) for a in ("SHARED", "INDIVIDUAL") for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 9701 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B97_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("restored", False) for r in rows if r.get("arm") == a) for a in ("SHARED", "INDIVIDUAL")}
    summ["s"] = sc; summ["pred"] = sc >= 3 * .019 and summ["SHARED"] >= 3 and summ["INDIVIDUAL"] <= 1
    print(json.dumps(summ))
    (OUT / "B97_result.json").write_text(json.dumps({"probe": "B97", "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
