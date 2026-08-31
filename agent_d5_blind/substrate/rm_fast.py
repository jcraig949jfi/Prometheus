"""Numba-JIT execution engine for RM-D5. PERFORMANCE PATH ONLY.

Semantics must be bit-identical to rm_vm.run (verified by test_equivalence.py
over random program orbits before any use in evidence; re-verified at battery
freeze). The AUTHORITATIVE exact oracle remains exact_oracle/oracle.solves on
the reference VM; every solution claimed by a navigator is re-verified there.
Meter semantics unchanged: 1 evaluation = one candidate scored on the full
table (the JIT computes the same bitwise-Hamming objective, no early stop).
"""
import numpy as np
from numba import njit
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rm_vm import OP_LIST, OPS, PALETTE, STEP_BUDGET

OPCODE = {name: i for i, name in enumerate(OP_LIST)}
PAL_ARR = np.array(PALETTE, dtype=np.int64)
# op ids resolved once (OP_LIST is sorted, frozen)
_AND = OPCODE['AND']; _ADD = OPCODE['ADD']; _JNZ = OPCODE['JNZ']
_MOD = OPCODE['MOD']; _MOV = OPCODE['MOV']; _MUL = OPCODE['MUL']
_OR = OPCODE['OR']; _SET = OPCODE['SET']; _SHL = OPCODE['SHL']
_SHR = OPCODE['SHR']; _SKG = OPCODE['SKG']; _SKZ = OPCODE['SKZ']
_SUB = OPCODE['SUB']; _XOR = OPCODE['XOR']


def encode(prog):
    """Genotype tuple -> int64 array [n,3]."""
    arr = np.empty((len(prog), 3), dtype=np.int64)
    for i, (op, a, b) in enumerate(prog):
        arr[i, 0] = OPCODE[op]
        arr[i, 1] = a
        arr[i, 2] = b
    return arr


@njit(cache=True)
def _run_one(code, x0, x1, pal, step_budget):
    regs = np.zeros(8, dtype=np.int64)
    regs[0] = x0 & 0xFFFF
    regs[1] = x1 & 0xFFFF
    pc = 0
    steps = 0
    n = code.shape[0]
    while pc < n and steps < step_budget:
        op = code[pc, 0]
        a = code[pc, 1]
        b = code[pc, 2]
        steps += 1
        nxt = pc + 1
        if op == _MOV:
            regs[a] = regs[b]
        elif op == _SET:
            regs[a] = pal[b]
        elif op == _ADD:
            regs[a] = (regs[a] + regs[b]) & 0xFFFF
        elif op == _SUB:
            regs[a] = (regs[a] - regs[b]) & 0xFFFF
        elif op == _MUL:
            regs[a] = (regs[a] * regs[b]) & 0xFFFF
        elif op == _AND:
            regs[a] = regs[a] & regs[b]
        elif op == _OR:
            regs[a] = regs[a] | regs[b]
        elif op == _XOR:
            regs[a] = regs[a] ^ regs[b]
        elif op == _SHL:
            regs[a] = (regs[a] << (regs[b] % 16)) & 0xFFFF
        elif op == _SHR:
            regs[a] = regs[a] >> (regs[b] % 16)
        elif op == _MOD:
            if regs[b] != 0:
                regs[a] = regs[a] % regs[b]
            else:
                regs[a] = 0
        elif op == _SKZ:
            if regs[a] == 0:
                nxt = pc + 2
        elif op == _SKG:
            if regs[a] > regs[b]:
                nxt = pc + 2
        elif op == _JNZ:
            if regs[a] != 0:
                nxt = pc - b
                if nxt < 0:
                    nxt = 0
        pc = nxt
    return regs[0]


@njit(cache=True)
def bit_dist_jit(code, xs, ys, targets, pal, step_budget):
    """Sum over table rows of popcount(output XOR target)."""
    total = 0
    for i in range(xs.shape[0]):
        out = _run_one(code, xs[i], ys[i], pal, step_budget)
        v = out ^ targets[i]
        # popcount of 16-bit value
        v = v - ((v >> 1) & 0x5555)
        v = (v & 0x3333) + ((v >> 2) & 0x3333)
        v = (v + (v >> 4)) & 0x0F0F
        total += (v + (v >> 8)) & 0x1F
    return total


@njit(cache=True)
def outputs_jit(code, xs, ys, pal, step_budget):
    out = np.empty(xs.shape[0], dtype=np.int64)
    for i in range(xs.shape[0]):
        out[i] = _run_one(code, xs[i], ys[i], pal, step_budget)
    return out


class FastTask:
    """Precompiled table for fast navigation distance."""
    def __init__(self, task):
        tab = task['table']
        self.xs = np.array([inp[0] for inp, _ in tab], dtype=np.int64)
        self.ys = np.array([inp[1] if len(inp) > 1 else 0 for inp, _ in tab],
                           dtype=np.int64)
        self.targets = np.array([out for _, out in tab], dtype=np.int64)

    def dist(self, prog):
        return int(bit_dist_jit(encode(prog), self.xs, self.ys, self.targets,
                                PAL_ARR, STEP_BUDGET))

    def outputs(self, prog):
        return outputs_jit(encode(prog), self.xs, self.ys, PAL_ARR, STEP_BUDGET)
