"""Diagnostic (OVERRIDE prog_len 20): homogeneous clocked flood that relays BOTH flag types by random
per-tick multiplexing (RAND sign -> SEL +S1 / -S2) + emission window. Measures the family's capacity at
84cf905d physics so the 16-line failure can be attributed to the line budget."""
from v_common import *
import k16

def bodym(w, window=True):
    L = k16.clock("one")
    L += [("ADD", "T0", "SENSE", "IN0_0", 0), ("MAX", "S1", "S1", "T0", 0), ("SUB", "T1", "ZERO", "T0", 0),
          ("MAX", "S2", "S2", "T1", 0), ("GT", "S1", "S1", "T3", 0), ("GT", "S2", "S2", "T3", 0),
          ("XOR", "T1", "S1", "S2", 0), ("ADDI", "S0", "T1", 0, -128),
          ("RAND", "T0", "T3", 0, 0)]  # placeholder fixed below
    L[-1] = ("RAND", "PAY0", "ENERGY", 0, 0)                       # random sign, |.| <= E
    L += [("SUB", "T1", "ZERO", "S2", 0), ("SEL", "PAY0", "S1", "T1", 0), ("ADD", "EMIT", "S1", "S2", 0)]
    if window:
        L += [("ADDI", "T0", "T2", 0, -w), ("GT", "T0", "ZERO", "T0", 0), ("MULQ", "EMIT", "EMIT", "T0", 0)]
    return L

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    ph0, env = row_phys("84cf905d")
    ph = ph0.replace(prog_len=21)
    vs = [("nowin", 0), ("w10", 10), ("w12", 12), ("w14", 14)]
    G = np.stack([asm(ph, bodym(w, v != "nowin")) for v, w in vs])
    acc, st = veval(ph, G, env, seeds)
    for i, (v, w) in enumerate(vs):
        print(v, len(bodym(w, v != "nowin")), summarize(acc[i]), int(st["emitters"][i]))
    save("k20_dev.json", {"res": {v: summarize(acc[i]) for i, (v, w) in enumerate(vs)}, "override_prog_len": 21, "cpu_s": ck.cpu()})
