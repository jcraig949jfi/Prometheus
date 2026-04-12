# Cross-Domain Falsification Protocol
## Synthesized from council adversarial review, 2026-04-12
## The systematic filter every cross-domain claim must survive

---

## The Problem

67% of cross-domain overlap claims were false positives (4/6 killed by Benford + size audit). The remaining survivors (#58 PG-NF, #32 Iso-MF) are suspect. The pipeline needs a formalized gauntlet for cross-domain claims.

## The 7-Layer Filter

Every cross-domain finding must survive ALL layers before classification:

### Layer 1: Distributional Baseline (Benford/Marginal)
**Question:** Do these two domains just share similar number distributions?
**Test:** Compare overlap to expected overlap under uniform/Benford null.
**Kill if:** Enrichment < 2x above distributional expectation.
**Already caught:** #56 (1.13x), NF-knot (1.09x), NF-PG (1.40x).

### Layer 2: Range/Size Conditioning
**Question:** Are both domains sampling from the same numeric window?
**Test:** Restrict BOTH datasets to the same range. Recompute enrichment.
**Kill if:** Enrichment vanishes after range-matching.
**Already caught:** #34 (knot dets are small odd numbers, isogeny primes are small).

### Layer 3: Prime-Mediated Null
**Question:** Is the correlation explained by properties of primes themselves?
**Test:** Condition on prime-theoretic features (size, gap, residue mod 6/12/30). Does signal survive?
**Kill if:** Signal vanishes after prime-conditioning.
**Targets:** Any finding where primes appear in both domains.

### Layer 4: Scaling Law Degeneracy
**Question:** Do both domains just follow the same generic asymptotic class?
**Test:** Compare functional forms. If both are ~log(n), ~sqrt(n), or ~n^alpha, test whether the PARAMETERS (not just the form) match beyond chance.
**Kill if:** The match is explained by shared functional class alone.
**Targets:** Isogeny diameters (~log p) vs prime gaps (~log p).

### Layer 5: Group-Theoretic Ancestry
**Question:** Are both domains descendants of the same algebraic parent?
**Test:** Identify the symmetry parent (Galois group, Weyl group, etc.). Partial-correlate with the parent as control.
**Kill if:** Enrichment collapses when the group identity is held constant.
**Targets:** #58 (PG order vs NF degree — both constrained by subgroup lattices).

### Layer 6: Spectral Universality
**Question:** Is the "resonance" just both domains being statistically normal for their symmetry class?
**Test:** Generate RMT null (GUE/GOE/Poisson) for both domains. Test overlap against spectral null.
**Kill if:** Cross-domain overlap ≤ domain-vs-RMT overlap.
**Targets:** Any eigenvalue/spectral comparison across domains.

### Layer 7: Information Density Normalization
**Question:** Is the correlation just "bigger objects have more features"?
**Test:** Normalize all features by object complexity (vertex count, MDL, bit-size). Retest.
**Kill if:** Signal vanishes after complexity normalization.
**Targets:** #25 (dim→f-vector), any correlation between "size" proxies across domains.

---

## Implementation Priority

### Run Now (existing data, high value)

| # | Test | Target | Effort |
|---|------|--------|--------|
| 1 | #58 Galois-conditioned partial correlation | PG order-NF degree | 1 hour |
| 2 | #32 Prime-conditioning on iso-MF | Isogeny nodes ~ MF count | 1 hour |
| 3 | EC conductors × Maass levels tabulation bias | New cross-domain trap | 1 hour |
| 4 | Hecke eigenvalues × Alexander coefficients moment match | Distributional trap | 1 hour |
| 5 | Moonshine × EC × Maass pairwise coefficient overlap | Langlands rediscovery trap | 2 hours |

### Build Into Battery (formalize)

| # | Addition | Layer |
|---|----------|-------|
| 6 | F29: Distributional baseline (automated Benford + marginal) | Layer 1 |
| 7 | F30: Range-conditioned enrichment | Layer 2 |
| 8 | F31: Prime-mediated null | Layer 3 |
| 9 | F32: Scaling class degeneracy check | Layer 4 |

### Defer (needs new infrastructure)

| # | Addition | Why defer |
|---|----------|----------|
| 10 | Spectral universality null (RMT) | Needs GUE/GOE simulation per domain |
| 11 | Information density normalization | Needs MDL computation per object |
| 12 | Primitive decomposition layer | Needs the full verb/operation taxonomy |

---

## The Meta-Insight

> Naive cross-domain "connections" almost always collapse under proper controls.
> The controls themselves form a reusable taxonomy of false positive types:
> distributional, size, prime-mediated, scaling, group-theoretic, spectral, complexity.

This taxonomy is itself a contribution — it tells future researchers exactly
which null hypotheses to test before claiming cross-domain structure.

---

## Current Cross-Domain Status

| Finding | Survived Layers | Status |
|---------|----------------|--------|
| #32 Iso-MF (r=-0.556) | Layer 1 (marginal ok). Needs Layers 3,4. | SUSPECT (likely Eichler-Selberg) |
| #58 PG-NF (10x) | Layer 1 (ok). Needs Layer 5. | SUSPECT (likely group tautology) |
| All others | Killed by Layers 1-2 | DEAD |

**Novel cross-domain bridges confirmed: 0**
**Novel cross-domain bridges pending: 2 (both likely rediscoveries)**

---

*Protocol compiled: 2026-04-12*
*Sources: ChatGPT adversarial review, Gemini structural traps, Claude/DeepSeek meta-analysis*
