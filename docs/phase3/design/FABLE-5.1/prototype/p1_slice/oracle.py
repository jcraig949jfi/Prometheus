"""Pure-Python oracle for WM-mini and the RETAIN world.

Written separately from wm_mini.py, from the same specification, on purpose
in a different style (plain Python integers, lists and a class; no numpy, no
numba). differential_test.py checks that the two agree exactly on every trial
of every life for designed and random programs.

Honest limit: both implementations were written by the same author in the same
session. In the design's terms this is independence level I1 at best. It
catches transcription and compiler-level errors. It does not catch a shared
misreading of the specification. The design asks for a second implementation
by a different model family (REQUIREMENTS.md WLD-11); this file is not that.

Specification (the whole of it):

  hash       h = sm(seed); h = sm(h ^ life); h = sm(h ^ a); h = sm(h ^ b)
             sm(x): z = x + 0x9E3779B97F4A7C15
                    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
                    z = (z ^ (z >> 27)) * 0x94D049BB133111EB
                    return z ^ (z >> 31)          (all modulo 2^64)
  mapping    M(s) = hash(seed, life, 1000003, s) mod R
  stimulus   s(ep, t) = hash(seed, life, 2000003 + ep, t) mod K
  machine    8 registers, values 0..65535; fast memory of F cells; store of S
             cells; a program of n words (op, a, b, c); op = word0 mod 19;
             register indices are fields mod 8
  phase      start at pc 0; stop at OUT, at HALT, past the last word, or after
             `cap` instructions; action is 0 unless OUT set it
  ops        0 NOP | 1 IN a: r[a] = obs | 2 PH a: r[a] = phase
             3 SET a: r[a] = field_b mod 64 | 4 MOV a,b | 5 ADD a,b,c
             6 SUB a,b,c (mod 65536) | 7 SKZ a | 8 SKNZ a | 9 SKEQ a,b
             10 SKLT a,b (skip next if r[a] < r[b])
             11 STW a,b: store[r[a] mod S] = r[b]  (only if the store affordance is on)
             12 STR a,b: r[a] = store[r[b] mod S]
             13 FW a,b: fmem[r[a] mod F] = r[b] | 14 FR a,b: r[a] = fmem[r[b] mod F]
             15 OUT a: action = r[a] mod R, stop | 16 HALT: stop
             17 JMP: pc += field_c mod 16 (forward only) | 18 XOR a,b,c
  trial      stimulus phase (phase 0, obs = s, or obs = M(s) in the leaky world),
             then feedback phase (phase 1, obs = M(s)); registers and fast
             memory carry over between the two phases and between trials
  episode    T trials; the HARNESS zeroes registers and fast memory first
  life       E episodes; the store starts as the genome's store0 and is never
             reset
  types      PROBE: s was shown in an earlier episode, not yet in this one, and
                    has not been probed before in this life
             REPEAT: s was not shown in an earlier episode, was shown earlier in
                    this one, and has not been counted as a repeat before
             NOVEL: s was shown neither in an earlier episode nor in this one
             OTHER: anything else
"""

M64 = (1 << 64) - 1
T_NOVEL, T_REPEAT, T_PROBE, T_OTHER = 0, 1, 2, 3


def _sm(x):
    z = (x + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


def khash(seed, life, a, b):
    h = _sm(seed & M64)
    for v in (life, a, b):
        h = _sm(h ^ (v & M64))
    return h


def mapping(seed, life, s, R):
    return khash(seed, life, 1000003, s) % R


def stimulus(seed, life, ep, t, K):
    return khash(seed, life, 2000003 + ep, t) % K


class Machine:
    def __init__(self, prog, store0, F, R, cap, aff_store=True):
        self.prog = [tuple(int(v) for v in w) for w in prog]
        self.store = [int(v) for v in store0]
        self.fmem = [0] * F
        self.reg = [0] * 8
        self.R = R
        self.cap = cap
        self.aff_store = aff_store
        self.instr = 0

    def reset_fast(self, reset_fmem=True):
        self.reg = [0] * 8
        if reset_fmem:
            self.fmem = [0] * len(self.fmem)

    def phase(self, obs, phase):
        r, st, fm = self.reg, self.store, self.fmem
        pc, steps, action = 0, 0, 0
        n = len(self.prog)
        while steps < self.cap and pc < n:
            w = self.prog[pc]
            op, a, b, c = w[0] % 19, w[1] % 8, w[2] % 8, w[3] % 8
            pc += 1
            steps += 1
            if op == 1:
                r[a] = obs & 0xFFFF
            elif op == 2:
                r[a] = phase
            elif op == 3:
                r[a] = w[2] % 64
            elif op == 4:
                r[a] = r[b]
            elif op == 5:
                r[a] = (r[b] + r[c]) % 65536
            elif op == 6:
                r[a] = (r[b] - r[c]) % 65536
            elif op == 7:
                pc += 1 if r[a] == 0 else 0
            elif op == 8:
                pc += 1 if r[a] != 0 else 0
            elif op == 9:
                pc += 1 if r[a] == r[b] else 0
            elif op == 10:
                pc += 1 if r[a] < r[b] else 0
            elif op == 11:
                if self.aff_store:
                    st[r[a] % len(st)] = r[b]
            elif op == 12:
                r[a] = st[r[b] % len(st)]
            elif op == 13:
                fm[r[a] % len(fm)] = r[b]
            elif op == 14:
                r[a] = fm[r[b] % len(fm)]
            elif op == 15:
                action = r[a] % self.R
                break
            elif op == 16:
                break
            elif op == 17:
                pc += w[3] % 16
            elif op == 18:
                r[a] = r[b] ^ r[c]
        self.instr += steps
        return action


def run_life(prog, store0, seed, life, K, R, E, T, F, cap,
             aff_store=True, reset_fmem=True, leaky=False):
    """Returns (rows, final_store, instructions). rows: one (ep, t, type, s, action, correct) per trial."""
    m = Machine(prog, store0, F, R, cap, aff_store)
    earlier, probed, repeated = set(), set(), set()
    rows = []
    for ep in range(E):
        m.reset_fast(reset_fmem)
        this_ep = set()
        for t in range(T):
            s = stimulus(seed, life, ep, t, K)
            ans = mapping(seed, life, s, R)
            if s in earlier and s not in this_ep and s not in probed:
                ttype = T_PROBE
                probed.add(s)
            elif s not in earlier and s in this_ep and s not in repeated:
                ttype = T_REPEAT
                repeated.add(s)
            elif s not in earlier and s not in this_ep:
                ttype = T_NOVEL
            else:
                ttype = T_OTHER
            action = m.phase(ans if leaky else s, 0)
            m.phase(ans, 1)
            this_ep.add(s)
            rows.append((ep, t, ttype, s, action, 1 if action == ans else 0))
        earlier |= this_ep
    return rows, m.store, m.instr
