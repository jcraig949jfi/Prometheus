"""Z8 shadow tracer for the NPE ancestry replay (Archaeon commission #812/#818/#823; ANCESTRY_PREREG v4 + v5 delta).

OBSERVATION ONLY. The frozen VM (roles/Nestor/campaigns/z80atlas-verify-2026-09-22/z8.py) is never edited or patched. This
module re-executes an interaction from a captured pre-state with an interpreter that computes EXACTLY what z8.run computes
(checked on every interaction against the world's own result, and by selftest_shadow.py on random programs against
z8.run), and additionally carries, for every byte and register, a DATA LABEL and an ADDRESS-DEPENDENCE set.

Labels (v4 s1.2, readings N1-N7 posted to Archaeon as #832, CHOICE numbering of v5 Amendment C2 where it applies):
  ("E", ent, i, orig)  ENTITY MOVE: byte i of entity ent ('a' = side 0, 'b' = side 1) at interaction start;
                       orig = the persisted origin of that byte (reported, never gating)
  ("K", kind)          CONSTANT (FOREIGN-STRUCTURAL): 'reset' zero registers/flags, 'pad', 'in_exhausted', 'idiom', 'clear'
  ("X", op)            CONTEXT (FOREIGN-STRUCTURAL): 'GETPC', 'SENSE_side', 'SELF', 'ALLOC'
  ("P", ent, reg)      persisted register / flag of entity ent at interaction start (its own source group, v5 R1)
  ("C", bases)         COMPUTED over a frozenset of base labels (CONSTANT bases dropped, CHOICE 3)
  ("F", inner)         COMPUTED_FROM: register-only, no-operand bijective ops (INC r, DEC r)
  ("M", draw, old)     MUTATION at the harness write-back: draw = (interaction id, side, rng call index), old = old label
Base labels (members of dependence sets): ("E", ent, i), ("X", op), ("P", ent, reg), ("M", draw).
Every value carries an addr set: pointer dependence is transitive through memory and computation (CHOICE 5).
deps(cell) = base(data label) | addr set.

Dependence sets per store (the per-locus sets are those of the LAST store to the locus):
  ctrl  whole-interaction PC label: deps of every conditional's inputs EVALUATED so far (JR/JP cc flag reads, the LDIR
        count, ...), accumulated from interaction start (CHOICE N-a, reported to Archaeon; non-gating under v5 R1)
  addr  the addr set of the stored value (every load that contributed) plus the store pointer's deps
  exec  deps of every fetched opcode/operand byte from interaction start up to the store (and, separately, over the whole
        interaction)
Performer = the data label of the STORE instruction's opcode byte (for LDIR/LDDR the second byte B0/B8).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

B, C, D, E, H, L, M, A = 0, 1, 2, 3, 4, 5, 6, 7
OP_ALLOC, OP_BIRTH, OP_SELF, OP_GETPC, OP_SENSE, OP_SPLIT = 0x30, 0x31, 0x32, 0x33, 0x34, 0x35
OP_LDIR, OP_LDDR = 0xB0, 0xB8
EMPTY = frozenset()
K_RESET = ("K", "reset")


def base(dl) -> frozenset:
    k = dl[0]
    if k == "E":
        return frozenset({("E", dl[1], dl[2])})
    if k == "K":
        return EMPTY
    if k == "X":
        return frozenset((dl,))
    if k == "P":
        return frozenset((dl,))
    if k == "C":
        return dl[1]
    if k == "F":
        return base(dl[1])
    if k == "M":
        return frozenset({("M", dl[1])})
    raise ValueError(dl)


def deps(cell) -> frozenset:
    return base(cell[0]) | cell[1]


def computed(*cells):
    """COMPUTED over the operands' base labels; addr sets unioned."""
    bs, ad = set(), set()
    for c in cells:
        bs |= base(c[0])
        ad |= c[1]
    return (("C", frozenset(bs)), frozenset(ad))


class Store:
    __slots__ = ("addr", "val", "cell", "side", "step", "pc", "performer", "ctrl", "exec_", "tix", "six", "lix")

    def __init__(self, addr, val, cell, side, step, pc, performer, ctrl, exec_, tix=-1, six=-1, lix=-1):
        self.addr, self.val, self.cell, self.side, self.step = addr, val, cell, side, step
        self.pc, self.performer, self.ctrl, self.exec_ = pc, performer, ctrl, exec_
        self.tix, self.six, self.lix = tix, six, lix          # trace / store / load positions (record_trace only)


class Shadow:
    """One pair interaction on a shared tape, value-exact with z8.run under ARENA policy and no callbacks
    (the T-003 pair context: Ctx(tape, start, n, policy=ARENA, sense=who), no on_alloc/on_birth)."""

    def __init__(self, tape: bytes, tape_labels: List[tuple], regs: Dict[int, Optional[list]],
                 reg_labels: Dict[int, list], flags: Dict[int, Tuple[int, int]], flag_labels: Dict[int, list],
                 budget: int, ops_mask: int, record_trace: bool = False):
        self.mem = bytearray(tape)
        self.lab = list(tape_labels)                       # per address: (data label, addr set)
        self.size = len(self.mem)
        self.regs0, self.flags0 = regs, flags
        self.rl0, self.fl0 = reg_labels, flag_labels
        self.budget, self.ops_mask = budget, ops_mask
        self.ctrl = EMPTY
        self.exec_all = EMPTY
        self.stores: List[Store] = []
        self.record_trace = record_trace
        self.trace: List[tuple] = []                       # (pc, opcode[, ED second byte]) per fetched instruction
        self.store_addrs: List[int] = []
        self.load_addrs: List[int] = []
        self.out = {}
        self.budget_ended = {}

    # ---------------------------------------------------------------- one slice
    def run_slice(self, side: int, start: int):
        mem, lab, size = self.mem, self.lab, self.size
        mask = size - 1
        pow2 = (size & mask) == 0
        r0 = self.regs0[side]
        r = [0] * 8 if r0 is None else list(r0)
        rl = list(self.rl0[side])
        fz, fc = self.flags0[side]
        fzl, fcl = self.fl0[side]
        budget, ops_enabled = self.budget, self.ops_mask
        steps = 0
        pc = start
        halted = False
        outputs = []
        rec = self.record_trace

        def ad(x):
            return x & mask if pow2 else x % size

        def ptr_deps(hi, lo):
            return deps(rl[hi]) | deps(rl[lo])

        def fetch(a):
            a = ad(a)
            self.exec_all = self.exec_all | deps(lab[a])
            return mem[a], lab[a]

        def load(a, pdeps):
            a = ad(a)
            if rec:
                self.load_addrs.append(a)
            cell = lab[a]
            return mem[a], (cell[0], cell[1] | pdeps)

        def store(a, val, cell, pdeps, op_cell, at_pc):
            a = ad(a)
            if rec:
                self.store_addrs.append(a)
            new = (cell[0], cell[1] | pdeps)
            mem[a] = val & 0xFF
            lab[a] = new
            self.stores.append(Store(a, val & 0xFF, new, side, steps, at_pc, op_cell[0], self.ctrl, self.exec_all,
                                     len(self.trace), len(self.store_addrs) - 1, len(self.load_addrs)))

        while steps < budget:
            steps += 1
            pc = ad(pc)
            op, opl = fetch(pc)
            if rec:
                self.trace.append((pc, op))
            at_pc = pc

            if 0x40 <= op < 0x80:
                if op == 0x76:
                    halted = True
                    break
                dst, src = (op >> 3) & 7, op & 7
                if src == M:
                    hl = (r[H] << 8) | r[L]
                    v, cell = load(hl, ptr_deps(H, L))
                else:
                    v, cell = r[src], rl[src]
                if dst == M:
                    store((r[H] << 8) | r[L], v, cell, ptr_deps(H, L), opl, at_pc)
                else:
                    r[dst], rl[dst] = v, cell
                pc += 1
                continue

            if 0x80 <= op < 0xC0:
                src = op & 7
                if src == M:
                    v, cell = load((r[H] << 8) | r[L], ptr_deps(H, L))
                else:
                    v, cell = r[src], rl[src]
                kind = (op >> 3) & 7
                a = r[A]
                if kind == 0:
                    t = a + v
                elif kind == 1:
                    t = a + v + fc
                elif kind == 2:
                    t = a - v
                elif kind == 3:
                    t = a - v - fc
                elif kind == 4:
                    t = a & v
                elif kind == 5:
                    t = a ^ v
                elif kind == 6:
                    t = a | v
                else:
                    t = a - v
                idiom = src == A and kind in (2, 5, 7)       # SUB A,A / XOR A,A / CP A,A: result-independent
                if idiom:
                    res = (("K", "idiom"), EMPTY)
                elif kind in (1, 3):
                    res = computed(rl[A], cell, fcl)
                else:
                    res = computed(rl[A], cell)
                fc = 1 if (t > 255 or t < 0) else 0
                t &= 0xFF
                fz = 1 if t == 0 else 0
                fzl = fcl = res
                if kind != 7:
                    r[A], rl[A] = t, res
                pc += 1
                continue

            lo = op & 7
            if lo == 4 and op < 0x40:
                d = (op >> 3) & 7
                if d == M:
                    addr = (r[H] << 8) | r[L]
                    pd = ptr_deps(H, L)
                    v0, cell = load(addr, pd)
                    v = (v0 + 1) & 0xFF
                    res = computed(cell)
                    store(addr, v, res, pd, opl, at_pc)
                else:
                    v = r[d] = (r[d] + 1) & 0xFF
                    res = rl[d] = (("F", rl[d][0]), rl[d][1])
                fz = 1 if v == 0 else 0
                fzl = res
                pc += 1
                continue
            if lo == 5 and op < 0x40:
                d = (op >> 3) & 7
                if d == M:
                    addr = (r[H] << 8) | r[L]
                    pd = ptr_deps(H, L)
                    v0, cell = load(addr, pd)
                    v = (v0 - 1) & 0xFF
                    res = computed(cell)
                    store(addr, v, res, pd, opl, at_pc)
                else:
                    v = r[d] = (r[d] - 1) & 0xFF
                    res = rl[d] = (("F", rl[d][0]), rl[d][1])
                fz = 1 if v == 0 else 0
                fzl = res
                pc += 1
                continue
            if lo == 6 and op < 0x40:
                d = (op >> 3) & 7
                n, ncell = fetch(pc + 1)
                if d == M:
                    store((r[H] << 8) | r[L], n, ncell, ptr_deps(H, L), opl, at_pc)
                else:
                    r[d], rl[d] = n, ncell
                pc += 2
                continue

            if op == 0x01 or op == 0x11 or op == 0x21 or op == 0x31:
                n1, c1 = fetch(pc + 1)
                n2, c2 = fetch(pc + 2)
                if op != 0x31:
                    hi, lo_ = {0x01: (B, C), 0x11: (D, E), 0x21: (H, L)}[op]
                    r[hi], r[lo_] = n2, n1
                    rl[hi], rl[lo_] = c2, c1
                pc += 3
                continue
            if op == 0x02 or op == 0x12:
                hi, lo_ = (B, C) if op == 0x02 else (D, E)
                store((r[hi] << 8) | r[lo_], r[A], rl[A], ptr_deps(hi, lo_), opl, at_pc)
                pc += 1
                continue
            if op == 0x0A or op == 0x1A:
                hi, lo_ = (B, C) if op == 0x0A else (D, E)
                r[A], rl[A] = load((r[hi] << 8) | r[lo_], ptr_deps(hi, lo_))
                pc += 1
                continue
            if op in (0x03, 0x13, 0x23, 0x0B, 0x1B, 0x2B):
                hi, lo_ = (B, C) if op in (0x03, 0x0B) else ((D, E) if op in (0x13, 0x1B) else (H, L))
                v = ((r[hi] << 8) | r[lo_]) + (1 if op in (0x03, 0x13, 0x23) else -1)
                v &= 0xFFFF
                r[hi], r[lo_] = (v >> 8) & 0xFF, v & 0xFF
                # the pair as one register-only bijective op: low byte COMPUTED_FROM itself; high byte COMPUTED over
                # both (the carry/borrow) -- CHOICE N-b, reported
                chi, clo = rl[hi], rl[lo_]
                rl[lo_] = (("F", clo[0]), clo[1])
                rl[hi] = computed(chi, clo)
                pc += 1
                continue

            if op == 0x18 or op == 0x20 or op == 0x28 or op == 0x30 or op == 0x38:
                e, _c = fetch(pc + 1)
                if e > 127:
                    e -= 256
                if op == 0x20 or op == 0x28:
                    self.ctrl = self.ctrl | deps(fzl)
                elif op == 0x30 or op == 0x38:
                    self.ctrl = self.ctrl | deps(fcl)
                take = (op == 0x18 or (op == 0x20 and not fz) or (op == 0x28 and fz)
                        or (op == 0x30 and not fc) or (op == 0x38 and fc))
                pc = pc + 2 + e if take else pc + 2
                continue

            if op == 0xC3 or op == 0xC2 or op == 0xCA or op == 0xD2 or op == 0xDA:
                n1, _c1 = fetch(pc + 1)
                n2, _c2 = fetch(pc + 2)
                n = n1 | (n2 << 8)
                if op == 0xC2 or op == 0xCA:
                    self.ctrl = self.ctrl | deps(fzl)
                elif op == 0xD2 or op == 0xDA:
                    self.ctrl = self.ctrl | deps(fcl)
                take = (op == 0xC3 or (op == 0xC2 and not fz) or (op == 0xCA and fz)
                        or (op == 0xD2 and not fc) or (op == 0xDA and fc))
                pc = n if take else pc + 3
                continue

            if op in (0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE):
                v, vc = fetch(pc + 1)
                a = r[A]
                if op == 0xC6:
                    t = a + v
                elif op == 0xD6:
                    t = a - v
                elif op == 0xE6:
                    t = a & v
                elif op == 0xEE:
                    t = a ^ v
                elif op == 0xF6:
                    t = a | v
                else:
                    t = a - v
                res = computed(rl[A], vc)
                fc = 1 if (t > 255 or t < 0) else 0
                t &= 0xFF
                fz = 1 if t == 0 else 0
                fzl = fcl = res
                if op != 0xFE:
                    r[A], rl[A] = t, res
                pc += 2
                continue

            if op == 0xDB:                                   # IN: the pair context has no task inputs (N3)
                r[A], rl[A] = 0, (("K", "in_exhausted"), EMPTY)
                pc += 2
                continue
            if op == 0xD3:                                   # OUT: out_gate_reads == 0 in the pair context
                if len(outputs) < 64:
                    outputs.append(r[A])
                pc += 2
                continue

            if op == 0xED:
                op2, op2l = fetch(pc + 1)
                if rec:
                    self.trace[-1] = (at_pc, op, op2)
                pc += 2
                if op2 == OP_LDIR or op2 == OP_LDDR:
                    if not (ops_enabled & 0x20):
                        continue
                    step = 1 if op2 == OP_LDIR else -1
                    n = (r[B] << 8) | r[C]
                    self.ctrl = self.ctrl | deps(rl[B]) | deps(rl[C])          # the count / C == 0 exit
                    if n == 0:
                        n = 0x10000
                    src = (r[H] << 8) | r[L]
                    dst = (r[D] << 8) | r[E]
                    sdeps, ddeps = ptr_deps(H, L), ptr_deps(D, E)
                    room = budget - steps
                    if n > room:
                        n = room
                    for _ in range(n):
                        v, cell = load(src, sdeps)
                        store(dst, v, cell, ddeps, op2l, at_pc)
                        src += step
                        dst += step
                    steps += n
                    src &= 0xFFFF
                    dst &= 0xFFFF
                    r[H], r[L] = (src >> 8) & 0xFF, src & 0xFF
                    r[D], r[E] = (dst >> 8) & 0xFF, dst & 0xFF
                    r[B] = r[C] = 0
                    for x, dd in ((H, sdeps), (L, sdeps), (D, ddeps), (E, ddeps)):
                        rl[x] = (("C", frozenset()), dd)
                    rl[B] = rl[C] = (("K", "ldir_zero"), EMPTY)
                    fz = 1
                    fzl = (("K", "ldir_z"), EMPTY)
                    continue
                if op2 == OP_ALLOC:                          # no callback in the pair context: always fails
                    if not (ops_enabled & 0x01):
                        continue
                    fz, fzl = 0, (("X", "ALLOC"), EMPTY)
                    continue
                if op2 == OP_BIRTH or op2 == OP_SPLIT:
                    if op2 == OP_BIRTH and not (ops_enabled & 0x01):
                        continue
                    if op2 == OP_SPLIT and not (ops_enabled & 0x10):
                        continue
                    fz, fzl = 0, (("X", "BIRTH"), EMPTY)
                    continue
                if op2 == OP_SELF:
                    if not (ops_enabled & 0x02):
                        continue
                    base_ = start
                    r[H], r[L] = (base_ >> 8) & 0xFF, base_ & 0xFF
                    n_ = self.size // 2
                    r[B], r[C] = (n_ >> 8) & 0xFF, n_ & 0xFF
                    for x in (H, L, B, C):
                        rl[x] = (("X", "SELF"), EMPTY)
                    continue
                if op2 == OP_GETPC:
                    if not (ops_enabled & 0x04):
                        continue
                    p = (pc - 2) & 0xFFFF
                    r[H], r[L] = (p >> 8) & 0xFF, p & 0xFF
                    rl[H] = rl[L] = (("X", "GETPC"), EMPTY)
                    continue
                if op2 == OP_SENSE:
                    if not (ops_enabled & 0x08):
                        continue
                    r[A], rl[A] = side & 0xFF, (("X", "SENSE_side"), EMPTY)
                    continue
                continue

            pc += 1                                          # undefined byte: NOP

        if not halted:
            pc = ad(pc)
        self.budget_ended[side] = not halted
        self.out[side] = outputs
        return {"regs": r, "reg_labels": rl, "fz": fz, "fc": fc, "flag_labels": (fzl, fcl), "pc": pc,
                "halted": halted, "steps": steps}

    def run_pair(self, n: int):
        """Side 0 (a) from 0, then side 1 (b) from n: the world's order."""
        ra = self.run_slice(0, 0)
        rb = self.run_slice(1, n)
        return ra, rb


# ---------------------------------------------------------------- initial labels
def initial_tape_labels(ga: bytes, gb: bytes, n: int, size: int, orig_a=None, orig_b=None) -> List[tuple]:
    lab = [(("K", "pad"), EMPTY)] * size
    for side, g, org in ((0, ga, orig_a), (1, gb, orig_b)):
        ent = "a" if side == 0 else "b"
        off = 0 if side == 0 else n
        for i in range(len(g)):
            o = org[i] if org is not None and i < len(org) else None
            lab[off + i] = (("E", ent, i, o), EMPTY)
    return lab


def initial_reg_labels(side: int, regs) -> Tuple[list, tuple]:
    ent = "a" if side == 0 else "b"
    if regs is None:                                     # fresh organism: registers and flags are the zero reset
        return [(K_RESET, EMPTY)] * 8, ((K_RESET, EMPTY), (K_RESET, EMPTY))
    rl = [(("P", ent, i), EMPTY) for i in range(8)]
    return rl, ((("P", ent, "fz"), EMPTY), (("P", ent, "fc"), EMPTY))
