"""Z80-like byte VM for the Z80 x Atlas campaign (frozen at launch; see CAMPAIGN_CONTRACT.md).

Properties preserved from the donor: byte-addressable executable representation; jumps / control flow; register + flag
state; memory write and copy capability; no multiplication; mutation alters algorithm and architecture alike; any byte
decodes to SOME instruction (op = byte & 31, r = (byte >> 5) & 3, hi = byte >> 7), so a mutated tape is reinterpreted.

Address space (256 bytes):  [0, G)      the organism's own tape (executable, self-modifiable)
                            [128, 128+G) the neighbour window (the only place descendants can be caused)
                            everything else reads 0 and refuses writes (sandbox; counted as `illegal`)
Opcodes:
  0 NOP | 1 LD r,imm | 2 LD A,r (hi: LD r,A) | 3 ADD A,r | 4 SUB A,r | 5 INC r | 6 DEC r | 7 XOR A,r | 8 AND A,r | 9 OR A,r
 10 SHL A | 11 SHR A | 12 CMP A,r | 13 JP imm | 14 JR imm | 15 JZ imm | 16 JNZ imm | 17 JC imm
 18 LD A,(r) (hi: LD (r),A) | 19 LD A,(imm) (hi: LD (imm),A) | 20 COPY: mem[C]=mem[B]; B++; C++  (NOP unless copy_prim)
 21 IN r | 22 OUT r | 23 HALT | 24 SWAP A,r | 25 NEG A | 26 JP r | 27 DJNZ imm | 28 LD A,LEN | 29 SEAL | 30 NOP | 31 HALT
Registers r: 0=A 1=B 2=C 3=D. Flags Z, C. Relative jumps are signed bytes from the address after the operand.
"""
from __future__ import annotations

NBR = 128
OUT_CAP = 16


def I(op: int, r: int = 0, hi: int = 0) -> int:
    return (op & 31) | ((r & 3) << 5) | ((hi & 1) << 7)


def execute(tape, nbr, inputs, step_cap: int, copy_prim: bool, energy: float = -1.0, pc0: int = 0, allow_nbr_write: bool = True) -> dict:
    """Run one organism once. Returns a dict of everything the observatory needs; never raises on organism content."""
    G = len(tape)
    mem = bytearray(256); mem[0:G] = tape
    if nbr is not None:
        mem[NBR:NBR + len(nbr)] = nbr
    regs = [0, 0, 0, 0]; pc = pc0 & 255; z = 0; cf = 0
    outputs = []; ip = 0; ninp = len(inputs); steps = 0
    writes_own = 0; writes_nbr = 0; reads_nbr = 0; illegal = 0; self_overwrite = 0; exec_foreign = 0
    nbr_mask = bytearray(128)              # which neighbour bytes were written
    executed = bytearray(256)              # which addresses were fetched as opcodes
    hist = [0] * 32
    sealed = None; halted = False; starved = False
    cost = 1.0 if energy >= 0 else 0.0
    while steps < step_cap:
        if cost and energy <= 0:
            starved = True; break
        b = mem[pc]; op = b & 31; r = (b >> 5) & 3; hi = b >> 7
        if pc >= G:
            exec_foreign += 1
        executed[pc] = 1
        pc = (pc + 1) & 255; steps += 1; hist[op] += 1; energy -= cost
        if op == 0 or op == 30:
            continue
        if op == 1:
            regs[r] = mem[pc]; pc = (pc + 1) & 255
        elif op == 2:
            if hi: regs[r] = regs[0]
            else: regs[0] = regs[r]
        elif op == 3:
            t = regs[0] + regs[r]; cf = 1 if t > 255 else 0; regs[0] = t & 255; z = 1 if regs[0] == 0 else 0
        elif op == 4:
            t = regs[0] - regs[r]; cf = 1 if t < 0 else 0; regs[0] = t & 255; z = 1 if regs[0] == 0 else 0
        elif op == 5:
            regs[r] = (regs[r] + 1) & 255; z = 1 if regs[r] == 0 else 0
        elif op == 6:
            regs[r] = (regs[r] - 1) & 255; z = 1 if regs[r] == 0 else 0
        elif op == 7:
            regs[0] ^= regs[r]; z = 1 if regs[0] == 0 else 0
        elif op == 8:
            regs[0] &= regs[r]; z = 1 if regs[0] == 0 else 0
        elif op == 9:
            regs[0] |= regs[r]; z = 1 if regs[0] == 0 else 0
        elif op == 10:
            cf = regs[0] >> 7; regs[0] = (regs[0] << 1) & 255; z = 1 if regs[0] == 0 else 0
        elif op == 11:
            cf = regs[0] & 1; regs[0] >>= 1; z = 1 if regs[0] == 0 else 0
        elif op == 12:
            t = regs[0] - regs[r]; cf = 1 if t < 0 else 0; z = 1 if t == 0 else 0
        elif op == 13:
            pc = mem[pc]
        elif op == 14 or op == 15 or op == 16 or op == 17 or op == 27:
            imm = mem[pc]; pc = (pc + 1) & 255
            take = True
            if op == 15: take = z == 1
            elif op == 16: take = z == 0
            elif op == 17: take = cf == 1
            elif op == 27:
                regs[1] = (regs[1] - 1) & 255; take = regs[1] != 0
            if take:
                pc = (pc + (imm - 256 if imm > 127 else imm)) & 255
        elif op == 18 or op == 19:
            if op == 18: addr = regs[r]
            else: addr = mem[pc]; pc = (pc + 1) & 255
            if hi:
                if addr < G:
                    if executed[addr]: self_overwrite += 1
                    mem[addr] = regs[0]; writes_own += 1
                elif NBR <= addr < NBR + G and allow_nbr_write:
                    mem[addr] = regs[0]; nbr_mask[addr - NBR] = 1; writes_nbr += 1
                else:
                    illegal += 1
            else:
                if NBR <= addr < NBR + G: reads_nbr += 1
                regs[0] = mem[addr]
        elif op == 20:
            if copy_prim:
                src = regs[1]; dst = regs[2]
                if NBR <= src < NBR + G: reads_nbr += 1
                v = mem[src]
                if dst < G:
                    if executed[dst]: self_overwrite += 1
                    mem[dst] = v; writes_own += 1
                elif NBR <= dst < NBR + G and allow_nbr_write:
                    mem[dst] = v; nbr_mask[dst - NBR] = 1; writes_nbr += 1
                else:
                    illegal += 1
                regs[1] = (src + 1) & 255; regs[2] = (dst + 1) & 255
        elif op == 21:
            if ip < ninp: regs[r] = inputs[ip]; ip += 1
            else: regs[r] = 0
        elif op == 22:
            if len(outputs) < OUT_CAP: outputs.append(regs[r])
        elif op == 23 or op == 31:
            halted = True; break
        elif op == 24:
            regs[0], regs[r] = regs[r], regs[0]
        elif op == 25:
            regs[0] = (-regs[0]) & 255; z = 1 if regs[0] == 0 else 0
        elif op == 26:
            pc = regs[r]
        elif op == 28:
            regs[0] = G & 255
        elif op == 29:
            if sealed is None: sealed = bytes(mem[NBR:NBR + G])
    return {"outputs": outputs, "steps": steps, "halted": halted, "starved": starved, "writes_own": writes_own, "writes_nbr": writes_nbr,
            "reads_nbr": reads_nbr, "illegal": illegal, "self_overwrite": self_overwrite, "exec_foreign": exec_foreign,
            "nbr_window": sealed if sealed is not None else bytes(mem[NBR:NBR + G]), "nbr_mask": bytes(nbr_mask[:G]), "sealed": sealed is not None,
            "own_after": bytes(mem[0:G]), "executed": bytes(executed[:G]), "hist": hist, "inputs_read": ip, "energy": energy}


def arch_signature(hist) -> int:
    """Coarse architecture signature: which opcode classes are used (control / memory / io / copy / arith / halt)."""
    ctl = sum(hist[13:18]) + hist[26] + hist[27]; memw = hist[18] + hist[19]; io = hist[21] + hist[22]; cp = hist[20]; ar = sum(hist[3:13]) + hist[24] + hist[25]
    return (1 if ctl else 0) | (2 if memw else 0) | (4 if io else 0) | (8 if cp else 0) | (16 if ar else 0) | (32 if hist[29] else 0)
