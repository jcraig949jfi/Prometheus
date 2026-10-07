"""B20 -- single-operator neighbourhood of the 11-instruction tag-indexed solver (cf. B01-B for the slot solver).

Light probe. 2,000 grammar-v0.4 children of the indexed solver (tape 4096, persist tape), held-out on jittered W2_K2.
Bins as B01-B. Also: share of children landing at shelf level [.45, .62) -- near-misses selection could hold.
PREDICTION (before running): neutral share lower than the slot solver's .335 (the write/read pair is coupled through
one tag register, so most edits touching it are lethal); shelf share < .10.
"""
import json
from collections import Counter
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend

from archaeon.beta.b01_w2k2_existence import _prog, IN, LDC, EQ, JZ, OUT_, HALT
from archaeon.beta.b08j_jittered_ladder import jittered
from archaeon.wse.evolve import evaluate

OUT = Path(__file__).resolve().parent / "results"
LD, ST = 5, 6
HASH = _prog([(IN, 1, 0), (IN, 4, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 4), (IN, 5, 0), (ST, 4, 5), (HALT,),
              (LD, 6, 4), (OUT_, 6, 0), (HALT,)])
MANIFEST = {"schema_version": "proteus.player_manifest.v0", "n_regs": 8, "tape_words": 4096, "genome": HASH,
            "code_writable": False, "persist": "tape", "tick_budget": 32, "out_cap": 1}


def main(n=2000):
    eps = jittered("L6_w2k2", "heldout", 7, 48)
    parent = G.organism_record(MANIFEST, None, 0)
    base = evaluate(MANIFEST, eps, rng_seed=7)["reward"]
    bins, by_op = Counter(), {}
    for s in range(n):
        child, rec = descend(parent, 2_000_000 + s)
        r = evaluate(child["manifest"], eps, rng_seed=7)["reward"]
        k = "neutral_ge_.90" if r >= .9 else "mid_.62_.90" if r >= .62 else "shelf_.45_.62" if r >= .45 else "below_.45"
        bins[k] += 1
        op = rec["operators"][0].get("operator")
        d = by_op.setdefault(op, {"n": 0, "neutral": 0}); d["n"] += 1; d["neutral"] += r >= .9
    out = {"probe": "B20", "parent_heldout": base, "n": n, "bins": dict(bins), "neutral_share": bins["neutral_ge_.90"] / n,
           "shelf_share": bins["shelf_.45_.62"] / n, "by_operator": by_op}
    print(json.dumps({k: out[k] for k in ("parent_heldout", "bins", "neutral_share", "shelf_share")}))
    (OUT / "B20_result.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
