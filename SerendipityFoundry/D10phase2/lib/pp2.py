"""PP2 -- hand-constructed, mechanism-faithful KA/KQ candidates.

PP2 is an ASSAY-CAPACITY INSTRUMENT, never evidence for machine-created
keying. Human construction is permitted precisely because the question is
whether the interface CAN express task-conditional relevance.

Every candidate obeys exactly the constraints a future evolved organizer
would obey: the same StackVM instruction set, the same deterministic step
cap (organizer.KEY_MAX_STEPS), the same 64-bit key width, the same Hamming
geometry, the same top-k rule, the same encodings (organizer.artifact_words
/ organizer.evidence_words), and the same resource limits. No execution
primitive, no behaviour trace, no precomputed semantic feature.

ADMISSIBLE INPUTS
  KA: the genotype content words only (post-D1: no supplied length).
      Registers R0..R7 mirror the first 8 words = the first 64 bytes.
  KQ: [n_examples, arity, then per example 4 input slots + 1 output].
      The stack top is the LAST example's output, and successive outputs
      sit 5 words apart, so they are reachable by DROP.
"""
from __future__ import annotations

from foundry.engines.gp.stackvm import vm

OP = vm.OP


def asm(prog) -> bytes:
    """Tiny assembler. `prog` is a list of (mnemonic,) or (mnemonic, imm).
    Operand widths come from the VM's own table, so an assembled program is
    a legal StackVM program by construction."""
    out = bytearray()
    for item in prog:
        name = item[0]
        idx = OP[name]
        nops = vm.OPCODES[idx][1]
        out.append(idx)
        if nops == 0:
            if len(item) > 1:
                raise ValueError(f"{name} takes no operand")
        elif nops == 1:
            out.append(int(item[1]) & 0xFF)
        elif nops == 8:
            out += int(item[1]).to_bytes(8, "little")
    return bytes(out)


ACC = 7          # accumulator register used by every candidate


def _bit_from_top(mod_mask: int = 63):
    """Stack top holds a value v. Replace it with (1 << (v & mod_mask))."""
    return [("PUSH1", mod_mask), ("AND",),
            ("PUSH1", 1), ("SWAP",), ("SHL",)]


def _acc_or():
    """OR the stack top into the accumulator register."""
    return [("LDR", ACC), ("OR",), ("STR", ACC)]


def _acc_init():
    return [("PUSH1", 0), ("STR", ACC)]


def _acc_out():
    return [("LDR", ACC)]


# ---------------------------------------------------------------- KA
def ka_bytevalue_bitset(n_words: int = 3) -> bytes:
    """Key bit (b mod 64) is set for each byte b of the first `n_words`
    genotype content words (the genotype head, reached via registers).

    Rationale: a StackVM program's literal bytes are its only admissible
    content. If artifacts that are useful for a task tend to contain byte
    values related to that task's output values (PUSH1 immediates, masks,
    moduli), then a byte-value signature on the artifact side and an
    output-value signature on the query side should land near each other
    under Hamming.
    """
    prog = list(_acc_init())
    for w in range(n_words):
        for j in range(8):
            prog += [("LDR", w), ("PUSH1", 8 * j), ("SHR",)]
            prog += _bit_from_top()
            prog += _acc_or()
    prog += _acc_out()
    return asm(prog)


def ka_opcode_bitset(n_words: int = 3) -> bytes:
    """Key bit (b mod 33 -> opcode index) set for each byte of the head.
    Rationale: the decoded opcode is what actually determines behaviour."""
    prog = list(_acc_init())
    for w in range(n_words):
        for j in range(8):
            prog += [("LDR", w), ("PUSH1", 8 * j), ("SHR",),
                     ("PUSH1", 255), ("AND",),
                     ("PUSH1", vm.N_OPCODES), ("MOD",),
                     ("PUSH1", 1), ("SWAP",), ("SHL",)]
            prog += _acc_or()
    prog += _acc_out()
    return asm(prog)


def ka_constant_bitset(n_words: int = 3) -> bytes:
    """Only bytes that FOLLOW a PUSH1 opcode contribute, i.e. the program's
    literal constants. Cheaper proxy: set the bit for byte b only when the
    preceding byte decodes to PUSH1. Implemented without control flow by
    OR-ing in a mask computed as EQ(prev_opcode, PUSH1)."""
    prog = list(_acc_init())
    for w in range(n_words):
        for j in range(1, 8):
            # prev byte -> opcode
            prog += [("LDR", w), ("PUSH1", 8 * (j - 1)), ("SHR",),
                     ("PUSH1", 255), ("AND",),
                     ("PUSH1", vm.N_OPCODES), ("MOD",),
                     ("PUSH1", OP["PUSH1"]), ("EQ",)]        # 1 if PUSH1
            # this byte -> bit
            prog += [("LDR", w), ("PUSH1", 8 * j), ("SHR",)]
            prog += _bit_from_top()
            # bit * is_push1  (MUL gates it to 0 when not a constant)
            prog += [("MUL",)]
            prog += _acc_or()
    prog += _acc_out()
    return asm(prog)


# ---------------------------------------------------------------- KQ
def kq_output_bitset(n_examples: int = 8) -> bytes:
    """Key bit (v mod 64) set for each train OUTPUT v.

    The evidence stack is [n_examples, arity, (in0..in3, out) x N] with the
    last example's output on top, and outputs 5 words apart below it.
    """
    prog = list(_acc_init())
    for i in range(n_examples):
        prog += _bit_from_top()
        prog += _acc_or()
        if i != n_examples - 1:
            prog += [("DROP",)] * 4
    prog += _acc_out()
    return asm(prog)


def kq_output_and_input_bitset(n_examples: int = 5) -> bytes:
    """Bits from outputs AND from input slot 0 of each example."""
    prog = list(_acc_init())
    for i in range(n_examples):
        prog += _bit_from_top()                    # output
        prog += _acc_or()
        prog += [("DROP",), ("DROP",), ("DROP",)]  # in3, in2, in1
        prog += _bit_from_top()                    # in0
        prog += _acc_or()
    prog += _acc_out()
    return asm(prog)


def kq_constant_zero() -> bytes:
    """Planted-negative query side: a constant key, so retrieval is
    query-independent by construction."""
    return asm([("PUSH1", 0)])


def make_genome(ka: bytes, kq: bytes) -> bytes:
    """Package a hand-written (KA, KQ) pair as a REAL organizer genome.

    An evolved organizer is one byte string that `organizer.decode` splits
    into (KA, KQ) via a two-byte big-endian header taken modulo the body
    length. PP2 must be expressed the same way, or it is not obeying the
    interface it is supposed to test. Because `len(KA) <= len(body)`, the
    modulus is the identity here and the decode is exact -- asserted below.
    """
    body = bytes(ka) + bytes(kq)
    n = len(ka)
    if n > 0xFFFF:
        raise ValueError("KA too long for the 2-byte genome header")
    genome = n.to_bytes(2, "big") + body
    from lib.organizer import decode
    a, q = decode(genome)
    assert a == bytes(ka) and q == bytes(kq), "genome does not round-trip"
    return genome
