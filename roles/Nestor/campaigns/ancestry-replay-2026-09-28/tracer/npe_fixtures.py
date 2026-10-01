"""NPE fixture pack for the T-003 cell (ANCESTRY_PREREG v4 s4.4; draft semantics + Z8 images by Nestor, for Archaeon to
validate or correct; proposed in #831/#832).

Cell: 64-byte pair tape, a = side 0 at 0..31 runs FIRST from 0, b = side 1 at 32..63 runs second from 32; op mask 0x0C
(GETPC, SENSE); ARENA policy; no inputs; registers fresh (None = zero reset) unless the fixture says persisted.
Convention: unless stated, a[0] = HALT (a halts at once) and b is the writer, so the VICTIM is a and the last writer is b.

Each fixture = pre-state + expectations (data). Expectation keys, per victim-half locus j (0..31):
  value, kind ('E','K','X','P','C','F'), ent, src (ENTITY source locus), written (bool),
  ctrl_has / addr_has / exec_has / exec_lacks: base labels as strings "E|a|5", "P|b|1", "X|GETPC"
  performer_ent: entity of the storing instruction's opcode byte
Interaction-level keys: accepted (predecessor criterion on the victim half), budget_ended_b.

Inapplicable in this cell (reason): K10/K26/K27 (no LDIR/COPYALL: mask 0x0C), K13/K24 (no task inputs in the pair
context), K14 (OUT is not memory), K19 (LOCAL mutation: no indels), K20 (in-VM noise exists only inside LDIR), K33 (the
pair interaction IS the two-call shared-memory case: covered by K21). World-level (the harness, not the VM): K9/K28
(write-back mutation labelled at the draw) and K18 (order: both slices, then each half mutated) are checked by
world_fixtures() on the real Runner.
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
Z = HERE.parents[1] / "z80atlas-verify-2026-09-22"
for p in (str(Z), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)
import z8                                                     # noqa: E402  (frozen: assembler only)

N = 32
MASK = 0x0C
HALT = 0x76


def asm(src):
    return z8.asm(src)[0]


def half(code: bytes, data: dict = None, fill: int = 0x00) -> bytes:
    b = bytearray([fill]) * N
    b[0:len(code)] = code
    for k, v in (data or {}).items():
        assert k >= len(code), "fixture data at %d would overwrite code of length %d" % (k, len(code))
        b[k] = v
    assert len(b) == N
    return bytes(b)


A_HALT = half(bytes([HALT]), {k: 0x10 + k for k in range(1, N)})     # a: HALT, then distinct residue 0x11..0x2F
DATA_B = {16 + k: 0xA0 + k for k in range(8)}                        # b's data region b[16..23] = A0..A7
TABLE_B = {24: 0xC0, 25: 0xC1, 26: 0xC2, 27: 0xC3}


def fx(name, ga, gb, expect, regs_a=None, regs_b=None, flags_a=(0, 0), flags_b=(0, 0), budget=300, note=""):
    return {"name": name, "ga": ga, "gb": gb, "regs_a": regs_a, "regs_b": regs_b, "flags_a": flags_a,
            "flags_b": flags_b, "budget": budget, "mask": MASK, "expect": expect, "note": note}


def copy_loop(src, dst, count):
    return asm("""
        LD HL, %d
        LD DE, %d
        LD B, %d
    loop:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ loop
        HALT
    """ % (src, dst, count))


def fixtures():
    F = []
    # K1 exact (shifted) copy: b[16..23] -> a[8..15]; pointers from b's operands; count from b's operand
    code = copy_loop(48, 8, 8)
    exp = {}
    for k in range(8):
        exp[8 + k] = {"value": 0xA0 + k, "kind": "E", "ent": "b", "src": 16 + k, "written": True,
                      "performer_ent": "b", "addr_has": ["E|b|1", "E|b|4"], "exec_lacks": ["E|a|5"]}
        if k >= 1:                     # at-store ctrl: the first store precedes the first JRNZ on the count
            exp[8 + k]["ctrl_has"] = ["E|b|7"]
    exp[20] = {"written": False, "kind": "E", "ent": "a", "src": 20, "value": 0x10 + 20}
    F.append(fx("K1_copy_shifted", A_HALT, half(code, DATA_B), exp,
                note="bytewise LD A,(HL)/LD (DE),A loop; source locus != own index (also K4's shifted case)"))
    # K4 positional copy: b[16..19] -> a[16..19]
    code = copy_loop(48, 16, 4)
    F.append(fx("K4_copy_positional", A_HALT, half(code, DATA_B),
                {16 + k: {"value": 0xA0 + k, "kind": "E", "ent": "b", "src": 16 + k, "written": True} for k in range(4)}))
    # K2 scratch copy: b[0..3] (b's own first bytes) -> a[24..27] (scratch) -> a[4..7]; labels chain back to b
    code = asm("""
        LD HL, 32
        LD DE, 24
        LD B, 4
    l1:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ l1
        LD HL, 24
        LD DE, 4
        LD B, 4
    l2:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ l2
        HALT
    """)
    exp = {4 + k: {"value": code[k], "kind": "E", "ent": "b", "src": k, "written": True} for k in range(4)}
    exp.update({24 + k: {"value": code[k], "kind": "E", "ent": "b", "src": k, "written": True} for k in range(4)})
    F.append(fx("K2_scratch_copy", A_HALT, half(code), exp))
    # K3 = K25 partner-executed copy: b sets HL/DE/B and jumps into a's copy loop at a[1]; performer = a (occupant)
    a_loop = bytes([HALT]) + asm("""
    loop:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ loop
        HALT
    """)
    # the loop is assembled at 0 but placed at a[1]: its JRNZ is relative, so it is position independent
    ga = half(a_loop, {k: 0x10 + k for k in range(len(a_loop), N)})
    code = asm("""
        LD HL, 48
        LD DE, 20
        LD B, 4
        JP 1
    """)
    exp = {20 + k: {"value": 0xA0 + k, "kind": "E", "ent": "b", "src": 16 + k, "written": True,
                    "performer_ent": "a", "exec_has": ["E|a|2"]} for k in range(4)}
    F.append(fx("K3_K25_partner_executed_copy", ga, half(code, DATA_B), exp,
                note="writer sets the pointers; the occupant's opcode bytes perform the stores"))
    # K5 self-painter and K8 literal equal to the occupant's byte: LD (HL),n
    code = asm("""
        LD HL, 10
        LD (HL), 0x5A
        LD HL, 11
        LD (HL), 0x1B
        HALT
    """)
    F.append(fx("K5_K8_painter_literal", A_HALT, half(code), {
        10: {"value": 0x5A, "kind": "E", "ent": "b", "src": 4, "written": True, "performer_ent": "b"},
        11: {"value": 0x1B, "kind": "E", "ent": "b", "src": 9, "written": True,
             "note": "0x1B equals a's existing byte at 11: still the writer's operand, never retention"}}))
    # K6 computed byte: A = b[16] + 3
    code = asm("""
        LD HL, 48
        LD A, (HL)
        ADD A, 3
        LD (DE), A
        HALT
    """)
    F.append(fx("K6_computed", A_HALT, half(code, DATA_B), {
        0: {"value": 0xA3, "kind": "C", "written": True, "has_bases": ["E|b|16", "E|b|5"]}},
        note="DE = 0 from the zero reset: the store lands on a[0] (after a has halted)"))
    # K7 retention: covered in K1 (a[20] not written); explicit here with the whole victim half except one byte
    F.append(fx("K7_retention", A_HALT, half(asm("HALT")), {
        j: {"written": False, "kind": "E", "ent": "a", "src": j} for j in (0, 5, 31)}))
    # K11/K31 control-flow bit decoder: the value is recreated from constants under control of the partner's bit
    code = asm("""
        LD HL, 3
        LD A, (HL)
        AND 1
        JRZ zero
        XOR A
        INC A
        JR store
    zero:
        XOR A
    store:
        LD HL, 12
        LD (HL), A
        HALT
    """)
    ga = half(bytes([HALT]), {3: 0x01, **{k: 0x10 + k for k in range(4, N)}, 1: 0x11, 2: 0x12})
    F.append(fx("K31_K11_bit_decoder", ga, half(code), {
        12: {"value": 0x01, "kind": "F", "written": True, "ctrl_has": ["E|a|3"],
             "not_label": "E|a|3", "note": "a MOVE-labelling tracer (E|a|3) must fail"}}))
    # K12 translation table: index from the partner's byte, entry from the writer's table
    code = asm("""
        LD HL, 2
        LD A, (HL)
        ADD A, 56
        LD L, A
        LD H, 0
        LD A, (HL)
        LD HL, 13
        LD (HL), A
        HALT
    """)
    ga = half(bytes([HALT]), {2: 0x02, **{k: 0x10 + k for k in range(3, N)}, 1: 0x11})
    F.append(fx("K12_translation_table", ga, half(code, TABLE_B), {
        13: {"value": 0xC2, "kind": "E", "ent": "b", "src": 26, "written": True, "addr_has": ["E|a|2"]}}))
    # K15 persisted register (b's C) and the fresh zero reset (a's registers are None)
    code = asm("""
        LD HL, 14
        LD (HL), C
        HALT
    """)
    F.append(fx("K15_persisted_register", A_HALT, half(code), {
        14: {"value": 0x77, "kind": "P", "ent": "b", "reg": 1, "written": True}},
        regs_b=[0, 0x77, 0, 0, 0, 0, 0, 0]))
    code = asm("""
        LD HL, 15
        LD (HL), C
        HALT
    """)
    F.append(fx("K15b_zero_reset_register", A_HALT, half(code), {
        15: {"value": 0x00, "kind": "K", "written": True}}))
    # K16 self-code executed in the window: b copies [LD (HL),0x42 ; HALT] into a[20..22] and jumps there
    routine = asm("""
        LD (HL), 0x42
        HALT
    """)
    data = {24 + k: routine[k] for k in range(len(routine))}
    code = asm("""
        LD HL, 56
        LD DE, 20
        LD B, 3
    loop:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ loop
        LD HL, 9
        JP 20
    """)
    F.append(fx("K16_self_code_in_window", A_HALT, half(code, data), {
        9: {"value": 0x42, "kind": "E", "ent": "b", "src": 25, "written": True, "performer_ent": "b",
            "note": "the storing opcode sits in a's half but its material is b's (copied from b[24])"}}))
    # K16b (added after Archaeon's validation, for the performer_by_location mutant): the WRITER b copies the
    # OCCUPANT's store routine a[1..3] into its own half (56..58) and executes it there: material a, location b
    ga = half(bytes([HALT, 0x36, 0x42, HALT]), {k: 0x10 + k for k in range(4, N)})
    code = asm("""
        LD HL, 1
        LD DE, 56
        LD B, 3
    loop:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ loop
        LD HL, 10
        JP 56
    """)
    F.append(fx("K16b_occupant_code_run_in_writer_half", ga, half(code), {
        10: {"value": 0x42, "kind": "E", "ent": "a", "src": 2, "written": True, "performer_ent": "a",
             "note": "performer by MATERIAL (a) although the storing pc is in b's half"}}))
    # K16c: the OCCUPANT a, in its own slice, copies the writer's routine b[24..26] into a[24..26] and runs it there to
    # store into a[12]: stored BY a (store_by), performer by material = b, location a
    routine = asm("""
        LD (HL), 0x55
        HALT
    """)
    ga = half(bytes([0x00]) + asm("""
        LD HL, 56
        LD DE, 24
        LD B, 3
    loop:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ loop
        LD HL, 12
        JP 24
    """), {k: 0x10 + k for k in range(27, N)})
    gb = half(bytes([HALT]), {24 + k: routine[k] for k in range(len(routine))})
    F.append(fx("K16c_writer_code_run_by_occupant", ga, gb, {
        12: {"value": 0x55, "kind": "E", "ent": "b", "src": 25, "written": True, "performer_ent": "b",
             "store_by": "a", "note": "store_by = a (the slice), performer = b (the material of the storing opcode)"}}))
    # K17 address wrap: HL = 63 -> INC HL wraps to 0 on the 64-byte tape
    code = asm("""
        LD HL, 63
        INC HL
        LD (HL), 0x33
        HALT
    """)
    F.append(fx("K17_address_wrap", A_HALT, half(code), {
        0: {"value": 0x33, "kind": "E", "ent": "b", "src": 5, "written": True}}))
    # K17b budget-ended copy: count 20 but only a few iterations fit the budget
    code = copy_loop(48, 8, 20)
    F.append(fx("K17b_budget_ended", A_HALT, half(code, DATA_B), {
        8: {"value": 0xA0, "kind": "E", "ent": "b", "src": 16, "written": True},
        15: {"written": False, "kind": "E", "ent": "a", "src": 15}}, budget=12,
        note="flag budget_ended_b; only the first iterations complete"))
    # K21 both halves rewritten in one interaction: a writes into b's data region, then b copies it into a's half
    ga = half(asm("""
        LD HL, 52
        LD (HL), 0x66
        HALT
    """), {k: 0x10 + k for k in range(7, N)})
    code = asm("""
        LD HL, 52
        LD DE, 18
        LD A, (HL)
        LD (DE), A
        HALT
    """)
    F.append(fx("K21_both_halves", ga, half(code), {
        18: {"value": 0x66, "kind": "E", "ent": "a", "src": 4, "written": True, "performer_ent": "b",
             "note": "chain crosses entities: a's operand -> b's half -> a's half"}}))
    # K22 guard NOT taken: the branch reads the partner's byte (nonzero), is not taken; ctrl must hold it
    code = asm("""
        LD HL, 6
        LD A, (HL)
        CP 0
        JRZ skip
        LD HL, 19
        LD (HL), 0x2A
    skip:
        HALT
    """)
    F.append(fx("K22_guard_not_taken", A_HALT, half(code), {
        19: {"value": 0x2A, "kind": "E", "ent": "b", "written": True, "ctrl_has": ["E|a|6"]}}))
    # K23 operand cipher: partner byte XOR writer operand
    code = asm("""
        LD HL, 7
        LD A, (HL)
        XOR 0xFF
        LD HL, 21
        LD (HL), A
        HALT
    """)
    F.append(fx("K23_operand_cipher", A_HALT, half(code), {
        21: {"value": 0x17 ^ 0xFF, "kind": "C", "written": True, "has_bases": ["E|a|7", "E|b|5"]}}))
    # K29 GETPC stored into the child
    code = asm("""
        GETPC
        LD A, L
        LD HL, 22
        LD (HL), A
        HALT
    """)
    F.append(fx("K29_getpc_stored", A_HALT, half(code), {
        22: {"value": 32, "kind": "X", "op": "GETPC", "written": True}}))
    # K30 residue-majority ACCEPTED birth: a already equals b's genome except 4 bytes; b writes those 4 plus
    # repeated writes (the predecessor gate counts writes). Pure residue-only acceptance is impossible here: the gate
    # needs the victim changed by >= 10% (fid_self < 0.9), so the residue case is the MAJORITY-residue birth.
    gb_code = asm("""
        LD HL, 28
        LD (HL), 0xE1
        INC HL
        LD (HL), 0xE2
        INC HL
        LD (HL), 0xE3
        INC HL
        LD (HL), 0xE4
        LD (HL), 0xE4
        LD (HL), 0xE4
        LD (HL), 0xE4
        LD (HL), 0xE4
        HALT
    """)
    gb = half(gb_code, {28: 0xE1, 29: 0xE2, 30: 0xE3, 31: 0xE4})
    ga = bytearray(gb)
    ga[0] = HALT
    for k in range(28, 32):
        ga[k] = 0x00
    exp = {28 + k: {"value": 0xE1 + k, "kind": "E", "ent": "b", "written": True} for k in range(4)}
    exp[5] = {"written": False, "kind": "E", "ent": "a", "src": 5, "value": gb[5],
              "note": "residue: equals the donor's byte, never written by it"}
    F.append(fx("K30_residue_majority_birth", bytes(ga), gb, exp, note="expect accepted=True",
                ) | {"accepted": True})
    # K32 zero-reset pointer self-overlap fill (bytewise analogue of the CX1 replicator): copy a[0..23] -> a[8..31];
    # pointers from the zero reset, so a[8+k] chains back to a[k mod 8]
    code = asm("""
        LD B, 8
    l1:
        INC E
        DEC B
        JRNZ l1
        LD B, 24
    l2:
        LD A, (HL)
        LD (DE), A
        INC HL
        INC DE
        DEC B
        JRNZ l2
        HALT
    """)
    exp = {8 + k: {"kind": "E", "ent": "a", "src": k % 8, "written": True} for k in range(24)}
    F.append(fx("K32_reset_pointer_overlap_fill", A_HALT, half(code), exp,
                note="loci 8..31 sourced from 0..7 by the overlap chain; a positional tracer says k+8"))
    # K34 IN with no inputs: CONSTANT in_exhausted
    code = asm("""
        IN
        LD HL, 23
        LD (HL), A
        HALT
    """)
    F.append(fx("K34_in_exhausted", A_HALT, half(code), {23: {"value": 0, "kind": "K", "written": True}}))
    # K35 OR with a zero-reset register: value unchanged, label COMPUTED (not MOVE)
    code = asm("""
        LD HL, 9
        LD A, (HL)
        OR B
        LD HL, 25
        LD (HL), A
        HALT
    """)
    F.append(fx("K35_or_zero_register", A_HALT, half(code), {
        25: {"value": 0x19, "kind": "C", "written": True, "has_bases": ["E|a|9"], "not_label": "E|a|9"}}))
    # K36 loop count from the occupant: ctrl holds the occupant's byte
    code = asm("""
        LD HL, 1
        LD A, (HL)
        LD B, A
        LD HL, 26
    loop:
        LD (HL), 0x44
        DEC B
        JRNZ loop
        HALT
    """)
    ga = half(bytes([HALT, 0x03]), {k: 0x10 + k for k in range(2, N)})
    F.append(fx("K36_count_from_occupant", ga, half(code), {
        26: {"value": 0x44, "kind": "E", "ent": "b", "written": True, "ctrl_has": ["E|a|1"]}}))
    # K37 painting (operator directive s6): ONE source byte written to 8 loci by a loop. Every locus is a clean donor
    # MOVE label of the SAME source: 8 attributed loci are ONE cause (see the diversity diagnostic)
    code = asm("""
        LD HL, 48
        LD A, (HL)
        LD DE, 8
        LD B, 8
    loop:
        LD (DE), A
        INC DE
        DEC B
        JRNZ loop
        HALT
    """)
    F.append(fx("K37_painting_one_source", A_HALT, half(code, DATA_B),
                {8 + k: {"value": 0xA0, "kind": "E", "ent": "b", "src": 16, "written": True, "performer_ent": "b"}
                 for k in range(8)}))
    return F


INAPPLICABLE = {
    "K10": "no LDIR/COPYALL under op mask 0x0C", "K26": "no LDIR", "K27": "no COPYALL",
    "K13": "no task inputs in the pair context", "K24": "no task inputs in the pair context",
    "K14": "OUT is not memory in Z8", "K19": "LOCAL mutation: no insertions/deletions",
    "K20": "in-VM copy noise exists only inside LDIR/LDDR (disabled)",
    "K33": "the NPE pair interaction is itself the two-call shared-memory case (K21)",
}
WORLD_LEVEL = {"K9": "write-back mutation labelled at the RNG draw", "K28": "write-back with mutation",
               "K18": "order: slice a, slice b, then each half mutated"}
