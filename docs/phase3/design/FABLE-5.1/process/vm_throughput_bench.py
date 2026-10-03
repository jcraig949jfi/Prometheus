"""Micro-benchmark: throughput of a small integer register VM under Numba on this host.

Purpose: ground the compute requirements of the Phase 3 design in a measured
number instead of a guess. This is NOT a Prometheus engine and nothing here is
science. One toy interpreter, random programs, fixed step budget.

VM: 8 int64 registers, 64-cell memory, 16 opcodes (arith, load/store,
conditional skip, jump). Each instruction is 4 small ints (op, a, b, c).
"""
import time
import numpy as np
from numba import njit, prange


@njit(cache=False)
def run_one(prog, steps, seed):
    n = prog.shape[0]
    reg = np.zeros(8, dtype=np.int64)
    mem = np.zeros(64, dtype=np.int64)
    reg[0] = seed
    pc = 0
    acc = 0
    for _ in range(steps):
        op = prog[pc, 0]
        a = prog[pc, 1]
        b = prog[pc, 2]
        c = prog[pc, 3]
        pc += 1
        if op == 0:
            reg[a] = reg[b] + reg[c]
        elif op == 1:
            reg[a] = reg[b] - reg[c]
        elif op == 2:
            reg[a] = reg[b] ^ reg[c]
        elif op == 3:
            reg[a] = reg[b] & reg[c]
        elif op == 4:
            reg[a] = (reg[b] << 1) | (reg[c] & 1)
        elif op == 5:
            reg[a] = mem[reg[b] & 63]
        elif op == 6:
            mem[reg[a] & 63] = reg[b]
        elif op == 7:
            if reg[a] > reg[b]:
                pc += 1
        elif op == 8:
            if reg[a] == reg[b]:
                pc += 1
        elif op == 9:
            pc = (pc + c) % n
        elif op == 10:
            reg[a] = b * 8 + c
        elif op == 11:
            reg[a] = reg[b] >> 1
        elif op == 12:
            reg[a] = reg[b] * 3 + 1
        elif op == 13:
            reg[a] = -reg[b]
        elif op == 14:
            mem[(reg[a] + c) & 63] ^= reg[b]
        else:
            reg[a] = reg[a] + 1
        if pc >= n:
            pc = 0
        acc ^= reg[a & 7]
    return acc


@njit(parallel=True, cache=False)
def run_many(progs, steps):
    m = progs.shape[0]
    out = np.zeros(m, dtype=np.int64)
    for i in prange(m):
        out[i] = run_one(progs[i], steps, i)
    return out


def main():
    rng = np.random.default_rng(0)
    plen = 64
    one = np.empty((plen, 4), dtype=np.int64)
    one[:, 0] = rng.integers(0, 16, plen)
    one[:, 1:] = rng.integers(0, 8, (plen, 3))
    run_one(one, 10, 1)  # compile
    steps = 400_000_000
    t = time.perf_counter()
    run_one(one, steps, 1)
    dt = time.perf_counter() - t
    print("single core: %.1f M instr/s (%d steps in %.3f s)" % (steps / dt / 1e6, steps, dt))

    m = 4096
    progs = np.empty((m, plen, 4), dtype=np.int64)
    progs[:, :, 0] = rng.integers(0, 16, (m, plen))
    progs[:, :, 1:] = rng.integers(0, 8, (m, plen, 3))
    run_many(progs[:16], 10)  # compile
    steps = 3_000_000
    t = time.perf_counter()
    run_many(progs, steps)
    dt = time.perf_counter() - t
    total = m * steps
    print("all threads: %.1f M instr/s (%d organisms x %d steps in %.3f s)" % (total / dt / 1e6, m, steps, dt))
    print("lifetimes/day at 1e5 instr per lifetime: %.2e" % (total / dt * 86400 / 1e5))


if __name__ == "__main__":
    main()
