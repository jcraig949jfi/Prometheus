"""A small Z80-LIKE substrate. Not the Z80 ISA; the properties that matter are preserved:

  byte-addressable executable representation   one 256-byte address space, code and data are the same bytes
  jumps / control flow                          JP, JZ, JNZ, JC, JR, DJNZ
  register / state operations                   A B C D (data), S T (pointers), Z/C flags
  copy / memory-write capability                LD (T),A ; LD (S),A ; LDI ; LDIR  (LDI/LDIR are the real Z80's)
  no privileged multiplication                  there is no MUL; shifts and adds only
  mutation alters algorithm AND architecture    any byte may be an opcode or an operand depending on where the PC lands
  reinterpretation after mutation               undefined opcodes execute as NOP, so a mutated byte changes the decode

Address space layout (the SANDBOX; every address is taken mod 256, so nothing can write outside it):
  [0, L)         own tape (self-modifiable)
  [L, 2L)        the NEIGHBOUR window: the partner cell's tape. Writes here are reproduction attempts.
  IN_BASE..      task input bytes (read-only; a write here is the "corrupt validation state" exploit, recorded)
  OUT_BASE..     task output bytes as written by OUT
  the rest       scratch

A run of the VM is a pure function of (memory, entry, budget, inputs): it returns the mutated memory, the outputs
and a trace of what happened (writes, copy events, reads, halts) -- the observatory's raw material."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

SPACE = 256
IN_BASE = 0xE0          # 16 bytes of task input
OUT_BASE = 0xF0         # 16 bytes of task output (also captured in order by OUT)
IO_BASE = IN_BASE

# ---- opcodes ---------------------------------------------------------------------------------------------------
NOP = 0x00
LD_A_n, LD_B_n, LD_C_n, LD_D_n = 0x01, 0x02, 0x03, 0x04
LD_S_n, LD_T_n = 0x07, 0x08
LD_A_pS, LD_pT_A, LD_A_pT, LD_pS_A = 0x10, 0x11, 0x12, 0x13
LDI, LDIR = 0x14, 0x15
COPYALL = 0x16          # native explicit copy primitive: mem[T..T+L) = mem[S..S+L) in one instruction (vm_copy representation only)
ADD_A_B, SUB_A_B, INC_A, DEC_A, INC_S, INC_T, XOR_A_B, AND_A_B, OR_A_B, ADD_A_n, SHL_A, SHR_A, INC_C, DEC_C, CP_A_n, CP_A_B = (
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F)
JP_n, JZ_n, JNZ_n, JR_d, DJNZ_d, JC_n = 0x30, 0x31, 0x32, 0x33, 0x34, 0x35
IN_A, OUT_A = 0x40, 0x41
LD_B_A, LD_A_B, LD_C_A, LD_A_C, LD_S_A, LD_T_A, LD_A_S, LD_A_T, LD_D_A, LD_A_D, SWAP_A_B = (
    0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4D)
HALT = 0xFF

# operand length per opcode (0 for undefined -> NOP)
OPLEN = {NOP: 0, LD_A_n: 1, LD_B_n: 1, LD_C_n: 1, LD_D_n: 1, LD_S_n: 1, LD_T_n: 1,
         LD_A_pS: 0, LD_pT_A: 0, LD_A_pT: 0, LD_pS_A: 0, LDI: 0, LDIR: 0, COPYALL: 0,
         ADD_A_B: 0, SUB_A_B: 0, INC_A: 0, DEC_A: 0, INC_S: 0, INC_T: 0, XOR_A_B: 0, AND_A_B: 0, OR_A_B: 0, ADD_A_n: 1,
         SHL_A: 0, SHR_A: 0, INC_C: 0, DEC_C: 0, CP_A_n: 1, CP_A_B: 0,
         JP_n: 1, JZ_n: 1, JNZ_n: 1, JR_d: 1, DJNZ_d: 1, JC_n: 1, IN_A: 0, OUT_A: 0,
         LD_B_A: 0, LD_A_B: 0, LD_C_A: 0, LD_A_C: 0, LD_S_A: 0, LD_T_A: 0, LD_A_S: 0, LD_A_T: 0, LD_D_A: 0, LD_A_D: 0, SWAP_A_B: 0,
         HALT: 0}
DEFINED = frozenset(OPLEN)
MNEMONIC = {v: k for k, v in globals().items() if isinstance(v, int) and k[:1].isupper() and k not in ("SPACE", "IN_BASE", "OUT_BASE", "IO_BASE")}


@dataclass
class Trace:
    steps: int = 0
    halted: bool = False
    writes: Dict[int, int] = field(default_factory=dict)      # addr -> last value written
    self_writes: int = 0
    neighbour_writes: int = 0
    neighbour_reads: int = 0
    io_writes: int = 0                                         # writes into the input region
    io_corrupt: int = 0                                        # ... that CHANGED a byte there (the exploit signal)
    io_corrupt_step: Optional[int] = None                      # step of the first such change
    reads_in: int = 0
    outputs_before_read: int = 0
    outputs: List[int] = field(default_factory=list)
    first_out_step: Optional[int] = None
    first_in_step: Optional[int] = None
    copy_events: int = 0                                       # LDI/LDIR/COPYALL byte moves into the neighbour window
    opcodes: Dict[int, int] = field(default_factory=dict)      # executed opcode histogram (architecture signature)
    pc_max: int = 0
    # provenance of the LAST write to each window byte (offset -> (source address or None, pc, opcode)); measurement
    # only, added 2026-09-23 (forensics M1/M2/C8): lets the observer tell a self-copy from a sweep, a smear or a capture
    win_prov: Dict[int, Tuple[Optional[int], int, int]] = field(default_factory=dict)


COPY_OPS = frozenset((LDI, LDIR, COPYALL))


def execute(mem: bytearray, L: int, entry: int, budget: int, inputs: List[int], region: Optional[Tuple[int, int]] = None,
            allow_copyall: bool = False, cost_per_step: int = 1, strict_budget: bool = False, prov_L: Optional[int] = None) -> Trace:
    """Run from `entry` for at most `budget` steps. `region` restricts the PC to [lo, hi) (the SEPARATED layout):
    leaving it halts. Undefined opcodes are NOP (1 step). Returns the Trace; `mem` is mutated in place.
    strict_budget (physics v2): COPYALL executes only if its L//8 step cost fits the remaining budget (v1 overran it).
    prov_L: the window whose write provenance is recorded is [prov_L, 2*prov_L) (default L; pair execution passes the
    world's L because it runs with 2L)."""
    A = B = C = D = S = T = 0
    Z = False; CF = False
    pc = entry & 0xFF
    tr = Trace()
    inp = list(inputs); ip = 0
    lo, hi = (region if region else (0, SPACE))
    nb_lo, nb_hi = L, 2 * L
    pw = L if prov_L is None else prov_L
    while tr.steps < budget:
        if not (lo <= pc < hi):
            break
        op = mem[pc]
        tr.steps += 1
        tr.opcodes[op] = tr.opcodes.get(op, 0) + 1
        tr.pc_max = max(tr.pc_max, pc)
        n = OPLEN.get(op, 0)
        arg = mem[(pc + 1) & 0xFF] if n else 0
        npc = (pc + 1 + n) & 0xFF
        cur_pc = pc

        def W(addr: int, v: int, src: Optional[int] = None) -> None:
            addr &= 0xFF
            if pw <= addr < 2 * pw:
                tr.win_prov[addr - pw] = (src, cur_pc, op)
            if IN_BASE <= addr < OUT_BASE and mem[addr] != (v & 0xFF):
                tr.io_corrupt += 1                                 # the input region CHANGED: validation state corrupted
                if tr.io_corrupt_step is None:
                    tr.io_corrupt_step = tr.steps
            mem[addr] = v & 0xFF
            tr.writes[addr] = v & 0xFF
            if addr < L:
                tr.self_writes += 1
            elif nb_lo <= addr < nb_hi:
                tr.neighbour_writes += 1
            elif IN_BASE <= addr < OUT_BASE:
                tr.io_writes += 1

        if op == HALT:
            tr.halted = True; break
        elif op == LD_A_n: A = arg
        elif op == LD_B_n: B = arg
        elif op == LD_C_n: C = arg
        elif op == LD_D_n: D = arg
        elif op == LD_S_n: S = arg
        elif op == LD_T_n: T = arg
        elif op == LD_A_pS:
            A = mem[S]; tr.neighbour_reads += 1 if nb_lo <= S < nb_hi else 0
        elif op == LD_A_pT:
            A = mem[T]; tr.neighbour_reads += 1 if nb_lo <= T < nb_hi else 0
        elif op == LD_pT_A: W(T, A)
        elif op == LD_pS_A: W(S, A)
        elif op == LDI:
            v = mem[S]; W(T, v, S)
            if nb_lo <= T < nb_hi: tr.copy_events += 1
            S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
        elif op == LDIR:
            # bounded: each byte costs a step
            while True:
                v = mem[S]; W(T, v, S)
                if nb_lo <= T < nb_hi: tr.copy_events += 1
                S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
                tr.steps += 1
                if C == 0 or tr.steps >= budget:
                    break
        elif op == COPYALL and allow_copyall:
            if strict_budget and tr.steps + L // 8 > budget:
                break
            for i in range(L):
                W((T + i) & 0xFF, mem[(S + i) & 0xFF], (S + i) & 0xFF)
            if nb_lo <= T < nb_hi: tr.copy_events += L
            tr.steps += L // 8
        elif op == ADD_A_B: A = (A + B) & 0xFF; Z = A == 0
        elif op == SUB_A_B: CF = A < B; A = (A - B) & 0xFF; Z = A == 0
        elif op == INC_A: A = (A + 1) & 0xFF; Z = A == 0
        elif op == DEC_A: A = (A - 1) & 0xFF; Z = A == 0
        elif op == INC_S: S = (S + 1) & 0xFF
        elif op == INC_T: T = (T + 1) & 0xFF
        elif op == XOR_A_B: A ^= B; Z = A == 0
        elif op == AND_A_B: A &= B; Z = A == 0
        elif op == OR_A_B: A |= B; Z = A == 0
        elif op == ADD_A_n: A = (A + arg) & 0xFF; Z = A == 0
        elif op == SHL_A: CF = bool(A & 0x80); A = (A << 1) & 0xFF; Z = A == 0
        elif op == SHR_A: CF = bool(A & 1); A >>= 1; Z = A == 0
        elif op == INC_C: C = (C + 1) & 0xFF; Z = C == 0
        elif op == DEC_C: C = (C - 1) & 0xFF; Z = C == 0
        elif op == CP_A_n: Z = A == arg; CF = A < arg
        elif op == CP_A_B: Z = A == B; CF = A < B
        elif op == JP_n: npc = arg
        elif op == JZ_n:
            if Z: npc = arg
        elif op == JNZ_n:
            if not Z: npc = arg
        elif op == JC_n:
            if CF: npc = arg
        elif op == JR_d:
            d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == DJNZ_d:
            B = (B - 1) & 0xFF
            if B != 0:
                d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == IN_A:
            if tr.first_in_step is None: tr.first_in_step = tr.steps
            tr.reads_in += 1
            A = mem[(IN_BASE + ip) & 0xFF] if ip < 16 else 0     # the input region is real state: tampering with it is visible
            ip += 1
        elif op == OUT_A:
            if tr.first_out_step is None: tr.first_out_step = tr.steps
            if tr.first_in_step is None: tr.outputs_before_read += 1
            if len(tr.outputs) < 16:
                mem[OUT_BASE + len(tr.outputs)] = A
                tr.outputs.append(A)
        elif op in (LD_B_A, LD_A_B, LD_C_A, LD_A_C, LD_S_A, LD_T_A, LD_A_S, LD_A_T, LD_D_A, LD_A_D, SWAP_A_B):
            if op == LD_B_A: B = A
            elif op == LD_A_B: A = B
            elif op == LD_C_A: C = A
            elif op == LD_A_C: A = C
            elif op == LD_S_A: S = A
            elif op == LD_T_A: T = A
            elif op == LD_A_S: A = S
            elif op == LD_A_T: A = T
            elif op == LD_D_A: D = A
            elif op == LD_A_D: A = D
            else: A, B = B, A
        # undefined opcode: NOP
        pc = npc
    return tr


# ---- known witnesses (positive-control specimens) ---------------------------------------------------------------
def replicator(L: int) -> bytes:
    """LD S,0 ; LD T,L ; LD C,L ; LDIR ; HALT  -- copies the whole own tape into the neighbour window (8 bytes)."""
    return bytes([LD_S_n, 0, LD_T_n, L & 0xFF, LD_C_n, L & 0xFF, LDIR, HALT])


def replicator_copyall(L: int) -> bytes:
    return bytes([LD_S_n, 0, LD_T_n, L & 0xFF, COPYALL, HALT])


def witness_const(k: int) -> bytes:
    return bytes([LD_A_n, k & 0xFF, OUT_A, HALT])


def witness_echo() -> bytes:
    return bytes([IN_A, OUT_A, HALT])


def witness_inc() -> bytes:
    return bytes([IN_A, INC_A, OUT_A, HALT])


def witness_cond_one() -> bytes:
    """x if x < 128 else x+1 :  IN A ; CP A,128 ; JC out ; INC A ; out: OUT A ; HALT"""
    return bytes([IN_A, CP_A_n, 0x80, JC_n, 6, INC_A, OUT_A, HALT])


def witness_cond_multi() -> bytes:
    """x if x < 128 else ((x xor 0x55) + 3) : IN A ; CP A,128 ; JC out ; LD B,0x55 ; XOR A,B ; ADD A,3 ; out: OUT A ; HALT"""
    return bytes([IN_A, CP_A_n, 0x80, JC_n, 10, LD_B_n, 0x55, XOR_A_B, ADD_A_n, 3, OUT_A, HALT])


def witness_sum2() -> bytes:
    return bytes([IN_A, LD_B_A, IN_A, ADD_A_B, OUT_A, HALT])


def hybrid(rep: bytes, task: bytes) -> bytes:
    """replicate, then do the task, on one tape: the replicator's HALT is dropped so execution falls into the task."""
    return rep[:-1] + task


def disassemble(tape: bytes, limit: int = 64) -> List[str]:
    out = []; pc = 0
    while pc < min(len(tape), limit):
        op = tape[pc]; n = OPLEN.get(op, 0)
        name = MNEMONIC.get(op, "DB")
        if op not in DEFINED:
            out.append("%02x: DB %02x" % (pc, op)); pc += 1; continue
        if n:
            out.append("%02x: %s %d" % (pc, name, tape[pc + 1] if pc + 1 < len(tape) else 0))
        else:
            out.append("%02x: %s" % (pc, name))
        pc += 1 + n
    return out
