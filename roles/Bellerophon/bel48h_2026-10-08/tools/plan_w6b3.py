"""BEL-48H Window 6 block 3: fresh-seed confirmation of W4's provisional mechanisms (frozen by prereg s12 before any run).

    python3 plan_w6b3.py OUT.json

K1  ECHO acquisition, ON only (seeded copiers, physics v3 ECHO K40), 300 fresh distinct seeds -> new competent machines
    for the entanglement prevalence test.
K2  conflict repair, ON only (REP + BAD fixtures, INC K16), 300 fresh distinct seeds -> new repaired machines for the
    in-place vs cross-lineage test."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
SEED_BASE = 53_000_000_000_000


def plan():
    from prometheus.z80atlas import coupling_campaign as CC
    P = []
    for k in range(300):
        cfg = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); cfg.update(coupling="ON", task="ECHO", init="SEEDED_REPLICATOR", ticks=CC.TICKS, cells=CC.CELLS, budget=CC.BUDGET)
        P.append({"lane": "K1", "cell": "Bcop_ECHO_K40_ON", "arm": "ON", "pair": None, "k": k, "kind": "comp", "seed": SEED_BASE + k, "cfg": cfg})
    for k in range(300):
        F = CC.fixtures("INC", SEED_BASE + 10 ** 6 + k)
        cfg = dict(CC.COMMON, **CC.V3, **CC.K["K16"]); cfg.update(coupling="ON", init_tapes=[F["REP"], F["BAD"]], ticks=CC.TICKS, cells=CC.CELLS, budget=CC.BUDGET)
        P.append({"lane": "K2", "cell": "E2_REP_BAD_K16_ON", "arm": "ON", "pair": None, "k": k, "kind": "comp", "seed": SEED_BASE + 10 ** 6 + k, "cfg": cfg})
    for i, p in enumerate(P):
        p["id"] = "w6b3_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
