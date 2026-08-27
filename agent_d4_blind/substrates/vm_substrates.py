"""D-4 real computational bases. FROZEN at PREREG-PHASE1 commit.

Four machine-native substrates with total decode (every byte string is an
executable program — validity is trivially 1.0 by construction and is
disclosed as such, never rewarded). All share:

- probe suite: 8 frozen input tapes of 8 nibbles (seed PROBE_SEED)
- fingerprint per probe: (output tuple <=8 nibbles, steps bucket,
  touched bucket, halted flag, trace signature set)
- viability: output nonempty on >= 4 probes AND >= 2 distinct output tuples
  across probes (input sensitivity) AND >= 1 executed state-changing step
- d1: mean over probes of positional nibble mismatch on outputs padded to 8
  with sentinel
- mutation physics: 5 content-blind raw-encoding operators (bitflip burst,
  cell substitution, block copy, block swap, rotation) + one-point crossover
  (registered mechanism, reachable only via the recombining navigator)
- optional per-byte decode permutation (representation counterfactual):
  a frozen nonlinear bijection on byte values applied at decode time. The
  reachable program set is unchanged (bijection); bit-level mutation
  adjacency changes. Cell-level operators commute with the re-coding.

No filesystem, network, host introspection, or wall-clock enters any
substrate state. Everything is a pure function of (genome bytes, probe
inputs, frozen constants).
"""
from __future__ import annotations

import numpy as np

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from d4core.interface import Substrate  # noqa: E402

PROBE_SEED = 20260827
ENC_SEED = 3301
N_PROBES = 8
IN_LEN = 8
OUT_CAP = 8
SENTINEL = 255

_prng = np.random.default_rng(PROBE_SEED)
PROBE_INPUTS = [tuple(int(x) for x in _prng.integers(0, 16, size=IN_LEN))
                for _ in range(N_PROBES)]

_enc_rng = np.random.default_rng(ENC_SEED)
ENC_PERM = tuple(int(x) for x in _enc_rng.permutation(256))


def _bucket(x: int) -> int:
    b = 0
    while x > 0 and b < 7:
        x >>= 1
        b += 1
    return b


def _sign(v: int, bits: int) -> int:
    return v - (1 << bits) if v >= (1 << (bits - 1)) else v


class ProbeFingerprint:
    __slots__ = ("rows", "_key")

    def __init__(self, rows):
        # rows: tuple per probe: (out_tuple, steps_b, touched_b, halted, trace_fs)
        self.rows = rows
        self._key = hash(tuple((r[0], r[1], r[2], r[3]) for r in rows))

    def key(self):
        return self._key


class VMSubstrate(Substrate):
    """Shared physics frame; subclasses implement _run_program(code, inp)."""

    n_ops = 5
    cell = 1           # bytes per encoding cell (alignment unit for cell ops)
    glen = 96          # genome length in bytes

    def __init__(self, encoded: bool = False, radius2: bool = False):
        super().__init__()
        self.encoded = encoded
        self.radius2 = radius2  # counterfactual: doubled bitflip-burst radius
        self._cache: dict = {}

    # --- genome ------------------------------------------------------------
    def random_genome(self, rng) -> bytes:
        return bytes(int(x) for x in rng.integers(0, 256, size=self.glen))

    def _decode_byte(self, b: int) -> int:
        return ENC_PERM[b] if self.encoded else b

    # --- mutation physics (raw encoding, content-blind) --------------------
    def _blocklen(self, rng) -> int:
        L = 2
        while L < 8 and rng.random() < 0.4:
            L += 1
        return L

    def mutate(self, genome: bytes, op_index: int, rng) -> bytes:
        g = bytearray(genome)
        n = len(g)
        ncells = n // self.cell
        if op_index == 0:            # bitflip burst
            cap, cont = (16, 0.75) if self.radius2 else (8, 0.5)
            k = 1
            while k < cap and rng.random() < cont:
                k += 1
            for _ in range(k):
                p = int(rng.integers(0, n * 8))
                g[p // 8] ^= 1 << (p % 8)
        elif op_index == 1:          # cell substitution
            c = int(rng.integers(0, ncells))
            for i in range(self.cell):
                g[c * self.cell + i] = int(rng.integers(0, 256))
        elif op_index == 2:          # block copy (intra-genome duplication)
            L = min(self._blocklen(rng), ncells - 1)
            src = int(rng.integers(0, ncells - L + 1))
            dst = int(rng.integers(0, ncells - L + 1))
            blk = bytes(g[src * self.cell:(src + L) * self.cell])
            g[dst * self.cell:(dst + L) * self.cell] = blk
        elif op_index == 3:          # block swap (disjoint, equal length)
            L = min(self._blocklen(rng), ncells // 2)
            for _ in range(8):
                a = int(rng.integers(0, ncells - L + 1))
                b = int(rng.integers(0, ncells - L + 1))
                if abs(a - b) >= L:
                    ab = bytes(g[a * self.cell:(a + L) * self.cell])
                    bb = bytes(g[b * self.cell:(b + L) * self.cell])
                    g[a * self.cell:(a + L) * self.cell] = bb
                    g[b * self.cell:(b + L) * self.cell] = ab
                    break
        elif op_index == 4:          # rotation by whole cells
            r = int(rng.integers(1, ncells)) * self.cell
            g = g[r:] + g[:r]
        return bytes(g)

    def crossover(self, g1: bytes, g2: bytes, rng) -> bytes:
        c = int(rng.integers(1, len(g1) // self.cell)) * self.cell
        return g1[:c] + g2[c:]

    # --- behavior ----------------------------------------------------------
    def _evaluate_raw(self, genome: bytes):
        hit = self._cache.get(genome)
        if hit is not None:
            return hit
        rows = []
        for inp in PROBE_INPUTS:
            rows.append(self._run_program(genome, inp))
        fp = ProbeFingerprint(tuple(rows))
        if len(self._cache) < 400_000:
            self._cache[genome] = fp
        return fp

    def viable(self, fp: ProbeFingerprint) -> bool:
        rows = fp.rows
        nonempty = sum(1 for r in rows if len(r[0]) > 0)
        if nonempty < 4:
            return False
        outs = {r[0] for r in rows}
        if len(outs) < 2:
            return False
        return any(r[1] > 0 for r in rows)

    def pkey(self, fp: ProbeFingerprint):
        return fp.key()

    def fp_bytes(self, fp: ProbeFingerprint) -> bytes:
        parts = []
        for r in fp.rows:
            parts.append(bytes(r[0]) + bytes([r[1], r[2], int(r[3])]))
        return b"|".join(parts)

    def d1(self, f1: ProbeFingerprint, f2: ProbeFingerprint) -> float:
        tot = 0.0
        for r1, r2 in zip(f1.rows, f2.rows):
            o1, o2 = r1[0], r2[0]
            mism = 0
            for i in range(OUT_CAP):
                a = o1[i] if i < len(o1) else SENTINEL
                b = o2[i] if i < len(o2) else SENTINEL
                if a != b:
                    mism += 1
            tot += mism / OUT_CAP
        return tot / len(f1.rows)

    def d_aux(self, f1, f2) -> dict:
        ds = dt = dj = 0.0
        for r1, r2 in zip(f1.rows, f2.rows):
            ds += abs(r1[1] - r2[1]) / 7.0
            dt += abs(r1[2] - r2[2]) / 7.0
            t1, t2 = r1[4], r2[4]
            u = len(t1 | t2)
            dj += (1 - len(t1 & t2) / u) if u else 0.0
        n = len(f1.rows)
        return {"d_steps": ds / n, "d_touched": dt / n, "d_trace": dj / n}

    def disp_features(self, fp: ProbeFingerprint, fc: ProbeFingerprint) -> np.ndarray:
        out = np.zeros(13)
        out[0] = self.d1(fp, fc)
        out[1] = 1.0 if fp.key() == fc.key() else 0.0
        for i, (r1, r2) in enumerate(zip(fp.rows, fc.rows)):
            o1, o2 = r1[0], r2[0]
            mism = 0
            for j in range(OUT_CAP):
                a = o1[j] if j < len(o1) else SENTINEL
                b = o2[j] if j < len(o2) else SENTINEL
                if a != b:
                    mism += 1
            out[2 + i] = mism / OUT_CAP
        aux = self.d_aux(fp, fc)
        out[10] = aux["d_steps"]
        out[11] = aux["d_touched"]
        out[12] = aux["d_trace"]
        return out

    # subclasses ------------------------------------------------------------
    def _run_program(self, genome: bytes, inp: tuple):
        raise NotImplementedError

    def witness_genome(self) -> bytes:
        raise NotImplementedError


class S1Reg(VMSubstrate):
    """48 x 16-bit-word register machine, 4 registers, dense 16-opcode decode."""
    name = "S1_REG"
    cell = 2
    glen = 96
    NWORDS = 48
    STEPS = 128

    def _decode(self, genome: bytes):
        code = []
        for i in range(self.NWORDS):
            lo = self._decode_byte(genome[2 * i])
            hi = self._decode_byte(genome[2 * i + 1])
            w = lo | (hi << 8)
            code.append(((w >> 12) & 0xF, (w >> 10) & 3, (w >> 8) & 3, w & 0xFF))
        return code

    def _run_program(self, genome: bytes, inp: tuple):
        code = self._decode(genome)
        R = [0, 0, 0, 0]
        pc = 0
        ip = 0
        out = []
        steps = 0
        halted = False
        visited = set()
        n = self.NWORDS
        while steps < self.STEPS:
            op, rd, rs, imm = code[pc]
            visited.add(pc)
            steps += 1
            npc = pc + 1
            if op == 0:
                R[rd] = (R[rd] + R[rs]) & 0xFFFF
            elif op == 1:
                R[rd] = (R[rd] - R[rs]) & 0xFFFF
            elif op == 2:
                R[rd] &= R[rs]
            elif op == 3:
                R[rd] ^= R[rs]
            elif op == 4:
                R[rd] = (R[rd] << (imm & 7)) & 0xFFFF
            elif op == 5:
                R[rd] >>= (imm & 7)
            elif op == 6:
                R[rd] = imm
            elif op == 7:
                R[rd] = (R[rd] + imm) & 0xFFFF
            elif op == 8:
                R[rd] = R[rs]
            elif op == 9:
                if R[rd] == 0:
                    npc = pc + 2
            elif op == 10:
                if R[rd] > R[rs]:
                    npc = pc + 2
            elif op == 11:
                npc = pc + _sign(imm, 8)
            elif op == 12:
                R[rd] = inp[ip] if ip < len(inp) else 0
                ip += 1
            elif op == 13:
                if len(out) < OUT_CAP:
                    out.append(R[rd] & 0xF)
                    if len(out) >= OUT_CAP:
                        halted = True
                        break
            elif op == 14:
                R[rd], R[rs] = R[rs], R[rd]
            else:  # 15 HLT
                halted = True
                break
            pc = npc % n
        return (tuple(out), _bucket(steps), _bucket(len(visited)), halted,
                frozenset(visited))

    def witness_genome(self) -> bytes:
        # IN R0; OUT R0; JMP -2   (echo)
        words = [0xC000, 0xD000, 0xB000 | ((-2) & 0xFF)]
        words += [0x6000] * (self.NWORDS - len(words))
        g = bytearray()
        for w in words:
            g += bytes([w & 0xFF, (w >> 8) & 0xFF])
        return bytes(g)


class S2Stack(VMSubstrate):
    """96-instruction stack machine, circular 16-deep 16-bit stack."""
    name = "S2_STACK"
    cell = 1
    glen = 96
    STEPS = 128

    def _run_program(self, genome: bytes, inp: tuple):
        n = self.glen
        st = [0] * 16
        sp = 0
        pc = 0
        ip = 0
        out = []
        steps = 0
        halted = False
        visited = set()
        dec = self._decode_byte
        while steps < self.STEPS:
            b = dec(genome[pc])
            op = (b >> 5) & 7
            arg = b & 0x1F
            visited.add(pc)
            steps += 1
            npc = pc + 1
            if op == 0:      # PUSH
                sp = (sp + 1) % 16
                st[sp] = arg
            elif op == 1:    # ALU
                a = st[sp]
                sp = (sp - 1) % 16
                bb = st[sp]
                m = arg & 3
                if m == 0:
                    st[sp] = (bb + a) & 0xFFFF
                elif m == 1:
                    st[sp] = (bb - a) & 0xFFFF
                elif m == 2:
                    st[sp] = (bb * a) & 0xFFFF
                else:
                    st[sp] = bb ^ a
            elif op == 2:    # STK
                m = arg & 3
                if m == 0:   # dup
                    v = st[sp]
                    sp = (sp + 1) % 16
                    st[sp] = v
                elif m == 1:  # drop
                    sp = (sp - 1) % 16
                elif m == 2:  # swap
                    st[sp], st[(sp - 1) % 16] = st[(sp - 1) % 16], st[sp]
                else:         # over
                    v = st[(sp - 1) % 16]
                    sp = (sp + 1) % 16
                    st[sp] = v
            elif op == 3:    # CMP/unary
                m = arg & 3
                if m == 0:
                    a = st[sp]
                    sp = (sp - 1) % 16
                    st[sp] = 1 if st[sp] == a else 0
                elif m == 1:
                    a = st[sp]
                    sp = (sp - 1) % 16
                    st[sp] = 1 if st[sp] > a else 0
                elif m == 2:
                    st[sp] = 0 if st[sp] else 1
                else:
                    st[sp] = (-st[sp]) & 0xFFFF
            elif op == 4:    # BRZ
                v = st[sp]
                sp = (sp - 1) % 16
                if v == 0:
                    npc = pc + _sign(arg, 5)
            elif op == 5:    # BR
                npc = pc + _sign(arg, 5)
            elif op == 6:    # IN
                sp = (sp + 1) % 16
                st[sp] = inp[ip] if ip < len(inp) else 0
                ip += 1
            else:            # OUT
                v = st[sp]
                sp = (sp - 1) % 16
                if len(out) < OUT_CAP:
                    out.append(v & 0xF)
                    if len(out) >= OUT_CAP:
                        halted = True
                        break
            pc = npc % n
        return (tuple(out), _bucket(steps), _bucket(len(visited)), halted,
                frozenset(visited))

    def witness_genome(self) -> bytes:
        # IN; OUT; BR -2  (echo)
        prog = [0xC0, 0xE0, 0xA0 | ((-2) & 0x1F)]
        prog += [0x00] * (self.glen - len(prog))
        return bytes(prog)


class S3Rewrite(VMSubstrate):
    """16 rules x 3 bytes; leftmost-first pair rewriting over an 8-symbol
    alphabet; tape cap 16; halts when no rule matches."""
    name = "S3_REWRITE"
    cell = 3
    glen = 48
    STEPS = 64
    NRULES = 16

    def _rules(self, genome: bytes):
        rules = []
        for i in range(self.NRULES):
            b0 = self._decode_byte(genome[3 * i])
            b1 = self._decode_byte(genome[3 * i + 1])
            b2 = self._decode_byte(genome[3 * i + 2])
            active = (b2 >> 3) & 1
            if not active:
                continue
            lhs = (b0 & 7, (b0 >> 3) & 7)
            rhs_syms = (b1 & 7, (b1 >> 3) & 7, ((b1 >> 6) | ((b2 & 1) << 2)) & 7)
            rlen = (b2 >> 1) & 3   # 0..3 replacement symbols (0 = deletion)
            rules.append((i, lhs, rhs_syms[:rlen]))
        return rules

    def _run_program(self, genome: bytes, inp: tuple):
        rules = self._rules(genome)
        tape = [s & 7 for s in inp]
        steps = 0
        fired = set()
        while steps < self.STEPS:
            applied = False
            for pos in range(len(tape) - 1):
                pair = (tape[pos], tape[pos + 1])
                for ridx, lhs, rhs in rules:
                    if pair == lhs:
                        tape[pos:pos + 2] = list(rhs)
                        del tape[16:]
                        steps += 1
                        fired.add(ridx)
                        applied = True
                        break
                if applied:
                    break
            if not applied:
                break
        out = tuple(tape[:OUT_CAP])
        return (out, _bucket(steps), _bucket(len(tape)), steps < self.STEPS,
                frozenset(fired))

    def witness_genome(self) -> bytes:
        # 8 rules: (a,a) -> (a)  [collapse adjacent repeats]; 8 inactive
        g = bytearray()
        for a in range(8):
            b0 = a | (a << 3)
            b1 = a          # rhs symbol 0 = a
            b2 = (1 << 3) | (1 << 1)  # active, rlen=1
            g += bytes([b0, b1, b2])
        g += bytes(48 - len(g))
        return bytes(g)


class S4Mem(VMSubstrate):
    """72-op tape machine (3 bits per byte used), 16-cell wrapping tape,
    skip and bounded-back-jump control."""
    name = "S4_MEM"
    cell = 1
    glen = 72
    STEPS = 128

    def _run_program(self, genome: bytes, inp: tuple):
        n = self.glen
        tape = [0] * 16
        ptr = 0
        pc = 0
        ip = 0
        out = []
        steps = 0
        halted = False
        visited = set()
        dec = self._decode_byte
        while steps < self.STEPS:
            op = dec(genome[pc]) & 7
            visited.add(pc)
            steps += 1
            npc = pc + 1
            if op == 0:
                tape[ptr] = (tape[ptr] + 1) & 0xFF
            elif op == 1:
                tape[ptr] = (tape[ptr] - 1) & 0xFF
            elif op == 2:
                ptr = (ptr + 1) % 16
            elif op == 3:
                ptr = (ptr - 1) % 16
            elif op == 4:
                tape[ptr] = inp[ip] if ip < len(inp) else 0
                ip += 1
            elif op == 5:
                if len(out) < OUT_CAP:
                    out.append(tape[ptr] & 0xF)
                    if len(out) >= OUT_CAP:
                        halted = True
                        break
            elif op == 6:
                if tape[ptr] == 0:
                    npc = pc + 2
            else:  # 7 BACK
                if tape[ptr] != 0:
                    npc = pc - 6
            pc = npc % n
        return (tuple(out), _bucket(steps), _bucket(len(visited)), halted,
                frozenset(visited))

    def witness_genome(self) -> bytes:
        return bytes([4, 5] * (self.glen // 2))


SUBSTRATES = {
    "S1_REG": S1Reg,
    "S2_STACK": S2Stack,
    "S3_REWRITE": S3Rewrite,
    "S4_MEM": S4Mem,
}
