# Techne Changelog

All notable changes to the Techne arsenal and substrate-tier scaffolding are
recorded here. Per-tool versioning lives in `inventory.json` (each tool now
carries its own `version` field, starting at `1.0.0`). Substrate-tier schema
versioning is tracked in this file and in `contracts/substrate_tier_schema.md`.

Versioning convention:
- Top-level `inventory.json` schema version is an integer (`3`, `4`, ...). It
  bumps when the registry schema changes.
- Per-tool `version` is semver (`MAJOR.MINOR.PATCH`), starting at `1.0.0`.
- Techne release lines (`v3.x`, `v4.x`) are semver and are recorded here.

---

## v3.2.0 (minor) - 2026-05-13

Claim-stack pipeline ships. Adds the 7th substrate_block schema (`claim_v1`)
plus a Tier-1 claim runner that routes claims through verifier dispatch and
emits LearnerRecord output. Per `pivot/claim_stack_design_2026-05-11.md` +
Aporia adjudication 2026-05-12 (Mods 1+2 applied) + Track 1 prompt 2026-05-13
(three carry-through fields added).

### Added

- **`techne/contracts/substrate_block_schemas/claim_v1.json`** — 7th
  substrate_block schema. Fields: `_schema_version`, `id` (CLAIM-<prefix>-NNNNN
  pattern, uppercase prefix allowed for catalog refs), `claim_category`
  (frontier_survey/calibration/boundary/substrate_self/other), `claim_text`
  (>=20 chars), `expected_verifier_primary` + optional fallback (7-verifier
  enum), `expected_verdict` (survived/falsified/open/conditional),
  `ground_truth_source` (arXiv ID, DOI, or free-form via anyOf),
  `trust_tier`, `source_report`. Optional: `parent_block`, `paired_claim_id`,
  `prompt_template`, `expected_answer_shape`, `verifier_args`,
  `stratification_rule`, `caveats`. allOf: conditional verdict requires
  caveats; calibration category requires prompt_template. Three embedded
  examples all validate.
- **`techne/contracts/substrate_block_schemas/_common_definitions.json`** —
  `sourceReportRef.maxLength` bumped 120 → 400 (Aporia Mod 1). Carries mined
  provenance descriptively without adding a new schema field.
- **`prometheus_math/substrate_generation/learner_enrichment.py`** —
  `VERIFIER_OUTCOME_CLASSES` enum (5 values) per Aporia Mod 2. Splits real
  Learner signal ("verifier ran cleanly and returned inconclusive") from
  missing data ("verifier failed to run"). Four new Optional fields on
  `LearnerRecord`: `verifier_outcome_class` (Mod 2), `claim_id`,
  `claim_category`, `actual_verdict` (Track 1 2026-05-13). All default None
  so Tier-0 brute-force callsites stay backward-compatible.
- **`prometheus_math/substrate_generation/tier_1_claim_runner.py`** — new,
  ~400 LOC. Verifier dispatch wrapper with transient-vs-permanent retry
  discipline (`TimeoutError`/`ConnectionError`/5xx `HTTPError` = transient,
  retried once; everything else permanent). Seven verifier slots in
  `VERIFIER_REGISTRY` all Day-1 stubbed. `run_claim()` routes through primary
  + optional fallback. `run_claim_batch()` loads JSONL, enforces quality
  Rules A/B/C, emits run summary with health flags. CLI entrypoint.
- **`aporia/scripts/validate_substrate_blocks.py`** — `claim_v1` wired into
  schema registry.
- **`aporia/scripts/parse_substrate_blocks.py`** — `claim` added to
  `KNOWN_BLOCK_TYPES`.
- **`prometheus_math/tests/test_substrate_generation_tier_1.py`** — +29
  claim-stack tests (65 total, all pass in 13s).

### Smoke results

- Aporia's 20-claim starter batch validates 17/20. 3 calibration claims fail
  `prompt_template` requirement (citation/catalog-shaped, not Q&A-shaped);
  finding filed as
  `T-2026-05-13-techne-to-aporia-claim-stack-starter-batch-divergence`.
- End-to-end on the 17 valid claims: 17ms wall-clock, all dispatch through
  stubs as expected, every LearnerRecord carries the new four fields.

### Design-time bugs caught at smoke

- `ground_truth_source` `oneOf` → `anyOf` (arXiv strings match both branches).
- `id` pattern widened `[a-z]` → `[a-zA-Z]` in the prefix segment so catalog
  refs (`boundary-T4`) work.

### Next (Day 2-3)

Wire 4 highest-leverage verifiers (citation_audit / catalog_lookup /
mpmath_compute / substrate_self_check) on top of Day-1 stubs.

---

## v3.1.1 (patch) - 2026-05-13

Backwards-compatible patch to `training_anchor_v1.json` per Aporia approval
ticket `T-2026-05-11-aporia-to-techne-bs_coverage-schema-approved-as-v1.1`.

### Changed

- **`training_anchor_v1.json`** `_schema_version`: `const "1.0.0"` →
  `enum ["1.0.0", "1.1.0"]`. Existing emitters at v1.0.0 continue to validate
  unchanged.
- **`training_anchor_v1.json`** adds optional `bs_coverage` field
  (`Array[string]`, items pattern `^BS-\d{3,5}$`, uniqueItems). Per Ergon's
  `training_anchor_ingestion_spec.md` §3.1 + §5.1 Gap 1: explicit blind-spot
  links replace regex-heuristic inference of BS-NNN from
  prompt_template/caveats/source/dataset_source. Empty list and absent field
  are both legal; absent means Ergon's `derive_bs_coverage` falls back to
  regex heuristic.
- **`training_anchor_v1.json`** `source` field `oneOf` → `anyOf`. Same fix
  pattern as claim_v1.json: arXiv IDs and DOIs validate against both the
  structured citation pattern and the free-form fallback, and downstream
  consumers examine the string directly; no exclusivity needed. Caught when
  the v1.1.0 worked example (Cohen 1963 CH-independence anchor with DOI
  `10.1073/pnas.50.6.1143`) failed to validate against `oneOf`.
- Added a second embedded example (`anchor-set_theory-001` at v1.1.0)
  demonstrating the new field with `bs_coverage: ["BS-001"]`.

### Coordination

Filed `T-2026-05-13-techne-to-aporia-and-ergon-training_anchor-v1.1-ready` to
both inboxes; Ergon's `ingest_training_anchors.py` switches from regex
heuristic to explicit field consumption when v1.1 is detected.

---

## v3.1.0 (minor) - 2026-05-10

Scaffolding-only minor release. No tool interfaces changed; no substrate-tier
primitives registered. Lays the groundwork for v4.0 Wave 1.

### Added

- **Per-primitive versioning** in `inventory.json`. All 25 existing tools
  backfilled at `version: "1.0.0"`. No version numbers bumped; this is purely
  additive. No tool interfaces changed.
- Top-level `inventory.json` `version` bumped from `3` to `4` to mark schema
  change. New explicit `schema_version: "4.0"` field added for forward-clarity.
  New `schema_notes` field documents the change inline.
- `contracts/substrate_tier_schema.md` - defines Tier-A++, Tier-B, Tier-C,
  Tier-D, Tier-E. Required fields per tier (`name`, `version`, `parent_class`,
  `subtypes`, `composition_eligibility`, `anti_anchor_pins`, `source_reports`,
  `source_citations`). Composition-eligibility flags (Tier-B + Tier-D
  REQUIRED, Tier-B + Tier-E REQUIRED for GCT-flavour). Contract-change-window
  protocol (frozen-interface doctrine still applies inside windows; window is
  the controlled break). Source: synthesis sections 3 and 8.
- `registry/anti_anchors.jsonl` - 10 seed entries (`AA-001` through `AA-010`)
  drawn verbatim from synthesis section 4. Format:
  `{id, name, false_form, true_form, citation, last_verified, source_report}`.
  Covers GCT_OCCURRENCE_DEAD, ZAUNER_FALSE_ANCHOR, HILLAR_LIM resolved-not-open,
  SAXL T#99 resolved-not-open, CACTUS_BARRIER_6M_MINUS_4, LUCCA_ATTRIBUTION,
  TENSOR_TYPE2_NOT_SQRT_LOG_D, EQUIVARIANT_EXPONENTIAL_RESTRICTED,
  BORDER_CACTUS_DISTINCT_FIFTH_RANK, TYPE2_FIVE_REGION_RARE.
- `registry/compositions.jsonl` - 7 seed entries. 2 confirmed
  (`C-001` Tier-B x Tier-D BorderRank x PhaseTransition from T#73 fire #43;
  `C-002` Tier-B x Tier-D BorderRank x GenericityAE from T#40 fire #45) and
  5 future-candidate compositions (`C-003` Tier-B x Tier-E GCT,
  `C-004` Tier-A++ x Tier-B TensorNetwork x BorderRank,
  `C-005` Tier-C x Tier-B Defectivity x Waring,
  `C-006` Tier-D x Tier-D RandomTensor x PhaseTransition,
  `C-007` Tier-E x Tier-E KroneckerInvariant x PartitionObject) marked
  `confirmed: false` and gated on Wave 1-4 registrations.
- This `CHANGELOG.md`.

### Changed

- `inventory.json` `updated` field moved from `2026-04-22` to `2026-05-10`.

### Not changed (explicitly preserved)

- All 25 tool interfaces. Frozen-interface doctrine intact.
- Tool ordering in `inventory.json`.
- `stats` block contents and the `notes` field.
- `forged_date`, `tested`, `test_source`, `known_issues`, `dependencies`,
  `also`, `optional`, `fulfilled_request`, `fulfilled_date`, `tier`, `interface`,
  `file` fields per tool.

### Foreshadowed for v4.0 (next contract-change window)

Per synthesis section 8, v4.0 Wave 1 will register the first three
substrate-tier primitives. None of these are registered in v3.1.0; this is
forward-looking documentation only:

1. `TensorNetwork` + `ContractionOrderWitness` (Tier-A++; T#84). Foundational
   HARD-3 primitive; nothing depends on it but everything will.
2. `CactusRankWitness` (Tier-B; T#19). Pilot for Tier-B contract change -
   purely combinatorial, no degeneration sequence, no NP-hardness reduction.
3. `RankZooSignature` (Tier-A++; T#13). Tracks distinct rank coordinates
   `(R, R-bar, sr, cr, cr-bar, R_partition, R_analytic, R_geometric,
   R_strength, R_slice, ...)` as a single named tuple per tensor.

Waves 2 (Tier-B cluster), 3 (Tier-D + cross-tier composition ratification), 4
(Tier-E + GCT cluster), and 5 (paradigm-taxonomy work) are scoped in synthesis
section 8 and are NOT part of v3.1.0 or v4.0 Wave 1.

### Source

`aporia/docs/tensor_priority_synthesis_2026-05-09.md`, sections 3, 4, 5, 6, 8.
18-report tensor-priority deep-research batch.
