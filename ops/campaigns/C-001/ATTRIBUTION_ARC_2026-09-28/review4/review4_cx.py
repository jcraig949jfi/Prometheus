"""Review 4 counter-examples for ANCESTRY_PREREG_v2.md, executed on BEE's FROZEN VM (git 16fc6c2a:prometheus/z80atlas/vm.py).
Layout = r038751 (ENDOGENOUS_COPY, VM_COPY -> COPYALL on, L=64, SHARED, ECHO task: 1 input byte at 0xE0, budget 256, entry 0).
A reference shadow tracer implements v2 s1.1/s1.2 literally (data labels; ctrl_deps; addr_deps). Every case is value-checked
against the frozen vm.execute; only the labels are the rule set's. The s4.2 counterfactual check is implemented as written
(randomise one entity's bytes, 4 draws, soundness/completeness per locus).
Run: git show 16fc6c2a:prometheus/z80atlas/vm.py > /tmp/r4_vm16.py; python3 review4_cx.py"""
import importlib.util, random, sys
sp = importlib.util.spec_from_file_location("vm16", "/tmp/r4_vm16.py"); V = importlib.util.module_from_spec(sp); sys.modules["vm16"] = V; sp.loader.exec_module(V)
L = 64; IN0 = 0xE0

def base(l):                      # data label -> set of base labels
    return set(l[1]) if l[0] in ("COMPUTED", "COMPUTED_FROM", "CONSTANT") else {l}
def comp(*ls):
    s = set()
    for l in ls: s |= base(l)
    return ("COMPUTED", frozenset(s))
def ents(s): return {b[0] for b in s if b[0] in ("W", "P")}

def traced(mem, inputs, ctrl_mode="decided", bug=None):
    """ctrl_mode: 'taken' = only branches actually taken; 'decided' = every conditional branch evaluated. bug: None|'loc0'|'reverse'"""
    lab = {}
    for a in range(256):
        lab[a] = ("W", a) if a < L else ("P", a - L) if a < 2 * L else ("INPUT", a - IN0) if IN0 <= a < IN0 + 16 else ("OTHER", a)
    R = {r: ("RESET", r) for r in "ABCDSTZ"}; RA = {r: set() for r in "ABCDST"}   # RA: addr labels of the load that produced reg
    A = B = C = D = S = T = 0; Z = CF = False; pc = 0; steps = 0; ip = 0
    ctrl = []; lastw = {}; cdeps = {}; adeps = {}; t = 0
    def W(a, v, l, ad):
        a &= 0xFF; mem[a] = v & 0xFF; lab[a] = l
        if L <= a < 2 * L:
            cd = set().union(*[c for (tt, c) in ctrl if tt > lastw.get(a, -1)]) if ctrl else set()
            cdeps[a - L] = cd; adeps[a - L] = set(ad)
        lastw[a] = t
    while steps < 256:
        t += 1
        op = mem[pc]; steps += 1; n = V.OPLEN.get(op, 0); arg = mem[(pc + 1) & 0xFF] if n else 0
        al = lab[(pc + 1) & 0xFF]; npc = (pc + 1 + n) & 0xFF
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
        elif op == V.LD_pT_A: W(T, A, R["A"], base(R["T"]) | RA["A"])
        elif op == V.LD_pS_A: W(S, A, R["A"], base(R["S"]) | RA["A"])
        elif op in (V.LDI, V.LDIR):
            while True:
                W(T, mem[S], lab[S], base(R["S"]) | base(R["T"])); S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
                R["S"] = ("COMPUTED_FROM", frozenset(base(R["S"]))); R["T"] = ("COMPUTED_FROM", frozenset(base(R["T"])))
                R["C"] = ("COMPUTED_FROM", frozenset(base(R["C"])))
                if op == V.LDI: break
                steps += 1
                ctrl.append((t, base(R["C"])))          # LDIR's C==0 test is a loop exit decision
                if C == 0 or steps >= 256: break
        elif op == V.COPYALL:
            for i in range(L): W((T + i) & 0xFF, mem[(S + i) & 0xFF], lab[(S + i) & 0xFF], base(R["S"]) | base(R["T"]))
            steps += L // 8
        elif op in (V.ADD_A_B, V.SUB_A_B, V.XOR_A_B, V.AND_A_B, V.OR_A_B):
            if op == V.ADD_A_B: A = (A + B) & 0xFF
            elif op == V.SUB_A_B: CF = A < B; A = (A - B) & 0xFF
            elif op == V.XOR_A_B: A ^= B
            elif op == V.AND_A_B: A &= B
            else: A |= B
            Z = A == 0; R["A"] = comp(R["A"], R["B"]); R["Z"] = R["A"]
        elif op in (V.INC_A, V.DEC_A): A = (A + (1 if op == V.INC_A else -1)) & 0xFF; Z = A == 0; R["A"] = ("COMPUTED_FROM", frozenset(base(R["A"]))); R["Z"] = R["A"]
        elif op == V.ADD_A_n:          # v2 s1.1 lists "ADD n" as single-contributor bijective -> COMPUTED_FROM(label of A); operand dropped
            A = (A + arg) & 0xFF; Z = A == 0; R["A"] = ("COMPUTED_FROM", frozenset(base(R["A"]))); R["Z"] = R["A"]
        elif op == V.INC_S: S = (S + 1) & 0xFF
        elif op == V.INC_T: T = (T + 1) & 0xFF
        elif op in (V.CP_A_n, V.CP_A_B):
            k = arg if op == V.CP_A_n else B; Z = A == k; CF = A < k; R["Z"] = comp(R["A"], al if op == V.CP_A_n else R["B"])
        elif op in (V.JZ_n, V.JNZ_n, V.JC_n):
            take = (Z if op == V.JZ_n else (not Z) if op == V.JNZ_n else CF)
            if take: npc = arg
            if take or ctrl_mode == "decided": ctrl.append((t, base(R["Z"])))
        elif op == V.JP_n: npc = arg
        elif op == V.DJNZ_d:
            B = (B - 1) & 0xFF; R["B"] = ("COMPUTED_FROM", frozenset(base(R["B"])))
            if B != 0: npc = (pc + 2 + (arg - 256 if arg > 127 else arg)) & 0xFF
            if B != 0 or ctrl_mode == "decided": ctrl.append((t, base(R["B"])))
        elif op == V.IN_A: A = mem[(IN0 + ip) & 0xFF] if ip < 16 else 0; R["A"] = lab[(IN0 + ip) & 0xFF] if ip < 16 else ("CONSTANT", frozenset()); ip += 1
        elif op == V.OUT_A: mem[0xF0] = A; lab[0xF0] = R["A"]      # (single OUT only in these cases)
        elif op == V.LD_B_A: B = A; R["B"] = R["A"]
        elif op == V.LD_A_B: A = B; R["A"] = R["B"]
        pc = npc
    out = {}
    for i in range(L):
        l = lab[L + i]
        if bug == "loc0" and l[0] == "W": l = ("W", 0)
        if bug == "reverse" and l[0] == "W": l = ("W", L - 1 - l[1])
        out[i] = (l, cdeps.get(i, set()), adeps.get(i, set()))
    return out

def world_mem(wr, oc, x):
    m = bytearray(256); m[:L] = wr; m[L:2 * L] = oc; m[IN0] = x; return m
def run_vm(wr, oc, x):
    m = world_mem(wr, oc, x); tr = V.execute(m, L, 0, 256, [x], allow_copyall=True)
    nw = len({a for a in tr.writes if L <= a < 2 * L}); return bytes(m[L:2 * L]), nw
def check_values(wr, oc, x):
    m1 = world_mem(wr, oc, x); traced(m1, [x]); m2 = world_mem(wr, oc, x); V.execute(m2, L, 0, 256, [x], allow_copyall=True)
    assert m1 == m2, "tracer diverged from frozen VM"

def cf_check(wr, oc, x, labels, draws=4, seed=1):
    rng = random.Random(seed); base_child, _ = run_vm(wr, oc, x); changed = {"W": set(), "P": set()}
    for X in ("W", "P"):
        for _ in range(draws):
            w2 = bytes(rng.randrange(256) for _ in range(L)) if X == "W" else wr
            o2 = bytes(rng.randrange(256) for _ in range(L)) if X == "P" else oc
            c2, _ = run_vm(w2, o2, x)
            changed[X] |= {i for i in range(L) if c2[i] != base_child[i]}
    snd = [i in changed[l[0][0]] for i, l in labels.items() if l[0][0] in ("W", "P")]
    cmp_ = [X in (ents(base(l[0])) | ents(l[1]) | ents(l[2])) for X in ("W", "P") for i, l in labels.items() if i in changed[X]]
    return (sum(snd) / len(snd) if snd else float("nan"), sum(cmp_) / len(cmp_) if cmp_ else float("nan"), {k: len(v) for k, v in changed.items()})

def implicit(labels):
    n = 0
    for i, (d, cd, ad) in labels.items():
        de = ents(base(d)); others = (ents(cd) | ents(ad)) - de
        n += bool(others)
    return n

rng = random.Random(7)
def rnd(n): return bytes(rng.randrange(256) for _ in range(n))
def pad(code): return bytes(code) + rnd(L - len(code))
oc = rnd(L); x = 0x42
H = V
print("=== D1: s4.2 cannot see source-locus errors; soundness is vacuous for the executing entity ===")
wr = pad([H.LD_S_n, 0, H.LD_T_n, L, H.COPYALL, H.HALT]); check_values(wr, oc, x)
for bug in (None, "loc0", "reverse"):
    lb = traced(world_mem(wr, oc, x), [x], bug=bug)
    s, c, ch = cf_check(wr, oc, x, lb)
    print(f"  tracer={str(bug):8s} label[5]={lb[5][0]} distinct_source_loci={len({l[0] for l in lb.values()})} "
          f"soundness={s:.3f} completeness={c:.3f} loci_changed={ch}")
print("  -> a tracer that labels every locus (writer,0) [Q7: a painter] or reverses loci [K4 shift wrong] passes s4.2 at 100%/100%")

print("=== D2: Q8 / BROKEN driven by the ctrl_deps scoping, not by transmission ===")
# guard: 'do not overwrite an occupant whose first byte is HALT', then self-copy
wrA = pad([H.LD_S_n, L, H.LD_A_pS, H.CP_A_n, 0xFF, H.JZ_n, 12, H.LD_S_n, 0, H.LD_T_n, L, H.COPYALL, H.HALT])
wrB = pad([H.LD_S_n, L, H.LD_A_pS, H.CP_A_n, 0xFF, H.JNZ_n, 8, H.HALT, H.LD_S_n, 0, H.LD_T_n, L, H.COPYALL, H.HALT])
for name, w in (("JZ-skip (branch not taken)", wrA), ("JNZ-go (branch taken)", wrB)):
    check_values(w, oc, x); child, nw = run_vm(w, oc, x)
    for mode in ("taken", "decided"):
        lb = traced(world_mem(w, oc, x), [x], ctrl_mode=mode); s, c, ch = cf_check(w, oc, x, lb, seed=3)
        print(f"  {name:28s} ctrl={mode:7s} n_written={nw} child==writer:{child == w} IMPLICIT={implicit(lb)}/64 "
              f"soundness={s:.3f} completeness={c:.3f} changed_when_P_randomised={ch['P']}")
# exact dependence: fraction of occupant first bytes that change the child
dep = sum(run_vm(wrB, bytes([v]) + oc[1:], x)[0] != run_vm(wrB, oc, x)[0] for v in range(256))
print(f"  exhaustive: {dep}/256 values of the occupant's byte change the child (1 = only 0xFF). Q8 = 100% -> s2.5 BROKEN")

print("=== D3: task INPUT executed as an opcode (ECHO output byte at 0xF0) decides whether a birth happens ===")
wrC = pad([H.IN_A, H.OUT_A, H.LD_S_n, 0, H.LD_T_n, L, H.JP_n, 0xF0])
births = 0; ok = 0
for xv in range(256):
    child, nw = run_vm(wrC, oc, xv)
    births += nw >= L
    if nw >= L:
        lb = traced(world_mem(wrC, oc, xv), [xv]); ok += implicit(lb) == 0 and all(l[0][0] == "W" for l in lb.values())
print(f"  birth (n_written>=L) for {births}/256 input values; in all {ok} of them every locus is IDENTIFIED writer copy-descent;")
print("  s4.2 randomises entities only, so the INPUT dependence of the birth is never tested; ctrl/addr hold no opcode labels")

print("=== D4: v2 s1.1 'ADD n is single-contributor' drops the writer's operand ===")
# child[i] = occupant[i] + k  (k is a writer operand): a Caesar-shifted partner; 16 loci via unrolled loop
code = [H.LD_S_n, L, H.LD_T_n, L]
for i in range(8): code += [H.LD_A_pS, H.ADD_A_n, 0x40, H.LD_pT_A, H.INC_S, H.INC_T]
code += [H.HALT]; wrD = pad(code); check_values(wrD, oc, x)
lb = traced(world_mem(wrD, oc, x), [x]); s, c, ch = cf_check(wrD, oc, x, lb)
print(f"  label[0]={lb[0][0]} addr_deps={lb[0][2]}  -> counted as occupant descent when COMPUTED_FROM is not 'new'; "
      f"soundness={s:.3f} completeness={c:.3f}")
wrD2 = bytearray(wrD); wrD2[6] ^= 0x10
print(f"  changing ONLY the writer operand byte 6 changes child[0]: {run_vm(bytes(wrD2), oc, x)[0][0] != run_vm(wrD, oc, x)[0][0]}; "
      f"yet (W,6) is in neither data label nor ctrl/addr")

print("=== D5: occupant opcode byte performs the copy (K3-type); the performer is outside data/ctrl/addr ===")
oc5 = bytes([H.COPYALL, H.HALT]) + oc[2:]
wrE = pad([H.LD_S_n, 0, H.LD_T_n, L, H.JP_n, L]); check_values(wrE, oc5, x)
lb = traced(world_mem(wrE, oc5, x), [x]); s, c, ch = cf_check(wrE, oc5, x, lb)
print(f"  n_written={run_vm(wrE, oc5, x)[1]} IMPLICIT={implicit(lb)}/64 soundness={s:.3f} completeness={c:.3f} changed={ch}")
print("  -> every locus is 'identified' writer descent AND fails completeness: the rule set's K3 answer violates s4.2 by construction")
