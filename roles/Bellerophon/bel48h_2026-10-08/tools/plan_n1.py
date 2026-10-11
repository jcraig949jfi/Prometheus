"""BEL-48H N1: operator-matched completion, PREDICTIVE test of CL-17 (frozen by prereg s14 before any run).

    python3 plan_n1.py MOVE_ACCESS.json W6_RESULTS W6_PLAN OUT

Precursor classes from the 75 W6 C1 precursors (receipts/MOVE_ACCESS_POSTHOC.json): NEEDLE = completed by MUTATION and 0
single segment-move routes; MOVE_RICH = completed by UPTAKE or SELF_MOVE and >= 100 move routes. Each precursor (its
pre-event tape) is transplanted (a quarter of the initial slots) into a random majority of its origin cell's physics
(WELL_MIXED, PAIRED init, 100 ticks), at mutation VLOW (0.0005/byte/tick) and HIGH (0.03), 4 seeds per precursor and arm
(seeds shared by the two arms of a precursor = paired)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from plan_w5 import BASE
SEED = 55_000_000_000_000


def plan(ma, w6res, w6plan):
    acc = {x["id"]: x for x in json.load(open(ma))}
    R = {}
    for l in open(w6res):
        r = json.loads(l); R[r["id"]] = r
    PL = {p["id"]: p for p in json.load(open(w6plan))}
    P = []; pi = 0
    for rid in sorted(acc):
        x = acc[rid]
        if x["cause"] == "MUTATION" and x["move_routes"] == 0:
            cls = "NEEDLE"
        elif x["cause"] in ("UPTAKE", "SELF_MOVE") and x["move_routes"] >= 100:
            cls = "MOVE_RICH"
        else:
            continue
        pre = R[rid]["origin"]["origin_event"]["old"]
        repro = PL[rid]["cfg"]["reproduction"]
        for k in range(4):
            for arm in ("VLOW", "HIGH"):
                P.append({"lane": "N1", "cell": cls, "arm": arm, "pair": "%s|%d" % (rid, k), "k": k, "kind": "origin", "precursor": rid,
                          "seed": SEED + pi * 10 + k, "cfg": dict(BASE, reproduction=repro, mutation_rate=arm, init_tapes=[pre], init_draws="PAIRED", ticks=100)})
        pi += 1
    for i, p in enumerate(P):
        p["id"] = "n1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(*sys.argv[1:4]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[4], "wb").write(b)
    from collections import Counter
    print(len(P), hashlib.sha256(b).hexdigest(), Counter(p["cell"] for p in P))
