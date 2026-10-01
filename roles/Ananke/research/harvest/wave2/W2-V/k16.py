"""84cf905d (L16, D8, P1, C1, sync1, decay 1, random k3 dest-all, rules 4 FIXED per site, wimm 1, economy):
16-line clocked-flood candidates (STRICT). Kp[0] is a non-decaying tick counter (ADDI reads imm+Kp0, WIMM writes it).
Flags S1 (P) / S2 (Q) binarised each tick by GT S>X, X = 256 only at the reset tick.
Variants: 'split'  rules 0,1 relay P (PAY=+S1), rules 2,3 relay Q (PAY=-S2)   [per-site role from r0]
          'diff'   every site: EMIT=S1+S2, PAY=S1-S2 (both-flag sites relay nothing)
          'xreset' like split but reset X also at t%19 in {17,18,0} (cue caught at t%19==1)"""
from v_common import *

def clock(xmode):
    L = [("ADDI", "T0", "ZERO", 0, 1),            # T0 = Kp0 + 1  (I = imm + Kp[0])
         ("WIMM", "T1", "ZERO", "T0", 0),         # Kp[0] := T0   (A=ZERO -> slot 0, B=T0)
         ("ADDI", "T1", "ZERO", 0, 18),
         ("MOD", "T2", "T0", "T1", 0)]            # T2 = (t+1) mod 19 ; readout t%19==16 <-> T2==17
    if xmode == "one":
        L += [("ADDI", "T3", "T1", 0, -1), ("GT", "T3", "T2", "T3", 0)]       # X=256 iff T2==18 (t%19==17)
    else:   # X=256 iff T2 in {18,0,1}  <-> t%19 in {17,18,0}:  (T2+1) mod 19 < 3
        L += [("ADDI", "T3", "T2", 0, -17), ("MULQ", "T3", "T3", "T3", 0)]   # placeholder (replaced below)
    return L

def body(role, xmode="one"):
    L = clock(xmode)
    L += [("ADD", "T0", "SENSE", "IN0_0", 0), ("MAX", "S1", "S1", "T0", 0), ("SUB", "T1", "ZERO", "T0", 0),
          ("MAX", "S2", "S2", "T1", 0), ("GT", "S1", "S1", "T3", 0), ("GT", "S2", "S2", "T3", 0),
          ("XOR", "T1", "S1", "S2", 0), ("ADDI", "S0", "T1", 0, -128)]
    if role == "P":
        L += [("MOV", "EMIT", "S1", 0, 0), ("MOV", "PAY0", "S1", 0, 0)]
    elif role == "Q":
        L += [("MOV", "EMIT", "S2", 0, 0), ("SUB", "PAY0", "ZERO", "S2", 0)]
    else:
        L += [("ADD", "EMIT", "S1", "S2", 0), ("SUB", "PAY0", "S1", "S2", 0)]
    return L

def genome(ph, variant):
    if variant == "split":
        return asm(ph, None, [body("P"), body("P"), body("Q"), body("Q")])
    if variant == "diff":
        return asm(ph, body("D"))
    raise KeyError(variant)

if __name__ == "__main__":
    ck = Clock()
    seeds = assays.world_seeds(V_DEV, 16)
    ph, env = row_phys("84cf905d")
    names = ["split", "diff"]
    G = np.stack([genome(ph, v) for v in names])
    acc, st = veval(ph, G, env, seeds)
    for i, n in enumerate(names):
        print(n, len(body("P")), summarize(acc[i]), {k: int(st[k][i]) for k in ("emitters", "delivered", "energy_spent")})
    save("k16_dev.json", {"res": {n: summarize(acc[i]) for i, n in enumerate(names)}, "cpu_s": ck.cpu()})
    print(ck.cpu())
