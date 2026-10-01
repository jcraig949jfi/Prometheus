"""(2c) H16 on the W-Q engine plant arrays (near-degenerate known answers; workers/W-Q/out/plants_r1_*.npz,
[512 worlds, 12 trials] per-world-trial scores): certificates under REL3, H2 (recorded floor), floor-K (the
plan's stated per-pair-SD scale) and floor-2K, at P = 256 (all pairs) and P = 32 / 64 (first pairs).
Also the mirror structure per arm. Output out/h16_plants.json. numpy only."""
import glob
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import h16  # noqa: E402
from prometheus.ananke import swap_rel as sr  # noqa: E402

out = []
diff = []
for f in sorted(glob.glob(str(ROOT / "roles/Ananke/research/workers/W-Q/out/plants_r1_*.npz"))):
    z = np.load(f)
    plant = "P1SK" if "P1SK" in f else "P1S"
    qs = sorted({k.split("_")[0] for k in z.files})
    for q in qs:
        n = z[f"{q}_normal"]
        for k in z.files:
            if not k.startswith(q + "_") or k.endswith("_normal"):
                continue
            arm = k[len(q) + 1:]
            sw = z[k]
            both = ~np.isnan(n) & ~np.isnan(sw)
            a_all = sr.pair_means(np.where(both, n, np.nan))
            s_all = sr.pair_means(np.where(both, sw, np.nan))
            K = int(round(both.sum() / (2 * len(a_all))))
            for P in (32, 64, 256):
                a, s = a_all[:P], s_all[:P]
                g = ~np.isnan(a) & ~np.isnan(s)
                a, s = a[g], s[g]
                if len(a) < P:
                    continue
                C = sr.boot_counts(P)
                v = {"REL3": str(sr.certificate(a, s, K, method="BOOTT", C=C)["verdict"]),
                     "H2": str(sr.certificate(a, s, K, method="H2", C=C)["verdict"]),
                     "floorK": h16.cert_floor(a, s, math.sqrt(1 / (4 * K)) * .5, C=C),
                     "floor2K": h16.cert_floor(a, s, math.sqrt(1 / (8 * K)) * .5, C=C)}
                rec = {"plant": plant, "q": q, "arm": arm, "P": P, "K": K, "a": float(a.mean()), "s": float(s.mean()), **v}
                out.append(rec)
                if len(set(v.values())) > 1:
                    diff.append(rec)
summ = {m: sum(r[m] != r["REL3"] for r in out) for m in ("H2", "floorK", "floor2K")}
json.dump({"n": len(out), "differs_from_REL3": summ, "diff_rows": diff, "rows": out},
          open(HERE / "out" / "h16_plants.json", "w"), indent=1)
print(len(out), summ)
for r in diff:
    print(r)
