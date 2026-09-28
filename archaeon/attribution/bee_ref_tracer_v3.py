# SUPERSEDED 2026-09-28: prereg v3 version (r004041 world), kept as history; see bee_ref_tracer.py (v4).
"""Archaeon's INDEPENDENT reference shadow tracer for BEE's frozen VM (git 16fc6c2a prometheus/z80atlas/vm.py), implementing
ANCESTRY_PREREG_v3 s1.

Purposes:
- the fixture pack's expected label vectors (each also validated by the per-byte flip test on the frozen VM);
- the independent 1% per-locus agreement check on the owner's production export (prereg v3 s0);
- the s4.2 provenance tests.

The tracer re-implements the frozen execute() step for step. On every run it asserts that its memory equals what the frozen
vm.execute produces from the same state (value check). Only the labels are this module's.

Labels (tuples):
  ("E", ent, locus)                 entity material; ent is an entity id (e.g. "W" writer, "P" partner/occupant)
  ("INPUT", k) / ("OTHER", addr)    input byte k / other memory at addr
  ("RESET", reg)                    register or flag at execution start
  ("COMPUTED", frozenset(bases))    multi-input or non-bijective computation (flattened)
  ("COMPUTED_FROM", frozenset(bases)) single-register, no-operand bijective op (INC/DEC)
  ("CONSTANT", frozenset(bases))    result independent of operands; bases = the instruction byte's labels
Per child locus the tracer returns: data label, ctrl_deps (whole-execution scope, every conditional EVALUATED), addr_deps,
exec_deps (every fetched opcode or operand byte), performer (the STORE instruction's opcode-byte material), written flag.
Not implemented here: post-dominator-scoped ctrl_deps (the prereg's secondary scope); owners report it.
"""
from __future__ import annotations

import importlib.util
import os
import random
import subprocess
import sys

_VM = None


def vm16():
    """the frozen VM module, loaded from git 16fc6c2a (the repo must contain that commit)."""
    global _VM
    if _VM is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_vm16_frozen.py")
        if not os.path.exists(path):
            src = subprocess.run(["git", "show", "16fc6c2a:prometheus/z80atlas/vm.py"], capture_output=True, text=True, check=True).stdout
            open(path, "w", encoding="utf-8", newline="\n").write(src)
        sp = importlib.util.spec_from_file_location("bee_vm16", path); m = importlib.util.module_from_spec(sp)
        sys.modules["bee_vm16"] = m; sp.loader.exec_module(m)
        _VM = m
    return _VM


def base(l):
    return set(l[1]) if l[0] in ("COMPUTED", "COMPUTED_FROM", "CONSTANT") else {l}


def comp(*ls):
    s = set()
    for l in ls: s |= base(l)
    return ("COMPUTED", frozenset(s))


def cfrom(l):
    return ("COMPUTED_FROM", frozenset(base(l)))


def ents(s):
    return {b[1] for b in s if b[0] == "E"}


def start_labels(L, ents_by_region=None):
    """default start labels: [0,L) writer W, [L,2L) occupant P, input region INPUT, else OTHER."""
    V = vm16(); lab = {}
    for a in range(256):
        if a < L: lab[a] = ("E", "W", a)
        elif a < 2 * L: lab[a] = ("E", "P", a - L)
        elif V.IN_BASE <= a < V.IN_BASE + 16: lab[a] = ("INPUT", a - V.IN_BASE)
        else: lab[a] = ("OTHER", a)
    return lab


def trace(mem0, L, entry, budget, inputs, allow_copyall=False, region=None, lab0=None, bug=None, ctrl0=None, exec0=None, rec0=None,
          check=True):
    """returns (final memory, per-window-locus records, trace summary). mem0 is not modified. bug: None or a mutant name
    ('loc0', 'reverse', 'memmove', 'ptrlabel', 'noexec', 'noctrl_untaken') for mutation testing of the fixture pack."""
    V = vm16(); mem = bytearray(mem0); lab = dict(lab0 or start_labels(L))
    R = {r: ("RESET", r) for r in ("A", "B", "C", "D", "S", "T", "Z", "CF")}
    RA = {r: set() for r in ("A", "B", "C", "D", "S", "T")}           # address labels of the load that produced a register value
    A = B = C = D = S = T = 0; Z = False; CF = False
    pc = entry & 0xFF; steps = 0; ip = 0; outs = 0
    lo, hi = (region if region else (0, 256))
    ctrl = set(ctrl0 or ()); execd = set(exec0 or ()); fetched = set()
    rec = dict(rec0 or {})                                            # window locus -> dict at last write

    def W(addr, v, l, ad, store_pc):
        addr &= 0xFF; mem[addr] = v & 0xFF; lab[addr] = l
        if L <= addr < 2 * L:
            rec[addr - L] = {"data": l, "ctrl": set(ctrl), "addr": set(ad), "exec": set(execd), "performer": frozenset(base(lab_at_fetch[store_pc]))}

    lab_at_fetch = {}
    while steps < budget:
        if not (lo <= pc < hi): break
        op = mem[pc]; steps += 1; n = V.OPLEN.get(op, 0)
        arg = mem[(pc + 1) & 0xFF] if n else 0; al = lab[(pc + 1) & 0xFF]
        npc = (pc + 1 + n) & 0xFF
        lab_at_fetch[pc] = lab[pc]
        if bug != "noexec":
            execd |= base(lab[pc]); fetched.add(pc)
            if n: execd |= base(al); fetched.add((pc + 1) & 0xFF)
        if op == V.HALT: break
        elif op in (V.LD_A_n, V.LD_B_n, V.LD_C_n, V.LD_D_n, V.LD_S_n, V.LD_T_n):
            r = {V.LD_A_n: "A", V.LD_B_n: "B", V.LD_C_n: "C", V.LD_D_n: "D", V.LD_S_n: "S", V.LD_T_n: "T"}[op]
            if r == "A": A = arg
            elif r == "B": B = arg
            elif r == "C": C = arg
            elif r == "D": D = arg
            elif r == "S": S = arg
            else: T = arg
            R[r] = al; RA[r] = set()
        elif op == V.LD_A_pS: A = mem[S]; R["A"] = lab[S]; RA["A"] = base(R["S"])
        elif op == V.LD_A_pT: A = mem[T]; R["A"] = lab[T]; RA["A"] = base(R["T"])
        elif op in (V.LD_pT_A, V.LD_pS_A):
            p = "T" if op == V.LD_pT_A else "S"; ptr = T if p == "T" else S
            l = R["A"] if bug != "ptrlabel" else R[p]
            W(ptr, A, l, base(R[p]) | RA["A"], pc)
        elif op in (V.LDI, V.LDIR):
            while True:
                W(T, mem[S], lab[S], base(R["S"]) | base(R["T"]), pc)
                S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
                R["S"] = cfrom(R["S"]); R["T"] = cfrom(R["T"]); R["C"] = cfrom(R["C"])
                if op == V.LDI: break
                steps += 1
                ctrl |= base(R["C"])                                  # the C==0 exit is evaluated every iteration
                if C == 0 or steps >= budget: break
        elif op == V.COPYALL and allow_copyall:
            if bug == "memmove":                                          # mutant: labels snapshotted (values stay sequential)
                snap = [lab[(S + i) & 0xFF] for i in range(L)]
                for i in range(L): W((T + i) & 0xFF, mem[(S + i) & 0xFF], snap[i], base(R["S"]) | base(R["T"]), pc)
            else:
                for i in range(L): W((T + i) & 0xFF, mem[(S + i) & 0xFF], lab[(S + i) & 0xFF], base(R["S"]) | base(R["T"]), pc)
            steps += L // 8
        elif op in (V.ADD_A_B, V.SUB_A_B, V.XOR_A_B, V.AND_A_B, V.OR_A_B):
            if op == V.ADD_A_B: A = (A + B) & 0xFF
            elif op == V.SUB_A_B: CF = A < B; A = (A - B) & 0xFF; R["CF"] = comp(R["A"], R["B"])
            elif op == V.XOR_A_B: A ^= B
            elif op == V.AND_A_B: A &= B
            else: A |= B
            Z = A == 0; R["A"] = comp(R["A"], R["B"]); R["Z"] = R["A"]; RA["A"] = set()
        elif op in (V.INC_A, V.DEC_A):
            A = (A + (1 if op == V.INC_A else -1)) & 0xFF; Z = A == 0; R["A"] = cfrom(R["A"]); R["Z"] = R["A"]
        elif op == V.INC_S: S = (S + 1) & 0xFF; R["S"] = cfrom(R["S"])
        elif op == V.INC_T: T = (T + 1) & 0xFF; R["T"] = cfrom(R["T"])
        elif op in (V.INC_C, V.DEC_C):
            C = (C + (1 if op == V.INC_C else -1)) & 0xFF; Z = C == 0; R["C"] = cfrom(R["C"]); R["Z"] = R["C"]
        elif op == V.ADD_A_n: A = (A + arg) & 0xFF; Z = A == 0; R["A"] = comp(R["A"], al); R["Z"] = R["A"]; RA["A"] = set()
        elif op in (V.SHL_A, V.SHR_A):
            CF = bool(A & 0x80) if op == V.SHL_A else bool(A & 1)
            A = (A << 1) & 0xFF if op == V.SHL_A else A >> 1
            Z = A == 0; R["A"] = comp(R["A"]); R["Z"] = R["A"]; R["CF"] = R["A"]; RA["A"] = set()
        elif op == V.CP_A_n: Z = A == arg; CF = A < arg; R["Z"] = R["CF"] = comp(R["A"], al)
        elif op == V.CP_A_B: Z = A == B; CF = A < B; R["Z"] = R["CF"] = comp(R["A"], R["B"])
        elif op == V.JP_n: npc = arg
        elif op in (V.JZ_n, V.JNZ_n, V.JC_n):
            take = Z if op == V.JZ_n else ((not Z) if op == V.JNZ_n else CF)
            if bug != "noctrl_untaken" or take: ctrl |= base(R["CF"] if op == V.JC_n else R["Z"])
            if take: npc = arg
        elif op == V.JR_d:
            d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == V.DJNZ_d:
            B = (B - 1) & 0xFF; R["B"] = cfrom(R["B"])
            if bug != "noctrl_untaken" or B != 0: ctrl |= base(R["B"])
            if B != 0:
                d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == V.IN_A:
            if ip < 16: A = mem[(V.IN_BASE + ip) & 0xFF]; R["A"] = lab[(V.IN_BASE + ip) & 0xFF]
            else: A = 0; R["A"] = ("CONSTANT", frozenset(base(lab[pc])))
            RA["A"] = set(); ip += 1
        elif op == V.OUT_A:
            if outs < 16: mem[V.OUT_BASE + outs] = A; lab[V.OUT_BASE + outs] = R["A"]; outs += 1
        elif op in (V.LD_B_A, V.LD_A_B, V.LD_C_A, V.LD_A_C, V.LD_S_A, V.LD_T_A, V.LD_A_S, V.LD_A_T, V.LD_D_A, V.LD_A_D, V.SWAP_A_B):
            if op == V.LD_B_A: B = A; R["B"] = R["A"]; RA["B"] = set(RA["A"])
            elif op == V.LD_A_B: A = B; R["A"] = R["B"]; RA["A"] = set(RA["B"])
            elif op == V.LD_C_A: C = A; R["C"] = R["A"]
            elif op == V.LD_A_C: A = C; R["A"] = R["C"]; RA["A"] = set()
            elif op == V.LD_S_A: S = A; R["S"] = R["A"]
            elif op == V.LD_T_A: T = A; R["T"] = R["A"]
            elif op == V.LD_A_S: A = S; R["A"] = R["S"]; RA["A"] = set()
            elif op == V.LD_A_T: A = T; R["A"] = R["T"]; RA["A"] = set()
            elif op == V.LD_D_A: D = A; R["D"] = R["A"]
            elif op == V.LD_A_D: A = D; R["A"] = R["D"]; RA["A"] = set()
            else: A, B = B, A; R["A"], R["B"] = R["B"], R["A"]; RA["A"], RA["B"] = RA["B"], RA["A"]
        pc = npc
    if check:                                                         # value check against the frozen VM
        m2 = bytearray(mem0); V.execute(m2, L, entry, budget, list(inputs), region=region, allow_copyall=allow_copyall)
        assert bytes(m2) == bytes(mem), "reference tracer diverged from the frozen VM"
    if rec0 is not None or ctrl0 is not None:                         # continuation call (SEPARATED second half): raw state
        return bytes(mem), {"rec": rec, "lab": lab, "ctrl": ctrl, "exec": execd, "fetched": fetched}, {"steps": steps}
    out = {}
    for i in range(L):
        if i in rec:
            r = dict(rec[i]); r["written"] = True
        else:
            r = {"data": lab[L + i], "ctrl": set(ctrl), "addr": set(), "exec": set(execd),
                 "performer": frozenset(), "written": False}
        d = r["data"]
        if bug == "loc0" and d[0] == "E" and d[1] == "W": r["data"] = ("E", "W", 0)
        if bug == "reverse" and d[0] == "E" and d[1] == "W": r["data"] = ("E", "W", L - 1 - d[2])
        out[i] = r
    return bytes(mem), out, {"steps": steps, "fetched": fetched}


def identified(r, performer_exempt=True):
    """rule-identified (prereg v3 s2.1, with Amendment A2: the performer's entity is exempt in the dependence sets)."""
    d = r["data"]
    if d[0] != "E": return False
    allowed = {d}
    ok_ents = {d[1]} | (ents(r["performer"]) if performer_exempt else set())
    for s in (r["ctrl"], r["addr"], r["exec"]):
        for b in s:
            if b[0] == "E" and b[1] in ok_ents: continue
            if b in allowed: continue
            return False
    return True


# ---------------------------------------------------------------- world-level execution (frozen world.py _execute)
def world_cfg(cfg):
    """from a BEE run config dict: L, layout, budget, allow_copyall (frozen world.py semantics)."""
    return {"L": 32 if cfg["representation"] == "BYTECODE32" else 64, "layout": cfg["layout"], "budget": cfg["budget"],
            "allow_copyall": cfg["representation"] == "VM_COPY"}


def vm_world(mem, w, inputs):
    """value execution exactly as world._execute (SHARED or SEPARATED); mem modified in place."""
    V = vm16(); L = w["L"]
    if w["layout"] == "SEPARATED":
        V.execute(mem, L, 0, w["budget"] // 2, list(inputs), region=(0, L // 2), allow_copyall=w["allow_copyall"])
        V.execute(mem, L, L // 2, w["budget"] // 2, list(inputs), region=(L // 2, L), allow_copyall=w["allow_copyall"])
    else:
        V.execute(mem, L, 0, w["budget"], list(inputs), allow_copyall=w["allow_copyall"])
    return mem


def trace_world(mem0, w, inputs, bug=None, lab0=None):
    """labels for one world execution. Returns (final memory, per-window-locus records, info with the fetched addresses)."""
    L = w["L"]; lab = dict(lab0 or start_labels(L))
    if w["layout"] == "SEPARATED":
        m1, st1, _ = trace(mem0, L, 0, w["budget"] // 2, inputs, w["allow_copyall"], (0, L // 2), lab, bug, ctrl0=set(), exec0=set(),
                           rec0={}, check=False)
        m2, st2, _ = trace(m1, L, L // 2, w["budget"] // 2, inputs, w["allow_copyall"], (L // 2, L), st1["lab"], bug, ctrl0=st1["ctrl"],
                           exec0=st1["exec"], rec0=st1["rec"], check=False)
        fetched = st1["fetched"] | st2["fetched"]; st = st2
    else:
        m2, st, _ = trace(mem0, L, 0, w["budget"], inputs, w["allow_copyall"], None, lab, bug, ctrl0=set(), exec0=set(), rec0={}, check=False)
        fetched = st["fetched"]
    ref = vm_world(bytearray(mem0), w, inputs)
    assert bytes(ref) == bytes(m2), "reference tracer diverged from the frozen world execution"
    out = {}
    for i in range(L):
        if i in st["rec"]: r = dict(st["rec"][i]); r["written"] = True
        else: r = {"data": st["lab"][L + i], "ctrl": set(st["ctrl"]), "addr": set(), "exec": set(st["exec"]), "performer": frozenset(), "written": False}
        d = r["data"]
        if bug == "loc0" and d[0] == "E" and d[1] == "W": r["data"] = ("E", "W", 0)
        if bug == "reverse" and d[0] == "E" and d[1] == "W": r["data"] = ("E", "W", L - 1 - d[2])
        out[i] = r
    return bytes(m2), out, {"fetched": fetched}


# ---------------------------------------------------------------- provenance tests (s4.2)
def addr_of(label, L):
    V = vm16()
    if label[0] == "E": return label[2] if label[1] == "W" else L + label[2]
    if label[0] == "INPUT": return V.IN_BASE + label[1]
    return None


def flip_test(mem0, w, inputs, recs=None, fetched=None, bit=0):
    """per-byte where-provenance (prereg v3 s4.2): for each WRITTEN locus with an E label whose source byte was NOT fetched as an
    instruction, flip one bit of the source byte in the pre-execution memory; the child locus must take the flipped value."""
    L = w["L"]
    if recs is None: _, recs, info = trace_world(mem0, w, inputs); fetched = info["fetched"]
    ok = n = skipped = 0; fails = []
    for i, r in recs.items():
        d = r["data"]
        if not r["written"] or d[0] != "E": continue
        a = addr_of(d, L)
        if a is None or a in fetched: skipped += 1; continue
        m = bytearray(mem0); m[a] ^= (1 << bit)
        m2 = vm_world(bytearray(m), w, inputs)
        n += 1
        if m2[L + i] == m[a]: ok += 1
        else: fails.append(i)
    return {"tested": n, "pass": ok, "skipped_code_and_data": skipped, "fails": fails}


def completeness(mem0, w, inputs, recs=None, fetched=None, draws=3, seed=0):
    """entity arms: randomise the writer's / occupant's non-executed bytes, their executed bytes, and the input region; every
    child locus that changes must name the randomised source in data / ctrl / addr / exec."""
    V = vm16(); rng = random.Random(seed); L = w["L"]
    if recs is None: _, recs, info = trace_world(mem0, w, inputs); fetched = info["fetched"]
    base_child = bytes(vm_world(bytearray(mem0), w, inputs)[L:2 * L])
    arms = {"W_data": [a for a in range(L) if a not in fetched], "W_exec": [a for a in range(L) if a in fetched],
            "P_data": [a for a in range(L, 2 * L) if a not in fetched], "P_exec": [a for a in range(L, 2 * L) if a in fetched],
            "INPUT": list(range(V.IN_BASE, V.IN_BASE + 16))}
    res = {}
    for arm, addrs in arms.items():
        changed = set()
        if addrs:
            for _ in range(draws):
                m = bytearray(mem0)
                for a in addrs: m[a] = rng.randrange(256)
                inp = list(m[V.IN_BASE:V.IN_BASE + len(inputs)]) if arm == "INPUT" else list(inputs)
                vm_world(m, w, inp)
                changed |= {i for i in range(L) if m[L + i] != base_child[i]}
        src = "INPUT" if arm == "INPUT" else arm[0]
        def names(r):
            allb = base(r["data"]) | r["ctrl"] | r["addr"] | r["exec"]
            return any((b[0] == "INPUT") if src == "INPUT" else (b[0] == "E" and b[1] == src) for b in allb)
        res[arm] = {"changed": len(changed), "named": sum(1 for i in changed if names(recs[i])), "unnamed_loci": sorted(i for i in changed if not names(recs[i]))}
    return res
