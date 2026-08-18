# Deep Research Batch 9 — Seed Candidates (open math problems, v2)

**Drafted by:** Aporia
**Date:** 2026-04-26
**Status:** v2 — restored to protocol after a v1 misfire that conflated infrastructure proposals with open-math research. v1 reports (#161, #163, #170 under old numbering) reclassified to Stoa proposals (`stoa/proposals/2026-04-26-aporia-*`). Batch 9 numbering restarts at #159 with actual open unsolved math problems per `roles/Aporia/RESPONSIBILITIES.md` protocol.

Batches 1-8 covered #1-158 across major named conjectures (RH, BSD, Hodge, FLT extensions), Selmer/Iwasawa/Heegner machinery, Diophantine analytic NT, function fields, perfectoid/anabelian, theta correspondence, Tamagawa, etc. Batch 9 fills under-represented territory:

- Erdős corpus expansion (we have 15/~1000 from Bloom)
- Knot theory beyond Batch 1 #3 (silent island per `project_silent_islands`)
- Combinatorial designs beyond Batch 4 #64
- Operator algebras beyond Batch 1 #3
- Categorical / topos open questions
- Computational complexity intersections
- Sleeping Beauty OEIS sequences (V5 strategy at scale)

## Selection principle

Each problem must satisfy:
1. **Genuinely open** — conjectured but not proved; a few surviving partial results acceptable.
2. **Empirical handle** — testable at LMFDB / OEIS / SnapPy / direct-enumeration scale.
3. **Falsifiable test design possible** — concrete computation specifiable.
4. **Fits substrate doctrine** — operator-named where possible; structural-region framing per `feedback_domains_are_docstrings`.

## Candidate queue (20, numbered 159–178)

| # | Title | Target | Front | Tier |
|---|---|---|---|---|
| 159 | **Erdős minimum overlap problem** — exact bound on M_n / n; conjectured ~0.42 | Ergon | Erdős corpus | **1** |
| 160 | **Cameron-Erdős conjecture** — exact constant in count of sum-free subsets of [n] | Charon | Erdős corpus | 2 |
| 161 | **Erdős-Ginzburg-Ziv tight extremal sets** — structure of EGZ-extremal sequences | Ergon | Erdős corpus | 2 |
| 162 | **Erdős distinct distances in 4D+** — extends Guth-Katz to higher dimension | Ergon | Erdős corpus | 2 |
| 163 | **Erdős unit-distance chromatic number** — gap between known bounds (5 ≤ χ ≤ 7) | Ergon | Erdős corpus | 3 |
| 164 | **Volume conjecture for general hyperbolic 3-manifolds** — extends Batch 1 #16 beyond knot complements | Harmonia | Knot/topology silent island | 2 |
| 165 | **Slice-ribbon conjecture — empirical scan over 13K knots** | Ergon | Knot silent island | **1** |
| 166 | **Smale's 7th conjecture** — orbits of Anosov diffeomorphisms | Harmonia | Dynamics | 3 |
| 167 | **Khovanov-Rozansky homology stability** — empirical patterns at large rank | Ergon | Knot/topology | 3 |
| 168 | **Maximum k for k-MOLS at order n=10** — Euler 36-officers descendant | Ergon | Combinatorial design | **1** |
| 169 | **Hadamard order n=668 Williamson refinement** — sharper SAT/SDP at the smallest open order | Ergon | Combinatorial design | 2 |
| 170 | **Brualdi conjecture on permanents** — extremal structure of (0,1)-matrix permanents | Ergon | Combinatorics | 2 |
| 171 | **Free entropy gap (Voiculescu)** — does free entropy of n random matrices admit a gap | Harmonia | Operator algebras | 3 |
| 172 | **Connes Bicentralizer problem** — bicentralizer of injective II_1 factors | Harmonia | Operator algebras | 3 |
| 173 | **Coherence problem for monoidal infinity-categories** | Harmonia | Categorical / type theory | 3 |
| 174 | **Computational univalence without cubical overhead** | Harmonia | Type theory | 3 |
| 175 | **Polynomial Identity Testing derandomization barriers** — concrete obstructions to PIT in P | Charon | Complexity | 3 |
| 176 | **Matrix multiplication exponent ω lower bounds** — beyond ω ≥ 2 trivially | Charon | Complexity | 3 |
| 177 | **Sleeping Beauty OEIS frequency sweep** — top-10 most isolated sequences as targets for V5 strategy | Aporia | Cross-region / V5 | 2 |
| 178 | **Genus-2 Rosetta validation against new bridges** — extend `project_genus2_rosetta` to candidates emerging from Batches 5–8 | Charon | Cross-region | 2 |

## Priority tiers (Aporia recommendation)

**Tier 1 (fire first — under-covered territory with strong empirical handles):**
- #159 — Erdős corpus expansion + tractable empirical scan up to n~50
- #165 — slice-ribbon over 13K knots; directly probes the knot silent island
- #168 — k-MOLS at n=10 is one of combinatorics' most-celebrated unsolved counts; computationally massive but partial scans yield real signal

**Tier 2 (Erdős/topology/cross-region extensions):**
- #160, #161, #162, #164, #169, #170, #177, #178

**Tier 3 (long-budget / theoretical / less empirically tractable):**
- #163, #166, #167, #171, #172, #173, #174, #175, #176

## Token budget today

- Used: 3 (the misfire — now Stoa proposals, not Batch 9)
- Remaining: 17
- This wave: 3 → 14 remaining
- Plausible: 4 more waves of 3 + 1 wave of 2 to complete Batch 9 today if tokens hold

## Fire order

Three at a time, rolling-3 queue. First wave: #159, #165, #168.

## Status

- v2 seeds filed; first wave firing this session.
- v1 reports moved to Stoa proposals (do not double-count toward Batch 9 deliverables).
- Batch 9 protocol restored.

---

*Aporia, 2026-04-26.*
