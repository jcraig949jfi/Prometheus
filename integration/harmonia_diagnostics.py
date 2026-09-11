#!/usr/bin/env python3
"""HARMONIA DIAGNOSTIC ORGANISMS -- ground truth for the arena's instruments.

We cannot interpret an unknown organism until we can build one whose causal
behaviour we know by construction and recover it with the same instruments we
intend to point at the menagerie. This module builds those organisms.

THE ISA (proteus.foundry.vm, verified by reading the interpreter, not the docs)
  An instruction is FOUR words: [op, a, bw, cw]; op = word % 25.
    a  = tape[ip+1] % n_regs        -- a register index
    bw = tape[ip+2]                 -- RAW word (register index, immediate, or
                                       signed jump offset depending on op)
    cw = tape[ip+3]                 -- RAW word
  Opcodes used here:
     0 NOP
     1 HALT
     3 LOADI   regs[a] = bw
     7 ADD     regs[a] = regs[bw] + regs[cw]
    21 IN      regs[a] = inputs[regs[bw] % n_in][cursor++]     (in_reads++)
    23 OUT     outputs[regs[bw] % n_out].append(regs[a])       (out_writes++)
  Registers start at 0, so a bw naming an untouched register selects channel 0.

WHY THESE ORGANISMS EXIST
  Each one is a control with a KNOWN answer, so that an instrument returning the
  wrong answer is caught by the control rather than by a later argument about an
  unknown genome.

    WC_POS   reads channel 0 and emits it        -> MUST be world-coupled
    WC_NEG   emits a constant                    -> MUST be world-blind
    KP_DEP   A writes r0 from input, B emits r0  -> A+B has a GENUINE
                                                    cross-component dependence:
                                                    B's output depends on A
                                                    having run
    KN_INDEP A writes r5 (nothing reads it), B emits r0
                                                 -> both components execute and
                                                    both "activate", and there
                                                    is NO causal contribution
                                                    from A to B's output. This
                                                    is the known-NEGATIVE that
                                                    any interaction test must
                                                    reject.

  KN_INDEP is the important one. A test that calls it an interaction is not
  measuring interaction, it is measuring "something changed".

THE COUNTERFACTUAL THAT SETTLES CAUSATION
  proteus.compose.segments.ablate() rewrites only the OPCODE word of each
  instruction in the named component to NOP and preserves every operand, the
  length, and every other component's offsets. For straight-line components it
  is therefore SEMANTIC NEUTRALISATION AT CONSTANT LAYOUT AND CONSTANT OP COUNT
  -- the structure-preserving counterfactual we need. It stops being
  layout-neutral only if the ablated component contained a taken branch, which
  is why `is_straight_line()` is exported and checked.
"""
from __future__ import annotations

import hashlib
import json

from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import Meter, Player

NOP, HALT, LOADI, ADD, IN, OUT = 0, 1, 3, 7, 21, 23
BRANCH_OPS = {18, 19, 20}
IW = 4


def instr(op, a=0, bw=0, cw=0):
    return [op, a, bw, cw]


def genome(*instrs):
    out = []
    for i in instrs:
        out.extend(i)
    return out


def envelope(tape_words=64, n_regs=8, tick_budget=64, out_cap=8,
             persist="tape", code_writable=False):
    return {"n_regs": n_regs, "tape_words": tape_words,
            "code_writable": code_writable, "persist": persist,
            "tick_budget": tick_budget, "out_cap": out_cap}


def manifest(g, env=None):
    env = env or envelope()
    m = {"schema_version": "proteus.player_manifest.v0", "genome": list(g)}
    m.update(env)
    return m


def is_straight_line(g):
    """True if no instruction in g is a branch. Ablation is layout-neutral only
    for straight-line components, so this is a precondition, not a nicety."""
    return all(g[i] % 25 not in BRANCH_OPS for i in range(0, len(g), IW))


# ---------------------------------------------------------------- organisms
# r1 is never written, so r1 == 0 and (bw=1) selects channel 0 for IN and OUT.
SEG_READ_R0 = genome(instr(IN, 0, 1, 0))            # r0 <- channel 0
SEG_EMIT_R0 = genome(instr(OUT, 0, 1, 0), instr(HALT))
SEG_WRITE_R5 = genome(instr(LOADI, 5, 12345, 0))    # r5 <- 12345; nothing reads r5
SEG_CONST_R0 = genome(instr(LOADI, 0, 42, 0))       # r0 <- 42 (ignores the world)

ORGANISMS = {
    # world coupling, solo
    "WC_POS": genome(instr(IN, 0, 1, 0), instr(OUT, 0, 1, 0), instr(HALT)),
    "WC_NEG": genome(instr(LOADI, 0, 42, 0), instr(OUT, 0, 1, 0), instr(HALT)),
    # a reader that never emits: coupled only through state
    "WC_STATE_ONLY": genome(instr(IN, 0, 1, 0), instr(HALT)),
    # emits but never reads: the preserved negative for coupling
    "EMIT_ONLY": genome(instr(LOADI, 0, 7, 0), instr(OUT, 0, 1, 0), instr(HALT)),
    # inert
    "INERT": genome(instr(NOP), instr(HALT)),
}

# component pairs, as (A_segment, B_segment, expected_truth)
PAIRS = {
    "KP_DEP": (SEG_READ_R0, SEG_EMIT_R0,
               "A writes r0 from the world; B emits r0. B's OUTPUT depends on A."),
    "KN_INDEP": (SEG_WRITE_R5, SEG_EMIT_R0,
                 "A writes r5; nothing reads r5. B emits r0 (always 0). "
                 "Both execute. NO causal contribution from A to B."),
    "KP_CONST": (SEG_CONST_R0, SEG_EMIT_R0,
                 "A sets r0=42 with no world input; B emits r0. B's output "
                 "depends on A, but NOT on the world."),
}


# ---------------------------------------------------------------- observation
def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)


def observe(man, inputs, seed=20260905, ticks=1, n_out=2, budget=None):
    """One observation. EXECUTION and IMAGE are returned SEPARATELY and must
    never be hashed together: the runtime copies the genome onto the tape, so a
    longer genome changes the image whether or not it runs (see packet 01, L4)."""
    p = Player(man)
    st = p.fresh_state()
    rng = SplitMix64(seed)
    m = Meter()
    tr, status = [], []
    for _ in range(ticks):
        outs, s = p.run_tick(st, inputs, n_out, rng, meter=m, budget=budget)
        tr.append(outs)
        status.append(s)
        if s == "halt":
            break
    d = m.as_dict(man)
    for k in ("wall_s", "cpu_s", "footprint_words", "persistent_state_words"):
        d.pop(k, None)
    return {
        "outputs": tr,
        "statuses": status,
        "meter": d,
        "exec_hash": hashlib.sha256(canon({"m": d, "s": status, "t": tr}).encode()).hexdigest()[:12],
        "image_hash": hashlib.sha256(canon(st).encode()).hexdigest()[:12],
        "out_hash": hashlib.sha256(canon(tr).encode()).hexdigest()[:12],
    }


DEFAULT_WORLDS = [
    [[11, 12, 13, 14], [21, 22, 23, 24]],
    [[99, 98, 97, 96], [1, 2, 3, 4]],
    [[0, 0, 0, 0], [0, 0, 0, 0]],
]


def coupling(man, worlds=None, **kw):
    """Which surfaces respond to the world? Returned per surface, never merged
    into one boolean -- packet 01 L2 found one specimen transcript-sensitive and
    meter-blind, and four detectable only through state."""
    worlds = worlds or DEFAULT_WORLDS
    obs = [observe(man, w, **kw) for w in worlds]
    return {
        "output": len({o["out_hash"] for o in obs}) > 1,
        "execution": len({o["exec_hash"] for o in obs}) > 1,
        "image": len({o["image_hash"] for o in obs}) > 1,
        "any": len({(o["exec_hash"], o["image_hash"]) for o in obs}) > 1,
        "observations": obs,
    }


if __name__ == "__main__":
    print("DIAGNOSTIC ORGANISM SELF-TEST (known answers)")
    expect = {"WC_POS": True, "WC_NEG": False, "WC_STATE_ONLY": True,
              "EMIT_ONLY": False, "INERT": False}
    ok = True
    for name, g in ORGANISMS.items():
        c = coupling(manifest(g))
        got = c["any"]
        good = got == expect[name]
        ok &= good
        print("  %-14s coupled(any)=%-5s expected=%-5s %s   [out=%s exec=%s image=%s] straight_line=%s"
              % (name, got, expect[name], "OK" if good else "*** MISMATCH ***",
                 c["output"], c["execution"], c["image"], is_straight_line(g)))
    print("SELF-TEST", "PASS" if ok else "FAIL")
