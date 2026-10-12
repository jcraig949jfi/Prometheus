"""BEL-48H Window 5 block 2 (exploratory; frozen by BEL_48H_PREREG.md s8 before any run).

    python3 plan_w5b2.py OUT.json

E5c  REACHABILITY CONSEQUENCE OF TARGET MATERIAL: fresh RANDOM worlds, ENDOGENOUS_PARTIAL, GRID WELL_MIXED, 500 ticks,
     target_fill preserve vs zero, 200 seed-pairs (arms paired by seed = same initial population), OriginWorld."""
import hashlib, json, sys
from plan_w5 import BASE
SEED_BASE = 49_500_000_000_000


def plan():
    P = []
    for k in range(200):
        for arm in ("preserve", "zero"):
            P.append({"lane": "E5c", "cell": "RANDOM/PARTIAL/WELL_MIXED", "arm": arm, "pair": k, "k": k, "kind": "origin",
                      "seed": SEED_BASE + k, "cfg": dict(BASE, target_fill=arm)})
    for i, p in enumerate(P):
        p["id"] = "w5b2_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
