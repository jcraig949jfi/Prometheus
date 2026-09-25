"""Z8: a byte-addressable, Z80-like instruction substrate for the Z80 x Atlas campaign.

WHY THIS SUBSTRATE. The campaign needs a representation in which (a) heredity can be
ENDOGENOUS - an organism persists only by executing behaviour that writes its own bytes
somewhere a descendant can run from - and (b) mutation can alter both algorithm and
architecture, because instructions are variable length and a byte-level edit shifts the
reading frame, so the same bytes decode as different programs. A fixed-width word VM
(Proteus) cannot do (b); that contrast is itself a campaign factor.

NOT A Z80 EMULATOR. The relevant properties are preserved, not the ISA:
  byte-addressable executable memory; variable-length instructions; register/state ops;
  control flow (relative and absolute jumps, conditional on Z/C); memory read and write
  through register pointers; a block-copy primitive (LDIR, two bytes - the reason short
  self-replicators exist at all); NO multiplication and no privileged copy operator;
  every undefined byte decodes as a one-byte NOP, so the opcode space is dense and
  mutation lands on a runnable program rather than a fault.

WORLD OPS. Endogenous reproduction needs the organism, not the runner, to cause
descendants. The ED-prefixed world ops are the only channel:
  ED 30 ALLOC   request a child buffer of BC bytes; DE = base, Z set on success
  ED 31 BIRTH   declare the child at [DE, DE+BC)
  ED 32 SELF    HL = own base, BC = own length          (self_location = PRIMITIVE)
  ED 33 GETPC   HL = current pc                         (self_location = PC_RELATIVE)
  ED 34 SENSE   A = a world sense byte
  ED 35 SPLIT   partial birth: child = [DE, DE+C)       (ENDOGENOUS_PARTIAL)
  ED B0 LDIR    copy BC bytes HL -> DE, both ascending
  ED B8 LDDR    copy BC bytes HL -> DE, both descending
Which of these exist in a given run is a FACTOR (see grammar.py: self_location,
copy_primitive, world_ops). Removing ED 32 and ED B0 does not make replication
impossible - it makes it longer, which is the accessibility question applied to heredity.

SANDBOX. Every write goes through one policy: OWN (writes outside the organism's own
span are dropped and counted), ARENA (any address in the arena is writable - the pair
tape), FREE (only addresses the world marks free). Out-of-policy writes are never
silently allowed; they are counted, and anticheat.py reads those counters.

ANSWER-BEFORE-READ. The machine records how many task input bytes had been consumed
when the first answer byte was emitted. That is cycle 8's probe, and here it is both an
accessibility coordinate and an evaluator-leakage detector.

Computational scope: integer programs on a bounded virtual machine. No biological
content of any kind.
"""
from __future__ import annotations

# ---------------------------------------------------------------- register file
# Z80 order: 0=B 1=C 2=D 3=E 4=H 5=L 6=(HL) 7=A
B, C, D, E, H, L, M, A = 0, 1, 2, 3, 4, 5, 6, 7
REGNAMES = ("B", "C", "D", "E", "H", "L", "(HL)", "A")

# sandbox policies
OWN, ARENA, FREE = 0, 1, 2

# world op second bytes
OP_ALLOC, OP_BIRTH, OP_SELF, OP_GETPC, OP_SENSE, OP_SPLIT = 0x30, 0x31, 0x32, 0x33, 0x34, 0x35
OP_LDIR, OP_LDDR = 0xB0, 0xB8


class Ctx:
    """Everything the machine may touch outside its own registers.

    The world supplies one Ctx per executing organism. The machine never allocates,
    never births and never reads task input by itself: it calls back into the world,
    so a treatment that declares reproduction EXOGENOUS simply supplies a Ctx whose
    alloc/birth callbacks refuse, and the refusal is recorded rather than hidden.
    """

    __slots__ = ("mem", "size", "base", "length", "policy", "free_lo", "free_hi",
                 "inputs", "outputs", "in_cursor", "on_alloc", "on_birth", "sense",
                 "copy_mut_rate", "rng", "ops", "writes", "writes_own", "writes_other",
                 "writes_blocked", "copy_bytes", "copy_errors", "births", "alloc_calls",
                 "alloc_fails", "birth_calls", "in_reads", "out_writes",
                 "in_reads_at_first_out", "halted", "world_op_calls", "max_addr_written",
                 "min_addr_written", "self_overwrites", "budget_exhausted",
                 "regs", "fz", "fc",
                 "prov", "prov_lit", "who", "ev")      # FORENSIC TELEMETRY (2026-09-23)

    def __init__(self, mem, base, length, policy=OWN, inputs=(), rng=None,
                 on_alloc=None, on_birth=None, sense=0, copy_mut_rate=0.0,
                 free_lo=0, free_hi=0):
        self.mem = mem
        self.size = len(mem)
        self.base = base
        self.length = length
        self.policy = policy
        self.free_lo = free_lo
        self.free_hi = free_hi
        self.inputs = list(inputs)
        self.outputs = []
        self.in_cursor = 0
        self.on_alloc = on_alloc
        self.on_birth = on_birth
        self.sense = sense
        self.copy_mut_rate = copy_mut_rate
        self.rng = rng
        self.ops = 0
        self.writes = 0
        self.writes_own = 0
        self.writes_other = 0
        self.writes_blocked = 0
        self.copy_bytes = 0
        self.copy_errors = 0
        self.births = 0
        self.alloc_calls = 0
        self.alloc_fails = 0
        self.birth_calls = 0
        self.in_reads = 0
        self.out_writes = 0
        self.in_reads_at_first_out = -1
        self.halted = False
        self.budget_exhausted = False
        self.world_op_calls = 0
        self.max_addr_written = -1
        self.min_addr_written = -1
        self.self_overwrites = 0
        # CPU state that may persist across time slices. A world that declares register
        # state non-heritable simply passes None here and anticheat checks that it did.
        self.regs = None
        self.fz = 0
        self.fc = 0
        # FORENSIC TELEMETRY (2026-09-23). Observation only: none of these changes what the
        # machine computes, and all are None/0 outside a forensic replay.
        #   prov/prov_lit/who  per-position provenance on the pair tape (P-11)
        #   ev                 callback(code) for funnel events:
        #                      'L' self-location executed, 'l' self-location byte hit while
        #                      the op is disabled, 'W' write inside the free window outside
        #                      own span, 'B' BIRTH/SPLIT executed with the op enabled
        self.prov = None
        self.prov_lit = None
        self.who = 0
        self.ev = None

    def telemetry(self):
        return {"ops": self.ops, "writes": self.writes, "writes_own": self.writes_own,
                "writes_other": self.writes_other, "writes_blocked": self.writes_blocked,
                "copy_bytes": self.copy_bytes, "copy_errors": self.copy_errors,
                "births": self.births, "alloc_calls": self.alloc_calls,
                "alloc_fails": self.alloc_fails, "birth_calls": self.birth_calls,
                "in_reads": self.in_reads, "out_writes": self.out_writes,
                "in_reads_at_first_out": self.in_reads_at_first_out,
                "halted": self.halted, "budget_exhausted": self.budget_exhausted,
                "self_overwrites": self.self_overwrites,
                "write_span": (self.min_addr_written, self.max_addr_written)}


def _writable(ctx, addr):
    p = ctx.policy
    if p == ARENA:
        return True
    if p == OWN:
        b = ctx.base
        return b <= addr < b + ctx.length
    # FREE: own span, or the world's declared free window
    b = ctx.base
    if b <= addr < b + ctx.length:
        return True
    return ctx.free_lo <= addr < ctx.free_hi


def run(ctx, pc, budget, ops_enabled=0xFF):
    """Execute at most `budget` instructions from `pc`. Returns the pc it stopped at.

    ops_enabled is a bitmask over world ops: bit0 ALLOC/BIRTH, bit1 SELF, bit2 GETPC,
    bit3 SENSE, bit4 SPLIT, bit5 LDIR/LDDR. A disabled world op decodes as ED + NOP
    (two bytes consumed, nothing done) so the byte stream stays the same length.
    """
    mem = ctx.mem
    size = ctx.size
    mask = size - 1
    pow2 = (size & mask) == 0
    r = [0] * 8 if ctx.regs is None else list(ctx.regs)   # B C D E H L (HL) A
    fz = ctx.fz
    fc = ctx.fc
    steps = 0
    rng = ctx.rng
    cmr = ctx.copy_mut_rate

    def wr(addr, val):
        """One byte write through the sandbox policy, with per-byte accounting."""
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
        ctx.writes += 1
        b = ctx.base
        if b <= a < b + ctx.length:
            ctx.writes_own += 1
            if a != b:
                ctx.self_overwrites += 1
        else:
            ctx.writes_other += 1
            if ctx.ev is not None and ctx.free_lo <= a < ctx.free_hi:
                ctx.ev("W")
        if ctx.max_addr_written < 0 or a > ctx.max_addr_written:
            ctx.max_addr_written = a
        if ctx.min_addr_written < 0 or a < ctx.min_addr_written:
            ctx.min_addr_written = a

    def rd(addr):
        return mem[addr & mask if pow2 else addr % size]

    while steps < budget:
        steps += 1
        pc = pc & mask if pow2 else pc % size
        op = mem[pc]

        # ---- 0x40-0x7F: LD r,r' (0x76 = HALT) ------------------------------
        if 0x40 <= op < 0x80:
            if op == 0x76:
                ctx.halted = True
                ctx.ops += steps
                ctx.regs, ctx.fz, ctx.fc = r, fz, fc
                return pc
            dst = (op >> 3) & 7
            src = op & 7
            v = rd((r[H] << 8) | r[L]) if src == M else r[src]
            if dst == M:
                wr((r[H] << 8) | r[L], v)
            else:
                r[dst] = v
            pc += 1
            continue

        # ---- 0x80-0xBF: ALU A,r --------------------------------------------
        if 0x80 <= op < 0xC0:
            src = op & 7
            v = rd((r[H] << 8) | r[L]) if src == M else r[src]
            kind = (op >> 3) & 7
            a = r[A]
            if kind == 0:                       # ADD
                t = a + v
            elif kind == 1:                     # ADC
                t = a + v + fc
            elif kind == 2:                     # SUB
                t = a - v
            elif kind == 3:                     # SBC
                t = a - v - fc
            elif kind == 4:                     # AND
                t = a & v
            elif kind == 5:                     # XOR
                t = a ^ v
            elif kind == 6:                     # OR
                t = a | v
            else:                               # CP: flags only
                t = a - v
            fc = 1 if (t > 255 or t < 0) else 0
            t &= 0xFF
            fz = 1 if t == 0 else 0
            if kind != 7:
                r[A] = t
            pc += 1
            continue

        # ---- 0x04+8d INC r / 0x05+8d DEC r / 0x06+8d LD r,n -----------------
        lo = op & 7
        if lo == 4 and op < 0x40:
            d = (op >> 3) & 7
            if d == M:
                addr = (r[H] << 8) | r[L]
                v = (rd(addr) + 1) & 0xFF
                wr(addr, v)
            else:
                v = r[d] = (r[d] + 1) & 0xFF
            fz = 1 if v == 0 else 0
            pc += 1
            continue
        if lo == 5 and op < 0x40:
            d = (op >> 3) & 7
            if d == M:
                addr = (r[H] << 8) | r[L]
                v = (rd(addr) - 1) & 0xFF
                wr(addr, v)
            else:
                v = r[d] = (r[d] - 1) & 0xFF
            fz = 1 if v == 0 else 0
            pc += 1
            continue
        if lo == 6 and op < 0x40:
            d = (op >> 3) & 7
            n = rd(pc + 1)
            if d == M:
                wr((r[H] << 8) | r[L], n)
            else:
                r[d] = n
            pc += 2
            continue

        # ---- 16-bit loads, pointer loads/stores, INC/DEC rr ----------------
        if op == 0x01 or op == 0x11 or op == 0x21 or op == 0x31:
            n = rd(pc + 1) | (rd(pc + 2) << 8)
            if op == 0x01:
                r[B], r[C] = (n >> 8) & 0xFF, n & 0xFF
            elif op == 0x11:
                r[D], r[E] = (n >> 8) & 0xFF, n & 0xFF
            elif op == 0x21:
                r[H], r[L] = (n >> 8) & 0xFF, n & 0xFF
            pc += 3
            continue
        if op == 0x02:
            wr((r[B] << 8) | r[C], r[A]); pc += 1; continue
        if op == 0x12:
            wr((r[D] << 8) | r[E], r[A]); pc += 1; continue
        if op == 0x0A:
            r[A] = rd((r[B] << 8) | r[C]); pc += 1; continue
        if op == 0x1A:
            r[A] = rd((r[D] << 8) | r[E]); pc += 1; continue
        if op == 0x03 or op == 0x13 or op == 0x23 or op == 0x0B or op == 0x1B or op == 0x2B:
            hi, lon = (B, C) if op in (0x03, 0x0B) else ((D, E) if op in (0x13, 0x1B) else (H, L))
            v = ((r[hi] << 8) | r[lon]) + (1 if op in (0x03, 0x13, 0x23) else -1)
            v &= 0xFFFF
            r[hi], r[lon] = (v >> 8) & 0xFF, v & 0xFF
            pc += 1
            continue

        # ---- relative jumps -------------------------------------------------
        if op == 0x18 or op == 0x20 or op == 0x28 or op == 0x30 or op == 0x38:
            e = rd(pc + 1)
            if e > 127:
                e -= 256
            take = (op == 0x18 or (op == 0x20 and not fz) or (op == 0x28 and fz)
                    or (op == 0x30 and not fc) or (op == 0x38 and fc))
            pc = pc + 2 + e if take else pc + 2
            continue

        # ---- absolute jumps --------------------------------------------------
        if op == 0xC3 or op == 0xC2 or op == 0xCA or op == 0xD2 or op == 0xDA:
            n = rd(pc + 1) | (rd(pc + 2) << 8)
            take = (op == 0xC3 or (op == 0xC2 and not fz) or (op == 0xCA and fz)
                    or (op == 0xD2 and not fc) or (op == 0xDA and fc))
            pc = n if take else pc + 3
            continue

        # ---- immediate ALU ---------------------------------------------------
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
                r[A] = t
            pc += 2
            continue

        # ---- task I/O ---------------------------------------------------------
        if op == 0xDB:                      # IN A,(n): next task input byte
            if ctx.in_cursor < len(ctx.inputs):
                r[A] = ctx.inputs[ctx.in_cursor] & 0xFF
                ctx.in_cursor += 1
                ctx.in_reads += 1
            else:
                r[A] = 0
            pc += 2
            continue
        if op == 0xD3:                      # OUT (n),A: emit an answer byte
            if ctx.in_reads_at_first_out < 0:
                ctx.in_reads_at_first_out = ctx.in_reads
            if len(ctx.outputs) < 64:
                ctx.outputs.append(r[A])
            ctx.out_writes += 1
            pc += 2
            continue

        # ---- ED-prefixed world ops ---------------------------------------------
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
                # charge per byte against the same instruction budget
                room = budget - steps
                if n > room:
                    n = room
                    ctx.budget_exhausted = True
                for _ in range(n):
                    v = rd(src)
                    if cmr and rng is not None and rng.random() < cmr:
                        v ^= 1 << rng.randrange(8)
                        ctx.copy_errors += 1
                    wr(dst, v)
                    src += step
                    dst += step
                    ctx.copy_bytes += 1
                steps += n
                src &= 0xFFFF
                dst &= 0xFFFF
                r[H], r[L] = (src >> 8) & 0xFF, src & 0xFF
                r[D], r[E] = (dst >> 8) & 0xFF, dst & 0xFF
                r[B] = r[C] = 0
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
                    fz = 1
                continue
            if op2 == OP_BIRTH or op2 == OP_SPLIT:
                if op2 == OP_BIRTH and not (ops_enabled & 0x01):
                    continue
                if op2 == OP_SPLIT and not (ops_enabled & 0x10):
                    continue
                ctx.world_op_calls += 1
                ctx.birth_calls += 1
                if ctx.ev is not None:
                    ctx.ev("B")
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
                    if ctx.ev is not None:
                        ctx.ev("l")
                    continue
                ctx.world_op_calls += 1
                if ctx.ev is not None:
                    ctx.ev("L")
                r[H], r[L] = (ctx.base >> 8) & 0xFF, ctx.base & 0xFF
                r[B], r[C] = (ctx.length >> 8) & 0xFF, ctx.length & 0xFF
                continue
            if op2 == OP_GETPC:
                if not (ops_enabled & 0x04):
                    if ctx.ev is not None:
                        ctx.ev("l")
                    continue
                ctx.world_op_calls += 1
                if ctx.ev is not None:
                    ctx.ev("L")
                p = (pc - 2) & 0xFFFF
                r[H], r[L] = (p >> 8) & 0xFF, p & 0xFF
                continue
            if op2 == OP_SENSE:
                if not (ops_enabled & 0x08):
                    continue
                ctx.world_op_calls += 1
                r[A] = ctx.sense & 0xFF
                continue
            continue                       # unknown ED op: two bytes, no effect

        # ---- everything else: a one-byte NOP ------------------------------------
        pc += 1

    ctx.ops += steps
    ctx.budget_exhausted = True
    ctx.regs, ctx.fz, ctx.fc = r, fz, fc
    return pc & mask if pow2 else pc % size


# ---------------------------------------------------------------- assembler
_SIMPLE = {
    "NOP": 0x00, "HALT": 0x76, "LDIR": None, "LDDR": None,
    "INC_BC": 0x03, "INC_DE": 0x13, "INC_HL": 0x23,
    "DEC_BC": 0x0B, "DEC_DE": 0x1B, "DEC_HL": 0x2B,
    "LD_A_(BC)": 0x0A, "LD_A_(DE)": 0x1A, "LD_(BC)_A": 0x02, "LD_(DE)_A": 0x12,
}
_R = {"B": B, "C": C, "D": D, "E": E, "H": H, "L": L, "(HL)": M, "A": A}
_ALU = {"ADD": 0, "ADC": 1, "SUB": 2, "SBC": 3, "AND": 4, "XOR": 5, "OR": 6, "CP": 7}
_WORLD = {"ALLOC": OP_ALLOC, "BIRTH": OP_BIRTH, "SELF": OP_SELF, "GETPC": OP_GETPC,
          "SENSE": OP_SENSE, "SPLIT": OP_SPLIT, "LDIR": OP_LDIR, "LDDR": OP_LDDR}


def asm(source):
    """Tiny assembler for hand-written positive controls and task witnesses.

    Lines are 'MNEMONIC arg, arg' with labels 'name:' and '.db 1,2,3'. Only what the
    campaign's controls need; organisms in the campaign are never written by hand except
    as instruments, and every instrument is labelled as one.
    """
    lines = [l.split(";")[0].strip() for l in source.strip().splitlines()]
    lines = [l for l in lines if l]
    labels, out, fixups = {}, bytearray(), []
    # two passes: sizes then emit
    for _pass in (0, 1):
        out = bytearray()
        fixups = []
        for line in lines:
            if line.endswith(":"):
                if _pass == 0:
                    labels[line[:-1]] = len(out)
                continue
            parts = line.replace(",", " ").split()
            m = parts[0].upper()
            args = parts[1:]

            def val(tok):
                tok = tok.strip()
                if tok.upper() in labels:
                    return labels[tok.upper()]
                if tok in labels:
                    return labels[tok]
                if tok.lower().startswith("0x"):
                    return int(tok, 16)
                return int(tok, 0)

            if m == ".DB":
                for t in args:
                    out.append(val(t) & 0xFF)
            elif m in _WORLD:
                out += bytes((0xED, _WORLD[m]))
            elif m == "IN":
                out += bytes((0xDB, 0))
            elif m == "OUT":
                out += bytes((0xD3, 0))
            elif m == "LD":
                dst, src = args[0].upper(), args[1]
                if dst in ("(BC)", "(DE)"):
                    out.append(0x02 if dst == "(BC)" else 0x12)
                elif src.upper() in ("(BC)", "(DE)"):
                    out.append(0x0A if src.upper() == "(BC)" else 0x1A)
                elif dst in ("BC", "DE", "HL"):
                    n = val(src) if _pass else 0
                    out += bytes(({"BC": 0x01, "DE": 0x11, "HL": 0x21}[dst], n & 0xFF, (n >> 8) & 0xFF))
                elif src.upper() in _R:
                    out.append(0x40 | (_R[dst] << 3) | _R[src.upper()])
                else:
                    n = val(src) if _pass else 0
                    out += bytes((0x06 | (_R[dst] << 3), n & 0xFF))
            elif m in _ALU:
                src = args[-1]
                if src.upper() in _R:
                    out.append(0x80 | (_ALU[m] << 3) | _R[src.upper()])
                else:
                    n = val(src) if _pass else 0
                    out += bytes(({"ADD": 0xC6, "SUB": 0xD6, "AND": 0xE6, "XOR": 0xEE,
                                   "OR": 0xF6, "CP": 0xFE}[m], n & 0xFF))
            elif m in ("INC", "DEC"):
                a = args[0].upper()
                if a in ("BC", "DE", "HL"):
                    out.append(_SIMPLE[m + "_" + a])
                else:
                    out.append((0x04 if m == "INC" else 0x05) | (_R[a] << 3))
            elif m in ("JR", "JRNZ", "JRZ", "JRNC", "JRC"):
                opc = {"JR": 0x18, "JRNZ": 0x20, "JRZ": 0x28, "JRNC": 0x30, "JRC": 0x38}[m]
                tgt = val(args[0]) if _pass else 0
                e = (tgt - (len(out) + 2)) & 0xFF
                out += bytes((opc, e))
            elif m in ("JP", "JPNZ", "JPZ", "JPNC", "JPC"):
                opc = {"JP": 0xC3, "JPNZ": 0xC2, "JPZ": 0xCA, "JPNC": 0xD2, "JPC": 0xDA}[m]
                n = val(args[0]) if _pass else 0
                out += bytes((opc, n & 0xFF, (n >> 8) & 0xFF))
            elif m in _SIMPLE:
                out.append(_SIMPLE[m])
            else:
                raise ValueError("unknown mnemonic %r" % m)
    return bytes(out), labels


def dis(code, base=0, limit=None):
    """Disassemble for specimen records: a campaign whose organisms cannot be read is
    a pile of bytes, and the serendipity archive is useless without this."""
    out, i = [], 0
    n = len(code) if limit is None else min(len(code), limit)
    while i < n:
        op = code[i]
        a = base + i
        if op == 0xED and i + 1 < n:
            op2 = code[i + 1]
            name = {v: k for k, v in _WORLD.items()}.get(op2)
            out.append((a, name or "ED %02X" % op2))
            i += 2
            continue
        if 0x40 <= op < 0x80:
            if op == 0x76:
                out.append((a, "HALT"))
            else:
                out.append((a, "LD %s,%s" % (REGNAMES[(op >> 3) & 7], REGNAMES[op & 7])))
            i += 1
            continue
        if 0x80 <= op < 0xC0:
            nm = [k for k, v in _ALU.items() if v == ((op >> 3) & 7)][0]
            out.append((a, "%s A,%s" % (nm, REGNAMES[op & 7])))
            i += 1
            continue
        lo = op & 7
        if op < 0x40 and lo == 6:
            out.append((a, "LD %s,%02X" % (REGNAMES[(op >> 3) & 7], code[i + 1] if i + 1 < n else 0)))
            i += 2
            continue
        if op < 0x40 and lo in (4, 5):
            out.append((a, "%s %s" % ("INC" if lo == 4 else "DEC", REGNAMES[(op >> 3) & 7])))
            i += 1
            continue
        if op in (0x01, 0x11, 0x21, 0x31):
            v = (code[i + 1] if i + 1 < n else 0) | ((code[i + 2] if i + 2 < n else 0) << 8)
            out.append((a, "LD %s,%04X" % ({0x01: "BC", 0x11: "DE", 0x21: "HL", 0x31: "SP"}[op], v)))
            i += 3
            continue
        if op in (0x18, 0x20, 0x28, 0x30, 0x38):
            e = code[i + 1] if i + 1 < n else 0
            out.append((a, "%s %+d" % ({0x18: "JR", 0x20: "JRNZ", 0x28: "JRZ", 0x30: "JRNC", 0x38: "JRC"}[op],
                                       e - 256 if e > 127 else e)))
            i += 2
            continue
        if op in (0xC3, 0xC2, 0xCA, 0xD2, 0xDA):
            v = (code[i + 1] if i + 1 < n else 0) | ((code[i + 2] if i + 2 < n else 0) << 8)
            out.append((a, "%s %04X" % ({0xC3: "JP", 0xC2: "JPNZ", 0xCA: "JPZ", 0xD2: "JPNC", 0xDA: "JPC"}[op], v)))
            i += 3
            continue
        if op in (0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE):
            out.append((a, "%s A,%02X" % ({0xC6: "ADD", 0xD6: "SUB", 0xE6: "AND", 0xEE: "XOR",
                                           0xF6: "OR", 0xFE: "CP"}[op], code[i + 1] if i + 1 < n else 0)))
            i += 2
            continue
        if op == 0xDB:
            out.append((a, "IN")); i += 2; continue
        if op == 0xD3:
            out.append((a, "OUT")); i += 2; continue
        if op in (0x02, 0x12, 0x0A, 0x1A, 0x03, 0x13, 0x23, 0x0B, 0x1B, 0x2B):
            out.append((a, {0x02: "LD (BC),A", 0x12: "LD (DE),A", 0x0A: "LD A,(BC)", 0x1A: "LD A,(DE)",
                            0x03: "INC BC", 0x13: "INC DE", 0x23: "INC HL",
                            0x0B: "DEC BC", 0x1B: "DEC DE", 0x2B: "DEC HL"}[op]))
            i += 1
            continue
        out.append((a, "NOP" if op == 0 else "nop(%02X)" % op))
        i += 1
    return out
