# Charon 2 review of Charon 1's batch (additive / multiplicative number theory)

**Reviewer:** Charon 2
**Date:** 2026-05-05
**Subject:** charon_1_01 through charon_1_05 + charon_1_SUMMARY.md
**Goal:** identify (a) Round-2 angles that would meaningfully change verdicts, (b) alternative attack surfaces Charon 1 did not try, (c) datasets the substrate could build to enable Round 2, (d) compute tools that would unblock specific attacks.

This is a Charon-on-Charon review applying the same falsification-battery discipline across the cross-batch boundary. I will be direct about where the work is incomplete or missed an attack surface — the substrate-grade output is rich criticism, not validation.

---

## Cross-batch executive summary

Charon 1 did 5 reasonable attack-profile passes in ~7 hours. Three problems produced PARTIAL_RESULT (Erdős–Straus, Brocard, Pillai); two produced clean obstruction-class maps (Twin Prime, Goldbach). The cross-cutting observations in the SUMMARY are sharp: the **shared parity barrier between Twin Prime and Goldbach**, and the **shared abc-conditional finiteness for Brocard and Pillai**, are exactly the substrate-grade cross-problem signals this batch was designed to surface.

**My headline claim: 4 of 5 problems are good Round-2 candidates, with very different scopes and execution profiles.**

1. **Erdős–Straus** — strongest Round-2 candidate by execution clarity. The 6 trouble residue classes mod 840 are a *finite, well-defined* search target, and Charon 1's empirical solution-size data (4–9 orders of magnitude blow-up) is the seed. A systematic parametric-family search via algebraic geometry (rational components on the quartic surface) is overdue.

2. **Brocard** — strongest Round-2 by compute-tractability. Berndt–Galway's 10⁹ verification bound is *25 years old*. A 2-week compute-engineering effort could plausibly extend to 10¹² or 10¹⁵, with modern hardware + optimized factorial-mod-prime + GPU.

3. **Twin Prime + Goldbach** — joint Round-2 candidates. Charon 1's Pattern 1 (shared parity barrier) suggests they should be attacked *together*, not separately. Substrate-grade Round 2: build a "sieve weight function landscape" that systematically explores parity-breaking candidates for linear additive configurations.

4. **Pillai** — moderate Round-2. Charon 1's structural map (three methods covering non-overlapping slices) is sharp; the gap is unifying them, which is research-grade not compute-grade. But computational extension of Stroeker–Tijdeman's c₀(3, 2) = 13 result to other (p, q) pairs is straightforward and substrate-grade.

**Recurring theme:** every problem in this batch has a **clear, finite, executable Round-2 plan**. None requires structural breakthroughs that aren't on the table; all require either (a) more compute, (b) systematic dataset-building, or (c) cross-problem methodological investment in shared obstructions (parity, abc).

---

## Per-problem critique and Round-2 plan

### Problem 1 — Twin Prime Conjecture

#### What Charon 1 did

Verified Hardy–Littlewood prediction at 10⁴, 10⁵, 10⁶ (ratios 1.317, 1.229, 1.181 — slow monotonic convergence to 1). Located the parity-barrier obstruction in Selberg/sieve theory; observed that even GEH-strength input to the Maynard framework yields k = 6 floor (not 2). Surveyed Friedlander–Iwaniec parity-break for non-linear configurations.

Verdict: NO_PROGRESS_DOCUMENTED_OBSTACLES.

#### What Charon 1 missed

**Three concrete attack surfaces are absent from the file:**

1. **Recent (2022–2025) Maynard / Sawin / Tao "primes in arithmetic progressions" line.** Maynard 2022 ("Primes in arithmetic progressions to large moduli") and Sawin 2024 ("Polynomial roots and Lehmer's problem", paraphrased venue) have produced refined bilinear-form input that wasn't available when the Polymath 8b retrospective was written. The k=6 GEH floor Charon 1 cites is from 2014; **the literature has moved**. Whether any of the post-2014 work narrows the GEH floor below 6 is something Charon 1 didn't check.

2. **Chowla conjecture / Möbius randomness machinery.** The Tao–Teräväinen 2018+ work on Chowla-style two-point correlations uses *entropy methods* + Matomaki–Radziwill multiplicative-functions-on-short-intervals. These techniques attack a structurally similar problem (correlations of arithmetic functions) and have not been systematically applied to twin primes. Charon 1 doesn't mention this line at all.

3. **AI-assisted automated sieve-search.** Charon 1 says: *"GPT/AI-assisted theorem proving has not produced traction here, as far as published literature shows."* This is true for *theorem proving*. But there is recent work (DeepMind's FunSearch 2023 for cap sets; AlphaProof 2024 for IMO problems) on using LLMs to *search for combinatorial constructions*. The Selberg / Maynard sieve weight functions are exactly the kind of structured combinatorial object FunSearch-style tooling could explore. **No published attempt has been made to systematically search the sieve-weight-function space using ML-augmented search.** The substrate is well-positioned to try.

#### Round-2 plan

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Survey post-2014 Maynard/Sawin/Tao bilinear-form work; check whether the k=6 GEH floor has been improved | 1 week | Updated obstruction-class map; potentially a corrected Charon 1 verdict |
| Apply Chowla / Matomaki–Radziwill machinery to twin-prime-shaped correlations: does the multiplicative-on-short-intervals theorem yield any twin-prime-relevant input? | 2–3 weeks (literature heavy) | Either a new partial result or clean negative documenting why this transfer fails |
| Build a "sieve weight function landscape": for parameterized families of Selberg-type weight functions, compute the resulting bounds; use ML-augmented search to look for parity-breaking candidates | 1 month (engineering + compute) | Reusable tool + dataset; novel research direction |

**Datasets the substrate could build:**
- **"Sieve weight function bound database":** for each Selberg/Maynard-style weight function (parameterized family), record the bound it produces for twin primes, the parity sensitivity, and the technical conditions. Currently this is folklore in the analytic number theory community.
- **"Pair-correlation dataset":** computed pair correlations of zeta zeros vs prime-pair distributions at scale (Montgomery 1973 was the conjecture; the substrate could maintain a numerical check at unprecedented scale).

**Compute tools:**
- An ML-augmented sieve-weight-search pipeline (FunSearch-style). The mathematical objects are well-defined (real-valued functions on small intervals with normalization conditions); the bound is computable; the parity-detection criterion is mechanical. **This is the single highest-novelty Round-2 angle in this whole batch.**

#### Honest assessment

Charon 1's parity-barrier diagnosis is correct as far as 2014 literature. **The post-2014 literature wasn't checked.** This is a real Round-2 gap. Beyond that, the ML-augmented sieve search is genuinely novel — no one has tried it systematically that I'm aware of, and the substrate's compute + AI stack make it tractable.

---

### Problem 2 — Goldbach's Conjecture (binary)

#### What Charon 1 did

Identified the s=2 vs s=3 circle-method asymmetry as the structural obstruction (binary lacks the "third factor" to spend on minor-arc cancellation). Surveyed exceptional-set exponent line (Pintz 2018 ~N⁰·⁷², Zhao 2025 — paraphrased venue). Verified empirical Goldbach to n=5000 with HL-ratio data. Connected Chen 1973's "p + (q or qr)" result to the same parity barrier as twin primes.

Verdict: NO_PROGRESS_DOCUMENTED_OBSTACLES.

#### What Charon 1 missed

1. **Decoupling theory applied to Goldbach.** The Bourgain–Demeter–Guth decoupling theorem (2016) yields refined Vinogradov mean-value estimates that translate to better bounds for the circle-method minor-arc loss. Charon 1's analysis of "you can't absorb minor-arc loss with only S(α)²" is correct *given fixed minor-arc estimates*. Decoupling-improved minor-arc bounds may shift the calculus. **Whether decoupling has been applied to binary Goldbach specifically is something Charon 1 didn't check.** Cf. attempt charon_2_03_lindelof.md, where decoupling was explicit.

2. **r(n) outlier analysis.** Charon 1 computed r(n) for n ≤ 5000 and reported HL ratios. **Outliers were not investigated.** For each even n, r(n) has a deterministic value; the HL ratio fluctuates. Are there even n with anomalously low r(n)? Anomalously high? Is there structural pattern (e.g., n divisible by many small primes)? This is a substrate-grade dataset opportunity: for every even n ≤ 10⁹, store r(n) and the ratio to HL prediction, look for structure in the residuals.

3. **Goldbach graph structure.** Define G_N: vertices are odd primes ≤ N, edges (p, q) where p + q ≤ N is even (i.e., p ≠ q). The conjecture says: every even n ≤ 2N is the sum of two endpoints of some edge. Studying G_N as a graph (degree distribution, clustering, expansion) could reveal whether Goldbach is "generic random graph" or has structural features. This kind of graph-theoretic analysis hasn't been systematically published.

4. **Connection to other "additive bases" problems.** Goldbach is the assertion that primes form an additive basis of order 2 for the even integers. Other classical bases (squares — Lagrange's four-square; cubes — Waring's problem) have been attacked with related-but-not-identical methods. The Vinogradov mean-value theorem for Waring is much better understood than for Goldbach. Cross-fertilization?

#### Round-2 plan

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Survey decoupling-theory applications to circle method for binary Goldbach (post-2016) | 1 week | Updated obstruction map |
| Build "Goldbach r(n) database" up to n=10⁹ with HL ratio + outlier flags | 2 weeks (compute, parallelizable) | Reusable dataset; outlier list as research candidates |
| Analyze Goldbach graph structure G_N for N=10⁵, 10⁶, 10⁷; compute degree distribution, clustering, expansion | 1 week | Novel structural angle |
| Attempt Waring-style cross-fertilization: do Vinogradov mean-value improvements translate? | 2 weeks (literature heavy) | Either a new partial result or clean negative |

**Datasets:**
- **"Goldbach r(n) database":** for every even n ≤ 10⁹, store r(n), HL-predicted r(n), ratio, and any anomaly flags. This dataset doesn't exist anywhere I'm aware of in clean form.
- **"Hardy–Littlewood residual database":** the same data but normalized — log(r(n)/HL(n)) plotted as a function of n's structural features. Residuals are where new patterns hide.

**Compute tools:**
- A parallelized r(n) computer: for each even n in a range, compute r(n) by checking primality of p and n−p for all p ≤ n/2. GPU-friendly with proper Sieve of Eratosthenes preprocessing.
- Goldbach graph G_N construction + standard graph metrics (NetworkX, but for primes — an embedded NumPy-friendly version).

#### Honest assessment

Charon 1's circle-method-asymmetry diagnosis is structurally correct, but **the modern decoupling literature wasn't surveyed**. The r(n) outlier analysis is a missed substrate-grade opportunity: with 1 week of compute, the substrate could produce a dataset that doesn't exist anywhere. Round 2 is well-defined.

---

### Problem 3 — Erdős–Straus Conjecture

#### What Charon 1 did (the most concrete partial result)

Reproduced the 7 Salez modular families covering most residues mod 840. Identified the 6 trouble residues {1, 121, 169, 289, 361, 529}. Computed empirical solution sizes for 5 trouble primes p ∈ {1009, 1129, 1201, 1801, 2521}, observing 4–9 order-of-magnitude blow-up of z relative to p. Connected to Tijdeman/abc-style finiteness arguments (speculative).

Verdict: PARTIAL_RESULT.

#### What Charon 1 missed (this is the most concrete Round-2 target)

**The quartic surface 4xyz = n(yz + xz + xy) is an algebraic-geometric object with an unstudied rational-component map.** Charon 1 noted this in Attack 3 but did not actually compute anything on the surface. Round 2 is straightforward:

1. **Systematic rational-points computation on the surface for each trouble residue.** For each of the 6 trouble residues r mod 840, treat n as a parameter ranging over primes p ≡ r (mod 840), and search for rational curves on the quartic surface 4xyz = n(yz + xz + xy) using Sage's `Curve` or `EllipticCurve` machinery. Each rational curve found = one new parametric family = one residue closed.

2. **Conversion to elliptic-curve language.** The Erdős–Straus surface for fixed n is a smooth quartic in ℙ³ — but it has a *family* structure as n varies. For each fixed n, the surface specializes to specific elliptic-fibration structure; the rational points correspond to torsion + Mordell–Weil generators. **Sage / Magma / PARI can compute these for individual n.** The substrate could systematically compute the Mordell–Weil rank of the elliptic surface over ℚ(n), looking for specialization-stable structure.

3. **Computational extension of Salez's verification past 10¹⁸.** The 2025 paper Charon 1 cited (arXiv:2509.00128) verified to 10¹⁸. Modern hardware + GPU could plausibly push to 10²⁰ or 10²². This is straightforward engineering.

4. **Tijdeman/abc reduction is genuinely speculative.** Charon 1 listed it but didn't verify whether anyone has tried it. Round 2 should explicitly check: is there a published reduction of Erdős–Straus to abc-style finiteness? If not, derive one and check whether weak abc gives finiteness.

#### Round-2 plan (this is the strong candidate for execution clarity)

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Build surface-geometry pipeline: for each trouble residue r mod 840, search Sage's rational-curve machinery for parametric families on the Erdős–Straus surface | 2 weeks | Either: closes 1+ residue (publishable) or negative result classifying why no parametric family exists |
| Extend Salez's verification to 10²⁰ (engineering) | 2 weeks (compute heavy) | Constrains the conjecture more tightly; ruled-out range data |
| Check abc/Tijdeman reduction in literature; if absent, attempt it | 1 week | Either: established conditional finiteness (analogous to Brocard) or documented gap |
| Build "Erdős–Straus solution-size database" for trouble primes up to 10¹⁰ | 1 week (compute) | Dataset; growth-pattern analysis |

**Datasets the substrate could build:**
- **"Trouble-residue solution database":** for each prime p in trouble residues up to some bound, store smallest (x, y, z), z-size, and growth-rate statistics. Charon 1's 5-prime sample is the seed; the substrate can scale to 10⁶+ primes.
- **"Quartic surface rational-component database":** for the Erdős–Straus quartic surface as a function of n, the known parametric families, the residue classes they cover, and the open residues.

**Compute tools:**
- A Sage-based surface rational-curve searcher that, given a quartic surface and a parameter family, exhaustively searches for low-degree rational parametrizations.
- A GPU-parallelized Egyptian-fraction solver (the brute-force search Salez and successors use is parallelizable; published code may not exploit modern hardware fully).

#### Honest assessment

**Erdős–Straus is the strongest Round-2 candidate by execution clarity in Charon 1's batch.** The mathematical reduction is concrete (6 finite residues), the algebraic-geometric framework is well-developed (Sage handles quartic surfaces), and the published frontier is recent (2025) and tractable. A 1-month focused Round 2 could plausibly close 1–2 trouble residues, which would be publishable.

---

### Problem 4 — Brocard's Problem

#### What Charon 1 did

Direct computational verification to n=1000 (consistent with Berndt–Galway 2000's 10⁹). Built QR sieve in (n, 2n], showing only {12, 14, 15, 23} survive for n ≤ 29 (excluding known solutions). Surveyed Wilson's-theorem structural identities. Identified Overholt 1993 weak-abc-conditional finiteness as the dominant theoretical structure.

Verdict: PARTIAL_RESULT.

#### What Charon 1 missed

1. **Computational verification range is 25 years stale.** Berndt–Galway's 10⁹ bound is from 2000. Modern hardware + optimized factorial-mod-prime arithmetic should reach 10¹² easily, possibly 10¹⁵ with 1 month of compute. Charon 1 mentions extending the range as a possible direction but didn't quantify the engineering. **This is a pure substrate engineering problem with clear deliverables.**

2. **Smallest-prime-factor distribution of n!+1 wasn't computed.** For each n in a range, compute the smallest prime factor of n!+1. If the conjecture holds, this is bounded by some structural function (Stormer's theorem gives related bounds); the empirical distribution might reveal pattern. **This is a substrate-grade dataset opportunity.**

3. **Wilson primes connection wasn't pushed.** Charon 1 noted Wilson configuration (n+1 prime gives p | m). Wilson primes themselves (where Wilson's theorem holds mod p², namely 5, 13, and 563 are the only known) are extremely sparse; if any Brocard solution corresponds to a Wilson prime, that would be a structural constraint. Verifying the relationship for the three known solutions and any future ones is a 5-minute check Charon 1 didn't run explicitly.

4. **Generalization n! + A = m² for varying A wasn't probed.** Dąbrowski 1996 generalized Overholt's argument to n! + A = m². The empirical structure across A values (which A admit known solutions, which don't) is a dataset. Could surface patterns invisible at A=1.

5. **abc-progress monitoring.** Charon 1 noted the abc-conditional dependence but didn't connect to the IUT/Scholze-Stix dispute (which is explicitly addressed in attempt charon_2_04_abc_conjecture.md). Cross-batch reference would tighten the Brocard dependency framing.

#### Round-2 plan

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Engineer extension of Berndt–Galway verification range from 10⁹ to 10¹² (or 10¹⁵ with more compute) | 1 month | New computational frontier; published-quality empirical bound |
| Build "n!+1 factor-structure database" — smallest prime factor, factorization shape, m'-value if Wilson configuration | 2 weeks | Dataset; potential structural pattern discovery |
| Check Wilson-primes / Brocard correspondence for known solutions | 1 day | Negligible cost; high-information sanity check |
| Empirical n! + A = m² survey for A ∈ [1, 1000] | 1–2 weeks | Generalization dataset; pattern detection across A |
| Cross-reference with abc-progress (Charon 2's attempt 04) | 1 day | Dependency-graph maintenance |

**Datasets the substrate could build:**
- **"n!+1 factorization database":** for n ≤ 10⁶ (or wherever factorization is tractable), the smallest prime factor and full factorization shape of n!+1.
- **"Brocard-Ramanujan generalization database":** for A in some range and n in some range, the (n, A) pairs where n!+A is a perfect square. Charon 1's analysis was A=1 only.

**Compute tools:**
- An optimized factorial-mod-prime engine: for verifying n!+1 ≡ 0 (mod p²) over many (n, p) pairs efficiently. The arithmetic is GPU-friendly.
- A modular-isqrt verifier: for given n in a range, check whether n!+1 is a perfect square by integer-sqrt + squared-back. Parallelizable.

#### Honest assessment

**Brocard is the strongest Round-2 candidate by compute-tractability.** A 1-month engineering effort plausibly produces a new published verification bound (Berndt–Galway's 10⁹ is genuinely old; the literature would absorb a 10¹² or 10¹⁵ bound). The factor-structure dataset is novel and substrate-grade. Cross-problem connection to abc-progress is structural maintenance.

---

### Problem 5 — Pillai's Conjecture

#### What Charon 1 did

Direct enumeration of small-k solutions; verified Catalan (k=1) and Pillai-extreme cases (k=7's 32³−181²=7). Mapped three method-coverage slices: Mihăilescu (k=1 only), Bennett (consecutive bases only), Baker linear-forms (general but ineffective). Surveyed Bennett 2001's exceptional-case list {(2,1), (2,5), (2,7), (2,13), (2,23), (3,13)}.

Verdict: PARTIAL_RESULT.

#### What Charon 1 missed

1. **Stroeker–Tijdeman c₀(p, q) computation for other (p, q).** Charon 1 cited c₀(3, 2) = 13 (Stroeker–Tijdeman 1982). Analogues for other exponent pairs — c₀(5, 2), c₀(5, 3), c₀(7, 2), etc. — likely exist case-by-case in the literature but not in consolidated form. **Compute the c₀(p, q) values for all (p, q) with p, q ≤ 10 in a clean table.** This is a substrate-grade reference artifact.

2. **LMFDB Mordell-curve database integration.** Charon 1 mentioned LMFDB Mordell curves in passing but didn't actually pull the data. The LMFDB has Mordell curves x³ − y² = k tabulated for k up to ~10⁵. **Cross-referencing this with Pillai's specific bases gives a sub-conjecture verification at scale.**

3. **Polynomial Pillai bridge.** Charon 1 cited arXiv:2201.10964 ("Pillai's conjecture for polynomials") but didn't analyze whether the polynomial result has an integer specialization. If polynomial Pillai is proven (or strongly partial), under what conditions does it descend to integer Pillai?

4. **Method-coverage matrix.** Charon 1 described the three-method fragmentation in prose. **The substrate could maintain a clean matrix: rows = (k, p, q), columns = methods (Mihăilescu, Bennett, Baker, abc-conditional), cells = [closed | partial | open].** This is the "tool-vs-target sparse matrix" pattern I noted in my Charon-3 review.

#### Round-2 plan

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Build "Pillai (p, q, k) method-coverage matrix" | 1 week | Substrate-grade reference artifact |
| Compute c₀(p, q) for (p, q) ∈ [2, 10]² via LMFDB Mordell-curve database integration | 2 weeks | Extension of Stroeker–Tijdeman 1982; publishable extension |
| Analyze polynomial Pillai → integer Pillai descent | 1 week (literature heavy) | Either a new partial result or clean negative |
| Cross-problem coordination: maintain abc-progress dependency map shared with Brocard, Charon 2's abc attempt | ongoing | Cross-batch dependency tracking |

**Datasets the substrate could build:**
- **"Pillai method-coverage matrix":** rows = (k, p, q) tuples, columns = effective-finiteness methods, cells = current status.
- **"c₀(p, q) table":** Stroeker–Tijdeman extended to all (p, q) ≤ some bound. The substrate could maintain this as a living artifact.

**Compute tools:**
- A Pillai-specific Sage/PARI wrapper that, given (p, q, k), checks all available finiteness methods and returns the status.
- Integration with LMFDB Mordell-curve API for cross-reference.

#### Honest assessment

**Pillai is the moderate Round-2 candidate.** The mathematical fragmentation is real and Charon 1's diagnosis is correct. Round 2 produces substrate-grade reference artifacts (method-coverage matrix, c₀(p, q) extension table) but doesn't move the underlying conjecture. Worth doing, but lower-priority than Erdős–Straus or Brocard.

---

## Cross-cutting observations from review

### Observation 1 — Two structural clusters mirror Charon 2's analytic/Diophantine split

Charon 1's batch (additive/multiplicative number theory) has its own 2-cluster structure that mirrors the Charon-2-batch (analytic/Diophantine) two-cluster pattern:

- **Sieve-theoretic / parity-barrier cluster:** Twin Prime, Goldbach. Both blocked by Selberg parity barrier; both would be unblocked by parity-breaking for linear additive configurations. **Cross-problem investment.**
- **Diophantine / abc-conditional cluster:** Erdős–Straus (speculative), Brocard (conditional via Overholt 1993), Pillai (conditional under abc). All three would benefit from abc/Szpiro progress. **Cross-problem investment.**

This 2-cluster pattern is genuinely substrate-grade. **A breakthrough in either cluster would unblock multiple problems.** The substrate's allocation should focus methodological work on (a) parity-breaking for linear additive configurations and (b) abc/Szpiro progress, rather than on individual problems.

### Observation 2 — Cross-batch abc dependency is a maintenance opportunity

Charon 1's Brocard and Pillai both depend on abc; Charon 2's attempt 04 directly attacks abc and surveys the IUT/Scholze-Stix dispute. **The substrate should maintain a cross-batch dependency map** showing which open problems are abc-conditional. This is cheap (1 day to build, 1 hour/month to maintain) and substrate-grade because it lets the substrate prioritize abc work proportional to its multi-problem unblock value.

Specifically: Brocard, Pillai, and a piece of Vojta-for-curves (charon_2_05_vojta) are all abc-conditional. **Three of nine problems across the Charon 1 + Charon 2 batches are abc-blocked.** That's a ~33% rate of abc-dependence in this slice of number theory. abc is a high-leverage substrate target.

### Observation 3 — Datasets are systematically missing from the literature

Each of Charon 1's 5 problems has a clean dataset opportunity that doesn't currently exist:

| Problem | Missing dataset |
|---|---|
| Twin Prime | Sieve weight function bound database; pair-correlation database |
| Goldbach | r(n) + HL-residual database (up to 10⁹) |
| Erdős–Straus | Trouble-residue solution database; quartic-surface rational-component database |
| Brocard | n!+1 factor-structure database; Brocard generalizations across A |
| Pillai | Method-coverage matrix; c₀(p, q) extension table |

**The substrate is unusually well-positioned to build these.** Most of the underlying compute is parallelizable, well-defined, and modest in cost (weeks, not months). **The math literature has not produced these datasets in clean form** because individual papers are scoped to individual results, not to maintained substrate.

### Observation 4 — Charon 1's voice was strong; their attack-surface coverage was uneven

The strongest pieces in Charon 1's batch:
- Twin Prime: the parity-barrier diagnosis and the GEH-floor-of-6 observation are sharp.
- Goldbach: the s=2 vs s=3 circle-method asymmetry diagnosis is the cleanest single insight in the batch.
- Erdős–Straus solution-size empirical data: the 4–9 order-of-magnitude blow-up is exactly the kind of substrate-grade observation that doesn't appear in the literature.

The weakest pieces:
- Twin Prime: post-2014 literature wasn't checked. The k=6 GEH floor citation is 12 years old.
- Goldbach: r(n) outlier analysis was a missed substrate-grade opportunity.
- Erdős–Straus: the algebraic-geometric Round-2 wasn't actually computed (Sage on quartic surfaces was within reach in 1.5 hours).
- Brocard: didn't quantify the engineering cost of extending verification past 10⁹.
- Pillai: didn't pull LMFDB Mordell-curve data for cross-reference.

This is normal for 1.25–1.5 hour passes. **Round 2 should target the missed compute opportunities.**

---

## Substrate-grade artifacts the substrate could build

Consolidated from the per-problem analyses:

### Datasets (single-investment, multi-paper-reuse value)

**Highest priority (would directly enable Round 2):**

1. **r(n) Goldbach representation database** (1–2 weeks compute): for every even n up to 10⁹, store r(n), HL-prediction, ratio, anomaly flags. **Doesn't exist anywhere I know in clean form.**

2. **Erdős–Straus trouble-residue database + quartic-surface rational-component database** (2 weeks): for each trouble residue mod 840 and each prime in that residue up to 10¹⁰, store smallest solution and growth metrics; for the underlying quartic surface, store known parametric families and their residue coverage.

3. **n!+1 factorization database** (2 weeks compute): for n ≤ 10⁶, store smallest prime factor and full factorization shape. Enables Brocard structural analysis.

**Medium priority:**

4. **Sieve weight function bound database** (Twin Prime / Goldbach cross-problem): parameterized Selberg/Maynard-style weight functions and their twin-prime / Goldbach bounds. Built as living substrate.

5. **Pillai (p, q, k) method-coverage matrix** (1 week): row=tuple, column=method, cell=status. Substrate-grade reference artifact.

6. **c₀(p, q) extension table** (2 weeks): Stroeker–Tijdeman c₀(3, 2) = 13 generalized to (p, q) ≤ 10.

**Cross-batch (Charon 1 + Charon 2 + others):**

7. **abc-conditional problem registry**: maintained dependency graph of which open problems unlock under abc/Szpiro progress.

### Compute tools (reusable infrastructure)

1. **Goldbach r(n) computer + outlier detector** (highest priority — directly enables Round 2 of Goldbach): GPU-parallelized over even n.

2. **Erdős–Straus quartic-surface rational-curve searcher** (high priority): Sage-based; given a quartic surface and a parameter family, exhaustively searches for low-degree rational parametrizations.

3. **Optimized factorial-mod-prime arithmetic for Brocard** (high priority): GPU-friendly modular factorial + isqrt verification.

4. **ML-augmented sieve-weight-function searcher** (highest novelty): FunSearch-style exploration of parity-breaking sieve candidates. **No published attempt; high-novelty Round-2.**

5. **LMFDB Mordell-curve API integration for Pillai** (medium): pulls k = x³ − y² data for cross-reference.

### Substrate-grade meta-direction

The "tool-vs-target sparse matrix" generalizes from Charon 3's batch to Charon 1's: every problem has a known set of methods, each with known coverage; the substrate's substrate-grade artifact is **the matrix itself** — what's covered, what's open, what dependency graphs connect them.

For Charon 1's batch specifically: building the abc-conditional registry + the parity-barrier registry would consolidate the cross-problem signals into navigable substrate.

---

## Round-2 priority ranking

By "substrate-effort to substrate-grade-output ratio":

1. **Erdős–Straus** (1 month focused work): closest to a publishable result via algebraic-geometric attack on the quartic surface. **Strong recommend.**

2. **Brocard** (1 month focused engineering): extension of Berndt–Galway's 25-year-old verification bound. Pure substrate engineering with clear deliverables.

3. **Twin Prime + Goldbach (joint)** (1–2 months): cross-problem attack on parity-barrier; ML-augmented sieve search is high-novelty Round-2. **Recommend if substrate has ML capacity.**

4. **Pillai** (2 weeks): substrate-grade reference artifacts (method-coverage matrix, c₀(p, q) extension); doesn't move conjecture but maintains substrate.

5. **Defer Twin Prime / Goldbach if no ML capacity:** without ML-augmented search, Round 2 reduces to literature consolidation, which is lower-leverage than the structural attacks above.

---

## Cross-batch coordination recommendation

This Charon 1 batch has structural overlaps with Charon 2's batch. Three coordination opportunities:

1. **abc-conditional registry**: Brocard (Charon 1), Pillai (Charon 1), Vojta-for-curves D=∅ (Charon 2 problem 5) are all abc-blocked. A single abc-progress-tracking artifact serves all three.

2. **Parity-barrier registry**: Twin Prime (Charon 1) and Goldbach (Charon 1) share the parity barrier; Charon 2's batch had no parity-barrier problems. The registry is Charon-1-specific but its structure (problem → method → ceiling) is transferable.

3. **Computational-extension cluster**: Brocard (Charon 1), Erdős–Straus (Charon 1), and to a lesser extent Volume Conjecture for 5_2 (Charon 3) all benefit from substrate compute extension of stale verification bounds. **The substrate could maintain a unified "verification-bound staleness" tracker** across batches.

---

## Honest reporting

Time spent on this review: ~75 minutes. I read all five Charon 1 attempt files plus the SUMMARY in detail, and produced concrete Round-2 plans with dataset/tool specifications.

**What I am confident about:**
- Erdős–Straus quartic-surface rational-component search is genuinely a 1-month focused project with publishable potential. The 6 trouble residues are finite and well-defined; Sage's machinery handles quartic surfaces; the literature gap (no parametric family for these residues despite 50+ years) is real.
- Brocard verification extension to 10¹² is straightforward engineering. Berndt–Galway's 10⁹ is genuinely 25 years old and modern hardware easily exceeds it.
- The cross-batch abc-dependency observation is real and actionable (3+ problems unblocked by abc progress).

**What I am less confident about:**
- The "ML-augmented sieve search" for parity-breaking is genuinely novel but I'm not confident it would produce traction in 1 month. It's higher-variance than the Erdős–Straus or Brocard Round 2s.
- Whether the post-2014 Maynard/Sawin/Tao literature actually narrows the GEH floor below 6. I'd want to verify before committing to that as a sub-claim.
- The polynomial-Pillai → integer-Pillai descent question. I cited it as a Round-2 angle but I'm uncertain whether such a descent is structurally feasible.

**What I did NOT verify in this review:**
- I did not run any computational searches myself.
- I did not fetch arxiv for 2024–2026 progress beyond what Charon 1 cited. Some of my "post-2014 literature wasn't checked" critique may be partially answered by papers Charon 1 implicitly relied on.
- I did not verify that arXiv:2509.00128 or arXiv:2511.07465 exist as Charon 1 cited them (Charon 1 marked some venues as paraphrased; my review trusts those tags).

**Recommendation for batch coordinator:**
- **Greenlight Round 2 for Erdős–Straus quartic-surface search** (1 month, clear deliverable, publishable potential).
- **Greenlight Round 2 for Brocard verification extension** (1 month, engineering, dataset deliverable).
- **Conditional greenlight for Twin Prime + Goldbach joint parity-barrier attack** with ML-augmented sieve search (1–2 months, higher variance, novel direction).
- **Lower-priority greenlight for Pillai method-coverage matrix** (2 weeks, substrate maintenance).
- **Greenlight cross-batch abc-dependency registry** (1 week, substrate infrastructure, multi-problem leverage).

— Charon 2, 2026-05-05
