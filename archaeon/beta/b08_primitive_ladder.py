"""B08 -- which memory PRIMITIVE is the wall? A ladder of minimal worlds (Phase 2-B Beta)

B07 (partial, 2026-10-07 ~01:00Z): even the ALWAYS-hinted arm, where the third word says which slot to answer from,
never reached train >= .90. So the wall is earlier than content addressing. Every rung below is a transform of the
SAME W2_K2 episodes (two tagged PUTs, then asks), so the input distribution is fixed and only the demand changes:

  L1_one     one PUT stream only (K=1 world)                       primitive: store + recall one value
  L3_last    two PUTs, one ask: the stream PUT LAST                primitive: overwrite-store (the shelf)
  L2_first   two PUTs, one ask: the stream PUT FIRST               primitive: write-once GUARD (do not overwrite)
  L4_order   two PUTs, two asks in fixed order first, then last    primitive: TWO SLOTS + ask counter
  L5_hint    W2_K2 asks (random order) + exact position hint       primitive: two slots + dispatch on a cue
  L6_w2k2    plain W2_K2                                           primitive: two slots + content addressing
Hand-written controls are scored on every rung (shelf program, B01 solver, B07 hint dispatcher).

Search: CMP3 config (N=200, E=16, E0, FOUNDRY_C2), fresh gen 0, G=200, 8 seeds per rung. Solved = train best >= .90
and confirmed on 48 held-out episodes of the same rung.

PREDICTION (before running): L1, L3 solved >= 7/8; L2 (guard) >= 4/8; L4, L5, L6 <= 1/8 -> the wall is the
SECOND SLOT, not the guard and not the addressing.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import (CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SHELF, SOLVER, TARGET, EQ, HALT, IN,
                                              JNZ, JZ, LDC, MOV, OUT_, _prog, manifest)
from archaeon.beta.b07_scaffold_withdrawal import hinted
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import K_ASK, Episode, WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
HINT_DISPATCH = _prog([(IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 10), (IN, 4, 0), (IN, 5, 0), (JNZ, 6, 4), (MOV, 6, 4),
                       (MOV, 7, 5), (HALT,), (MOV, 8, 4), (MOV, 9, 5), (HALT,), (IN, 4, 0), (IN, 3, 0), (JNZ, 3, 3),
                       (OUT_, 7, 0), (HALT,), (OUT_, 9, 0), (HALT,)])
K1 = WorldSpec("W0_K1", K=1, value_bits=4)


def transform(rung, eps):
    if rung == "L1_one":
        return eps                                    # caller supplies K=1 episodes
    if rung == "L6_w2k2":
        return eps
    if rung == "L5_hint":
        return hinted(eps, 1.0, ("b08",))
    out = []
    for ep in eps:
        puts = [tk for tk in ep.ticks if tk and tk[0] == 1]
        first, last = puts[0][1], puts[-1][1]
        head = [tk for i, tk in enumerate(ep.ticks) if i not in ep.expected]
        asks = {ep.ticks[i][1]: (ep.ticks[i], ep.expected[i]) for i in ep.expected}
        if rung == "L3_last":
            order = [last]
        elif rung == "L2_first":
            order = [first]
        elif rung == "L4_order":
            order = [first, last]
        else:
            raise ValueError(rung)
        ticks, exp = list(head), {}
        for t in order:
            ticks.append(list(asks[t][0])); exp[len(ticks) - 1] = asks[t][1]
        out.append(Episode(ticks=ticks, expected=exp, intervention_tick=ep.intervention_tick, meta=dict(ep.meta)))
    return out


def eps_for(rung, family, index, n):
    spec = K1 if rung == "L1_one" else TARGET
    return transform(rung, episodes_for(spec, CAMPAIGN_SEED, family, index, n))


RUNGS = ("L1_one", "L3_last", "L2_first", "L4_order", "L5_hint", "L6_w2k2")


def controls():
    progs = {"shelf": SHELF, "solver": SOLVER, "hint_dispatch": HINT_DISPATCH}
    return {name: {r: round(evaluate(manifest(g), eps_for(r, "heldout", 7, 48), rng_seed=7)["reward"], 4) for r in RUNGS}
            for name, g in progs.items()}


def cell(job):
    rung, seed, G_ = job["rung"], job["seed"], job["G"]
    t0 = time.time()
    ev = Evolution(K1 if rung == "L1_one" else TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b08",
                   foundry=FOUNDRY_C2)
    ho = eps_for(rung, "heldout", seed, 48)
    solved = None; best = []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=eps_for(rung, "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= SOLVED and evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"] >= SOLVED:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    final = evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"]
    return {"rung": rung, "seed": seed, "solved_gen": solved, "final_heldout": round(final, 4), "max_train": max(best),
            "elite_manifest": ev.scored[0][1]["manifest"], "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 200
    ctl = controls()
    print("controls", json.dumps(ctl), flush=True)
    jobs = [{"rung": r, "seed": s, "G": G_} for s in range(801, 809) for r in RUNGS]
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 24) as ex:
        for f in as_completed([ex.submit(cell, j) for j in jobs]):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("rung", "seed", "solved_gen", "final_heldout", "max_train", "wall_s")}), flush=True)
    summ = {r: {"solved": sum(x["rung"] == r and x["solved_gen"] is not None for x in rows),
                "gens": sorted(x["solved_gen"] for x in rows if x["rung"] == r and x["solved_gen"] is not None)} for r in RUNGS}
    print(json.dumps(summ), flush=True)
    (OUT / "B08_result.json").write_text(json.dumps({"probe": "B08", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
