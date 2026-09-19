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
}
OPNAMES = list(OPSPEC)
OP = {name: i for i, name in enumerate(OPNAMES)}
_FIRST_STORE_OP = OP["WS_READ"]
INPUT_FIELDS = ("current", "target", "interactions_left", "num_ops", "task_index",
                "steps_left", "last_delta", "current_block", "last_action")
IMM_RANGE = (-20, 20)


# ---------------------------------------------------------------- values


def to_int(v) -> int:
    if isinstance(v, tuple):
        return int(v[0]) if v else 0
    return int(v)


def _wrap(i: int) -> int:
    return ((i + INT_WRAP) % (2 * INT_WRAP)) - INT_WRAP


def _arith(fn, x, y):
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


def assemble(text: str) -> list:
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
    if len(program) > MAX_PROGRAM_LEN:
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
    __slots__ = ("regs", "ws", "blocks", "env", "recording", "depth", "instr_count")

    def __init__(self, env, ws, blocks):
        self.regs = [0] * NREG
        self.ws = ws
        self.blocks = blocks
        self.env = env
        self.recording = None
        self.depth = 0
        self.instr_count = 0


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
    try:
        _execute(b.instructions, st, block_id=b.block_id)
    finally:
        st.depth -= 1
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
            if isinstance(x, tuple) != isinstance(y, tuple):
                x, y = to_int(x), to_int(y)
            regs[a] = 1 if x < y else 0
        elif name == "NOT":
            regs[a] = 1 if is_zero(regs[b]) else 0
        elif name == "VGET":
            v = regs[b]
            regs[a] = v[to_int(regs[c]) % len(v)] if isinstance(v, tuple) and v else to_int(v)
        elif name == "VSET":
            v = regs[a]
            if isinstance(v, tuple) and v:
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
            else:
                regs[a] = env.observation()[INPUT_FIELDS[f]]
        elif name == "ACT":
            v = to_int(regs[a])
            if st.recording is not None:
                st.recording.append((OP["ACTI"], v % (world.NUM_OPS + 1), 0, 0))
            env.act(v)
        elif name == "ACTI":
            if st.recording is not None:
                st.recording.append((OP["ACTI"], a % (world.NUM_OPS + 1), 0, 0))
            env.act(a)
        else:
            raise RuntimeError("unknown opcode %r" % (opc,))


def _store_op(name, a, b, c, st, block_id):
    regs = st.regs
    ws = st.ws
    blocks = st.blocks
    if False:
        pass
    elif name == "WS_READ":
        regs[a] = ws.read(to_int(regs[b]))
    elif name == "WS_WRITE":
        ws.write(to_int(regs[a]), regs[b])
    elif name == "WS_APPEND":
        ws.append(to_int(regs[a]), regs[b])
    elif name == "WS_SREAD":
        regs[a] = ws.read_stream(to_int(regs[b]), to_int(regs[c]))
    elif name == "WS_SLEN":
        regs[a] = ws.stream_len(to_int(regs[b]))
    elif name == "WS_REC_NEW":
        regs[a] = ws.create_record()
    elif name == "WS_REC_GET":
        regs[a] = ws.get_field(to_int(regs[b]), to_int(regs[c]))
    elif name == "WS_REC_SET":
        ws.set_field(to_int(regs[a]), to_int(regs[b]), regs[c])
    elif name == "WS_LINK":
        ws.create_link(to_int(regs[a]), to_int(regs[b]), to_int(regs[c]))
    elif name == "WS_LINKS":
        regs[a] = len(ws.links_from(to_int(regs[b])))
    elif name == "WS_LINK_GET":
        regs[a] = ws.link_get(to_int(regs[b]), to_int(regs[c]))
    elif name == "WS_ALLOC":
        regs[a] = ws.allocate(to_int(regs[b]))
    elif name == "WS_FREE":
        ws.free(to_int(regs[a]))
    elif name == "WS_FIND":
        regs[a] = ws.find(regs[b])
    elif name == "BLK_NEW":
        regs[a] = blocks.create()
    elif name == "BLK_APPEND":
        ins = regs[b]
        if isinstance(ins, tuple) and len(ins) == 4:
            blocks.append(to_int(regs[a]), (ins[0] % len(OPNAMES), ins[1], ins[2], ins[3]))
        else:
            blocks.cost += 1
    elif name == "BLK_PATCH":
        ins = regs[c]
        if isinstance(ins, tuple) and len(ins) == 4:
            blocks.patch(to_int(regs[a]), to_int(regs[b]), (ins[0] % len(OPNAMES), ins[1], ins[2], ins[3]))
        else:
            blocks.cost += 1
    elif name == "BLK_COPY":
        regs[a] = blocks.copy(to_int(regs[b]))
    elif name == "BLK_COMPOSE":
        regs[a] = blocks.compose(to_int(regs[b]), to_int(regs[c]))
    elif name == "BLK_DELETE":
        blocks.delete(to_int(regs[a]))
    elif name == "BLK_INVOKE":
        invoke_block(to_int(regs[a]), st, from_block=block_id)
    elif name == "BLK_LEN":
        regs[a] = blocks.length(to_int(regs[b]))
    elif name == "BLK_COUNT":
        regs[a] = blocks.count()
    elif name == "BLK_STATE_GET":
        regs[a] = blocks.state_get(to_int(regs[b]), to_int(regs[c]))
    elif name == "BLK_STATE_SET":
        blocks.state_set(to_int(regs[a]), to_int(regs[b]), regs[c])
    elif name == "BLK_REC_BEGIN":
        if st.recording is None:
            st.recording = []
    elif name == "BLK_REC_END":
        if st.recording is None:
            regs[a] = -1
        else:
            rec = st.recording
            st.recording = None
            regs[a] = blocks.create(rec, origin="record")
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
