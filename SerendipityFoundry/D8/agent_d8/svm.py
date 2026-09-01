"""SVM-8: the frozen computational substrate for agent D-8.

PHYSICS (frozen at generation freeze; hash in frozen/MANIFEST.json):

- Values: unsigned 8-bit integers; all arithmetic wraps mod 256 (wraparound is
  legal physics, not a bug).
- Operand stack, capacity 12. Pop on an empty stack yields 0. Push on a full
  stack silently discards the BOTTOM element (lossy; legal physics).
- One scratch register R (initialized 0), accessed by STO/RCL (aliasing /
  self-interaction is legal physics).
- A program is a sequence of integer tokens:
      0..25          opcode
      256 + v        push literal v (v in 0..255)
      >= 1000        macro reference; expanded by the SEARCH layer before
                     execution. The VM itself never sees macro tokens.
  A bare CONST opcode (token 3) pushes 0.
- Max program length AFTER macro expansion: 12 tokens.
- Straight-line, total, deterministic. Execution cost = tokens executed.
- Task interface: three input bytes (x0, x1, x2); output = top of stack at
  program end (0 if the stack is empty).

Nothing here is sanitized: dead code, redundant ops, destructive stack moves,
pathological arithmetic and noncanonical representations are all legal.
"""

import hashlib
import random


def rng(*key):
    """Deterministic named RNG. All randomness in D-8 flows through this."""
    h = hashlib.sha256(("|".join(map(str, key))).encode()).digest()
    return random.Random(int.from_bytes(h[:12], "big"))


(LD0, LD1, LD2, CONST, ADD, SUB, MUL, MULHI, AND_, OR_, XOR, NOT_, SHL, SHR,
 INC, DEC, NEG, DUP, SWAP, OVER, DROP, STO, RCL, EQ, LT, SEL) = range(26)

NBASE = 26
STACK_CAP = 12
MAXLEN = 12

OPNAMES = ["LD0", "LD1", "LD2", "CONST", "ADD", "SUB", "MUL", "MULHI", "AND",
           "OR", "XOR", "NOT", "SHL", "SHR", "INC", "DEC", "NEG", "DUP",
           "SWAP", "OVER", "DROP", "STO", "RCL", "EQ", "LT", "SEL"]


def run(prog, x0, x1, x2):
    """Execute a base-token program. Returns (output_byte, steps). Total."""
    st = []
    R = 0
    steps = 0
    for t in prog:
        steps += 1
        if t >= 256:
            if len(st) >= STACK_CAP:
                del st[0]
            st.append(t - 256)
            continue
        if t == LD0:
            v = x0
        elif t == LD1:
            v = x1
        elif t == LD2:
            v = x2
        elif t == CONST:
            v = 0
        elif t == ADD:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = (a + b) & 255
        elif t == SUB:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = (a - b) & 255
        elif t == MUL:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = (a * b) & 255
        elif t == MULHI:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = ((a * b) >> 8) & 255
        elif t == AND_:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = a & b
        elif t == OR_:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = a | b
        elif t == XOR:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = a ^ b
        elif t == NOT_:
            a = st.pop() if st else 0
            v = (~a) & 255
        elif t == SHL:
            a = st.pop() if st else 0
            v = (a << 1) & 255
        elif t == SHR:
            a = st.pop() if st else 0
            v = a >> 1
        elif t == INC:
            a = st.pop() if st else 0
            v = (a + 1) & 255
        elif t == DEC:
            a = st.pop() if st else 0
            v = (a - 1) & 255
        elif t == NEG:
            a = st.pop() if st else 0
            v = (-a) & 255
        elif t == DUP:
            v = st[-1] if st else 0
        elif t == SWAP:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            if len(st) >= STACK_CAP:
                del st[0]
            st.append(b)
            if len(st) >= STACK_CAP:
                del st[0]
            st.append(a)
            continue
        elif t == OVER:
            v = st[-2] if len(st) >= 2 else 0
        elif t == DROP:
            if st:
                st.pop()
            continue
        elif t == STO:
            R = st.pop() if st else 0
            continue
        elif t == RCL:
            v = R
        elif t == EQ:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = 255 if a == b else 0
        elif t == LT:
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = 255 if a < b else 0
        elif t == SEL:
            c = st.pop() if st else 0
            b = st.pop() if st else 0
            a = st.pop() if st else 0
            v = a if c != 0 else b
        else:
            v = 0
        if len(st) >= STACK_CAP:
            del st[0]
        st.append(v)
    return (st[-1] if st else 0), steps


def disasm(prog):
    out = []
    for t in prog:
        if t >= 1000:
            out.append("MAC%d" % (t - 1000))
        elif t >= 256:
            out.append("#%d" % (t - 256))
        else:
            out.append(OPNAMES[t])
    return " ".join(out)
