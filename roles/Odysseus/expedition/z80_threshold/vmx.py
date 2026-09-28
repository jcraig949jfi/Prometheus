"""vmx -- BEE's vm.execute (prometheus/z80atlas/vm.py @7720539d4) with ONE added feature: opcodes listed in
`disabled` decode as NOP (ISA-level removal, as ldir="off" does for LDIR). Generated mechanically from vm.py source
by text copy; gate E0 in pilot.py checks equality with vm.execute when disabled is empty. Odysseus z80_threshold
pilot; EXPLORATORY."""
from __future__ import annotations
import os, sys
from typing import List, Optional, Tuple
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4)))
from prometheus.z80atlas.vm import *  # noqa: F401,F403  (opcodes, Trace, OPLEN, DEFINED, SPACE, IN_BASE, OUT_BASE)
from prometheus.z80atlas.vm import Trace, OPLEN, DEFINED  # noqa: E402


def execute(mem: bytearray, L: int, entry: int, budget: int, inputs: List[int], region: Optional[Tuple[int, int]] = None,
            allow_copyall: bool = False, cost_per_step: int = 1, strict_budget: bool = False, prov_L: Optional[int] = None,
            ldir: str = "on", undefined: str = "NOP", trace_pcs: bool = False, disabled: frozenset = frozenset()) -> Trace:
    """Run from `entry` for at most `budget` steps. `region` restricts the PC to [lo, hi) (the SEPARATED layout):
    leaving it halts. Undefined opcodes are NOP (1 step). Returns the Trace; `mem` is mutated in place.
    strict_budget (physics v2): COPYALL executes only if its L//8 step cost fits the remaining budget (v1 overran it).
    prov_L: the window whose write provenance is recorded is [prov_L, 2*prov_L) (default L; pair execution passes the
    world's L because it runs with 2L).
    Chemistry ablations (Phase 8 of the 2026-09-23 forensics; defaults = the historical chemistry):
      ldir       "on" | "off" (LDIR executes as an undefined byte) | "cost4" (each LDIR byte costs 4 steps)
      undefined  "NOP" | "HALT" (an undefined opcode stops execution: no neutral NOP slides)"""
    A = B = C = D = S = T = 0
    Z = False; CF = False
    pc = entry & 0xFF
    tr = Trace()
    if trace_pcs:
        tr.pcs = set()
    inp = list(inputs); ip = 0
    lo, hi = (region if region else (0, SPACE))
    nb_lo, nb_hi = L, 2 * L
    pw = L if prov_L is None else prov_L
    while tr.steps < budget:
        if not (lo <= pc < hi):
            break
        op = mem[pc]
        if op == LDIR and ldir == "off":
            op = NOP                                               # ablation: the byte is inert (its histogram entry reads NOP)
        if op in disabled:
            op = NOP                                               # vmx: ISA-level removal of further opcodes
        if undefined == "HALT" and op not in DEFINED:
            tr.steps += 1; tr.halted = True; break                 # ablation: no neutral undefined bytes
        tr.steps += 1
        tr.opcodes[op] = tr.opcodes.get(op, 0) + 1
        tr.pc_max = max(tr.pc_max, pc)
        if tr.pcs is not None:
            tr.pcs.add(pc)
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
                tr.steps += 4 if ldir == "cost4" else 1
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


