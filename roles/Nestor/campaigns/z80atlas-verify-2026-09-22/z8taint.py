"""Material provenance for the Z8 VM: `run_tainted`, a line-for-line copy of `z8.run`
that additionally carries a TAG with every byte value (C9-D14 repair, H3 ruler R3).

A tag names the niche in which a byte VALUE was created. It flows with the data:
  * a byte loaded from memory into a register keeps the memory byte's tag;
  * a register copied to a register or stored to memory carries its tag with it;
  * an immediate operand carries the tag of the genome byte it was read from;
  * LDIR/LDDR copy each source byte's tag to the destination (a copy-mutation flip
    makes that byte new material);
  * any COMPUTED value (ALU result, INC/DEC, task input, SENSE, SELF/GETPC, ALLOC
    return, pointer arithmetic) is new material and takes the executing organism's
    niche, `ctx.here`.
So a byte's tag answers "in which niche was this value made", following the actual
movement of material rather than the identity of whoever holds it.

`run_tainted` must compute EXACTLY what `z8.run` computes; the tags are observation
only. tests/test_h3_material.py checks bit identity on random programs, both policies.
"""
from __future__ import annotations

from z8 import (A, B, C, D, E, H, L, M, OP_ALLOC, OP_BIRTH, OP_GETPC, OP_LDDR, OP_LDIR,
                OP_SELF, OP_SENSE, OP_SPLIT, _writable)

UNKNOWN = 255


def run_tainted(ctx, pc, budget, ops_enabled=0xFF, orig=None, here=UNKNOWN, reg_taint=None):
    """As z8.run, plus tags. `orig` is a bytearray of tags parallel to ctx.mem; `here` is
    the executing organism's niche; `reg_taint` its register tags (None = all `here`).
    Returns (pc, reg_taint)."""
    mem = ctx.mem
    size = ctx.size
    mask = size - 1
    pow2 = (size & mask) == 0
    r = [0] * 8 if ctx.regs is None else list(ctx.regs)
    tr = [here] * 8 if reg_taint is None else list(reg_taint)
    fz = ctx.fz
    fc = ctx.fc
    steps = 0
    rng = ctx.rng
    cmr = ctx.copy_mut_rate

    def wr(addr, val, tg):
        a = addr & mask if pow2 else addr % size
        if not _writable(ctx, a):
            ctx.writes_blocked += 1
            return
        pv = ctx.prov
        if pv is None:
            mem[a] = val & 0xFF
        else:
            v8 = val & 0xFF
            if mem[a] != v8:
                pv[a] = ctx.who
            mem[a] = v8
            ctx.prov_lit[a] = ctx.who
        orig[a] = tg
        ctx.writes += 1
        b = ctx.base
        if b <= a < b + ctx.length:
            ctx.writes_own += 1
            if a != b:
                ctx.self_overwrites += 1
        else:
            ctx.writes_other += 1
        if ctx.max_addr_written < 0 or a > ctx.max_addr_written:
            ctx.max_addr_written = a
        if ctx.min_addr_written < 0 or a < ctx.min_addr_written:
            ctx.min_addr_written = a

    def ad(addr):
        return addr & mask if pow2 else addr % size

    def rd(addr):
        return mem[ad(addr)]

    def tg(addr):
        return orig[ad(addr)]

    while steps < budget:
        steps += 1
        pc = pc & mask if pow2 else pc % size
        op = mem[pc]

        if 0x40 <= op < 0x80:
            if op == 0x76:
                ctx.halted = True
                ctx.ops += steps
                ctx.regs, ctx.fz, ctx.fc = r, fz, fc
                return pc, tr
            dst = (op >> 3) & 7
            src = op & 7
            hl = (r[H] << 8) | r[L]
            if src == M:
                v, t = rd(hl), tg(hl)
            else:
                v, t = r[src], tr[src]
            if dst == M:
                wr(hl, v, t)
            else:
                r[dst], tr[dst] = v, t
            pc += 1
            continue

        if 0x80 <= op < 0xC0:
            src = op & 7
            v = rd((r[H] << 8) | r[L]) if src == M else r[src]
            kind = (op >> 3) & 7
            a = r[A]
            if kind == 0:
                t = a + v
            elif kind == 1:
                t = a + v + fc
            elif kind == 2:
                t = a - v
            elif kind == 3:
                t = a - v - fc
            elif kind == 4:
                t = a & v
            elif kind == 5:
                t = a ^ v
            elif kind == 6:
                t = a | v
            else:
                t = a - v
            fc = 1 if (t > 255 or t < 0) else 0
            t &= 0xFF
            fz = 1 if t == 0 else 0
            if kind != 7:
                r[A], tr[A] = t, here
            pc += 1
            continue

        lo = op & 7
        if lo == 4 and op < 0x40:
            d = (op >> 3) & 7
            if d == M:
                addr = (r[H] << 8) | r[L]
                v = (rd(addr) + 1) & 0xFF
                wr(addr, v, here)
            else:
                v = r[d] = (r[d] + 1) & 0xFF
                tr[d] = here
            fz = 1 if v == 0 else 0
            pc += 1
            continue
        if lo == 5 and op < 0x40:
            d = (op >> 3) & 7
            if d == M:
                addr = (r[H] << 8) | r[L]
                v = (rd(addr) - 1) & 0xFF
                wr(addr, v, here)
            else:
                v = r[d] = (r[d] - 1) & 0xFF
                tr[d] = here
            fz = 1 if v == 0 else 0
            pc += 1
            continue
        if lo == 6 and op < 0x40:
            d = (op >> 3) & 7
            n, t = rd(pc + 1), tg(pc + 1)
            if d == M:
                wr((r[H] << 8) | r[L], n, t)
            else:
                r[d], tr[d] = n, t
            pc += 2
            continue

        if op == 0x01 or op == 0x11 or op == 0x21 or op == 0x31:
            n = rd(pc + 1) | (rd(pc + 2) << 8)
            tlo, thi = tg(pc + 1), tg(pc + 2)
            if op == 0x01:
                r[B], r[C] = (n >> 8) & 0xFF, n & 0xFF
                tr[B], tr[C] = thi, tlo
            elif op == 0x11:
                r[D], r[E] = (n >> 8) & 0xFF, n & 0xFF
                tr[D], tr[E] = thi, tlo
            elif op == 0x21:
                r[H], r[L] = (n >> 8) & 0xFF, n & 0xFF
                tr[H], tr[L] = thi, tlo
            pc += 3
            continue
        if op == 0x02:
            wr((r[B] << 8) | r[C], r[A], tr[A]); pc += 1; continue
        if op == 0x12:
            wr((r[D] << 8) | r[E], r[A], tr[A]); pc += 1; continue
        if op == 0x0A:
            addr = (r[B] << 8) | r[C]
            r[A], tr[A] = rd(addr), tg(addr); pc += 1; continue
        if op == 0x1A:
            addr = (r[D] << 8) | r[E]
            r[A], tr[A] = rd(addr), tg(addr); pc += 1; continue
        if op == 0x03 or op == 0x13 or op == 0x23 or op == 0x0B or op == 0x1B or op == 0x2B:
            hi, lon = (B, C) if op in (0x03, 0x0B) else ((D, E) if op in (0x13, 0x1B) else (H, L))
            v = ((r[hi] << 8) | r[lon]) + (1 if op in (0x03, 0x13, 0x23) else -1)
            v &= 0xFFFF
            r[hi], r[lon] = (v >> 8) & 0xFF, v & 0xFF
            tr[hi] = tr[lon] = here
            pc += 1
            continue

        if op == 0x18 or op == 0x20 or op == 0x28 or op == 0x30 or op == 0x38:
            e = rd(pc + 1)
            if e > 127:
                e -= 256
            take = (op == 0x18 or (op == 0x20 and not fz) or (op == 0x28 and fz)
                    or (op == 0x30 and not fc) or (op == 0x38 and fc))
            pc = pc + 2 + e if take else pc + 2
            continue

        if op == 0xC3 or op == 0xC2 or op == 0xCA or op == 0xD2 or op == 0xDA:
            n = rd(pc + 1) | (rd(pc + 2) << 8)
            take = (op == 0xC3 or (op == 0xC2 and not fz) or (op == 0xCA and fz)
                    or (op == 0xD2 and not fc) or (op == 0xDA and fc))
            pc = n if take else pc + 3
            continue

        if op == 0xC6 or op == 0xD6 or op == 0xE6 or op == 0xEE or op == 0xF6 or op == 0xFE:
            v = rd(pc + 1)
            a = r[A]
            if op == 0xC6:
                t = a + v
            elif op == 0xD6:
                t = a - v
            elif op == 0xE6:
                t = a & v
            elif op == 0xEE:
                t = a ^ v
            elif op == 0xF6:
                t = a | v
            else:
                t = a - v
            fc = 1 if (t > 255 or t < 0) else 0
            t &= 0xFF
            fz = 1 if t == 0 else 0
            if op != 0xFE:
                r[A], tr[A] = t, here
            pc += 2
            continue

        if op == 0xDB:
            if ctx.in_cursor < len(ctx.inputs):
                r[A] = ctx.inputs[ctx.in_cursor] & 0xFF
                ctx.in_cursor += 1
                ctx.in_reads += 1
            else:
                r[A] = 0
            tr[A] = here
            pc += 2
            continue
        if op == 0xD3:
            if ctx.in_reads < ctx.out_gate_reads:
                ctx.out_suppressed += 1
                pc += 2
                continue
            if ctx.in_reads_at_first_out < 0:
                ctx.in_reads_at_first_out = ctx.in_reads
            if len(ctx.outputs) < 64:
                ctx.outputs.append(r[A])
            ctx.out_writes += 1
            pc += 2
            continue

        if op == 0xED:
            op2 = rd(pc + 1)
            pc += 2
            if op2 == OP_LDIR or op2 == OP_LDDR:
                if not (ops_enabled & 0x20):
                    continue
                ctx.world_op_calls += 1
                step = 1 if op2 == OP_LDIR else -1
                n = (r[B] << 8) | r[C]
                if n == 0:
                    n = 0x10000
                src = (r[H] << 8) | r[L]
                dst = (r[D] << 8) | r[E]
                room = budget - steps
                if n > room:
                    n = room
                    ctx.budget_exhausted = True
                for _ in range(n):
                    v, t = rd(src), tg(src)
                    if cmr and rng is not None and rng.random() < cmr:
                        v ^= 1 << rng.randrange(8)
                        ctx.copy_errors += 1
                        t = here
                    wr(dst, v, t)
                    src += step
                    dst += step
                    ctx.copy_bytes += 1
                steps += n
                src &= 0xFFFF
                dst &= 0xFFFF
                r[H], r[L] = (src >> 8) & 0xFF, src & 0xFF
                r[D], r[E] = (dst >> 8) & 0xFF, dst & 0xFF
                r[B] = r[C] = 0
                tr[H] = tr[L] = tr[D] = tr[E] = tr[B] = tr[C] = here
                fz = 1
                continue
            if op2 == OP_ALLOC:
                if not (ops_enabled & 0x01):
                    continue
                ctx.world_op_calls += 1
                ctx.alloc_calls += 1
                n = (r[B] << 8) | r[C]
                got = ctx.on_alloc(ctx, n) if ctx.on_alloc is not None else None
                if got is None:
                    ctx.alloc_fails += 1
                    fz = 0
                else:
                    r[D], r[E] = (got >> 8) & 0xFF, got & 0xFF
                    tr[D] = tr[E] = here
                    fz = 1
                continue
            if op2 == OP_BIRTH or op2 == OP_SPLIT:
                if op2 == OP_BIRTH and not (ops_enabled & 0x01):
                    continue
                if op2 == OP_SPLIT and not (ops_enabled & 0x10):
                    continue
                ctx.world_op_calls += 1
                ctx.birth_calls += 1
                dst = (r[D] << 8) | r[E]
                n = r[C] if op2 == OP_SPLIT else ((r[B] << 8) | r[C])
                ok = ctx.on_birth(ctx, dst, n, op2 == OP_SPLIT) if ctx.on_birth is not None else False
                if ok:
                    ctx.births += 1
                    fz = 1
                else:
                    fz = 0
                continue
            if op2 == OP_SELF:
                if not (ops_enabled & 0x02):
                    continue
                ctx.world_op_calls += 1
                r[H], r[L] = (ctx.base >> 8) & 0xFF, ctx.base & 0xFF
                r[B], r[C] = (ctx.length >> 8) & 0xFF, ctx.length & 0xFF
                tr[H] = tr[L] = tr[B] = tr[C] = here
                continue
            if op2 == OP_GETPC:
                if not (ops_enabled & 0x04):
                    continue
                ctx.world_op_calls += 1
                p = (pc - 2) & 0xFFFF
                r[H], r[L] = (p >> 8) & 0xFF, p & 0xFF
                tr[H] = tr[L] = here
                continue
            if op2 == OP_SENSE:
                if not (ops_enabled & 0x08):
                    continue
                ctx.world_op_calls += 1
                r[A] = ctx.sense & 0xFF
                tr[A] = here
                continue
            continue

        pc += 1

    ctx.ops += steps
    ctx.budget_exhausted = True
    ctx.regs, ctx.fz, ctx.fc = r, fz, fc
    return (pc & mask if pow2 else pc % size), tr
