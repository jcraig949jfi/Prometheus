# Gemini Deep Research Batch — Synthesis (2026-05-11)

**Batch:** 18 substantive reports, `aporia/docs/deep_research_batch_2026-05-10/`
**Source dispatch:** `aporia/docs/gemini_deep_research_deck_2026-05-10.md` (prompts 19–20 deferred — TBD wildcards unfired)
**Catalog under pressure:** `aporia/mathematics/tensor_open_problems_v1.md` (HARD-3 / `feedback_tensors_near_and_dear`)
**Doctrine:** HARD-1 (no paper-publishing framing), HARD-2 (anti-gravitational-well), HARD-3 (tensor-tools-we-need-most), HARD-5 (distinct coordinates), HARD-6 / behavior-delta (every recommendation must trace to a downstream consumer), `feedback_substrate_passive_consumer_warning.md`, `feedback_verify_upstream_attributions.md`.

---

## 1. Executive summary

The 2026-05-10 batch is the second 18-report Gemini Deep Research run inside a week, and unlike the 2026-05-09 tensor-priority dispatch (which was tightly clustered on `tensor_open_problems_v1.md` entries), this batch is **broadly diagonal**: 3 reports on anti-anchor verification, 3 tensor-catalog continuations, 3 calibration-anchor scouts (knots / Maass GL(3) / genus-2), 3 methodology reports (AlphaEvolve / SoS / tensor networks in QMB), 3 Learner v1.0 inputs (corpora / 3B–4B models / SR–ProgSynth), and 3 substrate-vocabulary expansions (type theory / DSL design / composition rules). The diagonal shape is exactly what was needed — Wave 1 (already-applied) showed that even high-quality reports can encode subtle errors, and the remaining 5 waves now provide enough cross-checking for the next contract-change window without forcing a single new mega-batch.

**Headline numbers:**

- **Catalog updates required: 9** new edits to `tensor_open_problems_v1.md` beyond the 2026-05-09 set, including 3 newly surfaced "X solved Y in 2025/26" claims that need second-pass verification before propagating (Strict Direct-Sum-7 [Rupniewski 2024], BorderRank Comon's at $n \le d+1$ [Mańdziuk-Ventura Nov 2024], $\det_4$ rank-12 over arbitrary char $\ne 2$ [Han-Ju-Kim 2025]) and 1 paradigm-class breakthrough (Boxer-Calegari-Gee-Pilloni 2025 unconditional modularity for a positive proportion of abelian surfaces over $\mathbb{Q}$).
- **New anti-anchor candidates: 11** — including 4 Wave-3 calibration-domain anchors that pre-empt the Lee-2025-style failure mode for the new domains (Khovanov / Maass / genus-2), and 4 methodology-domain anchors that pre-empt LLM gravitational wells.
- **New substrate primitive proposals: 18** across the 5 tiers + 3 outside-tier additions, plus a recommended **Tier-F (Domain-Anchor)** and **Tier-G (Method-Synthesis)** introduction for v0.2.0. Tier-B continues to dominate.
- **New paradigm candidates: 4** beyond the existing P31 + 5 candidates registered after the 2026-05-09 batch — `P32_EvolutionaryLLMSynthesis` is now **strongly load-bearing** (T#1 result + Wave 4 forensic reproducibility); `P33_ExistentialTheoryReduction` (T#56), `P34_PACBayesianTensorNorm` (Aden-Ali 2025 in T#24/T#71), `P35_PeriodIntegralMomentBypass` (Kwan 2024–25 in Maass GL(3)).
- **Surprises:** Wave 6 (substrate vocabulary) is the **highest-leverage wave** — multicategorical / colored-PROP formalism is exactly the right abstract structure for the empirically-confirmed Tier-B × Tier-D and Tier-B × Tier-E rules, and gives substrate a precise deflection of LLM-narrative gravity toward "just use Lean Mathlib." Wave 5 (Learner v1.0) is the **most immediately actionable**, with concrete model recommendation (Phi-4-Mini 3.8B) and corpus prioritization (Mathlib + ProofNet upsampled, OpenWebMath/MathPile downweighted with explicit anti-anchor filtering).

**Highest-leverage finding from the batch:** the **substrate's empirically-confirmed Tier-B × Tier-D and Tier-B × Tier-E composition rules have a known, mature mathematical formalism — Colored Operads (Multicategories) for single-output composition, Colored PROPs for multi-output, with Linear Type Systems enforcing the "use-once" constraint, all implementable in Julia via GATlab without the Coq performance penalty.** This collapses the Wave 6 "what's the right abstract structure for our composition rules?" question directly into a v0.2.0 vocabulary design decision. Behavior delta: opens path to substrate-tester probes that algebraically reject illegal cross-tier compositions before they execute.

The single **methodology gravity well to resist** (HARD-2) is Wave 4's AlphaEvolve survey reading as "evolutionary LLM-driven discovery is the future." That framing is not wrong but it is incomplete: AlphaEvolve's core mechanism is *meta-discovery* — it evolves the *search algorithm*, not the mathematical object. The poor-man's Prometheus version requires very specific scaffolding (island-based architecture, cascade evaluation, inspiration-based crossover) that is itself the substrate-grade contribution. HARD-2 reading: AlphaEvolve is a **paradigm-class finding to register**, not a roadmap to copy uncritically.

---

## 2. Catalog updates required

`aporia/mathematics/tensor_open_problems_v1.md` requires the following edits beyond the 2026-05-09 batch's 8-row table. Two-pass priority: edits marked **[VERIFY-LIVE]** need a primary-source second-pass per `feedback_verify_upstream_attributions.md` before propagating into the Learner corpus; edits marked **[PROPAGATE]** are well-confirmed.

| Entry | Current text | Required update | Source report | Status |
|---|---|---|---|---|
| T#5 (matrix mult exponent at small `n`) | "$\underline{R}(M\langle 3 \rangle) \in [17, 21]$ (Conner-Harper-Landsberg 2019)" | Add: cactus barrier for `m=9` is 50, so the [17, 21] window is *not* yet at the cactus barrier; gap between 17 and 21 is genuine geometry, not method-exhaustion. Cross-link AA-005. | report 04 (T#5) §2, §6 | **[PROPAGATE]** |
| T#6 (Strassen direct-sum, exact) | (current entry pre-Shitov framing) | Update: false in general (Shitov 2019 *Acta Math.*); **TRUE** for $R(T_i) \le 7$ over $\mathbb{C}$ and for one tensor in $\mathbb{C}^k \otimes \mathbb{C}^3 \otimes \mathbb{C}^3$ (Rupniewski 2024 *Linear Algebra Appl.*). Adds a "small-tensor additivity safe zone" to the rank-zoo. | reports 04 (T#6), 05 (T#23) | **[VERIFY-LIVE]** — Rupniewski 2024 small-tensor regime cited in two separate reports, but exact bound `R \le 7` should be primary-pinned before the safe zone is registered as substrate-canonical. |
| T#20 (Border Comon's conjecture, minimal border rank) | (open in catalog) | Status: TRUE for `n ≤ d+1`, for "tame" tensors, and for sharp tensors (Mańdziuk-Ventura Nov 2024, arXiv:2411.05721). Wild tensors remain the obstacle. **Standard Comon's** (exact rank, large `n`) is FALSE — Shitov 2018 counterexample at `n=800`. The two should NEVER be conflated — separate substrate entries. | report 04 (T#20) | **[VERIFY-LIVE]** — Mańdziuk-Ventura cited; verify `n ≤ d+1` regime. |
| T#21 (Alexander-Hirschowitz / Waring rank) | (existing entry) | Add: **R(perm_3) = 16 strictly < generic 19** (Shitov 2020 + validations). **R(det_3) ∈ [15, 17 or 18]** (lower from syzygies of apolar ideal, upper from explicit constructions). Both polynomials sit in the *sub-generic stratum* — calibration-grade for HARD-5 separation between generic Waring and structured-tensor Waring. | report 06 (T#21) §5 | **[PROPAGATE]** |
| T#23 (Strassen tensor rank additivity) | (paired with T#6) | Same update as T#6 row but with explicit rank-7 ceiling annotation. | report 05 (T#23) | **[VERIFY-LIVE]** |
| T#24 (operator norm of random tensors) | (current entry) | Add: **Boedihardjo Dec 2024** (independent-entry tensors, `(ln d)^2` penalty); **BGJLR 2024** (correlated entries, geometric covering); **Aden-Ali 2025** (PAC-Bayesian, removes log factors strictly improves BGJLR); **Dartois-McKenna Feb 2026** (deterministic, non-asymptotic, Gamma-function moment method). Four-paper cluster, 4 distinct techniques — register all as separate `RandomTensorConcentrationCert` sub-types. | report 05 (T#24) §3–6 | **[PROPAGATE]** |
| T#71 (log-factor elimination, matrix concentration) | (current entry) | Add: **BBvH 2023–24** (free probability, Inventiones) — log factor eliminable for matrices via intrinsic-freeness alignment; **for tensors `r ≥ 3`, log factor scales WORSE (`(ln d)^2` per Boedihardjo)** unless PAC-Bayesian or generic-chaining substitutes are used. Direct counter to "BBvH solves log factor for everything" gravity well. | report 05 (T#71) §3, §6 | **[PROPAGATE]** |
| T#86 (det/perm tensor rank, small `n`) | "$R(\det_n) \le n!$ classical; $R(\text{perm}_n) \le 2^{n-1}$ Glynn 2010" | Add: **$R(\det_n) \le B_n$** (Houston-Goucher-Johnston 2024, arXiv:2301.06586) — Bell-number bound via ordered partial partitions, dramatically below $n!$. Over $\mathbb{F}_2$: $R(\det_n) \le 2^n - n$. **$R(\det_4) = 12$ exactly** (Han-Ju-Kim 2025) over arbitrary characteristic $\ne 2$, matches the $\mathbb{F}_2$ value. **$R(\text{perm}_4) = 8$ exactly** (Han-Ju-Kim 2025). $R(\det_5) \le B_5 = 52$. | report 06 (T#86) | **[VERIFY-LIVE]** — Houston-Goucher-Johnston published claim looks well-founded (arXiv:2301.06586 has been on arXiv for ~3 years now); Han-Ju-Kim 2025 is the new claim and needs primary-pinning. |
| T#93 (orbit closure containment) | (existing entry) | Add: **TOCI complexity class** (Tensor Orbit Closure Intersection) — emerged 2024–2026 as the natural class for general $GL_n$ orbit closure problems; Graph Isomorphism is poly-time Karp-reducible to TOCI. **Bürgisser-Doğan-Makam-Wigderson 2026** — torus-action orbit closure intersection in P-time via moment-map polytopes. | report 06 (T#93) | **[VERIFY-LIVE]** — BDMW 2026 attribution should be primary-pinned. |
| T#95 / T#99 (Saxl) | (already updated to "OPEN" 2026-05-11) | No change. Re-verified by report 01. | report 01 (Wave 1) | (already done) |

**Beyond the tensor catalog** (Wave 3 surfaced new content for the calibration-anchor catalogs that don't have a dedicated `mathematics/` file yet):

- **Knots/Khovanov:** Burton 2018–21 prime knot tabulation through 20 crossings (1,847,319,428 knots, of which 99.99995% hyperbolic, 920 satellite, 1 torus). Lackenby 2021 quasi-polynomial unknot recognition still pre-publication as of late 2025 (flag, not catalog edit). Ren-Willis 2024 first analysis-free combinatorial proof of exotic 4-manifold pair via $\mathfrak{gl}_2$ skein lasagna module. Schmidhuber et al. 2025 (arXiv:2501.12378) Khovanov approximation is BQP-hard / DQC1-hard / #P-hard depending on regime.
- **Maass GL(3):** Cui-Wang-Peng 2025 explicit coarse trace formula for GL(3); Kwan 2024–25 spectral moment formulas for GL(3) × GL(2) Rankin-Selberg via period integrals (bypasses Kuznetsov + Voronoi).
- **Genus-2:** Boxer-Calegari-Gee-Pilloni 2025 unconditional modularity for a positive proportion of abelian surfaces over $\mathbb{Q}$ (paradigm event); van Bommel-Chidambaram-Costa-Kieffer 2024–25 first practical algorithm to map full isogeny classes for typical p.p. abelian surfaces over $\mathbb{Q}$; Shi 2025 Las Vegas $O(\log^{2+o(1)} p)$ lifting algorithm for local zeta functions (10–4100× speedup).

These should land in a new `aporia/mathematics/calibration_anchors_v1.md` rather than in `tensor_open_problems_v1.md`.

---

## 3. New anti-anchor candidates

Per `feedback_verify_upstream_attributions.md`, internal catalogs are Tier-2-or-worse; Wave 1's Lee-2025 catch demonstrated the value of forward-anchor pinning. The 11 candidates below are the highest-risk anchor-failures across the batch. They follow the existing `techne/registry/anti_anchors.jsonl` schema.

### Tensor-catalog forward anchors (Waves 2)

**AA-013 `STRASSEN_DIRECT_SUM_R7_SAFE_ZONE_NEEDS_PIN`** (risk: medium)
- *False form:* "Rupniewski's 2024 result proves Strassen direct-sum additivity for *all* small tensors, regardless of rank."
- *True form:* The safe-zone is precisely $R(T_1), R(T_2) \le 7$ over $\mathbb{C}$, OR one tensor in $\mathbb{C}^k \otimes \mathbb{C}^3 \otimes \mathbb{C}^3$. Outside this regime the conjecture is FALSE in general (Shitov 2019 *Acta Math.* in high dimension). Substrate must reject "additivity holds" claims that don't include the safe-zone qualifier.
- *Citation:* Rupniewski 2024 *Linear Algebra Appl.* (cite primary; reports 04 and 05 cite secondary).
- *Source report:* Wave 2 / prompts 04, 05.

**AA-014 `BORDER_COMON_NOT_STANDARD_COMON`** (risk: medium-high)
- *False form:* "Comon's conjecture is OPEN at minimal border rank, since the standard Comon was killed by Shitov 2018."
- *True form:* These are TWO DISTINCT CONJECTURES that operate on different rank invariants and different geometric closures. **Standard Comon's** (exact rank, $R(F) = R_S(F)$ for symmetric tensors): FALSE (Shitov 2018, $n=800$). **Border Comon's** (border rank, $\underline{R}(F) = \underline{R}_S(F)$): TRUE for `n ≤ d+1`, tame tensors, and sharp tensors (Mańdziuk-Ventura Nov 2024); wild tensors are the obstacle. Substrate must NOT collapse the two conjectures into a single status flag — register `RankZooSignature`-style separate entries.
- *Citation:* arXiv:2411.05721 (Mańdziuk-Ventura 2024); Shitov 2018 *SIAM J. Appl. Algebra Geom.*
- *Source report:* Wave 2 / prompt 04 (T#20).

**AA-015 `BELL_NUMBER_DET_BOUND_NOT_PERMANENT`** (risk: medium)
- *False form:* "Houston-Goucher-Johnston 2024 Bell-number bound applies to both determinant AND permanent."
- *True form:* The Bell-number bound $R(\det_n) \le B_n$ is **specific to the determinant** because the proof relies on the alternating-sign cancellations in the Leibniz expansion. The permanent has NO Bell-number analogue except in characteristic 2 (where det = perm trivially). Cross-confirms the 2026-05-09 T#22 finding on det/perm tooling-asymmetry. Substrate must reject any agent attempt to apply $B_n$ as a permanent upper bound in characteristic 0.
- *Citation:* arXiv:2301.06586 (Houston-Goucher-Johnston 2024).
- *Source report:* Wave 2 / prompt 06 (T#86).

**AA-016 `BBVH_FREE_PROBABILITY_MATRIX_ONLY`** (risk: high)
- *False form:* "Bandeira-Boedihardjo-van Handel free-probability framework eliminates the $\sqrt{\log d}$ factor for tensors of all orders."
- *True form:* BBvH 2023–24 (Inventiones) eliminates the log factor **for matrices ($r=2$) only**, via intrinsic-freeness alignment in noncommutative algebra. For tensors $r \ge 3$ there is **no algebraic analog of trace and freeness**, so BBvH cannot be extended directly. Boedihardjo Dec 2024's tensor-extension actually has a WORSE log factor `(ln d)^2`. Eliminating logs for higher-order tensors requires PAC-Bayesian methods (Aden-Ali 2025) or generic chaining (Brailovskaya-van Handel 2025–26), and is regime-restricted. Cross-tier dimensional confusion; PATTERN_RANK_PARITY_LEAK at the order-of-tensor level.
- *Citation:* arXiv:2108.06312 (BBvH); arXiv:2503.10580 (Aden-Ali 2025).
- *Source report:* Wave 2 / prompt 05 (T#71).

### Wave 3 calibration-anchor forward anchors (knots / Maass / genus-2)

**AA-017 `LACKENBY_QUASIPOLY_UNKNOT_PRE_PUBLICATION`** (risk: medium-high)
- *False form:* "Lackenby (2021) proved unknot recognition is in quasi-polynomial time `n^{c log n}`; this is a published, peer-reviewed result."
- *True form:* The Lackenby 2021 announcement is well-known in the topology community but had not completed standard peer-reviewed publication as of late 2025 (per report 07 §2). Substrate must annotate as "ANNOUNCED, REVIEW PENDING" rather than "PROVED." LLM training data may have absorbed the announcement as canonical; this is a forward false-anchor of exactly the AA-004 (Lee/Saxl) shape.
- *Citation:* Lackenby 2021 announcement; Hass-Lagarias-Pippenger 1999 (NP); Lackenby 2016 (co-NP).
- *Source report:* Wave 3 / prompt 07.

**AA-018 `KHOVANOV_HOMOLOGY_GIRTH_NOT_CROSSING_BOUND`** (risk: medium)
- *False form:* "Khovanov homology can be computed for any knot with up to 100 crossings on consumer hardware."
- *True form:* The computational ceiling is governed by **diagrammatic girth** (max number of strands a horizontal cut crosses), NOT total crossing number. Girth ≤ 12 → trivial; girth = 14 → ~80 crossings tractable; girth ≥ 16 → 32GB+ RAM and weeks of compute. Substrate must store girth as a first-class metadata field on `KnotInvariant` primitives, never collapse to "crossing count." HARD-5 / PATTERN_RANK_PARITY_LEAK at the diagram-complexity layer.
- *Citation:* report 07 §3 (citing MathOverflow + KnotJob documentation).
- *Source report:* Wave 3 / prompt 07.

**AA-019 `LMFDB_GL3_ROOT_NUMBER_AI_VS_PROVEN`** (risk: high)
- *False form:* "LMFDB GL(3) Maass-form root numbers ($\epsilon = \pm 1$) are analytically proven."
- *True form:* Many GL(3) Maass forms in the LMFDB were computed without enough numerical precision to deduce the sign of the functional equation. Machine-learning-based murmuration prediction is now used to fill missing signs. Substrate must distinguish `ANALYTICALLY_PROVEN` vs `ML_PREDICTED_VIA_MURMURATION` in any data pull from LMFDB, or downstream proofs of subconvexity / non-vanishing inherit AI hallucination risk. This is the **most operationally-significant Wave-3 anti-anchor** because Ergon's `maass_gl3_gap_scan.py` is in active use.
- *Citation:* report 08 §1, §6.
- *Source report:* Wave 3 / prompt 08.

**AA-020 `BCGP_2025_MODULARITY_PROPORTION_NOT_ALL`** (risk: medium-high)
- *False form:* "Boxer-Calegari-Gee-Pilloni 2025 proved that all abelian surfaces over $\mathbb{Q}$ are modular."
- *True form:* BCGP 2025 proves **potential modularity** in general, plus **unconditional modularity for a positive proportion** of abelian surfaces over $\mathbb{Q}$ — specifically, surfaces with good ordinary reduction at 3 satisfying a 3-distinguished big-image hypothesis. Approximately 11,384 of 63,107 LMFDB End $= \mathbb{Z}$ curves directly qualify. Substrate must NOT propagate "all modular." Forward false-anchor of the AA-002 (Zauner conditional) shape.
- *Citation:* arXiv (BCGP 2025); report 09 §2.
- *Source report:* Wave 3 / prompt 09.

### Wave 4 methodology forward anchors

**AA-021 `ALPHATENSOR_4X4_NOT_OVER_COMPLEX`** (risk: high)
- *False form:* "AlphaTensor (2022) discovered a faster-than-Strassen algorithm for $4\times 4$ matrix multiplication over the complex numbers."
- *True form:* AlphaTensor's $4\times 4$ rank-47 result is over $\mathbb{F}_2$ (boolean / characteristic-2) ONLY; over $\mathbb{C}$ and $\mathbb{R}$ AlphaTensor failed to beat Strassen's rank 49. **AlphaEvolve (DeepMind, May 2025) is the system that discovered the rank-48 decomposition over $\mathbb{C}$**, breaking the 56-year Strassen ceiling for the recursive block setting. Substrate must distinguish the two systems and the field of definition. Mainstream press conflates them.
- *Citation:* AlphaEvolve technical report (deepmind.google, 2025); reports 04, 10.
- *Source report:* Wave 4 / prompt 10.

**AA-022 `ALPHAEVOLVE_META_DISCOVERY_NOT_DIRECT_SEARCH`** (risk: medium)
- *False form:* "AlphaEvolve directly searches the tensor decomposition space for matrix multiplication algorithms."
- *True form:* AlphaEvolve's $4\times 4$ rank-48 result was found by evolving a **gradient-based search algorithm** (custom loss functions, optimizer choice, discretization terms), NOT by searching the tensor space directly. The LLM acts as a meta-mutator on PyTorch/JAX optimizer code. Substrate must register this as `MetaDiscoveryAlgorithmSynthesis` rather than "tensor search" — different paradigm class. Resists the "AlphaEvolve = scaled-up AlphaTensor" gravitational well.
- *Citation:* report 10 §2 (15 mutations enumerated); deepmind.google AlphaEvolve report.
- *Source report:* Wave 4 / prompt 10.

**AA-023 `SOS_NOT_ABSOLUTE_LIMIT_FOR_TENSOR_PCA`** (risk: medium)
- *False form:* "Sum-of-Squares hierarchy defines the absolute lower bound of polynomial-time achievability for Tensor PCA."
- *True form:* SoS dictates the threshold (Hopkins 2018: $\lambda \ge \tilde{\Omega}(d^{k/4})$), but does NOT dictate algorithmic supremacy. Ding-Gu-Liu-Fang 2025 (NSGA, normalized SGD with overparameterization) and Zhangsong Li 2025 (Kikuchi free-energy hypergraph counting) BOTH match the SoS threshold without paying the SDP $O(d^{k/2})$ overhead. Substrate must NOT collapse "SoS proves the limit" with "SoS is the only algorithm at the limit." HARD-2 anti-gravitational-well: SoS is the *theoretical* hammer, not the *algorithmic* universal solution.
- *Citation:* report 11 §3, §7.
- *Source report:* Wave 4 / prompt 11.

**Anti-anchor candidate count: 11.** Recommend registering AA-013 through AA-023 in `techne/registry/anti_anchors.jsonl` with `verified_against_primary: false` for all **[VERIFY-LIVE]** items pending second-pass primary-source pinning.

---

## 4. New substrate primitive proposals

Organized by Wave, then by tier within wave. All proposals trace to a downstream consumer per behavior-delta requirement.

### Wave 2 — Tier-B subtypes (border-rank cluster continuations)

**`SmallTensorAdditivitySafeZone`** (Tier-B sub-type of `BorderRankWitness`, also valid as exact-rank witness)
- Parent: `BorderRankWitness` parent class; `composition eligibility:` standalone witness.
- Records the explicit safe-zone for Strassen direct-sum additivity (`R \le 7` over $\mathbb{C}$, or `T_1 \in \mathbb{C}^k \otimes \mathbb{C}^3 \otimes \mathbb{C}^3$). Carries an explicit `safe_zone_constraint` field. Source: T#6, T#23.
- Downstream consumer: substrate-tester probe T-ST-T6-001 (proposed) auto-flags any rank-additivity claim outside the safe zone.

**`MinimalBorderRankComonWitness`** (Tier-B sub-type of `BorderRankWitness`)
- Parent: `BorderRankWitness`. Sub-types: `TameTensorWitness`, `SharpTensorWitness`, `SmallNDLeqDPlus1Witness`. Carries a `wild_or_tame` enum field.
- Distinct from standard Comon's witness (exact rank); explicit substrate separation enforced. Source: T#20.
- Downstream consumer: prevents AA-014 collapse; `RankZooSignature` cross-coordinate separation.

**`BellNumberDeterminantBound`** (Tier-B sub-type of `ComputationalComplexityCertificate`)
- Parent: `ComputationalComplexityCertificate`. Records the $R(\det_n) \le B_n$ bound with explicit `field_characteristic` field.
- Source: T#86. Downstream: prevents AA-015 mis-application to permanent.

**`PermanentNonExistenceCert`** (outside-tier; null-certificate / negative-result primitive)
- Records the **non-existence** of a Bell-number-style bound for the permanent in characteristic $\ne 2$. Negative-substrate primitive — encodes a known *gap* in the tooling-asymmetry. Source: T#86, T#22.
- Downstream: HARD-3 / HARD-6 marker — surfaces the det/perm tooling asymmetry as an explicit substrate field rather than implicit folklore.

**`RandomTensorConcentrationCert.PACBayesian`** (Tier-D sub-type of `RandomTensorConcentrationCert`)
- Parent: `RandomTensorConcentrationCert` (already registered after 2026-05-09). Records bound proven via PAC-Bayesian Lemma (Aden-Ali 2025), strictly improving BGJLR by removing log factors. Source: T#24, T#71.
- Downstream: Tier-D + Tier-D candidate composition (triple of {BGJLR-geometric, BBvH-free, PACBayesian, Dartois-McKenna-deterministic}); enables substrate-tester to flag any "tensor type-2 = $\sqrt{\log d}$" claim as AA-016 violation.

**`RandomTensorConcentrationCert.DeterministicMomentMethod`** (Tier-D sub-type)
- Records bound via Dartois-McKenna 2026 deterministic Gamma-function moment method. Source: T#24.
- Downstream: enables non-Gaussian-distribution substrate analysis (quantum information, spin glass).

### Wave 3 — Domain-specific calibration-anchor primitives (proposed Tier-F)

The 2026-05-09 batch already noted that some primitives don't fit the 5-tier hierarchy cleanly. Wave 3 forces the issue: **knot invariants, Maass-form L-data, and abelian-surface invariants are calibration anchors that are NOT tensor-rank witnesses, NOT distributional certs, NOT representation-theoretic invariants in the tensor-substrate sense.** They need their own tier.

**Recommend introducing Tier-F (Domain-Anchor)** for v0.2.0 vocabulary. Proposed Tier-F primitives from this batch:

**`KnotInvariantBundle`** (Tier-F, root of knot-domain primitives)
- Sub-types: `JonesPolynomial`, `KhovanovHomology`, `RasmussenSInvariant`, `AlexanderPolynomial`, `HyperbolicVolume`, `SkeinLasagnaModule`. Records crossing number, girth (mandatory per AA-018), prime/composite, hyperbolic/satellite/torus, calculation provenance (KnotJob / Regina / SnapPy / heuristic). Source: report 07.
- Downstream: Ergon calibration battery against the 1.8B-knot Burton 2018–21 census.

**`MaassGL3SpectralBundle`** (Tier-F)
- Sub-types: `MaassEigenvalues`, `LFunctionDirichletCoefficients`, `RootNumber` (with mandatory `analytically_proven` vs `ml_predicted_via_murmuration` enum per AA-019), `GammaTypeRType`, `RankinSelbergMomentBound`. Source: report 08.
- Downstream: Ergon's `maass_gl3_gap_scan.py` consumes this directly; Wave-3 anti-anchor AA-019 enforced at primitive level.

**`AbelianSurfaceArithmeticBundle`** (Tier-F)
- Sub-types: `Genus2CurveData`, `JacobianIsogenyClass`, `LFunctionLocalPolynomial`, `RegulatorAndRealPeriod`, `ShaOrderEstimate`, `TamagawaProduct`, `ParamodularNewformLink` (with explicit `modularity_conditional_or_unconditional` enum per AA-020), `SatoTateGroup` (52 valid Banaszak-Kedlaya types). Source: report 09.
- Downstream: Ergon EC zero projections (already in queue) extend naturally to genus-2; van Bommel 2024–25 isogeny computation infrastructure.

### Wave 4 — Methodology / paradigm primitives (proposed Tier-G)

The methodology-class deliverables don't fit Tier-F either — they are method-synthesis records, not calibration anchors. **Recommend introducing Tier-G (Method-Synthesis)** for v0.2.0:

**`AlgorithmEvolutionaryLoop`** (Tier-G, root of meta-discovery primitives)
- Sub-types: `IslandPopulationArchitecture`, `CascadeEvaluationGate`, `LLMInspirationCrossover`, `MetaPromptOptimization`. Records the algorithmic loop: parents pool → LLM mutation → execution gate → scored database. Carries `evaluator_function_required: bool` (always true; AlphaEvolve constraint). Source: report 10.
- Downstream: any Prometheus poor-man's-AlphaEvolve experiment registers under this; substrate-tester can probe whether the experiment respects the four required architectural compensations for 3B–4B models (per report 10 §7 blueprint).

**`SoSCertificate`** (Tier-G or Tier-D — placement TBD; current proposal is Tier-G as a proof-system witness)
- Sub-types: `PutinarPositivstellensatz`, `LasserrePseudoExpectation`, `LowDegreeLikelihoodRatio`, `PseudoCalibrationConstruction`. Carries `hierarchy_level: int` (k = 2/4/6/8) with explicit tractability-vs-theoretical annotation. Source: report 11.
- Downstream: enables substrate-tester to flag computational claims at SoS levels above 6 as `theoretical_only` rather than `executable`.

**`TensorNetworkContraction`** (Tier-A++ subtype of `ContractionOrderWitness`, lifted from 2026-05-09 batch)
- Sub-types: `DMRGContraction`, `iPEPSCorner_TransferMatrix`, `MERAHierarchical`, `iSOTNSHolographic`. Records bond-dimension regime ($D \le 6000$ commonly), symmetry-exploitation level ($U(1)$ / $SU(2)$), AD-CTMRG vs Boundary-MPS choice. Source: report 12.
- Downstream: substrate-tester compares Prometheus tensor-network experiments against canonical software stack (ITensor / TeNPy / block2 / quimb / YASTN benchmarks per report 12 §4).

### Wave 5 — Learner v1.0 inputs (corpus + model + SR-ProgSynth)

**`MathReasoningCorpusEntry`** (proposed root primitive for Ergon's Learner ingestion pipeline)
- Sub-types: `MATHProblem`, `GSM8KProblem`, `MiniF2FExercise`, `ProofNetExample`, `MathlibTheorem`, `OpenWebMathDocument`, `ArXivMathPaper`. Carries mandatory `anchor_density_profile` field per report 13's profiling (theorem-statement %, proof %, computation %, expository-prose %). Source: report 13.
- Downstream: Ergon's v1.0 Learner training pipeline consumes this directly; corpus-design behavior delta (anchor-density-first sampling per report 13 §4).

**`StepLevelPreferencePair`** (Tier-G or Learner-input primitive; supports Step-DPO)
- Records (correct preceding steps, correct next step, incorrect next step) triples per Step-DPO 10K corpus. Source: report 13 §3.
- Downstream: Ergon Learner uses for fine-grained credit assignment, avoiding "advantage collapse" of holistic DPO.

**`TheoremProverFeedbackTrace`** (Learner-input primitive)
- Records (proof sketch, autoformalization attempt, theorem-prover compilation result, error-message-as-corrective-prompt) tuples for RLTPF (Reinforcement Learning from Theorem Prover Feedback). Source: report 13 §3.
- Downstream: future Ergon integration with Lean 4 / Mathlib via Kimina-Prover-style feedback loop.

**`ModelEvalProfile`** (Learner-input primitive for model-zoo selection)
- Records per-model: parameter count, base architecture (Qwen2.5 / Llama / SambaY hybrid), training corpus token count, MATH score (CoT vs TIR — mandatory split per AA-022 + Wave-5 §7 caveat), GSM8K score (with `contamination_warning` flag), AIME 2024 score (with sampling protocol — Pass@1 vs Cons@N), MiniF2F score, VRAM footprint at FP16 / INT8 / INT4, TransformerLens compatibility flag (with explicit Phi-4-Mini exception flag for SambaY hybrid). Source: report 14.
- Downstream: Apollo / Rhea selection consumes this; behavior delta is concrete model recommendation (Phi-4-Mini 3.8B as top dense candidate at the 17GB VRAM ceiling, Qwen2.5-Math-1.5B as fastest baseline, Llemma-7B 4-bit-quantized for formal-theorem-proving lane).

### Wave 6 — Substrate-vocabulary expansion

**`MulticategoricalCompositionRule`** (proposed substrate-meta-primitive for `composition_rules.md` schema upgrade)
- Records a composition rule with explicit input-color list, single-output color, multifunctorial preservation properties. Maps directly to the existing Tier-B × Tier-D and Tier-B × Tier-E rules. Source: reports 16, 18.
- Downstream: composition_rules.md schema upgrade (proposal in §9 below); substrate-tester uses to algebraically reject ill-typed compositions before they execute.

**`ColoredPROPCompositionRule`** (proposed alternative for multi-output cases)
- For compositions yielding multiple distinct outputs (e.g., the candidate `Tier-B × Tier-D × Tier-E` triple from 2026-05-09 batch's candidate 7). Source: reports 16, 18.

**`LinearTypeUseConstraint`** (proposed substrate-meta-primitive)
- Annotates a primitive with a "use-once" / "use-at-most-once" / "freely-duplicable" structural rule per linear / affine / classical type system. Source: report 18.
- Downstream: substrate-tester rejects double-consumption of single-use witnesses; aligns with Sigma kernel's existing linear-capabilities design.

**Primitive proposal count: 18 new primitives** (5 Tier-B sub-types + 2 Tier-D sub-types + 1 outside-tier negative + 3 Tier-F + 4 Tier-G + 4 Learner-input + 3 substrate-meta), plus **2 new tiers (Tier-F, Tier-G)** for v0.2.0.

---

## 5. New attack paradigm candidates

Beyond the existing P31 + 5 paradigm candidates registered after the 2026-05-09 batch:

**`P32_EvolutionaryLLMSynthesis`** — promote from "candidate" to **load-bearing** based on Wave 4 forensics. Two independent confirmations now: T#1 (AlphaEvolve $4\times 4$ rank-48) plus the Wave 4 forensic reconstruction (report 10 §1–7) showing a complete reproducible architecture (island populations, cascade evaluation, multi-objective optimization, evolve-block markup). Concrete deliverable available; not just a frame. Sub-tactics: `IslandPopulationArchitecture`, `CascadeEvaluation`, `LLMInspirationCrossover`, `MetaPromptOptimization`, `MetaSearchAlgorithmSynthesis` (the AlphaEvolve trick of evolving the optimizer rather than the answer).

**`P33_ExistentialTheoryReduction`** — already candidate from 2026-05-09. No new evidence in this batch but Wave-4 SoS report (11 §2) confirms tensor spectral norm is $\exists\mathbb{R}$-hard, structurally cementing the paradigm class.

**`P34_PACBayesianTensorNorm`** (NEW — concrete-deliverable) — Aden-Ali 2025 (arXiv:2503.10580) provides a complete, reproducible, simpler proof technique that strictly improves the prior state of the art (BGJLR 2024). Sub-tactic: `PACBayesianRelativeEntropyBound`. Cross-domain: works for both tensor injective norm AND classical Latała Gaussian chaos moments. Strong candidate.

**`P35_PeriodIntegralMomentBypass`** (NEW — concrete-deliverable, Maass GL(3) specific) — Kwan 2024–25 explicit spectral moment formulas for GL(3) × GL(2) Rankin-Selberg L-functions via period integrals, completely bypassing Kuznetsov + Voronoi formulas. Sub-tactic: `MotohashiTypeReciprocityIdentity`. Highly specialized — promote only if a non-Maass independent confirmation appears in a future batch.

**`P_CANDIDATE_CompositionalDSLOverColoredOperad`** (Wave 6, future-promise) — Build a Prometheus-internal DSL (per reports 17, 18) with primitives typed by tier-as-color, composition rules typed as multifunctors, "use-once" constraints enforced via linear types. GATlab (Julia) is the recommended substrate. Not a paradigm candidate yet — a substrate-design candidate that, if implemented, would itself enable new paradigms.

**`P_CANDIDATE_EvolutionaryLLMOverSubstrateVocabulary`** (combinatorial of P32 × P_CAND-DSL) — Run AlphaEvolve-style evolution where the action space is the substrate vocabulary itself (typed primitives composed via colored-operad rules), rather than raw Python code. Resists P32's Python-bias; produces substrate-grade rather than code-grade artifacts. Honest assessment: speculative; would need both P32 substrate readiness and the P_CAND-DSL Wave 6 implementation as prerequisites.

**Paradigm candidate count: 4 new** (P32 promoted, P34, P35 added; P32 elevation primary; 2 future-promise meta-candidates noted).

**Paradigm-collision warning:** P32, P33, P34, P35 are all concrete-deliverable. If all four are assigned distinct paradigm slots, the registry inflates to P31–P35 in a single window; the 2026-05-09 batch already noted dilution risk. Recommend: P32 confirmed, P34 confirmed, P33 + P35 promoted on second-batch independent confirmation per the substrate-tester saturation-declaration protocol.

---

## 6. Cross-domain calibration anchor opportunities (Wave 3)

Wave 3 surfaced three rich, structured corpora that can serve as Ergon calibration batteries. Each has different anchor-density and license profiles.

### Knots / Khovanov

**Datasets surfaced:**
- **Burton et al. prime knot tabulation through 20 crossings** — 1,847,319,428 prime knots, of which 99.99995% hyperbolic, 920 satellite, 1 torus knot. Tabulated via Regina software (open-source) over distributed clusters.
- **The Knot Atlas (RDF data dumps)** — Jones polynomials, Alexander polynomials, Khovanov homology, hyperbolic volumes for hundreds of thousands of knots.
- **KnotInfo + LinkInfo databases** — well-curated MIT-style licensed.

**Calibration-grade known-true-positive sets:**
- Rasmussen $s$-invariant predictable from Khovanov polynomial with >99% ML accuracy (per Gukov et al., report 07 §6.2). Calibration target: Ergon's own neural calibration battery should match this baseline.
- Hyperbolic volume predictable from Jones polynomial with >97% accuracy (per report 07 §6.2). Calibration target: cross-domain prediction baseline.
- Ren-Willis 2024 exotic-pair distinguishability — first analysis-free combinatorial test. Single-pair benchmark; if Prometheus's substrate can replicate this distinction via a different combinatorial route, that's a significant cross-confirmation.

**Concrete Ergon ingestion path:** parse Knot Atlas RDF → `KnotInvariantBundle` (Tier-F) primitives → 1.8B-knot calibration battery → cross-correlation against Burton census.

### Maass GL(3)

**Datasets surfaced:**
- **LMFDB GL(3) Maass forms** for conductors $(d, N) \in \{(3,1), (3,4), (3,9), (4,1)\}$. Spectral parameters $(\mu_j, \nu_k)$, Dirichlet coefficients $a_p$ to ~6 decimal places. License: open via lmfdb.org GitHub repos.
- **Bian-Booker original 5 generic Maass forms + 1 self-dual lift.** Six forms total are highly-curated calibration anchors at the Bian-Booker 2010 level.
- **Farmer-Koutsoliotas-Lemurell expansion** to thousands of forms.

**Calibration-grade caveats:**
- AA-019: root-number ML-prediction status MUST be tracked per-form. Loading without this distinction injects AI hallucinations.
- Symmetric-square-lift forms are measure-zero in the spectral landscape but computationally easy — must not be conflated with generic forms (per report 08 §6).

**Concrete Ergon ingestion path:** Pull from LMFDB GitHub → `MaassGL3SpectralBundle` (Tier-F) primitives with explicit `analytically_proven` vs `ml_predicted` partition → `maass_gl3_gap_scan.py` consumes directly → murmuration cross-validation per Lowry-Duda et al. 2024.

### Genus-2 curves

**Datasets surfaced:**
- **Sutherland LMFDB expansion to 5,000,000+ genus-2 curves** with root analytic conductor up to $2^{20}$. 1,440,894 distinct isogeny classes with generic $USp(4)$ Sato-Tate group. Open license.
- **Original 66,158-curve LMFDB baseline** with rigorously computed Tamagawa numbers, real periods, regulators (van Bommel pipeline, ~1.67-2 sec/curve).
- **van Bommel-Chidambaram-Costa-Kieffer 2024–25 isogeny-class database** with massive indecomposable rational isogenies (degrees 22, 34, 114, up to 312).
- **Sutherland + Poor-Yuen 2025 paramodular forms tabulation through level 251** (incomplete above).

**Calibration-grade known-true-positive sets:**
- Boxer-Calegari-Gee-Pilloni 2025 unconditional modularity for ~11,384 LMFDB curves — gold-standard calibration anchor for any modular-prediction work.
- 52 Sato-Tate group classification (Banaszak-Kedlaya, made unconditional 2022) — discrete classification target with absolute right answer.
- Rank-prediction via murmurations (transfer-learned from elliptic curves, per IAIFI / He-Lee-Oliver 2023–24).

**Concrete Ergon ingestion path:** This domain is closest to Ergon's existing EC work. Expand `ergon/scripts/` to include genus-2 versions of Tamagawa, Sha, isogeny-class projections (the EC zero projections in current work queue can be extended). The 2025 Shi Las Vegas $O(\log^{2+o(1)} p)$ algorithm enables 10-4100× faster L-function computation — practical infrastructure improvement.

**Cross-cutting calibration insight:** all three domains exhibit "murmuration" phenomena (knots: Khovanov-to-$s$-invariant correlation; Maass GL(3): symmetric-square-lift murmurations of $a_f(p^2)$; genus-2: rank/parity murmurations confirmed in Sutherland 2023–24). Murmuration is itself a calibration meta-pattern — Prometheus substrate should have a `MurmurationSignature` primitive (proposed for v0.2.0) that registers across all three Tier-F domain bundles.

---

## 7. Methodology insights (Wave 4)

### AlphaEvolve forensics (report 10)

**What's reproducible:** the architectural pattern (asynchronous evolutionary loop, prompt sampler + LLM mutator + automated evaluator + MAP-Elites/island-based program database) is fully open via OpenEvolve (Sharma et al.) and CodeEvolve / ShinkaEvolve. License-clean and implementable on consumer hardware. The "evolve-block-start / evolve-block-end" markup convention is open. Multi-objective optimization with cascade evaluation is open.

**What's locked behind DeepMind tooling:** the Gemini Pro / Flash ensemble itself; the 14-target matrix-multiplication parallel sweep used for the rank-48 result; the exact prompts used for the 15 mutation suggestions; the planetary-scale Borg / Gemini kernel optimization deployment.

**Poor-man's Prometheus version recommended architecture (from report 10 §7):**
1. **Island-based architecture** (mandatory at 3B–4B because mode collapse is severe).
2. **Aggressive cascade evaluation** (Tier 1 syntax check ms, Tier 2 low-fidelity sec, Tier 3 high-fidelity min/hr) because 3B–4B models will saturate the gate with syntactic errors.
3. **Inspiration-based crossover** (LLM merging two parent programs) rather than pure mutation.
4. **Meta-prompt optimization** — system continuously updates its own prompt template per error-feedback channel.
5. **Target the search algorithm, not the math** — task the 3B–4B model with mutating gradient-descent loss functions and hyperparameter schedules in PyTorch/JAX skeletons; offload the actual mathematical heavy lifting to PyTorch optimizers.

**Concrete recommendation for the Apollo/Rhea pipeline:** if Prometheus pursues a poor-man's-AlphaEvolve, use **Phi-4-Mini 3.8B** or **Qwen2.5-Math-7B (4-bit quantized)** as the mutation engine; pair with `ergon/scripts/` PyTorch skeletons whose `# EVOLVE-BLOCK-START / # EVOLVE-BLOCK-END` markers wrap the gradient-search heuristics for tensor decomposition or border-rank witness construction. **Behavior delta:** evolves new tensor-side attack tactics directly into substrate-canonical form.

### SoS for tensor problems (report 11)

**Tractability frontier:**
- $k=2$ (degree-4 SoS): production-viable for $n \approx 100-500$.
- $k=4$ (degree-8 SoS): toy instances ($n \le 50$).
- $k=6$ (degree-12 SoS): theoretical only; $n < 20$ on physical hardware. **Critical** because $k=6$ is the level needed to break the matrix-unfolding barrier in tensor completion.
- $k=8$ (degree-16 SoS): pseudo-calibration constructions only.

**Practical implications for substrate-tester:** any agent claim of "polynomial-time SoS recovery at level 6 or higher" must be flagged as `theoretical_only` unless a concrete computation with $n \ge 20$ is exhibited. MOSEK warnings (`MSK_RES_WRN_ZEROS_IN_SPARSE_ROW`) from SOSTOOLS / YALMIP / SumOfSquares.jl are diagnostic of formulation problems, not solver bugs.

**The 2024–2026 paradigm shift:** SoS is now the *theoretical lower-bound tool* (via pseudo-calibration + LDLR + type-2-constant geometry) rather than the *algorithmic upper-bound tool*. Faster algorithms (NSGA, Kikuchi hypergraph counting) match the SoS threshold without paying the SDP overhead. AA-023 must be enforced.

### Tensor networks in QMB (report 12)

**Cross-pollination opportunities for Prometheus:**
- **Tensor-network engineering already operates at scales ($D = 4000-6000$, millions of parameters per tensor) that algebraic-geometry tensor work cannot reach.** This is HARD-3 actionable: Prometheus's Tier-A++ `TensorNetwork` primitive should adopt the QMB software conventions (block-sparse symmetry, AD-CTMRG for environment optimization, PEPS for 2D area-law, MERA / isoTNS for hierarchical / volume-law) rather than reinventing them.
- **The cultural gap between AG and QMB is a substrate opportunity, not a barrier.** AG provides the rigorous rank invariants (cactus, border-cactus, Waring) that QMB software does not track; QMB provides the production-scale numerical infrastructure that AG cannot. Prometheus, by hosting both vocabularies in one substrate, can be the bridging layer.
- **Concrete recommendation:** integrate ITensor.jl or quimb as a recommended Tier-A++ runtime backend (via FFI / direct memory bindings, NOT IPC string serialization per report 17 §5 lessons).

**Anti-anchor reading from report 12:** the QMB community uses SVD-based matrix rank exclusively because it dictates computational memory cost. Do NOT propagate "tensor rank = SVD rank" anywhere in substrate; this is a HARD-5 / PATTERN_RANK_PARITY_LEAK risk at the cross-community translation layer.

---

## 8. Learner v1.0 inputs (Wave 5)

### Math-reasoning corpora (report 13)

**Anchor-density-first prioritization for v1.0 corpus mix:**

| Corpus | Recommended sampling weight | Rationale |
|---|---|---|
| **Mathlib (Lean)** | High (upsample) | Apache 2.0; 100% formal anchor density; >100K theorems |
| **ProofNet** | High (upsample) | MIT; 30% theorem / 70% proof; 371 examples (small but pure) |
| **MATH** | Medium | MIT; 5% theorem / 15% proof / 60% computation / 20% expository; competition-style |
| **MiniF2F** | Medium | MIT; 480 cross-system formal exercises |
| **Step-DPO 10K** | Medium | step-level preference pairs; in-distribution from policy model > GPT-4-generated |
| **MetaMathQA** | Medium | FOBAR backward-reasoning is the key augmentation |
| **MAmmoTH MathInstruct** | Medium | hybrid CoT + PoT; 12M multimodal entries |
| **OpenWebMath / MathPile** | Low (heavy filter) | 40-45% expository prose; must strip per AA-pipeline |
| **GSM8K** | Low | functionally solved; n-gram contamination per report 14 §7 |
| **NaturalProofs** | Low-Medium | CC-BY-SA 3.0 dual-licensed; bridge informal to formal |

**License check summary:** Mathlib (Apache 2.0), ProofNet (MIT), MATH (MIT), GSM8K (MIT), MiniF2F (MIT), NaturalProofs (CC BY-SA 3.0 / MIT mix), MathPile (CC BY-NC-SA 4.0 — **non-commercial only, blocks downstream**), OpenWebMath (ODC-By 1.0 — Common Crawl ToU constraint), Coq stdlib (LGPL), Isabelle AFP (BSD-style + LGPL). MathPile is the only material non-commercial blocker; substitute with OpenWebMath + heavy filtering for v1.0.

**Underexplored corpora to register as Tier-F calibration sources:** LMFDB (1B+ statements, number theory), Stacks Project (algebraic geometry + commutative algebra, Tag system enables fine-grained anchoring), Knot Atlas RDF (topology). All three feed Wave 3 calibration battery work.

**Anti-anchor flag pipeline for corpus filtering** (report 13 §7):
1. `SemanticMismatchFilter` — drop autoformalization attempts that fail Lean/Coq compilation due to implicit-assumption omissions.
2. `UnreasonableMathProblemFilter` — drop trajectories that don't terminate against UMP-benchmark-style flawed-problem tests.
3. `SoundnessGapFilter` — drop trajectories with correct final answer but invalid intermediate steps (process supervision, not outcome supervision).
4. `BoilerplateOverheadFilter` — Lynx + LLM-based standardization for HTML stripping (Nemotron-CC-Math style).
5. `VerboseDeflectionFilter` — drop n-gram-loop / repetitive-thinking-block trajectories.

### 3B–4B locally-runnable models (report 14)

**Concrete recommendation for Apollo / Rhea given 17GB VRAM ceiling:**

**Tier 1 candidate: Phi-4-Mini 3.8B (Microsoft, MIT license).** Best fit at 3B–4B; FP16 needs ~7.6GB; INT4 ~3GB. MATH: 64% (0-shot CoT); GSM8K: 88.6% (8-shot CoT). **Hard caveat:** SambaY hybrid state-space-attention architecture means TransformerLens compatibility is **not native** — recommend `nnsight` instead for activation tooling.

**Tier 2 candidate: Qwen2.5-Math-1.5B (Alibaba, Apache 2.0).** Sub-4B, fits everywhere; MATH 49.8% (CoT) / 79.7% (TIR — must declare TIR usage per AA per report 14 §7). Native Qwen2.5 architecture, full TransformerLens support. Use as fastest baseline / activation-tooling lane.

**Tier 3 candidate: DeepSeek-R1-Distill-Qwen-1.5B (DeepSeek, MIT).** R1 reasoning-trace distillation; built on Qwen2.5; MATH-500 ~83%; AIME 2024 ~28-29%. DeepScaleR-1.5B community fine-tune pushes AIME to 43%. Use for chain-of-thought research where explicit `<think>` blocks are needed.

**Tier 4 / formal-proving lane: Llemma-7B (Princeton et al., MIT-style).** 4-bit quantized fits in 17GB; CodeLlama-7B initialized; trained on Proof-Pile-2 200B tokens; tailored for Lean/Isabelle. **Required** if Prometheus's downstream goal includes formal theorem proving (e.g., Wave-3 LMFDB → Mathlib autoformalization).

**Inference framework on Win11/NVIDIA:** vLLM (FP16 / AWQ / GPTQ); llama.cpp + Ollama (GGUF); **NEVER MLX** (Apple-Silicon only; engineering deadlock per report 14 §6).

**Behavior delta for Ergon:** the model recommendation can be operationalized in a single PR — `ergon/pipeline_d/model.py` registers `ModelEvalProfile` for Phi-4-Mini, Qwen2.5-Math-1.5B, DeepSeek-R1-Distill-1.5B, Llemma-7B (4-bit). v1.0 trial-2 harness (currently soft-blocked on this Wave-5 finding per WORK_QUEUE_2026-05-10 §B1) is unblocked.

### Symbolic regression / program synthesis (report 15)

**Direct impact on substrate-vocabulary-as-action-space bet:**

1. **PySR + DSO + SymbolicGPT all converge on context-free or attribute-grammar-constrained discrete action spaces** with masking-based validity enforcement at the sampling step. This is the closest mature analogue to Prometheus's substrate vocabulary as "discrete action space."

2. **DreamCoder / LILO / Stitch library-learning pipelines** demonstrate that automated abstraction discovery (compressing recurring patterns into named lambdas / tactics) can be operationalized via E-graph matching + branch-and-bound search. **For Prometheus, this means substrate-vocabulary expansion can itself be automated** — when many composite witnesses repeatedly co-instantiate the same sub-pattern, automatically promote to a new primitive. The naming step is LLM-assisted (LILO style).

3. **TacMiner Tactic Dependence Graphs** is the most directly applicable algorithm for Prometheus — applies to tactic-style proof refactoring, which maps directly onto attack-paradigm refactoring (e.g., if many P29 BorderApolarity attacks share the same scheme-smoothability subroutine, promote to a sub-tactic).

4. **HyperTree Proof Search (HTPS) + AlphaProof** demonstrate that MCTS over typed grammars works at IMO-medal level. Prometheus has the typed grammar (substrate vocabulary); building MCTS over it is mechanically feasible. **Speculative but not crazy:** an `AlphaProof-for-tensor-substrate` would be a long-term Wave-7 paradigm candidate.

**Honest assessment:** symbolic regression and program synthesis don't directly hand Prometheus a finished tool, but they validate the architectural bet (typed action space + automated abstraction discovery + MCTS-style search). Behavior delta: the substrate-vocabulary-as-action-space framing is now **literature-backed by 4 independent research thrusts**.

---

## 9. Substrate vocabulary expansion (Wave 6)

### Type theory / categorical foundations (report 16)

**Mathlib's organization vs Prometheus's tier hierarchy:**

| Mathlib organizing principle | Prometheus equivalent | Adopt? |
|---|---|---|
| Semi-bundled typeclasses (carrier unbundled, axioms bundled) | Tier-A through Tier-E with unbundled carrier types and bundled axioms | YES — already aligned |
| Multiple inheritance via `extends` clauses | Tier-B sub-types via parent-class chains | YES — already aligned |
| Diamond problem / judgmental equality enforcement | PATTERN_RANK_PARITY_LEAK (cross-coordinate non-collapse) | YES — direct analog |
| Strict CI linter ecosystem (overlapping instances, brittleness) | substrate-tester probes for primitive interface contract drift | YES — extend with v0.2.0 linters |
| `[deprecated]` tag with deprecation linter | substrate-vocabulary version.json + frozen-interface contracts | YES — adopt the IDE-warning UX |
| Monolithic continuous integration (`bors` bot) | per-PR substrate-tester full-battery run | PARTIAL — Prometheus is multi-repo; adopt cross-repo CI gating |

**Where Prometheus deliberately diverges (Wave 6 distinctive insight):** Mathlib refactors aggressively and forces downstream to adapt; Prometheus's **frozen-interface registry** stands deliberately stable, with **anti-anchor pins** to allow internal upgrades without semantic-guarantee breakage. This is genuinely novel per report 16 §7.

**Substrate-vocabulary v0.2.0 patch recommendations:**

1. **Add Tier-F (Domain-Anchor) and Tier-G (Method-Synthesis)** per §4 above.
2. **Upgrade `composition_rules.md` schema** to record explicit `categorical_structure: {Multicategory, ColoredPROP, TracedSymmetricMonoidal}` per rule. Default: Multicategory (n-input, 1-output) for the existing Tier-B × Tier-D and Tier-B × Tier-E rules.
3. **Add `linear_type_use_constraint` field** per primitive: `{exactly_once, at_most_once, freely_duplicable}`. Required for any primitive that records a consumed resource (e.g., a `BorderRankWitness` is exactly-once when it's the input to a strict-gap composition).
4. **Add a `failure_mode_taxonomy` section** to `primitives.md` documenting the diamond-problem analogues (PATTERN_RANK_PARITY_LEAK at the cross-tier-inheritance layer, typeclass-coherence failures at the cross-attribution layer).

### DSL design (report 17)

**Adopt:**
- Magma's **strong typing via parent structures** (Tier-A++ engagement; every tensor object lives in a registered ambient space, never untyped).
- SymPy's **assumptions system + lazy evaluation** (Tier-B and Tier-C primitives respect HARD-5: never collapse coordinates without explicit user-declared compatibility).
- SymPy's **strict 1-year deprecation cycle** (per report 17 §2.3; aligns with Mathlib `[deprecated]` linter).
- SymPy's **core-vs-applications module split** (Tier-A++ / Tier-A as core, Tier-D / Tier-E / Tier-F / Tier-G as applications).
- Julia / AbstractAlgebra.jl's **multiple dispatch + parameterized types** (key for cross-tier composition; aligns with multicategorical formalism).
- Wolfram Data Framework's **Entity / Quantity types with dimensional analysis** (Tier-F domain-anchor primitives carry units and ontological tags).

**Reject:**
- Mathematica's flat namespace (5,000+ built-ins at top level) — Prometheus uses explicit hierarchical module namespaces.
- SageMath's IPC string serialization for federation — use direct FFI / C-bindings (Cython-style libpari wrapping, not pseudo-TTY GAP wrapping).
- Pari/GP's untyped GP scripting (use only the rigidly typed PARI C-kernel layer).

### Composition-rule formalism recommendation (report 18)

**For Tier-B × Tier-D and Tier-B × Tier-E (single-output compositions):** **Multicategory (Colored Operad)** is the precise mathematical fit. Tiers are colors; composition rules are multimorphisms; multifunctorial preservation is the guarantee.

**For multi-output compositions (e.g., candidate Tier-B × Tier-D × Tier-E full-GCT-depth):** **Colored PROP** generalizes to $m$-input, $n$-output. Adopt only when actually needed (Wave 1 candidate composition 7).

**For cyclic / recursive compositions:** **Traced Symmetric Monoidal Category** with Joyal-Street-Verity coherence. Not yet needed but flagged in `composition_rules.md` TODO.

**For "use-once" enforcement:** **Linear Type System** (Girard) overlaid on the multicategorical formalism. Tier-G primitives that synthesize search algorithms naturally need linear types because the synthesized algorithm is a one-shot artifact.

**Implementation substrate:** **GATlab (Julia)** strongly recommended over Coq. Generalized Algebraic Theories provide the dependent-type structure for typed composition without Coq's exponential type-checking penalty (per report 16 §1, report 18 §6). Catlab.jl provides the categorical-doctrine framework.

**Concrete v0.2.0 patch recommendation for `composition_rules.md`:** add a header field per rule:
```
categorical_structure: Multicategory   # or ColoredPROP, TracedSymmetricMonoidal
input_colors: [TierB, TierD]
output_color: TierB
preservation: multifunctorial
linear_type_use_constraint:
  TierB_input: exactly_once
  TierD_input: at_most_once
```

This formalizes what is currently natural-language documentation and enables substrate-tester to algebraically reject ill-typed compositions before they execute. **Behavior delta:** substrate-tester gains a new capability class — categorical-type-checker probes that fire at composition time, not at probe time.

---

## 10. Updates to Ergon work queue

Specific items to add or modify in `ergon/WORK_QUEUE_2026-05-10.md`:

**ADD: Branch B item B0 (model-zoo registration unblock).** Wave 5 finding makes the soft-block on B1 resolvable in a single PR. Action: register `ModelEvalProfile` instances in `ergon/pipeline_d/model.py` for {Phi-4-Mini 3.8B, Qwen2.5-Math-1.5B, Qwen2.5-Math-7B (4bit), DeepSeek-R1-Distill-Qwen-1.5B, Llemma-7B (4bit)}; pull via Hugging Face into `ergon/models/`. Behavior delta: B1 trial-2 harness unblocked.

**ADD: Branch C item C-Wave3 (Tier-F domain-anchor pull).** Pull LMFDB GL(3) Maass forms (conductors $N=1,4,9$) and apply AA-019 sign-source partition. Pull LMFDB genus-2 expansion (5M curves) and apply Boxer-Calegari-Gee-Pilloni 2025 modularity-status partition. Pull Knot Atlas RDF subset (limit by girth ≤ 14 for tractability). Behavior delta: substrate gains 3 calibration-grade Tier-F bundles for HARD-3 cross-domain calibration.

**ADD: Branch B item B-PoorMansAlphaEvolve (speculative).** Stand up a 1-instance `ergon/scripts/evolve_tensor_decomposition.py` skeleton implementing the report 10 §7 5-element architecture (island populations, cascade evaluation, inspiration crossover, meta-prompt opt, target-the-search-not-the-math). Use Phi-4-Mini 3.8B (or Qwen2.5-Math-7B 4bit) as mutation engine. Target: rediscover Strassen rank-7 for $2\times2$. Behavior delta: minimal proof-of-concept that AlphaEvolve architecture works locally; if successful, scale to $3\times3$ which is currently $\underline{R}(M\langle 3 \rangle) \in [17, 21]$.

**MODIFY: Branch A items (math-research loop).** Add explicit AA-019 (Maass GL(3) root number) and AA-020 (BCGP 2025 modularity proportion) compliance checks to all `maass_gl3_*` scripts and any genus-2 extension scripts. Behavior delta: scripts become Wave-3-aware before consuming new datasets.

**MODIFY: Branch A item A2 (EC zero projections).** When extending to genus-2, register results under the new `AbelianSurfaceArithmeticBundle` Tier-F primitive rather than ad-hoc JSON. Use Shi 2025 $O(\log^{2+o(1)} p)$ Las Vegas algorithm if implementing local L-polynomial computation from scratch.

---

## 11. Updates to Techne work queue

Specific items to add or modify in `techne/WORK_QUEUE_2026-05-10.md`:

**ADD: Wave 1.5 (between Wave 1 and Wave 2) — register the 11 new anti-anchors.** Per `feedback_verify_upstream_attributions.md`, AA-013 through AA-023 should be added to `techne/registry/anti_anchors.jsonl` with `verified_against_primary: false` for the 6 [VERIFY-LIVE] items pending live primary-source pinning. Anchors AA-013 (Strassen-7), AA-014 (Border Comon's), AA-016 (BBvH matrix-only), AA-018 (Khovanov girth), AA-022 (AlphaEvolve meta-discovery), AA-023 (SoS not-the-only-algorithm) are the highest-priority for immediate registration (medium-high to high risk; PROPAGATE-ready).

**ADD: Wave 2.5 (parallel with Wave 2) — register Wave-2 Tier-B continuations.** New Tier-B sub-types from §4: `SmallTensorAdditivitySafeZone`, `MinimalBorderRankComonWitness`, `BellNumberDeterminantBound`, plus the outside-tier `PermanentNonExistenceCert`. Sources: T#5, T#6, T#20, T#86. Cross-link to AA-013, AA-014, AA-015.

**ADD: Wave 2.6 — register Wave-2 Tier-D continuations.** New Tier-D sub-types: `RandomTensorConcentrationCert.PACBayesian` (Aden-Ali 2025), `RandomTensorConcentrationCert.DeterministicMomentMethod` (Dartois-McKenna 2026). Cross-link to AA-016 (BBvH matrix-only).

**ADD: Wave 3 (NEW) — introduce Tier-F (Domain-Anchor) tier.** Open contract-change window declaring `expected_close: 2026-05-26`, `predeclared_primitives: [KnotInvariantBundle, MaassGL3SpectralBundle, AbelianSurfaceArithmeticBundle, MurmurationSignature]`. Update `aporia/doctrine/substrate_vocabulary/primitives.md` with new tier section. Cross-link to AA-017, AA-018, AA-019, AA-020.

**ADD: Wave 4 (NEW) — introduce Tier-G (Method-Synthesis) tier.** Open contract-change window declaring `predeclared_primitives: [AlgorithmEvolutionaryLoop, SoSCertificate, TensorNetworkContraction (lifted), StepLevelPreferencePair, TheoremProverFeedbackTrace, ModelEvalProfile]`. Cross-link to AA-021, AA-022, AA-023.

**ADD: Wave 5 (NEW) — composition-rule schema upgrade.** Update `composition_rules.md` schema to record `categorical_structure`, `input_colors`, `output_color`, `preservation`, `linear_type_use_constraint` fields per rule. Promote `MulticategoricalCompositionRule`, `ColoredPROPCompositionRule`, `LinearTypeUseConstraint` substrate-meta-primitives. Cross-link to Wave 6 reports 16, 17, 18.

**ADD: Wave 6 (NEW) — failure-mode taxonomy section in primitives.md.** Document the diamond-problem analogues (PATTERN_RANK_PARITY_LEAK at cross-tier-inheritance layer; typeclass-coherence failures at cross-attribution layer) per report 16 §5. This is preventive substrate-tester work — these failure modes WILL appear when Tier-F and Tier-G compose with existing Tier-B and Tier-E primitives.

**MODIFY: Wave 1 expected_close.** With 6 new waves added to the queue, the Wave 1 expected_close 2026-05-19 is unchanged (Wave 1 is independent), but downstream Wave numbering shifts. Re-version the queue header with a 6-wave schedule across 2026-05-12 to 2026-06-23.

---

## 12. Honest caveats

**Prompts 19–20 unfired.** The TBD wildcards were deferred. Whatever they were intended to probe is missing from this synthesis. Recommend: re-prompt Wave 7 with the two outstanding slots once the v0.2.0 substrate vocabulary is shipped, so the next batch can probe whatever Tier-F or Tier-G work surfaces gaps in.

**Reports of variable depth.** Report 09 (genus-2) leaned heavily on the BCGP 2025 paradigm event but spent §7 on "anti-anchor flags" that were generic LLM-context-engineering text rather than mathematical anchors — that section reads as prompt-template padding. Report 12 (tensor networks in QMB) is exceptionally rich and substantive; its §7 cultural-gap analysis is one of the highest-leverage paragraphs in the entire batch. Report 14 (3B–4B models) is operationally precise and ready to action immediately. Reports 16, 17, 18 are mature and convergent on multicategorical / linear-type recommendations — high confidence in the Wave 6 conclusions.

**Live verification still required for these claims:**
- AA-013 (Rupniewski 2024 small-tensor safe zone exact bound `R \le 7`)
- AA-014 (Mańdziuk-Ventura 2024 minimal border-rank Comon `n ≤ d+1` regime)
- AA-020 (BCGP 2025 modularity proportion exact statement of the 3-distinguished big-image hypothesis)
- AA-021 (AlphaTensor field-of-definition over $\mathbb{F}_2$ vs $\mathbb{C}$ — the report's claim that AlphaTensor failed over $\mathbb{C}$ should be primary-pinned via the Nature paper)
- T#86 catalog edits (Houston-Goucher-Johnston Bell-number bound + Han-Ju-Kim 2025 $\det_4 = 12$, $\text{perm}_4 = 8$ exact values)
- T#93 catalog edits (Bürgisser-Doğan-Makam-Wigderson 2026 torus-action P-time)

These should be pinned before any substrate-tester probe is built directly on them, per the Wave 1 lesson.

**Behavior-delta tracing per `feedback_substrate_passive_consumer_warning.md`:**
- §2 (catalog updates) → consumer: Learner v1.0 corpus + substrate-tester probes (catalog drives anchor pinning).
- §3 (anti-anchors) → consumer: substrate-tester / Learner training corpus filter.
- §4 (primitives) → consumer: Techne v4.0 contract-change window (Tier-F, Tier-G additions).
- §5 (paradigms) → consumer: `attack_angle_taxonomy.md` register (P32 promote, P34/P35 add).
- §6 (calibration) → consumer: Ergon Tier-F bundle ingestion (already in §10 work queue).
- §7 (methodology) → consumer: speculative `evolve_tensor_decomposition.py` (in §10 work queue).
- §8 (Learner inputs) → consumer: Ergon `pipeline_d/model.py` (already in §10 work queue, item B0).
- §9 (vocabulary) → consumer: Techne v0.2.0 schema upgrade (already in §11 work queue, Wave 5).

Every recommendation traces to a Techne registration, an Ergon training input, or a vocabulary update. **No new .md docs are proposed without a downstream consumer.**

**HARD-2 anti-gravitational-well audit:** the batch contains three strong gravity wells the synthesis explicitly resists:
1. "AlphaEvolve / evolutionary-LLM is the future" → resisted by AA-022 (meta-discovery vs direct search) and the §7 Methodology insights framing.
2. "BBvH free probability solves log factor everywhere" → resisted by AA-016 and §2 row T#71.
3. "Lean/Mathlib is the right substrate organization for everything" → resisted by §9 (Wave 6 distinctive divergences: frozen-interface, anti-anchor pins, multicategorical formalism over Mathlib's typeclass model).

**HARD-3 audit:** tensor-related findings get explicit priority. Wave 2 (border-rank cluster, additivity, det/perm) is the densest in this batch, generating 4 of the 11 anti-anchors and 7 of the 18 primitive proposals. Wave 6 multicategorical formalism feeds directly into the Tier-B × Tier-D and Tier-B × Tier-E rules that govern tensor-substrate composition.

---

## 13. Report manifest

```
aporia/docs/deep_research_batch_2026-05-10/
├── 01_verify_anti_anchors_aa_001_through_aa_004.md
│   — Wave 1: AA-001 (GCT) confirmed; AA-002 (Zauner) refined; AA-003 (Hillar-Lim)
│     citation corrected arXiv:1605.07532 → arXiv:1611.01559; AA-004 (Saxl) INVERTED
│     to OPEN; new AA-011 SAXL_CUBE_ANCHOR + AA-012 TENSOR_RANK_Z_UNDECIDABLE.
├── 02_verify_anti_anchors_aa_005_through_aa_007.md
│   — Wave 1: AA-005 (cactus barrier 6m-4) confirmed; AA-006 (Lucca attribution)
│     confirmed; AA-007 (tensor type-2 not sqrt-log-d) confirmed via Aden-Ali 2025.
├── 03_verify_anti_anchors_aa_008_through_aa_010.md
│   — Wave 1: AA-008 (equivariant-not-unrestricted) confirmed; AA-009 (border cactus
│     fifth rank) confirmed via Buczyńska-Buczyński Jan 2026; AA-010 (five-application
│     convergence) confirmed.
├── 04_border_rank_cluster_t_5_t_6_t_20.md
│   — Wave 2: M⟨3⟩ ∈ [17, 21] still; cactus barrier for m=9 is 50; Strassen
│     additivity Rupniewski 2024 safe zone R ≤ 7 + dim ≤ 4; Border Comon's true at
│     n ≤ d+1, tame, sharp tensors; standard Comon's killed by Shitov 2018.
├── 05_additivity_operator_norm_cluster_t_23_t_24_t_71.md
│   — Wave 2: Rupniewski 2024 safe-zone re-confirms; T#24 four-paper cluster
│     Boedihardjo / BGJLR / Aden-Ali / Dartois-McKenna; T#71 BBvH free-probability
│     matrix-only; PAC-Bayesian removes log for tensors in subgaussian regime.
├── 06_permanent_orbit_closure_t_86_t_93_t_21.md
│   — Wave 2: Bell-number bound R(det_n) ≤ B_n (Houston-Goucher-Johnston 2024);
│     R(det_4) = 12, R(perm_4) = 8 (Han-Ju-Kim 2025); TOCI complexity class for
│     orbit closure intersection; R(perm_3) = 16 < generic 19; permanent has no
│     Bell-number analog in char ≠ 2.
├── 07_knots_khovanov_homology_2024_2026_frontier.md
│   — Wave 3: Burton 1.847B prime knots through 20 crossings; Lackenby 2021 quasi-
│     poly unknot recognition pre-publication; Ren-Willis 2024 first analysis-free
│     exotic 4-manifold via skein lasagna; Schmidhuber 2025 Khovanov BQP/DQC1/#P-
│     hard; Quantinuum H2 Jones polynomial 600-crossing braid demonstration.
├── 08_maass_gl_3_spectral_forms_2024_2026.md
│   — Wave 3: Bian-Booker baseline; Farmer-Koutsoliotas-Lemurell expansion;
│     Cui-Wang-Peng 2025 explicit GL(3) trace formula; Kwan 2024-25 period
│     integral spectral moments bypass Kuznetsov; LMFDB ML-predicted vs proven
│     root numbers (AA-019).
├── 09_genus_2_curves_2024_2026_frontier.md
│   — Wave 3: Sutherland 5M curve LMFDB expansion; Boxer-Calegari-Gee-Pilloni
│     2025 unconditional modularity for positive proportion of abelian surfaces
│     over Q (paradigm event); van Bommel 2024-25 isogeny algorithm; murmurations
│     in genus-2 transferred from elliptic curves; Shi 2025 Las Vegas L-function.
├── 10_alphaevolve_workflow_forensics.md
│   — Wave 4: AlphaEvolve architecture decomposition (asynchronous loop, prompt
│     sampler, LLM ensemble, evaluator, MAP-Elites database); 4×4 rank-48 over
│     C via meta-discovery (evolves the search algorithm); 50 problems 75% match
│     SOTA + 20% new SOTA; OpenEvolve / CodeEvolve open-source replications;
│     blueprint for poor-man's-Prometheus version with 3B-4B models.
├── 11_sum_of_squares_hierarchies_for_tensor_problems_2024_2026.md
│   — Wave 4: SoS for tensor PCA / completion / rank; NSGA + Kikuchi match SoS
│     threshold without SDP overhead; tensor spectral norm ∃R-hard 2026; SDP
│     tractability ceiling at level 4; pseudo-calibration + LDLR for lower bounds;
│     T#72 type-2 constant geometry as the SoS lower-bound limiter.
├── 12_tensor_networks_in_quantum_many_body_2024_2026.md
│   — Wave 4: DMRG/MPS frontier D=4000-6000; iPEPS via CTMRG with AD; MERA /
│     hyperinvariant / holographic isoTNS for volume law; lattice gauge theory
│     bypasses sign problem; Tensor Train + Saten for LLM compression; deep
│     cultural gap between AG (rank invariants) and QMB (numerical infrastructure)
│     is the cross-pollination opportunity for Prometheus.
├── 13_math_reasoning_training_corpora_landscape_2024_2026.md
│   — Wave 5: Major corpora (MATH / GSM8K / MiniF2F / ProofNet / NaturalProofs /
│     MathPile / OpenWebMath / ArXiv-Math / Mathlib / Coq / Isabelle); MetaMath
│     / MAmmoTH / ToRA / DeepSeek-Math augmentation pipelines; Step-DPO step-level
│     preference; theorem-prover-as-judge feedback loop; LMFDB / Stacks Project /
│     Knot Atlas underexplored; anti-anchor flag pipeline for corpus filtering.
├── 14_3b_4b_locally_runnable_math_models_current_sota.md
│   — Wave 5: 17GB VRAM ceiling analysis; Phi-4-Mini 3.8B as primary 3-4B
│     candidate (caveat: SambaY hybrid breaks TransformerLens); Qwen2.5-Math-1.5B
│     and DeepSeek-R1-Distill 1.5B as fast baselines; Llemma-7B 4-bit for formal
│     proving; vLLM / llama.cpp / Ollama; MLX explicitly incompatible; MATH-80%
│     claims rely on TIR Python execution, not pure forward pass.
├── 15_symbolic_regression_program_synthesis_frontiers_2024_2026.md
│   — Wave 5: PySR / DSO / SymbolicGPT discrete grammars; DreamCoder / LILO /
│     Stitch library learning; FunSearch / AlphaEvolve / SOAR LLM-as-mutator;
│     Mathlib / Sledgehammer / Magnushammer / Tactician for premise selection;
│     HyperTree Proof Search and AlphaProof for MCTS over typed grammars; opera-
│     tional categorical formalisms for substrate-vocabulary-as-action-space bet.
├── 16_type_theory_categorical_foundations_for_primitive_registries.md
│   — Wave 6: Lean/Coq/Isabelle/Agda dependent-type registries; semi-bundled
│     typeclasses optimal; multicategories (colored operads) for Tier-B × Tier-D
│     composition; PROPs for multi-output; traced monoidal for cyclic; library
│     learning via Stitch / LILO / TacMiner; failure-mode taxonomy (diamond
│     problem); Mathlib versioning (`bors` + `[deprecated]`); Prometheus distinct-
│     ively diverges via frozen-interface + anti-anchor pins.
├── 17_dsl_design_for_mathematical_reasoning.md
│   — Wave 6: Mathematica flat namespace; SymPy core/applications + assumptions
│     + 1-year deprecation; Magma universal-algebra parent structures; Pari/GP
│     untyped-GP-vs-typed-PARI; SageMath federation via IPC vs Cython; Julia
│     AbstractAlgebra.jl multiple dispatch; mapping each onto Prometheus tier
│     A++ through E with explicit adopt/reject calls.
├── 18_composition_rule_literature_operads_props_multicategories.md
│   — Wave 6: Symmetric / non-symmetric / colored operads; PROPs (Mac Lane 1963);
│     multicategories synonymous with colored operads; substructural type systems
│     (linear / affine / separation logic) for use-once enforcement; multi-
│     functorial composition; GATlab (Julia) > Coq for performance; concrete
│     recommendation Multicategory + Linear Types + GATlab for Prometheus v0.2.0.
└── _dispatch_summary.jsonl
    — Dispatch metadata.
```

End of synthesis.
