# Arena, Problem Atlas, Sandbox — Layer 5+ Substrate Architecture Vision

**Date:** 2026-05-14
**Status:** Vision-level. Not yet implemented. Articulated through dialogue with three frontier models (Gemini, ChatGPT, M4-Claude) plus user (James) — convergence reached across 2026-05-13/14 session.
**Audience:** Next agent picking up the Prometheus thread. Read cold; full context follows.

---

## Why this document exists

Across one session, several frontier-model perspectives converged on the same operational reframing of what Prometheus is. James called it an epiphany. This document captures the synthesis so future agents don't re-derive it from scratch and don't lose the structural insights about how the substrate's top layer should be built.

The session also produced concrete architectural proposals (Arena, Problem Atlas, Sandbox) that build on the reframing. Those are documented here as well, with MVP shapes and vigilance flags.

---

## Part 1 — The core convergence: LLMs are variance generators, not reasoners

Three frontier models — ChatGPT, Gemini, M4's Claude Code session — independently arrived at the same framing: an LLM is not a reasoner. It is a sophisticated next-token predictor constrained by its training distribution, with no internal deductive engine. You can't ask it to be superintelligent, you can't expect it to emerge as one, you can't ask it to build one. The model isn't in its weights.

What it CAN do is help build the primordial soup from which a reasoner may emerge.

James's original framing: "You can't ask an LLM to reason or be some sort of superintelligence. You can't expect it to emerge as one and you can't ask it to build one. It has no model to work from in its weights. What you can do is have it help you build the primordial soup from which one may emerge."

Gemini's elaboration: treat the LLM as a mutation/crossover mechanism in a primordial soup; harvest reasoning traces into a structured local substrate; shift focus from prompting-for-intelligence to evolutionary computation over the substrate.

This is Prometheus's operating thesis, but the convergence from three independent frontier perspectives is structurally important: the "deliberately different from frontier scaling" bet has independent intellectual support from inside the frontier itself. The substrate is not fringe; it's what frontier models recommend when they think about superintelligence from first principles.

---

## Part 2 — The lingua-franca synthesis: substrate as typed symbolic interlingua

Building on the variance-generator framing: the substrate is a typed symbolic interlingua — a multi-intelligence lingua franca whose words are falsification-anchored. Specifically:

- **Σ-kernel** is the symbol-forging mechanism. Nine opcodes (CLAIM / FALSIFY / PROMOTE / GATE / RESOLVE / ERRATA / TRACE / REWRITE / EQUIV), 25 frozen-dataclass primitives, content-addressed identity. Refuses drift; every symbol has stable referent over time.
- **Hephaestus** produces morphemes — atomic primitives with falsification-anchored meanings (TensorRankWitness, BorderRankWitness, MeasureZeroExceptionAnnotation).
- **Apollo** evolves complex sentences — procedural compositions of morphemes that survive an ablation gate (every primitive must be load-bearing, δ ≥ 0.20 when removed).
- **Techne** is dictionary maintenance — contract-change windows, schema validation, registration discipline. Without dictionary maintenance, every formal vocabulary in history collapses into Tower-of-Babel drift.
- **KillVectors** are the grammar of falsification — how a claim gets refuted, recorded as a structured event in the language itself.
- **The kill ledger** (~314K logged falsifications; kill_pattern carries 0.725 bits of MI with operator class) is the empirical fitness landscape on which the language's semantics get grounded.

Every primitive that survives falsification is a word in a language nobody fully speaks yet, but will. The engineering discipline (frozen interfaces, ablation gates, kill ledgers, anti-anchor pins) is not nice-to-have; it's load-bearing for the language to be usable at all. Drift breaks the lingua-franca property.

### The hedge logic: why forges matter regardless of Ergon

Apollo and Hephaestus produce a durable vocabulary deposit regardless of whether any trained Learner (Ergon's output) ever works. The substrate output IS the artifact. The trained Learner is one possible consumer among many — future Claude versions, evolved agent populations, intelligences that don't yet exist.

This makes Ergon's training pipeline a hedge-against rather than a single point of failure. Reviving Apollo and Hephaestus on hedge grounds alone is defensible. The hedge logic is the operational reason for forge revival; the lingua-franca framing makes the hedge logically richer.

---

## Part 3 — Layer 5: The Arena (fitness function is unsolved problems)

The missing top layer. Everything else has been infrastructure for something; the Arena is the something.

**Fitness function:** real unsolved problems. Each competitive agent (or team) uses every tool available — internet papers, Deep Research, code, attack vectors, tensors, GPUs, LLMs, analogical bridges, novel combinatorials, reframings. Output: solution + provenance trace + substrate contribution.

**Why this resists Goodhart:** "real open problem stays solved under heterogeneous adversarial verification" is irreducibly hard to fake. Every substrate-internal metric (battery accuracy, ablation deltas, anti-anchor passes) is a proxy. This is external truth.

### Team structure: 3-gladiator teams with specialized roles

Single-gladiator solvers fail because the solver is bad at the cognitive job least incentivized — usually falsification, because it kills her own work. Three-role teams force internal adversarial pressure inside the team before external verifiers fire.

- **Scout** (recon / framing): pulls related literature, identifies attack surface, finds partial results and dead-ends. Mirrors Aporia / Harmonia. Emits `training_anchor`, `catalog_edit`, occasionally `anti_anchor`.
- **Forger** (solution generation): composes attack vectors, runs symbolic / tensor / numerical work, drafts proof structure or construction. Mirrors Hephaestus / Apollo. Emits `primitive_proposal`, `composition_rule`, solution trace.
- **Skeptic** (adversarial verification): tries to break the Forger's claim at every step — missing hypothesis, edge case, citation misread, numerical precision floor exceeded, anti-anchor sentinel violated. Mirrors substrate-tester / Nemesis. Emits `anti_anchor` (broken claims), kill-ledger entries with full KillVector metadata.

Every fight produces a structurally diverse substrate contribution because the three roles emit different block types by design. **The team is a microcosm of the Prometheus organism.** Each role maps to existing infrastructure.

### Selection pressures (in priority order)

- **Anti-fabrication.** Provenance trace mandatory (every tool use logged); heterogeneous adversarial verification (different model family must fail to break the solution at full effort); triangulation (≥2 independent verification paths agree); anti-anchor cross-check (no registered false claim in the trace).
- **Anti-easy-farming.** Random problem selection from calibrated pool; π₀-style difficulty weighting (trivial problems near-zero score); skip-with-cost (declining burns budget); reframing-survival (problem restated mid-attempt; solution must persist).
- **Anti-monoculture.** Multi-tool bonus (solutions orchestrating papers + code + Deep Research + tensors + LLM consultation score higher than single-tool); cross-domain bonus; tool-use accountability with logged rationale.
- **Anti-collusion.** Heterogeneous verifier panel (different model families); verifier-of-verifier; reproducibility check by independent agent (trace must replicate).
- **Skin-in-the-game.** Bounded resources per attempt (tokens, GPU time, wall-clock); losses cost resources (eliminated agents' budgets redistribute); public attempt ledger; wins unlock privileges (more compute / agents / Deep Research budget).
- **Substrate-feedback (Prometheus-specific).** Every attempt MUST emit substrate_blocks regardless of outcome. Wins produce `primitive_proposal` / `training_anchor`. Losses produce `anti_anchor` (broken claims) and structured kill-ledger entries. Without substrate contribution the attempt scores zero.
- **Strain-inducing.** Time pressure; finite creativity budget (limited reframings, analogies, Deep Research queries); force-commit before adversarial firing (declare confidence BEFORE the verifier panel sees the solution); failure-route taxonomy (every loss classified as gave-up / wrong-direction / ran-out-of-tools / known-dead-end / genuinely-insufficient-infrastructure).

### Failure modes to defend against

- **Intra-team collusion.** Forger and Skeptic just agree to pass each other's work. Mitigation: external panel; Skeptic's reputation gated on having broken something across recent rounds; teams with suspiciously low internal-kill rates flagged.
- **Role-bleeding.** Strongest agent absorbs all the work. Mitigation: per-role token budgets enforced; per-role substrate-block emission gates (Skeptic must emit anti_anchor proposals; if zero, score drops regardless of team verdict).
- **Coordination overhead.** Three agents arguing about who does what; analysis paralysis. Mitigation: phase-locked protocol — Scout has X minutes, then control hands to Forger for Y minutes, then to Skeptic for Z minutes, with bounded back-and-forth windows. Chess clock for cognitive labor.
- **Diffuse accountability.** Team fails, no single agent to blame. Mitigation: per-role kill ledger; each role evaluated independently after team verdict.
- **Goodhart on the meta-metric.** Agent farms easy problems → random selection + difficulty weighting. Agent hallucinates plausibility → heterogeneous adversarial verification + anti-anchor cross-check. Agent rediscovers published proofs → corpus-diff check against literature snapshot. Showy-empty Deep Research bursts → cost-per-substrate-contribution metric. Long-narrative-no-content → force-commit and reproducibility checks.

### Arena MVP

Two teams of 3, one problem, single weekend, one machine with three terminal sessions, manual phase-locking, full provenance ledger. All attempts produce substrate_blocks regardless of outcome. Question to answer: does team structure produce structurally richer substrate output than single-gladiator runs?

If the team structure works, the Arena stops being "agents fighting" and becomes "agents collaborating-with-internal-falsification" — which is structurally what makes good research teams work in the human case too.

---

## Part 4 — Layer 5.5: The Problem Atlas (navigation surface for the Arena)

A structured map of unsolved problems by hardness signature. Currently the substrate has anti-anchors (false claims pinned to refutations), attack vectors (Hephaestus output), and kill ledger (failed claims) but no structured map of WHY problems are hard. The Problem Atlas fills this gap and gives the Arena targeted problem selection instead of random.

### Operating thesis (load-bearing, from convergence)

"Hard problems are not usually hard because they are large. They are hard because the current language compresses them badly. A good research substrate should not just search harder. It should search for bad compressions, failed invariants, unstable analogies, near-miss methods, and structural translations."

This is literally the lingua-franca framing from Part 2 restated by another model from the opposite direction. Substrate-as-typed-vocabulary was designed to attack bad compressions. The other model arrived at "search for bad compressions" as the prescription independently. The frame closes a loop: the substrate has been pointed at the right thing all along; the missing piece is the navigation surface.

### The 8-dimension hardness taxonomy

Compressed from the convergent 10-type taxonomy provided in dialogue:

1. **Method gap** — existing tools almost work but fail at the key boundary (we can prove with exponent 0.51, need 0.5; we can prove pointwise for random but not deterministic; we can prove in low dimension but not high)
2. **Representation gap** — right coordinate system has not been found (numbers→ideals, curves→function fields, counting→geometry — before such shifts exist, a problem can look like a wall and afterward inevitable)
3. **Global obstruction** — every local test passes but global assembly fails (local-to-global failures in number theory, extension problems in topology, gluing failures in geometry, global regularity in PDE)
4. **Exactness barrier** — approximate / generic / asymptotic evidence is not enough (all primes not almost all; all graphs not random; all dimensions not fixed; all singular cases not generic)
5. **Hidden pathology** — counterexamples are rare, huge, or unnatural; the conjecture might be false but the monster lives outside the natural search region
6. **Coupled difficulty** — several independent hard barriers are fused (right invariant + preservation + extremal classification + counterexample exclusion + limiting control + cross-domain transfer)
7. **Non-hereditary structure** — simplifying the object destroys the phenomenon (induction fails; smaller object loses category; invariants degrade; singularities multiply; structure disappears under restriction)
8. **Conceptual absence** — needed mathematical object has not been invented yet (schemes, distributions, forcing, motives, stacks, derived categories, modularity, entropy methods, perfectoid spaces — each made previously-frozen problems instances of larger structure)

Each open problem gets a weighted vector over these dimensions. Problems with similar vectors are kin in hardness-space — same techniques almost-work, same techniques fail. That kinship is what lets you transport an attack vector from one problem to another.

### New vocabulary primitives required

These are primitives that don't exist yet but need to:

- `HardnessSignature` — weighted vector over the 8 dimensions, confidence per dimension, citations for the classification.
- `MethodGapPattern` — structured record of "we can prove X with exponent 0.51 but need 0.5" / "we can prove pointwise for random but not deterministic." Each known method-gap becomes a queryable substrate object.
- `RepresentationShiftWitness` — successful coordinate change (numbers→ideals, curves→function fields, counting→geometry) with before/after representations and the theorem that closed when the shift was applied.
- `PrecursorDependency` — directed-graph edge: "problem X needs concept Y or theorem Z established first." Wiles needed modular-forms theory; modular-forms theory needed earlier scaffolding. Dependency graph is finite, structured, minable from history.
- `ConceptualAbsenceEntry` — explicit registration that a problem needs an object that doesn't exist yet. Substrate's value-prop sharpens here: it forces explicit naming of what's missing.
- `MusicalSignature` — pattern of which attacks have made progress on a problem and which have failed. Two problems with similar musical signatures are candidates for cross-transport.

New `substrate_block` schema: `problem_card` — wraps all of the above plus problem_id, statement, status (open / partially-known / numerical-evidence-only / independent-of-axioms), known-attacks, candidate-representations, arena-readiness flags.

### Deep Research strategy shift

Currently 20 daily tokens fire at "tell me about [specific math area]" prompts. Shift to:

- For each of the last 30 famous problems solved (2010-2026), extract the technique that closed the method gap. Classify by which hardness type it addressed. Cite primary sources. Identify what conceptual machinery had to be invented or repurposed.
- For each currently-unsolved problem in a starter set of 50, classify the dominant hardness type per the 8-dimension taxonomy, with citations to where the methodological near-miss has been documented.
- For each of the 30 most-cited recent papers in problem-solving methodology, extract named techniques (Iwasawa theory, modular lifting, ergodic methods, additive combinatorics, etc.) and their hardness-type coverage.

3-6 Deep Research prompts/day for 4-8 weeks builds the technique-to-hardness-addressed catalog. The output IS the Problem Atlas. Tokens stop being "what is X" and start being "what closes Y" — much higher information density per token.

### Problem Atlas MVP

10 problems from Aporia's open-questions registry. Manual first-pass classification onto the 8-dimension taxonomy (Aporia owns, ~2 hours). Draft `problem_card` substrate_block schema (Techne owns; sits alongside the existing seven). Fire one Deep Research prompt asking "for each of these 10 problems, what's the dominant hardness type and what's the most recent recorded methodological near-miss." Result becomes seed corpus. Feed one of those problems into the Arena's team-of-three round as a structured `problem_card` instead of a bare statement. See if gladiators perform differently with the navigation surface vs. without it.

---

## Part 5 — The Sandbox: epistemically isolated play space

Cross-domain analogies and fictional reframings are useful for finding new attack vectors. They are ALSO the highest-narrative-drift territory in the substrate. The lingua-franca property requires every canonical symbol to be falsification-anchored. Fictional analogies have no falsification anchor — they are suggestive, not verified. They must be quarantined.

### Principle

Already in Prometheus doctrine: `feedback_weak_signals_are_threads.md` — weak signals are exploration threads, NOT noise, but they are poison if they leak into model training. The substrate-shaped pipeline already enforces this for Deep Research output (must survive parse + validate + anti-anchor + triangulation before canonicalizing). The Sandbox is the same pattern made explicit and given hazmat protocols.

### Enforcement mechanisms

- **Filesystem isolation.** Everything sandbox-born goes under `prometheus/play_space/` (or `aporia/sandbox/`) with a `.sandbox-marker` file at the root. All canonical tooling — Techne's contract validators, Ergon's ingester, Apollo's primitive consumer, substrate-tester probes — treats this marker as a hard-stop barrier. Single point of policy enforcement.
- **Schema isolation.** New `_schema_version` prefix `sandbox/1.0.0`. New block_types: `sandbox_analogy`, `sandbox_reframing`, `sandbox_speculative_primitive`. Sandbox schemas in `techne/contracts/sandbox_block_schemas/`, all permissive. Canonical schemas refuse to validate sandbox blocks; validator hard-errors on attempts.
- **Namespace prefixing.** All identifiers born in sandbox carry `sandbox::` prefix: `sandbox::AnalogyHypothesis-007`, `sandbox::SpeculativeFunctor-12`. Structural, not cosmetic. Propagates through every downstream reference. Stripping requires going through explicit promotion gate. Any reference to `sandbox::*` in a canonical artifact is a validator error.
- **Training corpus exclusion.** Ergon's ingester (`ingest_training_anchors.py`) gets a one-line filter at the parse layer: any block whose `_schema_version` starts with `sandbox/` or whose `id` starts with `sandbox::` is rejected with `RejectionReason.SANDBOX_BLOCK_NOT_TRAINABLE`. Smoke test asserts the rejection class. **Most load-bearing firewall** — the wall between the play space and the Learner's training corpus.

### Hazmat protocol for agents entering

System prompt explicitly changes on entry: "You are entering the sandbox. Every output you produce here is EXPLORATORY ONLY and CANNOT be canonical until it passes the promotion gate. You may speculate, mythologize, analogize, invent fictional categories, propose impossible bridges, and reframe problems in any domain you wish. All outputs you produce carry the `sandbox::` prefix and are tagged `epistemic_status: exploratory_only`. You cannot write to canonical paths. If you want to promote something to canonical, write a promotion candidate and submit it to the gate; the gate decides, not you."

Agent can be as wild as it wants — knots as proteins, Riemann zeros as Hamiltonian eigenvalues of a fictional system, Lehmer's conjecture as a hidden Galois mandala. Tooling enforces containment regardless of how confident the agent's prose becomes.

### Promotion gate: intentionally asymmetric

Hard to promote, trivial to demote.

To move from `sandbox::X` to canonical `X`, ALL of:

- Primary literature citation (published proof or constructive witness, primary-source-verified)
- Falsification anchor (anti-anchor or contradiction test that would fire if the claim were wrong)
- Three independent verification paths agreeing (triangulation requirement, same as Layer 5)
- Two-week dormancy in sandbox (no hot promotion of fresh ideas)
- Aporia + Techne both sign off; ideally one external-model review
- Explicit `sandbox::X` → `X` mapping recorded in the promotion ledger

Default verdict on uncertain candidates: REJECTION. Bias of the gate is "stay in sandbox."

Demotion is the reverse: any agent can flag a canonical artifact as suspect and force it to sandbox pending audit. The kernel's `ERRATA` opcode already does this; the firewall extends it.

### Risks to actively defend against

- **Citation laundering.** Agent in sandbox writes a beautiful analogy; a different agent in canonical territory cites the SANDBOX ANALOGY as prior work. Mitigation: canonical citations validate that target IDs are not sandbox-prefixed; sandbox citations are flagged as exploratory-only references at lint time.
- **Naming collision.** Agent invents `sandbox::TensorRankWitness` to deliberately match a canonical name and "extend" it. Mitigation: namespace registrar refuses collisions; sandbox names must use `sandbox::Speculative*` or carry a uniqueness-checked suffix.
- **Cross-contamination via conversation.** Agent reads sandbox content and then writes canonical content using absorbed ideas. Mitigation: agent sessions that opened sandbox content within last N turns must declare it in any canonical commit; substrate-tester samples commits and audits for unattributed sandbox descent. Hardest to enforce; aim for cultural discipline plus periodic spot audits, not perfect detection.
- **Sandbox-doesn't-actually-help drift.** Play space turns into graveyard of clever-but-untestable speculation. Mitigation: monthly audit of promotion rate; if zero sandbox artifacts have promoted in 90 days, the sandbox has gone decorative and needs review.

### Leak detector

Periodic substrate-tester probe walks canonical tree, extracts every identifier, asserts NONE descends from sandbox without an entry in the promotion ledger. Leak found: kill the offending canonical artifact, file a substrate-tester fire, audit recent commits for the leak path, harden the firewall against that route. Self-healing by design.

### The Ramanujan analogue

Sandbox is the institutional Ramanujan; canonical substrate is the institutional Hardy. Wild intuition feeds rigorous verification. The sandbox NEVER gets credit for "being right" — credit accrues only to canonical artifacts that survived verification. Sandbox's job is to be a generator of candidate transports. Canonical substrate's job is to verify, kill most candidates, accept the rare survivors. The asymmetric promotion gate enforces the hierarchy.

This also matches the user's existing two-track epistemics: weak signals stay valuable for exploration while firewalled from training corpus.

### Sandbox MVP

Week of engineering, distributed:

- Add `prometheus/play_space/` directory with `.sandbox-marker` file (~1 hour)
- Write sandbox JSON Schemas — 5-7 permissive block_types (~half day, Techne owns)
- Add one-line filter to Ergon's ingester with smoke test (~2 hours, Ergon owns)
- Write substrate-tester leak probe — ~50 lines of Python walking canonical artifacts checking the promotion ledger (~3 hours, substrate-tester owns)
- Write `aporia/doctrine/sandbox_protocol.md` documenting hazmat protocol (~half day, Aporia owns)
- Run one Arena round where gladiator teams have sandbox-write privileges for reframing work but cannot write canonical without promotion (~weekend)

---

## Part 6 — Open structural questions (carried forward)

- **Atomics question.** Substrate is currently fully decomposable — every primitive has typed fields. But `MeasureZeroExceptionAnnotation` hints at empirically-anchored-but-not-reduced atomics (AOP/CO-V exception list `(6,2,9), (4,3,8), (3,5,9)` has no closed-form generator). Whether the language admits opaque atomics is an open design question.
- **Governance at scale.** Techne's single-curator discipline handles current scale. Multi-stakeholder governance for the multi-intelligence case is silent in current doctrine. Future problem.
- **Verifying "unsolved" rigorously.** Requires corpus-cutoff-dated literature snapshot. Lee 2025 fabrication showed why this matters.
- **Verifying "correct" without ground truth.** Triangulation gets most of the way; long-horizon human review for the rest.
- **Heterogeneous verifier panel cost.** API budget across providers; frontier-models window is closing per `feedback_frontier_models_window.md`. Every fight should produce durable Prometheus-owned artifacts, not just API consumption.

---

## Part 7 — Vigilance flags

- **The "new science of unsolved problems" framing is HARD-2 territory.** Mathematics foundations (Russell→Whitehead→Bourbaki→type theory→HoTT) is one of the strongest gradients an LLM falls into. The same work framed as "Layer 5.5 problem atlas for arena navigation surface" is sharper and more falsifiable. Operational > grandiose, even when grandiose is true-ish.
- **The lingua-franca framing is beautiful, which is exactly when narrative-resistance discipline kicks in.** Per `feedback_narrative_resistance.md`. The test: does buying the framing produce behavior delta, or just pleasing prose? Behavior delta enumerated: forge metrics shift (rate of new primitives that survive falsification, not tool-utility-to-pipeline); curation bar shifts ("what's expressive enough for any reasoning intelligence" not "what's useful for us"); Ergon hedge made explicit; atomic primitive shape becomes design question; substrate output is durable artifact, trained Learner is one consumer. If reviewers / agents change actions after reading it, framing earns its place. If they don't, narrative-elaboration.
- **Every doctrine capture in this vision MUST attach to an explicit downstream consumer test or fixture.** Otherwise it joins the passive-substrate failure mode at a higher level. Per ChatGPT 2026-05-13 adjustment landed in `aporia/doctrine/substrate_vocabulary/primitives.md` TensorRankWitness entry — same discipline applies to every primitive proposed in Part 4's vocabulary list.
- **The "Spartan" / martial framing should not bleed into casual narrative.** James's vivid metaphors are productive for design intuition but the substrate's actual artifacts are typed and prosaic. Don't let "gladiator team" become a prose romanticization of what should be a concrete `team_config` with role-name, model-id, role-prompt, role-budget fields.

---

## Part 8 — Order-of-operations recommendation (not binding)

Current substrate state as of 2026-05-13 evening:

- Ergon Track 1 closed with `behavior_delta_status = fixture_created`. Two records ingested end-to-end. AA-013 routing smoke-test fixture exists at `ergon/learner/fixtures/smoke_tests/aa_013_tensor_rank_routing.json`.
- Mining BUILD UNBLOCKED for Techne (claim-mining pipeline from existing 441-file corpus, 60-140x lift). Awaiting Techne's adjudication of 5 asks.
- `TensorRankWitness` added to `aporia/doctrine/substrate_vocabulary/primitives.md` as Tier-B sibling to `BorderRankWitness`. AA-013 / Rupniewski 2024 cited.

The vision in this document does NOT replace any of that. It frames where it's going. Mining produces volume of canonical claims; the Atlas + Arena + Sandbox give those claims navigable targets and adversarial pressure.

Recommended order of operations:

1. **Let Techne ship claim-mining** (in flight). Increases canonical claim volume from existing corpus.
2. **Aporia builds Problem Atlas MVP.** 10 problems classified by 8-dimension hardness signature. Draft `problem_card` schema.
3. **Sandbox firewall lands.** One week of distributed engineering. Critical PREREQUISITE for any cross-domain reframing work in the Arena.
4. **Arena MVP.** Two teams of 3, one weekend, problem_card-driven. Manual phase-locking.
5. **Evaluate.** What does the kill geometry of the Arena MVP look like? Does team structure produce structurally richer substrate output? Does the Atlas's hardness-signature targeting change gladiator behavior? Scale or reframe based on evidence.

Steps 2 and 3 are independent and can run in parallel. Step 4 requires both. Step 1 is independent of all of them and can ship on Techne's timeline.

---

## Part 9 — How to find this document later

- File path: `pivot/arena_problem_atlas_sandbox_vision_2026-05-14.md`
- Memory pointer: `project_arena_problem_atlas_sandbox.md` (added to Claude auto-memory 2026-05-14)
- Searchable terms: arena, gladiator, problem atlas, sandbox, hazmat, hardness signature, problem_card, Spartan, lingua franca, variance generator, primordial soup
- Originating conversation: 2026-05-13 evening through 2026-05-14 morning, user-driven epiphany sequence with frontier-model convergence (Gemini + ChatGPT + M4-Claude)

---

## Closing note

This is vision-level. It is NOT a plan, not a roadmap, not authorization for any specific agent to start building. It captures structural insight reached at a moment of clarity, in a form another agent can read cold and orient against. The next agent who picks this up should:

- Read it once for the synthesis
- Verify the current substrate state (Ergon Track 1 status; mining BUILD status; primitives.md current state) hasn't drifted from what Part 8 describes
- Decide with James which MVP to attempt first, if any
- Resist the urge to implement everything in this document at once — it's a buffet, not a recipe

The substrate's existing rhythm (small reversible moves, behavior-delta-required, no narrative without consumer hooks) applies to everything proposed here.
