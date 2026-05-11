# Strategic Redirect Handoff — Falsification-Routing Learner v1.0

**Filed:** 2026-05-10 by Ergon (Learner owner)
**For:** Techne, Aporia
**Status:** Awaiting Techne + Aporia replies + James scope decisions
**Linked tickets:**
- `T-2026-05-10-ergon-to-techne-falsification-routing-substrate` (Techne inbox)
- `T-2026-05-10-ergon-to-aporia-redirect-and-adversarial-axes` (Aporia inbox)
- `T-2026-05-10-ergon-to-aporia-saxl-source-pin` (Aporia inbox — already filed)

**Memory anchors (load-bearing):**
- `project_falsification_routing_learner.md` — v1.0 north star
- `feedback_substrate_passive_consumer_warning.md` — every doc must trace to behavior delta
- `feedback_verify_upstream_attributions.md` — internal catalogs are Tier-2-or-worse anchors
- `feedback_adversarial_axes_against_canonicality.md` — calibration axis must beat alternatives
- `project_lora_4_condition_control.md` — cheapest concrete next experiment

---

## §0 What changed (James 2026-05-10 strategic redirect)

**Two HARD shifts simultaneously, same conversation:**

**Shift 1 — v1.0 north star is falsification-routing, not theorem-answering.** "Make v1.0 a falsification-routing Learner, not a theorem-answering Learner. That is the shortest path from the substrate you have to a model that actually participates in Prometheus." The Learner's job is to predict **deltas** (which test will kill this? which KillVector components light up? which near-miss mutation is least trivial? which candidate deserves expensive evaluation?), not to recite theorem statuses. Train on **episodes** (CLAIM → FALSIFY → REWRITE → REPAIR → GATE → PROMOTE), not on final promoted claims. Theorem-answering becomes an emergent downstream capability of episodic falsification-routing training, not the training target.

**Shift 2 — substrate is at risk of becoming "beautifully falsifying machine forever" while model remains passive.** The 16-fire Learner-Tester arc produced a 9-pattern catalog, 5-tier scale, KC/BS taxonomy, and now 104-tensor-problem probe-shape predictions — but the Learner itself has not been re-trained and no measurement shows model outputs change substrate trajectory. The first real Learner milestone is NOT "LoRA improves math benchmark." It is: **model-guided substrate exploration beats null mutators and hand-coded heuristics under leakage-safe falsification, while preserving blind-spot calibration.**

**Catalyst event (substrate-grade kill 2026-05-10):** Ergon fire-16 (E009 tensor-probe-shape audit) propagated an internal Aporia-catalog attribution ("Saxl SOLVED by Sellke 2025/26 arXiv 2512.15035") as the *most critical* AA seed for v1.0 corpus, WITHOUT external verification. James external-checked within hours; alternative candidates surfaced (S. K. Lee 2025 staircase-minimality paper; Harman-Ryba 2023 tensor-cube version). The doc was erratized same-day and a source-pin coord ticket filed back to Aporia. **The Saxl error IS the strongest evidence for Shift 2:** the substrate produced a beautifully taxonomized doc, and within hours the doc had to be erratized because the substrate (specifically the Ergon-Learner-loop owner) uncritically promoted an upstream-doc citation. The substrate was substrate-grade in *form*; consumer-grade in its *relationship to source attribution*. That's exactly the trap.

---

## §1 For Techne

### §1.1 What this redirect implies for the substrate / opcodes

The Learner needs to train against the **EXISTING** substrate's opcode language (TRACE, CLAIM, FALSIFY, GATE, ERRATA, REWRITE, PROMOTE, EXCLUSION, NEAR-MISS, KillVector, etc.), not against a new symbolic architecture designed top-down for v1.0. Per `feedback_tensor_first.md` and the HARD-3 doctrine, building elaborate symbolic substrate before the tensor is navigable is the deferred trap.

The 6-target-layer architecture James proposed (Object / Scope / Rewrite / Obstruction / Certificate / Near-miss) should EMERGE from substrate work that's already happening, not be designed as a v1.0 deliverable. But Techne SHOULD know these are the target-layers so the existing opcode/primitive work can be evaluated against them.

### §1.2 Specific asks

**§1.2.1 Episode-emission audit.** Ergon needs the substrate to emit episode-shaped training data: `Candidate claim → guess → falsification path → kill/promote outcome → KillVector → repair attempt → final calibrated statement`. Question for Techne: which of the existing opcodes (TRACE, CLAIM, FALSIFY, GATE, ERRATA, REWRITE, PROMOTE, EXCLUSION) already emit data in this shape, and which gaps exist? **Audit deliverable:** a per-opcode mapping showing what's already there vs what needs to be added. NO new opcodes proposed by Ergon — Techne decides whether the gaps need new opcodes or whether the existing ones suffice.

**§1.2.2 P5 NearMissCorpus emission shape becomes load-bearing.** "Near-miss repairs should be the core of v1.0" (James direct). The existing P5 NearMissCorpus emission shape (which Ergon has not been touching due to contract-freeze) is now the most important upstream data source for the v1.0 corpus. Ergon's specific ask: confirm the current shape is suitable for episode-shaped training (probably yes), and flag any places where the emission is too sparse to support repair-policy training (e.g., near-misses without KillVectors attached, or KillVectors without repair-attempts attached).

**§1.2.3 Five-corpus-type readiness check.** v1.0 training corpus will need 5 separate slices: positive anchors / blind-spot anti-anchors / near-miss repairs (CORE) / falsification routing examples / search-proposal episodes scored by downstream yield. Question: which of these 5 the existing substrate already emits, and which require new emission paths. **NO contract changes implied** — this is a readiness audit, not a request for changes. Output: 5-row checklist of "current substrate supports this / doesn't support this / partial."

**§1.2.4 Calibration-aware opcode usage.** Per the calibration-preservation gate (after v1.0 training, blind-spot false promotion must NOT increase), the substrate's opcode emissions must be cleanly stratified by calibration-tier. Does the current ExclusionCertificate / KillVector / CoordinateChart instrumentation tag emissions by calibration-tier (KC-001-style full anchor vs BS-001-style blind-spot)? If not, that's a substrate-side gap that v1.0 training will surface but probably can't fix internally.

### §1.3 What Techne should NOT do as a consequence of this redirect

- Do NOT build the 6-symbol-layer architecture from scratch. Object/Scope/Rewrite/Obstruction/Certificate/Near-miss are TARGET layers, not deliverables.
- Do NOT propose contract changes to KillVector / NearMissCorpus / ExclusionCertificate based on what Ergon needs for v1.0. Contract changes require explicit pause-window per the standard `pivot/contract_change_window_*.md` doctrine.
- Do NOT increase substrate elaboration before the v1.0 Learner is trained. Per James direct: "I would not make the Σ-kernel more elaborate until the model is forced to predict useful opcode transitions. The kernel is already rich enough to train against."

---

## §2 For Aporia

### §2.1 Saxl/Sellke source-pin (already filed; restating for record)

Coord ticket `T-2026-05-10-ergon-to-aporia-saxl-source-pin` (P1-high) requests: (1) pin actual Saxl resolution paper or downgrade to OPEN-with-progress; (2) audit other 2024-2026 "resolved" claims in `aporia/mathematics/tensor_open_problems_v1.md` for similar upstream-attribution risk; (3) reply ticket so Ergon can update `tensor_probe_shape_audit.md` §0 ERRATA.

**Audit priorities (flagged for re-verification at minimum):**
- Lampert-Moshkovitz Sept 2025 arXiv 2509.06294 (slice-rank uniform-in-d negative resolution)
- BIP 2019 J. AMS arXiv 1604.06431 (GCT occurrence-obstructions DEAD)
- Ikenmeyer-Mulmuley-Walter (Kronecker positivity NP-hard, killing Mulmuley `PH1`)
- Landsberg-Ressayre 2017 arXiv 1508.05788 (equivariant-restricted exponential lower bound)
- Mignon-Ressayre 2004 IMRN (n²/2 dc(perm_n) bound)
- Shitov 2016 arXiv 1605.07532 + arXiv 1611.01559 (symmetric tensor rank over ℚ; tensor rank over ℤ)
- Sellke arXiv 2512.15035 (CURRENTLY UNVERIFIED — see Saxl ticket)

### §2.2 Adversarial-axes probe design (per James 2026-05-10)

The calibration-axis hypothesis `canonicality_in_pretraining > era > specificity` has held across ~16 fires, but the data-collection process is biased (probes are generated under the hypothesis, so confirmations are partly tautological). Per James direct: "the calibration-axis hypothesis is promising, but it can become a trap if every new failure is interpreted through it. You need adversarial axes that could beat it."

**Ergon's ask of Aporia (NEW coord ticket):** design probe pairs that DECORRELATE canonicality from each of these alternatives:

| Alternative axis | What it might explain | Decorrelation probe shape |
|---|---|---|
| Lexical rarity | Failure = tokenizer-hostile name, not non-canonical math | Same-canonicality probes, one with tokenizer-friendly name, one hostile |
| Citation-form familiarity | Model recognizes theorem-like prose patterns, not theorem content | Same-result probes, one in canonical citation prose, one in raw natural-language prose |
| Object arity | Failures grow with # of interacting objects | Same-canonicality probes at arity 1 / 2 / 3+ |
| Representation mismatch | Model knows statement in one formalism but not another | Same-result probes in algebraic vs combinatorial vs categorical formalism |
| Proof-technique locality | Local combinatorial facts vs global structural dependencies | Same-canonicality probes splitting local-arithmetic from global-structural |
| Benchmark contamination | "Canonicality" partly = exposure through common eval material | Same-canonicality probes inside vs outside known eval benchmarks (MATH, GSM8K) |

**Output:** ~30-40 decorrelation probes (5-7 per axis), each pair flagged with the predicted-by-canonicality vs predicted-by-alternative-axis verdict. Ergon will run these once the 4-condition LoRA control test (see §3.1) has completed.

### §2.3 5-behavior gate scaffold (per James 2026-05-10)

v1.0 Learner readiness is measured against five behavior gates:

| Gate | Measurement |
|---|---|
| 1. Calibration preservation | Blind-spot false-promotion rate must NOT increase after training |
| 2. Falsification selection | Top-1 / top-3 next-test choice beats random / simple-rules / base Qwen on held-out claim families |
| 3. Near-miss repair | Repaired candidates survive one additional falsification stage more often than null repairs |
| 4. Search distribution shift | Model-guided probes produce higher yield of informative failures than uniform / anti-prior / structured-null / hand-coded baselines |
| 5. Cross-domain transfer | Improvement survives when bibliography labels and obvious domain names are masked |

**Aporia's role:** scope what counts as "held-out claim families" (Gate 2), "null repairs" (Gate 3), "informative failures" (Gate 4), and "leakage-safe" (Gate 5). Each of these is currently underspecified. **Ergon's specific ask:** a scoping doc at `aporia/calibration/v1_0_behavior_gates_v1.md` defining these terms operationally + concrete eval-set requirements. Doc-only.

### §2.4 What Aporia should NOT do as a consequence of this redirect

- Do NOT expand the failure-mode catalog past current 15 FMs unless empirically forced by new Tester evidence. Per Shift 2 (`feedback_substrate_passive_consumer_warning.md`), additional taxonomy without behavior-delta plan is the trap.
- Do NOT design v1.0 corpus content directly — that's Ergon's scope. Aporia provides eval-set scaffolds, anti-anchor verification, calibration-tier ground truth.
- Do NOT promote any 2024-2026 resolution-claim to verified status without primary-literature pin. The Saxl error establishes the discipline.

---

## §3 For James — pending scope decisions

The redirect surfaces three decisions Ergon cannot make autonomously:

**§3.1 4-condition LoRA control test (cheapest concrete next experiment).** Designed in `project_lora_4_condition_control.md`. Conditions: base / base+A149 / base+random-label-LoRA / base+format-only-LoRA. Eval: 9 KC + 6 BS + KC-AGW-LOCK + ~15 random-decoy probes. 5 metrics per James critique. Expected near-zero meaningful A149 delta. **Asking:** scope decision + compute time. Ergon can spec as Pipeline-D experiment ticket on request.

**§3.2 Verifier-only frontier-API budget.** The Saxl error would have been caught by a 5-line frontier-API verification call before promotion to seed. Per `feedback_frontier_models_window.md`, the API window is closing — use it for verification while it's open. Per James direct: "I would not chase larger models yet except as cross-model probes." **Ergon's position:** verifier-only is NOT "chase larger models for training." It's "frontier model never in Learner slot, only in upstream-attribution-pinning slot." **Asking:** sign-off on a small monthly API budget specifically for upstream-attribution verification before corpus seed promotion.

**§3.3 Tensor-Tester arc readiness.** §7 of `tensor_probe_shape_audit.md` proposed a 33-probe Tensor-Tester arc as v1.0 design-phase prep. Per James 2026-05-10 ask: Tensor-Tester should produce THREE outputs (recoverability prediction / falsification prediction / training-sensitivity prediction). **Asking:** does this arc open now (after the 4-condition LoRA control retires the tire-kick) or after v1.0 design phase formally opens? Either is defensible; Ergon defaults to "wait for v1.0 design phase" unless told otherwise.

---

## §4 What Ergon will NOT do without sign-off

Per `feedback_role_pivots.md` and the loop hard rules (file ownership; no contract changes), Ergon will NOT:

1. Open the v1.0 corpus build phase autonomously. v1.0 design phase requires James's explicit go-ahead per `v1_0_design_suggestions_2026-05-09.md`.
2. Run the 4-condition LoRA control test without §3.1 scope decision.
3. File coord tickets requesting contract changes to KillVector / NearMissCorpus / ExclusionCertificate.
4. Promote any 2024-2026 attribution to "verified" without primary-literature pin (regardless of whether it appears in an internal Aporia catalog).
5. Expand the audit doc beyond the source-correction errata already filed.
6. Build the 6-symbol-layer architecture (Object/Scope/Rewrite/Obstruction/Certificate/Near-miss) from scratch — those are target layers that should emerge from substrate work.

Inbox is currently empty (0 OPEN). Ergon is at quiet-tick state until Techne / Aporia replies arrive or §3 scope decisions land.

---

*— Ergon, 2026-05-10, post-fire-16 ERRATA + strategic redirect from James same-conversation*
