"""SlotVM arena -- the substrate for the Gen-3 composition campaign.

Frozen by PREREGISTRATION.md sections 1-3, as amended by AMENDMENTS 1-3 (all made
BEFORE experiment E1; see PREREGISTRATION.md).  Nothing here changes after E1 runs.

Design notes that matter for the science:

  * Straight-line programs only.  No loops, no branches.  Every program is therefore a
    TOTAL deterministic function and capability is decidable by exact equality -- no
    halting problem, no timeout heuristics, no "novelty" that is really a crash.
  * Registers are shared.  Inputs are NOT write-protected and scratch is common.  This
    is what makes interference real rather than assumed: concatenating two viable
    programs genuinely clobbers state.
  * The three worlds share the SAME primitives and differ only in the rule that combines
    them.  Any between-world difference is therefore a property of the combination rule,
    not of primitive difficulty -- which is the structural variable under test.
  * Probes are numpy uint8 vectors, so one instruction is one vectorised op over all
    probes at once.  Wraparound mod 256 is the dtype's own semantics.

Self-test:  python arena.py --test
"""

from __future__ import annotations

import argparse
import hashlib

import numpy as np

# --------------------------------------------------------------------------- VM

N_REG = 8
IN_LO, IN_HI = 0, 2          # R[0..1]  inputs
SCRATCH_LO, SCRATCH_HI = 2, 5    # R[2..4]  scratch
OUT_LO = 5                   # R[5..7]  outputs (3 capability slots)
N_SLOTS = 3

L_MAX = 48                   # frozen expressed-length cap

OPS = ["ADD", "SUB", "MUL", "XOR", "AND", "OR",
       "NOT", "SHL", "SHR", "MOV", "SETC", "SWAP"]
N_OPS = len(OPS)


def run(prog, X):
    """Execute `prog` on probe matrix X (2, P) uint8.  Returns registers (8, P) uint8."""
    P = X.shape[1]
    R = np.zeros((N_REG, P), dtype=np.uint8)
    R[IN_LO:IN_HI] = X
    for op, a, b in prog:
        if op == 0:    R[a] = R[a] + R[b]
        elif op == 1:  R[a] = R[a] - R[b]
        elif op == 2:  R[a] = R[a] * R[b]
        elif op == 3:  R[a] = R[a] ^ R[b]
        elif op == 4:  R[a] = R[a] & R[b]
        elif op == 5:  R[a] = R[a] | R[b]
        elif op == 6:  R[a] = ~R[a]
        elif op == 7:  R[a] = R[a] << (b & 7)
        elif op == 8:  R[a] = R[a] >> (b & 7)
        elif op == 9:  R[a] = R[b]
        elif op == 10: R[a] = np.uint8((b * 17) & 0xFF)
        elif op == 11:
            tmp = R[a].copy()
            R[a] = R[b]
            R[b] = tmp
    return R


def prog_hash(prog):
    return hashlib.sha256(
        ",".join("%d:%d:%d" % t for t in prog).encode("ascii")).hexdigest()[:16]


def fmt(prog):
    out = []
    for op, a, b in prog:
        if op == 6:        out.append("NOT  R%d" % a)
        elif op == 10:     out.append("SETC R%-2d %d" % (a, (b * 17) & 0xFF))
        elif op in (7, 8): out.append("%-4s R%-2d %d" % (OPS[op], a, b & 7))
        else:              out.append("%-4s R%-2d R%d" % (OPS[op], a, b))
    return out


# --------------------------------------------------------------- reference functions

def _u8(v):
    return np.asarray(v, dtype=np.uint8)


def _bit(v, i):
    return _u8((v >> i) & 1)


# Primitives, shared by all three worlds.
def prim_A(x):
    return _bit(x[0], 7)


def prim_B(x):
    return _bit(x[1], 7)


def prim_C(x):
    return _bit(x[0], 3)


# W1 PIPELINE -- declared composition-FAVOURABLE positive control.
# T = A + B is CORRELATED with each primitive: holding A alone already matches T
# whenever B = 0.  So this world has a real gradient AND an obvious composition route.
# It is where composition SHOULD win, and a win here is a control reading, not evidence.
def w1_T(x):
    return _u8(_bit(x[0], 7) + _bit(x[1], 7))


# W2 DECEPTIVE -- the same primitives, combined by XOR.
# T = A XOR B is statistically INDEPENDENT of A and of B, so holding either primitive
# scores exactly chance on the target.  There is no gradient into the optimum at all.
# The routes are a lucky structural jump, or crossing the valley by composing two
# already-viable behaviors.  This is where the composition hypothesis makes a real,
# non-trivial, falsifiable claim, and it is the load-bearing world of the campaign.
def w2_T(x):
    return _u8(_bit(x[0], 7) ^ _bit(x[1], 7))


# W3 INTERFERENCE -- three primitives; success is holding ALL THREE AT ONCE over shared
# scratch and adjacent output registers.  Concatenating two viable programs clobbers
# state, so composition is predicted to lose to compose-then-refine, and may lose to
# plain local mutation.  Composition is allowed to lose here.

WORLDS = {
    "W1_PIPELINE":     dict(refs=[prim_A, prim_B, w1_T], goal=(2,), boot=(0, 1),
                            note="T = A + B; graded credit + composition route (positive control)"),
    "W2_DECEPTIVE":    dict(refs=[prim_A, prim_B, w2_T], goal=(2,), boot=(0, 1),
                            note="T = A XOR B; ZERO gradient; valley-crossing test"),
    "W3_INTERFERENCE": dict(refs=[prim_A, prim_B, prim_C], goal=(0, 1, 2), boot=(0, 1),
                            note="hold ALL THREE slots simultaneously; shared scratch"),
}


# --------------------------------------------------------------------- probe streams

def make_probes(seed, n, kind="uniform"):
    """Probe matrix (2, n) uint8.  `kind` selects the input DISTRIBUTION."""
    rng = np.random.default_rng(seed)
    if kind == "uniform":
        return rng.integers(0, 256, size=(2, n), dtype=np.uint8)
    if kind == "structured":
        specials = [0, 1, 2, 15, 16, 127, 128, 129, 254, 255]
        cols = []
        for i in range(n):
            if i % 3 == 0:
                cols.append([int(rng.choice(specials)) for _ in range(2)])
            elif i % 3 == 1:
                v = int(rng.choice(specials))
                cols.append([v, v])
            else:
                cols.append([int(v) for v in rng.integers(0, 16, size=2)])
        return np.asarray(cols, dtype=np.uint8).T
    raise ValueError(kind)


# Frozen probe seeds.  DISJOINT streams -- HELDOUT is never visible to any arm.
SEED_TRAIN, SEED_HELDOUT, SEED_PERTURB = 11_000_001, 22_000_002, 33_000_003
N_TRAIN, N_HELDOUT, N_PERTURB = 16, 64, 64

# TRANSFER: the candidate is given inputs with the two registers swapped, while the
# reference is evaluated on the original inputs.  A candidate that hard-wired an input
# position fails; transfer failure is recorded but is NOT a promotion blocker.
TRANSFER_PERM = [1, 0]


class World:
    def __init__(self, name):
        spec = WORLDS[name]
        self.name = name
        self.refs = spec["refs"]
        self.note = spec["note"]
        self.goal = frozenset(spec["goal"])
        self.boot_slots = tuple(spec["boot"])
        self.n_slots = len(self.refs)
        self.train = make_probes(SEED_TRAIN, N_TRAIN)
        self.heldout = make_probes(SEED_HELDOUT, N_HELDOUT)
        self.perturb = make_probes(SEED_PERTURB, N_PERTURB, kind="structured")
        self._T_train = self.targets(self.train)

    def targets(self, X):
        return np.stack([f(X) for f in self.refs])

    def capset(self, prog, which="heldout"):
        """The FROZEN capability test: exact match on every probe of the named stream."""
        X = getattr(self, which)
        T = self.targets(X)
        R = run(prog, X)
        return frozenset(k for k in range(self.n_slots)
                         if np.array_equal(R[OUT_LO + k], T[k]))

    def capset_transfer(self, prog):
        X = self.heldout
        T = self.targets(X)
        R = run(prog, X[TRANSFER_PERM])
        return frozenset(k for k in range(self.n_slots)
                         if np.array_equal(R[OUT_LO + k], T[k]))

    def eval_train(self, prog, slots=None):
        """One pass: (exact, frac, train capability set).  The engine's hot path.

        `slots` restricts scoring to a subset.  The shared bootstrap phase passes the
        PRIMITIVE slots only, so the target capability is held out from the search
        machinery that builds the archive every arm inherits (assignment section 5).

        `frac` is the PER-PROBE exact-match fraction averaged over slots (prereg
        AMENDMENT 2: partial credit must live over probes, not over bits).  Its chance
        level is each reference's majority-class rate and is MEASURED in E1, not assumed.
        The promotion criterion is untouched: exact match on all 64 HELDOUT probes.
        """
        T = self._T_train
        R = run(prog, self.train)
        exact = 0
        frac = 0.0
        held = []
        ks = range(self.n_slots) if slots is None else slots
        n_k = self.n_slots if slots is None else len(ks)
        for k in ks:
            eq = (R[OUT_LO + k] == T[k])
            if eq.all():
                exact += 1
                held.append(k)
            frac += float(eq.mean())
        return exact, frac / n_k, frozenset(held)

    def fitness(self, prog):
        return self.eval_train(prog)[:2]

    def signature(self, prog):
        """Behavioral signature: canonicalises duplicates so behaviorally equivalent
        programs are not counted as distinct discoveries (competing explanation X7)."""
        R = run(prog, self.heldout)
        return hashlib.sha256(R[OUT_LO:].tobytes()).hexdigest()[:16]


# --------------------------------------------------------------------------- tests

def _test():
    ok = True
    X = make_probes(999, 64)

    hand = {
        "prim_A": ([(9, 5, 0), (8, 5, 7)], prim_A),
        "prim_B": ([(9, 5, 1), (8, 5, 7)], prim_B),
        "prim_C": ([(10, 2, 15), (8, 2, 7), (9, 5, 0), (8, 5, 3), (4, 5, 2)], prim_C),
        "w1_T":   ([(9, 2, 0), (8, 2, 7), (9, 3, 1), (8, 3, 7),
                    (9, 5, 2), (0, 5, 3)], w1_T),
        "w2_T":   ([(9, 2, 0), (8, 2, 7), (9, 3, 1), (8, 3, 7),
                    (9, 5, 2), (3, 5, 3)], w2_T),
    }
    for name, (prog, ref) in hand.items():
        good = np.array_equal(run(prog, X)[OUT_LO], ref(X))
        ok &= good
        print("  [%s] hand-written program reproduces %s (%d instr)"
              % ("PASS" if good else "FAIL", name, len(prog)))

    for wn, spec in WORLDS.items():
        for i, f in enumerate(spec["refs"]):
            v = f(X)
            good = len(np.unique(v)) > 1
            ok &= good
            print("  [%s] %s slot %d non-constant, majority-class rate %.3f"
                  % ("PASS" if good else "FAIL", wn, i,
                     max(np.bincount(v).tolist()) / len(v)))

    w = World("W1_PIPELINE")
    tr = set(map(tuple, w.train.T.tolist()))
    ho = set(map(tuple, w.heldout.T.tolist()))
    good = len(tr & ho) == 0
    ok &= good
    print("  [%s] TRAIN and HELDOUT disjoint (overlap %d)" % ("PASS" if good else "FAIL", len(tr & ho)))

    p = [(0, 5, 0), (3, 5, 1)]
    good = np.array_equal(run(p, X), run(p, X))
    ok &= good
    print("  [%s] execution is deterministic" % ("PASS" if good else "FAIL"))

    good = len(w.capset([])) == 0
    ok &= good
    print("  [%s] empty program holds no capability" % ("PASS" if good else "FAIL"))

    # a constant program must not hold any capability on HELDOUT (leakage control K2)
    for c in range(0, 16):
        const = [(10, 5, c), (10, 6, c), (10, 7, c)]
        if len(w.capset(const)) > 0:
            ok = False
    print("  [%s] no constant program holds a capability (K2 leakage control)"
          % ("PASS" if ok else "FAIL"))

    print("\n  %s" % ("ALL PASS" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    if ap.parse_args().test:
        raise SystemExit(_test())
    for n in WORLDS:
        w = World(n)
        print("%-18s slots=%d goal=%s  %s" % (n, w.n_slots, sorted(w.goal), w.note))
