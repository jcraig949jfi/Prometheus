# Cross-Landscape Findings: April 5, 2026
## First measurements of geometric correlation between mathematical datasets

---

## The Bridge Enrichment Test: POSITIVE

Namespaces in mathlib that share references to the same integer sequence
are significantly more likely to import each other:

| Sequence | Namespaces | Import Enrichment |
|----------|-----------|-------------------|
| fibonacci | 5 | 5.1x |
| lucas | 6 | 4.5x |
| bernoulli | 6 | 4.5x |
| catalan | 4 | 3.8x |
| motzkin | 4 | 2.8x |
| euler | 9 | 2.2x |

Base rate: 17.7% of namespace pairs connected. Fibonacci-sharing
namespaces: 90% connected. Integer sequences predict formal proof
dependencies.

## The RSA Test: NO SIGNIFICANT CORRELATION

Mantel test on 14 shared sequences: rho = 0.068, p = 0.52.

BUT: the OEIS distance matrix is degenerate. Most combinatorial
sequences are indistinguishable in log-term space (cosine dist < 0.02).
The failure is in the OEIS representation, not in the relationship.

Key observation: pairs close in mathlib (fibonacci-lucas, harmonic-lucas)
ARE numerically related. Pairs close in OEIS but far in mathlib
(catalan-motzkin) share numerical values but not proof context.

## OEIS Community Structure: Growth-Dominated

Spectral clustering (K=20) on 10K-sequence k-NN graph produces
clusters dominated by growth class and sign pattern:
- Alternating-sign cluster (213 seqs)
- Super-exponential cluster (87 seqs)
- Moderate-exponential cluster (176 seqs)
- Near-linear cluster (1,188 seqs)

The term-based embedding captures COMPUTATIONAL similarity (growth
behavior) but not MATHEMATICAL similarity (generative mechanism).
A better embedding would use cross-references or keywords.

## Cross-Landscape Search Results

| Test | Signal? | Key Finding |
|------|---------|-------------|
| OEIS -> mathlib (bridge) | YES (5.1x) | Sequences predict imports |
| OEIS -> mathlib (RSA) | No (p=0.52) | OEIS embedding too coarse |
| Groups -> OEIS | YES | 34 sequences share A000001 fingerprint |
| Zeros -> OEIS | YES | Floor/ceiling of zeta zeros ARE in OEIS |
| OEIS communities | Partial | Growth-dominated, needs richer features |

## What We Need Next

1. **Better OEIS embedding:** Cross-references, keywords, or formula
   structure instead of raw terms. The term embedding is dominated
   by growth rate, washing out mathematical structure.

2. **Full mathlib dependency graph:** The file-level import graph has
   only 1,799 edges. LeanDojo can extract 3M+ declaration-level
   edges. The richer graph would give stronger geometric signal.

3. **Shared objects as anchors:** The 14 sequences appearing in both
   OEIS and mathlib are too few for robust RSA. Need to expand the
   mapping (grep for specific term patterns, not just names).

4. **CCA on the shared subset:** After fixing the OEIS embedding,
   CCA would reveal how many shared dimensions exist between the
   two landscapes.

## The Emerging Picture

The landscapes are not geometrically aligned (RSA fails) but they
are topologically connected (bridge enrichment succeeds). This means:

- **Shared sequences create LOCAL bridges** between specific namespace
  pairs (fibonacci connects Algebra and NumberTheory)
- But **global geometry doesn't transfer** -- knowing a sequence is
  "close to Catalan" in OEIS tells you nothing about where it lives
  in mathlib

The relationship is topological (shared nodes create edges), not
geometric (shared distances create alignment). This is a real
structural finding about how mathematical knowledge is organized.
