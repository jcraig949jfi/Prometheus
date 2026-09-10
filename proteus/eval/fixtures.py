"""Hand-authored programs and specifications for WP-B1, plus the WP-X8 identity fixture.

Every program here is written by hand and its expected behaviour is stated in a comment, so the
tests check the VM against human intent rather than against the VM's own output. That is the
whole point of B1-a: an independent semantic fixture, not a snapshot.

INSTRUCTION FORMAT. Four words per instruction: (op, a, b, c); `op = word mod 25`. Operand `a`
is a register index taken mod n_regs. `b` and `c` are raw words whose meaning depends on the
opcode.

LDC's IMMEDIATE IS IN SLOT b. This was determined BY EXECUTION, not by reading documentation,
because the two available sources disagree: the affordance TABLE row says `a,imm` while
`affordances.py`'s prose says the immediate is operand `c`. The prose is wrong. That is Proteus
TODO T9, and it is not fixable in place because `runtime_hash` covers the whole file including
its docstring. Verified here: LDC r0 with b=42, c=7 puts 42 in r0.
"""
from __future__ import annotations

from proteus.eval.library import make_spec

PLAYER_SCHEMA = "proteus.player_manifest.v0"

# opcode constants, for readability only
NOP, HALT, YIELD, LDC, MOV, LD, ST, ADD = 0, 1, 2, 3, 4, 5, 6, 7
EQ, IN, INQ, OUT = 16, 21, 22, 23


def program(genome, n_regs=4, tape_words=16, tick_budget=64, out_cap=4,
            code_writable=False, persist="none"):
    """A player manifest around a hand-authored genome."""
    return {"schema_version": PLAYER_SCHEMA, "n_regs": n_regs, "tape_words": tape_words,
            "genome": list(genome), "code_writable": code_writable, "persist": persist,
            "tick_budget": tick_budget, "out_cap": out_cap}


# ------------------------------------------------------------------ B1-a programs

#: Reads one value from input channel 0 and writes it to output channel 0, then halts.
#: r1 is never written, so it is 0, which selects channel 0 for both IN and OUT.
ECHO = program([IN, 0, 1, 0,
                OUT, 0, 1, 0,
                HALT, 0, 0, 0])

#: Always emits the constant 1 regardless of input, then halts.
#: Against an echo specification it passes only the case whose input is 1.
CONST_ONE = program([LDC, 0, 1, 0,
                     OUT, 0, 1, 0,
                     HALT, 0, 0, 0])

#: r0 = 20 + 22 = 42, emitted once. Pure arithmetic, no input.
ADD_20_22 = program([LDC, 0, 20, 0,
                     LDC, 1, 22, 0,
                     ADD, 2, 0, 1,
                     OUT, 2, 3, 0,          # r3 == 0 -> channel 0
                     HALT, 0, 0, 0], n_regs=4, tape_words=32)

#: Consumes TWO input values and emits their sum. Exercises input consumption order.
SUM_TWO_INPUTS = program([IN, 0, 3, 0,
                          IN, 1, 3, 0,
                          ADD, 2, 0, 1,
                          OUT, 2, 3, 0,
                          HALT, 0, 0, 0], n_regs=4, tape_words=32)

#: Emits five values into a channel whose out_cap is 2. Exercises output-cap drop semantics.
OVERFLOW = program([LDC, 0, 9, 0,
                    OUT, 0, 1, 0, OUT, 0, 1, 0, OUT, 0, 1, 0,
                    OUT, 0, 1, 0, OUT, 0, 1, 0,
                    HALT, 0, 0, 0], n_regs=4, tape_words=32, out_cap=2)

#: Halts on the very first instruction. Emits nothing. Minimum-work control.
HALT_NOW = program([HALT, 0, 0, 0])

#: No HALT anywhere. The tape beyond the genome is zeros, which decode to NOP, so the instruction
#: pointer wraps forever and the tick always ends by exhausting its op budget.
SPIN = program([NOP, 0, 0, 0])


# ------------------------------------------------------------------ specifications

def echo_spec(values=(1, 2, 3)):
    """Ordered: 'echo the single input value'. Case i has input [[values[i]]]."""
    return make_spec([{"inputs": [[v]], "expected": [[v]]} for v in values],
                     n_out=1, ticks=4, label="echo")


def constant_spec(value=42, n_cases=2):
    """Ordered: 'emit `value` on every case, regardless of input'."""
    return make_spec([{"inputs": [[i]], "expected": [[value]]} for i in range(n_cases)],
                     n_out=1, ticks=4, label="constant")


def sum_spec(pairs=((1, 2), (10, 20))):
    return make_spec([{"inputs": [[a, b]], "expected": [[a + b]]} for a, b in pairs],
                     n_out=1, ticks=4, label="sum-two")


def no_expectation_spec():
    """Cases with `expected` = None can never be the witness."""
    return make_spec([{"inputs": [[1]], "expected": None},
                      {"inputs": [[2]], "expected": None}], n_out=1, ticks=4, label="observe")


# ------------------------------------------------------------------ WP-X8 identity fixture

def x8_equal_score_pair():
    """Two artifacts with EQUAL score and DIFFERENT observable behaviour (X8-a).

    Both score zero against `echo_spec()`: neither emits anything, so neither passes any case.
    A score-only view cannot tell them apart. Their EXECUTION is plainly different:

        HALT_NOW  halts on instruction 1        status "halt",   1 op,  1 tick
        SPIN      never halts, wraps on NOPs    status "budget", tick_budget ops

    This is the shape X8 needs: equal score must not imply equal behaviour, so retention keyed on
    score alone would discard a real distinction. Nothing here says either artifact is better;
    both score zero and neither is called interesting.
    """
    return {"a": HALT_NOW, "b": SPIN, "spec": echo_spec()}
