"""BEL-48H B1: is budget coupling a consequence of the step budget? (frozen by prereg s15 before any run)

    python3 plan_b1.py OUT.json

W4 M2 / W6 block 3 K1 setting (seeded copiers, physics v3, ECHO, K40, coupling ON, 500 ticks) at execution budget
192 / 256 / 384, 200 fresh seeds per budget (seed k shared across budgets = same initial population)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
SEED = 56_000_000_000_000


def plan():
    from prometheus.z80atlas import coupling_campaign as CC
    P = []
    for b in (192, 256, 384):
        for k in range(200):
            cfg = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); cfg.update(coupling="ON", task="ECHO", init="SEEDED_REPLICATOR", ticks=CC.TICKS, cells=CC.CELLS, budget=b)
            P.append({"lane": "B1", "cell": "budget_%d" % b, "arm": str(b), "pair": k, "k": k, "kind": "comp", "seed": SEED + k, "cfg": cfg})
    for i, p in enumerate(P):
        p["id"] = "b1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
