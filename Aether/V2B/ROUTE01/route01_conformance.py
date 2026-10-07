"""ROUTE01 conformance: V1 and L1 identical to PROP01's runner (same seeds); CPU == GPU for V1/L1/RT/RN tracer."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "PROP01"))
import route01_run as RR  # noqa: E402
import prop01_run as PR  # noqa: E402
ok, rec = True, {}
keys = ("origin", "warm_digest", "final_digest_control", "final_digest_impulse", "series", "gen_type_counts", "tree", "max_gen")
rows = []
for law in ("V1", "L1"):
    for k in (0, 1):
        a = RR.run_unit("gpu", law, k, 64, 200, 300); b = PR.run_unit("gpu", law, k, 64, 200, 300)
        eq = all(a[x] == b[x] for x in keys); rows.append({"law": law, "seed": k, "equal_prop01": eq}); ok &= eq
rec["vs_PROP01"] = rows; rows = []
for law in ("V1", "L1", "RT", "RN"):
    g = RR.run_unit("gpu", law, 0, 64, 200, 300); c = RR.run_unit("cpu", law, 0, 64, 200, 300)
    eq = all(g[x] == c[x] for x in keys); rows.append({"law": law, "cpu_equals_gpu": eq}); ok &= eq
rec["cpu_gpu"] = rows; rec["all_ok"] = bool(ok)
os.makedirs(os.path.join(HERE, "qual"), exist_ok=True)
json.dump(rec, open(os.path.join(HERE, "qual", "conformance_n64.json"), "w"), indent=1)
print("ALL_OK" if ok else "FAILED", rec, file=sys.stderr); sys.exit(0 if ok else 1)
