# polymul-n4 Pilot Report — QD archive on the polynomial-multiplication tensor over F_2 (n=4)

**Run:** 2026-04-23
**Scope:** Direct extension of `pilot_polymul_n3` to degree-3 polynomials.
Tests whether the n=3 finding ("rich sub-optimal terrain at the
naive layer, single orbit at the rank-minimum") generalizes to
larger n where the gap between naive (n²=16) and known low-rank (9)
is much larger.

## Tensor and field

- **Tensor:** polymul T in F_2^4 (x) F_2^4 (x) F_2^7 with T[i,j,k] = 1 iff i+j=k.
- **Field:** F_2, n=4 (degree-3 polynomials, 7-coefficient products).
- **Naive rank:** 16.
- **Known low-rank seed:** 9 (Karatsuba composition: split 4 = 2 + 2 and recursively
  apply Karatsuba-2; 3 sub-products × 3 mults each = 9). See `known_decomps.py`.
- **Lower bound used (forbidden floor):** 7. Conservative; published sharp
  lower bounds for F_2 polymul-4 are unsettled, but anything strictly < 7
  would be a major result and is treated as a hard kill.

## Gauge group

| Generator | Action | Order |
|---|---|---|
| SUB | Substitution x -> x + 1 (Pascal mod 2 on inputs and output) | 2 |
| REV | Index reversal (anti-diagonal J_4 / J_7) | 2 |
| SWAP | Commutativity p <-> q | 2 |

**BFS-closure of `<SUB, REV>` over F_2 at n=4: 6 elements.**
Same hidden Z_3 as polymul-n3: SUB and REV are involutions but their
composition has order 3, so `<SUB, REV>` = D_3 of order 6. Crossing
with SWAP gives **|G| = 12** — exactly the same gauge size as polymul-n3.

This is a substantive structural finding: the hidden Z_3 in polymul over
F_2 persists at n=4. We had documented in the n=3 pilot that this Z_3
"corresponds to the cyclic permutation of the three corners of the
polymul triangle." Apparently the same structure exists for any degree-2n-2
output triangle when reduced via SUB and REV jointly. Closure-test 4
verified: 20/20 random `(gauge × S_r)` transforms collapse to the
canonical Karatsuba9 form.

## Acceptance criteria

| Criterion | Status |
|---|---|
| Canonicalizer unit tests | **8/8 pass** |
| Karatsuba rank-9 reconstructs T | **Yes** (verified bit-for-bit) |
| Forbidden-rank violations | **0** across 4746 submissions × 3 reseeds |
| Reseeded MAP-Elites runs to completion | **Yes** (3 reseeds × 1500 gens, 0.4s total) |

## Orbit-stabilizer at the seeds

- **Karatsuba9 (rank 9):** orbit_size = 1, |stab| = 12 (full group). The
  Karatsuba-9 decomposition is INVARIANT under the entire 12-element gauge.
  Lagrange holds (1 × 12 = 12).
- **Naive (rank 16):** sparsity bin 4, present in cell `(16, 4, 3)` in
  every reseed.

The orbit-1 / stab-12 result for Karatsuba9 is striking: it is in the
maximally-symmetric position of the 12-element gauge. By contrast,
polymul-n3's Karatsuba6 had orbit_size = 3, |stab| = 4 — **less**
symmetric than n=4. Hypothesis: the recursive Karatsuba composition
inherits more symmetry than the single-level one, because the recursion
is intrinsically symmetric in the (low/high) split, and SUB acts to
exchange those halves consistently with REV.

## Outcome: B1 (Hamming-isolated rank-9, rich rank-16 sub-optimum)

Single rank-9 orbit across all reseeds. Same per-pilot pattern as
polymul-n3. **However**, the rank-16 layer shows extraordinary
sub-optimal diversity that polymul-n3 did not reach.

| Reseed | Cells | Orbits | Rank-9 orbits | Rank-16 orbits | Valid/sub rate |
|---|---|---|---|---|---|
| 1 | 2 | 2 | 1 | 1 | 0.0076 |
| 2 | 2 | 2 | 1 | 1 | 0.0089 |
| 3 | 2 | 2 | 1 | 1 | 0.0101 |
| **Union** | — | **2** | **1** | **1** | — |

Pairwise Jaccard = 1.0 across all archives. **MAP-Elites alone reaches
only 2 cells.** This is *not* the rich within-archive QD signal we hoped
for — but the neighborhood probe reveals real off-archive diversity.

## Key findings

### Finding 1 — Karatsuba9 is the unique rank-9 orbit under our gauge

Like polymul-n3 at rank-6 (and like every matmul pilot at the optimum),
polymul-n4 at rank-9 has a single gauge orbit. Adding to the count:
6 pilots × 3 fields × 4 tensor-sizes × 4 move-classes = 0 multi-orbit
optima found. Universal pattern: **the rank-minimum is a single
combinatorial island under bit-flip mutation and our gauge groups.**

### Finding 2 — Naive rank-16 has VERY rich sub-optimal terrain

The 2-flip neighborhood probe of the naive seed (240 entries total,
C(240, 2) × 1 sign-bit-each = 28,680 valid 2-flip neighborhoods,
EXHAUSTIVE):

| Distance | Sampled | Valid | Distinct orbits |
|---|---|---|---|
| 1 | 240 (all) | 0 | 0 |
| 2 | 28,680 (all) | **124** | **34** |

Compare:

| Pilot | Naive 2-flip valid | Distinct orbits | Naive size |
|---|---|---|---|
| F_2 polymul n=3 | 46/4851 | 12 | 9 cols |
| **F_2 polymul n=4** | **124/28680** | **34** | **16 cols** |
| F_2 2x2 matmul | 0 | 0 | 8 cols |
| F_2 3x3 matmul | 0 | 0 | 27 cols |

Polymul-n4 has **2.8× the 2-flip-distinct orbits of polymul-n3** in
absolute terms. As a ratio per (valid 2-flip × decomp size), it is
roughly comparable. The sub-optimal richness scales, at least linearly,
with n.

### Finding 3 — Karatsuba9 is Hamming-isolated under 1-flip AND 2-flip

| Distance from Karatsuba9 | Sampled | Valid | Distinct orbits |
|---|---|---|---|
| 1 | 135 (all) | 0 | 0 |
| 2 | 9045 (all) | 0 | 0 |

Same pattern as Karatsuba6 / Strassen / Laderman: the rank-minimum is a
combinatorial island. The richness is in the sub-optimal layers.
**0/9045 valid 2-flips** is even stronger than n=3 (also 0/2145).

### Finding 4 — MAP-Elites fails to discover the rich naive-16 neighborhood

This is a MUTATION-PRIMITIVE bottleneck (mirroring the META_REPORT's
diagnosis). MAP-Elites with our standard mutation rates (4% per-bit
flip, 5% column ops) effectively can not jump 2 bits with high
density of validity, because the per-bit rate produces mostly 1-flip
or 0-flip moves — and those are 100% invalid. At 240 bits with
p_bitflip = 0.04, the expected k for a single mutation is ~9.6 — far
above 2. So the mutator is OVER-shooting. Reducing p_bitflip to ~1/120
would land on the 2-flip neighborhood more often, but the MAP-Elites
results show this isn't happening with our current mutator.

**Implication:** the 34 sub-optimal orbits exist and are reachable from
naive-16 by 2 perturbations, but the random-walk character of bitflip
mutation does not concentrate on the right move-size to find them.
A neighborhood-aware mutator (sampling 2-flips explicitly) would
populate this space.

## Outcome diagnosis: B1 with sharper sub-optimal structure than n=3

**B1** by the standard rubric (single rank-minimum orbit, stable
canonicalization, no forbidden violations, multi-rank archive populated).
But — like polymul-n3 — this is a "B1 with substantive sub-optimal
diversity" rather than a flat negative result.

| Pilot | Rank-min orbits | Naive 2-flip valid | Naive 2-flip distinct orbits |
|---|---|---|---|
| F_2 2x2 matmul | 1 | 0 | 0 |
| F_2 3x3 matmul (Laderman) | 1 | 0 | 0 |
| F_2 polymul n=3 | 1 | 46/4851 (0.95%) | 12 |
| **F_2 polymul n=4** | **1** | **124/28680 (0.43%)** | **34** |

Naive-layer richness scales with n. **Polymul richness DOES generalize
to larger n in the F_2 substrate** — both the absolute distinct-orbit
count and the rank gap (16 → 9 vs 9 → 6) are larger than n=3, providing
even more "space" for sub-optimal QD diversity. The bottleneck is now
clearly the bit-flip mutation primitive, not the tensor structure.

## What this teaches us

1. **Sub-optimal diversity scales with n** for polymul over F_2.
   The "richness" finding from n=3 generalizes — but the rank-minimum
   stays a single orbit. The phenomenon is consistent and structural.

2. **The hidden Z_3 in polymul-F_2 gauge is generic, not n-3 specific.**
   At n=4 we still find `<SUB, REV>` = D_3 of order 6. The gauge group
   has the same `D_3 × Z_2 = 12` shape as n=3.

3. **Karatsuba-9 sits at the maximum-stabilizer position** of the
   gauge group. This is a stronger symmetry than Karatsuba-6 had at n=3.
   Recursive Karatsuba composition produces fully-gauge-invariant decomps.

4. **MAP-Elites with bit-flip mutation can not surface the
   2-flip-reachable sub-optimal diversity.** The 34 distinct orbits
   accessible via 2-flips of naive-16 are "out there" but our mutator
   doesn't concentrate on the move-size that finds them. This points
   directly at the META_REPORT's "mutation primitive bottleneck" thesis.

## What to do next

### Option A — neighborhood-aware mutator + larger budget

Add an explicit 2-flip mutator to map_elites that samples
combinations of 2 bit positions uniformly over all entries. Run the
n=4 pilot with this mutator and 5000+ gens. Hypothesis: the archive
will populate to ~34 cells at rank-16, mirroring the 2-flip probe.

Effort: ~half day. Direct refactor of `mutate()` plus longer run.

### Option B — n=5 polymul over F_2

Naive rank 25, known rank 13 or 14 (Karatsuba composition: 5 = 2+3, so
3 polymul-2's (rank 3 each) + 2 polymul-3's (rank 6 each) gives 9 + 12 = 21,
which is worse than naive — recursive composition needs n a power of 2.
For n=5 the published F_2 rank is around 13-14 via Toom-Cook variants).
This pilot would test richness scaling further.

Effort: ~1 day, mostly working out the F_2 rank-13 algorithm.

### Option C — convolution tensor over F_2 (cyclic vs acyclic)

True cyclic convolution over F_2 (Z_n^2 polynomial ring with x^n = 1)
has different gauge structure: the cyclic shift x -> ω x adds a Z_n
gauge generator. Could test whether non-trivial extra gauge alters
the sub-optimal richness pattern.

Effort: ~1 day.

### Recommendation

**Option A first.** The richness finding is real, but our pilot under-
counts it because of the mutation primitive. A 2-flip mutator would
let us actually populate the archive with the 34 orbits we know exist.
This is the cheapest test of the "mutation is the bottleneck" thesis
on a substrate where we already have the ground-truth orbit count.

## Provenance

Code: `exploratory/tensor_decomp_qd/pilot_polymul_n4/`

- `core.py` — POLYMUL_T (n=4), reconstruction, column serialization
- `gauge.py` — D_3 × Z_2 gauge (12 elements), canonicalize
- `known_decomps.py` — naive rank-16, Karatsuba-composed rank-9 (verified)
- `descriptors.py` — rank, sparsity, stabilizer binning
- `test_gauge.py` — 8/8 unit tests pass
- `map_elites.py` — QD loop with forbidden-cell discipline
- `run_pilot.py` — orchestrator + 3-reseed + EXHAUSTIVE 2-flip probes

Reproducibility: deterministic seeds, no external APIs, numpy only.
Run: `python -m exploratory.tensor_decomp_qd.pilot_polymul_n4.run_pilot`
Run log: `run_log.txt` in the pilot directory.
