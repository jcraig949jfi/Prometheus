# Techne — Next-Step Prompt (2026-05-11)

**Paste-target:** Techne agent session. Self-contained — agent has memory; this prompt is the directional update.

---

## Strategic update

James has called a pivot: **LoRA training is paused indefinitely until substrate volume + quality lifts materially.** See `pivot/strategic_pivot_2026-05-11_substrate_volume_first.md` for full analysis.

Substrate-volume-and-quality is the explicit gate. Techne is the natural lead on this, because:
- Techne owns contracts + schemas (the substrate-shaped pipeline's central artifacts).
- Techne owns the registry (anti_anchors.jsonl, compositions.jsonl, inventory.json — the canonical destinations for ingested substrate blocks).
- Techne's recent dialogue with Ergon (the derive_kill_signature audit catching polynomial-coefficient leakage) demonstrated exactly the substrate-grade discipline that the new pipeline needs to enforce mechanically.

## Your scope this week

**You will NOT:**
- Trigger any LoRA, Mahler, or --writeable substrate work (Ergon stand-down also applies here).
- Open the v4.0 contract-change window for Wave 1 primitive registration yet. Wave 1 stays in scaffolding state until Path 1 pilot evidence is in (see strategic_pivot §2). Premature contract changes would bake assumptions the pilot may invalidate.
- Burn cycles on the Phase-3 P2 substrate-hardening pile (T016/T017/T019/T022/T031-T037) this week. Resume when Path 1 pilot is past evidence stage.

**You will:**

### Track 1 — Lead the substrate-shaped pipeline pilot (PRIMARY)

The design exists at `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md`. Six substrate_block schemas (`anti_anchor`, `primitive_proposal`, `composition_rule`, `catalog_edit`, `training_anchor`, `paradigm_candidate`) need to land as canonical JSON schemas, then the parse/validate/stage tooling, then a 3-entry pilot fire compared against narrative-only equivalents. This is the leverage point — 5-10x reviewer throughput per Gemini batch if it works, with arXiv-verify gating Lee-2025-shaped withdrawals mechanically.

Specifically:

1. **Spec the 6 JSON schemas** at `techne/contracts/substrate_block_schemas/`:
   - `anti_anchor_v1.json`
   - `primitive_proposal_v1.json`
   - `composition_rule_v1.json`
   - `catalog_edit_v1.json`
   - `training_anchor_v1.json`
   - `paradigm_candidate_v1.json`
   Each schema is JSON Schema draft 2020-12. Fields match the YAML examples in the design doc; add `_schema_version` field for forward migration. HARD-5 enforced: no schema may merge two distinct rank coordinates or two distinct complexity coordinates into one field.

2. **Build the parse step** at `aporia/scripts/parse_substrate_blocks.py`:
   - Walks files in a batch dir (e.g., `aporia/docs/deep_research_batch_<date>/`)
   - Finds fenced YAML blocks tagged `# substrate_block: <type>`
   - Parses YAML, emits one JSONL line per block to `aporia/docs/staged_substrate_blocks/<date>/<type>.jsonl`
   - Tags each block with `source_report` and `extracted_at`

3. **Build the validate step** at `aporia/scripts/validate_substrate_blocks.py`:
   - jsonschema validation against the 6 schemas
   - arXiv citation existence check via export.arxiv.org HEAD request
   - arXiv withdrawal-status check (parse for "withdrawn" / "retracted" / comment fields)
   - Cross-reference checks (e.g., `catalog_edit.entry_id` must exist in `aporia/mathematics/tensor_open_problems_v1.md`; `primitive_proposal.parent_class` must exist in vocabulary primitives.md)
   - Reject blocks failing any check; route to `staged/<date>/rejected.jsonl` with reason field

4. **Coordinate with Aporia on the pilot fire.** Pilot fires 3 queue entries (suggested: DR-001 Strassen direct-sum, DR-007 LMFDB GL(3) root number, one Tier-3 calibration entry when ready) with substrate-shaped variants alongside the standard narrative-only equivalent. Aporia builds the deck; Techne owns the parse/validate/stage of the substrate-shaped outputs.

5. **DO NOT build the ingest step yet.** Ingestion (routing approved blocks to canonical registries) is gated on pilot evidence. Build it next week if pilot is positive.

### Track 2 — Continue Dims 2/3/10 audit-prep (precondition)

Continue the audit-prep doc you'd already proposed (path (a) from your earlier dialogue) at `techne/diagnostics/dims_2_3_10_audit_prep_2026-05-11.md`. Per-dim: what current substrate emission already carries, what minimum generator-side instrumentation would look like, contract-change implications if any. Doc-only. This is the precondition for cleaner episode emissions when LoRA does train.

Ergon will produce an Ergon-side consumption check (Track 2 of their prompt) responding to your audit-prep. Coordinate via `aporia/meta/queue/ergon_inbox.jsonl` and `aporia/meta/queue/techne_inbox.jsonl`.

### Track 3 — Memory entry: "generic dim → specific instance via code-level audit"

You proposed this as path (c) in your earlier dialogue. The pattern has 2 instances now:
1. Saxl capture (2026-05-09 generic claim → 2026-05-10 Lee 2025 withdrawal found via Gemini Deep Research arXiv verification)
2. derive_kill_signature factorization-leak catch (Ergon Dim 9 "structural separation" generic → Techne audit of kill_pattern strings found `(x**2 + 1)^1; (x**10 - x**9 + ...)` literal polynomial leak)

Write the memory entry at `C:\Users\jcrai\.claude\projects\F--Prometheus\memory\feedback_generic_to_specific_audit.md` (this is Claude Code memory, not the repo). Frame as: substrate's anti-passive-consumer remediation pattern — when a dim/claim is named at generic level, expect a code-level or citation-level audit to surface a concrete instance that reshapes the design. Reward this pattern.

Also add a one-line pointer in `C:\Users\jcrai\.claude\projects\F--Prometheus\memory\MEMORY.md` under the Feedback section.

## Bounded resources

- File ownership: `techne/` tree, plus `aporia/scripts/parse_substrate_blocks.py` and `aporia/scripts/validate_substrate_blocks.py` (these live in aporia/scripts/ to colocate with the existing dispatcher; Techne owns the schemas they reference).
- No compute. No API budget. No contract-change window.
- Estimated total work: 3-4 days across Tracks 1-3.

## What to file when work lands

- Track 1 schemas: append to `aporia/meta/queue/aporia_inbox.jsonl` flagging schemas are ready for pilot fire. P1-high.
- Track 1 tooling: append `techne/CHANGELOG.md` entries (v3.2.0 candidate? — or stay v3.1.x until ingest lands).
- Track 2 audit-prep: append to `aporia/meta/queue/ergon_inbox.jsonl` flagging the audit-prep doc is ready for Ergon consumption check. P2-medium.
- Track 3: memory entry lands at the memory path; no inbox ticket needed (it's Claude Code memory, not substrate registry).

## What you should NOT ask James about

The compute decision for LoRA is deferred to ~week 3+. Stop holding the compute-scope question open in your status_history. Move it from "BLOCKED on James decision" to "DEFERRED per strategic_pivot_2026-05-11."

## Pilot success criteria (for Track 1)

When the 3-entry pilot fires and returns, the comparison is:
- **Pass:** ≥80% of substrate blocks emitted across the 3 reports pass arXiv-verify + jsonschema validation. Reviewer time on substrate-shaped reports is ≤50% of reviewer time on narrative-only equivalents.
- **Conditional pass (revise):** 50-80% block validity. Schemas need refinement before full migration. Iterate one cycle.
- **Fail (revert):** <50% validity, or reviewer time doesn't decrease. Roll back; keep arXiv-verify as standalone post-hoc audit; substrate-shaped pipeline goes back to design.

Track the metrics empirically. Don't grade on narrative claims.

## Substrate-grade observation worth carrying forward

Same as Ergon's: the generic-dim → specific-instance pattern is the substrate's remediation against passive-consumer drift. Build Track 1 with that posture: the validate step is the audit that turns generic Gemini-emitted claims into concrete pass/reject decisions. The arXiv HEAD check is the lower-level instance audit that the substrate's generic-level schemas need.

End of prompt. Acknowledge receipt, then proceed with Track 1 schema design.
