"""RM-D5: bounded deterministic register machine. Spec: PREREG-PREFLIGHT.md section 1."""
import hashlib

WORD_MASK = 0xFFFF
NREG = 8
MAX_LEN = 24
STEP_BUDGET = 512
PALETTE = [0, 1, 2, 3, 5, 7, 11, 13, 16, 255]

# op -> kind of b operand: 'reg', 'const' (palette index), 'jump' (1..8), 'none'
OPS = {
    'MOV': 'reg', 'SET': 'const', 'ADD': 'reg', 'SUB': 'reg', 'MUL': 'reg',
    'AND': 'reg', 'OR': 'reg', 'XOR': 'reg', 'SHL': 'reg', 'SHR': 'reg',
    'MOD': 'reg', 'SKZ': 'none', 'SKG': 'reg', 'JNZ': 'jump',
}
OP_LIST = sorted(OPS)


def run(prog, inputs, step_budget=STEP_BUDGET):
    """Execute prog on inputs tuple; return (r0, steps). Total and deterministic."""
    regs = [0] * NREG
    for i, v in enumerate(inputs[:NREG]):
        regs[i] = v & WORD_MASK
    pc, steps, n = 0, 0, len(prog)
    while pc < n and steps < step_budget:
        op, a, b = prog[pc]
        steps += 1
        nxt = pc + 1
        if op == 'MOV':
            regs[a] = regs[b]
        elif op == 'SET':
            regs[a] = PALETTE[b]
        elif op == 'ADD':
            regs[a] = (regs[a] + regs[b]) & WORD_MASK
        elif op == 'SUB':
            regs[a] = (regs[a] - regs[b]) & WORD_MASK
        elif op == 'MUL':
            regs[a] = (regs[a] * regs[b]) & WORD_MASK
        elif op == 'AND':
            regs[a] &= regs[b]
        elif op == 'OR':
            regs[a] |= regs[b]
        elif op == 'XOR':
            regs[a] ^= regs[b]
        elif op == 'SHL':
            regs[a] = (regs[a] << (regs[b] % 16)) & WORD_MASK
        elif op == 'SHR':
            regs[a] = regs[a] >> (regs[b] % 16)
        elif op == 'MOD':
            regs[a] = regs[a] % regs[b] if regs[b] != 0 else 0
        elif op == 'SKZ':
            if regs[a] == 0:
                nxt = pc + 2
        elif op == 'SKG':
            if regs[a] > regs[b]:
                nxt = pc + 2
        elif op == 'JNZ':
            if regs[a] != 0:
                nxt = max(0, pc - b)
        pc = nxt
    return regs[0], steps


def behavior(prog, probe):
    """Output vector over probe inputs (each a tuple)."""
    return tuple(run(prog, x)[0] for x in probe)


def behavior_class(vec):
    return hashlib.sha256(repr(vec).encode()).hexdigest()[:16]


def hamming(vec_a, vec_b):
    return sum(1 for x, y in zip(vec_a, vec_b) if x != y)


def genotype_key(prog):
    return hashlib.sha256(repr(prog).encode()).hexdigest()[:16]
