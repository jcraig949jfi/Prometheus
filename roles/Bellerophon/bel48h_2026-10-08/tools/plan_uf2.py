"""BEL-48H UF2 (NEXT #11): why does CL-20 vanish in SOUP and at budget 384? (frozen by prereg s21 before any run)
    python3 plan_uf2.py OUT.json
UF's break/make accounting (UptakeFateWorld) in the two S1 substrates where the uptake-block effect was absent, plus the
original substrate as the within-block reference: ENDOGENOUS_PARTIAL, RANDOM, 500 ticks, 150 fresh distinct seeds each."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from plan_w5 import BASE
SEED = 62_000_000_000_000


def plan():
    P = []; n = 0
    for name, over in (("GRID_WM_budget256_reference", {}), ("SOUP_WELL_MIXED", {"world": "SOUP", "spatial": "WELL_MIXED"}), ("GRID_WM_budget384", {"budget": 384})):
        for k in range(150):
            P.append({"lane": "UF2", "cell": name, "arm": None, "pair": None, "k": k, "kind": "uptake_fate", "seed": SEED + n,
                      "cfg": dict(BASE, reproduction="ENDOGENOUS_PARTIAL", **over)}); n += 1
    for i, p in enumerate(P):
        p["id"] = "uf2_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
