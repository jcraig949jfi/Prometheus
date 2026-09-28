"""Review 5 counter-examples on BEE's FROZEN VM (git 16fc6c2a; vm sha256 2536b1ac..., world 5b985241...).
Run:  python3 review5_cx.py   (from the rev5 worktree; extracts the frozen modules to /tmp/r5f first)"""
import os, random, subprocess, sys
os.makedirs('/tmp/r5f', exist_ok=True)
for m in ('vm', 'world', 'grammar'):
    p = '/tmp/r5f/%s.py' % m
    if not os.path.exists(p):
        open(p, 'wb').write(subprocess.check_output(['git', 'show', '16fc6c2a:prometheus/z80atlas/%s.py' % m]))
sys.path.insert(0, '/tmp/r5f')
import vm  # noqa

def execute_traced(mem, L, entry, budget, region):
    """frozen vm.execute semantics (only the opcodes needed here are traced for provenance); records
    executed addresses (opcode + operand bytes), and for each window write its source address (MOVE) or None"""
    ex = set(); src_of = {}; A_src = None; regs_reset_used = set()
    A = B = C = D = S = T = 0; Z = False; CF = False; steps = 0; pc = entry
    lo, hi = region; reset = {'S': True, 'T': True, 'C': True, 'B': True, 'A': True}
    while steps < budget:
        if not (lo <= pc < hi): break
        op = mem[pc]; steps += 1; n = vm.OPLEN.get(op, 0)
        ex.add(pc); ex.update(((pc + 1) & 0xFF,) if n else ())
        arg = mem[(pc + 1) & 0xFF] if n else 0; npc = (pc + 1 + n) & 0xFF
        if op == vm.HALT: break
        elif op == vm.LD_A_pS:
            if reset['S']: regs_reset_used.add('S (load pointer)')
            A = mem[S]; A_src = S; reset['A'] = False
        elif op == vm.LD_T_A: T = A; reset['T'] = reset['A']
        elif op == vm.LD_T_n: T = arg; reset['T'] = False
        elif op == vm.LD_S_n: S = arg; reset['S'] = False
        elif op == vm.LD_C_n: C = arg; reset['C'] = False
        elif op == vm.SWAP_A_B: A, B = B, A; A_src = None
        elif op == vm.ADD_A_B: A = (A + B) & 0xFF; Z = A == 0; A_src = None
        elif op == vm.OR_A_B: A |= B; Z = A == 0; A_src = None
        elif op == vm.LD_pT_A:
            mem[T] = A; src_of[T] = A_src
        elif op == vm.LDIR:
            if reset['C']: regs_reset_used.add('C (LDIR count / C==0 exit)')
            if reset['S']: regs_reset_used.add('S (LDIR source pointer)')
            while True:
                src_of[T] = src_of.get(S, ('pre', S)) if S in src_of else ('pre', S)
                mem[T] = mem[S]
                S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF; steps += 1
                if C == 0 or steps >= budget: break
        elif op in vm.OPLEN and op not in (vm.NOP,):
            raise SystemExit('untraced opcode %s' % vm.MNEMONIC.get(op))
        pc = npc
    return ex, src_of, regs_reset_used, steps

def separated(writer, partner, L=32, budget=256):
    """world._execute, layout SEPARATED (world.py@16fc6c2a lines 271-285): two vm.execute calls, registers reset
    between them, PC confined to [0,L/2) then [L/2,L)"""
    mem = bytearray(256); mem[:L] = writer; mem[L:2 * L] = partner
    pre = bytes(mem)
    e1, s1, r1, st1 = execute_traced(mem, L, 0, budget // 2, (0, L // 2))
    e2, s2, r2, st2 = execute_traced(mem, L, L // 2, budget // 2, (L // 2, L))
    # compose provenance of the second half through the first half's writes
    src = dict(s1)
    for a, s in s2.items():
        if s and s[0] == 'pre' and s[1] in s1: src[a] = s1[s[1]]
        else: src[a] = s
    return pre, mem, e1 | e2, src, r1 | r2, (st1, st2)

print('=== CX1: r004041 dominant tape (TRACED_spontaneous.json top_tape), BYTECODE32 / SEPARATED / L=32 ===')
top = bytes.fromhex('1048d948b14ef7bd2050376a2898fc151048d948b14ef7bd2050376a2898fc15')
print(' disassembly of each half:', vm.disassemble(top[:16]))
rng = random.Random(1)
partner = bytes(rng.randrange(256) for _ in range(32))
pre, post, executed, src, reset_used, steps = separated(top, partner)
child = post[32:64]
print(' child == writer tape:', child == top, ' steps per half:', steps)
srcs = [src.get(32 + k) for k in range(32)]
print(' child locus -> pre-execution source address:', [s[1] if s else None for s in srcs])
n_exec_src = sum(1 for s in srcs if s and s[1] in executed)
print(' loci whose MOVE source byte was ALSO EXECUTED (excluded from the s4.2 core flip test): %d / 32' % n_exec_src)
print(' RESET register values the copy depends on:', sorted(reset_used))
print(' => every locus has RESET in addr_deps and ctrl_deps -> not RULE-IDENTIFIED (s2.1) -> birth not identifiable;')
print('    and the core flip test has an EMPTY denominator for this birth.')
# check the frozen VM agrees (not just my tracer)
mem = bytearray(256); mem[:32] = top; mem[32:64] = partner
vm.execute(mem, 32, 0, 128, [], region=(0, 16)); vm.execute(mem, 32, 16, 128, [], region=(16, 32))
print(' frozen vm.execute child == traced child:', bytes(mem[32:64]) == child)
# counterfactual: the second half [16,32) of the writer is NEVER a source: flip it, child unchanged
t2 = bytearray(top); t2[20] ^= 0x01
mem = bytearray(256); mem[:32] = t2; mem[32:64] = partner
vm.execute(mem, 32, 0, 128, [], region=(0, 16)); vm.execute(mem, 32, 16, 128, [], region=(16, 32))
print(' flip writer byte 20 -> child changes?', bytes(mem[32:64]) != child, '(child is 2 copies of bytes 0..15; byte 20 is overwritten before use)')

print()
print('=== CX2: canonical replicator (vm.replicator), SHARED layout: share of loci eligible for the core flip test ===')
for L in (32, 64):
    rep = vm.replicator(L) + bytes(rng.randrange(1, 255) for _ in range(L - 8))
    mem = bytearray(256); mem[:L] = rep; mem[L:2 * L] = bytes(L)
    ex, s, r, st = execute_traced(mem, L, 0, 256, (0, 256))
    eligible = sum(1 for k in range(L) if s.get(L + k) and s[L + k][1] not in ex)
    print(' L=%d: executed source bytes %d; flip-eligible loci %d/%d = %.1f%% (s2.1 needs >= 90%% IDENTIFIED)' % (L, len(ex & set(range(L))), eligible, L, 100.0 * eligible / L))

print()
print('=== CX3: bit-decoder implicit copy passes the single-bit flip test for a WRONG MOVE label ===')
# child[k] := occupant[k] rebuilt bit by bit through branches (A built from immediates only).
# Rule label: CONSTANT/COMPUTED of the immediates, ctrl_deps {(O,k)}.  A tracer that (wrongly) labels it MOVE (O,k)
# still passes "flip one bit -> child takes the value the move predicts" for EVERY bit.
def bitcopy_prog(src, dst):
    # acc (C) := 0; repeat 8 (DJNZ): acc <<= 1; D <<= 1; if carry: acc += 1 (INC A). acc is built from the immediate 0
    # and INC only; the occupant byte reaches it ONLY through the JC condition.
    return [vm.LD_S_n, src, vm.LD_A_pS, vm.LD_D_A, vm.LD_C_n, 0, vm.LD_B_n, 8,
            vm.LD_A_C, vm.SHL_A, vm.LD_C_A, vm.LD_A_D, vm.SHL_A, vm.LD_D_A,      # 8..13
            vm.JC_n, 18, vm.JR_d, 3,                                             # 14..17
            vm.LD_A_C, vm.INC_A, vm.LD_C_A,                                      # 18..20
            vm.DJNZ_d, 0xF1,                                                     # 21..22 -> 8
            vm.LD_A_C, vm.LD_T_n, dst, vm.LD_pT_A, vm.HALT]
L = 64
prog = bitcopy_prog(src=64 + 5, dst=64 + 9)   # copy occupant byte 5 into occupant locus 9, purely by control flow
def run_bc(occ):
    mem = bytearray(256); mem[:len(prog)] = bytes(prog); mem[64:128] = occ
    vm.execute(mem, 64, 0, 256, [])
    return mem[64 + 9]
occ = bytearray(rng.randrange(256) for _ in range(64)); occ[5] = 0xA6
base = run_bc(occ)
ok = 0
for b in range(8):
    o2 = bytearray(occ); o2[5] ^= 1 << b
    ok += run_bc(o2) == o2[5]
print(' program length %d bytes, frozen VM, L=64, budget 256' % len(prog))
print(' baseline child locus == occupant byte 5:', base == occ[5], '; bit flips reproduced by the "move prediction": %d/8' % ok)
print(' => the flip test cannot distinguish a MOVE label from a pure implicit (control-flow) copy; it validates')
print('    counterfactual dependence, not the rule label. Only the fixture pack can catch this mislabel.')

print()
print('=== CX4: OPCODE mutation (r004041 config) consumes a tape-DEPENDENT number of RNG draws ===')
import shutil
pkg = '/tmp/r5pkg'
if not os.path.exists(pkg + '/prometheus/z80atlas/world.py'):
    os.makedirs(pkg, exist_ok=True)
    subprocess.check_call('git archive 16fc6c2a prometheus/z80atlas prometheus/__init__.py | tar -x -C ' + pkg, shell=True)
sys.path.insert(0, pkg)
from prometheus.z80atlas import world as Wd  # noqa
t = bytearray(top); t2 = bytearray(t); t2[4] = vm.LD_S_n
print(' draws for r004041 top tape: %d; after one byte change (0x%02x -> LD S,n): %d' % (
    len(Wd.World._opcode_positions(None, t)), top[4], len(Wd.World._opcode_positions(None, t2))))
print(' => world.py _mutate (16fc6c2a) calls rng.random() once per opcode position; a flipped byte shifts every later')
print('    draw of the shared World.rng (partners, inputs, other tapes mutations). "Holding the RNG fixed" is only')
print('    meaningful inside one vm.execute; across ticks it requires per-purpose RNG streams, which the frozen harness lacks.')

print()
print('=== CX5: r004041 dominant self-copier is NOT is_sr under traced_replay.py criterion (b) ===')
# traced_replay.py:88 records, per window byte, the SOURCE ADDRESS of the LAST copy-op write; criterion (b)
# (line 222) needs >= 0.9*L of them with src < L.  Re-run the two SEPARATED halves recording raw src addresses.
def last_src(mem, entry, region, L=32, budget=128):
    out = {}; S = T = C = 0; A = 0; pc = entry; steps = 0
    while steps < budget and region[0] <= pc < region[1]:
        op = mem[pc]; steps += 1; n = vm.OPLEN.get(op, 0); arg = mem[pc + 1] if n else 0; npc = pc + 1 + n
        if op == vm.LD_A_pS: A = mem[S]
        elif op == vm.LD_T_A: T = A
        elif op == vm.LDIR:
            while True:
                mem[T] = mem[S]
                if L <= T < 2 * L: out[T - L] = S
                S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF; steps += 1
                if C == 0 or steps >= budget: break
        pc = npc
    return out
mem = bytearray(256); mem[:32] = top; mem[32:64] = partner
w = last_src(mem, 0, (0, 16)); w.update(last_src(mem, 16, (16, 32)))
own = sum(1 for k, s in w.items() if s < 32)
print(' window bytes written %d/32; last-write source inside own tape: %d/32 (criterion b needs >= %.1f)' % (len(w), own, 0.9 * 32))
print(' child is an exact copy of the writer, yet is_sr = 0: the eligibility filter (>=1 is_sr) and the "76 SR births"')
print(' count the criterion artifact, not self-copying (TRACED_spontaneous.json: hifi_births_tail_not_selfrep = 3334 of 3349).')
