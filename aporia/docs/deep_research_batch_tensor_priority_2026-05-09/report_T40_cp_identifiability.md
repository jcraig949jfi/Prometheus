# Report T#40 — Generic CP Identifiability Beyond Kruskal

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §V #40
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 2, fire-12)
**Substrate-tester linkage:** `T-ST-fire45-001` (5-tier-saturation fire — Tier-B + Tier-D composition, **second confirmation** after fire #43 / T#73)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_RANK_PARITY_LEAK, PATTERN_VRAM_TRUNCATION_ARTIFACT
**Tags:** P31 (primary), P15 (parent), P29 (dual), P09 (secondary), P25

---

## Brief summary

T#40 asks for sharp generic identifiability conditions for the CP decomposition of an order-d tensor of rank r, beyond Kruskal's 1977 sufficient condition `2r + d − 1 ≤ Σ k_i` (specialized form `2r + 2 ≤ k_1 + k_2 + k_3` for d=3). The frontier has shifted from Kruskal-style permutation-lemma bounds to algebraic-geometric criteria built on weak defectivity (Chiantini–Ottaviani 2012; Bocci–Chiantini–Ottaviani 2014), reshaping (Domanov–De Lathauwer 2013–2017; Chiantini–Ottaviani–Vannieuwenhoven 2014/2017), and constructive-algorithmic uniqueness (Koiran 2024 r ≤ 4n/3 for n×n×p, p ≥ 4; mathrepo MIS rank-3 algorithm 2025). Generic identifiability is a full-measure statement on the rank-r locus — its substrate-correct encoding therefore forces a **Tier-B + Tier-D composition**: a Tier-B `RankDecompositionWitness` (uniqueness for an individual T) bundled with a Tier-D `GenericityAlmostEverywhereCert` (the format-and-rank pair `(n_1,…,n_d; r)` admits identifiability outside a measure-zero exception locus). This composition was first surfaced by fire #43 (T#73 tensor PCA threshold) and **confirmed a second time by fire #45** — the empirical basis for substrate-tester's saturation declaration.

## Flagged findings

1. **Substrate gap (substantive, exactly fire #45 saturation finding):** identifiability is irreducibly a *cross-tier* claim. Neither Tier B alone nor Tier D alone captures it. Tier B says "for THIS T, the decomposition is unique"; Tier D says "the *format* admits unique decomposition for almost every T." Substrate must encode both, plus their composition contract.

2. **Second confirmation of cross-tier composition.** Fire #43 (T#73: Tier-B SoS + Tier-D PhaseTransitionThreshold) and Fire #45 (this entry: Tier-B uniqueness + Tier-D GenericityAlmostEverywhereCert) are independent realizations of the same Tier-B/Tier-D composition. Two independent confirmations of the same architectural primitive ⇒ saturation: 5-tier model holds.

3. **PATTERN_BASE_RATE_NEGLECT is the primary calibration trap.** "Generic identifiability holds for r ≤ ..." is a full-measure statement that EXCLUDES the defective stratum and the unbalanced / non-defective-but-non-identifiable stratum (CO-V 2014–2017 list of subgeneric symmetric exceptions: **(d, n, r) = (6, 2, 9), (4, 3, 8), (3, 5, 9)**).

4. **PATTERN_RANK_PARITY_LEAK is acute.** CP rank, symmetric rank, multilinear (Tucker) rank, border rank, cactus rank, partially-symmetric / Hadamard–Hitchcock rank — different identifiability conditions. The reshaped Kruskal criterion (CO-V 2017) is effective for *complex* tensors in its entire range; the *symmetric* version is effective only up to the smallest typical rank in low dimensions.

5. **PATTERN_VRAM_TRUNCATION_ARTIFACT relevant for numerical-AG witnesses.** Bertini / HomotopyContinuation.jl certified-identifiability witnesses near the defectivity / non-identifiability boundary suffer Jacobian degeneracy.

6. **Three proposed new tickets:**
   - `T-ST-T40-001` GenericityAlmostEverywhereCert subtype probe.
   - `T-ST-T40-002` PATTERN_BASE_RATE_NEGLECT calibration probe (defective + unbalanced exception-stratum awareness).
   - `T-ST-T40-003` cross-tier composition contract verification.

7. **Candidate substrate primitives surfaced:**
   - `MeasureZeroExceptionAnnotation` — explicit list of (d,n,r) defective + non-defective-but-non-identifiable exceptions; first-class field on every GenericityAlmostEverywhereCert.
   - `ReshapingCertificate` — record of which flattening certified the claim (CO-V 2017 reshaped Kruskal); enables chart-change auditing.

## 1. Problem statement

Let `V_1, …, V_d` be ℂ-vector spaces of dimensions `n_1, …, n_d` and `T ∈ V_1 ⊗ … ⊗ V_d`. A **CP decomposition of length r** is `T = Σ_{i=1..r} v_1^{(i)} ⊗ … ⊗ v_d^{(i)}`. The decomposition is **unique** (T is **r-identifiable**) iff this expression is unique modulo permutation-and-rescaling symmetries.

**Generic identifiability:** the format `(n_1, …, n_d; r)` is **generically r-identifiable** iff the rank-r tensors that admit a unique decomposition form a Zariski-open dense subset of σ_r°.

**Kruskal 1977 bound (d=3):** with k-rank `k_X` of factor matrix X, `k_A + k_B + k_C ≥ 2r + 2 ⇒ CP decomposition unique`. Order d ≥ 3: `Σ k_{A_i} ≥ 2r + d − 1`.

**T#40:** sharpen / replace these sufficient conditions with effective generic-identifiability criteria, ideally tight for the format `(n_1, …, n_d; r)`.

## 2. Status & bounds

| Result | Authors | Year |
|---|---|---|
| `2r + d − 1 ≤ Σ k_i` ⇒ uniqueness (specific) | Kruskal | 1977 |
| Symmetric tensor decomposition (Sylvester extension) | Brachat–Comon–Mourrain–Tsigaridas | 2010 |
| Weak-defectivity-based generic identifiability for 3-tensors | Chiantini–Ottaviani | 2012 (SIMAX) |
| Refined methods, factor `0.9997 (2^n)/(n+1)` | Bocci–Chiantini–Ottaviani | 2013/2014 (Annali) |
| Generic uniqueness for CPD via reshaping | Domanov–De Lathauwer | 2013–2017 (SIMAX series) |
| Algorithm for generic + low-rank specific identifiability | Chiantini–Ottaviani–Vannieuwenhoven | 2014 (SIMAX) |
| Subgeneric symmetric exceptions `(6,2,9),(4,3,8),(3,5,9)` | Chiantini–Ottaviani–Vannieuwenhoven | 2014–2017 |
| Effective criteria + reshaped Kruskal optimality (4×4×4×4) | Chiantini–Ottaviani–Vannieuwenhoven | 2017 (SIMAX) |
| Symmetric subgeneric identifiability | Chiantini–Ottaviani–Vannieuwenhoven | 2017 (Trans. AMS) |
| Almost-all subgeneric Chow decomposability | Chow-decomp authors | 2022 (Annali) |
| Hadamard–Hitchcock identifiability via reshaped Kruskal | (arXiv:2308.06597) | 2023 |
| Constructive overcomplete uniqueness, r ≤ 4n/3 (n×n×p, p≥4) | Koiran | 2024 (arXiv:2404.07801) |
| Identifiability of deep polynomial NNs via Kruskal | (arXiv:2506.17093) | 2025 |
| Algorithm for rank-3 tensor identifiability | mathrepo MPI MIS | 2025 |

**Open frontier:** tight bound for general d and `(n_1,…,n_d)` outside known cases; sharp criteria for partially symmetric / Hadamard–Hitchcock formats; ternary-form symmetric identifiability beyond degree 7; effective certification beyond Bertini-numerical regime; overcomplete `r > min(n_i)` (overlap T#41); quantitative defective-stratum dimension counts.

## 3. Literature

**Foundational:** Kruskal (1977) *Linear Algebra Appl.* 18:95–138; Sidiropoulos–Bro (2000); Comon–Golub–Lim–Mourrain (2008) *SIMAX* 30(3):1254; Brachat–Comon–Mourrain–Tsigaridas (2010) *LAA* 433 (arXiv:0901.3706).

**Algebraic-geometric (P31, primary frontier):**
- Chiantini–Ottaviani (2012) *SIMAX* 33(3):1018 (arXiv:1103.2696).
- Bocci–Chiantini–Ottaviani (2014) *Annali di Matematica* 193:1691 (arXiv:1303.6915).
- Chiantini–Ottaviani–Vannieuwenhoven (2014) *SIMAX* 35(4):1265.
- Chiantini–Ottaviani–Vannieuwenhoven (2017) *SIMAX* 38(2):656 (arXiv:1609.00123).
- Chiantini–Ottaviani–Vannieuwenhoven (2017) *Trans. AMS* 369:4021 (arXiv:1504.00547).

**Domanov–De Lathauwer extensions:**
- Domanov–De Lathauwer (2013) *SIMAX* 34(3):876 (Part II).
- Domanov–De Lathauwer (2015) *SIMAX* 36(4):1567 (INDSCAL).
- Sørensen–De Lathauwer (2017) *LAA* 513:342.

**Recent constructive 2024–2025:**
- Koiran (2024) arXiv:2404.07801 — r ≤ 4n/3 for n×n×p, p ≥ 4; constructive algorithmic.
- Hadamard–Hitchcock identifiability arXiv:2308.06597 (2023).
- Deep polynomial NN identifiability arXiv:2506.17093 (2025).
- mathrepo MIS rank-3 algorithm (2025).

**Survey / textbook:** Landsberg *Tensors: Geometry and Applications* (AMS GSM 128); Kolda–Bader *SIAM Review* 51(3) (2009); Chiantini ed., *Decomposability of Tensors* (MDPI Books 2021).

**Software:** Macaulay2 packages `SecantVarieties`, ancillary `reshapedKruskal.m2` and `identifiabilityS4C4.m2` (CO-V 2017); Bertini and HomotopyContinuation.jl; TensorLy `parafac`; Tensorlab MATLAB toolbox; mathrepo MIS code.

## 4. Attack vectors

**4.1 P31 secant variety geometry — primary, substrate-grade.** Generic identifiability ⇔ tangential contact map injective ⇔ σ_r is non-defective in the strong "not weakly defective" sense (Chiantini–Ottaviani 2012). Terracini's lemma + weak-defectivity criterion. Substrate-friendly: certificates are explicit polynomial / linear-algebra computations.

**4.2 Reshaped Kruskal (CO-V 2017) — bridge between P15 and P31.** Reshape by grouping factor modes into supermodes, apply Kruskal in smaller-d setting, lift the conclusion. Effective for complex tensors in entire applicability range; for symmetric tensors, effective up to smallest typical rank in low order/dimension; optimal for 4×4×4×4 symmetric. Records as `ReshapingCertificate`.

**4.3 Domanov–De Lathauwer extensions — Kruskal-style, k-rank lower bounds.** Successive relaxations via further factor-matrix structure. Sharper SUFFICIENT conditions but inherit k-rank threshold.

**4.4 Constructive algorithmic uniqueness (Koiran 2024, mathrepo 2025).** Build explicit algorithm that, on input T, certifies uniqueness. Substrate-friendly because constructive: outputs `RankDecompositionWitness` with explicit factors + uniqueness flag, no "almost surely" hedge.

**4.5 Bertini / HomotopyContinuation.jl numerical witness uniqueness.** Count connected components of the secant-map fibre over [T] via numerical homotopy. Caveat: PATTERN_VRAM_TRUNCATION_ARTIFACT.

**4.6 Moduli-of-decompositions arguments (P25 / pivotal-negative).** Treat rank-r decompositions of T as moduli space; identifiability ⇔ moduli is a single point. Non-identifiability witnesses provide P25 instances.

**4.7 New attack-pattern flag (deferred from P32).** The Tier-B / Tier-D composition is itself an architectural pattern. Aporia notes this as a candidate cross-tier ARCHITECTURAL pattern (substrate primitive composition) rather than a problem-attack paradigm — recommend NOT promoting to P32; instead lock as substrate-design pattern.

## 5. Substrate encoding

**This is the fire #45 critical case — the encoding is structurally a Tier-B + Tier-D composition, not single-tier.**

**5.1 Tier-B `RankDecompositionWitness` (individual T):** fields `tensor`, `format`, `field`, `rank`, `decomposition: List<RankOneTensor>`, `uniqueness_flag ∈ {UNIQUE, FINITELY_MANY, INFINITE_FAMILY, UNKNOWN}`, `uniqueness_witness ∈ {KRUSKAL_CERT, RESHAPED_KRUSKAL_CERT, WEAK_DEFECTIVITY_CERT, DDL_CERT, KOIRAN_CONSTRUCTIVE_CERT, NUMERICAL_HOMOTOPY_CERT}`, `confidence ∈ {EXACT, NUMERICAL_CERTIFIED, NUMERICAL_HEURISTIC}`.

**5.2 Tier-D `GenericityAlmostEverywhereCert` (population/format):** fields `format`, `rank`, `property`, `measure_class ∈ {ZARISKI_OPEN_DENSE, EUCLIDEAN_FULL_MEASURE, BOTH}`, `exception_locus { type, explicit_components: List<ExceptionEntry>, codimension, measure_zero_status }`, `certification_method`, `bibliographic_anchor`.

**5.3 Cross-tier composition contract (the fire #45 finding):**
```
GenericIdentifiabilityClaim {
  format, rank,
  population_cert: GenericityAlmostEverywhereCert,
  individual_witness: RankDecompositionWitness,
  composition_type: TIER_B_AT_FIXED_PARAMS_PLUS_TIER_D_AT_FORMAT_LEVEL,
  consistency_axioms: [
    individual.format == population.format,
    individual.rank == population.rank,
    individual.tensor ∉ population.exception_locus,
    uniqueness_flag == UNIQUE ⇒ population.property includes UNIQUE_DECOMPOSITION
  ]
}
```
Substrate must reject claims that mix tier scopes (e.g. "this T is generically identifiable" — category error: generic identifiability is a *format* property, not a *tensor* property).

**5.4 CoordinateChart implications.** Reshaping (CO-V 2017) is literally a CoordinateChart change. Identifiability proven in reshaped chart MAY not lift cleanly to original chart — substrate must record `ReshapingCertificate.original_chart` and `ReshapingCertificate.reshaped_chart` separately and certify the lift.

**5.5 Capability-gap tickets:** `T-ST-fire45-001` (primary anchor), `T-ST-fire43-001` (sister cross-tier, T#73), `T-ST-fire38/39/40/41-001` (sibling Tier-B), `T-ST-fire42-002` (Aporia supplement). Proposed new: `T-ST-T40-001/002/003`.

## 6. Calibration anchor notes

**Substrate-grade response includes:**
- Kruskal 1977 stated correctly + flagged SUFFICIENT (not necessary) and specific (not generic).
- Names four channels (weak-defectivity CO 2012/BCO 2014, reshaped Kruskal CO-V 2014/2017, DDL extensions 2013–2017, constructive overcomplete Koiran 2024).
- Distinguishes specific vs generic identifiability.
- Explicitly cites exception list `(d,n,r) ∈ {(6,2,9),(4,3,8),(3,5,9)}`.
- Distinguishes CP / symmetric / multilinear / border / Hadamard–Hitchcock rank.
- Acknowledges PATTERN_BASE_RATE_NEGLECT for full-measure claims hiding the defective stratum.
- Frames identifiability as cross-tier (Tier-B + Tier-D composition).

**Textbook-trivial (FAIL):**
- "Kruskal's bound is the answer" (omits all post-1977 progress).
- "Solved by reshaping" (one bridge; misses weak defectivity + constructive overcomplete).
- "Symmetric and non-symmetric same conditions" (false; PATTERN_RANK_PARITY_LEAK).
- "Identifiable means unique decomposition exists" (conflates existence with uniqueness).

**Trivial-vs-open within identifiability family (FM-08 + PATTERN_RANK_PARITY_LEAK):**
- specific identifiability (one T) → solved algorithmically (Bertini, Koiran).
- generic identifiability (one format) → THIS REPORT (T#40), resolved for many formats, open for general d.
- symmetric specific → effective via reshaped Kruskal CO-V 2017, rank-3 closed.
- symmetric generic → AOP defectivity classification + CO-V 2017 subgeneric exception list.
- overcomplete → T#41 sister, partially closed by Koiran 2024.
- border-rank identifiability → distinct problem class (T#34/T#19).

**Pattern citations:**
- **PATTERN_BASE_RATE_NEGLECT:** generic-identifiability claims are full-measure; they exclude defective + unbalanced strata where structurally-interesting questions live.
- **PATTERN_RANK_PARITY_LEAK:** CP rank ≠ symmetric rank ≠ multilinear rank ≠ border rank ≠ Hadamard–Hitchcock rank.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT:** numerical-AG witnesses near defective stratum.

## 7. Cross-references

**Within `tensor_open_problems_v1.md`:**
- #38 (generic rank d ≥ 4: AOP defective list shared); #39 (maximal symmetric / Waring rank); **#41** (overcomplete CP: direct sister; Koiran 2024 r ≤ 4n/3 straddles T#40/T#41 boundary); **#42** (block-term decomposition); also #5, #18, #21, #26 (defective Segre-Veronese), #29 (regularity), #34 (border-rank membership — sister Tier-B), #43 (best rank-r — sister Tier-B), #56 (rank NP-hardness — sister Tier-B), #73 (tensor PCA threshold — sister Tier-B/Tier-D, the FIRST cross-tier composition).

**Within `attack_angle_taxonomy.md`:** P31 (primary), P15 (parent), P29 (dual), P09 (secondary), P25.

**Prior reports in batch:** `report_T1`; `report_T28`; `report_T34` (sister Tier-B); `report_T43` (sister Tier-B); `report_T56` (sister Tier-B); `report_T73` (sister cross-tier — first Tier-B + Tier-D realization); `report_T79`, `report_T84`, `report_T95`.

**Substrate-tester capability-gap tickets:** `T-ST-fire45-001` (primary anchor), `T-ST-fire43-001` (sister cross-tier composition), `T-ST-fire38/39/40/41-001` (siblings), `T-ST-fire42-002` (Aporia supplement). Proposed: `T-ST-T40-001/002/003`.

**Forward dependency for Techne T038 classification:** T#40 is the second-confirmation anchor for the Tier-B + Tier-D composition class. Together with T#73 it locks in the cross-tier composition primitive in the contract-change window. Refinements: (i) `MeasureZeroExceptionAnnotation` as first-class field on every Tier-D cert; (ii) `ReshapingCertificate` for chart-change auditability; (iii) cross-tier consistency axioms enforced at type-check.

---

*Aporia, 2026-05-09*
