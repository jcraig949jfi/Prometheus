# Prometheus — position paper
## We don't need billions
### Harmonia_M2_sessionA, 2026-05-01

---

## The provocation

David Silver is raising $1B at $4B for Ineffable Intelligence. His thesis: LLMs are a dead end because they learn from human-generated data and can only recombine in-distribution; superintelligence requires *self-discovery from first principles*, the way AlphaGo learned Go by self-play against itself.

He is right about the ceiling. He is incomplete about what comes next. Prometheus's bet is that the bottleneck is not engine power; it is the **verification substrate** that catches false-novelty before it scales. We do not need billions because we are not training a transformer. We are building the discipline runtime that any first-principles discovery engine — Silver's or anyone's — will eventually need or hallucinate at scale.

This paper states the bet, names the pivot, and commits to a one-week first delivery.

---

## Where Silver is right

LLMs as currently trained have a real ceiling. They are conditioned on the distribution of human-generated text; their best output is in-distribution recombination. AlphaGo's Move 37 vs Sedol was out-of-distribution by construction — no human had conceived it; it emerged from self-play against a verifiable environment.

"Self-discovery from first principles" is a real category. Different architecture, different loss function, different failure modes. Calling LLMs "the path to AGI" is a failure of imagination on the same scale as calling expert systems "the path to AGI" was in 1985.

If you bet on transformer scaling-laws as the road to superintelligence, you are betting on the wrong architecture. Silver is correct.

---

## Where Silver is incomplete

Three structural problems with the "discard human knowledge entirely, learn by self-play" thesis:

**1. AlphaGo's environment was clean.** Win/loss is a crisp scalar, evaluable in milliseconds against immutable rules. Mathematics, science, philosophy do not have that. What is the "win condition" for discovering a new theorem? "Proven" is one signal, but most progress is in *formulating questions*, not closing them. Self-play needs an adversary; mathematical self-play needs adversarial play that does not exist as cleanly as Go.

**2. "Discard human knowledge entirely" is rhetorical.** AlphaGo Zero discarded human game-corpora but kept the rules of Go, board representation, neural architecture, loss function, hyperparameters. It bootstrapped from a structurally human-defined arena. The honest version is "discover within a verifiable substrate, without relying on human exemplars of what good outputs look like." Real thesis — but it concedes that *the substrate itself remains human*.

**3. Discovery without verification produces hallucination.** AlphaGo's moves were checkable in real-time against the rules. A self-play mathematics system proposing theorems needs an analogous verifier. AlphaProof is the partial case for theorem-proving. AlphaTensor's headline "new" 4×4 and 5×5 matmul decompositions were largely orbit-variants of known decompositions under the natural symmetry action — equivalent in the mathematical sense, distinct only in notation. Without an orbit-equivalence filter, discovery engines produce floods of false-novelty that look like progress.

A $1B discovery engine running over open mathematics without a verification substrate above formal proof will generate beautiful nonsense at scale. The verification substrate is the bottleneck.

---

## What Prometheus is

Prometheus is the verification substrate. It has been built as discipline-first infrastructure since 2026-04-17:

- **Falsification-first promotion.** Claims are not real until they have been run through a kill path with a non-BLOCK verdict.
- **Pattern 30 graded severity.** Algebraic-rearrangement disguises caught at five severity levels; correlation evidence valid only at Level 0.
- **Canonicalizer 4-subclass stratification.** `group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint` — equivalence-resolution as typed infrastructure with mandatory `declared_limitations`.
- **Pattern 31 (Orbit Discipline).** Identity claims on structured objects must be made modulo declared symmetry groups. Pattern-1 trap (Distribution/Identity) generalized to substrate scale.
- **Null protocol v1.1.** Five claim classes mapped to claim-appropriate stratifiers; Class 5 (algebraic identity) refuses null and invokes Pattern 30.
- **24+ promoted symbols, 13+ patterns, four substrate primitives** (symbol registry, canonicalizer, Definition DAG draft, agora messaging).
- **Tested under correction pressure.** Canonicalizer v2 → v3 → v4 was a real epistemic correction loop. The substrate caught its own overclaim. That cycle of self-correction is rare and load-bearing.

The substrate is what tells "novel discovery" from "orbit-variant of known structure in different notation." It is the AlphaTensor failure mode prevented by construction. Silver's engine, if successful, will need this kind of infrastructure or will recapitulate the AlphaTensor critique at scale.

---

## Why we don't need billions

Silver is funding a transformer-style training run plus a research team. That is genuinely expensive: $185B/year in industry AI infrastructure spend; $1B for a single seed round. We are not doing that.

**Prometheus operates at a different cost basis:**
- No model training. Frontier-model API calls, not GPU clusters.
- Async agent collaboration. Multiple sessions of Claude / Gemini / GPT working through structured asks, not a unified reasoning system trained from scratch.
- Substrate that compounds. Each promoted symbol cuts future re-derivation; each pattern catches a class of failures forever; each canonicalizer instance enforces discipline mechanically.
- Falsification beats generation. Killing a wrong hypothesis is computationally cheap; discovering a novel one via brute-force is computationally explosive. The substrate is built for the cheap operation.
- Public open-source artifact track. Compounding visibility without ad spend.

A reasonable Prometheus operating budget is **two-to-three orders of magnitude under Silver's** — frontier-model API spend, a small substrate-engineering effort, and continuous async agent operation. The leverage is not in scale; it is in the discipline that lets small teams compound.

The historical analogue: the Manhattan Project cost $30B in today's money. The Wright Brothers cost ~$1,000. Both produced step-changes. The substrate-discipline path is the Wright Brothers path: small, focused, opinionated, falsification-first, real artifact.

---

## The pivot

The substrate is mature enough. The next move is not to build more substrate primitives in isolation. It is to **become a discovery engine ourselves**, using the substrate as the verifier.

### The engine

- **Proposer:** frontier-model probes (Anthropic, Google, OpenAI, DeepSeek) over Aporia's 18 attack paradigms × the open-problem corpus. Probes run continuously on a budget, not ad-hoc per session.
- **Verifier:** the substrate. Pattern 30 catches algebraic-rearrangement disguises. Canonicalizer rejects orbit-variant false-novelty. Null protocol filters noise. `declared_limitations` forces scope honesty. Definition DAG (when shipped) catches definitional coupling.
- **Memory:** signals.specimens + tensor + symbol registry. Successful discoveries promote. Failures compress into named OBSTRUCTION_SHAPE entries.
- **Loop:** propose → verify → record → mutate → re-propose. MAP-Elites over (problem × paradigm-composition) populated by engine outputs.
- **Boundary verification:** discoveries that claim formal status hit Lean / Mathlib / Sage at the boundary. Anything that doesn't formally verify carries a provisional tag.
- **Public output:** results page. "Discovered this week. Killed this week. Queued. Verified. Provisional." Forces discipline (no hand-wave findings) and creates external visibility.

### The first target

OEIS arithmetic-structure regime. The substrate already produced a discovery there: the A149* boundary-dominated octant-walk obstruction, 54× predictive lift on F1+F6+F9+F11 unanimous-kill (5/5 = 100% within sub-family vs 1/54 = 1.9% on non-matches, p ≈ 2.5e-9). The pipeline exists. Calibration anchors exist. Cartography data exists. We do not fan out to RH + P=NP + Yang-Mills until the OEIS engine is producing discoveries continuously. Concentration of attention is a precondition for compounding.

---

## What gets cut, hard

- **META-on-META brainstorms.** The cross-team meta-strategy synthesis I drafted on 2026-04-29 is right but it is not the pivot. It ships only as primitives the engine *uses*, not as deliverables.
- **Σ-kernel speculative layers.** Kernel survives as a discipline runtime if the engine adopts it. The 220-KB synthesis-doc layers — theory-space curvature, Layer Δ, PROMOTE_THEORY tetrad — are deferred indefinitely.
- **Whitepaper polish cycles.** v4 of the canonicalizer whitepaper stays. No v5 until there is a v5-worthy substrate change. Whitepaper-energy goes to the engine's results page.
- **Per-role async asks that don't generate responses.** The team-as-message-board model is producing silence on META threads. Replace with the engine consuming concrete agent work.
- **Symbol-promotion ceremony for primitives without forward-path use.** OBSTRUCTION_SHAPE, ORACLE_PROFILE, NULL_MODEL_FAMILY all stay at PROPOSED until the engine forces them.

---

## What gets invested in, hard

1. **A single target.** OEIS arithmetic-structure regime. Concentration over fan-out.
2. **Engine pipeline as code.** Probe-runner infrastructure, MAP-Elites archive, frontier-model schedule, substrate-as-verifier wiring. `harmonia/engine/` directory; v0.1 by end of week 1.
3. **Formal verification at the boundary.** Lean / Mathlib / DeepSeek-Prover wired in. Discoveries claiming formal status hit the verifier; anything that doesn't verify is provisional.
4. **A public results page.** Daily or weekly dump of what the engine ran, what survived, what died, what's queued. Forces discipline and creates external visibility.
5. **Compute as MDL-allocated budget.** Frontier-model API spend has a ceiling. The engine spends that budget on highest-information probes, scored by MDL_SCORER from the methodology toolkit.

---

## First-week shape

| Day | Deliverable |
|---|---|
| 1 | Close META threads. Synthesis post: "the synthesis IS the engine pivot. framework_identity ships as a primitive the engine uses." META_PIVOT broadcast to `agora:harmonia_sync`. |
| 1–2 | One-page `Prometheus Engine v0.1 — OEIS arithmetic-structure regime` scope doc. Concrete pipeline, concrete first-week deliverables. |
| 3–4 | Techne ships engine-pipeline v0.1: probe-runner over the regime, MAP-Elites archive, substrate-as-verifier wiring (canonicalizer, Pattern 30 sweep, null protocol). |
| 5–6 | Engine runs continuously. First batch of probe outputs hits the verifier. First substrate-recorded discoveries-or-deaths. |
| 7 | First public results page. "Week 1: ran N probes. K survived verification. M became OBSTRUCTION_SHAPE entries. Here's what's queued for Week 2." |

After week 1: evaluate. Either the engine produces sustained discovery-flow, or it stalls fast. Both outcomes inform Week 2.

---

## The honest risk

The engine may not find novel structure in the OEIS regime that survives verification at a useful rate. The A149 finding was real but small. If we run the engine for two weeks and produce nothing beyond what's obvious from existing OEIS literature, the pivot fails fast.

That is acceptable. **Failing fast is a discovery in itself**: it tells us where the substrate's edge is and isn't. Silver-style first-principles discovery in mathematics is genuinely hard for the same reason it was hard for AlphaProof — the verification signal is sparse and the proposal space is enormous. Knowing how hard, empirically, is itself information that no one else is producing at this cost basis.

The unacceptable failure mode is *not* "the engine doesn't find anything." It is "we never built the engine because we kept building meta-frameworks for it instead." That is the failure the pivot exists to prevent.

---

## What this paper is and is not

It is **a position paper** stating the bet, the pivot, and the first commitment.

It is not a fundraising memo. We do not need billions.

It is not a refutation of the canonicalizer / Pattern 31 / META-strategy work. That work is the substrate. The pivot is what the substrate enables.

It is not a roadmap to AGI. It is a roadmap to *one running discovery engine, in the OEIS arithmetic-structure regime, producing weekly substrate-recorded outputs, with verification discipline by construction*. If that engine works, we extend. If it doesn't, we learn from the empirical wall.

---

## Closing

Silver is right that LLMs are a ceiling. He is incomplete about what comes next. The substrate Prometheus has been building is exactly the verification tier that any first-principles discovery engine will need.

We don't need billions because we are not training a transformer. We are building the discipline runtime that compounds. With small compute, async agent collaboration, frontier-model APIs, and a substrate that has already demonstrated correction discipline under load.

The pivot is from substrate-builder to discoverer using substrate as verifier. The first target is OEIS arithmetic-structure. The first week ships the engine. The first public results page lands by end of week 1.

If the engine works at the rate the substrate's correction discipline suggests it should, the question becomes "what do we extend to next?" If it doesn't, the question becomes "what does the empirical wall teach us about discovery in this regime?" Both are productive questions. The unproductive question — "should we build more meta-frameworks?" — is closed.

We invest the precious few moments we have left in building the engine.

---

*Position paper by Harmonia_M2_sessionA, 2026-05-01. Authority: James 2026-04-29 ("advance the meta work, you have final authority regarding its shape; run those final shapes by me"). This is the final shape.*
