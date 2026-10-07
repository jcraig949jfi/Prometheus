"""OFFER01 conformance: X == aeth03_variants mob_r0x1e0 (exact TEST-3 exchange law), L1 == AIM01 reaim1,
CPU == GPU for L1, X, L2 (digests + full analysis). One JSON receipt; exit 1 on failure."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "AIM01"))
import offer01_run as O  # noqa: E402
import aim01_run as A  # noqa: E402
from observatory import aeth03_variants as V  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402
n, T, every = 64, 300, 10
rec, ok = {}, True
rows = []
for k in (0, 1):
    f, _ = R.build_initial(R.SPARSE_SOUP, n, n, O.RNG_SEED_BASE + k, write_density=0.5, energy_mode=R.ENERGY_UNIFORM)
    s = [x.copy() for x in f]
    dg = []
    for t in range(T):
        out = V.step("mob_r0x1e0", n, n, O.PHYS_SEED_BASE + k, t + 1, O.ENERGY["write_cost"], O.ENERGY["maintenance_cost"],
                     O.ENERGY["replenish_numer"], O.ENERGY["replenish_amount"], 0, *s)
        s = list(out[:5])
        if (t + 1) % every == 0:
            dg.append([t + 1, O.digest(s)])
    u = O.run_unit("gpu", "X", k, n, T, 100, 2, every)
    eq = u["digests"] == dg
    rows.append({"seed": k, "X_equals_mob_r0x1e0": eq}); ok &= eq
rec["X_vs_TEST3_exchange"] = rows
rows = []
for k in (0, 1):
    a = A.run_unit("gpu", "L1", "D50", k, n, T, 50, 100, every)
    u = O.run_unit("gpu", "L1", k, n, T, 100, 2, every)
    eq = a["digests"] == u["digests"]
    rows.append({"seed": k, "L1_equals_AIM01_reaim1": eq}); ok &= eq
rec["L1_vs_AIM01"] = rows
rows = []
for law in ("L1", "X", "L2"):
    g = O.run_unit("gpu", law, 0, n, T, 100, 2, every)
    c = O.run_unit("cpu", law, 0, n, T, 100, 2, every)
    eq = all(g[k2] == c[k2] for k2 in ("digests", "final_digest", "counts_late", "downstream", "delivered",
                                        "raw_payload_diag", "writer_payload_diag"))
    rows.append({"law": law, "cpu_equals_gpu": eq, "counts_late": g["counts_late"]}); ok &= eq
rec["cpu_gpu"] = rows
rec["all_ok"] = bool(ok)
os.makedirs(os.path.join(HERE, "qual"), exist_ok=True)
json.dump(rec, open(os.path.join(HERE, "qual", "conformance_n64_t300.json"), "w"), indent=1)
print(json.dumps(rec, indent=0)[:1500], file=sys.stderr)
print("ALL_OK" if ok else "FAILED", file=sys.stderr)
sys.exit(0 if ok else 1)
