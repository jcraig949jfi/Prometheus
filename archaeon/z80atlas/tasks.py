"""Tasks with accessibility manipulations (Cycle 8 carried in as reward geometry + input regime), witnesses and replicators.

Task = (name, n_inputs, expected(inputs, params), grading). Grading: EXACT (all-or-nothing per case: an atomic constant) or
GRADED (1 - |out - expected| / 128: an incrementally reachable constant). Input regime: FORCED_READ (cases differ) or
ANSWER_BEFORE_READ (all cases in an epoch share one input, so a constant answer scores until the input changes: a moat).
Fresh cases are seeded from (run_seed, epoch, cell): an organism cannot memorise them; a FIXED replay exists only to
detect that exploit.
"""
from __future__ import annotations

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas.vm import I

TASKS = {
    "none":             {"n_in": 0, "grading": "NONE", "regime": "FORCED_READ"},
    "CONST_atomic":     {"n_in": 0, "grading": "EXACT", "regime": "FORCED_READ", "K": 0xB7},
    "CONST_incremental": {"n_in": 0, "grading": "GRADED", "regime": "FORCED_READ", "K": 0xB7},
    "ECHO_forced":      {"n_in": 1, "grading": "EXACT", "regime": "FORCED_READ"},
    "ECHO_abr":         {"n_in": 1, "grading": "EXACT", "regime": "ANSWER_BEFORE_READ"},
    "INC1":             {"n_in": 1, "grading": "EXACT", "regime": "FORCED_READ"},
    "NEG":              {"n_in": 1, "grading": "EXACT", "regime": "FORCED_READ"},
    "COND_1edit":       {"n_in": 1, "grading": "EXACT", "regime": "FORCED_READ"},
    "COND_multi":       {"n_in": 1, "grading": "EXACT", "regime": "FORCED_READ"},
    "ADD2":             {"n_in": 2, "grading": "EXACT", "regime": "FORCED_READ"},
}
CURRICULUM = ["ECHO_forced", "INC1", "COND_multi"]


def expected(name: str, ins, params: dict) -> int:
    K = params.get("K", TASKS[name].get("K", 0))
    if name.startswith("CONST"): return K & 255
    if name.startswith("ECHO"): return ins[0]
    if name == "INC1": return (ins[0] + 1) & 255
    if name == "NEG": return (-ins[0]) & 255
    if name == "COND_1edit": return ins[0] | 0x80
    if name == "COND_multi": return (ins[0] + 1) & 255 if ins[0] < 128 else (ins[0] - 1) & 255
    if name == "ADD2": return (ins[0] + ins[1]) & 255
    return 0


def cases(name: str, seed_parts, n_cases: int, epoch: int):
    """Fresh input cases. ANSWER_BEFORE_READ: one input shared by every case of the epoch (changes each epoch)."""
    t = TASKS[name]; n_in = t["n_in"]
    if n_in == 0:
        return [()] * n_cases
    if t["regime"] == "ANSWER_BEFORE_READ":
        r = SplitMix64(seed_from("z80.abr", *seed_parts[:1], epoch)); shared = tuple(r.randbelow(256) for _ in range(n_in))
        return [shared] * n_cases
    r = SplitMix64(seed_from("z80.cases", *seed_parts, epoch))
    return [tuple(r.randbelow(256) for _ in range(n_in)) for _ in range(n_cases)]


def score_case(name: str, outputs, ins, params: dict) -> float:
    if name == "none": return 0.0
    if not outputs: return 0.0
    e = expected(name, ins, params); o = outputs[0]
    if TASKS[name]["grading"] == "GRADED":
        d = abs(o - e); d = min(d, 256 - d)
        return max(0.0, 1.0 - d / 128.0)
    return 1.0 if o == e else 0.0


# ---------------------------------------------------------------- witnesses (positive controls) and replicators
def pad(bs, G):
    b = bytearray(bs); b += bytes(G - len(b)); return bytes(b[:G])


WITNESS = {
    "CONST_atomic": [I(1, 0), 0xB7, I(22, 0), I(23)],
    "CONST_incremental": [I(1, 0), 0xB7, I(22, 0), I(23)],
    "ECHO_forced": [I(21, 0), I(22, 0), I(23)],
    "ECHO_abr": [I(21, 0), I(22, 0), I(23)],
    "INC1": [I(21, 0), I(5, 0), I(22, 0), I(23)],
    "NEG": [I(21, 0), I(25), I(22, 0), I(23)],
    "COND_1edit": [I(21, 0), I(1, 1), 0x80, I(9, 1), I(22, 0), I(23)],
    "COND_multi": [I(21, 0), I(1, 1), 0x80, I(12, 1), I(17), 0x03, I(6, 0), I(14), 0x01, I(5, 0), I(22, 0), I(23)],
    "ADD2": [I(21, 0), I(21, 1), I(3, 1), I(22, 0), I(23)],
}


def replicator(copy_prim: bool) -> list:
    """Known replicator: copies its whole tape into the neighbour window, then halts."""
    if copy_prim:
        #        LD B,0     LD C,128       LD A,LEN  LD D,A       COPY   DEC D    JNZ -4        HALT
        return [I(1, 1), 0, I(1, 2), 128, I(28), I(2, 3, 1), I(20), I(6, 3), I(16), 0xFC, I(23)]
    #        LD B,0     LD C,128      LD A,(B)  LD (C),A     INC B    INC C    LD A,LEN CMP A,B  JNZ -8       HALT
    return [I(1, 1), 0, I(1, 2), 128, I(18, 1), I(18, 2, 1), I(5, 1), I(5, 2), I(28), I(12, 1), I(16), 0xF8, I(23)]


def task_then_replicate(task: str, copy_prim: bool) -> list:
    """A hybrid witness: solve the task, then copy the whole tape (shared-tape entanglement, hand-built)."""
    w = list(WITNESS[task])[:-1]                       # drop HALT
    return w + replicator(copy_prim)
