"""SBX: sensor-broadcast with binarized-flag XOR readout (11 lines + gains). Fits 4222a5f7 (L12) strictly."""
from v_common import *

def sbx(gains=1, th=60, th_sh=0, pay_src="ENERGY"):
    L = [("ADD", "S3", "S3", "SENSE", 0), ("MULQ", "EMIT", "S3", "S3", 0), ("MULQ", "PAY0", "S3", pay_src, 0)]
    L += [("MULQ", "PAY0", "PAY0", "ENERGY", 0)] * (gains - 1)
    L += [("MAX", "S1", "S1", "IN0_0", 0), ("SUB", "T0", "ZERO", "IN0_0", 0), ("MAX", "S2", "S2", "T0", 0),
          ("CONST", "T2", 0, th_sh, th),
          ("GT", "T0", "S1", "T2", 0), ("GT", "T1", "S2", "T2", 0), ("MULQ", "T1", "T0", "T1", 0),
          ("SUB", "S0", "T2", "T1", 0)]
    return L

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    ph, env = row_phys("4222a5f7")
    variants = [(1, t, 0) for t in (20, 40, 60, 80, 100, 127)] + [(1, 80, 1), (1, 100, 1)]
    G = np.stack([asm(ph, sbx(*v)) for v in variants])
    acc, st = veval(ph, G, env, seeds)
    res = [(v, summarize(a)) for v, a in zip(variants, acc)]
    for r in res:
        print(r)
    save("sbx_4222_dev.json", {"res": res, "cpu_s": ck.cpu(), "strict": True})
    print(ck.cpu())
