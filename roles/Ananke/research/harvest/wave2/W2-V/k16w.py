"""Diagnostic (OVERRIDE prog_len): k16 'split' + emission window (emit only while T2 < w), to test whether the
16-line failure is the in-flight leak. 19 lines."""
from v_common import *
import k16

def bodyw(role, w):
    L = k16.body(role)
    L = L[:-2] + [("ADDI", "T0", "T2", 0, -w), ("GT", "T0", "ZERO", "T0", 0)]
    if role == "P":
        L += [("MULQ", "EMIT", "S1", "T0", 0), ("MOV", "PAY0", "S1", 0, 0)]
    else:
        L += [("MULQ", "EMIT", "S2", "T0", 0), ("SUB", "PAY0", "ZERO", "S2", 0)]
    return L

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    ph0, env = row_phys("84cf905d")
    ph = ph0.replace(prog_len=18)
    ws = [10, 12, 14, 16]
    G = np.stack([asm(ph, None, [bodyw("P", w), bodyw("P", w), bodyw("Q", w), bodyw("Q", w)]) for w in ws])
    acc, st = veval(ph, G, env, seeds)
    for i, w in enumerate(ws):
        print("w", w, len(bodyw("P", w)), summarize(acc[i]))
    save("k16w_dev.json", {"res": {w: summarize(acc[i]) for i, w in enumerate(ws)}, "override_prog_len": 18, "cpu_s": ck.cpu()})
