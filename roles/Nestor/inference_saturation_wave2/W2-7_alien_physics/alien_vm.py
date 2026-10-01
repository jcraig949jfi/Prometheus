"""W2-7 alien reproductive physics: VM variants built by SOURCE INJECTION on the campaign's z8.py.

Read-only on campaign code: z8.py is read as text, edited in memory, exec'd into a fresh module (the
run_dc.dense_z8() pattern). Every variant starts from the DENSE VM (E5 -> LDIR, E7 -> LDDR one-byte aliases),
because the NPE findings under test were made on the dense VM.

Every injection asserts that its anchor occurs exactly once (a missed anchor would make the variant VACUOUS).
Every variant carries a module-level hit counter `_HITS[0]` that is incremented exactly when the modified
semantics fire; selftest.py uses it to prove bit-identity with the dense VM wherever the modification does not
apply (hits == 0 => identical state).

Variants (VM level):
  DENSE      the baseline dense VM (rd/rdd split only; identical to run_dc.dense_z8 - self-tested)
  NOBLOCK    (a) LDIR/LDDR and their aliases decode as no-ops of the same length (a world with no block copy)
  EXPLEN     (b) block copy with BC == 0 copies 0 bytes (no 0 -> 65,536 long count)
  NOWRAP     (c) DATA addresses are full 16-bit and do not wrap: reads >= tape size return 0, writes are dropped.
                 Code fetch (pc, operands) still wraps, so only the data path changes.
  HARV_HALT  (d) pc may only fetch an opcode inside its own half; leaving it stops the context (like HALT)
  HARV_WRAP  (d') as HARV_HALT, but pc wraps around inside its own half instead of stopping
  BLOCK_OWN  (g) block-copy writes outside the executing context's own half are dropped (bytewise stores allowed)
  AOFF       (f, h) every DATA address and every absolute jump target is offset by ctx.aoff before use; SELF returns
                 (base - aoff). aoff = 0 is the dense VM. ROTATE (tape rotation by r) is aoff = -r for both
                 contexts; RELADDR (registers are offsets from own base) is aoff = base per context.
  SELFCOPY   (j) the aliases E5/E7 become a register-free SELFCOPY: copy own [base, base+len) to [base+len, ...),
                 one budget step per byte, copy mutation as LDIR, registers untouched. ED B0 / ED B8 stay LDIR/LDDR.
"""
from __future__ import annotations

import pathlib
import sys
import types

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
C9 = NESTOR / "campaigns" / "z80atlas-verify-2026-09-22"
Z8_SRC = (C9 / "z8.py").read_text()
DENSE_MAP = {0xE5: 0xB0, 0xE7: 0xB8}
SELFCOPY_OP2 = 0x1F5          # cannot be read from memory (> 0xFF): reachable only through the aliases


def _rep(src, old, new, count=1):
    n = src.count(old)
    assert n == count, "anchor %r found %d times (expected %d): injection would be VACUOUS" % (old[:60], n, count)
    return src.replace(old, new)


def _dense(src):
    # identical text edit to run_dc.dense_z8()
    return _rep(src,
                "        if op == 0xED:\n"
                "            op2 = rd(pc + 1)\n"
                "            pc += 2\n",
                "        if op == 0xED or op in _DENSE:\n"
                "            if op == 0xED:\n"
                "                op2 = rd(pc + 1)\n"
                "                pc += 2\n"
                "            else:\n"
                "                op2 = _DENSE[op]\n"
                "                pc += 1\n")


def _split_rd(src, rdd_body):
    """Route every DATA read through rdd(); code fetches keep rd(pc...)."""
    src = _rep(src, "rd((r[", "rdd((r[", 4)
    src = _rep(src, "(rd(addr) ", "(rdd(addr) ", 2)
    src = _rep(src, "v = rd(src)", "v = rdd(src)")
    src = _rep(src,
               "    def rd(addr):\n        return mem[addr & mask if pow2 else addr % size]\n",
               "    def rd(addr):\n        return mem[addr & mask if pow2 else addr % size]\n\n"
               "    def rdd(addr):\n" + rdd_body)
    return src


RDD_PLAIN = "        return mem[addr & mask if pow2 else addr % size]\n"
WR_ANCHOR = "        a = addr & mask if pow2 else addr % size\n"


def build(name):
    src = _dense(Z8_SRC)
    dense_map = dict(DENSE_MAP)
    if name == "DENSE":
        src = _split_rd(src, RDD_PLAIN)
    elif name == "NOBLOCK":
        src = _split_rd(src, RDD_PLAIN)
        src = _rep(src,
                   "                if not (ops_enabled & 0x20):\n                    continue\n                ctx.world_op_calls += 1\n                step = 1",
                   "                if not (ops_enabled & 0x20):\n                    continue\n"
                   "                _HITS[0] += 1\n                continue\n                step = 1")
    elif name == "EXPLEN":
        src = _split_rd(src, RDD_PLAIN)
        src = _rep(src, "                if n == 0:\n                    n = 0x10000\n",
                   "                if n == 0:\n                    _HITS[0] += 1\n")
    elif name == "NOWRAP":
        src = _split_rd(src,
                        "        a16 = addr & 0xFFFF\n"
                        "        if a16 >= size:\n"
                        "            _HITS[0] += 1\n"
                        "            return 0\n"
                        "        return mem[a16]\n")
        src = _rep(src, WR_ANCHOR,
                   "        if (addr & 0xFFFF) >= size:\n"
                   "            _HITS[0] += 1\n"
                   "            ctx.writes_blocked += 1\n"
                   "            return\n" + WR_ANCHOR)
    elif name in ("HARV_HALT", "HARV_WRAP"):
        src = _split_rd(src, RDD_PLAIN)
        if name == "HARV_HALT":
            act = ("            ctx.halted = True\n"
                   "            ctx.ops += steps\n"
                   "            ctx.regs, ctx.fz, ctx.fc = r, fz, fc\n"
                   "            return pc\n")
        else:
            act = "            pc = ctx.base + (pc - ctx.base) % ctx.length\n"
        src = _rep(src,
                   "        pc = pc & mask if pow2 else pc % size\n        op = mem[pc]\n",
                   "        pc = pc & mask if pow2 else pc % size\n"
                   "        if not (ctx.base <= pc < ctx.base + ctx.length):\n"
                   "            _HITS[0] += 1\n" + act +
                   "        op = mem[pc]\n")
    elif name == "BLOCK_OWN":
        src = _split_rd(src, RDD_PLAIN)
        src = _rep(src, "                    wr(dst, v)\n",
                   "                    _a = dst & mask if pow2 else dst % size\n"
                   "                    if ctx.base <= _a < ctx.base + ctx.length:\n"
                   "                        wr(dst, v)\n"
                   "                    else:\n"
                   "                        _HITS[0] += 1\n"
                   "                        ctx.writes_blocked += 1\n")
    elif name == "AOFF":
        src = _rep(src, '"regs", "fz", "fc")', '"regs", "fz", "fc", "aoff")')
        src = _rep(src, "        self.fc = 0\n", "        self.fc = 0\n        self.aoff = 0\n")
        src = _rep(src, "    cmr = ctx.copy_mut_rate\n",
                   "    cmr = ctx.copy_mut_rate\n    aoff = ctx.aoff\n    if aoff:\n        _HITS[0] += 1\n")
        src = _split_rd(src, "        addr = addr + aoff\n" + RDD_PLAIN)
        src = _rep(src, WR_ANCHOR, "        addr = addr + aoff\n" + WR_ANCHOR)
        src = _rep(src, "            pc = n if take else pc + 3\n",
                   "            pc = (n + aoff) if take else pc + 3\n")
        src = _rep(src, "                r[H], r[L] = (ctx.base >> 8) & 0xFF, ctx.base & 0xFF\n",
                   "                _sb = (ctx.base - aoff) & 0xFFFF\n"
                   "                r[H], r[L] = (_sb >> 8) & 0xFF, _sb & 0xFF\n")
        src = _rep(src, "                p = (pc - 2) & 0xFFFF\n", "                p = (pc - 2 - aoff) & 0xFFFF\n")
    elif name == "SELFCOPY":
        src = _split_rd(src, RDD_PLAIN)
        dense_map = {0xE5: SELFCOPY_OP2, 0xE7: SELFCOPY_OP2}
        src = _rep(src, "            if op2 == OP_LDIR or op2 == OP_LDDR:\n",
                   "            if op2 == _SELFCOPY_OP2:\n"
                   "                if not (ops_enabled & 0x20):\n"
                   "                    continue\n"
                   "                _HITS[0] += 1\n"
                   "                ctx.world_op_calls += 1\n"
                   "                n = ctx.length\n"
                   "                src = ctx.base\n"
                   "                dst = ctx.base + ctx.length\n"
                   "                room = budget - steps\n"
                   "                if n > room:\n"
                   "                    n = room\n"
                   "                    ctx.budget_exhausted = True\n"
                   "                for _ in range(n):\n"
                   "                    v = rdd(src)\n"
                   "                    if cmr and rng is not None and rng.random() < cmr:\n"
                   "                        v ^= 1 << rng.randrange(8)\n"
                   "                        ctx.copy_errors += 1\n"
                   "                    wr(dst, v)\n"
                   "                    src += 1\n"
                   "                    dst += 1\n"
                   "                    ctx.copy_bytes += 1\n"
                   "                steps += n\n"
                   "                continue\n"
                   "            if op2 == OP_LDIR or op2 == OP_LDDR:\n")
    else:
        raise ValueError(name)
    mod = types.ModuleType("z8_alien_" + name.lower())
    mod.__dict__["_DENSE"] = dense_map
    mod.__dict__["_HITS"] = [0]
    mod.__dict__["_SELFCOPY_OP2"] = SELFCOPY_OP2
    exec(compile(src, mod.__name__, "exec"), mod.__dict__)
    mod.SOURCE = src
    return mod


VM_NAMES = ("DENSE", "NOBLOCK", "EXPLEN", "NOWRAP", "HARV_HALT", "HARV_WRAP", "BLOCK_OWN", "AOFF", "SELFCOPY")
