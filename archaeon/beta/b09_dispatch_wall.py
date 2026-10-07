"""B09 -- the dispatch wall: reading the cue, or selecting on it? (Phase 2-B Beta)

B08 (2026-10-07): L4_order (two slots, asks in FIXED order) solved 4/8; L5_hint (two slots, random ask order, exact
position hint as the ASK's THIRD word) 0/8. The wall is between them: answering from one of two stored values
according to a DATA cue. Two readings:
  READ    the barrier is consuming an extra input word at the right point (the third word of the tick).
  SELECT  the barrier is conditional selection between two stored values, however the cue arrives.
Rungs (all on the same W2_K2 episodes, random ask order, CMP3 search N=200, E=16, G=200, 8 seeds):
  L5_hint3   hint as the third word [2, tag, h]              (B08's L5, replicated)
  L5_hint2   hint as the SECOND word [2, h, tag]             (the first word after the kind)
  L5_kind    hint folded into the KIND: [2, tag] if h=0, [10, tag] if h=1 (programs already branch on kind)
PREDICTION (before running): SELECT holds -- all three <= 1/8. If L5_kind >= 3/8, the barrier is not selection
but a SECOND independent condition on input content (kind is already the program's one learned branch).
Controls: hand programs for each format are scored before the run.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import (CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET, EQ, HALT, IN, JNZ, JZ, LDC, MOV,
                                              OUT_, _prog, manifest)
from archaeon.beta.b08_primitive_ladder import HINT_DISPATCH
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import K_ASK, Episode, episodes_for

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
RUNGS = ("L5_hint3", "L5_hint2", "L5_kind")


def transform(rung, eps):
    out = []
    for ep in eps:
        first = next(tk[1] for tk in ep.ticks if tk and tk[0] == 1)
        ticks = []
        for tk in ep.ticks:
            tk = list(tk)
            if tk and tk[0] == K_ASK:
                h = 0 if tk[1] == first else 1
                if rung == "L5_hint3":
                    tk = [K_ASK, tk[1], h]
                elif rung == "L5_hint2":
                    tk = [K_ASK, h, tk[1]]
                else:
                    tk = [K_ASK if h == 0 else 10, tk[1]]
            ticks.append(tk)
        out.append(Episode(ticks=ticks, expected=dict(ep.expected), intervention_tick=ep.intervention_tick, meta=dict(ep.meta)))
    return out


def eps_for(rung, family, index, n):
    return transform(rung, episodes_for(TARGET, CAMPAIGN_SEED, family, index, n))


# controls: hint2 dispatcher reads h right after kind; kind dispatcher branches on kind == 10
HINT2 = _prog([(IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 10), (IN, 4, 0), (IN, 5, 0), (JNZ, 6, 4), (MOV, 6, 4),
               (MOV, 7, 5), (HALT,), (MOV, 8, 4), (MOV, 9, 5), (HALT,), (IN, 3, 0), (0,), (JNZ, 3, 3),
               (OUT_, 7, 0), (HALT,), (OUT_, 9, 0), (HALT,)])
KINDD = _prog([(IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 10), (IN, 4, 0), (IN, 5, 0), (JNZ, 6, 4), (MOV, 6, 4),
               (MOV, 7, 5), (HALT,), (MOV, 8, 4), (MOV, 9, 5), (HALT,), (LDC, 2, 10), (EQ, 3, 1, 2), (JNZ, 3, 3),
               (OUT_, 7, 0), (HALT,), (OUT_, 9, 0), (HALT,)])


def controls():
    progs = {"hint3_dispatch": HINT_DISPATCH, "hint2_dispatch": HINT2, "kind_dispatch": KINDD}
    return {n: {r: round(evaluate(manifest(g), eps_for(r, "heldout", 7, 48), rng_seed=7)["reward"], 4) for r in RUNGS}
            for n, g in progs.items()}


def cell(job):
    rung, seed, G_ = job["rung"], job["seed"], job["G"]
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b09", foundry=FOUNDRY_C2)
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
    return {"rung": rung, "seed": seed, "solved_gen": solved, "max_train": max(best),
            "final_heldout": round(evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"], 4),
            "elite_manifest": ev.scored[0][1]["manifest"], "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 200
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 24) as ex:
        for f in as_completed([ex.submit(cell, {"rung": r, "seed": s, "G": G_}) for s in range(901, 909) for r in RUNGS]):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("rung", "seed", "solved_gen", "final_heldout", "max_train", "wall_s")}), flush=True)
    summ = {r: {"solved": sum(x["rung"] == r and x["solved_gen"] is not None for x in rows),
                "gens": sorted(x["solved_gen"] for x in rows if x["rung"] == r and x["solved_gen"] is not None)} for r in RUNGS}
    print(json.dumps(summ), flush=True)
    (OUT / "B09_result.json").write_text(json.dumps({"probe": "B09", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
