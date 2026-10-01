"""Material tags on the DENSE VM: `dense_z8taint()`, the X-DD-DENSE-COPY source injection applied to z8taint.

Why: the C-A3-INTERNALIZE / X-A3-WITHDRAW worlds run `run_dc.dense_z8()`, a z8 whose one-byte alias opcodes
(DENSE: 0xE5 -> LDIR, 0xE7 -> LDDR) dispatch like their ED-prefixed forms. `world.py` switches to
`z8taint.run_tainted` whenever material tracking is on, and z8taint is a line-for-line copy of the PLAIN z8.
A tracked replay of a dense world would therefore silently run a different VM. `dense_z8taint()` injects the
identical alias dispatch into z8taint's copy of the dispatch block, with the same assertion that the anchor
text exists (an injection that matched nothing would be vacuous).

selftest() -- all must hold before any tag is read:
  E1 dense_z8taint.run_tainted == dense_z8.run on random programs rich in alias bytes (both policies): pc,
     memory, registers, flags, op/write counters, copy errors (the tags are observation only);
  E2 NON-VACUITY control: on the same programs the PLAIN z8taint differs from dense_z8.run on some programs
     (so the programs exercise the aliases, and E1 is not trivially true);
  E3 the plain equivalence the H3 test certified still holds (plain z8taint == plain z8).

    python dense_taint.py  -> prints the selftest; exit 0 iff E1-E3 hold
"""
from __future__ import annotations

import json
import pathlib
import random
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
C9 = ROOT / "z80atlas-verify-2026-09-22"
DC = ROOT / "npe-w1-donor-discovery-2026-09-26" / "x_dd_dense_copy"
for p in (C9, DC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

OLD = ("        if op == 0xED:\n"
       "            op2 = rd(pc + 1)\n"
       "            pc += 2\n")
NEW = ("        if op == 0xED or op in _DENSE:\n"
       "            if op == 0xED:\n"
       "                op2 = rd(pc + 1)\n"
       "                pc += 2\n"
       "            else:\n"
       "                op2 = _DENSE[op]\n"
       "                pc += 1\n")


def dense_z8taint():
    """z8taint with run_dc's alias dispatch injected (same text, same DENSE map as run_dc.dense_z8)."""
    import run_dc
    src = (C9 / "z8taint.py").read_text(encoding="utf-8")
    assert src.count(OLD) == 1, "z8taint ED dispatch not found: injection would be VACUOUS"
    mod = types.ModuleType("z8taint_dense_copy")
    mod.__dict__["_DENSE"] = dict(run_dc.DENSE)
    exec(compile(src.replace(OLD, NEW), "z8taint_dense_copy", "exec"), mod.__dict__)
    return mod


def _outs(vm_mod, run, mem, regs, pol, budget, seed, tainted):
    m = bytearray(mem)
    ctx = vm_mod.Ctx(m, 0, 96, policy=pol, rng=random.Random(seed), copy_mut_rate=0.02)
    ctx.regs = list(regs)
    pc = run(ctx, 0, budget, 0x3F, orig=bytearray(256), here=1)[0] if tainted else run(ctx, 0, budget, 0x3F)
    return (pc, bytes(m), ctx.regs, ctx.fz, ctx.fc, ctx.ops, ctx.writes, ctx.writes_other, ctx.copy_errors)


def selftest(n=600) -> dict:
    import run_dc
    import z8 as plain
    import z8taint
    dz8, dtaint = run_dc.dense_z8(), dense_z8taint()
    R = random.Random(20260930)
    e1_bad = e2_diff = e3_bad = 0
    aliases = list(run_dc.DENSE)
    for _ in range(n):
        mem = bytearray(R.randrange(256) for _ in range(256))
        for _k in range(R.randrange(4, 24)):                     # enrich with alias opcodes
            mem[R.randrange(96)] = R.choice(aliases)
        regs = [R.randrange(256) for _ in range(8)]
        pol, budget, seed = R.choice([plain.ARENA, plain.OWN]), R.choice([60, 220, 360]), R.randrange(10 ** 9)
        ref = _outs(dz8, dz8.run, mem, regs, pol, budget, seed, False)
        e1_bad += ref != _outs(dz8, dtaint.run_tainted, mem, regs, pol, budget, seed, True)
        e2_diff += ref != _outs(dz8, z8taint.run_tainted, mem, regs, pol, budget, seed, True)
        e3_bad += _outs(plain, plain.run, mem, regs, pol, budget, seed, False) != \
            _outs(plain, z8taint.run_tainted, mem, regs, pol, budget, seed, True)
    out = {"programs": n, "E1_dense_taint_mismatches": e1_bad, "E2_plain_taint_differs_on_dense": e2_diff,
           "E3_plain_taint_mismatches": e3_bad}
    out["pass"] = e1_bad == 0 and e2_diff > 0 and e3_bad == 0
    return out


if __name__ == "__main__":
    r = selftest()
    print(json.dumps(r, indent=1))
    sys.exit(0 if r["pass"] else 1)
