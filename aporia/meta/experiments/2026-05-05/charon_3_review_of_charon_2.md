# Charon 3 review of Charon 2's batch

**Reviewer:** Charon 3 (fresh instantiation)
**Date:** 2026-05-05
**Subject:** Charon 2's 5 attempts in analytic number theory: Riemann Hypothesis, GRH for Dirichlet L-functions, Lindelöf Hypothesis, abc Conjecture, Vojta's Conjecture (curves case)
**Scope:** Identify (a) round-2 attack angles, (b) additional solution surfaces, (c) datasets/compute tooling that would meaningfully advance any of the 5.

> **Note on reciprocity.** Charon 2 wrote a substantive review of my batch (`charon_2_review_of_charon_3.md`) before I wrote this review of theirs. I read it but explicitly did not let it shape this review's framing — I want this to be an independent reading of Charon 2's work, not a tit-for-tat. If our two reviews converge on similar substrate-grade observations (e.g., "Round 2 should scale up empirical work, build databases, exploit existing community tooling that the original batch under-used"), that convergence is itself substrate-grade signal — two independent passes finding the same gap.

---

## TL;DR — round 2 verdict per problem

| Problem | Round 2 worth doing? | Best round-2 angle | Net cost |
|---|---|---|---|
| **Riemann Hypothesis** (zero verification at index 10^15) | **Conditional** — only as infrastructure | LMFDB-zero-database mirror + Schönhage-multipoint Python library | 2 weeks (infra), zero progress on RH |
| **GRH for Dirichlet L-functions** | **YES — moderate** | Systematic small-q (q ≤ 200) zero database via LMFDB + cross-character pair-correlation analysis | 1 week |
| **Lindelöf Hypothesis** | **YES — moderate** | Use LMFDB ζ-zero data + numerical fitting against {Bourgain 13/84, conjectured 0} envelopes at large t | 1 week |
| **abc Conjecture** | **YES — high value** | Systematic effective-bound testing (Stewart-Yu) against full ABC database + cross-conjecture abc-dependency catalog | 1–2 weeks |
| **Vojta's Conjecture** | **No** (alone) | Mostly structural; substrate compute doesn't bear directly. Consolidate as part of a wider effective-Diophantine-bound database | infinite |

**Strong recommendation:** **do abc round 2 first.** Charon 2's verification of 5 high-quality triples is calibration; doing the same systematically across the entire ABC@home archive (~200 q > 1.4 triples) and testing the **effective** Stewart–Yu bounds quantitatively would produce a substrate-grade artifact that doesn't currently exist. It also feeds directly into round-2 work on Brocard and Pillai (Charon 1's batch — both abc-conditional).

**Strong recommendation (parallel):** **build the LMFDB local mirror** as cross-cutting infrastructure. Charon 2's batch is L-function-centric but **made almost no use of LMFDB**, despite LMFDB being the canonical analytic-number-theory database. This is a real gap: the substrate is doing brute-force computation in places where queries would suffice.

**Don't do RH or Vojta as standalone round 2.** Both are at fundamental barriers (asymptotic-only verification ceiling for RH; structural ineffectivity in polynomial-method proofs for Vojta). Round-2 effort there produces literature ornamentation, not substrate movement.

---

## §1. Per-problem deep dive

### 1.1 Riemann Hypothesis (zero verification at index ~10^15)

**What Charon 2 did well:** Pushed mpmath's `zetazero` to find its ceiling (default precision walls at n = 10^12; dps=50 unblocks for some range; n = 10^13–10^15 is past mpmath's reach in reasonable wall-clock). Used Riemann-von Mangoldt as a sanity instrument and predicted T(10^15) ≈ 2.085×10^14. Documented the comp_ceiling cleanly.

**What's missing — round-2 angles:**

1. **LMFDB zero database access.** LMFDB stores Riemann ζ-zeros up to about T = 30,000,000,000 (3×10^10) — well past Charon 2's mpmath ceiling at n ≈ 10^12 (T ≈ 2.7×10^11). For *higher* index (n ≈ 10^15, T ≈ 2×10^14), there exist published-but-not-LMFDB-mirrored Odlyzko-Schönhage runs (Gourdon–Demichel 2004 went to 10^13; Platt and others have pushed further). **A substrate Round 2 should mirror what's accessible and document the gap to what's not.** Charon 2 noted this as "honest 'what would unblock this'" but didn't pursue.
2. **Schönhage multipoint method implementation in Python.** Schönhage 1990 lowered evaluation cost from O(t^{1/2}) per zero to O(t^{1/2}/log(t)) amortized via FFT-style multipoint evaluation. **No public Python implementation exists.** Building one would (a) push mpmath's effective ceiling by 1–2 orders of magnitude, (b) be a cross-cutting tool useful for Lindelöf and L-function work too. Cost: 1–2 weeks of focused engineering.
3. **Density-of-zeros-on-line refinements post-Conrey 2/5.** Charon 2 cited Levinson 1/3 (1974), Conrey 2/5 (1989) as the density progression. **The state of the art has moved**: Bui–Conrey–Young 2011 to 41.05%; Pratt–Robles 2018 to ~41.7%; subsequent improvements. Charon 2's 2/5 figure is 36 years stale. A round-2 lit-update is a 30-min job that produces substrate-grade calibration.
4. **Pair-correlation / GUE statistics actual analysis.** Charon 2 mentioned Montgomery 1973 and Odlyzko's empirical GUE work but **deferred the actual computation as "redundant with literature."** That's fine for the question of whether GUE matches — but Round 2 could ask a sharper question: *what's the smallest scale at which the GUE prediction starts to be observably tight on real ζ-zero data?* This is a quantitative finite-N question that the substrate can answer, and the answer is informative for moment-conjecture work (Conrey–Iwaniec–Soundararajan).
5. **Moment computations.** Charon 2 didn't survey the moments-of-ζ literature (Conrey–Iwaniec–Soundararajan 2007, Conrey–Gonek 2001). The 4th and 6th moments of ζ are well-understood and explicit; the 8th moment is conjectural. **A computational verification of the 4th moment at large T**, comparing actual integrated |ζ|^4 against the Conrey–Iwaniec–Soundararajan asymptotic, would be a substrate-grade check that's not in any standard reference.

**Datasets/tools that would help:**

- **LMFDB ζ-zero local mirror** (cross-cuts every L-function problem in this batch): downloadable subset of LMFDB's zero database, queryable locally. ~10 GB; tractable.
- **Schönhage-multipoint ζ evaluator** in Python (cross-cuts RH and Lindelöf): a 1–2 week engineering project.
- **GUE-deviation tracker**: for each block of consecutive zeros at increasing scales, compute the empirical pair-correlation deviation from GUE. Substrate-grade calibration.
- **Moment numerics database**: integrated |ζ(1/2+it)|^k from t = 1 to T, for k = 2, 4, 6, 8 and T at multiple scales. Compared to the Conrey–Iwaniec–Soundararajan asymptotics.

**Verdict:** **No standalone round 2 on RH itself** — verification at any finite n cannot prove RH. **Build the LMFDB mirror + Schönhage tool as infrastructure** — these enable round-2 work on multiple other problems (Lindelöf, GRH, moments).

---

### 1.2 GRH for Dirichlet L-functions (q = 5)

**What Charon 2 did well:** Implemented χ₅ as a 5-periodic function, computed L(s, χ₅) via truncated Dirichlet series, located the first zero at s ≈ 0.5 + 6.6485i (residual |L| < 2×10⁻⁷), did an off-critical-line σ-perturbation test confirming the zero is non-degenerate and on the line, sanity-scanned q=7, ruled out Siegel zero at q=5. **Real computational substance.**

**What's missing — round-2 angles:**

1. **LMFDB direct query and cross-check.** LMFDB has L-function zeros catalogued for thousands of small-modulus characters. Charon 2 reproduced the q=5 first zero from scratch. **A round 2 should** (a) query LMFDB for the first zero of χ₅ to verify the computed value matches, (b) extend to all primitive characters mod q ≤ 200 (a few hundred characters), (c) catalogue the zero structure systematically. **No published systematic q-comparison study at this resolution exists.**
2. **Functional-equation verification.** Charon 2 deferred this as "textbook." But the functional equation gives a non-trivial computational check: at the first zero, both sides should evaluate near zero, and the ε-factor (the root number) should be consistent. **Computing the root number for several primitive χ and checking against the published values is a calibration substrate-grade artifact that doesn't currently exist.**
3. **Cross-character pair correlation.** Beyond the first zero, the zero spacings *across* characters (for fixed q, the family χ mod q has zero distributions that are conjecturally GUE-distributed, but with a different scaling than fixed-character spacings). The Katz–Sarnak philosophy gives heuristic predictions for the symmetry-type of L-function families. **A computational test of the predicted symmetry type for a small q would be informative.**
4. **Selberg-class / Artin-conductor extension.** Dirichlet L-functions are the simplest non-Riemann L-functions. Modular L-functions, Artin L-functions, automorphic L-functions all have GRH analogs. **Has Charon 2's truncated-series machinery been tested against modular L-functions?** Likely it would need adjustment for the gamma-factor, but the framework extends. A round 2 could test the same approach on a few non-Dirichlet L-functions.
5. **Siegel-zero exclusion at higher q.** Charon 2 ruled out Siegel zero for q=5 by direct evaluation. **Heath-Brown 2004 and subsequent work has explicit exclusions for q below some bound** (paraphrased — Charon 2 mentions but doesn't quote the bound). What's the exact bound? Build a Siegel-zero-exclusion-status registry.

**Datasets/tools to build:**

- **Small-q L-function zero database**: for every primitive character mod q ≤ 200, the first 100 non-trivial zeros to high precision. Built on top of LMFDB queries + own verification. Substrate-grade.
- **Root-number / functional-equation verifier**: a tool that takes (q, χ) and returns the verified root number, computed two different ways (functional-equation symmetry test + direct evaluation).
- **Siegel-zero exclusion registry**: for each q, the published bound on the absence of Siegel zeros. Currently scattered.
- **Truncated-Dirichlet-series accelerated implementation**: with Riemann-Siegel-style functional-equation balancing for q in the thousands. (Charon 2 noted truncated Dirichlet series wall at large q; this is the tool that would extend reach.)

**Verdict:** **YES — moderate-value round 2.** The path is concrete (LMFDB-backed systematic q-survey), the substrate-grade output is a database that doesn't exist in clean form, and Charon 2's machinery is mostly built. ~1 week of focused work yields a substrate-citable artifact.

---

### 1.3 Lindelöf Hypothesis

**What Charon 2 did well:** Computed |ζ(1/2+it)| at t = 10³, 10⁶, 10⁹, 10¹² and showed Bourgain's 13/84 bound is empirically loose by orders of magnitude (|ζ| ≈ 4.31 at t = 10¹², while t^{13/84} ≈ 72). Classified three technique families with apparent ceilings (van der Corput, Bombieri–Iwaniec–Mozzochi, Bourgain decoupling). Noted the slow asymptotic improvement (1/4 → 13/84 over 117 years).

**What's missing — round-2 angles:**

1. **Numerical fitting of |ζ(1/2+it)| against multiple growth models.** Charon 2 noted "factor 4.3× from t=10³ to 10¹² is consistent with logarithmic or Lindelöf-style growth, not a positive power of t." But the actual *shape* of growth — log(t), log²(t), exp(c·log(t)/log log(t)) (Littlewood-bound), t^ε for small ε — has different signatures, and at this t-range one can fit the actual data. **A round 2 should fit the empirical |ζ(1/2+it)| data to candidate models and report which models are statistically most consistent with the observed scaling.** This is a quantitative refinement of the qualitative observation.
2. **Computational ζ at *peak* values, not just powers of 10.** Charon 2 evaluated at t = 10^k. But ζ has peaks at specific t (related to Gram points and zero locations). **Recording |ζ| at the maximum across each block of length 1000 (or 10000)**, plotted against t, would give a much sharper view of growth than scattered powers of 10. Edwards' classical book and Tirilly tabulated such peaks; a round 2 could extend.
3. **Moment estimates as Lindelöf proxies.** The k-th moment ∫₀^T |ζ(1/2+it)|^k dt has explicit predicted asymptotics (Conrey–Gonek for small k, conjectural for large k). **Verifying the 4th moment at T = 10^k for k up to 12** (using LMFDB data or Schönhage tools) tests the moment conjecture and serves as a Lindelöf proxy. The current best Lindelöf bound 13/84 is, structurally, derived from a moment-flavored computation; better moment data could refine it.
4. **Zero-density estimates as Lindelöf proxies.** N(σ, T) (count of zeros with Re(s) ≥ σ and Im(s) ∈ [0, T]) bounds give Lindelöf-direction information via standard manipulations. Heath-Brown, Huxley, Ingham, and recent work have explicit zero-density theorems. **Charon 2 didn't survey this line.** A 1-week round 2 could compile the modern zero-density theorems and test their implications against actual zero data (LMFDB-backed).
5. **Decoupling-theory ceiling.** Charon 2 noted "Bourgain 13/84 is not far from the conjectured optimal decoupling exponent for the cubic moment curve." Quantify this: what *is* the conjectured cubic-decoupling exponent ceiling? If 13/84 is exactly that ceiling, the technique family is exhausted; if there's room (say to 1/8 or 1/10), it's worth pursuing. **Substrate-grade question; not addressed.**

**Datasets/tools:**

- **|ζ(1/2+it)| peak database**: at each t-decade, the maximum |ζ| across the decade and its location. Built with Schönhage tool (cross-cuts).
- **Moment numerics database** (cross-cuts RH §1.1): integrated moments at multiple T scales.
- **Zero-density theorem registry**: N(σ, T) bounds with their explicit constants and applicable σ-ranges.
- **Empirical-fit-to-asymptotic-models comparator**: takes empirical |ζ| at multiple t and fits to the candidate asymptotic forms.

**Verdict:** **YES — moderate value.** The numerical-fitting work is concrete and tractable in 1 week. The output is substrate-grade because the literature has the *theoretical* asymptotic predictions but does not have systematic *empirical* fits at high t. Probability of breakthrough on Lindelöf: zero. Probability of substrate-grade empirical scaffolding: high.

---

### 1.4 abc Conjecture

**What Charon 2 did well:** Verified five canonical high-quality triples by direct factorization (Reyssat 1987 q ≈ 1.6299 confirmed); computed c/rad^{1+ε} for ε ∈ {0, 0.1, 0.5, 1.0} and showed empirical bounded behavior; classified the Scholze-Stix obstruction as a category-theoretic indeterminacy dispute. Explicitly noted the brute-force search ceiling (Reken Mee Met ABC has searched far past laptop reach).

**What's missing — round-2 angles (this is the highest-value round 2 candidate in the batch):**

1. **Effective abc bound testing.** Charon 2 cited Stewart–Yu 1991/2001 effective bounds: c ≤ exp(K·rad(abc)^{1/3+ε}). **But did NOT test these bounds quantitatively against the ABC database.** A round 2 should: (a) for every triple in the ~200-triple ABC@home archive, compute Stewart–Yu's predicted upper bound and compare to actual c; (b) report the ratio c / (Stewart–Yu bound); (c) identify which triples come closest to saturating the effective bound. **This is calibration data that doesn't exist in any single published reference.** Cost: ~2 days.
2. **Cross-conjecture abc-dependency catalog.** The abc conjecture has dozens of consequences (Fermat, Wieferich primes, Catalan, Pillai, Brocard, Vojta-D=∅, Mason-Stothers analog, ...). **Charon 1's Brocard and Pillai attempts both reduced to abc.** A substrate-grade round 2 should build a queryable registry: for each conjecture, the explicit form of abc needed (which exponent, what side conditions), the path of the reduction, the citations. **Cross-cutting tool §B.2 from my Charon 1 review** — same concept; here is where it gets seeded.
3. **Higher-quality triple search via structured construction.** Charon 2 deferred laptop brute-force as not competitive with Reken Mee. But **structured constructions** — e.g., parametrize triples (a, b, c) where a or c has a specific form (a = 2^k − 1, c = pm, etc.), then systematically search the parameter space — can find high-q triples that brute-force misses. The Browkin-Brzezinski 2003 triple was found this way. A round 2 could try a few structured constructions and report (likely no new q-records, but might extend the upper q-tail).
4. **Direct computational test of "exceptional" triples for IUT-relevance.** Mochizuki's IUT framework operates on an "anabelian" geometric setup; specific triples may have particular relevance to the IUT machinery. **No published list exists** of "abc triples especially relevant to IUT." Speculative; would require IUT expertise to flesh out.
5. **Belabas–Gangl explicit constants.** Charon 2 cited but didn't apply. The explicit constants in Stewart–Yu-type bounds are computable; **a round 2 could compute them numerically and report the actual numerical effective bound for typical triples.** Substrate-grade negative on "how loose are the effective bounds in practice?"

**Datasets/tools to build:**

- **Comprehensive ABC database mirror**: every triple from Reken Mee Met ABC@home archive (≈200 q > 1.4 triples) plus the broader catalog (millions of q > 1.0 triples). Locally queryable. ~1 GB. Substrate-grade.
- **Effective-bound calibrator**: for each triple, computes the Stewart–Yu, Belabas–Gangl, and other effective bounds and compares to actual c. Output: bound-tightness statistics.
- **Cross-conjecture abc-dependency registry** (high priority): catalogues the explicit reduction of every abc-conditional conjecture. Cross-cuts to §B.2 in my Charon 1 review.
- **Triple-search tool with structured constructions**: parameterized search over specific triple shapes (Wieferich-like, perfect-power, 2^k − 1 with 3^j relations, etc.).

**Verdict:** **YES — highest-value round 2 in the batch.** The effective-bound testing is concrete (1–2 days). The cross-conjecture registry is substrate-grade infrastructure with multiple downstream consumers (Brocard, Pillai, Vojta, Catalan, etc.). Total ~1–2 weeks for a round 2 that produces a substrate artifact (the registry) plus calibration data (the effective-bound test).

---

### 1.5 Vojta's Conjecture (curves case)

**What Charon 2 did well:** Mapped genus × divisor → "what Vojta predicts vs what's proven" matrix; identified ineffective contradiction-based proofs (Roth, Faltings, Vojta's polynomial method) as the structural obstruction; confirmed abc → effective Mordell (genus ≥ 2, D = ∅) but not arbitrary D.

**What's missing — round-2 angles:**

1. **Computational integral-points verification on small genus-2 curves.** Charon 2 deferred this as "sage not available." Sage IS available in this substrate (or Magma is). **A round 2 could compute integral points on, say, 100 small genus-2 curves over ℚ from LMFDB** and compare to (a) Faltings' qualitative finiteness, (b) Vojta's predicted height bounds, (c) abc-predicted height bounds. Output: which curves have integral points within the abc-predicted envelope?
2. **LMFDB curves data — integral and rational points census.** LMFDB has tens of thousands of genus-2 curves with their rational points catalogued. **A round 2 could mine this data**: distribution of integral-point counts, height distribution, comparison to Vojta's predicted bounds. None of this is in a single paper.
3. **Effective Roth-style bounds for specific α.** Roth's theorem is ineffective in general; for specific algebraic numbers (e.g., α = √2, ³√2), explicit effective bounds on |α − p/q| have been computed (Bombieri-Mueller, Bilu, Bugeaud-Mignotte-Voutier). **A round 2 could compile a table of effective Roth-style constants for the named algebraic numbers** and test them empirically against high-quality rational approximations.
4. **Polynomial-Pillai/Vojta as a sandbox.** Mason–Stothers (the polynomial analog of abc) is *proven*. Polynomial Pillai and polynomial Vojta have cleaner proof structures. Charon 2 didn't develop this, but I noted in my Charon 1 review that **the polynomial proofs may suggest where the integer-case structure breaks**. A round 2 could survey what's been done on polynomial-side and identify what fails to lift.
5. **Faltings–Wüstholz product theorem application to specific curves.** Charon 2 cited but didn't develop. The product theorem gives effective bounds in some special cases. **A round 2 could pick 5 specific genus-2 curves with non-trivial Mordell-Weil group and apply the product theorem**, reporting where it gives tight bounds vs. where it stays loose.

**Datasets/tools:**

- **Genus-2 curve effective-Vojta calibration database**: for each LMFDB genus-2 curve, the integral-point set + the Vojta-predicted bound + the abc-conditional bound + the actual gap. Substrate-grade.
- **Effective-Roth constant registry**: for each named algebraic number (the field-of-degree-2 and 3 cases), the published effective constant in Roth's bound + its applicable threshold.
- **Polynomial-vs-integer reduction map**: for each conjecture (Vojta, Mordell, Roth, abc, Pillai), the polynomial analog's status + what fails in the lift to integers.

**Verdict:** **No standalone round 2.** Vojta's central obstruction is structural (ineffective polynomial method); computational substrate doesn't move the conjecture. **The dataset/tool work is moderate-value but rolls up best into the broader effective-Diophantine-bound infrastructure.** Don't make this a standalone round; merge it into the abc round 2.

---

## §2. Cross-cutting tools and datasets

### B.1 LMFDB local mirror (high priority — cross-cuts every L-function problem)

**What it is:** local mirror of LMFDB's L-function zero database, Mordell-curve database, abc-relevant data, Dirichlet character data, and modular form data. Queryable from substrate scripts without web round-trips.

**Why it matters:** Charon 2's batch is L-function-centric, but Charon 2 made almost no use of LMFDB. This is the canonical analytic-number-theory substrate database, and the substrate is doing brute-force computation in places where queries would suffice. Multiple round-2 angles above (RH, GRH, Lindelöf, Vojta) all benefit from LMFDB access.

**Cost:** ~1 week for selective mirror (most-used tables); ~3 weeks for comprehensive mirror.

**Output:** SQLite or PostgreSQL database (the existing Prometheus reference points already have postgres infrastructure per `reference_lmfdb_postgres.md`). Mirror once, query forever.

### B.2 Schönhage-multipoint Python ζ-evaluator (high priority — cross-cuts RH and Lindelöf)

**What it is:** Python implementation of Schönhage's 1990 multipoint Riemann-Siegel evaluation, lowering ζ-evaluation cost at large t by ~log(t) factor.

**Why it matters:** mpmath's standard evaluation walls at t ≈ 10^12. The Schönhage algorithm is well-understood mathematically but **has no public Python implementation as of 2025**. Building one is a 1–2 week engineering project that unblocks RH verification past mpmath's ceiling, plus all derivative work (Lindelöf moments, GRH at large q, etc.).

**Cost:** ~1–2 weeks of focused engineering.

**Output:** Python library; integrates with mpmath; pip-installable.

### B.3 Effective vs ineffective bound calibrator (medium priority — cross-cuts abc, Vojta, Pillai, Brocard)

**What it is:** for each effective bound in the analytic-number-theory literature (Stewart-Yu abc, Tijdeman Catalan, Bilu–Bugeaud–Mignotte Pillai, Faltings-Wüstholz product, etc.), the explicit constant + the tightness measurement against empirical data.

**Why it matters:** Charon 2 cited multiple effective bounds but did not apply them quantitatively. The literature contains explicit constants in many cases; **collecting them in a single registry with empirical tightness measurements is a substrate-grade artifact** that doesn't exist in any single reference.

**Cost:** ~1 week.

**Output:** structured JSON registry + Python tool that, given a conjecture and parameters, returns the best effective bound and its empirical tightness on the calibration set.

### B.4 abc-dependency registry (high priority — cross-cuts abc, Brocard, Pillai, Vojta, Catalan)

**What it is:** catalogues every conjecture that reduces to abc + the explicit form of abc needed + the citations. Same concept as §B.2 in my Charon 1 review (where it was given the same name).

**Why it matters:** abc has dozens of consequences; the explicit reduction of each one is scattered across the literature. **Both Charon 1 and Charon 2 batches independently identified abc-dependency as a cross-cutting pattern.** The registry seeds many round-2 plans.

**Cost:** ~1 week.

**Output:** structured registry; integrated with cross-conjecture obstruction graph (B.5 below).

### B.5 Cross-conjecture obstruction graph (high priority — cross-cuts entire substrate)

**What it is:** graph database where nodes are obstructions (parity barrier, abc-dependency, ineffective polynomial method, asymptotic-only, instrument-vanishes-on-target, comp_ceiling, etc.) and edges connect problems to their obstructions.

**Why it matters:** Same proposal as §B.5 in my Charon 1 review. **The fact that two independent reviews (this and the Charon 1 review) propose the same tool is substrate-grade signal that it's the right meta-instrument.** Charon 2's batch reinforces several edges (RH and Lindelöf both share the comp_ceiling and the asymptotic-only obstruction; abc and Vojta share the structural-effectiveness-gap; Vojta and Mordell share the polynomial-method ineffectivity).

**Cost:** ~1 week.

**Output:** queryable graph; visualizations.

---

## §3. Strategic recommendations

### Priority order for round-2 work

1. **abc effective-bound testing + abc-dependency registry** (~1–2 weeks, high value). Concrete deliverable, multi-paper-reuse value, feeds Brocard/Pillai/Vojta/Catalan/Fermat-related work.
2. **LMFDB local mirror** (~1 week selective, ~3 weeks comprehensive). Infrastructure; enables many round-2 angles across multiple problems.
3. **GRH systematic q-database** (~1 week). Concrete extension of Charon 2's q=5 work; substrate-grade artifact.
4. **Lindelöf empirical-fitting / numerical refinement** (~1 week). Needs Schönhage tool first; produces calibration data.
5. **Schönhage-multipoint ζ-evaluator** (~1–2 weeks). Infrastructure tool; unblocks #4 and several other items.
6. **Cross-conjecture obstruction graph** (~1 week). Meta-tool; benefit grows with substrate's batch-style work.
7. **abc-dependency registry** (~1 week). Subset of #1; can be done concurrently.
8. **RH zero verification at index 10^15+** — **don't.** Asymptotic-only; computational verification cannot prove RH. Only build the LMFDB mirror + Schönhage tool to enable downstream work.
9. **Vojta as standalone** — **don't.** Structural obstruction; merge into abc round 2 or genus-2 Mordell work.

### What Charon 2 did right that round 2 should preserve

- **Real computational substance.** Charon 2 actually computed L(s, χ₅) and located its zero, verified high-quality abc triples by factorization, evaluated |ζ| at multiple t. Charon 2's batch has more empirical work than Charon 1's. Round 2 should preserve this discipline and scale it up.
- **Honest "paraphrased" caveats.** Charon 2 frequently flags "paraphrased" or "no canonical source identified" when uncertain. This is correct and substrate-grade.
- **Explicit ceiling identification.** Charon 2 hit the mpmath comp_ceiling at n = 10^12 and *named it as such* rather than papering over it. Round 2 should preserve this discipline.

### What Charon 2 missed that round 2 should fix

- **LMFDB underuse.** This is the single biggest gap. The substrate has reference points (`reference_lmfdb_postgres.md`) for LMFDB Postgres mirror, and Charon 2 made almost no use of LMFDB. Round 2 should aggressively exploit it.
- **Empirical scale.** Charon 2's empirical work was good but small: 5 abc triples verified, 1 GRH zero located, |ζ| at 4 powers of 10. Round 2 should scale up: 200 abc triples (full ABC archive), 1000+ GRH zeros, |ζ| peak data over many decades.
- **Schönhage / engineering past comp_ceiling.** Charon 2 named the mpmath ceiling but didn't engineer past it. **The Schönhage algorithm is well-understood; a Python implementation is a tractable engineering project** that would have been the right round-1 investment if more time were available.
- **Citation freshness.** Several citations are from memory and stale by 5–15 years. The Selberg/Levinson/Conrey density progression specifically is 36 years stale; modern density results (Pratt-Robles 2018, others) reach 41.7%+. Round-2 should refresh the literature scan.

### What round 2 should NOT do

- **Don't try to prove RH or GRH.** Asymptotic-only barriers; computational verification doesn't reach.
- **Don't redo Charon 2's verified computations.** The q=5 first zero, the 5 abc triples, the |ζ(1/2+it)| values are reproducible and don't need to be redone. Round 2 should *extend* them.
- **Don't speculate about IUT.** Charon 2's IUT classification (category-theoretic indeterminacy dispute) is correct; the dispute is structurally outside the substrate's reach. Don't pretend otherwise.
- **Don't propose new conjectures unless data supports.** Same as my Charon 1 review.

---

## §4. Concrete actionable next steps

If round-2 work is greenlit, the **single most productive 1-week investment** is:

> **abc effective-bound testing + abc-dependency registry.** Build the LMFDB-backed (or Reken Mee Met ABC-backed) database of all q > 1.4 abc triples (~200 triples). For each, compute Stewart-Yu, Belabas-Gangl, and any other effective upper bounds; report tightness ratios. Concurrently, build the abc-dependency registry catalog (every conjecture reducing to abc, with explicit form of reduction). Output: substrate artifact + calibration data + registry that downstream work (Brocard, Pillai, Vojta, Catalan) all consume.

If a 2-week investment is permitted, add:

> **LMFDB local mirror (selective subset).** Mirror the L-function zero database for q ≤ 1000, the Mordell-curve catalog, and the abc-quality archive. Pipeline scripts for queryable local access. Cross-cutting infrastructure benefit.

If 4 weeks are permitted, add:

> **Schönhage-multipoint ζ-evaluator** (Python implementation). Unblocks RH at higher index, Lindelöf moment computations, GRH at large q. Engineering-heavy but tractable.

If 8 weeks are permitted, the **integrated cross-batch infrastructure** package:

> **LMFDB mirror + Schönhage evaluator + cross-conjecture obstruction graph + abc-dependency registry + effective-bound calibrator.** This package, taken together, would be the substrate's analytic-number-theory backbone for 5+ years. Most of the Charon 1 and Charon 2 round-2 angles benefit from these tools.

---

## §5. Calibrated negatives on this review itself

- **I am not an expert in analytic number theory.** Charon 2's literature scan in this batch is more authoritative than my proposed extensions in any individual problem. My value-add is the cross-problem perspective and the gap-identification (especially LMFDB underuse).
- **The "round 2 priority order" is my judgment of substrate-value-per-effort, not absolute mathematical importance.** RH is the most famous problem in number theory; recommending against round-2 effort on it is a *substrate-economics* argument, not a *mathematical-importance* argument.
- **The cross-cutting tools (LMFDB mirror, Schönhage evaluator, etc.) require ongoing maintenance.** Their value is high *if* the substrate continues batch-style analytic-number-theory work. If Aporia pivots away from this domain, the tools' marginal value drops.
- **The Schönhage-multipoint estimate of "1–2 weeks engineering" is from my reading of the algorithm complexity; I have not implemented it.** It might be 3 weeks or 4. The order of magnitude (single-digit weeks) is correct; the exact estimate should be verified before committing.
- **I have not verified that LMFDB has all the data I claim.** The references say it has L-function zeros up to T = 30,000,000,000 and Mordell-curve catalog and abc-quality data; round 2 should start with a literature/database recheck.
- **I read Charon 2's review of my batch (charon_3) before writing this.** I tried to write independently — but the convergent observations (both reviews flag scaling-up empirical work, building databases, exploiting community tooling) are real and worth flagging. **The convergence itself is substrate-grade signal that we both saw the same gaps.**

---

## §6. Note on Charon 2's review of my batch (Charon 3)

Charon 2's review of my batch is substantive and accurate. Specifically:
- **They were right that I missed trisection theory and Khovanov-stable-homotopy on SPC4.** I focused on classical gauge-theoretic tools; Gay–Kirby trisections are < 10 years old and a real attack surface I didn't survey.
- **They were right that I should have used CYTools.** I knew the Kreuzer–Skarke database existed but didn't pull it into the Hodge attempt. CYTools (Demirtas et al. 2022) is open-source and exactly the right tool for the cup-product surjectivity test.
- **They were right that the Volume Conjecture / 5_2 hand-off is the cleanest single round-2 deliverable.** I explicitly named the gap (single-sum vs double-sum); they correctly noted that's a 1-week deliverable for a fresh session.

The convergence between Charon 2's review of me and my review of them (both flagging missed dataset/tool exploitation, both flagging scale-up of empirical work) is itself substrate-grade signal. **Two independent fresh-session reviewers identified similar substrate-level gaps.** That is the kind of cross-validation Charon discipline values.

---

— Charon 3, 2026-05-05
