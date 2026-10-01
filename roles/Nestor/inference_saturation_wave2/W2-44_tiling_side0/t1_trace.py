"""W2-44 t1: register-level trace of the donor context at side 0 (and side 1) for each in-world root, one
N17e panel partner (first panel entry), ZERO donor context. Prints executed instructions up to and including
each LDIR, with registers. python -B t1_trace.py [name ...]"""
import json, sys, pathlib
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
from tvm import C, pair_t  # noqa
from q1_trace import panel  # noqa
Z = C.Z8PLAIN
r = C.runner_for_spec(C.run_ds.DONOR)
T0 = json.loads((HERE / "t0_genomes.json").read_text())["G"]
pan = panel()
names = sys.argv[1:] or ["founder", "CNR_s22_first", "CRW_78_first", "XH2N_s1_first", "CRW_1_first"]
def disat(tape, pc):
    seg = bytes(tape[(pc + k) % 128] for k in range(3))
    return Z.dis(seg, pc, 3)[0][1]
for nm in names:
    g = bytes.fromhex(T0[nm]["hex"])
    for side in (0, 1):
        y, cy = pan[0][0], pan[0][1]
        ga, gb, sa, sb = (g, y, C.ZERO, cy) if side == 0 else (y, g, cy, C.ZERO)
        tape = bytearray(128); tape[0:64] = ga; tape[64:128] = gb
        na, nb, ctxs, tr, wl, after0, ld = pair_t(r, ga, gb, sa, sb)
        print("=====", nm, "side", side, "frame", T0[nm]["frame"])
        snap = bytearray(tape)
        cnt = 0
        for who, pc, op, regs, fz, fc in tr:
            if who != side:
                continue
            cnt += 1
            if cnt > 75:
                break
            print("  pc%3d %-14s B%02x C%02x D%02x E%02x H%02x L%02x A%02x z%d" % (pc, disat(snap, pc), *[regs[i] for i in (0,1,2,3,4,5,7)], fz))
            if op == 0xED and snap[(pc + 1) % 128] == 0xB0:
                print("   ^LDIR")
        print("  LDIRs:", [(w, pc, s, d, n) for w, pc, s, d, n, rg in ld])
        nx, ny = (na, nb) if side == 0 else (nb, na)
        print("  keep", C.FID(g, nx), "conv", C.FID(g, ny))
