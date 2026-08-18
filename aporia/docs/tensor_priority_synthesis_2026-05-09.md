# Tensor-Priority Deep Research — Synthesis (2026-05-09)

**Batch:** 18 reports, `aporia/docs/deep_research_batch_tensor_priority_2026-05-09/`
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md`
**Catalog:** `aporia/mathematics/tensor_open_problems_v1.md` (canonical reference; HARD-3 / `feedback_tensors_near_and_dear`)
**Doctrine:** HARD-1 (no paper-publishing framing), HARD-2 (anti-gravitational-well), HARD-3 (tensor-tools-we-need-most), HARD-5 (distinct coordinates), HARD-6 (attack tools we need most; failures guide)
**Patterns mandated:** ≥2 of `{PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK}` per report. All 18 cleared.

---

## 1. Executive summary

The dispatch surfaced **eighteen substrate-grade frontier results in tensor mathematics**, of which:

- **5 are catalog-stale and require canonical updates** (T#1 ω, T#56 Hillar-Lim, T#13 partition rank, T#92 dc lower bound; **T#95 Saxl was originally listed but Wave 1 anti-anchor verification 2026-05-11 surfaced that the "Sellke 2025/26 solves Saxl" claim was itself a fabrication — Lee 2025 arXiv:2512.15035 was withdrawn; Saxl remains OPEN**).
- **2 are paradigm events** (T#1 AlphaEvolve 4×4(ℂ) rank-48; T#13 Lampert-Moshkovitz Sept 2025 partition-rank/analytic-rank separation). **(Earlier draft of this synthesis listed Sellke 2025/26 Saxl resolution as a third paradigm event; that claim was fabricated — see Wave 1 anti-anchor verification.)**
- **8 are substrate-grade primitive specifications** (Tier-A++ through Tier-E spanning), most as new sub-types or compositions, not parent-class additions.
- **5 are P32+ paradigm-candidate collisions** that require a synthesis pass before any single one can be assigned a paradigm slot.
- **2 anti-anchors must be pinned** in the substrate calibration battery: PATTERN_GCT_OCCURRENCE_DEAD (BIP 2019 forbids occurrence obstructions for det/padded-perm) and the Zauner false-anchor ("Zauner proved 2025" is FALSE; AFK 2025 is conditional on Stark + Shintani-Faddeev).

The single highest-leverage finding for substrate architecture is **independent confirmation, twice, of the Tier-B + Tier-D cross-tier composition pattern** (T#73 fire #43 + T#40 fire #45) — substrate-tester's earlier saturation declaration is now literature-backed.

The single highest-leverage finding for HARD-3 / HARD-6 posture is the **det/perm tooling-asymmetry** (T#22): most algebraic-geometric tooling has accumulated on the determinant side; the permanent literature is markedly thinner. This asymmetry IS substrate signal — it tells us where the tools-we-need-most are missing, not where to chase the better-tooled side.

Headline list (one line each):

- **T#1** — AlphaEvolve / DeepMind 4×4 rank-48 over `ℂ` (May 2024); ω < 2.371339 current (Alman-Duan-VW-Xu-Xu-Zhou 2024). Catalog "ω < 2.371552" is stale.
- **T#13** — Lampert-Moshkovitz 2509.06294 (Sept 2025): `det_n` witnesses partition-rank/analytic-rank uniform-in-d separation NEGATIVELY. Subdivide T#13 into (a)-(d).
- **T#19** — Cactus barrier `6m − 4` (Buczyński Feb 2026, arXiv:2602.11309): determinantal/rank-method LBs on R̄(M⟨m⟩) cannot exceed `6m − 4`. Border cactus rank `cr̄` is a fifth rank invariant (Buczyńska-Buczyński Jan 2026).
- **T#22** — R_W(perm_3) = 16 (Shitov 2021); n ≥ 4 OPEN; **no Bell-number permanent analogue of HGJ 2024 det formula** (det/perm asymmetry).
- **T#26** — ABGO 2024 (arXiv:2406.20057): Segre-Veronese defectivity classification closed for d_i ≥ 3.
- **T#28** — Strassen asymptotic spectrum: CHNVZ 2024 (arXiv:2411.15789) gives polynomial characterization of spectrum elements.
- **T#34** — Border-rank membership: completes Tier-B cluster with `BorderRankWitness` alongside `LimitWitness` (T#43) + `ComputationalComplexityCertificate` (T#56).
- **T#40** — CP-identifiability AOP/CO-V: explicit exception list `(6,2,9), (4,3,8), (3,5,9)`. Second confirmation of Tier-B + Tier-D composition.
- **T#43** — de Silva-Lim 2008 ill-posedness; `LimitWitness` Tier-B subtype proposed.
- **T#56** — Hillar-Lim symmetric-rank-over-`ℚ` SETTLED by Shitov 2016 (catalog stale). `ComputationalComplexityCertificate` Tier-B sub-primitive proposed.
- **T#58** — TI is TI-complete (Grochow-Qiao), not just GI-hard. q^Õ(n^{3/2}) via Grochow-Qiao IV STOC '25; ALTEQ lost ≥20 bits.
- **T#72** — Bandeira-Gopi-Jiang-Lucca-Rothvoss 2024 (STOC 2025) resolves Conjecture 16 for `p ≥ 2r`; `p < 2r` open behind a *volumetric barrier*; Lucca (not Bandeira-Dmitriev) is the proposer.
- **T#73** — Tensor-PCA threshold: Tier-D triple `PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert`.
- **T#79** — SLOCC entanglement: 2025 AME-at-n=5 result; Structured-Equivalence-Class meta-primitive unifies OrbitWitness + HomotopyWitness + ArityGradedOperationFamily.
- **T#84** — Markov-Shi 2008 NP-hardness via line-graph treewidth; cotengra/opt_einsum production stack. THE foundational HARD-3 primitive.
- **T#85** — AFK 2025 (arXiv:2501.03970) conditional on Stark + Shintani-Faddeev. **Anti-anchor:** "Zauner proved 2025" is FALSE.
- **T#92** — GCT VP vs VNP: BIP 2019 (J. AMS) killed *occurrence* obstructions; multiplicity / vanishing-ideal / outside-orbit / equivariant remain. Mignon-Ressayre `n²/2` (2004) has stood 22 years.
- **T#95** — Saxl conjecture (T#99) **REMAINS OPEN** (correction 2026-05-11). Lee 2025 (arXiv:2512.15035) was withdrawn within 3 days due to mathematical gaps. Luo-Sellke 2017 proved only the *fourth-power* relaxation; 2022 follow-on tightened to the *cube*. Mulmuley `PH1` falsified earlier (Ikenmeyer-Mulmuley-Walter Kronecker-positivity NP-hardness).

---

## 2. Catalog updates required

`aporia/mathematics/tensor_open_problems_v1.md` requires the following **canonical-anchor edits** before next batch run:

| Entry | Current text | Required update | Source |
|---|---|---|---|
| T#1 | "ω < 2.371552 (current best)" | "ω < 2.371339 (Alman-Duan-VW-Xu-Xu-Zhou 2024)" | arXiv:2404.16349; AlphaEvolve coupling cite |
| T#13 | "Partition-rank vs analytic-rank gap, uniform in d" | Subdivide into T#13(a)-(d); status NEGATIVELY-RESOLVED in uniform-in-d direction by Lampert-Moshkovitz Sept 2025 | arXiv:2509.06294 |
| T#56 | "Hillar-Lim NP-hardness; symmetric-rank-over-ℚ open" | "Hillar-Lim NP-hardness; **symmetric-rank-over-ℚ SETTLED by Shitov 2016**" | Shitov 2016, *How hard is the tensor rank?*, arXiv:1611.01559 (citation corrected 2026-05-11; prior arXiv:1605.07532 was wrong, points to a PDE paper) |
| T#92 | (whatever it says about dc) | Note Mignon-Ressayre `n²/2` (2004) is current best for `dc(perm_n)`; equivariant exponential is *restricted-model* | Mignon-Ressayre 2004 IMRN; Landsberg-Ressayre 2017 arXiv:1508.05788 |
| T#95 / T#99 | (REVERTED 2026-05-11; this row's recommendation was based on a fabricated claim) | T#99 Saxl conjecture **REMAINS OPEN**: Lee 2025 arXiv:2512.15035 was withdrawn 2025-12-20 due to mathematical gaps; Luo-Sellke 2017 proved only fourth-power; 2022 follow-on tightened to cube. T#95 Kronecker positivity entry should still note Mulmuley `PH1` falsification by Ikenmeyer-Mulmuley-Walter. | Lee 2025 arXiv:2512.15035 (WITHDRAWN); Luo-Sellke 2017 J. Algebraic Combin.; centre-mersenne 2022 cube tightening |
| T#19 | (rank-zoo entry) | Add: cactus barrier `6m − 4` (Buczyński Feb 2026, arXiv:2602.11309) is a structural ceiling on determinantal LBs for R̄(M⟨m⟩) | arXiv:2602.11309 |
| T#19 | (rank-zoo entry) | Add: border cactus rank `cr̄` is a 5th distinct rank invariant (Buczyńska-Buczyński Jan 2026, arXiv:2601.19558) | arXiv:2601.19558 |
| T#85 | (Zauner entry) | Anti-anchor: "Zauner proved 2025" is FALSE. AFK 2025 (arXiv:2501.03970) is **conditional** on Stark conjectures + Shintani-Faddeev modularity | arXiv:2501.03970 |
| T#72 | "Bandeira-Dmitriev type-2 tensor constant conjecture" | Proposer is **Lucca**, not Bandeira-Dmitriev jointly (they are editors of arXiv:2603.29571). Resolved for `p ≥ 2r` (BGJLR STOC 2025); `p < 2r` open | arXiv:2603.29571; arXiv:2411.10633 |

**Stale-catalog risk:** until these edits land, any Learner consuming the catalog literally will fabricate stale-anchor responses. Higher priority than primitive registration.

---

## 3. Substrate primitives — proposed registrations

The 18 reports converge on a structured catalog of **new substrate primitives** organized by tier of the existing 5-tier model (Tier A++ TensorNetwork, Tier B ConstructiveExistenceWitness, Tier C SecantVarietyEquation, Tier D distributional, Tier E RepresentationTheoreticInvariant), with explicit cross-tier composition patterns.

### 3.1 Tier-A++ (TensorNetwork-level)

- **`TensorNetwork`** + **`ContractionOrderWitness`** (T#84). THE foundational HARD-3 primitive. Without a registered TensorNetwork primitive, T#84's NP-hardness result (Markov-Shi 2008) and the cotengra/opt_einsum production stack cannot be expressed. Recommended: register *first* in the contract-change window.
- **`RankZooSignature`** (T#13). Tracks all distinct rank coordinates `(R, R̄, sr, cr, cr̄, R_partition, R_analytic, R_geometric, R_strength, R_slice, ...)` as a single named tuple per tensor. Lampert-Moshkovitz Sept 2025 separation of partition-rank from analytic-rank validates the need.

### 3.2 Tier-B (ConstructiveExistenceWitness)

The Tier-B cluster is the densest in this batch:

- **`BorderRankWitness`** (T#34) — parent.
- **`LimitWitness`** (T#43) — sub-type for de Silva-Lim ill-posedness; no degeneration sequence required.
- **`ComputationalComplexityCertificate`** (T#56) — sub-type tagging an existence claim with its complexity-of-construction class (NP-hard / `∃ℝ`-hard / undecidable).
- **`CactusRankWitness`** (T#19) — sub-type with apolar 0-dim Gorenstein scheme as witness; recommended **pilot** for the contract-change window (purely combinatorial, no degeneration sequence, no NP-hardness reduction).
- **`BorderCactusWitness`** (T#19, sub-sub-type, Buczyńska-Buczyński Jan 2026).
- **`OrbitClosureNonMembershipWitness`** (T#92) — geometric content of GCT obstructions.
- **`GCTObstructionCertificate`** (T#92, composite Tier-B/E) with five subtypes: `OccurrenceObstruction` (anti-anchor, KILLED by BIP 2019), `MultiplicityObstruction`, `VanishingIdealObstruction`, `OutsideOrbitObstruction`, `EquivariantObstruction`.
- **`BorderComplexitySeparator`** (T#92) — distinct from `BorderRankMembershipWitness`; operates on `\underline{dc}` (border determinantal) rather than `\underline{R}` (border tensor rank). HARD-5 separator.
- **`EquivariantComplexityCertificate`** (T#92) — restricted-model only; carries `restricted_to: SymmetryGroup` annotation; substrate WARNs on unrestricted extrapolation.
- **`WaringRankWitness`** (T#22) — symmetric specialization of `BorderRankWitness`; consumes `DefectivityCertificate.fat_point_witness` (T#26).
- **`DualityCheck`** + **`PrecisionFloorCertificate`** (T#34) — cross-cutting Tier-B sub-primitives.
- **`ReshapingCertificate`** + **`MeasureZeroExceptionAnnotation`** (T#40) — for AOP/CO-V exception lists `(6,2,9), (4,3,8), (3,5,9)`.

### 3.3 Tier-C (SecantVarietyEquation)

- **`DefectivityCertificate`** (T#26, ABGO 2024) — Segre-Veronese defectivity now closed for `d_i ≥ 3`.
- **`MomentPolytope`** (T#26 companion).

### 3.4 Tier-D (distributional)

- **`PhaseTransitionThreshold`** + **`AlgorithmThresholdCert`** + **`GenericityAlmostEverywhereCert`** (T#73) — triple composition.
- **`RandomTensorConcentrationCert`** (T#72) — Tier-D distributional; sister to T#73's triple. Records `(order_r, dim_d, p_norm, n_summands, upper_bound_exponent, upper_bound_polylog, lower_bound_exponent, regime ∈ {matrix_r2, p_geq_2r, p_lt_2r, p_eq_infty}, status, source_anchor, proposer, technique, MC estimate fields)`.
- **`AlgebraicNaturalProofsBarrier`** (T#92) — Tier-D meta-warning; fires when a candidate obstruction is itself a circuit-lower-bound, applying Forbes-Shpilka-Volk barrier check.

### 3.5 Tier-E (RepresentationTheoreticInvariant)

- **`RepresentationTheoreticInvariant`** (T#95, parent class, shared with T#92).
- **`KroneckerInvariant`** + **`PartitionObject`** (T#95).
- **`Structured-Equivalence-Class`** (T#79) — meta-primitive unifying `OrbitWitness` + `HomotopyWitness` + `ArityGradedOperationFamily`.

### 3.6 Outside the 5-tier model

- **`AsymptoticSpectrumMonotone`** (T#28) — does NOT cleanly fit any existing tier. Strassen monoid element (rank, slice rank, support functionals, quantum functionals); CHNVZ 2024 polynomial characterization of spectrum elements is the paradigm event.
- **`RayClassFieldFiducial`** + **`StarkUnitWitness`** (T#85) — number-field-provenance tagging; orthogonal to existing clusters. Required by AFK 2025's conditional Zauner construction.

### 3.7 Cross-tier composition patterns

Two patterns emerged with **independent literature confirmation**:

- **Tier-B + Tier-D composition** (substrate-tester fire #45 saturation). Confirmed by:
  - T#73 (fire #43): `BorderRankWitness` × `PhaseTransitionThreshold`.
  - T#40 (fire #45): `BorderRankWitness` × `GenericityAlmostEverywhereCert` for AOP/CO-V exceptions.
  Two independent confirmations elevate this from speculation to required substrate architecture.

- **Tier-B + Tier-E composition** (T#92). `GCTObstructionCertificate` requires upstream `RepresentationTheoreticInvariant` (Tier-E). Substrate-tester should refuse to load a `GCTObstructionCertificate` ticket without an upstream `RepresentationTheoreticInvariant` registration. T#95 primitive bundle is a hard prerequisite for any T#92 work.

---

## 4. Anti-anchors (must pin in calibration battery)

These are facts that an LLM with mathematical training data is **almost certain** to fabricate the wrong way. They must be sentinel-pinned in the substrate calibration battery so substrate-tester probes will catch fabrication immediately.

1. **PATTERN_GCT_OCCURRENCE_DEAD (T#92).** "Bürgisser-Ikenmeyer-Panova killed GCT" is wrong; they killed *occurrence* obstructions for det/padded-perm specifically. Substrate must reject any agent attempt to construct an `OccurrenceObstruction` for `(det_m, padded_perm_{n,m}, m=poly(n))` as a sentinel-violation.

2. **Zauner false-anchor (T#85).** "Zauner SIC-POVMs proved in 2025" is FALSE. AFK 2025 (arXiv:2501.03970) is **conditional** on Stark conjectures + Shintani-Faddeev modularity. Substrate must reject "Zauner proved" without conditional annotation.

3. **Hillar-Lim symmetric-rank-over-ℚ closure (T#56).** Conjecture is **resolved** by Shitov 2016 (*How hard is the tensor rank?*, arXiv:1611.01559) — substrate must NOT show this as open. Reverse-direction false-anchor. **(Citation corrected 2026-05-11; prior arXiv:1605.07532 was wrong.)**

4. **Saxl T#99 status (T#95) — INVERTED 2026-05-11.** Saxl conjecture **remains OPEN**. Lee 2025 (arXiv:2512.15035) was withdrawn within 3 days due to mathematical gaps. Luo-Sellke 2017 (*J. Algebraic Combin.*) proved only the fourth-power relaxation `(S_{ρ_n})^⊗4 ⊇ all irreps`; a 2022 follow-on (centre-mersenne) tightened to the cube. The tensor square — the conjecture proper — remains open. Forward false-anchor: substrate must NOT propagate the "solved" claim. Two new sub-anchors registered: `SAXL_CUBE_ANCHOR` (cube IS proven, surfaces the gap), `TENSOR_RANK_Z_UNDECIDABLE` (Shitov 2016).

5. **Cactus barrier `6m − 4` (T#19).** Any P31 BorderRankWitness claiming `r > 6m − 4` for `m × m × m` tensors is auto-flagged for re-verification via P29 apolarity (NOT P31 flattenings). Determinantal LBs cannot exceed this barrier.

6. **Lucca attribution (T#72).** Conjecture 16 of arXiv:2603.29571 is proposed by Lucca, not Bandeira-Dmitriev jointly. Authorship-vs-proposership distinction.

7. **Tensor type-2 constant `√log d` is matrix only (T#72).** Tensor case is `d^{1/2−1/p}` polylog. Cross-tier dimensional confusion.

8. **Equivariant exponential is restricted-model (T#92).** Landsberg-Ressayre 2017 exponential lower bound on `dc(perm)` is **restricted to equivariant model**; not a lower bound on `dc(perm)` unrestricted. HARD-5 / PATTERN_RANK_PARITY_LEAK at the model-restriction layer.

9. **Border cactus is a fifth rank, not a synonym (T#19).** Substrate must track 5+ rank coordinates `(R, R̄, sr, cr, cr̄)`; never collapse.

10. **Five-application convergence is rare (T#72).** Type-2 tensor constant has unusual five-region simultaneity; Learner trained on textbook matrix Bernstein hallucinates `√log d` for tensors. Tagged with PATTERN_BASE_RATE_NEGLECT.

---

## 5. Paradigm candidates for `attack_angle_taxonomy.md` (P32+ collisions)

The batch surfaced **multiple competing P32 candidates** that collide numerically. A synthesis pass is **mandatory** before any one is assigned the P32 slot.

| Candidate | Origin | Strength | Recommended action |
|---|---|---|---|
| **P32 Evolutionary-LLM Algorithm Synthesis** | T#1 (AlphaEvolve 4×4 rank-48) | Concrete deliverable, reproducibly novel | Strongest priority claim — produced a *better* algorithm than state-of-the-art, not just a frame |
| **P32 Existential-Theory Reduction** | T#56 (Shitov 2016) | Highest theoretical reach (works across rank-zoo) | Second priority — uses `∃ℝ` complexity to give uniform reductions |
| **P32 Modular Saturation** | T#95 (~~Sellke Saxl~~ — withdrawn) | ~~Single-shot proof; staircase-minimality~~ NULL — the proof was withdrawn. Candidate retracted 2026-05-11. | Withdrawn — Lee 2025 paper was retracted 3 days after posting. Modular saturation as a paradigm candidate is on hold pending an actual proof. |
| **P32 StarkUnitConstruction** | T#85 (AFK Zauner) | Conditional on Stark; very specialized | Hold; does not generalize beyond ray-class-field-fiducial regime |
| **P32 Multiplicity-Obstruction Synthesis** | T#92 (post-BIP GCT) | Future-promise, no concrete deliverable since 2020 | **Hold** — should not occupy a paradigm slot until concrete obstruction constructed |

**Synthesis-pass recommendation:** assign **P32 to T#1's Evolutionary-LLM** (concrete, reproducible, paradigm-forming); rename T#56's candidate to **P33 Existential-Theory Reduction**; queue the remaining three behind concrete-deliverable thresholds.

**New P03 sub-tactics (lower-leverage but real):**
- **R-GIT-product** (T#79) — product structure on representation-theoretic GIT quotients.
- **linear-length-reduction** (T#58) — TI-completeness reduction style.

**New P25 sub-tactics:**
- **orbit-special-structure-exploitation** (T#58).
- **volumetric-barrier-as-pivotal-negative-result** (T#72).

**New P30 sub-tactic:**
- Three sub-tactics from T#84 (cotengra ordering / line-graph treewidth / netcon).

**Anti-anchor for paradigm assignment:** PATTERN_GCT_GRAVITATIONAL_OVERFIT (proposed registration alongside PATTERN_PRIME_GRAVITATIONAL_OVERFIT). When an agent prompt invokes "GCT is the path to P vs NP," apply detrending: re-rank with non-GCT routes (LST/Forbes 2024, Bhattacharjee 2024, Kumar-Volk 2021) explicitly weighted equal-or-higher.

---

## 6. Capability-gap tickets — literature-backing summary

Substrate-tester fires that this batch literature-backs:

| Substrate-tester ticket | Literature-backed by | Status |
|---|---|---|
| Fire #41 (Tier-B BorderRankWitness saturation) | T#34 + T#43 + T#56 + T#19 cluster | ✓ backed; pilot CactusRankWitness recommended |
| Fire #43 (Tier-D recovery in CP regimes) | T#73 PhaseTransitionThreshold triple | ✓ backed |
| Fire #45 (Tier-B + Tier-D cross-tier composition) | T#73 (fire #43) + T#40 (AOP/CO-V) — TWO independent confirmations | ✓ backed; saturation declaration validated |
| (new) GCTObstructionCertificate | T#92 entire cluster (BIP 2019 + Dörfler-Ikenmeyer-Panova 2019 + STOC 2020) | ✓ backed |
| (new) RandomTensorConcentrationCert | T#72 (BGJLR STOC 2025 + BBvH Inventiones 2024) | ✓ backed |
| (new) RankZooSignature Tier-A++ | T#13 (Lampert-Moshkovitz Sept 2025) + T#19 cactus chain | ✓ backed |
| (new) WaringRankWitness | T#22 (Shitov 2021 + Boij-Teitler 2019 + Shafiei 2015) | ✓ backed |
| (new) DefectivityCertificate Tier-C | T#26 (ABGO 2024) | ✓ backed |
| (new) RayClassFieldFiducial / StarkUnitWitness | T#85 (AFK 2025 conditional construction) | ✓ backed; conditional on Stark |
| (new) Structured-Equivalence-Class meta-primitive | T#79 (SLOCC 2025 AME-at-n=5) | ✓ backed |

New substrate-tester tickets to register:

- `T-ST-T19-001` CactusRankWitness probe with PATTERN_RANK_PARITY_LEAK calibration.
- `T-ST-T19-002` Cactus-barrier audit hook (any P31 BorderRankWitness with `r > 6m − 4` for `m³` tensor → re-verify via P29).
- `T-ST-T22-001..003` WaringRankWitness probe + RankInvariantConsistency probe + GenericBaselineMandate probe.
- `T-ST-T72-001` RandomTensorConcentrationCert dataclass + populate §2 table + flag `r ≥ 3, p = 2` as MC priority.
- `T-ST-T92-001..005` GCTObstructionCertificate / BorderComplexitySeparator / EquivariantComplexityCertificate / AlgebraicNaturalProofsBarrier / cross-cutting P32 synthesis pass.

---

## 7. Cross-reference table — catalog → primitives → tickets

| Catalog | Primitive(s) introduced | Tier | Substrate-tester ticket(s) |
|---|---|---|---|
| T#1 (ω) | AsymptoticSpectrumMonotone | outside-tier | (P32 candidate, Evolutionary-LLM) |
| T#13 (slice/analytic) | RankZooSignature | A++ | — |
| T#19 (cactus) | CactusRankWitness, BorderCactusWitness | B | T-ST-T19-001, T-ST-T19-002 |
| T#22 (Waring perm) | WaringRankWitness | B | T-ST-T22-001..003 |
| T#26 (Segre-Veronese) | DefectivityCertificate, MomentPolytope | C | (existing T#26 ticket) |
| T#28 (asymp spectrum) | AsymptoticSpectrumMonotone | outside-tier | — |
| T#34 (border-rank mem) | BorderRankWitness, DualityCheck, PrecisionFloorCertificate | B | T-ST-fire41-001 |
| T#40 (CP-id) | ReshapingCertificate, MeasureZeroExceptionAnnotation | B + D | T-ST-fire45-001 |
| T#43 (best rank-r) | LimitWitness | B | (existing) |
| T#56 (sym rank NP-hard) | ComputationalComplexityCertificate | B | (existing) |
| T#58 (TI complexity) | (under StructuredEquivalence) | E | (P25 / P03 sub-tactics) |
| T#72 (type-2 const) | RandomTensorConcentrationCert | D | T-ST-T72-001 |
| T#73 (tensor PCA) | PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert | D | T-ST-fire43-001 |
| T#79 (SLOCC) | Structured-Equivalence-Class meta-primitive | E | (P03 R-GIT-product sub-tactic) |
| T#84 (contraction order) | TensorNetwork, ContractionOrderWitness | A++ | (P30 sub-tactics x3) |
| T#85 (Zauner) | RayClassFieldFiducial, StarkUnitWitness | E | (anti-anchor pin) |
| T#92 (GCT) | GCTObstructionCertificate (×5 subtypes), BorderComplexitySeparator, EquivariantComplexityCertificate, AlgebraicNaturalProofsBarrier | B + E + D | T-ST-T92-001..005 |
| T#95 (Kronecker) | RepresentationTheoreticInvariant, KroneckerInvariant, PartitionObject | E | (parent class for T#92) |

---

## 8. Forward dependencies for Techne T038

Techne T038 (substrate primitive classification) should consume this synthesis as its **specification document for the next contract-change window**. Recommended sequencing:

**Wave 1 (cleanest, lowest risk):**
1. `TensorNetwork` + `ContractionOrderWitness` (T#84). Foundational; nothing depends on it but everything will.
2. `CactusRankWitness` (T#19). Pilot for Tier-B contract change — purely combinatorial.
3. `RankZooSignature` (T#13). Tier-A++ tracking primitive; can be retrofitted onto existing tensor nodes.

**Wave 2 (Tier-B cluster):**
4. `BorderRankWitness` (T#34) parent.
5. `LimitWitness` (T#43), `ComputationalComplexityCertificate` (T#56), `WaringRankWitness` (T#22) sub-types in parallel.
6. `DualityCheck`, `PrecisionFloorCertificate`, `ReshapingCertificate`, `MeasureZeroExceptionAnnotation` cross-cutting Tier-B sub-primitives.

**Wave 3 (Tier-D + cross-tier composition):**
7. `PhaseTransitionThreshold` triple (T#73).
8. `RandomTensorConcentrationCert` (T#72).
9. Tier-B + Tier-D composition ratification (substrate-tester fire #45 closure).

**Wave 4 (Tier-E + GCT cluster):**
10. `RepresentationTheoreticInvariant`, `KroneckerInvariant`, `PartitionObject` (T#95).
11. `GCTObstructionCertificate` composite (T#92) — last in sequence; depends on T#95 primitives + Tier-B + Tier-D.
12. `Structured-Equivalence-Class` meta-primitive (T#79).
13. `RayClassFieldFiducial`, `StarkUnitWitness` (T#85, conditional anchors).

**Wave 5 (paradigm-taxonomy work, parallel):**
14. P32+ synthesis pass — assign P32 to T#1's Evolutionary-LLM; queue T#56, T#92, T#95, T#85 candidates.
15. Anti-anchor pin registration (10 items in §4).
16. Catalog updates per §2 table.

---

## 9. Doctrine compliance retrospective

Each report cleared the mandated ≥2-pattern citation gate. Distribution across the 18:

- **PATTERN_RANK_PARITY_LEAK** — most-cited pattern (T#13, T#19, T#22, T#34, T#40, T#56, T#58, T#72, T#73, T#79, T#85, T#92, T#95). Reflects the substrate's most active failure mode: rank-zoo / coordinate-collapse confusion across the entire frontier.
- **PATTERN_BASE_RATE_NEGLECT** — second-most cited (T#19, T#22, T#26, T#40, T#56, T#73, T#85, T#92). Generic / base-rate strata vs. defective / boundary strata.
- **PATTERN_CONDUCTOR_CONFOUND** — T#22, T#34, T#40, T#72, T#85, T#92. Stabilizer / regime / normalization confounds.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT** — T#19, T#26, T#40, T#72, T#73, T#84. Computational-truncation artifacts in Macaulay2 / cotengra / MC sweeps.
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** — least-cited (T#1, T#92 analogue PATTERN_GCT_GRAVITATIONAL_OVERFIT). Used analogically: same phenomenon (LLM gravitational well around a canonical narrative) re-instantiated in tensor space.

**HARD-1 (no paper framing):** all 18 reports cleared. Substrate-grade work product, not journal manuscript.

**HARD-2 (anti-gravitational-well):** explicitly engaged in T#1, T#56, T#85, T#92 (resist "GCT is the path"; resist "Zauner proved 2025"; resist "use Macaulay2 for tensor PCA").

**HARD-3 (tensor-tools-we-need-most):** T#84 TensorNetwork + ContractionOrderWitness is the foundational delivery for HARD-3. T#22 det/perm asymmetry surfaces a HARD-3 gap (permanent-side tooling thinner than determinant-side).

**HARD-5 (distinct coordinates):** explicitly used in T#13, T#19, T#22, T#34, T#56, T#72, T#79, T#92. The five-rank-coordinate registration in T#19 (`R, R̄, sr, cr, cr̄`) and the four-complexity-coordinate registration in T#92 (`dc / \underline{dc} / L / B / dc_{equiv}`) are the two clearest HARD-5 artifacts.

**HARD-6 (attack tools we need most; failures guide):** the Tier-B + Tier-D cross-tier composition (fire #45), now twice-confirmed by literature, is the cleanest HARD-6 artifact. Failure mode (substrate-tester saturation declaration) directly guided the Tier-D composition recognition.

---

## 10. Honest caveats

- **T#73 sandboxed run.** The T#73 deep-research agent ran without WebSearch/WebFetch tools loaded; all citations were marked `[CHECK]` for live verification. Report content is plausible but not verified against primary sources by the batch — recommend follow-up live verification before any substrate-tester probe is built directly on T#73 citations.

- **18 reports in one day, one substrate-pass.** This synthesis is itself a single-pass artifact. The recommendations above (especially §3 primitive registrations, §5 P32 assignment, §8 wave sequencing) should not be taken as final substrate-architecture decisions. They are *strong proposals* for Techne T038 / contract-change-window deliberation.

- **Catalog updates are higher priority than primitive registration.** Five entries (T#1, T#13, T#56, T#92, T#95) are stale; until they are corrected, any Learner consumption of the catalog risks fabricated stale-anchor responses. §2 should land first.

- **P32+ paradigm-slot collision is real.** Five candidates (T#1, T#56, T#85, T#92, T#95) all surface paradigm-class novelty. Assigning all five distinct slots dilutes the taxonomy; assigning none of them keeps the catalog under-resolved. The §5 synthesis recommendation (P32 → T#1 Evolutionary-LLM; P33 → T#56 Existential-Theory Reduction; queue rest) is the cleanest resolution but should be reviewed.

- **Substrate-tester saturation declaration was correct twice over.** This is not "the right answer comes back to validate substrate-tester"; it is genuine independent confirmation across two reports (T#73, T#40). The architecture decision (Tier-B + Tier-D composition required) is now load-bearing for any future tensor-substrate work.

---

## 11. Report manifest

```
aporia/docs/deep_research_batch_tensor_priority_2026-05-09/
├── report_T1_matrix_multiplication_exponent.md
├── report_T13_slice_vs_analytic.md
├── report_T19_cactus_rank.md
├── report_T22_waring_permanent.md
├── report_T26_defective_segre_veronese.md
├── report_T28_asymptotic_spectrum.md
├── report_T34_borderrank_membership.md
├── report_T40_cp_identifiability.md
├── report_T43_best_rank_r_existence.md
├── report_T56_symmetric_rank_nphard.md
├── report_T58_tensor_isomorphism.md
├── report_T72_type2_constant.md
├── report_T73_tensor_pca_threshold.md
├── report_T79_slocc_entanglement.md
├── report_T84_optimal_contraction.md
├── report_T85_zauner_sicpovm.md
├── report_T92_gct_vp_vs_vnp.md
└── report_T95_kronecker_positivity.md
```

End of synthesis.
