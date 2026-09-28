"""Archaeon's shadow tracer for BEE's frozen VM (git 16fc6c2a prometheus/z80atlas/vm.py), implementing ANCESTRY_PREREG_v4 s1-s2
and the s4 tests, for the SHARED layout (r025144's world).

Under v4 this is the SECOND implementation. The REFERENCE tracer is written by an isolated worker from the prereg text alone. The
v3 version is bee_ref_tracer_v3.py.

Labels (base labels are atomic):
- ("E", ent, locus)                    entity material (ent: "W" executing organism, "P" occupant)
- ("INPUT", k)                         FOREIGN-INFORMATIVE
- ("CONST", kind)                      FOREIGN-STRUCTURAL: fresh zero memory, RESET registers/flags, IN exhausted, computed from
                                       constants only
- ("COMPUTED", frozenset(bases))       flattened, CONST bases dropped
- ("COMPUTED_FROM", frozenset(bases))  INC/DEC of one register

Per window locus:
- data;
- ctrl (whole-execution PC label: every conditional EVALUATED);
- addr (the store pointer plus every contributing load's pointer);
- exec (every fetched opcode/operand byte);
- performer (the STORE opcode byte's entity material);
- written.

Not implemented:
- post-dominator-scoped ctrl (the secondary scope);
- the IN/OUT counter labels, which only re-add ctrl bases under whole-execution scope (a no-op here).
The budget is CONST and adds no label.
"""
from __future__ import annotations

import importlib.util
import os
import random
import subprocess
import sys

_VM = None


def vm16():
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
    return set(l[1]) if l[0] in ("COMPUTED", "COMPUTED_FROM") else {l}


def comp(*ls):
    s = set()
    for l in ls: s |= base(l)
    s = {b for b in s if b[0] != "CONST"}
    return ("COMPUTED", frozenset(s)) if s else ("CONST", "computed")


def cfrom(l):
    s = {b for b in base(l) if b[0] != "CONST"}
    return ("COMPUTED_FROM", frozenset(s)) if s else ("CONST", "computed")


def informative(b):
    return b[0] in ("INPUT", "ENV", "OTHER")


def start_labels(L, n_inputs, occupied=True):
    V = vm16(); lab = {}
    for a in range(256):
        if a < L: lab[a] = ("E", "W", a)
        elif a < 2 * L: lab[a] = ("E", "P", a - L) if occupied else ("CONST", "empty")
        elif V.IN_BASE <= a < V.IN_BASE + min(16, n_inputs): lab[a] = ("INPUT", a - V.IN_BASE)
        else: lab[a] = ("CONST", "zero")
    return lab


MUTANTS = ["loc0", "reverse", "memmove", "ptrlabel", "noexec", "noctrl_untaken", "noctrl_stops", "positional", "implicit_move", "exec_all"]


def trace(mem0, L, budget, inputs, allow_copyall=True, occupied=True, bug=None, check=True):
    """one SHARED interaction (entry 0, no region). Returns (final memory, per-locus records, info)."""
    V = vm16(); mem = bytearray(mem0); lab = start_labels(L, len(inputs), occupied)
    R = {r: ("CONST", "reset") for r in ("A", "B", "C", "D", "S", "T", "Z", "CF")}
    RA = {r: set() for r in ("A", "B", "C", "D", "S", "T")}
    A = B = C = D = S = T = 0; Z = False; CF = False
    pc = 0; steps = 0; ip = 0; outs = 0
    ctrl = set(); execd = set(); fetched = set(); path = []; stores = []; loads = []
    rec = {}; lab_at = {}

    def W(addr, v, l, ad, store_pc):
        addr &= 0xFF; mem[addr] = v & 0xFF; lab[addr] = l; stores.append(addr)
        if L <= addr < 2 * L:
            rec[addr - L] = {"data": l, "ctrl": set(ctrl), "addr": set(ad), "exec": "ALL" if bug == "exec_all" else set(execd),
                             "performer": frozenset(b for b in base(lab_at[store_pc]) if b[0] == "E")}

    while steps < budget:
        op = mem[pc]; steps += 1; n = V.OPLEN.get(op, 0)
        arg = mem[(pc + 1) & 0xFF] if n else 0; al = lab[(pc + 1) & 0xFF]
        npc = (pc + 1 + n) & 0xFF
        lab_at[pc] = lab[pc]; path.append((pc, op))
        fetched.add(pc)
        if n: fetched.add((pc + 1) & 0xFF)
        if bug != "noexec":
            execd |= base(lab[pc])
            if n: execd |= base(al)
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
        elif op == V.LD_A_pS: A = mem[S]; loads.append(S); R["A"] = lab[S]; RA["A"] = base(R["S"])
        elif op == V.LD_A_pT: A = mem[T]; loads.append(T); R["A"] = lab[T]; RA["A"] = base(R["T"])
        elif op in (V.LD_pT_A, V.LD_pS_A):
            p = "T" if op == V.LD_pT_A else "S"; ptr = T if p == "T" else S
            l = R["A"] if bug != "ptrlabel" else R[p]
            W(ptr, A, l, base(R[p]) | RA["A"], pc)
        elif op in (V.LDI, V.LDIR):
            while True:
                sl = lab[S]; loads.append(S)
                if bug == "positional" and L <= T < 2 * L: sl = ("E", "W", T - L)
                W(T, mem[S], sl, base(R["S"]) | base(R["T"]), pc)
                S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
                R["S"] = cfrom(R["S"]); R["T"] = cfrom(R["T"]); R["C"] = cfrom(R["C"])
                if op == V.LDI: break
                steps += 1
                if bug != "noctrl_stops": ctrl |= base(R["C"])
                if C == 0 or steps >= budget: break
        elif op == V.COPYALL and allow_copyall:
            snap = [lab[(S + i) & 0xFF] for i in range(L)] if bug == "memmove" else None
            for i in range(L):
                t = (T + i) & 0xFF; l = snap[i] if snap else lab[(S + i) & 0xFF]; loads.append((S + i) & 0xFF)
                if bug == "positional" and L <= t < 2 * L: l = ("E", "W", t - L)
                W(t, mem[(S + i) & 0xFF], l, base(R["S"]) | base(R["T"]), pc)
            steps += L // 8
        elif op in (V.ADD_A_B, V.SUB_A_B, V.XOR_A_B, V.AND_A_B, V.OR_A_B):
            if op == V.ADD_A_B: A = (A + B) & 0xFF
            elif op == V.SUB_A_B: CF = A < B; A = (A - B) & 0xFF
            elif op == V.XOR_A_B: A ^= B
            elif op == V.AND_A_B: A &= B
            else: A |= B
            if not (bug == "implicit_move" and R["B"][0] == "CONST"): R["A"] = comp(R["A"], R["B"])
            R["Z"] = R["A"]
            if op == V.SUB_A_B: R["CF"] = R["A"]
            RA["A"] = set(RA["A"]) | set(RA["B"]); Z = A == 0
        elif op in (V.INC_A, V.DEC_A):
            A = (A + (1 if op == V.INC_A else -1)) & 0xFF; Z = A == 0; R["A"] = cfrom(R["A"]); R["Z"] = R["A"]
        elif op == V.INC_S: S = (S + 1) & 0xFF; R["S"] = cfrom(R["S"])
        elif op == V.INC_T: T = (T + 1) & 0xFF; R["T"] = cfrom(R["T"])
        elif op in (V.INC_C, V.DEC_C):
            C = (C + (1 if op == V.INC_C else -1)) & 0xFF; Z = C == 0; R["C"] = cfrom(R["C"]); R["Z"] = R["C"]
        elif op == V.ADD_A_n: A = (A + arg) & 0xFF; Z = A == 0; R["A"] = comp(R["A"], al); R["Z"] = R["A"]
        elif op in (V.SHL_A, V.SHR_A):
            CF = bool(A & 0x80) if op == V.SHL_A else bool(A & 1)
            A = (A << 1) & 0xFF if op == V.SHL_A else A >> 1
            Z = A == 0; R["A"] = comp(R["A"]); R["Z"] = R["A"]; R["CF"] = R["A"]
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
            if ip < 16: A = mem[(V.IN_BASE + ip) & 0xFF]; loads.append((V.IN_BASE + ip) & 0xFF); R["A"] = lab[(V.IN_BASE + ip) & 0xFF]
            else: A = 0; R["A"] = ("CONST", "in_exhausted")
            RA["A"] = set(); ip += 1
        elif op == V.OUT_A:
            if outs < 16: mem[V.OUT_BASE + outs] = A; lab[V.OUT_BASE + outs] = R["A"]; stores.append(V.OUT_BASE + outs); outs += 1
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
    if check:
        m2 = bytearray(mem0); V.execute(m2, L, 0, budget, list(inputs), allow_copyall=allow_copyall)
        assert bytes(m2) == bytes(mem), "tracer diverged from the frozen VM"
    out = {}
    for i in range(L):
        if i in rec: r = dict(rec[i]); r["written"] = True
        else: r = {"data": lab[L + i], "ctrl": set(ctrl), "addr": set(), "exec": set(execd), "performer": frozenset(), "written": False}
        if r["exec"] == "ALL": r["exec"] = {b for a in range(256) for b in base(lab[a])}
        d = r["data"]
        if bug == "loc0" and d[0] == "E" and d[1] == "W": r["data"] = ("E", "W", 0)
        if bug == "reverse" and d[0] == "E" and d[1] == "W": r["data"] = ("E", "W", L - 1 - d[2])
        out[i] = r
    return bytes(mem), out, {"fetched": fetched, "path": path, "stores": stores, "loads": loads}


def identified(r):
    """v4 s2.1 rule-identification: data ENTITY; no FOREIGN-INFORMATIVE base and no ENTITY outside {data entity, performer}."""
    d = r["data"]
    if d[0] != "E" or not r["written"]: return False
    ok = {d[1]} | {b[1] for b in r["performer"]}
    for s in (r["ctrl"], r["addr"], r["exec"]):
        for b in s:
            if b[0] == "E" and b[1] not in ok: return False
            if informative(b): return False
    return True


def addr_of(label, L):
    V = vm16()
    if label[0] == "E": return label[2] if label[1] == "W" else L + label[2]
    if label[0] == "INPUT": return V.IN_BASE + label[1]
    return None


def flip_test(mem0, L, budget, inputs, allow_copyall=True, recs=None, info=None):
    """v4 s4.1 path-preserving flip test over all 8 bits (Amendment B1: the LOAD-address sequence must also be unchanged). Returns {locus: CONFIRMED | FAILED | INAPPLICABLE} for rule-identified
    loci. Paths come from this tracer's own execution, which is value-checked against the frozen VM on every call."""
    if recs is None: _, recs, info = trace(mem0, L, budget, inputs, allow_copyall)
    status = {}
    for i, r in recs.items():
        if not identified(r): continue
        a = addr_of(r["data"], L); applicable = failed = 0
        for bit in range(8):
            m = bytearray(mem0); m[a] ^= (1 << bit)
            m2, _, inf2 = trace(m, L, budget, inputs, allow_copyall)
            if inf2["path"] != info["path"] or inf2["stores"] != info["stores"] or inf2["loads"] != info["loads"]: continue
            applicable += 1
            if m2[L + i] != m[a]: failed += 1
        status[i] = "FAILED" if failed else ("CONFIRMED" if applicable else "INAPPLICABLE")
    return status


def arms(mem0, L, budget, inputs, allow_copyall=True, recs=None, K=8, seed=0):
    """v4 s4.2: completeness and precision per source group (W, P, INPUT), and Q8c (a suppressed write counts as a change)."""
    V = vm16(); rng = random.Random(seed)
    if recs is None: _, recs, _ = trace(mem0, L, budget, inputs, allow_copyall)
    base_mem = bytearray(mem0); V.execute(base_mem, L, 0, budget, list(inputs), allow_copyall=allow_copyall)
    out = {}
    groups = {"W": list(range(L)), "P": list(range(L, 2 * L)), "INPUT": [V.IN_BASE + k for k in range(min(16, len(inputs)))]}
    for g, addrs in groups.items():
        changed = {i: 0 for i in range(L)}
        if addrs:
            for _ in range(K):
                m = bytearray(mem0)
                for a in addrs: m[a] = rng.randrange(256)
                inp = list(m[V.IN_BASE:V.IN_BASE + len(inputs)]) if g == "INPUT" else list(inputs)
                V.execute(m, L, 0, budget, inp, allow_copyall=allow_copyall)
                for i in range(L):
                    if m[L + i] != base_mem[L + i]: changed[i] += 1

        def names(r, g=g):
            allb = base(r["data"]) | r["ctrl"] | r["addr"] | r["exec"]
            return any((b[0] == "INPUT") if g == "INPUT" else (b[0] == "E" and b[1] == g) for b in allb)
        ch = [i for i in range(L) if changed[i]]
        named = [i for i in range(L) if names(recs[i])]
        out[g] = {"changed": len(ch), "named_among_changed": sum(1 for i in ch if names(recs[i])),
                  "named": len(named), "named_that_changed": sum(1 for i in named if changed[i]),
                  "p_change": {i: changed[i] / K for i in range(L)}}
    q8c = []
    for i, r in recs.items():
        if not r["written"]: continue
        d = r["data"]; others = [g for g in ("W", "P") if not (d[0] == "E" and d[1] == g)]
        q8c.append(max(out[g]["p_change"][i] for g in others) if others else 0.0)
    out["Q8c_mean"] = sum(q8c) / len(q8c) if q8c else None
    return out


def homology(recs):
    """Q-homology: share of identified written loci whose source locus != own index; heritable writer loci."""
    ids = [(i, r["data"]) for i, r in recs.items() if identified(r)]
    return {"identified": len(ids), "shifted": sum(1 for i, d in ids if d[2] != i),
            "writer_source_loci": len({d[2] for i, d in ids if d[1] == "W"})}
