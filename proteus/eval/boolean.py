"""H1 Boolean substrate: a bounded typed grammar compiled to a DECLARED subset of VM semantics.

    expr -> compile_boolean(expr) -> player manifest -> proteus.eval.library.evaluate

WHAT IS DECLARED. The compiler emits ONLY these opcodes, and nothing here may quietly widen that
set without changing INTERFACE_VERSION:

    IN  (21)  read the next unread value from an input channel
    LDC (3)   load a 32-bit immediate           (immediate is in slot b -- verified by execution)
    AND (10)  OR (11)  XOR (12)                 bitwise, exact on {0,1}
    OUT (23)  append a register to an output channel
    HALT (1)  end the tick

NOT IS COMPILED AS `XOR x, ONE`, NOT as the VM's NOT opcode. The VM's NOT is bitwise complement
mod 2^32, so NOT(1) is 4294967294, not 0. Using it would silently leave the Boolean domain on the
very first negation. This is the single most important compilation decision in the file.

TRUTH VALUES are exactly 0 and 1. The compiler never produces another value, and the independent
evaluator asserts it.

REGISTER DISCIPLINE (n_regs = 16)
    r15   channel selector, always 0 -- registers start at 0 and r15 is never written
    r14   the constant 1, for NOT
    r0..r2  the three inputs, read once each, in declared order
    r3..r13 temporaries, allocated as a stack by post-order traversal (depth bound 11)

INDEPENDENCE. `truth_table` evaluates the AST in Python with no VM involvement whatsoever. It is
the independent oracle the brief requires; parity between it and the compiled program over all 8
inputs is what makes the substrate trustworthy, and a disagreement is a real defect rather than a
convention mismatch.

FINITE CORRECTNESS SCOPE is stated by `correctness_scope()` and is EXHAUSTIVE for 3-input tasks
over all 8 assignments. Nothing here is verified for wider arities; 4+ inputs are beta.

NOTHING IN THIS MODULE SELECTS, SCORES OR NAMES A PROGRAM INTERESTING.
"""
from __future__ import annotations

from proteus.eval.library import EvaluationError, evaluate, make_spec

INTERFACE_VERSION = "proteus.boolean3.v0"
GRAMMAR_VERSION = "proteus.boolean_grammar.v0"

N_INPUTS = 3
N_REGS = 16
TAPE_WORDS = 256
TICK_BUDGET = 256
OUT_CAP = 4

R_CHANNEL = 15          # holds 0 -> selects channel 0 for IN and OUT
R_ONE = 14              # holds the constant 1
R_INPUT_BASE = 0        # r0, r1, r2
TEMP_LO, TEMP_HI = 3, 13

# opcodes actually emitted (the declared subset)
OP_HALT, OP_LDC, OP_AND, OP_OR, OP_XOR, OP_IN, OP_OUT = 1, 3, 10, 11, 12, 21, 23
DECLARED_OPCODES = (OP_HALT, OP_LDC, OP_AND, OP_OR, OP_XOR, OP_IN, OP_OUT)

CONST, INPUT, NOT, AND, OR, XOR = "const", "input", "not", "and", "or", "xor"
ARITY = {CONST: 0, INPUT: 0, NOT: 1, AND: 2, OR: 2, XOR: 2}


class BooleanError(ValueError):
    """Malformed expression or one that cannot be compiled. Fails closed."""


# --------------------------------------------------------------------------- grammar

def C(v):
    if v not in (0, 1):
        raise BooleanError(f"constant must be 0 or 1, got {v!r}")
    return (CONST, v)


def I(i):
    if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < N_INPUTS:
        raise BooleanError(f"input index must be an int in [0,{N_INPUTS}), got {i!r}")
    return (INPUT, i)


def Not(x):
    return (NOT, x)


def And(x, y):
    return (AND, x, y)


def Or(x, y):
    return (OR, x, y)


def Xor(x, y):
    return (XOR, x, y)


def check(expr, _depth=0):
    """Type/arity/depth check. Returns the depth. Fails closed on anything malformed."""
    if not isinstance(expr, tuple) or not expr:
        raise BooleanError(f"expression must be a non-empty tuple, got {expr!r}")
    op = expr[0]
    if op not in ARITY:
        raise BooleanError(f"unknown operator {op!r}")
    n = ARITY[op]
    if op in (CONST, INPUT):
        if len(expr) != 2:
            raise BooleanError(f"{op} takes exactly one payload")
        if op == CONST and expr[1] not in (0, 1):
            raise BooleanError("constant must be 0 or 1")
        if op == INPUT and not (isinstance(expr[1], int) and 0 <= expr[1] < N_INPUTS):
            raise BooleanError("input index out of range")
        return _depth
    if len(expr) != n + 1:
        raise BooleanError(f"{op} takes exactly {n} operand(s), got {len(expr) - 1}")
    return max(check(a, _depth + 1) for a in expr[1:])


def truth_table(expr, n_inputs=N_INPUTS):
    """INDEPENDENT oracle: evaluate the AST in Python. No VM. Returns a list of 0/1, MSB-first.

    Assignment order is declared and fixed: index k of the returned list corresponds to the
    assignment whose bit j is (k >> (n_inputs - 1 - j)) & 1, i.e. input 0 is the most significant.
    """
    check(expr)
    out = []
    for k in range(2 ** n_inputs):
        env = [(k >> (n_inputs - 1 - j)) & 1 for j in range(n_inputs)]
        v = _eval(expr, env)
        if v not in (0, 1):
            raise BooleanError(f"independent evaluator left the Boolean domain: {v!r}")
        out.append(v)
    return out


def _eval(e, env):
    op = e[0]
    if op == CONST:
        return e[1]
    if op == INPUT:
        return env[e[1]]
    if op == NOT:
        return 1 - _eval(e[1], env)
    a = _eval(e[1], env)
    b = _eval(e[2], env)
    if op == AND:
        return a & b
    if op == OR:
        return a | b
    if op == XOR:
        return a ^ b
    raise BooleanError(f"unknown operator {op!r}")


def assignments(n_inputs=N_INPUTS):
    """The declared, ordered assignment list matching `truth_table`."""
    return [[(k >> (n_inputs - 1 - j)) & 1 for j in range(n_inputs)]
            for k in range(2 ** n_inputs)]


# --------------------------------------------------------------------------- compiler

def compile_boolean(expr, n_inputs=N_INPUTS):
    """Compile to a player manifest using only the DECLARED opcode subset."""
    depth = check(expr)
    words = []

    def emit(op, a=0, b=0, c=0):
        words.extend([op, a, b, c])

    # prologue: constant 1, then read the inputs in declared order
    emit(OP_LDC, R_ONE, 1, 0)
    for i in range(n_inputs):
        emit(OP_IN, R_INPUT_BASE + i, R_CHANNEL, 0)

    n_temps = TEMP_HI - TEMP_LO + 1

    def gen(e, t):
        """Emit code leaving the value of `e` in register `t`. Temporaries above t are free."""
        if t > TEMP_HI:
            raise BooleanError(
                f"expression needs more than {n_temps} temporaries (depth {depth}); "
                f"raise the bound deliberately rather than by accident")
        op = e[0]
        if op == CONST:
            emit(OP_LDC, t, e[1], 0)
        elif op == INPUT:
            # MOV would do; XOR with 0 keeps the emitted opcode set minimal and is exact on {0,1}
            emit(OP_XOR, t, R_INPUT_BASE + e[1], R_CHANNEL)
        elif op == NOT:
            gen(e[1], t)
            emit(OP_XOR, t, t, R_ONE)          # NOT x == x XOR 1 on {0,1}
        else:
            gen(e[1], t)
            gen(e[2], t + 1)
            emit({AND: OP_AND, OR: OP_OR, XOR: OP_XOR}[op], t, t, t + 1)

    gen(expr, TEMP_LO)
    emit(OP_OUT, TEMP_LO, R_CHANNEL, 0)
    emit(OP_HALT)

    for w in words[::4]:
        if w not in DECLARED_OPCODES:
            raise BooleanError(f"compiler emitted undeclared opcode {w}")
    if len(words) > TAPE_WORDS:
        raise BooleanError("compiled program exceeds the tape")
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": N_REGS,
            "tape_words": TAPE_WORDS, "genome": words, "code_writable": False,
            "persist": "none", "tick_budget": TICK_BUDGET, "out_cap": OUT_CAP}


# --------------------------------------------------------------------------- task / oracle

def boolean_spec(expr, n_inputs=N_INPUTS, ticks=2):
    """The exhaustive specification for `expr`: all 2^n assignments, in declared order.

    Labels come from the INDEPENDENT evaluator, so the specification never depends on the VM.
    """
    tt = truth_table(expr, n_inputs)
    cases = [{"inputs": [list(a)], "expected": [[v]]}
             for a, v in zip(assignments(n_inputs), tt)]
    return make_spec(cases, n_out=1, ticks=ticks, label="boolean3")


def oracle_labels(expr, inputs_list, n_inputs=N_INPUTS):
    """Recompute labels for arbitrary inputs with the INDEPENDENT evaluator.

    THIS IS THE ONLY WAY LABELS MAY ENTER A TARGET RUN. A witness pack carries INPUTS; the target
    oracle recomputes truth here. A transferred source label is never trusted, so a wrong source
    label cannot corrupt a target result -- it can only waste a probe.
    """
    check(expr)
    out = []
    for inputs in inputs_list:
        if len(inputs) != n_inputs or any(v not in (0, 1) for v in inputs):
            raise BooleanError(f"input must be {n_inputs} bits in {{0,1}}, got {inputs!r}")
        out.append(_eval(expr, list(inputs)))
    return out


def correctness_scope():
    """The EXACT finite scope over which this substrate is exhaustively verified."""
    return {
        "interface_version": INTERFACE_VERSION,
        "grammar_version": GRAMMAR_VERSION,
        "arity_exhaustively_verified": N_INPUTS,
        "assignments_per_task": 2 ** N_INPUTS,
        "assignment_order": "input 0 is most significant; k-th case has bit j = (k >> (n-1-j)) & 1",
        "primitives": [CONST, INPUT, NOT, AND, OR, XOR],
        "declared_opcodes": list(DECLARED_OPCODES),
        "not_is_compiled_as": "XOR x, 1 -- the VM's NOT is bitwise complement and leaves {0,1}",
        "max_temporaries": TEMP_HI - TEMP_LO + 1,
        "verified_beyond_3_inputs": False,
        "note": ("Exhaustive means all 8 assignments for every task tested, not all tasks. The "
                 "set of expressions checked is stated by the test that checks them."),
    }


# --------------------------------------------------------------------------- run helper

def run_boolean(expr, seed=0, genome_read=False):
    """Compile, evaluate exhaustively, and return the B1 result (ordering + budget policy intact)."""
    man = compile_boolean(expr)
    res = evaluate(man, boolean_spec(expr), seed=seed)
    if genome_read:
        from proteus.eval.genome_read import genome_read_report
        res["genome_read"] = genome_read_report(man, boolean_spec(expr), seed=seed)
    return man, res
