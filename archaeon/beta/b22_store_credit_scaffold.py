"""B22 -- stepping stone for the coupled write/read pair: credit the WRITE half alone, then withdraw it.

B20: the 11-instruction indexed solver (ST [tag] on PUT, LD [tag] on ASK) is an isolated peak; each half is silent
alone, so selection has no partial credit. Environmental scaffold (directive: environmental scaffolding, withdrawn):
for g < 150 the fitness is the MEAN of (recall reward, STORE credit), STORE credit = share of PUT ticks after which
tape[tag mod tape_words] == value, outside the read-only code region. From g >= 150: recall reward only. The
held-out readout is always recall-only, on 0-7 jitter (the B08K ruler); training uses 0-7 jitter too.

Arms (jittered-wide L4_order and L6_w2k2, CMP3 search N=200, E=16, FOUNDRY_C2, G=300, 4 seeds, 2 procs):
  STORE    scaffold as above
  NONE     recall only throughout (= B08J on the wide ruler)
Controls before the run: hand indexed solver store-credit ~1, recall 1; hand slot solver store-credit ~0, recall 1;
one-slot shelf store-credit ~0.
PREDICTION (before running): STORE reaches store-credit >= .9 by g 150 in >= 3/4 cells per world; after withdrawal
recall-solved (>= .90 held-out) in >= 1/4 per world; NONE 0/4. If STORE learns the write but never the read, the
pair is not just "missing partial credit" -- the read half has its own isolated step.

B22b schedule (2026-10-07 ~11:30Z, after the first STORE cells): the write half IS learned under credit (store-credit
.91-.99 by g 100-125 in 2/4 STORE cells) but is LOST within 25 generations of withdrawal, before any read appears.
Arm KEEP: weight .5 for g < 150, then .2 permanently (recall carries .8) -- hold the write while the read is sought.
PREDICTION (B22b, before running): KEEP recall-solved >= 1/4 per world by G=400; store-credit stays >= .8 after 150.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Meter, Player

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SHELF, SOLVER, TARGET, manifest
from archaeon.beta.b08k_wide_jitter_rescore import _plain, wide
from archaeon.beta.b20_hash_neighbourhood import MANIFEST as INDEXED
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
SCAFFOLD_UNTIL = 150
_STATE = {"store_weight": 0.0}
_orig_evaluate = EV.evaluate
ARMS = ("STORE", "NONE")


def eps_for(rung, family, index, n):
    return wide(_plain(rung, family, index, n), ("b22", rung, family, index))


def store_credit(m, episodes, rng_seed=7):
    p = Player(m)
    n, glen = m["tape_words"], len(m["genome"])
    hit = puts = 0
    for ei, ep in enumerate(episodes):
        st = p.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ei))
        for words in ep.ticks:
            p.run_tick(st, [words], 1, rng, meter=None)
            if words and words[0] == 1 and len(words) >= 3:
                puts += 1
                a = words[1] % n
                if a >= glen and st["tape"][a] == words[2]:
                    hit += 1
    return hit / max(1, puts)


def scaffold_evaluate(manifest_, episodes, intervention=None, rng_seed=0, reward_mode="per_ask"):
    r = _orig_evaluate(manifest_, episodes, intervention=intervention, rng_seed=rng_seed, reward_mode=reward_mode)
    w = _STATE["store_weight"]
    if w > 0:
        sc = store_credit(manifest_, episodes, rng_seed=rng_seed)
        r = dict(r, recall_reward=r["reward"], store_credit=sc, reward=(1 - w) * r["reward"] + w * sc)
    return r


def controls():
    out = {}
    for rung in ("L4_order", "L6_w2k2"):
        eps = eps_for(rung, "heldout", 7, 48)
        out[rung] = {name: {"recall": round(_orig_evaluate(m, eps, rng_seed=7)["reward"], 4), "store": round(store_credit(m, eps), 4)}
                     for name, m in (("indexed", INDEXED), ("slot_solver", manifest(SOLVER)), ("shelf", manifest(SHELF)))}
    return out


def cell(job):
    EV.evaluate = scaffold_evaluate
    arm, rung, seed, G_ = job["arm"], job["rung"], job["seed"], job["G"]
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b22", foundry=FOUNDRY_C2)
    ho = eps_for(rung, "heldout", seed, 48)
    solved, trace = None, []
    for g in range(G_):
        if arm == "STORE":
            _STATE["store_weight"] = 0.5 if g < SCAFFOLD_UNTIL else 0.0
        elif arm == "KEEP":
            _STATE["store_weight"] = 0.5 if g < SCAFFOLD_UNTIL else 0.2
        else:
            _STATE["store_weight"] = 0.0
        row = ev.evaluate_generation(episodes=eps_for(rung, "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        elite = ev.scored[0][1]["manifest"]
        if g % 25 == 0 or g == G_ - 1:
            trace.append({"g": g, "best_fit": row["best_reward"], "elite_store": round(store_credit(elite, ho), 4),
                          "elite_recall": round(_orig_evaluate(elite, ho, rng_seed=7)["reward"], 4)})
        if g >= SCAFFOLD_UNTIL or arm == "NONE":
            if _orig_evaluate(elite, ho, rng_seed=7)["reward"] >= SOLVED:
                solved = g
                break
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    _STATE["store_weight"] = 0.0
    return {"arm": arm, "rung": rung, "seed": seed, "solved_gen": solved, "trace": trace,
            "final_recall": round(_orig_evaluate(elite, ho, rng_seed=7)["reward"], 4), "final_store": round(store_credit(elite, ho), 4),
            "elite_manifest": elite}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    global ARMS
    ARMS = tuple(argv[2].split(",")) if len(argv) > 2 else ("STORE", "NONE")
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 2) as ex:
        futs = {ex.submit(cell, {"arm": a, "rung": r, "seed": 2201 + s, "G": G_}): (a, r, s)
                for s in range(4) for r in ("L4_order", "L6_w2k2") for a in ARMS}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, rr, s = futs[f]; r = {"arm": a, "rung": rr, "seed": 2201 + s, "solved_gen": None, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / ("B22_cells.jsonl" if ARMS != ("KEEP",) else "B22b_cells.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {"%s/%s" % (a, r): sum(x["arm"] == a and x["rung"] == r and x["solved_gen"] is not None for x in rows)
            for a in ARMS for r in ("L4_order", "L6_w2k2")}
    print(json.dumps(summ), flush=True)
    (OUT / ("B22_result.json" if ARMS != ("KEEP",) else "B22b_result.json")).write_text(json.dumps({"probe": "B22", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
