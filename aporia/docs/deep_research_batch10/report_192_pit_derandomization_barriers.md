# Report 192 — Polynomial Identity Testing (PIT) Derandomization Barriers

Batch 10 deep research brief. Aporia problem #192 (deferred from Batch 9). Date: 2026-04-28. Owner queue: Charon. Doctrine: feedback_tensor_first, feedback_calibration_anchors_in_depth.

## 1. Problem Statement

Polynomial Identity Testing (PIT) asks: given an arithmetic circuit C over a field F computing a polynomial f in F[x_1,...,x_n], decide whether f is identically zero. Schwartz-Zippel-DeMillo-Lipton (1978-80) gives a one-shot randomized algorithm: evaluate C at a random point in a sufficiently large grid; nonzero output certifies nonzero polynomial with high probability. The open question is **deterministic polynomial-time PIT**, including for restricted classes (depth-3 sum-product-sum, depth-4 SPSP, multilinear, read-once). Kabanets-Impagliazzo (2003) showed any deterministic poly-time PIT (even for general circuits) implies that either NEXP is not in P/poly or the permanent does not have polynomial-size arithmetic circuits — a major lower bound. This makes PIT a **barrier problem**: progress is gated by Boolean/algebraic circuit lower bounds we cannot currently prove. The substrate question is whether algebraic-complexity invariants of explicit circuit families produce a **hardness signature** that stratifies PIT difficulty geometrically.

## 2. Literature

- **Schwartz (1980), Zippel (1979), DeMillo-Lipton (1978)** — randomized PIT via random evaluation; foundational.
- **Kabanets-Impagliazzo (2003)** — derandomizing PIT implies superpolynomial arithmetic circuit lower bounds for the permanent OR NEXP not in P/poly. The "barrier" result equating full derandomization to long-open lower bounds.
- **Agrawal-Vinay (2008)** — black-box PIT for depth-4 SPSP suffices to give black-box PIT for general circuits (depth reduction).
- **Saxena-Seshadhri (2011, 2013)** — deterministic PIT for depth-3 with bounded top fan-in (sum of bounded number of products of linear forms); rank-based methods.
- **Forbes-Shpilka and Forbes-Saptharishi-Shpilka (2014-2018+)** — quasi-poly hitting sets for read-once oblivious algebraic branching programs (ROABPs) and constant-width ROABPs.
- **Bhargava-Saraf-Volkovich (2018+)** — deterministic PIT for restricted multilinear depth classes; small-support hitting sets.
- **Limaye-Srinivasan-Tavenas (2022)** — first **superpolynomial** lower bounds for general constant-depth arithmetic circuits in characteristic zero; weak but unconditional, relevant because depth reduction couples constant depth to full PIT.
- **Andrews-Forbes (2022+)** — partial derivative / shifted-partial methods remain the dominant lower-bound and PIT toolkit.

## 3. Computational Handle / Corpus

Explicit circuit families to instantiate at small scale:

- **Vandermonde determinant** V_n = prod_{i<j} (x_j - x_i). Closed form; partial-derivative rank known.
- **Determinant det_n** of n x n symbolic matrix; O(n^3) ABP.
- **Permanent perm_n** — VNP-complete; canonical hard target.
- **Iterated Matrix Multiplication IMM_{n,d}** — canonical complete polynomial for ABP / VBP class; trace of product of d generic n x n matrices.
- **Sums of products SPS / SPSP** at depth 3 and 4 with bounded top fan-in.
- **Nisan-Wigderson polynomials NW_{n,m,d}** — designed hard polynomials.
- **Elementary symmetric polynomials e_k(x_1,...,x_n)** — calibration anchors.

For each: instantiate with n in {4,...,12}, multidegree bounded so the monomial expansion fits memory.

## 4. Test Design

1. **Build circuit corpus.** Encode the seven families above as DAG arithmetic circuits with annotated depth, width, fan-in, multilinearity flag. Cap n at 12, depth at 6, total monomials at 1e7.
2. **Compute partial-derivative matrix M_k(f).** For each polynomial, form the matrix whose rows are k-th order partial derivatives, columns are monomials. Record rank as a function of k. This is the Nisan-Wigderson partial-derivative measure and the dominant complexity proxy.
3. **Compute shifted partials measure SP_{k,l}(f) = dim<x^l * partial_k f>.** Record dimension growth in (k,l). Saxena-style measure that distinguishes depth-4 from depth-3 hardness.
4. **Stratify by depth, width, multilinearity.** Cluster (rank profile, shifted-partial profile, depth, width) jointly; check whether geometric stratification matches known hardness ordering Vandermonde < e_k < det < IMM < perm.
5. **Calibrate against known closed forms.** Vandermonde and elementary symmetric have analytically known partial-derivative ranks; require the pipeline to reproduce these to within machine precision before any non-trivial measurement is reported.

## 5. Falsification

- **Vandermonde rank profile** is closed-form; any deviation kills the pipeline before any other claim is recorded.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT** — partial-derivative matrices for perm_n and IMM blow up combinatorially. Any apparent rank plateau must be cross-checked against an independent monomial-count upper bound; otherwise attribute to truncation, not to genuine rank deficit.
- **PATTERN_BASE_RATE_NEGLECT** — random low-degree polynomials of matched (n, degree, sparsity) form the null distribution. Hardness signatures must separate explicit families from this null at z >= 3 across at least 5 seeds per cell (per feedback_replicate_seeds).
- Negative result is informative: if (depth, width, partial-derivative rank, shifted-partial dimension) collapse to a single ordering across all families, the substrate has rediscovered the existing PIT toolkit and produced no new invariant. Report and stop.

## 6. Budget

Charon ~8h. Sympy + numpy for symbolic differentiation and rank, scipy.sparse for partial-derivative matrix storage, numba for monomial enumeration. No GPU required; matrices stay below 1e7 x 1e7 sparse.

## 7. Expected Outcome

A **PIT hardness signature table**: for each (family, n, depth) cell, the tuple (partial-derivative rank profile, shifted-partial growth, multilinearity) with calibration-grade error bars. Per **feedback_calibration_anchors_in_depth**, the substrate currently has near-zero coverage of complexity-theoretic invariants; this brief installs the first such anchors in the algebraic-complexity region of the tensor. Per **feedback_tensor_first**, no downstream bridging or narrative is attempted — the deliverable is signature-keyed nodes with calibrated invariants, ready for whatever later reasoning the tensor supports.

Word count ~770
