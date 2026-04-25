# polymul-n3 over F_3 Pilot Report — QD archive on the polynomial-multiplication tensor over F_3

**Run:** 2026-04-23
**Scope:** Field-change extension of `pilot_polymul_n3`. Tests whether
the n=3 polymul richness over F_2 (single rank-6 orbit, 12 distinct
sub-optimal orbits at naive rank-9) generalizes to F_3, where matmul
pilots showed 100× higher fitness rate. Reuses the polymul-n3
architecture with F_3 arithmetic, a larger gauge group, and per-column
F_3* scaling.

## Tensor and field

- **Tensor:** polymul T in F_3^3 (x) F_3^3 (x) F_3^5 with T[i,j,k] = 1 iff i+j=k.
- **Field:** F_3 = {0, 1, 2}, n=3.
- **Naive rank:** 9.
- **Known low-rank seed:** 6 (Karatsuba-3-way over Z, signed coefficients
  reduced mod 3). Verified bit-for-bit against POLYMUL_T.
- **Lower bound used (forbidden floor):** 5 — by parameter counting (5
  output coefficients require ≥ 5 multiplications). Rank-5 itself, if
  found, would be a discovery.

Note on rank-5: over Q with Toom-Cook 3-way, polymul-3 has rank 5 via
5 evaluation points (e.g., 0, 1, -1, 2, ∞). Over F_3 there are only 3
finite elements + ∞ = 4 evaluation points, so Toom-Cook does NOT apply,
and the published F_3-rank of polymul-3 is 6 (Karatsuba). Whether
rank 5 over F_3 is achievable by a non-evaluation algorithm is, to my
knowledge, unsettled.

## Gauge group

| Generator | Action | Order |
|---|---|---|
| SUB1 | Substitution x -> x + 1; (Pascal_1)^{-T} on inputs, Pascal_1 on output | **3** |
| SCAL2 | Scaling x -> 2x; diag(1, 2, 1) on inputs, diag(1, 2, 1, 2, 1) on output | 2 |
| REV | Index reversal (J_3, J_3, J_5) | 2 |
| SWAP | Commutativity p <-> q | 2 |

**Closure surprise:** the BFS-closure of `<SUB1, SCAL2, REV>` produces
**24 elements** (non-swap subgroup). With SWAP: **|G| = 48**.

This is much larger than polymul-n3 over F_2 (|G| = 12), reflecting:
- The order-3 substitution generator (only order-2 over F_2).
- The non-trivial scaling subgroup F_3* (trivial over F_2).
- Non-trivial intersections between the three generators when closed
  under multiplication.

The naive product `3 × 2 × 2 = 12` is one quarter of the actual size 24:
there are non-commutative interactions making the full group considerably
larger than the direct product would suggest. This is a real closure
surprise and is the load-bearing reason test [4] was added with explicit
gauge-transformation enumeration.

Plus per-column F_3* scaling gauge (lambda, mu, (lambda·mu)^{-1}) for
lambda, mu in {1, 2}, quotiented by `normalize_all_columns()`.

## Acceptance criteria

| Criterion | Status |
|---|---|
| Canonicalizer unit tests | **9/9 pass** (extra subtest [4b] for F_3* scaling) |
| Karatsuba rank-6 reconstructs T | **Yes** (verified bit-for-bit) |
| Forbidden-rank violations | **0** across 4746 submissions × 3 reseeds |
| Reseeded MAP-Elites runs to completion | **Yes** (3 reseeds × 1500 gens, 1.3s total) |

## Orbit-stabilizer at the seeds

- **Karatsuba6 (rank 6):** orbit_size = 12, |stab| = 4 (Lagrange: 12 × 4 = 48). ✓
- **Naive9 (rank 9):** orbit_size = 6, |stab| = 8 (Lagrange: 6 × 8 = 48). ✓

These are real orbit-stabilizer computations at full 48-element gauge.
By contrast, n=4 over F_2 had Karatsuba9 with orbit_size = 1 (full
stabilizer); over F_3 at n=3, Karatsuba6 has stabilizer of order 4 only —
much less symmetric. Hypothesis: the larger gauge (more ways to
permute) means a generic Karatsuba decomposition is no longer a
fixed point.

## Outcome: B1 with non-trivial reseed disagreement at rank-9

**Single rank-6 orbit reproduced across all reseeds.** Same B1 pattern
as the matmul pilots and the F_2 polymul pilots. **However**, the
rank-9 (naive) layer shows interesting structure: 4 distinct rank-9
orbits across reseeds, with reseed-disagreement.

| Reseed | Cells | Orbits | Rank-6 orbits | Rank-9 orbits | Valid/sub rate |
|---|---|---|---|---|---|
| 1 | 3 | 3 | 1 | 2 | 0.0329 |
| 2 | 3 | 4 | 1 | 3 | 0.0259 |
| 3 | 2 | 2 | 1 | 1 | 0.0259 |
| **Union** | — | **5** | **1** | **4** | — |

Pairwise Jaccard = 0.500, 0.667, 0.667 (avg 0.611). Reseeds disagree
on which rank-9 orbits they find. **The rank-9 layer shows real QD
diversity.** Fitness rate (~3%) is comparable to F_2 polymul-n3 (3%)
but considerably below F_3 2x2 matmul (10%).

## Key findings

### Finding 1 — Karatsuba6 over F_3 has a unique orbit under our 48-element gauge

Like every other rank-minimum we've found across 7 pilots:
**single orbit at the rank-minimum**. The richness is in sub-optimal
layers, never at the optimum. This holds even with the much larger
gauge group of F_3 (48 vs 12 for F_2 polymul) — the larger gauge does
NOT reveal any additional rank-6 orbits.

### Finding 2 — Rank-9 (naive) layer has 4 distinct orbits, reseed-disagreement

Less rich than F_2 polymul-n3 (12 orbits at rank-9 layer in 2-flip
probe; 8 orbits in 3-reseed MAP-Elites archive). But richer than any
matmul pilot.

| Pilot | Rank-min orbits | Sub-optimum orbits (MAP-Elites union) | Sub-opt 2-flip distinct |
|---|---|---|---|
| F_2 2x2 matmul | 1 | - | 0 |
| F_3 2x2 matmul | 1 | - | 0/13944 |
| F_2 polymul n=3 | 1 | 8 | 12 |
| F_2 polymul n=4 | 1 | 1 | 34 |
| **F_3 polymul n=3** | **1** | **4** | **16** |

The 16 distinct 2-flip naive orbits over F_3 is comparable to F_2
polymul (12 at n=3, 34 at n=4). **The polymul richness pattern
generalizes to F_3, with similar magnitude.**

### Finding 3 — Karatsuba6 is Hamming-isolated under 1-flip and 2-flip

Exhaustive ternary 1-flip and 2-flip neighborhood probe of Karatsuba6
(66 entries × 2 deltas-per-entry):

| Distance | Sampled | Valid | Distinct orbits |
|---|---|---|---|
| 1 | 132 (all) | 0 | 0 |
| 2 | 8580 (all) | 3 | **0** |

The 3 valid 2-flip neighbors are gauge-equivalent reformulations of
Karatsuba (they canonicalize back to the same byte string). So
Karatsuba6 is genuinely Hamming-isolated under 2-flip mutation.

### Finding 4 — Naive9 has rich 2-flip neighborhood, MAP-Elites finds a subset

Exhaustive ternary 1-flip and 2-flip probe of naive9 (99 entries):

| Distance | Sampled | Valid | Distinct orbits |
|---|---|---|---|
| 1 | 198 (all) | 0 | 0 |
| 2 | 19,404 (all) | **119** | **16** |

MAP-Elites finds 4 of these 16 orbits across 3 reseeds. Random-walk
mutation discovers ~25% of the structurally-accessible 2-flip
neighborhood within 1500 generations.

### Finding 5 — F_3* scaling is a non-trivial gauge component

The per-column F_3* scaling test (`test_F3_scaling_collapses`, [4b])
verifies: 20 random per-column scalings of Karatsuba6 all canonicalize
back to the same form. This is a real component of the gauge that
F_2 pilots simply do not have. Without `normalize_all_columns`, every
non-trivial F_3*-scaled Karatsuba would appear as a "different orbit"
and inflate the orbit count. The canonicalizer correctly handles this.

### Finding 6 — Closure of <SUB, SCAL, REV> over F_3 is 24, not 12

The naive product `Z_3 × Z_2 × Z_2 = 12` would be the answer if SUB,
SCAL, REV pairwise commuted. They don't. SUB and REV interact much
like the F_2 polymul case (creating a hidden order-3 structure in
their product), and SCAL doesn't commute either with the substitution
x → x+1 (since c·(x + 1) = c·x + c ≠ c·x + 1 unless c = 1). The closure
to 24 is the load-bearing correctness gate — without it, test [4]
would have failed. This was caught and documented during construction
rather than via a debug cycle, but only because the F_2 polymul-n3
pilot's experience with `<SUB, REV>` non-commutativity was already
present in the precedent.

## Outcome diagnosis: B1 (with B2-leaning at rank-9)

**B1** at the rank-minimum (single rank-6 orbit, stable across reseeds).
Strictly speaking the rank-9 layer is "B2-shaped" — single rank-6 orbit
+ reseed disagreement at higher ranks — but per the standard rubric
this counts as B1 because the OPTIMUM is single-orbit.

**Polymul richness DOES generalize to F_3.** The rank-9 layer has
genuine QD diversity (4 orbits in MAP-Elites, 16 in 2-flip probe).
Fitness rate (~3%) is in line with the F_2 polymul-n3 baseline.

## What this teaches us

1. **Polymul richness generalizes across fields** at consistent magnitude.
   Both F_2 (12, 34 distinct 2-flip orbits at n=3, n=4) and F_3
   (16 at n=3) show double-digit naive-layer 2-flip diversity. The
   rank-minimum stays a single orbit in all cases.

2. **The fitness-rate boost from F_2 → F_3 (2x2 matmul: 0.1% → 10%)
   does NOT replicate at polymul.** Both polymul fields land at
   ~3% fitness rate, whereas matmul jumped 100×. Hypothesis:
   matmul's structure interacts uniquely with field-size
   (more F_3-valid combinations of {0, 1, 2} for the multiplication
   diagonal); polymul's diagonal-counting structure is mostly
   field-agnostic.

3. **F_3 gauges are genuinely larger and more intricate** than F_2 ones.
   Closure of `<SUB, SCAL, REV>` requires care — naive product gives
   12, true closure is 24. Per-column F_3* scaling is a separate
   gauge layer requiring `normalize_all_columns`. This adds canonicalizer
   complexity but the orbit-stabilizer test [6] verifies correctness.

4. **MAP-Elites again under-explores the rich 2-flip neighborhood.**
   Of 16 distinct rank-9 orbits accessible via 2-flips of naive-9,
   MAP-Elites finds 4 in 1500 gens. Random-walk mutation rate is
   off-target (over-flipping). Same diagnosis as polymul-n4.

## What to do next

### Option A — F_5 polymul-3

Test field scaling further. F_5 has 4 finite + ∞ = 5 evaluation points,
so Toom-Cook 3-way IS available — published rank is 5 (not 6).
Discovering rank-5 over F_5 with our QD setup would be a positive
existence result. Gauge size will be larger still (Z_5 × Z_4 × Z_2 × Z_2
naive ≈ 80, true closure perhaps ~100-200).

Effort: ~1 day. Mostly working out canonicalizer correctness for
the larger gauge.

### Option B — F_3 polymul-n4 or n=5

Same field, larger n. F_3 polymul-4 has known rank 9 (via Karatsuba
composition) just like F_2; maybe Toom-Cook variants reach 8 or 9
better. F_3 polymul-5 is unstudied territory.

Effort: ~1 day.

### Option C — Search rank-5 over F_3 directly

Spend the search budget exclusively at rank-5 (initialize all genomes
at rank 5, mutate within rank-5 candidates only). If after 50K gens
we find no rank-5 polymul, that's strong evidence rank 6 is tight
over F_3. This would be a publishable negative result.

Effort: ~half-day. Reuses existing infrastructure.

### Recommendation

**Option C** as a quick high-value test, then **Option A** for the
positive existence over F_5. The combination would establish:
- F_3 polymul-3 has rank ≥ 6 (negative result, currently conjectural)
- F_5 polymul-3 has rank-5 algorithms reachable via QD (positive result,
  a first-of-its-kind QD-discovered rank-minimum bilinear algorithm)

## Provenance

Code: `exploratory/tensor_decomp_qd/pilot_polymul_n3_F3/`

- `core.py` — POLYMUL_T over F_3, reconstruction, F_3* per-column normalization
- `gauge.py` — 48-element gauge (24 input × SWAP), canonicalize
- `known_decomps.py` — naive rank-9, Karatsuba rank-6 (signed Z-form, mod 3)
- `descriptors.py` — rank, sparsity, stabilizer binning (RANK_MIN_HARD = 5)
- `test_gauge.py` — 9/9 unit tests pass (incl. F_3* scaling subtest)
- `map_elites.py` — QD loop with ternary perturbations + F_3* scaling moves
- `run_pilot.py` — orchestrator + 3-reseed + EXHAUSTIVE 2-flip probes

Reproducibility: deterministic seeds, no external APIs, numpy only.
Run: `python -m exploratory.tensor_decomp_qd.pilot_polymul_n3_F3.run_pilot`
Run log: `run_log.txt` in the pilot directory.
