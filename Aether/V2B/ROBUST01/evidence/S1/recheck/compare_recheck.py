"""Compare S1 recheck units to the S1 outputs: every field except wall-clock times must be identical, and the
combine npz arrays must be equal."""
import glob
import json
import os
import sys

import numpy as np

A = "C:/Prometheus-data/aether_robust01/S1/search"
B = "C:/Prometheus-data/aether_robust01/S1_recheck/search"


def strip(d):
    d = dict(d)
    d.pop("wall_seconds", None)
    d["log"] = [{k: v for k, v in e.items() if k != "seconds"} for e in d.get("log", [])]
    return d


ok = True
for pb in sorted(glob.glob(os.path.join(B, "G1_*_s*.json"))):
    name = os.path.basename(pb)
    if name.endswith("_cert.json"):
        continue
    a, b = json.load(open(os.path.join(A, name))), json.load(open(pb))
    same_json = strip(a) == strip(b)
    diff = sorted(k for k in set(a) | set(b) if strip(a).get(k) != strip(b).get(k))
    same_npz = None
    if a.get("combine_npz") or b.get("combine_npz"):
        za, zb = np.load(os.path.join(A, a["combine_npz"])), np.load(os.path.join(B, b["combine_npz"]))
        same_npz = sorted(za.files) == sorted(zb.files) and all(np.array_equal(za[k], zb[k]) for k in za.files)
    print(name, "json_identical", same_json, "npz_identical", same_npz, "diff_fields", diff)
    ok = ok and same_json and same_npz is not False
print("ALL_IDENTICAL" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
