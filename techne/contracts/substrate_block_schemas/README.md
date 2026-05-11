# Substrate-Block Schemas (v1)

**Date filed:** 2026-05-11
**Status:** Pilot. Schemas are JSON Schema draft 2020-12. Six block types, one schema per type, plus shared `_common_definitions.json`.

Per `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md`. These schemas are the canonical write-time contract for substrate blocks emitted by Gemini Deep Research reports under substrate-shaped prompt variants. Validation enforces them mechanically; ingestion routes valid blocks to canonical registries.

Per `techne/PROMPT_2026-05-11_substrate_first.md` Track 1: this is the leverage point — 5-10x reviewer throughput per Gemini batch if the pilot succeeds, with arXiv-verify gating Lee-2025-shaped withdrawals mechanically.

---

## The six schemas

| Schema | Primary registry target | Required for |
|---|---|---|
| `anti_anchor_v1.json` | `techne/registry/anti_anchors.jsonl` | Tier-1 (mandatory), all others (optional) |
| `primitive_proposal_v1.json` | `aporia/doctrine/substrate_vocabulary/primitives.md` | Tier-3 + Tier-4 (mandatory) |
| `composition_rule_v1.json` | `techne/registry/compositions.jsonl` | Tier-2 + Tier-4 (optional) |
| `catalog_edit_v1.json` | `aporia/mathematics/tensor_open_problems_v1.md` | Tier-2 (mandatory if stale) |
| `training_anchor_v1.json` | `techne/registry/training_anchors.jsonl` (new) | Tier-3 (mandatory) |
| `paradigm_candidate_v1.json` | `aporia/doctrine/paradigm_candidates.jsonl` (new) | Tier-4 (optional) |

Plus `_common_definitions.json` for shared shapes (citation, withdrawn-status, schema-version).

## Schema versioning

Every block carries `_schema_version: "1.0.0"` for forward migration. Validator rejects blocks whose `_schema_version` does not match the schema's declared version with a clear "schema version mismatch" message. Future migrations live in `aporia/scripts/migrate_substrate_blocks.py` (placeholder this pilot).

Schemas evolve **additively** by default (new optional fields, no new mandatory fields). Mandatory-field additions require an explicit "schema break window" event.

## HARD-5 enforcement at write-time

The substrate's HARD-5 doctrine — distinct coordinates must be carried as distinct fields — is enforced mechanically here:

- **`primitive_proposal.required_fields`** rejects ambiguous coordinate names. A `field_name` of `"rank"` (without qualifier) is REJECTED; `"border_rank"`, `"slice_rank"`, `"cactus_rank"`, etc. are ACCEPTED. Pattern: field names matching `^(rank|complexity|dimension|degree)$` (the four most-collapsed coordinates per fire-#42 saturation) trigger validation failure with a hint to disambiguate.
- **`anti_anchor.true_form`** has minimum length 60 to discourage qualifier-clipping.
- **`composition_rule.precondition_primitives`** + **`output_primitive`** are required UpperCamelCase identifiers, never bare nouns.
- **`catalog_edit.before` / `after`** are verbatim strings, not synthesized — the validator does NOT enforce verbatim-ness (that's the reviewer's job) but the ingestion script at `ingest_substrate_blocks.py` will refuse to apply a `before` string that does not appear unchanged in the target file.

## Anti-leakage / anti-fabrication enforcement

- **`citation`** must match `^arXiv:\d{4}\.\d{4,5}$` (arXiv ID format) or `^\d{2}\.\d{4}/\S+$` (DOI). Hallucinated citation strings fail at parse time.
- **`citation_withdrawn_status`** is an enum or `withdrawn YYYY-MM-DD` pattern. Used by `verify_arxiv_citations.py` as a cross-check against arXiv API.
- **`verified_against_primary`** is a boolean assertion the reviewer must re-verify. The validator records the assertion; it does not trust it.

## Validation pipeline

```
Gemini Deep Research report
  -> aporia/scripts/parse_substrate_blocks.py
       extracts fenced YAML blocks tagged "# substrate_block: <type>"
       -> parsed_substrate_blocks.jsonl
  -> aporia/scripts/validate_substrate_blocks.py
       validates against the 6 schemas + arXiv HEAD check + cross-references
       -> validated.jsonl + rejected.jsonl
  -> [stage / review / ingest steps live downstream of this pilot scope]
```

This pilot scope includes: 6 schemas + parse + validate. Ingestion is gated on pilot evidence per the prompt.

## Cross-references

- `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md` — design doc
- `techne/PROMPT_2026-05-11_substrate_first.md` — this work's prompt
- `pivot/strategic_pivot_2026-05-11_substrate_volume_first.md` — strategic context
- `techne/registry/anti_anchors.jsonl` (12 entries as of 2026-05-11) — existing AA registry; new schema is a superset of its fields
- `techne/registry/compositions.jsonl` (7 entries) — existing composition registry; new schema enriches `literature_confirmation` to objects
- `aporia/mathematics/tensor_open_problems_v1.md` — catalog_edit target
- `aporia/doctrine/substrate_vocabulary/primitives.md` — primitive_proposal narrative target

— Techne, 2026-05-11
