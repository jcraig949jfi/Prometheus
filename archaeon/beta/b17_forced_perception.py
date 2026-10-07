"""B17 -- close the LATCH route: does forced perception open the two-value wall? (Phase 2-B Beta, world lane)

B16: 56% of genuine one-value organisms store the value by STOPPING PERCEPTION (read input on tick 0, then loop).
A latched organism cannot store a second value. World change: every PUT tick also carries an expected answer, the
ECHO of the value just put. An organism must read input on every PUT tick to score the echoes, so latching stops
paying from generation 0. The recall asks are unchanged; jitter (0-3 NOISE ticks before each ask) as in B08J.

  L4E   L4_order + echo on every PUT     (two values, fixed ask order)
  L6E   W2_K2 + echo on every PUT        (two values, random ask order)
Readout: RECALL reward only (ask ticks), so echoes cannot inflate the headline; echo reward reported separately.
Cells: {L4E, L6E} x 8 seeds, CMP3 search (N=200, E=16, E0, FOUNDRY_C2), training reward = per-ask over echoes AND
recall asks (the selective pressure), G=300.  Comparison: B08J L4 0/8, L6 0/8 (no echo).

PREDICTION (before running): L4E >= 2/8 recall-solved (>= .90 recall on held-out); L6E 0/8. If L4E stays 0/8 while
echoes are learned (echo reward >= .90), perception is not the missing piece and latching was a symptom, not a cause.
Status: STAGED for the next budget window (this seat is over the 24 h envelope until ~2026-10-08 00:00Z).
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b08j_jittered_ladder import jittered
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import Episode

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
BASE_RUNG = {"L4E": "L4_order", "L6E": "L6_w2k2"}


def with_echo(eps):
    out = []
    for ep in eps:
        exp = dict(ep.expected)
        for i, tk in enumerate(ep.ticks):
            if tk and tk[0] == 1:
                exp[i] = tk[2] if len(tk) > 2 else 0
        out.append(Episode(ticks=[list(t) for t in ep.ticks], expected=exp, intervention_tick=ep.intervention_tick,
                           meta=dict(ep.meta, recall_ticks=sorted(ep.expected))))
    return out


def recall_only(eps):
    return [Episode(ticks=e.ticks, expected={i: e.expected[i] for i in e.meta["recall_ticks"]},
                    intervention_tick=e.intervention_tick, meta=e.meta) for e in eps]


def echo_only(eps):
    return [Episode(ticks=e.ticks, expected={i: v for i, v in e.expected.items() if i not in e.meta["recall_ticks"]},
                    intervention_tick=e.intervention_tick, meta=e.meta) for e in eps]


def eps_for(world, family, index, n):
    return with_echo(jittered(BASE_RUNG[world], family, index, n))


def cell(job):
    world, seed, G_ = job["world"], job["seed"], job["G"]
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b17", foundry=FOUNDRY_C2)
    ho = eps_for(world, "heldout", seed, 48)
    ho_rec, ho_echo = recall_only(ho), echo_only(ho)
    solved, best = None, []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=eps_for(world, "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= SOLVED and evaluate(ev.scored[0][1]["manifest"], ho_rec, rng_seed=7)["reward"] >= SOLVED:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    return {"world": world, "seed": seed, "solved_gen": solved, "max_train": max(best),
            "recall_heldout": round(evaluate(elite, ho_rec, rng_seed=7)["reward"], 4),
            "echo_heldout": round(evaluate(elite, ho_echo, rng_seed=7)["reward"], 4), "elite_manifest": elite}


def controls():
    from archaeon.beta.b01_w2k2_existence import SOLVER, SHELF, manifest
    return {name: {w: {"recall": round(evaluate(manifest(g), recall_only(eps_for(w, "heldout", 7, 48)), rng_seed=7)["reward"], 4),
                       "echo": round(evaluate(manifest(g), echo_only(eps_for(w, "heldout", 7, 48)), rng_seed=7)["reward"], 4)}
                   for w in BASE_RUNG} for name, g in (("slot_solver", SOLVER), ("one_slot_shelf", SHELF))}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"world": w, "seed": s, "G": G_}): (w, s) for s in range(1701, 1709) for w in BASE_RUNG}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                      # noqa: BLE001
                w, s = futs[f]; r = {"world": w, "seed": s, "solved_gen": None, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B17_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {w: sum(r["world"] == w and r["solved_gen"] is not None for r in rows) for w in BASE_RUNG}
    print(json.dumps(summ), flush=True)
    (OUT / "B17_result.json").write_text(json.dumps({"probe": "B17", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
