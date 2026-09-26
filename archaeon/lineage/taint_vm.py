"""Label-propagating shadow of the FROZEN z80atlas VM (archaeon/z80atlas/vm.py, unchanged since campaign commit c7610ea19).

Executes the same instruction semantics and additionally carries, for every memory byte and register, a LABEL naming where the
byte's VALUE came from. It is used only at birth events (genetic attribution); every result field must equal vm.execute exactly
(differential-tested), so it can never change physics -- if it ever disagreed, the caller refuses the attribution (loud error).

Labels (atoms):  ('E', p)  byte p of the executor's own tape as it was at the start of execution
                 ('N', q)  byte q of the neighbour window as it was at the start of execution (the occupant's genome, or zeros)
                 ('I',)    an input byte (environment)          ('K',)  a constant (LD A,LEN, zero-initialised registers)
                 ('Z',)    untouched scratch memory (zeros)
A value produced by arithmetic/logic from other values is ('X', frozenset(source atoms)) -- NEW material with conservative
contributors. Plain moves (LD, COPY, SWAP, LD r,imm reading a code byte) carry the source label unchanged.
Also returned: how many opcode fetches executed bytes labelled E (self material), N (neighbour material) or other.
"""
from __future__ import annotations

from archaeon.z80atlas.vm import NBR, OUT_CAP

K = ("K",); Z = ("Z",); I = ("I",)


def _x(*labels):
    s = set()
    for l in labels:
        if l[0] == "X": s |= l[1]
        elif l[0] in ("E", "N"): s.add(l)
    return ("X", frozenset(s))


def execute_taint(tape, nbr, inputs, step_cap: int, copy_prim: bool, energy: float = -1.0, pc0: int = 0, allow_nbr_write: bool = True):
    G = len(tape)
    mem = bytearray(256); mem[0:G] = tape
    lab = [Z] * 256
    for p in range(G): lab[p] = ("E", p)
    if nbr is not None:
        mem[NBR:NBR + len(nbr)] = nbr
        for q in range(len(nbr)): lab[NBR + q] = ("N", q)
    regs = [0, 0, 0, 0]; rl = [K, K, K, K]; pc = pc0 & 255; z = 0; cf = 0
    outputs = []; ip = 0; ninp = len(inputs); steps = 0
    writes_own = 0; writes_nbr = 0; reads_nbr = 0; illegal = 0; self_overwrite = 0; exec_foreign = 0
    nbr_mask = bytearray(128); executed = bytearray(256); hist = [0] * 32
    sealed = None; sealed_lab = None; halted = False; starved = False
    cost = 1.0 if energy >= 0 else 0.0
    ex_self = ex_nbr = ex_other = 0
    while steps < step_cap:
        if cost and energy <= 0:
            starved = True; break
        b = mem[pc]; op = b & 31; r = (b >> 5) & 3; hi = b >> 7
        lb = lab[pc]
        if lb[0] == "E": ex_self += 1
        elif lb[0] == "N": ex_nbr += 1
        else: ex_other += 1
        if pc >= G:
            exec_foreign += 1
        executed[pc] = 1
        pc = (pc + 1) & 255; steps += 1; hist[op] += 1; energy -= cost
        if op == 0 or op == 30:
            continue
        if op == 1:
            regs[r] = mem[pc]; rl[r] = lab[pc]; pc = (pc + 1) & 255
        elif op == 2:
            if hi: regs[r] = regs[0]; rl[r] = rl[0]
            else: regs[0] = regs[r]; rl[0] = rl[r]
        elif op == 3:
            t = regs[0] + regs[r]; cf = 1 if t > 255 else 0; regs[0] = t & 255; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0], rl[r])
        elif op == 4:
            t = regs[0] - regs[r]; cf = 1 if t < 0 else 0; regs[0] = t & 255; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0], rl[r])
        elif op == 5:
            regs[r] = (regs[r] + 1) & 255; z = 1 if regs[r] == 0 else 0; rl[r] = _x(rl[r])
        elif op == 6:
            regs[r] = (regs[r] - 1) & 255; z = 1 if regs[r] == 0 else 0; rl[r] = _x(rl[r])
        elif op == 7:
            regs[0] ^= regs[r]; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0], rl[r])
        elif op == 8:
            regs[0] &= regs[r]; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0], rl[r])
        elif op == 9:
            regs[0] |= regs[r]; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0], rl[r])
        elif op == 10:
            cf = regs[0] >> 7; regs[0] = (regs[0] << 1) & 255; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0])
        elif op == 11:
            cf = regs[0] & 1; regs[0] >>= 1; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0])
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
                regs[1] = (regs[1] - 1) & 255; take = regs[1] != 0; rl[1] = _x(rl[1])
            if take:
                pc = (pc + (imm - 256 if imm > 127 else imm)) & 255
        elif op == 18 or op == 19:
            if op == 18: addr = regs[r]
            else: addr = mem[pc]; pc = (pc + 1) & 255
            if hi:
                if addr < G:
                    if executed[addr]: self_overwrite += 1
                    mem[addr] = regs[0]; lab[addr] = rl[0]; writes_own += 1
                elif NBR <= addr < NBR + G and allow_nbr_write:
                    mem[addr] = regs[0]; lab[addr] = rl[0]; nbr_mask[addr - NBR] = 1; writes_nbr += 1
                else:
                    illegal += 1
            else:
                if NBR <= addr < NBR + G: reads_nbr += 1
                regs[0] = mem[addr]; rl[0] = lab[addr]
        elif op == 20:
            if copy_prim:
                src = regs[1]; dst = regs[2]
                if NBR <= src < NBR + G: reads_nbr += 1
                v = mem[src]; vl = lab[src]
                if dst < G:
                    if executed[dst]: self_overwrite += 1
                    mem[dst] = v; lab[dst] = vl; writes_own += 1
                elif NBR <= dst < NBR + G and allow_nbr_write:
                    mem[dst] = v; lab[dst] = vl; nbr_mask[dst - NBR] = 1; writes_nbr += 1
                else:
                    illegal += 1
                regs[1] = (src + 1) & 255; regs[2] = (dst + 1) & 255; rl[1] = _x(rl[1]); rl[2] = _x(rl[2])
        elif op == 21:
            if ip < ninp: regs[r] = inputs[ip]; ip += 1; rl[r] = I
            else: regs[r] = 0; rl[r] = K
        elif op == 22:
            if len(outputs) < OUT_CAP: outputs.append(regs[r])
        elif op == 23 or op == 31:
            halted = True; break
        elif op == 24:
            regs[0], regs[r] = regs[r], regs[0]; rl[0], rl[r] = rl[r], rl[0]
        elif op == 25:
            regs[0] = (-regs[0]) & 255; z = 1 if regs[0] == 0 else 0; rl[0] = _x(rl[0])
        elif op == 26:
            pc = regs[r]
        elif op == 28:
            regs[0] = G & 255; rl[0] = K
        elif op == 29:
            if sealed is None: sealed = bytes(mem[NBR:NBR + G]); sealed_lab = list(lab[NBR:NBR + G])
    res = {"outputs": outputs, "steps": steps, "halted": halted, "starved": starved, "writes_own": writes_own, "writes_nbr": writes_nbr,
           "reads_nbr": reads_nbr, "illegal": illegal, "self_overwrite": self_overwrite, "exec_foreign": exec_foreign,
           "nbr_window": sealed if sealed is not None else bytes(mem[NBR:NBR + G]), "nbr_mask": bytes(nbr_mask[:G]), "sealed": sealed is not None,
           "own_after": bytes(mem[0:G]), "executed": bytes(executed[:G]), "hist": hist, "inputs_read": ip, "energy": energy}
    wl = sealed_lab if sealed is not None else list(lab[NBR:NBR + G])
    return res, wl, {"self": ex_self, "nbr": ex_nbr, "other": ex_other}
