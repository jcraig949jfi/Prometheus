"""S4 REV -- reversible affine register machine over (Z_251)^6.

Every instruction is a bijection on register space (add/sub a multiple of one
register into another, swap, negate, controlled add with three distinct
registers), so every program is invertible and every tuple is a valid program.

Output arity is fixed at 6.  This basis is included as an adversarial control
for "total validity + reversibility is enough"; it is not repaired if it fails.
"""
from . import common
from .common import MAXVAL, PROG_MAX

NAME = "S4"
R = 6
M = 251
NOPS = 5
NREG = R
NMUL = 2
FUEL = 64
OPNAMES = ["ADD", "SUB", "SWAP", "NEG", "CADD"]

_PERM = list(range(NOPS))
_IPERM = list(range(NOPS))
_PERMA = list(range(NREG))
_IPERMA = list(range(NREG))


def set_order(perm_op, perm_reg):
    global _PERM, _IPERM, _PERMA, _IPERMA
    _PERM = list(perm_op)
    _IPERM = [0] * NOPS
    for i, v in enumerate(_PERM):
        _IPERM[v] = i
    _PERMA = list(perm_reg)
    _IPERMA = [0] * NREG
    for i, v in enumerate(_PERMA):
        _IPERMA[v] = i


def _tok(op, a, b, k):
    return _IPERM[op] + NOPS * _IPERMA[a % NREG] + NOPS * NREG * (b % NREG) \
        + NOPS * NREG * NREG * (k % NMUL)


def _untok(t):
    op = _PERM[t % NOPS]
    a = _PERMA[(t // NOPS) % NREG]
    b = (t // (NOPS * NREG)) % NREG
    k = (t // (NOPS * NREG * NREG)) % NMUL
    return op, a, b, k + 1


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
    regs = [0] * R
    for j, v in enumerate(inp):
        regs[j % R] = (regs[j % R] + int(v)) % M
    regs[R - 1] = (regs[R - 1] + len(inp)) % M
    n = 0
    for (op, a, b, k) in decode(prog):
        n += 1
        if n > FUEL:
            return None, "timeout"
        if op == 0:
            if a != b:
                regs[a] = (regs[a] + k * regs[b]) % M
        elif op == 1:
            if a != b:
                regs[a] = (regs[a] - k * regs[b]) % M
        elif op == 2:
            if a != b:
                regs[a], regs[b] = regs[b], regs[a]
        elif op == 3:
            regs[a] = (-regs[a]) % M
        else:
            c = (a + b + 1) % R
            if a != b and c != a and c != b and regs[c] != 0:
                regs[a] = (regs[a] + regs[b]) % M
    return tuple(regs), "ok"


def random_program(rng, size_hint=8):
    n = max(1, min(PROG_MAX, size_hint))
    return tuple(_tok(rng.randrange(NOPS), rng.randrange(NREG),
                      rng.randrange(NREG), rng.randrange(NMUL)) for _ in range(n))


def random_tokens(rng, n):
    return tuple(rng.randrange(0, NOPS * NREG * NREG * NMUL) for _ in range(n))
