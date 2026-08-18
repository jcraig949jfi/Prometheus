# Report T#34 — Border-Rank Variety Membership Problem

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §IV #34
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 2, fire-7)
**Substrate-tester linkage:** capability-gap ticket `T-ST-fire41-001` (Tier-B four-fire ConstructiveExistenceWitness convergence)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_RANK_PARITY_LEAK, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_BASE_RATE_NEGLECT
**Tags:** P29 (border apolarity, primary), P31 (secant variety geometry, dual framework), P25 (pivotal-negative-result), P15 (parent-paradigm), P09 (exhaustive computation, secondary)

---

## Brief summary

T#34 is the algorithmic decision problem `T ∈ σ_r?` (border-rank variety membership), distinct from rank decision (T#56, NP-hard / ∃F-complete per Hillar–Lim 2013 and Schaefer–Štefankovič 2018) and from rank-r best-approximation (T#43, ill-posed per de Silva–Lim 2008). Border-rank-specific complexity classification remains open beyond the rank baseline. Four substrate-relevant attack channels: (1) **P29 border apolarity** (Buczyńska–Buczyński Duke 2021; Conner–Harper–Landsberg Forum Math Pi 2023; B-invariant ideal enumeration — substrate-friendly because certificates are CONSTRUCTIVE); (2) **P31 Young flattenings** (Landsberg–Ottaviani; Kronecker–Young extensions arXiv:2602.12762 reach beyond cactus stratum); (3) **numerical AG** (Bertini, HomotopyContinuation.jl); (4) **SDP / SoS hierarchies**. Maps directly to Tier-B `ConstructiveExistenceWitness` substrate primitive. Per the T#43 + T#56 sister-primitive pattern, T#34 supplies the `BorderRankWitness` subtype completing the Tier-B cluster.

## Flagged findings

1. **Substrate gap (substantive, exactly fire-41):** No primitive certifies positive existential `T ∈ σ_r`. Substrate has `ExclusionCertificate` (negative direction) but no companion for constructive membership — the four-fire Tier-B convergence point.

2. **Sister-primitive composition locked:** `BorderRankWitness ⊃ LimitWitness ⊃ DecompositionCertificate`. All three Tier-B subtypes (T#34, T#43, T#56) should land in the same contract-change window.

3. **PATTERN_RANK_PARITY_LEAK is the primary calibration trap.** Six rank notions — rank, border rank, cactus rank, symmetric rank, symmetric border rank, multilinear rank — share the word "rank" but are distinct decision problems. Hillar–Lim NP-hardness is for *rank*, not *border rank*. T#34 IS a leakage-test problem.

4. **PATTERN_VRAM_TRUNCATION_ARTIFACT is acute for numerical-AG witness sets.** Path-tracking near σ_r boundary suffers Jacobian degeneracy at the singular locus. 64-bit double precision can produce false in-set OR false out-of-set certificates. Substrate-tester must require adaptive-precision endgame engagement on any NAG-based T#34 witness.

5. **PATTERN_BASE_RATE_NEGLECT trap:** σ_r is full-dimensional in non-defective cases, so "almost surely T ∈ σ_r once r ≥ generic_rank" hides the structurally-interesting *defective* stratum where membership is the real question.

6. **Two proposed new tickets:**
   - `T-ST-T34-001` BorderRankWitness probe with PATTERN_VRAM_TRUNCATION_ARTIFACT compliance check.
   - `T-ST-T34-002` PATTERN_RANK_PARITY_LEAK calibration probe.

7. **Candidate substrate primitives surfaced (not paradigms but architecture):**
   - `DualityCheck` — cross-verify P29 (apolarity, NON-membership) against P31 (Young flattenings, equation-vanishing) certificates.
   - `PrecisionFloorCertificate` — promote NAG endgame precision tracking to a substrate-level primitive auditable across all numerical-AG-based witnesses.

## 1. Problem statement

Let `V_1, V_2, V_3` be finite-dimensional ℂ-vector spaces. The Segre variety is the image of `Seg : P V_1 × P V_2 × P V_3 → P(V_1 ⊗ V_2 ⊗ V_3)` via `([v_1], [v_2], [v_3]) ↦ [v_1 ⊗ v_2 ⊗ v_3]`. The **r-th secant variety** σ_r = σ_r(Seg) is the Zariski closure of the union of (r−1)-secant `(r−1)`-planes.

**Border rank:** `R̲(T) := min { r : [T] ∈ σ_r }`. Border rank can be strictly less than rank (Bini's degeneration).

**T#34 problem:** *Given T and integer r, decide whether `[T] ∈ σ_r`.*

Equivalent formulations:
- (Closure form, P31) Decide whether T is the limit of a sequence of rank-r tensors.
- (Defining-equations form) Decide whether all defining polynomials of σ_r vanish at T.
- (Apolar form, P29) Decide whether there exists a saturated apolar 0-dimensional Gorenstein scheme of length r with appropriate B-invariance.

**Why structurally distinct from T#43:** T#43 is optimization on the **non-closed** S_r (may have no minimizer). T#34 is decision on the **closed** σ_r = clos(S_r) (always well-defined). Closure FIXES existence; it does NOT make membership computationally easy.

**Why structurally distinct from T#56:** T#56 is hardness of *computing rank*. T#34 is *fixed-r decision*.

## 2. Status & bounds

| Result | Authors | Year |
|---|---|---|
| Tensor rank decision NP-complete over finite fields | Håstad | 1990 |
| Tensor rank decision NP-hard over ℚ, ℝ, ℂ | Hillar, Lim | 2013 |
| Tensor rank ∃ℝ-/∃ℂ-/∃ℚ-complete | Schaefer, Štefankovič | 2018 |
| Tensor rank decidability over ℤ undecidable | Shitov | 2016 |
| Border-rank decidability over ℝ in ∃ℝ | folk | — |
| Border apolarity (general theory + algorithm) | Buczyńska, Buczyński | 2021 |
| Border-apolarity algorithm for matrix mult | Conner, Harper, Landsberg | 2023 |
| Numerical homotopy-continuation tensor decomposition | Bernardi, Daleo, Hauenstein, Mourrain | 2017 |
| Homotopy techniques for perfect identifiability | Hauenstein, Oeding, Ottaviani, Sommese | 2019 |
| Border-rank R̲(M⟨3⟩) ≥ 17 | Landsberg, Michałek; CHL | 2017–2023 |
| Kronecker–Koszul / Kronecker–Young flattenings beyond cactus | Galązka, Mańdziuk et al. | 2026 |
| Border rank of 4×4 determinant tensor = 12 | (preprint cluster) | 2025 |

**Open frontier:**
1. Border-rank decision precise complexity over ℝ — in ∃ℝ; whether ∃ℝ-complete is open.
2. Border-rank decision over ℚ — conditional on Hilbert's tenth.
3. Approximation hardness for border-rank computation.
4. Parameterized complexity in r and tensor format.
5. SoS-degree-vs-approximation-quality tradeoff.

## 3. Literature

**Canonical complexity:**
- Håstad 1990, *Tensor rank is NP-complete*, J. Algorithms 11(4):644–654.
- Hillar, Lim (2013). *Most tensor problems are NP-hard*, J. ACM 60(6):45.
- Schaefer, Štefankovič (2018). *The complexity of tensor rank*, Theory Comput. Syst. 62(5).
- Shitov (2016). *How hard is the tensor rank?* arXiv:1611.01559.

**Border apolarity (P29):**
- Buczyńska, Buczyński (2021). Duke Math. J. 170(16):3659–3702, arXiv:1910.01944.
- Conner, Harper, Landsberg (2023). Forum Math. Pi 11:e17, arXiv:1911.07981.
- Mańdziuk, Ventura (2024). arXiv:2310.19625.
- Recent: arXiv:2510.11051 (border rank of 4×4 det = 12); arXiv:2601.19558 (border cactus).

**Secant varieties / Young flattenings (P31):**
- Landsberg (2012). *Tensors: Geometry and Applications*, AMS GSM 128.
- Landsberg, Ottaviani (2013). Ann. Mat. Pura Appl. 192:569–606.
- Galązka, Mańdziuk et al. (2026). arXiv:2602.12762.

**Numerical algebraic geometry:**
- Bates, Hauenstein, Sommese, Wampler (2013). *Numerically Solving Polynomial Systems with Bertini*, SIAM.
- Bernardi, Daleo, Hauenstein, Mourrain (2017). J. Symbolic Comput., arXiv:1512.04312.
- Hauenstein, Oeding, Ottaviani, Sommese (2019). Crelle's J., DOI 10.1515/crelle-2016-0067.
- HomotopyContinuation.jl (Breiding–Timme).

**Algebraic statistics anchor:**
- Allman, Rhodes (2008). Adv. Appl. Math. 40:127–148.

**Software:** Macaulay2 (`SecantVarieties`, `Apolarity`, `MultigradedHilbert`); Bertini + HomotopyContinuation.jl + PHCpack; kashbari/BorderApolarity GitHub; TensorLy; Mosek / SDPT3.

## 4. Attack vectors

**4.1 P29 border apolarity — primary (substrate-grade).**
Algorithm: compute apolar ideal `T^⊥`; enumerate B-invariant ideals `J ⊃ T^⊥` of fixed multigraded Hilbert function corresponding to length r; check fixed-ideal-theorem conditions; output NO valid J → R̲(T) > r (NEGATIVE certificate) or candidate decompositions (POSITIVE candidates). Substrate-friendly: certificates CONSTRUCTIVE, auditable, signature-keyable. Pairs with `TriangulationProtocol`. Audit hook: `ApolarSchemeWitness(T, r, scheme=J or ABSENT)`.

**4.2 P31 Young flattenings — polynomial-test certificates.**
Landsberg–Ottaviani Young flattenings give explicit determinantal equations: matrix flattenings of T whose minors must vanish if T ∈ σ_r. Non-vanishing of one Young flattening proves T ∉ σ_r. Kronecker–Koszul / Kronecker–Young (arXiv:2602.12762) extend beyond cactus stratum. Limitations: Young flattenings cut out a variety LARGER than σ_r in general — necessary, NOT sufficient.

**4.3 Numerical algebraic geometry — Bertini / HomotopyContinuation.jl.**
Direct membership test: parameter homotopy `T_t = T + t·perturbation`, track CP decompositions, endgame at t=0. Witness set route: compute σ_r witness set; intersect with T's slice. Returns ALL decompositions when finitely many. PATTERN_VRAM_TRUNCATION_ARTIFACT: 64-bit double precision can produce false certificates either way — adaptive-precision endgame REQUIRED for substrate-grade verification.

**4.4 SDP / SoS hierarchies.**
Lasserre / SoS relaxations approximate σ_r-membership via outer-approximation hierarchy. Convergent in d → ∞ under Archimedean conditions. Cost `O(n^d)` — tractable only small (n, d). Does NOT give exact decisions.

**4.5 Reduction to existential theory of the reals.**
Schaefer–Štefankovič ∃F-completeness for rank-decision; closure version (T ∈ σ_r) in ∃F, exact lower bound open.

**4.6 New substrate-architecture proposals (not paradigms):**
- P29 ↔ P31 duality is operationally TWO-WAY: cross-verify NON-membership (apolarity) against equation-vanishing (Young flattenings). Suggests `DualityCheck` substrate primitive.
- Numerical-AG endgame as substrate primitive: `PrecisionFloorCertificate` to audit any numerical T#34 result for PATTERN_VRAM_TRUNCATION_ARTIFACT compliance.

## 5. Substrate encoding

**Current gap (= fire #41):** Substrate has `ExclusionCertificate` for `T ∉ σ_r`. NO companion `ConstructiveExistenceWitness` for `T ∈ σ_r`. This asymmetry is the four-fire convergence point.

**Required primitive (Tier-B `ConstructiveExistenceWitness` → `BorderRankWitness` subtype):**

```
BorderRankWitness {
  tensor:           TensorObject
  ambient_field:    {ℚ, ℝ, ℂ}
  border_rank_r:    Integer
  witness_type:     {DECOMPOSITION, DEGENERATION_SEQUENCE, APOLAR_SCHEME, FLATTENING_RANK, NAG_WITNESS_SET}

  decomposition:    optional<List<RankOneTensor>>
  degeneration:     optional<{
    family:         ParameterizedFamily<TensorObject>
    limit:          TensorObject
    rank_along_family: Integer
    blowup_pattern: {STANDARD, SCHONHAGE, BINI}
  }>
  apolar_witness:   optional<{
    apolar_ideal:   GradedIdealOverPolynomialRing
    length:         Integer
    B_invariance:   bool
    saturation:     bool
    multigraded_hilbert_function: List<Integer>
  }>
  flattening:       optional<{
    flattening_type: {YOUNG, KRONECKER_YOUNG, KOSZUL, CATALECTICANT}
    flattening_matrix: Matrix
    rank_at_T:      Integer
    rank_threshold: Integer
  }>
  nag_witness:      optional<{
    witness_set:    List<TensorObject>
    homotopy:       HomotopyPath
    precision_floor: Float
    endgame_engaged: bool
  }>

  closure_status:   {IN_INTERIOR, ON_BOUNDARY, IN_CACTUS_STRATUM_NOT_BORDER, UNKNOWN}
  confidence:       {EXACT, NUMERICAL_CERTIFIED, NUMERICAL_HEURISTIC}
}
```

**Composition with sister primitives:**
- `BorderRankWitness ⊃ LimitWitness (T#43)` — every degeneration-sequence witness IS a `LimitWitness`.
- `BorderRankWitness` complements `ComputationalComplexityCertificate (T#56)` — T#56: "deciding this is NP-hard"; T#34 BorderRankWitness: "for THIS T, here's the decision proof."
- Composes with `ExclusionCertificate` via duality: `ExclusionCertificate(T, r-1)` ∧ `BorderRankWitness(T, r)` ⇒ exact border-rank determination.

**CoordinateChart hint:** the same T registers different CoordinateCharts depending on encoding (CP vs apolar-ideal vs Young flattening vs witness-set). The chosen `witness_type` IS chart selection — substrate must reject heterogeneous-chart claims.

**Capability-gap tickets:**
- `T-ST-fire41-001` — primary anchor.
- `T-ST-fire41-002` — ConstructiveExistenceWitness root flag.
- `T-ST-fire38-001`, `T-ST-fire39-001`, `T-ST-fire40-001` — sibling fires.
- **Proposed new** `T-ST-T34-001` — BorderRankWitness probe with PATTERN_VRAM_TRUNCATION_ARTIFACT compliance check.
- **Proposed new** `T-ST-T34-002` — PATTERN_RANK_PARITY_LEAK calibration probe.

## 6. Calibration anchor notes

**Substrate-grade response:**
- States σ_r-membership decidable; precise complexity beyond rank-decision baseline is open.
- Names four channels (P29 apolarity, P31 Young flattenings, NAG, SDP) with distinct certificate types.
- Distinguishes σ_r (border rank), S_r (rank, T#43), cactus-rank-r (T#19), symmetric variants (T#20).
- Cites canonical authors properly.
- Acknowledges PATTERN_VRAM_TRUNCATION_ARTIFACT for numerical-AG path-tracking.
- Acknowledges PATTERN_RANK_PARITY_LEAK as primary calibration trap.

**Textbook-trivial (FAIL):**
- "It's NP-hard, end of story." — wrong resolution.
- "Compute the rank, check ≤ r." — RANK ≠ BORDER RANK; PATTERN_RANK_PARITY_LEAK trigger.
- "Use Young flattenings — necessary and sufficient." — necessary, NOT sufficient.
- "SDP gives the answer." — outer-relaxation only.
- "Just run Bertini." — without adaptive precision, PATTERN_VRAM_TRUNCATION_ARTIFACT.

**Trivial-vs-open within rank-zoo (FM-08 + PATTERN_RANK_PARITY_LEAK):**
- Rank R(T) decision (S_r) → NP-hard, ∃F-complete — sister problem.
- **Border rank R̲(T) decision (σ_r) → THIS REPORT (T#34): in ∃ℝ; precise complexity open.**
- Cactus rank → scheme-theoretic, T#19, often strictly larger.
- Symmetric border rank → T#20.
- Generic / typical rank → T#37.
- Slice / partition / analytic / geometric rank → P27, completely different.

**Pattern citations:**
- **PATTERN_RANK_PARITY_LEAK.** Six rank notions sharing the word "rank" but distinct decision problems. T#34 IS a leakage-test problem.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT.** Numerical-AG path-tracking near σ_r boundary suffers Jacobian degeneracy; double precision can produce false certificates either way.
- **PATTERN_BASE_RATE_NEGLECT.** σ_r full-dimensional in non-defective cases; "almost surely T ∈ σ_r" hides defective stratum (T#26) where membership is the real question.

## 7. Cross-references

**Within `tensor_open_problems_v1.md`:**
- **#5** (border rank M⟨n⟩) — direct application; CHL 2023 R̲(M⟨3⟩) ≥ 17 is leading T#34-via-P29 result.
- **#6** (border-rank additivity); **#19** (cactus rank); **#26** (defective Segre-Veronese); **#29** (regularity); **#31** (defining equations); **#33** (singularities); **#43** (sister Tier-B); **#56** (sister Tier-B); **#57**; **#58** (sister fire #40); **#84** (sibling Tier-A++ fire #39).

**Within `attack_angle_taxonomy.md`:**
- P29 (primary), P31 (dual framework), P25, P15, P09.

**Prior reports in batch:**
- `report_T1_matrix_multiplication_exponent.md`; `report_T28_asymptotic_spectrum.md`; `report_T43_best_rank_r_existence.md` (sister Tier-B); `report_T56_symmetric_rank_nphard.md` (sister Tier-B); `report_T79_slocc_entanglement.md`; `report_T95_kronecker_positivity.md`.

**Substrate-tester capability-gap tickets:**
- `T-ST-fire41-001` (primary anchor); `T-ST-fire41-002`; `T-ST-fire38/39/40-001` (siblings).
- Proposed `T-ST-T34-001`, `T-ST-T34-002`.

**Forward dependency for Techne T038 classification:** T#34 specifies the BorderRankWitness subtype completing the Tier-B contract-change-window scope (with T#43 LimitWitness and T#56 ComputationalComplexityCertificate).

---

*Aporia, 2026-05-09*
