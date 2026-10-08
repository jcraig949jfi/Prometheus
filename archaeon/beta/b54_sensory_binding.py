"""B54 -- isolate the READ half: a sensory-binding organ that writes keyed memory AUTOMATICALLY (staged for next window).

B22b: with a perfect write held for 250 generations, the matching read was never found. B53 preview: even with
single-instruction STK/LDK the organ is not adopted (wiring). B54 removes the write entirely from the organism's job.
The VM binds kv[word1] = word2 for EVERY tick that carries >= 3 input words, before the program runs -- generic (it
knows no event kinds: PUT [1, tag, v] binds tag -> v; NOISE [8, a, b] binds a -> b; ASK [2, tag] binds nothing).
LDK (op 2, was YIELD): r_a = kv.get(r_b, 0). STK is absent. So the full W2_K2 / K-anything solution is a straight-line
read every tick: IN kind; IN tag; LDK r, tag; OUT r -- no branch, no write wiring.
Controls: hand READER (above) on K2-K8 (wide jitter, 64 x 4); slot solver unchanged; stock-VM reader ~0.
PREDICTION (written now): >= 4/8 B54 seeds reach K6 >= .9. If the straight-line READ is not found even here, the
memory wall is in reading (output routing), not in writing or wiring the write.
"""
import inspect
import json
import sys
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import proteus.foundry.vm as stockvm

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, IN, OUT_, HALT, REGIMES, SOLVER, TARGET, _prog, manifest
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.wse import evolve as EV
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
OLD2 = "            elif op == 2:\n                status = \"yield\"\n                ip = nip\n                break\n"
NEW2 = "            elif op == 2:\n                regs[a] = state.setdefault(\"kv\", {}).get(regs[bw % nr], 0)\n"
HOOK = "        self.begin_tick(state)\n        t0 = time.perf_counter()\n"
BIND = ("        self.begin_tick(state)\n        if inputs and len(inputs[0]) >= 3:\n"
        "            state.setdefault(\"kv\", {})[inputs[0][1]] = inputs[0][2]\n        t0 = time.perf_counter()\n")
LDK = 2


def build():
    src = inspect.getsource(stockvm)
    assert src.count(OLD2) == 1 and src.count(HOOK) == 1, "stock VM changed"
    src = src.replace(OLD2, NEW2).replace(HOOK, BIND)
    src = src.replace("from .affordances import", "from proteus.foundry.affordances import").replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_bindvm")
    exec(compile(src, "archaeon_beta_bindvm", "exec"), mod.__dict__)
    return mod


BINDVM = build()
READER = _prog([(IN, 1, 0), (IN, 4, 0), (LDK, 6, 4), (OUT_, 6, 0), (HALT,)])


def score_k(m, k, vm):
    EV.Player = BINDVM.Player if vm == "bind" else stockvm.Player
    spec = TARGET if k == 2 else WorldSpec("K%d" % k, K=k, value_bits=4)
    r = sum(EV.evaluate(m, wide(episodes_for(spec, CAMPAIGN_SEED, "heldout", 7 + s, 64), ("b54", k, s)), rng_seed=7)["reward"]
            for s in range(4)) / 4
    EV.Player = stockvm.Player
    return round(r, 4)


def controls():
    return {name: {"K%d" % k: score_k(m, k, vm) for k in (2, 3, 6, 8)}
            for name, m, vm in (("reader/bind", manifest(READER, n_regs=8), "bind"), ("reader/stock", manifest(READER, n_regs=8), "stock"),
                                ("slot_solver/bind", manifest(SOLVER), "bind"))}


def train_eps(g, seed):
    return wide(episodes_for(TARGET, CAMPAIGN_SEED, "train", g * 100003 + seed, 16), ("b54t", g, seed))


def cell(job):
    EV.Player = BINDVM.Player
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b54", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    prof = {"K%d" % k: score_k(m, k, "bind") for k in (2, 3, 6)}
    g_ = m["genome"]
    return {"seed": job["seed"], "profile": prof, "keyed": prof["K6"] >= .9,
            "elite_LDK": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == LDK), "elite_manifest": m}


def main(argv):
    if not argv or argv[0] == "controls":
        r = controls(); print(json.dumps(r, indent=0)); (OUT / "B54_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8"); return 0
    G_ = int(argv[1]) if len(argv) > 1 else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[2]) if len(argv) > 2 else 8) as ex:
        futs = {ex.submit(cell, {"seed": 5401 + s, "G": G_}): s for s in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 5401 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B54_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {"keyed": sum(r.get("keyed", False) for r in rows), "n": len(rows)}
    print(json.dumps(summ), flush=True)
    (OUT / "B54_result.json").write_text(json.dumps({"probe": "B54", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
