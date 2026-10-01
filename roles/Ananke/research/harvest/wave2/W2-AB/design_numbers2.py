"""W2-AB addendum: pooled family-level arm-contrast power (BASE 4x12=48 vs arm 4x8=32), unit counts with BASE n=12."""
import json
from scipy import stats as st
def power(n0, n1, p0, p1, alpha=0.05):
    pw = 0.0
    for a in range(n0 + 1):
        pa = st.binom.pmf(a, n0, p0)
        if pa < 1e-12: continue
        for b in range(n1 + 1):
            pb = st.binom.pmf(b, n1, p1)
            if pb < 1e-12: continue
            if st.fisher_exact([[b, n1 - b], [a, n0 - a]], alternative="greater")[1] <= alpha:
                pw += pa * pb
    return round(pw, 3)
out = {"pooled_48v32": {f"{p0}->{p1}": power(48, 32, p0, p1) for p0, p1 in ((0.05, 0.25), (0.1, 0.3), (0.1, 0.35), (0.2, 0.45), (0.05, 0.2))}}
arms = {"BASE": (12, 1), "W0": (8, 1), "M32": (8, 4), "B4X": (8, 4), "PSEED": (4, 1), "KSEED": (12, 1), "STEP": (8, 1)}
full = sum(n * c for n, c in arms.values()); t1 = sum(arms[a][0] * arms[a][1] for a in ("BASE", "W0", "M32", "PSEED", "KSEED"))
ctrl = 12 + 8 + 4
out["units"] = {"full_cell": full, "tier1_cell": t1, "control_cell": ctrl, "per_arm_per_cell": {a: n * c for a, (n, c) in arms.items()}}
for name, nc in (("core12", 12), ("core16_with_xor", 16)):
    uf, ut = nc * full + 4 * ctrl, nc * t1 + 4 * ctrl
    out["units"][name] = {"full": uf, "tier1": ut, "gpu_h_full": [round(uf * s / 3600, 1) for s in (37, 60)],
                          "gpu_h_tier1": [round(ut * s / 3600, 1) for s in (37, 60)],
                          "cpu_core_h_full": [round(uf * m / 60) for m in (20, 80)]}
    out["units"][name]["per_arm_gpu_h@37-60s"] = {a: [round(nc * n * c * s / 3600, 2) for s in (37, 60)] for a, (n, c) in arms.items()}
print(json.dumps(out, indent=1)); json.dump(out, open("design_numbers2.json", "w"), indent=1)
