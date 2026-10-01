"""SBF: sensor broadcast + one-shot stateless forwarding on a second channel (12 lines, fits 4222a5f7 strictly).
 0 ADD  S3 = S3 + SENSE          sensor's signed decaying latch (only sensors ever write S3)
 1 MULQ PAY0 = S3*ENERGY         sensor payload (ENERGY = e_max = 1000 at economy-off rows)
 2 ADD  PAY0 = PAY0 + IN0_0      + forward whatever arrived on ch0 (one hop only)
 3 MULQ EMIT = PAY0*PAY0         emit iff |PAY0| >= 16
 4 MOV  CHAN = CNT0              forwarded traffic leaves on ch=#ch0 arrivals (1 mostly); sensors on ch0
 5 ADD  T3 = IN0_0 + IN1_0       evidence = direct + forwarded
 6 MAX  S1 = S1, T3              P amplitude latch (decays with the physics)
 7 SUB  T0 = ZERO - T3
 8 MAX  S2 = S2, T0              Q amplitude latch
 9 MULQ T1 = S1*S2
10 CONST T2 = c
11 SUB  S0 = T2 - T1             '-' iff both amplitudes large
"""
from v_common import *

def sbf(c_imm=100, c_sh=0, readout="prod"):
    L = [("ADD", "S3", "S3", "SENSE", 0), ("MULQ", "PAY0", "S3", "ENERGY", 0), ("ADD", "PAY0", "PAY0", "IN0_0", 0),
         ("MULQ", "EMIT", "PAY0", "PAY0", 0), ("MOV", "CHAN", "CNT0", 0, 0), ("ADD", "T3", "IN0_0", "IN1_0", 0),
         ("MAX", "S1", "S1", "T3", 0), ("SUB", "T0", "ZERO", "T3", 0), ("MAX", "S2", "S2", "T0", 0)]
    if readout == "prod":
        L += [("MULQ", "T1", "S1", "S2", 0), ("CONST", "T2", 0, c_sh, c_imm), ("SUB", "S0", "T2", "T1", 0)]
    else:   # binarized (14 lines; override diagnostic only)
        L += [("CONST", "T2", 0, c_sh, c_imm), ("GT", "T0", "S1", "T2", 0), ("GT", "T1", "S2", "T2", 0),
              ("MULQ", "T1", "T0", "T1", 0), ("SUB", "S0", "T2", "T1", 0)]
    return L

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    ph, env = row_phys("4222a5f7")
    variants = [(c, s) for (c, s) in ((50, 0), (100, 0), (100, 1), (100, 2), (100, 3), (125, 4), (125, 5))]
    G = np.stack([asm(ph, sbf(*v)) for v in variants])
    acc, st = veval(ph, G, env, seeds)
    res = [(v, summarize(a), {k: int(st[k][i]) for k in ("collided", "emitters", "delivered")}) for i, (v, a) in enumerate(zip(variants, acc))]
    for r in res:
        print(r)
    save("sbf_4222_dev.json", {"res": res, "cpu_s": ck.cpu(), "strict": True})
    print(ck.cpu())
