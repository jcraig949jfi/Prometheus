"""NPE reference ancestry tracer (independent, from ANCESTRY_PREREG_v4 s1/s2.1-2.2/s4.1 as
amended by ANCESTRY_PREREG_v5 R1, R4, R8, C1-C5).

Cell: Z8_32 (L = 32), PAIR_TAPE x PAIR_EXECUTION, ops mask 0x0C (GETPC + SENSE), BYTEWISE,
no inputs, OPCODE/LOCAL mutation at write-back (rate LOW = 0.002).

Observation-only shadow. `shadow_slice` is a line-for-line shadow of z8.run (frozen engine,
z8.py:160-488) that carries, per byte and per register/flag, a DATA LABEL and an ADDR SET, and
per interaction the PC label (ctrl), a post-dominator-scoped PC label stack and the running
exec set. Every slice is asserted equal to the frozen engine (z8.run on a copy: tape, regs,
flags, returned pc, halted and every telemetry counter), every interaction is asserted equal to
p11.interact (the engine's own re-execution of world._pair_interact), and the write-back
mutation is asserted equal to world.Runner._mutate on a clone of the RNG. No engine file is
modified; the engine is imported read-only from ENGINE_DIR.

Label vocabulary (tuples, hashable):
  ('ENTITY', side, j, orig_id)   side in {'a','b'}: pre-interaction byte j of that organism's half
  ('CONST', kind)                FOREIGN-STRUCTURAL; never a member of a dependence set (C2 CHOICE 3)
  ('CONTEXT', op)                GETPC -> 'GETPC', SENSE -> 'SENSE_side' (C5 N2)
  ('PREG', side, name)           an organism's persisted register / flag at interaction start
  ('COMPUTED', frozenset(bases))
  ('COMPUTED_FROM', label)       INC/DEC r (register-only bijective); flattened, never nested
  ('MUTATION', draw, old_label)  write-back mutation; draw = (side, rng-call index within
                                 this interaction's write-back, position)
See SPEC_ISSUES.md for every reading taken.
"""
from __future__ import annotations

import os
import random
import sys
import types

ENGINE_DIR = os.path.expanduser(
    "~/Prometheus-worktrees/npereftr/roles/Nestor/campaigns/z80atlas-verify-2026-09-22")
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

import z8        # noqa: E402  (frozen engine, read-only)
import p11       # noqa: E402
import world     # noqa: E402

N = 32
TAPE = 64
BUDGET = 360          # grammar.TIERS["L"]["slice"]
OPS_MASK = 0x0C       # world.Runner._ops_mask() for the T-003 cell
MUT_RATE = 0.002      # world.MUT_RATE["LOW"]
CELL = {"atlas_axis": "DELETERIOUS_LOAD", "bridge": "VALLEY", "copy_primitive": "BYTEWISE",
        "environment": "RESOURCE_LIMITED", "mutation_locality": "LOCAL",
        "mutation_operator": "OPCODE", "mutation_rate": "LOW", "pressure": "EXEC_TIME_COST",
        "read_order": "FORCED_READ", "representation": "Z8_32", "reproduction": "PAIR_EXECUTION",
        "seeding": "RANDOM", "self_location": "PC_RELATIVE", "structure": "RESERVOIR",
        "task_transform": "ADD37", "world": "PAIR_TAPE"}      # manifest.H3_CELLS[0]

B, C, D, E, H, L, M, A = 0, 1, 2, 3, 4, 5, 6, 7
REGN = ("B", "C", "D", "E", "H", "L", "M", "A")
EMPTY = frozenset()

# ------------------------------------------------------------------ label algebra


def bases(lab):
    """Base labels of a data label. CONSTANT contributes nothing (C2 CHOICE 3)."""
    k = lab[0]
    if k == "CONST":
        return EMPTY
    if k == "COMPUTED":
        return lab[1]
    if k == "COMPUTED_FROM":
        return bases(lab[1])
    return frozenset((lab,))          # ENTITY, CONTEXT, PREG, MUTATION


def computed(*sets):
    s = frozenset().union(*sets) if sets else EMPTY
    return ("COMPUTED", s)


def computed_from(lab):
    if lab[0] in ("COMPUTED_FROM", "COMPUTED"):
        return lab
    return ("COMPUTED_FROM", lab)


def entity_of(lab):
    """The material entity a label counts to (inherited labels count to their carrier)."""
    if lab is None:
        return None
    if lab[0] == "ENTITY":
        return lab[1]
    if lab[0] == "COMPUTED_FROM":
        return None
    return None


def is_move(lab):
    return lab is not None and lab[0] == "ENTITY"


# ------------------------------------------------------------------ static decode helpers
_NOP1 = "NOP1"


def _canon(op, op2, ops_mask):
    """Semantic opcode for the flip-test path (R4): undefined 1-byte ops are one class, and
    disabled/unknown ED ops are one 2-byte class."""
    if op == 0xED:
        en = {0xB0: 0x20, 0xB8: 0x20, 0x30: 0x01, 0x31: 0x01, 0x32: 0x02, 0x33: 0x04,
              0x34: 0x08, 0x35: 0x10}.get(op2)
        if en is not None and (ops_mask & en):
            return ("ED", op2)
        return ("ED", "NOP2")
    if _length(op) == 1 and _is_nop(op):
        return _NOP1
    return op


def _is_nop(op):
    if 0x40 <= op < 0xC0:
        return False
    if op < 0x40 and (op & 7) in (4, 5, 6):
        return False
    return op not in (0x01, 0x11, 0x21, 0x31, 0x02, 0x12, 0x0A, 0x1A, 0x03, 0x13, 0x23, 0x0B,
                      0x1B, 0x2B, 0x18, 0x20, 0x28, 0x30, 0x38, 0xC3, 0xC2, 0xCA, 0xD2, 0xDA,
                      0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE, 0xDB, 0xD3, 0xED)


def _length(op):
    if op < 0x40 and (op & 7) == 6:
        return 2
    if op in (0x01, 0x11, 0x21, 0x31, 0xC3, 0xC2, 0xCA, 0xD2, 0xDA):
        return 3
    if op in (0x18, 0x20, 0x28, 0x30, 0x38, 0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE, 0xDB, 0xD3, 0xED):
        return 2
    return 1


def _succ(mem, p):
    """CFG successors of tape address p under the current tape contents (65 = EXIT)."""
    mask = len(mem) - 1
    op = mem[p]
    if op == 0x76:
        return (TAPE,)
    if op in (0x18, 0x20, 0x28, 0x30, 0x38):
        e = mem[(p + 1) & mask]
        e = e - 256 if e > 127 else e
        t = (p + 2 + e) & mask
        return (t,) if op == 0x18 else (t, (p + 2) & mask)
    if op in (0xC3, 0xC2, 0xCA, 0xD2, 0xDA):
        t = (mem[(p + 1) & mask] | (mem[(p + 2) & mask] << 8)) & mask
        return (t,) if op == 0xC3 else (t, (p + 3) & mask)
    return ((p + _length(op)) & mask,)


def ipdoms(mem):
    """Immediate post-dominator of every tape address in the CFG of the current tape (EXIT =
    HALT). Addresses that cannot reach EXIT (budget-only termination) get None: their scope
    lasts to the end of the slice. The step budget is not an edge (it is CONSTANT)."""
    n = len(mem)
    succ = [_succ(mem, p) for p in range(n)]
    pred = [[] for _ in range(n + 1)]
    for p in range(n):
        for s in succ[p]:
            pred[s].append(p)
    reach = {n}
    stack = [n]
    while stack:
        x = stack.pop()
        for p in pred[x]:
            if p not in reach:
                reach.add(p)
                stack.append(p)
    full = (1 << (n + 1)) - 1
    pd = [full] * (n + 1)
    pd[n] = 1 << n
    changed = True
    while changed:
        changed = False
        for p in range(n):
            if p not in reach:
                continue
            m = full
            for s in succ[p]:
                m &= pd[s]
            m |= 1 << p
            if m != pd[p]:
                pd[p] = m
                changed = True
    out = [None] * n
    for p in range(n):
        if p not in reach:
            continue
        strict = pd[p] & ~(1 << p)
        # the ipdom is the strict post-dominator whose own set equals the strict set
        q = strict
        while q:
            low = q & -q
            d = low.bit_length() - 1
            if pd[d] == strict:
                out[p] = d
                break
            q ^= low
    return out


# ------------------------------------------------------------------ the shadow


class EngineMismatch(AssertionError):
    pass


class Interaction:
    """Label state of one pair interaction (both slices share tape labels, exec and ctrl)."""

    def __init__(self, tape, orig_a, orig_b, n=N):
        self.n = n
        self.mem = bytearray(tape)
        self.ml = [None] * len(tape)
        self.ma = [EMPTY] * len(tape)
        for j in range(n):
            self.ml[j] = ("ENTITY", "a", j, orig_a[j])
            self.ml[n + j] = ("ENTITY", "b", j, orig_b[j])
        self.exec_run = set()          # every fetched byte since interaction start
        self.ctrl_run = set()          # PC label since interaction start (primary)
        self.info = {}                 # tape addr -> last-store record
        self.trace = []                # (who, pc, canonical opcode)
        self.loads = []                # (who, addr) ; ('IN', cursor) entries
        self.stores = []               # (who, addr) ; ('OUT', count) entries
        self.flags = {"budget_ended": [False, False], "halted": [False, False]}
        self.writes_other = [0, 0]
        self.donor_store_deps = [set(), set()]
        self._pd_cache = {}

    def pd(self):
        k = bytes(self.mem)
        r = self._pd_cache.get(k)
        if r is None:
            r = self._pd_cache[k] = ipdoms(self.mem)
        return r


def _reg_labels(side, st, reg_labels):
    """Initial register/flag labels of one organism. regs None = the Org default (zeros):
    CONSTANT('reset'). Otherwise the persisted values get PREG base labels, unless the caller
    passes labels carried from the previous interaction (label persistence, v4 s1.2)."""
    regs, fz, fc = st
    if reg_labels is not None:
        rl, ra, zl, za, cl, ca = reg_labels
        return list(rl), list(ra), zl, za, cl, ca
    if regs is None:
        c = ("CONST", "reset")
        return [c] * 8, [EMPTY] * 8, c, EMPTY, c, EMPTY
    rl = [("PREG", side, REGN[i]) for i in range(8)]
    return (rl, [EMPTY] * 8, ("PREG", side, "fz"), EMPTY, ("PREG", side, "fc"), EMPTY)


def shadow_slice(S, who, start, budget, ops_mask, st, rlab):
    """Line-for-line shadow of z8.run(ctx, start, budget, ops_enabled) for one pair slice
    (ctx = Ctx(tape, start, n, ARENA, sense=who)). Returns (pc, regs, fz, fc, tel, rlab)."""
    mem, ml, ma = S.mem, S.ml, S.ma
    size = len(mem)
    mask = size - 1
    n = S.n
    side = "ab"[who]
    regs, fz, fc = st
    r = [0] * 8 if regs is None else list(regs)
    rl, ra, zl, za, cl, ca = rlab
    steps = 0
    tel = dict(ops=0, writes=0, writes_own=0, writes_other=0, writes_blocked=0,
               self_overwrites=0, world_op_calls=0, halted=False, budget_exhausted=False,
               in_reads=0, out_writes=0, outputs=[])
    ctrl_slice = set()                 # PC label reset at slice entry (secondary)
    pdstack = []                       # [ipdom, set]
    in_lab = EMPTY                     # IN counter label (C2)
    out_lab = EMPTY                    # OUT counter label
    exec_run, ctrl_run = S.exec_run, S.ctrl_run

    def dep(lab, adr):
        return bases(lab) | adr

    def fetch(addr):
        a = addr & mask
        exec_run.update(bases(ml[a]))
        exec_run.update(ma[a])
        return a, mem[a]

    def ptr(hi, lo):
        return bases(rl[hi]) | ra[hi] | bases(rl[lo]) | ra[lo]

    def load(addr, pdeps):
        a = addr & mask
        S.loads.append((who, a))
        return mem[a], ml[a], ma[a] | pdeps

    def cond(deps, pc_here, branch):
        ctrl_run.update(deps)
        ctrl_slice.update(deps)
        if branch and deps:
            ip = S.pd()[pc_here]
            if pdstack and pdstack[-1][0] == ip:
                pdstack[-1][1].update(deps)
            else:
                pdstack.append([ip, set(deps)])

    def store(addr, val, lab, adr, pdeps, op_pc, perf):
        a = addr & mask
        # z8.py:178-204 (ARENA policy: always writable)
        mem[a] = val & 0xFF
        ml[a] = lab
        ma[a] = frozenset(adr | pdeps)
        tel["writes"] += 1
        if start <= a < start + n:
            tel["writes_own"] += 1
            if a != start:
                tel["self_overwrites"] += 1
        else:
            tel["writes_other"] += 1
        S.stores.append((who, a))
        pdom = set()
        for _ip, s in pdstack:
            pdom |= s
        S.info[a] = {"written": True, "who": side, "store_pc": op_pc, "performer": perf,
                     "ctrl": frozenset(ctrl_run), "ctrl_slice": frozenset(ctrl_slice),
                     "ctrl_pdom": frozenset(pdom), "exec": frozenset(exec_run),
                     "addr": ma[a], "ptr": frozenset(pdeps)}
        S.donor_store_deps[who] |= ctrl_run
        S.donor_store_deps[who] |= pdeps

    pc = start
    while steps < budget:              # z8.py:209 (budget: CONSTANT, flagged not labelled)
        steps += 1
        pc = pc & mask
        while pdstack and pdstack[-1][0] == pc:
            pdstack.pop()
        _, op = fetch(pc)
        perf = ml[pc]                  # performer = material label of this opcode byte
        op_pc = pc

        if 0x40 <= op < 0x80:          # z8.py:215-229
            if op == 0x76:
                S.trace.append((who, pc, op))
                tel["halted"] = True
                S.flags["halted"][who] = True
                tel["ops"] = steps
                return pc, r, fz, fc, tel, (rl, ra, zl, za, cl, ca)
            S.trace.append((who, pc, op))
            dst = (op >> 3) & 7
            src = op & 7
            hlp = ptr(H, L)
            if src == M:
                v, vl, va = load((r[H] << 8) | r[L], hlp)
            else:
                v, vl, va = r[src], rl[src], ra[src]
            if dst == M:
                store((r[H] << 8) | r[L], v, vl, va, hlp, op_pc, perf)
            else:
                r[dst], rl[dst], ra[dst] = v, vl, va
            pc += 1
            continue

        if 0x80 <= op < 0xC0:          # z8.py:232-259
            S.trace.append((who, pc, op))
            src = op & 7
            if src == M:
                v, vl, va = load((r[H] << 8) | r[L], ptr(H, L))
            else:
                v, vl, va = r[src], rl[src], ra[src]
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
            # labels
            if src == A and kind in (2, 5, 7):          # SUB A,A / XOR A,A / CP A,A: idioms
                idl = ("CONST", ("SUB_AA", "XOR_AA", "CP_AA")[(2, 5, 7).index(kind)])
                resl, resa = idl, EMPTY
                zl2, za2, cl2, ca2 = idl, EMPTY, idl, EMPTY
            else:
                bs = bases(rl[A]) | bases(vl)
                ad = ra[A] | va
                if kind in (1, 3):
                    bs = bs | bases(cl)
                    ad = ad | ca
                resl, resa = computed(bs), ad
                zl2, za2 = resl, resa
                if kind in (4, 5, 6):                    # logic ops: carry is always 0
                    cl2, ca2 = ("CONST", "logic_nc"), EMPTY
                else:
                    cl2, ca2 = resl, resa
            fc = 1 if (t > 255 or t < 0) else 0
            t &= 0xFF
            fz = 1 if t == 0 else 0
            zl, za, cl, ca = zl2, za2, cl2, ca2
            if kind != 7:
                r[A], rl[A], ra[A] = t, resl, resa
            pc += 1
            continue

        lo = op & 7
        if lo in (4, 5) and op < 0x40:  # z8.py:263-284 INC/DEC r
            S.trace.append((who, pc, op))
            d = (op >> 3) & 7
            delta = 1 if lo == 4 else -1
            if d == M:
                hlp = ptr(H, L)
                addr = (r[H] << 8) | r[L]
                ov, ovl, ova = load(addr, hlp)
                v = (ov + delta) & 0xFF
                nl = computed(bases(ovl))                # memory operand: not register-only
                store(addr, v, nl, ova, hlp, op_pc, perf)
                zl, za = nl, ova | hlp
            else:
                v = r[d] = (r[d] + delta) & 0xFF
                rl[d] = computed_from(rl[d])
                zl, za = computed(bases(rl[d])), ra[d]
            fz = 1 if v == 0 else 0
            pc += 1
            continue
        if lo == 6 and op < 0x40:      # z8.py:285-293 LD r,n
            S.trace.append((who, pc, op))
            d = (op >> 3) & 7
            oa, nv = fetch(pc + 1)
            if d == M:
                hlp = ptr(H, L)
                store((r[H] << 8) | r[L], nv, ml[oa], ma[oa], hlp, op_pc, perf)
            else:
                r[d], rl[d], ra[d] = nv, ml[oa], ma[oa]
            pc += 2
            continue

        if op in (0x01, 0x11, 0x21, 0x31):   # z8.py:296-305
            S.trace.append((who, pc, op))
            a1, v1 = fetch(pc + 1)
            a2, v2 = fetch(pc + 2)
            if op != 0x31:
                hi, lo_ = {0x01: (B, C), 0x11: (D, E), 0x21: (H, L)}[op]
                r[hi], rl[hi], ra[hi] = v2, ml[a2], ma[a2]
                r[lo_], rl[lo_], ra[lo_] = v1, ml[a1], ma[a1]
            pc += 3
            continue
        if op in (0x02, 0x12):         # z8.py:306-309
            S.trace.append((who, pc, op))
            hi, lo_ = (B, C) if op == 0x02 else (D, E)
            store((r[hi] << 8) | r[lo_], r[A], rl[A], ra[A], ptr(hi, lo_), op_pc, perf)
            pc += 1
            continue
        if op in (0x0A, 0x1A):         # z8.py:310-313
            S.trace.append((who, pc, op))
            hi, lo_ = (B, C) if op == 0x0A else (D, E)
            v, vl, va = load((r[hi] << 8) | r[lo_], ptr(hi, lo_))
            r[A], rl[A], ra[A] = v, vl, va
            pc += 1
            continue
        if op in (0x03, 0x13, 0x23, 0x0B, 0x1B, 0x2B):   # z8.py:314-320
            S.trace.append((who, pc, op))
            hi, lo_ = (B, C) if op in (0x03, 0x0B) else ((D, E) if op in (0x13, 0x1B) else (H, L))
            v = ((r[hi] << 8) | r[lo_]) + (1 if op in (0x03, 0x13, 0x23) else -1)
            v &= 0xFFFF
            r[hi], r[lo_] = (v >> 8) & 0xFF, v & 0xFF
            hl_, ha_ = computed(bases(rl[hi]), bases(rl[lo_])), ra[hi] | ra[lo_]
            rl[lo_] = computed_from(rl[lo_])
            rl[hi], ra[hi] = hl_, ha_
            pc += 1
            continue

        if op in (0x18, 0x20, 0x28, 0x30, 0x38):   # z8.py:323-330
            S.trace.append((who, pc, op))
            _, e = fetch(pc + 1)
            if e > 127:
                e -= 256
            if op != 0x18:
                fl = (zl, za) if op in (0x20, 0x28) else (cl, ca)
                cond(dep(*fl), pc, True)
            take = (op == 0x18 or (op == 0x20 and not fz) or (op == 0x28 and fz)
                    or (op == 0x30 and not fc) or (op == 0x38 and fc))
            pc = pc + 2 + e if take else pc + 2
            continue

        if op in (0xC3, 0xC2, 0xCA, 0xD2, 0xDA):   # z8.py:333-338
            S.trace.append((who, pc, op))
            _, v1 = fetch(pc + 1)
            _, v2 = fetch(pc + 2)
            nn = v1 | (v2 << 8)
            if op != 0xC3:
                fl = (zl, za) if op in (0xC2, 0xCA) else (cl, ca)
                cond(dep(*fl), pc, True)
            take = (op == 0xC3 or (op == 0xC2 and not fz) or (op == 0xCA and fz)
                    or (op == 0xD2 and not fc) or (op == 0xDA and fc))
            pc = nn if take else pc + 3
            continue

        if op in (0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE):   # z8.py:341-362
            S.trace.append((who, pc, op))
            oa, v = fetch(pc + 1)
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
            resl = computed(bases(rl[A]), bases(ml[oa]))
            resa = ra[A] | ma[oa]
            fc = 1 if (t > 255 or t < 0) else 0
            t &= 0xFF
            fz = 1 if t == 0 else 0
            zl, za = resl, resa
            if op in (0xE6, 0xEE, 0xF6):
                cl, ca = ("CONST", "logic_nc"), EMPTY
            else:
                cl, ca = resl, resa
            if op != 0xFE:
                r[A], rl[A], ra[A] = t, resl, resa
            pc += 2
            continue

        if op == 0xDB:                 # z8.py:365-373 (the operand byte is never read)
            S.trace.append((who, pc, op))
            in_lab = frozenset(ctrl_run)          # counter label = PC label here (C2)
            cond(in_lab, pc, False)               # in_cursor < len(inputs) guard
            S.loads.append(("IN", who, 0))
            r[A], rl[A], ra[A] = 0, ("CONST", "in_exhausted"), in_lab   # C5 N3: no inputs
            pc += 2
            continue
        if op == 0xD3:                 # z8.py:374-392 (no tape store; operand never read)
            S.trace.append((who, pc, op))
            cond(in_lab, pc, False)               # H1 gate: in_reads < out_gate_reads (0)
            cond(out_lab, pc, False)              # len(outputs) < 64 guard
            if len(tel["outputs"]) < 64:
                tel["outputs"].append(r[A])
            S.stores.append(("OUT", who, tel["out_writes"]))
            tel["out_writes"] += 1
            out_lab = frozenset(ctrl_run)
            pc += 2
            continue

        if op == 0xED:                 # z8.py:395-480
            _, op2 = fetch(pc + 1)
            S.trace.append((who, pc, _canon(op, op2, ops_mask)))
            pc += 2
            if op2 in (0xB0, 0xB8, 0x30, 0x31, 0x35, 0x32):
                bit = {0xB0: 0x20, 0xB8: 0x20, 0x30: 0x01, 0x31: 0x01, 0x35: 0x10, 0x32: 0x02}[op2]
                if not (ops_mask & bit):
                    continue
                raise NotImplementedError("world op %02X enabled: outside the T-003 cell" % op2)
            if op2 == 0x33:
                if not (ops_mask & 0x04):
                    continue
                tel["world_op_calls"] += 1
                p = (pc - 2) & 0xFFFF
                r[H], r[L] = (p >> 8) & 0xFF, p & 0xFF
                rl[H] = rl[L] = ("CONTEXT", "GETPC")
                ra[H] = ra[L] = EMPTY
                continue
            if op2 == 0x34:
                if not (ops_mask & 0x08):
                    continue
                tel["world_op_calls"] += 1
                r[A], rl[A], ra[A] = who & 0xFF, ("CONTEXT", "SENSE_side"), EMPTY
                continue
            continue

        S.trace.append((who, pc, _NOP1))   # z8.py:483 one-byte NOP
        pc += 1

    tel["ops"] = steps
    tel["budget_exhausted"] = True
    S.flags["budget_ended"][who] = True
    return pc & mask, r, fz, fc, tel, (rl, ra, zl, za, cl, ca)


# ------------------------------------------------------------------ engine checks


def _engine_slice(tape, who, start, n, budget, ops_mask, st):
    ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=random.Random(0), copy_mut_rate=0.0,
                 sense=who)
    regs, fz, fc = st
    ctx.regs, ctx.fz, ctx.fc = (None if regs is None else list(regs)), fz, fc
    pc = z8.run(ctx, start, budget, ops_enabled=ops_mask)
    return pc, ctx


def _check_slice(label, mine, eng_tape, pc_e, ctx, S):
    pc, r, fz, fc, tel, _ = mine
    probs = []
    if bytes(S.mem) != bytes(eng_tape):
        probs.append("tape")
    if (pc, list(r), fz, fc) != (pc_e, list(ctx.regs), ctx.fz, ctx.fc):
        probs.append("pc/regs/flags %r vs %r" % ((pc, r, fz, fc), (pc_e, ctx.regs, ctx.fz, ctx.fc)))
    for k in ("ops", "writes", "writes_own", "writes_other", "writes_blocked", "self_overwrites",
              "world_op_calls", "halted", "budget_exhausted", "in_reads", "out_writes"):
        if tel[k] != getattr(ctx, k):
            probs.append("%s %r vs %r" % (k, tel[k], getattr(ctx, k)))
    if tel["outputs"] != ctx.outputs:
        probs.append("outputs")
    if probs:
        raise EngineMismatch("%s: shadow != frozen z8.run: %s" % (label, "; ".join(probs)))


def _engine_mutate(g, rng, cell=CELL, mut_rate=MUT_RATE, slot_size=2 * N):
    stub = types.SimpleNamespace(cell=cell, mut_rate=mut_rate, rng=rng, slot_size=slot_size)
    stub._boundaries = lambda gg: world.Runner._boundaries(stub, gg)
    stub._recombine = lambda gg: world.Runner._recombine(stub, gg)
    return world.Runner._mutate(stub, g)


# ------------------------------------------------------------------ write-back


class _CountingRNG:
    def __init__(self, rng):
        self.rng = rng
        self.calls = 0

    def random(self):
        self.calls += 1
        return self.rng.random()

    def randrange(self, *a):
        self.calls += 1
        return self.rng.randrange(*a)


def writeback_mutation(side, half, labels, crng, rate=MUT_RATE):
    """Shadow of world.Runner._mutate for OPCODE/LOCAL (world.py:484-550). Returns
    (new bytes, new labels, events). Decode-dependence = base labels of the opcode bytes at
    the linear-decode boundaries BEFORE position i (they fix i's position class)."""
    g = bytearray(half)
    labs = list(labels)
    bnds = [a for a, _ in z8.dis(bytes(g))]         # computed once, pre-mutation
    opcodes = set(bnds)
    events = []
    for i in range(len(g)):
        draw = crng.calls
        u = crng.random()
        if u >= rate:
            continue
        if i not in opcodes:                         # OPCODE operator skips operands
            events.append({"pos": i, "draw": draw, "applied": False, "reason": "not_opcode",
                           "decode_dependence": _decdep(bnds, i, labels)})
            continue
        old_v, old_l = g[i], labs[i]
        g[i] = crng.randrange(256)
        labs[i] = ("MUTATION", (side, draw, i), old_l)
        events.append({"pos": i, "draw": draw, "applied": True, "old": old_v, "new": g[i],
                       "old_label": old_l, "decode_dependence": _decdep(bnds, i, labels)})
    return bytes(g), labs, events


def _decdep(bnds, i, labels):
    s = set()
    for b_ in bnds:
        if b_ >= i:
            break
        s |= bases(labels[b_])
    return frozenset(s)


# ------------------------------------------------------------------ the public entry point


def trace_interaction(ga, gb, st_a, st_b, *, n=N, budget=BUDGET, ops_mask=OPS_MASK,
                      rng=None, mut_rate=MUT_RATE, cell=CELL, orig_a=None, orig_b=None,
                      reg_labels_a=None, reg_labels_b=None, check_engine=True):
    """Trace one NPE pair interaction.

    ga, gb     : the two organisms' genomes (world.Runner._genome), len <= n
    st_a, st_b : (regs or None, fz, fc) persisted BEFORE the interaction (a runs first)
    rng        : the world RNG at write-back time (random.Random); None = no write-back.
                 It is not consumed: a clone is used, and the clone's state is returned.
    orig_a/b   : per-locus orig_id carried into the ENTITY labels (default: 'a'/'b')
    Returns a dict; 'loci' is a list of 2n records, index h*n + i for half h in (a, b).
    """
    orig_a = orig_a or ["a"] * n
    orig_b = orig_b or ["b"] * n
    tape = bytearray(1 << (2 * n - 1).bit_length())
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    pre = bytes(tape)
    S = Interaction(tape, orig_a, orig_b, n)
    rl0 = [_reg_labels("a", st_a, reg_labels_a), _reg_labels("b", st_b, reg_labels_b)]
    out_regs = []
    tels = []
    etape = bytearray(pre)
    for who, start, st in ((0, 0, st_a), (1, n, st_b)):
        res = shadow_slice(S, who, start, budget, ops_mask, st, rl0[who])
        if check_engine:
            pc_e, ctx = _engine_slice(etape, who, start, n, budget, ops_mask, st)
            _check_slice("slice %s" % "ab"[who], res, etape, pc_e, ctx, S)
        out_regs.append((res[1], res[2], res[3]))
        tels.append(res[4])
        S.writes_other[who] = res[4]["writes_other"]
        rlab = res[5]
        rl0[who] = rlab
    if check_engine:
        tp, _, _, wo = p11.interact(z8, n=n, tape_len=len(pre), ga=ga, gb=gb, st_a=st_a,
                                    st_b=st_b, budget=budget, ops_mask=ops_mask, cmr=0.0,
                                    rng=random.Random(0))
        if bytes(tp) != bytes(S.mem) or list(wo) != S.writes_other:
            raise EngineMismatch("interaction != p11.interact")
    post = bytes(S.mem)
    exec_whole = frozenset(S.exec_run)
    ctrl_whole = frozenset(S.ctrl_run)

    loci = []
    for h, side in enumerate("ab"):
        for i in range(n):
            a = h * n + i
            inf = S.info.get(a)
            lab = S.ml[a]
            rec = {"half": side, "i": i, "tape_addr": a, "pre": pre[a], "post": post[a],
                   "label": lab, "written": inf is not None, "mutated": False}
            if inf:
                rec.update({"store_by": inf["who"], "store_pc": inf["store_pc"],
                            "performer": inf["performer"],
                            "performer_entity": entity_of(inf["performer"]),
                            "ctrl_deps": inf["ctrl"], "ctrl_deps_slice": inf["ctrl_slice"],
                            "ctrl_deps_pdom": inf["ctrl_pdom"], "ctrl_deps_whole": ctrl_whole,
                            "addr_deps": inf["addr"], "exec_deps": inf["exec"],
                            "exec_deps_whole": exec_whole})
            else:
                rec.update({"store_by": None, "store_pc": None, "performer": None,
                            "performer_entity": None, "ctrl_deps": EMPTY,
                            "ctrl_deps_slice": EMPTY, "ctrl_deps_pdom": EMPTY,
                            "ctrl_deps_whole": EMPTY, "addr_deps": S.ma[a], "exec_deps": EMPTY,
                            "exec_deps_whole": EMPTY})
            loci.append(rec)

    out = {"pre_tape": pre, "post_tape": post, "loci": loci, "regs_after": out_regs,
           "reg_labels_after": rl0, "telemetry": tels, "flags": S.flags,
           "trace": S.trace, "loads": S.loads, "stores": S.stores,
           "writes_other": list(S.writes_other), "exec_whole": exec_whole,
           "ctrl_whole": ctrl_whole}

    # ---- write-back (world.py:817-830): a's half then b's half, one RNG
    if rng is not None:
        crng = _CountingRNG(random.Random())
        crng.rng.setstate(rng.getstate())
        erng = random.Random()
        erng.setstate(rng.getstate())
        halves = {}
        for h, side in enumerate("ab"):
            half = post[h * n:(h + 1) * n]
            labs = [loci[h * n + i]["label"] for i in range(n)]
            new, nl, ev = writeback_mutation(side, half, labs, crng, mut_rate)
            if check_engine:
                enew = _engine_mutate(half, erng, cell, mut_rate)
                if enew != new:
                    raise EngineMismatch("write-back mutation != world.Runner._mutate")
            for e in ev:
                if e["applied"]:
                    rec = loci[h * n + e["pos"]]
                    rec["mutated"] = True
                    rec["mutation"] = e
                    rec["label"] = nl[e["pos"]]
                    rec["addr_deps"] = EMPTY          # Amendment C10(b), 2026-09-28 post-agreement-test repair: a MUTATION value is a
                                                      # fresh draw at a fixed position; no pointer selects it (decode-dependence is in the event)
            for i in range(n):
                loci[h * n + i]["final"] = new[i]
            halves[side] = (new, ev)
        if check_engine and crng.rng.getstate() != erng.getstate():
            raise EngineMismatch("RNG consumption differs from the engine")
        out["rng_state_after"] = crng.rng.getstate()
        out["rng_calls"] = crng.calls
        out["mutation_events"] = {s: halves[s][1] for s in "ab"}
        out["births"] = _births(ga, gb, halves, loci, S, n)
    return out


def _births(ga, gb, halves, loci, S, n):
    """N1: a birth = P-11 predecessor acceptance of a half (world.py:835-843)."""
    res = {}
    for h, side in enumerate("ab"):
        new = halves[side][0]
        old = ga if side == "a" else gb
        other = gb if side == "a" else ga
        donor = 1 - h
        fid_self = world._fidelity(old, new)
        fid_other = world._fidelity(other, new)
        dw = S.writes_other[donor]
        acc = p11.predecessor_accepts(fid_other, fid_self, dw, n)
        victim_final = set()
        for i in range(n):
            victim_final |= bases(loci[h * n + i]["label"])
        ex = {"victim_final_half": frozenset(victim_final),
              "victim_pre": frozenset(("ENTITY", side, j) for j in range(len(old))),
              "donor_pre": frozenset(("ENTITY", "ab"[donor], j) for j in range(len(other))),
              "donor_writes_other": frozenset(S.donor_store_deps[donor])}
        res[side] = {"victim": side, "donor": "ab"[donor], "accepted": bool(acc),
                     "fid_self": fid_self, "fid_other": fid_other, "donor_writes_other": dw,
                     "birth_existence_deps": ex}
    return res


# ------------------------------------------------------------------ s4.1 flip test (+B1, R4)


def _path(out):
    return (tuple(out["trace"]), tuple(out["stores"]), tuple(out["loads"]))


def flip_test(ga, gb, st_a, st_b, base=None, *, n=N, budget=BUDGET, ops_mask=OPS_MASK,
              check_engine=True):
    """Path-preserving flip test over every written locus whose data label is ENTITY MOVE.
    Applicable bit: fetched-instruction trace (pc, semantic opcode; R4), store-address
    sequence (incl. OUT, R4) and load-address sequence (B1) all unchanged. Evaluated on the
    interaction output (before write-back mutation). Returns {tape_addr: verdict record}."""
    if base is None:
        base = trace_interaction(ga, gb, st_a, st_b, n=n, budget=budget, ops_mask=ops_mask,
                                 check_engine=check_engine)
    bpath = _path(base)
    cache = {}
    res = {}
    for rec in base["loci"]:
        if not rec["written"] or not is_move(rec["label"]) or rec.get("mutated"):
            continue
        _, X, j, _o = rec["label"]
        src = (0 if X == "a" else n) + j
        bits = []
        for bit in range(8):
            key = (src, bit)
            if key not in cache:
                fa, fb = bytearray(ga), bytearray(gb)
                (fa if X == "a" else fb)[j] ^= 1 << bit
                cache[key] = trace_interaction(bytes(fa), bytes(fb), st_a, st_b, n=n,
                                               budget=budget, ops_mask=ops_mask,
                                               check_engine=check_engine)
            fo = cache[key]
            if _path(fo) != bpath:
                bits.append("INAPPLICABLE")
                continue
            pred = base["pre_tape"][src] ^ (1 << bit)
            bits.append("CONFIRMED" if fo["post_tape"][rec["tape_addr"]] == pred else "FAILED")
        if "FAILED" in bits:
            v = "FAILED"
        elif "CONFIRMED" in bits:
            v = "CONFIRMED"
        else:
            v = "INAPPLICABLE"
        res[rec["tape_addr"]] = {"verdict": v, "bits": bits, "label": rec["label"]}
    return res


# ------------------------------------------------------------------ R1.3 / R2 intervention arm


def dependence_arm(ga, gb, st_a, st_b, base=None, *, K=8, seed=0, n=N, budget=BUDGET,
                   ops_mask=OPS_MASK, check_engine=True):
    """Randomise each source group (ENTITY a bytes, ENTITY b bytes, persisted registers+flags
    of a, of b) K times; per written ENTITY-MOVE locus count value changes among draws in which
    the write occurs, for groups OUTSIDE {data-label entity, performer entity} (R1.3, R2), and
    write suppressions for every group, performer included (Q8c-whether, C4.1)."""
    if base is None:
        base = trace_interaction(ga, gb, st_a, st_b, n=n, budget=budget, ops_mask=ops_mask,
                                 check_engine=check_engine)
    rr = random.Random(seed)
    groups = ["a", "b"]
    if st_a[0] is not None:
        groups.append("regs_a")
    if st_b[0] is not None:
        groups.append("regs_b")
    runs = {}
    for g in groups:
        runs[g] = []
        for _k in range(K):
            xa, xb, sa, sb = ga, gb, st_a, st_b
            if g == "a":
                xa = bytes(rr.randrange(256) for _ in range(len(ga)))
            elif g == "b":
                xb = bytes(rr.randrange(256) for _ in range(len(gb)))
            elif g == "regs_a":
                sa = ([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2))
            else:
                sb = ([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2))
            runs[g].append(trace_interaction(xa, xb, sa, sb, n=n, budget=budget,
                                             ops_mask=ops_mask, check_engine=check_engine))
    res = {}
    for rec in base["loci"]:
        if not rec["written"]:
            continue
        a = rec["tape_addr"]
        own = {entity_of(rec["label"]), rec["performer_entity"]}
        r_ = {"label": rec["label"], "value_change": 0, "draws": 0, "suppressed": {},
              "outside": []}
        for g, outs in runs.items():
            ent = g if g in ("a", "b") else None
            r_["suppressed"][g] = sum(1 for o in outs if not o["loci"][a]["written"])
            if ent is not None and ent in own:
                continue
            r_["outside"].append(g)
            for o in outs:
                if not o["loci"][a]["written"]:
                    continue
                r_["draws"] += 1
                if o["post_tape"][a] != rec["post"]:
                    r_["value_change"] += 1
        res[a] = r_
    return res


def identified(base, flips, arm):
    """R1: ENTITY MOVE, flip not FAILED, and 0 value changes from outside groups."""
    out = {}
    for rec in base["loci"]:
        if not rec["written"]:
            continue
        a = rec["tape_addr"]
        ok = (is_move(rec["label"]) and flips.get(a, {}).get("verdict") != "FAILED"
              and arm.get(a, {}).get("value_change", 1) == 0)
        out[a] = ok
    return out


def fmt_label(lab):
    if lab is None:
        return "-"
    k = lab[0]
    if k == "ENTITY":
        return "%s%d" % (lab[1], lab[2])
    if k == "CONST":
        return "CONST(%s)" % (lab[1],)
    if k == "CONTEXT":
        return "CTX(%s)" % lab[1]
    if k == "PREG":
        return "PREG(%s.%s)" % (lab[1], lab[2])
    if k == "COMPUTED":
        return "COMPUTED{%s}" % ",".join(sorted(fmt_label(x) for x in lab[1]))
    if k == "COMPUTED_FROM":
        return "CF(%s)" % fmt_label(lab[1])
    if k == "MUTATION":
        return "MUT(%s,%s)" % (lab[1], fmt_label(lab[2]))
    return repr(lab)


def fmt_set(s):
    return "{%s}" % ",".join(sorted(fmt_label(x) for x in s))
