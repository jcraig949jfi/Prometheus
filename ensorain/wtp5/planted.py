"""Constructed (planted) TAPE solutions, one per world variant (PREREG_WTP05 s4).

Used ONLY for expressibility validation, solvability, minimum-mechanism size estimates, instrument calibration
and the reachability diagnostics (plant / break-one-edit / repair). Never supplied to the experimental search:
search.py does not import this module (a test asserts it)."""
import numpy as np

from .tape import node, genome, W
from .worlds import P0, P1, P2, F1, F2, FG

N = node


def _c(x):
    return np.full(W, float(x))


def _lin_row(vec):
    M = np.zeros((W, W))
    M[0, 0], M[0, 1] = vec
    return M


def _event_gates(nodes):
    """Append the standard flag decoders. Returns dict of node indices (OBS = 0). A gate value >= 0 means 'on'."""
    i = len(nodes)
    nodes += [N("CH", 0, i=F1), N("CONST", v=_c(-0.5)), N("ADD", i, i + 1),          # i+2 evt (>= 0 at events)
              N("CH", 0, i=F2), N("CONST", v=_c(-1.0)), N("MUL", i + 3, i + 4),       # i+3 tag, i+4 -1, i+5 -tag
              N("ADD", i + 3, i + 1), N("ADD", i + 5, i + 1),                         # i+6 tag-.5, i+7 -tag-.5
              N("SEL", i + 2, i + 6, i + 4), N("SEL", i + 2, i + 7, i + 4),           # i+8 gP, i+9 gN
              N("MUL", i + 3, i + 3), N("MUL", i + 10, i + 4),                        # i+11 -(tag^2)
              N("SEL", i + 2, i + 11, i + 4)]                                         # i+12 g0 (event & tag = 0)
    return dict(evt=i + 2, tag=i + 3, m1=i + 4, ntag=i + 5, gP=i + 8, gN=i + 9, g0=i + 12, half=i + 1)


def latch_A(rung):
    n = [N("OBS"), N("READ", s=0), N("READ", s=1)]
    e = _event_gates(n)
    p0 = len(n)
    n += [N("CH", 0, i=P0)]
    newA = len(n)
    n += [N("SEL", e["gP"], p0, 1), N("WRITE", newA, s=0)]
    if rung in ("R0", "R2"):
        if rung == "R0":
            n += [N("ACT", newA)]
        else:
            n += [N("CH", 0, i=P2)]
            n += [N("MUL", newA, len(n) - 1), N("ACT", len(n))]
        return genome(n, S=1)
    newB = len(n)
    n += [N("SEL", e["gN"], p0, 2), N("WRITE", newB, s=1)]
    if rung == "R1":
        n += [N("SEL", e["tag"], newA, newB)]
        n += [N("ACT", len(n) - 1)]
    else:
        n += [N("MUL", newA, newB), N("CH", 0, i=P2)]
        n += [N("MUL", len(n) - 2, len(n) - 1)]
        n += [N("ACT", len(n) - 1)]
    return genome(n, S=2)


def parity_N(rung):
    n = [N("OBS"), N("READ", s=0), N("READ", s=1), N("READ", s=2)]
    e = _event_gates(n)
    one = len(n)
    n += [N("CONST", v=_c(1.0)), N("CH", 0, i=P0)]
    p0 = one + 1

    def acc(slot_node, gate, s):
        i = len(n)
        n.extend([N("MUL", slot_node, slot_node), N("ADD", i, e["half"]), N("SEL", i + 1, slot_node, one),   # eff
                  N("MUL", i + 2, p0), N("SEL", gate, i + 3, i + 2), N("WRITE", i + 4, s=s)])
        return i + 4
    h0 = acc(1, e["gP"], 0)
    if rung == "R2":
        n += [N("ACT", h0)]
        return genome(n, S=1)
    h1 = acc(2, e["gN"], 1)
    p1 = len(n)
    n += [N("CH", 0, i=P1)]
    m = len(n)
    n += [N("SEL", e["g0"], p1, 3), N("WRITE", m, s=2)]
    n += [N("SEL", m, h0, h1)]
    n += [N("ACT", len(n) - 1)]
    return genome(n, S=3)


def lock_B(rung, world, stepping=False):
    n = [N("OBS"), N("READ", s=0), N("READ", s=1), N("READ", s=2)]
    e = _event_gates(n)

    def store(vec, gate, slot, read):
        i = len(n)
        n.extend([N("LIN", 0, M=_lin_row(vec)), N("SIGN", i), N("SEL", gate, i + 1, read), N("WRITE", i + 2, s=slot)])
        return i + 2
    a = store(world.u, e["gP"], 0, 1)
    b = store(world.v, e["gN"], 1, 2)
    i = len(n)
    n += [N("MUL", a, b)]
    out = i
    if rung == "R3":
        c = store(world.w, e["g0"], 2, 3)
        n += [N("MUL", out, c)]
        out = len(n) - 1
    if stepping:      # gate tag +1 -> sign(u.a) (slot 0); tag -1 -> sign(v.b) (slot 1); tag 0 -> composition
        j = len(n)
        n += [N("SEL", e["ntag"] + 2, 2, out), N("SEL", e["ntag"] + 1, 1, j)]
        out = j + 1
    n += [N("ACT", out)]
    return genome(n, S=3 if rung == "R3" else 2)


def switch_C(eta=1.0, sigma=0.5):
    """act = theta * s for type-1 (tag +1, payload P0), q for type-2 (tag -1, payload P1); theta plastic."""
    n = [N("OBS"), N("CH", 0, i=P0), N("CH", 0, i=P1), N("CH", 0, i=F2), N("CONST", v=_c(0.2), plastic=True)]
    n += [N("MUL", 1, 4), N("SEL", 3, 5, 2), N("ACT", 6)]
    return genome(n, S=1, eta=eta, sigma=sigma)


def planted(world):
    f, r, c = world.family, world.rung, world.cond
    if f == "A":
        return latch_A(r)
    if f == "N":
        return parity_N(r)
    if f == "B":
        return lock_B(r, world, stepping=(c == "stepping"))
    if f == "C":
        return switch_C()
    raise KeyError(f)
