"""AR-1 machine: a linear STACK-TAPE STREAM machine (Beta-04 Experiment E, the alien-representation reserve).

INDEPENDENT INTERPRETER. Nothing here imports or mirrors tfs1.core or the foundry interpreter; the only shared things
are the contract-v0 I/O conventions: input = one list of ints (xs); output = an Int / Bool / List value or FAIL
(the string "FAIL"); any arithmetic result with |v| > 10**18 is FAIL; a FAIL anywhere makes the whole output FAIL.

PROGRAM = a TAPE: a flat sequence of tokens. EVERY token sequence is an executable program (no syntax filter).
Base alphabet (23 tokens; see AR1_DESIGN.md s2 for the rationale and what is deliberately absent):

  0 1 2 3      push the constant
  a            push register A                     A   pop -> register A      (A starts at 0)
  + - * / %    pop y, pop x, push x op y  (/ floor division, % Python modulo; y == 0 -> FAIL)
  n            negate the top                      <   pop y, pop x, push 1 if x < y else 0
  =            pop y, pop x, push 1 if x == y else 0
  d            dup the top                         s   swap the top two          p   pop (drop) the top
  ?            pop c; if c == 0 SKIP the next instruction (one token, one whole loop block, or one macro token)
  [  ]         loop block: for each element e of the current list L (snapshot at loop entry): push e, run the body.
               An unmatched ']' is a no-op; an unmatched '[' closes at the end of its tape.
  .            pop -> append to the output buffer O
  l            re-list: L := O, O := []   (L starts as the input xs)
  #            push len(L)

MACROS (acquired units): a macro token '@<name>' stands for a tape segment; it executes the segment inline and is ONE
instruction for '?'. Macro bodies are tapes themselves (they may contain earlier macros).

OUTPUT by the family's output type (inferred from dev outputs, exactly like the arm view does):
  Int  -> the top of the stack at the end (empty stack -> FAIL)
  Bool -> top of the stack != 0 (empty -> FAIL)
  List -> the output buffer O

GUARDS (all -> FAIL): stack underflow; division / modulo by 0; |arithmetic result| > CEIL; more than ITER_MAX loop
iterations in one run; stack depth > STACK_MAX, checked at every loop-iteration start and at the end of the run (a
straight-line stretch is bounded by the tape length, so these two checks bound the stack).

TWO IMPLEMENTATIONS of the same semantics: `run_compiled` (the reference interpreter below; also counts the ledgers)
and `compile_fast` (straight-line Python code generation, used by the search for speed). They are checked against
each other on random tapes by alien/tests/run_tests.py (differential test).

LEDGERS (contract cost accounting): EXPANDED = every executed base instruction, including inside macros;
PROMOTED = every executed instruction written in the caller's own tape, a macro call counting 1.
"""
from typing import Dict, List, Optional, Sequence, Tuple

CEIL = 10 ** 18
FAIL = "FAIL"
STACK_MAX = 128
ITER_MAX = 1024

BASE: Tuple[str, ...] = ("0", "1", "2", "3", "a", "A", "+", "-", "*", "/", "%", "n", "<", "=", "d", "s", "p", "?",
                         "[", "]", ".", "l", "#")
BINOPS = frozenset("+-*/%<=")
PURE = frozenset("0123a+-*/%n<=ds")          # side-effect-free tokens (no store / emit / control / list state)
OPERATORS = frozenset("+-*/%n<=")

# opcodes
(OP_PUSH, OP_LDA, OP_STA, OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD, OP_LT, OP_EQ, OP_NEG, OP_DUP, OP_SWAP, OP_POP,
 OP_SKIP, OP_LOOP, OP_EMIT, OP_RELIST, OP_LEN, OP_MAC) = range(20)       # ADD..EQ contiguous (binary ops)
_SIMPLE = {"a": OP_LDA, "A": OP_STA, "+": OP_ADD, "-": OP_SUB, "*": OP_MUL, "/": OP_DIV, "%": OP_MOD, "n": OP_NEG,
           "<": OP_LT, "=": OP_EQ, "d": OP_DUP, "s": OP_SWAP, "p": OP_POP, "?": OP_SKIP, ".": OP_EMIT,
           "l": OP_RELIST, "#": OP_LEN}


class MachineFail(Exception):
    pass


_FX = MachineFail()


def _fail():
    raise _FX


# ================================================================ text
def parse(text: str) -> Tuple[str, ...]:
    """Canonical text = tokens separated by single spaces ('[ 1 + 3 / ]'). Base tokens may also be written run
    together ('[1+3/]'); macro tokens are '@name' and must be space-delimited."""
    out: List[str] = []
    for w in text.split():
        if w.startswith("@"):
            out.append(w)
            continue
        for ch in w:
            if ch not in BASE:
                raise ValueError("unknown AR-1 token %r in %r" % (ch, text))
            out.append(ch)
    return tuple(out)


def to_str(tape: Sequence[str]) -> str:
    return " ".join(tape)


def is_macro(tok: str) -> bool:
    return tok.startswith("@")


# ================================================================ compile
def compile_tape(tape: Sequence[str], macros: Optional[Dict[str, Tuple[str, ...]]] = None, _depth: int = 0):
    """Tape -> nested instruction list [(opcode, arg), ...]. Loops carry their compiled body; macros carry theirs."""
    if _depth > 8:
        raise ValueError("macro nesting too deep")
    macros = macros or {}
    pos = 0
    n = len(tape)

    def block(top: bool):
        nonlocal pos
        out = []
        while pos < n:
            t = tape[pos]
            pos += 1
            if t == "]":
                if top:
                    continue                 # unmatched ']' -> no-op
                return out
            if t == "[":
                out.append((OP_LOOP, block(False)))
            elif t in _SIMPLE:
                out.append((_SIMPLE[t], None))
            elif t in "0123":
                out.append((OP_PUSH, ord(t) - 48))
            elif t.startswith("@"):
                if t not in macros:
                    raise ValueError("unknown macro %s" % t)
                out.append((OP_MAC, compile_tape(macros[t], macros, _depth + 1)))
            else:
                raise ValueError("bad token %r" % t)
        return out                            # unmatched '[' closes at the end of the tape
    return block(True)


# ================================================================ execute
class _St:
    __slots__ = ("S", "A", "L", "O", "it", "ue", "up")

    def __init__(self, xs):
        self.S: List[int] = []
        self.A = 0
        self.L = xs
        self.O: List[int] = []
        self.it = 0
        self.ue = 0
        self.up = 0


def _exec(prog, st: _St, inmac: int):
    S = st.S
    i = 0
    m = len(prog)
    while i < m:
        op, arg = prog[i]
        i += 1
        st.ue += op != OP_MAC
        if not inmac:
            st.up += 1
        if op == OP_PUSH:
            S.append(arg)
        elif OP_ADD <= op <= OP_EQ:
            if len(S) < 2:
                _fail()
            y = S.pop()
            x = S[-1]
            if op == OP_ADD:
                r = x + y
            elif op == OP_SUB:
                r = x - y
            elif op == OP_MUL:
                r = x * y
            elif op == OP_DIV:
                if y == 0:
                    _fail()
                r = x // y
            elif op == OP_MOD:
                if y == 0:
                    _fail()
                r = x % y
            elif op == OP_LT:
                r = 1 if x < y else 0
            else:
                r = 1 if x == y else 0
            if r > CEIL or r < -CEIL:
                _fail()
            S[-1] = r
        elif op == OP_LOOP:
            for e in list(st.L):
                S.append(e)
                st.it += 1
                if len(S) > STACK_MAX or st.it > ITER_MAX:
                    _fail()
                _exec(arg, st, inmac)
        elif op == OP_DUP:
            if not S:
                _fail()
            S.append(S[-1])
        elif op == OP_SWAP:
            if len(S) < 2:
                _fail()
            S[-1], S[-2] = S[-2], S[-1]
        elif op == OP_POP:
            if not S:
                _fail()
            S.pop()
        elif op == OP_LDA:
            S.append(st.A)
        elif op == OP_STA:
            if not S:
                _fail()
            st.A = S.pop()
        elif op == OP_NEG:
            if not S:
                _fail()
            S[-1] = -S[-1]
        elif op == OP_SKIP:
            if not S:
                _fail()
            if S.pop() == 0:
                i += 1
        elif op == OP_EMIT:
            if not S:
                _fail()
            st.O.append(S.pop())
        elif op == OP_RELIST:
            st.L = st.O
            st.O = []
        elif op == OP_LEN:
            S.append(len(st.L))
        elif op == OP_MAC:
            _exec(arg, st, inmac + 1)


def run_compiled(prog, xs: List[int], out_type: str, ledger: Optional[list] = None):
    """Value or FAIL. ledger, if given, receives [expanded_units, promoted_units] (added)."""
    st = _St(list(xs))
    try:
        _exec(prog, st, 0)
        if len(st.S) > STACK_MAX:
            _fail()
        if out_type == "List":
            v = list(st.O)
        elif not st.S:
            v = FAIL
        elif out_type == "Bool":
            v = st.S[-1] != 0
        else:
            v = st.S[-1]
    except MachineFail:
        _FX.__traceback__ = None              # shared instance: never let tracebacks accumulate (tfs1 lesson)
        v = FAIL
    except RecursionError:
        v = FAIL
    if ledger is not None:
        ledger[0] += st.ue
        ledger[1] += st.up
    return v


def run(tape, xs: List[int], out_type: str, macros=None, ledger=None):
    if isinstance(tape, str):
        tape = parse(tape)
    return run_compiled(compile_tape(tape, macros), xs, out_type, ledger)


def run_frame(tape, stack: List[int], reg: int, macros=None):
    """Run a (pure) segment from a given stack + register; returns the final top of stack or FAIL (probe use)."""
    prog = compile_tape(tuple(tape), macros)
    st = _St([])
    st.S = list(stack)
    st.A = reg
    try:
        _exec(prog, st, 0)
        return st.S[-1] if st.S else FAIL
    except MachineFail:
        _FX.__traceback__ = None
        return FAIL


def same_value(a, b) -> bool:
    return a == b and type(a) is type(b)


# ================================================================ static stack signature
_EFFECT = {"0": (0, 1), "1": (0, 1), "2": (0, 1), "3": (0, 1), "a": (0, 1), "A": (1, 0), "+": (2, 1), "-": (2, 1),
           "*": (2, 1), "/": (2, 1), "%": (2, 1), "n": (1, 1), "<": (2, 1), "=": (2, 1), "d": (1, 2), "s": (2, 2),
           "p": (1, 0), ".": (1, 0), "#": (0, 1), "l": (0, 0)}


def signature(seg: Sequence[str], macros=None) -> Optional[Tuple[int, int]]:
    """(inputs consumed from below the segment's start, values left) for a STRAIGHT-LINE segment (no '?', '[', ']').
    Macros contribute their own signature. None if the segment is not straight-line."""
    macros = macros or {}
    d = k = 0
    for t in seg:
        if t.startswith("@"):
            sg = signature(macros[t], macros)
            if sg is None:
                return None
            m, q = sg[0], sg[1]
        elif t in _EFFECT:
            m, q = _EFFECT[t]
        else:
            return None
        if d < m:
            k += m - d
            d = m
        d = d - m + q
    return k, d


# ================================================================ fast path: straight-line Python code generation
_GEN = {
    OP_LDA: ["S.append(A)"],
    OP_STA: ["A = S.pop()"],
    OP_ADD: ["y = S.pop()", "r = S[-1] + y", "if r > C or r < -C: raise F", "S[-1] = r"],
    OP_SUB: ["y = S.pop()", "r = S[-1] - y", "if r > C or r < -C: raise F", "S[-1] = r"],
    OP_MUL: ["y = S.pop()", "r = S[-1] * y", "if r > C or r < -C: raise F", "S[-1] = r"],
    OP_DIV: ["y = S.pop()", "S[-1] = S[-1] // y"],          # y == 0 -> ZeroDivisionError -> FAIL
    OP_MOD: ["y = S.pop()", "S[-1] = S[-1] % y"],
    OP_LT: ["y = S.pop()", "S[-1] = 1 if S[-1] < y else 0"],
    OP_EQ: ["y = S.pop()", "S[-1] = 1 if S[-1] == y else 0"],
    OP_NEG: ["S[-1] = -S[-1]"],
    OP_DUP: ["S.append(S[-1])"],
    OP_SWAP: ["S[-1], S[-2] = S[-2], S[-1]"],
    OP_POP: ["S.pop()"],
    OP_EMIT: ["O.append(S.pop())"],
    OP_RELIST: ["L = O", "O = []"],
    OP_LEN: ["S.append(len(L))"],
}


def _gen_block(prog, ind: int, lines: List[str], ctr: List[int]):
    pad = " " * ind
    if not prog:
        lines.append(pad + "pass")
        return
    prev_skip = None
    for op, arg in prog:
        if prev_skip is not None:                 # guarded by the preceding '?'
            if op == OP_SKIP:
                ctr[0] += 1
                k = "k%d" % ctr[0]
                lines.append(pad + "%s = False" % k)
                lines.append(pad + "if not %s:" % prev_skip)
                lines.append(pad + "    %s = S.pop() == 0" % k)
                prev_skip = k
                continue
            lines.append(pad + "if not %s:" % prev_skip)
            _gen_one(op, arg, ind + 4, lines, ctr)
            prev_skip = None
            continue
        if op == OP_SKIP:
            ctr[0] += 1
            k = "k%d" % ctr[0]
            lines.append(pad + "%s = S.pop() == 0" % k)
            prev_skip = k
            continue
        _gen_one(op, arg, ind, lines, ctr)


def _gen_one(op, arg, ind, lines, ctr):
    pad = " " * ind
    if op == OP_PUSH:
        lines.append(pad + "S.append(%d)" % arg)
    elif op == OP_LOOP:
        ctr[0] += 1
        lines.append(pad + "for e%d in list(L):" % ctr[0])
        lines.append(pad + "    S.append(e%d)" % ctr[0])
        lines.append(pad + "    it += 1")
        lines.append(pad + "    if it > IM or len(S) > SM: raise F")
        _gen_block(arg, ind + 4, lines, ctr)
    elif op == OP_MAC:
        lines.append(pad + "if True:")
        _gen_block(arg, ind + 4, lines, ctr)
    else:
        for ln in _GEN[op]:
            lines.append(pad + ln)


def compile_fast(tape: Sequence[str], out_type: str, macros=None):
    """Tape -> a Python function xs -> value or FAIL with exactly the reference semantics (no ledgers)."""
    prog = compile_tape(tuple(tape), macros)
    lines = ["def f(xs):", "    S = []", "    A = 0", "    L = xs", "    O = []", "    it = 0", "    try:"]
    body: List[str] = []
    _gen_block(prog, 8, body, [0])
    lines += body
    lines.append("    except (IndexError, ZeroDivisionError, MachineFail):")
    lines.append("        F.__traceback__ = None")
    lines.append("        return 'FAIL'")
    lines.append("    if len(S) > SM: return 'FAIL'")
    if out_type == "List":
        lines.append("    return O")
    elif out_type == "Bool":
        lines.append("    return (S[-1] != 0) if S else 'FAIL'")
    else:
        lines.append("    return S[-1] if S else 'FAIL'")
    ns = {"C": CEIL, "F": _FX, "IM": ITER_MAX, "SM": STACK_MAX, "MachineFail": MachineFail}
    exec(compile("\n".join(lines), "<ar1>", "exec"), ns)
    return ns["f"]


# ================================================================ fast path 2: closure threading (no compile())
def _c_push(k):
    def f(S, st):
        S.append(k)
    return f


def _c_lda(S, st):
    S.append(st[0])


def _c_sta(S, st):
    st[0] = S.pop()


def _c_add(S, st):
    y = S.pop()
    r = S[-1] + y
    if r > CEIL or r < -CEIL:
        raise _FX
    S[-1] = r


def _c_sub(S, st):
    y = S.pop()
    r = S[-1] - y
    if r > CEIL or r < -CEIL:
        raise _FX
    S[-1] = r


def _c_mul(S, st):
    y = S.pop()
    r = S[-1] * y
    if r > CEIL or r < -CEIL:
        raise _FX
    S[-1] = r


def _c_div(S, st):
    y = S.pop()
    S[-1] = S[-1] // y


def _c_mod(S, st):
    y = S.pop()
    S[-1] = S[-1] % y


def _c_lt(S, st):
    y = S.pop()
    S[-1] = 1 if S[-1] < y else 0


def _c_eq(S, st):
    y = S.pop()
    S[-1] = 1 if S[-1] == y else 0


def _c_neg(S, st):
    S[-1] = -S[-1]


def _c_dup(S, st):
    S.append(S[-1])


def _c_swap(S, st):
    S[-1], S[-2] = S[-2], S[-1]


def _c_pop(S, st):
    S.pop()


def _c_emit(S, st):
    st[2].append(S.pop())


def _c_relist(S, st):
    st[1] = st[2]
    st[2] = []


def _c_len(S, st):
    S.append(len(st[1]))


def _c_skip(S, st):
    return S.pop() == 0


_CL = {OP_LDA: _c_lda, OP_STA: _c_sta, OP_ADD: _c_add, OP_SUB: _c_sub, OP_MUL: _c_mul, OP_DIV: _c_div,
       OP_MOD: _c_mod, OP_LT: _c_lt, OP_EQ: _c_eq, OP_NEG: _c_neg, OP_DUP: _c_dup, OP_SWAP: _c_swap, OP_POP: _c_pop,
       OP_EMIT: _c_emit, OP_RELIST: _c_relist, OP_LEN: _c_len, OP_SKIP: _c_skip}


def _cl_block(prog):
    fns = []
    has_skip = False
    for op, arg in prog:
        if op == OP_PUSH:
            fns.append(_c_push(arg))
        elif op == OP_LOOP:
            fns.append(_cl_loop(_cl_block(arg)))
        elif op == OP_MAC:
            fns.append(_cl_block(arg))
        else:
            fns.append(_CL[op])
            has_skip = has_skip or op == OP_SKIP
    fns = tuple(fns)
    n = len(fns)
    if not has_skip:
        def run(S, st):
            for fn in fns:
                fn(S, st)
        return run

    def run_skip(S, st):
        i = 0
        while i < n:
            if fns[i](S, st):
                i += 1
            i += 1
    return run_skip


def _cl_loop(body):
    def f(S, st):
        for e in list(st[1]):
            S.append(e)
            st[3] += 1
            if st[3] > ITER_MAX or len(S) > STACK_MAX:
                raise _FX
            body(S, st)
    return f


def compile_closure(tape: Sequence[str], out_type: str, macros=None):
    """Tape -> a function xs -> value or FAIL with exactly the reference semantics (no ledgers). Closure-threaded.
    Note: a macro (or loop) body returns None, so a '?' before it skips it as ONE instruction, as specified."""
    blk = _cl_block(compile_tape(tuple(tape), macros))
    lst, bl = out_type == "List", out_type == "Bool"

    def f(xs):
        S = []
        st = [0, xs, [], 0]
        try:
            blk(S, st)
        except (IndexError, ZeroDivisionError, MachineFail):
            _FX.__traceback__ = None
            return FAIL
        if len(S) > STACK_MAX:
            return FAIL
        if lst:
            return st[2]
        if not S:
            return FAIL
        return (S[-1] != 0) if bl else S[-1]
    return f
