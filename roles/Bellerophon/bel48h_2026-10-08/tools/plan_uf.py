"""BEL-48H UF: mechanism of uptake's net suppression (frozen by prereg s17 before any run).   python3 plan_uf.py OUT
Fresh RANDOM WELL_MIXED worlds, 500 ticks, normal physics: PARTIAL 200 + PAIR 100 distinct seeds, UptakeFateWorld."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from plan_w5 import BASE
SEED = 58_000_000_000_000


def plan():
    P = []; n = 0
    for r, m in (("ENDOGENOUS_PARTIAL", 200), ("PAIR_EXECUTION", 100)):
        for k in range(m):
            P.append({"lane": "UF", "cell": r, "arm": None, "pair": None, "k": k, "kind": "uptake_fate", "seed": SEED + n, "cfg": dict(BASE, reproduction=r)}); n += 1
    for i, p in enumerate(P):
        p["id"] = "uf_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
