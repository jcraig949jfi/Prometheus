#!/usr/bin/env python
"""Harmonia B Gen-3B -- INTERVENTION OPERATORS, defined separately from substrates.

WHY THIS FILE EXISTS AT ALL. The campaign's third mandate forbids comparing
"byte substrate + terrible mutator" against "continuous substrate +
sophisticated optimiser" and calling the difference substrate geometry. The
only way to honour that is to make the operator a FIRST-CLASS, CROSSABLE
factor, so that (substrate, operator) is a cell in a matrix rather than a
package deal. Hence: substrates expose coordinates and semantics; operators
decide which coordinate is touched and how far.

A mutator is a callable (substrate, genotype, rng) -> (genotype', site, meta)
or None when it declines to produce an edit on this genotype (declines are
COUNTED, never silently skipped -- a declined draw is data about the operator).

BUDGET. Every operator here performs exactly ONE elementary intervention per
call, so the intervention budget is matched by construction across the whole
matrix. Compute is matched separately, at the search stage, by counting
phenotype evaluations -- the only currency all substrates share.
"""
from __future__ import annotations

import numpy as np


class Mutator:
    name = "abstract"
    applies_to = ()          # substrate names, or () for "any"

    def __call__(self, sub, g, rng):
        raise NotImplementedError


# ------------------------------------------------------------------ generic

class UniformSite(Mutator):
    """Pick a site uniformly, then an alternative value uniformly.

    This is the CANONICAL operator of the campaign: it is defined identically
    for every discrete substrate, it touches exactly one coordinate, and it is
    ignorant of semantics. Every substrate is measured under it, which is what
    makes the substrate main effect estimable at all.
    """
    name = "M-UNIFORM"

    def __call__(self, sub, g, rng):
        sites = sub.sites(g)
        site = sites[int(rng.integers(len(sites)))]
        alts = sub.alternatives(g, site)
        if not alts:
            return None
        val = alts[int(rng.integers(len(alts)))]
        return sub.apply(g, site, val), site, {"kind": "uniform"}


class ExhaustiveSiteSweep:
    """Not a random operator: the full single-edit neighbourhood of a genotype.

    Used for the geometry assay, where the estimand is the SITE POPULATION and
    not an operator-weighted distribution. This distinction is the one external
    review #1 (Q4) forced on D-14, and it is adopted here at design time:
    where a claim is about the substrate's sites, the sweep supplies it; where
    a claim is about what an operator actually draws, the operator supplies it.
    Both are reported and they are never interchanged.
    """
    name = "SWEEP-ALL"

    @staticmethod
    def neighbourhood(sub, g, rng=None, cap_per_site=None):
        for site in sub.sites(g):
            alts = sub.alternatives(g, site)
            if alts is None:
                continue
            if cap_per_site is not None and len(alts) > cap_per_site:
                idx = rng.choice(len(alts), cap_per_site, replace=False)
                alts = [alts[i] for i in sorted(int(v) for v in idx)]
            for v in alts:
                yield site, v, sub.apply(g, site, v)


# ------------------------------------------------------------- byte-specific

class RawByte(Mutator):
    """Byte-level scramble: replace one byte with a uniform random other byte.

    The honest 'naive' operator for a byte-addressed genotype. It has no idea
    where an instruction boundary is, and it may turn an opcode into an operand
    or vice versa.
    """
    name = "M-RAWBYTE"
    applies_to = ("BYTEVM", "N2-HASH")

    def __call__(self, sub, g, rng):
        i = int(rng.integers(len(g)))
        v = int(rng.integers(256))
        if v == g[i]:
            v = (v + 1) % 256
        return sub.apply(g, i, v), i, {"kind": "rawbyte"}


class InstructionAware(Mutator):
    """SAME substrate, SAME genotype, semantics-respecting edit.

    Changes EITHER the opcode (keeping the operand field) OR the operand
    (keeping the opcode) -- never both, which is what a raw byte write does
    roughly half the time. This is the whole substrate-vs-operator experiment
    in one class: BYTEVM x M-RAWBYTE and BYTEVM x M-INSTR share every byte of
    the genotype->phenotype map and differ only in which neighbours exist.
    """
    name = "M-INSTR"
    applies_to = ("BYTEVM",)

    def __call__(self, sub, g, rng):
        i = int(rng.integers(len(g)))
        op, arg = sub.decode(g[i])
        nops = sub.NOPS
        if rng.random() < 0.5:
            new_op = int(rng.integers(nops - 1))
            if new_op >= op:
                new_op += 1
            v = new_op + nops * arg
            kind = "opcode"
        else:
            hi = (255 - op) // nops
            if hi < 1:
                return None
            new_arg = int(rng.integers(hi + 1))
            if new_arg == arg:
                new_arg = (new_arg + 1) % (hi + 1)
            v = op + nops * new_arg
            kind = "operand"
        if v > 255 or v == g[i]:
            return None
        return sub.apply(g, i, v), i, {"kind": kind}


# ---------------------------------------------------------- circuit-specific

class OpOnly(Mutator):
    """Circuit operator-family arm: only gate OPS change; topology frozen."""
    name = "M-OPONLY"
    applies_to = ("CIRCUIT",)

    def __call__(self, sub, g, rng):
        i = int(rng.integers(len(g)))
        site = ("op", i)
        alts = sub.alternatives(g, site)
        return sub.apply(g, site, alts[int(rng.integers(len(alts)))]), site, \
            {"kind": "op"}


class WireOnly(Mutator):
    """Circuit topology arm: only wires are rewired; ops frozen."""
    name = "M-WIREONLY"
    applies_to = ("CIRCUIT",)

    def __call__(self, sub, g, rng):
        i = int(rng.integers(len(g)))
        site = ("wa", i) if rng.random() < 0.5 else ("wb", i)
        alts = sub.alternatives(g, site)
        if not alts:
            return None
        return sub.apply(g, site, alts[int(rng.integers(len(alts)))]), site, \
            {"kind": "wire"}


# ------------------------------------------------------- continuous-specific

class GaussianStep(Mutator):
    """One coordinate, Gaussian step of scale sigma.

    sigma is the operator's parameter, not the substrate's. Sweeping it is how
    'how local is local' becomes an operator question instead of a substrate
    assumption -- and it is the only way a continuous arm can be given an
    intervention budget commensurable with a discrete one.
    """
    name = "M-GAUSS"
    applies_to = ("RELAX",)

    def __init__(self, sigma=0.5):
        self.sigma = sigma
        self.name = f"M-GAUSS[{sigma}]"

    def __call__(self, sub, g, rng):
        sites = sub.sites(g)
        bi, j = sites[int(rng.integers(len(sites)))]
        val = g[bi][j] + float(rng.normal(0, self.sigma))
        return sub.apply(g, (bi, j), val), (bi, j), {"kind": "gauss"}


# ---------------------------------------------------------------- registries

def canonical_mutators(sub_name):
    """Every operator admissible for a substrate, canonical one FIRST."""
    out = [UniformSite()]
    for cls in (RawByte, InstructionAware, OpOnly, WireOnly):
        if sub_name in cls.applies_to:
            out.append(cls())
    if sub_name == "RELAX":
        out = [GaussianStep(0.25), GaussianStep(1.0), GaussianStep(4.0)]
    return out
