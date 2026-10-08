"""BEL-48H Window 5 plan, block 1 (exploratory; frozen by BEL_48H_PREREG.md s7 before any W5 run).

    python3 plan_w5.py OUT.json

E5a  COMPLEMENTATION REPAIR: does target material keep broken copiers producing functional offspring?
     SEEDED_REPLICATOR, ENDOGENOUS_PARTIAL, GRID WELL_MIXED, 500 ticks; mutation MED and HIGH; target_fill preserve vs
     zero (the kernel's ablation: unwritten child bytes are fresh zeros instead of the target's); 40 seed-pairs per
     mutation level (arms paired by seed; distinct seeds across levels).
E5b  CAUSAL ABLATION OF W2's COMPLEMENTATION: the H2 'A' world (prefix-writer fragment, PAIRED init, 300 ticks) under
     target_fill preserve vs zero, 40 seed-pairs.
Seeds: distinct per (block, level, k) (amendment 2)."""
import hashlib
import json
import pathlib
import sys

SEED_BASE = 49_000_000_000_000
BASE = dict(world="GRID", representation="Z80_64", layout="SHARED", reproduction="ENDOGENOUS_PARTIAL", pressure="IMPLICIT",
            spatial="WELL_MIXED", task="INC", scoring="ATOMIC", read_gate="ABR", env_dynamics="FIXED", mutation="BYTE",
            mutation_rate="MED", recombination="NONE", init="RANDOM", physics="v2", ticks=500, cells=256, budget=256)


def plan():
    sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
    from plan_w2 import fragments
    A, _B = fragments()
    P = []
    for li, lvl in enumerate(("MED", "HIGH")):
        for k in range(40):
            for arm in ("preserve", "zero"):
                P.append({"lane": "E5a", "cell": "SEEDED/PARTIAL/%s" % lvl, "arm": arm, "pair": k, "k": k, "kind": "heredity",
                          "seed": SEED_BASE + li * 10 ** 6 + k,
                          "cfg": dict(BASE, init="SEEDED_REPLICATOR", mutation_rate=lvl, target_fill=arm)})
    for k in range(40):
        for arm in ("preserve", "zero"):
            P.append({"lane": "E5b", "cell": "A/PARTIAL", "arm": arm, "pair": k, "k": k, "kind": "heredity",
                      "seed": SEED_BASE + 10 ** 9 + k,
                      "cfg": dict(BASE, init_tapes=[A], init_draws="PAIRED", ticks=300, target_fill=arm)})
    for i, p in enumerate(P):
        p["id"] = "w5_%05d" % i
    return P


if __name__ == "__main__":
    P = plan()
    b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b)
    print(len(P), hashlib.sha256(b).hexdigest())
