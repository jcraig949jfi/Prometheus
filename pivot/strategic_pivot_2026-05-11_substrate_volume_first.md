# Strategic Pivot — Substrate Volume + Quality Before LoRA

**Filed:** 2026-05-11
**By:** James (decision), drafted by Claude Code in dialogue
**Supersedes:** parts of `strategic_redirect_handoff_2026-05-10.md` §3 compute-decision framing — that decision is now: NO compute for LoRA pilot yet; substrate-volume-and-quality is the explicit prerequisite.

---

## §0 The call

**LoRA training is paused indefinitely.** Not because the design is wrong — the 4-condition pilot spec at `ergon/learner/v1_0_plans/pilot_lora_design_tier_1_corpus.md` is sound, the eval harness design is clean, the gating sub-pattern is correct. The pause is because **training on the current substrate would teach the model to memorize ~12 anti-anchors and ~22 primitive specs as a closed corpus**. Falsification-routing requires episode volume (CLAIM → FALSIFY → REWRITE → REPAIR → GATE → PROMOTE) at a scale that doesn't exist yet. The Tier-1 corpus is 998 lines of generator-side enrichment; that's necessary infrastructure, not training-corpus volume.

**Substrate-volume-and-quality is now the explicit gate.** Until the substrate produces materially more registered primitives, anti-anchors, composition rules, and clean episode emissions, the LoRA experiment is premature and would produce a calibration-poisoning result.

This call is consistent with the 2026-05-10 standing HARD WARNING: *"substrate is at risk of becoming a beautifully falsifying machine forever while the model remains passive."* The remediation is NOT to force the model to train prematurely. The remediation is to **make the substrate qualitatively load-bearing first**, then train.

---

## §1 What gets us more substrate fastest — analysis

Six paths considered. Ranking by leverage:

### Path 1 — Substrate-shaped Deep Research pipeline (THE compound multiplier)

The epiphany already designed at `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md`. Modify Gemini prompts so reports return *both* the existing narrative report AND YAML-tagged substrate blocks (anti_anchor, primitive_proposal, composition_rule, catalog_edit, training_anchor, paradigm_candidate). A parse / validate / stage pipeline routes blocks into canonical registries with arXiv-citation verification at the validate step.

- **Volume effect:** same Gemini yield (~10 AAs + ~15 primitives + ~10 catalog edits per 20-prompt batch), but 5-10x faster reviewer throughput (~30-60 min review vs 5-6 hours synthesis).
- **Quality effect:** arXiv-verify gate catches Lee-2025-shaped withdrawn-paper fabrications mechanically (the Saxl capture took manual luck; with the pipeline it would have been auto-rejected at validation). HARD-5 distinct-coordinates enforced at write-time, not read-time.
- **Cost:** 2-3 engineering days for the parse/validate/stage tooling + 6 JSON schemas.
- **Compounding:** every batch from this point forward produces *more usable* substrate per token. This is the only path on the list that compounds.
- **Owner:** Techne (owns contracts + schemas).

### Path 2 — Techne v4.0 Wave 1 primitive registration (substrate ACTIVATION)

Register the 7 foundational primitives (5 unified metas + 2 P0): TensorNetwork, ConstructiveExistenceWitness, GenericityAlmostEverywhereCert, RepresentationTheoreticInvariant, MomentPolytope, CoordinateChart, CanonicalizationProtocol. Sigma's 94 contract tests across 35 classes un-skip the moment these land.

- **Volume effect:** doesn't increase raw substrate volume; activates 94 contract tests that have been waiting.
- **Quality effect:** the activation IS quality. Contract tests will start finding gaps where the vocabulary specs are inconsistent with what Sigma expects.
- **Cost:** 1-2 days for the registration sprint + contract-change-window discipline.
- **Defer until:** Path 1 pilot has run, so registrations are informed by what the substrate-shaped pipeline produces.
- **Owner:** Techne.

### Path 3 — Dims 2/3/10 audit-prep + episode-emission audit (precondition for clean training data)

Techne's path (a) from the dialogue: audit-prep doc on Dims 2/3/10. Plus the episode-emission audit Ergon requested in T-2026-05-10 (which opcodes already emit episode-shaped data, which gaps need new emission).

- **Volume effect:** none directly; precondition.
- **Quality effect:** when LoRA does run, the training corpus will have cleaner episode structure → better falsification-routing signal.
- **Cost:** 1-2 days doc work.
- **Owner:** Techne (already started; standing down on compute side).

### Path 4 — Continue burning Gemini queue daily (the baseline)

Default behavior per `feedback_use_or_lose_research_tokens.md`. 20 reports/day = ~140/week. The 423-entry queue runways ~21 days at this rate.

- **Volume effect:** linear; ~70/week new substrate inputs.
- **Quality effect:** depends entirely on whether Path 1 ships. Without Path 1, translation bottleneck keeps reviewer throughput at 5-6 hr/batch.
- **Cost:** ~30 min daily orchestration overhead.
- **Owner:** Aporia (via `burn_research_tokens.py`).

### Path 5 — Cross-domain Tier-F bundle primitives (unblock Tier-3 calibration mining)

Per `aporia/docs/gemini_research_synthesis_2026-05-11.md` §11: build Tier-F primitive bundles for knots (`KnotInvariantBundle`), Maass forms (`MaassGL3SpectralBundle`), abelian surfaces (`AbelianSurfaceArithmeticBundle`), OEIS/RMT/AG-moduli. Currently these domains have "soft" Tier-3 queue entries because their downstream-consumer primitives don't exist.

- **Volume effect:** opens previously-blocked queue lanes; ~50-80 additional high-leverage queue entries become firable.
- **Quality effect:** breadth of substrate (non-tensor domains) catches up to depth (tensor domains).
- **Cost:** 1-2 days per bundle. Total: 1 week for 4-5 bundles.
- **Owner:** Aporia (specs the bundles); Techne (registers them).

### Path 6 — Episode-curation pass on the 314K kill ledger

Per the gradient-archaeology analysis showing 0.725 bits MI between kill_pattern and operator class — there's real signal in the kill ledger. A curation pass to extract the most-informative ~5-10K episodes would produce a clean training corpus before any new substrate generation.

- **Volume effect:** extracts ~5-10K episodes from existing logged kills.
- **Quality effect:** depends on curation discipline. High variance.
- **Cost:** 3-5 days design + execution.
- **Defer:** until Path 1 and Path 3 are in place; otherwise we'd extract bad-quality episodes.

---

## §2 The plan (ordered)

**This week (Mon-Wed):**
- **Path 1** — Techne leads substrate-shaped pipeline pilot. Spec 6 JSON schemas, build parse/validate/stage scripts, fire 3 queue entries with substrate-shaped variants alongside narrative-only equivalents. Compare yield + arXiv-verify pass rate.
- **Path 3** — Techne continues Dims 2/3/10 audit-prep in parallel (already started).
- **Path 4** — Aporia continues daily Gemini burn at 20/day (unchanged from current cadence).
- **Path 2 — DEFERRED.** Don't open the contract-change window until Path 1 pilot evidence is in.

**This week (Thu-Fri):**
- Pilot evidence assessed.
- If positive: migrate all 4 tier templates to substrate-shaped variants. Build ingest tooling.
- If negative: revert to narrative-only and keep arXiv-verify as standalone audit.

**Next week:**
- **Path 2** — Techne v4.0 Wave 1 registration (informed by Path 1 schemas).
- **Path 1 (continued)** — full migration of templates; daily burns produce JSONL substrate blocks at scale.
- **Ergon** — builds entry harness so Learner v1.0 can ingest training_anchor blocks directly when LoRA fires.

**Week 3+:**
- **Path 5** — Cross-domain Tier-F bundles, parallelized.
- **Path 6** — Episode-curation pass.
- **LoRA pilot** — fires only after substrate volume has materially lifted (target: 5x current AA count, 3x primitive registration count, 100+ confirmed composition rule traces).

---

## §3 What's gated on James

After this pivot doc, nothing in the near-term plan requires a James compute decision. Both Ergon and Techne can proceed:

- **Ergon** — build entry-harness for substrate-block ingestion. No compute. No frontier-API budget.
- **Techne** — build substrate-shaped pipeline pilot. No compute (the API tokens are Aporia's daily burn; Techne's work is parser/validator). No frontier-API budget.

The LoRA compute decision moves out to ~week 3+ when substrate volume justifies it. James can ignore that question until then.

What James SHOULD know:
- Path 1 (substrate-shaped pipeline pilot) is the leverage point. Everything else is linear.
- If the pilot fails (arXiv-verify too noisy, schemas don't fit, prompt-size bloat compresses narrative quality unacceptably), the fallback is "continue narrative-only at current pace + add arXiv-verify as a post-hoc audit." Not catastrophic.
- LoRA stays paused. Tier-1 corpus stays as designed infrastructure, not consumed yet.

---

## §4 What this is NOT

- NOT a retraction of the falsification-routing north star. That's still the v1.0 target.
- NOT a retraction of the pilot LoRA design. The 4-condition spec is good; it's deferred, not redesigned.
- NOT a contract-change window. Vocabulary v0.1.0, Techne v3.1.0 scaffolding, anti-anchor registry — all stay frozen as they are. Path 2 will open a window when ready.
- NOT a substrate v3 proposal. Per `pivot/substrate_v3_proposal_stub_2026-05-08.md`, v3 work is deferred. This pivot operates within v2.x.

---

## §5 Update protocol

- Ergon updates `ergon/STATUS.md` Learner Branch section after each path-3 deliverable lands.
- Techne updates `techne/CHANGELOG.md` after each Path 1 substrate-shaped pipeline stage (schemas / parser / validator / stager / ingester).
- Aporia continues daily burn; logs each fire to `aporia/docs/gemini_research_queue/fired_log.jsonl`.
- This pivot doc gets a §6 retrospective when Path 1 pilot evidence lands.

---

## §6 Pilot retrospective (TBD — fills in after Path 1 lands)

[reserved]
