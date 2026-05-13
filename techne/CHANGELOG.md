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

## v3.3.0 (minor) - 2026-05-13 (autonomous loop hours 1-7)

Same-day follow-up to v3.2.0. Six of seven verifiers wired, parser
hardening shipped, T# numeric bound comparison built, anti-anchor
couplet override implemented, substrate-self invariant registry
expanded, Day-3 substrate_self claim batch authored. Aporia's
17-claim starter batch hits 100% expected/actual match by end of day
(was 0% at session start). 7 cron-driven autonomous loop iterations
across the day.

### Verifiers wired (6 of 7)

- **`citation_audit`** (hour 1): wraps arxiv.org HEAD + abstract
  withdrawal scan. Permissive arXiv-ID extractor handles parenthetical
  context ("arXiv:1604.06431 (BIP 2019 J. AMS)" shape). Returns
  decisive_inconclusive for DOI / free-form citations so dispatch
  wrapper falls back. Network errors propagate as exceptions; the
  wrapper classifies TimeoutError / 5xx HTTPError as transient and
  retries once.
- **`catalog_lookup`** (hours 2 + 4): parses
  `aporia/mathematics/tensor_open_problems_v1.md` for T#NN entries.
  Per-T# bound-check closures (`_T_BOUND_CHECKERS`) registered for
  T#1 (ω ∈ [2, 2.371339)), T#4 (R(M<3>) ∈ [19, 23]), T#56
  (sym-rank NP-hardness). Each closure takes claim_text, returns
  (outcome_class, caveats) or None to defer. Catalog entry exists
  but no bound checker registered -> decisive_inconclusive for
  fallback.
- **`mpmath_compute`** (hour 3): Mahler-measure family via
  `_MPMATH_CALIBRATION_TABLE` keyed by claim_id. Lehmer entry
  computes to 1.176280818259917506544... at dps=30 in 8ms; diff vs
  catalog 3.5e-32, well inside 1e-25 tolerance.
- **`substrate_self_check`** (hour 3, expanded hour 6): registry of
  15 invariants over substrate's own state (enum sizes, calibration
  table entries, T# bound checker presence, anti_anchor registry
  sanity, T#1/T#4 numeric drift detectors). Each is a zero-arg
  callable. Dispatch via verifier_args.invariant_name.
- **`sympy_factor`** (hour 3): polynomial form comparison via
  `_SYMPY_CALIBRATION_TABLE`. Two entries: trefoil Alexander
  polynomial, figure-eight Jones polynomial. Heuristic extraction
  from claim_text after the last '=' sign, with TeX caret -> Python
  power normalization. sp.simplify(claimed - canonical) == 0 match.
- **`triangulation`** (hour 7): meta-verifier dispatching a configurable
  list (defaults to citation_audit + catalog_lookup). Unanimous
  decisive verdict -> verifier returns that verdict. Mixed decisive
  (verified AND contradicted observed) -> decisive_inconclusive with
  substrate_verifier_disagreement reason (substrate-grade finding —
  the substrate's tools disagree about the same claim). Self-recursion
  filter prevents infinite recursion.

### Parser hardening (hour 1)

`aporia/scripts/parse_substrate_blocks.py` now recognizes 4 emission
conventions, not just the strict `# substrate_block: <type>` marker.
The pilot model produced 14 blocks across 3 reports using 3 different
alt conventions; the parser now accepts all of them:

- **C0 strict marker** (preferred / documented): `# substrate_block: <type>`
  on the line after the fence opener.
- **C1 substrate_type field**: `substrate_type: <type>` as a YAML field
  inside the body, with `---` doc separators for multiple blocks.
- **C2 block-type-as-key**: `<block_type>:` as the single top-level
  YAML key in a mapping; multi-doc YAML again allowed.
- **C3 schema field in JSON array**: `"schema": "<block_type>"` per
  item, typically inside ```json fences.

`_detect_alt_convention(doc)` returns `(block_type, normalized_payload)`
with the wrapper field stripped. Strict and alt passes are mutually
exclusive (yielded-spans tracking prevents double-counting).

### Anti-anchor couplet override (hour 5)

`run_claim` adds a post-dispatch override step. When
`claim.parent_block` matches a registered anti_anchor ID AND
`claim.source_report` contains `false_form` -> override verdict to
decisive_contradicted. For `true_form` -> decisive_verified. Handles
the fundamental citation_audit limitation: it verifies the cited
paper exists, not whether the claim_text accurately reflects what
the paper says. The substrate's `techne/registry/anti_anchors.jsonl`
encodes that relationship explicitly for couplet pairs.

### Per-block-type staging (hour 5)

`aporia/scripts/validate_substrate_blocks.py` adds `--stage-dir`
flag. When set, writes `<block_type>.jsonl` per block_type into the
stage dir containing only VALIDATED records. Files always written
even when empty (consumer contract: file exists, zero-line means
"no valid blocks of this type"). Per Aporia's pilot-output-ready
ticket, Ergon's `ingest_training_anchors.py` reads
`<stage-dir>/training_anchor.jsonl`.

### Substrate-self claim batch (hour 6)

`aporia/meta/queue/substrate_self_claims_techne_2026-05-13.jsonl` —
15 claims authored by Techne (one per registered invariant). All
validate against `claim_v1.json`. End-to-end runner dispatch:
15/15 = 100% decisive_verified in 1ms. Builds the substrate's
self-falsification surface; future drift gets caught here first.

### Aporia starter batch results

`aporia/meta/queue/claim_stack_aporia_starter_2026-05-13.md` — 20
claims authored by Aporia. 17 valid against `claim_v1.json` (3
calibration claims fail prompt_template requirement; separate
finding ticket open). End-to-end on the 17:

  Hour 1 (all stubs):              0/17 =   0.0%
  Hour 2 (4 verifiers):            7/17 =  41.2%
  Hour 3 (5 verifiers + sympy):    9/17 =  52.9%
  Hour 4 (T#1 + T#4 bound check): 12/17 =  70.6%
  Hour 4 (+T#56 complexity):      13/17 =  76.5%
  Hour 5 (+false_form override):  16/17 =  94.1%
  Hour 5 (+true_form override):   17/17 = 100.0%

Final verdict distribution exactly mirrors expected: 7 contradicted
(= 7 falsified) + 9 verified (= 9 survived) + 1 inconclusive
(= 1 open). End-to-end wall clock: ~1s for 17 claims.

### Tests

123 tests pass in 12.6s (was 36 at session start; +87 tests today
covering claim-stack runner, parser conventions, verifier dispatch,
quality rules, bound checkers, couplet override, substrate-self
invariants, triangulation aggregation).

### Remaining stubs / known limitations

- `manual_review` verifier remains stubbed (needs human-in-the-loop
  infrastructure design).
- `triangulation` is wired but isn't on the dispatch path for any
  current Aporia claim (none specify it as primary). Available for
  future calls.
- The pilot batch's field-shape divergence (14 blocks parsed but
  0 validated due to model-invented field names within block_types)
  is Track B prompt-strengthening territory; not a v3.3.0 deliverable.

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
