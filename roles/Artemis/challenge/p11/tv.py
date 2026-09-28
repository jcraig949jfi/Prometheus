"""Toy VM (PREREG_P11.md s2.3) with the interface p11.py expects of `z8`.

make(alphabet) returns a module-like namespace (Ctx, run, OWN, ARENA) whose painter opcodes 0x10-0x1F are active
only when in `alphabet`. Decoding is strand-symmetric: d(x) = x if x < 0x80 else x ^ 0xFF.
"""
from __future__ import annotations

import hashlib
from types import SimpleNamespace

OWN, ARENA = 0, 1


class Ctx:
    def __init__(self, mem, base, length, policy=OWN, rng=None, copy_mut_rate=0.0, sense=0, **_kw):
        self.mem, self.size, self.base, self.length = mem, len(mem), base, length
        self.policy, self.rng, self.copy_mut_rate, self.sense = policy, rng, copy_mut_rate, sense
        self.prov = self.prov_lit = None
        self.who = 0
        self.regs, self.fz, self.fc = None, 0, 0
        self.writes = self.writes_other = self.writes_own = self.writes_blocked = 0
        self.ops = 0
        self.halted = False


def _dec(x):
    return x if x < 0x80 else x ^ 0xFF


def _stream(data, n):
    out = bytearray()
    c = 0
    while len(out) < n:
        out += hashlib.sha256(bytes(data) + c.to_bytes(4, "big")).digest()
        c += 1
    return bytes(out[:n])


def make(alphabet=frozenset(), ops=None):
    """ops: active non-painter decoded opcodes (AMENDMENT 2026-09-28b B2); None = all (pre-repair shared ISA)."""
    alphabet = frozenset(alphabet)
    ops = None if ops is None else frozenset(ops)

    def run(ctx, pc, budget, ops_enabled=0xFF):
        mem, T, base, n = ctx.mem, ctx.size, ctx.base, ctx.length
        R = W = K = 0
        steps = 0
        cmr, rng = ctx.copy_mut_rate, ctx.rng

        def wr(a, v):
            a %= T
            if ctx.policy == OWN and not (base <= a < base + n):
                ctx.writes_blocked += 1
                return
            v &= 0xFF
            if ctx.prov is not None:
                if mem[a] != v:
                    ctx.prov[a] = ctx.who
                ctx.prov_lit[a] = ctx.who
            mem[a] = v
            ctx.writes += 1
            if base <= a < base + n:
                ctx.writes_own += 1
            else:
                ctx.writes_other += 1

        def cpy(v):
            if cmr and rng is not None and rng.random() < cmr:
                v ^= 1 << rng.randrange(8)
            return v

        while steps < budget:
            pc %= T
            d = _dec(mem[pc])
            steps += 1
            if ops is not None and d not in ops and not (0x10 <= d <= 0x1F):
                d = 0x00
            if d == 0x01:
                R, W, K = base, (base + n) % T, 0
            elif d in (0x02, 0x03):
                if K < n:
                    v = mem[R % T]
                    wr(W, cpy(v ^ 0xFF if d == 0x03 else v))
                    R, W, K = R + 1, W + 1, K + 1
            elif d == 0x04:
                if K < n:
                    pc -= 1
                    continue
            elif d == 0x05:
                ctx.halted = True
                break
            elif d == 0x06:
                R = base ^ n
                W = (R + 2 * n) % T
                for j in range(n):
                    wr(W + j, cpy(mem[(R + j) % T]))
                steps += n - 1
            elif d == 0x07:
                a = (base + n + 5) % T
                wr(a, mem[a] + 1)
            elif 0x10 <= d <= 0x1F and d in alphabet:
                for j in range(n):
                    wr(base + n + j, d)
                steps += n - 1
                ctx.halted = True
                break
            elif d == 0x20:
                for j in range(n):
                    wr(base + n + j, 0x20 if j % 2 == 0 else 0x21)
                steps += n - 1
                ctx.halted = True
                break
            elif d == 0x40:
                own = bytes(mem[(base + j) % T] for j in range(n))
                h = _stream(own, n - 1)
                wr(base + n, 0x40)
                for j in range(n - 1):
                    wr(base + n + 1 + j, h[j])
                steps += n - 1
                ctx.halted = True
                break
            pc += 1
        ctx.ops += steps
        return pc % T

    return SimpleNamespace(Ctx=Ctx, run=run, OWN=OWN, ARENA=ARENA, alphabet=alphabet, ops=ops)
