"""The Player VM: a small register bytecode machine over ints and int tuples.

Instruction = (opcode, a, b, c). Eight registers R0..R7 hold an int or a
tuple of ints. Arithmetic is elementwise on tuples with int broadcast.
One instruction = one compute unit charged to the TaskRun. Registers are
volatile: they are reset at every task; persistence across tasks goes
only through the Workspace and the BlockStore.

Executable blocks (crius/artifacts.py) run in the caller's register file as
a macro call with their own local_state; a block's ACT instructions act
on the world. Recording (BLK_REC_BEGIN/END) captures emitted actions as
ACTI instructions into a new block.
"""

from __future__ import annotations

import hashlib
import json

from . import world
from .env import TaskOver

NREG = 8
INT_WRAP = 1 << 20
MAX_PROGRAM_LEN = 64
MAX_CALL_DEPTH = 4

# name -> argument kinds: R register, I immediate, A code address, F input field, N none
OPSPEC = {
    "CONST": ("R", "I", "N"),
    "MOV": ("R", "R", "N"),
    "ADD": ("R", "R", "R"),
    "SUB": ("R", "R", "R"),
    "MUL": ("R", "R", "R"),
    "DIV": ("R", "R", "R"),
    "MOD": ("R", "R", "R"),
    "EQ": ("R", "R", "R"),
    "LT": ("R", "R", "R"),
    "NOT": ("R", "R", "N"),
    "VGET": ("R", "R", "R"),
    "VSET": ("R", "R", "R"),
    "VLEN": ("R", "R", "N"),
    "BRZ": ("R", "A", "N"),
    "BRNZ": ("R", "A", "N"),
    "JMP": ("A", "N", "N"),
    "HALT": ("N", "N", "N"),
    "INPUT": ("R", "F", "N"),
    "ACT": ("R", "N", "N"),
    "ACTI": ("I", "N", "N"),
    "WS_READ": ("R", "R", "N"),
    "WS_WRITE": ("R", "R", "N"),
    "WS_APPEND": ("R", "R", "N"),
    "WS_SREAD": ("R", "R", "R"),
    "WS_SLEN": ("R", "R", "N"),
    "WS_REC_NEW": ("R", "N", "N"),
    "WS_REC_GET": ("R", "R", "R"),
    "WS_REC_SET": ("R", "R", "R"),
    "WS_LINK": ("R", "R", "R"),
    "WS_LINKS": ("R", "R", "N"),
    "WS_LINK_GET": ("R", "R", "R"),
    "WS_ALLOC": ("R", "R", "N"),
    "WS_FREE": ("R", "N", "N"),
    "WS_FIND": ("R", "R", "N"),
    "BLK_NEW": ("R", "N", "N"),
    "BLK_APPEND": ("R", "R", "N"),
    "BLK_PATCH": ("R", "R", "R"),
    "BLK_COPY": ("R", "R", "N"),
    "BLK_COMPOSE": ("R", "R", "R"),
    "BLK_DELETE": ("R", "N", "N"),
    "BLK_INVOKE": ("R", "N", "N"),
    "BLK_LEN": ("R", "R", "N"),
    "BLK_COUNT": ("R", "N", "N"),
    "BLK_STATE_GET": ("R", "R", "R"),
    "BLK_STATE_SET": ("R", "R", "R"),
    "BLK_REC_BEGIN": ("N", "N", "N"),
    "BLK_REC_END": ("R", "N", "N"),
    # ---- C2 typed procedures (DESIGN_C2 s4). Present in OPNAMES at every rung; executable only when the
    #      substrate enables them (SUBSTRATE flags); mutation draws from opcode_names(substrate).
    "PSTEP": ("I", "I", "N"),        # inside a procedure block: primitive (kind, (parg + off) mod L)
    "PREC_BEGIN": ("N", "N", "N"),
    "PREC_END": ("R", "N", "N"),
    "PINVOKE": ("R", "R", "N"),      # procedure handle, argument
    "PSIM": ("R", "R", "R"),         # r <- procedure(h, a) applied in the head to the object in r
    "PMATCH": ("R", "R", "R"),       # r <- 1 iff procedure(h, a) applied in the head to current == target
}
TYPED_OPS_B = ("PSTEP", "PREC_BEGIN", "PREC_END", "PINVOKE")
TYPED_OPS_C = ("PSIM", "PMATCH")
SUBSTRATE = {"typed_procedures": False, "psim": False}


def set_substrate(sub: dict) -> None:
    SUBSTRATE["typed_procedures"] = bool((sub or {}).get("typed_procedures", False))
    SUBSTRATE["psim"] = bool((sub or {}).get("psim", False))


def opcode_names(sub: dict = None) -> list:
    """The rung's mutable instruction set: base ops, plus typed ops the substrate enables."""
    sub = sub if sub is not None else SUBSTRATE
    names = [n for n in OPNAMES if n not in TYPED_OPS_B + TYPED_OPS_C]
    if sub.get("typed_procedures"):
        names += [n for n in TYPED_OPS_B if n != "PSTEP"]  # PSTEP is written by PREC_END, not by mutation
    if sub.get("psim"):
        names += list(TYPED_OPS_C)
    return names
OPNAMES = list(OPSPEC)
OP = {name: i for i, name in enumerate(OPNAMES)}
_FIRST_STORE_OP = OP["WS_READ"]
_TYPED_SET = {OP[n] for n in TYPED_OPS_B + TYPED_OPS_C}
INPUT_FIELDS = ("current", "target", "interactions_left", "num_ops", "task_index",
                "steps_left", "last_delta", "current_block", "last_action", "status", "last_primitive")


class Fail:
    """Tagged failure sentinel (DESIGN_C1 s4). Poisons arithmetic, never acts, never stored."""
    __slots__ = ("code",)

    def __init__(self, code: int = 1):
        self.code = code

    def __eq__(self, other):
        return isinstance(other, Fail) and other.code == self.code

    def __hash__(self):
        return hash(("Fail", self.code))

    def __repr__(self):
        return "FAIL(%d)" % self.code


FAIL = Fail(1)
IMM_RANGE = (-20, 20)


# ---------------------------------------------------------------- values


def to_int(v):
    """Int view of a value; None for the FAIL sentinel (callers treat None as invalid)."""
    if isinstance(v, Fail):
        return None
    if isinstance(v, tuple):
        return int(v[0]) if v else 0
    return int(v)


def _ti(v) -> int:
    """Int view for addressing: FAIL addresses nothing useful; map to -1."""
    i = to_int(v)
    return -1 if i is None else i


def _wrap(i: int) -> int:
    return ((i + INT_WRAP) % (2 * INT_WRAP)) - INT_WRAP


def _arith(fn, x, y):
    if isinstance(x, Fail) or isinstance(y, Fail):
        return FAIL
    if isinstance(x, tuple) or isinstance(y, tuple):
        if not isinstance(x, tuple):
            x = (x,) * len(y)
        if not isinstance(y, tuple):
            y = (y,) * len(x)
        return tuple(_wrap(fn(p, q)) for p, q in zip(x, y))
    return _wrap(fn(x, y))


def _div(p, q):
    return p // q if q != 0 else 0


def _mod(p, q):
    return p % q if q != 0 else 0


def is_zero(v) -> bool:
    if isinstance(v, Fail):
        return False
    if isinstance(v, tuple):
        return all(e == 0 for e in v)
    return v == 0


# ---------------------------------------------------------------- programs


def program_hash(program) -> str:
    return hashlib.sha256(json.dumps(program_to_json(program)).encode("ascii")).hexdigest()[:16]


def program_to_json(program) -> list:
    return [[OPNAMES[i[0]], int(i[1]), int(i[2]), int(i[3])] for i in program]


def program_from_json(data) -> list:
    return [(OP[i[0]], int(i[1]), int(i[2]), int(i[3])) for i in data]


def assemble(text: str, max_len: int = None) -> list:
    """Two-pass assembler: `label:` lines, `OP a, b, c`, `;` comments, R-prefixed regs."""
    lines = []
    labels = {}
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        if line.endswith(":"):
            labels[line[:-1].strip()] = len(lines)
            continue
        lines.append(line)
    program = []
    for line in lines:
        parts = line.replace(",", " ").split()
        name = parts[0].upper()
        args = parts[1:]
        kinds = OPSPEC[name]
        vals = []
        for k, kind in enumerate(kinds):
            if kind == "N":
                vals.append(0)
                continue
            tok = args[k]
            if kind == "R":
                vals.append(int(tok[1:]) if tok[0] in "Rr" else int(tok))
            elif kind == "A":
                vals.append(labels[tok] if tok in labels else int(tok))
            elif kind == "F":
                vals.append(INPUT_FIELDS.index(tok) if tok in INPUT_FIELDS else int(tok))
            else:
                vals.append(int(tok))
        program.append((OP[name], vals[0], vals[1], vals[2]))
    if len(program) > (max_len or MAX_PROGRAM_LEN):
        raise ValueError("program too long: %d" % len(program))
    return program


def disassemble(program) -> str:
    out = []
    for pc, (opc, a, b, c) in enumerate(program):
        name = OPNAMES[opc]
        kinds = OPSPEC[name]
        args = []
        for kind, v in zip(kinds, (a, b, c)):
            if kind == "N":
                continue
            if kind == "R":
                args.append("R%d" % v)
            elif kind == "F":
                args.append(INPUT_FIELDS[v] if 0 <= v < len(INPUT_FIELDS) else str(v))
            else:
                args.append(str(v))
        out.append("%3d  %-14s %s" % (pc, name, ", ".join(args)))
    return "\n".join(out)


# ---------------------------------------------------------------- execution


class VMState:
    __slots__ = ("regs", "ws", "blocks", "env", "recording", "depth", "instr_count", "trace", "prec", "parg")

    def __init__(self, env, ws, blocks):
        self.regs = [0] * NREG
        self.ws = ws
        self.blocks = blocks
        self.env = env
        self.recording = None
        self.depth = 0
        self.instr_count = 0
        self.trace = {}  # opcode name -> executions this task (store ops, ACT, INPUT); for post-hoc recovery
        self.prec = None   # list of revealed primitives while PREC recording
        self.parg = 0      # the argument of the procedure being executed (PINVOKE sets it)


def run_program(program, env, ws, blocks) -> VMState:
    """Run a Player program on one task until the task ends or the program halts."""
    st = VMState(env, ws, blocks)
    try:
        _execute(program, st, block_id=-1)
    except TaskOver:
        pass
    except RecursionError:
        pass
    return st


def invoke_block(block_id: int, st: VMState, from_block: int = -1) -> bool:
    """Execute a stored block in the caller's register file. Used by the VM and by baselines."""
    b = st.blocks.blocks.get(int(block_id))
    if b is None:
        st.blocks.cost += 1
        return False
    if st.depth >= MAX_CALL_DEPTH:
        return False
    st.blocks.note_invocation(b.block_id, from_block)
    st.depth += 1
    entry = tuple(st.regs[:4])
    t0 = len(st.env.trajectory)
    was_success = st.env.success
    try:
        _execute(b.instructions, st, block_id=b.block_id)
    finally:
        st.depth -= 1
        if st.env.success and not was_success:
            st.env.success_in_block = True  # the solving action was emitted inside an invoked block
        st.blocks.log_invocation(b.block_id, entry, [a for a, _ in st.env.trajectory[t0:]])
    return True


def _execute(code, st: VMState, block_id: int):
    regs = st.regs
    env = st.env
    ws = st.ws
    blocks = st.blocks
    n = len(code)
    pc = 0
    while 0 <= pc < n:
        opc, a, b, c = code[pc]
        pc += 1
        env.charge(1)
        st.instr_count += 1
        name = OPNAMES[opc]
        if opc >= _FIRST_STORE_OP or name in ("ACT", "ACTI", "INPUT", "BLK_INVOKE"):
            st.trace[name] = st.trace.get(name, 0) + 1
        if opc in _TYPED_SET:
            cost0 = ws.cost + blocks.cost
            _typed_op(name, a, b, c, st, block_id)
            extra = ws.cost + blocks.cost - cost0
            if extra > 0:
                env.charge_store(extra)
            continue
        if opc >= _FIRST_STORE_OP:
            # workspace and block operations: their cost units count against the step budget too
            cost0 = ws.cost + blocks.cost
            _store_op(name, a, b, c, st, block_id)
            extra = ws.cost + blocks.cost - cost0
            if extra > 0:
                env.charge_store(extra)
            continue
        if name == "CONST":
            regs[a] = _wrap(b)
        elif name == "MOV":
            regs[a] = regs[b]
        elif name == "ADD":
            regs[a] = _arith(lambda p, q: p + q, regs[b], regs[c])
        elif name == "SUB":
            regs[a] = _arith(lambda p, q: p - q, regs[b], regs[c])
        elif name == "MUL":
            regs[a] = _arith(lambda p, q: p * q, regs[b], regs[c])
        elif name == "DIV":
            regs[a] = _arith(_div, regs[b], regs[c])
        elif name == "MOD":
            regs[a] = _arith(_mod, regs[b], regs[c])
        elif name == "EQ":
            regs[a] = 1 if regs[b] == regs[c] else 0
        elif name == "LT":
            x, y = regs[b], regs[c]
            if isinstance(x, Fail) or isinstance(y, Fail):
                regs[a] = 0
            else:
                if isinstance(x, tuple) != isinstance(y, tuple):
                    x, y = to_int(x), to_int(y)
                regs[a] = 1 if x < y else 0
        elif name == "NOT":
            regs[a] = 1 if is_zero(regs[b]) else 0
        elif name == "VGET":
            v = regs[b]
            if isinstance(v, Fail) or isinstance(regs[c], Fail):
                regs[a] = FAIL
            else:
                regs[a] = v[to_int(regs[c]) % len(v)] if isinstance(v, tuple) and v else to_int(v)
        elif name == "VSET":
            v = regs[a]
            if isinstance(v, tuple) and v and not isinstance(regs[b], Fail) and not isinstance(regs[c], Fail):
                i = to_int(regs[b]) % len(v)
                regs[a] = v[:i] + (_wrap(to_int(regs[c])),) + v[i + 1 :]
        elif name == "VLEN":
            v = regs[b]
            regs[a] = len(v) if isinstance(v, tuple) else 1
        elif name == "BRZ":
            if is_zero(regs[a]):
                pc = b
        elif name == "BRNZ":
            if not is_zero(regs[a]):
                pc = b
        elif name == "JMP":
            pc = a
        elif name == "HALT":
            if block_id == -1:
                env.halt()
            return
        elif name == "INPUT":
            f = b % len(INPUT_FIELDS)
            if f == 7:
                regs[a] = block_id
            elif f == 9:
                regs[a] = env.status
            elif f == 10:
                regs[a] = env.last_primitive
            else:
                regs[a] = env.observation()[INPUT_FIELDS[f]]
        elif name == "ACT":
            v = to_int(regs[a])
            if v is not None and env.valid_action(v) and st.recording is not None:
                st.recording.append((OP["ACTI"], v, 0, 0))
            _act(st, v)
        elif name == "ACTI":
            if env.valid_action(a) and st.recording is not None:
                st.recording.append((OP["ACTI"], a, 0, 0))
            _act(st, a)
        else:
            raise RuntimeError("unknown opcode %r" % (opc,))


# ---------------------------------------------------------------- typed procedures (C2 rungs B-D)

CAL_ORIGIN = "calibration"
PROC_ORIGIN = "procedure"


def _act(st, v):
    """Perform an action and, when the substrate keeps a calibration object, record what it did."""
    env = st.env
    before = env.interactions
    env.act(v)
    if SUBSTRATE["typed_procedures"] and env.interactions > before and env.last_primitive >= 0:
        _calibrate(st, v, env.last_primitive)
    if st.prec is not None and env.interactions > before and env.last_primitive >= 0:
        st.prec.append(env.last_primitive)


def _cal_block(st, create: bool):
    for b in st.blocks.blocks.values():
        if b.origin == CAL_ORIGIN:
            return b
    if not create:
        return None
    from . import world_c1 as w
    bid = st.blocks.create([], origin=CAL_ORIGIN)
    if bid < 0:
        return None
    b = st.blocks.blocks[bid]
    b.local_state[0] = tuple([-1] * w.NUM_PRIMITIVES)
    b.local_state[1] = tuple([-1] * w.NUM_PRIMITIVES)
    return b


def _calibrate(st, action: int, prim: int):
    b = _cal_block(st, create=True)
    if b is None:
        return
    fwd = list(b.local_state[0])
    inv = list(b.local_state[1])
    if 0 <= action < len(fwd) and fwd[action] != prim:
        fwd[action] = prim
        inv[prim] = action
        b.local_state[0] = tuple(fwd)
        b.local_state[1] = tuple(inv)
        st.blocks.cost += 1


def _proc_steps(st, handle):
    h = to_int(handle)
    if h is None:
        return None
    b = st.blocks.blocks.get(h)
    if b is None or b.origin != PROC_ORIGIN:
        return None
    return [(ins[1], ins[2]) for ins in b.instructions if OPNAMES[ins[0]] == "PSTEP"]


def _mental(st, steps, arg, x):
    from . import world_c1 as w
    if not isinstance(x, tuple) or len(x) != w.L:
        return FAIL
    for kind, off in steps:
        x = w.apply_primitive(w.KINDS[kind % len(w.KINDS)], (arg + off) % w.L, x)
    st.env.charge(len(steps))
    return x


def _typed_op(name, a, b, c, st, block_id):
    env = st.env
    regs = st.regs
    from . import world_c1 as w
    if not SUBSTRATE["typed_procedures"] or (name in TYPED_OPS_C and not SUBSTRATE["psim"]):
        env.status = 1
        if OPSPEC[name][0] == "R":
            regs[a] = FAIL
        return
    if name == "PSTEP":
        cal = _cal_block(st, create=False)
        prim = (a % len(w.KINDS)) * w.L + (st.parg + b) % w.L
        act_id = cal.local_state[1][prim] if cal is not None else -1
        if act_id < 0:
            env.status = 1
            return
        _act(st, act_id)
    elif name == "PREC_BEGIN":
        st.prec = []   # (re)start: a PREC_BEGIN while recording discards the recording so far
    elif name == "PREC_END":
        if st.prec is None or not st.prec:
            st.prec = None
            env.status = 1
            regs[a] = FAIL
            return
        prims = st.prec
        st.prec = None
        base = prims[0] % w.L
        ins = [(OP["PSTEP"], p // w.L, (p % w.L - base) % w.L, 0) for p in prims]
        bid = st.blocks.create(ins, origin=PROC_ORIGIN)
        regs[a] = _fail(st, bid)
    elif name == "PINVOKE":
        steps = _proc_steps(st, regs[a])
        arg = to_int(regs[b])
        if steps is None or arg is None:
            env.status = 1
            return
        saved = st.parg
        st.parg = arg % w.L
        try:
            invoke_block(to_int(regs[a]), st, from_block=block_id)
        finally:
            st.parg = saved
    elif name == "PSIM":
        steps = _proc_steps(st, regs[b])
        arg = to_int(regs[c])
        regs[a] = FAIL if (steps is None or arg is None) else _mental(st, steps, arg % w.L, regs[a])
        if isinstance(regs[a], Fail):
            env.status = 1
    elif name == "PMATCH":
        steps = _proc_steps(st, regs[b])
        arg = to_int(regs[c])
        if steps is None or arg is None:
            regs[a] = 0        # "no match" for a handle that is not a procedure; status says why
            env.status = 1
        else:
            regs[a] = 1 if _mental(st, steps, arg % w.L, env.current) == env.target else 0


def _fail(st, result):
    """Map a store's negative id to the FAIL sentinel and set the status channel."""
    if isinstance(result, int) and result < 0:
        st.env.status = 1
        return FAIL
    return result


def _status(st, ok: bool):
    if not ok:
        st.env.status = 1


def _store_op(name, a, b, c, st, block_id):
    regs = st.regs
    ws = st.ws
    blocks = st.blocks
    if False:
        pass
    elif name == "WS_READ":
        regs[a] = ws.read(_ti(regs[b]))
    elif name == "WS_WRITE":
        _status(st, ws.write(_ti(regs[a]), regs[b]))
    elif name == "WS_APPEND":
        _status(st, ws.append(_ti(regs[a]), regs[b]))
    elif name == "WS_SREAD":
        regs[a] = ws.read_stream(_ti(regs[b]), _ti(regs[c]))
    elif name == "WS_SLEN":
        regs[a] = ws.stream_len(_ti(regs[b]))
    elif name == "WS_REC_NEW":
        regs[a] = _fail(st, ws.create_record())
    elif name == "WS_REC_GET":
        regs[a] = ws.get_field(_ti(regs[b]), _ti(regs[c]))
    elif name == "WS_REC_SET":
        _status(st, ws.set_field(_ti(regs[a]), _ti(regs[b]), regs[c]))
    elif name == "WS_LINK":
        ws.create_link(_ti(regs[a]), _ti(regs[b]), _ti(regs[c]))
    elif name == "WS_LINKS":
        regs[a] = len(ws.links_from(_ti(regs[b])))
    elif name == "WS_LINK_GET":
        regs[a] = ws.link_get(_ti(regs[b]), _ti(regs[c]))
    elif name == "WS_ALLOC":
        regs[a] = _fail(st, ws.allocate(_ti(regs[b])))
    elif name == "WS_FREE":
        ws.free(_ti(regs[a]))
    elif name == "WS_FIND":
        regs[a] = ws.find(regs[b])
    elif name == "BLK_NEW":
        regs[a] = _fail(st, blocks.create())
    elif name == "BLK_APPEND":
        ins = regs[b]
        if isinstance(ins, tuple) and len(ins) == 4:
            blocks.append(_ti(regs[a]), (ins[0] % len(OPNAMES), ins[1], ins[2], ins[3]))
        else:
            blocks.cost += 1
    elif name == "BLK_PATCH":
        ins = regs[c]
        if isinstance(ins, tuple) and len(ins) == 4:
            blocks.patch(_ti(regs[a]), _ti(regs[b]), (ins[0] % len(OPNAMES), ins[1], ins[2], ins[3]))
        else:
            blocks.cost += 1
    elif name == "BLK_COPY":
        regs[a] = _fail(st, blocks.copy(_ti(regs[b])))
    elif name == "BLK_COMPOSE":
        regs[a] = _fail(st, blocks.compose(_ti(regs[b]), _ti(regs[c])))
    elif name == "BLK_DELETE":
        blocks.delete(_ti(regs[a]))
    elif name == "BLK_INVOKE":
        invoke_block(_ti(regs[a]), st, from_block=block_id)
    elif name == "BLK_LEN":
        regs[a] = blocks.length(_ti(regs[b]))
    elif name == "BLK_COUNT":
        regs[a] = blocks.count()
    elif name == "BLK_STATE_GET":
        regs[a] = blocks.state_get(_ti(regs[b]), _ti(regs[c]))
    elif name == "BLK_STATE_SET":
        blocks.state_set(_ti(regs[a]), _ti(regs[b]), regs[c])
    elif name == "BLK_REC_BEGIN":
        if st.recording is None:
            st.recording = []
    elif name == "BLK_REC_END":
        if st.recording is None:
            regs[a] = FAIL
            st.env.status = 1
        else:
            rec = st.recording
            st.recording = None
            regs[a] = _fail(st, blocks.create(rec, origin="record"))
    else:
        raise RuntimeError("unknown store opcode %r" % (name,))


# ---------------------------------------------------------------- the ARM-S seed

ENUMERATE_SOURCE = """
; iterative deepening over op sequences of length 1..3 using RESET (value = num_ops).
; uses no workspace and no blocks. R1 = num_ops, R5 = 1.
    INPUT R1, num_ops
    CONST R5, 1
    CONST R0, 0
    MOV   R2, R1
L1:
    LT    R3, R0, R2
    BRZ   R3, D2
    ACT   R1
    ACT   R0
    ADD   R0, R0, R5
    JMP   L1
D2:
    CONST R0, 0
    MUL   R2, R1, R1
L2:
    LT    R3, R0, R2
    BRZ   R3, D3
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    ADD   R0, R0, R5
    JMP   L2
D3:
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L3:
    LT    R3, R0, R2
    BRZ   R3, END
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    ADD   R0, R0, R5
    JMP   L3
END:
    HALT
"""


def enumerate_program() -> list:
    return assemble(ENUMERATE_SOURCE)
