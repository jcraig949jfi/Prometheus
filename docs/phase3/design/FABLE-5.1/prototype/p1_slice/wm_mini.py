"""WM-mini and the RETAIN world: compiled integer kernels for the P1 calibration slice.

This is a PROTOTYPE of one slice of the Phase 3 design (RSE_ARCHITECTURE.md,
experiment P1). It is not the workspace machine and not a Prometheus engine.
It implements only what the slice needs:

  organism   a tiny stored-program machine with
               - fast state: 8 registers and a fast memory (reset by the harness
                 at every episode boundary)
               - persistent structure: a store that survives episode boundaries
               - genome: the program and the initial store
  world      RETAIN: a life of E episodes shares a hidden mapping
             stimulus -> response; feedback reveals the correct response after
             each trial; fast state is reset between episodes

Physics rules followed (REQUIREMENTS.md ORG-08, WLD-01):
  - integers only; register and cell values live in [0, 65535]
  - every instruction word decodes (total semantics)
  - no backward jumps and a step cap, so every phase halts
  - randomness is a counter-based hash of (seed, life, a, b): the same call
    always gives the same number, on any host

An independently written pure-Python implementation of the same semantics is
in oracle.py; differential_test.py compares the two bit for bit.
"""
import numpy as np
from numba import njit, prange

NREG = 8
MASK = 0xFFFF

# opcodes
NOP, IN, PH, SET, MOV, ADD, SUB, SKZ, SKNZ, SKEQ, SKLT, STW, STR, FW, FR, OUT, HALT, JMP, XOR = range(19)
NOPS = 19
OPNAMES = ["NOP", "IN", "PH", "SET", "MOV", "ADD", "SUB", "SKZ", "SKNZ", "SKEQ", "SKLT",
           "STW", "STR", "FW", "FR", "OUT", "HALT", "JMP", "XOR"]

# trial types
T_NOVEL = 0        # stimulus never seen before in this life
T_REPEAT = 1       # FIRST repeat, inside one episode, of a stimulus first met in that episode
T_PROBE = 2        # FIRST presentation in an episode of a stimulus seen in an EARLIER episode,
                   # counted once per stimulus per life (the BUILD probe)
T_OTHER = 3        # everything else (not scored by any ruler)
NTYPES = 4

# purposes for the hash (kept distinct so streams never collide)
P_MAP = 1_000_003
P_STIM = 2_000_003

_C1 = np.uint64(0x9E3779B97F4A7C15)
_C2 = np.uint64(0xBF58476D1CE4E5B9)
_C3 = np.uint64(0x94D049BB133111EB)
_S30 = np.uint64(30)
_S27 = np.uint64(27)
_S31 = np.uint64(31)


@njit(cache=True)
def _sm(x):
    """One splitmix64 step on a uint64."""
    z = x + _C1
    z = (z ^ (z >> _S30)) * _C2
    z = (z ^ (z >> _S27)) * _C3
    return z ^ (z >> _S31)


@njit(cache=True)
def khash(seed, life, a, b):
    """Counter-based hash: uint64 from four non-negative integers."""
    h = _sm(np.uint64(seed))
    h = _sm(h ^ np.uint64(life))
    h = _sm(h ^ np.uint64(a))
    h = _sm(h ^ np.uint64(b))
    return h


@njit(cache=True)
def mapping(seed, life, s, R):
    """The hidden response for stimulus s in this life: uniform on 0..R-1."""
    return np.int64(khash(seed, life, P_MAP, s) % np.uint64(R))


@njit(cache=True)
def stimulus(seed, life, ep, t, K):
    """The stimulus shown at trial t of episode ep: uniform on 0..K-1."""
    return np.int64(khash(seed, life, P_STIM + ep, t) % np.uint64(K))


@njit(cache=True)
def run_phase(prog, n, reg, fmem, store, obs, phase, R, cap, aff_store):
    """Run the program once from pc 0. Returns (action, instructions executed).

    The phase ends at OUT, at HALT, when the program runs off its end, or at the
    step cap. Without an OUT the action is 0.
    """
    S = store.shape[0]
    F = fmem.shape[0]
    pc = 0
    steps = 0
    action = 0
    while steps < cap and pc < n:
        op = prog[pc, 0] % NOPS
        a = prog[pc, 1] % NREG
        b = prog[pc, 2] % NREG
        c = prog[pc, 3] % NREG
        pc += 1
        steps += 1
        if op == NOP:
            pass
        elif op == IN:
            reg[a] = obs & MASK
        elif op == PH:
            reg[a] = phase
        elif op == SET:
            reg[a] = prog[pc - 1, 2] % 64
        elif op == MOV:
            reg[a] = reg[b]
        elif op == ADD:
            reg[a] = (reg[b] + reg[c]) & MASK
        elif op == SUB:
            reg[a] = (reg[b] - reg[c]) & MASK
        elif op == SKZ:
            if reg[a] == 0:
                pc += 1
        elif op == SKNZ:
            if reg[a] != 0:
                pc += 1
        elif op == SKEQ:
            if reg[a] == reg[b]:
                pc += 1
        elif op == SKLT:
            if reg[a] < reg[b]:
                pc += 1
        elif op == STW:
            if aff_store:
                store[reg[a] % S] = reg[b]
        elif op == STR:
            reg[a] = store[reg[b] % S]
        elif op == FW:
            fmem[reg[a] % F] = reg[b]
        elif op == FR:
            reg[a] = fmem[reg[b] % F]
        elif op == OUT:
            action = reg[a] % R
            break
        elif op == HALT:
            break
        elif op == JMP:
            pc += prog[pc - 1, 3] % 16
        else:  # XOR
            reg[a] = reg[b] ^ reg[c]
    return action, steps


@njit(cache=True)
def run_episode(prog, n, reg, fmem, store, seen_prev, probed, repeated,
                seed, life, ep, K, R, T, cap, aff_store, leaky, out):
    """Run one episode. The CALLER (the harness) is responsible for resetting
    fast state before the call. Writes one row per trial into out[t, :]:
    (trial type, stimulus, action, correct). Returns instructions executed.

    seen_prev[s]  1 if s was shown in an earlier episode of this life
    probed[s]     1 if the BUILD probe for s was already taken in this life
    repeated[s]   1 if the HOLD repeat for s was already taken in this life
    leaky         fire-test switch: the stimulus observation IS the answer
    """
    seen_ep = np.zeros(K, dtype=np.int64)
    instr = 0
    for t in range(T):
        s = stimulus(seed, life, ep, t, K)
        m = mapping(seed, life, s, R)
        if seen_prev[s] == 1 and seen_ep[s] == 0 and probed[s] == 0:
            ttype = T_PROBE
            probed[s] = 1
        elif seen_prev[s] == 0 and seen_ep[s] == 1 and repeated[s] == 0:
            ttype = T_REPEAT
            repeated[s] = 1
        elif seen_prev[s] == 0 and seen_ep[s] == 0:
            ttype = T_NOVEL
        else:
            ttype = T_OTHER
        obs = m if leaky else s
        action, st = run_phase(prog, n, reg, fmem, store, obs, 0, R, cap, aff_store)
        instr += st
        _, st = run_phase(prog, n, reg, fmem, store, m, 1, R, cap, aff_store)
        instr += st
        seen_ep[s] = 1
        out[t, 0] = ttype
        out[t, 1] = s
        out[t, 2] = action
        out[t, 3] = 1 if action == m else 0
    for s in range(K):
        if seen_ep[s] == 1:
            seen_prev[s] = 1
    return instr


@njit(cache=True)
def eval_life(prog, n, store0, seed, life, K, R, E, T, F, cap, aff_store, reset_fmem, leaky, counts):
    """Run one whole life under the standard harness and add to counts[type, 0:2] = (n, k).

    reset_fmem=False is the BROKEN harness used by a fire test: fast memory is
    not cleared at episode boundaries. Returns instructions executed.
    """
    reg = np.zeros(NREG, dtype=np.int64)
    fmem = np.zeros(F, dtype=np.int64)
    store = store0.copy()
    seen_prev = np.zeros(K, dtype=np.int64)
    probed = np.zeros(K, dtype=np.int64)
    repeated = np.zeros(K, dtype=np.int64)
    out = np.zeros((T, 4), dtype=np.int64)
    instr = 0
    for ep in range(E):
        for i in range(NREG):
            reg[i] = 0
        if reset_fmem:
            for i in range(F):
                fmem[i] = 0
        instr += run_episode(prog, n, reg, fmem, store, seen_prev, probed, repeated,
                             seed, life, ep, K, R, T, cap, aff_store, leaky, out)
        for t in range(T):
            counts[out[t, 0], 0] += 1
            counts[out[t, 0], 1] += out[t, 3]
    return instr


@njit(parallel=True, cache=True)
def eval_lives(prog, n, store0, seed, life0, nlives, K, R, E, T, F, cap, aff_store, reset_fmem, leaky):
    """Evaluate one organism on lives life0 .. life0+nlives-1 in parallel.

    Returns (counts[type, 0:2] summed over lives, per-life probe (n, k), instructions).
    """
    per = np.zeros((nlives, NTYPES, 2), dtype=np.int64)
    ins = np.zeros(nlives, dtype=np.int64)
    for j in prange(nlives):
        ins[j] = eval_life(prog, n, store0, seed, life0 + j, K, R, E, T, F, cap,
                           aff_store, reset_fmem, leaky, per[j])
    total = np.zeros((NTYPES, 2), dtype=np.int64)
    for j in range(nlives):
        for ty in range(NTYPES):
            total[ty, 0] += per[j, ty, 0]
            total[ty, 1] += per[j, ty, 1]
    return total, per[:, T_PROBE, :].copy(), ins.sum()


@njit(cache=True)
def probe_fitness(prog, n, store0, seed, life0, nlives, K, R, E, T, F, cap):
    """Search fitness: number of correct BUILD probes over a block of lives."""
    counts = np.zeros((NTYPES, 2), dtype=np.int64)
    for j in range(nlives):
        eval_life(prog, n, store0, seed, life0 + j, K, R, E, T, F, cap, True, True, False, counts)
    return counts[T_PROBE, 1], counts[T_PROBE, 0]
