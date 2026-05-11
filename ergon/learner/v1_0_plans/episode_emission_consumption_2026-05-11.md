# Episode-Emission Consumption Capacity — Ergon-Side

**Filed:** 2026-05-11 by Ergon (Learner owner)
**Track:** Track 2 of `ergon/PROMPT_2026-05-11_substrate_first.md`
**Status:** **PARTIAL** — pre-Techne-audit-prep scaffold. This doc captures what `learner_enrichment.py` can consume TODAY for each of the 8 substrate opcodes. When Techne's audit-prep doc lands at `techne/diagnostics/dims_2_3_10_audit_prep_2026-05-11.md`, the per-opcode gaps section gets filled by cross-reference.
**Upstream:** Techne's Track 2 in `techne/PROMPT_2026-05-11_substrate_first.md` — Dims 2/3/10 audit-prep.
**Convention:** No new opcode proposals from Ergon side. This is a CONSUMPTION check, not a contract-change proposal.

---

## §0 What this doc is — and what it depends on

**Is:** Ergon's per-opcode consumption-capacity inventory. For each of the 8 Σ-kernel opcodes (TRACE, CLAIM, FALSIFY, GATE, ERRATA, REWRITE, PROMOTE, EXCLUSION), what fields of `LearnerRecord` (`prometheus_math/substrate_generation/learner_enrichment.py:79-86`) can be populated from current substrate emissions vs require an emission addition.

**Depends on:** Techne's audit-prep doc at `techne/diagnostics/dims_2_3_10_audit_prep_2026-05-11.md` for the *emission* side. This doc owns the *consumption* side. Cross-reference produces the gap analysis.

**Doctrine:** HARD-2 (no new opcodes; consumption shapes around existing emission), `feedback_substrate_passive_consumer_warning.md` (every line in here must trace to a behavior delta — currently the closest behavior delta is the 4-condition pilot LoRA, deferred per pivot).

---

## §1 Reference: what `LearnerRecord` consumes today

Per `learner_enrichment.py:79-86`, a `LearnerRecord` has 8 fields:

1. `underlying_record_hash` — SHA256 of substrate `DiscoveryRecord.candidate_hash` (or, in the training-anchor ingestion path, SHA256 of canonical anchor blob — see `ergon/learner/v1_0_plans/training_anchor_ingestion_spec.md` §1.3).
2. `episode_id` — equals `underlying_record_hash` in Tier-1 (1:1).
3. `episode_phase` — single-phase `"evaluate"` in Tier-1; future phases include `"claim"`, `"falsify"`, `"promote"`, `"errata"`.
4. `verification_tier` — read from `CoordinateChart.canonicalization.decidability_status` via `lookup_verification_tier()`.
5. `chart_id` — `f"{domain}:{region_key}"` if a registered chart applies, else `None`.
6. `decoy_kind` — `"seeded_survivor"` / `"known_kill"` / `None`.
7. `kill_signature` — `Tuple[str, ...]`, 7 recognized first-element kinds + `"other"` fallback.
8. `outcome_class` — `"rejected"` / `"survived"` / `"promoted"` / `"errored"`.

The 4 calibration-gate metrics that depend on each field:

| Gate | Consumes |
|---|---|
| Calibration preservation (Gate 1) | `verification_tier`, `outcome_class`, `kill_signature` (must distinguish KC-tier vs BS-tier) |
| Falsification-test choice (Gate 2) | `kill_signature[0]` (the test that DID fire), `episode_id` (for counterfactual completeness — Dim 2) |
| Near-miss repair (Gate 3) | requires Dim 5 + Dim 8 emissions not yet shipped |
| Search distribution shift (Gate 4) | requires Dim 2 + Dim 10 — counterfactual completeness + cross-fire replication |
| Cross-domain transfer (Gate 5) | `domain` masking; `chart_id` must be separable from label tokens — verified in Dim 9 anti-leakage at Tier-1 |

---

## §2 Per-opcode consumption status (8 opcodes)

For each opcode, the table records: (a) what `LearnerRecord` field that opcode's emission would populate, (b) whether the current substrate emits a sufficient signal, (c) whether the deferred Dims 2/3/10 affect it.

### §2.1 TRACE

**Function (Σ-kernel):** Records the candidate's path through the kernel state machine.
**Consumes into:** `episode_id` (binding context), `episode_phase` ("trace" is not a current phase enum value — would map to "evaluate" in Tier-1).
**Sufficient today?** TBD — depends on whether TRACE emits a record that can be JOINED with downstream CLAIM/FALSIFY/PROMOTE via `episode_id`. If TRACE emissions carry no `candidate_hash`, joining is brittle (Dim 1 episode-density gap).
**Gap candidate:** Awaiting Techne audit-prep §[TRACE].

### §2.2 CLAIM

**Function:** Records a candidate's substrate-side proposed claim status.
**Consumes into:** `episode_id`, `kill_signature[0] = "claim"` (would require extending the 7 enum kinds).
**Sufficient today?** Partially — Tier-1 only emits at `"evaluate"` phase, CLAIM is downstream. The 1:1 `episode_id = underlying_record_hash` mapping means CLAIM emissions sharing the same candidate join cleanly.
**Counterfactual completeness (Dim 2):** Does CLAIM carry the *alternative* claims considered? If yes, the policy-step that selected this CLAIM is recoverable (Gate 2 trainable). If no, the policy is opaque and Gate 2 reverts to imitation.
**Gap candidate:** Awaiting Techne audit-prep §[CLAIM] for "counterfactual completeness on CLAIM" answer.

### §2.3 FALSIFY

**Function:** Records the kill applied + the test selected.
**Consumes into:** `kill_signature` (the test that fired), `outcome_class` ("rejected"), `verification_tier` (the chart that decided the kill).
**Sufficient today?** Yes for Tier-1 deg-12 Lehmer corpus — `derive_kill_signature` covers f1/f6/f9/f11_killed, reducible, out_of_band, catalog_hit. The 7 kinds were validated against the smoke run.
**Counterfactual completeness (Dim 2):** Does FALSIFY emit which tests were CONSIDERED and rejected? In Tier-0/Tier-1 the test order is hard-coded in `discovery_pipeline` — implicit counterfactual. For Gate 2 training the counterfactual needs to be EXPLICIT in the emission.
**Gap candidate:** Awaiting Techne audit-prep §[FALSIFY].

### §2.4 GATE

**Function:** Promotion gate — decision boundary between FALSIFY and PROMOTE.
**Consumes into:** `outcome_class`, `verification_tier`.
**Sufficient today?** Partially — GATE in Tier-1 is binary (promoted vs not). The actual gate-criterion (which check fired the promotion) is encoded in `kill_signature` only when negative.
**Calibration-tier provenance (Dim 3):** Does GATE emit the underlying claim's calibration tier (KC-001-style anchor vs BS-001-style blind-spot)? Currently `verification_tier` reads `CoordinateChart.canonicalization.decidability_status` (decidable/undecidable/conditional/unknown), which is NOT the KC/BS tier. **This is the Dim 3 gap.** Without GATE emitting KC/BS tier, Gate 1 calibration preservation can't be enforced post-train.
**Gap candidate:** Strongly suspected — awaiting Techne audit-prep §[GATE] for confirmation.

### §2.5 ERRATA

**Function:** Records a correction to a previously-emitted record.
**Consumes into:** `episode_phase = "errata"`, `outcome_class` (the corrected terminal_state).
**Sufficient today?** TBD — ERRATA is rare in Tier-0/Tier-1 throughput; it surfaces as a same-day correction (like the Saxl errata) typically at the doc level, not the substrate-emission level.
**Cross-fire replication tagging (Dim 10):** ERRATA is one of the natural triggers for replication-status downgrade. If a record gets erratized in fire N, its `replication_status` should flip from "single-fire" to "fire-corrected" — currently no such field exists.
**Gap candidate:** Awaiting Techne audit-prep §[ERRATA].

### §2.6 REWRITE

**Function:** Records a substrate-side claim mutation (smallest viable modification preserving identity-of-claim).
**Consumes into:** Would populate a near-miss-repair record; currently no LearnerRecord field captures this directly.
**Sufficient today?** No — REWRITE is one of the Dim 5 (process traces) opcodes that current generators don't route through. Per Techne's earlier reply, REWRITE/EQUIV could carry process steps when the Learner needs them; that emission path is the Dim 5 deferred gap.
**Near-miss attribution (Dim 8 from earlier discussion):** REWRITE is the natural place to attach near-miss attribution. Without REWRITE in the emission stream, repair-policy training (Gate 3) has no training signal.
**Gap candidate:** Deferred per Techne's "Dim 5 reclassified as real-gap, not easy-fix."

### §2.7 PROMOTE

**Function:** Final-state PROMOTE; the claim becomes a substrate-grade Symbol.
**Consumes into:** `outcome_class = "promoted"`.
**Sufficient today?** Yes for binary promote/not-promote. PROMOTE in Tier-1 deg-12 Lehmer corpus emits records consumable by `learner_enrichment.enrich(...)`.
**Calibration-tier provenance (Dim 3):** Same gap as §2.4 GATE — PROMOTE doesn't emit KC/BS tier.
**Gap candidate:** Inherited from §2.4.

### §2.8 EXCLUSION

**Function:** Scope-bounded kill (exclusion certificate with explicit applicability scope).
**Consumes into:** `kill_signature` (would benefit from a new kind tag), `chart_id` (the chart that defines the exclusion scope).
**Sufficient today?** Partially — EXCLUSION is shipped per `sigma_kernel/exclusion_certificate.py`; the consumption path is to record exclusion in `kill_signature` as a structured signature. Currently `derive_kill_signature` has no EXCLUSION-specific first-element kind; falls into `"other"` bucket. **Substrate-grade note:** scoped exclusions are valuable training signal for Gate 4 (search distribution shift) — a model that learns "X is excluded in scope Y" is closer to a falsification-routing Learner than a model that learns "X is killed in all cases."
**Gap candidate:** Minor — `derive_kill_signature` could add `"exclusion"` as an 8th kind once Techne audit confirms the substrate-side emission shape.

---

## §3 Consolidated gap inventory (pending Techne audit-prep cross-reference)

| Gap ID | Description | Tied to Dim | Status |
|---|---|---|---|
| EEC-001 | TRACE → episode binding via `candidate_hash` | Dim 1 (episode density) | Awaiting Techne §[TRACE] |
| EEC-002 | CLAIM counterfactual completeness | Dim 2 | Awaiting Techne §[CLAIM] |
| EEC-003 | FALSIFY counterfactual completeness | Dim 2 | Awaiting Techne §[FALSIFY] |
| EEC-004 | GATE / PROMOTE KC/BS tier provenance | Dim 3 | **Strongly suspected gap** — confirmed once Techne audit lands |
| EEC-005 | ERRATA replication-status emission | Dim 10 | Awaiting Techne §[ERRATA] |
| EEC-006 | REWRITE not routed through (process traces) | Dim 5 | Deferred per Techne's pre-audit reply |
| EEC-007 | EXCLUSION `kill_signature` 8th-kind extension | (consumption refinement) | Minor; out-of-scope until pilot evidence |

**Note:** EEC-006 (Dim 5) is explicitly classified as "real-gap" by Techne and parked for pilot-evidence triage. EEC-004 (Dim 3 KC/BS tier provenance) is Ergon's strongest suspicion of a load-bearing gap for the calibration-preservation gate; the audit-prep doc will confirm or refute.

---

## §4 No-new-opcode discipline preserved

Per the prompt's "No new opcode proposals; this is a consumption check, not a contract change":

- **None of EEC-001 through EEC-007 propose new opcodes.** Each is a request for additional emission fields on existing opcodes.
- **No `LearnerRecord` schema changes** proposed. All gaps are described in terms of what the existing 8 fields would consume from richer emissions.
- **EEC-007 EXCLUSION** is the closest to a substrate-side request — but it's an internal `derive_kill_signature` refinement, not a contract change.
- **Trust-tier mapping** (training-anchor ingestion §2.1) is an Ergon-side convention, not a substrate emission requirement.

---

## §5 What this doc does NOT do

- Does NOT pre-judge what Techne's audit-prep will say. The "awaiting" entries in §3 are explicitly conditional.
- Does NOT propose specific emission additions to TRACE/CLAIM/FALSIFY/etc. Techne owns the emission side; Ergon's job here is to document consumption capacity so the gap analysis is fast when both sides are on the table.
- Does NOT request the pilot LoRA fire. Stand-down on compute/training preserved per pivot.
- Does NOT modify any existing Σ-kernel contract.
- Does NOT proxy for cross-fire replication discipline. EEC-005 ERRATA replication-status is one specific surface; the broader Dim 10 replication-status tagging requires a separate substrate-side decision.

---

## §6 Next action — when Techne audit-prep lands

When `techne/diagnostics/dims_2_3_10_audit_prep_2026-05-11.md` is filed:

1. Read it section-by-section.
2. For each of the 8 §2.x opcode sections in this doc, fill in the "Sufficient today?" + "Gap candidate" rows from Techne's emission spec.
3. Update §3 gap inventory with confirmed vs ruled-out status.
4. Append a 1-2 paragraph "consolidated gap response" summarizing which gaps Ergon believes block pilot LoRA training (vs which are nice-to-haves).
5. File a reply ticket to `aporia/meta/queue/techne_inbox.jsonl` (P2-medium) per Track 2 prompt.

This doc structure is designed for fast post-audit cross-reference, not pre-emption.

---

*— Ergon, 2026-05-11, Track 2 consumption-capacity scaffold pre-Techne-audit*
