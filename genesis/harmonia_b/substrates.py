#!/usr/bin/env python
"""Harmonia B Gen-3B campaign -- the comparative substrate arena.

EVERY substrate in this file maps a genotype to the SAME phenotype space:
a Boolean function on {0,1}^N, N=10, held as a 1024-entry bool truth table.
That is deliberate and it is the design's load-bearing choice: the consequence
ruler d(f,g) = Hamming(f,g)/1024 is then EXACTLY comparable across substrates,
so a cross-substrate comparison is a comparison of genotype->phenotype maps and
NOT a comparison of two different behaviour spaces wearing one name.

RULER PROVENANCE. `minmass`, `d_of`, `jaccard`, `surv_sym`, `r_vec2`, the
circuit evaluator, `circuit_edit_space` and `apply_edit` are VERBATIM PORTS of
Harmonia A's frozen Gen-3 machinery, copied rather than imported so that A's
live D-14 tree is never a dependency of mine and my results cannot drift if A
amends. Source and hash recorded here and in the charter:
  genesis/harmonia_a/gen3/common.py
  sha256 87a59d2aa964b3da71915d52f571850d972287d6b67ceff2cc96adc2c7516628
Constants carried verbatim: N=10, G=24, EPS_TRIV=0.025, LOCAL_BAND=0.25.
Reusing A's exact ruler is what makes my CIRCUIT arm a calibration anchor: it
must reproduce A's published marginals (83.6% neutral / 11.9% band / 4.5% far)
or my harness is wrong, and that check is E1's first clause.

NOT STACKVM. `ByteVM` is a byte-addressed stack machine written here, locally,
as an ANALOG of the byte-level genotype->behaviour map. It is NOT the Foundry's
stackvm-v1, it is not measured against it, and no result here is a StackVM
result. StackVM lives on the M1 instrument and is Harmonia A's D-14 lane, live
at the time of writing; this campaign does not read, drive, or tune against it.
"""
from __future__ import annotations

import hashlib

import numpy as np

# ---------------------------------------------------------------- constants
N = 10
DOM = 1 << N              # 1024
G = 24                    # gates in a native circuit
EPS_TRIV = 0.025          # A's DESTRUCTION threshold on minmass
LOCAL_BAND = 0.25         # A's SMALL/LARGE cut on d

INPUT_COLS = ((np.arange(DOM)[:, None] >> np.arange(N)) & 1).astype(bool)


def rng_for(*key):
    return np.random.default_rng(np.random.SeedSequence(list(key)))


# ---------------------------------------------------------------- the ruler
# (verbatim port; see module docstring for source + hash)

def minmass(f):
    m = float(f.mean())
    return min(m, 1.0 - m)


def d_of(f, g):
    return float(np.count_nonzero(f != g)) / DOM


def jaccard(a, b):
    u = np.count_nonzero(a | b)
    return float(np.count_nonzero(a & b)) / u if u else 1.0


def surv_sym(f, g):
    return min(jaccard(f, g), jaccard(~f, ~g))


def r_vec2(f, g):
    """A's frozen 4-class consequence ruler. NEUTRAL/DESTRUCTION/SMALL/LARGE."""
    if np.array_equal(f, g):
        return "NEUTRAL"
    if minmass(g) <= EPS_TRIV:
        return "DESTRUCTION"
    d = d_of(f, g)
    return "SMALL" if (d <= LOCAL_BAND and surv_sym(f, g) >= 0.5) else "LARGE"


# ================================================================ substrates
#
# A Substrate supplies, deterministically:
#   sample(seed)            -> genotype
#   phenotype(genotype)     -> bool[DOM]           (exact, by full enumeration)
#   sites(genotype)         -> list of site ids    (intervention coordinates)
#   edits(genotype, site)   -> list of alternative values at that site
#   apply(genotype, site, value) -> genotype'
# Mutators are defined SEPARATELY (mutators.py-style, below) so that
# substrate and intervention operator can be crossed factorially. That
# separation is mandatory for this campaign and is why they are not methods.


class Substrate:
    name = "abstract"
    smooth_by_design = None      # declared, not measured -- see charter S5
    navigable_by_design = None   # declared, not measured

    def sample(self, seed):
        raise NotImplementedError

    def phenotype(self, g):
        raise NotImplementedError

    def sites(self, g):
        raise NotImplementedError

    def alternatives(self, g, site):
        raise NotImplementedError

    def apply(self, g, site, value):
        raise NotImplementedError


# ---------------------------------------------------------------- S1 CIRCUIT

def gate_eval(op, a, b):
    if op == 0:
        return a & b
    if op == 1:
        return a | b
    if op == 2:
        return a ^ b
    return ~(a & b)


def eval_wires(gates):
    wires = [INPUT_COLS[:, i] for i in range(N)]
    for op, a, b in gates:
        wires.append(gate_eval(op, wires[a], wires[b]))
    return wires


class Circuit(Substrate):
    """A's native representation: G straight-line gates over {AND,OR,XOR,NAND}.

    Genotype = tuple of (op, a, b). Output = last wire. Verbatim from A's
    bench1/common, including the balance screen used to build Gen-1 objects.
    """
    name = "CIRCUIT"
    smooth_by_design = False
    navigable_by_design = None       # empirical -- this is the object of study

    def __init__(self, n_gates=G, balance_screen=True):
        self.n_gates = n_gates
        self.balance_screen = balance_screen

    def _draw(self, rng):
        gates = []
        for gi in range(self.n_gates):
            nw = N + gi
            gates.append((int(rng.integers(4)),
                          int(rng.integers(nw)), int(rng.integers(nw))))
        return tuple(gates)

    def sample(self, seed):
        rng = rng_for(seed, 0xC1)
        for _ in range(50):                      # A's resample cap
            g = self._draw(rng)
            if not self.balance_screen:
                return g
            if minmass(self.phenotype(g)) > EPS_TRIV:
                return g
        return g

    def phenotype(self, g):
        return eval_wires(g)[-1]

    def sites(self, g):
        # a site is a gate slot: ("op",i) / ("wa",i) / ("wb",i)
        out = []
        for i in range(len(g)):
            out.append(("op", i))
            out.append(("wa", i))
            out.append(("wb", i))
        return out

    def alternatives(self, g, site):
        kind, i = site
        op, a, b = g[i]
        nw = N + i
        if kind == "op":
            return [v for v in range(4) if v != op]
        cur = a if kind == "wa" else b
        return [w for w in range(nw) if w != cur]

    def apply(self, g, site, value):
        kind, i = site
        op, a, b = g[i]
        out = list(g)
        if kind == "op":
            out[i] = (value, a, b)
        elif kind == "wa":
            out[i] = (op, value, b)
        else:
            out[i] = (op, a, value)
        return tuple(out)


# ---------------------------------------------------------------- S2 BYTEVM

class ByteVM(Substrate):
    """A byte-addressed stack machine. AN ANALOG OF a byte-level genotype map.

    NOT the Foundry's stackvm-v1 (see module docstring). Written here so that a
    byte-level map can enter the factorial at zero instrument cost.

    Decode: byte -> (opcode = byte % NOPS, operand = byte // NOPS).
    Stack holds bool[DOM] vectors; execution is vectorised over the whole
    domain at once, so the truth table is EXACT by full enumeration, never
    sampled. Underflow is defined (not a fault): a missing operand reads as the
    all-false vector, so every program has a total semantics and 'destruction'
    is a behavioural class, never an execution exception. That choice is
    DECLARED: it removes the fault channel from this substrate on purpose, so
    that fault rate cannot masquerade as consequence geometry.
    """
    name = "BYTEVM"
    smooth_by_design = False
    navigable_by_design = None

    OPS = ("PUSHX", "AND", "OR", "XOR", "NOT", "NAND", "DUP", "SWAP",
           "DROP", "PUSH0")
    NOPS = len(OPS)

    def __init__(self, length=48):
        self.length = length

    def sample(self, seed):
        rng = rng_for(seed, 0xB2)
        for _ in range(50):
            g = tuple(int(v) for v in rng.integers(0, 256, self.length))
            if minmass(self.phenotype(g)) > EPS_TRIV:
                return g
        return g

    def decode(self, byte):
        return byte % self.NOPS, byte // self.NOPS

    def phenotype(self, g):
        false = np.zeros(DOM, dtype=bool)
        st = []

        def pop():
            return st.pop() if st else false

        for byte in g:
            op, arg = self.decode(byte)
            name = self.OPS[op]
            if name == "PUSHX":
                st.append(INPUT_COLS[:, arg % N])
            elif name == "PUSH0":
                st.append(false)
            elif name == "NOT":
                st.append(~pop())
            elif name == "DUP":
                v = pop()
                st.append(v)
                st.append(v)
            elif name == "DROP":
                pop()
            elif name == "SWAP":
                a, b = pop(), pop()
                st.append(a)
                st.append(b)
            else:
                a, b = pop(), pop()
                if name == "AND":
                    st.append(b & a)
                elif name == "OR":
                    st.append(b | a)
                elif name == "XOR":
                    st.append(b ^ a)
                else:
                    st.append(~(b & a))
            if len(st) > 64:
                del st[:-64]
        return (st[-1] if st else false)

    def sites(self, g):
        return list(range(len(g)))

    def alternatives(self, g, site):
        # RAW byte alternatives: every other byte value. The instruction-aware
        # restriction is a MUTATOR, not a substrate property -- see mutators.
        return [v for v in range(256) if v != g[site]]

    def apply(self, g, site, value):
        out = list(g)
        out[site] = value
        return tuple(out)


# ---------------------------------------------------------------- S4 DNF

class DNF(Substrate):
    """Grammar-constrained: k-term DNF over N variables.

    Genotype = k x N matrix with entries in {0:absent, 1:positive, 2:negative}.
    Phenotype = OR over terms of AND over present literals. An empty term is
    the constant TRUE (declared). Every genotype is well-formed by
    construction -- there is no invalid-program class at all, which is exactly
    what makes this the typed/grammar arm.
    """
    name = "DNF"
    smooth_by_design = False
    navigable_by_design = None

    def __init__(self, k=6):
        self.k = k

    def sample(self, seed):
        rng = rng_for(seed, 0xD4)
        for _ in range(50):
            g = tuple(tuple(int(v) for v in row)
                      for row in rng.integers(0, 3, (self.k, N)))
            if minmass(self.phenotype(g)) > EPS_TRIV:
                return g
        return g

    def phenotype(self, g):
        out = np.zeros(DOM, dtype=bool)
        for term in g:
            acc = np.ones(DOM, dtype=bool)
            for j, s in enumerate(term):
                if s == 1:
                    acc &= INPUT_COLS[:, j]
                elif s == 2:
                    acc &= ~INPUT_COLS[:, j]
            out |= acc
        return out

    def sites(self, g):
        return [(t, j) for t in range(self.k) for j in range(N)]

    def alternatives(self, g, site):
        t, j = site
        return [v for v in range(3) if v != g[t][j]]

    def apply(self, g, site, value):
        t, j = site
        rows = [list(r) for r in g]
        rows[t][j] = value
        return tuple(tuple(r) for r in rows)


# ---------------------------------------------------------------- S5 RELAXED

class RelaxedCircuit(Substrate):
    """Continuous genotype over the SAME phenotype space, temperature tau.

    Genotype = float vector: per gate, 4 op-logits and two wire-logit vectors.
    Soft evaluation in [0,1]: AND=ab, OR=a+b-ab, XOR=a+b-2ab, NAND=1-ab, mixed
    by softmax(op_logits/tau); each operand is a softmax(wire_logits/tau)
    weighted average of the available wires. The phenotype is the THRESHOLD of
    the soft output at 0.5 -- so the behaviour space is still exactly Boolean
    and d is still exactly comparable.

    tau -> 0 recovers the discrete circuit (argmax); larger tau blends. This is
    the arm that tests reviewer Q13's frozen-prediction-shaped claim that
    relaxation changes the consequence spectrum, and it is the arm where
    'smooth' can be varied continuously rather than asserted.
    """
    name = "RELAX"
    smooth_by_design = True
    navigable_by_design = None

    def __init__(self, n_gates=12, tau=0.5, scale=1.0):
        self.n_gates = n_gates
        self.tau = tau
        self.scale = scale

    def _shape(self):
        # per gate gi: 4 op logits + (N+gi) wire logits for a + same for b
        return [(4, N + gi, N + gi) for gi in range(self.n_gates)]

    def sample(self, seed):
        rng = rng_for(seed, 0x5E)
        vec = []
        for (no, na, nb) in self._shape():
            vec.append(rng.normal(0, self.scale, no))
            vec.append(rng.normal(0, self.scale, na))
            vec.append(rng.normal(0, self.scale, nb))
        return tuple(tuple(float(x) for x in blk) for blk in vec)

    @staticmethod
    def _soft(logits, tau):
        z = np.asarray(logits, float) / max(tau, 1e-9)
        z = z - z.max()
        e = np.exp(z)
        return e / e.sum()

    def phenotype(self, g):
        wires = [INPUT_COLS[:, i].astype(float) for i in range(N)]
        for gi in range(self.n_gates):
            ow, aw, bw = g[3 * gi], g[3 * gi + 1], g[3 * gi + 2]
            pa = self._soft(aw, self.tau)
            pb = self._soft(bw, self.tau)
            W = np.stack(wires, axis=1)                 # DOM x nwires
            a = W @ pa
            b = W @ pb
            po = self._soft(ow, self.tau)
            val = (po[0] * (a * b)
                   + po[1] * (a + b - a * b)
                   + po[2] * (a + b - 2 * a * b)
                   + po[3] * (1.0 - a * b))
            wires.append(val)
        return wires[-1] > 0.5

    def sites(self, g):
        return [(bi, j) for bi in range(len(g)) for j in range(len(g[bi]))]

    def alternatives(self, g, site):
        # continuous: alternatives are supplied by the MUTATOR's step, not
        # enumerable here. Returning None is the substrate saying so.
        return None

    def apply(self, g, site, value):
        bi, j = site
        blocks = [list(b) for b in g]
        blocks[bi][j] = value
        return tuple(tuple(b) for b in blocks)


# ================================================== designed control substrates
# The three below are DECLARED constructions, not discoveries. They exist to
# qualify the assay (section 5 of the charter). Their smoothness and
# navigability are properties of their definitions, so they carry NO empirical
# content about real substrates -- exactly as A declared the FAULT class
# definitional in Gen-3G. Their only job is to make the assay falsifiable:
# an assay that cannot separate P1 from N2 is not qualified to rank anything.


class BlocksPositive(Substrate):
    """P1: smooth AND navigable, by construction. The 'millimetre' the ruler
    must be able to see (external review Q16).

    Genotype = L bits. The domain is partitioned into L equal blocks; bit i
    XORs block i of a fixed target function. So d(f, target) = popcount(b)/L
    exactly, every single-bit edit moves d by exactly 1/L, and hill-climbing
    reaches the target in at most L steps with a strictly monotone path. The
    consequence spectrum is a single spike at 1/L.
    """
    name = "P1-BLOCKS"
    smooth_by_design = True
    navigable_by_design = True

    def __init__(self, L=16, target_seed=7):
        self.L = L
        self.blocks = np.array_split(np.arange(DOM), L)
        self.target = rng_for(target_seed, 0xB1).integers(0, 2, DOM).astype(bool)

    def sample(self, seed):
        rng = rng_for(seed, 0xB1A)
        return tuple(int(v) for v in rng.integers(0, 2, self.L))

    def phenotype(self, g):
        f = self.target.copy()
        for i, bit in enumerate(g):
            if bit:
                f[self.blocks[i]] = ~f[self.blocks[i]]
        return f

    def sites(self, g):
        return list(range(self.L))

    def alternatives(self, g, site):
        return [1 - g[site]]

    def apply(self, g, site, value):
        out = list(g)
        out[site] = value
        return tuple(out)


class SmoothUnreachable(Substrate):
    """N1: smooth and NON-navigable. Graded consequences, provably zero progress.

    BOOTSTRAP CORRECTION (recorded rather than quietly fixed). The first version
    restricted the free region to half the domain, which made N1's consequence
    spectrum a spike at 1/32 while P1's sat at 1/16 -- so the two controls
    differed in BOTH geometry and navigability, and any separation between them
    would have been uninterpretable. The whole point of this control is that it
    is geometrically INDISTINGUISHABLE from P1 and behaviourally opposite.

    Repaired construction. Same L blocks over the same full domain as P1, so
    every single-bit edit changes exactly DOM/L outputs and the spectrum is the
    identical spike at 1/L. What differs is the TARGET's relationship to the
    reachable set: the target is built to disagree with the anchor on exactly
    HALF of every block. Flipping any block therefore exchanges the agreeing
    and disagreeing halves of that block and leaves d(f, target) EXACTLY
    unchanged. Every reachable phenotype is equidistant from the target:
    d(f, target) = 0.5 for all 2^L of them, provably, with no search able to
    move it by any amount at any budget.

    So: identical local consequence geometry to the positive control, and a
    flat, information-free target landscape. Any navigability statistic that
    ranks these two the same is measuring smoothness, not navigability -- which
    is precisely the distinction section 5 of the charter must not collapse.
    """
    name = "N1-SMOOTH-UNREACHABLE"
    smooth_by_design = True
    navigable_by_design = False

    def __init__(self, L=16, anchor_seed=13):
        self.L = L
        self.blocks = np.array_split(np.arange(DOM), L)
        rng = rng_for(anchor_seed, 0x11)
        self.anchor = rng.integers(0, 2, DOM).astype(bool)
        # target: disagrees with the anchor on exactly half of every block
        t = self.anchor.copy()
        for blk in self.blocks:
            half = rng.permutation(blk)[: len(blk) // 2]
            t[half] = ~t[half]
        self.own_target = t

    def sample(self, seed):
        rng = rng_for(seed, 0x1AA)
        return tuple(int(v) for v in rng.integers(0, 2, self.L))

    def phenotype(self, g):
        f = self.anchor.copy()
        for i, bit in enumerate(g):
            if bit:
                f[self.blocks[i]] = ~f[self.blocks[i]]
        return f

    def sites(self, g):
        return list(range(self.L))

    def alternatives(self, g, site):
        return [1 - g[site]]

    def apply(self, g, site, value):
        out = list(g)
        out[site] = value
        return tuple(out)


class HashSubstrate(Substrate):
    """N2: discontinuous AND non-navigable. The pathological floor.

    Every genotype maps to an INDEPENDENT pseudorandom truth table via sha256.
    No locality of any kind: the consequence of every edit is a fresh draw, so
    d concentrates at 0.5 and nothing is ever neutral or small. If an assay
    cannot tell this apart from a real substrate it is measuring nothing.
    """
    name = "N2-HASH"
    smooth_by_design = False
    navigable_by_design = False

    def __init__(self, length=32):
        self.length = length

    def sample(self, seed):
        rng = rng_for(seed, 0x2AA)
        return tuple(int(v) for v in rng.integers(0, 256, self.length))

    def phenotype(self, g):
        # counter-mode expansion: DOM independent bits, not a repeated digest.
        seed = bytes(g)
        raw = b"".join(hashlib.sha256(seed + i.to_bytes(2, "big")).digest()
                       for i in range((DOM + 255) // 256))
        bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8))[:DOM]
        return bits.astype(bool)

    def sites(self, g):
        return list(range(self.length))

    def alternatives(self, g, site):
        return [v for v in range(256) if v != g[site]]

    def apply(self, g, site, value):
        out = list(g)
        out[site] = value
        return tuple(out)
