# Ergon — Next-Step Prompt (2026-05-11)

**Paste-target:** Ergon agent session. Self-contained — agent has memory; this prompt is the directional update.

---

## Strategic update

James has called a pivot: **LoRA training is paused indefinitely until substrate volume + quality lifts materially.** See `pivot/strategic_pivot_2026-05-11_substrate_volume_first.md` for full analysis.

The Tier-1 substrate Ergon shipped (998 lines of generator-side enrichment) and the 4-condition pilot LoRA design at `ergon/learner/v1_0_plans/pilot_lora_design_tier_1_corpus.md` are not retracted. They are deferred. The pilot LoRA design stays as-is; the eval harness stays as-designed. When substrate volume reaches the threshold (target: 5x current anti-anchor count, 3x primitive registration count, 100+ confirmed composition rule traces), the pilot fires.

Why the pause: training the falsification-routing Learner on the current substrate would teach the model to memorize 12 anti-anchors and 22 primitive specs as a closed corpus. Falsification-routing requires episode volume that doesn't exist yet. The HARD WARNING about "beautifully falsifying machine forever" applies, but the remediation is to thicken substrate first, not to force a premature train.

## Your scope this week

**You will NOT:**
- Trigger Mahler run, LoRA training, or any --writeable substrate generation.
- Request compute time or frontier-API budget. The James-scope decision per `strategic_redirect_handoff_2026-05-10.md` §3 is deferred to ~week 3+.
- Open a contract-change window.
- Re-litigate the pilot LoRA design. It's good. It waits.

**You will:**

### Track 1 — Build the entry harness for substrate-block ingestion (PRIMARY)

Techne is leading the substrate-shaped pipeline pilot this week — Gemini Deep Research reports will start emitting YAML-tagged substrate blocks (anti_anchor, primitive_proposal, composition_rule, catalog_edit, training_anchor, paradigm_candidate) per the design at `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md`. The training_anchor block schema is yours to consume.

Build the entry harness so that when the substrate-shaped pipeline starts producing JSONL training_anchor blocks at scale, Ergon can ingest them directly into the v1.0 corpus. Specifically:

1. **Spec the training_anchor → Tier-1 corpus mapping.** A document at `ergon/learner/v1_0_plans/training_anchor_ingestion_spec.md` showing: (a) which fields of the training_anchor schema map to which fields of LearnerRecord, (b) how trust_tier (analytically_proven / numerically_certified / ml_predicted / unverified) propagates into the 4-condition eval harness, (c) what blind-spot anchor coverage each ingested batch contributes.
2. **Build the ingester (doc-only, no compute).** A Python script at `ergon/learner/scripts/ingest_training_anchors.py` that reads `aporia/docs/staged_substrate_blocks/<date>/training_anchor.jsonl` (when Techne's pipeline produces it) and emits LearnerRecord-shaped output to `ergon/learner/corpus/v1_0_tier_pending/`. Don't actually run it yet; the substrate-shaped pipeline output doesn't exist. Build it ready.
3. **Coordinate with Techne** on the training_anchor schema. If you see fields you'd want different (e.g., adding episode_id slot to support falsification-routing training), file an Aporia ticket — don't modify schemas directly.

### Track 2 — Episode-emission consumption check

Coordinate with Techne's path (a) audit-prep on Dims 2/3/10. When Techne's audit-prep doc lands (this week per Techne's dialogue), read it and produce a 1-2 page Ergon-side response at `ergon/learner/v1_0_plans/episode_emission_consumption_2026-05-11.md` covering:

- For each of the 8 substrate opcodes Techne audits (TRACE, CLAIM, FALSIFY, GATE, ERRATA, REWRITE, PROMOTE, EXCLUSION): can Ergon's existing learner_enrichment.py consume what's emitted, or are gaps surfaced?
- Specific blind-spot calibration question: does each opcode's emission carry enough trust_tier signal that the post-train calibration-preservation gate (KC-001-style anchor vs BS-001-style blind-spot) can be enforced?
- No new opcode proposals; this is a consumption check, not a contract change.

### Track 3 — Blind-spot probe coverage assertion

Build a simple test at `ergon/learner/tests/test_blind_spot_probe_coverage.py` that asserts the current 5 confirmed blind-spots (BS-001 Cohen, BS-003 Helfgott, BS-004 Faltings, BS-005 McKay, BS-006 Margulis) all have probe representation in the Tier-1 eval set. Failing test = corpus gap. Make this a CI gate when CI lands.

## Bounded resources

- File ownership: `ergon/` tree, plus `aporia/meta/queue/ergon_inbox.jsonl` for status updates.
- No compute. No API budget. No contract changes.
- Estimated total work: 3-4 days across Tracks 1-3.

## What to file when work lands

- Track 1: append to `aporia/meta/queue/techne_inbox.jsonl` flagging the training_anchor ingester is built and ready for pipeline output. P2-medium.
- Track 2: append to `aporia/meta/queue/techne_inbox.jsonl` as a response to Techne's audit-prep doc. P2-medium.
- Track 3: standalone test commit; no inbox ticket needed.
- Update `ergon/STATUS.md` Learner Branch section after each track lands.

## What you should ask James about

Nothing this week. The compute decision is deferred to ~week 3+. If Track 1 surfaces a question about the training_anchor schema you can't resolve with Techne, file an Aporia ticket for substrate-design adjudication rather than escalating to James.

## Substrate-grade observation worth carrying forward

The 2026-05-09 → 2026-05-10 Saxl capture cycle and the 2026-05-11 derive_kill_signature factorization-leak catch are the same shape: **generic dim-name at the design level + lower-level code/citation audit revealing a concrete instance + reshape of design from the instance.** This is the pattern that pulls the substrate away from "beautifully falsifying machine forever." Build Tracks 1-3 with that posture: ship the generic-level harness, expect the audit at consumption time to surface specific instances that reshape the design.

End of prompt. Acknowledge receipt, then proceed with Track 1.
