"""S2 FLAT -- total flat bytecode over (working list, stack).

Every nonempty tuple of in-range ints is a valid program: validity is closed
under *any* edit by construction.  Arithmetic saturates, stack pops on empty
yield 0, and a global step meter bounds the backward jump, so every program
halts.  This basis tests whether free validity buys phenotype diversity.
"""
from . import common
from .common import clampv, clampl, MAXVAL, PROG_MAX

NAME = "S2"
NOPS = 24
NARG = 16
FUEL = 300
SMAX = 32

OPNAMES = ["NOP", "PUSHK", "POP", "ADD", "SUB", "MUL", "MOD", "DUP", "SWAPS",
           "PUSHLEN", "GETIDX", "SETIDX", "APPEND", "PREPEND", "POPHEAD",
           "POPTAIL", "REVERSE", "ROTL", "MAPADD", "MAPMUL", "SELFCAT", "JZ",
           "JB", "TRUNC"]

_PERM = list(range(NOPS))
_IPERM = list(range(NOPS))
_PERMA = list(range(NARG))
_IPERMA = list(range(NARG))


def set_order(perm_slot, perm_arg):
    global _PERM, _IPERM, _PERMA, _IPERMA
    _PERM = list(perm_slot)
    _IPERM = [0] * NOPS
    for i, v in enumerate(_PERM):
        _IPERM[v] = i
    _PERMA = list(perm_arg)
    _IPERMA = [0] * NARG
    for i, v in enumerate(_PERMA):
        _IPERMA[v] = i


def _tok(op, arg):
    return _IPERM[op] + NOPS * _IPERMA[arg % NARG]


def _untok(t):
    return _PERM[t % NOPS], _PERMA[(t // NOPS) % NARG]


def is_valid(prog):
    if not isinstance(prog, tuple) or not (0 < len(prog) <= PROG_MAX):
        return False
    for t in prog:
        if t < -MAXVAL or t > MAXVAL:
            return False
    return True


def decode(prog):
    return [_untok(t) for t in prog]


def run(prog, inp):
    common.METER["runs"] += 1
    if not is_valid(prog):
        return None, "invalid"
    code = decode(prog)
    n = len(code)
    L = list(clampl(inp))
    S = []
    pc = 0
    fuel = FUEL
    while 0 <= pc < n:
        fuel -= 1
        if fuel < 0:
            return None, "timeout"
        op, arg = code[pc]
        pc += 1
        if op == 0:
            pass
        elif op == 1:
            if len(S) < SMAX:
                S.append(arg - 8)
        elif op == 2:
            if S:
                S.pop()
        elif op == 3:
            b = S.pop() if S else 0
            a = S.pop() if S else 0
            if len(S) < SMAX:
                S.append(clampv(a + b))
        elif op == 4:
            b = S.pop() if S else 0
            a = S.pop() if S else 0
            if len(S) < SMAX:
                S.append(clampv(a - b))
        elif op == 5:
            b = S.pop() if S else 0
            a = S.pop() if S else 0
            if len(S) < SMAX:
                S.append(clampv(a * b))
        elif op == 6:
            b = S.pop() if S else 0
            a = S.pop() if S else 0
            if len(S) < SMAX:
                S.append(a % b if b else 0)
        elif op == 7:
            if S and len(S) < SMAX:
                S.append(S[-1])
        elif op == 8:
            if len(S) >= 2:
                S[-1], S[-2] = S[-2], S[-1]
        elif op == 9:
            if len(S) < SMAX:
                S.append(len(L))
        elif op == 10:
            i = S.pop() if S else 0
            v = L[i % len(L)] if L else 0
            if len(S) < SMAX:
                S.append(v)
        elif op == 11:
            v = S.pop() if S else 0
            i = S.pop() if S else 0
            if L:
                L[i % len(L)] = clampv(v)
        elif op == 12:
            v = S.pop() if S else 0
            if len(L) < common.MAXLEN:
                L.append(clampv(v))
        elif op == 13:
            v = S.pop() if S else 0
            if len(L) < common.MAXLEN:
                L.insert(0, clampv(v))
        elif op == 14:
            if L and len(S) < SMAX:
                S.append(L.pop(0))
        elif op == 15:
            if L and len(S) < SMAX:
                S.append(L.pop())
        elif op == 16:
            L.reverse()
        elif op == 17:
            if L:
                k = arg % len(L)
                L = L[k:] + L[:k]
        elif op == 18:
            d = arg - 8
            L = [clampv(v + d) for v in L]
        elif op == 19:
            m = (arg % 5) - 2
            L = [clampv(v * m) for v in L]
        elif op == 20:
            L = (L + L)[:common.MAXLEN]
        elif op == 21:
            v = S.pop() if S else 0
            if v == 0:
                pc += arg + 1
        elif op == 22:
            pc -= arg + 1
        elif op == 23:
            L = L[:arg + 1]
    return clampl(L), "ok"


def random_program(rng, size_hint=8):
    n = max(1, min(PROG_MAX, size_hint))
    return tuple(_tok(rng.randrange(NOPS), rng.randrange(NARG)) for _ in range(n))


def random_tokens(rng, n):
    return tuple(rng.randrange(0, NOPS * NARG) for _ in range(n))
