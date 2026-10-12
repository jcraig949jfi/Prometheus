"""BEL-48H Window 6 block 4 (frozen by prereg s13 before any run).   python3 plan_w6b4.py RUNS_ROOT OUT_U OUT_R OUT_X

U  UPTAKE NECESSITY / ROUTE SUBSTITUTABILITY: fresh RANDOM WELL_MIXED worlds, ENDOGENOUS_PARTIAL and PAIR_EXECUTION,
   400 seed-pairs each: OriginWorld (normal) vs UptakeBlockWorld (partner bytes cannot be imported into the own tape).
R  DETERMINISTIC REPLAY SAMPLE: every 33rd run (by id order) of W1v2, W2, W4, W5 block 1, W6 block 1 re-executed with the
   current code; end-state hash must equal the recorded one (lockstep runs excluded: no single end hash).
X  ARCHITECTURE COMPETITION, INDEPENDENT SPECIMEN PAIR: from W6 block 3 K1, the first (by run id) BUDGET_COUPLED and the
   first SEPARATED competent machine; same design as W5 block 3 (ON/OFF x MED/HIGH x order, 24 fresh seeds per level)."""
import hashlib, json, os, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix()); sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from plan_w5 import BASE
SEED_U = 54_000_000_000_000; SEED_X = 54_500_000_000_000


def plan_u():
    P = []; n = 0
    for r in ("ENDOGENOUS_PARTIAL", "PAIR_EXECUTION"):
        for k in range(400):
            for arm, kind in (("normal", "origin"), ("blocked", "origin_block")):
                P.append({"lane": "U", "cell": "%s/WELL_MIXED" % r, "arm": arm, "pair": k, "k": k, "kind": kind,
                          "seed": SEED_U + n, "cfg": dict(BASE, reproduction=r)})
            n += 1
    for i, p in enumerate(P):
        p["id"] = "w6u_%05d" % i
    return P


def plan_r(root):
    P = []
    for wname, plan in (("w1v2", "w1v2_plan.json"), ("w2", "w2_plan.json"), ("w4", "w4_plan.json"), ("w5", "w5_plan.json"), ("w6", "w6_plan.json")):
        res = {}
        for l in open(os.path.join(root, wname, "results.jsonl")):
            r = json.loads(l); res[r["id"]] = r
        specs = sorted(json.load(open(os.path.join(root, plan))), key=lambda p: p["id"])
        for i, p in enumerate(specs):
            if i % 33 or p["kind"] == "lockstep":
                continue
            r = res.get(p["id"])
            if r is None or r.get("void") or "end_hash" not in r:
                continue
            q = dict(p); q["lane"] = "R"; q["cell"] = wname; q["expect_end_hash"] = r["end_hash"]; q["id"] = "w6r_" + p["id"]
            P.append(q)
    return P


def plan_x(root):
    from analyze_w6b3 import budget_class
    from prometheus.z80atlas import coupling_campaign as CC
    rs = sorted((json.loads(l) for l in open(os.path.join(root, "w6b3", "results.jsonl"))), key=lambda r: r["id"])
    E = S = None
    for r in rs:
        if r.get("void") or r["lane"] != "K1" or not (r["comp"]["comp_func_alive"] > 0 and r["comp"].get("dominant")):
            continue
        d = r["comp"]["dominant"]; c = budget_class(d["tape"], d["shared"])
        if c == "BUDGET_COUPLED" and E is None:
            E = (r["id"], d["tape"])
        if c == "SEPARATED" and S is None:
            S = (r["id"], d["tape"])
    assert E and S
    P = []
    for li, lvl in enumerate(("MED", "HIGH")):
        for k in range(24):
            for cp in ("ON", "OFF"):
                for order, tx in (("ES", [E[1], S[1]]), ("SE", [S[1], E[1]])):
                    cfg = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); cfg.update(coupling=cp, task="ECHO", mutation_rate=lvl, init_tapes=tx,
                                                                              init_draws="PAIRED", ticks=300, cells=CC.CELLS, budget=CC.BUDGET)
                    P.append({"lane": "X", "cell": lvl, "arm": "%s_%s" % (cp, order), "pair": k, "k": k, "kind": "compete",
                              "seed": SEED_X + li * 10 ** 6 + k, "cfg": cfg, "specimens": {"E": E[0], "S": S[0]}})
    for i, p in enumerate(P):
        p["id"] = "w6x_%05d" % i
    return P


if __name__ == "__main__":
    root = sys.argv[1]
    for P, outp in ((plan_u(), sys.argv[2]), (plan_r(root), sys.argv[3]), (plan_x(root), sys.argv[4])):
        b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode(); open(outp, "wb").write(b)
        print(outp.rsplit("/", 1)[-1], len(P), hashlib.sha256(b).hexdigest(), (P[0].get("specimens") if P else None))
