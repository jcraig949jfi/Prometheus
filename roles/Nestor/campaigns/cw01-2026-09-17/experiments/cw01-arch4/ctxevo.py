"""Evolution in the context worlds (cycle 7): fresh episodes every generation, held-out sets for the final
read, thresholds above every invariant ceiling. Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import numpy as np

import common as CM
import ctxworlds as CW
import evolver as EV
A = CM.A
THRESH = {"A": 0.90, "B": 0.80, "C": 0.80}
HELD_N = 4


def transform(world, seed, control=None, **kw):
    def f(eps, g):
        return CW.make(world, seed, g, control=control, **kw)
    return f


def held_sets(world, seed, control=None, **kw):
    return [CW.make(world, seed, 10_000 + i, control=control, **kw) for i in range(HELD_N)]


def held_reward(m, sets):
    return float(np.mean([CW.reward(m, s) for s in sets]))


def run_world(world, seed, G=120, control=None, init=None, top=16, label="nestor.ctx", **kw):
    """Evolve in `world`; return tops ranked by held-out reward (genomes kept) and the run history."""
    evo_kw = {k: kw.pop(k) for k in list(kw) if k in ("mate_rate", "persist_lock", "on_generation", "mutator", "archive_gens", "k_t")}
    if init is None:
        init, _ = EV.init_population()
    r = EV.run("select", seed, init, G_=G, env="W0", ep_transform=transform(world, seed, control, **kw), label="%s|%s|%s" % (label, world, control or "plain"), **evo_kw)
    sets = held_sets(world, seed, control, **kw)
    scored = [dict(x, held=held_reward(x["m"], sets), per_set=[CW.reward(x["m"], s) for s in sets]) for x in r["final"]]
    scored.sort(key=lambda x: -x["held"])
    return {"world": world, "seed": seed, "control": control, "kw": kw, "G": G, "history": [h["reward_mean"] for h in r["history"]], "len_final": r["history"][-1]["len_mean"],
            "pw_final": r["history"][-1]["persistent_words"], "persist_final": r["history"][-1]["persist"], "tops": [{"m": x["m"], "held": x["held"], "per_set": x["per_set"], "anc": x["anc"]} for x in scored[:top]],
            "pop_held_mean": float(np.mean([x["held"] for x in scored])), "final_pop": [{"m": x["m"], "anc": x["anc"]} for x in r["final"]]}


def crossed(run, world=None):
    w = world or run["world"]
    return bool(np.mean([t["held"] for t in run["tops"][:4]]) >= THRESH[w])
