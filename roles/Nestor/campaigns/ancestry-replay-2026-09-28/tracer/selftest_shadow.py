"""Bit-identity of the Z8 shadow tracer against the FROZEN z8.run (the tracer must compute exactly what the VM computes).

Random pair interactions (64-byte tape, random registers/flags or fresh None registers, budgets 1..400, op masks 0x0C
(the T-003 cell) plus 0x2C/0x3F with LDIR and no copy noise), run twice: through z8.run with the pair context the world
builds (Ctx(tape, start, n, policy=ARENA, sense=who), no callbacks) and through z8shadow.Shadow. Compared: tape,
registers, flags, pc, halted, per side. Negative control: an injected defect (ADD computed as SUB in the shadow) must
be detected.

    python selftest_shadow.py [N]
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
Z = HERE.parents[1] / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(Z))
sys.path.insert(0, str(HERE))
import z8                                                    # noqa: E402  (frozen VM, read-only)
import z8shadow                                              # noqa: E402

N_HALF = 32
SIZE = 64


def world_pair(tape, regs, flags, budget, mask):
    t = bytearray(tape)
    out = {}
    for side, start in ((0, 0), (1, N_HALF)):
        ctx = z8.Ctx(t, start, N_HALF, policy=z8.ARENA, sense=side)
        ctx.regs, (ctx.fz, ctx.fc) = (None if regs[side] is None else list(regs[side])), flags[side]
        pc = z8.run(ctx, start, budget, ops_enabled=mask)
        out[side] = {"regs": list(ctx.regs), "fz": ctx.fz, "fc": ctx.fc, "pc": pc, "halted": ctx.halted}
    return bytes(t), out


def shadow_pair(tape, regs, flags, budget, mask):
    lab = z8shadow.initial_tape_labels(tape[:N_HALF], tape[N_HALF:], N_HALF, SIZE)
    rl, fl = {}, {}
    for s in (0, 1):
        rl[s], fl[s] = z8shadow.initial_reg_labels(s, regs[s])
    sh = z8shadow.Shadow(tape, lab, {0: regs[0], 1: regs[1]}, rl, {0: flags[0], 1: flags[1]}, fl, budget, mask)
    ra, rb = sh.run_pair(N_HALF)
    out = {}
    for side, rr in ((0, ra), (1, rb)):
        out[side] = {"regs": list(rr["regs"]), "fz": rr["fz"], "fc": rr["fc"], "pc": rr["pc"], "halted": rr["halted"]}
    return bytes(sh.mem), out, sh


def rand_case(rng):
    # bias toward executable structure: mix of random bytes and common opcodes
    common = [0x7E, 0x77, 0x23, 0x13, 0x2B, 0x1A, 0x12, 0x0A, 0x02, 0x21, 0x11, 0x01, 0x3E, 0x36, 0x20, 0x28, 0x18,
              0xC2, 0xC3, 0x10, 0xED, 0x33, 0x34, 0x86, 0xAF, 0x97, 0xBF, 0xFE, 0xC6, 0x3C, 0x3D, 0x34, 0x35, 0x76]
    tape = bytes(rng.choice(common) if rng.random() < 0.5 else rng.randrange(256) for _ in range(SIZE))
    regs = {s: (None if rng.random() < 0.3 else [rng.randrange(256) for _ in range(8)]) for s in (0, 1)}
    flags = {s: (0, 0) if regs[s] is None else (rng.randrange(2), rng.randrange(2)) for s in (0, 1)}
    budget = rng.choice([1, 2, 5, 30, 300, 300, 400])
    mask = rng.choice([0x0C, 0x0C, 0x0C, 0x2C, 0x3F])
    return tape, regs, flags, budget, mask


def run(n=3000, defect=False):
    rng = random.Random(20260928)
    orig = None
    if defect:
        orig = z8shadow.Shadow.run_slice

        def bad(self, side, start):                           # injected defect: corrupt one ADD per slice
            res = orig(self, side, start)
            if any(op in range(0x80, 0x88) for op in self.mem):
                res["regs"][z8shadow.A] ^= 0x01
            return res
        z8shadow.Shadow.run_slice = bad
    mism = 0
    try:
        for _ in range(n):
            case = rand_case(rng)
            wt, wo = world_pair(*case)
            st, so, _sh = shadow_pair(*case)
            if wt != st or wo != so:
                mism += 1
    finally:
        if orig is not None:
            z8shadow.Shadow.run_slice = orig
    return mism


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    good = run(n)
    bad = run(min(n, 500), defect=True)
    res = {"cases": n, "mismatches": good, "defect_detected": bad > 0, "pass": good == 0 and bad > 0}
    print(json.dumps(res))
    sys.exit(0 if res["pass"] else 1)
