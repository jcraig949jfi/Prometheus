# Report T#26 — Defective Segre-Veronese Varieties Classification

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §IV #26
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 2, fire-11)
**Substrate-tester linkage:** Tier-C `SecantVarietyEquation` / `MomentPolytope` meta-primitive
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_RANK_PARITY_LEAK
**Tags:** P31 (primary), P29 (dual framework), P15 (parent), P09 (computation), P25 (pivotal-negative-result); proposed candidate paradigms: **"Inductant" induction-witness construction** (Dolezalek-Ken 2025) and **"Multigraded fat-point Hilbert function tracking"**

---

## Brief summary

T#26 is the classification problem: enumerate ALL defective Segre-Veronese varieties — i.e., images of `SV_{(d_1,...,d_t)}: P^{n_1} x ... x P^{n_t} → P(S^{d_1}V_1 ⊗ ... ⊗ S^{d_t}V_t)` whose r-th secant variety `sigma_r` has dimension strictly less than the parameter count predicts. Sister to Alexander-Hirschowitz (1995, complete for pure Veronese) and Abo-Ottaviani-Peterson 2009 (pure Segre, balanced t<7 plus unbalanced asymptotic). **Major recent resolution: Abo-Brambilla-Galuppi-Oneto 2024 (arXiv:2406.20057) prove non-defectivity whenever every d_i ≥ 3**, by induction on (number of factors, degree, dimension) using the differential Horace method. Open frontier: cases with some d_i in {1,2}; in particular bidegree (1,2) was partially closed by **Dolezalek-Ken 2025 (arXiv:2503.21972) for n >> m^3, m ≥ 3** via the "inductant" construction. Maps to Tier-C SecantVarietyEquation + MomentPolytope companion. Heavy PATTERN_BASE_RATE_NEGLECT and PATTERN_CONDUCTOR_CONFOUND traps.

## Flagged findings

1. **Substrate gap:** Tier-C `SecantVarietyEquation` requires a new `DefectivityCertificate` dataclass with `MomentPolytope` companion — full schema in §5.
2. **Sister-classification cluster:** T#26, T#27, T#28, T#29 form a coupled Tier-C module that should land in one contract-change window.
3. **PATTERN_BASE_RATE_NEGLECT is the primary trap:** defective cases are EXCEPTIONAL; conflating "generic non-defective" with "always non-defective" is the canonical Learner failure mode. Classification IS the base-rate map.
4. **PATTERN_CONDUCTOR_CONFOUND:** defectivity concentrates in specific multidegree regimes (low d_i, unbalanced factor dimensions, low factor count); the multidegree IS the confounder. ABGO 2024 succeeds precisely because it restricts to `d_i ≥ 3`; the open frontier IS the confounded low-d_i regime.
5. **PATTERN_RANK_PARITY_LEAK:** "defective" means different things across rank notions (sigma_r-defective, generic-rank-defective, identifiability-defective, border-rank-defective, cactus-rank-defective). Substrate must record which.
6. **Two new ticket proposals:** `T-ST-T26-001` (DefectivityCertificate probe with VRAM-truncation compliance check) and `T-ST-T26-002` (MultidegreeBaseRate calibration probe).
7. **Two candidate new paradigms:** "Inductant" induction-witness construction (Dolezalek-Ken 2025) and "Multigraded fat-point Hilbert function tracking" — neither cleanly fits P29 or P31 alone.

## 1. Problem statement

Let `(n_1,...,n_t)`, `(d_1,...,d_t)` be positive integers; `V_i` a `(n_i+1)`-dim ℂ-vector space. The Segre-Veronese variety:

```
SV: P^{n_1} x ... x P^{n_t} → P(S^{d_1}V_1 ⊗ ... ⊗ S^{d_t}V_t)
([v_1],...,[v_t]) → [v_1^{d_1} ⊗ ... ⊗ v_t^{d_t}]
```

`dim(SV) = sum n_i`. Ambient `N = prod binom(n_i+d_i, d_i) - 1`. The r-th secant `sigma_r(SV)` is the closure of `(r-1)`-secant `(r-1)`-planes; **expected dimension** `min(r(sum n_i + 1) - 1, N)`. **Defective** if actual < expected; the gap is the **defect**.

**T#26: classify all `((n_i),(d_i),r)` with `sigma_r(SV)` defective.**

**Equivalent reformulations:**
- (P31, secant) Compute `dim sigma_r(SV)` via Terracini.
- (Fat-point) Defectivity ↔ generic union of r double points on `P^{n_1} x ... x P^{n_t}` failing independent conditions on multigraded line bundle `O(d_1,...,d_t)`.
- (P02, cohomological) Defectivity ↔ non-vanishing of specific `H^1` of fat-point ideal sheaf.
- (P29, multigraded apolar) Bounds existence of saturated B-invariant multigraded apolar Gorenstein schemes.

## 2. Status & bounds

| Result | Authors | Year | Coverage |
|---|---|---|---|
| Quadratic Veronese complete | Severi, Terracini | early 20th c. | complete |
| Clebsch's d=4, n=2 case | Clebsch | 1860 | first non-trivial |
| **Alexander-Hirschowitz (pure Veronese complete)** | Alexander, Hirschowitz | **1992-1995** | complete for t=1 |
| First systematic SV study | Catalisano, Geramita, Gimigliano | 2002-2008 | foundational |
| (P^1)^3 case complete | Catalisano-Geramita-Gimigliano | 2005 | subcase |
| **Pure Segre, balanced t<7 + unbalanced asymptotic** | Abo, Ottaviani, Peterson | **2009** | complete subrange (TAMS 361) |
| New defective examples (3-, 4-factor SV) | Abo, Brambilla | 2011 | discovery |
| Conjecturally complete two-factor SV list | Abo, Brambilla | 2013 | conjectural |
| Tangential of SV surfaces non-defective | Abo, Vannieuwenhoven | 2018 | subcase |
| Two-factor SV non-defective when both d_i ≥ 3 | Galuppi, Oneto | 2022 | subcase |
| **Full SV non-defective when all d_i ≥ 3** | Abo, Brambilla, Galuppi, Oneto | **2024** | major (arXiv:2406.20057) |
| Almost-optimal one d_i = 1, others ≥ 3 | ABGO | 2024 | corollary |
| **(1,2) bidegree non-defective for n >> m^3, m ≥ 3** | Dolezalek, Ken | **2025** | inductant method (arXiv:2503.21972) |
| Brambilla-Ottaviani modern reproof of A-H | Brambilla, Ottaviani | 2008 | clean reproof |

**Open frontier:**
1. Cases with `d_i in {1,2}` — particularly (1,2) bidegree below `n >> m^3` threshold; (1,1,...,1)/Segre tail.
2. Verification of full Abo-Brambilla 2013 conjectural list.
3. With ≥5 factors, are unbalanced cases the only defective? (Open in ABGO 2024.)
4. Sharp control of the *defect* (not just defectivity Y/N) in known defective cases.
5. Real-vs-complex defectivity classification.
6. Quantitative regularity bounds on fat-point ideals at defective points (T#29 link).

## 3. Literature

**Foundational:**
- Alexander, Hirschowitz (1995). *Polynomial interpolation in several variables*. J. Alg. Geom. 4(2):201-222.
- Brambilla, Ottaviani (2008). *On the Alexander-Hirschowitz theorem*. arXiv:math/0701409.
- Chandler (2002). TAMS 353(5):1907-1920.
- Postinghel (2012). Ann. Mat. Pura Appl. 191:77-94.

**Multi-factor Segre-Veronese:**
- Catalisano, Geramita, Gimigliano series (2002-2008).
- Abo, Ottaviani, Peterson (2009). *Induction for secant varieties of Segre varieties*. TAMS 361:767-792. arXiv:math/0607191.
- Abo, Brambilla (2011). *New examples of defective secant varieties of Segre-Veronese*. Coll. Math. 63:287-297. arXiv:1101.3202.
- Abo, Brambilla (2013). *On the dimensions of secant varieties of Segre-Veronese varieties*. Ann. Mat. Pura Appl. 192:61-92.
- Catalisano, Geramita, Gimigliano (2008). *SV varieties P^m × P^n embedded by O(1,2)*. arXiv:0809.4837.
- Bernardi, Carlini, Catalisano, Geramita, Gimigliano (2018). *Hitchhiker Guide to: Secant Varieties and Tensor Decomposition*. Mathematics 6(12):314.

**Recent (2022-2026):**
- Galuppi, Oneto (2022). *Secant non-defectivity via collisions of fat points*. arXiv:2104.02522.
- Araujo, Massarenti, Rischter (2019). *On non-secant defectivity of Segre-Veronese*. J. Algebra.
- Taveira Blomenhofer, Casarotti (2023). Improved non-defectivity bounds.
- Ballico (2024). Math. Z., DOI 10.1007/s00209-024-03573-x.
- **Abo, Brambilla, Galuppi, Oneto (2024).** *Non-defectivity of Segre-Veronese varieties*. Proc. AMS Ser. B 11. arXiv:2406.20057.
- **Dolezalek, Ken (2025/2026).** arXiv:2503.21972.

**Identifiability cross-link (T#40):**
- Chiantini, Ottaviani, Vannieuwenhoven (2014). SIAM J. Matrix Anal. Appl. arXiv:1403.4157.
- Chiantini, Ottaviani (2012). On generic identifiability of 3-tensors of small rank.

**Tools:** Macaulay2 (`TerraciniLoci`, `MultiprojectiveVarieties`, `SchurRings`, `Apolarity`); Bertini, HomotopyContinuation.jl; Sage/Singular; PHCpack; TensorLy.

## 4. Attack vectors active in the literature

**4.1 P31 secant-variety geometry — primary.** Terracini's lemma + Hilbert function of generic union of r double points on the multiprojective space. Substrate-friendly: certificates are CONSTRUCTIVE.

**4.2 P02 cohomological-vanishing (T#27 input).** Postinghel-style: prove H^1 vanishes via Künneth-type splittings.

**4.3 Differential Horace method — recursive engine.** Specialize fat points onto a divisor; track residual scheme; recurse. ABGO 2024 induction is on (t, sum d_i, sum n_i).

**4.4 P29 multigraded border apolarity.** Buczyńska-Buczyński 2021 framework adapted to multigraded setting.

**4.5 P09 exhaustive computer-assisted verification.** Macaulay2 `TerraciniLoci` package — randomized Jacobian-rank algorithm. Bertini / HomotopyContinuation.jl provide numerical witness sets.

**4.6 Schur-functor / representation theory.** Ambient representation has `prod GL(V_i)`-action; defining ideal of `sigma_r` is equivariant; representation-theoretic decomposition reduces dim counts to combinatorial multiplicities.

**4.7 Toric / Newton-polytope methods.** Laface-Postinghel toric degeneration. Multidegree (d_1,...,d_t) defines a Newton polytope; defectivity detectable from polytope-combinatorial conditions.

**4.8 Conjecture-driven: Abo-Brambilla 2013 list.** Conjecturally complete catalog of two-factor defective cases.

**4.9 NEW ATTACK PATTERNS — candidates for taxonomy expansion:**
- **"Inductant" induction-witness construction (Dolezalek-Ken 2025).** Generalizes Brambilla-Ottaviani's induction template by encoding it as a single explicit construction whose verification reduces to finite computer-assisted base cases.
- **"Multigraded fat-point Hilbert function tracking."** Substrate-grade because every step is a numeric Hilbert-function value; no cohomological black box. Could become canonical Tier-C `SecantVarietyEquation` certificate type.

## 5. Substrate encoding

Tier-C `SecantVarietyEquation` (primary) + `MomentPolytope` (companion).

**Proposed `DefectivityCertificate` dataclass:**

```
DefectivityCertificate {
  family:                {SEGRE, VERONESE, SEGRE_VERONESE, GRASSMANNIAN_PLUCKER}
  factor_dims:           List<Integer>          // (n_1, ..., n_t)
  multidegree:           List<Integer>          // (d_1, ..., d_t)
  num_factors:           Integer
  ambient_dim_N:         Integer
  expected_dim_sigma_r:  Integer
  actual_dim_sigma_r:    Integer
  defect_delta:          Integer                // expected - actual; >0 ⇒ defective
  rank_r:                Integer

  status:                {NON_DEFECTIVE, DEFECTIVE, OPEN, OPEN_AT_THIS_PRECISION}

  witness_type:          {
    TERRACINI_JACOBIAN,
    FAT_POINT_HILBERT,
    COHOMOLOGICAL_VANISHING,
    HORACE_INDUCTION,
    INDUCTANT,                                  // Dolezalek-Ken
    APOLAR_GORENSTEIN_MULTIGRADED,
    EXPLICIT_DECOMPOSITION_FAMILY,
    COMPUTER_ALGEBRA_CERTIFIED,
    UNRESOLVED
  }

  terracini_witness:        optional<{
    point_data:             List<MultiHomogeneousPoint>
    jacobian_matrix:        Matrix
    jacobian_rank:          Integer
    precision_floor:        Float                  // VRAM_TRUNCATION_ARTIFACT compliance
    randomization_seed:     Integer
  }>

  fat_point_witness:        optional<{
    fat_point_scheme:       MultigradedSubschemeOfPnProduct
    multiplicity:           Integer
    hilbert_function_value: Integer
    expected_value:         Integer
    h1_value:               Integer
  }>

  horace_log:               optional<{
    specialization_steps:   List<HoraceStep>
    base_case_evidence:     List<DefectivityCertificate>
    induction_invariant:    String                 // (t, |d|, |n|) ordering
  }>

  inductant_witness:        optional<{
    inductant_object:       AlgebraicGeometricObject
    base_cases:             List<DefectivityCertificate>
    computer_verification:  ComputerAlgebraTrace
  }>

  defective_decomposition_family: optional<{
    parameterization:       AlgebraicMap
    proof_of_lower_dim:     CohomologicalArgument
  }>

  moment_polytope:          MomentPolytope         // companion primitive
  schur_functor_data:       optional<List<(YoungDiagram, Multiplicity)>>

  field:                    {C, R, Q}
  real_vs_complex_note:     optional<String>

  references:               List<CitationKey>
  canonical_attribution:    {AH95, AOP09, AB13, GO22, ABGO24, DK25, ...}
}
```

**Composition with sister primitives:**
- `DefectivityCertificate` IS the primary input/output of Tier-C `SecantVarietyEquation`.
- Composes with `BorderRankWitness` (T#34): membership decisions are NON-TRIVIAL precisely on defective stratum.
- Composes with `LimitWitness` (T#43): de Silva-Lim ill-posedness concentrates on defective loci.
- Composes with `IdentifiabilityCertificate` (T#40): non-defectivity is necessary but not sufficient for generic identifiability.
- Coordinates with `SpecialLineBundleCertificate` (T#27), `TerraciniLocusCertificate` (T#28), `RegularityCertificate` (T#29).

**MomentPolytope companion:** multidegree `(d_1,...,d_t)` defines a Newton polytope stored as the structural-region coordinate distinguishing Segre-Veronese families.

**Capability-gap tickets:**
- Sister fire #41 cluster (T#34 `BorderRankWitness`) is upstream consumer.
- Sister fire #45 cluster (T#40 identifiability) is downstream consumer.
- **Proposed new** `T-ST-T26-001` — `DefectivityCertificate` probe.
- **Proposed new** `T-ST-T26-002` — `MultidegreeBaseRate` calibration probe.

## 6. Calibration anchor notes

**Substrate-grade response on T#26 must:**
- Distinguish Veronese (t=1, A-H complete) from pure Segre (AOP 2009 partial) from Segre-Veronese (multi-factor, ABGO 2024 closes d_i ≥ 3).
- Cite ABGO 2024, Alexander-Hirschowitz 1995, AOP 2009, Abo-Brambilla 2013.
- Acknowledge classification IS NOT COMPLETE: low-degree (d_i in {1,2}) cases partially open.
- Acknowledge differential Horace method as unifying engine.
- State Terracini's lemma + multigraded fat-point Hilbert function as canonical translation.
- Acknowledge defectivity is structurally rare and concentrated in low-degree / unbalanced regimes.

**Textbook-trivial responses (FAIL):**
- "All SV non-defective except a finite list." — wrong; some infinite families defective.
- "Just compute the Terracini Jacobian." — substrate-tester catches this as ignoring family structure.
- "Defectivity = no generic identifiability." — RANK_PARITY_LEAK; they're distinct in general.
- "Alexander-Hirschowitz solved this." — solved t=1 only; multi-factor IS T#26.
- "Use the Abo-Brambilla list." — conjecturally complete only for two-factor SV.

**Trivial-vs-open within classification (FM-08 + PATTERN_RANK_PARITY_LEAK):**
- Pure Veronese (t=1): A-H 1995, **CLOSED**.
- Pure Segre balanced t<7: AOP 2009, **CLOSED**.
- Pure Segre balanced t≥7: **OPEN**.
- Pure Segre unbalanced asymptotic: AOP 2009, **CLOSED**.
- Two-factor SV both d≥3: Galuppi-Oneto 2022, **CLOSED**.
- Multi-factor SV all d_i≥3: ABGO 2024, **CLOSED** (recent landmark).
- Multi-factor SV some d_i=1: ABGO corollary covers (1,≥3,...,≥3); rest **OPEN**.
- Multi-factor SV some d_i=2: **MOSTLY OPEN**; defective examples known.
- O(1,2) bidegree: DK 2025 closes asymptotic regime; finite exceptions need verification.
- Real-vs-complex: **OPEN**.
- ≥5 factors "are unbalanced cases the only defective?": **OPEN** (raised in ABGO 2024).
- Identifiability defectivity vs secant defectivity: distinct (cross-ref T#40).

**Pattern citations:**
- **PATTERN_BASE_RATE_NEGLECT (primary).** Defective cases are exceptional; "generic" ≠ "always." Classification IS the base-rate map.
- **PATTERN_CONDUCTOR_CONFOUND.** Multidegree is the confounder; results stated "generally" without restricting multidegree are mis-scoped.
- **PATTERN_RANK_PARITY_LEAK.** "Defective" means different things across rank notions.

**Canonical attribution at risk:** Major canonical authors: J. Alexander, A. Hirschowitz, H. Abo, G. Ottaviani, C. Peterson, M. C. Brambilla, F. Galuppi, A. Oneto, M. V. Catalisano, A. T. Geramita, A. Gimigliano, E. Ballico, M. Mella, M. Postinghel, C. Raicu. Common Learner fabrications: (a) attributing ABGO 2024 to one author — it's a four-author paper; (b) attributing conjectural list to wrong name — it's specifically Abo-Brambilla 2013; (c) confusing AOP 2009 (pure Segre) with ABGO 2024 (Segre-Veronese); (d) inflating A-H to claim it covers Segre-Veronese — it does not.

## 7. Cross-references

**Within `tensor_open_problems_v1.md`:**
- **#21** — symmetric Waring rank, A-H extensions; T#26's pure-Veronese face.
- **#27** — special line bundles; UPSTREAM coupling (cohomological-vanishing input).
- **#28** — Terracini loci; SCHEME-THEORETIC REFINEMENT.
- **#29** — regularity of minimal apolar schemes; bounds cohomological-vanishing range.
- **#30** — GADs; DOWNSTREAM.
- **#31** — defining equations; DOWNSTREAM.
- **#33** — singularities of `sigma_r`; concentrate near defective stratum boundaries.
- **#38** — generic rank d≥4; DOWNSTREAM CONSUMER.
- **#40** — generic CP identifiability; STRONG COUPLING.
- **#43** — de Silva-Lim ill-posedness; INTERACTION.
- **#34** — border-rank membership; TIER-B ADJACENT.
- **#22, #39** — specific-form / maximal Waring rank.

**Within `attack_angle_taxonomy.md`:** P31 (primary), P29 (dual), P02 (cohomological), P15 (parent), P09 (computation), P25 (negative-result). Candidates for new paradigms: inductant-witness, multigraded fat-point Hilbert tracking.

**Prior reports in batch:** T#1, T#28, T#34 (sister Tier-B), T#43, T#56, T#79, T#84, T#95.

**Substrate-tester capability-gap tickets:**
- Proposed `T-ST-T26-001` (DefectivityCertificate probe + VRAM-truncation compliance).
- Proposed `T-ST-T26-002` (MultidegreeBaseRate calibration probe).
- Sibling fires: `T-ST-fire41-001` (T#34), `T-ST-fire45-001` (T#40).

**Forward dependency for Techne T038 classification:** T#26 is THE foundational Tier-C `SecantVarietyEquation` calibration anchor. The proposed `DefectivityCertificate` should land in the same contract-change window as BorderRankWitness, LimitWitness, ComputationalComplexityCertificate. Without T#26 properly encoded, Tier-C primitives cannot distinguish "valid generically" from "valid always" — the substrate-grade discipline that distinguishes calibration-anchor outputs from textbook-trivial ones.

**Sources:**
- arXiv:2406.20057 — ABGO (2024), Non-defectivity of SV
- arXiv:2503.21972 — Dolezalek-Ken (2025), inductant for (1,2) bidegree
- arXiv:1101.3202 — Abo-Brambilla (2011), new defective examples
- arXiv:math/0607191 — AOP (2009), induction for SV secants
- arXiv:math/0701409 — Brambilla-Ottaviani (2008), modern A-H reproof
- Abo-Brambilla (2013), Ann. Mat. Pura Appl. 192:61-92
- arXiv:2104.02522 — Galuppi-Oneto, fat-point collisions
- Bernardi-Carlini-Catalisano-Geramita-Gimigliano (2018), Hitchhiker Guide

---

*Aporia, 2026-05-09*
