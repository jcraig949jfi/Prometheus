"""W2-21 shared: a dynamic TAINT interpreter that re-implements z8.run + the DENSE patch (E5 -> LDIR, E7 -> LDDR)
semantics byte-for-byte, and carries a label set beside every register, flag and tape byte.

Labels: the initial register file 'B','C','D','E','H','L','A' and flags 'fz','fc' (the INHERITED context), plus
'SELF' (value came from the SELF world op = base/length of the running context) and 'SENSE'. Immediate bytes taken
from the tape inherit the tape byte's taint (empty for untouched code). Constants (XOR A / SUB A, LDIR's B=C=0)
carry no label. Control taint = union of the flag taint of every conditional branch evaluated, plus the taint of any
executed opcode / operand byte.

Effective copy operands on a 128-byte tape (address mask 127): src = L & 127 (H is irrelevant), dst = E & 127
(D irrelevant), count = B<<8|C (0 -> 65536, capped at the remaining budget). So the operand taints that matter are
t(L) for src, t(E) for dst, t(B)|t(C) for count.

Correctness is checked against z8.run (dense VM) in s1 on every copier in many contexts (tape, regs, flags, pc)."""
from __future__ import annotations

B, C, D, E, H, L, M, A = 0, 1, 2, 3, 4, 5, 6, 7
INIT = ("B", "C", "D", "E", "H", "L", None, "A")
REGSET = frozenset(("B", "C", "D", "E", "H", "L", "A", "fz", "fc"))
F0 = frozenset()


def trun(tape, base, length, sense, regs, fz, fc, pc, budget, mask_ops=42, dense=True, who=0, log=None):
    """Execute in place on `tape`. Returns dict(regs, fz, fc, pc, halted, copies=[...], ctrl, trace)."""
    mem = tape
    size = len(mem)
    am = size - 1
    r = [0] * 8 if regs is None else list(regs)
    t = [frozenset([INIT[i]]) if INIT[i] else F0 for i in range(8)]
    tz, tc = frozenset(["fz"]), frozenset(["fc"])
    mt = [F0] * size                      # tape taint
    ctrl = set()
    copies = []
    trace = []
    steps = 0

    def rd(a):
        return mem[a & am]

    def wr(a, v, tv):
        mem[a & am] = v & 0xFF
        mt[a & am] = tv

    halted = False
    while steps < budget:
        steps += 1
        pc &= am
        op = mem[pc]
        ctrl |= mt[pc]
        trace.append(pc)
        if 0x40 <= op < 0x80:
            if op == 0x76:
                halted = True
                break
            dst = (op >> 3) & 7; src = op & 7
            if src == M:
                v = rd((r[H] << 8) | r[L]); tv = mt[r[L] & am] | t[L]
            else:
                v = r[src]; tv = t[src]
            if dst == M:
                wr((r[H] << 8) | r[L], v, tv | t[L])
            else:
                r[dst] = v; t[dst] = tv
            pc += 1; continue
        if 0x80 <= op < 0xC0:
            src = op & 7
            if src == M:
                v = rd((r[H] << 8) | r[L]); tv = mt[r[L] & am] | t[L]
            else:
                v = r[src]; tv = t[src]
            kind = (op >> 3) & 7
            a = r[A]
            if kind == 0: x = a + v
            elif kind == 1: x = a + v + fc
            elif kind == 2: x = a - v
            elif kind == 3: x = a - v - fc
            elif kind == 4: x = a & v
            elif kind == 5: x = a ^ v
            elif kind == 6: x = a | v
            else: x = a - v
            res_t = t[A] | tv | (tc if kind in (1, 3) else F0)
            if src == A and kind in (2, 5, 7):     # SUB A / XOR A / CP A: constant result
                res_t = (tc if kind == 3 else F0)
            if src == A and kind == 3:
                res_t = tc
            fc = 1 if (x > 255 or x < 0) else 0
            x &= 0xFF
            fz = 1 if x == 0 else 0
            tz = tc = res_t
            if kind != 7:
                r[A] = x; t[A] = res_t
            pc += 1; continue
        lo = op & 7
        if lo == 4 and op < 0x40:
            d = (op >> 3) & 7
            if d == M:
                ad = (r[H] << 8) | r[L]; v = (rd(ad) + 1) & 0xFF; tv = mt[ad & am] | t[L]; wr(ad, v, tv)
            else:
                v = r[d] = (r[d] + 1) & 0xFF; tv = t[d]
            fz = 1 if v == 0 else 0; tz = tv
            pc += 1; continue
        if lo == 5 and op < 0x40:
            d = (op >> 3) & 7
            if d == M:
                ad = (r[H] << 8) | r[L]; v = (rd(ad) - 1) & 0xFF; tv = mt[ad & am] | t[L]; wr(ad, v, tv)
            else:
                v = r[d] = (r[d] - 1) & 0xFF; tv = t[d]
            fz = 1 if v == 0 else 0; tz = tv
            pc += 1; continue
        if lo == 6 and op < 0x40:
            d = (op >> 3) & 7
            v = rd(pc + 1); tv = mt[(pc + 1) & am]
            if d == M:
                wr((r[H] << 8) | r[L], v, tv | t[L])
            else:
                r[d] = v; t[d] = tv
            pc += 2; continue
        if op in (0x01, 0x11, 0x21, 0x31):
            v = rd(pc + 1) | (rd(pc + 2) << 8); tv = mt[(pc + 1) & am] | mt[(pc + 2) & am]
            hi_lo = {0x01: (B, C), 0x11: (D, E), 0x21: (H, L)}.get(op)
            if hi_lo:
                r[hi_lo[0]], r[hi_lo[1]] = (v >> 8) & 0xFF, v & 0xFF
                t[hi_lo[0]] = mt[(pc + 2) & am]; t[hi_lo[1]] = mt[(pc + 1) & am]
            pc += 3; continue
        if op == 0x02:
            wr((r[B] << 8) | r[C], r[A], t[A] | t[C]); pc += 1; continue
        if op == 0x12:
            wr((r[D] << 8) | r[E], r[A], t[A] | t[E]); pc += 1; continue
        if op == 0x0A:
            ad = (r[B] << 8) | r[C]; r[A] = rd(ad); t[A] = mt[ad & am] | t[C]; pc += 1; continue
        if op == 0x1A:
            ad = (r[D] << 8) | r[E]; r[A] = rd(ad); t[A] = mt[ad & am] | t[E]; pc += 1; continue
        if op in (0x03, 0x13, 0x23, 0x0B, 0x1B, 0x2B):
            hi, lon = (B, C) if op in (0x03, 0x0B) else ((D, E) if op in (0x13, 0x1B) else (H, L))
            v = ((r[hi] << 8) | r[lon]) + (1 if op in (0x03, 0x13, 0x23) else -1)
            v &= 0xFFFF
            r[hi], r[lon] = (v >> 8) & 0xFF, v & 0xFF
            t[hi] = t[hi] | t[lon]          # carry/borrow into the high byte
            pc += 1; continue
        if op in (0x18, 0x20, 0x28, 0x30, 0x38):
            e = rd(pc + 1); ctrl |= mt[(pc + 1) & am]
            if e > 127:
                e -= 256
            if op == 0x20 or op == 0x28:
                ctrl |= tz
            if op == 0x30 or op == 0x38:
                ctrl |= tc
            take = (op == 0x18 or (op == 0x20 and not fz) or (op == 0x28 and fz)
                    or (op == 0x30 and not fc) or (op == 0x38 and fc))
            pc = pc + 2 + e if take else pc + 2
            continue
        if op in (0xC3, 0xC2, 0xCA, 0xD2, 0xDA):
            v = rd(pc + 1) | (rd(pc + 2) << 8); ctrl |= mt[(pc + 1) & am] | mt[(pc + 2) & am]
            if op in (0xC2, 0xCA):
                ctrl |= tz
            if op in (0xD2, 0xDA):
                ctrl |= tc
            take = (op == 0xC3 or (op == 0xC2 and not fz) or (op == 0xCA and fz)
                    or (op == 0xD2 and not fc) or (op == 0xDA and fc))
            pc = v if take else pc + 3
            continue
        if op in (0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE):
            v = rd(pc + 1); tv = mt[(pc + 1) & am]
            a = r[A]
            if op == 0xC6: x = a + v
            elif op == 0xD6: x = a - v
            elif op == 0xE6: x = a & v
            elif op == 0xEE: x = a ^ v
            elif op == 0xF6: x = a | v
            else: x = a - v
            res_t = t[A] | tv
            if (op == 0xE6 and v == 0 and not tv) or (op == 0xF6 and v == 0xFF and not tv):
                res_t = F0
            fc = 1 if (x > 255 or x < 0) else 0
            x &= 0xFF
            fz = 1 if x == 0 else 0
            tz = tc = res_t
            if op != 0xFE:
                r[A] = x; t[A] = res_t
            pc += 2; continue
        if op == 0xDB:
            r[A] = 0; t[A] = F0; pc += 2; continue
        if op == 0xD3:
            pc += 2; continue
        if op == 0xED or (dense and op in (0xE5, 0xE7)):
            if op == 0xED:
                op2 = rd(pc + 1); ctrl |= mt[(pc + 1) & am]; pc += 2
            else:
                op2 = 0xB0 if op == 0xE5 else 0xB8; pc += 1
            if op2 in (0xB0, 0xB8):
                if not (mask_ops & 0x20):
                    continue
                step = 1 if op2 == 0xB0 else -1
                n = (r[B] << 8) | r[C]
                if n == 0:
                    n = 0x10000
                src = (r[H] << 8) | r[L]; dst = (r[D] << 8) | r[E]
                room = budget - steps
                if n > room:
                    n = room
                tsrc, tdst, tcnt = t[L], t[E], t[B] | t[C]
                rec = {"pc": (pc - (2 if op == 0xED else 1)) & am, "op": "LDIR" if step == 1 else "LDDR",
                       "byte": op, "src": src & am, "dst": dst & am, "n": n, "BC": (r[B] << 8) | r[C],
                       "t_src": sorted(tsrc), "t_dst": sorted(tdst), "t_cnt": sorted(tcnt),
                       "ctrl": sorted(ctrl), "step": steps, "regs": list(r)}
                copies.append(rec)
                for _ in range(n):
                    v = rd(src); wr(dst, v, mt[src & am] | tsrc | tdst | tcnt)
                    src += step; dst += step
                steps += n
                src &= 0xFFFF; dst &= 0xFFFF
                r[H], r[L] = (src >> 8) & 0xFF, src & 0xFF
                r[D], r[E] = (dst >> 8) & 0xFF, dst & 0xFF
                t[H] = t[L] = t[H] | tsrc | tcnt
                t[D] = t[E] = t[D] | tdst | tcnt
                r[B] = r[C] = 0; t[B] = t[C] = F0
                fz = 1; tz = F0
                continue
            if op2 == 0x32:
                if not (mask_ops & 0x02):
                    continue
                r[H], r[L] = (base >> 8) & 0xFF, base & 0xFF
                r[B], r[C] = (length >> 8) & 0xFF, length & 0xFF
                t[H] = t[L] = t[B] = t[C] = frozenset(["SELF"])
                continue
            if op2 == 0x33:
                if not (mask_ops & 0x04):
                    continue
                p = (pc - 2) & 0xFFFF
                r[H], r[L] = (p >> 8) & 0xFF, p & 0xFF
                t[H] = t[L] = frozenset(["GETPC"])
                continue
            if op2 == 0x34:
                if not (mask_ops & 0x08):
                    continue
                r[A] = sense & 0xFF; t[A] = frozenset(["SENSE"])
                continue
            if op2 in (0x30, 0x31, 0x35):
                # ALLOC/BIRTH/SPLIT: disabled under mask 42 (bit0, bit4 clear) -> no effect
                if (op2 in (0x30, 0x31) and (mask_ops & 0x01)) or (op2 == 0x35 and (mask_ops & 0x10)):
                    raise RuntimeError("ALLOC/BIRTH/SPLIT enabled: not modelled")
                continue
            continue
        pc += 1
    return {"regs": r, "fz": fz, "fc": fc, "pc": pc & am, "halted": halted, "copies": copies,
            "ctrl": sorted(ctrl), "trace": trace, "steps": steps, "taint": [sorted(x) for x in t]}


# ------------------------------------------------------------------ disassembler (z8 + DENSE)
RN = ("B", "C", "D", "E", "H", "L", "(HL)", "A")
ALU = ("ADD", "ADC", "SUB", "SBC", "AND", "XOR", "OR", "CP")


def dis1(g, pc):
    """(length, text) for the instruction at pc of the 128-byte tape / genome view g (wraps)."""
    sz = len(g)
    op = g[pc % sz]
    b1 = g[(pc + 1) % sz]; b2 = g[(pc + 2) % sz]
    if op == 0x76: return 1, "HALT"
    if 0x40 <= op < 0x80: return 1, "LD %s,%s" % (RN[(op >> 3) & 7], RN[op & 7])
    if 0x80 <= op < 0xC0: return 1, "%s A,%s" % (ALU[(op >> 3) & 7], RN[op & 7])
    lo = op & 7
    if op < 0x40 and lo == 4: return 1, "INC %s" % RN[(op >> 3) & 7]
    if op < 0x40 and lo == 5: return 1, "DEC %s" % RN[(op >> 3) & 7]
    if op < 0x40 and lo == 6: return 2, "LD %s,%02X" % (RN[(op >> 3) & 7], b1)
    if op in (0x01, 0x11, 0x21, 0x31): return 3, "LD %s,%04X" % ({1: "BC", 0x11: "DE", 0x21: "HL", 0x31: "SP"}[op], b1 | b2 << 8)
    if op == 0x02: return 1, "LD (BC),A"
    if op == 0x12: return 1, "LD (DE),A"
    if op == 0x0A: return 1, "LD A,(BC)"
    if op == 0x1A: return 1, "LD A,(DE)"
    m = {0x03: "INC BC", 0x13: "INC DE", 0x23: "INC HL", 0x0B: "DEC BC", 0x1B: "DEC DE", 0x2B: "DEC HL"}
    if op in m: return 1, m[op]
    if op in (0x18, 0x20, 0x28, 0x30, 0x38):
        e = b1 - 256 if b1 > 127 else b1
        return 2, "JR%s %+d (->%d)" % ({0x18: "", 0x20: " NZ", 0x28: " Z", 0x30: " NC", 0x38: " C"}[op], e, (pc + 2 + e) % sz)
    if op in (0xC3, 0xC2, 0xCA, 0xD2, 0xDA):
        return 3, "JP%s %04X" % ({0xC3: "", 0xC2: " NZ", 0xCA: " Z", 0xD2: " NC", 0xDA: " C"}[op], b1 | b2 << 8)
    if op in (0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE):
        return 2, "%s %02X" % ({0xC6: "ADD", 0xD6: "SUB", 0xE6: "AND", 0xEE: "XOR", 0xF6: "OR", 0xFE: "CP"}[op], b1)
    if op == 0xDB: return 2, "IN A"
    if op == 0xD3: return 2, "OUT A"
    if op == 0xE5: return 1, "LDIR(E5)"
    if op == 0xE7: return 1, "LDDR(E7)"
    if op == 0xED:
        w = {0xB0: "LDIR", 0xB8: "LDDR", 0x32: "SELF", 0x34: "SENSE", 0x33: "GETPC(off)", 0x30: "ALLOC(off)",
             0x31: "BIRTH(off)", 0x35: "SPLIT(off)"}.get(b1, "ED %02X(nop)" % b1)
        return 2, w
    return 1, "nop[%02X]" % op
