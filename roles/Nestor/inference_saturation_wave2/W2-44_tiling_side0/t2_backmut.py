"""W2-44 t2: single-byte back-mutation of each in-world rotated root toward the pure rotation P_s of its own frame
(P_s = founder rotated so founder byte i sits at s+i). For every differing position j: revert g[j] := P_s[j], re-assay
(N=1000 panel). Also forward single-byte additions g[j] into P_s. And the converting LDIR label of the baseline.
python -B t2_backmut.py -> t2_backmut.json"""
import json, time
from common44 import *  # noqa
t0 = time.process_time()
NAMES = ["CNR_s22_first", "CNR_s22_last", "CRW_78_first", "CRW_78_last", "XH2N_s1_first", "CRW_1_first", "CRW_1_last",
         "XH2N_s1_last", "CNR_s4_first", "CRW_75_first"]
out = {}
for nm in NAMES:
    g = GEN[nm]
    s = T0[nm]["frame"][0]
    P = rot_of(F, s)
    base = A(g)
    D = [j for j in range(64) if g[j] != P[j]]
    rows = []
    for j in D:
        x = bytearray(g); x[j] = P[j]; a = A(bytes(x))
        fwd = bytearray(P); fwd[j] = g[j]; b = A(bytes(fwd))
        rows.append({"pos": j, "founder_pos": (j - s) % 64, "g": "%02x" % g[j], "P": "%02x" % P[j],
                     "rev_conv_s0": a["conv_s0"], "rev_conv_s1": a["conv_s1"], "rev_keep_s0": a["keep_s0"],
                     "rev_keep_s1": a["keep_s1"], "rev_m": a["m_base"],
                     "fwd_conv_s0": b["conv_s0"], "fwd_conv_s1": b["conv_s1"], "fwd_m": b["m_base"]})
    out[nm] = {"frame": T0[nm]["frame"], "base": base, "P_assay": A(P), "n_diff": len(D), "rows": rows,
               "ldir_s0": conv_ldirs(g, 0), "ldir_s1": conv_ldirs(g, 1)}
    crit0 = [(q["pos"], q["g"], q["P"], q["rev_conv_s0"]) for q in rows if q["rev_conv_s0"] < 0.5 * max(base["conv_s0"], 1e-9)]
    crit1 = [(q["pos"], q["g"], q["P"], q["rev_conv_s1"]) for q in rows if q["rev_conv_s1"] < 0.5 * max(base["conv_s1"], 1e-9)]
    fw = [(q["pos"], q["g"], q["fwd_conv_s0"]) for q in rows if q["fwd_conv_s0"] > 0.1]
    print(nm, s, "base", base["conv_s0"], base["conv_s1"], base["m_base"], "ndiff", len(D))
    print("   crit side0:", crit0)
    print("   crit side1:", crit1)
    print("   fwd single giving side0>0.1:", fw)
    print("   ldir s0", out[nm]["ldir_s0"]); print("   ldir s1", out[nm]["ldir_s1"])
out["_cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "t2_backmut.json").write_text(json.dumps(out, indent=1))
print("cpu", out["_cpu_s"])
