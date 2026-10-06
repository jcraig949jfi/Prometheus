"""AIM02 conformance: the AIM02 law step reproduces AIM01 (L0, L1 at B_balanced) and ER01 (R1 free compute,
R2 rich rain) bit-for-bit, and CPU == GPU for every condition. Writes one JSON receipt; exit 1 on any failure."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "AIM01"))
sys.path.insert(0, os.path.join(HERE, "..", "ER01"))
import aim02_run as B  # noqa: E402
import aim01_run as A  # noqa: E402
import er01_run as E  # noqa: E402

n, T, every = 64, 300, 10
rec, ok = {}, True
# vs AIM01 runner (same seeds, density, law)
c1 = []
for cond, (law, dens, en) in B.CONDS.items():
    if en != "B":
        continue
    d = {0.25: "D25", 0.5: "D50", 0.75: "D75"}[dens]
    for k in (0, 1):
        a = A.run_unit("gpu", law, d, k, n, T, 50, 100, every)
        b = B.run_unit("gpu", cond, k, n, T, 100, 2, every)
        eq = a["digests"] == b["digests"] and a["final_digest"] == b["final_digest"]
        c1.append({"cond": cond, "seed": k, "equal_to_aim01": eq})
        ok &= eq
rec["vs_AIM01"] = c1
# vs ER01 runner (R1 free compute, R2 rich rain, P0)
c2 = []
for cond, reg in (("C1FREE", "R1"), ("C2RICH", "R2")):
    for k in (0, 1):
        e = E.run_unit("gpu", reg, "P0", k, n, T, 50, 100, every)
        b = B.run_unit("gpu", cond, k, n, T, 100, 2, every)
        eq = e["digests"] == b["digests"] and e["final_digest"] == b["final_digest"]
        c2.append({"cond": cond, "er01_regime": reg, "seed": k, "equal_to_er01": eq})
        ok &= eq
rec["vs_ER01"] = c2
# CPU == GPU, including the full primary analysis
c3 = []
for cond in B.CONDS:
    g = B.run_unit("gpu", cond, 0, n, T, 100, 2, every)
    c = B.run_unit("cpu", cond, 0, n, T, 100, 2, every)
    eq = all(g[k] == c[k] for k in ("digests", "final_digest", "primary", "diagnostic_arg0_raw",
                                    "late_nonaim_turnover_site"))
    c3.append({"cond": cond, "cpu_equals_gpu": eq})
    ok &= eq
rec["cpu_gpu"] = c3
rec["all_ok"] = bool(ok)
os.makedirs(os.path.join(HERE, "qual"), exist_ok=True)
json.dump(rec, open(os.path.join(HERE, "qual", "conformance_n64_t300.json"), "w"), indent=1)
print("ALL_OK" if ok else "FAILED", file=sys.stderr)
sys.exit(0 if ok else 1)
