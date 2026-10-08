"""B50 -- a SEARCH lever for the memory law: lexicase vs tournament selection on two genuinely stored values.

Memory law (B08J/B22b/B40/B45/B47/B49): write-once state is reachable; update-on-condition state is not, whatever the
VM, world or incentive. Untested: the SELECTION scheme. Lexicase selection picks parents by filtering the population
through the test CASES (here: each ask of each episode) in random order, keeping specialists that solve rarely-solved
cases -- a standard remedy when partial solutions are invisible in the mean.
World: B08J L4_order (two values, fixed ask order) with B08K WIDE jitter (0-7 NOISE ticks), train and held-out.
One GA loop for both arms (identical evaluation, grammar v0.4 descend, elitism 4 by mean, N=200, E=16 -> 32 cases,
G=300, FOUNDRY_C2 gen 0); arms differ ONLY in parent selection: TOURNAMENT (k=4 on mean) vs LEXICASE.
Held-out: 64 episodes x 4 seeds (B45 standard). Solved = held-out >= .90.
PREDICTION (before running): LEXICASE >= 2/8 solved, TOURNAMENT 0/8 (= B08J L4 0/8).
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2
from archaeon.beta.b08_primitive_ladder import eps_for as plain_eps
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.wse.evolve import evaluate, gen0
from proteus.foundry.vm import Player

OUT = Path(__file__).resolve().parent / "results"


def eps(family, index, n):
    return wide(plain_eps("L4_order", family, index, n), ("b50", family, index))


def case_vector(m, episodes):
    p = Player(m); v = []
    for ei, ep in enumerate(episodes):
        st = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ei))
        for ti, words in enumerate(ep.ticks):
            outs, _ = p.run_tick(st, [words], 1, rng)
            if ti in ep.expected:
                v.append(1 if (outs[0] and outs[0][0] == ep.expected[ti]) else 0)
    return v


def lexicase(pop, vecs, rng):
    idx = list(range(len(pop)))
    cases = list(range(len(vecs[0])))
    for i in range(len(cases) - 1, 0, -1):
        j = rng.randbelow(i + 1); cases[i], cases[j] = cases[j], cases[i]
    for c in cases:
        best = max(vecs[i][c] for i in idx)
        idx = [i for i in idx if vecs[i][c] == best]
        if len(idx) == 1:
            break
    return pop[idx[rng.randbelow(len(idx))]]


def tournament(pop, means, rng, k=4):
    best = None
    for _ in range(k):
        i = rng.randbelow(len(pop))
        if best is None or means[i] > means[best]:
            best = i
    return pop[best]


def heldout(m):
    return sum(evaluate(m, eps("heldout", 7 + k, 64), rng_seed=7)["reward"] for k in range(4)) / 4


def cell(job):
    rng = SplitMix64(seed_from("archaeon.beta.b50", job["seed"], job["arm"]))
    pop = gen0(CAMPAIGN_SEED, job["seed"], 200, FOUNDRY_C2)
    solved = None; best_trace = []
    for g in range(job["G"]):
        e = eps("train", g * 100003 + job["seed"], 16)
        vecs = [case_vector(o["manifest"], e) for o in pop]
        means = [sum(v) / len(v) for v in vecs]
        order = sorted(range(len(pop)), key=lambda i: -means[i])
        best_trace.append(round(means[order[0]], 4))
        if means[order[0]] >= .9 and solved is None and heldout(pop[order[0]]["manifest"]) >= .9:
            solved = g
            break
        new = [pop[i] for i in order[:4]]
        while len(new) < len(pop):
            parent = lexicase(pop, vecs, rng) if job["arm"] == "LEXICASE" else tournament(pop, means, rng)
            child, _ = descend(parent, rng.next_u64() & ((1 << 62) - 1))
            new.append(child)
        pop = new
    elite = pop[0]["manifest"] if solved is None else pop[order[0]]["manifest"]
    return {"arm": job["arm"], "seed": job["seed"], "solved_gen": solved, "heldout": round(heldout(elite), 4),
            "max_train": max(best_trace), "elite_manifest": elite}


def main(argv):
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 5001 + s, "G": G_}): (a, s) for s in range(8) for a in ("LEXICASE", "TOURNAMENT")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, s = futs[f]; r = {"arm": a, "seed": 5001 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B50_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {a: sum(r.get("arm") == a and r.get("solved_gen") is not None for r in rows) for a in ("LEXICASE", "TOURNAMENT")}
    print(json.dumps(summ), flush=True)
    (OUT / "B50_result.json").write_text(json.dumps({"probe": "B50", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
