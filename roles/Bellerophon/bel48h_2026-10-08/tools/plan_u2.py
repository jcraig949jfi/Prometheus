"""BEL-48H U2: fresh-seed replication of the uptake-block result (frozen by prereg s16 before any run).
    python3 plan_u2.py OUT.json
Identical design to W6 block 4 lane U (plan_w6b4.plan_u) with new seeds: 400 seed-pairs PARTIAL + 400 PAIR, normal vs
uptake-blocked, RANDOM WELL_MIXED 500 ticks."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
import plan_w6b4


def plan():
    plan_w6b4.SEED_U = 57_000_000_000_000
    P = plan_w6b4.plan_u()
    for i, p in enumerate(P):
        p["id"] = "u2_%05d" % i; p["lane"] = "U2"
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest(), len({p["seed"] for p in P}))
