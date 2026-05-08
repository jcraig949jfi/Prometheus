# Deep Research Batch 11 — Seed Candidates (open math problems, 2026-05-08)

**Drafted by:** Aporia
**Date:** 2026-05-08
**Status:** 18 candidates drafted (#199-216). Daily routine `aporia-batch-deep-research-daily` (cron 0 8 * * *, trigger `trig_01VUnq7wKU5YDgQzsnq1uMiF`) picks up batch10's 3 deferred reports first (#189 Effros-Marechal, #191 Bose-Einstein rigorous, #193 Razborov-Smolensky) then advances to this batch.

Batch 10 covered higher-dim AG, p-adic, Erdős corpus, operator algebras, L-functions beyond GL(2)/Q. Batch 11 pivots to a different under-represented territory derived from `aporia/docs/problem_database_coverage_2026-05-08.md` cross-reference: 32 confirmed gaps in the existing problems database against James's 134-problem 2026-05-08 prompt. Batch 11 picks 18 of those 32 gaps; the remaining 13 (mostly dynamics, transcendence, and specialized algebra) queue for batch 12.

## Doctrine constraints (binding)

Per `aporia/doctrine/critical_memories.md`:
- HARD-1: NO paper/publication framing in any subagent output
- HARD-2: actively suppress conventional-approach reflexes
- HARD-3: tensor-first; report should advance unified-tensor build
- HARD-4: every probe should yield calibration-anchor candidates
- HARD-5: structural-region language; NO bridge-narrative; physics-flavor extracts math, leaves probabilistic interpretation as docstring

Each report MUST cite at least 2 of:
PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND,
PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT,
PATTERN_RANK_PARITY_LEAK.

## Five fronts for Batch 11

1. **Number-theoretic non-prime conjectures** — totient, perfect-number variants, perfect-power gaps. Substrate has prime-heavy coverage (per `feedback_prime_atmosphere`); detrending pressure pushes us toward non-prime structure.
2. **Decidability and undecidability frontier** — Hilbert 10 over rationals, Euclid-Mullin, Riesel/Sierpiński. Calibration anchors for the substrate's verdict-vs-undecidable axis.
3. **Combinatorial graph cycles + toughness** — Erdős-Gyárfás 2^k cycle, Chvátal toughness, Erdős-Ko-Rado generalizations. Extends Batch 10's Erdős-corpus coverage downstream.
4. **Topology / triangulation / geometric ambiguity** — triangulation conjecture, Riemannian Zoll, illumination, congruent-number. Substrate currently thin in topology.
5. **Mean-value / classification-of-singularities** — Painlevé classification, mean-value polynomial conjecture. Operator-output-on-polynomials probe surface.

## Candidate queue (18, numbered 199-216)

| # | Title | Target | Front | Tier |
|---|---|---|---|---|
| 199 | **Lehmer's totient problem** — composite n with φ(n) divides n-1; brute-force search to 10^22 finds none; computational corpus tractable | Charon | NT non-prime | **1** |
| 200 | **Hilbert's tenth problem over Q** — decidability of rational-solution existence to polynomial Diophantines; Mazur uniform-boundedness adjacent | Charon | Decidability | **1** |
| 201 | **Erdős-Gyárfás 2^k cycle conjecture** — every graph with min degree ≥3 contains a cycle of power-of-2 length; empirical scan tractable | Ergon | Combinatorics | **1** |
| 202 | **Pillai's conjecture** — gaps between perfect powers grow arbitrarily large; Catalan-Mihăilescu provides anchor at gap 1; broader gap structure open | Charon | NT non-prime | 2 |
| 203 | **Quasiperfect numbers (σ(n)=2n+1)** — none known; existence open; sister to odd-perfect-number problem (which is in database, this is not) | Charon | NT non-prime | 2 |
| 204 | **Pollock tetrahedral conjecture** — every positive integer is the sum of at most 5 tetrahedral numbers; verified to large bounds; structure of exceptional integers if any | Ergon | NT non-prime | 2 |
| 205 | **Euclid-Mullin sequence** — recursively defined prime sequence; question whether every prime appears; relates to ineffectivity of Euclid's-style proofs of prime-infinitude | Charon | Decidability | 2 |
| 206 | **Riesel problem** — smallest k with k·2^n - 1 always composite; current candidate k=509203; many candidates eliminated empirically; verification vs proof gap | Charon | Decidability | 2 |
| 207 | **Sierpiński number problem** — smallest odd k with k·2^n + 1 always composite; conjecturally k=78557 (Selfridge 1962); verification structure | Charon | Decidability | 2 |
| 208 | **Triangulation conjecture** — every topological manifold triangulable; FALSE in dim ≥5 (Manolescu 2013 cohomology obstruction); subtle dim-4 boundary remains | Harmonia | Topology | 2 |
| 209 | **Congruent number problem** — deterministic algorithm for rational-sided right-triangle areas; Tunnell's theorem assumes BSD; computational frontier without BSD | Charon | NT non-prime | 2 |
| 210 | **Feit-Thompson divisibility conjecture** — for distinct primes p,q, (p^q-1)/(p-1) never divisible by (q^p-1)/(q-1); related to odd-order theorem foundations | Charon | NT non-prime | 3 |
| 211 | **Erdős-Ko-Rado generalizations** — specific open variants beyond classical k-uniform intersecting; r-wise intersecting, weighted versions, infinite-dimensional analogs | Ergon | Combinatorics | 3 |
| 212 | **Chvátal toughness conjecture** — toughness threshold guaranteeing Hamiltonicity; counterexamples for small thresholds; conjectured t=9/4 unresolved | Ergon | Combinatorics | 3 |
| 213 | **Riemannian Zoll surface classification** — manifolds where all geodesics are closed; round sphere is Zoll; what other Zoll metrics exist on S^2, S^n | Harmonia | Topology | 3 |
| 214 | **Illumination problem** — every mirrored room illuminable from a single point source; counterexamples exist for non-convex; convex case open in many subcases | Harmonia | Topology | 3 |
| 215 | **Painlevé integrability classification** — characterize ODEs with movable-singularities-only-poles property; six Painlevé transcendents canonical; classification frontier | Harmonia | Singularity classification | 3 |
| 216 | **Mean-value polynomial conjecture** — for degree-d polynomial f and z, ∃ critical point c with \|f(z)-f(c)\| ≤ \|f'(z)\|·\|z-c\|; Smale's conjecture; sharp constant unknown | Charon | Singularity classification | 3 |

## Priority tiers (Aporia recommendation)

**Tier 1 (fire first — 3 entries):**
- **#199 Lehmer's totient** — clean number-theoretic test; computational corpus to 10^22; calibration-anchor density growth in totient territory which has been thin in the substrate
- **#200 Hilbert 10 over Q** — decidability frontier; Mazur uniform-boundedness adjacency provides hooks; substrate's verdict-vs-undecidable axis benefits from explicit treatment
- **#201 Erdős-Gyárfás 2^k cycle** — combinatorics; high empirical tractability (random regular graphs as test corpus); tests PATTERN_BASE_RATE_NEGLECT directly via cycle-length distributions

**Tier 2 (operator-extension extensions — 8 entries):**
- 202, 203, 204, 205, 206, 207, 208, 209

**Tier 3 (theoretical / less LMFDB-tractable — 7 entries):**
- 210, 211, 212, 213, 214, 215, 216

## Token budget

- 20/day Google Deep Research, 3 concurrent agents per `aporia-batch-deep-research-daily` routine
- Plan: 6-7 waves of 3 (final wave of 2-3) over ~2-3 hours of agent firing
- Cloud agent picks up batch10 deferred (#189, #191, #193) first, then #199-216 in tier order

## Deferred to Batch 12 (13 of the 32 gaps)

- Sierpiński m²-n² form (similar shape to covered conjectures; lower priority)
- Cullen primes infinitude
- Palindromic primes infinitude
- Fibonacci primes infinitude
- Kusner L¹ conjecture
- Arnold diffusion (would need dedicated dynamics front)
- FPU paradox
- Ruelle-Takens turbulence transition
- Church-Turing physics thesis (philosophical; lower deep-research yield)
- Guralnick-Thompson conjecture
- Herzog-Schönheim conjecture
- Kaplansky direct finiteness (sister to zero-divisor which IS covered; partial overlap)
- π and e algebraic independence (transcendence theory; outside computational reach)

Batch 12 will pick a subset of these plus new gaps surfaced by future coverage cross-references.

## Status

- **2026-05-08: Batch 11 seeded.** Cloud routine (`trig_01VUnq7wKU5YDgQzsnq1uMiF`) will process on next 0 8 * * * UTC fire after completing batch10's 3 deferred reports.
- **Sensitivity Conjecture (Huang 2019)** intentionally excluded from batch 11 — it is RESOLVED. Backfilled to `aporia/mathematics/solved_problems_genealogy.md` as a calibration anchor (HARD-4) rather than a deep-research target.

---

*Aporia, 2026-05-08*
