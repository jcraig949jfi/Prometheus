"""B07 -- environmental scaffolding: can a withdrawn positional cue make content-addressed recall reachable?

B03 (2026-10-07): 0/24 summits on W2_K2 for BASE, HEAVY (heavy-tailed edit count) and RELOC (jump fix-up). Generic
variation does not cross the silent plateau (B02: ~5 behaviourally silent edits, then one jump). Change the WORLD
instead: give the intermediate structure something to do.

Scaffold: every ASK tick [2, tag] gains a third word, the POSITION hint: 0 if the asked stream was PUT first, 1 if
second. A program can then answer by DISPATCHING ON THE HINT (two value slots, no tag memory, no comparison). Withdraw
the hint: with probability 1 - p(g) the third word is a uniformly random 0/1 instead. A hint-dispatcher then scores
~.5 on unhinted asks; a program that compares the asked tag with the stored first tag scores 1.0 either
way, so as p falls, content addressing becomes the only route to the top and is ONE substitution away from hint
dispatch (read the stored tag and EQ instead of reading the hint word).

Arms (N=200, E=16, E0, FOUNDRY_C2, fresh CMP3 gen 0, G=400, 12 seeds each; the held-out readout is ALWAYS the plain
W2_K2 world with no third word -- the grammar's own held-out episodes):
  BASE      p = 0 throughout (third word random from generation 0: same input format, no information).
  SCAFFOLD  p = 1 for g < 100, linear 1 -> 0 over g in [100, 300), 0 for g >= 300.
  ALWAYS    p = 1 throughout (control: does the hint-dispatcher ever leave? expected: no, held-out stays ~.5).
Summit = held-out plain W2_K2 >= .90 (48 episodes). Also logged: best hinted-train reward, first gen best >= .90.

PREDICTIONS (before running): SCAFFOLD >= 3/12 summits; BASE 0/12; ALWAYS 0/12 on the plain held-out (it solves the
hinted task early, >= 8/12 reach train >= .90 by g 100). If SCAFFOLD = 0/12 while ALWAYS solves the hinted task,
the "one substitution away" step is itself not crossed and the plateau is not about silent structure alone.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SUMMIT, TARGET
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import K_ASK, Episode, episodes_for

OUT = Path(__file__).resolve().parent / "results"


def p_of(arm, g):
    if arm == "BASE":
        return 0.0
    if arm == "ALWAYS":
        return 1.0
    if g < 100:
        return 1.0
    if g < 300:
        return 1.0 - (g - 100) / 200
    return 0.0


def hinted(eps, p, key):
    rng = SplitMix64(seed_from("archaeon.beta.b07.hint", *key))
    out = []
    for ep in eps:
        first_tag = None
        ticks = []
        for tk in ep.ticks:
            tk = list(tk)
            if tk and tk[0] == 1 and first_tag is None:
                first_tag = tk[1]
            if tk and tk[0] == K_ASK:
                pos = 0 if tk[1] == first_tag else 1
                tk = tk + [pos if rng.unit() < p else rng.randbelow(2)]
            ticks.append(tk)
        out.append(Episode(ticks=ticks, expected=dict(ep.expected), intervention_tick=ep.intervention_tick, meta=dict(ep.meta)))
    return out


def cell(job):
    arm, seed, G_ = job["arm"], job["seed"], job["G"]
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b07", foundry=FOUNDRY_C2)
    ho = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    first_train = first_summit = None
    best, ho_trace = [], {}
    for g in range(G_):
        eps = hinted(ev.episodes(), p_of(arm, g), (seed, g, arm))
        row = ev.evaluate_generation(episodes=eps, last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if first_train is None and row["best_reward"] >= SUMMIT:
            first_train = g
        if g % 25 == 0 or g == G_ - 1 or (row["best_reward"] >= SUMMIT and first_summit is None):
            h = evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"]
            ho_trace[str(g)] = round(h, 4)
            if first_summit is None and h >= SUMMIT and p_of(arm, g) == 0.0:
                first_summit = g
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    final_ho = evaluate(elite, ho, rng_seed=7)["reward"]
    if first_summit is None and final_ho >= SUMMIT:
        first_summit = G_ - 1
    return {"arm": arm, "seed": seed, "first_train_ge_.90": first_train, "first_summit_gen": first_summit,
            "final_heldout_plain": round(final_ho, 4), "heldout_trace": ho_trace, "trace_best": best,
            "elite_manifest": elite, "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 400
    jobs = [{"arm": a, "seed": s, "G": G_} for s in range(701, 713) for a in ("SCAFFOLD", "BASE", "ALWAYS")]
    rows = []
    with ProcessPoolExecutor(max_workers=24) as ex:
        futs = {ex.submit(cell, j): j for j in jobs}
        from concurrent.futures import as_completed
        for f in as_completed(futs):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("arm", "seed", "first_train_ge_.90", "first_summit_gen", "final_heldout_plain", "wall_s")}), flush=True)
    summ = {a: {"n": sum(r["arm"] == a for r in rows), "summits": sum(r["arm"] == a and r["first_summit_gen"] is not None for r in rows),
                "train_ge_.90": sum(r["arm"] == a and r["first_train_ge_.90"] is not None for r in rows)} for a in ("SCAFFOLD", "BASE", "ALWAYS")}
    print(json.dumps(summ), flush=True)
    (OUT / "B07_result.json").write_text(json.dumps({"probe": "B07", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
