"""R1 conformance: r1_test4.law_step == aeth03_variants.step for X/R/RX (CPU, 2 seeds, 300 ticks);
decodability unit CPU == GPU (64^2, all laws); tracer via r1_trace CPU == GPU (RX, R)."""
import json, os, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import r1_test4 as T  # noqa: E402
import r1_trace  # noqa: E402,F401  (patches prop01_run)
import prop01_run as P  # noqa: E402
from observatory import aeth03_variants as V  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402
ok, rec = True, {}
rows = []
_, K = T.load_backend("cpu")
for law, var in (("X", "mob_r0x1e0"), ("R", "mob_r1x0e0"), ("RX", "mob_r1x1e0")):
    for k in (0, 1):
        f, _ = R.build_initial(R.SPARSE_SOUP, 64, 64, T.RNG_SEED_BASE + k, write_density=0.5, energy_mode=R.ENERGY_UNIFORM)
        a = [x.copy() for x in f]; b = [x.copy() for x in f]
        for t in range(300):
            a = list(V.step(var, 64, 64, T.PHYS_SEED_BASE + k, t + 1, T.ENERGY["write_cost"], T.ENERGY["maintenance_cost"],
                            T.ENERGY["replenish_numer"], T.ENERGY["replenish_amount"], 0, *a)[:5])
            b, _ = T.law_step(np, K, law, 64, T.PHYS_SEED_BASE + k, t + 1, b)
        eq = T.digest(a) == T.digest(b); rows.append({"law": law, "ref": var, "seed": k, "equal": eq}); ok &= eq
rec["law_vs_aeth03"] = rows; rows = []
tmp = tempfile.mkdtemp()
for law in ("V1", "X", "R", "RX"):
    g = T.run_unit("gpu", law, 0, 64, 200, 100, os.path.join(tmp, "g.npz"), origins=[(16, 16), (16, 48), (48, 16), (48, 48)])
    c = T.run_unit("cpu", law, 0, 64, 200, 100, os.path.join(tmp, "c.npz"), origins=[(16, 16), (16, 48), (48, 16), (48, 48)])
    zg, zc = np.load(os.path.join(tmp, "g.npz")), np.load(os.path.join(tmp, "c.npz"))
    eq = (g["branch_final_digests"] == c["branch_final_digests"] and g["base_final_digest"] == c["base_final_digest"]
          and np.array_equal(zg["H"], zc["H"]) and np.array_equal(zg["D"], zc["D"]))
    rows.append({"law": law, "unit_cpu_equals_gpu": eq}); ok &= eq
rec["decode_unit_cpu_gpu"] = rows; rows = []
for law in ("R", "RX"):
    g = P.run_unit("gpu", law, 0, 64, 200, 300); c = P.run_unit("cpu", law, 0, 64, 200, 300)
    keys = ("origin", "final_digest_control", "final_digest_impulse", "series", "gen_type_counts", "tree")
    eq = all(g[x] == c[x] for x in keys); rows.append({"law": law, "trace_cpu_equals_gpu": eq}); ok &= eq
rec["trace_cpu_gpu"] = rows; rec["all_ok"] = bool(ok)
os.makedirs(os.path.join(HERE, "qual"), exist_ok=True)
json.dump(rec, open(os.path.join(HERE, "qual", "conformance.json"), "w"), indent=1)
print("ALL_OK" if ok else "FAILED", json.dumps(rec), file=sys.stderr); sys.exit(0 if ok else 1)
