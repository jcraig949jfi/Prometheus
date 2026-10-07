"""B11 -- is the W2_K2 SHELF a delay line? (Phase 2-B Beta)

On W2_K2 the ticks are PUT, PUT, ASK, ASK with the asks in random order. A 2-tick delay line answers ask 1 with the
first value and ask 2 with the second, so it is right exactly when the ask order matches the put order: ~.5, the
shelf. B11 scores the 72 B03 final elites (the current search's shelf, all arms) and the hand-written one-slot shelf
program on W2_K2 plain vs jittered (0-3 NOISE ticks before each ask). Also: the share of correct answers that came
from the stream PUT 2 ticks earlier ("delay-consistent").
PREDICTION (before running): >= 90% of B03 elites drop by >= .15 under jitter; the hand one-slot program does not.
"""
import json
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, SHELF, TARGET, manifest
from archaeon.beta.b08b_delay_line_check import jitter
from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import episodes_for

OUT = Path(__file__).resolve().parent / "results"


def main():
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 7, 48)
    jit = jitter(eps, ("b11",))
    b3 = json.loads((OUT / "B03_result.json").read_text(encoding="utf-8"))
    rows = [{"who": "hand_one_slot_shelf", "plain": evaluate(manifest(SHELF), eps, rng_seed=7)["reward"],
             "jitter": evaluate(manifest(SHELF), jit, rng_seed=7)["reward"]}]
    for r in b3["rows"]:
        m = r.get("final_manifest") or r.get("summit_manifest")
        rows.append({"who": "B03_%s_%d" % (r["arm"], r["seed"]), "plain": round(evaluate(m, eps, rng_seed=7)["reward"], 4),
                     "jitter": round(evaluate(m, jit, rng_seed=7)["reward"], 4)})
    ev = [x for x in rows if x["who"].startswith("B03")]
    drop = [x["plain"] - x["jitter"] for x in ev]
    summ = {"n": len(ev), "mean_plain": round(sum(x["plain"] for x in ev) / len(ev), 4),
            "mean_jitter": round(sum(x["jitter"] for x in ev) / len(ev), 4),
            "share_drop_ge_.15": round(sum(d >= .15 for d in drop) / len(ev), 4), "hand_shelf": rows[0]}
    print(json.dumps(summ))
    (OUT / "B11_result.json").write_text(json.dumps({"probe": "B11", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
