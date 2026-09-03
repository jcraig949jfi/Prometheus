"""Null control processes. Published BEFORE the V0.3 grammar is run (brief section 3).

Purpose: separate a MUTATION PRIOR from the GEOMETRY OF THE SPACE BEING MUTATED. Each control is
deliberately simple and its expected behaviour is either analytic or independently simulatable.
None of them encodes a desired Proteus outcome; three of the four have a stationary distribution
that is known in closed form, and the fourth is a pure geometry reference with no mutation at all.

NC1  SYMMETRIZED REFLECTED WALK. No content, no VM, no phenotype. An integer walk on genome
     length in [1, cap] driven by the SYMMETRIZED version of the V0.3 grammar's own length
     kernel: the kernel is measured on random genomes, then replaced by
     p_sym(d) = (p(d) + p(-d)) / 2. A symmetric kernel has zero drift in an unbounded space by
     construction, and out-of-range steps are no-ops exactly as the grammar's bounds behave.
     EVERY unit of drift NC1 shows is therefore attributable to the reflecting bounds and the
     finite support and to nothing else. This is the GEOMETRY term. The same construction is
     applied to each numeric configuration coordinate.

NC2  WHOLE-GENOME UNIFORM RESAMPLER. Every mutation replaces the entire genome with fresh uniform
     32-bit words of the SAME length. Length is frozen; content is redrawn. The stationary
     content distribution is uniform over words BY CONSTRUCTION, so the analytic expectation for
     every opcode-frequency coordinate is the exact multinomial induced by op = word mod 25:
     opcodes 0..20 have probability 171798692 / 2^32, opcodes 21..24 have 171798691 / 2^32
     (2^32 = 25 * 171798691 + 21). Any measured opcode drift under NC2 is sampling variance.

NC3  SINGLE-SITE UNIFORM RESAMPLER. Every mutation overwrites exactly one uniformly chosen
     instruction with four uniform words. This is the V0.3 operator `replacement` at weight 1.0.
     Length frozen; the content chain is an independent-site Markov chain whose stationary
     distribution is again uniform over words. Distinguishes "the grammar's site-selection and
     length machinery" from "resampling content at all".

NC4  GEOMETRY REFERENCE (no mutation). For a given length distribution, draw fresh uniform
     genomes of those lengths and measure the same phenotype coordinates. This is what the
     phenotype coordinates look like when content is EXACTLY uniform at that length. Any
     phenotype movement in the V0.3 crucible that is matched by NC4 at the same length
     distribution is attributable to the length distribution and the phenotype geometry, not to
     the mutation kernel.

All four are run with the same lineage counts, horizons, checkpoints and measurement code as the
V0.3 crucible.
"""
from __future__ import annotations

from proteus.foundry.grammar import GMAX, GMIN
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import SCHEMA

IW = 4
NAMES = ("NC1_reflected_length_walk", "NC2_whole_genome_uniform", "NC3_single_site_uniform",
         "NC4_geometry_reference")

# Exact analytic opcode probabilities for uniform 32-bit words under op = word mod 25.
_TWO32 = 1 << 32
_Q, _R = divmod(_TWO32, 25)
ANALYTIC_OPCODE_P = tuple(((_Q + 1) if i < _R else _Q) / _TWO32 for i in range(25))
assert abs(sum(ANALYTIC_OPCODE_P) - 1.0) < 1e-15


def fresh_manifest(rng: SplitMix64, n_instr: int, tape_words: int, n_regs: int,
                   persist: str, code_writable: bool, tick_budget: int, out_cap: int) -> dict:
    return {"schema_version": SCHEMA, "n_regs": n_regs, "tape_words": tape_words,
            "genome": [rng.next_u32() for _ in range(IW * n_instr)],
            "code_writable": code_writable, "persist": persist,
            "tick_budget": tick_budget, "out_cap": out_cap}


def nc1_step(length: int, rng: SplitMix64, kernel: list, cap: int) -> int:
    """One step of the reflected length walk. `kernel` is a list of (delta, weight)."""
    deltas = [d for d, _w in kernel]
    weights = [w for _d, w in kernel]
    d = rng.weighted(deltas, weights)
    nxt = length + d
    if nxt < GMIN or nxt > cap:
        return length          # reflection by no-op, exactly as the grammar's bounds behave
    return nxt


def nc2_mutate(m: dict, rng: SplitMix64) -> dict:
    c = dict(m)
    c["genome"] = [rng.next_u32() for _ in range(len(m["genome"]))]
    return c


def nc3_mutate(m: dict, rng: SplitMix64) -> dict:
    c = dict(m)
    g = list(m["genome"])
    pos = rng.randbelow(len(g) // IW) * IW
    g[pos:pos + IW] = [rng.next_u32() for _ in range(IW)]
    c["genome"] = g
    return c


def nc4_population(rng: SplitMix64, lengths: list, template: dict) -> list:
    """Fresh uniform genomes at the given lengths, all other manifest fields from the template."""
    out = []
    for L in lengths:
        out.append(fresh_manifest(rng, L, template["tape_words"], template["n_regs"],
                                  template["persist"], template["code_writable"],
                                  template["tick_budget"], template["out_cap"]))
    return out


def symmetrize(kernel: list) -> list:
    """p_sym(d) = (p(d) + p(-d)) / 2. Mechanical, no judgment, provably zero-mean.

    A symmetric step distribution has zero drift in an unbounded space BY CONSTRUCTION. So every
    unit of drift NC1 exhibits is attributable to the reflecting bounds and the finite support,
    and nothing else. That is precisely the GEOMETRY term the brief asks to separate out.
    """
    p = dict(kernel)
    ds = set(p) | {-d for d in p}
    sym = [(d, (p.get(d, 0.0) + p.get(-d, 0.0)) / 2.0) for d in sorted(ds)]
    tot = sum(w for _d, w in sym)
    return [(d, w / tot) for d, w in sym]


def nc1_walk(start: int, rng: SplitMix64, kernel: list, lo: int, hi: int, n_steps: int,
             checkpoints: set) -> dict:
    """Reflected bounded walk on an integer coordinate. Out-of-range steps are no-ops.

    The no-op reflection is not a modelling choice: it is exactly how the grammar's own bounds
    behave (an operator that would leave the published range returns the manifest unchanged).
    """
    deltas = [d for d, _w in kernel]
    weights = [w for _d, w in kernel]
    v = start
    out = {0: v}
    for i in range(1, n_steps + 1):
        d = rng.weighted(deltas, weights)
        nxt = v + d
        if lo <= nxt <= hi:
            v = nxt
        if i in checkpoints:
            out[i] = v
    out[n_steps] = v
    return out


def measure_length_kernel(sample_rng: SplitMix64, n_samples: int, sizes: list, tape_words: int):
    """Empirical length-step distribution of the ACTIVE grammar, for use as NC1's kernel.

    Measured on uniformly random genomes at the given sizes, one operator per draw, chosen by the
    grammar's own frozen weights. Returns a list of (delta, probability). This is a measurement of
    the grammar, not a choice about it.
    """
    from proteus.foundry import grammar
    counts = {}
    total = 0
    for L in sizes:
        for _ in range(n_samples):
            m = fresh_manifest(sample_rng, L, tape_words, 8, "none", False, 64, 4)
            mate = fresh_manifest(sample_rng, L, tape_words, 8, "none", False, 64, 4)
            _c, rec = grammar.mutate(m, sample_rng, mate)
            d = rec["len_after"] - rec["len_before"]
            counts[d] = counts.get(d, 0) + 1
            total += 1
    return sorted((d, c / total) for d, c in counts.items())
