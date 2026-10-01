"""W2-10 constructs: a bilateral pair-tape copier prefix + an answer routine, padded to 64 bytes.

COPIER (7 bytes, state-free on the pair tape, either side):
    ED 32      SELF        HL = own base (0 or 64), BC = own length (64)
    7D         LD A,L
    EE 40      XOR 0x40    A = base ^ 64 = the other half's base
    5F         LD E,A      DE = other half (D is irrelevant: the 128-byte tape masks addresses to 7 bits)
    E5         LDIR alias  (dense VM) copy own 64 bytes onto the partner half
Under task scoring (tasks.score: plain z8, ops_enabled = 0) SELF is a 2-byte no-op and E5 is a 1-byte NOP,
so the prefix only clobbers A/E/flags before the answer routine starts; the routine re-derives everything.

ANSWER ROUTINES
  W  = tasks.witness(FORCED_READ ADD37): the cell's nominal task, solved exactly.
  U  = universal: reads 3 bytes, detects read order (FORCED_READ key is in [1,255]; under ANSWER_BEFORE_READ
       the 2nd byte is the regime in {0,1} and the 3rd IN returns 0), regime 0 -> base, regime 1 -> base
       (NEUTRAL_BRIDGE half credit; the transform is not observable from the inputs).
  UA = U but regime 1 under FORCED_READ answers base+37 (ADD37), so it solves the nominal task exactly too.
"""
from __future__ import annotations
import random
from common import tasks, z8_plain

COPIER = bytes.fromhex("ED327DEE405FE5")


def _asm(src):
    return z8_plain.asm(src)[0]


def witness():
    return tasks.witness(tasks.TaskSpec(transform="ADD37", read_order="FORCED_READ", bridge="NEUTRAL_BRIDGE"))


U_SRC = """
    IN
    LD B,A        ; x1
    IN
    LD C,A        ; x2
    IN
    LD D,A        ; x3
    LD A,C
    CP 2
    JRC abr       ; x2 < 2 -> ANSWER_BEFORE_READ (base = x1, regime = x2)
    LD A,B
    XOR C         ; FORCED_READ base = x1 ^ x2, regime = x3
    OUT
    HALT
abr:
    LD A,B
    OUT
    HALT
"""

UA_SRC = """
    IN
    LD B,A
    IN
    LD C,A
    IN
    LD D,A
    LD A,C
    CP 2
    JRC abr
    LD A,B
    XOR C
    LD B,A
    LD A,D
    CP 0
    LD A,B
    JRZ emit
    ADD A,37
emit:
    OUT
    HALT
abr:
    LD A,B
    OUT
    HALT
"""

ROUTINES = {"W": witness, "U": lambda: _asm(U_SRC), "UA": lambda: _asm(UA_SRC)}


def pad(g, seed=20261001, n=64):
    rng = random.Random(seed)
    tail = bytearray()
    while len(g) + len(tail) < n:
        b = rng.randrange(256)
        tail.append(b)
    return bytes(g) + bytes(tail)


def genomes():
    out = {}
    for k, f in ROUTINES.items():
        out["ANS_" + k] = pad(f())                 # answer routine alone
        out["CT_" + k] = pad(COPIER + f())          # copier + answer routine
    out["COPY_ONLY"] = pad(COPIER)
    out["KNOWN_2E001E40E5"] = pad(bytes.fromhex("2E001E40E5"))
    return out


if __name__ == "__main__":
    for k, g in genomes().items():
        print(k, len(g), g.hex().upper())
        if k.startswith("CT_"):
            for a, s in z8_plain.dis(g, limit=len(COPIER) + len(ROUTINES[k[3:]]())):
                print("   %02X  %s" % (a, s))
