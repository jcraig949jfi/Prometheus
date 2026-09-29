"""Bellerophon's observation-only shadow tracer for BEE (E-003; ANCESTRY_PREREG v4 s1 + v5 + Amendments C2/C7.2).

Written from the prereg TEXT only (independence rule, Archaeon #920): archaeon/attribution/bee_ref_tracer.py and the
reference tracer were not read.

One call = one INTERACTION (v4 s1.1; BEE SHARED = one vm.execute call). The tracer is a label-carrying twin of the
frozen vm.execute (git 16fc6c2a, vm sha256 2536b1ac). Every run is VALUE-CHECKED against the frozen VM itself: final
memory, outputs, steps and the halt flag must be identical. The tracer never writes into the world.

Values. Every register, flag and memory byte carries (value, data label, addr set).
- Data label:
  * base labels ('E', entity, locus) / ('INPUT', k) / ('CONST', kind);
  * ('COMPUTED', frozenset(base labels));
  * ('COMPUTED_FROM', label).
- Addr set (C2 CHOICE 5): the base labels of every pointer that determined where the value was read from or written to.
  It is TRANSITIVE through memory and computation.
- bases(label):
  * E / INPUT -> {label};
  * CONST -> {} (C2 CHOICE 3: CONSTANT is never a member of a dependence set);
  * COMPUTED -> its set;
  * COMPUTED_FROM(x) -> bases(x).
- dep(value) = bases(label) | addr. dep is what a condition, a pointer or a fetched byte contributes.

Initial labels:
- own tape [0,L) -> ('E','W',i);
- window [L,2L) -> ('E','P',j);
- supplied input byte k -> ('INPUT',k);
- every other byte, including unsupplied input-region bytes (C2 CHOICE 9), -> ('CONST','zero');
- registers and flags -> ('CONST','reset').

Propagation (v4 s1.2):
- moves and loads carry the label; an immediate operand carries its byte's label;
- INC/DEC of a register -> COMPUTED_FROM (nested COMPUTED_FROM is flattened);
- every other computation -> COMPUTED(bases of all inputs);
- flags take the label of the operation that set them;
- IN reads the input byte's CURRENT label; beyond 16 reads it is ('CONST','in_exhausted');
- the IN/OUT counter's label is the PC label at that point, and it acts as the load / store pointer (C2).

Dependence sets per written window locus (the LAST store to it):
- ctrl (primary, whole-execution): the PC label, i.e. the dep() of every condition EVALUATED so far (JZ/JNZ/JC flag,
  DJNZ's B, each LDIR C==0 test); the budget is CONSTANT and never a label;
- addr: the stored value's addr set, which includes the store's pointer dep;
- exec_at_store: dep() of every fetched opcode/operand byte from interaction start up to and including the store;
  exec_whole is the same over the whole interaction;
- performer: the ENTITY bases of the store instruction's opcode byte label (for LDIR/COPYALL, that byte);
- the post-dominator ctrl scope (secondary, non-gating) is NOT implemented yet and is reported as absent.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional, Tuple

ZERO = ("CONST", "zero")
RESET = ("CONST", "reset")
EXHAUSTED = ("CONST", "in_exhausted")
EMPTY: FrozenSet = frozenset()


def bases(lab) -> FrozenSet:
    k = lab[0]
    if k in ("E", "INPUT"):
        return frozenset((lab,))
    if k == "CONST":
        return EMPTY
    if k == "COMPUTED":
        return lab[1]
    if k == "COMPUTED_FROM":
        return bases(lab[1])
    raise ValueError(lab)


def computed(*labs) -> tuple:
    s = set()
    for l in labs:
        s |= bases(l)
    return ("COMPUTED", frozenset(s))


def computed_from(lab) -> tuple:
    return lab if lab[0] == "COMPUTED_FROM" else ("COMPUTED_FROM", lab)


class V:
    """a value: (v, lab, addr)"""
    __slots__ = ("v", "lab", "addr")

    def __init__(self, v: int, lab, addr: FrozenSet = EMPTY):
        self.v = v & 0xFF; self.lab = lab; self.addr = addr

    def dep(self) -> FrozenSet:
        return bases(self.lab) | self.addr


def initial_labels(L: int, n_inputs: int, in_base: int) -> List[tuple]:
    labs = [ZERO] * 256
    for i in range(L):
        labs[i] = ("E", "W", i)
        labs[L + i] = ("E", "P", i)
    for k in range(n_inputs):
        labs[(in_base + k) & 0xFF] = ("INPUT", k)
    return labs


def trace(vm, mem: bytearray, L: int, budget: int, inputs: List[int], allow_copyall: bool = True,
          labels: Optional[List[tuple]] = None, check: bool = True, ev: Optional[list] = None) -> Tuple[bytearray, Dict[int, dict], dict]:
    """Shadow-execute one SHARED interaction from entry 0. Returns (memory after, recs per window locus 0..L-1, info).
    `mem` is NOT mutated. check=True value-checks against vm.execute on a copy.
    ev (optional list): the PATH is appended in execution order, for the flip test (v4 s4.1 + B1 + R4 + C7.2):
    ("F", pc, opclass) for each fetch, where opclass is the opcode, or "U" for any undefined byte (R4: undefined opcodes
    are equivalent NOPs); ("S", addr) for each store, OUT stores included; ("L", addr) for each data read (LD A,(r),
    LDI/LDIR/COPYALL sources, IN reads)."""
    il = labels if labels is not None else initial_labels(L, len(inputs), vm.IN_BASE)
    M = [V(mem[a], il[a]) for a in range(256)]
    R = {r: V(0, RESET) for r in "ABCDST"}
    Z = V(0, RESET); CF = V(0, RESET)
    pc = 0; steps = 0; halted = False; ip = 0; outputs: List[int] = []
    pcl: FrozenSet = EMPTY                                   # PC label (whole-execution ctrl scope)
    ex: FrozenSet = EMPTY                                    # exec deps so far
    recs: Dict[int, dict] = {}
    flags = {"ldir_c0_entered": False, "in_window_source": False, "budget_ended": False}
    nb_lo, nb_hi = L, 2 * L

    def store(addr: int, val: V, perf_lab, ptr_dep: FrozenSet):
        addr &= 0xFF
        if ev is not None:
            ev.append(("S", addr))
        M[addr] = V(val.v, val.lab, val.addr | ptr_dep)
        if nb_lo <= addr < nb_hi:
            recs[addr - L] = {"written": True, "ctrl": pcl, "addr": M[addr].addr, "exec": ex,
                              "performer": frozenset(b for b in bases(perf_lab) if b[0] == "E"), "step": steps}

    while steps < budget:
        op = M[pc].v
        steps += 1
        if ev is not None:
            ev.append(("F", pc, op if op in vm.OPLEN else "U"))
        n = vm.OPLEN.get(op, 0)
        opl = M[pc].lab
        ex = ex | M[pc].dep()
        argV = M[(pc + 1) & 0xFF] if n else None
        if n:
            ex = ex | argV.dep()
        arg = argV.v if n else 0
        npc = (pc + 1 + n) & 0xFF
        if op == vm.HALT:
            halted = True; break
        elif op in (vm.LD_A_n, vm.LD_B_n, vm.LD_C_n, vm.LD_D_n, vm.LD_S_n, vm.LD_T_n):
            reg = {vm.LD_A_n: "A", vm.LD_B_n: "B", vm.LD_C_n: "C", vm.LD_D_n: "D", vm.LD_S_n: "S", vm.LD_T_n: "T"}[op]
            R[reg] = V(arg, argV.lab, argV.addr)
        elif op in (vm.LD_A_pS, vm.LD_A_pT):
            P = R["S" if op == vm.LD_A_pS else "T"]; src = M[P.v]
            if ev is not None: ev.append(("L", P.v))
            R["A"] = V(src.v, src.lab, src.addr | P.dep())
        elif op in (vm.LD_pT_A, vm.LD_pS_A):
            P = R["T" if op == vm.LD_pT_A else "S"]
            store(P.v, R["A"], opl, P.dep())
        elif op == vm.LDI:
            S_, T_ = R["S"], R["T"]; src = M[S_.v]
            if ev is not None: ev.append(("L", S_.v))
            if nb_lo <= S_.v < nb_hi: flags["in_window_source"] = True
            store(T_.v, V(src.v, src.lab, src.addr | S_.dep()), opl, T_.dep())
            R["S"] = V(S_.v + 1, computed_from(S_.lab), S_.addr); R["T"] = V(T_.v + 1, computed_from(T_.lab), T_.addr)
            R["C"] = V(R["C"].v - 1, computed_from(R["C"].lab), R["C"].addr)
        elif op == vm.LDIR:
            if R["C"].v == 0: flags["ldir_c0_entered"] = True
            while True:
                S_, T_ = R["S"], R["T"]; src = M[S_.v]
                if ev is not None: ev.append(("L", S_.v))
                if nb_lo <= S_.v < nb_hi: flags["in_window_source"] = True
                store(T_.v, V(src.v, src.lab, src.addr | S_.dep()), opl, T_.dep())
                R["S"] = V(S_.v + 1, computed_from(S_.lab), S_.addr); R["T"] = V(T_.v + 1, computed_from(T_.lab), T_.addr)
                R["C"] = V(R["C"].v - 1, computed_from(R["C"].lab), R["C"].addr)
                steps += 1
                pcl = pcl | R["C"].dep()                        # `C == 0 or steps >= budget`: the C test is ALWAYS evaluated
                if R["C"].v == 0:
                    break
                if steps >= budget:
                    flags["budget_ended"] = True; break          # the budget is CONSTANT: no label
        elif op == vm.COPYALL and allow_copyall:
            S_, T_ = R["S"], R["T"]
            for i in range(L):
                src = M[(S_.v + i) & 0xFF]
                if ev is not None: ev.append(("L", (S_.v + i) & 0xFF))
                if nb_lo <= (S_.v + i) & 0xFF < nb_hi: flags["in_window_source"] = True
                store((T_.v + i) & 0xFF, V(src.v, src.lab, src.addr | S_.dep()), opl, T_.dep())
            steps += L // 8
        elif op in (vm.ADD_A_B, vm.XOR_A_B, vm.AND_A_B, vm.OR_A_B):
            a, b = R["A"], R["B"]
            v = {vm.ADD_A_B: a.v + b.v, vm.XOR_A_B: a.v ^ b.v, vm.AND_A_B: a.v & b.v, vm.OR_A_B: a.v | b.v}[op]
            R["A"] = V(v, computed(a.lab, b.lab), a.addr | b.addr); Z = V(int(R["A"].v == 0), R["A"].lab, R["A"].addr)
        elif op == vm.SUB_A_B:
            a, b = R["A"], R["B"]; lab = computed(a.lab, b.lab); ad = a.addr | b.addr
            CF = V(int(a.v < b.v), lab, ad); R["A"] = V(a.v - b.v, lab, ad); Z = V(int(R["A"].v == 0), lab, ad)
        elif op in (vm.INC_A, vm.DEC_A):
            a = R["A"]; R["A"] = V(a.v + (1 if op == vm.INC_A else -1), computed_from(a.lab), a.addr)
            Z = V(int(R["A"].v == 0), R["A"].lab, R["A"].addr)
        elif op in (vm.INC_S, vm.INC_T):
            r = "S" if op == vm.INC_S else "T"; x = R[r]; R[r] = V(x.v + 1, computed_from(x.lab), x.addr)
        elif op == vm.ADD_A_n:
            a = R["A"]; R["A"] = V(a.v + arg, computed(a.lab, argV.lab), a.addr | argV.addr)
            Z = V(int(R["A"].v == 0), R["A"].lab, R["A"].addr)
        elif op in (vm.SHL_A, vm.SHR_A):
            a = R["A"]; lab = computed(a.lab)
            CF = V(int(bool(a.v & 0x80)) if op == vm.SHL_A else int(bool(a.v & 1)), lab, a.addr)
            R["A"] = V((a.v << 1) if op == vm.SHL_A else (a.v >> 1), lab, a.addr); Z = V(int(R["A"].v == 0), lab, a.addr)
        elif op in (vm.INC_C, vm.DEC_C):
            c = R["C"]; R["C"] = V(c.v + (1 if op == vm.INC_C else -1), computed_from(c.lab), c.addr)
            Z = V(int(R["C"].v == 0), R["C"].lab, R["C"].addr)
        elif op in (vm.CP_A_n, vm.CP_A_B):
            a = R["A"]; o = argV if op == vm.CP_A_n else R["B"]
            lab = computed(a.lab, o.lab); ad = a.addr | o.addr
            Z = V(int(a.v == o.v), lab, ad); CF = V(int(a.v < o.v), lab, ad)
        elif op == vm.JP_n:
            npc = arg
        elif op in (vm.JZ_n, vm.JNZ_n, vm.JC_n):
            f = CF if op == vm.JC_n else Z
            pcl = pcl | f.dep()
            take = (f.v == 1) if op != vm.JNZ_n else (f.v == 0)
            if take: npc = arg
        elif op == vm.JR_d:
            d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == vm.DJNZ_d:
            b = R["B"]; R["B"] = V(b.v - 1, computed_from(b.lab), b.addr)
            pcl = pcl | R["B"].dep()
            if R["B"].v != 0:
                d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == vm.IN_A:
            if ip < 16:
                src = M[(vm.IN_BASE + ip) & 0xFF]; R["A"] = V(src.v, src.lab, src.addr | pcl)
                if ev is not None: ev.append(("L", (vm.IN_BASE + ip) & 0xFF))
            else:
                R["A"] = V(0, EXHAUSTED, pcl)
            ip += 1
        elif op == vm.OUT_A:
            if len(outputs) < 16:
                if ev is not None: ev.append(("S", vm.OUT_BASE + len(outputs)))
                a = R["A"]; M[vm.OUT_BASE + len(outputs)] = V(a.v, a.lab, a.addr | pcl); outputs.append(a.v)
        elif op in (vm.LD_B_A, vm.LD_A_B, vm.LD_C_A, vm.LD_A_C, vm.LD_S_A, vm.LD_T_A, vm.LD_A_S, vm.LD_A_T, vm.LD_D_A, vm.LD_A_D):
            dst, src = {vm.LD_B_A: "BA", vm.LD_A_B: "AB", vm.LD_C_A: "CA", vm.LD_A_C: "AC", vm.LD_S_A: "SA", vm.LD_T_A: "TA",
                        vm.LD_A_S: "AS", vm.LD_A_T: "AT", vm.LD_D_A: "DA", vm.LD_A_D: "AD"}[op]
            x = R[src]; R[dst] = V(x.v, x.lab, x.addr)
        elif op == vm.SWAP_A_B:
            R["A"], R["B"] = R["B"], R["A"]
        pc = npc
    if steps >= budget and not halted:
        flags["budget_ended"] = True
    after = bytearray(x.v for x in M)
    out_recs: Dict[int, dict] = {}
    for i in range(L):
        r = recs.get(i) or {"written": False, "ctrl": EMPTY, "addr": EMPTY, "exec": EMPTY, "performer": EMPTY, "step": None}
        out_recs[i] = dict(r, data=M[L + i].lab)
    info = {"steps": steps, "halted": halted, "outputs": outputs, "exec_whole": ex, "pc_label_end": pcl, **flags}
    if check:
        mm = bytearray(mem)
        tr = vm.execute(mm, L, 0, budget, list(inputs), allow_copyall=allow_copyall)
        if mm != after or tr.outputs != outputs or tr.halted != halted or tr.steps != steps:
            raise AssertionError("shadow tracer diverged from the frozen VM (memory %s, outputs %s, halted %s, steps %s/%s)"
                                 % (mm == after, tr.outputs == outputs, tr.halted == halted, tr.steps, steps))
    info["labels_after"] = [x.lab for x in M]
    info["addr_after"] = [x.addr for x in M]
    return after, out_recs, info


def identified_rule(rec: dict) -> bool:
    """v4 s2.1 RULE identification (used by the v4 fixture pack): the data label is an ENTITY, and ctrl/addr/exec hold no
    FOREIGN-INFORMATIVE label (INPUT) and no ENTITY other than {the data-label entity, the performer entity}."""
    d = rec["data"]
    if d[0] != "E":
        return False
    allowed = {d[1]} | {b[1] for b in rec["performer"]}
    for s in (rec["ctrl"], rec["addr"], rec["exec"]):
        for b in s:
            if b[0] == "INPUT" or (b[0] == "E" and b[1] not in allowed):
                return False
    return True
