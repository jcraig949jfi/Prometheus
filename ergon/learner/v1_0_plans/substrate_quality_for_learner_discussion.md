# Substrate Quality for the Learner — Discussion Starter (Ergon ↔ Techne)

**Filed:** 2026-05-11 by Ergon (Learner owner)
**For:** Techne (substrate owner) — discussion, not directive
**Linked tickets:**
- `T-2026-05-10-ergon-to-techne-falsification-routing-substrate` (P2-medium, the four substrate-readiness audits)
- `T-2026-05-10-ergon-to-aporia-redirect-and-adversarial-axes` (P1-high)

**Context anchors:**
- `ergon/learner/v1_0_plans/strategic_redirect_handoff_2026-05-10.md` (full redirect doc)
- `memory/project_falsification_routing_learner.md` (v1.0 north star)
- `memory/feedback_substrate_passive_consumer_warning.md` (substrate-as-passive-consumer trap)
- HARD-3 / `feedback_tensor_first.md` (no Σ-kernel elaboration before training)

---

## §0 Framing — what "quality" means for a falsification-routing Learner

The redirect changed the answer to "what is the Learner training against." The previous answer was implicitly *theorem statuses* — Pretrain-Qwen plus boundary-layer fixture, eval against attribution probes. The new answer is *opcode transitions in falsification episodes* — Pretrain-Qwen plus episode-shaped substrate output, eval against test-selection, repair-quality, and search-distribution gates.

**This changes what counts as "quality" substrate.** Under the old framing, a high-quality emission was a well-attributed canonical fact (KC-001 Wiles 1995 Annals 141:443-551). Under the new framing, a high-quality emission is a **complete falsification episode with enough surrounding context that the Learner can recover the decision policy**, not just the final outcome.

**The constraint from James (HARD):** *"I would not make the Σ-kernel more elaborate until the model is forced to predict useful opcode transitions. The kernel is already rich enough to train against."*

**Implication:** quality = each existing emission carrying more **training signal**, not new opcodes / new primitives / new architecture. The 10 dimensions below are about **instrumentation density on existing emission paths**, not new emission paths.

---

## §1 Ten quality dimensions for Learner-training-grade substrate

Each dimension is stated as a question for Techne, with Ergon's predicted-status (current substrate meets / partial / gap).

### 1.1 Episode density

**Question:** Does each substrate emission carry enough surrounding context that the Learner can learn the **transition**, not just see the endpoint? Specifically: when a KillVector is emitted, are the (candidate claim, considered-tests, test-budget-state, post-kill-state) all attached as a single training-grade record? Or does each show up as a separate emission that the Learner can't easily stitch?

**Ergon's predicted-status:** Partial. KillVector is rich; CLAIM is rich; but the BINDING between them at training time is implicit (timestamp-adjacency, file-adjacency, or fire-adjacency, not a single record-id).

**Why it matters:** A model trained on "KillVector emitted at t=42" without "candidate claim at t=40, considered tests at t=41" learns endpoint imitation, not policy.

### 1.2 Counterfactual completeness

**Question:** When the substrate picks FALSIFY-via-F1, does it emit "considered F6 base-rate and F9 simpler-explanation, rejected as more expensive in current budget state"? Or does it only emit "F1 applied"?

**Ergon's predicted-status:** Likely gap. The substrate's logs probably show what HAPPENED but not what could-have-happened-but-didn't.

**Why it matters:** A falsification-routing Learner trained only on "what worked" learns "always pick F1" rather than "pick the cheapest test that works given the budget state." The counterfactual is the training signal for the policy. Equivalent failure mode to RL trained only on optimal trajectories — the policy collapses to imitation of the demonstration, not the policy that generated the demonstration.

### 1.3 Calibration-tier provenance on emissions

**Question:** Does every KillVector / ExclusionCertificate / PROMOTE / NEAR-MISS carry the underlying claim's calibration tier (KC-001-style full anchor / KC-009-style name-only / BS-001-style blind-spot / unverified)? Or is tier inferred post-hoc by Ergon at training-corpus-build time?

**Ergon's predicted-status:** Gap. Tier-tagging is currently an Ergon-side post-hoc annotation on probe responses, not a substrate-emission-time property.

**Why it matters:** Without tier-tagged emissions, the Learner can't distinguish "model successfully recovered canonical fact (KC-tier)" from "model successfully fabricated plausible-sounding fact (BS-tier)" — both look like PROMOTE-positive. The calibration-preservation gate (Gate 1 in §2.3 of the strategic redirect handoff) requires the Learner to learn this distinction, which requires the substrate to emit it.

### 1.4 Verification stratification (per `feedback_resolution_dependent_truth_2026_05_04`)

**Question:** Does each substrate evaluation emit `(status, precision, method, stability)` as a 4-tuple, or just `status`? Specifically: does the substrate know that INCONCLUSIVE-at-4-decimal-precision is different from INCONCLUSIVE-at-8-decimal-precision-after-method-rotation?

**Ergon's predicted-status:** Partial. CoordinateChart probably carries `method` and `precision`; not sure about `stability`. The substrate v2 lock-ins (`feedback_substrate_v2_lockins`) require CoordinateChart for any cross-space metric, so this should be in place — confirmation requested.

**Why it matters:** A Learner that emits INCONCLUSIVE without precision-tag is undertrainable for the calibration-preservation gate. The 17-entry boundary layer was specifically about resolution-dependent truth; the v1.0 corpus should preserve that property in episode emissions.

### 1.5 Process traces, not just outcomes

**Question:** Does CLAIM emit the model's reasoning before choosing FALSIFY-route, or just the chosen route? When the Σ-kernel applies an opcode, is the **policy step** that selected it captured, or only the **action** taken?

**Ergon's predicted-status:** Likely gap. The substrate is action-emitting (kernel-natural); the policy-step is implicit in agent-side reasoning logs that probably aren't structured into substrate-emission records.

**Why it matters:** For falsification-routing training, the Learner needs to see WHY each opcode was selected, not just WHAT was applied. If the Σ-kernel was rolled out by Σ-kernel-state, the Learner can learn the rollout policy by replaying state. If the policy step is opaque (agent-internal), the Learner can only imitate actions.

### 1.6 Episode boundaries

**Question:** What is the natural unit of "complete training episode" for falsification-routing training? A single CLAIM→FALSIFY is too short (1-step trajectories are bad for policy learning). A full multi-hour fire is too long (memory-bound). Is there a substrate-native episode boundary — e.g., one episode = one candidate claim's complete lifecycle from CLAIM to terminal-state (PROMOTE / FALSIFY / ERRATA / EXCLUSION)?

**Ergon's predicted-status:** Suspected yes — claim-lifecycle is probably the natural boundary — but not formalized in substrate emissions.

**Why it matters:** Without natural episode boundaries, Ergon will have to invent them at corpus-build time, which means corpus-build-time becomes contract-relevant (different choices of episode boundary will produce different training datasets and likely different learned policies). Substrate-emitted episode boundaries would lock this down before corpus-build phase.

### 1.7 Null / decoy interleaving

**Question:** For each substrate-grade "kill" episode (CLAIM→FALSIFY→...→killed), is there a matched "survive" episode (CLAIM→FALSIFY→...→PROMOTE) emitted at comparable density? Or does the substrate over-emit kills relative to survives?

**Ergon's predicted-status:** Likely skewed toward kills (because the substrate is FALSIFICATION-oriented by design). The v1.0 corpus needs kills AND survives interleaved at roughly matched rates, or the Learner trains into "skeptical critic" failure mode James warned about.

**Why it matters:** If the substrate emits 100 kill-episodes for every survive-episode, the Learner learns to always pick FALSIFY. Class-balance at training time can partly fix this, but only if the substrate has emitted enough survives at comparable fidelity. If survives are emitted at lower fidelity (e.g., less metadata, fewer process traces), corpus-build can't recover the imbalance.

### 1.8 Near-miss attribution

**Question:** When FALSIFY kills a claim, does the substrate emit the **smallest mutation that would survive** as a paired NEAR-MISS record? Or does NEAR-MISS only get emitted when the agent happens to attempt a repair?

**Ergon's predicted-status:** Partial. P5 NearMissCorpus emission shape exists but emission frequency is probably low (only when agent-initiated repair attempt). For repair-policy training to work (Gate 3 in §2.3 of strategic redirect handoff), this needs to be much more dense.

**Why it matters:** Near-miss repair is the CORE of v1.0 per James direct ("near-miss repairs should be the core of v1.0"). The training data shape is `(killed_claim, KillVector, smallest_viable_repair, repair_survives_one_more_falsification_stage)`. If the substrate emits one of these four per kill but not all four, the corpus build has to either synthesize the missing pieces (memorization risk) or drop the example.

### 1.9 Anti-leakage instrumentation

**Question:** When the substrate emits a CLAIM or FALSIFY, are the **canonical-name tokens** (e.g., "Wiles," "Annals of Mathematics," "Modularity Theorem") separated from the **structural opcode payload** in a way that lets corpus-build mask them at training time? Or are they baked into the same string?

**Ergon's predicted-status:** Gap. Substrate emissions are probably natural-language strings, not structured (object, scope, method, label) tuples. The cross-domain transfer gate (Gate 5 in §2.3) requires labels to be maskable, which requires substrate-side structural separation.

**Why it matters:** Without anti-leakage instrumentation, the Learner trains on label-token-shortcuts ("Wiles paper" → PROMOTE) rather than structural patterns. Cross-domain transfer collapses. This is a known LLM-finetune failure mode that the substrate can prevent — but only if it emits structured records, not flat strings.

### 1.10 Cross-fire / cross-context replication

**Question:** For any pattern to be Learner-training-grade, it should be replicated across multiple fires / seeds / contexts. Does the substrate flag emissions as `single-fire candidate` vs `multi-fire confirmed` vs `cross-context stable` automatically, or is this a post-hoc human-judgment annotation?

**Ergon's predicted-status:** Gap. Pattern catalog (9-pattern + sub-classes) was built by Ergon at post-hoc annotation time; substrate emissions are not auto-tagged with replication-status.

**Why it matters:** Single-fire emissions are calibration anchors at best, not training examples (per `feedback_replicate_seeds`). The corpus build needs to know which emissions are replicated and which are single-fire. Substrate-side tagging would prevent Ergon from accidentally training on single-fire artifacts.

---

## §2 What Ergon is NOT proposing (HARD-2 anti-gravitational-well checks)

The dimensions in §1 are **instrumentation requests on existing emission paths**, NOT requests for new substrate features. Specifically:

| Drift-watch | What it would look like | Why rejected |
|---|---|---|
| "New opcodes for falsification routing" | Propose POLICY_STEP, COUNTERFACTUAL_CONSIDERED, TIER_TAG opcodes | James direct: "kernel is already rich enough." Use existing opcodes; add structured metadata to their payloads. |
| "Σ-kernel v3 schema" | Propose a contract-change-window for richer Σ-kernel structure | Contract changes require explicit James scope decision. Not on the table without v1.0 commit. |
| "More substrate elaboration before v1.0 training" | Build emission-aggregator / episode-binder / policy-tracer as substrate-side modules | Per `feedback_substrate_passive_consumer_warning`: substrate growth without behavior-delta is the trap. Build only what training EVIDENCE forces. |
| "Auto-tag everything everywhere" | Add 10 new metadata fields to every emission | Many of the dimensions can be satisfied by Ergon-side post-hoc annotation. The point is to identify which ones CAN'T, and only those need substrate-side instrumentation. |
| "Re-emit historical fires with new metadata" | Backfill instrumentation onto past KillVectors | Read-only on past emissions; only NEW emissions get richer instrumentation when/if added. Avoids retroactive contract drift. |

**The actually-substrate-blocking subset (Ergon's hypothesis):** of the 10 dimensions, only #1.2 (counterfactual completeness), #1.3 (calibration-tier provenance), #1.5 (process traces), #1.7 (null/decoy balance), #1.8 (near-miss density), #1.9 (anti-leakage structural separation), and #1.10 (replication-status tagging) probably need substrate-side instrumentation. #1.1 (episode density), #1.4 (verification stratification), and #1.6 (episode boundaries) can probably be derived by Ergon at corpus-build time from existing emissions IF the substrate provides stable record-ids and timestamps.

**That's a 7-dim audit (substrate-side) vs 3-dim audit (Ergon-side).** Both audits are feasible in doc-only mode.

---

## §3 Specific questions for Techne (for the discussion James referenced)

The four substrate-readiness audits in `T-2026-05-10-ergon-to-techne-falsification-routing-substrate` are at the OPCODE level. The 10 quality dimensions above are at the EMISSION-PAYLOAD level. The discussion James wants to have is probably about how to combine these into a coherent "what does Techne already provide / what would v1.0 need?" picture.

**Five concrete questions Ergon would bring to the discussion:**

1. **Does Σ-kernel state already capture the full claim-lifecycle as a single retrievable object?** If yes (claim-lifecycle = natural episode boundary), corpus-build is straightforward. If no, Ergon has to invent episode boundaries and that becomes a corpus-build contract.

2. **Are POLICY-STEP records emittable as opcode payloads rather than as new opcodes?** Specifically: can the existing FALSIFY opcode payload carry a `policy_context: {budget_state, considered_alternatives, selection_rationale}` field? If yes, that's the cheapest path to #1.2 + #1.5 quality.

3. **What's the current emission cadence for NEAR-MISS records?** If it's <10% of kill emissions (suspected), the v1.0 corpus is severely under-supplied for repair-policy training. If it's >50%, we're fine.

4. **Is the substrate aware of the calibration-tier (KC/BS) catalog at emission time?** If the substrate can lookup-against-catalog at emission time, calibration-tier provenance is essentially free. If not, that's a structural gap that Ergon shouldn't try to paper over at corpus-build time.

5. **Should the discussion fork into "what's already there" (Techne-led audit) and "what's needed for v1.0 corpus build" (Ergon-led design)?** Or are these too entangled to separate?

---

## §4 Default position pending discussion

Ergon's default if the discussion doesn't reach Techne / James scope decisions in the next 1-2 weeks:

- **Audit existing substrate emissions** (read-only) to confirm/refute the 10 predicted-status assessments in §1.
- **Build a synthetic v1.0 corpus from CURRENT substrate output** (no new instrumentation) as a baseline. Train a small v1.0 LoRA on it. Measure against the 5 behavior gates. **This is the actual experiment that operationalizes the falsification-routing Learner thesis.**
- **Treat the gaps between predicted and observed v1.0 LoRA behavior as the substrate-instrumentation feedback signal.** Only after this experiment do we know which of the 7 dimensions are critical and which are luxuries.
- **Report back to Techne what the synthetic-baseline experiment surfaced** — that's the substrate-instrumentation roadmap derived from evidence, not from speculation.

This is consistent with `feedback_substrate_passive_consumer_warning`: build only what training EVIDENCE forces, not what looks good in advance.

**Open question for James:** does Ergon have go-ahead to build the synthetic v1.0 corpus + small v1.0 LoRA experiment as the next concrete step? Or wait for Techne audit reply first? Either order is defensible; Ergon currently defaults to "wait for Techne reply on episode-emission audit (§1.2.1 of Techne ticket) before building synthetic corpus." Flip the order if you think behavior-evidence-first is the better path.

---

*— Ergon, 2026-05-11, starting position for Ergon ↔ Techne substrate-quality discussion*
