"""Instrumented dense VM (in memory only): the exact run_dc.dense_z8() source transformation, plus two
passive hooks that never change what is executed or written:
  _TRACE: list or None  -> appends (pc, op, regs-before) for every executed instruction;
  _ORIG:  list or None  -> per tape address, the ORIGIN address of the byte now stored there
                           (block-copy writes inherit the origin of their source byte; any other write
                           stores -1 = "made from a register").
equivalence() checks the instrumented VM reproduces the stock dense VM's screen verdicts.
"""
from __future__ import annotations

import random
import types

import fsetup as F

C9 = F.CAMP / "z80atlas-verify-2026-09-22"


def build(dense=True):
    src = (C9 / "z8.py").read_text()
    if dense:
        old = ("        if op == 0xED:\n"
               "            op2 = rd(pc + 1)\n"
               "            pc += 2\n")
        assert src.count(old) == 1
        new = ("        if op == 0xED or op in _DENSE:\n"
               "            if op == 0xED:\n"
               "                op2 = rd(pc + 1)\n"
               "                pc += 2\n"
               "            else:\n"
               "                op2 = _DENSE[op]\n"
               "                pc += 1\n")
        src = src.replace(old, new)
    hooks = [
        ("        op = mem[pc]\n",
         "        op = mem[pc]\n        if _TRACE is not None:\n            _TRACE.append((pc, op, tuple(r)))\n"),
        ("        pv = ctx.prov\n",
         "        if _ORIG is not None:\n            _ORIG[a] = -1\n        pv = ctx.prov\n"),
        ("                    wr(dst, v)\n                    src += step\n",
         "                    _o = _ORIG[src & mask] if _ORIG is not None else None\n"
         "                    wr(dst, v)\n"
         "                    if _ORIG is not None and _writable(ctx, dst & mask):\n"
         "                        _ORIG[dst & mask] = _o\n"
         "                    src += step\n"),
    ]
    for o, n in hooks:
        assert src.count(o) == 1, o
        src = src.replace(o, n)
    mod = types.ModuleType("z8_dense_instrumented" if dense else "z8_plain_instrumented")
    mod.__dict__["_DENSE"] = dict(F.run_dc.DENSE)
    mod.__dict__["_TRACE"] = None
    mod.__dict__["_ORIG"] = None
    exec(compile(src, mod.__name__, "exec"), mod.__dict__)
    return mod


IVM = {True: build(True), False: build(False)}
LAST_PARTNER_TRACE = []   # trace of the partner (victim) execution in the last interact() call


def ilen(mem, pc, dense=True):
    """Length in bytes of the instruction at pc (as z8.run decodes it)."""
    n = len(mem)
    op = mem[pc % n]
    if dense and op in (0xE5, 0xE7):
        return 1
    if op == 0xED:
        return 2
    if 0x40 <= op < 0xC0:
        return 1
    if op < 0x40 and (op & 7) == 6:
        return 2
    if op in (0x01, 0x11, 0x21, 0x31, 0xC3, 0xC2, 0xCA, 0xD2, 0xDA):
        return 3
    if op in (0x18, 0x20, 0x28, 0x30, 0x38, 0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE, 0xDB, 0xD3):
        return 2
    return 1


def interact(g, side=0, dense=True, regs=None, seed=0, trace=True, orig=False):
    """One pair interaction exactly as p11.interact (org a at offset 0 runs first, then b at offset n), donor g on
    `side`, victim half uniform random (seeded). Trace is recorded for the DONOR's execution only; origins span
    both executions. Returns (tape, trace, orig, n)."""
    vm = IVM[dense]
    r = F.runner("7ae3", dense)
    n = r.L
    tl = F.world._pow2(2 * n)
    rng = random.Random(seed)
    vb = bytes(rng.randrange(256) for _ in range(n))
    tape = bytearray(tl)
    d0 = 0 if side == 0 else n
    v0 = n - d0
    tape[d0:d0 + len(g)] = bytes(g)
    tape[v0:v0 + n] = vb
    prov, lit = bytearray(tl), bytearray(tl)
    tr = []
    ptr = []
    global LAST_PARTNER_TRACE
    LAST_PARTNER_TRACE = ptr
    vm._ORIG = list(range(tl)) if orig else None
    crng = random.Random(seed + 1)
    try:
        for who, start in ((0, 0), (1, n)):
            ctx = vm.Ctx(tape, start, n, policy=vm.ARENA, rng=crng, copy_mut_rate=r.copy_mut, sense=who)
            ctx.regs, ctx.fz, ctx.fc = (list(regs) if regs is not None else None), 0, 0
            ctx.prov, ctx.prov_lit, ctx.who = prov, lit, who + 1
            vm._TRACE = tr if (trace and who == side) else (ptr if trace else None)
            vm.run(ctx, start, r.t["slice"], ops_enabled=r._ops_mask())
        return tape, tr, vm._ORIG, n
    finally:
        vm._TRACE = None
        vm._ORIG = None


def equivalence(genomes, cell="7ae3"):
    """Instrumented VM (hooks off) must give the same competent verdict as the frozen dense VM."""
    out = []
    for g in genomes:
        F.set_vm(True)
        a = F.run_de.competent(F.world, F.runner(cell), bytes(g), {})
        F.world.z8 = IVM[True]
        b = F.run_de.competent(F.world, F.runner(cell), bytes(g), {})
        F.set_vm(True)
        out.append(a == b)
    return all(out), len(out)
