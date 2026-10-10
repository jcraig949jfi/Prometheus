"""BEL-RD-72 D2: selective uptake ablation -- is the origin cost of uptake damage to PRECURSORS (LDIR carriers)?
    python3 plan_d2.py OUT.json
Substrates: S_PAIR320 (D1: effect present, highest power) and S_REF = the BEL-48H reference (BASE: ENDOGENOUS_PARTIAL, GRID
WELL_MIXED, budget 256). 400 seeds per substrate (new seed base); each seed runs 4 arms on the SAME seed (paired by design):
normal (OriginWorld), block_all (UptakeBlockWorld), block_ldir, block_noldir (uptake_select)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent / "bel48h_2026-10-08" / "tools"))
from plan_w5 import BASE
SEED = 72_200_000_000_000
SUBSTRATES = (("S_PAIR320", {"reproduction": "PAIR_EXECUTION", "budget": 320}), ("S_REF", {}))
ARMS = (("normal", "origin"), ("block_all", "origin_block"), ("block_ldir", "origin_block_ldir"), ("block_noldir", "origin_block_noldir"))


def plan():
    P = []; n = 0
    for name, over in SUBSTRATES:
        for k in range(400):
            for arm, kind in ARMS:
                P.append({"lane": "D2", "cell": name, "arm": arm, "pair": k, "k": k, "kind": kind, "seed": SEED + n, "cfg": dict(BASE, **over)})
            n += 1
    for i, p in enumerate(P):
        p["id"] = "d2_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
