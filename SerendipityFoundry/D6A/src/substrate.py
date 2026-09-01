"""D6-A FROZEN SUBSTRATE.

Machine-native artifact = straight-line boolean program over N_IN inputs.
Whole-domain semantics of a wire = one DOM-bit integer (its full truth table).
Nothing in this file knows about tasks, targets, families, or history.

FROZEN once written. Any change invalidates the generation.
"""

N_IN = 6
DOM = 1 << N_IN              # 64 domain rows -> full-domain verification is exact
FULL = (1 << DOM) - 1

def _input_tt(i):
    v = 0
    for r in range(DOM):
        if (r >> i) & 1:
            v |= 1 << r
    return v

INPUT_TT = tuple(_input_tt(i) for i in range(N_IN))

OP_NAMES = ("AND", "OR", "XOR", "NAND", "NOR", "XNOR", "ANDN", "ORN")
N_OPS = len(OP_NAMES)

LMIN = 1
LMAX = 32

def evaluate(prog):
    """Full-domain trace: list of wire truth tables (inputs first, then one per instruction)."""
    w = list(INPUT_TT)
    ap = w.append
    for op, a, b in prog:
        x = w[a]; y = w[b]
        if   op == 0: ap(x & y)
        elif op == 1: ap(x | y)
        elif op == 2: ap(x ^ y)
        elif op == 3: ap((~(x & y)) & FULL)
        elif op == 4: ap((~(x | y)) & FULL)
        elif op == 5: ap((~(x ^ y)) & FULL)
        elif op == 6: ap(x & (~y & FULL))
        else:         ap((x | (~y & FULL)) & FULL)
    return w

def behavior(prog, n_out=1):
    """Designated outputs = last n_out wires. Returns a tuple of truth tables."""
    w = evaluate(prog)
    return tuple(w[-n_out:])

# ---------------------------------------------------------------- construction

def random_instr(rng, n_wires):
    return (rng.randrange(N_OPS), rng.randrange(n_wires), rng.randrange(n_wires))

def random_program(rng, lo=2, hi=12):
    L = rng.randint(lo, hi)
    p = []
    for k in range(L):
        p.append(random_instr(rng, N_IN + k))
    return tuple(p)

# ------------------------------------------------------------ mutation physics
# FROZEN. Identical for every arm of every condition.

P_POINT, P_INS, P_DEL = 0.70, 0.15, 0.15

def _insert(prog, rng, pos):
    new = list(prog[:pos])
    new.append(random_instr(rng, N_IN + pos))
    shift = N_IN + pos
    for op, a, b in prog[pos:]:
        new.append((op, a + 1 if a >= shift else a, b + 1 if b >= shift else b))
    return tuple(new)

def _delete(prog, rng, pos):
    W = N_IN + pos
    repl = prog[pos][1]                      # dangling refs redirect to first operand
    new = list(prog[:pos])
    for op, a, b in prog[pos + 1:]:
        a = repl if a == W else (a - 1 if a > W else a)
        b = repl if b == W else (b - 1 if b > W else b)
        new.append((op, a, b))
    return tuple(new)

def mutate(prog, rng):
    L = len(prog)
    r = rng.random()
    if r < P_POINT or (L <= LMIN and r < P_POINT + P_DEL):
        pos = rng.randrange(L)
        op, a, b = prog[pos]
        which = rng.randrange(3)
        if which == 0:
            op = rng.randrange(N_OPS)
        elif which == 1:
            a = rng.randrange(N_IN + pos)
        else:
            b = rng.randrange(N_IN + pos)
        return prog[:pos] + ((op, a, b),) + prog[pos + 1:]
    if r < P_POINT + P_INS and L < LMAX:
        return _insert(prog, rng, rng.randrange(L + 1))
    if L > LMIN:
        return _delete(prog, rng, rng.randrange(L))
    return prog

# ------------------------------------------------------------------- composing

def splice(pa, pb):
    """Concatenate two programs into one. Returns (prog, out_wire_a, out_wire_b)."""
    la = len(pa)
    out_a = N_IN + la - 1
    tail = []
    for op, a, b in pb:
        tail.append((op, a + la if a >= N_IN else a, b + la if b >= N_IN else b))
    prog = tuple(pa) + tuple(tail)
    return prog, out_a, N_IN + len(prog) - 1

def combine(pa, pb, op):
    """(pa OP pb) as a single program whose last wire is the combination."""
    prog, wa, wb = splice(pa, pb)
    return prog + ((op, wa, wb),)
