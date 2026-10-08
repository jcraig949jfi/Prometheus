"""BEL-48H Window 5 block 3 (exploratory; frozen by prereg s10 before any run).   python3 plan_w5b3.py W4_RESULTS OUT

E5d  ENTANGLED vs SEPARATED computation-reproduction architecture, head to head. Two evolved ECHO competent
     self-replicators from W4 (M2 ON): E = w4_00735 (competence-critical and copy-critical bytes shared: LD C,0x40; the
     answer is produced after the copy), S = w4_00963 (IN_A; OUT_A at bytes 0-1, copier separate). Both transplanted
     (each half of the transplant quarter) into a random majority, PAIRED init, physics v3 ECHO K40 (W4 M2 setting),
     300 ticks. Arms: coupling ON / OFF x mutation MED / HIGH x slot order ES / SE; 24 seeds per mutation level, shared
     by the four ON/OFF x order arms (paired)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
SEED_BASE = 51_000_000_000_000


def plan(w4res):
    from prometheus.z80atlas import coupling_campaign as CC
    R = {}
    for l in open(w4res):
        r = json.loads(l); R[r["id"]] = r
    E = R["w4_00735"]["comp"]["dominant"]["tape"]; S = R["w4_00963"]["comp"]["dominant"]["tape"]
    P = []
    for li, lvl in enumerate(("MED", "HIGH")):
        for k in range(24):
            for cp in ("ON", "OFF"):
                for order, tx in (("ES", [E, S]), ("SE", [S, E])):
                    cfg = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); cfg.update(coupling=cp, task="ECHO", mutation_rate=lvl, init_tapes=tx,
                                                                              init_draws="PAIRED", ticks=300, cells=CC.CELLS, budget=CC.BUDGET)
                    P.append({"lane": "E5d", "cell": lvl, "arm": "%s_%s" % (cp, order), "pair": k, "k": k, "kind": "compete",
                              "seed": SEED_BASE + li * 10 ** 6 + k, "cfg": cfg, "order": order})
    for i, p in enumerate(P):
        p["id"] = "w5b3_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[2], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
