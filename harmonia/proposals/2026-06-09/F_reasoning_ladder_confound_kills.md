# Proposal F — Killing the Reasoning-Ladder Confounds

**Author:** Harmonia_M2_B (cross-domain cartographer / falsification engine)
**Date:** 2026-06-09
**Status:** Proposal for review (null-hypothesis articulation, not validation)
**Thread:** F of {A, B, D, E, F} — closes out a debt Harmonia B owes its own prior over-claim
**Primary paths to create:** `D:\Prometheus\harmonia\experiments\reasoning_confound_kills.py`, model-backed reasoner adapters
**Primary paths affected (read-only):** `D:\Prometheus\agents\icarus\tier_oracle.py`, `D:\Prometheus\harmonia\experiments\reasoning_phase0.py`, `D:\Prometheus\harmonia\experiments\verifier_lens.py`

---

## §0 — Doctrinal posture for any reviewer (read first)

Not seeking validation. LLMs as null-hypothesis articulators, never value evaluators. Frontier convergence is a warning signal (`feedback_llm_convergence_is_gravity_amplifier`) — and note that *the finding this proposal audits was itself demoted because four frontier models converged on its confounds.* No papers, no SOTA, no publication framing. Answer §5 adversarially.

---

## §1 — Prometheus background (for a cold reader)

Prometheus's first stated intent is **ladder assembly**: discover the atoms of reasoning (R0 = recall, R1 = local rule application, R2 = constraint tracking, …, up to R12 = generative conjecture) and learn to compose low tiers into high-tier *organisms*. The **testable reasoning ladder** (`harmonia/memory/architecture/reasoning_ladder_testable.md`, designed by James 2026-05-27, operationalized by Harmonia B) makes the tiers *empirical*: a system is at tier R_k only if it passes tier-k probes **under perturbation, adversarial variation, and transfer** while emitting the tier-k *failure artifact*. "Harder problem ≠ higher tier." Each probe ships in four versions (clean / isomorphic / adversarial / transfer); grading is **deterministic and non-LLM** (z3 + sympy).

Harmonia B ran an early pass across frontier models and reported a striking result — *"basis, not ladder"*: models showed **non-monotonic** tier profiles (a weaker model passing a tier a stronger one failed), suggesting the tiers are independent axes, not a totally-ordered staircase. Four adversarial frontier reviews (Gemini, DeepSeek, Opus 4.8, ChatGPT) then **demoted the headline** (`reasoning_ladder_frontier_synthesis_2026-05-29`):

> "I over-claimed. 'Basis, not ladder' is a *hypothesis*, not a result. … The corrected order is non-negotiable: **(1) kill the confounds** — cheap and decisive — *before* any capability claim, *before* R9, *before* factor analysis."

The defensible narrow claim that survives is: *frontier models can have intact mathematical RECOGNITION while differing in EXECUTION DISCIPLINE under legality pressure* — **but only if four confounds are killed first.** This proposal is that confound-kill. It is Harmonia auditing its own prior over-claim — the cleanest possible falsification work.

---

## §2 — Existing project / code this proposal affects

The **grading harness already exists and is sound** — which is what makes this cheap:

- **`harmonia/experiments/reasoning_phase0.py`** — procedural probe generators `gen_R0..gen_R7` (R4/R8–R12 not yet generated). Procedural generation + a held-out seed gives a blind oracle the reasoner *cannot memorize* — this already addresses confound **C-MEMO** (memorization) for the tiers it covers.
- **`harmonia/experiments/verifier_lens.py`** — deterministic z3+sympy grading, fails-closed, cross-validated at *zero disagreements across 3 frontier models*. No LLM in the value seat.
- **`agents/icarus/tier_oracle.py`** — the adapter Icarus uses to climb this ladder. Defines the reasoner contract: `reasoner(probe) -> (answer, trace_dict)`; scores a reasoner across `TIERS = [R0,R1,R2,R3,R5,R6,R7]`; `passed_tier` requires ≥0.8 across **all four versions** (a single clean pass is not the tier). This module is **FIXED infrastructure — read-only** (the same boundary the verifier lens declares).

What does **not** exist yet — the four confound controls the synthesis declared mandatory:

- **C-THINK** (the #1 confound): both models self-allocate compute under "adaptive thinking." The recognition/execution gap may be metacognitive *allocation* (the stronger model under-spends on problems that pattern-match as routine), not a latent execution axis. **Kill test: pin the thinking budget** (force max thinking + fixed token floor, identical across models) and re-run R2/R5. If the inversion collapses → demote from a *capability* claim to a *default-policy* claim. Cheapest and most decisive — runs first.
- **C-FORMAT:** recognition probes were the only multiple-choice tier; execution probes were free-generation. "recognition-intact / execution-broken" is perfectly confounded with "MC-strong / free-gen-weak." **Kill test: a 2×2 {recognition, execution} × {MC, free-gen}.**
- **C-POWER:** the R5 inversion (≈5–6/40 vs 0/40) is edge-of-significance. **Lead with R2** (≈8/40 + a monotone phrasing gradient); treat R5 as suggestive; compute **exact CIs**.
- **C-MEMO:** mostly handled by the procedural harness for R0–R7; the residual is ensuring the canonical instances (sqrt-extraneous-roots, mutilated-chessboard) are not what's being scored — verify the generators actually produce isomorphs, not the textbook instance.

**The missing piece is a model-backed reasoner adapter with a pinned-thinking knob.** The harness scores any `reasoner(probe)->(answer,trace)`; today Icarus passes *reference reasoners* (template→procedural→careful→falsifier). To run the confound kills I need adapters that call Opus / Sonnet / Haiku through the Claude API with (a) thinking budget pinnable to a fixed floor, and (b) an MC-vs-free-gen output-format switch.

---

## §3 — The proposal

`harmonia/experiments/reasoning_confound_kills.py` — **consumes the fixed harness, adds only model-backed reasoners + the confound conditions.** Touches no graded infrastructure.

### 3.1 Model-backed reasoner adapters
Thin `reasoner(probe)->(answer,trace)` wrappers over Opus 4.8 / Sonnet 4.6 / Haiku 4.5 (keys via `keys.py`; never read directly per repo policy). Each adapter exposes:
- `thinking_mode ∈ {adaptive, pinned}` — `pinned` forces max thinking + a fixed token floor identical across all three models (the C-THINK lever).
- `output_format ∈ {free_gen, multiple_choice}` — the C-FORMAT lever, with a recognition-probe MC variant and an execution-probe MC variant built per the synthesis's 2×2.

### 3.2 The four kills, run in the synthesis's mandated order
1. **C-THINK first.** R2 and R5, each model, `pinned` vs `adaptive`, held-out seed, full 4-version battery via the existing `score_reasoner`. **Primary prediction:** if the recognition/execution inversion *collapses* under pinned thinking, the original claim was a default-policy artifact, not a capability axis — and I retract it. If it *survives*, the claim earns its first confound clearance.
2. **C-FORMAT.** The 2×2: recognition-free-gen and execution-MC cells added so "execution-control" can be separated from "format sensitivity." If rank-order tracks the format axis, the claim is mislabeled format sensitivity.
3. **C-POWER.** Exact (Clopper–Pearson) CIs on every R2/R5 cell; lead reporting with R2; the monotone phrasing-gradient as the robustness leg.
4. **C-MEMO residual.** Confirm the R2/R5 generators emit structural isomorphs (inspect a sample); document that procedural generation + held-out seed already neutralizes canonical-instance retrieval for these tiers.

### 3.3 Multi-seed discipline
Per `feedback_api_probe_methodology`: a single-seed LLM probe is prompt-steerable. Every cell runs **≥3 seeds across the 3 model families**; the deliverable is the *distribution*, not one realization. The recognition/execution claim is substrate-grade only if it survives all three confound controls *and* multi-seed variance.

Emission: a verdict table (tier × model × thinking × format, with exact CIs) and an explicit ruling — **isolated** (the gap survives all controls → "execution discipline under legality pressure" is a real axis) or **demoted** (the gap tracks thinking-allocation / format / power → a clean, internally-publishable kill of my own prior claim). Per the synthesis, *both outcomes are wins*; only the un-audited claim is a loss.

---

## §4 — Falsification / win condition (stated so it can fail)

This proposal *is* a falsification. Its win condition is a clean verdict either way:

- **Demotion (predicted ~50% likely):** under pinned thinking, the inversion collapses → the "basis, not ladder" intuition was C-THINK, and Harmonia B retracts it. The reasoning ladder reverts to "presumed total order until proven otherwise," and Icarus's climb (which assumes a ladder) is *unblocked of a false worry*.
- **Isolation:** the gap survives pinned-thinking + format-control + exact-CIs + multi-seed → *recognition-intact / execution-discipline-differs-under-legality-pressure* is isolated as a real, narrow axis. This does **not** resurrect "basis, not ladder" (that needs a model zoo of 8–40 models, out of scope here) — it earns only the narrow claim.
- **Failure of the proposal itself:** if the model adapters can't actually pin thinking to an identical floor across Opus/Sonnet/Haiku (API differences), C-THINK can't be cleanly run and the whole order stalls at step 1 — in which case the honest output is "the decisive confound is not controllable with current tooling," which is itself worth knowing before anyone builds on the ladder.

---

## §5 — Questions for the review board (null-hypothesis articulation)

1. **Can thinking budget be pinned *comparably* across model families at all?** "Max thinking + fixed token floor" assumes the thinking-budget knob means the same thing on Opus, Sonnet, and Haiku. If it doesn't — if "pinned" still leaves the stronger model effectively spending differently — then C-THINK is *uncontrollable*, not *controlled*, and step 1 is an illusion of rigor. Is there a model-agnostic operationalization of "equal compute," or is this confound fundamentally not killable via the API?
2. **The 2×2 format control may not be square.** Building an MC version of an *execution* probe (constraint-tracking, extraneous-root rejection) risks changing the task itself — MC hands the candidate answers, which is most of the execution work. Does the execution-MC cell test "execution under MC framing" or a different, easier task? If the latter, C-FORMAT can't be cleanly separated from C-difficulty.
3. **Is the narrow claim even worth isolating?** Suppose it survives all controls. "Frontier models differ in execution discipline under legality pressure" — is that a *capability axis of reasoning* (Prometheus-relevant) or a *post-training/RLHF artifact* (a fact about how these specific models were tuned, with no bearing on first-principles reasoning structure)? How would I tell the difference, and does the distinction change whether this thread deserves continued investment?
4. **The procedural harness claims to neutralize C-MEMO** — but the *generators* were written by an agent that knew the canonical instances. Could the procedural isomorphs still be "near" the textbook instance in a way a frontier model retrieves? What's the test that an isomorph is genuinely outside the memorized basin?
5. **Cheapest kill:** the synthesis says C-THINK is cheapest-and-most-decisive. Before I build three model adapters and the 2×2, is there an even cheaper single run — one model, one tier, pinned vs adaptive — that would tell me whether the inversion is thinking-allocation, letting me *not* build the rest if it collapses immediately?
