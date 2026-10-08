"""B53 -- REPRESENTATION lever for the memory law: a KV-store organism (staged for the next budget window).

Memory law (B08J..B52): write-once state is reliable; keyed / update-on-condition state is rare or unreached across
VM, world, incentive, selection and mutation levers. The untried lever is REPRESENTATION: give the organism a memory
organ addressed by content, so "store by key" and "read by key" are single instructions.
  STK a  (op 24, was RND):   kv[r_a] = r_b                      (b = operand word 2, as a register)
  LDK a  (op 2,  was YIELD): r_a = kv.get(r_b, 0)
kv is a per-episode dict in the player state (created on first use; fresh_state gives a fresh one), persisting across
ticks within an episode regardless of the persist policy -- an ORGAN, not tape. Built from the stock VM source with
only those two branches replaced (asserted).
Controls: hand KV solver (IN kind; IN tag; PUT -> IN v; STK tag, v | ASK -> LDK r, tag; OUT r) on W2_K2 and K3/K4/K6/K8
(wide jitter, 64 x 4); slot solver on the KV VM (unchanged semantics); a delay line must not pass.
Evolution (next window): W2_K2-wide, 8 seeds, G=300, KV VM vs stock (B08J/B40 baselines).
PREDICTION (written now): KV VM >= 3/8 keyed solvers (K6 >= .9); if not, the wall is wiring, not the memory primitive.
"""
import inspect
import json
import sys
import types
from pathlib import Path

import proteus.foundry.vm as stockvm

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, EQ, HALT, IN, JZ, LDC, OUT_, SOLVER, TARGET, _prog, manifest
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.wse import evolve as EV
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
OLD24 = "            elif op == 24:\n                regs[a] = rng.next_u32()\n                rnd_draws += 1\n"
NEW24 = "            elif op == 24:\n                state.setdefault(\"kv\", {})[regs[a]] = regs[bw % nr]\n"
OLD2 = "            elif op == 2:\n                status = \"yield\"\n                ip = nip\n                break\n"
NEW2 = "            elif op == 2:\n                regs[a] = state.setdefault(\"kv\", {}).get(regs[bw % nr], 0)\n"
STK, LDK = 24, 2


def build_kv_vm():
    src = inspect.getsource(stockvm)
    assert src.count(OLD24) == 1 and src.count(OLD2) == 1, "stock VM changed"
    src = src.replace(OLD24, NEW24).replace(OLD2, NEW2)
    src = src.replace("from .affordances import", "from proteus.foundry.affordances import").replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_kvvm")
    exec(compile(src, "archaeon_beta_kvvm", "exec"), mod.__dict__)
    return mod


KVVM = build_kv_vm()
KV_SOLVER = _prog([(IN, 1, 0), (IN, 4, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 4), (IN, 5, 0), (STK, 4, 5), (HALT,),
                   (LDK, 6, 4), (OUT_, 6, 0), (HALT,)])


def score_k(m, k, vm):
    EV.Player = KVVM.Player if vm == "kv" else stockvm.Player
    spec = TARGET if k == 2 else WorldSpec("K%d" % k, K=k, value_bits=4)
    r = sum(EV.evaluate(m, wide(episodes_for(spec, CAMPAIGN_SEED, "heldout", 7 + s, 64), ("b53", k, s)), rng_seed=7)["reward"]
            for s in range(4)) / 4
    EV.Player = stockvm.Player
    return round(r, 4)


def controls():
    out = {}
    for name, m, vm in (("kv_solver/kv", manifest(KV_SOLVER, n_regs=8), "kv"), ("kv_solver/stock", manifest(KV_SOLVER, n_regs=8), "stock"),
                        ("slot_solver/kv", manifest(SOLVER), "kv")):
        out[name] = {"K%d" % k: score_k(m, k, vm) for k in (2, 3, 4, 6, 8)}
    return out


if __name__ == "__main__" and not (len(sys.argv) > 1 and sys.argv[1] == "exp"):
    r = controls(); print(json.dumps(r, indent=0))
    OUT.mkdir(exist_ok=True)
    (OUT / "B53_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- B53 EXP (next window, leased)
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402

from archaeon.beta.b01_w2k2_existence import FOUNDRY_C2, REGIMES  # noqa: E402


def train_eps(g, seed):
    return wide(episodes_for(TARGET, CAMPAIGN_SEED, "train", g * 100003 + seed, 16), ("b53t", g, seed))


def cell(job):
    vm, seed, G_ = job["vm"], job["seed"], job["G"]
    EV.Player = KVVM.Player if vm == "kv" else stockvm.Player
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b53", foundry=FOUNDRY_C2)
    for g in range(G_):
        ev.evaluate_generation(episodes=train_eps(g, seed), last=(g == G_ - 1))
        if g < G_ - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    prof = {"K%d" % k: score_k(m, k, vm) for k in (2, 3, 6)}
    g_ = m["genome"]
    return {"vm": vm, "seed": seed, "profile": prof, "keyed": prof["K6"] >= .9,
            "elite_STK": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == STK),
            "elite_LDK": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == LDK), "elite_manifest": m}


def main_exp(argv):
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"vm": v, "seed": 5301 + s, "G": G_}): (v, s) for s in range(8) for v in ("kv", "stock")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                v, s = futs[f]; r = {"vm": v, "seed": 5301 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B53_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {v: sum(r.get("vm") == v and r.get("keyed", False) for r in rows) for v in ("kv", "stock")}
    print(json.dumps(summ), flush=True)
    (OUT / "B53_result.json").write_text(json.dumps({"probe": "B53", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "exp":
    sys.exit(main_exp(sys.argv[2:]))
