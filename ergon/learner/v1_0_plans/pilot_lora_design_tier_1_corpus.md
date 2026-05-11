# Pilot LoRA Design — Tier-1 Enriched Substrate Corpus

**Filed:** 2026-05-11 by Ergon (Learner owner)
**Trigger:** Techne shipped Tier-1 instrumentation (commit `20d64203`, 2026-05-11) addressing 4 of 5 easy-fix Ergon quality dims; Ergon discussion doc §4 proposed behavior-evidence-first default; Techne's reply explicitly adopts that gating sub-pattern.
**Linked:**
- `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md` (10-dim discussion)
- `ergon/learner/v1_0_plans/strategic_redirect_handoff_2026-05-10.md` (falsification-routing redirect)
- Techne files: `prometheus_math/substrate_generation/learner_enrichment.py`, `survivor_seed_pool.py`, `tier_1_lehmer_enriched.py`
- Tests: `prometheus_math/tests/test_substrate_generation_tier_1.py` (36 methods, 8 classes, 17s wall-clock, all pass)
**Memory anchors:**
- `feedback_verify_upstream_attributions.md` — verified Techne's summary against shipped code; claims hold
- `feedback_substrate_passive_consumer_warning.md` — pilot LoRA is the first concrete behavior-delta experiment
- `project_falsification_routing_learner.md` — v1.0 north star
- `project_lora_4_condition_control.md` — original cheapest-first experiment (this pilot subsumes it)

---

## §0 Verification record (Ergon ↔ Techne handshake)

Per `feedback_verify_upstream_attributions.md`, Ergon does NOT accept Techne's summary at face value. Ergon verified:

- **Commit `20d64203` exists** (`git log --oneline -10`), authored 2026-05-11.
- **Three new modules + one test suite** in `prometheus_math/substrate_generation/` and `prometheus_math/tests/`: 998 insertions total.
- **`LearnerRecord` 8-field schema** is exactly as Techne described: `underlying_record_hash`, `episode_id`, `episode_phase`, `verification_tier`, `chart_id`, `decoy_kind`, `kill_signature`, `outcome_class` (`learner_enrichment.py:79-86`). Frozen dataclass.
- **7 signature kinds** in `derive_kill_signature` (`learner_enrichment.py:122-176`): `survived`, `out_of_band`, `reducible` (with `n_factors=N`), `f1/f6/f9/f11_killed`, `catalog_hit` (with source-name), `error`, `other`.
- **3 deg-12 in-band Mossinghoff survivors** at M = 1.176281 (`survivor_seed_pool.py:34-50`): Lehmer-extension (deg 12), Lehmer × Phi_3, Lehmer × Phi_4. All palindromic per coefficient inspection.
- **Deterministic interleave** with `interval = max(2, round(1/decoy_rate))` (`survivor_seed_pool.py:120-132`).
- **Anti-leakage tests**: 15 grep-hits on `kill_signature|coefficients|literal|polynomial` in `test_substrate_generation_tier_1.py`; explicit assertions that NO literal polynomial coefficients appear in signature elements.
- **Tier-1 composition**: `tier_1_lehmer_enriched.py` exposes `run_tier_1`, `_record_to_dict`, `main` (lines 58, 179, 198). Sits on top of Tier-0 harness without modifying it.
- **All 36 tests pass** in 17.06s under `PYTHONPATH=F:/prometheus PYTHONUTF8=1`.

**Verification verdict:** Techne's summary is accurate. Ergon proceeds on the verified state, not the summary state.

---

## §1 What Tier-1 actually addresses, vs the 10 Ergon dims

Mapping verified against shipped code, not against Techne's summary:

- **Dim 1 (episode density):** ADDRESSED at generator-level. `LearnerRecord.episode_id = underlying_record_hash` in Tier-1 (1:1 mapping). Multi-record episodes (CLAIM → FALSIFY → PROMOTE chains) deferred to Tier-2+ when generators emit through the full opcode lifecycle. Tier-1 stance is honest about being 1:1, which is fine for the pilot.
- **Dim 4 (verification stratification):** ADDRESSED. `lookup_verification_tier()` reads `CoordinateChart.canonicalization.decidability_status` (the field shipped fire #64). 4-value enum: `decidable`, `undecidable`, `conditional`, `unknown`. The `unknown` fallback when no chart is registered is the correct discipline (don't fail; tag-as-unknown so pilot can measure how much of corpus actually has registered charts).
- **Dim 6 (episode boundaries):** ADDRESSED at generator-level. `EPISODE_PHASES` enum exists (`"evaluate"`, `"claim"`, `"falsify"`, `"promote"`, `"errata"`) but Tier-1 generators emit only `"evaluate"`. The schema is forward-compatible without requiring Tier-1 generators to do more than they should.
- **Dim 7 (null/decoy interleaving):** ADDRESSED. 3 curated deg-12 survivors at M = 1.176281; deterministic interleave at configurable rate (default 0.1). `decoy_kind="seeded_survivor"` tag enables train/eval split discipline.
- **Dim 9 (anti-leakage tuple-vs-string):** ADDRESSED. `kill_signature: Tuple[str, ...]` strips literal polynomial coefficients from `kill_pattern`. 15 anti-leakage assertions in tests. This is the highest-value dim addressed in Tier-1 because the literal-coefficient leakage was a real train/eval bleed risk that Ergon did NOT anticipate at the dim-naming level — Techne's `kill_pattern` audit caught a leakage class Ergon didn't know to spec.
- **Dim 5 (process traces vs outcomes):** DEFERRED, correctly. Techne re-classified it from "easy-fix" to "real gap" — substrate's REWRITE/EQUIV opcodes could carry process steps but generators don't route through them yet. Wait for pilot LoRA to report what process traces it actually needs.

**Dims still in deferred state (4 real gaps from §1 discussion):** Dim 2 (counterfactual completeness), Dim 3 (calibration-tier provenance with KC/BS catalog lookup — partial via CoordinateChart's decidability_status, but not the KC-001/BS-001-style tier), Dim 5 (process traces), Dim 10 (cross-fire replication-status tagging). These are exactly the gaps the pilot LoRA should surface as measured deficiencies.

---

## §2 Pilot LoRA — concrete spec

The corpus Ergon trains on is the **LearnerRecord JSONL stream** emitted by `tier_1_lehmer_enriched.py`. The schema is locked. The pilot subsumes the 4-condition LoRA control test (`project_lora_4_condition_control.md`) by using Tier-1 enriched output as the "actual training corpus" and the 3 null conditions for falsifying the LoRA's effect.

### §2.1 Conditions (4-condition pattern, adapted to Tier-1)

1. **Base Qwen2.5-Math-1.5B-Instruct** — no LoRA. Reference policy.
2. **Base + Tier-1 LoRA** — trained on the JSONL stream from `run_tier_1(...)` (post-greenlight Mahler run).
3. **Base + label-shuffled Tier-1 LoRA** — same JSONL records, but `outcome_class` / `kill_signature` / `verification_tier` shuffled across records before training. Null control for "the LoRA learned anything specific about the actual labels vs the format."
4. **Base + format-only Tier-1 LoRA** — trained on Tier-1-format JSONL with payload fields replaced by random valid-enum values matching the same schema. Null control for "the LoRA learned anything content-bearing vs style only."

### §2.2 Eval set

Existing calibration corpus, NOT Tier-1 enumerated candidates (to keep train/eval clean):
- **9 KC anchors** (KC-001 .. KC-009 + KC-AGW-LOCK numerical reproducibility) — positive-recovery probes
- **6 BS blind-spots** (BS-001 Cohen, BS-002 Lefschetz, BS-003 Helfgott, BS-004 Faltings, BS-005 McKay-deterministic, BS-006 Margulis-partial-recovery) — false-promotion probes
- **8 trivial-vs-open pairs** (TVO-01 .. TVO-05 from `learner_fabrication_corpus_v1.json` + 3 new tensor-domain TVO pairs Ergon will draft, NOT seeded into training)
- **~15 random-decoy probes** for entropy baseline
- **Tier-1 hold-out**: 20% of Tier-1 LearnerRecords held out from training, grouped by `episode_id` (no episode leaks across split).

### §2.3 Metrics (6, per James 2026-05-10 critique)

1. **Promotion-error rate** on BS blind-spots — detects harmful overconfidence. Must NOT increase vs base (Gate 1 in handoff §2.3).
2. **Blind-spot preservation** — false-promotion delta vs base. Negative is good (preserves more calibration than base).
3. **Anchor recovery** — KC-tier recovery delta vs base. Positive is good (more KC-001-style full recovery).
4. **Falsification-test choice** on synthetic claim/test pairs — top-1 / top-3 accuracy for choosing the kill-relevant test. This is the falsification-routing gate.
5. **Answer entropy / hedging** — detects style-only LoRA effect. If conditions 3 and 4 produce similar entropy delta to condition 2, that's evidence Tier-1 LoRA is style-shaping, not content-shaping.
6. **Kill-signature consistency** — does the LoRA-trained model emit kill_signatures that match the true ones on held-out Tier-1 records? This is a direct measure of whether the structured-signature anti-leakage discipline is being learned.

**Expected outcome:** Tier-1 LoRA shows meaningful gains on metrics 4 and 6 (the falsification-routing-specific signals), small or null gains on 1-3 (it's a deg-12 Lehmer corpus, not a theorem-attribution corpus), null gains on conditions 3 and 4. The KEY comparison is **Tier-1 vs label-shuffled** — that's where the falsification-routing capability claim either lives or dies.

### §2.4 What this experiment teaches (the gating sub-pattern)

If Tier-1 LoRA shows measurable lift on metric 4 (falsification-test choice) over base AND over the two null controls, then:
- Substrate Tier-1 enrichment IS Learner-trainable.
- The falsification-routing thesis (`project_falsification_routing_learner.md`) is no longer aspirational — there's evidence.
- Targeted audit of the 4 deferred gaps (Dims 2/3/5/10) becomes the next behavior-driven scope decision.

If Tier-1 LoRA shows null lift on metric 4 (no better than base or null controls):
- Tier-1 enrichment is insufficient.
- Pilot evidence forces specific gap identification: which of Dims 2/3/5/10 most explains the null result.
- That's the substrate-instrumentation roadmap derived from evidence, not speculation.

Either outcome is informative. This is the Tier-1-to-audit feedback loop the gating sub-pattern is designed to produce.

---

## §3 Aporia greenlight ask (gating sub-pattern formalization)

Per Techne's framing: "Ready for greenlight on the gating sub-pattern (pilot LoRA on this Tier-1 corpus → measured deficiencies → targeted audit) without further design conversation."

**What needs Aporia sign-off:**
1. The pilot-LoRA-first ordering is the agreed protocol (not "audit all 10 dims first, then build").
2. Pilot results trigger a TARGETED audit of whichever subset of Dims 2/3/5/10 the evidence implicates, not a sweep of all four.
3. Tier-1 JSONL corpus is the Ergon-side ground-truth training input until pilot evidence redirects.
4. The `--writeable` flag stays blocked pending Aporia greenlight on the full Mahler-throughput run, separate from the schema/format greenlight.

**What stays under James scope:**
- Compute time for the pilot LoRA run (1.5B model + 4 LoRA configs ≈ small-but-not-free).
- Verifier-only frontier-API budget per `strategic_redirect_handoff_2026-05-10.md` §3.2.
- Tensor-Tester arc timing per same handoff §3.3.

---

## §4 What Ergon will and won't do without further go-ahead

**Will do (within file ownership, doc-only):**
- Wait for Aporia greenlight on the gating sub-pattern.
- Draft pilot LoRA configuration files in `ergon/pipeline_d/` (training config, eval config, metric scaffolding) — no run, just config.
- Draft 3 new tensor-domain TVO pairs to expand the eval set (doc-only; will not seed into training corpus).
- Acknowledge pending Techne ticket items as ABLE-TO-ADVANCE pending pilot evidence.

**Will not do without go-ahead:**
- Trigger the Mahler-throughput Tier-1 run (waits for James/Aporia).
- Train any pilot LoRA (waits for James compute scope decision).
- Promote any Tier-1 JSONL output to "verified training corpus" before pilot evidence (per `feedback_verify_upstream_attributions.md` — even substrate-shipped output is a Tier-2-or-worse anchor until empirically validated).
- File contract-change request on KillVector / NearMissCorpus / CoordinateChart (the deferred Dims 2/3/5/10 require contract-change-window protocol, not bypass).

---

## §5 Substrate-grade observation

This is the **first substrate ↔ Learner round-trip** in the Prometheus arc that traces directly to behavior-delta intent:

1. James 2026-05-10 strategic redirect (falsification-routing > theorem-answering; substrate-passive-consumer warning).
2. Ergon 2026-05-11 discussion doc (10 quality dims; default position §4: behavior-evidence-first build a synthetic v1.0 corpus + small LoRA from CURRENT substrate output).
3. Techne 2026-05-11 reply (Tier-1 instrumentation shipped at GENERATOR level; HARD-2 anti-gravitational-well preserved; 4 easy-fix dims addressed without contract change; 1 dim correctly reclassified as gap and deferred; gating sub-pattern formalized).
4. Ergon 2026-05-11 (this doc) pilot LoRA spec locked + Aporia greenlight ask + verification record.

Total elapsed: ~1 day. The substrate did NOT slip into "more taxonomy, more elaboration, more design" — it shipped a 998-line generator-side enrichment that is concretely consumable. This is what `feedback_substrate_passive_consumer_warning.md` was warning AGAINST and `feedback_substrate_passive_consumer_warning.md` was hoping FOR. The substrate participated in producing a behavior-delta-shaped artifact rather than another beautifully-taxonomized doc.

The Saxl error 24 hours ago could have been the high-water-mark of "beautiful taxonomy without behavior delta." Tier-1 shipping today (1 commit, 4 files, generator-level instrumentation, no contract change, gating sub-pattern adopted) is the substrate proving it can do better.

**Caveat:** none of this is *evidence the Learner improves* yet. Pilot LoRA is the next gate. Tier-1 is necessary infrastructure, not sufficient evidence. Ergon stays calibrated per `feedback_calibration.md`.

---

*— Ergon, 2026-05-11, post-Techne-Tier-1-handoff pilot LoRA design lock-in*
