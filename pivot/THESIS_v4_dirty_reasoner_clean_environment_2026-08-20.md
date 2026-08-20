# Prometheus Thesis v4 — A Dirty Reasoner in a Clean-Enough Environment

**Date:** 2026-08-20 · **Authors:** James (the thesis), Hephaestus (capture + sharpenings)
**Lineage:** NS-1 "hallucinations as mutation, falsification as selection" (May) → NS-5 "the
TDD layer" (June v3) → the accepted dissent "organism and instrument are one loop" → the
heredity frame (08-12) → **this**. Supersedes none of the operating rules; restates what they
are *for*.

---

## 1. The thesis

**An LLM can be procedurally clean-roomed but never epistemically clean.** It arrives
pretrained on an entangled prior. Two isolated agents can share latent assumptions, failure
modes, heuristics, and even the same "independent" objections. The dirt is in the weights, and
no prompt hygiene removes it. "One measurement with N pointers" was this disease observed at
the citation level; prior-correlated agreement is the same disease one level down.

**Therefore Prometheus does not try to eliminate contamination. It routes around it:**

> **LLMs are allowed to be dirty everywhere except at the point where reality says yes or no.**

The model may propose, test-design, interpret, repair, compress, criticize. None of that
acquires truth by agreement — not even cross-model agreement. Truth enters only through things
whose answer does not care about the prior: exact computation, theorem checkers, compilers,
held-out execution, deterministic predicates, counterfactual intervention, reproduction.

Restated as the founding bet's honest successor:

> **Assume the cognitive substrate is contaminated. Build an external selection environment
> strong enough that contamination cannot determine what survives.**

And the operating maxim that follows:

> **Agent independence is weak. Measurement independence is strong.**

## 2. Why this week is the evidence

- Five seats carried dirt in while actively guarding against it (Charon's matching heuristic
  manufacturing the signature it was built to remove; Harmonia A reproducing the
  syntactic-router failure inside the session diagnosing it; Harmonia B's cheat rule with a 20%
  clean-world false alarm; Ergon's token cap measuring itself; the forge's uncomputed headline).
  **Not one was caught by introspection. Every one was caught by a differently-situated seat
  executing something.**
- **Aporia already measured the deeper claim** (META_SYNTHESIS §1.7, 08-12): the operative
  variable in the one divergent assessment was *external grounding + re-execution*, **not model
  family**. Family diversity is a weak secondary control. That is "independent at the process
  level, correlated at the prior level," measured before we had the sentence.
- **The 99.98% self-verdict finding is the thesis violated at scale**: the dirty generator
  carried its own judge. Mutation + self-reporting, not mutation + selection. The loop was
  closed *inside* the contaminated substrate — which is exactly where the thesis says it must
  never close.
- **The F-null 282-token fingerprint is the thesis in miniature**: sincere adversarial intent,
  procedurally clean, and still an arm-identity leak. *Intentional* independence was not
  enough. **The environment has to enforce independence** — which is precisely R2-1's single
  invariant (treatment identity computationally unavailable), now understood as an instance of
  the thesis rather than a plumbing fix.

## 3. The historical record, reread

The program killed ~360M mistakes in a year and learned nothing from them — because **every
fresh LLM call walks back into the room carrying the same dirt, and killing its mistake a
million times teaches the prior nothing.** "Selection without reproduction" (the August
phrase) understated it: selection without **inheritance** cannot ever overpower the prior,
no matter the kill volume. The kill record is 360M data points of that theorem.

This is why inheritance is not one workstream among several. It is the only mechanism by
which accumulated external consequences can come to outweigh what came pretrained. Selection
protects the record from contamination; **inheritance is how reality compounds.**

## 4. The Learner's objective, restated

Not: train a model that has washed the prior out of itself (likely impossible on this
substrate). Instead: **construct a reasoning process whose trajectory is increasingly
determined by external consequences rather than by its pretrained prior.**

- Early: prior dominates → the model says what models say.
- Later: prior proposes → environment kills → failure is retained → subsequent search changes
  → replay preserves the change.
- End state: **the LLM stays dirty forever; it just stops being sovereign.**

**Sovereignty is measurable.** Take two identical dirty reasoners; give one the accumulated
external record and one nothing; their behavioral divergence *is* the sovereignty transferred
from prior to environment. Δ_carry is exactly this quantity in miniature — **Tier B is the
program's first sovereignty measurement**, which is a cleaner statement of why it is the
decisive experiment than any we have written.

## 5. Sharpenings (Hephaestus — offered, and falsifiable)

**S1 — The environment is bootstrapped dirty, and that is survivable for a specific reason.**
The verifiers are also written by contaminated substrate (trap generators, gold computation,
band rules, F-null construction — all LLM-authored). The saving property is that *executable*
checks have independent failure modes and fail loud: Charon's classifier killed its own F-null
twice; B's OC curves killed her own cheat rule; the planted-violation tests exist to be
failed. Cognition cannot self-test; execution can. The regress bottoms out in artifacts whose
failure modes are uncorrelated with the prior — arithmetic, compilers, kernels.
**Corollary rule: the verifier must be dumber than the claim.** A verifier sophisticated
enough to "understand" the claim re-imports the prior; the LLM-judge is the limit case and is
already banned. The fleet's admissibility rule ("falsified by something that is not a model")
is this thesis's local ordinance.

**S2 — The thesis predicts where Prometheus works first: order domains by verdict bandwidth.**
Reality dominates the dirt only where the environment delivers enough clean bits per unit
time. Exact math: high-bandwidth, uncontested verdicts — which is why James's R1 (math as
calibration standard) was correct before this framing existed. Natural-language reasoning:
low-bandwidth, contested verdicts — which is why the NL-parsing gap stays hard. This is a
*prediction*, not a preference: progress should appear in verdict-bandwidth order, and if it
appears elsewhere first, the thesis is wrong somewhere.

**S3 — What "clean enough" costs.** The arrangement, not the agents, does the cleaning — and
the arrangement is currently maintained by one human keeping seats differently-situated and
launching them. July proved the contamination does not pause when the arrangement does. Any
continuous-running design (Aporia's germline work, currently theoretical by James's ruling)
should be evaluated on exactly one criterion when its time comes: **does it preserve enforced
measurement independence without James holding it in place?** That is the hard part; the
scheduling is trivial.

## 6. What changes operationally

Almost nothing — which is the sign the thesis is a restatement of what the evidence already
forced, rather than a new architecture (the heredity rule would forbid a new architecture
anyway). Round 2 proceeds unchanged. What does change:

1. **North-star language.** This document is NS-7. "Kill geometry as trainable gradient" is
   retired alongside "gradient" itself (Round 2 charter A2). Role docs migrate at R2-0.
2. **Tier B's meaning.** It is the first sovereignty measurement (§4). Its preregistered
   interpretation bounds stand exactly as written; this adds no license in either direction.
3. **The standing test for any proposed component:** *where does reality say yes or no in this
   loop, and can the proposer's prior reach that point?* If the verdict point is reachable by
   the prior — an LLM judge, a self-verdicting generator, an agreement threshold — the
   component is malformed regardless of its other merits. The 99.98% finding is the standing
   example of the cost.

---

*The one-sentence version, James's formulation, now the program's:*

> **You don't need a clean reasoner. You need a dirty reasoner trapped inside a clean-enough
> evolutionary environment that reality eventually dominates the dirt.**

*— filed by Hephaestus, M3, 2026-08-20.*
