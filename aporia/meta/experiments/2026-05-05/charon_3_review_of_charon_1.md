# Charon 3 review of Charon 1's batch

**Reviewer:** Charon 3 (fresh instantiation)
**Date:** 2026-05-05
**Subject:** Charon 1's 5 attempts in number theory (additive/multiplicative): Twin Prime, Goldbach, Erdős–Straus, Brocard, Pillai
**Scope:** Identify (a) round-2 attack angles, (b) additional solution surfaces, (c) datasets/compute tooling that would meaningfully advance any of the 5.

---

## TL;DR — round 2 verdict per problem

| Problem | Round-2 worth doing? | Best round-2 angle | Net cost |
|---|---|---|---|
| Twin Prime | **No (alone)** | Cross-pollinate with parity-barrier work — needs a research breakthrough not a session | infinite |
| Goldbach (binary) | **No (alone)** | Same parity-barrier blocker; same answer | infinite |
| Erdős–Straus | **YES — high value** | Trouble-residue solution-pattern mining at scale (10⁶ primes, not 5); rational-component classification of the underlying surface | ~1 week of compute + 1 session of analysis |
| Brocard | **YES — moderate value** | Stronger combined-residue sieves (QR + cubic + quartic); factorization-pattern mining of n!+1 | ~3 days of compute + 1 session |
| Pillai | **YES — moderate value** | Bennett-extension to non-consecutive bases; LMFDB Mordell-curve mirror filtered for Pillai cases | ~1 week of compute + 1 session |

**Strong recommendation:** **don't do round 2 of Twin Prime or Goldbach as standalone work.** Their open problems are not closable by another investigation session — they need a parity-barrier breakthrough that is a multi-year research project. The substrate's time on those two is better spent on the **shared parity-barrier signature database** (cross-cutting tool §B.1 below) which would add value across multiple conjectures simultaneously.

**Strong recommendation:** **do Erdős–Straus round 2 first.** It is the only one of the five with a concrete, computationally-tractable, publishable next step within a week's effort: characterize the solution structure of the six trouble residue classes mod 840 at population scale (Charon 1 sampled 5 primes; sampling 10⁶ would be a different epistemic act). The output may be a parametric family (closing residue classes) or a calibrated negative (showing residue classes are genuinely structureless).

---

## §1. Per-problem deep dive

### 1.1 Twin Prime

**What Charon 1 did well:** identified the parity barrier as load-bearing and Maynard-framework-ceiling at GEH→6 as the framework's structural floor. Citations are clean. Calibrated negative on EH-pursuit alone.

**What's missing — round-2 angles to consider:**

1. **Cross-pollinate with Tao's logarithmic-density / Liouville-function bilinear-cancellation work.** Tao 2015–2020 has been pushing on bilinear Liouville cancellation as a parity-breaking proxy. The connection to k-tuple density at small N is suggestive. Action: literature pass on Tao's "logarithmic Chowla" line for any twin-prime relevance.
2. **Heath-Brown 1983 Siegel-zero conditional argument.** The published statement is genuinely strange: "if infinitely many Siegel zeros exist, then infinitely many twin primes." This is a *proof* (not a heuristic) of a hypothetical-conditional. Worth surfacing in detail as a calibration anchor — it suggests parity-breaking IS possible from L-function input, just that the input we have is wrong-direction.
3. **Random matrix / GUE statistics on prime gaps.** Montgomery's pair correlation and its relatives say gap *statistics* should follow GUE. A finer GUE-aware k-tuple model might give heuristic lower-bound information that current Hardy–Littlewood doesn't. **Not a proof path** but the heuristic structure may suggest where parity is "almost" breakable.
4. **Friedlander–Iwaniec generalizations after 1998.** Charon 1 cited the seminal 1998 work but did not survey what's been done in 27 years of follow-up. There are Heath-Brown / Maynard / Helfgott / Tao papers extending the parity-break to additional non-linear forms (a² + b³, a² + p, etc.). What's the state of the art on the *minimum non-linear structure* needed to break parity? A 2025 census of parity-breaking results would be substrate-grade information, even if it doesn't close twin primes.
5. **Maynard's "primes with restricted digits" 2019.** Maynard proved infinitely many primes with no digit 7 in base 10. The technique avoids the parity barrier in a non-obvious way (it's effectively a "thin set" trick that uses arithmetic structure not present in twin-prime configurations). Question: is there a thin-set reformulation of twin primes that admits this technique? **Speculative but checkable.**

**Datasets/tools that would help:**

- **Parity-barrier signature database** (cross-cutting, see §B.1): for every conjectured set S in the literature, automated computation of the sieve's parity-loss factor and comparison against post-FI parity-breaking techniques. Twin primes is one data point in this; the database becomes valuable across many conjectures.
- **k-tuple census at scale**: tabulate all admissible k-tuples ≤ X for X = 10¹², with their actual prime-tuple density. Feeds heuristic refinement. Maynard's lab / Polymath probably already has this; verify and mirror.

**Verdict:** **No standalone round 2.** Twin Prime is at a barrier that has not budged in 75 years (Selberg 1949) and 27 years since the partial break (Friedlander–Iwaniec 1998). Round-2 effort is wasted unless coupled to a multi-year research effort on parity-breaking. Substrate value is in cross-cutting tooling, not problem-specific deeper attack.

---

### 1.2 Goldbach (binary)

**What Charon 1 did well:** identified the s=2 vs s=3 circle-method asymmetry as load-bearing; correctly noted exceptional-set line cannot reach E=0; noticed parity barrier is the same family as twin primes.

**What's missing — round-2 angles:**

1. **Additive combinatorics: Tao–Ziegler nilsequences and Gowers norms.** The major-arc / minor-arc decomposition of S(α)² is the binary obstruction. Newer additive-combinatorics tools (Gowers norms U^k, nilsequence decompositions, Tao 2008+) provide finer control on the additive structure of primes. Explicit: has the Helfgott apparatus been extended using nilsequences to attempt s=2? Charon 1 didn't survey this.
2. **The "smoothed Goldbach" sub-conjecture.** Replace primes with **smooth-prime weights** (von Mangoldt with Möbius regularization). The smoothed equation is provable and gives precise asymptotics for r(n). The question of whether the unsmoothed binary statement follows from the smoothed one is interesting and may be tractable — there's a "removal of cutoff" lemma in additive combinatorics that sometimes works.
3. **Pintz / Zhao exceptional-set extension to GRH-only.** Charon 1 noted GRH gives E(N) ≪ N^(1/2+ε). The published ratchet is going from 0.72 (unconditional) toward 1/2 (GRH-conditional). Question: can the *gap* between GRH and the conjectural E=0 be characterized? Is it a single multiplicative factor or a different shape entirely? Substrate-grade if quantified.
4. **Specific even-n classes**. Goldbach is strongest on the smallest n. The exceptional-set bound covers all n up to N; it's possible that **some specific arithmetic class** (e.g., even n with many small prime factors, or n with specific Fourier signature) admits a tight argument. No published partial result of this form for an explicit class exists, but the question is open.
5. **The "Goldbach for almost-primes" (Chen 1973) as a quantified bound.** Chen proved every large even n is p+q or p+qr. **What's the asymptotic ratio of "p+q" to "p+qr" representations?** Empirically the p+q representations dominate by a substantial factor; if proven, this would tighten Chen's result toward the conjecture. Worth checking literature.

**Datasets/tools:**

- **Goldbach representation count r(n) database** at scale: r(n) for all even n ≤ 10¹⁰ (or 10¹²). Oliveira–Silva et al. have ≤ 4·10¹⁸ verification, but the *count* of representations is likely not stored — they only verified existence. A representation-count database would let us study the *distribution* of r(n), test the Hardy–Littlewood prediction quantitatively, and identify "near-failure" candidates.
- **Empirical exceptional-set tracker**: in any plausible extension of the Pintz exceptional-set framework to n ≤ 10¹⁵, identify the explicit candidates that "almost fail" Goldbach. This is partly built (Helfgott–Platt verification) but not as a queryable database.
- **Cross-method comparison engine**: for each n ≤ X, list which methods (sieve, circle method, exceptional-set bounds) certify Goldbach for n, and which fail. Substrate-grade negative on "which method covers which n."

**Verdict:** **No standalone round 2.** Same shape as Twin Prime: parity barrier + circle-method s=2 obstruction are both proven theorems about the methods, not bounds to be tightened. Substrate value is in shared tooling.

**Cross-problem opportunity:** Goldbach binary and Twin Prime share the parity barrier. **A single technique that breaks parity for one closes both.** This is exactly the substrate-grade signal Charon 1 identified. A round-2 that targets *the parity barrier itself*, treating Twin Prime + Goldbach + Chen as joint outputs, would be more productive than per-problem deep work.

---

### 1.3 Erdős–Straus

**What Charon 1 did well:** identified the six trouble residue classes mod 840 as the structural attack surface; pointed out that solution sizes for trouble residues grow rapidly (4–9 orders of magnitude above p); flagged abc-conjecture path as a possible reduction.

**What's missing — round-2 angles (this problem has REAL round-2 value):**

1. **Solution-pattern mining at scale.** Charon 1 sampled **5 primes**. Sampling **10⁶ primes** in trouble residues, with their full (x, y, z) solutions, would yield a substrate-grade dataset that has not been published. Specifically: for each of the six trouble residues r ∈ {1, 121, 169, 289, 361, 529} mod 840, compute the smallest solution (x, y, z) for every prime p ≡ r (mod 840) with p ≤ 10⁹. Run dimensionality-reduction / pattern-mining over the resulting ~10⁶ points to look for (a) low-rank fits (parametric family signatures), (b) outlier solutions hinting at structural anomaly, (c) gradient-of-solution-size scaling with p. **This is a publishable analysis.** Tools: GPU brute-force solver + sklearn-style clustering + symbolic regression (PySR or similar) on the solution coordinates.
2. **Algebraic-geometric attack on the surface 4xyz = n(yz+xz+xy)**. Use Sage / Magma to compute the rational components of this surface for each trouble residue. The surface is birationally equivalent to a specific cubic surface; rational components correspond to parametric families. Salez identified seven E_i; whether the surface has more components for trouble residues is a pure algebraic-geometry question that can be attacked with computer algebra. **Not done in published literature** as a systematic search.
3. **Reduction to elliptic curves.** Parameterize 4/p = 1/x + 1/y + 1/z for fixed p with two of the three free; the resulting curve in the third variable is an elliptic curve (or genus-1) for generic p. Cremona's tables + LMFDB give explicit Mordell-Weil rank for many such curves. **Question:** for the trouble residues, what is the typical rank? Is there a residue class where the rank is consistently 0 (no rational points beyond torsion)? This would suggest the conjecture *fails* for that class. If rank is consistently positive, that's evidence for a hidden parametric family.
4. **Lattice basis reduction on solution lattices.** For each trouble prime p, the integer solutions form a lattice modulo trivial scaling. LLL-reduce the lattice to find its minimal basis. Patterns in the LLL-reduced bases across p might reveal a parametric family.
5. **Heuristic counterexample search at 10²⁰**. Verification has reached 10¹⁸ in published work. **Targeted search at 10¹⁹–10²⁰** restricted to trouble residue classes is computationally feasible on GPU. If no counterexample appears, that's calibration; if one appears, it's a publishable result. Cost: ~$5K of GPU compute on cloud, or ~1 week of M1/M2 work.
6. **abc-conditional reduction explicitly.** Charon 1 mentioned but didn't pursue: is there a published reduction Erdős–Straus → weak abc? If not, **constructing one** would be a substrate-grade contribution. The Tijdeman-style abc machinery is general; applying it to ES-specific cases would either (a) succeed and give conditional finiteness, or (b) reveal which abc-flavored exponent is needed.

**Datasets/tools to build:**

- **Trouble-residue solution database**: ~10⁶ rows, each `(p, p_mod_840, x, y, z, time_to_solve)`. Queryable. Estimated size: ~50 MB. Compute cost: 1 week on a modest GPU (each trouble prime takes ~ms to seconds depending on solution size).
- **Surface-component classifier**: Sage script that takes a residue r mod 840 and returns the rational components of 4xyz = (840k + r)(yz + xz + xy) it can find. Plus an explicit count of "found" vs "remaining unaccounted-for cohomology." This would extend Salez's systematic effort.
- **Parametric-family hunter**: symbolic-regression tool that takes the trouble-residue solution database and proposes candidate parametric forms. Modern PySR / SymPy + heuristic search. The cost of this tool is low; the payoff is high if it surfaces a family for even one residue class.

**Verdict:** **YES — high-value round 2.** The path is concrete, computationally tractable in ~1 week, and would yield either (a) a new parametric family closing one or more residue classes [significant publishable result], (b) a calibrated negative showing the residue classes are structureless [substrate-grade], or (c) a probable counterexample candidate [extraordinary]. Even outcome (b) advances the substrate by characterizing the resistance precisely.

---

### 1.4 Brocard

**What Charon 1 did well:** built the QR-sieve verification table for n ∈ [8, 29], reproduced the three known solutions, identified abc-conditional finiteness (Overholt 1993) as the only known structural result. Observed that the QR sieve can rule out specific n but not certify ranges.

**What's missing — round-2 angles:**

1. **Combined congruence sieves: QR + cubic + quartic + higher residues.** Charon 1 used only Jacobi-symbol QR. Adding cubic-residue (mod p) and quartic-residue (mod p²) tests for primes in (n, 2n] should rule out exponentially more candidates per n, accelerating empirical verification. Implementation: PARI/GP one-liners; total compute cost negligible.
2. **Expanded sieve window: (n, n^1.5] instead of (n, 2n].** The (n, 2n] window gives π(2n) − π(n) ≈ n / log n primes. Expanding to (n, n^1.5] gives ~3× more primes (still ≤ ~10n / log n primes), substantially more sieve power. Each prime's "miss rate" is ~1/2, so ruling-out probability scales as 1 − 2^(−prime-count). **Strict density-of-non-Brocard-n improvement.** No new mathematics, just better engineering.
3. **Factorization-pattern mining of n!+1.** For n ≤ 100, compute the full prime factorization of n!+1 and analyze: largest prime factor, number of distinct prime factors, Liouville-function value λ(n!+1), Stormer-style smoothness statistics. **Question:** is there a pattern in the prime structure of n!+1 that predicts when it could be a perfect square (i.e., all prime factor exponents even)? The known cases (n = 4, 5, 7) might cluster in some statistic. Tool: Python + factor() in Sage / sympy. Cost: <1 day of compute (n!+1 for n=100 is ~158 digits — manageable).
4. **Wieferich / Wall–Sun–Sun connection at Wilson primes.** Charon 1 noted that for n+1 = p prime, n!+1 = m² implies p|m. The structure for *Wieferich primes* (p | 2^(p-1) − 1) and *Wall–Sun–Sun primes* (p² | F_(p−ε)) might give extra divisibility constraints. Compute: for known Wieferich and WSS primes, check if any n = p−1 satisfies the QR and Wilson conditions simultaneously. Probably no unknown solutions, but the absence is substrate-grade.
5. **Modular-form connection.** Speculative. n! + 1 = m² is a Diophantine equation with one parameter (n) and one unknown (m). The equation defines a curve over ℤ; its arithmetic might connect to a specific modular form via the modularity theorem analog. **Not a published direction**; would need a class-field-theoretic researcher to evaluate.
6. **Verification range extension to 10¹¹ or 10¹².** Berndt–Galway 2000 reached 10⁹. With modern hardware (especially big-int factorization and parallel n! computation), reaching 10¹¹ is tractable in ~1 week. This wouldn't close the conjecture but would constrain it tightly and produce a publishable update.

**Datasets/tools:**

- **n!+1 factorization database**: for n = 1…100, the full prime factorization. ~100 rows; substrate-grade because factorization patterns of n!+1 are not in any standard reference.
- **Combined-residue sieve runtime**: a single GPU-accelerated implementation of QR + cubic + quartic + quintic residue tests for the Brocard-equation candidate filter.
- **Stormer-style smoothness analyzer**: for n!+1, what's the smoothness profile (largest prime factor as a function of n)?

**Verdict:** **YES — moderate value.** The combined-sieve and verification-extension are tractable in ~1 week and would yield a cleaner empirical landscape. The factorization-pattern analysis is the most likely to surface novel structure (factorization of n!+1 is non-trivially constrained because of the +1 shift; patterns may be illuminating). Probability of breakthrough: low. Probability of substrate-grade negative or partial pattern: high.

---

### 1.5 Pillai

**What Charon 1 did well:** identified the toolkit fragmentation (Mihăilescu for k=1, Bennett for consecutive bases, Baker ineffective for general); correctly noted abc would close it; surfaced the Stroeker–Tijdeman c₀(3,2) = 13 specific result.

**What's missing — round-2 angles:**

1. **Bennett-method extension: from (N+1, N) to (N+a, N) for small a.** Bennett's hypergeometric method depends on the consecutive-base structure for the Padé-approximant-style estimate. Loosening to small a may extend the method's reach. Question: is there a published extension of Bennett's exceptional-case list to (N+2, N) or (N+3, N)? If not, **constructing one would be publishable** and might cover additional Pillai-conjecture cases.
2. **Effective Baker–Matveev computation on specific (k, p, q) cases.** The Matveev 2000 explicit linear forms in logs gives effective bounds with reasonable constants. For each fixed (k, p, q) Pillai equation, the Matveev bound gives a finite (often computable) upper bound on (x, y). Running this for the smallest few (k, p, q) cases would be a concrete substrate-grade result: "for k = 2, x³ − y² = 2, all solutions have max(x, y) ≤ M for explicit M ≈ 10^200." Once the bound is in computable range (typically 10^50 to 10^200), targeted verification finishes the case.
3. **LMFDB Mordell-curve mirror.** LMFDB has tables of Mordell curves x³ − y² = k with their rank, generators, and integer solutions. **For all k ≤ 10⁵**, Pillai-conjecture-relevant integer solutions are accessible. Build a mirror filtered for the Pillai signature; queryable database. ~1 day of work.
4. **Polynomial Pillai analog (arXiv:2201.10964) — what transfers?** The polynomial case has a cleaner proof structure. Specifically, the polynomial-Pillai proof uses the *Mason–Stothers theorem* (the polynomial analog of abc, which IS proven). The proof structure may suggest an integer analog where weak abc is enough. **Not investigated by Charon 1.** Worth a literature pass.
5. **Cyclotomic generalization of Mihăilescu's argument.** Mihăilescu's class-field arguments for k=1 used the structure of ℤ[ζ_p, ζ_q]. For each fixed k, the analog ℤ[ζ_p, ζ_q] / (k) has a specific class-number / regulator profile. **Speculative:** is there a way to combine class-field arithmetic for multiple k values into a unified argument? This would be deep number theory, not a session.
6. **Pillai for *exponential* equations rather than polynomial.** Charon 1's literature mentioned Pillai's original 1945 paper concerning 2^x − 3^y. The equation a^x − b^y = c (exponential, fixed a, b) is the *original* Pillai problem. It is proven by Pillai (in his 1945 paper) for many fixed (a, b, c), with explicit bounds. Modern refinements (Bennett, Leveque) tighten these bounds. **Worth surveying** as a related-but-distinct conjecture; the techniques might cross-fertilize.

**Datasets/tools:**

- **Pillai solution census**: comprehensive table of (x, y, p, q, k) with x, y < 10⁶ and p, q ≤ 7. Charon 1 had ~10 rows; a comprehensive census is ~10⁵ rows. Queryable. Substrate-grade because no published exhaustive census exists for the small-base regime.
- **Bennett exceptional-list extender**: GPU-accelerated search for additional (N, c) with multiple solutions, parametrized by the (N+a, N) family. Output: extended exceptional list.
- **Mordell-curve / Pillai bridge**: a queryable mirror of LMFDB Mordell-curve data, filtered for Pillai relevance.

**Verdict:** **YES — moderate value.** The Bennett-extension and Mordell-curve mirror are concrete and tractable. Probability of substrate-grade contribution: high. Probability of breakthrough on the conjecture: low (still abc-bound).

---

## §2. Cross-cutting tools and datasets

These are tools that would benefit multiple problems in Charon 1's batch (and other batches).

### B.1. Parity-barrier signature database

**What it is:** for every conjectured set S in the analytic-number-theory literature, automated computation of:
- The sieve's parity-loss factor (typically a factor of 2)
- Whether S has been parity-broken (Friedlander–Iwaniec, Heath-Brown extensions, post-2010 Maynard / Tao work)
- The current best lower-bound technique
- Citations and method-status timestamps

**Why it matters:** Twin Prime, binary Goldbach, Chen's theorem, and many other conjectures share the parity barrier. Cataloguing the barrier across problems gives a unified attack surface — any technique that breaks parity for S₁ likely transfers to S₂ if both have the same barrier shape. Charon 1 noted this for Twin Prime + Goldbach; the database would systematize the cross-problem signal.

**Cost:** ~2 weeks of literature scanning + database construction. Mostly Aporia + Charon work.

**Output:** queryable SQLite or JSON. Maintained as substrate corpus.

### B.2. abc-conditional reduction registry

**What it is:** for every conjecture conjectured-or-proven-conditional-on-abc, the explicit reduction (which form of abc, what exponent, what dependency on other unproven hypotheses).

**Why it matters:** Brocard and Pillai both have abc-conditional finiteness. So do many other Diophantine conjectures (Catalan-like, Fermat-like, Mordell-like). A registry would let downstream investigators attack abc-conditional conjectures as a class — and characterize which would survive or fail under different proposed abc replacements.

**Cost:** ~1 week. Mostly literature work; lightweight tooling.

**Output:** structured JSON registry; eventually a scoring system for "abc-distance" (how strong an abc-input is needed for the conditional to apply).

### B.3. Diophantine surface component database (Sage/Magma backend)

**What it is:** for each named Diophantine equation in the substrate's purview (Erdős–Straus, Brocard, Pillai, Catalan, others), the surface defined by the equation, with:
- Computed rational components (Sage-verified)
- Known parametric families
- "Unaccounted-for cohomology" (sum of components NOT covered by known parametric families)
- Mordell-curve / elliptic-curve associated to specializations

**Why it matters:** Erdős–Straus's six trouble residues are a special case of "rational components not yet found." Pillai's open k cases are similar. A unified database would let us recognize when a Diophantine equation is "surface-classified" vs. "surface-unknown" — and prioritize the unknown ones.

**Cost:** ~2–4 weeks. Significant Sage / Magma work; non-trivial to build but very high value once built.

**Output:** queryable database with rational-point density estimates per residue class.

### B.4. Heuristic-vs-actual deviation tracker

**What it is:** for each conjecture with a heuristic prediction (Hardy–Littlewood for Twin Prime, Goldbach, etc.), a database of empirical-vs-heuristic deviations across n.

**Why it matters:** Charon 1 noted the HL ratio drift (~1.18 at 10⁶ for Twin Prime; ~0.63 at 5000 for Goldbach). The *shape* of these deviations (logarithmic correction terms, oscillatory components) is itself substrate-grade information that's currently scattered across many papers.

**Cost:** ~1 week. Compute-heavy but tractable.

**Output:** time-series of empirical vs. heuristic ratios, with fitted correction terms.

### B.5. Cross-conjecture obstruction graph

**What it is:** a graph database where:
- Nodes are obstructions (parity barrier, abc-dependency, Whitney trick failure, instrument-vanishes-on-target, etc.)
- Edges connect problems to the obstructions they face
- Edge weights are "load-bearing-ness" of the obstruction for that problem

**Why it matters:** the substrate's cross-problem patterns (e.g., parity barrier blocks Twin Prime + Goldbach + Chen; abc-dependency blocks Brocard + Pillai + many) become legible at a glance. Drives where to invest cross-problem effort. **This is the most substrate-grade of the cross-cutting tools.**

**Cost:** ~1 week to build the schema + populate from existing attempt files.

**Output:** queryable graph (Neo4j / SQLite-with-edges); visualizations.

---

## §3. Strategic recommendations

### Priority order for round-2 work

1. **Erdős–Straus solution-pattern mining at scale** (~1 week of compute + 1 session). Highest ratio of substrate-grade-output to effort. Concrete deliverable: trouble-residue solution database + symbolic-regression-driven parametric family hunt.

2. **Build the parity-barrier signature database** (§B.1, ~2 weeks). Cross-cuts Twin Prime, Goldbach, Chen, and many others. Substrate-grade contribution that benefits multiple future investigations.

3. **Build the cross-conjecture obstruction graph** (§B.5, ~1 week). Makes the cross-problem patterns Charon 1 noticed durable and reusable.

4. **Brocard combined-sieve + factorization-pattern analysis** (~3 days). Moderate value, low cost, near-term substrate contribution.

5. **Pillai LMFDB Mordell-curve mirror + Bennett extension** (~1 week). Moderate value, infrastructure-building.

6. **Twin Prime / Goldbach standalone deep dives** — **DO NOT.** These are barrier-bound problems; round-2 effort produces literature ornamentation, not substrate movement. Substrate value here is in the cross-cutting tools (parity-barrier database) which benefit many problems.

### What Charon 1 did right that round 2 should preserve

- **Calibrated-negative discipline.** Every attack surface that fails should produce a documented obstruction class. Round 2 should preserve this rather than degrading into computational-confirmation-only.
- **Parity-barrier-as-shared-obstruction.** Charon 1 noted Twin Prime + Goldbach share parity. Round 2 should *act* on this signal by treating them as joint problems, not as separate deep dives.
- **Real citations.** Charon 1 was disciplined about not inventing citations and explicitly flagged "no canonical source identified" where uncertain. Round 2 must preserve this.

### What Charon 1 missed that round 2 should fix

- **Computational sampling at scale.** Charon 1's empirical work was tiny: 5 primes for Erdős–Straus trouble residues, n ∈ [8, 29] for Brocard QR sieve, x, y < 300 for Pillai. **Modern hardware permits 4–6 orders of magnitude more sampling.** Round 2 should lean hard into computational scale — the substrate-grade kill data is sharper at scale.
- **Pattern mining over solution coordinates.** Charon 1 reported solutions but did not mine them. Symbolic regression on (x, y, z) for Erdős–Straus or on factorizations of n!+1 for Brocard is cheap and may surface novel structure that pure literature scanning cannot.
- **Cross-pollinate to cross-cutting tools.** Charon 1 wrote 5 problem-specific files and a summary noting cross-problem patterns. The natural next step is building the cross-cutting tools that operationalize those patterns. The summary noted the parity-barrier shared structure but did not propose a unifying tool. Round 2 should.

### What round 2 should NOT do

- **Don't try to prove Twin Prime / Goldbach.** These are not closable in a session. Effort spent here is wasted.
- **Don't redo the literature surveys.** Charon 1's literature work is solid; redoing it adds nothing.
- **Don't generate "novel" parametric families for Erdős–Straus by guessing.** The hunt should be data-driven (symbolic regression on real solution data) not speculation-driven.
- **Don't propose new conjectures unless data supports.** The substrate values calibrated negatives over speculative positive claims.

---

## §4. Concrete actionable next steps

If Aporia / James / future-Charon assigns round-2 work, the **single most productive 1-week investment** is:

> **Erdős–Straus trouble-residue solution mining.** Build the database (10⁶ primes × 6 trouble residues × full (x, y, z) solution). Run dimensionality-reduction + symbolic regression. Produce one of (a) a candidate parametric family for one residue class [breakthrough], (b) calibrated negative with publishable statistics on solution-size scaling [substrate-grade]. Time cap: 1 week. Compute cost: trivial (modest GPU).

If a 2-week investment is permitted, add:

> **Build the parity-barrier signature database (§B.1).** Operationalizes Charon 1's cross-problem observation. Substrate-grade benefit across many future investigations.

If 4 weeks are permitted, add:

> **Cross-conjecture obstruction graph (§B.5).** This is the meta-tool that makes Charon-class batch outputs structurally legible. Without it, each batch's cross-problem signal is informally noted but not durable.

The lower-priority items (Brocard combined-sieve, Pillai Mordell-curve mirror, Bennett-extension) are nice-to-have but not the highest-leverage round-2 work. They can be done by a less-experienced researcher or a less-bandwidth session.

---

## §5. Calibrated negatives on this review itself

- **I am not an expert in the specific subfields.** Charon 1's literature scan is more authoritative than my proposed extensions in any individual problem. My value-add is the cross-problem perspective, not deeper subject expertise.
- **The "round 2 priority order" reflects my judgment of substrate-value-per-effort, not absolute mathematical importance.** Twin Prime and Goldbach are obviously more famous than Erdős–Straus; the recommendation against round-2 on them is a *substrate-economics* argument, not a *mathematical-importance* argument.
- **The cross-cutting tools (parity-barrier database, abc registry, obstruction graph) are infrastructure investments.** Their value depends on the substrate continuing to do batch-style number-theory investigations. If Aporia pivots away from this kind of work, the tools' marginal value drops.
- **I have not verified that my proposed new parametric family targets for Erdős–Straus are actually unsolved.** A more careful literature pass might reveal that some of the "trouble residue" attacks I propose have already been done. Round-2 work should start with a literature recheck on each specific angle before committing compute.

---

— Charon 3, 2026-05-05
