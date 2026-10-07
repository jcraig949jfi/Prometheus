"""B08K -- ruler repair: re-score every B08J solved elite under WIDE jitter (0-7 NOISE ticks before each ask).

Two weak signals (B13 queue .79, B21 .82) were LAG-WINDOW timing exploits that the 0-3 jitter ruler could not
reject: they score 1.0 when the first ask comes within 0-2 extra ticks and fall to the shelf beyond. Any count of
"genuine memory" made with 0-3 jitter (B08J L1 7, L3 8, L2 5 solved) may be inflated. Re-score each B08J solved
elite plus hand controls (slot solver, indexed solver) under 0-7 jitter; genuine = held-out >= .90 under 0-7.
"""
import json
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import SOLVER, manifest
import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b20_hash_neighbourhood import MANIFEST as INDEXED
from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import K_NOISE, Episode

OUT = Path(__file__).resolve().parent / "results"
_plain = B.eps_for


def wide(eps, key, kmax=7):
    rng = SplitMix64(seed_from("archaeon.beta.b08k", *key))
    out = []
    for ep in eps:
        ticks, exp = [], {}
        for i, tk in enumerate(ep.ticks):
            if i in ep.expected:
                for _ in range(rng.randbelow(kmax + 1)):
                    ticks.append([K_NOISE, rng.next_u32(), rng.next_u32()])
            ticks.append(list(tk))
            if i in ep.expected:
                exp[len(ticks) - 1] = ep.expected[i]
        out.append(Episode(ticks=ticks, expected=exp, intervention_tick=ep.intervention_tick, meta=dict(ep.meta)))
    return out


def main():
    d = json.loads((OUT / "B08J_result.json").read_text(encoding="utf-8"))
    rows = []
    for rung in ("L1_one", "L3_last", "L2_first", "L4_order"):
        eps = wide(_plain(rung, "heldout", 7, 96), ("b08k", rung))
        for name, m in (("hand_slot_solver", manifest(SOLVER)), ("hand_indexed", INDEXED)):
            rows.append({"rung": rung, "who": name, "wide": round(evaluate(m, eps, rng_seed=7)["reward"], 4)})
        for r in d["rows"]:
            if r["rung"] == rung and r["solved_gen"] is not None:
                rows.append({"rung": rung, "who": "B08J_seed%d" % r["seed"], "wide": round(evaluate(r["elite_manifest"], eps, rng_seed=7)["reward"], 4)})
    summ = {}
    for rung in ("L1_one", "L3_last", "L2_first"):
        ev = [x for x in rows if x["rung"] == rung and x["who"].startswith("B08J")]
        summ[rung] = {"solved_0_3": len(ev), "genuine_0_7": sum(x["wide"] >= .90 for x in ev), "wide": [x["wide"] for x in ev]}
    print(json.dumps(summ))
    print(json.dumps([x for x in rows if x["who"].startswith("hand")]))
    (OUT / "B08K_result.json").write_text(json.dumps({"probe": "B08K", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
