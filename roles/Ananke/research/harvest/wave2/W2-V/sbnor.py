"""SB-NOR (one-flag cheat, NOT parity) at the L8/C1 rows, STRICT 8-line genome: does a SIGNAL-level (lo99>.55)
non-XOR program fit the sampled genome?  '+' iff no fresh '+'-cue packet amplitude."""
from v_common import *

def sbnor(c_imm, c_sh, gains=1):
    L = [("ADD", "S3", "S3", "SENSE", 0), ("MULQ", "EMIT", "S3", "S3", 0), ("MULQ", "PAY0", "S3", "ENERGY", 0)]
    L += [("MULQ", "PAY0", "PAY0", "ENERGY", 0)] * (gains - 1)
    L += [("MAX", "S1", "S1", "IN0_0", 0), ("CONST", "T2", 0, c_sh, c_imm), ("SUB", "S0", "T2", "S1", 0)]
    return L

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    vs = [(g, c, s) for g in (1, 2) for (c, s) in ((40, 0), (80, 0), (120, 0), (80, 1), (80, 2), (80, 3))]
    res = {}
    for c8 in ["48256f59", "1974a9cf", "333d6b2b"]:
        ph, env = row_phys(c8)
        G = np.stack([asm(ph, sbnor(c, s, g)) for g, c, s in vs])
        acc, st = veval(ph, G, env, seeds)
        res[c8] = [(v, summarize(acc[i])) for i, v in enumerate(vs)]
        for v, s in res[c8]:
            print(c8, v, s)
    save("sbnor_dev.json", {"res": res, "cpu_s": ck.cpu(), "strict": True})
    print(ck.cpu())
