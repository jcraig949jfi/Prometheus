"""B01 -- is the W2_K2 ceiling an ORGANISM limit or a SEARCH limit? (Phase 2-B Beta, first EXP window)

Background (forensic dossier docs/phase3/intake/sisyphus/seats/Archaeon.md s5): in CMP1-CMP3 the two-stream
keyed-memory cell W2_K2 (K=2, D=1, 4-bit values) was never summited in 60 runs; shelf elites remember ONE value.
The organism and the search were never varied separately, so the ceiling is unattributed.

Cheapest discriminator, four parts, all on the frozen CMP3 evaluator/search (archaeon.wse.evolve, E0, FOUNDRY_C2):
  A  EXISTENCE: a hand-written 20-instruction Proteus program (two tag/value slots in registers, persist=all)
     scored on train and held-out episodes. If it fails, the organism is the limit as specified.
  B  NEIGHBOURHOOD: 2,000 single-operator children of the solver under grammar v0.4; held-out reward histogram.
  C  SHELF REFERENCE: the hand-written one-slot program (remember the last PUT) -- the shelf the GA found.
  D  RE-CLIMB: GA cells (N=200, E=16, G=60) whose gen 0 holds 4 copies of the solver damaged by k operators,
     k in {1,2,4,8,16}, 3 cell seeds each. Summit = held-out >= 0.90 on 48 episodes (CMP3 rule).

PREDICTIONS (written before the first run, 2026-10-07):
  A  held-out 1.000 (the program is exact by construction).
  B  neutral share (held-out >= .90) between .30 and .70; the rest mostly at .50 or below.
  C  held-out ~ .50.
  D  k=1,2 re-summit in >= 5/6 cells; k=16 in <= 1/3 of cells. If k=1 does NOT re-summit, selection on E=16
     training episodes cannot hold a summit, and the ceiling is a SELECTION/EVALUATION limit, not reachability.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend

from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_SEED
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, common_fill, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
SUMMIT = 0.90

NOP, HALT, LDC, MOV, EQ, JZ, JNZ, IN, OUT_ = 0, 1, 3, 4, 16, 19, 20, 21, 23


def _prog(instrs):
    return [w for ins in instrs for w in (list(ins) + [0, 0, 0])[:4]]


def manifest(genome, n_regs=10):
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": n_regs, "tape_words": 128, "genome": genome,
            "code_writable": False, "persist": "all", "tick_budget": 64, "out_cap": 1}


# r0 = 0 is the input/output channel; r1 kind; r3 test; r4 tag; r5 value; slots (r6,r7) and (r8,r9).
SOLVER = _prog([
    (IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 10),            # 0-3   kind == PUT ?  else -> 13
    (IN, 4, 0), (IN, 5, 0), (JNZ, 6, 4),                              # 4-6   slot A taken -> 10
    (MOV, 6, 4), (MOV, 7, 5), (HALT,),                                # 7-9   fill slot A
    (MOV, 8, 4), (MOV, 9, 5), (HALT,),                                # 10-12 fill slot B
    (IN, 4, 0), (EQ, 3, 4, 6), (JZ, 3, 3), (OUT_, 7, 0), (HALT,),     # 13-17 ASK: tag == A -> out A
    (OUT_, 9, 0), (HALT,),                                            # 18-19 else out B
])
SHELF = _prog([
    (IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 5),               # 0-3   kind == PUT ? else -> 8
    (IN, 4, 0), (IN, 7, 0), (HALT,), (NOP,),                          # 4-7   remember the last value
    (OUT_, 7, 0), (HALT,),                                            # 8-9
])


def heldout(m, seed=7, n=48, vocab="train"):
    spec = TARGET if vocab == "train" else WorldSpec("W2_K2", K=2, value_bits=4, vocab=vocab)
    return evaluate(m, episodes_for(spec, CAMPAIGN_SEED, "heldout", seed, n), rng_seed=7)


def part_a():
    m = manifest(SOLVER)
    tr = evaluate(m, episodes_for(TARGET, CAMPAIGN_SEED, "train", 0, 16), rng_seed=7)
    hos = [heldout(m, seed=s)["reward"] for s in range(5)]
    sh = manifest(SHELF)
    return {"solver_genome_words": len(SOLVER), "solver_train": tr["reward"], "solver_heldout_5seeds": hos,
            "solver_heldout_episode_mode": heldout(m)["reward_episode"],
            "shelf_heldout_5seeds": [heldout(sh, seed=s)["reward"] for s in range(5)],
            "shelf_per_ask": heldout(sh)["per_ask_reward"]}


def part_b(n=2000):
    parent = G.organism_record(manifest(SOLVER), None, 0)
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 7, 48)
    rows = []
    for s in range(n):
        child, rec = descend(parent, s)
        r = evaluate(child["manifest"], eps, rng_seed=7)["reward"]
        rows.append({"op": rec["operators"][0].get("operator"), "r": round(r, 4)})
    bins = {"neutral_ge_.90": 0, "mid_.55_.90": 0, "shelf_.45_.55": 0, "below_.45": 0}
    by_op = {}
    for x in rows:
        r = x["r"]
        k = "neutral_ge_.90" if r >= .9 else "mid_.55_.90" if r >= .55 else "shelf_.45_.55" if r >= .45 else "below_.45"
        bins[k] += 1
        d = by_op.setdefault(x["op"], {"n": 0, "neutral": 0})
        d["n"] += 1; d["neutral"] += r >= .9
    return {"n": n, "bins": bins, "neutral_share": bins["neutral_ge_.90"] / n, "by_operator": by_op}


def damaged(k, idx):
    parent = G.organism_record(manifest(SOLVER), None, 0)
    child, _ = descend(parent, 1_000_000 + 1000 * k + idx, n_ops=k)
    return child["manifest"]


def run_cell(job):
    k, seed, G_ = job["k"], job["seed"], job["G"]
    t0 = time.time()
    subs = [damaged(k, i) for i in range(4)]
    sub_ho = [round(heldout(m)["reward"], 4) for m in subs]
    init, prov = common_fill(CAMPAIGN_SEED, seed, 200, subs, tag="damaged", foundry=FOUNDRY_C2)
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b01-k%d" % k,
                   foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov)
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    first = None; best = []
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        best.append(row["best_reward"])
        if first is None and row["best_reward"] >= SUMMIT:
            if evaluate(ev.scored[0][1]["manifest"], eps, rng_seed=7)["reward"] >= SUMMIT:
                first = g
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    final_ho = evaluate(res["elite"]["manifest"], eps, rng_seed=7)["reward"]
    return {"k": k, "seed": seed, "damaged_heldout": sub_ho, "first_summit_gen": first, "final_heldout": round(final_ho, 4),
            "trace_best": best, "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    out = {"probe": "B01", "campaign_seed": CAMPAIGN_SEED, "target": TARGET.knobs()}
    out["A"] = part_a(); print("A", json.dumps(out["A"]), flush=True)
    out["B"] = part_b(); print("B", json.dumps({k: out["B"][k] for k in ("bins", "neutral_share")}), flush=True)
    jobs = [{"k": k, "seed": s, "G": 60} for k in (1, 2, 4, 8, 16) for s in (101, 102, 103)]
    with ProcessPoolExecutor(max_workers=15) as ex:
        out["D"] = list(ex.map(run_cell, jobs))
    for r in out["D"]:
        print("D k=%d seed=%d damaged=%s first_summit=%s final=%.3f %ss" % (r["k"], r["seed"], r["damaged_heldout"],
              r["first_summit_gen"], r["final_heldout"], r["wall_s"]), flush=True)
    (OUT / "B01_result.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
