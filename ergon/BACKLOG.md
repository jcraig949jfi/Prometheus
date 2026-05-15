# Ergon BACKLOG — Phase 0 → Phase 3 work items

**Filed:** 2026-05-15 by Ergon (Learner owner)
**Authority:** `pivot/atlas_continuous_attack_roadmap_2026-05-15.md` first roadmap-as-work assignment for Ergon. Per-agent BACKLOG seeded per roadmap §5 specialization.
**Format per item:** `BL-E-NNN | Phase | Title` + Dependencies + Estimated effort + Substrate-block emission expected.
**Phase boundaries:** Phase 0 = weeks 1-4 (mid-May → mid-June 2026); Phase 1 = weeks 5-12 (mid-June → mid-August 2026); Phase 2 = weeks 13-18 (September → mid-October 2026); Phase 3 = months 5-8 (November 2026 → February 2027).
**Capstone:** Phase 3 first substrate-grade Learner training run (BL-E-030).
**Stand-down posture preserved throughout:** no LoRA training kickoff outside Phase 3 framework; no Mahler; no writeable substrate; no API budget escalation; no kernel contract changes. If any item drifts toward a hard-stop class, file ticket and skip rather than push.

Pull-before-pick discipline (per multi-instance coordination doctrine): always `git pull --ff-only` and check `ergon/STATUS.md` before claiming a backlog item.

Effort scale: **S** = 1 session (~1-4 hours), **M** = 1-2 sessions (~4-12 hours), **L** = 3-5 sessions (~1-2 days wall-clock spread across the week), **XL** = ~1+ week (training-experiment design docs, full training run prep).

---

## Phase 0 (weeks 1-4) — Foundation hardening

### BL-E-001 | Phase 0 | Apply AA index to LearnerRecord sidecars (tagging step)
- **Dependencies:** AA index at `ergon/learner/corpus/anti_anchor_index/index.json` (built 2026-05-15). Existing LearnerRecord JSONL at `corpus/v1_0_tier_pending/<date>/under_threshold/`.
- **Estimated effort:** M.
- **Substrate-block emission expected:** Per-existing-LearnerRecord re-emission with `_anti_anchor_applicability: [AA-NNN, ...]` sidecar field; no new substrate_blocks. Enables Phase 1 corpus assembly to inject AA-NNN false_form as known_kill decoys.

### BL-E-002 | Phase 0 | Add BS-NNN regex backfill for AA-014/015/016 P-vs-NP topics
- **Dependencies:** AA index (BL-E-001 prereq for the tagging-pipeline shape).
- **Estimated effort:** S.
- **Substrate-block emission expected:** None direct. Updates `BS_TOPIC_REGEXES` in `ingest_training_anchors.py:115-122` to add Baker-Gill-Solovay 1975 / Razborov-Rudich 1997 / Aaronson-Wigderson 2008 regex patterns so the regex fallback path matches when v1.0.0 emitters don't supply explicit `bs_coverage`.

### BL-E-003 | Phase 0 | Update training_anchor_ingestion_spec.md with stratifier Q5/Q6 adjudication
- **Dependencies:** stratifier shipped (2026-05-15). `source_report_stratification_spec.md` §5 currently lists 7 questions as "open"; needs marking as "answered per Aporia adjudication 2026-05-15."
- **Estimated effort:** S.
- **Substrate-block emission expected:** None direct (doc-only).

### BL-E-004 | Phase 0 | Pre-ingest schema validator for staged_substrate_blocks
- **Dependencies:** Existing `ingest_training_anchors.py`. Substrate-block schemas at `techne/contracts/substrate_block_schemas/`.
- **Estimated effort:** M.
- **Substrate-block emission expected:** None direct. Catches wrapped-vs-flat shape mismatch and schema-field violations BEFORE the ingester's `validate_block` runs, giving a clearer error message than "9 missing required fields." Reduces coordination-round-trip cost when Aporia/Techne staged shape drifts.

### BL-E-005 | Phase 0 | ingest_training_anchors.py: per-batch metrics rollup
- **Dependencies:** Existing ingester + ingest_summary template.
- **Estimated effort:** S.
- **Substrate-block emission expected:** Augments existing `ingest_summary_<run_id>.json` output with cumulative-across-batches counters (running totals of trust_tier mix, AA-NNN coverage, domain distribution). Enables Phase 1 "are we approaching v1.0 inclusion threshold?" measurement.

### BL-E-006 | Phase 0 | Ergon daily cron at :47 (per roadmap §7)
- **Dependencies:** Cron infrastructure (Techne :17 cron is the model). Ergon stand-down posture; the cron runs read-only daily-cycle work, not LoRA training kickoff.
- **Estimated effort:** S.
- **Substrate-block emission expected:** Per-cron-fire status note in `ergon/STATUS.md` Learner Branch + closure ticket if new substrate blocks landed in `staged_substrate_blocks/<today>/`.

### BL-E-007 | Phase 0 | Sandbox-firewall consumer notes (Harmonia integration prep)
- **Dependencies:** Aporia's `aporia/doctrine/sandbox_protocol.md` (per roadmap §4 Phase 0 Aporia commitment). Harmonia's `RepresentationShiftWitness` block format (TBD by Harmonia / Aporia).
- **Estimated effort:** S.
- **Substrate-block emission expected:** None direct. Documents Ergon's downstream-consumer expectations for the sandboxed RepresentationShiftWitness payload so the firewall-to-corpus pipeline is shape-aligned by the time Harmonia produces first records (Phase 1 mid-July 2026).

---

## Phase 1 (weeks 5-12) — Continuous attack infrastructure

### BL-E-008 | Phase 1 | Ingest support for problem_card v1.0 block_type
- **Dependencies:** Techne promotes problem_card v0 → v1.0 (per roadmap §4 Phase 0 Techne commitment). Aporia ships 10-card Atlas MVP smoke pass.
- **Estimated effort:** M.
- **Substrate-block emission expected:** Per-problem_card LearnerRecord with hardness_signature + field_invariants_used surfaced into sidecar. Enables Learner-routing-head to train on hardness-class targets.

### BL-E-009 | Phase 1 | Ingest support for mining-pipeline emit format
- **Dependencies:** Techne ships mining pipeline (5+ extractors per roadmap §4 Phase 0 Techne commitment). Format spec from Techne's `claim_mining_extractor_v0.1` output.
- **Estimated effort:** M.
- **Substrate-block emission expected:** Per-mined-claim LearnerRecord ingested through extended `ingest_training_anchors.py` (or a sibling script `ingest_mined_claims.py` if the schemas diverge enough).

### BL-E-010 | Phase 1 | Stratification: ship `strata_classifier=external_function`
- **Dependencies:** stratify_source_report.py shipped (2026-05-15). Aporia/Techne registered classifier-function path convention (e.g. `aporia/calibration/classifiers/<source>_classifier.py:classify`).
- **Estimated effort:** M.
- **Substrate-block emission expected:** None direct. Unlocks per-source stratification by computed classifier (e.g. parse paper title for sub-domain) rather than requiring inline strata field on every candidate.

### BL-E-011 | Phase 1 | Stratification: ship `strata_classifier=enum`
- **Dependencies:** BL-E-010 (similar pattern). Use case: stratify by exact match against a fixed enum list (simpler than external_function but more flexible than pure inline).
- **Estimated effort:** S.
- **Substrate-block emission expected:** None direct.

### BL-E-012 | Phase 1 | Promotion criteria: under_threshold/ → tier_pending/
- **Dependencies:** Cumulative ≥5 records per anchor + ≥2 high-trust per anchor across the v1_0_tier_pending date-batches.
- **Estimated effort:** M.
- **Substrate-block emission expected:** Per-promotion LearnerRecord re-emit (now at `tier_pending/<anchor_id>/`) with provenance trail noting which batch(es) contributed. Promoted records become eligible for corpus assembly.

### BL-E-013 | Phase 1 | Trust-tier mix policy: per-condition sample-weight at corpus assembly
- **Dependencies:** BL-E-012 (need tier_pending/ records to assemble). Pilot LoRA design §2.2 weighting policy.
- **Estimated effort:** M.
- **Substrate-block emission expected:** None direct. Implements §2.2 trust-tier weighting (decidable=1.0×, conditional=0.5×, unknown=excluded) as a corpus-assembly step. Output is a weighted-corpus JSONL ready for training (no training run yet).

### BL-E-014 | Phase 1 | First training-experiment design doc (Phase 1 quarterly)
- **Dependencies:** Tier_pending/ records (BL-E-012). Sufficient corpus volume for a meaningful design exercise (~50+ records).
- **Estimated effort:** XL (~1 week wall-clock for the design doc + Aporia review round).
- **Substrate-block emission expected:** New `ergon/learner/v1_0_plans/training_experiment_design_2026_phase1.md` covering the null-control LoRA exercise. Design doc only; no training run.

### BL-E-015 | Phase 1 | tier_pending/ → tier_validated/ promotion gate (substrate-tester audit)
- **Dependencies:** BL-E-012 (tier_pending/ shape exists). Substrate-tester audit infrastructure (cross-agent coordination with Techne / substrate-tester role).
- **Estimated effort:** L.
- **Substrate-block emission expected:** Per-promotion gate-passed LearnerRecord at `tier_validated/<anchor_id>/`. Substrate-tester audit findings become anti_anchor candidates if the gate fails.

### BL-E-016 | Phase 1 | AA-applicability tagging at LearnerRecord re-emission
- **Dependencies:** BL-E-001 (AA tagging step). Used at corpus-assembly time per spec §1.4.
- **Estimated effort:** S.
- **Substrate-block emission expected:** Re-emitted LearnerRecord JSONL with `_anti_anchor_applicability` sidecar.

### BL-E-017 | Phase 1 | Per-domain corpus health dashboard
- **Dependencies:** Cumulative LearnerRecord JSONL across tier_pending + tier_validated.
- **Estimated effort:** M.
- **Substrate-block emission expected:** None direct. Builds an aggregation report (by domain × trust_tier × outcome_class × AA-coverage) that Aporia can read at weekly review per roadmap §5.

---

## Phase 2 (weeks 13-18) — Arena MVP

### BL-E-018 | Phase 2 | Arena round output ingest path
- **Dependencies:** Aporia ships `aporia/doctrine/arena_protocol.md` (roadmap §4 Phase 2). Techne lands per-attempt provenance ledger format. First 2-team-of-3 weekend run completes (roadmap §4 Phase 2 Aporia commitment).
- **Estimated effort:** L.
- **Substrate-block emission expected:** Per-attempt LearnerRecord stream with Scout / Forger / Skeptic role-tagged emissions feeding the unified corpus. Per-role substrate-block emission gate enforced.

### BL-E-019 | Phase 2 | Per-role substrate-block emission gate (Scout/Forger/Skeptic)
- **Dependencies:** BL-E-018 (Arena ingest path exists). Role-spec from Aporia per-team specialization doc.
- **Estimated effort:** M.
- **Substrate-block emission expected:** None direct. Enforces that every Arena attempt emits at least one substrate_block per the role's expected block-type distribution (Scout→training_anchor / catalog_edit; Forger→primitive_proposal / composition_rule; Skeptic→anti_anchor / kill_ledger entries).

### BL-E-020 | Phase 2 | First attempt at Learner-routing-head training run (feasibility)
- **Dependencies:** Phase 1 corpus volume (BL-E-012 promoted records). HARD-GATED: this is the first training run in the roadmap. Goes through Aporia adjudication + James authorization. Falls under Phase 2 → Phase 3 boundary; treat as feasibility-only, not full training.
- **Estimated effort:** XL.
- **Substrate-block emission expected:** Training-run artifacts (loss curves, eval metrics, checkpoint hashes) + post-training corpus audit pinning what was learned vs. what wasn't. NOT a full v1.0 training run; minimal feasibility experiment.

### BL-E-021 | Phase 2 | Second training-experiment design doc (Phase 2 quarterly)
- **Dependencies:** BL-E-020 outcome.
- **Estimated effort:** XL.
- **Substrate-block emission expected:** `ergon/learner/v1_0_plans/training_experiment_design_2026_phase2.md` covering the routing-head feasibility outcome + design adjustments for the Phase 3 full training run.

### BL-E-022 | Phase 2 | Stratification: multi-rule composition (Tier-2)
- **Dependencies:** Q7 adjudication 2026-05-15 deferred this to Tier-2. Triggered when a real source needs subdivided stratification (e.g. LMFDB EC simultaneously by rank-stratum AND Sha-stratum).
- **Estimated effort:** M.
- **Substrate-block emission expected:** None direct. Stratifier extension to accept `rules: List[Dict]` instead of single `rule: Dict`, with composition semantics (intersection-of-strata, or union, per registered policy).

### BL-E-023 | Phase 2 | Weekly training-experiment summary in STATUS.md
- **Dependencies:** Phase 1+ weekly cadence per roadmap §5 Ergon commitment.
- **Estimated effort:** S (per week, recurring).
- **Substrate-block emission expected:** STATUS.md update + closure ticket to Aporia weekly digest.

### BL-E-024 | Phase 2 | AA-013 fixture promotion to eval_run status
- **Dependencies:** BL-E-020 (Learner head exists). AA-013 fixture v0.2 from 2026-05-14 + the 6 test cases (1 positive + 3 contrapositive + 2 ambiguous).
- **Estimated effort:** S.
- **Substrate-block emission expected:** behavior_delta_status advances from `fixture_created` to `eval_run` once the smoke-test executes against the routing head. If the head passes all 6 cases per the fixture's expectation, status advances to `eval_passed`.

### BL-E-025 | Phase 2 | corpus_inclusion_threshold dial — Phase 1 actuals review
- **Dependencies:** Phase 1 corpus accumulation actuals + Phase 1 training-experiment design (BL-E-014) lessons.
- **Estimated effort:** S.
- **Substrate-block emission expected:** None direct. Documents whether the ≥5-total / ≥2-high-trust threshold needs adjustment based on Phase 1 actual yield. May tighten OR loosen depending on what Phase 1 surfaces.

---

## Phase 3 (months 5-8) — Scale + automation; first training run

### BL-E-026 | Phase 3 | Third training-experiment design doc (Phase 3 quarterly)
- **Dependencies:** Phase 2 lessons (BL-E-020 + BL-E-021). Phase 3 month-5 onset trigger.
- **Estimated effort:** XL.
- **Substrate-block emission expected:** `ergon/learner/v1_0_plans/training_experiment_design_2026_phase3.md` — the full substrate-grade run design.

### BL-E-027 | Phase 3 | Corpus v1.0 inclusion threshold met (verification gate)
- **Dependencies:** Phase 1 + Phase 2 cumulative corpus volume.
- **Estimated effort:** M (verification + corpus audit, not new code).
- **Substrate-block emission expected:** None direct. Pre-training gate: confirm ≥1000 high-trust blocks across the 6 corpus sources (substrate-shaped pipeline / Atlas problem_cards / mined extracts / Tier-1 Lehmer / AA index decoys / Harmonia bridges). If not met, training run defers to BL-E-030 successor and Phase 3 milestone slips.

### BL-E-028 | Phase 3 | Per-condition trust-tier mix policy adjudication for first training run
- **Dependencies:** BL-E-027 (threshold met). Pilot LoRA design §2.2 baseline policy.
- **Estimated effort:** M.
- **Substrate-block emission expected:** None direct. Updated trust-tier mix policy (likely tightens decidable-vs-conditional weighting based on Phase 1 + Phase 2 evidence) with closure ticket to Aporia for adjudication.

### BL-E-029 | Phase 3 | Pre-training corpus snapshot freeze
- **Dependencies:** BL-E-027 + BL-E-028.
- **Estimated effort:** S.
- **Substrate-block emission expected:** Frozen corpus snapshot at `ergon/learner/corpus/v1_0_assembled/<freeze_date>/training_corpus.jsonl` with SHA256 manifest. Reproducibility anchor for the first training run.

### BL-E-030 | Phase 3 | First substrate-grade Learner training run (CAPSTONE)
- **Dependencies:** BL-E-026 (design doc adjudicated) + BL-E-027 (threshold met) + BL-E-028 (trust-tier policy locked) + BL-E-029 (corpus frozen). HARD-GATED on James authorization for compute scope (per roadmap §3 — Phase 3 month 5 at earliest).
- **Estimated effort:** XL.
- **Substrate-block emission expected:** Training-run artifacts (checkpoints, loss curves, per-condition eval metrics across the 4-condition matrix from pilot LoRA design §2.1). Post-training: behavior_delta_status advances toward `eval_run` / `eval_passed` for AA-013 + all fixtures created by then.

### BL-E-031 | Phase 3 | Routing-head accuracy baseline on held-out corpus
- **Dependencies:** BL-E-030 trained checkpoint.
- **Estimated effort:** M.
- **Substrate-block emission expected:** Eval-set report covering the 20%-held-out portion of corpus (grouped by `episode_id` per pilot LoRA design §2.2). Baseline accuracy on trust-tier prediction + outcome_class prediction.

### BL-E-032 | Phase 3 | Post-training corpus audit: AA-respect vs AA-violation
- **Dependencies:** BL-E-031.
- **Estimated effort:** M.
- **Substrate-block emission expected:** Per-AA report showing whether the trained Learner correctly rejects each AA-NNN's false_form on held-out + targeted probes. AAs the Learner violates become high-priority new anti_anchor candidates (per existing pattern: every overreach surfaces a new pin).

### BL-E-033 | Phase 3 | Learner v1.1 design doc (post-v1.0 outcome)
- **Dependencies:** BL-E-030 + BL-E-031 + BL-E-032 outcomes.
- **Estimated effort:** XL.
- **Substrate-block emission expected:** `ergon/learner/v1_1_plans/v1_1_design.md` covering the revisions to the 4-condition matrix, eval set, metrics, and trust-tier weighting based on Phase 3 evidence. Sets up Phase 4 steady-state cadence.

---

## Cross-cutting / open

### BL-E-034 | Cross-cutting | Memory entry: stratification design adjudication 2026-05-15
- **Dependencies:** None.
- **Estimated effort:** S.
- **Substrate-block emission expected:** None direct. Project memory entry recording the Q5/Q6 adjudication outcome so future sessions can reference the design without re-deriving (anti-narrative-construction, narrow specific memory entry).

---

## Notes on this backlog

- **Total items:** 34 (BL-E-001 through BL-E-034). Slight over James's "~30 items" — kept all items because each is a discrete unit of work with clear dependencies. Trim list is BL-E-002 (regex backfill) or BL-E-017 (corpus dashboard) if a strict 30-item cap is needed; both are nice-to-have rather than load-bearing.
- **Phase 0 / Phase 1 weight:** ~17 items pre-Phase-2 vs ~17 items in Phase 2-3. That's intentional: Phase 0-1 is where Ergon's infrastructure has to mature before the Arena lands; Phase 2-3 is bigger-scope but fewer items (each is XL).
- **Training-run gating:** BL-E-020 (Phase 2 feasibility) and BL-E-030 (Phase 3 capstone) are the only items that touch actual training. Both are HARD-GATED on James authorization per the stand-down posture. No item kickstarts training implicitly.
- **Per-item closure pattern:** when an item completes, file a brief closure ticket to `aporia/meta/queue/aporia_inbox.jsonl` referencing the `BL-E-NNN` ID. The backlog itself is the durable record; the closure ticket is the per-cycle behavior delta.
- **Re-prioritization:** James / Aporia can re-order at any phase boundary. The roadmap §9 explicitly says "if Phase 0 doesn't produce, the plan is wrong" — the backlog inherits that discipline.

---

*— Ergon, 2026-05-15, Phase 0 first roadmap-as-work assignment.*
