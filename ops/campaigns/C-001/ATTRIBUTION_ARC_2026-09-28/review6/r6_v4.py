"""Review 6, step 2: apply ANCESTRY_PREREG_v4 rules, as written and as simply as possible, to the 92 actual births of
r025144 (pre-states captured by r6_replay.py on the frozen harness).

shadow(): a re-implementation of the frozen vm.execute (SHARED, allow_copyall) that also carries v4 s1.2/s1.3 labels.
Its memory result and write map are CHECKED against the frozen vm.execute on every run it performs (baseline, flips,
randomisations); any mismatch aborts.

Labels. base label = ('W',i) executing organism, ('O',j) occupant, ('INPUT',k), ('C',kind) CONSTANT.
Data label = ('M', base) (a move; ('M',('C',k)) is a CONSTANT), ('CF', bases) COMPUTED_FROM, ('X', bases) COMPUTED
(constant bases dropped; empty -> CONSTANT).  Per memory byte / register we carry (data, addr_deps).
ctrl_deps = whole-execution PC label (union of condition-input bases of every conditional evaluated) -- recorded at the
store (LENIENT reading) and at the end of the interaction (STRICT reading).  exec_deps = bases of every fetched
opcode/operand byte, at the store (LENIENT) and whole interaction (STRICT)."""
import json, os, random, sys, collections, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "scratch"))
from prometheus.z80atlas import vm as V  # frozen (sha256-checked in r6_replay.py)

L = 64; BUDGET = 256; IN_BASE = V.IN_BASE; OUT_BASE = V.OUT_BASE
CONSTK = lambda k: ('M', ('C', k))


def bases(d):
    if d[0] == 'M':
        return {d[1]}
    return set(d[1]) if d[1] else {('C', 'computed_const')}


def comp(*ds, kind='X'):
    b = set()
    for d in ds:
        b |= {x for x in bases(d) if x[0] != 'C'}
    if not b:
        return CONSTK('computed')
    return (kind, frozenset(b))


def cfrom(d):  # COMPUTED_FROM: register-only bijective (INC/DEC)
    if d[0] == 'M' and d[1][0] == 'C':
        return d
    return ('CF', frozenset(bases(d) - {('C', 'computed_const')}))


def init_labels(occ_present, n_inputs):
    lab = []
    for a in range(256):
        if a < L: b = ('W', a)
        elif a < 2 * L: b = ('O', a - L) if occ_present else ('C', 'empty')
        elif IN_BASE <= a < OUT_BASE: b = ('INPUT', a - IN_BASE) if a - IN_BASE < n_inputs else ('C', 'in_pad')
        else: b = ('C', 'scratch')
        lab.append((('M', b), frozenset()))
    return lab


def shadow(mem, inputs, occ_present, want_labels=True):
    """returns dict: mem, writes(addr->val), fetch trace [(pc,op)], store addrs, and per window-locus label records."""
    mem = bytearray(mem)
    lab = init_labels(occ_present, len(inputs)) if want_labels else None
    R = {r: (CONSTK('reset'), frozenset()) for r in 'ABCDST'}
    Zl = CFl = CONSTK('reset')
    A = B = C = D = S = T = 0; Z = CF = False
    pc = 0; steps = 0; ip = 0; nout = 0
    ctrl = set(); exe = set(); fetch = []; stores = []; writes = {}; rec = {}; halted = False; budget_end = False

    def ptr(r):
        d, a = R[r]; return set(bases(d)) | set(a)

    def store(addr, val, dl, perf, harness_w=True):
        addr &= 0xFF
        mem[addr] = val & 0xFF; stores.append(addr)
        if harness_w: writes[addr] = val & 0xFF        # OUT stores bypass the frozen W(): not in tr.writes
        if want_labels:
            lab[addr] = dl
            if L <= addr < 2 * L:
                rec[addr - L] = {'data': dl[0], 'addr': frozenset(dl[1]), 'ctrl_store': frozenset(ctrl), 'exec_store': frozenset(exe),
                                 'perf': perf}

    while steps < BUDGET:
        op = mem[pc]; steps += 1; fetch.append((pc, op))
        n = V.OPLEN.get(op, 0)
        arg = mem[(pc + 1) & 0xFF] if n else 0
        if want_labels:
            opl = lab[pc]; exe |= bases(opl[0])
            argl = lab[(pc + 1) & 0xFF] if n else None
            if n: exe |= bases(argl[0])
            perf = opl[0]
        npc = (pc + 1 + n) & 0xFF
        if op == V.HALT:
            halted = True; break
        elif op in (V.LD_A_n, V.LD_B_n, V.LD_C_n, V.LD_D_n, V.LD_S_n, V.LD_T_n):
            r = {V.LD_A_n: 'A', V.LD_B_n: 'B', V.LD_C_n: 'C', V.LD_D_n: 'D', V.LD_S_n: 'S', V.LD_T_n: 'T'}[op]
            if r == 'A': A = arg
            elif r == 'B': B = arg
            elif r == 'C': C = arg
            elif r == 'D': D = arg
            elif r == 'S': S = arg
            else: T = arg
            if want_labels: R[r] = argl
        elif op in (V.LD_A_pS, V.LD_A_pT):
            p = S if op == V.LD_A_pS else T
            A = mem[p]
            if want_labels:
                R['A'] = (lab[p][0], frozenset(set(lab[p][1]) | ptr('S' if op == V.LD_A_pS else 'T')))
        elif op in (V.LD_pT_A, V.LD_pS_A):
            p = T if op == V.LD_pT_A else S
            dl = (R['A'][0], frozenset(set(R['A'][1]) | ptr('T' if op == V.LD_pT_A else 'S'))) if want_labels else None
            store(p, A, dl, perf if want_labels else None)
        elif op == V.LDI or op == V.LDIR:
            while True:
                v = mem[S]
                dl = (lab[S][0], frozenset(set(lab[S][1]) | ptr('S') | ptr('T'))) if want_labels else None
                store(T, v, dl, perf if want_labels else None)
                S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
                if want_labels:
                    R['S'] = (cfrom(R['S'][0]), R['S'][1]); R['T'] = (cfrom(R['T'][0]), R['T'][1]); R['C'] = (cfrom(R['C'][0]), R['C'][1])
                if op == V.LDI:
                    break
                steps += 1
                if want_labels: ctrl |= bases(R['C'][0]) | set(R['C'][1])       # the C==0 exit test (budget test is CONSTANT)
                if C == 0 or steps >= BUDGET:
                    break
        elif op == V.COPYALL:
            for i in range(L):
                a_s = (S + i) & 0xFF
                dl = (lab[a_s][0], frozenset(set(lab[a_s][1]) | ptr('S') | ptr('T'))) if want_labels else None
                store(T + i, mem[a_s], dl, perf if want_labels else None)
            steps += L // 8
        elif op in (V.ADD_A_B, V.SUB_A_B, V.XOR_A_B, V.AND_A_B, V.OR_A_B):
            if op == V.ADD_A_B: A = (A + B) & 0xFF
            elif op == V.SUB_A_B: CF = A < B; A = (A - B) & 0xFF
            elif op == V.XOR_A_B: A ^= B
            elif op == V.AND_A_B: A &= B
            else: A |= B
            Z = A == 0
            if want_labels:
                nl = (comp(R['A'][0], R['B'][0]), frozenset(set(R['A'][1]) | set(R['B'][1])))
                if op == V.SUB_A_B: CFl = nl[0]
                R['A'] = nl; Zl = nl[0]
        elif op in (V.INC_A, V.DEC_A):
            A = (A + (1 if op == V.INC_A else -1)) & 0xFF; Z = A == 0
            if want_labels: R['A'] = (cfrom(R['A'][0]), R['A'][1]); Zl = R['A'][0]
        elif op in (V.INC_S, V.INC_T):
            r = 'S' if op == V.INC_S else 'T'
            if r == 'S': S = (S + 1) & 0xFF
            else: T = (T + 1) & 0xFF
            if want_labels: R[r] = (cfrom(R[r][0]), R[r][1])
        elif op == V.ADD_A_n:
            A = (A + arg) & 0xFF; Z = A == 0
            if want_labels: R['A'] = (comp(R['A'][0], argl[0]), frozenset(set(R['A'][1]) | set(argl[1]))); Zl = R['A'][0]
        elif op in (V.SHL_A, V.SHR_A):
            if op == V.SHL_A: CF = bool(A & 0x80); A = (A << 1) & 0xFF
            else: CF = bool(A & 1); A >>= 1
            Z = A == 0
            if want_labels: R['A'] = (comp(R['A'][0]), R['A'][1]); Zl = CFl = R['A'][0]
        elif op in (V.INC_C, V.DEC_C):
            C = (C + (1 if op == V.INC_C else -1)) & 0xFF; Z = C == 0
            if want_labels: R['C'] = (cfrom(R['C'][0]), R['C'][1]); Zl = R['C'][0]
        elif op == V.CP_A_n:
            Z = A == arg; CF = A < arg
            if want_labels: Zl = CFl = comp(R['A'][0], argl[0])
        elif op == V.CP_A_B:
            Z = A == B; CF = A < B
            if want_labels: Zl = CFl = comp(R['A'][0], R['B'][0])
        elif op == V.JP_n: npc = arg
        elif op in (V.JZ_n, V.JNZ_n, V.JC_n):
            if want_labels: ctrl |= bases(Zl if op != V.JC_n else CFl)
            cond = Z if op == V.JZ_n else (not Z if op == V.JNZ_n else CF)
            if cond: npc = arg
        elif op == V.JR_d:
            d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == V.DJNZ_d:
            B = (B - 1) & 0xFF
            if want_labels: R['B'] = (cfrom(R['B'][0]), R['B'][1]); ctrl |= bases(R['B'][0]) | set(R['B'][1])
            if B != 0:
                d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
        elif op == V.IN_A:
            A = mem[(IN_BASE + ip) & 0xFF] if ip < 16 else 0
            if want_labels: R['A'] = lab[(IN_BASE + ip) & 0xFF] if ip < 16 else (CONSTK('in_exhausted'), frozenset())
            ip += 1
        elif op == V.OUT_A:
            if nout < 16:
                store(OUT_BASE + nout, A, R['A'] if want_labels else None, perf if want_labels else None, harness_w=False)
                nout += 1
        elif op in (V.LD_B_A, V.LD_A_B, V.LD_C_A, V.LD_A_C, V.LD_S_A, V.LD_T_A, V.LD_A_S, V.LD_A_T, V.LD_D_A, V.LD_A_D, V.SWAP_A_B):
            m = {V.LD_B_A: ('B', 'A'), V.LD_A_B: ('A', 'B'), V.LD_C_A: ('C', 'A'), V.LD_A_C: ('A', 'C'), V.LD_S_A: ('S', 'A'),
                 V.LD_T_A: ('T', 'A'), V.LD_A_S: ('A', 'S'), V.LD_A_T: ('A', 'T'), V.LD_D_A: ('D', 'A'), V.LD_A_D: ('A', 'D')}
            regs = {'A': A, 'B': B, 'C': C, 'D': D, 'S': S, 'T': T}
            if op == V.SWAP_A_B:
                A, B = B, A
                if want_labels: R['A'], R['B'] = R['B'], R['A']
            else:
                dst, src = m[op]; regs[dst] = regs[src]
                A, B, C, D, S, T = (regs[k] for k in 'ABCDST')
                if want_labels: R[dst] = R[src]
        pc = npc
    else:
        budget_end = True
    if steps >= BUDGET and not halted:
        budget_end = True
    return {'mem': mem, 'writes': writes, 'fetch': fetch, 'stores': stores, 'rec': rec, 'ctrl_end': frozenset(ctrl),
            'exec_end': frozenset(exe), 'budget_end': budget_end, 'halted': halted}


def frozen(mem, inputs):
    m = bytearray(mem); tr = V.execute(m, L, 0, BUDGET, inputs, allow_copyall=True)
    return m, tr


def run(mem, inputs, occ_present, want_labels=True):
    r = shadow(mem, inputs, occ_present, want_labels)
    m, tr = frozen(mem, inputs)
    assert m == r['mem'] and tr.writes == r['writes'], "shadow VM diverges from frozen vm.execute"
    return r


def build_mem(wt, ot, inputs):
    mem = bytearray(256); mem[:L] = wt
    if ot is not None: mem[L:2 * L] = ot
    for k, v in enumerate(inputs[:16]): mem[IN_BASE + k] = v
    return mem


def born(r, occ):
    written = {a - L for a in r['writes'] if L <= a < 2 * L}
    if len(written) < L: return False
    child = bytes(r['mem'][L:2 * L])
    return occ is None or child != bytes(occ)


def ent(b): return b[0] if b[0] in ('W', 'O') else None
