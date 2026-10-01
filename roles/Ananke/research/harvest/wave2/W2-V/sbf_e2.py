"""Capacity probe (OVERRIDE state_dim 4, prog_len 14) of the SBF family at e2fd1e07 physics (async .5, noise 64,
fanout 4, economy). ENERGY is not a constant there, so the payload gain uses a CONST register K."""
from v_common import *

def sbfk(k_imm, k_sh, c_imm, c_sh):
    return [("ADD", "S3", "S3", "SENSE", 0), ("CONST", "T2", 0, k_sh, k_imm), ("MULQ", "PAY0", "S3", "T2", 0),
            ("ADD", "PAY0", "PAY0", "IN0_0", 0), ("MULQ", "EMIT", "PAY0", "PAY0", 0), ("MOV", "CHAN", "CNT0", 0, 0),
            ("ADD", "T3", "IN0_0", "IN1_0", 0), ("MAX", "S1", "S1", "T3", 0), ("SUB", "T0", "ZERO", "T3", 0),
            ("MAX", "S2", "S2", "T0", 0), ("MULQ", "T1", "S1", "S2", 0), ("CONST", "T2", 0, c_sh, c_imm),
            ("SUB", "S0", "T2", "T1", 0)]

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    ph0, env = row_phys("e2fd1e07")
    ph = ph0.replace(prog_len=14, state_dim=4)
    vs = [(125, 3, 100, s) for s in (1, 2, 3, 4)] + [(125, 5, 100, s) for s in (3, 4, 5, 6)]
    G = np.stack([asm(ph, sbfk(*v)) for v in vs])
    acc, st = veval(ph, G, env, seeds)
    res = []
    for i, v in enumerate(vs):
        s = summarize(acc[i]); res.append((v, s)); print(v, s, int(st["emitters"][i]))
    save("sbf_e2_capacity_dev.json", {"res": res, "override": {"prog_len": 14, "state_dim": 4}, "cpu_s": ck.cpu()})
