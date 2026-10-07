"""B08b -- are B08's L4 solvers memory or a DELAY LINE? (Phase 2-B Beta)

Disassembly of the 4 evolved L4_order solvers (archaeon/beta/disasm.py) suggests a shift-register / delay-line
mechanism: answer = the input word from a fixed number of ticks earlier. L4's ticks are always PUT, PUT, ASK(first),
ASK(last), so a 2-tick delay line is exact. Check: score every evolved solver of every solved rung and the hand slot solver with 0-3 NOISE
ticks inserted (uniformly, independently) before each ask. A slot memory is unaffected; a delay line collapses.
"""
import json
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import SOLVER, manifest
from archaeon.beta.b08_primitive_ladder import eps_for
from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import K_NOISE, Episode

OUT = Path(__file__).resolve().parent / "results"


def jitter(eps, key):
    key = key if isinstance(key, tuple) else (key,)
    rng = SplitMix64(seed_from("archaeon.beta.b08b", *key))
    out = []
    for ep in eps:
        ticks, exp = [], {}
        for i, tk in enumerate(ep.ticks):
            if i in ep.expected:
                for _ in range(rng.randbelow(4)):
                    ticks.append([K_NOISE, rng.next_u32(), rng.next_u32()])
            ticks.append(list(tk))
            if i in ep.expected:
                exp[len(ticks) - 1] = ep.expected[i]
        out.append(Episode(ticks=ticks, expected=exp, intervention_tick=ep.intervention_tick, meta=dict(ep.meta)))
    return out


def main():
    d = json.loads((OUT / "B08_result.json").read_text(encoding="utf-8"))
    rows = []
    for rung in ("L1_one", "L3_last", "L2_first", "L4_order"):
        eps = eps_for(rung, "heldout", 7, 48)
        jit = jitter(eps, 1)
        rows.append({"rung": rung, "who": "hand_slot_solver", "plain": evaluate(manifest(SOLVER), eps, rng_seed=7)["reward"],
                     "jitter": evaluate(manifest(SOLVER), jit, rng_seed=7)["reward"]})
        for r in d["rows"]:
            if r["rung"] == rung and r["solved_gen"] is not None:
                m = r["elite_manifest"]
                rows.append({"rung": rung, "who": "B08_seed%d" % r["seed"], "plain": round(evaluate(m, eps, rng_seed=7)["reward"], 4),
                             "jitter": round(evaluate(m, jit, rng_seed=7)["reward"], 4)})
    for x in rows:
        print(json.dumps(x))
    (OUT / "B08b_result.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
