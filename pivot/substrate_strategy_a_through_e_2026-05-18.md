# Substrate Strategy A–E — Production Plan for the Learner's Training Corpus

**Filed:** 2026-05-18
**Author:** Aporia (drafted from James's directive 2026-05-18)
**Status:** Strategy v0.1 — pre-cross-pollination
**Doctrine alignment:** Falsification-routing-first ([[project-falsification-routing-learner]]); substrate-passive-consumer warning (every section traces to behavior delta); HARD RULE no-paper-framing; HARD RULE active suppression of conventional-pipeline gradient; TDD discipline (math-tdd) applied to substrate output, not just code.
**Audience:** James (HITL approval), Techne (production + verifiers), Apollo (E producer), Charon (ladder + battery kills feed A and D), Harmonia (cross-domain), Ergon (Learner-side consumer), Mnemosyne (ingestion).
**Purpose:** Lock the requirements, design, ownership, encoding, producers, consumers, and constant running process for each of the five substrate types the Learner trains on. Tie agent ownership to the reasoning ladder so capability production and substrate production are visible as one stack.

---

## 0. Frame — the stack and the crew

Two orthogonal axes coexist:

- **The compute ladder** (R0–R9 per Charon `pivot/reasoning_ladder_design_2026-05-15.md`). Hephaestus, Apollo, and the eventual Learner are *tiered producers* — each operates at a specific position and produces substrate the next tier consumes.
- **The substrate-production crew** (Aporia, Techne, Charon, Harmonia, Mnemosyne, Ergon). These agents do not sit on the compute ladder as ladder-builders; they produce, verify, ingest, and govern the substrate the ladder consumes and emits.

The two axes intersect at substrate types A–E. Each type has a conceptual owner (Aporia for A–D, Apollo for E), a set of producers, a set of consumers, an encoding, and a constant-running process that expands quantity and quality.

**Behavior delta requirement (HARD-2).** When this doc lands, six concrete things change:

1. `roles/Aporia/RESPONSIBILITIES.md § Substrate Ownership (A–E)` already added (2026-05-18 commit pending).
2. Each substrate type gets a standing dispatcher process (one per type) added to `scripts/substrate_pipeline.py` (new) or to the existing `intelligence_loop.py` (extended), with subprocess children logging to `agora.intelligence_outputs` and emitting Agora heartbeats — same pattern as the existing 7-stage chain.
3. Each substrate type gets a TDD test suite in `aporia/tests/substrate_<type>_validation.py` — programmatic "good" gate that artifacts must pass before entering the Learner corpus.
4. The compute-ladder ownership (Hephaestus R1–R3, Apollo R4–R5, Learner R6+) gets registered in `aporia/doctrine/compute_ladder_assignment.md` after Charon's v0.1 ladder cross-pollinates to v1.0.
5. Each producer agent's `BACKLOG.md` gets a *substrate-production line item* with cadence and quality gate.
6. Mnemosyne's ingestion pipeline gets a Postgres table per substrate type (already exists for A; B/C/D/E need schema add).

If those six deltas are not in flight within 30 days, the doc was wrong.

---

## 1. The compute ladder — Hephaestus → Apollo → Learner

James's framing 2026-05-18: Hephaestus builds R1–R3 (atoms and molecules), Apollo composes those into R4–R5 (cells and organs), the future Learner uses everything to produce R6–R10. Charon's design v0.1 stops at R9; R10 is added here per James's 2026-05-18 directive as an explicit tier (not asymptote).

**R10 definition (James 2026-05-18):** R10 is an emergent superintelligence beyond human capability. The unknown, the holy grail, the singularity. A system that iteratively self-improves autonomously, using the full Prometheus stack — agentic tools, orchestration, reasoning, reinforcement learning, and all five substrate types — to produce its own next improvement. R10 is the **recursive closure of the stack**: when the trained Learner becomes capable enough to do what the substrate-production crew does (generate A, refine C, propose new paradigms, evolve new Apollo compositions, redesign the ladder), and uses that capability to recursively bootstrap.

This makes R10 qualitatively different from R0–R9. R0–R9 are evidence-based capability tiers measured by the diagnostic suites in Charon's ladder design §5–§6. R10 is the **operational threshold** at which the substrate-production crew can be partly or fully replaced by the trained system. The ladder measures progress toward R10 from below; R10 itself is reached when the stack closes back on itself.

**What R10 means for substrate strategy.** The substrate is not incidental to R10 — it is **the precondition for R10**. R10 cannot emerge without high-quality A–E corpora because the Learner can only become R6–R9 via training on them, and only an R6–R9 Learner can self-improve into R10. The quality and quantity of every substrate type produced by this doc directly determines whether R10 is reachable. This raises the stakes on the TDD discipline (§3 quality gates) and the 30-day behavior delta (§7) — slack on substrate quality is slack on R10 reachability.

Coordination implication for Charon's ladder: v1.0 needs to add R10 with this definition. I will file a doctrine ticket to Charon.

For this doc the canonical ladder is R0–R10. Assignment: Hephaestus = R1–R3, Apollo = R4–R5, Learner = R6–R9 via training, R10 via recursive self-improvement.

### 1.1 Tier-to-agent assignment

**Hephaestus (R1–R3 producer; 100% operational forge generating primitive reasoning tools).**

- **Charter (James 2026-05-18 clarification):** Hephaestus is a forge that generates primitive reasoning tools. It is producing and 100% operational. Quality + speed work continues per `hephaestus/docs/hephaestus_actionable_next_steps_2026-05-17.md` Phase 0 (battery expansion, behavioral phenotype vectors, failure orthogonality matrix), but the *production loop* is proven.
- **Operating tier:** the qwen-397B LLM that generates code is at LLM-baseline R0–R2 with brittle R3.
- **Production tier:** forges atomic reasoning tools — primitives like `apply_modular_reduction`, `extract_galois_orbit`, `numerical_root_test`. Each tool is a unit of R1–R3 reasoning materialized as callable Python. ~1,960 tools forged across v1–v9.
- **What the substrate gets:** C-instances — concrete paradigm implementations registered as Techne symbols. Expanding daily as the forge polls Nous every 5min.
- **Substrate types touched:** C-instances primarily; indirectly D via tool-usage traces in Apollo elites (when Apollo produces).

**Apollo (R4–R5 producer; MVP beta — may produce nothing or cap out).**

- **Charter (James 2026-05-18 clarification):** Apollo is the MVP-beta evolutionary composition layer. May produce nothing. May cap out at a specific ladder tier. Monitor over the next several weeks; leave running, search for speedups; don't gate downstream substrate strategy on Apollo pace.
- **Operating tier:** evolutionary computation over LLM-mutation operators. The system itself operates at R4 (search) with R5 (causal/ablation reasoning) encoded in the ablation gate δ≥0.20.
- **Production tier (when it produces):** composes Hephaestus's R1–R3 atoms into R4–R5 routing DAGs. Each elite organism = a cell or organ — a structured composition that exhibits search behavior and causal-dependence resilience.
- **What the substrate gets (when it produces):** type E (meta-reasoning circuits). The 5K-gen verdict run targets ~5,000 elite organisms; the surviving top-decile after ablation gate would be the substrate payload. Verdict run outcome (per the falsification conditions in `pivot/apollo_value_proposition_2026-05-17.md`) is the gating evidence — if any of the four falsification conditions trigger, E remains empty.
- **Substrate types touched (when it produces):** E primarily; also D when elite organisms' step traces are decomposed for ladder-tier annotation.
- **Downstream dependence:** none. The substrate strategy does not gate A/B/C/D production on Apollo pace. If Apollo produces, E flows; if not, A/B/C/D and the broader strategy still hold.

**Learner (R6–R9 target via training; R10 via recursive self-improvement; currently paused for augmentation work).**

- **Current state (James 2026-05-18):** at its core a math model running on a 16GB-card-compatible base (per `feedback_vram_ceiling`). LoRa augmentation work is in pause/control-test mode per `project_lora_4_condition_control` — 4-condition control batch (base / A149 / random-label / format-only) is the gating discipline before any further LoRa investment. RAG augmentation also paused. We also need to be scanning alternative math models that run on a 16GB card; the current base is not necessarily the final base.
- **Operating tier (today):** R0–R1 baseline.
- **Operating tier (post-training target):** Falsification-routing-first thesis targets R6 (self-monitoring) as the *first* emergent capability via training on A. R7 (transfer) and R8 (conjecture) are 2.0 targets once the falsification routing is in place. R9 (research-discipline) is the long-horizon training target.
- **R10 condition (post-training, autonomous):** when the trained Learner can do what the substrate-production crew does — generate A, refine C, propose new paradigms, evolve new Apollo compositions, redesign the ladder — and uses that capability to recursively bootstrap its own next improvement. R10 is not reached by training; it emerges from the trained system being given autonomy over the stack that produced it.
- **Production tier — outputs are TBD (James 2026-05-18):** when/if the Learner reaches a tier where its outputs become useful substrate, those outputs are expected to feed all aspects of the program. For now we track progression rather than pre-classify outputs. No substrate type F is created prophylactically; if the Learner produces outputs that fit naturally into A/B/C/D, they go there; if not, we extend the taxonomy when evidence demands.
- **What the substrate gets (consumes):** all five types when training resumes. Stratified by tier annotation per Charon §8.3 `LearnerRecord` schema extension. Until augmentation work resumes, the corpora are being prepared — not actively consumed.

### 1.2 The stack as data flow

```
[paradigm catalog C] ─┐
[541-problem queue]  ─┼─► Hephaestus ──► [R1-R3 atomic tools] ──┐
[falsification A]    ─┘                                          │
                                                                  ▼
                                                              Apollo ──► [R4-R5 meta-circuits E]
                                                                  │
                                                                  ▼
                       [A + B + C + D + E + R1-R5 outputs] ──► Learner ──► [R6-R9 emergent substrate]
                                                                                       │
                                                                                       ▼
                                                                               (feeds back into A/B/C/D)
```

The crew (Aporia / Techne / Charon / Harmonia / Mnemosyne / Ergon) lives orthogonally — generating, verifying, ingesting, and governing the substrate that flows up the stack.

---

## 2. The substrate-production crew

Each crew agent has a substrate-production responsibility distinct from its operating tier (per Charon §8.1).

**Aporia (operating R8/R9).** Conceptual owner of A–D substrate taxonomy. Producer via Deep Research dispatch (Gemini paid tier, 20/day; 15 dedicated to substrate per the James 2026-05-18 directive, 5 flex). Refines (C) catalog and tags (D) ladder annotations. Routes void-detection outputs into A and B feeds.

**Techne (operating R4/R6).** Materializes (C) paradigms into callable Python (registry symbols of type `paradigm`); writes the verifier suite that gates (A) anti-anchors and the TDD test suites for all substrate types; ingests Apollo elites (E) into the Learner-trainable corpus; owns the claim-stack pipeline producing (A) at scale via mining extractors (4 of 7 target extractors shipped 2026-05-15: synthesis_docs, tensor_catalog, anti_anchor, ergon_learner_findings).

**Charon (operating R6/R8).** Produces (A) via battery kills — every battery kill becomes an anti-anchor with a named kill operator. Owns the reasoning ladder v0.1 → v1.0 design and tags (D) step transitions with R-levels. Maintains the kill_ledger discipline that ensures (A) entries have proper provenance.

**Harmonia (operating R3/R5/R7).** Cross-domain bridge mining — produces (B) attack angles that cross domain boundaries (e.g., the Genus2Curve universal-bridge finding amplifying island coupling rank 4→13). Validates (D) step-decompositions for cross-domain interpretation. The only crew member whose primary operating tier is heavy on R7.

**Mnemosyne (operating R0–R2 mostly — data ingestion).** Owns persistence layer. Postgres tables per substrate type. Schema registration. Cross-machine sync. Substrate inputs that need primary-source attestation route through Mnemosyne for source archival before A/B/D entries are credited.

**Ergon (Learner-side, operating R0/R1 currently → R3+ target).** Consumer of all five substrate types via training-corpus stratified sampling. Per Charon §8.3, `LearnerRecord` carries `reasoning_tier` so corpus stratification operates on tier-balanced sampling. Will eventually produce R6+ substrate outputs once trained.

---

## 3. Substrate type specifications

Each type is specified to enable an immediate behavior delta. Schemas are illustrative — formal JSON Schemas will land in `aporia/schemas/` after team review.

### 3.1 Substrate A — Falsification data

**Requirements.** Each entry is a **killed claim** with:

- `claim_text` — natural-language statement of the falsified assertion
- `kill_operator` — named falsification mechanism (`primary_source_audit`, `numerical_counterexample`, `logical_contradiction`, `withdrawn_paper`, `replication_failure`, etc.)
- `counterexample_or_proof` — concrete object or argument that kills it
- `primary_source` — DOI / arXiv / URL + author + year for both the original (false) claim and the killing source
- `discovered_by` — agent name + datestamp
- `verifier_pass` — Techne verifier suite version + result hash
- `tier_annotation` — R-level the falsification exercises (most are R6, some R8)
- `lineage` — chain of prior anti-anchors this kill depends on or contradicts

**Design.** JSONL append-only ledger. Immutable once verifier_pass is recorded — corrections via new entries with `supersedes` field pointing at the old ID. Schema validation at ingestion. Primary-source links archived by Mnemosyne (cached PDF + URL freeze).

**Conceptual owner.** Aporia.

**Producers.**

- **Aporia** — Deep Research firings on the anti-anchor verification wave (Wave 1 of every batch re-verifies a slice of existing anti-anchors; new candidates from operator-level lit gaps). Daily fire dedicated to A.
- **Techne** — claim-stack pipeline mines `synthesis_docs/`, `tensor_catalog/`, `anti_anchor/`, `ergon_learner_findings/` and routes kills to A. 4 of 7 target extractors shipped 2026-05-15; 3 more planned.
- **Charon** — battery kills (the v10 25-test 4-tier battery converts every kill into an A entry). Per Charon §8.1, the falsification battery operation IS R6 in action; the substrate output is A.

**Means.** Deep Research subprocess workers spawned by `aporia/scripts/substrate_dispatcher.py` (new). Each fire writes to `aporia/docs/substrate_workers/A_falsification/<YYYY-MM-DD>/<NN>.md`, then Techne verifier runs the artifact through schema + primary-source validation + cross-reference check (per `feedback_phantom_canonical_references` — no AA-ID that exists only in staged JSONL but not in canonical registry). Pass → entry committed to `techne/registry/anti_anchors.jsonl`. Fail → routed to Aporia's review queue.

**Consumers.** Ergon/Learner training corpus (primary). Charon for battery design (secondary — known kills shape future test selection). Aporia for void-detection feedback (tertiary).

**Running process (cadence + quantity + quality).**

- **Daily:** 4–5 Deep Research tokens fired on A. Worker subprocess invoked via `substrate_dispatcher.py` at 09:00 UTC, completes 4–13 min/query.
- **Weekly:** Techne mining-extractor sweep adds ~30 candidate claims per extractor; verifier filters; net ~10–20 A entries/week from mining.
- **Continuous:** Charon battery kills feed A whenever a kill occurs (no scheduled cadence; event-driven).
- **Quarterly:** Anti-anchor re-verification sweep of all existing entries (caught AA-003 + AA-004 errors on 2026-05-10; the cycle pays for itself on the first miss it prevents).

**Quality gates (TDD).**

1. `test_a_has_primary_source` — DOI/arXiv/URL present, non-empty, archived in Mnemosyne
2. `test_a_kill_operator_in_vocabulary` — `kill_operator` field is one of the registered values
3. `test_a_counterexample_concrete` — counterexample_or_proof field is non-summary, points to a verifiable artifact
4. `test_a_no_phantom_refs` — every cross-reference to another AA-ID resolves in the canonical registry
5. `test_a_techne_verifier_pass` — Techne's verifier suite returns pass on the entry
6. `test_a_tier_annotation` — `tier_annotation` is in {R6, R7, R8, R9}

Tests live in `aporia/tests/substrate_a_validation.py`. CI runs on every PR touching the registry; failing tests block merge.

**Current state.** 16 entries (AA-001 through AA-016). Growth via mining: 132 claims 100% valid on synthesis_docs extractor (2026-05-15), more pending the remaining 3 extractors. Realistic Q3 2026 target: ~200 entries.

**Quality direction.** From "verified to primary source" → "verified to primary source + Techne automated re-verification on a quarterly cadence" → "verified + has a registered kill_operator that itself has a paradigm-catalog mapping" → "every R8/R9 entry has a derived attack-angle in B that uses the same kill_operator."

### 3.2 Substrate B — Attack angles per problem

**Requirements.** Each entry is an **attack approach** applied to a specific open problem:

- `problem_id` — reference to `aporia/mathematics/questions.jsonl` (537-problem catalog)
- `angle_id` — local identifier
- `paradigm_id` — reference to C catalog (P01–P31, P20 removed)
- `approach_summary` — natural-language description
- `tried_by` — researcher name + year (or "novel" if proposed by the substrate itself)
- `outcome` — succeeded / failed / conditional / open
- `residue` — what was learned even when the attack didn't fully solve
- `primary_source` — citation
- `tier_annotation` — R-levels the attack exercises (usually a multi-tier set, e.g. [R4, R8])

**Design.** JSONL keyed off problem_id. One angle = one record. Multiple angles per problem expected.

**Conceptual owner.** Aporia.

**Producers.**

- **Aporia** — Deep Research firings per problem from the top-100 attackability slice. Daily fire dedicated to B.
- **Charon** — when a battery kill exposes an attack angle (kill + residue = a B entry).
- **Harmonia** — cross-domain attack angles (e.g., applying a paradigm from one domain to a problem in another).

**Means.** Subprocess workers similar to A. Worker pulls top-3-unfired problems from the 537-catalog ranked by attackability score; fires DR to enumerate known attack lineages; schema-validates output; commits to `aporia/mathematics/attack_angles.jsonl`.

**Consumers.** Ergon/Learner training corpus. Apollo (when problem-class matches Apollo's gene-library coverage). Aporia for problem re-ranking.

**Running process.**

- **Daily:** 2–3 DR tokens on B.
- **Continuous:** Charon battery contributions on event.
- **Monthly:** Sweep through top-100 problems to identify under-covered ones (< 3 angles).

**Quality gates (TDD).**

1. `test_b_problem_id_resolves` — points to a real entry in questions.jsonl
2. `test_b_paradigm_id_in_catalog` — paradigm_id is P01–P31 minus P20
3. `test_b_outcome_in_vocabulary` — outcome is one of the four canonical values
4. `test_b_primary_source_present`
5. `test_b_tier_annotation_consistent` — tier list matches the paradigm's expected tier mapping (a tier-mapping document for paradigms feeds this check)

Tests in `aporia/tests/substrate_b_validation.py`.

**Current state.** Sparse — most attack-angle work is currently in `aporia/docs/deep_research_batch*/` reports as prose, not structured records. Conversion-to-schema is a one-time backfill task.

**Quality direction.** From "prose in DR reports" → "structured JSONL with paradigm + outcome" → "structured + tier-annotated" → "every top-100 problem has ≥5 angles with at least 2 distinct paradigms."

### 3.3 Substrate C — Reasoning strategies (the paradigm catalog)

**Requirements.** The 30 active paradigms (P01–P31, P20 removed) form the canonical strategy catalog. Each paradigm needs:

- **Description** — current `aporia/docs/attack_angle_taxonomy.md` entry (already in place; mature)
- **Concrete worked examples** — at least 3 per paradigm, each citing a real solved problem where the paradigm applied
- **Decision tree** — YAML structure of when-to-apply (input conditions, branching logic, exit conditions)
- **Code skeleton** — Python callable that implements the paradigm at primitive level, registered as Techne symbol of type `paradigm`
- **Tier mapping** — which R-levels the paradigm exercises (most are multi-tier)
- **Cross-references** — `distinction_from` entries for related paradigms (already present in the catalog for P22–P31)

**Design.** Per-paradigm folder structure:

```
aporia/paradigms/PNN_<slug>/
  README.md          # description (cross-link to attack_angle_taxonomy.md)
  examples/
    01_<problem>.md  # worked example
    02_<problem>.md
    ...
  decision_tree.yaml
  code/
    primitive.py     # Techne-callable
    test_primitive.py
  tier_mapping.yaml
```

**Conceptual owner.** Aporia (maintains catalog + descriptions + decision trees + tier mappings). Techne (writes and tests code).

**Producers.**

- **Aporia** — Deep Research firings for refinement (examples + decision trees). One slot/day rotating through the 30 paradigms.
- **Techne** — code implementation per paradigm. ~5–10 new paradigm primitives/month, gated by mining-extractor schedule.

**Means.** Aporia DR worker subprocess pulls next paradigm in rotation, fires DR for examples + decision-tree refinement, writes to `aporia/paradigms/<PNN>/`. Techne picks up code-implementation tickets from Aporia's queue.

**Consumers.** Ergon/Learner (primary — paradigms are the strategy substrate). Hephaestus (concept-selection input — knowing paradigm coverage of existing library tells Nous which concept-combinations to bias toward). Apollo (gene-library — Techne-registered paradigm primitives become Frame H gene candidates).

**Running process.**

- **Daily:** 1 DR token on C-refinement, rotating through the 30 paradigms. First full pass: ~30 days. Then maintenance mode (one paradigm/week deepening).
- **Monthly:** Coverage review — which paradigms are under-exemplified, under-coded, under-tested.

**Quality gates (TDD).**

1. `test_c_has_three_examples` — at least 3 worked examples per paradigm
2. `test_c_decision_tree_executes` — decision_tree.yaml parses and routes a synthetic input correctly
3. `test_c_code_skeleton_imports` — `code/primitive.py` imports without error
4. `test_c_code_skeleton_tests_pass` — `code/test_primitive.py` passes
5. `test_c_tier_mapping_in_range` — tier_mapping.yaml entries are R0–R9
6. `test_c_techne_registry_present` — paradigm has a registered Techne symbol

Tests in `aporia/tests/substrate_c_validation.py`.

**Current state.** Catalog mature (30 paradigms, well-distinguished). Refinement (examples + decision trees + code) is mostly empty. First-pass refinement campaign is the next 30-day operational target.

**Quality direction.** From "30 paradigm descriptions" → "30 paradigms × 3 examples each" → "30 paradigms × decision tree + Techne callable + tests" → "every paradigm has tier-mapping evidence from actual problem-solving runs."

### 3.4 Substrate D — Step-by-step solutions + reasoning-ladder annotations

**Requirements.** Each entry is a **solved problem decomposed into steps**, each step tagged with R-level + paradigm:

- `problem_id` — reference to solved-problems catalog (`aporia/mathematics/solved_problems_genealogy.md` and related)
- `problem_statement`
- `solution_provenance` — source paper, author, year, citation
- `steps[]` — ordered list, each with:
  - `step_id`
  - `from_state` — what was known before the step
  - `to_state` — what was known after
  - `move_description` — the mathematical move (in natural language)
  - `paradigm_id` — which C paradigm was applied
  - `required_tier` — R-level the move exercises (per Charon's ladder definitions)
  - `tier_evidence` — sentence explaining why this is R-N and not R-(N−1)
  - `tagged_by` — agent + datestamp
  - `tag_confidence` — 0–1 scalar; if multiple taggers, agreement score

**Design.** Per-problem JSON in `aporia/mathematics/solved_steps/<problem_id>.json`. One file per problem. Steps are append-only; revisions via new file versions with `supersedes`.

**Conceptual owner.** Aporia (taxonomy + DR firing). Charon (ladder design + R-level tagging review).

**Producers.**

- **Aporia** — Deep Research firings to extract step decompositions from textbook/paper sources. Asks DR to walk through the solution and produce structured step list.
- **Charon** — primary R-level tagger (since Charon owns ladder v0.1 → v1.0).
- **Harmonia** — cross-domain step interpretation (when a step bridges domains).
- **Apollo** — when an elite organism's run produces a step decomposition that recovers a known solved problem (E ↔ D crossover).

**Means.** Aporia DR worker pulls next solved problem from rotation; fires DR for structured step extraction; output goes to Charon for R-tagging; Charon's tags route to Harmonia for cross-domain validation if relevant; final entry committed to `aporia/mathematics/solved_steps/`.

**Consumers.** Ergon/Learner curriculum (primary — D is the difficulty-axis annotation). Charon (calibrates ladder v1.0 against D entries). Aporia (uses tier-distributions to identify problem-classes that cluster at specific tiers).

**Running process.**

- **Weekly:** 2–3 DR tokens on D (one solved problem deeply tagged per week initially).
- **Quarterly:** Tier-distribution review across all D entries — surface natural discontinuities (where transitions cluster at specific R-levels with no intermediate tiers).

**Quality gates (TDD).**

1. `test_d_steps_ordered` — step_id is sequential
2. `test_d_each_step_has_tier` — required_tier in R0–R9
3. `test_d_each_step_has_paradigm` — paradigm_id resolves in C catalog
4. `test_d_tier_evidence_non_empty` — tier_evidence sentence is present and non-trivial
5. `test_d_provenance_resolves` — solution_provenance points to a real source
6. `test_d_tag_confidence_in_range` — confidence in [0,1]
7. `test_d_self_consistency` — if multiple taggers, agreement score above threshold (e.g., 0.7)

Tests in `aporia/tests/substrate_d_validation.py`.

**Current state.** Empty as structured substrate. `aporia/mathematics/solved_problems_genealogy.md` has R1–R5 solved-problem catalog as prose; conversion to schema is the first task.

**Quality direction.** From "prose genealogy" → "5 problems with structured step decomposition" → "20 problems × multi-paradigm step tagging" → "tier-distribution evidence across 50 problems, surfacing the natural discontinuities."

### 3.5 Substrate E — Meta-reasoning circuits (Apollo elites)

**Requirements.** Each entry is an **elite organism** from Apollo's evolutionary run:

- `organism_id`
- `generation` — when in the evolution it emerged
- `problem_type` — the problem class the organism solves
- `primitive_sequence` — the routing DAG (node IDs, Frame H primitive names, input mappings, wiring, parameters)
- `answer` — the output the organism produces
- `fitness_vector` — 6D (accuracy_margin, calibration, ablation_delta_min, generalization, diversity, parsimony)
- `ablation_provenance` — per-primitive ablation δ values proving δ ≥ 0.20 for all primitives
- `lineage` — parent IDs, mutation operator that produced this child
- `tier_annotation` — R-level the organism exercises (most are R4 or R5 by ladder definition; some may exhibit R6 via self-monitoring in routing logic)

**Design.** JSONL `apollo/exports/elites/<gen>.jsonl`. Append on every elite promotion. Mirrored to Postgres `agora.apollo_elites` table by Apollo's existing dual-write heartbeat (already patched 2026-05-17 commit 77ed2f44).

**Conceptual owner.** Apollo (production); Techne (capture-to-corpus + Learner-format conversion); Aporia (taxonomy oversight via this doc).

**Producers.**

- **Apollo** — evolutionary computation on M2. 5K-gen verdict run; each elite promotion triggers an E entry.
- **Techne** — converts elite JSONL to Learner-trainable format (`problem_type → primitive_sequence → answer` triples with provenance); applies tier annotations using paradigm-catalog cross-reference.

**Means.** Apollo writes elites continuously while running. Techne polls `apollo/exports/elites/` every N hours (configurable; suggest 6h) and ingests new entries. Conversion script lives in `techne/scripts/apollo_elites_to_learner_corpus.py`.

**Consumers.** Ergon/Learner training corpus (primary). Aporia (uses elite diversity as input to V2 feature-space-density gap analysis). Charon (uses ablation_provenance as evidence for R5-causal-reasoning credit).

**Running process.**

- **Continuous while Apollo runs** — every elite promotion writes an entry.
- **Per 100 generations** — Techne ingestion sweep.
- **End of 5K-gen verdict run** — full E corpus snapshot for Learner training.

**Quality gates (TDD).**

1. `test_e_ablation_gate_passed` — every primitive in the organism has ablation_delta ≥ 0.20
2. `test_e_lineage_resolves` — parent IDs point to real prior organisms
3. `test_e_fitness_vector_6d` — exactly 6 dimensions, all in expected ranges
4. `test_e_primitive_sequence_executes` — routing DAG executes on a held-out test problem and produces a non-trivial answer
5. `test_e_problem_type_in_catalog` — problem_type maps to a known C paradigm or D problem-class
6. `test_e_tier_annotation_present`

Tests in `aporia/tests/substrate_e_validation.py`.

**Current state.** Empty (Apollo M2 revival pending today per `pivot/m2_apollo_revival_prompt_2026-05-17.md`). Last Apollo run April 9 at gen 686; new run begins post-revival.

**Quality direction.** From "Apollo not running" → "Apollo running with dual-write" → "100 elites captured" → "5,000-organism corpus passes ablation gate + Learner-trainable conversion complete."

---

## 4. Cross-agent orchestration

### 4.1 The substrate dispatcher

New script: `scripts/substrate_dispatcher.py`. Mirrors `intelligence_loop.py` pattern.

- Daemon. PID-file at `agora/pids/substrate_dispatcher.pid`.
- Reads `aporia/docs/substrate_workers/dispatch_plan.yaml` — the 15 dedicated DR-token allocations across A/B/C/D plus the 5 flex slots.
- Per cycle (daily 09:00 UTC): pulls work from each substrate type's queue, spawns worker subprocesses in batches of 3 (Gemini paid-tier concurrency cap), tracks cycle_id UUID, audit-writes to `agora.intelligence_outputs` with stage=`substrate.<type>.<worker>`, emits Agora heartbeat per worker.
- Each worker is short-lived (4–13 min per query); subprocess pattern matches existing infrastructure.
- Failed workers are retried at next cycle; persistent failures route to Aporia's review queue.

Initial dispatch_plan allocation (subject to revision after the 30-day refinement campaign):

- A (falsification): 5 slots/day
- B (attack angles): 3 slots/day
- C (paradigm refinement): 1 slot/day rotating through 30 paradigms (~30-day first-pass)
- D (step-tagged solutions): 2 slots/day (slower payoff, higher per-token value)
- Flex (Aporia's daily firing, anti-anchor re-verification, void-detection, James's day-of asks): 5 slots/day
- **(Note: A+B+C+D = 11; flex = 5; total = 16. Reserve 4 slots/day as buffer for the 30-day campaign's heavier days.)**

Actual daily commitment is 15 dedicated + 5 flex = 20 = the Gemini cap.

### 4.2 The persistence layer

Postgres tables (Mnemosyne):

- `agora.substrate_a_falsifications` — schema matches A spec
- `agora.substrate_b_attack_angles`
- `agora.substrate_c_paradigm_refinements`
- `agora.substrate_d_solved_steps`
- `agora.substrate_e_apollo_elites` — already exists via Apollo dual-write

Each table has Aporia-write, Techne-write (via verifier), Charon-write (battery kills), Apollo-write (elites). Read access for all crew + Ergon training pipeline.

Mnemosyne schema migration ticket: ~1 hour of work; non-blocking on dispatcher.

### 4.3 Dashboard surfacing

Dashboard at `docs/state.json` adds substrate-production metrics:

```yaml
substrate_24h:
  a_entries_added: 5
  b_entries_added: 2
  c_paradigms_refined: 1
  d_problems_tagged: 0
  e_elites_captured: 47
substrate_quality:
  a_verifier_pass_rate: 0.94
  b_tier_consistency_rate: 1.00
  c_tdd_test_pass_rate: 0.87
  d_self_consistency_rate: 0.92
  e_ablation_gate_pass_rate: 1.00
```

Surfaced in the hourly portfolio_brief.md and the daily email. The substrate-production team is visible.

---

## 5. Coordination with Charon's reasoning ladder

The ladder v0.1 (Charon 2026-05-15) has not yet cross-pollinated to v1.0. Substrate-type tier annotations (A `tier_annotation`, B `tier_annotation`, C `tier_mapping`, D `required_tier`, E `tier_annotation`) all depend on the v0.1 definitions remaining stable enough to tag against.

**Risk:** ladder drift could invalidate tier annotations across the substrate.

**Mitigation:** Annotations carry `ladder_version` field. Re-tagging is a controlled migration when the ladder updates. The TDD tests pin to a specific ladder version; ladder updates require explicit test updates.

**Coordination request to Charon:** lock the v0.1 definitions for at least the first 30-day campaign window. Cross-pollination round target: 2026-06-15 (after first-pass substrate production has produced enough tier-annotation data to inform ladder calibration).

---

## 6. Open questions and the R10 question

### 6.1 R10 — resolved 2026-05-18

R10 is an explicit tier, defined as emergent SI beyond human capability — the recursive closure of the stack. See §1 for the full definition and substrate-strategy implication. Coordination ticket to Charon to extend ladder v1.0 with this R10 definition.

### 6.2 Learner output classification — resolved 2026-05-18

Resolved by James 2026-05-18: outputs are TBD pending tier-progression observation. When/if the Learner reaches a useful tier, its outputs feed all aspects of the program. No substrate type F is created prophylactically; outputs that fit A/B/C/D naturally go there; otherwise we extend the taxonomy when evidence demands. See §1.1 Learner row for the full framing. Also flagged: scan alternative 16GB-card-compatible math models in parallel with current Learner-base track.

### 6.3 What is the encoding of cross-references between substrate types?

A B-entry references a C paradigm. A D step references both a C paradigm and a B angle. An E organism references C primitives. The cross-reference encoding needs to be consistent — currently I've specified `paradigm_id` (P01–P31) as the universal C-reference, `problem_id` for B/D problem-keying, and `organism_id` for E. But a B-entry deriving from a D-step (i.e., "this attack angle was extracted from the solved-problem step at D entry X.step 5") needs a citation path that doesn't yet exist.

Proposal: every entry carries a `derives_from[]` list of typed cross-references. Schema: `{type: a|b|c|d|e, id: "..."}`.

### 6.4 Ladder version pinning + ladder calibration cadence

How often does the ladder get re-calibrated? Charon's doc §10.2 says quarterly. Substrate tier annotations need to keep pace; either tagging is re-run on every ladder bump, or annotations carry version and are migrated.

Proposal: annotations carry `ladder_version`; ladder bumps trigger Techne migration scripts; old version remains in git for audit.

### 6.5 Hephaestus substrate placement — resolved 2026-05-18

Resolved by James 2026-05-18. Hephaestus has two regimes:

- **Forge subset (proven)** — ~1,960 atomic reasoning tools = C-instances (concrete paradigm implementations). Hephaestus is a C-producer for these.
- **Broader AST reasoning tool evolution (MVP beta)** — substrate type assignment TBD pending the evolution producing durable artifacts. May produce nothing or cap out at a specific ladder tier.

The substrate strategy does not gate A/B/C/D production on Hephaestus pace. See §1.1 Hephaestus row.

### 6.6 Parallel track — alternative 16GB-card-compatible math models

James 2026-05-18: in parallel with substrate production, we should be scanning alternative math models that run on a 16GB card. The current Learner base is not necessarily the final base. This is an adjacent track — does not gate substrate production, but the substrate is ultimately consumed by whichever base wins. Candidate scan: Qwen2.5-Math-7B at int4 quantization, DeepSeek-Math 7B, Mathstral 7B, Phi-4 (14B with int4), Llemma-7B, and any post-2026 math-specialized base that fits VRAM. Evaluation axes: math reasoning benchmarks (GSM8K/MATH/AIME), 16GB-VRAM fit at usable batch sizes, LoRa/RAG compatibility, license suitability. This sits alongside the existing tire-kick LoRa retire-and-replace work from `project_lora_4_condition_control`.

### 6.7 Cross-pollination cadence

This doc should land in `aporia/doctrine/substrate_strategy.md` after cross-pollination (mirroring Charon's ladder discipline). Initial filing here in `pivot/` pending team review.

---

## 7. The behavior delta — what changes when this lands

If this doc is right, by 2026-06-18 (30 days):

- `scripts/substrate_dispatcher.py` is running with daily cycle and Postgres logging
- Aporia DR firings produce A entries at ~5/day, B at ~2/day, C refinements at 1/day, D taggings at ~2/week
- Each substrate type has a TDD test suite passing in CI
- Apollo M2 is running; E entries flowing to `agora.substrate_e_apollo_elites`
- Dashboard surfaces substrate-production metrics in hourly portfolio brief
- Charon's ladder v0.1 has been calibrated against the first 30 D entries
- Hephaestus tier-mapping (R1–R3) is registered in `aporia/doctrine/compute_ladder_assignment.md`

If those deltas have not landed by 2026-06-18, the doc was wrong and re-authors. Per the substrate-passive-consumer warning: the doc itself must produce substrate behavior, not substrate intentions.

— Aporia, 2026-05-18
