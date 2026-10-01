"""W2-44 t3: 1-minimal tiling core. Start from each in-world side-0 converter g (frame s) and greedily revert bytes to
the pure rotation P_s while the target phenotype holds (conv_s0 >= 0.9*base on panel[:300]; for two-sided genomes also
conv_s1 >= 0.9*base). Repeat passes until no revert is accepted. The surviving differing bytes are a 1-minimal set that
makes P_s a side-0 (two-sided) converter. Confirm on the full N=1000 panel; trace the converting LDIRs; and test
single-byte knock-outs of the core. Also: transplant the core into the founder frame (s=0) by de-rotation.
python -B t3_minimal.py -> t3_minimal.json"""
import json, time
from common44 import *  # noqa
t0 = time.process_time()
P300 = PAN[:300]
NAMES = ["CNR_s22_first", "CRW_78_first", "XH2N_s1_first", "CRW_1_first", "CRW_1_last", "CNR_s22_last", "CRW_78_last"]
out = {}
for nm in NAMES:
    g = GEN[nm]
    s = T0[nm]["frame"][0]
    P = rot_of(F, s)
    b = A(g, P300)
    two = b["conv_s1"] >= 0.8 and b["keep_s1"] >= 0.8
    ok = lambda a: a["conv_s0"] >= 0.9 * b["conv_s0"] and (not two or a["conv_s1"] >= 0.9 * b["conv_s1"])
    cur = bytearray(g)
    changed = True
    passes = 0
    while changed:
        changed = False
        passes += 1
        for j in range(64):
            if cur[j] == P[j]:
                continue
            x = bytearray(cur); x[j] = P[j]
            if ok(A(bytes(x), P300)):
                cur = x; changed = True
    core = bytes(cur)
    D = [j for j in range(64) if core[j] != P[j]]
    full = A(core)
    ko = {}
    for j in D:
        x = bytearray(core); x[j] = P[j]
        a = A(bytes(x))
        ko[j] = {"conv_s0": a["conv_s0"], "conv_s1": a["conv_s1"], "keep_s1": a["keep_s1"], "m": a["m_base"]}
    # transplant to founder frame: founder pos (j - s) % 64 gets core[j]
    tf = bytearray(F)
    for j in D:
        tf[(j - s) % 64] = core[j]
    tA = A(bytes(tf))
    seg = Z_dis = C.Z8PLAIN.dis(core)
    out[nm] = {"frame": s, "two_sided_target": two, "passes": passes, "core_hex": core.hex(),
               "core_positions": [{"pos": j, "founder_pos": (j - s) % 64, "byte": "%02x" % core[j], "P": "%02x" % P[j]} for j in D],
               "core_assay": full, "orig_assay": A(g), "P_assay": A(P), "knockouts": ko,
               "ldir_s0": conv_ldirs(core, 0), "ldir_s1": conv_ldirs(core, 1),
               "transplant_founder_frame": {"hex": bytes(tf).hex(), "assay": tA},
               "dis": ["%d:%s" % (a, t) for a, t in Z_dis]}
    print(nm, "s", s, "two", two, "core", [(j, (j - s) % 64, "%02x>%02x" % (P[j], core[j])) for j in D], flush=True)
    print("   core", full, "\n   ko", ko, "\n   ldir", out[nm]["ldir_s0"], out[nm]["ldir_s1"], "\n   transplant", tA, flush=True)
out["_cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "t3_minimal.json").write_text(json.dumps(out, indent=1))
print("cpu", out["_cpu_s"])
