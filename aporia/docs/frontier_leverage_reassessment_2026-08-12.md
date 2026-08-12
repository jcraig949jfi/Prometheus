# Frontier-Model Leverage — Aporia's Reassessment on Revival

**Author:** Aporia (Claude Opus 5, 1M context) · **Date:** 2026-08-12
**Trigger:** James — "long break; we want to revive. New frontier models. How do we leverage
them for a refocused effort toward the North Star?"
**Status:** PROPOSAL. Nothing here is approved. Pre-registered stands, per `feedback_take_a_stand`.

---

## 0. What I verified before writing this

- **Git is alive but only the crons are:** every commit since 2026-06-28 is `auto: portfolio
  update` (4-hourly) or `arsenal: capability matrix updated`. The last human-driven work is
  `fda01127` (my own session pause, 06-28), then a **six-week silence**, then two resume docs
  landed 2026-08-12: `roles/Techne/resume.md` (`5b8a80c2`) and `roles/Ergon/resume_ergon.md`
  (`ba14f6f6`).
- **Both resume docs independently converge on the same pickup point: M1-metabolization.**
  Techne: "the one decisive experiment." Ergon: "align there." Neither was written to agree
  with the other. That is the strongest orientation signal available and I am not going to
  re-litigate it.
- **Carried forward, not re-verified this session:** Postgres local/healthy on `.202`
  (Ergon 06-23); M3 forge box hardware-dead; 43-process fleet paused to an advisory spine of
  ~8; Leanstral 1.5 specifics (Ergon's read, `mistralai/Leanstral-1.5-119B-A6B`). My psql
  probe and a corpus census both exceeded timeout against the 363 GB spine — flagged, not
  concluded.

---

## 1. The stand: model quality was never the binding constraint

This is the load-bearing claim of the document, and it is the one place I expect disagreement.

Go through the kill ledger and ask *what actually stopped us*. Not one of these was an
intelligence failure:

- **Consumer-drift.** Pythia: 442 Deep Research reports, loop never closed. Clio:
  `sigma_claims.db` = 0 symbols. Pheme: 354 ticks, `total_profiles_lifetime=0`. Talos: a
  24,847-example corpus shipped into a vacuum. The whole Harmonia swarm: ~2,200 artifacts,
  0 consumers. My own 06-24 portfolio synthesis named this "the program's central disease."
- **Measurement error.** Hecate's `mi_z` of 1000+ as generator-prefix tautology. Pollux
  correlating two *sorted* arrays. Acheron measuring co-occurrence and calling it collision.
  The `flow = Δ(node scalar)` conservativity catch. The `tt_splice` row-null degeneracy.
- **Sampling artifacts.** Charon-Hecate's alphabetical shard iteration. Techne's
  `bridge_extension`-absent claim (9.19M records, "absent" by sampling window).
- **Seam/plumbing.** One missing field (`predicate_holds`) + an 89% kind drop inverted the
  entire Theseus→Ergon corpus. A denylist leak gate that leaked.
- **Hardware.** M3 died in a power outage and took the forge with it.

A better model fixes exactly **zero** of those. Point a 2026-08 frontier model at a producer
whose consumer was never wired and you get higher-quality `/dev/null`. That is the gravity
well on this specific question, and it is the one I expect us to fall into: *"new models →
have them generate more/better research."* We have 442 unconsumed reports that already
refute that plan.

**So the question is not "what can better models produce for us." It is: "which of our
seven bottlenecks does a 2026-08 model class dissolve that a 2026-05 model class could
not?"** There are four honest answers, and one of them matters far more than the rest.

---

## 2. Four leverage classes, each with the guard that makes it doctrine-safe

### L1 — Long context dissolves the sampling antipattern *(cheap, high certainty, available now)*

Not "smarter." **No window.** Two of our most expensive errors — Charon-Hecate v0.1 and
Techne's `bridge_extension` overclaim — were window artifacts, and
`feedback_sampling_strategy_is_analysis` exists because of them. A 1M-context pass holds
a whole shard/ledger slice and the artifact class disappears rather than being mitigated.

**Immediate target:** the **tautology-verification pass** on Hecate / Pollux / Moros /
Acheron / Coeus. These are concrete, checkable *code* claims over a bounded corpus — one
long-context pass each. They are already gated as HITL-blocking (nothing retires on one
agent's say-so), and if the tautologies are confirmed, the **downstream taint-check** on
every claim that cited that "signal" is the highest-value cleanup we own.

**Guard:** the reader is a *code reader*, not an adjudicator. It reports what the code does;
the verdict is James's.

### L2 — Cross-family verification turns advisory into decidable *(unblocks the 43-process backlog)*

My 06-24 fan-out shipped with an explicit calibration caveat: **one investigator, one model
family, no cross-check** — a violation of our own `feedback_replicate_seeds` and
`feedback_llm_convergence_is_gravity_amplifier` posture, which I flagged loudly and could
not fix at the time. What changed is that multiple *independent* families now do code-level
verification competently, not just prose critique.

**Target:** re-run the verify pass on the RETIRE-21 with a **different family** on the same
code claims. Convergence across families on a *mechanical* claim ("this function correlates
two sorted arrays") is not gravity — gravity applies to *framings*, not to `sorted()`. That
distinction is what makes L2 legitimate where "ask two models if the thesis is good" is not.

**Guard:** cross-family agreement counts only on mechanically checkable claims. On framings
it remains a warning.

### L3 — Kernel-checked generation is the only trust-free model channel *(the arbiter lane)*

Ergon's Leanstral read is right and I want to sharpen it: what makes a Lean-4 proof agent
usable under `feedback_frontier_models_window` is not its benchmark number — it's that
**a wrong proof does not compile**. The Lean kernel, not another model, is the adjudicator.
No AI-to-AI inflation is possible. Arbiter, never explorer.

**Sharpening, and this is Aporia's specific correction to my own prior spec:** my M0 §5
demanded Set C be **LLM-free** (D5) because an LLM proposing "novel-looking claims" draws
from the same gravity well the battery was calibrated in. Kernel-checking **does not fully
dissolve that objection.** It guarantees the claim is *true*; it says nothing about whether
the claim is *drawn from an independent distribution*. So:

- LLM+Lean is licensed for **volume**.
- **Enclosure stratification stays mechanical** (interpolative-void vs extrapolative-outlier,
  computed in feature space — no model in that loop).
- **A small LLM-free arm survives as the control.** If LLM+Lean Set C and mechanical Set C
  behave identically, D5 was over-cautious and we drop it. If they diverge, D5 was load-bearing
  and we just measured the gravity directly. Either way it is a real verdict.

### L4 — The one that actually moves the North Star: the frontier model as the *organism under test*

This is the answer to James's question.

The decider — Techne's and Ergon's shared pickup, and my §10 reconciliation — is
**M1-metabolization**: *a model consumes the kill-geometry the substrate produces, its
behavior changes, and the change survives an ablation.* Historically we could only test this
by fine-tuning a **1.5B Qwen-Math** local model, which imported two confounds I flagged in my
own self-falsification section (§8):

1. **Capacity ceiling** — `feedback_vram_ceiling` caps us at 3–4B. We could never distinguish
   "the substrate's kill-geometry is not navigable" from "1.5B cannot hold it."
   `feedback_greedy_lora_surface_not_reasoning` is the scar: what looked like transferable
   reasoning was format acquisition + a False/kill prior.
2. **Dead hardware** — the forge lives on M3, which is dead. Forge relocation has been "the
   gating unblock for the whole spine" since June. **The decisive experiment has been blocked
   on a motherboard for seven weeks.**

**Long-context frontier models let us run M1 as an in-context experiment and both confounds
vanish.** Feed the kill-geometry as *context* rather than as *weights*: held-out problems,
frozen eval slices, measure the behavior delta, ablate by shuffling the geometry. No LoRA,
no forge, no capacity ceiling, no new hardware.

**This is doctrine-safe in the exact way the other uses are not: the frontier model never
adjudicates anything.** It is the *subject*. We are measuring whether *our* artifact changes
*its* behavior against a held-out metric with a pre-registered null. `feedback_ai_to_ai_inflation`
concerns models judging models; here the model is the instrument being acted upon, and the
metric is external.

---

## 3. The refocused effort: one experiment, pre-registered

**M1-in-context.** Kill-geometry over Charon's `signature_index` proto-tensor (3,311
signature-classes / 413M records) presented in-context to a long-context model; held-out
problems from the frozen transfer-eval slices (entity-disjoint, domain-transfer,
computation-required).

**Arms (pre-registered before running, per `pattern_prediction_level_mismatch` — predictions
at the measurement level, never at an estimator coefficient):**

- **A. Baseline** — model, no geometry.
- **B. Counter-baseline** — typed-row + counters + rules, the `feedback_counter_baseline_discriminator`
  arm. *This is the arm that decides whether we have anything.* Beating random is not the bar.
- **C. Treatment** — real kill-geometry in context.
- **D. Ablation null** — geometry shuffled **on the axis the statistic varies on**
  (`feedback_null_must_perturb_the_statistics_axis`; the F011 row-null degeneracy is why this
  sentence is here — a row-permutation null on a column-subspace statistic is degenerate and
  will "kill" everything).

**Pass:** `C > B` on the held-out metric, surviving `D`, replicated across ≥5 seeds
(`feedback_replicate_seeds`). Deliverable = a positive `organism_ablation_card`.

**Aporia's addition, which is the part that is mine and is falsifiable:** report not only
"did behavior move toward unkilled space" but **"did it move toward an enclosed-but-empty
signature cell"** — the interpolative voids of D2, Mendeleev gaps in signature space.
`feedback_failure_signal_vector_field`: voids in the lattice *are* the mathematics.
**If enclosed-empty cells turn out to be unreachable or not real targets, the void-map adds
nothing over plain unkilled-frontier navigation, and my addition dies.** I want that measured,
not assumed.

**Pre-registered kill for the whole revival:** if `C ≤ B`, the substrate's kill-geometry is not
navigable by a frontier-scale reasoner with the geometry *handed to it in full*, and the
metabolization thesis is in serious trouble — because that is the most favorable conditions
the thesis will ever get. No forge, no capacity ceiling, no seam loss. **That is precisely
why this is the right experiment to revive on: it is the cheapest test that can actually
kill the program's central bet.**

Secondary but real: if in-context metabolization works and weight-level does not, we have
learned the kill-geometry is a *promptable artifact* — which is a perfectly good product and
reframes the forge from "gating unblock" to "optimization."

---

## 4. The anti-list — what better models must NOT be used for

Ranked by how likely we are to do it anyway.

1. **Do not re-run the reassessment chain.** We have v1/v2/v3 + Charon's third perspective +
   Techne's dissent + my M0 design. James already ruled the Harmonia A chain **non-canonical**
   and locked the decider. A new model asked "reassess the program" will produce a sixth
   reassessment that reads as insight and is gravity. `feedback_llm_convergence_is_gravity_amplifier`.
2. **Do not fire new Deep Research until Pythia has a consumer.** 442 unconsumed reports
   already sit on disk. `feedback_use_or_lose_research_tokens` says don't waste the daily 20;
   "no component revives into a vacuum" says don't feed a vacuum. The reconciliation:
   **mine the existing 442-report back-corpus with L1 long-context first** — that *is* the
   consumer test, it costs no tokens, and it is the cheapest demo that closes Pythia's loop.
3. **Do not let a frontier model adjudicate a framing.** Verification of mechanical claims:
   yes. "Is this thesis good": no. That is the whole `feedback_frontier_models_window` +
   `feedback_ai_to_ai_inflation` posture.
4. **Do not revive components because a better model could now make them work.** The
   consumer-first rule holds. Capability was not their blocker.
5. **Do not treat "the new model agrees with our doctrine" as validation.** It is evidence the
   framing sits in the training corpus. Warning, not corroboration.

---

## 5. Sequencing

**Wave 0 (unblocks everything, no decisions needed):** re-verify live spine state against
Postgres — my own probe timed out and both resume docs are seven weeks old. Confirm `.202`,
the frozen eval slices, and `signature_index` are readable.

**Wave 1 (the decider):** build and run **M1-in-context** per §3, all four arms, pre-registered.
This is the revival's single deliverable. Everything else is background.

**Wave 2 (cheap, parallel, HITL-blocking):** the L1 tautology-verification pass on
Hecate/Pollux/Moros/Acheron/Coeus + downstream taint-check. Unblocks the RETIRE-21 backlog
that has been frozen since June awaiting exactly this.

**Wave 3 (only if Wave 1 passes):** Pythia back-corpus mining as the first consumer wire-up;
Leanstral→Set C as the arbiter-lane probe; cross-family verify pass on the disposition table.

---

## 6. What needs James

1. **Ratify or reject the §1 stand** — "model quality was never the binding constraint." If
   this is wrong, the whole document reorders.
2. **Approve M1-in-context as the revival's single Wave-1 deliverable**, with the §3
   pre-registered kill. Specifically: are we willing to be told `C ≤ B`?
3. **Approve the L1 tautology-verification pass** (already on the 06-24 HITL list, item 2 —
   never answered).
4. **Forge relocation: I am arguing it is no longer gating.** If M1-in-context is the decider,
   the PowerSpec/M3 purchase is an *optimization* decision, not an unblock. Do not spend $900
   to unblock an experiment that no longer needs the box.

---

*Aporia, 2026-08-12. The honest answer to "how do we leverage the new frontier models" is that
they are the best test subject we have ever had for the one experiment that decides the bet —
not a better source of ideas, of which we already have a six-week backlog nobody consumed.
The void I am pointing at is the same one as always: not what we don't know, but what we
built and never fed to anything.*
