# Report T#56 — Symmetric Tensor Rank NP-Hardness (Hillar–Lim Conjecture)

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §VII #56
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 1, fire-4)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_RANK_PARITY_LEAK, PATTERN_VRAM_TRUNCATION_ARTIFACT
**Tags:** P22 (polynomial method), P25 (pivotal negative result), P27 (slice rank / polynomial method on F_q), P29 (border apolarity); proposed candidate paradigm: Existential-Theory Reduction / Algebraic Universality (synthesis to renumber given T#1's P32 candidate collision)

---

## Brief summary

T#56 (Symmetric tensor rank NP-hardness, the Hillar–Lim conjecture) is the complexity-class lower bound that calibrates which substrate operations on tensors can be exact and which must be approximate, declined, or routed to a stable substitute. **Catalog status correction (substantive):** the catalog framing "current results are partial" is stale — Shitov 2016 (arXiv:1611.01559) **settled the Hillar–Lim symmetric-rank-over-ℚ NP-hardness conjecture**, also proving tensor rank over ℤ is undecidable; Schaefer–Štefankovič 2018 sharpened tensor rank to ∃ℚ-/∃ℝ-/∃ℂ-complete; Swernofsky 2018 added inapproximability; Shitov's 2025 *Pacific J. Math.* paper is the cleanest extant exposition. The substrate consequence is not "tensor rank is hard" (textbook-trivial) but a primitive-design directive: I propose `ComputationalComplexityCertificate` as a Tier-B sister primitive to `ConstructiveExistenceWitness`, plus a `ComplexityStratifier` decorator that every tensor-touching primitive must register.

## Flagged findings (priority for synthesis)

1. **STALE CATALOG ENTRY:** `tensor_open_problems_v1.md` line 486 says "current results are partial" for symmetric-rank NP-hardness over ℚ. Wrong as of late 2016 (Shitov), reinforced by 2018 (Schaefer–Štefankovič) and 2025 (Shitov PJM). The Hillar–Lim conjecture is **SETTLED**. Recommend editing the catalog. Genuinely open frontier: (a) ℚ-decidability (T#55, conditional on H10/ℚ); (b) sharp inapproximability factors for symmetric rank specifically; (c) parameterized complexity in r; (d) average-case / cryptographic-strength reductions; (e) whether symmetric rank is also ∃ℚ-complete.

2. **SUBSTRATE GAP (substantive):** No current primitive carries a complexity certificate. Every tensor-touching call implicitly assumes tractable computation. Proposed tickets `T-ST-T56-001`/-002/-003 register `ComputationalComplexityCertificate` and the mandatory `ComplexityStratifier` decorator.

3. **NEW PARADIGM CANDIDATE:** Existential-Theory Reduction / Algebraic Universality (Schaefer–Štefankovič machinery — tensor rank is polynomial-time equivalent to existential theory of the field). Distinct from P22 (spectral on signed graphs), P25 (pivotal negative result), and P29 (border apolarity). T#1 also flagged a P32 candidate (Evolutionary-LLM Algorithm Synthesis); the two candidates conflict numerically. Synthesis to assign Pn vs Pm.

4. **CANONICAL ATTRIBUTION RISK:** Popular-press writeups credit Hillar–Lim for everything in this neighborhood. Calibration anchor must spread credit: Håstad 1990 (original NP-completeness over finite fields), Hillar–Lim 2013 (J. ACM survey + symmetric NP-hardness conjecture), Shitov 2016/2025 (settles symmetric over ℚ; undecidability over ℤ), Schaefer–Štefankovič 2018 (∃-theory completeness), Swernofsky 2018 (inapproximability), Bhattiprolu–Ghosh–Guruswami–Lee–Tulsiani (matrix p→q inapproximability, spectral-norm side).

5. **SISTER-PRIMITIVE PAIRING for Techne T038:** T#43 (LimitWitness — topological ill-posedness) + T#56 (ComputationalComplexityCertificate — complexity intractability) should be treated as a **paired** Tier-B sub-primitive set under `ConstructiveExistenceWitness`. T#43 forbids assuming a minimizer exists; T#56 forbids assuming exact rank is computable. Together they bound the substrate's tensor-decomposition primitive.

---

## 1. Problem statement

For a 3-tensor T ∈ ℚ^{n×n×n}:

> **TENSOR-RANK over ℚ.** Given T and r ∈ ℕ, decide whether rank_ℚ(T) ≤ r.
> **NP-hard** (Håstad 1990 over finite fields; Hillar–Lim 2013 over ℚ); **∃ℚ-complete** (Schaefer–Štefankovič 2018); **undecidable when ℚ is replaced by ℤ** (Shitov 2016).

For a symmetric tensor F ∈ S^d(ℚ^n), d ≥ 3:

> **SYMMETRIC-RANK over ℚ (= Waring rank).** Given F and r ∈ ℕ, decide whether rank_S,ℚ(F) ≤ r.
> **NP-hard** (Shitov 2016, settling Hillar–Lim 2013 conjecture; refined Shitov 2025 PJM).

The catalog's "current results are partial" annotation is stale. The Hillar–Lim symmetric-rank-over-ℚ NP-hardness conjecture is now a theorem.

The genuinely open frontier on T#56 family (2026):
- (a) Decidability of tensor rank over ℚ (T#55, conditional on H10/ℚ).
- (b) Sharp inapproximability factor for symmetric rank — Swernofsky 2018 gave inapproximability for ordinary rank; symmetric-rank-specific tightness is open.
- (c) Parameterized complexity in r: is rank ≤ r decision FPT in r? Polynomial-time algorithms for symmetric rank ≤ 3, 4, 5? (Some special cases known.)
- (d) Average-case hardness with cryptographic-strength reductions (relevant to T#101 MinRank / tensor-isomorphism cryptosystems).
- (e) Whether **symmetric rank** is also ∃ℚ-complete.
- (f) Hardness of approximation under SoS lower bounds.

## 2. Status & bounds

Unconditional results (calibration anchors):

| Result | Authors | Year | Source |
|---|---|---|---|
| Tensor rank NP-complete over finite fields | Håstad | 1990 | *J. Algorithms* 11(4) |
| Most tensor problems NP-hard (rank, rank-1 approx, eigenvalue, sing. value, spectral norm, including symmetric restriction) | Hillar–Lim | 2013 | *J. ACM* 60(6):45 |
| Tensor rank over ℤ **undecidable** | Shitov | 2016 | arXiv:1611.01559 / *TOCS* |
| Symmetric rank over ℚ **NP-hard** (settles Hillar–Lim conjecture) | Shitov | 2016 | arXiv:1611.01559 |
| Tensor rank ∃ℚ-/∃ℝ-/∃ℂ-complete | Schaefer–Štefankovič | 2018 | *TOCS* / arXiv:1612.04338 |
| Tensor rank hard to approximate (inapproximability) | Swernofsky | 2018 | *APPROX/RANDOM* LIPIcs 116 |
| Inapproximability of matrix p→q norms (spectral-norm side) | Bhattiprolu–Ghosh–Guruswami–Lee–Tulsiani | 2018/2022 | *SICOMP* / arXiv:1802.07425 |
| Symmetric rank computation refinements | Shitov | 2025 | *Pacific J. Math.* 334(1) |

Conditional / partial: ℚ-decidability open (conditional on H10/ℚ); sharp inapproximability constants open; parameterized complexity in r largely open.

Algorithmic upper bounds (the polynomial side of the rank-zoo): Tucker / multilinear rank polynomial via HOSVD; TT rank polynomial via TT-SVD (Oseledets 2011); symmetric border rank ≤ r decision characterized via apolar 0-d Gorenstein scheme (P29 Buczyńska–Buczyński); matrix rank polynomial; slice / analytic rank polynomial.

## 3. Literature

Canonical (HARD-4 calibration anchors):
- Håstad, J. (1990). "Tensor rank is NP-complete." *J. Algorithms* 11(4):644–654. — Original NP-completeness for finite-field 3-tensors. Often miscredited.
- Hillar, C. J. & Lim, L.-H. (2013). "Most tensor problems are NP-hard." *J. ACM* 60(6):45. DOI 10.1145/2512329. arXiv:0911.1393. — THE survey result.
- Shitov, Y. (2016). "How hard is the tensor rank?" arXiv:1611.01559. *Theory of Computing Systems*. — Settles Hillar–Lim symmetric-rank-NP-hardness over ℚ. Proves tensor rank over ℤ undecidable.
- Shitov, Y. (2025). "Several remarks on tensor rank computation." *Pacific J. Math.* 334(1) Article 6.
- Schaefer, M. & Štefankovič, D. (2018). "The Complexity of Tensor Rank." *Theory of Computing Systems*. arXiv:1612.04338. — ∃ℚ-/∃ℝ-/∃ℂ-complete.
- Swernofsky, J. (2018). "Tensor Rank is Hard to Approximate." *APPROX/RANDOM 2018* LIPIcs 116:26.
- Bhattiprolu, V., Ghosh, M. K., Guruswami, V., Lee, E., Tulsiani, M. (2018/2022). "Inapproximability of Matrix p→q Norms." arXiv:1802.07425, *SICOMP* DOI 10.1137/18M1233418.
- Bhattiprolu et al. (2017). "Sum-of-Squares Certificates for Maxima of Random Tensors on the Sphere." *APPROX/RANDOM 2017*.
- Barak, B. & Moitra, A. (2016). "Noisy Tensor Completion via the Sum-of-Squares Hierarchy." arXiv:1501.06521.

Adjacent / supporting: Comon–Mourrain symmetric tensor decomposition; Landsberg 2012 *Tensors: Geometry and Applications* (AMS GSM 128); Buczyńska–Buczyński border apolarity; Iarrobino–Kanev 1999 *Power Sums, Gorenstein Algebras, Determinantal Loci*; Carlini–Catalisano–Geramita Waring decompositions of monomials; Comas–Seiguer 2011 polynomial-time symmetric rank for binary forms.

Software (HARD-6): Macaulay2 (Apolarity, SecantVarieties); Bertini, HomotopyContinuation.jl; Magma / GAP for finite-field tensor rank; TensorLy `decomposition.symmetric_parafac` (heuristic ALS, no certificate); Yalmip / Mosek + Lasserre SoS hierarchies.

## 4. Attack vectors active in the literature

**4.1 P25 Pivotal Negative Result (the central paradigm here).** NP-hardness IS the pivotal negative result that reorients attack strategy. Hillar–Lim's contribution is the substrate-grade formulation. Shitov's contribution is the sharper P25 instance closing the symmetric-rank-over-ℚ conjecture and proving undecidability over ℤ. Schaefer–Štefankovič's contribution is the ∃-theory-completeness sharpening — a P25 with algebraic-universality flavor. The substrate's KILL operator at the meta-level is exactly this paradigm.

**4.2 Reduction gadgetry.** 3-SAT / clique → tensor rank (Hillar–Lim line); polynomial-system feasibility → tensor rank (Shitov's tighter equivalence — gives undecidability over ℤ for free via Hilbert's tenth, ∃-theory completeness over ℚ/ℝ/ℂ via Schaefer–Štefankovič machinery); symmetric flattenings + catalecticant matrices as gadgets; Waring-rank lower bounds via apolarity (P29) as the gadget primitive.

**4.3 P22 Polynomial Method.** Secondary connection: PIT-flavored relevance to ∃-theory-completeness; Schwartz–Zippel-style arguments appear in approximation hardness. Don't confuse with multilinear apolarity (P29).

**4.4 P27 Slice Rank / Polynomial Method on F_q.** Substrate moral: when an NP-hard quantity has a polynomial-time slice-rank-style upper bound, the bound is a substrate-grade primitive even when the underlying decision is NP-hard.

**4.5 P29 Border Apolarity.** For symmetric tensors, apolarity gives constructive lower bounds polynomial-time verifiable once a candidate apolar scheme is provided — verification polynomial, search NP-hard. Canonical P25 / P29 interplay.

**4.6 SoS lower-bound machinery.** SoS hierarchies give degree-Ω(n) integrality gaps for tensor rank decision in worst case — *unconditional* (no P ≠ NP assumption) but apply only to SoS algorithms.

**4.7 New paradigm candidate: Existential-Theory Reduction / Algebraic Universality** (Schaefer–Štefankovič). Reduces a tensor problem to "is this system of polynomial equations over field K satisfiable?" — produces *completeness* in a logical theory, not just hardness in a complexity class. Distinct from P22, P25, P29. Sub-paradigm: Shitov's integral-domain polynomial-equivalence (tensor rank ≡_p polynomial-system feasibility over the same integral domain). **Numbering note:** T#1 also flagged a P32 candidate (Evolutionary-LLM Algorithm Synthesis); synthesis must renumber.

## 5. Substrate encoding

**Current gap:** Substrate's existing primitives operate at the *computable-in-practice* level. None carry a complexity certificate. Tensor-rank-shaped queries have no machinery to refuse with "this is NP-hard, route to a stable substitute or escalate."

**Required primitive (Tier-B `ComputationalComplexityCertificate`, sister of `ConstructiveExistenceWitness`):**

```
ComputationalComplexityCertificate {
  query: TensorQuery                       // e.g. "rank(T) ≤ r over ℚ?"
  format: TensorFormat                     // CP / symmetric-CP / Tucker / TT / border / slice
  field: Field                             // ℚ / ℝ / ℂ / 𝔽_q / ℤ
  complexity_class: {
    P, BPP,
    NP_HARD,                               // Hillar–Lim 2013
    EXISTS_K_COMPLETE,                     // Schaefer–Štefankovič 2018, K = field
    UNDECIDABLE,                           // Shitov 2016 (ℤ case)
    UNKNOWN_OPEN
  }
  hardness_witness: optional<{
    reduction_source: {3SAT, CLIQUE, POLY_SYSTEM_FEASIBILITY, ...}
    reduction_target: TensorQuery
    reduction_proof_ref: Citation
  }>
  upper_bound_witness: optional<{
    algorithm: {HOSVD, TT_SVD, APOLARITY_SEARCH, LASSERRE_SOS_DEGREE_d, ALS}
    runtime_class: {POLY, QPOLY, EXP, ...}
    approximation_factor: optional<Real>
    certificate_kind: {EXACT, APPROX_WITH_GAP, HEURISTIC_NO_CERT}
  }>
  substrate_routing: {
    ACCEPT_EXACT,                          // small-r polynomial special case
    ACCEPT_BOUNDED_FORMAT,                 // route to Tucker / TT
    ACCEPT_APPROX_WITH_GAP,                // SoS / spectral, gap reported
    DECLINE_NP_HARD,                       // raise CapabilityGapTicket
    DECLINE_UNDECIDABLE                    // ℤ-rank case
  }
}
```

**ComplexityStratifier decorator (load-bearing):** every tensor-touching primitive must register a `ComplexityStratifier` that, given a query, returns one of the five `substrate_routing` actions. Non-optional — primitives without a stratifier cannot be promoted to canon.

**Coordinate-chart hint:** Complexity class is a property of (chart, field, query), not of the bare tensor. The same symmetric tensor in CP-symmetric chart over ℚ has NP-hard rank decision; in Tucker chart it has polynomial multilinear-rank decision.

**Sister-primitive relationship:** `ComputationalComplexityCertificate` is to `ConstructiveExistenceWitness` as P25 is to P29 / P31. They compose: a `ConstructiveExistenceWitness` whose verifier is polynomial but whose search is NP-hard carries a `ComputationalComplexityCertificate` of class `NP_HARD_BUT_VERIFIABLE_IN_P` — exactly the P29 apolarity case.

**Capability-gap tickets:**
- Proposed new: `T-ST-T56-001` — register `ComputationalComplexityCertificate` as Tier-B primitive.
- Proposed new: `T-ST-T56-002` — `ComplexityStratifier` decorator required on every tensor-touching primitive.
- Proposed new: `T-ST-T56-003` — substrate-tester probe: any "computed rank" claim on a 3-tensor over ℚ must carry a complexity certificate.

## 6. Calibration anchor notes

**Substrate-grade response to "is symmetric tensor rank computable?":**
- Symmetric rank over ℚ NP-hard (Shitov 2016, settling Hillar–Lim 2013 conjecture; refined Shitov 2025 PJM).
- Ordinary tensor rank over ℚ is ∃ℚ-complete (Schaefer–Štefankovič 2018) — stronger than NP-hardness.
- Tensor rank over ℤ undecidable (Shitov 2016).
- Cites Hillar–Lim, Shitov, Schaefer–Štefankovič, Håstad with venues.
- Distinguishes (i) decision (NP-hard / undecidable), (ii) approximation (Swernofsky inapproximability), (iii) verification of fixed-rank witness (often polynomial via apolarity), (iv) bounded-format reformulation (Tucker / TT polynomial).
- Distinguishes the rank-zoo: CP / symmetric / border / multilinear / TT / slice / analytic — different complexity classes.

**Textbook-trivial response (FAIL signal):**
- "Tensor rank is NP-hard." — Stops at headline.
- "Hillar–Lim 2013 settled it." — WRONG. Hillar–Lim left symmetric-rank-over-ℚ as conjecture; Shitov 2016 settled.
- "Just use SVD." — Confuses matrix rank (poly) with tensor rank (NP-hard). PATTERN_RANK_PARITY_LEAK.
- "ALS converges in practice, so the problem is fine." — PATTERN_VRAM_TRUNCATION_ARTIFACT trap.

**Trivial-vs-open (FM-08 anchor):**
- Rank decision over ℚ: NP-hard (settled), ∃ℚ-complete (settled).
- Symmetric rank decision over ℚ: NP-hard (settled, Shitov 2016).
- Rank approximation factor sharpness: OPEN.
- Rank decidability over ℚ: OPEN, conditional on H10/ℚ.
- Rank over ℤ: undecidable (settled).
- Multilinear / TT rank: polynomial (settled).

**Attribution canonicality:** Highest popular: Hillar, Lim. High technical, lower popular: Shitov (the actual settler of multiple conjectures). High technical, niche popular: Schaefer, Štefankovič; Håstad. Calibration risk: a Learner trained on popular-press writeups will credit Hillar–Lim for *everything*, including results actually due to Shitov, Schaefer–Štefankovič, or Håstad.

**Pattern citations:**

- **PATTERN_BASE_RATE_NEGLECT.** NP-hardness is the typical-case complexity behavior of tensor problems, not the exotic edge case. The trap is treating "tensor rank is NP-hard" as a surprising finding rather than the base rate. Polynomial special cases are the exceptions worth tracking, not the rule.

- **PATTERN_RANK_PARITY_LEAK.** T#56 is the textbook leakage test:

  | Rank notion | Field | Complexity |
  |---|---|---|
  | CP rank | ℚ | NP-hard, ∃ℚ-complete |
  | CP rank | ℝ | ∃ℝ-complete |
  | CP rank | ℂ | ∃ℂ-complete |
  | CP rank | ℤ | UNDECIDABLE |
  | Symmetric rank | ℚ | NP-hard (Shitov 2016) |
  | Border rank | ℝ/ℂ | ∃ℝ-complete (in many forms) |
  | Multilinear (Tucker) rank | any | POLYNOMIAL |
  | TT rank | any | POLYNOMIAL |
  | Slice / analytic rank | finite | POLYNOMIAL (different question) |
  | Cactus rank | scheme-theoretic | varies |

- **PATTERN_VRAM_TRUNCATION_ARTIFACT.** Numerical ALS terminates when residuals hit float ceilings — produces a "looks polynomial" surface masking the underlying NP-hardness. Substrate must check (a) factor-norm divergence (T#43 signal), (b) residual stagnation independent of precision (T#56 signal), (c) refuse to issue a "computed rank" claim without a complexity certificate.

## 7. Cross-references

**Within `tensor_open_problems_v1.md`:**
- #55 Tensor rank decidability over ℚ — direct sibling. T#56 closes NP-hardness side; T#55 is open decidability side.
- #57 Constant-factor approximation — Swernofsky inapproximability + Bhattiprolu et al. matrix-p→q.
- #58 Tensor isomorphism complexity — same complexity-class neighborhood; cryptographic relevance.
- #59 Hyperdeterminant decision problems.
- #67 Tensor spectral norm approximation.
- #69 Symmetric positive-definiteness decision.
- #101 MinRank / tensor isomorphism cryptographic foundations.

**Within `attack_angle_taxonomy.md`:**
- P25 (Pivotal Negative Result) — primary paradigm.
- P22, P27, P29, P31 secondary.
- **New paradigm candidate (proposed):** Existential-Theory Reduction / Algebraic Universality.

**Within `aporia/docs/deep_research_batch_tensor_priority_2026-05-09/`:**
- report_T43 (existence of best rank-r approximation) — sister paper. T#43 = topological / numerical ill-posedness; T#56 = complexity-theoretic intractability. Together they bound the substrate's tensor-decomposition primitive.
- report_T1, report_T28 — meta-anchors above the decision-rank zoo.
- (forthcoming) tensor_priority_synthesis_2026-05-09.md — must register the proposed paradigm candidate (resolve numbering against T#1's P32 candidate) and the proposed `ComputationalComplexityCertificate` primitive.

**Substrate-tester capability-gap tickets where complexity-stratification was implicit:**
- T-ST-fire39-001 (T#84 optimal contraction order); T-ST-fire40-001 (T#58 tensor isomorphism); T-ST-fire41-001 (T#34 border-rank variety membership); T-ST-fire43-001 (T#73 tensor PCA).
- Proposed new: T-ST-T56-001, T-ST-T56-002, T-ST-T56-003.

**Forward dependency for Techne T038 classification:** T#56 contributes the `ComputationalComplexityCertificate` primitive specification to the Tier-B meta-primitive class, sister to `ConstructiveExistenceWitness`. T038 should treat (LimitWitness from T#43) + (ComputationalComplexityCertificate from T#56) as a paired primitive set. Contract window must include the `ComplexityStratifier` decorator requirement on every tensor-touching component.

---

*Aporia, 2026-05-09*
