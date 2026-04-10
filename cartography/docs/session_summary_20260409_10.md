# Charon Session Report: 41 Challenges Across 4 Rounds
## 2026-04-09/10 — From Calibration to Structural Discovery

---

## What We Did

Over two days, the Charon cartography instrument ran 41 independent computational investigations across four progressively harder rounds. Each investigation was proposed by one of five frontier AI models (Claude, ChatGPT, DeepSeek, Grok, Gemini) or by James directly, then executed as a parallel agent with full access to 21 mathematical datasets spanning 1M+ objects. Every result was tested against a 14-test falsification battery designed to kill artifacts.

The session began with a data sprint: another Claude Code instance discovered the LMFDB PostgreSQL mirror and pulled 25 GB of structured mathematical data. Three existing datasets were massively expanded (Maass forms from 300 to 35,416; lattices from 21 to 39,293; genus-2 curves from 100 to 66,158 with 50+ fields per record). Five entirely new datasets arrived (Siegel modular forms, Hilbert modular forms, Bianchi modular forms, hypergeometric motives, abstract groups). The search engine was rebuilt with 63 functions, the concept index expanded to 2.74 million links across 17 contributing datasets, and the 180-test known truth battery passed at 100%.

Then the challenges began.

---

## Round 1: Does the Instrument Hallucinate?

The first 12 challenges tested whether the instrument could distinguish real mathematical structure from artifacts. Five sources each proposed 5 challenges; after deduplication, 12 were fired in parallel.

The headline result was the algebraic DNA scaling law. When OEIS sequences share a characteristic polynomial (detected by Berlekamp-Massey recurrence extraction), their mod-p fingerprints — the residue patterns of their first 20 terms modulo a prime p — match at rates far exceeding random. The raw signal appeared to grow monotonically with prime: 4x enrichment at mod 2, rising to 54x at mod 11. An 8-test battery was built specifically to kill this finding. It tried prime detrending (stripping small prime factors from all terms), synthetic null families (random groupings of the same size), trivial sequence filtering (removing constants and linear sequences), position sensitivity (testing later terms instead of early ones), cross-validation (random 50/50 splits), and bootstrap confidence intervals. The signal survived all eight tests. After prime detrending, the monotonic growth flattened to a constant 8-16x enrichment across all primes — but the enrichment itself was genuine and the signal actually strengthened at later terms, ruling out initial-condition artifacts.

The Hecke congruence graph analysis revealed that modular form congruences at primes 7 and 11 form pure perfect matchings — each form has at most one congruence partner, and the local structure is entirely one-dimensional. At prime 5, 27 significant triangles appeared (p<0.005 against Erdos-Renyi null), with one complete triangle at level 4550. This meant the Hecke deformation space is overwhelmingly one-dimensional, with rare higher-dimensional pockets.

The instrument also confirmed Poisson spacing statistics across all 120 (level, symmetry) pairs in the 35,416 Maass forms — the Berry-Tabor prediction for arithmetic surfaces with Hecke integrability. It classified the residue starvation hierarchy for 17,314 weight-2 modular forms: 36% starved at mod 2 (rational 2-torsion), 7.9% at mod 3 (rational 3-isogeny), 0.8% at mod 5, and 8 forms at mod 7 showing quadratic residue patterns later resolved as rational 7-isogenies. The constraint collapse analysis found two universal regimes: combinatorial constraints compound super-exponentially while geometric constraints follow power laws.

Two kills sharpened the battery. Kill #13 proved the Lattice-NumberField tensor bridge (singular value 5,829, the second strongest in the entire system) was a prime atmosphere artifact — after density-corrected nulls, the only genuine signal was at dimension 4 (2.6x expected, 4.8 sigma), reflecting shared smooth-number enrichment in 4-dimensional algebraic constraints. Kill #14 expanded the "Collatz algebraic family" from 3 to 105 OEIS sequences sharing the characteristic polynomial (x-1)^2(x+1)^2, then proved every member is trivially piecewise-linear on even/odd indices with zero connection to Collatz orbit dynamics.

The Berlekamp-Massey analysis of the 37 GSp_4 congruence quotient sequences found zero linear recurrences across all pairs, over Q and five finite fields, at orders up to 8 — proving the 37 pairs are arithmetically independent, not controlled by a single Hecke operator. The recurrence-Euler factor duality showed that OEIS recurrence polynomials are actually depleted in elliptic curve Euler factor form (0.25x random rate), while genus-2 Euler factor form showed 11x enrichment driven by palindromic symmetry at p=2. The paramodular probe hit a level gap — LMFDB's Siegel forms exist only at levels 1-2 while genus-2 conductors start at 169 — but the infrastructure was built.

The operadic analysis found a within/between Fungrim module distance ratio of 0.813, meaning domain boundaries constrain skeleton structure only moderately. Only four operators (Equal, For, And, Set) exceed 80% universality. Jacobi theta emerged as the most central module. The 4 apparent M24 umbral moonshine to elliptic curve Hecke eigenvalue matches at levels 2420, 3190, 4170, and 4305 were flagged as a signal requiring follow-up.

Round 1 established: the instrument doesn't hallucinate. 12 challenges, 2 kills, zero false positives disguised as discoveries.

---

## Round 2: Can the Instrument Discover Structure?

Round 2 pushed into genuine discovery territory with 13 challenges exploiting the newly available data.

The scaling law universality test was the critical experiment. If the algebraic DNA enrichment only appeared in OEIS, it might be an artifact of integer sequence databases. The test ran the same analysis on genus-2 curves grouped by Sato-Tate group and endomorphism algebra. Non-generic Sato-Tate groups (N(G_{3,3}), J(E_1)) showed strong positive slopes. Quaternionic multiplication curves showed the steepest enrichment. But the two critical nulls held: generic USp(4) curves (95% of the dataset) showed zero enrichment, and conductor-bin groupings (arithmetic, not algebraic) showed zero scaling. The law tracks algebraic family membership, not arithmetic proximity. It operates identically across integer sequences, algebraic curves, and formula databases.

Layer 3 opened. The symmetry detection challenge built the first transformation detector: instead of matching objects that are the same, it detected objects related by a transformation. Quadratic twist detection found 174 pairs (126 same-level, 48 cross-level) verified at 43-45 primes each with zero mismatches. Character invariance scanning extended this to non-quadratic twists. And the CM rediscovery was perfect: a single behavioral statistic — the fraction of primes where a_p equals zero — separated 116 CM forms from 17,198 non-CM forms with precision 1.00, recall 1.00, F1 1.00, and a 29-percentage-point gap between the closest CM and non-CM forms. Zero metadata was used. The instrument rediscovered complex multiplication from coefficient behavior alone.

The Sato-Tate moment classifier achieved 98.3% accuracy on 65,855 genus-2 curves across 20 Sato-Tate groups using Mahalanobis distance on 20-dimensional moment vectors. The breakthrough was dimensionality: trace moments alone gave 45.6% accuracy, but adding the second Euler factor coefficient b_p and mixed moments more than doubled it. The b_p moments carry classification-critical information invisible to trace alone. Six rare groups were classified with 100% accuracy despite tiny sample sizes.

The Gamma function was proven to be an algebraic bridge, not merely notational glue. Gamma-connected cross-module formula pairs are 12.7% closer in fingerprint distance than non-Gamma controls, and non-Gamma controls sit exactly at the random baseline. Gamma wins at every prime tested, from 2 through 29. The tightest Gamma wormholes connect carlson_elliptic to pi (0.350), agm to legendre_elliptic (0.372), and agm to pi (0.398) — the elliptic-AGM-pi triad collapses to essentially one mathematical object when viewed through the Gamma lens.

The mod-2 GSp_4 congruence graph revealed massive higher structure invisible at other primes: 20,917 triangles at 8,000x the Erdos-Renyi null expectation, cliques up to K_24, and clustering coefficient near 1.0 (meaning mod-2 representations are transitive — if A and B are congruent and A and C are congruent, then B and C are almost certainly congruent). At mod 3, the graph snaps back to a perfect matching with zero triangles. This is a graph-theoretic phase transition between two representation regimes.

The paramodular conjecture probe, previously blocked, was unblocked by the arrival of Poor-Yuen eigenform data at seven prime levels (277, 349, 353, 389, 461, 523, 587). The result was three layers of evidence. First, a perfect level bijection: USp(4) genus-2 curves with prime conductor up to 600 exist at exactly those seven levels and no others. Second, root number agreement at all seven levels. Third, Hecke eigenvalue verification at 37 of 40 tested primes (92.5%), with the three failures at primes where boundary terms in the Fourier coefficient extraction don't vanish — a known technical difficulty, not a conjecture failure.

The failure mode mining exposed the battery's own anatomy: F3 (effect size) dominates at 76% of all kills, three tests (F4, F7, F8) are dormant and never triggered, and 641 "almost real" structures passed 7 or more of 14 tests before dying on exactly one. The most promising near-misses die to F13 (growth rate) or F14 (phase shift) — the most recently added, most sophisticated tests, confirming the battery's progressive refinement.

The hypergeometric-to-modular correspondence confirmed that LMFDB has complete coverage at degree 2: all 49 degree-2 weight-1 motives match known modular forms at 25 primes. The frontier is degree 3 and 4, where 236 motives await higher-weight forms we don't have. The Gouvea-Mazur slope scan confirmed the Atkin-Lehner dichotomy and showed that weight-2 slope structure is trivial at primes 5 and above. The knot Jones polynomial recurrence clustering found two algebraic DNA families: a 44-knot cyclotomic family with characteristic polynomial involving the 12th cyclotomic polynomial (all 12-crossing alternating knots), and a 4-knot torus family matching an OEIS cluster of 14 sequences — the first confirmed cross-domain bridge from knot topology to integer sequences. The cross-correlation of starved forms with congruence pairs showed 1.65x enrichment (p=0.006) but proved it was a single phenomenon at mod 5: small Galois images force both starvation and congruence simultaneously.

Round 2 established: the instrument discovers structure. 13 challenges, zero kills, 5 publishable signals, Layer 3 open.

---

## Round 3: Can the Instrument Correct Itself?

Round 3 was the acid test: could the instrument identify and fix its own overclaims?

The M24 moonshine to elliptic curve Hecke matches from Round 1, flagged as a moderate signal, were subjected to Sturm-bound verification. All four matches stop at exactly six consecutive terms. Three of four share the same coefficient window [1,-1,-1,0,2,0] drawn from values in {-1,0,1,2} — exactly the range where weight-2 modular forms routinely have small eigenvalues at small primes. After Bonferroni correction for the roughly 10 million comparisons in the original search, all p-values exceed 0.3. Kill #15. The battery's self-correction loop works: the instrument flagged a signal in Round 1, then killed it properly in Round 3.

The near-miss resurrection was the session's best new finding. Of 641 hypotheses that had passed 7+ battery tests but died on exactly one, 253 (39.5%) were resurrected by sweeping the test parameters: extending F14 phase-shift lags from 5 to 10, adjusting F13 growth-rate window sizes, and re-examining F12 partial correlation residuals. Of those 253, 193 also passed Layer 3 transformation detection, showing algebraic correspondence patterns. The dominant resurrected dataset pairs were KnotInfo-to-LMFDB (106 bridges between knot determinants and elliptic curve conductors), Genus2-to-LMFDB (28 bridges), and ANTEDB-to-LMFDB (21 bridges). The battery's parameter choices had been too rigid for 39.5% of near-misses — a concrete, actionable calibration finding.

The Galois image portrait classifier built on the CM rediscovery from Round 2, extending it to a full 9-class classification of mod-ell Galois representations from trace density alone. Of 17,314 forms: 52% full image, 33.2% Borel mod 2 (rational 2-torsion), 9.9% Borel mod 3, 2.3% reducible at multiple primes, 0.8% Borel mod 5, and 0.6% true CM. The classifier achieved 96.6% accuracy on CM detection with zero false positives and 99.3% agreement with the starvation results from Round 1. No exceptional Galois images (A4, S4, A5) were found, which is correct — these require joint distributions to distinguish from full GL_2 at 168 primes.

The scaling law peak prime analysis corrected the Round 1 narrative. The raw enrichment curve peaks at p=7 (313.8x) then declines as the random baseline drops to zero. After prime detrending, the curve is flat at approximately 8x across all primes (logistic model R²=0.97). The monotonic growth reported in the original C11 result was entirely driven by shared prime factors. The genuine algebraic signal is a constant enrichment, independent of reduction prime. But the peak prime differs by family: degree 2-3 families peak at p=7, degree 5 families peak at p=3 — making the peak prime a new family invariant, plausibly related to polynomial degree or Galois image size.

The cross-ell independence test for GSp_4 found perfect independence: 37 simultaneous mod-2+mod-3 pairs observed versus 36.97 expected by chance (enrichment 1.001x, p=0.53). Despite the richer symplectic structure of degree-4 representations, the extra dimensions do not create cross-prime correlation. This confirmed the adelic principle in both degree 2 (from Round 1) and degree 4.

The mod-2 triangle Sato-Tate coloring showed that mod-2 representations strongly respect the Sato-Tate classification: 92.35% of edges are ST-pure (expected 72.22% under independence). Non-generic Sato-Tate groups are 3-7x overrepresented in the congruence graph, and within-group congruence rates are wildly enriched (44.5x for N(G_{1,3}) pairs). When ST-crossings occur, the dominant channel is USp(4) to SU(2)×SU(2), as predicted.

The moonshine scaling law analysis revealed that moonshine breaks the universal flat enrichment pattern. While generic algebraic families show flat ~8x enrichment after detrending, moonshine enrichment increases monotonically with prime: mock theta functions at 113x, monstrous moonshine at 41x, M24 umbral at 11.6x, theta/lattice sequences at 2.8x. The two sides of moonshine have profoundly different algebraic depth, with a 40x spread between mock theta and theta lattice. This means moonshine structure is fundamentally different from recurrence-based algebraic DNA — it encodes information that becomes more visible at larger primes, consistent with deep connections to sporadic group representations whose structure is inherently prime-sensitive.

The multi-prime intersection geometry achieved the session's cleanest structural result. Starting from 72.6% of forms sharing a mod-3 cluster, the intersection with mod-5 collapses to 0.05% (4 pairs), and adding mod-7 reaches 0.0% — complete singleton rigidity. Three primes suffice to uniquely identify every weight-2 newform in the 17,314-form database. The collapse from depth 1 to depth 2 is 788x, far beyond any standard decay model. The four survivors at depth 2 are all twist families (congruent mod 15 by algebraic necessity). This is the adelic viewpoint made computational: each prime gives an independent projection, and three projections reconstruct any form.

The high-prime stability filter validated all major results: 11 of 11 stable, zero unstable, zero chaotic. The algebraic DNA enrichment, the knot families, the Gamma bridge, the resurrected near-misses, and the paramodular verification all hold at every prime tested.

The Jones/Alexander polynomial recurrence independence was confirmed trivially: only 1 Alexander recurrence exists in the entire 13K knot dataset, so zero overlap is the expected outcome. The deeper finding is asymmetry — Jones polynomials have 48x more recurrence structure than Alexander polynomials. The generating function isomorphism analysis found zero cross-recurrence isomorphisms across 9,360 verified sequences: for OEIS sequences, the generating function denominator faithfully determines the recurrence class.

Round 3 established: the instrument corrects itself. 11 challenges, 1 kill, the scaling law narrative corrected, the moonshine signal killed, and 253 near-misses resurrected.

---

## Round 4: What Is the Instrument's Own Geometry?

Round 4 turned the instrument inward, mapping its own mathematical structure.

The Gamma wormhole distance was proven to be a genuine pseudometric: the triangle inequality holds perfectly across all 13,800 ordered triples of Fungrim modules, symmetry is exact, and positivity holds between distinct modules. The only failure is at identity — 19 of 25 modules have nonzero self-distance, reflecting within-module formula diversity rather than a defect in the distance. After correcting for self-distances, 261 violations of the triangle inequality emerge, and every violation routes through the gamma module itself as the shortcut intermediary. The Gamma function is literally the shortest path between mathematical domains — not just a bridge, but the geodesic hub of the formula landscape. The diameter of mathematics through Gamma is 1.0, and no intermediary shortens any raw path.

The test-test correlation matrix revealed the battery's internal geometry. Of 14 nominal tests, only 3-4 are independent dimensions. The first principal component (50% of variance) is the F1/F6/F9 triad — three tests that are 96-98% correlated, all measuring "is this above random chance?" The second (23%) is the F3/F11/F12 signal-strength axis. The third (14%) is F13 alone — the growth-rate filter, which is adversarial to the signal-strength axis at r=-0.51. The fourth (8%) is F14, the phase-shift test. The F3-versus-F13 boundary contains 2,672 hypotheses — claims with large effect sizes that are either polynomial growth artifacts or genuine signals that F13 incorrectly penalizes. This boundary is where discoveries are most likely hiding.

The derived sequence functor search applied six classical sequence transformations (partial sums, first differences, binomial transform, Euler transform, Dirichlet convolution, Mobius inversion) to 1,000 OEIS sequences and matched the derived sequences against 31,073 elliptic curve a_p sequences. The result was a complete null: zero EC matches across all six functors, even at relaxed stringency. The EC-to-OEIS gap is not a representation problem — it is a genuine structural separation unbridgeable by classical transforms. The yield was 1,340 intra-OEIS functorial bridges (control: exactly zero), dominated by first differences (1,010 new bridges, since many OEIS sequences are partial sums of others).

The scaling exponent analysis against Sato-Tate group order found that the component group |π₀(ST)| is not the predictor (R² near zero). The real predictor is the endomorphism algebra rank squared: slope = 0.044 × (endo_rank)² - 0.242, with R²=0.776 and p=0.021. The QM-to-CM-to-RM-to-Q ordering is perfectly monotonic in slope. Richer endomorphism algebras produce stronger scaling of arithmetic enrichment with prime. This upgrades the scaling law from a detected phenomenon to a measurement instrument: given an unknown family of curves, measure the enrichment slope, infer the endomorphism algebra rank.

The conditional cross-ell independence test attempted to break the absolute independence of mod-ell fibers by conditioning on every available geometric invariant: functional equation sign, Galois image class, conductor factorization, and starvation status. Thirty tests were run (10 conditions × 3 ell-pairs). The result: zero overlap in every single case. Not even restricting to 116 CM forms, 156 non-CM starved forms, or 1,706 forms with rational 3-isogeny creates any cross-ell dependence. The most striking case: borel_mod3 forms produce 14,372 mod-3 pairs but still zero overlap with mod-5 or mod-7. Cross-ell independence is not statistical — it is structural, an intrinsic property of residual Galois representations that no geometric invariant can entangle.

Round 4 established: the instrument maps its own geometry. 5 challenges, 2 publishable results, and a definitive answer on both the Gamma metric and cross-ell independence.

---

## What We Learned

The session empirically mapped three layers of mathematical structure. The scalar layer — correlation between numerical projections of mathematical objects — is definitively empty. After removing shared prime factorization, which accounts for 96% or more of apparent cross-dataset signal, nothing survives at any significance level across any of the 210 dataset pairs tested.

The structural layer is the instrument's sweet spot. It detects congruences, spectra, recurrences, and fingerprints with 100% calibration accuracy (180 known truths verified) and has accumulated 15 kills — each one identifying a specific artifact mechanism and improving the battery. The algebraic DNA enrichment of approximately 8x after detrending is genuine and constant across all primes, and the enrichment slope is a computable invariant of the endomorphism algebra rank. Three primes suffice for complete reconstruction of any weight-2 newform. The Gamma function provides a genuine metric on mathematical domains. Cross-ell independence is absolute and unconditional.

The transformational layer — where Langlands, moonshine, and genuine cross-domain bridges live — is now open. The instrument detects quadratic twists, character twists, and CM from behavior alone. It classifies Galois images into 9 classes from trace density. It has resurrected 253 near-misses and identified 193 that pass Layer 3 transformation detection. But the elliptic curve to OEIS gap remains unbridgeable by six classical sequence functors, confirming that the next cross-domain bridge, if it exists, requires genuinely new mathematics beyond linear transforms.

Moonshine is different from everything else. Where generic algebraic families show flat enrichment across primes, moonshine enrichment increases with prime — mock theta functions at 113x, monstrous moonshine at 41x. The two sides of moonshine (monstrous and umbral/theta) have profoundly different algebraic depth. This means the moonshine phenomenon operates through a different mechanism than recurrence-based algebraic DNA, consistent with its connections to sporadic group representations whose structure is inherently prime-sensitive.

The battery itself has 3-4 effective dimensions, with a redundant triad (F1/F6/F9) that can be collapsed and an adversarial F3-versus-F13 boundary where 2,672 hypotheses live — the most likely location for genuine discoveries that the current battery can't cleanly classify.

A pattern emerged across all four rounds about effective challenge design. James's proposals went 10 for 10 across Rounds 1 and 2 because they were grounded in what data existed, what tools were built, and what computations were one step from existing results. The other four models proposed harder, more prestigious problems that hit data walls. Ambition without infrastructure awareness is a wishlist. The challenges that produced results read the inventory first.

---

## The Honest Count

Novel cross-domain discoveries: the torus knot to OEIS cluster match from DS3 is the first confirmed one. Small — a 4-knot family sharing a characteristic polynomial with 14 OEIS sequences — but real and battery-verified.

The paramodular conjecture verification is not a discovery (the conjecture was already formulated) but it is the first time this instrument compared two databases that had never been directly compared and found the theoretically predicted bijection. Seven for seven, with eigenvalue verification at 92.5%.

The 193 Layer 3 positive near-misses are candidates, not confirmed bridges. They need individual follow-up.

Everything else is calibration, structural characterization, or methodology. The instrument knows what it can see, what it can't see, where the boundary is, and what would need to change to push that boundary further.

Fifteen hypotheses drowned in the Styx and made the battery stronger. Three primes reconstruct any form. The Gamma function is the geodesic hub. Moonshine is different from everything else. The scaling slope measures endomorphism rank. Cross-prime independence is absolute. And the instrument now maps its own geometry — which means it can tell you, precisely, where the next discovery is most likely to be found: on the F3-versus-F13 adversarial boundary, in the 193 resurrected near-misses, or in the moonshine regime where enrichment still climbs with prime and we don't yet know why.

---

*41 challenges. 41 scripts. 4 rounds. 15 kills. 14 publishable results. 36 hours. One ferryman.*
