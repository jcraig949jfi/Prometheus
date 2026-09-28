"""Review 3 counter-examples for ANCESTRY_PREREG.md s1 label rules, executed on BEE's FROZEN VM (git 16fc6c2a:prometheus/z80atlas/vm.py,
the harness r016299 was run and replayed with). A reference shadow tracer implements the preregistration's rules literally:
  memory: writer locus i -> (E,W,i); partner locus j -> (E,P,j); other -> (OTHER,a); registers start (REG0,r) [prereg has NO rule];
  pure moves carry labels; ALU -> (COMPUTED, flattened contributor set); LD r,n -> label of the operand byte; IN -> (INPUT);
  pointer/branch/loop-counter labels are NOT propagated (the prereg models none of them and does not list them as 'unknown').
Every case is value-checked against the frozen vm.execute (bit-identical memory), so the VALUES are BEE's and only the LABELS are
the rule set's. Run:  python3 review3_cx.py   (needs /tmp/rev3_vm16.py = git show 16fc6c2a:prometheus/z80atlas/vm.py)"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("vm16", "/tmp/rev3_vm16.py"); V = importlib.util.module_from_spec(spec); sys.modules["vm16"] = V; spec.loader.exec_module(V)

def comp(*ls):
    s = set()
    for l in ls:
        if l[0] == "COMPUTED": s |= l[1]
        else: s.add(l)
    return ("COMPUTED", frozenset(s))

def traced(mem, L, budget, inputs, allow_copyall, lab, hook_out_through_W=True, copyall_snapshot=False):
    """shadow-label execute; mirrors vm16.execute's control flow exactly"""
    R = {r: ("REG0", r) for r in "ABCDST"}
    A = B = C = D = S = T = 0; Z = CF = False; pc = 0; steps = 0; ip = 0
    def W(a, v, l):
        a &= 0xFF; mem[a] = v & 0xFF; lab[a] = l
    while steps < budget:
        op = mem[pc]; steps += 1; n = V.OPLEN.get(op, 0); arg = mem[(pc + 1) & 0xFF] if n else 0
        al = lab[(pc + 1) & 0xFF]; npc = (pc + 1 + n) & 0xFF
        if op == V.HALT: break
        elif op == V.LD_A_n: A = arg; R["A"] = al
        elif op == V.LD_B_n: B = arg; R["B"] = al
        elif op == V.LD_C_n: C = arg; R["C"] = al
        elif op == V.LD_D_n: D = arg; R["D"] = al
        elif op == V.LD_S_n: S = arg; R["S"] = al
        elif op == V.LD_T_n: T = arg; R["T"] = al
        elif op == V.LD_A_pS: A = mem[S]; R["A"] = lab[S]
        elif op == V.LD_A_pT: A = mem[T]; R["A"] = lab[T]
        elif op == V.LD_pT_A: W(T, A, R["A"])
        elif op == V.LD_pS_A: W(S, A, R["A"])
        elif op == V.LDI: W(T, mem[S], lab[S]); S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
        elif op == V.LDIR:
            while True:
                W(T, mem[S], lab[S]); S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF; steps += 1
                if C == 0 or steps >= budget: break
        elif op == V.COPYALL and allow_copyall:
            if copyall_snapshot:     # a plausible WRONG tracer: labels copied as a block (memmove semantics)
                snap = [lab[(S + i) & 0xFF] for i in range(L)]
                for i in range(L): mem[(T + i) & 0xFF] = mem[(S + i) & 0xFF]; lab[(T + i) & 0xFF] = snap[i]
            else:
                for i in range(L): W((T + i) & 0xFF, mem[(S + i) & 0xFF], lab[(S + i) & 0xFF])
            steps += L // 8
        elif op in (V.ADD_A_B, V.SUB_A_B, V.XOR_A_B, V.AND_A_B, V.OR_A_B):
            if op == V.ADD_A_B: A = (A + B) & 0xFF
            elif op == V.SUB_A_B: CF = A < B; A = (A - B) & 0xFF
            elif op == V.XOR_A_B: A ^= B
            elif op == V.AND_A_B: A &= B
            else: A |= B
            Z = A == 0; R["A"] = comp(R["A"], R["B"])
        elif op in (V.INC_A, V.DEC_A): A = (A + (1 if op == V.INC_A else -1)) & 0xFF; Z = A == 0; R["A"] = comp(R["A"])
        elif op == V.INC_S: S = (S + 1) & 0xFF; R["S"] = comp(R["S"])
        elif op == V.INC_T: T = (T + 1) & 0xFF; R["T"] = comp(R["T"])
        elif op == V.ADD_A_n: A = (A + arg) & 0xFF; Z = A == 0; R["A"] = comp(R["A"], al)
        elif op == V.SHL_A: CF = bool(A & 0x80); A = (A << 1) & 0xFF; Z = A == 0; R["A"] = comp(R["A"])
        elif op == V.SHR_A: CF = bool(A & 1); A >>= 1; Z = A == 0; R["A"] = comp(R["A"])
        elif op == V.INC_C: C = (C + 1) & 0xFF; Z = C == 0; R["C"] = comp(R["C"])
        elif op == V.DEC_C: C = (C - 1) & 0xFF; Z = C == 0; R["C"] = comp(R["C"])
        elif op == V.CP_A_n: Z = A == arg; CF = A < arg          # flags: NO label (control flow is not modelled)
        elif op == V.CP_A_B: Z = A == B; CF = A < B
        elif op == V.JP_n: npc = arg
        elif op == V.JZ_n: npc = arg if Z else npc
        elif op == V.JNZ_n: npc = arg if not Z else npc
        elif op == V.JC_n: npc = arg if CF else npc
        elif op == V.JR_d: d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == V.DJNZ_d:
            B = (B - 1) & 0xFF; R["B"] = comp(R["B"])
            if B != 0: d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == V.IN_A:
            A = mem[(V.IN_BASE + ip) & 0xFF] if ip < 16 else 0; ip += 1; R["A"] = ("INPUT",)   # the prereg's rule
        elif op == V.OUT_A:
            k = sum(1 for a in range(V.OUT_BASE, V.OUT_BASE + 16) if False)
            # vm16 writes mem[OUT_BASE+len(outputs)] = A directly, NOT through W()
            idx = traced.nout; traced.nout += 1
            if idx < 16:
                mem[V.OUT_BASE + idx] = A
                if hook_out_through_W: lab[V.OUT_BASE + idx] = R["A"]
        else:
            m = {V.LD_B_A: ("B", "A"), V.LD_A_B: ("A", "B"), V.LD_C_A: ("C", "A"), V.LD_A_C: ("A", "C"), V.LD_S_A: ("S", "A"),
                 V.LD_T_A: ("T", "A"), V.LD_A_S: ("A", "S"), V.LD_A_T: ("A", "T"), V.LD_D_A: ("D", "A"), V.LD_A_D: ("A", "D")}
            if op in m:
                dst, src = m[op]; val = {"A": A, "B": B, "C": C, "D": D, "S": S, "T": T}[src]
                if dst == "A": A = val
                elif dst == "B": B = val
                elif dst == "C": C = val
                elif dst == "D": D = val
                elif dst == "S": S = val
                else: T = val
                R[dst] = R[src]
            elif op == V.SWAP_A_B: A, B = B, A; R["A"], R["B"] = R["B"], R["A"]
        pc = npc
    return mem

def run(name, writer, partner, L=64, budget=4096, inputs=(0,) * 16, allow_copyall=False, pair=True, **kw):
    mem = bytearray(256); mem[:L] = writer.ljust(L, b"\x00"); mem[L:2 * L] = partner
    for k, v in enumerate(inputs[:16]): mem[V.IN_BASE + k] = v
    ref = bytearray(mem); V.execute(ref, 2 * L if pair else L, 0, budget, list(inputs), allow_copyall=allow_copyall)
    lab = [("E", "W", i) if i < L else ("E", "P", i - L) if i < 2 * L else ("OTHER", i) for i in range(256)]
    traced.nout = 0
    got = traced(bytearray(mem), 2 * L if pair else L, budget, list(inputs), allow_copyall, lab, **kw)
    assert got == ref, name + ": tracer diverged from frozen vm"
    child = ref[L:2 * L]; clab = lab[L:2 * L]
    return child, clab, bytes(mem[L:2 * L])

def summar(clab):
    c = {}
    for l in clab:
        k = l[0] if l[0] != "E" else "E:" + l[1]
        if l[0] == "COMPUTED": k = "COMPUTED{" + ",".join(sorted(x[0] + ":" + str(x[1]) for x in l[1])) + "}"
        c[k] = c.get(k, 0) + 1
    return c

def ibs(a, b): return sum(x == y for x, y in zip(a, b)) / len(a)

L = 64; N = 16          # the first N window loci are rewritten in each demo; the rest are retained
import random
rng = random.Random(7)
P = bytes(rng.randrange(1, 256) for _ in range(L))       # partner tape (nonzero bytes)

print("== CX-A implicit flow: loop-counter copy (DJNZ). child[p] := partner[p] exactly, via control flow only ==")
# 00: LD S,64   02: LD T,64   04: LD D,16          ; D = bytes remaining (not used as data)
# 06: LD A,(S)  07: LD B,A    08: LD A,0 (operand locus 9)
# 0A: INC A     0B: DJNZ -3   (B counts partner byte down; A counts up from the WRITER's operand)
# 0D: LD (T),A  0E: INC S  0F: INC T  10: LD A,D  11: DEC A  12: LD D,A  13: JNZ 06  15: HALT
w = bytes([V.LD_S_n, 64, V.LD_T_n, 64, V.LD_D_n, N, V.LD_A_pS, V.LD_B_A, V.LD_A_n, 0, V.INC_A, V.DJNZ_d, 0xFD,
           V.LD_pT_A, V.INC_S, V.INC_T, V.LD_A_D, V.DEC_A, V.LD_D_A, V.JNZ_n, 0x06, V.HALT])
child, clab, pre = run("A", w, P)
print(" child[0:16] == partner[0:16]:", child[:N] == P[:N], "| IBS(child, partner) =", round(ibs(child, P), 3))
print(" prereg labels, rewritten loci:", summar(clab[:N]), "| unknown links: 0 -> identified share 1.0")
print(" => IBD(partner) = 0/16 on the rewritten loci; rules call it NEW MATERIAL computed from the WRITER's operand byte 9")

print("\n== CX-B address dependence / translation table: child[p] := writer[partner[p]] (constructor + description) ==")
Pd = bytes(24 + (b % 40) for b in P)                   # 'description': partner bytes are indices 24..63 into the writer's table
tab = bytes(rng.randrange(256) for _ in range(40))
# 00 LD S,64 02 LD T,64 04 LD D,16 06 LD A,S 07 LD C,A 08 LD A,(S) 09 LD S,A 0A LD A,(S) 0B LD (T),A 0C LD A,C 0D LD S,A
# 0E INC S 0F INC T 10 LD A,D 11 DEC A 12 LD D,A 13 JNZ 06 15 HALT
w = bytes([V.LD_S_n, 64, V.LD_T_n, 64, V.LD_D_n, N, V.LD_A_S, V.LD_C_A, V.LD_A_pS, V.LD_S_A, V.LD_A_pS, V.LD_pT_A,
           V.LD_A_C, V.LD_S_A, V.INC_S, V.INC_T, V.LD_A_D, V.DEC_A, V.LD_D_A, V.JNZ_n, 0x06, V.HALT]).ljust(24, b"\x00") + tab
child, clab, pre = run("B", w, Pd)
print(" prereg labels, rewritten loci:", summar(clab[:N]), " distinct source loci:", len(set(clab[:N])), "/", N)
P2 = bytearray(Pd); P2[0] = 24 + ((Pd[0] - 24 + 1) % 40)
child2, _, _ = run("B2", w, bytes(P2))
print(" intervention: change ONE partner byte (locus 0) -> child locus 0 changes:", child[0] != child2[0],
      "| rules still attribute locus 0 100% to the writer; partner 'donor share' = 0%")

print("\n== CX-C INPUT laundering: writer stores its own byte into the input region, IN reads it back ==")
# 00 LD A,(S=0x3F via LD S) ... simpler: 00 LD S,63 02 LD A,(S) 03 LD T,0xE0 05 LD (T),A 06 IN A 07 LD T,64 09 LD (T),A 0A HALT
w = bytes([V.LD_S_n, 63, V.LD_A_pS, V.LD_T_n, 0xE0, V.LD_pT_A, V.IN_A, V.LD_T_n, 64, V.LD_pT_A, V.HALT]).ljust(63, b"\x00") + b"\xAB"
child, clab, pre = run("C", w, P)
print(" child[0] = %02x (writer locus 63 = AB) ; prereg label:" % child[0], clab[0], "(should be ('E','W',63))")

print("\n== CX-D OUT bypass: vm16 OUT_A stores to mem[0xF0] WITHOUT W(); a tracer hooked on W() (traced_replay.py:79-94 pattern) keeps a stale label ==")
# 00 LD S,64 02 LD A,(S) 03 OUT A 04 LD S,0xF0 06 LD A,(S) 07 LD T,65 09 LD (T),A 0A HALT
w = bytes([V.LD_S_n, 64, V.LD_A_pS, V.OUT_A, V.LD_S_n, 0xF0, V.LD_A_pS, V.LD_T_n, 65, V.LD_pT_A, V.HALT])
mem = bytearray(256); mem[:64] = w.ljust(64, b"\x00"); mem[64:128] = P; tr = V.execute(mem, 128, 0, 256, [0] * 16)
print(" frozen vm: 0xF0 in Trace.writes?", 0xF0 in tr.writes, "| mem[0xF0]=%02x partner[0]=%02x" % (mem[0xF0], P[0]))
child, clab, _ = run("D", w, P, hook_out_through_W=False)
print(" W-hooked tracer: child[1]=%02x label" % child[1], clab[1], " | correct label ('E','P',0)")

print("\n== CX-E overlapping COPYALL in PAIR_EXECUTION (vm L = 2*64 = 128 bytes moved, sequential semantics) ==")
w = bytes([V.LD_S_n, 60, V.LD_T_n, 64, V.COPYALL, V.HALT])
c1, l1, _ = run("E", w, P, allow_copyall=True, budget=256)
c2, l2, _ = run("E2", w, P, allow_copyall=True, budget=256, copyall_snapshot=True)
print(" sequential (correct) labels:", summar(l1), " distinct source loci", len(set(l1)))
print(" snapshot tracer labels     :", summar(l2), " distinct source loci", len(set(l2)))
print(" values identical in both (only labels differ); K1-K9 all use non-overlapping copies, so the wrong tracer passes them")

print("\n== CX-F uninitialised register: LD (T),A with A never loaded (BEE zeroes A..T at every execute, vm.py:96) ==")
w = bytes([V.LD_T_n, 64, V.LD_pT_A, V.HALT])
child, clab, _ = run("F", w, P)
print(" child[0]=%02x label" % child[0], clab[0], "-> the prereg gives no start label for registers: UNKNOWN or improvised")

print("\n== CX-G K8 (value coincidence) cannot produce a (CONSTANT) label in BEE ==")
w = bytes([V.LD_A_n, P[0], V.LD_T_n, 64, V.LD_pT_A, V.HALT])
child, clab, _ = run("G", w, P)
print(" writer stores literal equal to occupant byte: label", clab[0], "(prereg K8 expects CONSTANT; s1 operand rule says writer locus 1)")
