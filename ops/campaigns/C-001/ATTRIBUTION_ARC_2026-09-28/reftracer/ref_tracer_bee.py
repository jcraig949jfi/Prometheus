"""REFERENCE shadow tracer for BEE (z80atlas frozen VM, git 16fc6c2a), per ANCESTRY_PREREG_v4 s1, s2.1-2.2, s4.1.

Written from the prereg text alone (plus the frozen vm.py / world.py _execute). Every interpretive choice is marked
"CHOICE <n>" and listed in SPEC_ISSUES.md under the same number.

World supported: r025144 (VM_COPY -> COPYALL enabled, L=64, SHARED, one vm.execute per interaction, budget 256, entry 0).

Label representation (hashable tuples):
    ("ENTITY", role, locus, orig_id)     role "w" = executing organism, "o" = occupant/partner
    ("INPUT", k)
    ("CONSTANT", kind)                   kind in reset | scratch | empty | in_exhausted | idiom | computed
    ("COMPUTED", frozenset(base labels)) CONSTANT bases dropped
    ("COMPUTED_FROM", label)             INC/DEC of a non-CONSTANT, non-COMPUTED label
Base labels of a label: ENTITY/INPUT -> {itself}; CONSTANT -> {} (CHOICE 3); COMPUTED(s) -> s; COMPUTED_FROM(x) -> base(x).

Every value (register, flag, memory byte) carries (label, addr) where addr is the set of base labels of every pointer used by
a load/store that contributed to the value (s1.3 addr_deps).

Public API:
    trace_interaction(pre_mem, inputs, cfg, pre_labels=None) -> Result   (asserts equality with frozen vm.execute)
    flip_test(pre_mem, inputs, cfg, locus, result=None) -> dict          (s4.1, one window locus)
    flip_test_all(pre_mem, inputs, cfg, result=None) -> {locus: dict}
    make_pre_mem(w_tape, o_tape_or_None, inputs, L) -> bytearray         (world.py _execute layout)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN_VM_PATH = os.path.join(HERE, "frozen_vm_16fc6c2a.py")      # `git show 16fc6c2a:prometheus/z80atlas/vm.py`
FROZEN_VM_SHA256_PREFIX = "2536b1ac"


def _load_frozen_vm():
    with open(FROZEN_VM_PATH, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    assert sha.startswith(FROZEN_VM_SHA256_PREFIX), "frozen vm.py pin mismatch: %s" % sha
    spec = importlib.util.spec_from_file_location("bee_frozen_vm_16fc6c2a", FROZEN_VM_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod                                  # dataclasses needs the module registered
    spec.loader.exec_module(mod)
    return mod


vm = _load_frozen_vm()
SPACE, IN_BASE, OUT_BASE = vm.SPACE, vm.IN_BASE, vm.OUT_BASE


# ---- config -------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Cfg:
    L: int = 64
    budget: int = 256
    allow_copyall: bool = True
    entry: int = 0

    @staticmethod
    def from_run_config(path: str) -> "Cfg":
        with open(path) as f:
            d = json.load(f)
        c = d["config"]
        assert c["layout"] == "SHARED", "only the SHARED layout (one vm.execute per interaction) is supported"
        assert c["reproduction"] != "PAIR_EXECUTION"
        L = 32 if c["representation"] == "BYTECODE32" else 64               # world.py Config.L
        return Cfg(L=L, budget=c["budget"], allow_copyall=c["representation"] == "VM_COPY", entry=0)


def make_pre_mem(w_tape: bytes, o_tape: Optional[bytes], inputs: List[int], L: int = 64) -> bytearray:
    """world.py _execute: own tape at [0,L), partner at [L,2L) (zeros if EMPTY), inputs[:16] at IN_BASE, zero elsewhere."""
    mem = bytearray(SPACE)
    mem[:L] = bytes(w_tape)[:L]
    if o_tape is not None:
        mem[L:2 * L] = bytes(o_tape)[:L]
    for k, v in enumerate(inputs[:16]):
        mem[IN_BASE + k] = v
    return mem


# ---- labels -------------------------------------------------------------------------------------------------------------
def C(kind: str):
    return ("CONSTANT", kind)


RESET = C("reset")


def base(label) -> FrozenSet:
    t = label[0]
    if t == "CONSTANT":
        return frozenset()                                    # CHOICE 3: structural labels are not dependence members
    if t == "COMPUTED":
        return label[1]
    if t == "COMPUTED_FROM":
        return base(label[1])
    return frozenset([label])                                 # ENTITY, INPUT (OTHER/ENV/MUTATION would go here too)


def is_move_label(label) -> bool:
    return label[0] in ("ENTITY", "INPUT")


@dataclass(frozen=True)
class V:
    label: tuple
    addr: FrozenSet = frozenset()

    def deps(self) -> FrozenSet:
        """Full dependence of the value: its data-label bases plus the pointer labels of its loads/stores. CHOICE 5."""
        return base(self.label) | self.addr


def v_unary_bij(x: V) -> V:
    """INC / DEC (register-only, no operand, bijective) -> COMPUTED_FROM(label). CHOICE 4 for CONSTANT / COMPUTED inputs."""
    lab = x.label
    if lab[0] == "CONSTANT":
        return V(C("computed"), x.addr)
    if lab[0] in ("COMPUTED", "COMPUTED_FROM"):
        return V(lab, x.addr)
    return V(("COMPUTED_FROM", lab), x.addr)


def v_compute(*xs: V) -> V:
    """Everything else that computes -> COMPUTED(flattened bases, CONSTANT dropped). All-CONSTANT -> CONSTANT computed (CHOICE 4)."""
    b = frozenset().union(*(base(x.label) for x in xs))
    a = frozenset().union(*(x.addr for x in xs))
    if not b:
        return V(C("computed"), a)
    return V(("COMPUTED", b), a)


def same_move_value(a: V, b: V) -> bool:
    """Two values carrying the identical ENTITY/INPUT MOVE label hold the same byte (each pre-state byte has a unique label
    and moves preserve value), so XOR/SUB/CP of them is result-independent (CHOICE 7)."""
    return a.label == b.label and is_move_label(a.label)


IDIOM = V(C("idiom"))


# ---- result -------------------------------------------------------------------------------------------------------------
@dataclass
class Locus:
    locus: int
    value: int
    label: tuple
    ctrl_deps: FrozenSet                  # whole-execution PC label (primary)
    addr_deps: FrozenSet
    exec_deps: FrozenSet                  # whole-execution fetched-byte labels (primary)
    performer: Optional[tuple]            # data label of the (last) store's opcode byte; None if never written
    written: bool
    ctrl_deps_at_store: Optional[FrozenSet] = None     # secondary diagnostic (PC label when the final store happened)
    exec_deps_at_store: Optional[FrozenSet] = None
    rule_identified: bool = False

    def entity(self) -> Optional[str]:
        return self.label[1] if self.label[0] == "ENTITY" else None


@dataclass
class Result:
    loci: List[Locus]
    final_mem: bytearray
    fetch_trace: List[Tuple[int, int]]            # (pc, opcode) per fetched instruction
    store_addrs: List[int]                        # every store incl. per-byte LDIR/COPYALL and OUT, in order
    load_addrs: List[int]
    ctrl_deps: FrozenSet
    exec_deps: FrozenSet
    structural_seen: FrozenSet                    # CONSTANT kinds met in conditions / fetches / pointers (reported only)
    halted: bool
    budget_end: bool                              # path ended at the step budget (flag, not label: s1.3)
    steps: int
    outputs: List[int]
    n_written: int
    birth: Optional[bool]                         # ENDOGENOUS_COPY: n_written >= L and child != occupant
    birth_existence_deps: FrozenSet
    mem_labels: List[V] = field(default_factory=list)


# ---- shadow execution ---------------------------------------------------------------------------------------------------
def initial_labels(L: int, n_inputs: int, occupant: bool, pre_labels: Optional[Dict[int, tuple]] = None,
                   w_orig: object = "w", o_orig: object = "o") -> List[V]:
    labs: List[V] = []
    for a in range(SPACE):
        if a < L:
            lab = ("ENTITY", "w", a, w_orig)
        elif a < 2 * L:
            lab = ("ENTITY", "o", a - L, o_orig) if occupant else C("empty")
        elif IN_BASE <= a < IN_BASE + min(n_inputs, 16):
            lab = ("INPUT", a - IN_BASE)
        else:
            lab = C("scratch")                     # incl. input-region bytes beyond len(inputs) (CHOICE 9)
        if pre_labels and a in pre_labels:
            lab = pre_labels[a]
        labs.append(V(lab))
    return labs


def trace_interaction(pre_mem: bytes, inputs: List[int], cfg: Cfg = Cfg(), occupant: bool = True,
                      pre_labels: Optional[Dict[int, tuple]] = None, w_orig: object = "w", o_orig: object = "o",
                      check: bool = True) -> Result:
    """Shadow-execute one SHARED interaction. `pre_mem` is the 256-byte memory as world._execute builds it.
    `occupant` False -> the window is EMPTY (CONSTANT empty). `pre_labels` optionally overrides initial labels per address
    (e.g. persisted orig_ids). Asserts that the final memory (and outputs/steps/halted/writes) equal the frozen VM's."""
    assert len(pre_mem) == SPACE
    L, budget = cfg.L, cfg.budget
    mem = bytearray(pre_mem)
    ml = initial_labels(L, len(inputs), occupant, pre_labels, w_orig, o_orig)
    performer: Dict[int, tuple] = {}
    store_ctrl: Dict[int, FrozenSet] = {}
    store_exec: Dict[int, FrozenSet] = {}
    writes: Dict[int, int] = {}                   # W() writes only (mirrors Trace.writes; OUT is not in it)

    R = {r: V(RESET) for r in "ABCDST"}
    Z = V(RESET); CF = V(RESET)
    pc = cfg.entry & 0xFF
    steps = 0; halted = False
    ip = 0; outputs: List[int] = []
    pcl: FrozenSet = frozenset()                  # PC label (never popped)
    exe: FrozenSet = frozenset()
    structural = set()
    fetch_trace: List[Tuple[int, int]] = []
    store_addrs: List[int] = []
    load_addrs: List[int] = []                    # data loads (not fetches); used only by the strict flip variant
    val = {r: 0 for r in "ABCDST"}; val["Z"] = False; val["CF"] = False

    def cond(x: V):
        nonlocal pcl
        pcl = pcl | x.deps()
        if x.label[0] == "CONSTANT":
            structural.add(x.label[1])

    def load(addr: int, ptr: FrozenSet) -> V:
        load_addrs.append(addr & 0xFF)
        m = ml[addr & 0xFF]
        return V(m.label, m.addr | ptr)

    def store(addr: int, value: int, v: V, ptr: FrozenSet, op_label: tuple, via_W: bool = True):
        addr &= 0xFF
        mem[addr] = value & 0xFF
        ml[addr] = V(v.label, v.addr | ptr)
        performer[addr] = op_label
        store_ctrl[addr] = pcl
        store_exec[addr] = exe
        store_addrs.append(addr)
        if via_W:
            writes[addr] = value & 0xFF

    def ptr_of(r: str) -> FrozenSet:
        if R[r].label[0] == "CONSTANT":
            structural.add(R[r].label[1])
        return R[r].deps()

    while steps < budget:                         # budget: CONSTANT "budget", recorded by flag (s1.3)
        # region exit (SHARED: region = whole space; condition input is pc, whose label is the PC label itself -> no-op)
        op = mem[pc]
        op_label = ml[pc].label
        exe = exe | ml[pc].deps()
        if op_label[0] == "CONSTANT":
            structural.add(op_label[1])
        fetch_trace.append((pc, op))
        steps += 1
        n = vm.OPLEN.get(op, 0)
        arg = mem[(pc + 1) & 0xFF] if n else 0
        argv = ml[(pc + 1) & 0xFF] if n else None
        if n:
            exe = exe | argv.deps()
        npc = (pc + 1 + n) & 0xFF

        if op == vm.HALT:
            halted = True; break
        elif op in (vm.LD_A_n, vm.LD_B_n, vm.LD_C_n, vm.LD_D_n, vm.LD_S_n, vm.LD_T_n):
            r = {vm.LD_A_n: "A", vm.LD_B_n: "B", vm.LD_C_n: "C", vm.LD_D_n: "D", vm.LD_S_n: "S", vm.LD_T_n: "T"}[op]
            val[r] = arg; R[r] = argv                                    # immediate used as value: operand byte's label
        elif op == vm.LD_A_pS:
            val["A"] = mem[val["S"]]; R["A"] = load(val["S"], ptr_of("S"))
        elif op == vm.LD_A_pT:
            val["A"] = mem[val["T"]]; R["A"] = load(val["T"], ptr_of("T"))
        elif op == vm.LD_pT_A:
            store(val["T"], val["A"], R["A"], ptr_of("T"), op_label)
        elif op == vm.LD_pS_A:
            store(val["S"], val["A"], R["A"], ptr_of("S"), op_label)
        elif op == vm.LDI:
            v = mem[val["S"]]; lv = load(val["S"], ptr_of("S"))
            store(val["T"], v, lv, ptr_of("T"), op_label)
            val["S"] = (val["S"] + 1) & 0xFF; val["T"] = (val["T"] + 1) & 0xFF; val["C"] = (val["C"] - 1) & 0xFF
            R["S"] = v_unary_bij(R["S"]); R["T"] = v_unary_bij(R["T"]); R["C"] = v_unary_bij(R["C"])
        elif op == vm.LDIR:
            while True:
                v = mem[val["S"]]; lv = load(val["S"], ptr_of("S"))
                store(val["T"], v, lv, ptr_of("T"), op_label)
                val["S"] = (val["S"] + 1) & 0xFF; val["T"] = (val["T"] + 1) & 0xFF; val["C"] = (val["C"] - 1) & 0xFF
                R["S"] = v_unary_bij(R["S"]); R["T"] = v_unary_bij(R["T"]); R["C"] = v_unary_bij(R["C"])
                steps += 1
                cond(R["C"])                                             # the C==0 exit (evaluated every iteration)
                if val["C"] == 0 or steps >= budget:                     # budget part: flag only
                    break
        elif op == vm.COPYALL and cfg.allow_copyall:
            pT = ptr_of("T"); pS = ptr_of("S")                           # T+i / S+i: pointer label = T's / S's (CHOICE 11)
            for i in range(L):
                a_src = (val["S"] + i) & 0xFF
                store((val["T"] + i) & 0xFF, mem[a_src], load(a_src, pS), pT, op_label)   # sequential: overlap chain
            steps += L // 8
        elif op in (vm.ADD_A_B, vm.SUB_A_B, vm.XOR_A_B, vm.AND_A_B, vm.OR_A_B):
            a, b = val["A"], val["B"]
            idiom = op in (vm.SUB_A_B, vm.XOR_A_B) and same_move_value(R["A"], R["B"])
            if op == vm.ADD_A_B: r = (a + b) & 0xFF
            elif op == vm.SUB_A_B:
                CF = IDIOM if idiom else v_compute(R["A"], R["B"]); val["CF"] = a < b; r = (a - b) & 0xFF
            elif op == vm.XOR_A_B: r = a ^ b
            elif op == vm.AND_A_B: r = a & b
            else: r = a | b
            val["A"] = r; val["Z"] = r == 0
            R["A"] = IDIOM if idiom else v_compute(R["A"], R["B"])
            Z = IDIOM if idiom else v_compute(R["A"])
        elif op in (vm.INC_A, vm.DEC_A):
            val["A"] = (val["A"] + (1 if op == vm.INC_A else -1)) & 0xFF
            R["A"] = v_unary_bij(R["A"]); Z = v_compute(R["A"]); val["Z"] = val["A"] == 0
        elif op == vm.INC_S:
            val["S"] = (val["S"] + 1) & 0xFF; R["S"] = v_unary_bij(R["S"])
        elif op == vm.INC_T:
            val["T"] = (val["T"] + 1) & 0xFF; R["T"] = v_unary_bij(R["T"])
        elif op == vm.ADD_A_n:
            val["A"] = (val["A"] + arg) & 0xFF; R["A"] = v_compute(R["A"], argv); Z = v_compute(R["A"]); val["Z"] = val["A"] == 0
        elif op in (vm.SHL_A, vm.SHR_A):
            a = val["A"]
            CF = v_compute(R["A"]); val["CF"] = bool(a & 0x80) if op == vm.SHL_A else bool(a & 1)
            val["A"] = ((a << 1) & 0xFF) if op == vm.SHL_A else (a >> 1)
            R["A"] = v_compute(R["A"]); Z = v_compute(R["A"]); val["Z"] = val["A"] == 0
        elif op in (vm.INC_C, vm.DEC_C):
            val["C"] = (val["C"] + (1 if op == vm.INC_C else -1)) & 0xFF
            R["C"] = v_unary_bij(R["C"]); Z = v_compute(R["C"]); val["Z"] = val["C"] == 0
        elif op == vm.CP_A_n:
            Z = v_compute(R["A"], argv); CF = Z; val["Z"] = val["A"] == arg; val["CF"] = val["A"] < arg
        elif op == vm.CP_A_B:
            if same_move_value(R["A"], R["B"]):
                Z = IDIOM; CF = IDIOM
            else:
                Z = v_compute(R["A"], R["B"]); CF = Z
            val["Z"] = val["A"] == val["B"]; val["CF"] = val["A"] < val["B"]
        elif op == vm.JP_n:
            npc = arg                                                    # target = operand byte: exec_deps
        elif op == vm.JZ_n:
            cond(Z)
            if val["Z"]: npc = arg
        elif op == vm.JNZ_n:
            cond(Z)
            if not val["Z"]: npc = arg
        elif op == vm.JC_n:
            cond(CF)
            if val["CF"]: npc = arg
        elif op == vm.JR_d:
            d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == vm.DJNZ_d:
            val["B"] = (val["B"] - 1) & 0xFF; R["B"] = v_unary_bij(R["B"])
            cond(R["B"])
            if val["B"] != 0:
                d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == vm.IN_A:
            # IN counter is a register whose label is the PC label at this IN (s1.2 hidden state); used as the pointer
            ctr = pcl
            if ip < 16:                                                   # guard input = IN counter -> PC label (no-op)
                a_in = (IN_BASE + ip) & 0xFF
                val["A"] = mem[a_in]; R["A"] = load(a_in, ctr)
            else:
                val["A"] = 0; R["A"] = V(C("in_exhausted"))
            ip += 1
        elif op == vm.OUT_A:
            ctr = pcl                                                     # OUT counter label; 16-output guard: cond on it
            if len(outputs) < 16:
                store(OUT_BASE + len(outputs), val["A"], R["A"], ctr, op_label, via_W=False)
                outputs.append(val["A"])
        elif op in (vm.LD_B_A, vm.LD_A_B, vm.LD_C_A, vm.LD_A_C, vm.LD_S_A, vm.LD_T_A, vm.LD_A_S, vm.LD_A_T, vm.LD_D_A,
                    vm.LD_A_D):
            dst, src = {vm.LD_B_A: ("B", "A"), vm.LD_A_B: ("A", "B"), vm.LD_C_A: ("C", "A"), vm.LD_A_C: ("A", "C"),
                        vm.LD_S_A: ("S", "A"), vm.LD_T_A: ("T", "A"), vm.LD_A_S: ("A", "S"), vm.LD_A_T: ("A", "T"),
                        vm.LD_D_A: ("D", "A"), vm.LD_A_D: ("A", "D")}[op]
            val[dst] = val[src]; R[dst] = R[src]
        elif op == vm.SWAP_A_B:
            val["A"], val["B"] = val["B"], val["A"]; R["A"], R["B"] = R["B"], R["A"]
        # else: undefined opcode (or COPYALL with copyall disabled) = NOP
        pc = npc

    budget_end = (not halted) and steps >= budget

    # ---- value check against the frozen VM --------------------------------------------------------------------------
    if check:
        ref = bytearray(pre_mem)
        tr = vm.execute(ref, L, cfg.entry, budget, list(inputs), allow_copyall=cfg.allow_copyall)
        assert ref == mem, "shadow final memory != frozen vm.execute memory"
        assert tr.outputs == outputs and tr.steps == steps and tr.halted == halted and tr.writes == writes, \
            "shadow trace != frozen vm trace"

    # ---- per-locus export ---------------------------------------------------------------------------------------------
    win_written = sorted({a for a in writes if L <= a < 2 * L})
    n_written = len(win_written)
    loci = []
    for j in range(L):
        a = L + j
        m = ml[a]
        w = a in writes
        loc = Locus(locus=j, value=mem[a], label=m.label, ctrl_deps=pcl, addr_deps=m.addr, exec_deps=exe,
                    performer=performer.get(a) if w else None, written=w,
                    ctrl_deps_at_store=store_ctrl.get(a) if w else None, exec_deps_at_store=store_exec.get(a) if w else None)
        loc.rule_identified = rule_identified(loc)
        loci.append(loc)

    child = bytes(mem[L:2 * L])
    birth = (n_written >= L) and (not occupant or child != bytes(pre_mem[L:2 * L]))
    # birth-existence: n_written >= L (which addresses got stored: store pointers + PC label) and child != occupant
    # (every child byte's dependence and every occupant byte). s1.3.
    bed = set(pcl)
    for a in win_written:
        bed |= ml[a].addr
    for j in range(L):
        bed |= ml[L + j].deps()
        if occupant:
            bed.add(("ENTITY", "o", j, o_orig))
    return Result(loci=loci, final_mem=mem, fetch_trace=fetch_trace, store_addrs=store_addrs, load_addrs=load_addrs, ctrl_deps=pcl, exec_deps=exe,
                  structural_seen=frozenset(structural), halted=halted, budget_end=budget_end, steps=steps, outputs=outputs,
                  n_written=n_written, birth=birth, birth_existence_deps=frozenset(bed), mem_labels=ml)


# ---- identification (s2.1) ------------------------------------------------------------------------------------------------
FOREIGN_INFORMATIVE = ("INPUT", "ENV", "OTHER")


def entity_of(label) -> Optional[str]:
    return label[1] if label and label[0] == "ENTITY" else None


def rule_identified(loc: Locus) -> bool:
    if loc.label[0] != "ENTITY":
        return False
    allowed = {loc.label[1]}
    pe = entity_of(loc.performer) if loc.performer else None
    if pe:
        allowed.add(pe)
    for s in (loc.ctrl_deps, loc.addr_deps, loc.exec_deps):
        for b in s:
            if b[0] in FOREIGN_INFORMATIVE:
                return False
            if b[0] == "ENTITY" and b[1] not in allowed:
                return False
    return True


# ---- s4.1 path-preserving flip test ----------------------------------------------------------------------------------------
def entity_addr(label, L: int) -> int:
    assert label[0] == "ENTITY"
    return label[2] if label[1] == "w" else L + label[2]


def flip_test(pre_mem: bytes, inputs: List[int], cfg: Cfg, locus: int, occupant: bool = True,
              result: Optional[Result] = None, strict_path: bool = False) -> dict:
    """One window locus. Applies to rule-identified loci whose data label is an ENTITY MOVE label (X, j). For each bit:
    flip bit of (X, j) in the pre-state, re-run (shadow, value-checked against the frozen VM); if the (pc, opcode) fetch
    trace and the store-address sequence are unchanged the child locus must equal pre[(X,j)] ^ bit.
    strict_path=True (NOT the v4 text; SPEC_ISSUES FLIP-1) also requires the data-load address sequence to be unchanged."""
    base_r = result or trace_interaction(pre_mem, inputs, cfg, occupant=occupant)
    loc = base_r.loci[locus]
    if not (loc.rule_identified and loc.label[0] == "ENTITY"):
        return {"locus": locus, "status": "NOT_APPLICABLE", "bits": []}
    src = entity_addr(loc.label, cfg.L)
    bits = []
    for b in range(8):
        m2 = bytearray(pre_mem); m2[src] ^= (1 << b)
        r2 = trace_interaction(bytes(m2), inputs, cfg, occupant=occupant)
        if r2.fetch_trace != base_r.fetch_trace or r2.store_addrs != base_r.store_addrs or \
                (strict_path and r2.load_addrs != base_r.load_addrs):
            bits.append("INAPPLICABLE"); continue
        predicted = pre_mem[src] ^ (1 << b)
        bits.append("CONFIRMED" if r2.final_mem[cfg.L + locus] == predicted else "FAILED")
    if "FAILED" in bits:
        status = "FAILED"
    elif "CONFIRMED" in bits:
        status = "CONFIRMED"
    else:
        status = "INAPPLICABLE"
    return {"locus": locus, "status": status, "bits": bits, "source": loc.label}


def flip_test_all(pre_mem: bytes, inputs: List[int], cfg: Cfg, occupant: bool = True, result: Optional[Result] = None,
                  written_only: bool = True, strict_path: bool = False) -> Dict[int, dict]:
    r = result or trace_interaction(pre_mem, inputs, cfg, occupant=occupant)
    out = {}
    for loc in r.loci:
        if written_only and not loc.written:
            continue
        if loc.rule_identified and loc.label[0] == "ENTITY":
            out[loc.locus] = flip_test(pre_mem, inputs, cfg, loc.locus, occupant, r, strict_path)
    return out


def fmt_label(lab) -> str:
    if lab is None:
        return "-"
    t = lab[0]
    if t == "ENTITY":
        return "%s%d" % (lab[1], lab[2])
    if t == "INPUT":
        return "in%d" % lab[1]
    if t == "CONSTANT":
        return "K:" + lab[1]
    if t == "COMPUTED":
        return "COMP{" + ",".join(sorted(fmt_label(x) for x in lab[1])) + "}"
    if t == "COMPUTED_FROM":
        return "CF(" + fmt_label(lab[1]) + ")"
    return str(lab)


def fmt_set(s) -> str:
    return "{" + ",".join(sorted(fmt_label(x) for x in s)) + "}"
