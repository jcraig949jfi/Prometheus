"""B55 -- WIRING-WALL test: does the reach rate of keyed recall rise as the register-coupled chain shortens?

B54 preview: on a VM that auto-binds kv[word1] = word2 every tick, the 3-instruction straight-line reader
(IN tag -> rX; LDK rY, rX; OUT rY) is never found (0/2), although it scores 1.0 at every K. Hypothesis: a chain of
links coupled by matched register names, each link silent or harmful alone, is not reached. Three binding VMs differ
ONLY in the number of register-coupled links the read needs (op 2 replaced; auto-binding as B54):
  L3  LDK  r_a = kv[r_b]                      solution: IN; IN rX; LDK rY, rX; OUT rY      (tag must flow via rX)
  L2  LDK2 r_a = kv[inputs[0][1]] (implicit)  solution: LDK2 rY; OUT rY                     (one coupling: rY)
  L1  OUTK out ch0 <- kv[inputs[0][1]]        solution: OUTK                                (no register coupling)
Evolution: W2_K2-wide (B08K jitter), CMP3 search, N=200, E=16, G=300, 8 seeds per variant, FOUNDRY_C2; held-out
64 x 4 at K2/K3/K6. Keyed = K6 >= .9.
PREDICTION (written 2026-10-08 ~19:30Z): L1 >= 6/8, L2 >= 3/8, L3 <= 1/8.
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
from archaeon.wse import evolve as EV
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
NEW2 = {
    "L3": "            elif op == 2:\n                regs[a] = state.setdefault(\"kv\", {}).get(regs[bw % nr], 0)\n",
    "L2": ("            elif op == 2:\n                regs[a] = state.setdefault(\"kv\", {}).get(inputs[0][1], 0) "
           "if (inputs and len(inputs[0]) >= 2) else 0\n"),
    "L1": ("            elif op == 2:\n                if n_out and inputs and len(inputs[0]) >= 2:\n"
           "                    if len(outputs[0]) < out_cap:\n"
           "                        outputs[0].append(state.setdefault(\"kv\", {}).get(inputs[0][1], 0)); out_writes += 1\n"),
}


def build(variant):
    src = inspect.getsource(stockvm)
    assert src.count(OLD2) == 1 and src.count(HOOK) == 1
    src = src.replace(OLD2, NEW2[variant]).replace(HOOK, BIND)
    src = src.replace("from .affordances import", "from proteus.foundry.affordances import").replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_chain_" + variant)
    exec(compile(src, "archaeon_beta_chain_" + variant, "exec"), mod.__dict__)
    return mod


VMS = {v: build(v) for v in NEW2}
SOL = {"L3": _prog([(IN, 1, 0), (IN, 4, 0), (2, 6, 4), (OUT_, 6, 0), (HALT,)]),
       "L2": _prog([(2, 6, 0), (OUT_, 6, 0), (HALT,)]),
       "L1": _prog([(2, 0, 0), (HALT,)])}


def score_k(m, k, variant):
    EV.Player = VMS[variant].Player
    spec = TARGET if k == 2 else WorldSpec("K%d" % k, K=k, value_bits=4)
    r = sum(EV.evaluate(m, wide(episodes_for(spec, CAMPAIGN_SEED, "heldout", 7 + s, 64), ("b55", k, s)), rng_seed=7)["reward"]
            for s in range(4)) / 4
    EV.Player = stockvm.Player
    return round(r, 4)


def controls():
    out = {}
    for v in VMS:
        for sv in VMS:
            out["sol_%s_on_%s" % (sv, v)] = {"K%d" % k: score_k(manifest(SOL[sv], n_regs=8), k, v) for k in (2, 6)}
    return out


def train_eps(g, seed):
    return wide(episodes_for(TARGET, CAMPAIGN_SEED, "train", g * 100003 + seed, 16), ("b55t", g, seed))


def cell(job):
    v = job["variant"]
    EV.Player = VMS[v].Player
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b55", foundry=FOUNDRY_C2)
    first = None
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        if first is None and row["best_reward"] >= .9:
            first = g
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    prof = {"K%d" % k: score_k(m, k, v) for k in (2, 3, 6)}
    return {"variant": v, "seed": job["seed"], "profile": prof, "keyed": prof["K6"] >= .9, "first_train_ge_.9": first,
            "elite_op2": sum(1 for i in range(0, len(m["genome"]), 4) if m["genome"][i] % 25 == 2), "elite_manifest": m}


def main(argv):
    if not argv or argv[0] == "controls":
        r = controls(); print(json.dumps(r, indent=0)); (OUT / "B55_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8"); return 0
    G_ = int(argv[1]) if len(argv) > 1 else 300
    variants = argv[3].split(",") if len(argv) > 3 else ["L1", "L2", "L3"]
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[2]) if len(argv) > 2 else 12) as ex:
        futs = {ex.submit(cell, {"variant": v, "seed": 5501 + s, "G": G_}): (v, s) for s in range(8) for v in variants}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                v, s = futs[f]; r = {"variant": v, "seed": 5501 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B55_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: x for k, x in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {v: sum(r.get("variant") == v and r.get("keyed", False) for r in rows) for v in variants}
    print(json.dumps(summ), flush=True)
    (OUT / "B55_result.json").write_text(json.dumps({"probe": "B55", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
