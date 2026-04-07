# Charon Journal — 2026-04-07 Morning
## Overnight Triage: Zero New Discoveries, Three Confirmed Findings

---

## Overnight Run (8pm-1am, ~$0.08)
- 282 completed cycles, 96% success rate
- 681 threads tested, 204 battery runs
- 137 unique survivors after dedup

## Deep Dive Results

Every overnight survivor was manually tested with proper nulls.
**Zero new discoveries.** Every survivor was one of:

1. **Combinatorial noise** (64%): Knot determinants overlap EC conductors
   because both are subsets of odd integers. p=0.40 hypergeometric.
   ANTEDB bound ratios match constants because small fractions
   approximate everything. p=0.049.

2. **Tautologies** (16%): Fungrim zeta formulas correlate with mathlib
   zeta imports. Both reference the same math. Not a discovery.

3. **Known math** (5%): Zeta-Bernoulli co-occurrence (Euler's formula),
   Bernoulli mod 5 (Kummer congruences). Pipeline validates by rediscovery.

4. **Untestable** (8%): Crystal-knot connections (Materials data 0% complete),
   mathlib L-function↔knot distance (no knot modules in mathlib).

5. **Malformed** (2%): L(1,χ) values as knot determinants — irrationals ≠ integers.

6. **Resolution limits** (5%): Rank-0 vs rank-1 conductors, d=0.16.
   Direction real, magnitude too small.

## What Survived (all from Day 1 manual exploration, not overnight)

1. **Metabolism z=32** — 108/108 organisms, size-matched null confirmed
2. **Base-phi clustering** — independent PC3 axis (-0.661)
3. **5D constant-space** — effective dimensionality of ratio manifold

## Lessons

The v2 pipeline is an excellent hypothesis KILLER but a poor hypothesis
GENERATOR. The LLM proposes English-plausible but mathematically trivial
hypotheses: integers match integers, same-topic databases correlate,
small fractions approximate constants.

The battery catches most noise but its nulls are too lenient for integer
data — continuous random distributions don't match the combinatorial
structure of integer comparisons.

v3 needs: bridge-driven hypothesis generation (structural, not verbal),
integer-aware nulls, tautology prevention, and research memory to stop
retesting the same hypotheses.

## Fixes Implemented This Morning

1. **Research memory** — 451 hypotheses recorded with outcomes. Dedup gate
   rejects previously-falsified or 3x-tested hypotheses.
2. **Tautology detector** — rejects single-dataset and same-topic hypotheses.
3. **Research memory in prompt** — LLM gets exclusion list of what's been tested.
4. **Active threads reset** — overnight file grew to 121MB, reset to empty.

## Moving to v3

The overnight run proved v2 works as designed — it generates, tests, and
kills hypotheses autonomously at $0.08 for 6 hours. But it doesn't
discover anything new because the hypothesis generator is the bottleneck.

v3 replaces LLM hypothesis generation with tensor-train bridge detection.
The tensor finds structural bridges across datasets computationally.
The battery still adjudicates. The LLM becomes a fallback, not the driver.

---

*282 cycles. 681 threads. Zero discoveries. Three confirmed findings.*
*The pipeline works. The hypotheses don't. Time for tensors.*
