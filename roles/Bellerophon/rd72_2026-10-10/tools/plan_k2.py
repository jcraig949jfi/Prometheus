"""BEL-RD-72 K2 = K amended after adversarial review (prereg s3 amendment A1; frozen before ANY K run).
    python3 plan_k2.py OUT.json
Changes from plan_k.py (which stays as frozen and is superseded, never run):
  dose match   X_ONLY = X_al + REP, Y_ONLY = Y_al + REP (16 fixture + 16 copier transplants, as XY gets 16 + 16)
  selection    XY_AL x RANDOM_REWARD per operator regime (same total bonus, no individual link) replaces XY_AL x OFF;
               XY_AL x OFF kept under PARTIAL_BYTE only (60)
  everything else as K: v3 COMMON + K40, COND_MULTI, 1,000 ticks, PAIRED init, 60 distinct seeds per cell (new seed base)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix()); sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from fixtures_k import fixtures
from plan_k import OPS, cfg
SEED = 71_500_000_000_000
FIX = {"XY_AL": ("X_al", "Y_al"), "XY_SH": ("X_sh", "Y_sh"), "XY_NS": ("X_sh", "Y_ns"), "X_ONLY": ("X_al", "REP"), "Y_ONLY": ("Y_al", "REP"), "REP": ("REP",)}


def plan():
    F = {k: v.hex() for k, v in fixtures().items()}
    P = []; n = 0
    for ops in OPS:
        for fx, names in FIX.items():
            for k in range(60):
                P.append({"lane": "K2", "cell": "%s/%s" % (fx, ops), "arm": "ON", "k": k, "pair": None, "kind": "comp", "seed": SEED + n,
                          "cfg": cfg(ops, [F[x] for x in names])}); n += 1
        for arm in (("RANDOM_REWARD", "OFF") if ops == "PARTIAL_BYTE" else ("RANDOM_REWARD",)):
            for k in range(60):
                P.append({"lane": "K2", "cell": "XY_AL/%s" % ops, "arm": arm, "k": k, "pair": None, "kind": "comp", "seed": SEED + n,
                          "cfg": cfg(ops, [F["X_al"], F["Y_al"]], coupling=arm)}); n += 1
    for i, p in enumerate(P):
        p["id"] = "k2_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
