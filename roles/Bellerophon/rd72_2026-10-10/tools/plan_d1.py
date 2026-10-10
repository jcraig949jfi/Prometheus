"""BEL-RD-72 D1: the functional loss/gain ratio as a FROZEN PREDICTION of the uptake-block effect in new substrates.
    python3 plan_d1.py OUT.json
Two substrates not used in BEL-48H: S_LOCAL = ENDOGENOUS_PARTIAL, GRID LOCAL, budget 256; S_PAIR320 = PAIR_EXECUTION, GRID
WELL_MIXED, budget 320. Per substrate: UF arm (UptakeFateWorld, 150 distinct seeds) measures R = FUNC_LOSS / FUNC_GAIN of
uptake events; U arm (400 seed-pairs, normal OriginWorld vs UptakeBlockWorld) measures the origin effect."""
import hashlib, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent / "bel48h_2026-10-08" / "tools"))
from plan_w5 import BASE
SEED = 70_000_000_000_000
SUBSTRATES = (("S_LOCAL", {"reproduction": "ENDOGENOUS_PARTIAL", "spatial": "LOCAL"}),
              ("S_PAIR320", {"reproduction": "PAIR_EXECUTION", "budget": 320}))


def plan():
    P = []; n = 0
    for name, over in SUBSTRATES:
        for k in range(150):
            P.append({"lane": "D1_UF", "cell": name, "arm": None, "pair": None, "k": k, "kind": "uptake_fate", "seed": SEED + n, "cfg": dict(BASE, **over)}); n += 1
        for k in range(400):
            for arm, kind in (("normal", "origin"), ("blocked", "origin_block")):
                P.append({"lane": "D1_U", "cell": name, "arm": arm, "pair": k, "k": k, "kind": kind, "seed": SEED + n, "cfg": dict(BASE, **over)})
            n += 1
    for i, p in enumerate(P):
        p["id"] = "d1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
