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
