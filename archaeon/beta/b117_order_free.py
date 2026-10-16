"""B117 -- remove the ORDER coupling too: is the read then L2-like? (Finding 3 open question 1)

B55/B56: keyed recall by read-chain length: L1 8/8 (gen ~1), L2 8/8 (~8), L3 2-3/8 (~44-203).
B57 (L3f: every IN also writes r0): 6/8, median ~72. The remaining constraint is ORDER (the tag must be the LAST IN
before LDK).
L3o VM = the L3 VM (LDK r_a = kv[r_b]; auto-binding kv[word1] = word2) plus: at tick start r0 = the tick's word 1
(the tag), before any instruction runs. No IN is needed and there is no order constraint. Solution:
LDK rY, r0; OUT rY. That is L2 (LDK2 rY; OUT rY) plus exactly ONE register-name coupling (LDK's source = r0).
Same world (W2_K2-wide), search, scrubbed gen 0 (B56), held-out 64 x 4; 8 seeds 11701-11708; G=300.
Control: the hand L3o solution is keyed (K2/K6 >= .9) on the L3o VM.
PREDICTION (committed before running), order-is-the-remaining-cost hypothesis: L3o >= 7/8 keyed AND median first
solve <= 30 generations (L2-like). If L3o ~ L3f (<= 6/8 or median > 30), then a single register coupling inside
LDK costs as much as the order constraint, and the cost is per coupling, not specific to order.
"""
import inspect
import json
import sys
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import proteus.foundry.vm as stockvm

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, HALT, OUT_, REGIMES, TARGET, _prog, manifest
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.beta.b54_sensory_binding import BIND, HOOK, OLD2
from archaeon.beta.b55_chain_length import NEW2, train_eps
from archaeon.beta.b56_chain_length_from_scratch import scrubbed_gen0
from archaeon.wse import evolve as EV
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
OLD_R = "        regs = state[\"regs\"]\n"
NEW_R = "        regs = state[\"regs\"]\n        if inputs and len(inputs[0]) >= 2:\n            regs[0] = inputs[0][1] & MASK32\n"


def build():
    src = inspect.getsource(stockvm)
    assert src.count(OLD2) == 1 and src.count(HOOK) == 1 and src.count(OLD_R) == 1
    src = src.replace(OLD2, NEW2["L3"]).replace(HOOK, BIND).replace(OLD_R, NEW_R)
    src = src.replace("from .affordances import", "from proteus.foundry.affordances import").replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_l3o")
    exec(compile(src, "archaeon_beta_l3o", "exec"), mod.__dict__)
    return mod


L3O = build()
SOL = _prog([(2, 6, 0), (OUT_, 6, 1), (HALT,)])                     # LDK r6, r0; OUT r6 (channel r1 == 0); HALT


def score_k(m, k):
    EV.Player = L3O.Player
    spec = TARGET if k == 2 else WorldSpec("K%d" % k, K=k, value_bits=4)
    r = sum(EV.evaluate(m, wide(episodes_for(spec, CAMPAIGN_SEED, "heldout", 7 + s, 64), ("b117", k, s)), rng_seed=7)["reward"]
            for s in range(4)) / 4
    EV.Player = stockvm.Player
    return round(r, 4)


def cell(job):
    EV.Player = L3O.Player
    pop = scrubbed_gen0(job["seed"], 200)
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b117", foundry=FOUNDRY_C2,
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
        r = {"L3o_solution": {"K%d" % k: score_k(manifest(SOL, n_regs=8), k) for k in (2, 6)}}
        print(json.dumps(r)); return 0
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"seed": 11701 + s, "G": G_}): s for s in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 11701 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B117_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: x for k, x in r.items() if k != "elite_manifest"}) + chr(10))
    ks = sorted(r["first_train_ge_.9"] for r in rows if r.get("keyed"))
    summ = {"keyed": len(ks), "first_gens": ks, "median_first": ks[len(ks) // 2] if ks else None}
    summ["pred"] = len(ks) >= 7 and summ["median_first"] is not None and summ["median_first"] <= 30
    print(json.dumps(summ), flush=True)
    (OUT / "B117_result.json").write_text(json.dumps({"probe": "B117", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
