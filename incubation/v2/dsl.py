"""dsl.py — the search-program grammar and its canonical enumeration.

A program is a STAGE or a SEQ of two stages (well-typed only on via-tasks):

    STAGE := (procs, sched, halt)
      procs : 1..2 specs, each (root, gen), root in {A: stage start, Z: stage goal},
              gen in {S: successors, P: predecessors}; pairs stored sorted (unordered)
      sched : (ONLY,i) | (ALT,) | (IF, obs_a, op, obs_b)
              IF compares obs_a measured on proc0 with obs_b on proc1 (op in {LE,GT});
              true -> expand proc0 else proc1. "Expand the smaller frontier" is a
              CONSTRUCTED policy here, not a token.
      halt  : GOAL | MEET | ANY

There is no BIDIRECTIONAL token, no INTERSECT-and-return combinator, no oriented
"backward search" primitive. A meet-in-the-middle organization requires jointly
choosing a (A,S) process, a (Z,P) process, a schedule that actually advances both, and
a MEET or ANY halt — one region of a space the census must show is neither dominated by
that region nor trivially indexed to it.

Enumeration is canonical and frozen before any run: sorted by (size, serial string).
The sha256 of the full enumeration is recorded in the preregistration so the order
cannot be tuned after the fact.
"""
from __future__ import annotations

import hashlib

SPECS = (("A", "S"), ("A", "P"), ("Z", "S"), ("Z", "P"))
OBS = ("DEPTH", "DUPS", "FSIZE")
OPS = ("GT", "LE")
HALTS = ("ANY", "GOAL", "MEET")

BASELINE = ("STAGE", (("A", "S"),), ("ONLY", 0), "GOAL")     # the fixed forward solver


def stage_programs():
    progs = []
    for spec in SPECS:
        progs.append(("STAGE", (spec,), ("ONLY", 0), "GOAL"))
    pairs = [(SPECS[i], SPECS[j]) for i in range(len(SPECS))
             for j in range(i, len(SPECS))]
    scheds = [("ONLY", 0), ("ONLY", 1), ("ALT",)] + \
             [("IF", a, op, b) for a in OBS for op in OPS for b in OBS]
    for pair in pairs:
        for sched in scheds:
            for halt in HALTS:
                progs.append(("STAGE", pair, sched, halt))
    return progs


def size(prog):
    if prog[0] == "SEQ":
        return 1 + size(prog[1]) + size(prog[2])
    _t, procs, sched, _h = prog
    ssz = 4 if sched[0] == "IF" else 1
    return 1 + 2 * len(procs) + ssz + 1


def serial(prog):
    if prog[0] == "SEQ":
        return f"SEQ({serial(prog[1])},{serial(prog[2])})"
    _t, procs, sched, halt = prog
    p = "+".join(f"{r}{g}" for r, g in procs)
    s = ":".join(str(x) for x in sched)
    return f"STAGE[{p}|{s}|{halt}]"


def enumerate_stage():
    return sorted(stage_programs(), key=lambda p: (size(p), serial(p)))


def enumerate_seq(stages=None):
    """All SEQ programs over the stage space, canonical (size, serial) order."""
    stages = stages if stages is not None else enumerate_stage()
    pairs = [("SEQ", a, b) for a in stages for b in stages]
    pairs.sort(key=lambda p: (size(p), serial(p)))
    return pairs


def enumeration_sha(programs):
    h = hashlib.sha256()
    for p in programs:
        h.update(serial(p).encode())
        h.update(b"\n")
    return h.hexdigest()[:16]


# ── preregistered structural classifier ─────────────────────────────────────────────

def classify(artifact, trace=None):
    """Executable macro-vs-architecture rule, fixed before any run.

    MACRO          a word of domain primitives (extends an action alphabet)
    NOT_NEW        exactly the baseline program
    PARAMETRIC     single successor-process from the start with GOAL halt — same
                   topology and control class as the baseline, whatever the tokens
    ARCHITECTURAL  anything that changes computation's topology or control policy:
                   >=2 processes, any predecessor generator, any non-GOAL halt, or
                   multi-stage sequencing. When a trace is supplied, the behavioral
                   record must agree (a structural claim unexercised at runtime does
                   not count).
    """
    if isinstance(artifact, dict) and artifact.get("kind") == "macro":
        return "MACRO"
    prog = artifact["prog"] if isinstance(artifact, dict) else artifact
    if prog == BASELINE:
        return "NOT_NEW"

    def stages(p):
        return [p[1], p[2]] if p[0] == "SEQ" else [p]

    structural = prog[0] == "SEQ"
    for st in stages(prog):
        _t, procs, _s, halt = st
        if len(procs) >= 2 or any(g == "P" for _r, g in procs) or halt != "GOAL":
            structural = True
    if not structural:
        return "PARAMETRIC"
    if trace is not None:
        behavioral = (trace["spawned"] >= 2 or "P" in trace["gens"]
                      or trace["halt"] in ("meet", "goal_bwd"))
        if not behavioral:
            return "PARAMETRIC"
    return "ARCHITECTURAL"
