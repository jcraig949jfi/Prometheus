"""BEL-RD-72 A3 predictive accessibility.
Stage 1a  python3 plan_a3.py harvest OUT                      -> 180 fresh worlds (60 x PARTIAL / PAIR / COPY, WELL_MIXED,
                                                                 distinct seeds), harvest at tick 100, <= 20 non-FUNC tapes each
Stage 1b  python3 plan_a3.py scan HARVEST_RESULTS OUT         -> a seeded sample of <= 200 tapes per physics, scanned in chunks
                                                                 of 10 (one-step routes to FUNC under SUB / MOVE / INS / DEL)
Stage 2   python3 plan_a3.py test SCAN_RESULTS OUT            -> (frozen in prereg s5 after stage 1, before any stage-2 run)"""
import hashlib, json, random, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent / "bel48h_2026-10-08" / "tools"))
from plan_w5 import BASE
SEED = 72_000_000_000_000
PHYS = ("ENDOGENOUS_PARTIAL", "PAIR_EXECUTION", "ENDOGENOUS_COPY")


def plan_harvest():
    P = []; n = 0
    for r in PHYS:
        for k in range(60):
            P.append({"lane": "A3H", "cell": r, "arm": None, "pair": None, "k": k, "kind": "harvest", "harvest_tick": 100, "n_sample": 20,
                      "seed": SEED + n, "cfg": dict(BASE, reproduction=r)}); n += 1
    for i, p in enumerate(P):
        p["id"] = "a3h_%05d" % i
    return P


def plan_scan(hres):
    rng = random.Random(7203)
    by = {r: [] for r in PHYS}
    for l in open(hres):
        x = json.loads(l)
        if x.get("void"):
            continue
        for t in x["harvest"]["tapes"]:
            by[x["cell"]].append((x["id"], t))
    P = []
    for r in PHYS:
        items = sorted(set(by[r])); rng.shuffle(items); items = items[:200]
        for i in range(0, len(items), 10):
            chunk = items[i:i + 10]
            P.append({"lane": "A3S", "cell": r, "arm": None, "pair": None, "k": i // 10, "kind": "scan", "seed": 0,
                      "cfg": dict(BASE, reproduction=r), "tapes": [t for _, t in chunk], "sources": [s for s, _ in chunk]})
    for i, p in enumerate(P):
        p["id"] = "a3s_%05d" % i
    return P


if __name__ == "__main__":
    mode = sys.argv[1]
    P = plan_harvest() if mode == "harvest" else plan_scan(sys.argv[2])
    outp = sys.argv[2] if mode == "harvest" else sys.argv[3]
    b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode(); open(outp, "wb").write(b)
    print(mode, len(P), hashlib.sha256(b).hexdigest())
