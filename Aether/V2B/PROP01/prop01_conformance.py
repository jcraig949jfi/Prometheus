"""PROP01 conformance: law steps vs reference implementations, and CPU == GPU for the tracer."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "OFFER01"))
import prop01_run as P  # noqa: E402
import offer01_run as O  # noqa: E402
from observatory import aeth03_variants as V  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402
import numpy as np
n, T = 64, 300
rec, ok = {}, True
rows = []
for law, var in (("RX", "mob_r1x1e0"), ("X", "mob_r0x1e0")):
    for k in (0, 1):
        f, _ = R.build_initial(R.SPARSE_SOUP, n, n, P.RNG_SEED_BASE + k, write_density=0.5, energy_mode=R.ENERGY_UNIFORM)
        a = [x.copy() for x in f]; b = [x.copy() for x in f]
        for t in range(T):
            a = list(V.step(var, n, n, P.PHYS_SEED_BASE + k, t + 1, P.ENERGY["write_cost"], P.ENERGY["maintenance_cost"],
                            P.ENERGY["replenish_numer"], P.ENERGY["replenish_amount"], 0, *a)[:5])
            b, _ = P.law_step(np, P.load_backend("cpu")[1], law, n, P.PHYS_SEED_BASE + k, t + 1, b)
        eq = P.digest(a) == P.digest(b)
        rows.append({"law": law, "ref": var, "seed": k, "equal": eq}); ok &= eq
for law in ("L1", "X", "L2"):
    f, _ = R.build_initial(R.SPARSE_SOUP, n, n, P.RNG_SEED_BASE, write_density=0.5, energy_mode=R.ENERGY_UNIFORM)
    a = [x.copy() for x in f]; b = [x.copy() for x in f]
    K = P.load_backend("cpu")[1]
    for t in range(T):
        a = O.law_step(np, K, law, n, P.PHYS_SEED_BASE, t + 1, a)[0]
        b = P.law_step(np, K, law, n, P.PHYS_SEED_BASE, t + 1, b)[0]
    eq = P.digest(a) == P.digest(b)
    rows.append({"law": law, "ref": "offer01_run", "equal": eq}); ok &= eq
rec["law_equivalence"] = rows
rows = []
for law in ("V1", "L1", "X", "L2", "RX"):
    g = P.run_unit("gpu", law, 0, n, 200, 300)
    c = P.run_unit("cpu", law, 0, n, 200, 300)
    keys = ("origin", "warm_digest", "final_digest_control", "final_digest_impulse", "extinct_tick", "reentry_events",
            "series", "gen_type_counts", "tree", "ever_sites", "max_gen", "unknown_sites")
    eq = all(g[k2] == c[k2] for k2 in keys)
    rows.append({"law": law, "cpu_equals_gpu": eq, "ever_sites": g["ever_sites"], "max_gen": g["max_gen"]}); ok &= eq
rec["tracer_cpu_gpu"] = rows
rec["all_ok"] = bool(ok)
os.makedirs(os.path.join(HERE, "qual"), exist_ok=True)
json.dump(rec, open(os.path.join(HERE, "qual", "conformance_n64.json"), "w"), indent=1)
print(json.dumps(rec), file=sys.stderr); print("ALL_OK" if ok else "FAILED", file=sys.stderr)
sys.exit(0 if ok else 1)
