"""W2-7 variant registry: name -> (vm name, layout, one-line description). Built lazily, cached."""
from __future__ import annotations

import alien_vm

VARIANTS = {
    "STOCK":       ("DENSE", {}, "dense VM, stock layout (baseline)"),
    "STOCK_B1500": ("DENSE", {"budget": 1500}, "baseline with 5x slice (budget control for A5)"),
    "A_NOBLOCK":   ("NOBLOCK", {}, "(a) no block copy at all: bytewise LD/ST only"),
    "A5_NOBLOCK_B1500": ("NOBLOCK", {"budget": 1500}, "(a') no block copy, 5x slice (removes the budget confound)"),
    "B_EXPLEN":    ("EXPLEN", {}, "(b) block copy with BC=0 copies nothing (no 65,536 long count)"),
    "C_NOWRAP":    ("NOWRAP", {}, "(c) data addresses full 16-bit, no wrap: the 7-bit alias trick fails"),
    "C2_RING192":  ("DENSE", {"tape_len": 192}, "(c') 192-byte ring: halves at 0/64, 64-byte zero gap"),
    "D_HARV_HALT": ("HARV_HALT", {}, "(d) Harvard: pc leaving its own half stops the context"),
    "D2_HARV_WRAP": ("HARV_WRAP", {}, "(d') Harvard: pc wraps inside its own half"),
    "E_REGRAND":   ("DENSE", {"regs": "RAND"}, "(e) entry registers+flags uniform random per interaction"),
    "F_ROTATE":    ("AOFF", {"aoff": "ROT"}, "(f) tape rotated by r~U[0,128) per interaction"),
    "G_BLOCK_OWN": ("BLOCK_OWN", {}, "(g) partner half read-only to block ops (bytewise stores allowed)"),
    "H_RELADDR":   ("AOFF", {"aoff": "REL"}, "(h) pointers and JP targets are offsets from own base"),
    "I_SIDERAND":  ("DENSE", {"order": "RAND"}, "(i) side order random per interaction"),
    "J_SELFCOPY":  ("SELFCOPY", {}, "(j) E5/E7 = register-free SELFCOPY (reverse control)"),
}
_VM = {}


def vm(name):
    if name not in _VM:
        _VM[name] = alien_vm.build(name)
    return _VM[name]


def get(vname):
    v, layout, desc = VARIANTS[vname]
    return vm(v), layout, desc
