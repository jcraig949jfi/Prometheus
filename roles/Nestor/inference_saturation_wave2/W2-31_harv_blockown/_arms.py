"""W2-31 arms: HARV_HALT (W2-7 build) x write confinement, by source injection on the same DENSE source.
Read-only on everything outside this folder.

Counters (module level, reset by callers):
  _HITS[0]  HARV fired (pc left own half -> halt)          (same name/semantics as W2-7 / W2-23)
  _HB[0]    block-copy byte writes dropped                  _HBC[0] of those, ones that would have CHANGED the byte
  _HS[0]    byte-store writes dropped                       _HSC[0] of those, ones that would have CHANGED the byte
  _ORD      [tape object, set of half-bases that have started run on it]   (order protection state)
"""
from __future__ import annotations
import pathlib, sys, types
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W27 = HERE.parent / "W2-7_alien_physics"
if str(W27) not in sys.path:
    sys.path.insert(0, str(W27))
import alien_vm  # noqa: E402

HARV_ANCHOR = "        pc = pc & mask if pow2 else pc % size\n        op = mem[pc]\n"
HARV_HALT_ACT = ("            ctx.halted = True\n"
                 "            ctx.ops += steps\n"
                 "            ctx.regs, ctx.fz, ctx.fc = r, fz, fc\n"
                 "            return pc\n")
RUN_ANCHOR = "    cmr = ctx.copy_mut_rate\n"
BLK_ANCHOR = "                    wr(dst, v)\n"
WR_ANCHOR = "        a = addr & mask if pow2 else addr % size\n"

# condition text (evaluated with `_a` = wrapped target address) for "this write is forbidden"
COND = {
    "OP": "_prot and _plo <= _a < _phi",                        # into the other half whose owner has not run yet
    "BL": "not (ctx.base <= _a < ctx.base + ctx.length)",       # anywhere outside own half (W2-7 BLOCK_OWN rule)
}
ARMS = {"HALT": (None, False), "BO_OP": ("OP", False), "SO_OP": ("OP", True),
        "BO_BL": ("BL", False), "SO_BL": ("BL", True)}


def source(arm):
    mode, stores = ARMS[arm]
    src = alien_vm._split_rd(alien_vm._dense(alien_vm.Z8_SRC), alien_vm.RDD_PLAIN)
    src = alien_vm._rep(src, HARV_ANCHOR,
                        "        pc = pc & mask if pow2 else pc % size\n"
                        "        if not (ctx.base <= pc < ctx.base + ctx.length):\n"
                        "            _HITS[0] += 1\n" + HARV_HALT_ACT +
                        "        op = mem[pc]\n")
    if mode is None:
        return src
    c = COND[mode]
    if mode == "OP":
        src = alien_vm._rep(src, RUN_ANCHOR, RUN_ANCHOR +
                            "    if _ORD[0] is not mem:\n"
                            "        _ORD[0] = mem\n"
                            "        _ORD[1] = set()\n"
                            "    _ORD[1].add(ctx.base)\n"
                            "    _plo = (ctx.base + ctx.length) % size\n"
                            "    _phi = _plo + ctx.length\n"
                            "    _prot = (size == 2 * ctx.length) and (_plo not in _ORD[1])\n")
    src = alien_vm._rep(src, BLK_ANCHOR,
                        "                    _a = dst & mask if pow2 else dst % size\n"
                        "                    if " + c + ":\n"
                        "                        _HB[0] += 1\n"
                        "                        _HBC[0] += mem[_a] != (v & 0xFF)\n"
                        "                        ctx.writes_blocked += 1\n"
                        "                    else:\n"
                        "                        wr(dst, v)\n")
    if stores:
        # every other write goes through wr(); block writes reaching wr() already passed the block gate
        src = alien_vm._rep(src, WR_ANCHOR, WR_ANCHOR +
                            "        _a = a\n"
                            "        if " + c + ":\n"
                            "            _HS[0] += 1\n"
                            "            _HSC[0] += mem[a] != (val & 0xFF)\n"
                            "            ctx.writes_blocked += 1\n"
                            "            return\n")
    return src


_C = {}


def vm(arm):
    if arm not in _C:
        src = source(arm)
        mod = types.ModuleType("z8_w231_" + arm.lower())
        d = mod.__dict__
        d["_DENSE"] = dict(alien_vm.DENSE_MAP)
        for k in ("_HITS", "_HB", "_HBC", "_HS", "_HSC"):
            d[k] = [0]
        d["_ORD"] = [None, set()]
        exec(compile(src, mod.__name__, "exec"), d)
        mod.SOURCE = src
        _C[arm] = mod
    return _C[arm]


def reset(z):
    for k in ("_HITS", "_HB", "_HBC", "_HS", "_HSC"):
        getattr(z, k)[0] = 0


def counts(z):
    return {k: getattr(z, k)[0] for k in ("_HITS", "_HB", "_HBC", "_HS", "_HSC")}
