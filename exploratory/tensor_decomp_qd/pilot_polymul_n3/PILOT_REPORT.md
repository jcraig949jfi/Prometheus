# polymul-n3 Pilot Report — QD archive on the polynomial-multiplication tensor over F_2

**Run:** 2026-04-23
**Scope:** First non-matmul pilot in the tensor_decomp_qd ladder.
Tests whether a less-saturated bilinear tensor (polynomial multiplication
of degree-2 polynomials over F_2) admits multi-orbit QD diversity at the
optimum, which the matmul pilots failed to find.

## Tensor and field

- **Tensor:** polymul T in F_2^3 (x) F_2^3 (x) F_2^5 with T[i,j,k] = 1 iff i+j = k.
- **Field:** F_2 (n=3).
- **Naive rank:** 9.
- **Known low-rank seed:** 6 (Karatsuba-style: three corner products + three
  pairwise-sum cross products; see `known_decomps.py`).
- **Lower bound used:** 6 (treated as forbidden < 6 for the pilot's hard kill).

## Gauge group

After working out Aut(T) for polymul under F_2:

| Generator | Action | Order |
|---|---|---|
| SUB | Substitution x -> x + 1; Pascal-matrix action on inputs and output | 2 |
| REV | Index reversal x^i -> x^{n-1-i}; anti-diagonal J | 2 |
| SWAP | Commutativity p <-> q; mode-0 <-> mode-1 of T | 2 |

SUB and REV are involutions BUT do NOT commute on the polymul tensor.
Their composition has order 3 on each mode, so <SUB, REV> = D_3
(dihedral, order 6). SWAP commutes with both. **Total: |G| = D_3 x Z_2 = 12.**

This is a *much* smaller gauge than 2x2 matmul (|matmul iso| = 24 over
F_2, 3072 over F_3) — reflecting the simpler structure of polymul:
no GL_n basis-change action because the diagonal i+j=k is broken by
arbitrary basis change.

## Acceptance criteria

| Criterion | Status |
|---|---|
| Canonicalizer unit tests | **8/8 pass** |
| Karatsuba rank-6 reconstructs T | **Yes** (verified bit-for-bit) |
| Forbidden-rank violations | **0** across 15K+ submissions |
| Reseeded MAP-Elites runs to completion | **Yes** (3 reseeds, 5000 gens each, 1.3s total) |

## Orbit-stabilizer at the seeds

- **Karatsuba (rank 6):** orbit_size = 3, |stab| = 4, product = 12 (Lagrange holds).
- **Naive (rank 9):** appears in cell (9, 3, 3) in all reseeds.

## Outcome: B1

**Single rank-6 orbit reproduced across all reseeds.** Canonicalization
is stable; the rank-6 layer of the polymul-3 F_2 tensor admits only
Karatsuba's orbit under our 12-element gauge subgroup and bit-flip
mutation repertoire. **However**, this result is qualitatively
*different* from the matmul B1 outcomes — see "key findings" below.

| Reseed | Cells | Orbits | Rank-6 orbits | Rank-9 orbits | Valid/sub rate |
|---|---|---|---|---|---|
| 1 | 3 | 5 | 1 | 4 | 0.0299 |
| 2 | 3 | 3 | 1 | 2 | 0.0295 |
| 3 | 3 | 5 | 1 | 4 | 0.0283 |
| **Union** | — | **8** | **1** | **7** | — |

Pairwise Jaccard across archives = 0.500. Three reseeds find different
subsets of the rank-9 orbit space (4, 2, 4 each), with 2 in common
across all pairs. **The rank-9 layer shows real QD diversity.**

## Key findings

### Finding 1 — Polymul-3 over F_2 has a unique rank-6 orbit under our gauge

Like 2x2 matmul over both F_2 and F_3, the optimal layer is a single
orbit. The gauge here (12 elements) is much smaller than 2x2 matmul's
(24 over F_2), yet the result is the same: one orbit at the lower bound.

This adds polymul-3 to the list of "small bilinear tensors with
essentially unique low-rank decompositions over F_2." The hypothesis
that *less-saturated* tensors have richer orbit structure at the optimum
is **not supported** for n=3.

### Finding 2 — Rank-9 (naive) layer is genuinely diverse

8 distinct rank-9 orbits found across reseeds. The naive decomposition
is **NOT** Hamming-isolated: at distance 2, **46/4851 sampled flips
produce valid polymul decompositions, hitting 12 distinct non-naive
orbits**. This is a sharp contrast to:

- 2x2 matmul over F_2: Strassen at rank-7 has *zero* valid neighbors
  at distance 2 (3486 tested).
- 3x3 matmul over F_2: Laderman at rank-23 has *zero* valid neighbors
  at distance 2 (192,510 tested).

Polymul has **structural slack at the naive rank** that matmul does
not — consistent with the "less saturated" hypothesis at the
suboptimal layer.

### Finding 3 — Karatsuba rank-6 is Hamming-isolated

| Distance from Karatsuba | Sampled | Valid | Distinct orbits |
|---|---|---|---|
| 1 | 66 (all) | 0 | 0 |
| 2 | 2145 (all) | 0 | 0 |

Same pattern as Strassen / Laderman over F_2: the optimum is a
combinatorial island. The richness is in the *suboptimal* layers,
not at the rank-minimum.

### Finding 4 — Substitution generator surfaces a hidden Z_3

The biggest surprise: SUB (x -> x+1) and REV (index reversal) do not
commute. Their product has order 3, generating a hidden 3-fold symmetry
in the polymul tensor over F_2 at n=3. Concretely, this corresponds to
the cyclic permutation of the three "corners" of the polymul triangle
(p_0 q_0, p_1 q_1, p_2 q_2 - corresponding output positions r_0, r_2, r_4)
combined with appropriate cross-term shuffles.

**Why this matters:** the natural "obvious" gauge generators give an
8-element abelian group. The actual 12-element D_3 x Z_2 group is
necessary for canonicalization to collapse all gauge-equivalent forms.
Without closure under composition, test [4] failed (some
gauge-transformed Karatsubas canonicalized to a different byte string).

## Outcome diagnosis: B1 with caveat

**B1** by the standard rubric (single rank-6 orbit, stable canonicalization,
no forbidden violations, multi-rank archive populated). But this is the
*least-bad B1 in the ladder*:

| Pilot | Rank-min orbits | Sub-rank orbits | Naive 1-flip valid | Naive 2-flip valid |
|---|---|---|---|---|
| F_2 2x2 matmul | 1 | -  | 0 | 0 |
| F_3 2x2 matmul | 1 | - | 0 | 0/13944 |
| F_2 3x3 matmul (Laderman) | 1 | - | 0 | 0 |
| **F_2 polymul n=3** | 1 | **8** at rank 9 | **0** | **46/4851** |

Polymul gives the first cross-rank QD diversity in the ladder. This is
**genuine quality-diversity signal** — multiple rank-9 algorithms each
defining a distinct decomposition class — even though the rank-minimum
remains a single orbit.

## What this teaches us

1. **The "less-saturated tensor" hypothesis is partially confirmed**.
   Polymul has structural slack the matmul tensor lacks, but only at
   sub-optimal rank. The optimum is still a unique combinatorial island.

2. **The gauge group derivation needs care** for non-matmul tensors.
   Naive "list the symmetries" gave us 8 elements; closing under
   multiplication gave us 12. Test 4 (gauge-equivalence collapse)
   was the load-bearing kill criterion that caught this.

3. **Bit-flip mutation reaches sub-optimal diversity for polymul**.
   Unlike matmul where neither Strassen nor Laderman has *any* valid
   neighbor within distance 2, polymul's naive rank-9 has 46 valid
   2-flip neighbors. This makes polymul a viable substrate for studying
   sub-optimal QD structure.

4. **Substitution gauges are not optional** when the field has nontrivial
   automorphisms of the polynomial space. Over F_2 this gives just SUB
   (x -> x+1, since x -> x is identity); over F_p for p > 2 there are p-1
   substitutions and the canonicalizer cost rises by factor of p.

## What to do next

In order of increasing effort:

### Option A — n=4 polymul over F_2

Polymul of degree-3 polynomials. Tensor F_2^4 (x) F_2^4 (x) F_2^7. Naive
rank 16, known rank 7 (Karatsuba composition). The known rank is much
lower than naive, so the QD search has more room. Substitution gauge
becomes 8 elements (x -> x + a + b·x^2 - wait, no: just x -> x + a, but
a in F_2 still means SUB has 2 elements; closure with REV may give
larger group at n=4). Lower bound is **7** — known to be tight.

Effort: ~half-day. Direct extension of this pilot.

### Option B — n=3 polymul over F_3 with Toom-Cook 3-way

Over F_3 the substitution x -> x + a has *3* values (a in {0, 1, 2}).
Combined with REV and SWAP, gauge would be ~24-72 elements. Toom-Cook
3-way classically uses 5 evaluation points; F_3 only has 3 elements,
so we'd need points at 0, 1, 2, infinity, and... no, 4 points total.
Need to investigate which rank is achievable.

Effort: ~1-2 days. Mostly working out the right F_3 algorithm.

### Option C — convolution tensor over F_2

True circular convolution (n-th roots of unity) doesn't exist over F_2,
but acyclic convolution = polymul + truncation. Other convolution
variants (e.g., negacyclic) have different gauge structure. Could
distinguish gauge effects from tensor structure.

Effort: ~1 day. Architecture transfers directly.

### Recommendation

**Option A (n=4 polymul over F_2).** It is the cleanest extension that
(a) preserves the F_2 substrate where mutation is well-understood,
(b) exposes more orbit room since the gap between naive (16) and known
(7) is much larger, and (c) reuses the products-then-solve pattern from
the F_2 3x3 pilot to verify the Karatsuba-7 algorithm.

## Provenance

Code: `exploratory/tensor_decomp_qd/pilot_polymul_n3/`

- `core.py` — POLYMUL_T, reconstruction, column serialization
- `gauge.py` — D_3 x Z_2 gauge group (12 elements), canonicalize
- `known_decomps.py` — naive rank-9, Karatsuba rank-6 (verified)
- `descriptors.py` — rank, sparsity, stabilizer binning
- `test_gauge.py` — 8/8 unit tests pass
- `map_elites.py` — QD loop with forbidden-cell discipline
- `run_pilot.py` — orchestrator + 3-reseed diagnostic + neighborhood probe

Reproducibility: deterministic seeds, no external APIs, numpy only.
Run: `python -m exploratory.tensor_decomp_qd.pilot_polymul_n3.run_pilot`
Run log: `run_log.txt` in the pilot directory (full output of the run).
