"""SB family capacity probe (OVERRIDE prog_len, diagnostic only): is ANY SB variant >= .60 at these rows?
Batched over variants. 10-line SB: gain g in {1,2} MULQ-by-ENERGY payload stages, readout threshold c."""
from v_common import *

def sb(gains, c_imm, c_sh):
    L = [("ADD", "S3", "S3", "SENSE", 0), ("MULQ", "EMIT", "S3", "S3", 0), ("MULQ", "PAY0", "S3", "ENERGY", 0)]
    L += [("MULQ", "PAY0", "PAY0", "ENERGY", 0)] * (gains - 1)
    L += [("MAX", "S1", "S1", "IN0_0", 0), ("SUB", "T0", "ZERO", "IN0_0", 0), ("MAX", "S2", "S2", "T0", 0),
          ("MULQ", "T1", "S1", "S2", 0), ("CONST", "T2", 0, c_sh, c_imm), ("SUB", "S0", "T2", "T1", 0)]
    return L

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    variants = [(g, ci, cs) for g in (1, 2) for (ci, cs) in ((25, 0), (50, 0), (100, 0), (100, 1), (100, 2), (125, 3), (125, 4), (125, 5))]
    res = {}
    for c8 in ["48256f59", "1974a9cf", "333d6b2b"]:
        ph0, env = row_phys(c8)
        ph = ph0.replace(prog_len=11)
        G = np.stack([asm(ph, sb(*v)) for v in variants])
        acc, st = veval(ph, G, env, seeds)
        res[c8] = [(v, summarize(a)) for v, a in zip(variants, acc)]
        best = max(res[c8], key=lambda x: x[1]["acc"])
        print(c8, "best", best, ck.cpu(), flush=True)
        for v, s in res[c8]:
            print("  ", v, s["acc"])
    save("sb_grid.json", {"res": res, "cpu_s": ck.cpu(), "note": "override prog_len 11 diagnostic"})
