"""PLAN s2.3 attainability tables (gate) + PLAN s4 V1 synthetic FC checks.
No specimen data is read. Writes out/attain2_table.json and out/v1_fc_checks.json."""
import json
import time

import swap_rel2 as s2

t0 = time.time()
table = s2.load_table()
for P, K in ((256, 11), (256, 12), (64, 11), (32, 3), (32, 11), (128, 11)):
    key = f"P{P}_K{K}"
    if key not in table:
        table[key] = s2.build_design(P, K)
        s2.TABLE.write_text(json.dumps(table, indent=1))
    d = table[key]
    print(key, "p_min", {v: d["p_min"][v] for v in s2.CERTS},
          {m: d["p_min"][m] for m in s2.MODELS}, "fc_max", {v: round(x, 4) for v, x in d["fc_max"].items()},
          "cert_ok", d["cert_ok"], f"{time.time()-t0:.0f}s", flush=True)

# V1: out-of-model heterogeneous FC, tiny P, and the must-fail looser CI level
v1 = {"hetero": {}, "tiny_P": {}, "level80": {}}
for P, K in ((256, 11), (256, 12), (64, 11), (32, 3)):
    fc = s2.fc_curve("hetero", P, K)
    v1["hetero"][f"P{P}_K{K}"] = {f"{p:.2f}": r for p, r in fc.items()}
    print("hetero", P, K, "max", {v: max(r[v] for r in fc.values()) for v in s2.CERTS}, flush=True)
for P, K in ((4, 11), (8, 11), (16, 3)):
    fc = {m: s2.fc_curve(m, P, K) for m in s2.MODELS}
    v1["tiny_P"][f"P{P}_K{K}"] = {m: {f"{p:.2f}": r for p, r in c.items()} for m, c in fc.items()}
    print("tiny", P, K, {m: {v: max(r[v] for r in c.values()) for v in s2.CERTS} for m, c in fc.items()}, flush=True)
for P, K in ((256, 11),):
    fc = {m: s2.fc_curve(m, P, K, grid=(0.50, 0.52, 0.60), level=0.80) for m in s2.MODELS}
    v1["level80"][f"P{P}_K{K}"] = {m: {f"{p:.2f}": r for p, r in c.items()} for m, c in fc.items()}
    print("level80", P, K, fc, flush=True)
json.dump(v1, open(s2.HERE / "out" / "v1_fc_checks.json", "w"), indent=1)
print("done", f"{time.time()-t0:.0f}s")
