"""Sensor-broadcast (SB) family: only sensors emit (their own signed decaying latch S3); every site keeps a
P-amplitude latch S1 and a Q-amplitude latch S2 (MAX, decaying with the physics); readout
S0 = ENERGY - S1*S2/256 ('-' iff both amplitudes large). ENERGY = e_max = 1000 is a free constant at
economy-off rows. Variants differ in gain placement. Diagnostics at 9-10 lines are OVERRIDE runs (labelled)."""
import sys
from v_common import *

def sb8(gain="pay"):
    L = [("ADD", "S3", "S3", "SENSE", 0),
         ("MULQ", "EMIT", "S3", "S3", 0),
         ("MULQ", "PAY0", "S3", "ENERGY", 0),
         ("MAX", "S1", "S1", "IN0_0", 0),
         ("SUB", "T0", "ZERO", "IN0_0", 0),
         ("MAX", "S2", "S2", "T0", 0),
         ("MULQ", "T1", "S1", "S2", 0),
         ("SUB", "S0", "ENERGY", "T1", 0)]
    if gain == "pay2":      # 9 lines: second payload gain
        L.insert(3, ("MULQ", "PAY0", "PAY0", "ENERGY", 0))
    if gain == "thr":       # 9 lines: explicit readout threshold c = imm<<sh in T2
        L = L[:7] + [("CONST", "T2", 0, 0, 100), ("SUB", "S0", "T2", "T1", 0)]
    return L

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    res = {}
    for c8 in ["48256f59", "1974a9cf", "333d6b2b"]:
        ph, env = row_phys(c8)
        for gain in ["pay", "pay2"]:
            lines = sb8(gain)
            p = ph if len(lines) <= ph.prog_len else ph.replace(prog_len=len(lines))
            acc, st = veval(p, asm(p, lines)[None], env, seeds)
            s = summarize(acc[0]); s["len"] = len(lines); s["override"] = len(lines) > ph.prog_len
            s["emit"] = int(st["emitters"][0])
            res[f"{c8}_{gain}"] = s
            print(c8, gain, s, ck.cpu(), flush=True)
