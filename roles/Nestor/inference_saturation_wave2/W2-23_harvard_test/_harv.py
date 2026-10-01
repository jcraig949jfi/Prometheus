"""W2-23 HARV builders. DENSE arms come straight from W2-7 alien_vm.build. PLAIN arms (stock z8, used by
K3 / N1 / N2) get the SAME anchor + replacement text as alien_vm's HARV branch, applied to the plain z8 source
(no dense alias patch, no rd split - the split is semantics-preserving and HARV does not touch the data path).
Read-only on everything outside this folder."""
from __future__ import annotations
import pathlib, sys, types
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W27 = HERE.parent / "W2-7_alien_physics"
if str(W27) not in sys.path:
    sys.path.insert(0, str(W27))
import alien_vm  # noqa: E402

ANCHOR = "        pc = pc & mask if pow2 else pc % size\n        op = mem[pc]\n"
ACT = {
    "HARV_HALT": ("            ctx.halted = True\n"
                  "            ctx.ops += steps\n"
                  "            ctx.regs, ctx.fz, ctx.fc = r, fz, fc\n"
                  "            return pc\n"),
    "HARV_WRAP": "            pc = ctx.base + (pc - ctx.base) % ctx.length\n",
}


def harv_src(src, name):
    return alien_vm._rep(src, ANCHOR,
                         "        pc = pc & mask if pow2 else pc % size\n"
                         "        if not (ctx.base <= pc < ctx.base + ctx.length):\n"
                         "            _HITS[0] += 1\n" + ACT[name] +
                         "        op = mem[pc]\n")


def _exec(src, modname, dense_map=None):
    mod = types.ModuleType(modname)
    mod.__dict__["_DENSE"] = dense_map or {}
    mod.__dict__["_HITS"] = [0]
    exec(compile(src, modname, "exec"), mod.__dict__)
    mod.SOURCE = src
    return mod


_C = {}


def plain(name):
    """name in STOCK, HARV_HALT, HARV_WRAP; built on the plain campaign z8.py."""
    if name not in _C:
        src = alien_vm.Z8_SRC
        if name != "STOCK":
            src = harv_src(src, name)
        _C[name] = _exec(src, "z8_plain_" + name.lower())
    return _C[name]


def dense(name):
    """name in STOCK (= alien_vm DENSE), HARV_HALT, HARV_WRAP; W2-7's own builds."""
    key = ("D", name)
    if key not in _C:
        _C[key] = alien_vm.build("DENSE" if name == "STOCK" else name)
    return _C[key]


def dense_mine(name):
    """ST2 only: my injection on top of alien_vm's dense+split source."""
    src = alien_vm._split_rd(alien_vm._dense(alien_vm.Z8_SRC), alien_vm.RDD_PLAIN)
    return _exec(harv_src(src, name), "z8_dense_mine_" + name.lower(), dict(alien_vm.DENSE_MAP))
