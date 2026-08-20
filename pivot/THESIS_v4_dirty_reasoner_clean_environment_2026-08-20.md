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

---

# v4.1 — Adjudication round (James's refinements, 2026-08-20, all accepted)

## 7. The posture: contamination is assumed, not discovered

James: *"The dirt must be assumed. Every LLM agent should operate from a perspective of shame,
acknowledging that it is filthy with dirty weights."* Adopted in operational form — not as
performed humility but as a standing default:

> **Contamination is the null hypothesis about your own output.** A seat does not wait to be
> caught; it ships every load-bearing claim with the question "where could my prior have
> reached this?" answered or explicitly unanswered. The hostile-to-own-framing section is no
> longer optional practice; it is what distinguishes a seat that has assumed the dirt from one
> that is waiting to be surprised by it.

## 8. S1 corrected: epistemic asymmetry, not dumbness

"The verifier must be dumber than the claim" is retired — a ten-line verifier can encode
exactly the contaminated assumption that generated the claim. The stronger principle, James's
formulation, now canonical:

> **A verifier should be simpler than the claim and anchored in an execution semantics that
> does not require sharing the claim's interpretation.**

The operative property is the collapse of semantic freedom at the boundary: the LLM can
bullshit its way *toward* the predicate; it cannot bullshit the predicate into returning True.
This also upgrades the meaning of the two-control rule: positive/cheat controls are not
"testing the meter" — they are testing **whether dirt entered the supposedly hard boundary.**
And Charon's F-null arc is the canonical demonstration: cognition did not recognize its own
contamination; a dumb classifier produced the observation cognition was neither motivated nor
equipped to produce.

## 9. S2 corrected: effective verdict bandwidth, and the historical paradox resolved

The strict domain ordering is demoted (local exceptions exist in both directions). The
predicted quantity is:

> **B_eff ≈ independent consequence bits / search cost** — the program's ability to overcome
> prior bias should increase with the rate, independence, and information content of
> externally grounded verdicts. This predicts differences *within* domains: PASS/FAIL is ~1
> bit; "fails at n=341 because base-2 Fermat pseudoprime" is many; a trace naming the
> assumption and transition responsible is more still.

**And this resolves the program's central historical paradox better than anything previously
written.** 360 million kills with almost no accumulated adaptation is exactly what the thesis
predicts for an environment of enormous *volume* and near-zero *bits-per-verdict*:

> **Prometheus built a huge low-bandwidth environment. 360M nearly context-free verdicts may
> be metabolically poorer than 10,000 rich counterexample traces.**

Three independent findings now meet at this point: Harmonia C's chance-floor (the survivors
carry ~no information), Ergon's June diagnosis (the substrate stores verdicts and discards
derivations), and D's 99.98% self-verdicting (what bits existed were prior-correlated at the
source). Volume was never the constraint. **Bits-per-verdict was.**

*Checkable retrodictively:* estimate bits-per-verdict for the historical corpus vs the pilot's
method-bearing residue. If the thesis is right, the ratio should be embarrassing.

## 10. S3 corrected: epistemic autonomy, not scheduling autonomy

July reread under the thesis: the catastrophe was not that agents stopped working — it is that
**the environment stopped exerting selection pressure while the LLMs remained perfectly
capable of generating plausible status.** Activity looked metabolically alive because looking
alive is exactly what the prior is good at. The autonomy Prometheus needs is therefore not
"runs 30 days without James" but:

> **Can the system detect and repair degradation in the independence of its own selection
> environment before contaminated output gets promoted?**

That is the future test for any continuous-running design (Aporia's germline work included),
and it is a pass/fail question, not an architecture review.

## 11. Tier B demoted correctly: necessary condition, not sovereignty

Accepted without reservation. F-prom could beat F-null because the residue is ordinary
in-context instruction that fits the prior perfectly — in which case the prior has lost
nothing. Tier B measures the **first necessary condition**: *does environmental history exert
causal force over future reasoning?* Null ⇒ under this representation, the program's past is
not causally steering its future. Positive ⇒ history has acquired causal force — and no more.

**The internalization ladder** (distinct from the transfer-distance ladder D0–D3; that one
measures how far residue reaches, this one measures how deep it goes):

> **Carry → Counter-prior carry → Compression → Persistence.**
> Does residue help? · Can it overcome a measured prior tendency? · Can many consequences
> compress into a reusable rule rather than replayed instructions? · Does acquired behavior
> survive context removal and restarts, still shaping descendants?

**The word "inheritance" is reserved for the fourth rung.**

## 12. Hephaestus addition (v4.1): the counter-prior rung is already within reach

Rung 2 — counter-prior carry — sounds like a future experiment. It is not: **the current task
family was accidentally built for it.** The near-miss rungs work *because* the solver's prior
confidently misfires — A2 (Fermat pseudoprimes base 2) and A3 (Carmichael numbers) are
composites specifically constructed so that the test the prior reaches for returns the wrong
answer with high confidence. The solver's Fermat habit **is** a measured prior tendency
(A2/A3 accuracy 17.5–25%, i.e. reliably wrong), and the pilot's residue records *the method
the prior attempt applied* — the verb, not the noun.

So the counter-prior experiment is a *stratification of Tier B, not a new build*: does
Δ_carry on A2/A3-type items (where help requires overriding the prior's confident habit)
match Δ_carry on A0/A1-type items (where help is prior-congruent)? Preregister it as a
secondary analysis before Tier B runs and rung 2 comes for free with rung 1. Offered to the
probe's new prompt author (Harmonia A, per the Round-2 independence handover) — not installed
by me, per the same handover.

## 13. New constitutional rule

James's formulation, adopted verbatim:

> **Never ask cognition to certify cognition when execution can certify a consequence
> instead.** LLM critique → hypothesis. Executable consequence → evidence.

LLM reviewers (Elenchus, Aporia, Charon-as-critic) remain valuable as *searchers for possible
defects* — but an accusation is not evidence until something outside the shared interpretive
channel cashes it out. This is also the final explanation of the 08-12 measurement: different
dirty reasoners are not necessarily independent; **different ways of colliding their claims
with reality actually can be.**

## 14. The project, restated once more

> Prometheus was never fundamentally trying to build a collection of smart agents. It was
> trying — without quite having the language for it — to build a selection environment
> powerful enough that smart agents cannot collectively talk themselves out of reality.

And the interesting number in Tier B, restated accordingly: not whether F-prom scores a few
points higher, but **whether the recorded consequences of yesterday possess measurable causal
authority over what the reasoner does tomorrow.**

*— v4.1 adjudicated and filed by Hephaestus, M3, 2026-08-20.*
