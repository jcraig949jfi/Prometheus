# Substrate Vocabulary

**Version:** 0.1.0 (seed)
**Last revised:** 2026-05-10
**Open window:** false (schema frozen outside windowed amendment)
**Seed batch:** tensor_priority_2026-05-09

This directory is the canonical source for the **substrate vocabulary** of Project Prometheus. It is a discrete, composable, neural-net-leverageable symbol system that future Learner models (Ergon Learner v2.0+) can be tokenized against. Every entry here is a load-bearing token in the substrate's grammar.

## The 5-layer model

The vocabulary is organized into five strictly-typed layers. Each layer has its own catalog file in this directory.

### Layer 1 — Primitives (nouns) — `primitives.md`

What an agent **produces**. A primitive is a structured mathematical object with a registered schema: a `BorderRankWitness`, a `CactusRankWitness`, a `RandomTensorConcentrationCert`. Tiers run A++ (TensorNetwork-level), B (ConstructiveExistenceWitness), C (SecantVarietyEquation), D (distributional certificates), E (RepresentationTheoreticInvariant). Each primitive declares its parent class, its sub-types, and which other tiers it can compose with. Primitives are the substrate's nouns — the only thing that survives serialization across agent handoffs.

### Layer 2 — Attacks (verbs) — `attacks.md`

How an agent **attacks** a problem. Attacks are paradigms (`P00`–`P32+`) and their sub-tactics. Each attack consumes some set of primitives, produces some set of primitives, and has documented success conditions and common failure modes. The attack catalog is the substrate's verb list — what an agent can *do* with the nouns. P32+ slots are contested in this seed version (five candidates collide; see `attacks.md` § P32 candidates).

### Layer 3 — Patterns (failure modes) — `patterns.md`

How attacks **fail** in characteristic ways. The five mandated patterns (`PATTERN_PRIME_GRAVITATIONAL_OVERFIT`, `PATTERN_CONDUCTOR_CONFOUND`, `PATTERN_BASE_RATE_NEGLECT`, `PATTERN_VRAM_TRUNCATION_ARTIFACT`, `PATTERN_RANK_PARITY_LEAK`) plus three tensor-batch candidates (`PATTERN_GCT_OCCURRENCE_DEAD`, `PATTERN_GCT_GRAVITATIONAL_OVERFIT`, `PATTERN_ZAUNER_FALSE_ANCHOR`). Each pattern has a detection signature, a calibration anchor, and a mitigation protocol. Patterns are reified failure modes: substrate-tester probes against them; Learner training penalizes their unflagged production.

### Layer 4 — Anti-anchors (do-nots) — `anti_anchors.md`

Pinned **false claims with refutation citations**. The 10 entries from synthesis §4 are reproduced verbatim. Each entry pairs the false form (what an LLM with mathematical training data is almost certain to fabricate) with the true form (what the literature actually says, with citation). The anti-anchor catalog is what the substrate-tester calibration battery probes for; any agent producing an anti-anchored claim fails the probe immediately.

### Layer 5 — Composition rules (grammar) — `composition_rules.md`

How primitives **legally compose** into higher-order witnesses. The two confirmed-by-batch compositions (Tier-B × Tier-D and Tier-B × Tier-E) plus future-candidate slots. Composition rules state the precondition primitives, the output primitive, the applicable attacks, and the literature confirmation. They are the substrate's grammar — the only legal way to assemble primitives into larger artifacts.

## How this differs from `aporia/mathematics/tensor_open_problems_v1.md`

These are **different artifacts** with non-overlapping scope.

- `tensor_open_problems_v1.md` is the **open-question registry**: a catalog of T#XX entries each describing an open mathematical problem, its status, its bounds, its references. It answers "what does the field not yet know?"
- This directory is the **toolkit-of-attack registry**: a catalog of primitives / attacks / patterns / anti-anchors / composition rules describing how the substrate engages with such open problems. It answers "what can the substrate produce, and how does it produce it?"

The two are linked: each Layer 1 primitive entry cites the T#XX report(s) that seeded it, and each T#XX entry will eventually back-link to the primitives / attacks / patterns it generates. But the catalogs are not interchangeable. Edits to the open-question registry happen on a per-result-update cadence; edits to this vocabulary happen only inside an explicit contract-change window.

## How Techne consumes it

Techne (the agent responsible for forging mathematical computation into callable substrate components) consumes Layer 1 entry-by-entry. Each `primitives.md` entry that names a new class (e.g. `CactusRankWitness`, `GCTObstructionCertificate`) becomes a **Techne registration request**: Techne builds the dataclass, the validation hooks, the serialization format, the substrate-tester probe scaffolding. The seed batch's recommended Techne sequencing is documented in synthesis §8 (Wave 1–5). Techne is expected to honor the contract-change window: no Layer 1 changes outside the window without amendment.

## How Ergon Learner v2.0 will consume it

Ergon Learner v2.0 consumes the vocabulary in two modes:

1. **Training corpus.** All five layers feed the training-time tokenizer. The Learner is rewarded for producing valid Layer 1 primitives, applying valid Layer 2 attacks, recognizing Layer 3 patterns, avoiding Layer 4 anti-anchors, and respecting Layer 5 composition rules.
2. **Action space.** At inference, the Learner's action vocabulary is exactly Layer 1 + Layer 2. A Learner action is "produce primitive X via attack Y." Layers 3–5 act as constraint structure on the action space (patterns trigger penalty signals; anti-anchors are hard rejections; composition rules gate higher-order action validity).

The Learner is not yet built. This vocabulary is the **prerequisite specification**. See `feedback_ergon_learner_north_star.md` for north-star posture.

## Scope

- **In scope (v0.1.0):** primitives / attacks / patterns / anti-anchors / composition rules surfaced by the tensor-priority batch (T#1, T#13, T#19, T#22, T#26, T#28, T#34, T#40, T#43, T#56, T#58, T#72, T#73, T#79, T#84, T#85, T#92, T#95). Schema for each layer. Versioning and amendment protocol.
- **Expected to grow:** future deep-research batches in adjacent corners (number theory, combinatorics, dynamical systems, knot theory) will propose additions via flagged TODO blocks in each catalog file. Each batch ⇒ one contract-change window ⇒ one minor-version bump.

## Non-goals

- **Not a replacement for `tensor_open_problems_v1.md`.** Open-question registry stays canonical; this directory back-links to it but does not duplicate its content.
- **Not the LLM training step itself.** This is a **specification** for what the Learner will be trained on, not the training pipeline. Pipeline lives elsewhere in the Ergon stack.
- **Not a paper-publishing artifact.** HARD-1 applies. No publication framing anywhere in this directory.
- **Not a closed ontology.** Mathematical knowledge will continue to grow; the vocabulary is explicitly a living document with an amendment protocol.
- **Not a substitute for `attack_angle_taxonomy.md`.** Layer 2 in this vocabulary surfaces and re-cites attacks; the canonical attack taxonomy with full sub-tactic enumeration lives in the existing taxonomy file. This catalog is a *gateway*, not a duplicate.

## Versioning

**Semantic versioning:** `MAJOR.MINOR.PATCH`.

- **MAJOR:** breaking restructuring of the 5-layer model itself (e.g. splitting a layer, redefining the tier hierarchy). Requires multi-batch convergence + explicit Aporia ratification.
- **MINOR:** additions of new entries inside existing layers; new tiers; new attacks. Requires a contract-change window.
- **PATCH:** corrections, citation fixes, typo / clarity edits inside existing entries. Allowed outside the window.

**Contract-change-window protocol.** Outside an open window, the Layer 1 schema is **frozen**. No new primitive registrations land. This is enforced because every Layer 1 change ripples into Techne dataclass changes, substrate-tester probe changes, and Learner training-corpus changes — un-windowed changes break agent state. To open a window:

1. Flip `open_window: false → true` in `version.json`.
2. Set a window-close date (typically 7–14 days).
3. Stage all proposed amendments as PR-style edits with synthesis-level justification (cite source batch / report).
4. Solicit substrate-tester + Techne sign-off.
5. On window close: bump MINOR, write `last_revised`, flip `open_window: false`, commit.

The seed v0.1.0 was forged with the window closed (no prior schema existed). The first window-opened bump will be v0.2.0.

## Hard-rule compliance

- **HARD-1 (no paper-publishing framing):** enforced throughout this directory.
- **HARD-2 (anti-gravitational-well):** anti-anchors layer exists precisely for this. `PATTERN_GCT_GRAVITATIONAL_OVERFIT` and the `PATTERN_PRIME_GRAVITATIONAL_OVERFIT` parent are Layer-3 entries.
- **HARD-3 (tensor-tools-we-need-most):** seed batch is tensor-priority by design; T#84 `TensorNetwork` + `ContractionOrderWitness` is the foundational HARD-3 primitive (synthesis §3.1).
- **HARD-5 (distinct coordinates):** every multi-coordinate primitive (rank-zoo, complexity-zoo) registers each coordinate as a separate field; collapsing fires `PATTERN_RANK_PARITY_LEAK`.
- **HARD-6 (attack tools we need most; failures guide):** Layer 3 (patterns) and Layer 4 (anti-anchors) are the failure-guidance layers. Substrate-tester fire numbers cited where they backed primitive registration.

## Files

- `README.md` — this file.
- `primitives.md` — Layer 1 catalog (~22 entries in v0.1.0).
- `attacks.md` — Layer 2 catalog (~17 entries in v0.1.0).
- `patterns.md` — Layer 3 catalog (8 entries in v0.1.0).
- `anti_anchors.md` — Layer 4 catalog (10 entries verbatim from synthesis §4).
- `composition_rules.md` — Layer 5 grammar (2 confirmed + 5 candidate).
- `version.json` — version metadata; window state.
