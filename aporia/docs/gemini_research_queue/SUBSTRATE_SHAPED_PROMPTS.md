# Substrate-Shaped Gemini Deep Research Prompts — Design Document

**Filed:** 2026-05-11
**Author role:** Aporia / dispatch designer
**Doctrine:** HARD-1 (no paper framing), HARD-2 (anti-gravitational-well — be honest about leverage), HARD-5 (distinct coordinates), `feedback_substrate_passive_consumer_warning.md`, `feedback_verify_upstream_attributions.md`
**Companion to:** `prompt_templates.md`, `queue.jsonl`, `aporia/docs/gemini_research_synthesis_2026-05-11.md`
**Empirical baseline:** 2026-05-10 batch — 18 prompts yielded 11 new anti-anchors + 18 primitive proposals + 9 catalog edits + 4 paradigm candidates, all via narrative reports + Claude-mediated synthesis.

---

## 0. The epiphany in one sentence

> Today, every Deep Research report passes through a human / Claude translation step before it can touch a registry. The proposal: engineer the prompts so the report comes back already-carrying the structured artifacts (anti-anchor entries, primitive specs, composition rules, catalog diffs, training anchors) in fenced, schema-validated YAML blocks, so the synthesis step becomes mechanical extraction rather than interpretation.

This document designs that pipeline, scopes the conditions under which it is genuinely higher-leverage (and the conditions under which it is just shifting work around), and lays out a concrete migration path.

---

## 1. Diagnosis of the current translation step

### 1.1 The pipeline today

```
[queue.jsonl entry]
    -> build_deck_from_queue.py
       (prepends FRAMING + tier-template body)
    -> Gemini Deep Research (~3-10 min per prompt, narrative + tables)
    -> aporia/docs/deep_research_batch_<DATE>/NN_<slug>.md
    -> [Human or Claude reads]
    -> aporia/docs/gemini_research_synthesis_<DATE>.md
       (executive summary + catalog edits table + AA candidates list + primitive proposals list + ...)
    -> [Human-mediated extract step]
       -> append to techne/registry/anti_anchors.jsonl
       -> append to techne/registry/compositions.jsonl
       -> edit aporia/mathematics/tensor_open_problems_v1.md
       -> edit aporia/doctrine/substrate_vocabulary/primitives.md
       -> append to ergon training corpus
```

Five touchpoints, four serial reads, and the registry shape only enters the loop at the very end.

### 1.2 What's lost in translation

**Schema-shape mismatch.** The reports are 7-section narrative + a status-bounds table. The registry is JSONL with strict keys (`id`, `name`, `false_form`, `true_form`, `citation`, `verified_against_primary`, `source_report`). The synthesizer reads the narrative, mentally compiles to JSONL, and pastes. That compile step is lossy: nuance in section 3 (PROBLEM STATEMENT) routinely gets compressed into a single `true_form` sentence, and conditionality qualifiers (the "for `n <= d+1`, tame tensors, and sharp tensors" qualifier on AA-014 Border Comon's, for example) are easy to clip.

**Coordinate-collapse risk (HARD-5).** The reports already cite PATTERN_RANK_PARITY_LEAK as the most-cited pattern in the 2026-05-09 batch. The synthesizer is exposed to exactly the same gradient: when summarizing five distinct rank invariants (`R`, `R-bar`, `sr`, `cr`, `cr-bar`) into a paragraph for the synthesis doc, the temptation to collapse to "rank" is constant. A registry-shaped block forces the writer to list each coordinate as a separate field at write-time.

**Citation provenance gets weaker each step.** Gemini's reports cite primary sources with arXiv IDs and dates. The synthesis doc cites the report number (`report 04 §3`) and the original citation. The downstream JSONL entry often only carries one of these. By the time a primitive lands in `primitives.md`, the chain back to the original arXiv ID can be a single hyperlink — easy to lose under file renames or git history rewrites. Embedding the primary citation directly in the structured block at Gemini-emit time preserves provenance without re-typing.

**Withdrawn-paper detection only at synthesis step.** Lee 2025 (arXiv:2512.15035, withdrawn 2025-12-20) was caught only because Wave 1 of the 2026-05-10 batch happened to verify the Saxl conjecture — the existing AA-004 was previously a wrong-direction anchor saying "Saxl solved." If Wave 1 hadn't run, the false anchor would still be live. The narrative report had to be read end-to-end by a human to surface this; a structured block format that requires a `withdrawn_status: "withdrawn 2025-12-20" | "active"` field on every cited preprint forces the question into every emit.

**Synthesis-doc bias toward narrative coherence.** The synthesis docs read well because they are structured for a reader. But "reads well" is not the registry's goal; the registry's goal is to be ingestible by Ergon, substrate-tester, and downstream agents. The narrative discipline trades off against the ingestion discipline at every step.

### 1.3 Where it's NOT lossy

Honest counter-pressure: some things the narrative format does well and the structured format would do worse.

- **Cross-coordinate synthesis** ("the four-paper cluster on T#24 / T#71 — Boedihardjo, BGJLR, Aden-Ali, Dartois-McKenna — uses four distinct techniques") is a 1-paragraph narrative observation that doesn't map cleanly onto any single substrate block. The synthesis doc earned its keep by spotting that cluster shape.
- **HARD-2 anti-gravity-well calls** ("AlphaEvolve is paradigm-class to register, not roadmap to copy uncritically") are interpretive, not extractive.
- **Surprise findings outside the prompt's scope** (Wave 6 substrate-vocabulary as the highest-leverage wave, surfaced from prompt 18) require a reader noticing.

The right framing is **dual-emit, not replacement**: keep the narrative, add the structured blocks, let the human / Claude reader focus their attention on the things the structured format can't capture.

---

## 2. The substrate-shaped prompt variants

Each variant prepends the existing FRAMING string (in `build_deck_from_queue.py`) and inherits the tier-specific section structure. At the END of the response, the prompt explicitly demands a SUBSTRATE BLOCKS section containing one or more fenced YAML blocks tagged with `# substrate_block: <type>`. Six block types are defined (Section 2.6).

### 2.1 Tier-1 substrate-shaped: anti-anchor verification

**Use when:** queue entry's `template: tier1_aa_verify`. Adds substrate blocks of types `anti_anchor` (the registered or refined AA), `primitive_proposal` (any sub-types or new primitives the verification surfaces), and optionally `catalog_edit` (if a catalog entry needs amending).

**Append this text after Section (d) RECOMMENDATION:**

```
---

**SUBSTRATE BLOCKS (mandatory).**

After your narrative report, emit a SUBSTRATE BLOCKS section containing one or
more fenced YAML blocks, each tagged with `# substrate_block: <type>` on the
first line. Required emissions for a Tier-1 verification:

1. ONE `# substrate_block: anti_anchor` block per anchor verified, capturing
   the registry-shaped version of your final recommendation (status verified /
   refined / inverted, refined citation if needed, exact false_form and
   true_form strings ready to register).

2. ZERO OR MORE `# substrate_block: primitive_proposal` blocks if the
   verification surfaces new substrate primitives or sub-types (e.g. a new
   distinct rank coordinate, a new witness sub-type, a new outside-tier
   negative-cert primitive).

3. ZERO OR MORE `# substrate_block: catalog_edit` blocks if a tensor_open_
   problems_v1.md catalog entry T#XX requires textual amendment (give the
   before-string and after-string verbatim, plus the citation that motivates
   the edit).

Schema for `anti_anchor` blocks (v1.0.0 — strict; pilots have surfaced recurring
failure modes that this hardened template is designed to prevent):

```yaml
# substrate_block: anti_anchor
- _schema_version: "1.0.0"      # REQUIRED const "1.0.0" — must match schema-version regex
  id: "AA-XXX"                  # REQUIRED. Use literal "AA-XXX" placeholder when proposing a
                                # new anchor (parser auto-canonicalizes; ingest assigns next
                                # free AA-NNN at register time). Use "AA-013" form ONLY when
                                # verifying an already-registered anchor. Do NOT invent
                                # descriptive ids like "AA-PNP-RELAT" — if you want to
                                # preserve a semantic descriptive token, put it in
                                # descriptive_id_alias (optional field below) and keep id as AA-XXX.
  name: "RELATIVIZATION_BARRIER_TOTALITY"   # REQUIRED. shortSnakeUpper, max 80 chars. NO bare-noun
                                            # coordinate words ("RANK", "COMPLEXITY", "DIMENSION", "DEGREE")
                                            # without specifier — those collapse HARD-5 distinct coordinates.
  false_form: |                  # REQUIRED. One-sentence false statement an LLM might emit.
    <false statement>
  true_form: |                   # REQUIRED. Min 60 chars. ALL conditional qualifiers verbatim
                                 # (regime restrictions, special-case carve-outs, definitional
                                 # qualifiers like "occurrence vs multiplicity"). Qualifier-clipping
                                 # is the dominant anti-anchor failure mode.
    <true statement with all qualifiers explicit>
  citation: "arXiv:2501.03970"   # REQUIRED. MUST match regex ^(arXiv:\d{4}\.\d{4,5}|\d{2}\.\d{4}/\S+)$
                                 # Examples valid: "arXiv:2501.03970", "10.1090/jams/918", "10.1006/jcss.1997.1494"
                                 # Examples INVALID: "J. Comput. Syst. Sci. 55(1):24-35", "Razborov-Rudich 1997"
                                 # Citations in journal-name format will be rejected. Convert to DOI or arXiv.
  citation_withdrawn_status: "active"   # OPTIONAL. Enum: "active" | "preprint-only" | "withdrawn YYYY-MM-DD"
                                        # DO NOT emit "citation_status" — that field is not in v1 schema.
                                        # If you want to convey peer-reviewed status, use "active"; preprint -> "preprint-only";
                                        # withdrawn -> "withdrawn YYYY-MM-DD" with the exact withdrawal date.
  verified_against_primary: true # REQUIRED boolean. true if you read the primary source, false if you only saw a citation.
  verification_source: "Gemini Deep Research <prompt-id> <YYYY-MM-DD>; primary cite <author> <year> <venue>"
                                 # REQUIRED. Min 8 chars, MAX 240 chars. Free-form provenance string.
                                 # Do NOT exceed 240 chars — split cross-references into separate brief mentions.
  source_report: "<filename of this Gemini report>"   # REQUIRED. Filename of the report this block came from.
  recommended_action: "register-as-new"   # REQUIRED. Enum: "register-as-new" | "refine-existing" | "invert-existing" | "no-change"
                                          # If id is "AA-XXX" placeholder, recommended_action MUST be "register-as-new" (parser will auto-fill if missing).
                                          # If "refine-existing" or "invert-existing", you MUST also include refines_existing_aa_id field.
  refines_existing_aa_id: null    # OPTIONAL when recommended_action is register-as-new; REQUIRED when refine-existing or invert-existing.
                                  # Format: "AA-013" / "AA-014" / etc. (existing canonical ID being refined).
  risk_tier: "high"               # REQUIRED. Enum LOWERCASE: "high" | "medium-high" | "medium" | "low"
                                  # Do NOT emit "HIGH" / "MEDIUM" / capitalized — schema enum is lowercase.
  descriptive_id_alias: "PNP-RELAT"   # OPTIONAL string max ~64 chars. Use to preserve a semantic descriptive token
                                      # when id is the placeholder AA-XXX. The substrate-tester probe surfaces this
                                      # as the human-readable disambiguator at registration time.
```

Common pitfalls these pilots have surfaced repeatedly — your output will be rejected if you:
- Use descriptive ids like "AA-PNP-RELAT" instead of "AA-XXX" (use descriptive_id_alias if you want to preserve the token).
- Cite as journal/venue string instead of arXiv:NNNN.NNNNN or DOI (10.NNNN/...).
- Emit "citation_status" — that field is not in v1; use citation_withdrawn_status with the enum values shown above.
- Use uppercase risk_tier values — must be lowercase enum.
- Omit verification_source or recommended_action — both are required.
- Exceed verification_source maxLength=240.

Schema for `primitive_proposal` blocks (Tier-1 commonly surfaces only Tier-B
sub-types or outside-tier negative certs from anti-anchor work):

```yaml
# substrate_block: primitive_proposal
- name: BellNumberDeterminantBound  # UpperCamelCase
  tier: A++ | B | C | D | E | F | G | outside_tier
  parent_class: ComputationalComplexityCertificate
  sub_types: []  # list of declared sub-type names
  composition_eligibility:
    - tier: D
      required: false
      rationale: <one sentence>
  required_fields:
    - field_characteristic: int  # explicit field key the primitive must carry
    - bell_number_value: int
  anti_anchor_pins: [AA-015]
  downstream_consumer: <substrate-tester probe | Ergon script | catalog edit>
  source_report: T#86 | report 06
  source_citations:
    - arXiv:2301.06586
```

Schema for `catalog_edit` blocks:

```yaml
# substrate_block: catalog_edit
- catalog_file: aporia/mathematics/tensor_open_problems_v1.md
  entry_id: T#86
  field: status_paragraph  # or specific section header
  before: |
    <verbatim current text, copy-pasted from the catalog>
  after: |
    <verbatim replacement text, with all citations inline>
  citation: arXiv:2301.06586
  citation_date: 2024-XX-XX
  edit_type: PROPAGATE | VERIFY-LIVE  # propagate=well-confirmed; verify-live=needs second-pass
  motivation: <one sentence — why this edit is required now>
  source_report: T#86
```

Be terse inside the blocks; verbose-but-precise in the narrative. Do NOT cite
the blocks back in the narrative; the narrative stands on its own and the
blocks are mechanically ingestible.
```

### 2.2 Tier-2 substrate-shaped: frontier survey

**Use when:** queue entry's `template: tier2_frontier_survey`. Tier-2 reports typically yield catalog edits (the 7-section structure already feeds Section 4 STATUS & BOUNDS straight into catalog rows) and primitive proposals (Section 3 PROBLEM STATEMENT calls out distinct coordinates). Heavier on `catalog_edit` and `primitive_proposal` blocks than Tier 1.

**Append this text after Section 7 CROSS-REFERENCES:**

```
---

**SUBSTRATE BLOCKS (mandatory).**

After your 7-section narrative report, emit substrate blocks per the schemas
in this document. Required emissions for a Tier-2 frontier survey:

1. ONE OR MORE `# substrate_block: catalog_edit` blocks for any T#XX entry
   whose current text in `tensor_open_problems_v1.md` is now stale,
   misleading, or incomplete given the literature you surveyed. Bias toward
   small, surgical edits over wholesale rewrites.

2. ZERO OR MORE `# substrate_block: primitive_proposal` blocks for any new
   primitive or sub-type the frontier surfaces, particularly when you
   identified two-or-more distinct coordinates being collapsed into one
   catalog field. Each new coordinate is a primitive proposal.

3. ZERO OR MORE `# substrate_block: anti_anchor` blocks for any "X solved Y
   in 2024-2026" claim that should be pinned as a forward false-anchor
   candidate.

4. ZERO OR MORE `# substrate_block: composition_rule` blocks if your survey
   surfaces a pair of primitives that legitimately compose under literature
   confirmation. Each composition rule must cite the literature confirming
   it. Speculative compositions go in the narrative; only literature-
   confirmed compositions go in the block.

Use the schemas defined in this document. The `composition_rule` schema:

```yaml
# substrate_block: composition_rule
- id: C-XXX  # propose next free ID
  name: TierB_x_TierD_BorderRank_x_PhaseTransition  # descriptive snake_case
  precondition_primitives: [BorderRankWitness, PhaseTransitionThreshold]
  output_primitive: ConstructiveDistributionalWitness
  applicable_attacks: [P29, P15]
  literature_confirmation:
    - citation: arXiv:XXXX.XXXXX
      context: T#73 fire #43
  confirmed: true | false  # true only if 2+ independent literature confirmations
  tiers: [B, D]
  source_report: T#73
  notes: <one paragraph rationale>
```

Be ruthless about Section 4 STATUS & BOUNDS staleness — if the catalog says
omega < 2.371552 and current is 2.371339, emit a catalog_edit block. Every
stale row is a catalog_edit candidate.
```

### 2.3 Tier-3 substrate-shaped: calibration-anchor mining

**Use when:** queue entry's `template: tier3_calibration_mining`. Tier-3 reports surface domain-anchor primitives (Tier-F) and **training anchors** — labeled instances Ergon's calibration battery can verify against ground truth.

**Append this text after Section 7 ANTI-ANCHOR + CROSS-REFERENCES:**

```
---

**SUBSTRATE BLOCKS (mandatory).**

Required emissions for a Tier-3 calibration-anchor survey:

1. ONE `# substrate_block: primitive_proposal` block proposing the Tier-F
   bundle primitive for the domain (e.g. `KnotInvariantBundle`,
   `MaassGL3SpectralBundle`, `AbelianSurfaceArithmeticBundle`), including
   the mandatory sub-types and the schema fields a downstream Ergon script
   would consume.

2. ONE OR MORE `# substrate_block: training_anchor` blocks for the calibration-
   grade known-true-positive sets you surface. A training_anchor block records
   one labeled instance (or a labeled set with explicit count) that Ergon can
   use to verify Learner predictions against ground truth. Schema:

```yaml
# substrate_block: training_anchor
- id: anchor-<domain>-<NNN>
  domain: knots | maass_gl3 | genus2 | tensor | ...
  anchor_type: invariant_value | classification | bound | predicate
  dataset_source: <URL or LMFDB table or paper reference>
  dataset_license: <license string>
  scale:
    instance_count: <int or null if not enumerable>
    coverage_qualifier: <"complete up to conductor N" | "all hyperbolic <= 20 crossings" | etc>
  prompt_template: |
    <natural-language form of the verification question>
  expected_answer_shape: <type description>
  verification_method: analytical_proof | ml_prediction | computational_certified | folklore
  trust_tier: analytically_proven | numerically_certified | ml_predicted | unverified
  source: <primary citation>
  source_date: YYYY-MM-DD
  caveats: |
    <paragraph capturing measure-zero exceptions, AI-prediction admixture, completeness qualifiers>
  consumed_by: <Ergon script path or queue entry>
```

3. ONE OR MORE `# substrate_block: anti_anchor` blocks for any domain-
   specific forward false-anchor candidates you surface (the AA-019 type:
   "LMFDB root numbers are analytically proven" when in fact many are
   ML-predicted via murmuration).

4. OPTIONAL `# substrate_block: catalog_edit` blocks if your survey reveals
   a `tensor_open_problems_v1.md` entry needs cross-domain references.

Be explicit about the analytically_proven | ml_predicted | numerically_certified
trust tier on every training_anchor — Wave 3 of the 2026-05-10 batch
established this as load-bearing for AA-019, AA-020, AA-017.
```

### 2.4 Tier-4 substrate-shaped: methodology / corpus / vocabulary

**Use when:** queue entry's `template: tier4_methodology`. Tier-4 reports are the heaviest yield per fire and produce primitives across Tier-G, substrate-meta primitives (composition rules, type-system constraints), and paradigm candidates.

**Append this text after Section 7 ANTI-ANCHOR + CROSS-REFERENCE:**

```
---

**SUBSTRATE BLOCKS (mandatory).**

Required emissions for a Tier-4 methodology / corpus / vocabulary report:

1. ONE OR MORE `# substrate_block: primitive_proposal` blocks for each new
   primitive or sub-type proposed in Section 6 SUBSTRATE-INTEGRATION
   RECOMMENDATIONS. Tier placement is mandatory; if you propose a primitive
   that doesn't fit Tiers A++/B/C/D/E, propose Tier-F (domain-anchor) or
   Tier-G (method-synthesis) with rationale.

2. ZERO OR MORE `# substrate_block: composition_rule` blocks for any
   composition pattern surfaced by your survey of categorical / type-
   theoretic / operadic foundations.

3. ZERO OR MORE `# substrate_block: anti_anchor` blocks for methodology
   forward false-anchors (the AA-021/AA-022/AA-023 type).

4. OPTIONAL `# substrate_block: paradigm_candidate` block if your survey
   proposes a new attack paradigm class (PXX). Schema:

```yaml
# substrate_block: paradigm_candidate
- id: P-CANDIDATE-<name>  # use P-CANDIDATE until confirmed, then assign P32+
  proposed_id_if_promoted: P32 | P33 | ...
  name: EvolutionaryLLMSynthesis
  sub_tactics: [IslandPopulationArchitecture, CascadeEvaluationGate, ...]
  confirmation_status: concrete_deliverable | future_promise | speculation
  required_independent_confirmations: 2  # substrate-tester saturation rule
  current_confirmations:
    - citation: arXiv:XXXX.XXXXX
      context: <T#1 / report 10>
  literature_anchors:
    - <primary citation>
  source_report: report 10
  promotion_gate: |
    <what additional evidence is needed to promote from candidate to active>
```

Tier-4 reports often surface 5-10 primitives in a single fire (Wave 4 of the
2026-05-10 batch surfaced 14). Use multiple primitive_proposal blocks (one
per primitive); do NOT bundle into a single block.
```

### 2.5 Variant for narrow re-verifications

When a queue entry is a re-verification of an existing AA-NNN (every 90-120
days per the existing protocol), the substrate-shaped variant collapses to a
single `# substrate_block: anti_anchor` emission whose only fields are
`id`, `last_verified`, `verification_source`, `verified_against_primary`, and
either `no_change: true` or the specific field updates. This avoids re-emitting
the whole anchor at re-verify time.

### 2.6 The six block types — one-line summary

| Block type | Primary registry target | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---|---|---|---|---|
| `anti_anchor` | `techne/registry/anti_anchors.jsonl` | mandatory | optional | optional | optional |
| `primitive_proposal` | `aporia/doctrine/substrate_vocabulary/primitives.md` | optional | optional | mandatory (Tier-F) | mandatory (multiple) |
| `composition_rule` | `techne/registry/compositions.jsonl` | rare | optional | rare | optional |
| `catalog_edit` | `aporia/mathematics/tensor_open_problems_v1.md` (+ future calibration_anchors_v1.md) | optional | mandatory if stale | optional | optional |
| `training_anchor` | new file: `techne/registry/training_anchors.jsonl` | rare | rare | mandatory | rare |
| `paradigm_candidate` | new file: `aporia/doctrine/paradigm_candidates.jsonl` | rare | rare | rare | optional |

Six distinct schemas, each preserving its own coordinates (HARD-5): no field is shared across schemas except the embedded citation, which is normalized to `{arXiv:..., journal:..., date:...}` structure.

---

## 3. The ingestion pipeline

A new pipeline runs **after** each Gemini Deep Research return, **before** the synthesis doc is written.

### 3.1 Steps

1. **Parse.** `aporia/scripts/parse_substrate_blocks.py <report_dir>` scans every `.md` file in the directory, extracts every fenced code block tagged `# substrate_block: <type>` (regex: `^# substrate_block: (\w+)$` on first line inside the fence), parses the YAML, and emits a flat list of `(type, payload, source_file, source_line)` tuples.

2. **Validate.** `aporia/scripts/validate_substrate_blocks.py <parsed.jsonl>` runs each block through a Pydantic / `dataclasses` schema validator. Schemas live at `techne/contracts/substrate_block_schemas.py` (new module) with one `@dataclass(frozen=True)` per block type. Validation failures are written to a `validation_errors.jsonl` file with the source_file and source_line; the human reviewer fixes them inline in the report's substrate block before re-running validate.

3. **Stage.** Valid blocks are written to `aporia/docs/staged_substrate_blocks/<YYYY-MM-DD>/<type>.jsonl`. One staging file per block type per batch date. The staging files are git-tracked but explicitly NOT linked from any canonical registry until the review step approves them.

4. **Review.** Human or Claude inspects the staging files. The review step is the only step in this pipeline where narrative-level judgment is necessary (does the anti-anchor's `true_form` correctly capture the conditional qualifiers? does the primitive_proposal's `composition_eligibility` field misclassify? does the catalog_edit's `before` string actually match the current catalog text?). The reviewer emits either `approved: true` or `approved: false` with a `review_note` on each block, written into a `<type>_reviewed.jsonl` next to the staging file.

5. **Ingest.** `aporia/scripts/ingest_substrate_blocks.py --date <YYYY-MM-DD>` reads the `_reviewed.jsonl` files, filters to `approved: true`, and appends to the canonical registries:
   - `anti_anchor` -> `techne/registry/anti_anchors.jsonl` (with newly assigned AA-NNN IDs if the block said `AA-XXX`)
   - `composition_rule` -> `techne/registry/compositions.jsonl`
   - `primitive_proposal` -> `aporia/doctrine/substrate_vocabulary/primitives.md` (markdown section append, structured by tier — this is the one ingestion target that is markdown, not JSONL)
   - `catalog_edit` -> applies the diff to `aporia/mathematics/tensor_open_problems_v1.md` via a `before -> after` string replace (script verifies the `before` string is unique in the catalog before applying)
   - `training_anchor` -> `techne/registry/training_anchors.jsonl` (new file)
   - `paradigm_candidate` -> `aporia/doctrine/paradigm_candidates.jsonl` (new file)

   Each ingest writes a one-line CHANGELOG entry to `techne/CHANGELOG.md` referencing the source report and date.

### 3.2 Idempotency and re-runs

The parse and validate steps are idempotent. The ingest step is NOT idempotent (it appends to canonical registries), so it carries a `--dry-run` flag for review and emits a digest of "would append N anti-anchors, would apply M catalog edits, would create K new staged_substrate_blocks files" before doing any write. The script refuses to ingest a block whose proposed `AA-XXX` ID already exists in the registry unless `--force-renumber` is passed.

### 3.3 Schema versioning

Every block carries an implicit schema version pinned at parse time. The validator looks up the schema version against `techne/contracts/substrate_block_schemas.py`'s `SCHEMA_VERSION` constant (start at `0.1.0`). If a future change breaks the schema, old reports remain parseable (the parse step is dumb regex), but the validator rejects them with a clear "schema_version mismatch: report emitted under v0.1.0, current is v0.2.0" message. The fix is to re-emit the original Gemini prompt under the new schema, or to write a schema migration in `aporia/scripts/migrate_substrate_blocks.py`.

---

## 4. Risks and limitations

This is where HARD-2 demands honesty.

### 4.1 Hallucinated structured output risk

Gemini may emit a substrate block whose `citation: arXiv:XXXX.XXXXX` field points to an arXiv ID that doesn't exist, or that points to a real paper that doesn't say what the block claims. This is the same risk as in the narrative format, but with two new dynamics:

- **Worse:** structured output looks ingestible, so a tired reviewer may stamp `approved: true` without re-reading the cited paper. The narrative format forces some level of reader engagement.
- **Better:** the citation lives in a known field name. A validator can call out to the arXiv API to verify the arXiv ID exists, that the title matches the cited title, and (for withdrawn status) that the paper is not flagged withdrawn. This is mechanical pre-review hygiene that the narrative format cannot easily automate.

**Mitigation:** add an `arxiv_verify` step between parse and stage: for every block that names an arXiv ID, fetch the abstract page, verify existence, title hash, and `withdrawn` flag. Block any ingest where the verification fails or `withdrawn` is set with `withdrawn_status: active`. Concrete script: `aporia/scripts/verify_arxiv_citations.py <parsed.jsonl>`. This is the single most valuable hardening.

### 4.2 Schema lock-in

If the substrate schema evolves, old reports become stale. Concretely: if v0.2.0 adds a mandatory `risk_tier` field to `anti_anchor` blocks, every report emitted under v0.1.0 becomes non-ingestible without a migration. The migration can be mechanical (set `risk_tier: unknown`) but it's still a workflow cost.

**Mitigation:** keep schemas additive whenever possible (new optional fields, never new mandatory fields). Reserve mandatory-field additions for explicit "schema break window" events analogous to the contract-change windows for substrate primitives. Version the schema in the validator; refuse to ingest under a version mismatch; require manual migration to upgrade.

### 4.3 Prompt size bloat

Doctrine framing (~300 words) + 7-section structure (~400 words of instructions) + substrate-shaping instructions (~800 words for all six block types) = roughly 1500 words of preamble before the topic is named. The 2026-05-10 batch's prompts are ~600 words of preamble; this proposal more than doubles that. Two concerns:

- **Quality dilution.** Gemini may spend more output budget on the substrate blocks (mechanical YAML) and less on the substantive narrative. The reports may get terser. The 2026-05-10 batch's reports averaged ~3500 words and the depth of attribution was load-bearing.
- **Latency / cost.** Deep Research is rate-limited at 20 tokens/day; the prompts are token-budgeted as well as time-budgeted.

**Mitigation:** the substrate-shaping instructions should be **lean per-tier** rather than full-schema-dump. Each tier's prompt only includes the schemas for the block types it commonly emits. Tier 1 includes anti_anchor + primitive_proposal + catalog_edit schemas (~400 words). Tier 4 includes all six (~700 words). This trades schema-DRY for prompt-leanness; acceptable.

**Mitigation 2:** the schemas themselves can be shipped as a reference URL or as a single line ("Use the schemas at `techne/contracts/substrate_block_schemas.md`") — Gemini Deep Research follows URLs. This is brittle if URL contents drift, but during pilot it may be the right compression.

### 4.4 Validation false-positives

A loose schema accepts a block that is syntactically valid but semantically garbage. Example: an `anti_anchor` block with `false_form: ""` (empty string) and `true_form: "TBD"` passes a "non-null string" validator but is useless.

**Mitigation:** tight schemas with min-length / regex constraints on every text field. `false_form` and `true_form` minimum 40 characters. `citation` regex-matched to `arXiv:\d{4}\.\d{4,5}` or `\d{2}\.\d{4}/\w+`. Trust tier enum strictly enforced. First-N batches go through human review on every block (no auto-approve) until the schema's failure modes are characterized.

### 4.5 The narrative-format-outperforms condition

When does the narrative format outperform the substrate-shaped format?

- **Open-ended scouting prompts.** "Survey adjacent fields for ideas substrate could borrow" (Tier-4e, the most exploratory variant) is not well-served by a schema. The output is intentionally diffuse. A substrate block forces structure where none belongs.
- **Single-fire questions where the answer is a yes/no.** Re-verification of an existing AA every 90 days mostly produces "still verified, no change." The 6-block schema is overkill.
- **Methodology decomposition prompts where the value is the architectural narrative** (Wave 4 prompt 10 on AlphaEvolve). The forensic reproduction of the four required architectural compensations is a paragraph, not a YAML block. Forcing it into a primitive_proposal compresses out the insight.

**Practical rule:** keep the narrative format for re-verifications and for explicitly-scouting prompts. Use the substrate-shaped format for the high-volume Tier-2 and Tier-3 prompts where catalog edits and primitive proposals are the primary deliverable.

### 4.6 Is this genuinely higher-leverage or just shifting work?

Honest answer: **partially genuinely higher-leverage, partially shifting work, depending on the bottleneck.**

Genuinely higher-leverage:
- The arXiv-citation auto-verification is automation that the narrative format cannot easily support. This catches Lee-2025-shaped withdrawals at parse time, not at synthesis time.
- The HARD-5 discipline is enforced at write-time (Gemini must enumerate the rank coordinates as separate fields) rather than at read-time (synthesizer must remember not to collapse them).
- The schema versioning + ingestion idempotency lets the substrate handle reports asynchronously: a report can sit unread for a week and still be safely ingested when reviewed.

Shifting work:
- The reviewer still has to read the narrative AND inspect the blocks. Two surface areas instead of one. The hope is that the blocks are mechanical to inspect, but a tired reviewer who rubber-stamps `approved: true` produces worse output than the current "Claude reads carefully and writes synthesis."
- The structured format is brittle to prompt-engineering drift. If Gemini changes how it formats fenced blocks across a version update, the parse step breaks. The narrative format has no such fragility.

The honest leverage gain is the **arXiv-verification step plus the HARD-5 write-time discipline.** The rest is either neutral or work-shifting. I'd estimate the genuine leverage at 30-50% improvement in yield per fire, mostly through reducing the rate at which subtle conditional qualifiers get clipped during synthesis-doc writing.

---

## 5. Concrete migration plan

### 5.1 Pilot (1 day)

Pick 3 queue entries with diverse block-type profiles:

- **DR-001** (Tier-1 AA verification: AA-013 Strassen direct-sum). Expected substrate blocks: 1 anti_anchor (refined AA-013), 1 primitive_proposal (`SmallTensorAdditivitySafeZone` sub-type), 1 catalog_edit (T#6 / T#23 row). Simple block set, mechanical schema fit.
- **DR-007** (Tier-1 AA verification with high downstream-script urgency: AA-019 LMFDB GL(3) root number). Expected: 1 anti_anchor, 1 primitive_proposal (`MaassGL3SpectralBundle.RootNumber` schema), 1 training_anchor (LMFDB GL(3) gold set with `analytically_proven` partition). This pilots the training_anchor schema.
- **A Tier-3 calibration-mining queue entry** if one is queued (e.g. a knots-domain follow-up). Expected: full Tier-F bundle primitive_proposal + 3-5 training_anchor blocks. Pilots the heaviest schema usage.

Fire all three with substrate-shaped variants. **Also fire one of them in parallel under the existing narrative-only template.** Compare:

- Did the substrate-shaped version preserve the same narrative quality as the narrative-only?
- How many blocks emitted? How many parse / validate clean?
- How many human-review interventions on the blocks vs. the narrative?
- arXiv-verify hit rate (real citations vs hallucinated)?

Decision criteria for go/no-go:
- **GO** if all three substrate-shaped reports validate clean (no parse / no schema failures) and the narrative section is no shorter than 70% of the narrative-only version's length and the arXiv-verify pass rate is >= 90%.
- **NO-GO** if narrative quality drops materially or if more than one block per report fails schema validation. Iterate prompt design and retry.

### 5.2 Roll-out (1 week)

Conditional on pilot GO:

- Day 1-2: build `parse_substrate_blocks.py` + `validate_substrate_blocks.py` + `verify_arxiv_citations.py`. Single-file, no dependencies beyond `pyyaml` and `requests`.
- Day 3: write the six block-type schemas in `techne/contracts/substrate_block_schemas.py` as frozen dataclasses. Each schema explicitly mirrors an existing registry's JSONL shape.
- Day 4: modify `build_deck_from_queue.py` to inject the substrate-shaped variant per-tier. Add a `--substrate-shaped` flag so the old prompt-only mode remains available.
- Day 5: fire a full 20-token batch under substrate-shaped variants. Run the parse / validate / arXiv-verify pipeline end-to-end. Stage all blocks. Review approval rate.
- Day 6: build `ingest_substrate_blocks.py`. Ingest the first batch with extensive review (no auto-approve). Measure the time per block reviewed; target is <= 90 seconds per block sustained.
- Day 7: write `migrate_substrate_blocks.py` placeholder (empty handler), document the schema versioning protocol in `techne/contracts/substrate_block_schemas.md`, commit.

### 5.3 Steady state (ongoing)

After roll-out:

- Every burn (20 tokens) produces ~20 reports each carrying 2-10 substrate blocks. Total blocks per burn: ~80-200.
- The synthesis doc shrinks: it becomes "what was approved this batch, what was rejected and why, what cross-domain patterns the blocks revealed that no single block could capture." Aim for 800-1500 words instead of the current ~3000-5000.
- The bulk of the synthesis-doc value pivots from "extract structured artifacts from narrative" (mechanical now) to "spot the cross-cutting patterns the blocks individually cannot see" (the part the narrative format does well).
- The reviewer's time-per-burn drops from 60-90 minutes of synthesis-doc writing to 30-45 minutes of block review + 30 minutes of cross-pattern note-writing.

### 5.4 The rollback condition

If after 2-3 burns the substrate-shaped format is producing worse narratives than the narrative-only format, OR if the reviewer is rubber-stamping blocks without engagement, roll back. The substrate-shaped format is a tool for the reviewer; if it's degrading the reviewer's attention, it is net-negative regardless of how clean the schemas look.

---

## 6. Tooling recommendation

Scripts to build (all in `aporia/scripts/`):

| Script | Inputs | Outputs | LOC estimate |
|---|---|---|---|
| `parse_substrate_blocks.py` | directory of report `.md` files | flat `parsed_substrate_blocks.jsonl` with `(type, payload, source_file, source_line)` | ~80 |
| `validate_substrate_blocks.py` | `parsed_substrate_blocks.jsonl` | `validated_substrate_blocks.jsonl` + `validation_errors.jsonl` | ~120 |
| `verify_arxiv_citations.py` | validated blocks | annotated blocks with `arxiv_verified: true / false / withdrawn` | ~100 |
| `stage_substrate_blocks.py` | verified blocks | `aporia/docs/staged_substrate_blocks/<YYYY-MM-DD>/<type>.jsonl` | ~60 |
| `ingest_substrate_blocks.py` | reviewed blocks | appends to canonical registries; emits CHANGELOG; verifies `before` strings unique | ~200 |
| `migrate_substrate_blocks.py` (placeholder) | old-schema blocks | new-schema blocks per migration version | ~50 (initial empty) |

Modifications to existing scripts:

- `aporia/scripts/build_deck_from_queue.py` — add `--substrate-shaped` flag; load per-tier substrate-shaping appendix from a new file `aporia/docs/gemini_research_queue/substrate_shaping_appendix_<tier>.md`; concatenate framing + tier-template-body + substrate-shaping-appendix. Six lines of code change plus the appendix files.

New canonical files:

- `techne/contracts/substrate_block_schemas.py` — frozen dataclasses for all six block types
- `techne/contracts/substrate_block_schemas.md` — human-readable schema docs
- `techne/registry/training_anchors.jsonl` — new registry for training-anchor blocks
- `aporia/doctrine/paradigm_candidates.jsonl` — new registry for paradigm-candidate blocks
- `aporia/docs/gemini_research_queue/substrate_shaping_appendix_<tier>.md` — four files, one per tier, holding the substrate-shaping instructions appended to each tier's prompt

Total new code: roughly 600-800 LOC across 6 scripts plus 4 prompt-appendix markdown files plus 2 new registry files plus 1 schema module plus 1 schema doc. Manageable in 2-3 focused engineering days.

---

## 7. Expected yield delta vs. baseline

The 2026-05-10 batch yielded 11 new AAs + 18 primitives + 9 catalog edits + 4 paradigm candidates from 18 prompts. Substrate-shaped variants would be expected to:

- **Match or marginally exceed** the absolute counts (perhaps 12-14 AAs, 20-25 primitives, 10-12 catalog edits, 4-5 paradigm candidates), because forcing structured emission tends to surface a few more candidates that the narrative format would have folded into the body text.
- **Strictly improve** the per-artifact fidelity: every AA carries its conditional qualifiers in a structured field; every primitive carries its composition_eligibility explicitly; every catalog_edit carries the exact before/after strings; every training_anchor carries the trust-tier enum.
- **Strictly improve** the per-artifact provenance: every block carries arXiv-verified citations with publication dates.
- **Reduce** the time from report return to canonical ingestion: from current ~60-90 minutes of synthesis-doc writing + manual extract to ~30-45 minutes of block review + 15-30 minutes of cross-pattern annotation. Roughly 30-50% time saving per burn.
- **Add new failure modes**: schema-validation failures on Gemini drift, arXiv-verify failures on cited-but-non-existent papers, false-positive auto-approvals from rubber-stamp review. Mitigated by the review-step discipline.

Honest expectation: the yield count goes up modestly, the yield fidelity goes up materially, the reviewer time goes down modestly, and one new class of failure (schema drift) appears.

---

## 8. Honest assessment — would I bet on this being higher-leverage?

**Yes, but bounded.** The genuine leverage gains are concrete and mechanical: arXiv-citation auto-verification, HARD-5 discipline enforced at write-time, schema-versioned async ingestion. These three together justify the build.

The leverage is **not** "10x." It's roughly "30-50% better yield-per-fire fidelity + 30-50% reviewer time saving." That's enough to be worth doing, especially since the marginal cost (one week of script writing + one tuning iteration) is low.

The leverage gain compounds the more burns you run. At one burn per week (20 tokens), the time saving is 30 minutes per week. At one burn per day during high-pressure substrate-change windows, the time saving is 30 minutes per day. The substrate-shaped format pays for itself faster the harder you're firing.

The leverage gain does NOT compound the better the reports get. As Gemini's narrative quality improves over time, the marginal value of structured-block extraction declines (because the synthesizer is doing less extraction work to begin with). If Gemini gets dramatically better at narrative coherence over 2026, this proposal's value erodes.

The leverage gain does NOT eliminate the reviewer. The reviewer is still load-bearing for catching cross-cutting patterns, anti-gravity-well calls, and HARD-2 interpretive moves. The substrate-shaped format frees the reviewer from extraction work; it does not free them from interpretation work. That's the right division of labor and matches the existing `feedback_forge_division.md` doctrine ("APIs mine cheap ore in bulk; Claude Code forges gems from near-misses").

**The bet:** build the substrate-shaped pipeline in week 1 (pilot + scripts), measure yield delta over batches 2-4 (weeks 2-4), then evaluate keep / iterate / rollback. The downside is bounded (week of engineering); the upside is permanent reviewer-time reduction and material fidelity gain. Worth doing.

The condition under which this is NOT worth doing: if the dispatch frequency drops below one burn per two weeks, the amortization doesn't work and the engineering cost dominates. As of 2026-05-11 the dispatch is firing at roughly one burn per day during active windows, so the amortization works. Re-evaluate if dispatch frequency drops materially.

---

End of design document.
