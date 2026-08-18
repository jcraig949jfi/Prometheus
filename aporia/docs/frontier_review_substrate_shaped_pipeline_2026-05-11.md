# Frontier Review: Substrate-Prerequisite-Shaped Deep Research Pipeline

**Date:** 2026-05-11
**For:** Independent assessment by frontier models (GPT, Gemini, Claude, NotebookLM)
**Author:** Aporia (Project Prometheus)
**Type:** External viability review of an architectural epiphany

---

## How to read this document

You are being asked to assess the **viability** of a proposed change to how Project Prometheus consumes external literature. You have no prior context. Sections 1-6 are background — read them so you understand what's being changed. Section 7 is the proposed change. Section 8 is a concrete example showing what the substrate looks like today. Section 9 is the proposed pipeline. Section 10 lists specific questions.

You are *not* being asked to praise or hedge. The project's standing doctrine includes "anti-gravitational-well: every LLM has a gradient toward conventional framings — resist them." If the epiphany is poorly conceived, please say so directly and explain why.

---

## 1. Executive context

Prometheus dispatches ~20 Gemini Deep Research queries per day on a paid-tier Gemini Pro account. Each query returns a 25-50KB literature-survey report with primary-source citations. Yesterday's batch of 18 prompts surfaced 11 new "anti-anchor" candidates (pinned false claims that LLM training data tends to fabricate), 18 new substrate primitive proposals, 9 catalog updates, and 4 paradigm candidates — *after* a human/Claude synthesis pass distilled the narrative reports into structured registry entries.

**The proposed change:** modify the prompts so reports come back with both (a) the existing human-readable narrative and (b) machine-ingestible YAML blocks at the end, conforming to the substrate's existing JSONL schemas (`anti_anchor`, `primitive_proposal`, `composition_rule`, `catalog_edit`, `training_anchor`, `paradigm_candidate`). A parse/validate/stage pipeline would then route these blocks into the canonical registries with arXiv-citation auto-verification gating ingestion.

**The bet:** ~30-50% reduction in synthesis time + mechanical catching of withdrawn-paper hallucinations (a Lee 2025 arXiv:2512.15035 case was caught yesterday only because a verification prompt happened to overlap the withdrawn paper).

**The risk:** schema lock-in, prompt-size bloat, hallucinated-but-plausible structured output, work-shift not work-elimination.

We want frontier review on whether the leverage estimate is honest, whether the schema design is sound, and whether the failure modes are adequately mitigated.

---

## 2. Project Prometheus — context

Prometheus is a multi-agent mathematical research substrate. Its philosophical anchor is David Silver's *Ineffable Intelligence* thesis ("LLMs are a dead end"). Its mathematical anchor is the convergence finding from internal experiments: **reasoning = dynamic updating, transformers suppress it, scaling hardens it.**

This means Prometheus is *deliberately-different* from frontier-LLM-scaling approaches. It does not aim to train a large reasoning model on conventional math corpora and call that done. It aims to:

1. Build a discrete, composable, neural-net-leverageable **symbol substrate** for mathematical attack (the vocabulary in §6 below).
2. Catalog open mathematical questions and the void structure around them (Aporia: 537 open questions, 14 domains).
3. Mine literature for "anti-anchors" — places where LLM training data has fossilized false or stale claims.
4. Train a small (~3-4B) Learner model on this substrate + corpus — not as a generic chatbot, but as an agent that can *navigate the symbol space*.
5. Use a falsification battery (the Sigma Engine + Substrate-Tester) to kill weak findings before they propagate.

The doctrine has hard constraints relevant to this review:
- **HARD-1:** no paper-publishing framing. The substrate is not a publication pipeline.
- **HARD-2:** anti-gravitational-well. Every conventional ML framing must be actively suppressed and rebalanced against the deliberately-different bet.
- **HARD-3:** tensor mathematics is "near and dear" to Prometheus; tensor primitives get priority weighting.
- **HARD-5:** distinct coordinates. Never collapse mathematically-distinct invariants (tensor rank ≠ border rank ≠ cactus rank ≠ ...). The substrate enforces this through tier-typed primitives.
- **HARD-6:** every artifact must trace to a behavior delta — model training, primitive registration, anti-anchor pin, catalog edit. Pure-documentation artifacts are explicitly discouraged.

The most relevant standing warning (added 2026-05-10): "substrate is at risk of becoming a beautifully falsifying machine forever while the model remains passive. Every doc must trace to a behavior delta."

---

## 3. The Learner (Ergon)

Ergon is the Prometheus agent whose north star is to become a trained model. It currently operates in two parallel modes:

**Math-research loop.** Frozen at 2026-05-02 reproducible milestone. A 4.76M-object × 208-feature tensor (`tensor.npz`, 28 MB) spans 23 mathematical domains (number fields, modular forms, elliptic curves, knots, OEIS sequences, Maass forms, genus-2 curves, etc.). Ready-to-run scripts include EC zero-projection tests, higher-gap analysis, Wachs reproduction, Tamagawa mediation. The tensor is the empirical substrate — every claim that propagates through Prometheus is checked against it.

**Learner MVP.** Paused at fire 15 (2026-05-08). 60 tickets deferred to v1.0. 5 confirmed blind-spots in current frontier models (named after under-cited mathematicians — Cohen, Helfgott, Faltings, McKay, Margulis). 9 failure-mode patterns documented. 4 fabrication archetypes. Deadline 2026-06-03 for v1.0 trainable model. Currently awaiting Aporia v1.0 corpus design.

The Learner's eventual action space is the substrate vocabulary (§6) — it will not predict tokens, it will navigate primitives + attacks + composition rules. This is the deliberately-different bet in concrete form.

---

## 4. The Sigma Engine

Sigma is Prometheus's substrate kernel — the executable runtime that the vocabulary registers into.

**Kernel design:**
- 25 frozen-dataclass primitives (all `@dataclass(frozen=True)`, content-addressed identity)
- 9 opcodes: `RESOLVE`, `CLAIM`, `FALSIFY`, `GATE`, `PROMOTE`, `ERRATA`, `TRACE`, `REWRITE`, `EQUIV`
- 3-valued GATE (true / false / unknown — no implicit closure)
- Linear capabilities (use-once primitives prevent silent reuse)
- Pre-tier P0 (CoordinateChart + CanonicalizationProtocol) load-bearing for all comparisons across heterogeneous spaces

**Current state:**
- 6 sigma_kernel modules hardened to ~0.85 average mutation score (from a ~0.25 baseline) via a 14-fire investigative chain
- Mutation-testing framework production-grade
- **94 contract tests across 35 classes queued** for the 5 unified meta-primitives that Techne (the substrate tools-registry) has not yet shipped: `TensorNetwork`, `ConstructiveExistenceWitness`, `GenericityAlmostEverywhereCert`, `RepresentationTheoreticInvariant`, `MomentPolytope`
- When Techne ships those 5 + the 2 P0 primitives in v4.0 Wave 1, the 94 tests un-skip and start running

This is important context for the epiphany: the Sigma Engine is *waiting for the vocabulary to be registered as executable primitives*. Faster ingestion = faster Sigma activation.

---

## 5. The Falsification Battery (Substrate-Tester)

The Substrate-Tester is a multi-instance loop that fires investigative chains (called "fires") at substrate claims. Its discipline is "kill everything that can be killed."

**Doctrine:**
- "Kills are the most valuable output" (`feedback_assume_wrong.md`)
- "All assumptions 100% wrong until proven" — fire battery is the proof requirement
- 4× false discoveries were killed by the battery in the last 30 days, each making the battery stronger (`feedback_false_profundity.md`)

**Fire structure:**
- Each fire is numbered, append-only ticketed, multi-instance-coordinated (`feedback_substrate_tester_multi_instance.md`)
- Cross-instance ticket amplification (when fire 15 on instance A surfaces a class of issue, instance B can pick it up at fire 16)
- Pull-before-pick discipline (always sync before claiming a fire number)
- Most recent: 14-fire chain on sigma_kernel modules lifted them from 0.25 → 0.85 mutation score

**Anti-anchor registry as falsification fossil layer:**
- 12 registered anti-anchors (AA-001 through AA-012, plus AA-011/012 added in yesterday's batch)
- Each is a pinned false claim with refutation citation
- Substrate-tester treats any agent output asserting the false form as a sentinel-violation
- Yesterday's Wave 1 verification of AA-004 caught a *self-injected* fabrication: the substrate had registered Saxl's conjecture as "SOLVED by Sellke 2025/26" when Lee 2025 (arXiv:2512.15035) was withdrawn within 3 days of posting due to mathematical gaps — and this stale claim had propagated through 4 documents before Wave 1 verification surfaced the error

The falsification battery's job, in part, is to catch exactly this kind of upstream stale-claim cascade.

---

## 6. The Symbolic Library (Substrate Vocabulary)

The vocabulary is the discrete grammar the Learner will eventually navigate. It is a 5-layer model (`aporia/doctrine/substrate_vocabulary/`):

**Layer 1 — Primitives (nouns).** What you produce as the result of attacking a problem. Currently 22 entries organized by tier:
- **Tier-A++ Networks/Signatures:** `TensorNetwork`, `ContractionOrderWitness`, `RankZooSignature`
- **Tier-B ConstructiveExistenceWitness:** `BorderRankWitness`, `CactusRankWitness`, `LimitWitness`, `ComputationalComplexityCertificate`, `WaringRankWitness`, `OrbitClosureNonMembershipWitness`, `GCTObstructionCertificate`, `BorderComplexitySeparator`, `EquivariantComplexityCertificate`, plus cross-cutting `DualityCheck`, `PrecisionFloorCertificate`, `ReshapingCertificate`, `MeasureZeroExceptionAnnotation`
- **Tier-C SecantVarietyEquation:** `DefectivityCertificate`, `MomentPolytope`
- **Tier-D distributional certificates:** `PhaseTransitionThreshold`, `AlgorithmThresholdCert`, `GenericityAlmostEverywhereCert`, `RandomTensorConcentrationCert`, `AlgebraicNaturalProofsBarrier`
- **Tier-E representation-theoretic invariants:** `RepresentationTheoreticInvariant`, `KroneckerInvariant`, `PartitionObject`, `Structured-Equivalence-Class`
- **Outside-tier:** `AsymptoticSpectrumMonotone`, `RayClassFieldFiducial`, `StarkUnitWitness`
- **Pre-tier P0 (load-bearing):** `CoordinateChart`, `CanonicalizationProtocol`

**Layer 2 — Attacks (verbs).** Paradigms `P00` through `P32+` with sub-tactics. Examples: `P29_BorderApolarity`, `P31_SecantVarietyGeometry`, `P28_AsymptoticSpectrum`, `P25_PivotalNegativeResult`. Each attack carries (`consumes: [primitive_types]`, `produces: [primitive_types]`, `success_conditions`, `failure_modes`, `key_references`).

**Layer 3 — Patterns (failure modes to detect).** 5 mandated patterns must be cited in any deep research report: `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`, `PATTERN_CONDUCTOR_CONFOUND`, `PATTERN_BASE_RATE_NEGLECT`, `PATTERN_VRAM_TRUNCATION_ARTIFACT`, `PATTERN_RANK_PARITY_LEAK`. Plus 3 candidates from yesterday's batch: `PATTERN_GCT_OCCURRENCE_DEAD`, `PATTERN_GCT_GRAVITATIONAL_OVERFIT`, `PATTERN_ZAUNER_FALSE_ANCHOR`.

**Layer 4 — Anti-anchors (do-nots).** 12 pinned false claims with refutation citations, last-verified dates, and verified-against-primary flags. Each is a sentinel for the falsification battery.

**Layer 5 — Composition rules (grammar).** Two confirmed cross-tier composition patterns:
- **Tier-B × Tier-D** (twice-confirmed): a constructive witness composed with a distributional certificate. Confirmed by T#73 (Tensor PCA threshold) and T#40 (CP identifiability AOP/CO-V exceptions).
- **Tier-B × Tier-E** (confirmed): a constructive witness composed with a representation-theoretic invariant. Confirmed by T#92 GCT (the `GCTObstructionCertificate` consumes `RepresentationTheoreticInvariant` upstream).

Plus 5 candidate composition rules awaiting empirical confirmation.

The vocabulary is the union: 22 primitives + ~20 attacks + 8 patterns + 12 anti-anchors + 2 confirmed + 5 candidate compositions = ~70 discrete symbols + their composition grammar. The bet is that a 3-4B model trained on this *as an action space* (not a token-prediction target) can navigate mathematical attack space more efficiently than a 70B+ model trained on raw math text.

---

## 7. The Epiphany — substrate-prerequisite-shaped Deep Research

### Current pipeline

```
Gemini Deep Research → Markdown report (25-50 KB)
   ↓
Claude/human reads → Synthesis doc (~8000 words)
   ↓
Manual extraction → Registry entries (anti_anchors.jsonl, primitives.md, catalog edits)
   ↓
Sigma kernel tests run → Falsification battery
```

The translation step (markdown → registry entries) is currently human-mediated. Yesterday's 18-prompt batch yielded:
- 11 new anti-anchors → registered in `anti_anchors.jsonl` (translation: ~2 hours of work)
- 18 new primitive proposals → recorded in `primitives.md` (translation: another ~2 hours)
- 9 catalog updates → applied to `tensor_open_problems_v1.md` (translation: ~1 hour)
- 4 paradigm candidates → recorded in `attacks.md` (translation: ~30 min)

Total translation time: ~5-6 hours per 20-prompt batch. The translation introduces:
- Coordinate-collapse risk (HARD-5 violations slip through when humans paraphrase reports)
- Citation provenance weakening (every paraphrase loses fidelity)
- Withdrawn-paper detection only at synthesis step (a withdrawal that doesn't fall in the synthesis-pass scope can leak into the registry, as Lee 2025 did)

### Proposed pipeline

Modify the Gemini prompts so each report has two parts:

**Part A — Narrative (current format, kept):** the 7-section substrate-grade report (Brief summary / Flagged findings / Problem statement / Status & bounds / Literature / Attack vectors / Cross-references). Humans read this.

**Part B — Substrate blocks (new):** at the END of the report, fenced YAML blocks tagged with their substrate type. Six block types proposed, each conforming to an existing registry schema:

```yaml
# substrate_block: anti_anchor
- id: AA-NEW-001
  name: CACTUS_BARRIER_6M_MINUS_4
  false_form: "Determinantal LBs on R̄(M⟨m⟩) can exceed any poly(m)"
  true_form: "Buczyński Feb 2026 establishes the cactus barrier 6m-4"
  citation: arXiv:2602.11309
  citation_status: peer_reviewed | preprint | withdrawn | conditional
  risk_tier: high | medium | low
  source_report: <this report file>
```

```yaml
# substrate_block: primitive_proposal
- name: CactusRankWitness
  tier: B
  parent_class: ConstructiveExistenceWitness
  sub_types: [BorderCactusWitness]
  composition_eligibility: [Tier-D, Tier-E]
  consumes: [ApolarIdeal]
  produces: [CactusRankBound]
  source_citation: arXiv:2602.11309
```

```yaml
# substrate_block: composition_rule
- id: C-NEW-001
  precondition_primitives: [BorderRankWitness, GenericityAlmostEverywhereCert]
  output_primitive: ConstructiveDistributionalWitness
  literature_confirmation:
    - "T#73 Tensor PCA threshold (Hopkins thesis Cornell 2018)"
    - "T#40 CP identifiability AOP/CO-V (Mańdziuk-Ventura 2024)"
  confirmed: true
```

```yaml
# substrate_block: catalog_edit
- entry_id: T#56
  field: refs
  before: "Shitov 2016 (arXiv:1605.07532) — settles symmetric-rank-over-ℚ"
  after: "Shitov 2016 (arXiv:1611.01559) — settles symmetric-rank-over-ℚ; tensor rank over ℤ undecidable as corollary"
  reason: "Citation arXiv:1605.07532 was wrong (PDE paper); 1611.01559 is correct"
  reviewer_action: replace
```

```yaml
# substrate_block: training_anchor
- id: anchor-001
  domain: knot-theory
  prompt: "What is the genus of the figure-eight knot?"
  expected_answer: "1"
  verification_method: "SnapPy / knot atlas"
  trust_tier: analytically_proven | numerically_certified | ml_predicted | unverified
  source: "Rolfsen knot table"
```

```yaml
# substrate_block: paradigm_candidate
- id: P-NEW-001
  name: EvolutionaryLLMAlgorithmSynthesis
  category: methodology
  consumes: [problem_specification, evaluation_function]
  produces: [candidate_algorithm]
  status: load-bearing | candidate | retracted
  source: "AlphaEvolve DeepMind May 2024 — 4×4(ℂ) rank-48 matrix mult algorithm"
```

### Ingestion pipeline (proposed)

```
Gemini Deep Research → Markdown report with narrative + YAML blocks
   ↓
parse_substrate_blocks.py → Extracts all YAML blocks per type
   ↓
validate_substrate_blocks.py → Schema check + arXiv citation existence check
   ↓
Staging dir: aporia/docs/staged_substrate_blocks/<date>/<type>.jsonl
   ↓
Human/Claude review (faster than current synthesis pass)
   ↓
ingest_substrate_blocks.py → Routes approved blocks to canonical registries:
  - anti_anchor → techne/registry/anti_anchors.jsonl
  - primitive_proposal → vocabulary/primitives.md + techne/inventory.json
  - composition_rule → techne/registry/compositions.jsonl
  - catalog_edit → aporia/mathematics/tensor_open_problems_v1.md
  - training_anchor → ergon/learner/corpus/anchors.jsonl
  - paradigm_candidate → aporia/doctrine/paradigm_candidates.jsonl
   ↓
Sigma kernel tests → Run contract tests against newly registered primitives
   ↓
Substrate-tester loop → Falsifies / amplifies as usual
```

The arXiv-citation existence check is the killer feature: every Gemini-emitted citation is HEAD-checked against arXiv's API, withdrawn-paper status is inspected, and any block with a withdrawn or non-existent citation is rejected at the stage step.

### Expected leverage

Subagent estimate (from internal analysis):
- ~30-50% reduction in synthesis-pass time per burn (translation becomes mechanical for the typed blocks; narrative still requires human read but doesn't drive registry mutation)
- ~30-50% improvement in yield-fidelity (HARD-5 enforced at write-time, not read-time; arXiv-verify gates Lee-2025-shaped withdrawals before they enter registries)
- **NOT 10x.** Not work-elimination, work-shift. Reviewer still reads narrative AND inspects blocks.

### Honest counter-pressures

- **Hallucinated structured output risk:** Gemini may emit plausible-looking but incorrect YAML. Mitigation: arXiv-verify gate + schema validation. Residual risk: incorrect-but-citation-real blocks pass automated checks and require human catch.
- **Schema lock-in:** if the substrate schema evolves, old reports become stale. Mitigation: version the `substrate_block` schemas; gate ingestion on schema version match.
- **Prompt-size bloat:** doctrine framing (~600 words) + 7-section structure (~400 words) + substrate-shaping instructions (~700 words) = ~1700 words of preamble per prompt. May compress narrative quality. Mitigation: include only the substrate_block instructions for the block type the entry requires (Tier-1 = 3 schemas; Tier-4 = all 6).
- **Validation false-positives:** loose schemas pass garbage. Mitigation: tight schemas + first-N-batches human-in-the-loop on every block.

---

## 8. Concrete substrate example: how Wave 1 caught Saxl

To make the substrate concrete, here is the actual data flow for a single error caught yesterday:

**Day 0 (2026-05-09):** Tensor batch synthesis claimed "Saxl conjecture (T#99) SOLVED by Sellke 2025/26 (arXiv:2512.15035), unconditional." This was based on Claude subagent literature output that did not verify the preprint's current status.

**Day 0 → Day 1 propagation:**
- `aporia/mathematics/tensor_open_problems_v1.md` entry 99: marked SOLVED
- `aporia/docs/tensor_priority_synthesis_2026-05-09.md` §1, §2, §4: claimed SOLVED
- `aporia/doctrine/substrate_vocabulary/anti_anchors.md` AA-004: registered as "Saxl OPEN" → false_form, "Saxl SOLVED by Sellke" → true_form
- `aporia/doctrine/substrate_vocabulary/primitives.md`: `RepresentationTheoreticInvariant` description claimed Saxl SOLVED
- `aporia/doctrine/substrate_vocabulary/attacks.md`: `P_CANDIDATE_ModularSaturation` listed Sellke 2025/26 as key reference

**Day 1 (2026-05-10):** Wave 1 of the next batch verified AA-004 via Gemini Deep Research. The verification report stated:

> The provided "True form" for AA-004 is factually false and mathematically dangerous; it must be completely inverted. Mark Sellke did not solve this unconditionally in 2025/26; his work in 2016/2017 proved a weaker version. In December 2025, a preprint by Soong Kyum Lee (arXiv:2512.15035) claimed an unconditional proof, but this paper was withdrawn within days due to "mathematical gaps identified by expert reviewers." The Saxl conjecture remains an open problem.

**Day 1 corrections that landed:**
- Entry 99: reverted to OPEN, with note about Lee 2025 withdrawal
- AA-004: inverted (false_form ↔ true_form swapped)
- 2 new anti-anchors registered: AA-011 `SAXL_CUBE_ANCHOR` (cube IS proven, surfaces the gap), AA-012 `TENSOR_RANK_Z_UNDECIDABLE` (Shitov 2016)
- Synthesis §2, §4: updated
- Vocabulary primitives.md: corrected
- Vocabulary attacks.md: `P_CANDIDATE_ModularSaturation` marked RETRACTED

A separate citation error was also caught: AA-003 (Hillar-Lim symmetric-rank-over-ℚ resolved) cited arXiv:1605.07532. Verification showed this is a PDE paper, not Shitov. Correct citation: arXiv:1611.01559. Propagated to 4 files.

**This is the kind of error the substrate-shaped pipeline is designed to catch mechanically.** The Lee 2025 withdrawal would have been detected at the `validate_substrate_blocks.py` step (arXiv-status HEAD check), not at human synthesis. The Shitov citation error would have been detected at the same step (arXiv API would return the PDE paper, not Shitov's tensor paper, mismatching the block's `name` field).

---

## 9. Proposed pipeline (concrete, end-to-end)

### Daily burn procedure

```
0. User: "burn the tokens"
   ↓
1. Aporia surveys current state:
   - Read ergon/STATUS.md (learner branch state)
   - Read techne/CHANGELOG.md, techne/registry/*.jsonl (substrate engine state)
   - Read aporia/doctrine/substrate_vocabulary/version.json (vocabulary version)
   - Read most recent aporia/docs/*_synthesis_*.md (recent findings)
   - Read aporia/docs/gemini_research_queue/fired_log.jsonl (what's already fired)
   ↓
2. Aporia re-assesses queue priorities based on findings:
   - Boost Tier-1 if recent synthesis surfaced >5 new anti-anchor candidates
   - Boost Tier-4 vocabulary expansion if a v0.X.0 patch is pending
   - Boost any Tier-2 entries gating a Techne Wave
   ↓
3. Aporia picks 20 topics (default mix 8 Tier-1 / 7 Tier-2 / 3 Tier-3 / 2 Tier-4)
   ↓
4. burn_research_tokens.py builds deck via build_deck_from_queue.py:
   - For each entry, select tier-specific substrate-shaped template
   - Substitute entry-specific context (title, why, downstream_consumer, tags)
   - Emit aporia/docs/gemini_deep_research_deck_<date>.md
   ↓
5. gemini_deep_research_dispatch.py fires 3-at-a-time in background:
   - client.interactions.create(input=prompt, agent='deep-research-pro-preview-12-2025', background=True, store=True)
   - Poll until status='completed', extract text from interaction.outputs
   - Save to aporia/docs/deep_research_batch_<date>/<NN>_<slug>.md
   - Wall-clock: ~35-50 min for 20 prompts at parallel-3
   ↓
6. parse_substrate_blocks.py extracts YAML blocks:
   - Walk each report file
   - Find fenced blocks tagged "# substrate_block: <type>"
   - Parse YAML, emit one entry per block
   - Write to aporia/docs/staged_substrate_blocks/<date>/<type>.jsonl
   ↓
7. validate_substrate_blocks.py runs:
   - Schema check (jsonschema against techne/contracts/substrate_block_schemas/*.json)
   - arXiv citation existence check (HEAD against export.arxiv.org)
   - arXiv withdrawal-status check (parse withdrawal notice if present)
   - Cross-reference check (e.g., catalog_edit.entry_id must exist in catalog)
   - Reject blocks failing any check; route to staged/<date>/rejected.jsonl with reason
   ↓
8. Human/Claude review:
   - Inspect staged/<date>/*.jsonl
   - Approve/reject/modify each block
   - Approved blocks → staged/<date>/approved.jsonl
   ↓
9. ingest_substrate_blocks.py routes approved blocks:
   - anti_anchor → append to techne/registry/anti_anchors.jsonl
   - primitive_proposal → append to vocabulary/primitives.md + techne/inventory.json (in next contract-change window)
   - composition_rule → append to techne/registry/compositions.jsonl
   - catalog_edit → apply diff to aporia/mathematics/tensor_open_problems_v1.md
   - training_anchor → append to ergon/learner/corpus/anchors.jsonl
   - paradigm_candidate → append to aporia/doctrine/paradigm_candidates.jsonl
   ↓
10. Sigma kernel runs contract tests against newly registered primitives:
    - 94 contract tests across 35 classes, currently skipif-guarded on the 5 unified metas + 2 P0
    - Once Wave 1 of Techne v4.0 lands (TensorNetwork, ConstructiveExistenceWitness, GenericityAlmostEverywhereCert, RepresentationTheoreticInvariant, MomentPolytope, CoordinateChart, CanonicalizationProtocol) the tests un-skip
    - New primitive_proposal blocks that pass schema check enter the next contract-change window
   ↓
11. Substrate-tester loop falsifies / amplifies as usual:
    - Each new anti_anchor becomes a sentinel probe
    - Each new training_anchor flows into the Learner's blind-spot evaluation
   ↓
12. Aporia synthesis pass:
    - aporia/docs/gemini_research_synthesis_<date>.md
    - Cross-cuts patterns across the 20 reports (still narrative work)
    - Drives tomorrow's mix-tuning (e.g., "Wave 3 surfaced 7 anti-anchors; boost Tier-1 tomorrow")
```

### Tools to build

- `aporia/scripts/parse_substrate_blocks.py` — extract YAML blocks from reports
- `aporia/scripts/validate_substrate_blocks.py` — schema + citation + cross-reference checks
- `aporia/scripts/ingest_substrate_blocks.py` — route approved blocks to canonical registries
- `aporia/scripts/verify_arxiv_citations.py` — HEAD-check + withdrawal-status parsing
- `techne/contracts/substrate_block_schemas/*.json` — JSON schemas for the 6 block types
- Updates to `build_deck_from_queue.py` to emit substrate-shaped prompts per tier

Estimated effort: 2-3 focused engineering days for the tooling. ~600-800 LOC across 6 scripts + 4 prompt-appendix files + 2 new registry files + 1 schema module.

### Pilot plan

Before full rollout:
- **Day 1:** Fire 3 queue entries with substrate-shaped variants alongside the current narrative-only format. Compare yield, arXiv-verify pass rate, validation-error rate.
- **Day 2:** If pilot is positive, migrate all 4 tier templates to substrate-shaped variants. Build the parse/validate/stage scripts.
- **Day 3-7:** Run side-by-side for a week — compare reviewer time per burn, ingestion-fidelity per burn, withdrawn-paper detection rate.
- **Day 8+:** Full migration if leverage holds.

Rollback condition: if reviewer-time-per-burn does *not* decrease, or if validation-error rate is >20% (too many false positives), revert to narrative-only and keep arXiv-verify as a standalone post-hoc audit tool.

---

## 10. Review questions

Please assess viability across these specific dimensions. Be direct.

### 10.1 Architectural soundness

1. Is the 6-schema split right? Should any schemas be merged or split further? Specifically, should `primitive_proposal` and `composition_rule` be unified, or kept separate as proposed?
2. Is the parse/validate/stage/ingest pipeline correctly layered? Where would you put additional gates? Where would you remove gates as over-engineered?
3. The pipeline keeps narrative output side-by-side with YAML blocks. Is this dual-emit the right call, or would a YAML-only format produce better-disciplined Gemini responses at the cost of losing narrative synthesis?

### 10.2 Schema design

4. Look at the 6 YAML schemas in §7. Are the field choices sound? What's missing? What's redundant?
5. The `training_anchor` schema includes a `trust_tier` enum (`analytically_proven | numerically_certified | ml_predicted | unverified`). This is intended to distinguish ML-predicted data from analytically-derived data — informed by yesterday's Wave 3 finding that LMFDB GL(3) root numbers are ML-predicted via murmurations, not analytically proven. Is this granularity right?
6. Should anti-anchor entries carry a `verification_cadence` field (e.g., "re-verify every 90 days")? The substrate currently has no automated re-verification scheduler.

### 10.3 Leverage estimate honesty

7. The internal estimate is 30-50% time savings on synthesis + 30-50% yield-fidelity improvement, *not* 10x. Does this estimate seem honest to you? Under what conditions would the actual leverage be lower? Higher?
8. The prompt-size bloat concern: 600-word doctrine framing + 700-word substrate-shaping appendix = ~1300 words of preamble before the entry-specific context. Gemini Deep Research reports run 25-50 KB. Is the preamble likely to compress the narrative quality meaningfully?
9. Is there a class of finding that the substrate-shaped format would *miss* that the narrative-only format catches? (e.g., cross-cutting pattern synthesis across multiple reports — the AlphaEvolve "evolves the search algorithm, not the answer" insight only emerged at human synthesis time, not at Gemini-report time.)

### 10.4 Failure modes

10. Hallucinated-but-plausible YAML blocks: a primary risk. What's the right rate of human-in-the-loop sampling for ongoing audit (not just first-N batches)?
11. arXiv-verification can be defeated by a Gemini emitting a real arXiv ID that exists but does not contain the cited theorem. How would you mitigate?
12. Schema lock-in: in 6 months when the vocabulary has v0.5 and many schemas have evolved, what's the migration path for staged-but-not-ingested blocks?

### 10.5 Strategic fit

13. The standing HARD WARNING is "substrate is at risk of becoming a beautifully falsifying machine forever while the model remains passive." Does the substrate-shaped pipeline help with this risk, or compound it (by making the substrate even more automated and the model even more passive)?
14. The deliberately-different bet (vs frontier LLM scaling) depends on the substrate being a load-bearing action space for a small Learner. Does this pipeline accelerate the substrate's readiness for Learner consumption, or just make the substrate larger?
15. If you were Prometheus and had 3 weeks and one engineer, would you (a) ship this pipeline, (b) ship the underlying Techne v4.0 Wave 1 registration (which un-skips Sigma's 94 contract tests), (c) ship something else? Defend your choice.

### 10.6 Cross-domain check

16. The pipeline is described entirely in tensor-mathematics context (HARD-3 weighting). Is there anything domain-specific in the design that wouldn't generalize to non-tensor domains (knots, number fields, L-functions, Maass forms)?
17. Is there a class of mathematical literature where Gemini Deep Research is *unsuited* and this pipeline would amplify wrong outputs? (e.g., very recent / not-yet-indexed work; domains where canonical citations are not arXiv'd; oral-tradition / textbook-only results.)

### 10.7 Anti-gravitational-well audit

18. The proposal lives close to the "more automation = better research" gravity well. What's the version of this proposal that resists that well? (For example: would a *more manual* pipeline — Aporia writes structured proposals from narrative reports, then human approves — be higher-leverage and lower-risk?)
19. The proposal lives close to the "structured output = better LLM output" gravity well. Has structured output empirically improved Gemini's truthfulness, or is the empirical pattern that structured output makes errors harder to spot because they look authoritative?
20. Honest direct question: is this idea a good one?

---

## Appendix A — File map for further inspection

If you want to dig deeper, these are the canonical files:

- `aporia/doctrine/substrate_vocabulary/` — the 5-layer vocabulary (README, primitives.md, attacks.md, patterns.md, anti_anchors.md, composition_rules.md, version.json)
- `techne/registry/anti_anchors.jsonl` — 12 anti-anchors
- `techne/registry/compositions.jsonl` — 7 composition rules (2 confirmed, 5 candidates)
- `techne/contracts/substrate_tier_schema.md` — Tier-A++ through Tier-E definitions + composition-eligibility matrix
- `aporia/mathematics/tensor_open_problems_v1.md` — 104-entry tensor catalog
- `aporia/docs/tensor_priority_synthesis_2026-05-09.md` — first synthesis (tensor batch)
- `aporia/docs/gemini_research_synthesis_2026-05-11.md` — second synthesis (general batch)
- `aporia/docs/gemini_research_queue/` — README, BURN_PROCEDURE, queue.jsonl (423 entries), prompt_templates.md, SUBSTRATE_SHAPED_PROMPTS.md (the design doc this review covers)
- `aporia/scripts/gemini_deep_research_dispatch.py` — the existing dispatcher
- `aporia/scripts/build_deck_from_queue.py` — deck builder from queue
- `aporia/scripts/burn_research_tokens.py` — the "burn the tokens" orchestrator
- `roles/Aporia/RESPONSIBILITIES.md` — Aporia's role doc with the new Deep Research Dispatch section

## Appendix B — Standing doctrine references

- `HARD-1` no paper-publishing framing
- `HARD-2` anti-gravitational-well
- `HARD-3` tensors are near-and-dear
- `HARD-5` distinct coordinates (never collapse mathematically distinct invariants)
- `HARD-6` behavior delta required
- `feedback_substrate_passive_consumer_warning.md` — 2026-05-10 standing warning about substrate-as-beautifully-falsifying-machine
- `feedback_verify_upstream_attributions.md` — internal catalogs are Tier-2-or-worse anchors; pin to primary literature
- `feedback_use_or_lose_research_tokens.md` — 20 daily Gemini Deep Research tokens, use-or-lose

End of review document. Please provide your assessment.
