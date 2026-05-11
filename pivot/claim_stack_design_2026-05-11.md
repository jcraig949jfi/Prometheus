# Claim-Stack Pipeline — Design Sketch (2026-05-11)

**Status:** SKETCH FOR APORIA REVIEW. Not implemented; the design space is being mapped here so Aporia can react before any code lands. Author: Techne, drafted in response to James 2026-05-11.

**Strategic context:** the kernel's central opcode is CLAIM, but current substrate generators bypass it (brute-force enumeration emits kill_vectors directly via `DiscoveryPipeline.process_candidate`; substrate-shaped pipeline produces blocks that are scaffolded by but never executed against CLAIM/FALSIFY/PROMOTE). The claim-stack puts the lifecycle back in the loop, which is what the kernel was designed for. Aporia is the natural author of the stack because the three highest-value categories of claim (frontier-survey from Gemini outputs, calibration from training_anchor blocks, boundary from catalog entries) all need synthesis-level reading of materials Aporia already maintains.

**Honest caveat up front:** random claims produce volume, not learning signal. If the stack is uniform-trivial ("Lehmer's polynomial has Mahler measure 1.176..." style), substrate volume goes up and Learner gain is zero, mirroring the Tier-0 brute-force 0.026% in-band rate problem. The SHAPE of the stack matters more than its existence. §3 below is where the shape is specified.

---

## 0. What this pipeline produces and why

A claim-stack run consumes one or more `claim_stack.jsonl` files authored by Aporia, routes each claim through the kernel's CLAIM/FALSIFY/PROMOTE lifecycle using existing verifier infrastructure (mpmath, sympy, catalog adapters, arXiv HEAD check, TriangulationProtocol), and emits enriched LearnerRecord JSONL suitable for direct LoRA pilot ingest.

The behavior delta (per HARD WARNING 2026-05-10): the kernel goes from "shipped but unused" to "exercised at every claim." The Learner corpus gains a class of records currently absent — full claim-lifecycle traces, not just terminal kill_vectors.

No compute escalation, no contract change, no Aporia Phase-2 dependency. All within file ownership of `prometheus_math/substrate_generation/` plus a new author-side file under `aporia/`.

---

## 1. Claim-block schema sketch

New entry in `techne/contracts/substrate_block_schemas/` family. Schema name: `claim_v1.json`. The shape mirrors the existing six substrate_block schemas (sharing `_common_definitions.json` references for citation patterns, trust tiers, etc.) so the same parse/validate pipeline can ingest these.

Proposed required fields:

- `_schema_version: "1.0.0"`
- `id` — string matching `^CLAIM-[a-z_]+-\d{4,5}$` (e.g. `CLAIM-frontier-00001`, `CLAIM-calibration-knots-00042`, `CLAIM-boundary-T4-00001`). Prefix names the category for grouping.
- `claim_category` — enum: `frontier_survey | calibration | boundary | substrate_self | other`
- `claim_text` — natural language statement, minimum 20 characters, the proposition being claimed
- `expected_verifier_primary` — enum: `citation_audit | catalog_lookup | mpmath_compute | sympy_factor | triangulation | substrate_self_check | manual_review`
- `expected_verifier_fallback` — same enum, optional second verifier when primary is uncertain
- `expected_verdict` — enum: `survived | falsified | open | conditional`. `open` is allowed (substrate's INCONCLUSIVE_WAITING outcome class extended to claim level).
- `ground_truth_source` — citation (arXiv/DOI per existing common-defs regex) OR dataset reference (LMFDB table name / KnotInfo URL / etc.)
- `trust_tier` — same enum as training_anchor: `analytically_proven | numerically_certified | ml_predicted | folklore | unverified`. Required even when `expected_verdict: open` — captures how the ground truth status is known.
- `source_report` — what produced this claim (Gemini batch report, anti_anchor entry, training_anchor entry, T#NN catalog entry, fire #NN audit, etc.)

Optional/Conditional fields:

- `parent_block` — when the claim was derived from another substrate_block (e.g. an `anti_anchor` becoming two paired claims), references back to that block by id. Cross-reference checked at validate time.
- `prompt_template` — for calibration claims, the natural-language form a Learner-Tester would use to ask the question. For other categories, optional (claim_text often suffices).
- `expected_answer_shape` — Python type description, optional but useful for calibration claims.
- `verifier_args` — opaque dict of arguments passed to the verifier (e.g. for mpmath_compute, the dps to use; for catalog_lookup, the catalog source).
- `caveats` — free-form text capturing measure-zero exceptions, conditionality (under-GRH, etc.), expected drift.
- `paired_claim_id` — when this claim is part of a pair (e.g. false_form/true_form derived from an anti_anchor), reference the partner.

The schema rejects ambiguous claim categories that should have been split. For example, "R(M⟨3⟩) = 22" should be `boundary` not `frontier_survey` even though it appears in a frontier survey; the category is determined by claim shape, not source.

---

## 2. Runner architecture

New module `prometheus_math/substrate_generation/tier_1_claim_runner.py`. Composes the existing kernel + verifier infrastructure; no new substrate primitives.

Skeleton flow per claim:

1. Load the claim's schema-validated payload.
2. Mint a kernel capability (`kernel.mint_capability("PromoteCap")`).
3. Emit `kernel.CLAIM(...)` with `target_name` = claim id, `hypothesis` = claim_text, `kill_path` = primary verifier name, `evidence` = dict capturing the ground_truth_source + trust_tier + parent_block + verifier_args.
4. Route to the verifier function indexed by `expected_verifier_primary`. Each verifier returns a structured result: `{verdict, evidence_blob, runtime_ms, method_used, precision_dps, caveats}`.
5. Emit `kernel.FALSIFY(claim, ...)` with the verifier's verdict translated to one of the kernel's three verdict strings: `verified | contradicted | inconclusive`. The translation: `survived → verified`, `falsified → contradicted`, `open → inconclusive`, `conditional → inconclusive` (with caveat metadata explaining the conditionality).
6. If verdict is `verified`, emit `kernel.PROMOTE(claim, cap)` to register a Symbol in the substrate.
7. Build a LearnerRecord via the existing `learner_enrichment.enrich()` adapter (reusing episode_id / episode_phase / verification_tier / kill_signature derivation). Add three claim-specific fields: `claim_category`, `expected_verdict`, `actual_verdict` (so train/eval can split by category and by expected-vs-actual agreement).
8. Emit the LearnerRecord to the output JSONL stream.

A single claim produces between 1 and 3 LearnerRecords (one per emitted opcode phase). Default emits all three (claim / falsify / promote-or-errata) so the Learner sees full lifecycle traces.

Verifier function index (initial set):

- `citation_audit` — wraps `aporia/scripts/validate_substrate_blocks.py:_arxiv_head_check` + `_arxiv_withdrawal_check`. Returns `verified` if citation resolves and is active; `contradicted` if withdrawn; `inconclusive` on network failure.
- `catalog_lookup` — wraps `prometheus_math.catalog_consistency.run_consistency_check` plus the per-catalog adapters (LMFDB, OEIS, Mossinghoff, arXiv). Compares the claim's predicted catalog presence/absence against actual.
- `mpmath_compute` — for numeric claims (Mahler measures, eigenvalues, etc.), runs mpmath.polyroots / mpmath.mpf operations at the dps requested in verifier_args. Compares to expected value within precision tolerance.
- `sympy_factor` — for algebraic identity claims (irreducibility, factorization shape, polynomial equality), runs sympy.factor / sympy.Poly operations.
- `triangulation` — for high-trust claims, runs the existing `TriangulationProtocol` with synthetic paths derived from multiple verifier methods. Returns the protocol's verdict.
- `substrate_self_check` — for meta-claims about substrate behavior, dispatches to a small table of known substrate invariants (e.g. "TriangulationProtocol returns INCONCLUSIVE_WAITING for n_paths < 3").
- `manual_review` — escape hatch. Returns `inconclusive` with a flag that this claim needs human review. Use when no automated verifier exists yet.

Compute budget: each claim is bounded by `verifier_budget_ms` (default 5000ms). Verifiers that exceed timeout return `inconclusive` with a `timeout` flag. Runner is CPU-bound, single-process default; multiprocessing fan-out is a future Tier-2 enhancement matching the substrate-generation roadmap.

---

## 3. Three category specs + worked examples

### 3.1 Category — frontier_survey (derived from Gemini outputs)

Highest value per claim because it composes the substrate-shaped pipeline (gated on pilot fire) with the kernel's CLAIM machinery. Each `anti_anchor` block becomes two paired claims; each `catalog_edit` becomes one or two claims; each `composition_rule` becomes one.

**Worked example, derived from AA-001 (GCT_OCCURRENCE_DEAD):**

```yaml
# substrate_block: claim
- id: CLAIM-frontier-00001
  _schema_version: "1.0.0"
  claim_category: frontier_survey
  claim_text: |
    Bürgisser-Ikenmeyer-Panova killed GCT entirely; occurrence obstructions
    for det/padded-perm are still a viable path to VP vs VNP separation.
  expected_verifier_primary: citation_audit
  expected_verdict: falsified
  ground_truth_source: arXiv:1604.06431
  trust_tier: analytically_proven
  source_report: AA-001 anti_anchor false_form
  parent_block: AA-001
  paired_claim_id: CLAIM-frontier-00002
  caveats: |
    Paired with CLAIM-frontier-00002 which carries the TRUE form including
    the multiplicity / vanishing-ideal / outside-orbit / equivariant carve-outs.

- id: CLAIM-frontier-00002
  _schema_version: "1.0.0"
  claim_category: frontier_survey
  claim_text: |
    BIP 2019 (J. AMS) killed *occurrence* obstructions for
    (det_m, padded_perm_{n,m}, m=poly(n)) specifically. Multiplicity,
    vanishing-ideal, outside-orbit, and equivariant obstructions remain.
  expected_verifier_primary: citation_audit
  expected_verdict: survived
  ground_truth_source: arXiv:1604.06431
  trust_tier: analytically_proven
  source_report: AA-001 anti_anchor true_form
  parent_block: AA-001
  paired_claim_id: CLAIM-frontier-00001
  caveats: |
    The true form must preserve all four carve-outs verbatim; if a verifier
    promotes a version with any of (multiplicity / vanishing-ideal /
    outside-orbit / equivariant) missing, that is a substrate failure not
    a verdict.
```

What happens at runtime: both claims are CLAIMed; verifier (citation_audit) fetches arXiv:1604.06431, confirms it exists and is active, reads the abstract for "occurrence obstructions" qualifier text. CLAIM-00001 returns `contradicted` (the false form IS false per the citation). CLAIM-00002 returns `verified` (the true form matches the abstract). Both records land in the LearnerRecord stream, paired by `paired_claim_id`, with `actual_verdict` matching `expected_verdict` in both cases. The Learner sees: false-form FALSIFIED, true-form PROMOTED.

Volume: ~12 existing anti_anchors × 2 paired claims = ~24 claims. Substrate-shaped pipeline pilot would add 11+ new AAs per burn × 2 = 20-30+ more claims per Gemini batch. Plus catalog_edit and composition_rule claims, roughly another 10-15 per batch. Steady state: ~30-50 frontier_survey claims per Gemini burn.

**Worked example, derived from a catalog_edit block:**

```yaml
# substrate_block: claim
- id: CLAIM-frontier-00100
  _schema_version: "1.0.0"
  claim_category: frontier_survey
  claim_text: |
    The current text of tensor_open_problems_v1.md T#1 (matrix multiplication
    exponent ω) states the upper bound as 2.371552 (DWZ 2023). This is stale
    relative to VWXXZ 2024 which establishes 2.371339.
  expected_verifier_primary: catalog_lookup
  expected_verifier_fallback: citation_audit
  expected_verdict: survived
  ground_truth_source: arXiv:2404.16349
  trust_tier: analytically_proven
  source_report: catalog_edit block from frontier survey 2026-05-NN
  parent_block: catalog_edit:T#1:status_paragraph
  caveats: |
    Verification path: catalog_lookup re-reads the catalog entry; citation_audit
    confirms arXiv:2404.16349 exists and is the latest VWXXZ preprint. If both
    succeed, claim is SURVIVED (the catalog IS stale, the edit IS warranted).
```

### 3.2 Category — calibration (derived from training_anchor blocks)

High volume, mostly known-verifiable, exercises verifier infrastructure cleanly. Each training_anchor with `instance_count: N` produces up to N claims (or a sampled subset).

**Worked example, derived from the KnotInfo training_anchor (anchor-knots-001):**

```yaml
# substrate_block: claim
- id: CLAIM-calibration-knots-00001
  _schema_version: "1.0.0"
  claim_category: calibration
  claim_text: |
    The Alexander polynomial of the trefoil knot (3_1) is t**2 - t + 1
    (in canonical form, normalized to constant term +1).
  expected_verifier_primary: sympy_factor
  expected_verifier_fallback: catalog_lookup
  expected_verdict: survived
  ground_truth_source: KnotInfo 2024-12 snapshot, knot 3_1
  trust_tier: numerically_certified
  source_report: anchor-knots-001
  parent_block: anchor-knots-001
  prompt_template: |
    Compute the Alexander polynomial of the knot 3_1 (trefoil). Normalize
    to canonical form (constant term = +1).
  expected_answer_shape: sympy.Poly over ZZ in variable t
  verifier_args:
    canonical_form: constant_term_positive
    tolerance: exact
```

What happens: CLAIM emitted; sympy_factor verifier computes the Alexander polynomial from the knot's Gauss code (stored as part of KnotInfo); compares to expected `t**2 - t + 1` in canonical form. If match → `verified` → PROMOTE. The LearnerRecord captures the claim_text + the verifier output (the actual polynomial computed) + the runtime cost. Across 2978 knot entries, ~2978 calibration claims; running them takes substantial wall-clock but is embarrassingly parallel (Tier-2 enhancement).

Calibration claim subtlety: some training_anchor blocks have `verification_method: ml_prediction` (the Wave 3 finding on LMFDB GL(3) root numbers). Those entries should NOT generate calibration claims with `expected_verdict: survived`. Two options for what to do with them:
- Skip entirely (purist: don't pollute the calibration stream with ml-predicted data).
- Generate `expected_verdict: open` claims tagged `trust_tier: ml_predicted` (pragmatic: substrate sees them as decoys for adversarial training; Learner learns to discount ml-predicted ground truth).

**Recommend the pragmatic option** with a hard ratio cap: ml_predicted calibration claims must not exceed 10% of the calibration stream, and must always be tagged `trust_tier: ml_predicted` so train/eval can filter them.

### 3.3 Category — boundary (derived from tensor catalog entries)

For each T#NN entry with explicit bounds (lower ≤ value ≤ upper, or `value ∈ {a, b, c}`, etc.), generate 4-8 claims spanning the boundary types: `survived (within established range)`, `falsified (violates established bound)`, `open (within unresolved range)`, `conditional (true under stated assumption like GRH)`.

**Worked example, derived from T#4 (M⟨3⟩ rank, bounds 19 ≤ R ≤ 23):**

```yaml
# substrate_block: claim
- id: CLAIM-boundary-T4-00001
  _schema_version: "1.0.0"
  claim_category: boundary
  claim_text: |
    The exact rank of the 3x3 matrix multiplication tensor M<3> satisfies
    R(M<3>) <= 23.
  expected_verifier_primary: catalog_lookup
  expected_verifier_fallback: citation_audit
  expected_verdict: survived
  ground_truth_source: arXiv:1204.1111
  trust_tier: analytically_proven
  source_report: T#4 catalog entry, upper bound
  parent_block: T#4

- id: CLAIM-boundary-T4-00002
  _schema_version: "1.0.0"
  claim_category: boundary
  claim_text: |
    R(M<3>) <= 22 (the matrix multiplication tensor M<3> has rank at most 22).
  expected_verifier_primary: catalog_lookup
  expected_verdict: open
  ground_truth_source: T#4 catalog entry — no known construction below 23
  trust_tier: unverified
  source_report: T#4 catalog entry, boundary probe
  parent_block: T#4
  caveats: |
    OPEN: no construction is currently known to lower the upper bound below 23.
    This claim is in the unresolved range. Substrate should record verdict
    as inconclusive and tag trust_tier ml_predicted only if some future
    construction is claimed by a non-verified source.

- id: CLAIM-boundary-T4-00003
  _schema_version: "1.0.0"
  claim_category: boundary
  claim_text: |
    R(M<3>) <= 18 (the matrix multiplication tensor M<3> has rank at most 18).
  expected_verifier_primary: catalog_lookup
  expected_verifier_fallback: citation_audit
  expected_verdict: falsified
  ground_truth_source: Landsberg lower bound R(M<3>) >= 19
  trust_tier: analytically_proven
  source_report: T#4 catalog entry, falsification probe (violates lower bound)
  parent_block: T#4
  caveats: |
    Any claim of R(M<3>) <= 18 contradicts the established lower bound of 19.
    Substrate MUST emit FALSIFIED here; if it doesn't, that's a substrate
    failure surfacing a verifier gap.

- id: CLAIM-boundary-T4-00004
  _schema_version: "1.0.0"
  claim_category: boundary
  claim_text: |
    R(M<3>) = 22 (the exact rank of the matrix multiplication tensor M<3>
    is 22).
  expected_verifier_primary: catalog_lookup
  expected_verdict: open
  ground_truth_source: T#4 catalog entry — exact value unknown in (19, 23)
  trust_tier: unverified
  source_report: T#4 catalog entry, exact-value probe
  parent_block: T#4
```

Across the catalog's 104 entries, an average of 4-6 boundary claims per entry yields ~400-600 claims. This is the highest-volume category and the most diverse in verdict mix: roughly 50% expected_survived (in-range bounds), 30% expected_falsified (violation probes), 20% expected_open (gap probes within established intervals).

Boundary claims are the category most likely to surface verifier gaps. If a CLAIM-boundary expects `falsified` but the substrate returns `inconclusive`, that's a finding: the substrate's verifier infrastructure couldn't recognize the contradiction without literature support. Worth a substrate-tester ticket.

### 3.4 Category — substrate_self (meta-claims about substrate behavior)

Lower volume, but high value because these claims exercise the kernel's invariants directly.

**Worked examples:**

```yaml
# substrate_block: claim
- id: CLAIM-substrate-self-00001
  _schema_version: "1.0.0"
  claim_category: substrate_self
  claim_text: |
    TriangulationProtocol.evaluate(paths) with len(paths) < 3 returns
    verdict INCONCLUSIVE_WAITING.
  expected_verifier_primary: substrate_self_check
  expected_verdict: survived
  ground_truth_source: sigma_kernel/triangulation_protocol.py:388
  trust_tier: analytically_proven
  source_report: fire #55 triangulation primitive hardening
  parent_block: T-2026-05-09-ST-fire55-001
  caveats: |
    Self-claim: substrate verifies its own invariants. If FALSIFIED, that
    means the substrate's TriangulationProtocol has regressed and the
    fire #55 hardening was undone.

- id: CLAIM-substrate-self-00002
  _schema_version: "1.0.0"
  claim_category: substrate_self
  claim_text: |
    KillComponent with non-string kill_path raises TypeError on construction
    (T-2026-05-07-ST-fire29-002 Tier-3 contract).
  expected_verifier_primary: substrate_self_check
  expected_verdict: survived
  ground_truth_source: sigma_kernel/sigma_kernel.py:CLAIM input validation
  trust_tier: analytically_proven
  source_report: fire #29 + fire #33 mini-window contract
  parent_block: T-2026-05-07-ST-fire29-002
```

These are essentially substrate-tester pattern compiled into the claim format. They give the Learner explicit examples of the substrate's contract invariants. Volume: ~20-50 self-claims total across the substrate's primitives, refreshed when contracts change. Low ongoing volume, high anchoring value.

---

## 4. Outputs — how this flows to the Learner

Per-claim, the runner emits 1-3 LearnerRecords (one per emitted kernel opcode). The schema reuses the existing `LearnerRecord` from `prometheus_math/substrate_generation/learner_enrichment.py` with three claim-specific extensions:

- `claim_id` (the CLAIM-... identifier)
- `claim_category` (frontier_survey / calibration / boundary / substrate_self)
- `actual_verdict` (the verifier's verdict, possibly different from expected_verdict — disagreement is informative)

A successful frontier_survey claim produces three LearnerRecords with `episode_id` shared across them, distinguishable by `episode_phase` (claim / falsify / promote). Train/eval can split by `episode_id` (anti-leakage), by `claim_category` (balanced sampling), by `actual_verdict == expected_verdict` (correctness signal), or by `trust_tier` (filter ml_predicted claims out of evaluation).

The claim runner emits to a sibling JSONL file alongside the Tier-1 enriched generator output: `learner_records_claim_stack_<YYYY-MM-DD>.jsonl`. Same downstream LoRA pipeline consumes both streams.

---

## 5. Quality criteria and sampling discipline

Three rules to bias the stack toward research-grade rather than volume-only:

**Rule A: per-batch diversity.** Each Aporia-authored batch must include at least 3 claim categories and at least 5 distinct verifier types across the batch. A batch dominated by calibration_knots claims fails this rule because the Learner sees one verifier shape repeatedly.

**Rule B: expected-vs-actual mix.** Each batch must include claims with each of the four expected_verdict values (survived / falsified / open / conditional), in roughly 40% / 25% / 25% / 10% ratio. A batch that's 90% expected_survived fails this rule — the Learner doesn't see falsification or open cases.

**Rule C: trust-tier balance.** ml_predicted claims must not exceed 10% of any batch. analytically_proven + numerically_certified should be ≥70%. This prevents murmuration-style contamination of training corpus.

The runner enforces these rules at load time (rejects a batch JSONL that violates any of A/B/C, with a structured rejection reason). Aporia authors balanced batches; the runner verifies.

A fourth, softer rule:

**Rule D (suggested, not enforced).** Each batch should include at least one claim that the author suspects will be `actual_verdict ≠ expected_verdict`. The substrate's value compounds when it catches us being wrong. A batch of 100 claims with 100 expected agreements teaches the substrate nothing about its own failure modes; one disagreement per batch is the falsification-engine's actual food.

---

## 6. Open questions for Aporia

These are the points where my judgment is bounded and Aporia's authoring context is necessary:

1. **Volume budget per batch.** What's the right size — 50 claims? 200? 500? Smaller batches let us iterate; larger batches give more Learner volume per fire. My instinct is start at ~50 (1 day of authoring) and scale up after first runs show the verifier infrastructure holds.

2. **Calibration sampling rate.** The KnotInfo training_anchor has 2978 entries. We don't need 2978 claims per batch. Should the runner deterministically sample (e.g. first 100 + every 30th thereafter for a total of ~200) or should Aporia hand-pick a representative subset? Hand-pick scales worse but gets better Learner coverage per claim.

3. **Open-claim handling.** The kernel's verdict vocabulary is `verified | contradicted | inconclusive`. `open` claims map to `inconclusive` but the substrate doesn't currently distinguish "open" (no resolution exists) from "inconclusive" (verifier couldn't decide this run). Should we add a metadata field at FALSIFY time, or is the kernel's `inconclusive` + `caveats` enough? Adding a field is a contract-change ask; sticking with caveats is the conservative move.

4. **Composition_rule verification.** For frontier_survey claims derived from composition_rule blocks, what does verification look like? Re-run the substrate's TriangulationProtocol with the precondition_primitives as paths? Or just literature_audit the claimed confirmations? My instinct: literature_audit for the pilot, defer TriangulationProtocol routing to a Tier-2 enhancement.

5. **Substrate-self claim authoring discipline.** Should substrate_self claims be authored by Techne (as the substrate-tester role formally would) or by Aporia (as substrate-architect)? My recommendation: Techne authors substrate_self claims because they require code-level knowledge of the invariants; Aporia authors frontier_survey + calibration + boundary. Two authors per stack, separated by file (`aporia/meta/queue/claim_stack_aporia.jsonl` + `techne/registry/claim_stack_techne.jsonl`).

6. **Persistence model.** When CLAIM/FALSIFY/PROMOTE fires, the kernel writes to its SQLite/Postgres backend. For Tier-1 baseline (in-memory only, no production writes), what's the right artifact shape? My instinct: emit the LearnerRecord JSONL stream + a separate `kernel_trace.jsonl` of the substrate's own opcode emissions (for substrate-tester audit). Production writes (`--writeable`) gated on James compute decision per existing precedent.

7. **Failure budget.** If the runner can't verify 30% of claims (verifier timeout, citation_audit network failure, etc.), what's the right response? Retry on next batch? Mark the claims `inconclusive` permanently? Reject the batch? My recommendation: emit `inconclusive` with timeout/error metadata, but flag any batch where >20% of claims are inconclusive for Aporia review (might indicate a stack-shape problem).

8. **Pilot ordering vs the substrate-shaped pipeline pilot.** The substrate-shaped pipeline is gated on Aporia firing 3 queue entries. The claim-stack runner depends on schema parsing + validation infrastructure that's already shipped (the parse/validate scripts work on any substrate_block including claim blocks). Recommend: ship claim-stack runner + 50-claim seed batch in parallel with substrate-shaped pipeline pilot. The two workstreams compound — substrate-shaped pipeline produces anti_anchors and training_anchors that automatically feed the claim-stack author's source material.

---

## 7. Estimated scope + what ships first

If Aporia approves the sketch:

**Day 1 (Techne).** Ship `techne/contracts/substrate_block_schemas/claim_v1.json` schema + extend `aporia/scripts/validate_substrate_blocks.py` to validate claim blocks against it. Ship `prometheus_math/substrate_generation/tier_1_claim_runner.py` with the 7 verifier functions as stubs (return `inconclusive` with `not_yet_implemented` flag) + integration with the existing LearnerRecord enrichment. ~250 LOC.

**Day 2 (Techne).** Wire up the four most-leveraged verifiers: `citation_audit` (existing arxiv code), `catalog_lookup` (existing catalog_consistency code), `mpmath_compute`, `substrate_self_check`. The remaining three (`sympy_factor`, `triangulation`, `manual_review`) are stub-completable but lower-priority. ~150 LOC + smoke tests.

**Day 3 (Techne).** Seed-author ~10-20 example claims spanning all four categories so Aporia has a concrete reference document. Ship at `pivot/claim_stack_seed_examples_2026-05-NN.jsonl`. ~100 LOC of YAML examples.

**Day 4-5 (Aporia).** Aporia authors first 50-claim batch using the seed examples as template. Runs through validator. Iterates one cycle.

**Day 6 (Techne).** First runner execution against Aporia's 50-claim batch. Smoke results + per-verifier success rates + Learner record output for inspection.

**Day 7+ (joint).** Iterate on stack shape based on smoke results. Either scale up to 200-claim batches or refine the rules in §5 based on what produced informative records vs noise.

Total: ~5-7 days to a working baseline + first substantive claim run. Lower compute / coordination cost than the substrate-shaped pipeline pilot because it doesn't depend on a Gemini burn.

---

## 8. Cross-references

- `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md` (parent design for substrate_block schema family; this proposal adds claim_v1 to the family)
- `techne/PROMPT_2026-05-11_substrate_first.md` (Techne's directional update; claim-stack is a natural extension of Track 1)
- `pivot/strategic_pivot_2026-05-11_substrate_volume_first.md` (strategic context; this proposal addresses the substrate-volume-and-quality gate directly)
- `pivot/substrate_generation_pipeline_2026-05-11.md` (Tier-0/1/2/3 roadmap; claim-stack is Tier-1 extension)
- `prometheus_math/substrate_generation/learner_enrichment.py` (LearnerRecord adapter; reused with three claim-specific extension fields)
- `prometheus_math/discovery_pipeline.py` (existing verifier wiring; claim-stack reuses F-gate / catalog / mpmath verifiers)
- `sigma_kernel/sigma_kernel.py` (CLAIM/FALSIFY/PROMOTE opcodes; claim-stack invokes these directly)
- `sigma_kernel/triangulation_protocol.py` (one of the seven verifier types; cross-fire replication-status follows Dim 10 audit-prep)
- `techne/registry/anti_anchors.jsonl` (frontier_survey claim source material)
- `aporia/mathematics/tensor_open_problems_v1.md` (boundary claim source material)
- `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md` (Ergon's 10-dim discussion; this proposal addresses the underused-CLAIM-opcode shape implicit in their pilot LoRA design)

— Techne, 2026-05-11 (sketch for Aporia review)
