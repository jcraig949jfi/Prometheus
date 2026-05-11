# Layer 2 — Attacks (verbs)

Attacks are the **paradigms** an agent applies to a problem. Each attack consumes some Layer-1 primitives, produces some Layer-1 primitives, and has documented success conditions and characteristic failure modes (Layer-3 patterns). The full canonical taxonomy with every sub-tactic enumerated lives in `aporia/doctrine/attack_angle_taxonomy.md` (TODO: file may not yet exist; this catalog seeds the gateway). Entries below are organized by paradigm number `Pxx`. Each entry names the primitives consumed / produced, success conditions, common failure modes, key references, and source seed report. **The P32 slot is contested** — five candidates collide; the seed-batch synthesis recommendation is `P32 = T#1 Evolutionary-LLM` with `P33 = T#56 Existential-Theory Reduction`, but this is provisional.

---

## Base paradigms (P00–P31, batch-relevant)

### `P03_ExhaustiveComputation`

- **Category:** classical / computational base
- **Consumes:** ambient mathematical input (tensor, form, partition, etc); compute budget annotation.
- **Produces:** any Tier-B witness via brute / enumeration; typical pairing with `PrecisionFloorCertificate` and `VRAM_TRUNCATION_ARTIFACT` mitigation.
- **Success conditions:** tractable problem-size; bounded enumeration depth provably exhaustive; no silent truncation.
- **Common failure modes:** `PATTERN_VRAM_TRUNCATION_ARTIFACT` (silent truncation); `PATTERN_BASE_RATE_NEGLECT` (generic-stratum spot-check missing the defective phenomena).
- **New sub-tactics from this batch:**
  - **R-GIT-product** (T#79) — product structure on representation-theoretic GIT quotients.
  - **linear-length-reduction** (T#58, `report_T58_tensor_isomorphism.md`) — TI-completeness reduction style; q^Õ(n^{3/2}) via Grochow–Qiao IV STOC '25.
- **Key references:** Buczyńska–Buczyński Algorithm 5.1 (border-apolarity B-invariant ideal enumeration, Duke 2021); cotengra / opt_einsum.
- **Source:** T#79, T#58; synthesis §5.

### `P04_GenericPositionAnalysis`

- **Category:** algebraic-geometric base
- **Consumes:** ambient mathematical input; genericity / dimension-counting baseline.
- **Produces:** `GenericityAlmostEverywhereCert` (Tier-D); paired with `MeasureZeroExceptionAnnotation` when explicit exceptions known.
- **Success conditions:** baseline holds on Zariski-open dense subset; explicit exception list (if any) is finite and characterized.
- **Common failure modes:** `PATTERN_BASE_RATE_NEGLECT` (mistaking the measure-zero defective stratum for negligible); collapse into `P09_DimensionCounting` without registering exceptions.
- **Key references:** ABGO 2024 (Segre–Veronese defectivity classification, arXiv:2406.20057); Bernardi–Ranestad cubic-form bound.
- **Source:** T#26, T#40; synthesis §5.

### `P09_DimensionCounting`

- **Category:** algebraic-geometric base
- **Consumes:** ambient variety; expected dimension formula.
- **Produces:** `DefectivityCertificate` (Tier-C) when discrepancy detected.
- **Success conditions:** expected vs actual dimension provably distinct.
- **Common failure modes:** `PATTERN_RANK_PARITY_LEAK` if dimension-count is reported without distinguishing which secant order; `PATTERN_BASE_RATE_NEGLECT`.
- **Key references:** Alexander–Hirschowitz; ABGO 2024.
- **Source:** T#26; synthesis cross-references.

### `P15_ParentParadigm`

- **Category:** parent / structural
- **Consumes:** problem statement; sub-paradigm choice.
- **Produces:** dispatch into a sub-paradigm.
- **Success conditions:** sub-paradigm is well-suited to the problem class.
- **Common failure modes:** `PATTERN_GCT_GRAVITATIONAL_OVERFIT` (forcing sub-paradigm into GCT when non-GCT routes are stronger).
- **Source:** T#19 cross-references; synthesis context.

### `P22_RepresentationTheoreticPlethystic`

- **Category:** representation-theoretic
- **Consumes:** `RepresentationTheoreticInvariant` (Tier-E), `KroneckerInvariant`, `PartitionObject`.
- **Produces:** `GCTObstructionCertificate.MultiplicityObstruction` candidates; plethysm-positivity bounds.
- **Success conditions:** character / multiplicity computation tractable; positivity / vanishing argument constructs an obstruction.
- **Common failure modes:** `PATTERN_RANK_PARITY_LEAK` (collapsing Kronecker / Littlewood-Richardson / plethysm coefficients); `PATTERN_GCT_OCCURRENCE_DEAD` (attempting occurrence obstructions for `(det_m, padded_perm_{n,m})`); active program-stall risk (synthesis §F-T92-03).
- **Key references:** GCT I–V (Mulmuley–Sohoni); Bürgisser–Ikenmeyer–Panova J.AMS 2019 (BIP, occurrence-killer); Dörfler–Ikenmeyer–Panova ICALP 2019 (multiplicity stronger than occurrence); Ikenmeyer–Pak–Panova IMRN 2024 (PH-hardness of `S_n` character positivity).
- **Source:** T#92, T#95; synthesis §5.

### `P25_PivotalNegativeResult`

- **Category:** structural / barrier
- **Consumes:** target attack vector; barrier construction.
- **Produces:** a documented barrier / impossibility-of-an-attack annotation that re-routes downstream attacks.
- **Success conditions:** the barrier rules out a non-trivial slice of the candidate-attack space.
- **Common failure modes:** treating the barrier as final ("GCT killed") rather than as a re-routing signal.
- **New sub-tactics from this batch:**
  - **orbit-special-structure-exploitation** (T#58) — exploits TI-special structure to prove negative results.
  - **volumetric-barrier-as-pivotal-negative-result** (T#72) — type-2 tensor constant `p < 2r` open behind a volumetric barrier.
- **Key references:** BIP 2019 J.AMS; cactus barrier `6m − 4` (Buczyński Feb 2026 arXiv:2602.11309); Forbes–Shpilka–Volk algebraic natural proofs barrier.
- **Source:** T#19, T#58, T#72, T#92; synthesis §5.

### `P28_AsymptoticSpectrumMachinery`

- **Category:** structural
- **Consumes:** ambient tensor; Strassen-monoid candidate spectrum element.
- **Produces:** `AsymptoticSpectrumMonotone` (outside-tier); contributions toward `ω` upper bounds (T#1).
- **Success conditions:** candidate map is `≤_∼`-monotone; CHNVZ 2024 polynomial-characterization gates apply.
- **Common failure modes:** `PATTERN_RANK_PARITY_LEAK` (conflating tensor rank with asymptotic-rank); cactus rank does NOT obviously lift to asymptotic-spectrum element.
- **Key references:** Strassen 1988; CHNVZ 2024 (arXiv:2411.15789); Christandl–Hoeberechts–Nieuwboer–Vrana–Zuiddam STOC 2025.
- **Source:** T#28, T#1; synthesis cross-references.

### `P29_BorderApolarity`

- **Category:** algebraic-geometric / scheme-theoretic (PRIMARY)
- **Consumes:** symmetric form / tensor; apolar-scheme search infrastructure.
- **Produces:** `CactusRankWitness`, `BorderRankWitness`, `BorderCactusWitness` (Tier-B). Composes with `RankZooSignature` for full-coordinate registration.
- **Success conditions:** saturated 0-dim Gorenstein apolar scheme constructed; multigraded Hilbert function computed; truncation depth recorded.
- **Common failure modes:** `PATTERN_VRAM_TRUNCATION_ARTIFACT` (Macaulay2 B-invariant-ideal enumeration blows up combinatorially); `PATTERN_RANK_PARITY_LEAK` (collapsing `cr` / `R̄` / `sr` / `cr̄`); confusing classical apolarity with border apolarity.
- **Key references:** Buczyńska–Buczyński Duke 2021 (THE foundational P29 paper, arXiv:1910.01944); Buczyńska–Buczyński Jan 2026 (border apolarity for cactus, arXiv:2601.19558); Bernardi–Reig Fité Aug 2025 (arXiv:2508.15062).
- **Source:** T#19 (primary), T#34, T#92; synthesis §3.2, §4 entry 5.

### `P30_OccurrenceObstructions` (anti-anchored)

- **Category:** representation-theoretic (KILLED in canonical regime)
- **Consumes:** `(det_m, padded_perm_{n,m}, m=poly(n))` pair; representation-theoretic infrastructure.
- **Produces:** `GCTObstructionCertificate.OccurrenceObstruction` — **provably non-existent** in this regime.
- **Success conditions:** **none in the canonical GCT regime.** BIP 2019 (J.AMS) is the impossibility theorem.
- **Common failure modes:** **the entire attack fails by construction in the regime.** `PATTERN_GCT_OCCURRENCE_DEAD` (Layer-3) and `anti_anchors.md` entry 1 fire as sentinel violations on any agent attempt.
- **New sub-tactics from this batch:** three from T#84 (cotengra ordering / line-graph treewidth / netcon) — these are P30 sub-tactics in the **contraction-order** sense (a different axis from GCT occurrence); the same paradigm-number happens to host both a killed and a live cluster of sub-tactics. **Substrate must distinguish the two senses** — TODO: re-number in v0.2.0 to avoid this collision.
- **Key references:** BIP 2019 J.AMS (arXiv:1604.06431); Markov–Shi 2008 (line-graph treewidth NP-hardness for contraction).
- **Source:** T#92 (anti-anchored sense), T#84 (contraction-order sense); synthesis §5.

### `P31_SecantVarietyGeometry` / `P31_OrbitClosureGeometry`

- **Category:** algebraic-geometric (sister to P29)
- **Consumes:** secant variety / orbit closure of target tensor or polynomial; equation generation infrastructure.
- **Produces:** `BorderRankWitness` via flattening / catalecticant minors; `OrbitClosureNonMembershipWitness` via `OutsideOrbitObstruction`.
- **Success conditions:** equations vanishing on `σ_r` (or orbit-closure) but not at the target.
- **Common failure modes:** **cactus barrier** — determinantal / catalecticant equations vanish on `κ_r ⊋ σ_r`, so they cannot prove `R̄(M⟨m⟩) > 6m − 4` (anti-anchor 5). `PATTERN_CONDUCTOR_CONFOUND` if the equation system is reported without stabilizer / regime annotation.
- **Key references:** Buczyński–Keneshlou Oct 2024 (arXiv:2410.21908, catalecticant minors as sharp κ_r equations on dense open subset); Galązka–Mańdziuk–Rupniewski 2023 FoCM (Veronese κ_14, arXiv:2007.16203); Implementing GCT STOC 2020 (arXiv:1911.03990).
- **Source:** T#19, T#34, T#92; synthesis §5.

---

## P32+ paradigm candidates (CONTESTED)

The seed batch surfaced **five P32-class candidates** that collide numerically. A synthesis pass is mandatory before any single one is assigned the canonical P32 slot. Synthesis-pass recommendation (provisional, synthesis §5):

| Slot | Recommended assignment | Rationale |
|---|---|---|
| **P32** | `P32_EvolutionaryLLMSynthesis` (T#1) | Concrete deliverable (AlphaEvolve produced 4×4(ℂ) rank-48); reproducibly novel; produced a *better* algorithm than state-of-the-art. |
| **P33** | `P33_ExistentialTheoryReduction` (T#56) | Highest theoretical reach; uses `∃ℝ` complexity for uniform reductions across rank-zoo. |
| (queued) | `P_CANDIDATE_ModularSaturation` (T#95) | Single-shot proof; staircase-minimality; use-case-specific. |
| (queued) | `P_CANDIDATE_StarkUnitConstruction` (T#85) | Conditional on Stark; very specialized; does not generalize beyond ray-class-field-fiducial regime. |
| (HOLD) | `P_CANDIDATE_MultiplicityObstructionSynthesis` (T#92) | **Hold** — should not occupy a paradigm slot until concrete obstruction constructed; future-promise without deliverable since 2020. |

The five entries below are documented as candidates pending synthesis-pass resolution.

### `P32_EvolutionaryLLMSynthesis` (candidate, recommended P32)

- **Category:** novel / computational-search
- **Consumes:** target tensor identity; LLM-driven search infrastructure; reward signal (e.g. rank reduction).
- **Produces:** novel decompositions (e.g. AlphaEvolve 4×4(ℂ) rank-48); contributes toward ω upper bounds.
- **Success conditions:** synthesized decomposition verifiably equals the target tensor; rank strictly improves on prior state-of-the-art.
- **Common failure modes:** `PATTERN_PRIME_GRAVITATIONAL_OVERFIT` analogue (LLM gravitational well around canonical decomposition templates); reproducibility hazard (compute access asymmetry).
- **Key references:** AlphaEvolve / DeepMind May 2024; Alman–Duan–VW–Xu–Xu–Zhou 2024 (arXiv:2404.16349, ω < 2.371339).
- **Source:** T#1; synthesis §5.

### `P33_ExistentialTheoryReduction` (candidate, recommended P33)

- **Category:** complexity-theoretic
- **Consumes:** existence problem in algebraic-geometric setting; `∃ℝ`-completeness reduction infrastructure.
- **Produces:** `ComputationalComplexityCertificate.ExistsRHardClass`; uniform reductions across rank-zoo.
- **Success conditions:** explicit reduction from a known `∃ℝ`-hard problem to the target.
- **Common failure modes:** `PATTERN_RANK_PARITY_LEAK` (conflating rank-decision complexity classes); over-extension to settings where `∃ℝ` is not the right complexity class.
- **Key references:** Shitov 2016 (arXiv:1611.01559, *How hard is the tensor rank?* — symmetric tensor rank over `ℚ` is NP-hard; tensor rank over `ℤ` is undecidable). **(Citation corrected 2026-05-11 per Wave 1 anti-anchor verification; prior arXiv:1605.07532 was wrong.)**
- **Source:** T#56; synthesis §5.

### `P_CANDIDATE_ModularSaturation` (RETRACTED 2026-05-11)

- **Status:** **RETRACTED.** This candidate was sourced from Lee 2025 arXiv:2512.15035, which was withdrawn within 3 days due to mathematical gaps. Wave 1 anti-anchor verification surfaced the retraction. The "staircase minimality" technique itself remains a candidate methodology, but no successful application of it exists.
- **Category:** combinatorial / partition-theoretic (hypothetical)
- **Consumes:** `PartitionObject`; staircase-minimality machinery (would need to be rebuilt without the withdrawn lifting step).
- **Produces:** would have produced single-shot resolutions of partition-positivity claims; does not in current state.
- **Common failure modes:** the Bessenrodt–Bowman–Sutton lifting step does not in fact discharge dominance-minimality as claimed.
- **Source:** T#95; synthesis §5; Wave 1 anti-anchor verification (prompt 01).

### `P_CANDIDATE_StarkUnitConstruction` (queued)

- **Category:** number-field / conditional
- **Consumes:** ray-class-field of real-quadratic field; Stark-conjecture infrastructure.
- **Produces:** `RayClassFieldFiducial` + `StarkUnitWitness` constructions (conditional).
- **Success conditions:** **conditional on Stark conjectures + Shintani–Faddeev modularity.** Unconditional case is OPEN.
- **Common failure modes:** **`PATTERN_ZAUNER_FALSE_ANCHOR`** (anti-anchor 2); reporting AFK 2025 as unconditional.
- **Key references:** AFK 2025 (arXiv:2501.03970).
- **Source:** T#85; synthesis §5.

### `P_CANDIDATE_MultiplicityObstructionSynthesis` (HOLD)

- **Category:** representation-theoretic
- **Consumes:** Tier-E representation infrastructure; multiplicity / vanishing-ideal / outside-orbit obstruction templates.
- **Produces:** would produce live-route `GCTObstructionCertificate` candidates if a concrete obstruction were constructed.
- **Success conditions:** **none yet achieved.** No concrete obstruction constructed in this regime since 2020.
- **Common failure modes:** `PATTERN_GCT_GRAVITATIONAL_OVERFIT`; substrate-tester refusal-to-load if unsupported by upstream Tier-E primitive.
- **Key references:** Dörfler–Ikenmeyer–Panova ICALP 2019; Implementing GCT STOC 2020 (arXiv:1911.03990).
- **Source:** T#92; synthesis §5. **Held out of paradigm slot pending concrete deliverable.**

---

## TODO for future batches

- **Resolve P30 collision.** P30 hosts both a killed cluster (occurrence obstructions, BIP 2019) and a live sub-tactic cluster (cotengra / line-graph treewidth / netcon contraction-order). Re-number in v0.2.0.
- **Synthesis pass on P32 candidates.** Five candidates collide; assignment is provisional. Convene Aporia ratification before locking.
- **Sub-tactic enumeration.** Each base paradigm above lists the new sub-tactics from the seed batch, but the historical sub-tactics from prior work are not enumerated here. Next contract-change window should cross-link `attack_angle_taxonomy.md` exhaustive list.
- **Non-tensor paradigms.** Seed batch is tensor-priority. Adjacent corners (number theory, knot theory, dynamical systems) will surface paradigms not in the current `P00–P32+` numbering.
