"""BEL-48H P1: architecture-payment effect across a SPECIMEN PANEL (frozen by prereg s18 before any run).
    python3 plan_p1.py RUNS_ROOT OUT
From W6 block 3 K1 (excluding w6b3_00001 / w6b3_00020 used in X), the first 4 BUDGET_COUPLED and first 4 SEPARATED
competent machines by run id (analyze_w6b3.budget_class). 16 pairings (E_i vs S_j), MED mutation only, physics v3 ECHO
K40, PAIRED init, 300 ticks, coupling ON / OFF, slot order ES / SE, 8 seeds per pairing shared by its 4 arms."""
import hashlib, json, os, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix()); sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
SEED = 59_000_000_000_000


def plan(root):
    from analyze_w6b3 import budget_class
    from prometheus.z80atlas import coupling_campaign as CC
    rs = sorted((json.loads(l) for l in open(os.path.join(root, "w6b3", "results.jsonl"))), key=lambda r: r["id"])
    E, S = [], []
    for r in rs:
        if r.get("void") or r["lane"] != "K1" or r["id"] in ("w6b3_00001", "w6b3_00020"):
            continue
        if not (r["comp"]["comp_func_alive"] > 0 and r["comp"].get("dominant")):
            continue
        d = r["comp"]["dominant"]; c = budget_class(d["tape"], d["shared"])
        if c == "BUDGET_COUPLED" and len(E) < 4:
            E.append((r["id"], d["tape"]))
        elif c == "SEPARATED" and len(S) < 4:
            S.append((r["id"], d["tape"]))
    assert len(E) == 4 and len(S) == 4, (len(E), len(S))
    P = []; pi = 0
    for e in E:
        for s in S:
            for k in range(8):
                for cp in ("ON", "OFF"):
                    for order, tx in (("ES", [e[1], s[1]]), ("SE", [s[1], e[1]])):
                        cfg = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); cfg.update(coupling=cp, task="ECHO", mutation_rate="MED", init_tapes=tx,
                                                                                  init_draws="PAIRED", ticks=300, cells=CC.CELLS, budget=CC.BUDGET)
                        P.append({"lane": "P1", "cell": "%s_vs_%s" % (e[0], s[0]), "arm": "%s_%s" % (cp, order), "pair": k, "k": k,
                                  "kind": "compete", "seed": SEED + pi * 100 + k, "cfg": cfg})
            pi += 1
    for i, p in enumerate(P):
        p["id"] = "p1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[2], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest(), sorted({p["cell"] for p in P})[:2])
