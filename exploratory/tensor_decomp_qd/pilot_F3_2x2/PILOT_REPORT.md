# 2x2 F_3 Pilot Report — QD archive, next substrate after F_2

**Run:** Harmonia_M2_sessionB, 2026-04-23
**Scope:** port the 2x2 QD pilot from F_2 to F_3. Tests the hypothesis
that char-2 orthogonality was the primary cause of outcome B in the F_2
pilots by moving to a field where the orthogonal group is not degenerate.

## Outcome

**B1, with an important refinement.** The method works MUCH better over
F_3 (10× higher fitness rate, meaningful exploration), but the DOMAIN
(2x2 matmul rank-7) still has essentially a single orbit under our gauge.

**This separates two previously-conflated hypotheses:**
1. **Char-2 is the problem** → predicts F_3 would show multiple orbits.
   **REJECTED** — F_3 has the same outcome.
2. **2x2 matmul is too small** → predicts small matmul tensors have
   unique low-rank decompositions regardless of field.
   **SUPPORTED** — F_2 and F_3 both show this.

So char-2 was a contributor (it collapsed `O_n(F_2)` to just permutations
and slashed orbit count), but the deeper cause is the structural simplicity
of 2x2 matmul. The rank-7 decomposition is essentially unique.

## What works better over F_3

| Metric | F_2 | F_3 |
|---|---|---|
| \|GL_2\| | 6 | 48 |
| \|O_2\| | 2 | 8 |
| Matmul isotropy subgroup | 24 | 3072 |
| Strassen stabilizer | 2 | 16 |
| Strassen orbit size | 12 | 192 |
| Fitness rate during MAP-Elites | 0.1% | ~10% |
| Valid 1-bit neighbors of Strassen | 0 | 0 |
| Valid 2-entry neighbors | 0/3,486 | 0/13,944 |
| Valid 3-entry neighbors | 0/95,284 | **12/762,272** |

The 12 valid 3-entry perturbations over F_3 all canonicalize to Strassen's
orbit — but their mere existence is the fundamental difference. Over F_3
the valid set is **locally connected** (you can walk within Strassen's orbit
via small moves), whereas over F_2 it's totally isolated.

## What passed (infrastructure)

| Check | Result |
|---|---|
| Canonicalizer unit tests (8) | all pass |
| `\|GL_2(F_3)\|` | 48 ✓ |
| `\|O_2(F_3)\|` | 8 ✓ (signed permutation matrices — I and swap with ±1 entries) |
| Matmul isotropy subgroup | 3072 ✓ |
| Scaling gauge over F_3* = {1, 2} | correctly quotiented via per-column normalization |
| Canonicalize performance | ~265 ms per call |
| Strassen rank-7 validated over F_3 | ✓ via products-then-solve method (signs reduced mod 3) |
| Strassen stabilizer-orbit | 16 × 192 = 3072 ✓ Lagrange |
| Gauge-equivalence collapse (15 random transforms) | ✓ all canonicalize to same bytes |
| Forbidden-rank check (< 7 per Hopcroft-Kerr) | 0 violations |

## What didn't change from F_2

Still at a single rank-7 orbit. MAP-Elites with 3 reseeds × 2000 gens ×
50 pop = ~18,000 submissions across archives, producing 600+ valid
decompositions — **all in Strassen's orbit or naive's orbit.**

## What this tells us (refined)

**The calibration ladder has now distinguished three causes:**

1. **Char-2 orthogonality degeneracy** (F_2-specific, 2× smaller
   orthogonal group than F_3 at n=2, 28× smaller at n=3). Real, but
   not the core issue.
2. **Tensor smallness** (2x2 matmul). 2x2 matmul rank-7 decomposition
   has essentially one equivalence class under column-perm + scaling +
   basis-change. This is a property of the TENSOR, not the field.
3. **Factor-matrix Hamming geometry** (the universal finding across all
   F_p matmul tested so far). Valid decompositions are isolated or
   very sparsely connected in factor-matrix space; bit-flip mutation
   alone cannot navigate.

Only when we move to **3x3 (or larger) matmul** AND **F_3 or larger
field** is there a realistic chance of finding multiple rank-r orbits
under a tractable gauge. But 3x3 over F_3 has `|GL_3(F_3)|^3 ≈ 10^12`
matmul isotropy size — brute-force canonicalization is infeasible.

## What to do next

### Option A — 3x3 matmul over F_3 with smart canonicalization

Critical blocker: `ISO_SIZE` would be ~10^7-10^10 for 3x3 over F_3
(after orthogonality filter). Brute-force canonicalize is infeasible.

Solution approach: **invariant-based canonicalization**. Instead of
enumerating 10^10 isotropy elements, compute gauge-invariant
fingerprints (stabilizer structure, eigenvalue-like invariants,
sparsity-after-normalization, ...) and bin by them. Might lose some
orbit discrimination but makes the search tractable.

Effort: ~1-2 days design + implementation.

### Option B — 3x3 matmul over F_2 with higher-arity flip-graph moves

We established (3x3 F_2 pilot) that 3-to-2 and 2-to-2 moves don't
fire from Laderman. Higher-arity moves (4-to-3 with rank-3 tensor
decomposition primitive) might. Rank-3 decomposition over F_2 is the
key primitive — harder than rank-2 but doable.

Effort: ~2-3 days for rank-3 decomposition + integration.

### Option C — move away from matmul

The thesis "QD archive of tensor decompositions" does not depend on
matmul specifically. Less-saturated bilinear tensors:
- Polynomial multiplication (Karatsuba territory)
- Convolution tensors
- Group-algebra multiplication (e.g., quaternion, complex)

Each has its own isotropy structure, potentially smaller than 3x3
matmul isotropy, with known rank upper bounds and unexplored orbit
counts.

Effort: ~2 days to build + seed one tensor family.

### Recommendation

Option B or Option C. Both push into genuinely unexplored territory
with tractable compute. Option A is blocked by canonicalization scaling
until someone invents a faster method.

If **B**: we extend the existing 3x3 F_2 infrastructure with higher-arity
moves; carries the char-2 limitations forward but tests whether higher
moves break the Laderman isolation.

If **C**: fresh architecture but simpler tensors; chance to show QD's
value on something the literature hasn't saturated.

## Provenance

Code: `tensor_decomp_qd/pilot_F3_2x2/`
- `core.py` — F_3 arithmetic, per-column scaling normalization
- `gauge.py` — GL_2(F_3) = 48, O_2(F_3) = 8, matmul isotropy = 3072
- `known_decomps.py` — naive rank-8, Strassen rank-7 (verified via solve-for-outputs)
- `descriptors.py`, `map_elites.py`, `run_pilot.py`
- `test_gauge.py` — 8/8 unit tests pass

Reproducibility: deterministic seeds, no external APIs.
