"""Hand-written organisms: positive controls, payload-reading nulls, and the cheat battery.

A POS organism proves the world is solvable IN THIS VM with the published opcodes and that
the measurement sees it. A NULL organism (constant, echo) reads the payload without solving:
a world where a null scores high leaks its answer. The CHEAT battery runs the POS organisms
under the interventions and must DETECT the mechanism they were written with.

The assembler is for writing controls only; nothing evolved passes through it.
"""
from __future__ import annotations

from typing import List, Sequence

from proteus.foundry.affordances import MNEMONIC
from proteus.foundry.vm import SCHEMA, validate_manifest

MASK32 = 0xFFFFFFFF
OPCODE = {v: k for k, v in MNEMONIC.items()}
_ABC = {"ADD", "SUB", "MUL", "AND", "OR", "XOR", "SHL", "SHR", "EQ", "LT"}
_AB = {"MOV", "LD", "ST", "NOT", "IN", "INQ", "OUT"}


def _reg(x) -> int:
    return int(str(x)[1:]) if isinstance(x, str) and x.startswith("r") else int(x)


def asm(lines: Sequence[tuple]) -> List[int]:
    """lines: ("label", "NAME") or (MNEMONIC, operands...). Jump targets are labels; the offset
    is target_index - instruction_index in instructions (the VM's convention)."""
    labels = {}
    idx = 0
    for ln in lines:
        if ln[0] == "label":
            labels[ln[1]] = idx
        else:
            idx += 1
    words: List[int] = []
    idx = 0
    for ln in lines:
        if ln[0] == "label":
            continue
        op = ln[0]
        code = OPCODE[op]
        if op in ("NOP", "HALT", "YIELD"):
            w = [code, 0, 0, 0]
        elif op == "LDC":
            w = [code, _reg(ln[1]), int(ln[2]) & MASK32, 0]
        elif op in _AB:
            w = [code, _reg(ln[1]), _reg(ln[2]), 0]
        elif op in _ABC:
            w = [code, _reg(ln[1]), _reg(ln[2]), _reg(ln[3])]
        elif op == "JMP":
            w = [code, 0, (labels[ln[1]] - idx) & MASK32, 0]
        elif op in ("JZ", "JNZ"):
            w = [code, _reg(ln[1]), (labels[ln[2]] - idx) & MASK32, 0]
        elif op == "RND":
            w = [code, _reg(ln[1]), 0, 0]
        else:
            raise ValueError(op)
        words.extend(w)
        idx += 1
    return words


def manifest(genome: List[int], *, n_regs: int, tape_words: int, persist: str,
             tick_budget: int = 256, out_cap: int = 1, code_writable: bool = False) -> dict:
    m = {"schema_version": SCHEMA, "n_regs": n_regs, "tape_words": tape_words, "genome": genome,
         "code_writable": code_writable, "persist": persist, "tick_budget": tick_budget, "out_cap": out_cap}
    validate_manifest(m)
    return m


def organism(name: str, m: dict) -> dict:
    from proteus.foundry.generate import organism_record
    rec = organism_record(m, None, 0)
    rec["control_name"] = name
    return rec


# ---------------------------------------------------------------- nulls
CONST0 = manifest(asm([("LDC", "r0", 0), ("LDC", "r1", 0), ("OUT", "r0", "r1"), ("HALT",)]),
                  n_regs=2, tape_words=16, persist="none")

ECHO_LAST = manifest(asm([
    ("LDC", "r7", 0),
    ("label", "L"),
    ("INQ", "r2", "r7"),
    ("JZ", "r2", "OUT"),
    ("IN", "r1", "r7"),
    ("JMP", "L"),
    ("label", "OUT"),
    ("OUT", "r1", "r7"),
    ("HALT",),
]), n_regs=8, tape_words=32, persist="none")

# ---------------------------------------------------------------- POS: one value in a register
# PUT [1,tag,v] -> r4 := v (D=1) ; ASK [2,tag] -> OUT r4. persist=regs keeps r4 across ticks.
POS_REGS = manifest(asm([
    ("LDC", "r7", 0),
    ("IN", "r0", "r7"),                       # kind
    ("LDC", "r1", 1),
    ("EQ", "r2", "r0", "r1"),
    ("JZ", "r2", "ASKCHK"),
    ("IN", "r3", "r7"),                       # tag (unused)
    ("IN", "r4", "r7"),                       # v
    ("HALT",),
    ("label", "ASKCHK"),
    ("LDC", "r1", 2),
    ("EQ", "r2", "r0", "r1"),
    ("JZ", "r2", "END"),
    ("OUT", "r4", "r7"),
    ("label", "END"),
    ("HALT",),
]), n_regs=8, tape_words=64, persist="regs")

# ---------------------------------------------------------------- POS: tag table on the tape
# (tag, s) pairs from BASE; count at BASE-1; PUT accumulates s += v (ADD op); ASK outputs s.
_TABLE_LINES = [
    ("LDC", "r7", 0),
    ("LDC", "r10", 1),
    ("LDC", "r8", 2),
    ("LDC", "r9", "BASE"),
    ("LDC", "r11", "COUNT"),
    ("IN", "r0", "r7"),                       # kind
    ("LDC", "r5", 1),
    ("EQ", "r4", "r0", "r5"),
    ("JZ", "r4", "ASKCHK"),
    ("IN", "r1", "r7"),                       # tag
    ("IN", "r2", "r7"),                       # v
    ("MOV", "r3", "r9"),                      # ptr = base
    ("LD", "r6", "r11"),                      # count
    ("LDC", "r4", 0),                         # i
    ("label", "PLOOP"),
    ("EQ", "r12", "r4", "r6"),
    ("JNZ", "r12", "NOTFOUND"),
    ("LD", "r13", "r3"),
    ("EQ", "r12", "r13", "r1"),
    ("JNZ", "r12", "FOUND"),
    ("ADD", "r3", "r3", "r8"),
    ("ADD", "r4", "r4", "r10"),
    ("JMP", "PLOOP"),
    ("label", "NOTFOUND"),
    ("ST", "r3", "r1"),
    ("ADD", "r3", "r3", "r10"),
    ("ST", "r3", "r2"),
    ("ADD", "r6", "r6", "r10"),
    ("ST", "r11", "r6"),
    ("HALT",),
    ("label", "FOUND"),
    ("ADD", "r3", "r3", "r10"),
    ("LD", "r13", "r3"),
    ("ADD", "r13", "r13", "r2"),
    ("ST", "r3", "r13"),
    ("HALT",),
    ("label", "ASKCHK"),
    ("LDC", "r5", 2),
    ("EQ", "r4", "r0", "r5"),
    ("JZ", "r4", "END"),
    ("IN", "r1", "r7"),                       # tag
    ("MOV", "r3", "r9"),
    ("LD", "r6", "r11"),
    ("LDC", "r4", 0),
    ("label", "ALOOP"),
    ("EQ", "r12", "r4", "r6"),
    ("JNZ", "r12", "END"),
    ("LD", "r13", "r3"),
    ("EQ", "r12", "r13", "r1"),
    ("JNZ", "r12", "OUTF"),
    ("ADD", "r3", "r3", "r8"),
    ("ADD", "r4", "r4", "r10"),
    ("JMP", "ALOOP"),
    ("label", "OUTF"),
    ("ADD", "r3", "r3", "r10"),
    ("LD", "r13", "r3"),
    ("OUT", "r13", "r7"),
    ("label", "END"),
    ("HALT",),
]


def _table_manifest(tape_words: int = 256) -> dict:
    n_instr = sum(1 for ln in _TABLE_LINES if ln[0] != "label")
    base = n_instr * 4 + 8
    lines = [tuple(("BASE" and base) if x == "BASE" else (base - 1 if x == "COUNT" else x) for x in ln)
             for ln in _TABLE_LINES]
    return manifest(asm(lines), n_regs=14, tape_words=tape_words, persist="all", tick_budget=512)


POS_TABLE = _table_manifest()

POSITIVE = {"W0": POS_REGS, "W1": POS_REGS, "W2": POS_TABLE, "W3": POS_TABLE}
NULLS = {"CONST0": CONST0, "ECHO_LAST": ECHO_LAST}

# ---------------------------------------------------------------- v0.2 boundary organisms
# SELECTIVE: one (tag, last value) slot per entity seen; PUT replaces, RETIRE stores 0.
# FULL_LOG: appends every (tag, value) / (tag, 0) it sees; ASK scans the log BACKWARDS for
# the tag (re-reads history). Neither is ever a seed for evolution; they map the economics.
_SELECTIVE_LINES = [
    ("LDC", "r7", 0), ("LDC", "r10", 1), ("LDC", "r8", 2), ("LDC", "r9", "BASE"), ("LDC", "r11", "COUNT"),
    ("IN", "r0", "r7"),
    ("LDC", "r5", 1), ("EQ", "r4", "r0", "r5"), ("JNZ", "r4", "PUT"),
    ("LDC", "r5", 9), ("EQ", "r4", "r0", "r5"), ("JNZ", "r4", "RET"),
    ("LDC", "r5", 2), ("EQ", "r4", "r0", "r5"), ("JNZ", "r4", "ASK"),
    ("HALT",),
    ("label", "PUT"), ("IN", "r1", "r7"), ("IN", "r2", "r7"), ("JMP", "UPSERT"),
    ("label", "RET"), ("IN", "r1", "r7"), ("LDC", "r2", 0),
    ("label", "UPSERT"), ("MOV", "r3", "r9"), ("LD", "r6", "r11"), ("LDC", "r4", 0),
    ("label", "PLOOP"), ("EQ", "r12", "r4", "r6"), ("JNZ", "r12", "NOTFOUND"),
    ("LD", "r13", "r3"), ("EQ", "r12", "r13", "r1"), ("JNZ", "r12", "FOUND"),
    ("ADD", "r3", "r3", "r8"), ("ADD", "r4", "r4", "r10"), ("JMP", "PLOOP"),
    ("label", "NOTFOUND"), ("ST", "r3", "r1"), ("ADD", "r3", "r3", "r10"), ("ST", "r3", "r2"),
    ("ADD", "r6", "r6", "r10"), ("ST", "r11", "r6"), ("HALT",),
    ("label", "FOUND"), ("ADD", "r3", "r3", "r10"), ("ST", "r3", "r2"), ("HALT",),
    ("label", "ASK"), ("IN", "r1", "r7"), ("MOV", "r3", "r9"), ("LD", "r6", "r11"), ("LDC", "r4", 0),
    ("label", "ALOOP"), ("EQ", "r12", "r4", "r6"), ("JNZ", "r12", "END"),
    ("LD", "r13", "r3"), ("EQ", "r12", "r13", "r1"), ("JNZ", "r12", "OUTF"),
    ("ADD", "r3", "r3", "r8"), ("ADD", "r4", "r4", "r10"), ("JMP", "ALOOP"),
    ("label", "OUTF"), ("ADD", "r3", "r3", "r10"), ("LD", "r13", "r3"), ("OUT", "r13", "r7"),
    ("label", "END"), ("HALT",),
]

_FULLLOG_LINES = [
    ("LDC", "r7", 0), ("LDC", "r10", 1), ("LDC", "r8", 2), ("LDC", "r9", "BASE"), ("LDC", "r11", "COUNT"),
    ("IN", "r0", "r7"),
    ("LDC", "r5", 1), ("EQ", "r4", "r0", "r5"), ("JNZ", "r4", "PUT"),
    ("LDC", "r5", 9), ("EQ", "r4", "r0", "r5"), ("JNZ", "r4", "RET"),
    ("LDC", "r5", 2), ("EQ", "r4", "r0", "r5"), ("JNZ", "r4", "ASK"),
    ("HALT",),
    ("label", "PUT"), ("IN", "r1", "r7"), ("IN", "r2", "r7"), ("JMP", "APPEND"),
    ("label", "RET"), ("IN", "r1", "r7"), ("LDC", "r2", 0),
    ("label", "APPEND"), ("LD", "r6", "r11"), ("MUL", "r3", "r6", "r8"), ("ADD", "r3", "r3", "r9"),
    ("ST", "r3", "r1"), ("ADD", "r3", "r3", "r10"), ("ST", "r3", "r2"),
    ("ADD", "r6", "r6", "r10"), ("ST", "r11", "r6"), ("HALT",),
    ("label", "ASK"), ("IN", "r1", "r7"), ("LD", "r6", "r11"),
    ("label", "SLOOP"), ("JZ", "r6", "END"), ("SUB", "r6", "r6", "r10"),
    ("MUL", "r3", "r6", "r8"), ("ADD", "r3", "r3", "r9"), ("LD", "r13", "r3"),
    ("EQ", "r12", "r13", "r1"), ("JZ", "r12", "SLOOP"),
    ("ADD", "r3", "r3", "r10"), ("LD", "r13", "r3"), ("OUT", "r13", "r7"), ("HALT",),
    ("label", "END"), ("HALT",),
]


def _bind(lines, tape_words: int, tick_budget: int) -> dict:
    n_instr = sum(1 for ln in lines if ln[0] != "label")
    base = n_instr * 4 + 8
    bound = [tuple(base if x == "BASE" else (base - 1 if x == "COUNT" else x) for x in ln) for ln in lines]
    return manifest(asm(bound), n_regs=14, tape_words=tape_words, persist="all", tick_budget=tick_budget)


SELECTIVE = _bind(_SELECTIVE_LINES, 512, 1024)      # code ~230 words + up to ~140 slots (v0.2.1)
FULL_LOG = _bind(_FULLLOG_LINES, 2048, 8192)        # code ~200 words + ~900 log entries
TRIVIAL = POS_REGS                                  # the last value seen, in a register
BOUNDARY = {"FULL_LOG": FULL_LOG, "SELECTIVE": SELECTIVE, "TRIVIAL": TRIVIAL}
