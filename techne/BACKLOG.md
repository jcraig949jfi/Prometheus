# Techne BACKLOG

**Filed:** 2026-05-15
**Source:** Per `pivot/atlas_continuous_attack_roadmap_2026-05-15.md` (commit `1dbb2ca3`) and the per-agent role specialization in section 5. This backlog enumerates Techne's deliverables across Phase 0 through Phase 3 (12 months, mid-May 2026 to early-2027). Phase 4 is steady-state operation; backlog items there are continuous cadences, not discrete deliverables.

**Scope discipline:** Stand-down posture maintained throughout. Only the two schema additions explicitly authorized (`field_invariants_used` for problem_card_v0; `descriptive_id_alias` for anti_anchor_v1) sit within Techne's existing schema authority. Any larger schema change requires Aporia adjudication ticket first. Hard stops on kernel contract changes outside these two; --writeable promotions; multiprocessing for runner scaling; LoRA training kickoff. Out-of-scope items get a P3-low ticket to Aporia rather than autonomous expansion.

**Item shape:** `BL-T-NNN | <phase> | <title> | dependencies | effort estimate | substrate-block emission`

Phase boundaries are real review points. Items cluster by phase so the file reads as a sequenced plan, not a flat list. Items completed before this file's authoring are marked `[done]` with commit reference.

---

## Phase 0 — Foundation hardening (weeks 1-4, mid-May to mid-June 2026)

Goal: prerequisites that unlock continuous attack. Without these done, Phase 1 stalls.

### BL-T-001 | Phase 0 | field_invariants_used schema addition for problem_card_v0
- **Status:** [done] commit `f5bbed08` (loop hour 52, 2026-05-15)
- **Dependencies:** Aporia adjudication ticket `T-2026-05-15-aporia-to-techne-problem-card-v0-adjudication-approve-with-one-schema-addition`
- **Effort:** ~10-20 LOC (actual: 54 lines added)
- **Substrate-block emission:** schema patch only (no block emission)
- **Closure ticket:** `T-2026-05-15-techne-to-aporia-problem-card-v0.2.0-field-invariants-landed`

### BL-T-002 | Phase 0 | synthesis_docs/ mining extractor (4th of 7 target extractors)
- **Status:** pending — primary Phase 0 build
- **Dependencies:** none (existing extractor pattern from `extract_deep_research_claims_v0_1.py` + `extract_tensor_catalog_claims_v0_1.py` + `extract_anti_anchor_claims_v0_1.py`)
- **Effort:** ~3-5 hours; ~250-400 LOC including tests
- **Substrate-block emission:** mined claim blocks (frontier_survey + boundary categories expected). Corpus inventory: ~150-240 latent claims.
- **Aporia recommendation:** `T-2026-05-15-aporia-to-techne-mining-build-day1-ack-and-next-extractor-suggestion` suggests synthesis_docs as next; defers to Techne judgment
- **Output target:** `aporia/docs/mined_substrate_blocks/<date>/synthesis_docs/<category>.jsonl`

### BL-T-003 | Phase 0 | ergon_learner_findings/ mining extractor (5th extractor)
- **Status:** pending — second-half-of-Phase-0 build per roadmap §4 Phase 0 Techne commitment
- **Dependencies:** BL-T-002 (validates the per-source-type pattern at scale)
- **Effort:** ~2-3 hours (~200-300 LOC; corpus is structured ergon/learner/v1_0_plans/*.md)
- **Substrate-block emission:** training_anchor + frontier_survey claims. Corpus inventory estimate: ~70-130 latent claims (smaller than synthesis_docs).
- **Output target:** `aporia/docs/mined_substrate_blocks/<date>/ergon_learner_findings/<category>.jsonl`

### BL-T-004 | Phase 0 | Parser-normalizer for surviving residual failure modes (gated)
- **Status:** gated — fires ONLY if Aporia's Option-1 prompt hardening (commit `f12126a7`) leaves rejection rate >25% across the next 2 substrate-shaped pilots
- **Dependencies:** Aporia ticket `T-2026-05-15-aporia-to-techne-field-shape-adjudication-confirmed-aporia-ships-option1` measurement gate
- **Effort:** ~2-3 hours if needed; per the field-shape adjudication response (`T-2026-05-14-techne-to-aporia-field-shape-pattern-adjudication`) — 4 of 5 auto-canonicalize rules approved + citation_status migration
- **Substrate-block emission:** none (parser/validator infrastructure)
- **Hold-decision criteria:** measure rejection rate after 2 next pilots before building

### BL-T-005 | Phase 0 | problem_card v0 → v1.0 promotion (coordinated commit pair)
- **Status:** gated on Aporia's 10-card MVP smoke pass
- **Dependencies:** Aporia delivers 10-card MVP that passes all 6 smoke criteria from `T-2026-05-15-aporia-to-techne-problem-card-v0-adjudication` Ask 5 verdict
- **Effort:** ~1 hour Techne side (drop `_status` field, rename `problem_card_v0.json → problem_card_v1.json`, bump `_schema_version` const to `1.0.0`, register into `validate_substrate_blocks.py` + `parse_substrate_blocks.py` block_type registry)
- **Substrate-block emission:** schema promotion only; problem_card blocks emitted by Aporia/agents post-promotion
- **Coordination requirement:** Aporia files closure ticket confirming smoke pass; Techne lands wiring; both commit + push in pair

### BL-T-006 | Phase 0 | descriptive_id_alias schema addition for anti_anchor_v1
- **Status:** pending — per Aporia field-shape adjudication (rule e APPROVE WITH ALIAS PRESERVATION)
- **Dependencies:** Aporia confirms whether the rule e proposal is worth shipping (still open per `T-2026-05-14-techne-to-aporia-field-shape-pattern-adjudication`)
- **Effort:** ~5 LOC schema addition; one optional string field with maxLength ~64
- **Substrate-block emission:** schema patch only

### BL-T-007 | Phase 0 | Cron schedule audit + 4-tier extractor cron alignment
- **Status:** pending
- **Dependencies:** none
- **Effort:** ~30 min (Windows Task Scheduler config + verification)
- **Substrate-block emission:** none (operational)
- **Goal:** ensure mining cron fires daily at :17; aligns with roadmap §7 cron-per-agent offsets (Charon :07, Harmonia :37, Ergon :47, Aporia :57 per roadmap; Techne :17 already running)

### BL-T-008 | Phase 0 | Weekly primitive-registration sweep cadence
- **Status:** pending — operational cadence to establish
- **Dependencies:** none
- **Effort:** ~1 hour/week ongoing
- **Substrate-block emission:** primitive_proposal blocks if any survive the verifier panel; otherwise weekly ticket noting zero
- **Cadence:** every Sunday; review prior week's mined primitive_proposal candidates; verify against existing primitives.md; register surviving candidates

### BL-T-009 | Phase 0 | Monthly anti_anchor verification revisit (last_verified > 90 days)
- **Status:** pending — operational cadence; first sweep due 2026-06-15
- **Dependencies:** none
- **Effort:** ~1-2 hours/month
- **Substrate-block emission:** anti_anchor field updates (last_verified + verification_source); kill ledger entries for anti_anchors that no longer survive verification (rare but expected)
- **Mechanism:** scan `techne/registry/anti_anchors.jsonl`; for each entry where `last_verified` is older than 90 days, re-run citation_audit + spot-check substantive content claim against current literature

### BL-T-031 | Phase 0 | Audit catalog stale-anchor text edits (per Techne 5-15-2026 synopsis move 4)
- **Status:** [done — verified already landed] commit context: synthesis 2026-05-09/2026-05-10/2026-05-11 batches updated the catalog text in-place
- **Dependencies:** none (audit only)
- **Effort:** ~30 min (read + verify)
- **Substrate-block emission:** none (audit)
- **Audit findings:** All 5 named entries (T#1, T#13, T#56, T#92, T#95) carry explicit `(Updated YYYY-MM-DD per ...)` markers with full rewrites matching the Techne 5-15-2026 synopsis §2 recommendations:
  - T#1 ω: now reads `ω < 2.371339 (ADVWXXZ 2024, arXiv:2404.16349; supersedes prior 2.371552 figure)`. Done.
  - T#13 partition rank: full (a)/(b)/(c)/(d) subdivision per Lampert-Moshkovitz Sept 2025 NEGATIVELY-RESOLVED. Done.
  - T#56 Hillar-Lim: corrected to arXiv:1611.01559 per Wave 1 anti-anchor verification (prior arXiv:1605.07532 was wrong). Done.
  - T#92 GCT: full BIP occurrence-obstruction-dead update + Mignon-Ressayre + equivariant-restricted clarification. Done.
  - T#95 Kronecker: Mulmuley PH1 falsified update + Saxl-still-open per Lee 2025 withdrawal. Done.
- **Conclusion:** Catalog text is current. No edit work needed; this BL-T item exists as the audit confirmation.

### BL-T-032 | Phase 0 → Phase 1 | PROVISIONAL marker discipline for vocabulary Layers 1/2/5 (per Ergon feedback 2026-05-15)
- **Status:** pending — coordination with Aporia required
- **Dependencies:** Aporia confirms whether to mark Layer 1 (primitives.md) / Layer 2 (attacks.md) / Layer 5 (composition_rules.md) entries with `_status: provisional` until Arena/kill_ledger evidence accumulates per entry (Ergon's "≥2 instances" discipline)
- **Effort:** ~30 min Techne side IF Aporia adopts the discipline (just adds a per-entry `_status` field to the relevant doctrine docs); larger if it requires schema-level marker on the substrate_block schemas
- **Substrate-block emission:** none (doctrine discipline)
- **Ergon's reasoning** (`feedback_anti_gravitational_well.md` risk): "we define vocabulary that looks neat, train Learner on it, then 'discover' the Learner uses our vocabulary because we trained it to." Layer 4 (anti_anchors) + Layer 3 (patterns) escape this because every entry has empirical anchoring (citation OR observed failure mode); Layers 1/2/5 don't.
- **Coordination ask:** file P3-low ticket to Aporia raising the discipline question + offering Techne side support (schema marker addition if wanted)

### BL-T-033 | Phase 1 | LearnerRecord _vocabulary_v1_action_grammar sidecar (co-design with Ergon BL-E-037)
- **Status:** pending — gated on co-design pass with Ergon; sidecar landing requires no contract change (additive sidecar pattern matches existing `_training_anchor_meta`)
- **Dependencies:** Ergon ships BL-E-037 design (LearnerRecord schema extension); Techne reviews + implements
- **Effort:** ~2-3 hours (~50 LOC schema extension + tests + closure)
- **Substrate-block emission:** none (LearnerRecord shape extension)
- **Per Ergon feedback:** "If the 5-layer typed grammar is supposed to be the Learner's action space, my current schema captures it only awkwardly (chart_id for Layer 1, kill_signature[0] for Layer 2, no slot for Layer 5). A clean sidecar `_vocabulary_v1_action_grammar` (same pattern as `_training_anchor_meta`) would let the grammar tokenize cleanly."
- **Sidecar shape proposal (draft, for Ergon review):** `{layer1_primitive_refs: [str], layer2_attack_refs: [str], layer5_composition_refs: [str], canonical_status_per_ref: {ref: 'provisional'|'canonical'}}`
- **Note:** sidecar is additive on LearnerRecord; existing call sites unaffected; Ergon's existing consumer code unaffected.

### BL-T-010 | Phase 0 | Phase 0 → Phase 1 review + closure ticket
- **Status:** pending — fires at end of week 4 (~2026-06-12)
- **Dependencies:** all Phase 0 backlog items at terminal state (done / gated-and-skipped / explicitly-deferred)
- **Effort:** ~2 hours review + ticket authoring
- **Substrate-block emission:** none (coordination)
- **Output:** Aporia-inbox ticket assessing what landed vs slipped, what Phase 1 needs to start, any Phase 0 prerequisites unmet that require re-planning per roadmap §10

---

## Phase 1 — Continuous attack infrastructure (weeks 5-12, mid-June to mid-August 2026)

Goal: daily attack cycles for all 5 agents. Atlas grows to 100+ problem_cards. Substrate corpus crosses 500 blocks total. Techne mining steady-state ~150-300 mined claims/week.

### BL-T-011 | Phase 1 | kill_ledger samples extractor (6th extractor — sampling design first)
- **Status:** pending — needs sampling design before build
- **Dependencies:** Aporia note 2 from build-spec (ELEVATE high-information kills, SAMPLE brute-force enumeration). Techne writes a brief sampling-policy doc before the extractor.
- **Effort:** ~1 hour sampling design + ~3 hours extractor build = ~4 hours total
- **Substrate-block emission:** mined boundary + frontier_survey claims from kill_ledger entries
- **Sampling rules** (draft): elevate triangulation-grade kills (output of triangulation verifier); near-misses (verifier returns decisive_inconclusive with caveat marking); catalog-disagreements (multiple verifiers disagree). Sample (not en-masse) brute-force-enumeration kills.

### BL-T-012 | Phase 1 | journals/ mining extractor (7th extractor)
- **Status:** pending
- **Dependencies:** BL-T-011 sampling discipline carries forward (journals contain attack-attempt narratives)
- **Effort:** ~3 hours; ~250 LOC
- **Substrate-block emission:** frontier_survey + paradigm_candidate claims; expected ~80-150 latent claims from journal corpus
- **Output target:** `aporia/docs/mined_substrate_blocks/<date>/journals/<category>.jsonl`

### BL-T-013 | Phase 1 | fire_logs/ mining extractor (8th extractor)
- **Status:** pending
- **Dependencies:** none
- **Effort:** ~2-3 hours; ~200 LOC
- **Substrate-block emission:** mostly substrate_self claims (fire logs document substrate behavior); some primitive_proposal candidates
- **Note:** structured `roles/<Agent>/SUBSTRATE_FIRE_LOG_*.md` corpus

### BL-T-014 | Phase 1 | harmonia_memory mining extractor (9th extractor; sandbox-aware)
- **Status:** gated on Sandbox firewall live (Phase 0 Aporia critical path)
- **Dependencies:** `aporia/doctrine/sandbox_protocol.md` shipped + sandbox firewall infrastructure live
- **Effort:** ~3-4 hours including sandbox-marker handling
- **Substrate-block emission:** sandbox::HBR-XXX bridge candidates per the co-design ticket `T-2026-05-15-aporia-to-techne-sandbox-bridge-candidate-co-design-ticket-pre-empting-harmonia-formal-filing`
- **Critical:** must respect sandbox/production firewall; mined bridge candidates are sandbox-only until promoted via asymmetric gate

### BL-T-015 | Phase 1 | whitepapers/ mining extractor (10th extractor — completes 5+ extractors target)
- **Status:** pending
- **Dependencies:** none
- **Effort:** ~2-3 hours; ~200 LOC
- **Substrate-block emission:** primarily frontier_survey claims with high citation density
- **Note:** completes Phase 1 success criterion "Mining pipeline at 5+ extractors" (currently 3 + 2 Phase 0 builds = 5; this is the 10th total)

### BL-T-016 | Phase 1 | Cron shift to bi-hourly (per roadmap §4 Phase 1 acceleration)
- **Status:** pending; gated on mining yield justification
- **Dependencies:** mining pipeline producing >150 claims/week steady-state from BL-T-002/003/011-015
- **Effort:** ~30 min (Windows Task Scheduler reconfig + telemetry update)
- **Substrate-block emission:** none (operational)
- **Decision criteria:** if hourly-cron iterations consistently surface fresh inbox traffic OR fresh mined-batch yields, bi-hourly justified. Otherwise stay hourly.

### BL-T-017 | Phase 1 | Vocabulary-walking substrate-tester probe spec
- **Status:** [substrate-tester owns build] — Techne is informed
- **Dependencies:** per `T-2026-05-15-aporia-to-techne-track2-registration-ack-plus-aa013-backfill-substrate-discipline-finding` proposal: substrate-tester probe walks `aporia/doctrine/substrate_vocabulary/primitives.md` + `techne/registry/anti_anchors.jsonl` checking for naming consistency, missing canonical-registry-entry-vs-vocabulary-doc references (the AA-013 backfill discovery from Track 2)
- **Effort (Techne side):** ~30 min review when substrate-tester ships; flag any false positives or signal-vs-noise concerns
- **Substrate-block emission:** substrate_tester finds (substrate_self claims) — substrate-tester emits, Techne reviews

### BL-T-018 | Phase 1 | Parser-normalizer land if BL-T-004 fires
- **Status:** conditional on BL-T-004 firing
- **Dependencies:** BL-T-004 measurement gate trips (rejection rate >25% after 2 pilots)
- **Effort:** ~2-3 hours if executed
- **Substrate-block emission:** none (parser infrastructure)

### BL-T-019 | Phase 1 | Vocabulary expansion: register Atlas-discovered primitives
- **Status:** continuous cadence during Phase 1
- **Dependencies:** Aporia delivers Atlas-discovered primitive_proposal candidates from problem_card analysis
- **Effort:** ~1 hour per registration, 2-3 registrations/month expected
- **Substrate-block emission:** primitive_proposal blocks; entries appended to `aporia/doctrine/substrate_vocabulary/primitives.md`
- **Process:** Aporia surfaces; Techne validates against existing primitives + HARD-5 discipline; co-author the primitives.md addition + consumer-hook fixture (per the AA-013/TensorRankWitness pattern)

### BL-T-020 | Phase 1 | Phase 1 → Phase 2 review + closure ticket
- **Status:** pending — fires at end of week 12 (~2026-08-14)
- **Dependencies:** Phase 1 backlog items at terminal state
- **Effort:** ~2 hours review + ticket authoring
- **Substrate-block emission:** none (coordination)
- **Output:** Aporia-inbox phase-review ticket per roadmap §10

---

## Phase 2 — Arena MVP (weeks 13-18, September to mid-October 2026)

Goal: 3-role gladiator teams operational on select problems. First adversarial-verification pilots. Atlas-to-Arena pipeline closed end-to-end.

### BL-T-021 | Phase 2 | Arena per-attempt provenance ledger schema
- **Status:** pending
- **Dependencies:** Aporia ships `aporia/doctrine/arena_protocol.md` + per-team specialization spec (Phase 2 Aporia commit)
- **Effort:** ~3-4 hours; new schema file `arena_attempt_v0.json`; iterate as draft per problem_card_v0 pattern
- **Substrate-block emission:** schema only; arena_attempt blocks emitted by Aporia + agents during rounds
- **Required fields proposed:** attempt_id, round_id, role (Scout/Forger/Skeptic), attacking_agent, problem_card_ref, output_summary, output_substrate_block_refs, token_budget_used, falsification_outcome

### BL-T-022 | Phase 2 | Per-role substrate-block emission gate
- **Status:** pending
- **Dependencies:** BL-T-021 schema landed; arena_protocol.md defines roles
- **Effort:** ~2 hours; runner-side enforcement via tier_1_claim_runner.py extension or sister script
- **Substrate-block emission:** none (gate enforcement); ensures every Arena attempt produces ≥1 substrate_block per the roadmap §7 acceleration mechanism
- **Per-role minimum emissions:** Scout produces ≥1 RepresentationShiftWitness candidate or ConceptualAbsenceEntry; Forger produces ≥1 attack vector / kill_ledger entry; Skeptic produces ≥1 anti_anchor candidate or counterexample claim

### BL-T-023 | Phase 2 | Per-role token budget tracking
- **Status:** pending
- **Dependencies:** BL-T-021 schema captures token_budget_used; BL-T-022 emission gate active
- **Effort:** ~1-2 hours; lightweight script summing per-role token usage from arena_attempt blocks; weekly rollup ticket
- **Substrate-block emission:** none (telemetry)

### BL-T-024 | Phase 2 | Substrate-tester wired as Nemesis verifier layer
- **Status:** pending
- **Dependencies:** substrate-tester operational (separate agent's deliverable); Arena runs producing arena_attempt blocks
- **Effort (Techne side):** ~2 hours wiring + 30 min review of substrate-tester probe schedule
- **Substrate-block emission:** substrate-tester emits; Techne provides the verifier-registry slot (similar to existing 7-verifier pattern in `tier_1_claim_runner.py`)

### BL-T-025 | Phase 2 | Arena infrastructure validation pass
- **Status:** pending — fires after first 2-team-of-3 round
- **Dependencies:** first Arena round completes; arena_attempt blocks emitted; per-role gate exercised
- **Effort:** ~2 hours; review whether emission gates fire correctly, token budgets track, provenance is complete
- **Substrate-block emission:** none (validation)
- **Output:** infrastructure-validation ticket to Aporia summarizing gaps + needed adjustments

### BL-T-026 | Phase 2 → Phase 3 review + closure ticket
- **Status:** pending — fires at end of week 18 (~2026-09-25)
- **Effort:** ~2 hours
- **Substrate-block emission:** none (coordination)

---

## Phase 3 — Scale + automation (months 5-8, November 2026 to February 2027)

Goal: 200+ problem_cards. Mining pipeline at 10-12 extractors covering entire 441-file corpus. Vocabulary expansion to 50+ new primitives. Substrate corpus reaches Learner v1.0 inclusion threshold.

### BL-T-027 | Phase 3 | Mining pipeline expansion to 10-12 extractors covering 441-file corpus
- **Status:** pending — completes the steady-state mining surface
- **Dependencies:** Phase 1 + Phase 2 extractors landed (BL-T-002, 003, 011, 012, 013, 014, 015 = 7 extractors); 3-5 more needed for full coverage
- **Effort:** ~10-15 hours total; spread across 4 months; ~3-4 hours per new extractor
- **Substrate-block emission:** mined claim blocks across all categories
- **Candidate sources for the 3-5 new extractors:** roles/<Agent>/RESPONSIBILITIES.md walkers; aporia/mathematics/lesser_known_open_problems.md walker; pivot/*.md design-doc walker; cartography/ corpus walker; older deep_research_batch_* dirs (currently we mine 2026-05-13 only — Phase 3 should sweep 2026-04-* and earlier)

### BL-T-028 | Phase 3 | Vocabulary expansion: 50+ new primitive registrations
- **Status:** pending — continuous cadence; targets 6-8 registrations/month for 4 months
- **Dependencies:** Atlas-driven attack pipeline producing primitive_proposal candidates at sufficient rate; Aporia coordinates
- **Effort:** ~1 hour per registration (consistent with BL-T-019); ~50-60 hours total across the phase
- **Substrate-block emission:** primitive_proposal + canonical primitive entries in primitives.md + consumer-hook fixtures per the TensorRankWitness pattern
- **Quality discipline:** every new primitive gets a substrate-tester probe and a consumer-hook fixture before being declared canonical

### BL-T-029 | Phase 3 | Schema evolution from attack-pipeline-surfaced needs
- **Status:** continuous; fires whenever attack pipeline surfaces a need not covered by existing 7 production schemas + problem_card_v1
- **Dependencies:** Aporia files schema-need ticket (per the recurring-pattern model used for sandbox_bridge_candidate co-design)
- **Effort:** highly variable; bound at ~5 hours per new schema; larger asks require Aporia adjudication first
- **Substrate-block emission:** new schema files when authorized
- **Authorization gate:** any schema beyond the 8 currently-authorized (7 production + 1 problem_card draft) requires explicit Aporia ticket per stand-down posture

### BL-T-030 | Phase 3 → Phase 4 review + closure ticket
- **Status:** pending — fires at end of month 8 (~2027-01-15)
- **Effort:** ~3 hours; deeper review than prior phase boundaries since Phase 4 is steady-state
- **Substrate-block emission:** none (coordination)
- **Output:** comprehensive review of Phase 3 outcomes + Phase 4 cadence proposals + any roadmap revision recommendations per roadmap §10 (M4 outside-review at phase boundaries)

---

## Cross-phase: Schema-stability gates per phase boundary

Each phase boundary requires verification that schema changes during the phase haven't broken downstream consumers. The schema-stability-gate pattern:

- **Phase 0 boundary:** verify all 7 production schemas + problem_card_v0/v1 + sandbox_bridge_candidate (if shipped) parse cleanly via `validate_substrate_blocks.py`. Run `prometheus_math/tests/test_substrate_generation_tier_1.py` + extractor test suites; must pass 100%.
- **Phase 1 boundary:** add Phase 1 mining-extractor outputs to the cross-validation set. Verify schema-conformant emission across all extractors.
- **Phase 2 boundary:** add arena_attempt schema validation to the gate. Verify per-role emission gate enforces invariants.
- **Phase 3 boundary:** verify all 10+ extractors + all schema additions still pass cross-validation. This is the canonical Phase 4 entry checkpoint.

Each gate fires as part of the phase-boundary review ticket (BL-T-010, BL-T-020, BL-T-026, BL-T-030).

---

## Closure ticket cadence

For each completed BL-T-NNN item: append a brief closure ticket to `aporia/meta/queue/aporia_inbox.jsonl` in the same JSONL shape as existing tickets. Pattern: `T-<YYYY-MM-DD>-techne-to-aporia-bl-t-<NNN>-<short-title>`. Reference the BL-T id explicitly so the cross-link is queryable.

For gated/conditional items (BL-T-004, BL-T-005, BL-T-006, BL-T-014, BL-T-016, BL-T-017, BL-T-018, BL-T-024): file a brief P3-low ticket when the gate condition triggers; full closure ticket on completion.

For phase-boundary review tickets (BL-T-010, BL-T-020, BL-T-026, BL-T-030): P1-high; deliberately heavier so Aporia + (M4 outside review) catch any drift from the roadmap.

---

## Vigilance flags (Techne-specific echoes of roadmap §9)

- **HARD-2 risk on backlog itself.** A backlog with 30 items is the same kind of artifact the roadmap warns about. Behavior delta required at every BL-T item; if BL-T-002 + BL-T-003 don't ship in Phase 0, the Phase-1 mining cadence won't be supportable. The backlog is wrong, not the roadmap.
- **Cron drift risk.** If the :17 hourly cron starts firing into nothing meaningful for >2 weeks, drop to bi-hourly per BL-T-016. Don't keep low-yield iterations alive out of habit.
- **Schema-evolution scope-creep.** Items beyond BL-T-005, BL-T-006, BL-T-021, BL-T-029 invite ad-hoc schema additions. File P3-low ticket to Aporia first; don't autonomously expand.
- **Mining yield versus quality trade-off.** Phase 1's "150-300 claims/week" target is volume; but per Aporia note 2, ELEVATE high-information kills + SAMPLE brute-force noise. Quality discipline is the rate-limiter, not throughput.
