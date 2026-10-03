"""Designed organisms for the P1 calibration slice.

Each is a short program for WM-mini (wm_mini.py). They are the calibration set
of REQUIREMENTS.md section 1.3:

  POSITIVE   builder(m)     writes stimulus -> response into the PERSISTENT store
                            for the first m stimuli; m = K is the full builder;
                            graded m gives graded positives with a known answer
  NEGATIVE   holder         the same logic using FAST memory only, so it cannot
                            carry anything across an episode boundary
  IMPOSTORS  constant       always answers 0
             lookup         inherits the mapping of ONE life in its genome and
                            writes nothing (scores perfectly on that life only)
             leak_reader    answers with its raw observation (only works in the
                            deliberately leaky world of a fire test)

The "smuggler" impostor is not a separate program. It is the holder run under
a harness that fails to reset fast memory (a fire test of the harness check).
"""
import numpy as np
from wm_mini import (NOP, IN, PH, SET, MOV, ADD, SUB, SKZ, SKNZ, SKEQ, SKLT,
                     STW, STR, FW, FR, OUT, HALT, JMP, XOR, OPNAMES, NOPS, mapping)


def asm(words):
    """List of (op, a, b, c) tuples -> int64 array [n, 4]."""
    return np.array([tuple(w) + (0,) * (4 - len(w)) for w in words], dtype=np.int64)


def listing(prog):
    return "\n".join("%2d  %-5s %d %d %d" % (i, OPNAMES[int(w[0]) % NOPS], w[1], w[2], w[3])
                     for i, w in enumerate(prog))


def builder(m, write=STW, read=STR):
    """Store the answer for stimuli s < m and use it later.

    r0 = stimulus (kept from the stimulus phase to the feedback phase)
    Cells hold answer + 1, so 0 means "nothing stored".
    """
    return asm([
        (PH, 6),            # 0  r6 = phase
        (SKZ, 6),           # 1  phase 0: skip the jump
        (JMP, 0, 0, 10),    # 2  phase 1: to 13
        (IN, 0),            # 3  r0 = s
        (SET, 5, m),        # 4  r5 = m
        (SKLT, 0, 5),       # 5  s < m: skip the jump
        (JMP, 0, 0, 4),     # 6  s >= m: to 11 (guess)
        (read, 1, 0),       # 7  r1 = cell[s]
        (SET, 7, 1),        # 8  r7 = 1
        (SUB, 2, 1, 7),     # 9  r2 = r1 - 1
        (OUT, 2),           # 10 answer
        (SET, 2, 0),        # 11 guess 0
        (OUT, 2),           # 12
        (IN, 3),            # 13 r3 = correct answer
        (SET, 5, m),        # 14
        (SKLT, 0, 5),       # 15 s < m: skip the halt
        (HALT,),            # 16
        (SET, 7, 1),        # 17
        (ADD, 3, 3, 7),     # 18 r3 = answer + 1
        (write, 0, 3),      # 19 cell[s] = answer + 1
        (HALT,),            # 20
    ])


def holder(m):
    """The builder's logic on fast memory. Same length, same structure."""
    return builder(m, write=FW, read=FR)


def constant():
    return asm([(SET, 0, 0), (OUT, 0)])


def lookup():
    """Reads an inherited table and never writes."""
    return asm([(IN, 0), (STR, 1, 0), (SET, 7, 1), (SUB, 2, 1, 7), (OUT, 2)])


def lookup_store(seed, life, K, R, S):
    """The inherited table: the mapping of one life, as answer + 1."""
    st = np.zeros(S, dtype=np.int64)
    for s in range(K):
        st[s] = mapping(seed, life, s, R) + 1
    return st


def leak_reader():
    return asm([(IN, 0), (OUT, 0)])


def empty_store(S):
    return np.zeros(S, dtype=np.int64)


def builder_min():
    """The shortest builder: 8 instructions, every one of them needed.

    Stores the answer itself (no "+1"), so an empty cell reads as answer 0.
    This is the target of the search-power measurement in reach.py.
    """
    return asm([
        (PH, 6),            # 0  r6 = phase
        (SKZ, 6),           # 1  phase 0: skip the jump
        (JMP, 0, 0, 3),     # 2  phase 1: to 6
        (IN, 0),            # 3  r0 = s
        (STR, 1, 0),        # 4  r1 = store[s]
        (OUT, 1),           # 5  answer
        (IN, 3),            # 6  r3 = correct answer
        (STW, 0, 3),        # 7  store[s] = answer
    ])
