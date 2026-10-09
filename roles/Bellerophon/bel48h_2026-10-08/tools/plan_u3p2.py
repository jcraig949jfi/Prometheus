"""BEL-48H U3 + P2 (frozen by prereg s20 before any run).   python3 plan_u3p2.py RUNS_ROOT OUT_U3 OUT_P2
U3  split CL-20: paired seeds, RANDOM WELL_MIXED 500 ticks, PARTIAL 300 + PAIR 300 seed-triples; arms normal (OriginWorld),
    block_all (UptakeBlockWorld), block_selfcopy (SelfCopyUptakeBlockWorld: imports reverted only during an execution in
    which the organism lays down a self-copy).
P2  the P1 panel (same 16 pairings, plan_p1) at HIGH mutation, fresh seeds."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from plan_w5 import BASE
import plan_p1
SEED_U3 = 61_000_000_000_000; SEED_P2 = 61_500_000_000_000


def plan_u3():
    P = []; n = 0
    for r in ("ENDOGENOUS_PARTIAL", "PAIR_EXECUTION"):
        for k in range(300):
            for arm, kind in (("normal", "origin"), ("block_all", "origin_block"), ("block_selfcopy", "origin_block_selfcopy")):
                P.append({"lane": "U3", "cell": r, "arm": arm, "pair": k, "k": k, "kind": kind, "seed": SEED_U3 + n, "cfg": dict(BASE, reproduction=r)})
            n += 1
    for i, p in enumerate(P):
        p["id"] = "u3_%05d" % i
    return P


def plan_p2(root):
    plan_p1.SEED = SEED_P2
    P = plan_p1.plan(root)
    for i, p in enumerate(P):
        p["cfg"]["mutation_rate"] = "HIGH"; p["lane"] = "P2"; p["id"] = "p2_%05d" % i
    return P


if __name__ == "__main__":
    for P, outp in ((plan_u3(), sys.argv[2]), (plan_p2(sys.argv[1]), sys.argv[3])):
        b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode(); open(outp, "wb").write(b)
        print(outp.rsplit("/", 1)[-1], len(P), hashlib.sha256(b).hexdigest())
