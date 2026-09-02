"""The V0 affordance table. Published, versioned, hashed. Amendment A2.

Every primitive here is a minimal computational affordance from one of the ten categories the
external review allowed. Nothing here names a cognitive function. There is no cost opcode:
resource information, if a world chooses to expose it, arrives through the opaque input
channels like any other value (A2: "randomness does not intrinsically know its cost").

Instruction format: FOUR consecutive tape words (op, a, b, c). Every word is a 32-bit unsigned
integer. `op` is taken modulo N_OPCODES, so EVERY tape word sequence is a valid program and
mutation can never produce an illegal instruction. `a` and `b` are register indices modulo the
organism's register count. `c` is a register index (modulo register count) for three-register
ops, a signed 32-bit immediate for LDC, and a signed instruction offset for jumps.

Category ids are the primitive CLASSES for the knockout signature (A5). The knockout null rule
is: every instruction whose opcode is in the class is rewritten to NOP with operands preserved.
NOP therefore exists as the null element of the table and belongs to the halt/yield class;
knocking out that class rewrites HALT and YIELD to NOP.

The table's identity is `AFFORDANCE_HASH`, the sha256 of its canonical serialisation. The
runtime identity (identity.py) folds this in, so a change to the table is a change of runtime.
"""
from __future__ import annotations

import hashlib
import json

# (opcode, mnemonic, category, operand shape, one-line semantics)
TABLE = (
    (0,  "NOP",  "halt_yield",    "-",        "no effect; null element for knockout"),
    (1,  "HALT", "halt_yield",    "-",        "end this tick; instruction pointer resets to 0 next tick"),
    (2,  "YIELD","halt_yield",    "-",        "end this tick; resume at the next instruction next tick"),
    (3,  "LDC",  "read_write",    "a,imm",    "r[a] = imm (32-bit)"),
    (4,  "MOV",  "read_write",    "a,b",      "r[a] = r[b]"),
    (5,  "LD",   "indirection",   "a,b",      "r[a] = tape[r[b] mod tape_words]"),
    (6,  "ST",   "indirection",   "a,b",      "tape[r[a] mod tape_words] = r[b]; ignored inside a protected genome region"),
    (7,  "ADD",  "arithmetic",    "a,b,c",    "r[a] = (r[b] + r[c]) mod 2^32"),
    (8,  "SUB",  "arithmetic",    "a,b,c",    "r[a] = (r[b] - r[c]) mod 2^32"),
    (9,  "MUL",  "arithmetic",    "a,b,c",    "r[a] = (r[b] * r[c]) mod 2^32"),
    (10, "AND",  "logical",       "a,b,c",    "r[a] = r[b] & r[c]"),
    (11, "OR",   "logical",       "a,b,c",    "r[a] = r[b] | r[c]"),
    (12, "XOR",  "logical",       "a,b,c",    "r[a] = r[b] ^ r[c]"),
    (13, "NOT",  "logical",       "a,b",      "r[a] = ~r[b] mod 2^32"),
    (14, "SHL",  "logical",       "a,b,c",    "r[a] = (r[b] << (r[c] mod 32)) mod 2^32"),
    (15, "SHR",  "logical",       "a,b,c",    "r[a] = r[b] >> (r[c] mod 32)"),
    (16, "EQ",   "comparison",    "a,b,c",    "r[a] = 1 if r[b] == r[c] else 0"),
    (17, "LT",   "comparison",    "a,b,c",    "r[a] = 1 if r[b] < r[c] (unsigned) else 0"),
    (18, "JMP",  "control",       "off",      "ip = ip + 4*off (mod tape_words), off signed"),
    (19, "JZ",   "control",       "a,off",    "if r[a] == 0: ip = ip + 4*off"),
    (20, "JNZ",  "control",       "a,off",    "if r[a] != 0: ip = ip + 4*off"),
    (21, "IN",   "opaque_io",     "a,b",      "r[a] = next unread value on input channel (r[b] mod n_in), or 0 if none"),
    (22, "INQ",  "opaque_io",     "a,b",      "r[a] = number of unread values on input channel (r[b] mod n_in)"),
    (23, "OUT",  "opaque_io",     "a,b",      "append r[a] to output channel (r[b] mod n_out); dropped beyond out_cap"),
    (24, "RND",  "randomness",    "a",        "r[a] = next 32-bit value from the externally supplied random stream"),
)

N_OPCODES = len(TABLE)
MNEMONIC = {row[0]: row[1] for row in TABLE}
CATEGORY = {row[0]: row[2] for row in TABLE}
CATEGORIES = tuple(sorted({row[2] for row in TABLE}))
OPCODES_IN = {cat: tuple(row[0] for row in TABLE if row[2] == cat) for cat in CATEGORIES}
NOP = 0

# Bounded-storage category: not an opcode class. It is the pair of manifest limits below and is
# part of the published table so that a change to the bounds is a change of affordance.
STORAGE_BOUNDS = {
    "tape_words": {"min": 16, "max": 4096},
    "n_regs": {"min": 2, "max": 16},
    "genome_words": {"min": 4, "max": 4096},
    "tick_budget": {"min": 8, "max": 65536},
    "out_cap": {"min": 1, "max": 256},
    "word_bits": 32,
    "instruction_words": 4,
}

CATEGORY_DESCRIPTIONS = {
    "halt_yield":   "halt/yield (plus the NOP null element)",
    "read_write":   "read/write of registers and constants",
    "indirection":  "tape access addressed by register contents",
    "arithmetic":   "modular arithmetic",
    "logical":      "logical/bitwise transformation",
    "comparison":   "comparison",
    "control":      "conditional control transfer",
    "opaque_io":    "opaque input/output channels",
    "randomness":   "externally supplied randomness",
}


def canonical() -> str:
    doc = {
        "table_version": "proteus.affordances.v0",
        "instruction_words": 4,
        "opcodes": [list(r) for r in TABLE],
        "storage_bounds": STORAGE_BOUNDS,
        "knockout_null_rule": "rewrite opcode to NOP (0), operands preserved, per category",
    }
    return json.dumps(doc, sort_keys=True, separators=(",", ":"))


AFFORDANCE_HASH = hashlib.sha256(canonical().encode("utf-8")).hexdigest()


def publish(path: str) -> str:
    """Write the table + hash as JSON. Called once to freeze; the audit compares against it."""
    doc = json.loads(canonical())
    doc["affordance_hash"] = AFFORDANCE_HASH
    doc["categories"] = CATEGORY_DESCRIPTIONS
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return AFFORDANCE_HASH
