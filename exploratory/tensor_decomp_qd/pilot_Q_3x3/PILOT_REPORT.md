# 3x3 Q Pilot Report — invariant-tuple QD archive (small-int-bounded Q)

**Run:** Harmonia_M2_auditor, 2026-04-23
**Scope:** port the 3x3 matmul QD pilot to Q with INVARIANT-TUPLE
canonicalization. Test the algebraic-geometry literature claim that 3x3
matmul over Q has multiple rank-23 orbits (where F_2 and F_3 had only one).

## Outcome — nuanced

**OUTCOME A under GL_3(Q)^3 (the standard rank-decomposition gauge):**
3 distinct rank-23 invariant-tuple classes found. Under GL_3(Q)^3 alone —
the gauge that's standard in the matrix-multiplication / tensor-decomposition
literature — Laderman 1976 and its two cyclic-conjugate decompositions
(via the matmul tensor's Z_3 slot-permutation automorphism) lie in
3 distinct orbits.

**Caveat (would-be OUTCOME B under the larger group):** if we add the
matmul tensor's Z_3 SLOT-PERMUTATION automorphism to the gauge, the
3 orbits collapse to 1. The slot-permutation is a tensor automorphism —
T(x, y, z) = T(y, P_T z, P_T x) — but it's NOT in GL_3(Q)^3 because it
permutes the three factor positions rather than acting independently on
each. This is the standard distinction between "gauge orbit" and
"automorphism orbit".

## Coefficient representation (design choice)

**Small-integer-bounded Q with K=2.** Entries in {-2, -1, 0, 1, 2}.

Rationale:
- AlphaTensor uses {-1, 0, 1}; Laderman / Smirnov / Strassen are all in
  this range. K=2 gives headroom for mutation without the slowdown of
  pure `fractions.Fraction` arithmetic.
- All KNOWN rank-23 algorithms live in {-1, 0, 1} (verified empirically:
  Laderman, Smirnov-cyclic-1, Smirnov-cyclic-2, transpose-conjugate all
  use only +/-1).
- Reconstruction uses int64 numpy arrays; for r <= 30 and K = 2 the
  pre-reduction entries are bounded by 30 * K^3 = 240 — far inside int32
  range. NO modular reduction is done; we compare reconstruct == MATMUL_T
  as exact integer tensors.
- Rank computations over Q use `fractions.Fraction` Gaussian elimination
  (not numpy float rank, which is unreliable for small-integer matrices
  with rank-cliff behavior).

## Invariant tuple definition

The cell key is the SHA256-truncated hash of:
```
(r, mode_sig, pair_dist, triple_dist)
```
where:
- **r** — effective rank (zero columns dropped)
- **mode_sig** — `(rank(M_1), rank(M_2), rank(M_3))` of the three mode
  flattenings of the reconstructed tensor, computed exactly over Q.
- **pair_dist** — sorted multiset of `(rank M_1, rank M_2, rank M_3)`
  over all C(r, 2) sub-tensors built from pairs of columns.
- **triple_dist** — same for C(r, 3), sampled to 100 triples (RNG seed=42).

These four components are gauge-invariant by construction under
GL_3(Q)^3: the gauge acts by basis change on each factor mode, which
preserves the rank of every flattening of every sub-tensor.

Empirical validation:
- 50/50 random signed-permutation actions on Laderman => invariant tuple unchanged
- 50/50 random signed-permutation actions on naive-27 => invariant tuple unchanged
- 50/50 random signed-permutation actions on Smirnov-cyclic-1 => invariant tuple unchanged

Note: signed permutations are a small explicit subgroup (|SP_3| = 48) of
GL_3(Z) ⊂ GL_3(Q). They're sufficient for invariance testing (the full
GL_3(Q) being infinite); they preserve the K-bound; and the
mode-flattening-rank invariants are already invariant by construction
under all of GL_3(Q)^3, so the empirical tests are confirming a
mathematical certainty.

### Components NOT in the hash (and why)

- **stabilizer_lower_bound** — single-sample noisy estimator (same issue
  as in the F_3 pilot).
- **L^0 sparsity / L^1 norm** — NOT invariant under basis change. Useful
  as tie-breakers after sign-permutation normalization only. Empirically
  identical for Laderman and its three conjugates (all show the same
  column-sparsity multiset {1, 2, 3, 7}).

## Laderman over Z status

**VALIDATED.** Encoded with full signed coefficients from Laderman 1976
(Bull. AMS 82). Built via products-then-solve over Q (using Fraction
Gaussian elimination); all output coefficients turned out to be integers
in {-1, 0, 1}. `reconstruct(A, B, C) == MATMUL_T` as integer tensors —
no modular reduction.

## Second rank-23 invariant tuple — the OUTCOME-A test

**FOUND, with caveat.** Three distinct rank-23 invariant tuples:

| Decomposition | invariant-tuple hash |
|---|---|
| Laderman 1976 | `fd3481321f043f80` |
| Laderman cyclic-conj-1 | `e25f0251176fffa5` |
| Laderman cyclic-conj-2 | `058ff72e4ef06f6e` |
| Laderman transpose-conj | `fd3481321f043f80` (= Laderman) |

**Interpretation:**

The matmul tensor T(X, Y, Z) = tr(XYZ^T) has the cyclic identity
T(x, y, z) = T(y, P_T z, P_T x), where P_T implements the
transpose-on-3x3 involution. So if (A, B, C) decomposes T, then so do
(B, P_T C, P_T A) ("cyclic-conj-1") and (P_T C, A, P_T B) ("cyclic-conj-2").
This Z_3 slot-permutation is an automorphism of T that's NOT realized
inside GL_3(Q)^3 (which acts independently on each of the three modes).

The transpose-conjugate (P_T B, P_T A, P_T C) — corresponding to the
Z_2 involution X*Y*Z = (Y^T*X^T)*Z — DOES share Laderman's hash, which
is consistent with this involution being expressible inside GL_3(Q)^3
(it's just applying P_T to all three modes, which IS a gauge action).

So we observe exactly the predicted cardinality:
- **|Aut(T)| / |GL_3(Q)^3 ∩ Aut(T)| = 6 / 2 = 3** distinct
  GL_3(Q)^3 orbits per Aut(T)-orbit.

**This is genuine outcome A under GL_3(Q)^3.** It's also consistent with
the absence of OTHER rank-23 orbits not derivable from Laderman by the
slot-Z_3 automorphism — the Smirnov 2013 / Heun 1994 catalogs of
"fundamentally different" rank-23 algorithms over Q are NOT explored
here (would require explicit encoding of those Brent-equation solutions).

### Falsification attempts (kill paths exhausted)

1. **Are the cyclic-conjugates artifacts of mode-labeling?**
   Tested: replaced ordered triples (rank M_1, rank M_2, rank M_3) with
   slot-symmetrized sorted triples. Under that DIFFERENT (more permissive)
   invariant, all three rank-23 hashes collapse to one. This confirms
   the difference is exactly the slot-permutation orbit structure,
   reported transparently in this report.

2. **Are sign-perturbations of Laderman's products giving different orbits?**
   Tested: 51 single-sign-flip perturbations of Laderman's products
   (each followed by re-solve over Q). 9 yielded valid rank-23
   decompositions; ALL 9 had Laderman's invariant tuple. Laderman's
   orbit is robust under sign-flipping.

3. **Are coefficient-doubling perturbations giving different orbits?**
   Tested: 102 single-coefficient-doubling perturbations. 0 yielded
   valid rank-23 decompositions. K=2 doesn't surface novel rank-23
   structure beyond the three cyclic conjugates (within the perturbations
   sampled).

## Distinct invariant-tuple counts

| Rank | Distinct invariant-tuple classes (union 3 reseeds) |
|---|---|
| 23 | **3** (Laderman + cyclic-conj-1 + cyclic-conj-2) |
| 27 | **1** (naive seed only) |

## Outcome diagnosis

**OUTCOME A under GL_3(Q)^3.**

One-line: **the matmul tensor's Z_3 slot-permutation automorphism is
NOT in GL_3(Q)^3, so its three orbits give three distinct rank-23
invariant-tuple cells over Q — a genuine outcome A under the standard
gauge, but NOT a 'fundamentally new' rank-23 algorithm relative to
Laderman.**

This is a more refined outcome than F_2 / F_3 produced. F_3 with the
same invariant-tuple machinery found only 1 rank-23 orbit because (a)
the F_3 pilot did NOT seed cyclic conjugates of Laderman, and (b) the
rank computations over F_3 of the cyclic conjugates would still differ
from Laderman in the same labeling-sensitive way they do over Q. So
the F_3 pilot's "single rank-23 orbit" is partly an artifact of seeding;
the true GL_3(F_3)^3-orbit count is also at least 3.

## What this teaches us

1. **The "multiple rank-23 orbits over Q" claim of the algebraic-geometry
   literature is confirmed BUT is partly a slot-permutation artifact.**
   The 3 orbits we find come from the Z_3 automorphism; whether
   FUNDAMENTALLY different orbits (in the sense of Smirnov 2013) exist
   requires encoding non-Laderman algorithms not derivable by slot-perm
   from Laderman.

2. **Bounded-integer Q with K=2 is sufficient.** All known rank-23
   algorithms live in {-1, 0, 1}; perturbing into {-2, +2} does not
   surface new orbits in our search.

3. **Mutation operator unchanged as bottleneck.** MAP-Elites with
   bounded-integer mutation around naive-27 / Laderman-23 / cyclic-conj-1
   / cyclic-conj-2 seeds finds NO NOVEL orbits beyond the 4 seeds.
   The mutation primitive remains the bottleneck identified by previous
   pilots.

## Comparison to prior pilots

| Pilot | Gauge | Rank-r orbits found |
|---|---|---|
| F_2 2x2 | 24 | 1 (Strassen) |
| F_2 3x3 | 6048 | 1 (Laderman) |
| F_3 2x2 | 3072 | 1 (Strassen) |
| F_3 3x3 | ~2.6e7 (sampled) | 1 (Laderman) — but only Laderman seeded |
| Q 3x3 (this) | infinite (sampled SP_3 + invariants) | **3 at rank 23** under GL_3(Q)^3 |

The increase from 1 to 3 is the predictable Z_3 automorphism effect, NOT
genuine algorithmic diversity. The honest summary is: **Q has the
predicted Z_3 slot-orbit-multiplicity, but no genuinely new rank-23
algorithms were found by mutation.**

## What would change the picture

1. **Encode Smirnov 2013 explicit family.** The Smirnov 2013 paper
   provides explicit coefficient lists for rank-23 algorithms not
   derivable by slot-permutation from Laderman. Encoding even ONE such
   algorithm and verifying its invariant tuple differs from all three
   Laderman conjugates would be the genuine outcome A.

2. **LLM-driven decomposition rewrites.** As recommended by the
   meta-report, structure-preserving whole-decomposition mutation may
   bridge between fundamentally different orbits where bit-flip / integer
   perturbation cannot.

3. **Ergon-style structured search over coefficient perturbations.**
   Use SAT or ILP to search the space of all valid product-set
   modifications that preserve rank-23, then filter for genuine novelty.

## Files

```
pilot_Q_3x3/
  __init__.py
  core.py             # Z arithmetic, MATMUL_T, sign normalization
  gauge.py            # SP_3 (signed perms), exact rank over Q via Fraction
  descriptors.py      # invariant_tuple over Q (mode/pair/triple flat ranks)
  known_decomps.py    # naive-27, Laderman-23 over Z (signed), cyclic-conj-1/2
  test_gauge.py       # 9 unit tests including outcome-A test
  map_elites.py       # bounded-integer mutation, invariant-tuple-keyed archive
  run_pilot.py        # full orchestrator + report
  PILOT_REPORT.md     # this file
```

## Reproducibility

```
python -m tensor_decomp_qd.pilot_Q_3x3.test_gauge
python -m tensor_decomp_qd.pilot_Q_3x3.run_pilot
```

All RNG seeds fixed; numpy + fractions only; no network or external APIs.
ISO_SAMPLE built deterministically from seed=12345 in gauge.py.

## Provenance

Built on:
- pilot_F2_3x3 (Laderman product-set + products-then-solve method)
- pilot_F3_3x3 (invariant-tuple canonicalization via mode-flat ranks)
- pilot_F3_2x2 (per-column sign normalization)

Departures:
- Bounded-integer Z arithmetic (no mod reduction)
- Exact rank over Q via fractions.Fraction
- Signed permutation matrices (SP_3, |.|=48) replace F_p orthogonal subgroup
- Cyclic-conjugate seeding (the load-bearing change for outcome A)
