"""B57 -- direct test of the wiring mechanism: remove ONE register coupling from the 3-link read.

B55/B56: keyed recall on the sensory-binding VM is reached 8/8 with a 1- or 2-link read but 2-3/8 with the 3-link read
(IN tag -> rX; LDK rY, rX; OUT rY); waiting time ~10x per link. Prediction of that mechanism: provide one coupling for
free and the 3-link read behaves like a 2-link read.
L3f VM = the L3 VM (LDK r_a = kv[r_b]; auto-binding kv[word1] = word2) plus: every IN also writes the word it read into
r0. The solution becomes IN; IN; LDK rY, r0; OUT rY -- the tag no longer has to be routed to a register the program
chooses. Same world (W2_K2-wide), search, scrubbed gen 0 (B56), held-out 64 x 4; 8 seeds.
PREDICTION (before running): L3f >= 6/8 keyed, first solve median <= 30 generations (L2-like); L3 was 2/8 at 95-171.
"""
import inspect
import json
import sys
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import proteus.foundry.vm as stockvm

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, HALT, IN, OUT_, REGIMES, TARGET, _prog, manifest
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.beta.b54_sensory_binding import BIND, HOOK, OLD2
from archaeon.beta.b55_chain_length import NEW2, train_eps
from archaeon.beta.b56_chain_length_from_scratch import scrubbed_gen0
from archaeon.wse import evolve as EV
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
OLD_IN = "                        regs[a] = src[cur] & MASK32\n"
NEW_IN = "                        regs[a] = src[cur] & MASK32\n                        regs[0] = regs[a]\n"


def build():
    src = inspect.getsource(stockvm)
    assert src.count(OLD2) == 1 and src.count(HOOK) == 1 and src.count(OLD_IN) == 1
    src = src.replace(OLD2, NEW2["L3"]).replace(HOOK, BIND).replace(OLD_IN, NEW_IN)
    src = src.replace("from .affordances import", "from proteus.foundry.affordances import").replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_l3f")
    exec(compile(src, "archaeon_beta_l3f", "exec"), mod.__dict__)
    return mod


L3F = build()
SOL = _prog([(IN, 1, 1), (IN, 4, 1), (2, 6, 0), (OUT_, 6, 1), (HALT,)])   # channel reg r1 == 0 at tick start


def score_k(m, k):
    EV.Player = L3F.Player
    spec = TARGET if k == 2 else WorldSpec("K%d" % k, K=k, value_bits=4)
    r = sum(EV.evaluate(m, wide(episodes_for(spec, CAMPAIGN_SEED, "heldout", 7 + s, 64), ("b57", k, s)), rng_seed=7)["reward"]
            for s in range(4)) / 4
    EV.Player = stockvm.Player
    return round(r, 4)


def cell(job):
    EV.Player = L3F.Player
    pop = scrubbed_gen0(job["seed"], 200)
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b57", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance={"fill": "gen0 scrubbed", "verified_common": True})
    first = None
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        if first is None and row["best_reward"] >= .9:
            first = g
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    prof = {"K%d" % k: score_k(m, k) for k in (2, 3, 6)}
    return {"seed": job["seed"], "profile": prof, "keyed": prof["K6"] >= .9, "first_train_ge_.9": first, "elite_manifest": m}


def main(argv):
    if argv and argv[0] == "controls":
        r = {"L3f_solution": {"K%d" % k: score_k(manifest(SOL, n_regs=8), k) for k in (2, 6)}}
        print(json.dumps(r)); return 0
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"seed": 5701 + s, "G": G_}): s for s in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 5701 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B57_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: x for k, x in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {"keyed": sum(r.get("keyed", False) for r in rows), "first_gens": sorted(r["first_train_ge_.9"] for r in rows if r.get("keyed"))}
    print(json.dumps(summ), flush=True)
    (OUT / "B57_result.json").write_text(json.dumps({"probe": "B57", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
