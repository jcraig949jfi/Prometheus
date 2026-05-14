# Training-Anchor Ingestion Spec — Ergon Entry Harness for Substrate-Shaped Pipeline

**Filed:** 2026-05-11 by Ergon (Learner owner)
**Track:** Track 1 of `ergon/PROMPT_2026-05-11_substrate_first.md` (PRIMARY)
**Upstream:** Techne-led substrate-shaped Gemini pipeline (`aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md`)
**Downstream:** v1.0 Learner corpus (currently DEFERRED per pivot 2026-05-11 — pilot LoRA waits for substrate volume threshold)
**Doctrine:** HARD-2 (no contract changes), HARD-5 (distinct coordinates preserved), `feedback_verify_upstream_attributions.md`, `feedback_substrate_passive_consumer_warning.md`

---

## §0 Purpose + scope

When Techne's substrate-shaped pipeline produces JSONL `training_anchor` blocks at scale, Ergon must be able to ingest them into the v1.0 corpus directly — no manual translation step, no per-batch judgment calls on schema mapping. This spec defines how each `training_anchor` block becomes a `LearnerRecord` and what trust-tier discipline propagates into the (deferred) 4-condition eval harness.

**Not in scope for this spec:**
- The substrate-shaped pipeline itself (Techne owns parse / validate / stage).
- Running any ingestion (compute deferred; this is a doc + ready-to-fire script).
- Modifying the `training_anchor` schema (file Aporia ticket for any gap; do not edit upstream).
- Modifying `learner_enrichment.py` `LearnerRecord` schema (contract-frozen).

**In scope:**
- Field-level mapping from `training_anchor` YAML schema → `LearnerRecord` 8-field schema.
- Trust-tier propagation into the 4-condition eval harness specified at `pilot_lora_design_tier_1_corpus.md` §2.
- Blind-spot anchor coverage accounting per ingested batch.
- Ingester script behavior contract (input dir, output dir, validation, idempotency, dry-run).

---

## §1 Schema mapping — `training_anchor` block → `LearnerRecord`

### §1.1 Upstream schema (per `SUBSTRATE_SHAPED_PROMPTS.md` §2.3)

```yaml
# substrate_block: training_anchor
- id: anchor-<domain>-<NNN>
  domain: knots | maass_gl3 | genus2 | tensor | ...
  anchor_type: invariant_value | classification | bound | predicate
  dataset_source: <URL or LMFDB table or paper reference>
  dataset_license: <license string>
  scale:
    instance_count: <int or null if not enumerable>
    coverage_qualifier: <string>
  prompt_template: |
    <natural-language form of the verification question>
  expected_answer_shape: <type description>
  verification_method: analytical_proof | ml_prediction | computational_certified | folklore
  trust_tier: analytically_proven | numerically_certified | ml_predicted | unverified
  source: <primary citation>
  source_date: YYYY-MM-DD
  caveats: |
    <paragraph with measure-zero exceptions, AI-prediction admixture, completeness qualifiers>
  consumed_by: <Ergon script path or queue entry>
```

### §1.2 Downstream schema (per `prometheus_math/substrate_generation/learner_enrichment.py:79-86`)

```python
LearnerRecord(
    underlying_record_hash: str,
    episode_id: str,
    episode_phase: str,            # one of EPISODE_PHASES
    verification_tier: str,        # one of VERIFICATION_TIERS or "unknown"
    chart_id: Optional[str],
    decoy_kind: Optional[str],     # one of DECOY_KINDS or None
    kill_signature: Tuple[str, ...],
    outcome_class: str,            # one of OUTCOME_CLASSES
)
```

### §1.3 Field-level mapping

| `training_anchor` field | `LearnerRecord` field | Mapping rule |
|---|---|---|
| `id` | `underlying_record_hash` | SHA256 of canonical training-anchor blob (id + prompt_template + expected_answer_shape + trust_tier + source). Stable across re-ingestion. Not the raw `id` string — hash for downstream deduplication and join-safety. |
| `id` | `episode_id` | Equals `underlying_record_hash` in Tier-1 (1:1, same convention as `learner_enrichment.enrich()` line 299). Tier-2+ may group ingested anchors into multi-record episodes. |
| (synthesized) | `episode_phase` | `"evaluate"` for Tier-1 ingestion (matches `EPISODE_PHASES[0]`). When Techne ships REWRITE/EQUIV opcode-emission (deferred to Dim 5 path), training-anchor ingestion paths can split into "claim" / "falsify" / "promote" sub-records. Tier-1 = single phase. |
| `trust_tier` | `verification_tier` | Mapping table in §2 below. Trust-tier-to-decidability is not 1:1; spec records the convention. |
| `domain` (+ chart registry lookup) | `chart_id` | `f"{domain}:<region_key>"` if a registered chart exists for the domain; else `None`. Region-key heuristic: use `anchor_type` as region-key initially, refine when CoordinateChart registrations land for non-tensor domains. |
| (synthesized) | `decoy_kind` | `None` for ingested training-anchors. Training-anchors are not decoys — they are positive ground-truth anchors. Decoy injection happens at corpus-assembly time, not ingestion time. |
| (synthesized) | `kill_signature` | `("training_anchor", anchor_type)` — a 2-tuple capturing the structural type without leaking the anchor's prompt or expected answer. **Anti-leakage discipline preserved (Dim 9):** prompt_template and expected_answer_shape are NOT placed in the signature. |
| `verification_method` + `trust_tier` | `outcome_class` | Mapping table in §3 below. Encodes what the trained model SHOULD emit for this anchor's prompt. |

### §1.4 Fields not mapped (preserved at JSONL-attached metadata)

The following `training_anchor` fields do not fit cleanly into `LearnerRecord` but are critical for downstream eval. The ingester emits them as a **sidecar dict** on each `LearnerRecord` JSONL line under the key `_training_anchor_meta` (NOT part of `LearnerRecord` dataclass; serialization-only):

- `prompt_template` — the actual training prompt; needed at training time
- `expected_answer_shape` — needed for eval-time scoring
- `source` + `source_date` — provenance for downstream audit / verification
- `dataset_source` + `dataset_license` — license compliance
- `caveats` — preserved verbatim for review at corpus-assembly time
- `consumed_by` — original training-anchor consumer hint (may differ from this ingester)
- `scale.instance_count` + `scale.coverage_qualifier` — for batch-level statistics

This sidecar pattern keeps `LearnerRecord` schema-frozen while giving the corpus-assembly step the metadata it needs.

---

## §2 Trust-tier propagation into eval harness

### §2.1 `trust_tier` → `verification_tier` mapping

Per `learner_enrichment.py:98-100`, `VERIFICATION_TIERS = ("decidable", "undecidable", "conditional", "unknown")`. The mapping below is Ergon's working convention; **gap candidate** — flagged for Aporia adjudication if Techne disagrees.

| `training_anchor.trust_tier` | `LearnerRecord.verification_tier` | Rationale |
|---|---|---|
| `analytically_proven` | `decidable` | Primary-source theorem with proof; eligible for full positive-anchor weight |
| `numerically_certified` | `decidable` | Computational verification with interval-arithmetic / certified-precision; same eligibility as analytical for Tier-1, can be split in Tier-2+ if precision-stratification needed |
| `ml_predicted` | `conditional` | The math is "predicted by ML model", e.g. LMFDB murmuration-derived root numbers; conditionality is explicit, the model should NOT treat as ground truth |
| `unverified` | `unknown` | Ingestion DROPS these records by default (config flag `--allow-unverified` overrides for explicit experiments only) |

### §2.2 Trust-tier weighting across the 4-condition eval harness

Per `pilot_lora_design_tier_1_corpus.md` §2.1, the 4 conditions are: (1) base no-LoRA, (2) base + Tier-1 LoRA, (3) base + label-shuffled, (4) base + format-only.

| Condition | trust-tier policy |
|---|---|
| 1. Base no-LoRA | Eval set uses `decidable` + `conditional` anchors. `unknown` excluded. ml_predicted anchors flagged in eval output but scored separately. |
| 2. Base + Tier-1 LoRA | Training corpus: `decidable` anchors get full sample-weight; `conditional` anchors get 0.5x sample-weight; `unknown` excluded. Eval set identical to condition 1. |
| 3. Label-shuffled control | Training: identical anchors as condition 2 but `outcome_class` shuffled across records. Trust-tier preserved (shuffle is on labels, not metadata). |
| 4. Format-only control | Training: identical anchors as condition 2 but `kill_signature` and `outcome_class` replaced with random valid-enum values. Trust-tier preserved. |

**Key property:** trust-tier MUST appear in eval metrics (per `pilot_lora_design_tier_1_corpus.md` §2.3 metric 6 "kill-signature consistency") so that the calibration-preservation gate can be enforced independently per trust-tier. A LoRA that improves on `decidable` anchors but degrades `conditional` calibration is a calibration-poisoning result and must be rejected per Gate 1.

### §2.3 `outcome_class` mapping

Per `learner_enrichment.py:103-108`, `OUTCOME_CLASSES = ("rejected", "survived", "promoted", "errored")`. The mapping below encodes what the model SHOULD emit for this anchor's prompt.

| `anchor_type` + `trust_tier` | `outcome_class` | Rationale |
|---|---|---|
| `invariant_value` + `analytically_proven`/`numerically_certified` | `promoted` | Known-correct positive anchor; model should emit the value with high confidence |
| `classification` + `analytically_proven`/`numerically_certified` | `promoted` | Known-correct classification; same as invariant_value |
| `bound` + `analytically_proven`/`numerically_certified` | `promoted` | Known-tight bound; model should emit |
| `predicate` (true) + analytical/numerical | `promoted` | Predicate that holds; model should emit "yes" with provenance |
| `predicate` (false) + analytical/numerical | `rejected` | Predicate that fails; model should emit "no" |
| any `anchor_type` + `ml_predicted` | `survived` | The math is unverified; model should pass F-gate battery but NOT PROMOTE (decidability is conditional) |
| any `anchor_type` + `unverified` | NOT INGESTED | Default drop; see §2.1 |

**Note:** `errored` is reserved for ingestion-time parse failures, NOT a valid training target. Records that map to `errored` go to `validation_errors.jsonl`, not to the corpus.

---

## §3 Blind-spot anchor coverage per ingested batch

### §3.1 BS-coverage propagation (schema v1.1, explicit field with regex fallback)

Blind-spot coverage is critical to the calibration-preservation gate (`pilot_lora_design_tier_1_corpus.md` §2.3 Gate 1). Per `feedback_substrate_passive_consumer_warning.md`, blind-spot ingestion is one of the highest-value behavior-delta paths (a Tier-1 training corpus without explicit BS coverage produces a calibration-poisoning result).

**Schema status (2026-05-13):** `training_anchor` v1.1.0 ships an optional `bs_coverage: Array[String matching ^BS-\d{3,5}$]` field, uniqueItems, empty list and absent both legal (`techne/contracts/substrate_block_schemas/training_anchor_v1.json:142-152`). Authority: ticket `T-2026-05-13-techne-to-aporia-and-ergon-training_anchor-v1.1-ready` (originating gap was §5.1 Gap 1 below, closed by this ship). v1.0.0 emitters validate unchanged; v1.1.0 emitters can supply `bs_coverage` explicitly.

**Ingester behavior (two code paths, both live):**

1. **Explicit field (v1.1.0 path, preferred):** If the block carries a `bs_coverage` key whose value is a list (including empty list `[]`), the ingester uses that list verbatim. Empty list is a meaningful signal: "author considered BS coverage; no link applies." This is the path that closes the silent-miss prone Q-form anchor failure mode (e.g., Cohen 1963 CH-independence, where the answer "Cohen, 1963" lives in `source` not `prompt_template`).
2. **Regex fallback (v1.0.0 path, backwards-compat):** If the block has no `bs_coverage` key, the ingester scans **`prompt_template + caveats + source + dataset_source` concatenation** against canonical BS topic regexes from `aporia/calibration/learner_known_blind_spots_v1.json`. Bug caught at 2026-05-11 smoke test: scanning `prompt_template` alone silent-missed all Q-form anchors (prompt carries the QUESTION, not the prover's name). Search-corpus expanded accordingly. Matches are written to the sidecar `_training_anchor_meta.bs_coverage` field.

**Version detection:** the ingester does NOT inspect `_schema_version` explicitly. It dispatches solely on `bs_coverage` field presence (`block.get("bs_coverage") is not None`). This is correct because Techne's upstream schema validator (`stage_substrate_blocks`) rejects v1.0.0 blocks containing `bs_coverage` (additionalProperties:false on v1.0.0); therefore any `bs_coverage` reaching Ergon's ingester is from a validated v1.1.0 block. Defense-in-depth `_schema_version`-prefix check is intentionally omitted to keep ingester logic minimal.

**Reviewer hook (regression-discipline):** the per-batch summary's `bs_coverage.unmapped` count is the residual silent-miss indicator. Batches with `unmapped` high while authors are emitting v1.0.0 are the population most at risk of Q-form silent miss; encourage author migration to v1.1.0 + explicit `bs_coverage` for those domains.

### §3.2 Per-batch BS coverage accounting

The ingester produces a per-batch summary JSON at `ergon/learner/corpus/v1_0_tier_pending/<date>/ingest_summary.json` containing:

```json
{
  "ingest_date": "YYYY-MM-DD",
  "source_batch": "<upstream batch tag>",
  "total_anchors_input": <int>,
  "total_anchors_ingested": <int>,
  "total_anchors_dropped": <int>,
  "drop_reasons": {
    "unverified_trust_tier": <int>,
    "schema_validation_failure": <int>,
    "missing_required_field": <int>
  },
  "by_trust_tier": {
    "analytically_proven": <int>,
    "numerically_certified": <int>,
    "ml_predicted": <int>,
    "unverified": <int>
  },
  "by_domain": {
    "knots": <int>,
    "maass_gl3": <int>,
    ...
  },
  "by_outcome_class": {
    "promoted": <int>,
    "survived": <int>,
    "rejected": <int>
  },
  "bs_coverage": {
    "BS-001": <int>,
    "BS-003": <int>,
    "BS-004": <int>,
    "BS-005": <int>,
    "BS-006": <int>,
    "unmapped": <int>
  }
}
```

This summary is what an Aporia / James reviewer looks at to assess "did this batch contribute usable training corpus?" Threshold for inclusion in the v1.0 corpus assembly step: `total_anchors_ingested >= 5` AND `by_trust_tier.analytically_proven + by_trust_tier.numerically_certified >= 2`. Batches below threshold go to `v1_0_tier_pending/<date>/under_threshold/` for later review.

---

## §4 Ingester script behavior contract

### §4.1 Path

`ergon/learner/scripts/ingest_training_anchors.py`

### §4.2 Invocation

```bash
python ergon/learner/scripts/ingest_training_anchors.py \
  --input aporia/docs/staged_substrate_blocks/2026-05-15/training_anchor.jsonl \
  --output-dir ergon/learner/corpus/v1_0_tier_pending/ \
  --batch-date 2026-05-15 \
  --dry-run    # default; prints what would be written without writing
```

### §4.3 Inputs

- **`--input`** (required): JSONL file from `aporia/docs/staged_substrate_blocks/<date>/training_anchor.jsonl`. Each line is one `training_anchor` block per the YAML schema (serialized as JSON dict by Techne's `stage_substrate_blocks.py`).
- **`--output-dir`** (default: `ergon/learner/corpus/v1_0_tier_pending/`): where the per-batch directory is written.
- **`--batch-date`** (required): YYYY-MM-DD; becomes the subdirectory name.
- **`--dry-run` / `--write`** (default: dry-run): mirror of substrate-shaped pipeline's `--writeable` discipline. No writes without explicit `--write` flag.
- **`--allow-unverified`** (default: false): override the `trust_tier: unverified` drop policy. Use only for explicit experiments.

### §4.4 Outputs (when `--write` set)

- `ergon/learner/corpus/v1_0_tier_pending/<date>/training_anchor_learner_records.jsonl` — one LearnerRecord JSON per line, with `_training_anchor_meta` sidecar dict
- `ergon/learner/corpus/v1_0_tier_pending/<date>/ingest_summary.json` — per §3.2 schema
- `ergon/learner/corpus/v1_0_tier_pending/<date>/validation_errors.jsonl` — one parse/validation failure per line (mirrors Techne's `stage_substrate_blocks.py:validation_errors.jsonl` convention)
- `ergon/learner/corpus/v1_0_tier_pending/<date>/under_threshold/` — if total ingested below threshold per §3.2 final paragraph

### §4.5 Validation rules (minimum)

The ingester rejects (writes to `validation_errors.jsonl`) any `training_anchor` block missing any of:

- `id` (string, non-empty, matches regex `^anchor-[a-z0-9_]+-\d+$`)
- `domain` (string, non-empty)
- `anchor_type` (string, one of `{invariant_value, classification, bound, predicate}`)
- `trust_tier` (string, one of `{analytically_proven, numerically_certified, ml_predicted, unverified}`)
- `verification_method` (string, one of `{analytical_proof, ml_prediction, computational_certified, folklore}`)
- `prompt_template` (string, non-empty, min 20 characters)
- `expected_answer_shape` (string, non-empty)
- `source` (string, non-empty)
- `source_date` (string, regex `^\d{4}-\d{2}-\d{2}$`)

Records with `trust_tier: unverified` go to a separate drop bucket (not validation errors); records below dataset-license or anti-leakage checks should also be flagged.

### §4.6 Idempotency

The ingester is **idempotent on inputs**: re-running with the same `--input` and `--batch-date` produces identical output bytes (`underlying_record_hash` is deterministic from canonical anchor blob; output JSON ordered by `id`).

It is **NOT idempotent on appending**: running with the same date twice will overwrite the previous batch's outputs in that directory. The script refuses to write to an existing non-empty directory unless `--overwrite` is passed.

### §4.7 What the ingester does NOT do

- **Does NOT run any LoRA training.** This is corpus assembly only.
- **Does NOT call any API.** No arXiv-verify, no LMFDB query, no model API call. Trust the upstream `verified_against_primary` flag at Techne's stage; trust-tier metadata is propagated, not re-derived.
- **Does NOT modify substrate registries.** Read-only on `techne/registry/*.jsonl`, `aporia/calibration/*.json`.
- **Does NOT auto-promote anchors to corpus.** Output goes to `v1_0_tier_pending/`; a separate (TBD) corpus-assembly step promotes from `pending` to `assembled` after review.

---

## §5 Coordination with Techne

### §5.1 Schema gaps + resolutions

Per the prompt's "If you see fields you'd want different (e.g., adding episode_id slot to support falsification-routing training), file an Aporia ticket — don't modify schemas directly."

**Gap 1: `bs_coverage` field on `training_anchor` — RESOLVED 2026-05-13.** Closed by Techne ship of v1.1.0 schema (`T-2026-05-13-techne-to-aporia-and-ergon-training_anchor-v1.1-ready`). Optional array of `^BS-\d{3,5}$`-matching strings, uniqueItems. Ingester dual-path (explicit-then-fallback) documented in §3.1. Originating gap was the silent-miss-prone regex path on Q-form anchors (Cohen 1963 CH-independence the canonical case).

**Gap 2: `episode_id` slot (potentially deferred).** Currently the ingester uses SHA256-of-canonical-blob as `underlying_record_hash` and 1:1 as `episode_id`. This is fine for Tier-1. If Techne's substrate-shaped pipeline ever wants to emit multi-record episodes (one prompt + multiple training-anchor blocks sharing an episode), the schema would need an explicit `episode_id` field. Defer ticket until pilot evidence forces it.

**Gap 3: `decoy_kind` ambiguity.** `training_anchor` blocks describe positive ground-truth anchors. The `LearnerRecord.decoy_kind` field currently has values `seeded_survivor` (Tier-1 Mossinghoff) and `known_kill`. Ingested training-anchors are neither — they're upstream-curated positives. Spec sets `decoy_kind=None` for now. If a future iteration wants explicit "positive ingested anchor" tagging, propose adding `training_anchor_positive` to `DECOY_KINDS`. Defer.

### §5.2 Filing order

Gap 1 RESOLVED via v1.1 ship (2026-05-13). File Gap 2 and Gap 3 only if pilot evidence (when LoRA fires, post-substrate-volume-threshold) shows they bite.

---

## §6 Calibration

Per `feedback_calibration.md`: this spec covers Track 1 of the 2026-05-11 prompt. It does NOT claim:

- That the substrate-shaped pipeline will produce useful `training_anchor` blocks at scale (Techne pilot evidence required).
- That trust-tier mapping in §2 is the right convention (Aporia adjudication may revise).
- That the BS-coverage regex fallback in §3.1 will catch all silent-miss candidates (the v1.1 explicit `bs_coverage` field is the proper fix for v1.1.0-emitter blocks; v1.0.0 blocks still rely on the heuristic).
- That `outcome_class` mapping in §2.3 is final (predicates that are TRUE vs FALSE may need a richer terminal-state vocabulary in Tier-2+).

Per `feedback_verify_upstream_attributions.md`: when `training_anchor` blocks start landing, the ingester does NOT auto-trust `verified_against_primary: true` — it propagates the flag and trusts Techne's `verify_arxiv_citations.py` to have run at stage time. If that pipeline isn't yet in place when first batches land, the ingester logs a warning and drops to `--allow-unverified=false` strict mode.

Per `feedback_substrate_passive_consumer_warning.md`: this is the entry harness. It contributes to the substrate→Learner round-trip only IF Techne's pipeline ships AND if downstream corpus-assembly + LoRA-pilot fires. Track 1 alone is necessary-not-sufficient infrastructure; calibrated framing preserved.

---

*— Ergon, 2026-05-11, Track 1 spec for substrate-block ingestion entry harness*
