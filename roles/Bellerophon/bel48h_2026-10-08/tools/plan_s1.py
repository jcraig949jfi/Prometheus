"""BEL-48H S1: substrate perturbation of the strongest causal findings (frozen by prereg s19 before any run).
    python3 plan_s1.py OUT.json
S1a  uptake-block effect (CL-20) in perturbed substrates: ENDOGENOUS_PARTIAL, RANDOM init, 500 ticks;
     SOUP / WELL_MIXED (world model changed) and GRID / WELL_MIXED with execution budget 384 (step budget changed);
     400 seed-pairs each, normal (OriginWorld) vs uptake-blocked.
S1b  two-fragment complementation (CL-04, variant V1 = LD T,0xA0 @4 + LDIR @10, writer without LDIR) in SOUP / WELL_MIXED
     and GRAPH / LOCAL: arms AB (ENDOGENOUS_PARTIAL) vs AB_copy (ENDOGENOUS_COPY), 40 seed-pairs each, PAIRED init, 300 ticks."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix()); sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
from plan_w5 import BASE
import plan_w6b2
SEED = 60_000_000_000_000


def plan():
    P = []; n = 0
    for name, over in (("SOUP_WELL_MIXED", {"world": "SOUP", "spatial": "WELL_MIXED"}), ("GRID_WELL_MIXED_budget384", {"budget": 384})):
        for k in range(400):
            for arm, kind in (("normal", "origin"), ("blocked", "origin_block")):
                P.append({"lane": "S1a", "cell": name, "arm": arm, "pair": k, "k": k, "kind": kind, "seed": SEED + n,
                          "cfg": dict(BASE, reproduction="ENDOGENOUS_PARTIAL", **over)})
            n += 1
    A, B, _ = plan_w6b2.build(4, 0xA0, 10)
    for name, over in (("SOUP_WELL_MIXED", {"world": "SOUP", "spatial": "WELL_MIXED"}), ("GRAPH_LOCAL", {"world": "GRAPH", "spatial": "LOCAL"})):
        for k in range(40):
            for arm, repro in (("AB", "ENDOGENOUS_PARTIAL"), ("AB_copy", "ENDOGENOUS_COPY")):
                P.append({"lane": "S1b", "cell": name, "arm": arm, "pair": k, "k": k, "kind": "heredity", "seed": SEED + 10 ** 6 + n,
                          "cfg": dict(BASE, reproduction=repro, init_tapes=[A.hex(), B.hex()], init_draws="PAIRED", ticks=300, **over)})
            n += 1
    for i, p in enumerate(P):
        p["id"] = "s1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
