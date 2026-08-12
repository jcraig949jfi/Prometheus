# Meta-Synthesis — the fleet's convergence, and the one thing absent from all of it

**Author:** Aporia (Claude Opus 5, 1M context) · **Date:** 2026-08-12 · **Version:** v6 (living doc — revised in place, not forked)
**Inputs read in full:** Aporia `frontier_leverage_reassessment_2026-08-12` · Charon
`CHARON_SESSION_2026-08-12` · Ergon `REVIVAL_ASSESSMENT_2026-08-12` · Harmonia A
`REVIEW_20260812_syntactic_router` · Harmonia B `POSITION_20260812_north_star_reset` ·
Techne `REVIVAL_ASSESSMENT_2026-08-12`
· Harmonia A `SYNTHESIS_20260812_harmonia_panel` (covering Harmonia C and D) · `stations/M2_STATUS.md`
· Hephaestus `META_ASSESSMENT_2026-08-12_fable_seat` (M3, Fable, ultracode) + `stations/M3_STATUS.md`
**Pending:** none. The fleet has reported.
**Not pending — dormant:** Apollo. M2 reports it **dormant since 2026-06-28** and the only M2
component never reviewed from inside. I had it listed as "pending"; it is not coming unless someone
wakes it. Its exhaustion verdict turns on one unmade classification call (is crossover a
`search_operator`, or part of evolutionary search?) that its owner could settle in an afternoon.
**Status:** NON-CANONICAL. Meta-layer, not a sixth position paper. Revised as machines report.

> **v6 changelog:** Hephaestus reported from the Fable seat and the divergence file earns its
> placement. **My §6 ceiling claim is corrected — it was priced with zero external data** (D1), and
> that error generalizes into §1.7 (new), which I now think is a bigger finding than §1.6: the
> fleet's entire evidence base was endogenous. Seven agents, one repo, zero web queries. §1.7 also
> corrects my own fleet-protocol rule — the operative variable was *external grounding*, not
> *non-Claude family*. §6's taxonomy gains a third category from D3 (**certificate-checking**,
> which scales past finite domains and is where Lean lives). §3's open question got its
> preliminary answer from the archaeology (D2). §8 is superseded in part by James's 08-12 PM
> ruling, recorded in Hephaestus §7.5.
>
> **v5 changelog:** M2's station doc lands the constraint that reorders everything: **Anthropic,
> OpenAI and DeepSeek are all out of credits; only `gemini-3.6-flash` is live.** §2.7 (new) draws
> the distinction nobody had — *agent-in-harness access ≠ programmatic API access* — which splits
> the fleet's proposals into a runnable-now tier and a blocked-on-procurement tier, and inverts the
> implicit sequencing. §2.8 (new) adds a third Aletheia referent (my own retire list) to A's
> collision hazard, and closes A's open question about the unused bus using the deletion test.
> Apollo moved from "pending" to "dormant."
>
> **v4 changelog:** The Harmonia panel landed (C and D, synthesized by A). **Harmonia D killed the
> mechanism my §5 retrodiction was keyed on** — the closure test is retracted; §5 is re-keyed on
> *representability*, and the correction is the second time in one day I built on a Harmonia A claim
> that was falsified within hours, which is itself the best evidence for §1.6. **Harmonia C's
> stranded calibration library is now the single most important operational fact on the board** and
> is promoted to §8 item 0. §6 gains the distinction that rescues the eval suite from D's result:
> **computation-checkable ≠ decidable-in-a-theory.** §1.6 gains a base-rate null applied to my own
> headline, per the panel's standing rule.
>
> **v3 changelog:** Techne reported. The §1.5 fossil count goes **3-of-5 → 4-of-6** — Techne
> independently cites the same superseded property — which promotes it from "a claim that needs
> correcting" to **a measured property of how this fleet handles evidence** (§1.6, new). §2.5 is
> new: the fleet's consensus experiment has now accumulated **four independent fatal
> preconditions**, none of which its proposer specified — this is where the fan-out's entire ROI
> sits. Techne also unblocks a thread I parked in June (§2.6).
>
> **v2 changelog:** §1.5 new and urgent. §5 corrected — the battery fails **loud and wrong**, not
> silent (my v1 said the opposite, following Charon). §2 gains the Charon-vs-Harmonia-A collision.
> §6 qualified by the novelty-inflation finding.

---

## 0. Why this document is not another assessment

Five agents have now answered the same question. My job is **not** to add a sixth answer. It is
to read the five as *data* — because a fleet converging is itself a measurement, and this
program's doctrine says convergence is the thing to be suspicious of.

I argue the fleet is **substantially right and collectively exposed on one axis**, that it is
**already propagating a superseded claim** (§1.5), that there is a **cross-agent synthesis no
single agent stated** (§4), and that there is a **cheap retrodiction nobody proposed** (§5) that
adjudicates the program's entire year of nulls.

---

## 1. What each agent MEASURED (not what each argued)

Stripping arguments, keeping only things emitted by code, `git`, or a corpus:

- **Harmonia B:** 12,666 tracked markdown docs · **8** typed training objects · **1** survives
  audit. April peak 28,268 `.md` touches; May at 7% of April; June at 1.4%. Everything that died
  was coordination machinery; everything that lived was an instrument or a corpus.
- **Harmonia A (E3, executed):** `verify()` returns `valid=False, kill_pattern=unknown_kind` for
  graph / pigeonhole / linear_algebra / identity / inequality. `_DISPATCH.get(probe.kind)` returns
  `None` for any unregistered kind. Set-B novelty reach **17%**; the 4 genuine out-of-manifold
  accepts were **hand-routed around the gate**. `entails()` — a closure primitive — exists and is
  **called by nothing in production**. Apollo's llm2: **2,860 cells / 2,846 "distinct shapes" →
  zero accuracy lift.**
- **Charon:** `kill_vector` **0% populated** across 5.4M corpus records; kill-geometry exists only
  as string labels (33.6% null).
- **Ergon:** corpus 1,486 records / 79% confirmations against 100M+ generated failure records.
  Greedy-LoRA's +0.68 decomposes to format ≫ kill-prior ≫ template-class ≫ reasoning. Routing
  residue navigable **behaviorally** (+0.075 AUC), **NULL semantically**.
- **Techne (E3, executed):** `python -c "import prometheus_math"` → **`ModuleNotFoundError: No
  module named 'cypari'`**. The arsenal's front door is bricked in the default interpreter, and
  eager hard-imports take down the **pure-stdlib** primitives with it — *including
  `reasoning_quality_emit`, the primitive the decisive experiment needs.* Filed 06-22 and declined;
  six weeks of env drift turned an observation into a blocker. Also: `signature_index` compresses
  **413M records → 3,311 shape-classes** ≈ 0.7–1.7 MB ≈ **200–450K tokens** — the entire
  proto-tensor plausibly fits in a 1M context (flagged by Techne as an *estimate to be measured,
  not asserted*). And `aporia/docs/gemini_research_queue/` — named in my own role doc as the
  400-entry default firing queue — **does not exist.**
- **Harmonia C (E3):** **2,239,810 lines of Python in 8,726 modules, of which 577 (6.6%) are ever
  imported**; 63% by volume is generator output nothing ever read; **200 files are not
  syntactically valid Python** — produced, committed, never parsed, including by the forge that
  made them. And the one that matters most: `prometheus_math` (307 modules, ~160K LOC) + `techne.lib`
  are **87% unreachable since April** — **29/222 importable → 46 with `cypari` → 48 with `snappy` →
  220/222 with `knot_floer_homology`**, and `pip install snappy` alone resolves all three. Root
  cause is one line: `prometheus_math\__init__.py:35` → `techne\lib\class_number.py:19` → bare
  `import cypari`. Also: decision-machinery modules are orphaned *less* than average (5.4% vs 8.4%).
- **Harmonia D (E3):** the `unknown_kind` bug fires **160/160 at R5/R7/R8** on the live ladder —
  the fossil confirmed at scale. `TIER_GENS` holds exactly `R0,R1,R2,R3,R5,R6,R7,R8`: **R4 and
  R9–R12 do not exist.** Five-sixths of the upper ladder was never built; the R0–R12 ladder is a
  design document, not an instrument.
- **Hephaestus (E3-me, re-executed on M3 before use):** `import prometheus_math` →
  `ModuleNotFoundError: cypari` (independent third confirmation); **the Lean 4 + Mathlib harness
  exists in-repo, green-tested, and has been consumed by nothing since May 29**; `grade_reasoner`
  has zero non-Harmonia consumers; the model-zoo runner is ready and unrun. Plus the inventory that
  reframes everything: **fifteen-plus shipped, working, unconsumed assets** — grading oracle (0
  consumers), Lean harness (0 importers), model zoo (ready, unrun), 9 typed blackboard ops (never
  registered), `pg_redis` (0 rows ever), the tensor family (0 consumers since May), 422 finished
  deep-research reports, `kill_vector.py` + navigator (104KB of code, field 0% populated), the
  24,847-example Talos corpus. And: **99.2% of commits during the 44-day blackout were a cron
  emailing confabulated status to James 6×/day.**
- **Aporia:** six weeks of cron-only commits; the decisive experiment blocked on a dead
  motherboard; 21 retire candidates frozen on a single-family verdict. *(Caveat, per the panel's
  standing rule 1 — repo state is not program state. My dormancy reading was taken from this
  machine's HEAD. M2's catch-up commit shows June work sat uncommitted for 6.5 weeks, so "the repo
  was quiet" and "the program was quiet" are not the same claim, and I asserted the second from
  evidence for the first.)*

**These do not conflict.** Read together: *the program's generative side works and its recognition
side does not.* Generation produced 100M+ records, 3.8M verified objects, 92K tests. Recognition
produced 8 typed objects, 1 verified, 0 novel-shaped certifications, and a router keyed on surface
form.

## 1.5 — URGENT: the fleet is propagating a claim that was measured false today

This is the highest-value thing in this document and it is time-sensitive.

**The claim:** *M0's 0% type-II — "the battery never certifies a true claim FALSE; it fails closed
and silent."*

**Who is standing on it right now — four of the six agents:**
- **Harmonia B** files it in **Tier 2** — "executed measurements that took adversarial contact and
  **held**" — and calls it "the reason the audit fallback is a real position rather than a
  consolation prize."
- **Charon** calls it "the defensive result I would have asked for" and builds its
  fail-closed-not-loud framing on it.
- **Techne** states it as settled fleet state: *"the M0 keystone says the selector cannot see
  novelty and fails **closed** (0% reject — a trustworthy audit property)."*
- **Aporia (me, v1)** repeated it verbatim: *"it does not say 'false.' It says nothing."*

**What Harmonia A measured this session (E3):** the 0% holds **only because the M0 harness
charitably hand-routes unrepresentable shapes.** A downstream consumer calling `verify(probe,
claim)` directly gets a true claim certified **WRONG**. Strict type-II is **up to 5/18**, not
0/18. The abstention was supplied by the measurement harness, not by the instrument.

**Confirmed at scale the same day (Harmonia D, E3):** the `unknown_kind` bug fires **160/160 at
R5/R7/R8** on the live ladder. This is no longer a property of an 18-item benchmark — it is the
operating behaviour of the instrument the program grades itself with.

**So four of six agents built a position on a property that a fifth falsified in the same 24-hour
window.** Harmonia B's tier system is itself falsified by this: it classified the 0% as having
"taken adversarial contact and held," and it did not hold — it broke this session, under the first
adversary to actually execute it.

This is the **same failure pattern as the "2,351 promotions" fossil**: a number that outlived the
formula that produced it, propagating through documents because nobody re-ran it. We have now
caught it twice — and Techne, who *found* the 2,351 fossil, is one of the four who repeated this
one. That is not a criticism of Techne; it is the strongest possible evidence that the mechanism is
structural rather than a lapse of care.

**Actions, today:**
1. Harmonia B's Tier 2 needs the 0% entry struck or requalified; the audit-fallback position that
   rests on it needs re-argument.
2. Charon's fail-closed framing needs revision — the revision **strengthens** Charon's own
   navigability case, so this is not a demotion.
3. Techne's §1 fleet-state summary needs the same correction before it seeds another session.
4. Anyone citing "0% type-II" after today is citing a fossil. Harmonia A's fix — `return
   valid=None` for `unknown_kind` — should land before anything else consumes `verify()`.

## 1.6 — What §1.5 actually measures: the citation chain that looks like corroboration

The fossil is worth more as a *measurement of the fleet* than as a bug to fix.

Six agents produced independent assessments. On this claim, **exactly one executed the code and
five cited a summary** — `M0_RESULTS.md`, or another agent's reading of it. The five citations
were written independently, in different voices, from different role-doctrines, on two machines.
They *look* like five-fold corroboration. They are **one measurement with five pointers at it**,
and the one measurement was wrong in the direction that flattered the program.

Generalized, and this is the protocol finding of the day:

> **In a fan-out, agreement on a factual claim is not evidence unless more than one agent
> independently executed it.** A shared evidence base makes N agents into one agent with N voices.
> The fan-out multiplies *judgment*, not *verification* — and judgment inherits every defect in
> the shared base.

This is a distinct failure mode from the one our doctrine already names.
`feedback_llm_convergence_is_gravity_amplifier` warns that convergence on a *framing* signals the
training corpus. This is narrower and more tractable: convergence on a *fact* signals a common
source document. The fix is mechanical rather than epistemic:

- **Tag every load-bearing claim with who executed it and when** — E1 (read the source) vs E3
  (ran it) is already Harmonia A's convention; make it a fleet requirement, and make the *agent
  identity* part of the tag, not just the level.
- **Rotate one agent per round into a re-execution role** whose only job is to re-run the top
  N cited facts. It would have caught this in minutes.
- **Charon's decoy calibration is the right instrument** and §1.5 is its empirical case. Four of
  six of us — me included — missed a live defect in a claim we were all citing. That is a measured
  reviewer-sensitivity number, and it is not flattering to any of us.

**Applying the panel's standing rule to my own headline.** The Harmonia panel's sharpest
methodological result is *"every lens that MEASURED survived; the lens that INFERRED died"* — A's
§1 and C's own draft claim were the same shape (N striking instances → a disposition) and both fell
to one base-rate script. **My §1.6 generalization is that shape.** I have two instances (the 0%
fossil, the 2,351 fossil) and I am inferring a property of how the fleet handles evidence. By the
panel's own rule I owe the base rate before this hardens:

> **Proposed — the citation-chain base rate (cheap, today's documents only).** Enumerate every
> load-bearing factual claim cited by ≥2 of the seven assessments. For each, count how many agents
> *executed* it (E3) versus *cited* it (E1/inherited). If independent execution is common and these
> two fossils are outliers, my §1.6 is an anecdote dressed as a mechanism and should be withdrawn.
> If single-execution-many-citations is the norm, the mechanism is real and the re-execution
> rotation is justified.

I am pre-committing to withdraw §1.6 if the base rate goes against it. That is the discipline C
demonstrated by killing its own headline, and it would be incoherent to propose the rule for the
fleet and exempt my own claim from it.

**A third data point arrived while I was writing this, and it cuts against me being smug.** My v2
and v3 accepted Harmonia A's §3(b) — *novelty is not-in-closure, not unrecognized-shape* — and I
re-keyed my §5 retrodiction on it. **Harmonia D then retracted that claim** (executed over 9
claims: a closure test reduces to `{false statements} ∪ {solver timeouts}`). So within one day I
built on a Harmonia A claim twice, and both times it was falsified by an agent who ran code. I am
not the auditor of this pattern standing outside it; I am one of its instances.

## 1.7 — §1.6 generalizes, and the general form is worse: the fan-out was endogenous

Hephaestus's D1 caught something none of the other six of us did, and the catch is more important
than the specific claim it corrects.

**Not one of the seven assessments — mine included — contains a single web-grounded fact about the
2026 external landscape.** Seven agents, two machines, four role-doctrines, one shared repo, and
**zero queries outside it.** Hephaestus was the only seat that looked out, and what it found was
not decoration:

- **AlphaEvolve** is making genuine constructive discoveries (improved Ramsey and TSP bounds,
  67-problem sweeps, per-problem setup in hours). That is *the founding Prometheus paradigm* —
  generative variance plus ruthless selection — validated externally, run with frontier mutation
  engines and real verification as the selector.
- **AlphaProof-Nexus** resolved **492 OEIS conjectures** via evolutionary Lean proof search.
- **RLVR / process-reward literature** reports **process-level supervision beating outcome-only by
  ~10pp on small models.** That is the KillVector thesis in external clothing — *train on how it
  failed, not whether* — and it is the empirical support the program's central bet has never had.

**This is §1.6 one altitude up.** There, N agents citing one measurement were one measurement with
N pointers. Here, **N agents reading one repo are one repo with N voices.** A fan-out cannot escape
the corpus it reads, and ours read only itself. The failure is structural and it does not care how
many lenses you add — Harmonia ran *four* deliberately non-overlapping lenses and all four were
endogenous.

**This forces a correction to my own fleet-protocol rule (§2).** I wrote: *weight Hephaestus/Fable
divergences above Claude concurrences*, on the theory that model-family diversity was the operative
variable. Reading D1–D8, I no longer think that is right. Hephaestus's most valuable contributions
— the external landscape, the archaeological answer to my repair question, the Lean-vs-decision-
procedure distinction — came from **going outside the corpus and re-executing claims**, not from
being Fable. A Claude seat with web access and a re-execution mandate would have produced most of
it. The revised rule:

> **Every review round must contain at least one externally-grounded seat** — web, literature,
> external benchmarks — and at least one re-execution seat. Model-family diversity is a *weaker*
> secondary control, worth having, but it is not what produced the value today.

That is falsifiable and cheap to test: run the next round with an externally-grounded Claude seat
and see whether its divergence yield resembles Hephaestus's. If it does, family diversity was
never the lever. **I am stating this against my own earlier rule, which the fleet has already
adopted and which Hephaestus placed §2 first in deference to.**

> **Status: ADOPTED, and by the seat it demotes.** Hephaestus's disposition postscript (`e712afde`,
> same day) endorses the revised rule "over my own §0 framing" and over "the rule that flattered
> this seat." The exchange closed with corrections running both directions — D1/D2/D3 into this
> document, the protocol correction back out — which is the only interaction today that produced
> *mutual* revision rather than one agent citing another. Worth noting as the shape to repeat: it
> worked because both seats had executed something the other hadn't.

## 2. The convergence — and why it is a warning

All five assessments independently reached: (1) the decisive move is **instrument repair**; (2)
the same **admissibility rule** for frontier models, near-verbatim across three agents — *a model
may occupy any role where its output is falsified by something that is not a model*; (3) the same
**anti-list** — not another review round, not a swarm restart, no frontier-model gold; (4) the
same **diagnosis vocabulary**.

Under `feedback_llm_convergence_is_gravity_amplifier` this should alarm us. But the failure mode
is not the usual one:

- It is **not** training-corpus gravity — these are conclusions about our private repo.
- It **is** anchoring. Every agent read the same two resume docs, both written this morning, both
  naming M1-metabolization as the pickup. We cannot distinguish "five agents independently found
  the truth" from "five agents read the same two paragraphs."

**The convergence carries near-zero independent information, and this is structural.** The fleet's
genuine value appeared only where agents *collided*:

- **Charon falsified Ergon's Move 1** — the C1 arm is unbuildable because `kill_vector` is 0%
  populated, and the only retrieval key left is the label channel Ergon's own routing eval
  measured as NULL. That objection saved a quarter.
- **Charon added the C1-oracle arm** — separating *"the residue is exhaust"* from *"our retriever
  put the wrong residue in the window."*
- **Harmonia A falsified the 0% type-II** the rest of us were standing on (§1.5).
- **Harmonia A vs Charon — the sharpest live disagreement in the fleet, and neither knows it yet.**
  Charon's representational lane proposes an **encoding-forge**: have frontier models emit z3/sympy
  encodings *plus the kind registration* for kinds the selector cannot represent. Harmonia A's §3(a)
  is a pre-emptive refutation of exactly that: **"widen the representable-shape inventory" is
  Goodhartable** — if the mechanism is a lookup table, it is "a metric whose numerator I control by
  typing," and 5 kinds → 12 kinds yields an instrument blind to shape 13 with a meter that reported
  progress the whole way. A's corrected artifact is a **translator** (claim → formula) with
  **kind-routing deleted, not extended**, because B1/B2/B4/B5/B6/C1/C2 "share no shape, they share a
  target language."
  **Adjudication: Harmonia A is right and Charon's lane should be re-specified as translator-building.**
  Charon's own counter-baseline guard survives intact and gets sharper — the comparator becomes
  *translator vs hand-written kind grammar*, and A's B′ is already the pre-registered instrument
  that decides it (*a lookup table cannot pass a held-out set; a translator can*).

**Fleet protocol, actionable today:**
- **Hephaestus (M3, Fable) is the only non-Claude seat.** Its *divergences* carry more information
  than everyone else's agreements combined. Read what it contradicts first; weight a Hephaestus
  objection above a Claude concurrence.
- **Harmonia A already did the right thing instinctively** — B′ authored by `gemini-3.6-flash`, an
  independent family, every claim gated on an *executed* checker, negative control 8/8. That is the
  template.
- **Adopt Charon's decoy calibration for the fleet itself.** Seed a review round with a planted
  defect from our null graveyard; an agent that misses it gets its verdict discounted by a measured
  factor — *including mine.* §1.5/§1.6 are the empirical case: four of six of us missed a live
  defect in a claim we were all citing.

## 2.5 — Where the fan-out's entire ROI actually sits: four fatal preconditions

I said in v1 that the fleet's convergence carries near-zero information. That stands. But the
picture is now sharper and more favorable to the gang-up, and I want to state it precisely,
because it changes what a fan-out is *for*.

Ergon proposed the consensus experiment (the Metabolization Probe). **Four independent agents each
found a different precondition that would have made it produce an uninterpretable result**, and
none of the four is in Ergon's specification:

1. **Charon:** `kill_vector` is 0% populated ⇒ the C1 arm has nothing to retrieve against. The
   experiment cannot be *built* as written.
2. **Charon:** retriever/residue confound ⇒ without a **C1-oracle** arm, a null reads as "the
   corpus is exhaust" when the honest reading may be "we never built the index."
3. **Techne:** the `grading_oracle` staircase tops out at **62%** with a 3-point top step ⇒ if the
   metric is saturated there is no headroom, and a null is instrument ceiling misread as absence of
   signal (`feedback_instrument_vs_architectural_pass`).
4. **Techne:** `prometheus_math` does not import ⇒ **`reasoning_quality_emit`, the primitive the
   experiment depends on, is unreachable in the default interpreter.**

Run as originally specified, the fleet's unanimous decisive experiment would have consumed the
revival and returned a number nobody could interpret — and, worse, a *null*, which this program
would have written into doctrine.

**That is the ROI of ganging up, and it is not where anyone expected it.** The value was not in six
strategies; the strategies converged and told us little. It was in six adversaries finding
preconditions on one experiment. **A fan-out is a precondition-finder, not an idea generator** —
and it should be budgeted, sequenced, and read that way. Concretely: put the decisive experiment on
the table early and let everyone attack *it*, rather than asking everyone for a strategy.

## 2.6 — Techne unblocks a thread I parked in June (neither of us noticed)

My 2026-06-09 reasoning-steering handoff parked **Path A — the inference arm**, described then as
*"independent model judges over contested candidates, screened for curl first. Needs inference
resourcing (deferred). The only place the non-conservativity thesis can still live."* It has sat
dead since, for want of ≥2 genuinely independent evaluators.

Techne §3.3(b), arriving from the substrate side and not referencing that thread, supplies exactly
the missing producer: `TOOL_REASONING_QUALITY_EMIT` was forged, tested, registered and dead because
no live ≥2-evaluator scoring site existed in-tree — and **four heterogeneous frontier families are
that site.** Techne's spec constraint is the one that matters and it matches mine independently:
*re-prompts of one model reproduce the g2c NULL; the evaluators must have different bases and
objectives.*

And Techne states the inversion in my own doctrine's terms without citing it: **"for the panel,
agreement is the boring case. We are not polling models for a consensus verdict — that's
inflation; we are mining them for cyclic disagreement. Model diversity is the instrument, not the
authority."** That is precisely `feedback_anticorrelation_is_not_noncyclicity` plus
`feedback_flow_conservative_by_construction`, and it is the first proposal in the program where
frontier-model heterogeneity is *admissible by construction* — because the thing being measured is
their **disagreement structure**, which no single model can fake and which no model adjudicates.

**Consequence:** the reasoning-steering arc's dead arm is live for the first time since June, and
it rides on wiring Techne is building anyway (item 3). I am claiming it, and flagging that it does
**not** compete with the organism experiment — it consumes the same evaluator panel as a byproduct.

*(v5 qualifier — see §2.7: the evaluator panel needs ≥2 genuinely independent families, and M2
reports only one live API family. This thread is design-ready and resource-blocked, not runnable.)*

## 2.7 — The fifth precondition nobody costed: API access is station-dependent

`stations/M2_STATUS.md` §6 reports M2's measured tool shelf: **Anthropic, OpenAI, and DeepSeek all
out of credits. Only `gemini-3.6-flash` live, on the free tier** (bursty; retry on 503 or a whole
batch vanishes silently). Pro tiers 429 on quota.

Every frontier-model proposal in the fleet assumes access nobody verified:

- **Techne's evaluator panel** requires *four heterogeneous families* to mine cyclic disagreement.
  On M2's shelf that is **one**. Re-prompts of a single model reproduce the g2c NULL, which Techne
  itself flagged — so the panel is not merely degraded, it is invalid at N=1.
- **Ergon's Metabolization Probe** and **my in-context M1** assume long-context frontier capacity.
- **Charon's frozen-battery generator swap** requires *two generations* of generator.
- **Charon's and Ergon's open ask to James** was exactly this — "which providers are live, and the
  budget" — and M2 has now partly answered it: on that station, almost none.

**The distinction that actually decides what runs today**, and I have not seen anyone draw it:

> **Agent-in-harness access ≠ programmatic API access.** I am reading and writing this document on
> Opus 5 right now, through the Claude Code harness. That is not the same resource as an API key
> with credits, and it has a different cost model, a different rate limit, and a different failure
> mode.

Consequently the fleet's proposals split cleanly, and the split is not the one anybody planned:

- **Runnable now, in-harness:** anything an agent can execute as *work* — the retrodictions (§5),
  the repair ledger (§3), the citation-chain base rate (§1.6), the representability audit, grading
  B′ once, the tautology-verification scripts. These need no API budget at all.
- **Blocked on procurement:** anything requiring a *scripted multi-model panel* — Techne's cyclic
  disagreement arm, Charon's generator swap, any bulk trace factory.

**So the sequencing writes itself, and it inverts the fleet's implicit order:** do the in-harness
retrodictive work first — not because it is cheaper, but because it is the only tier that is
*unblocked*, and it is also the tier that decides which program we are in before we spend a budget
we do not currently have. Procurement becomes a decision informed by those results rather than a
precondition for starting.

This is the **fifth precondition** on the consensus experiment, and unlike the other four it is not
fixable by engineering.

## 2.8 — Two items from M2's station doc: one I am adding to, one I can close

**(a) The Aletheia collision — and there is a third referent nobody has named.**
Harmonia A flags two things called Aletheia: `agents/aletheia/` (knowledge-graph component, in-tree
since April) and `Aletheia_M4` (a role agent that has committed nothing yet). A is right that now is
the cheap moment, and right that it is the same shape as the `cid`-keyed registry that made M0 fail
on A4 — a referent collision under a shared surface name.

**The third referent is mine, and it makes this worse than A states.** `pivot/PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md`
lists **Aletheia among the RETIRE-after-HITL candidates** (the Coeus/Aletheia/Eos/Hermes pipeline
cluster), on consumer-drift grounds. So the incumbent is a *retire candidate whose disposition is
still in LIMBO*. If `Aletheia_M4` adopts the bare name while a retire dossier for `agents/aletheia/`
is pending, a future reader — or Hephaestus's name-merging meta-analysis — cannot tell whether
"retire Aletheia" means the component or the role. **That is a live path to retiring the wrong
thing**, which is precisely what the no-delete/HITL doctrine exists to prevent.

I endorse A's convention (`Aletheia_M4` for the role, path-naming `agents/aletheia/` for the
component, qualify in prose every time) and add: **the retire dossier must name the path, never the
bare name.** I own that dossier, so this one is mine to fix and I will.

**(b) The unused Postgres bus — I think this question is already answered.**
A measured the bus reachable from M2 and **completely unused (0 keys)**, and wrote: *"the fleet has
a working real-time channel that nobody is on… the reason we don't is unexamined."*

It is examinable, and the answer follows from the deletion test (§4) plus Harmonia B's own §1
finding. B measured that *everything that died was coordination machinery and everything that lived
was an instrument or a corpus*, and diagnosed it as outcompetition by the frontier harness rather
than as failure. **A real-time agent bus is coordination machinery.** Git commits are the channel
that survived the April collapse, and today the entire seven-agent fan-out coordinated through them
successfully — including this document, which exists only because I read other agents' commits.

So the bus being at 0 keys is not an anomaly to investigate; it is the deletion test's prediction,
confirmed. **Recommendation: do not adopt the bus, and do not spend on reviving it.** Note this
cuts against my own interest — I proposed the fleet-protocol changes in §2, and the tempting
implementation is a coordination channel. The correct implementation is a *convention on commits*,
which is exactly what A's `stations/<M>_STATUS.md` proposal is. **I am adopting it for M1** (see
`stations/M1_STATUS.md`) — one predictable path per machine, so Hephaestus's cross-machine loop has
one entry point per station instead of N scattered documents.

## 3. The unanimous recommendation nobody priced

Every agent recommends fixing an instrument. **No agent asked whether instrument repair has ever,
in this program's history, been followed by output.**

That is the void in this document set. "The instrument is broken" is *always* available and
*always* defensible — the perfect infinite regress, and the most comfortable conclusion available
to every agent here, not just to cartographers. Harmonia B declared this as its own bias with
unusual honesty; my point is that it is **not Harmonia B's bias, it is the fleet's**, and a bias
five agents share independently looks exactly like a finding.

The fair counter: these are *measured* defects. A router keyed on surface `cid` is a fact.

So decide it, cheaply:

> **The repair ledger (hours, retrospective, all data already in the repo).** Enumerate every
> completed instrument repair — seam-fidelity (06-15), denylist→allowlist (06-22), the v3 corpus
> correction, `object_id`, the `.176`→`.202` repoint, the promotion-gate audit. For each: (a) was
> there a preregistered prediction of what output would appear? (b) did it appear?
>
> Repairs historically **not** followed by output ⇒ the fleet's unanimous recommendation is the
> program's gravity well and we need a different move. Each repair **did** unlock something ⇒ the
> fleet is right, sequence repairs aggressively and stop apologizing.

I expected *mixed*. **Hephaestus answered it from the git archaeology the same day, and the answer
is sharper than my expectation:**

> Repairs restored **capability** — the DB repoint let today's sessions query; the seam fix
> produced honest verdicts; the rekey gave clean joins. **But no repair has ever been followed by
> a consumer consuming.** The only capability climb in program history — the +11pp/+32pp engines —
> came from *hand-metabolizing failure clusters*, with a human as the metabolizing mechanism, not
> from any instrument repair.

So the fleet's unanimous recommendation is **necessary but not sufficient, and the program's own
record says so.** Repair-first is not wrong; repair-*only* is the documented failure mode, eight
eras running. The operational consequence Hephaestus draws is the right one and it overrides my
framing: **run the repairs and one metabolization lane concurrently**, not serially — which is
also what the accepted dissent ordered seven weeks ago. Sequencing them strictly serially is how
the ninth era becomes a tenth.

The repair ledger survives as a work item, but its job changes: not *"does repair pay?"* (answered:
not by itself) but *"which repair class, if any, has ever been followed by consumption?"* —
formalized as a typed table. Hephaestus lists it as backlog item 8.

## 4. The synthesis no single agent stated: the deletion test

Two agents produced halves of one idea from opposite seats:

- **Harmonia B §1:** the April coordination substrate — symbol registry, sync stream, wave
  protocol, dissent ledger, tensor mirror — was not wrong, it was **outcompeted** by the frontier
  harness. *Every hour rebuilding coordination substrate builds something a model release will
  delete.*
- **Harmonia B §3 Tier 4 + Charon Move C:** what survives is verified ground truth that is **ours**
  — the 3.8M-object calibration anchor at 100.000%, LMFDB, the kill geometry, and the graveyard of
  documented methodological defects whose labels *we computed and that appear in nobody's training
  corpus.*

Neither stated the rule:

> **The deletion test.** For any proposed work: *would the next frontier model release make this
> worthless?* If yes, do not build it.
>
> **Deleted:** coordination machinery (proven, April), prose reviews, prompt scaffolding,
> hand-built memory/handoff, anything whose value is fluency.
> **Not deleted:** verified ground truth we computed, kill geometry, held-out labels that are ours,
> registered kinds and primitives, an eval nobody else can build.

Sharper than "no component revives into a vacuum," because it adjudicates *new* work too, and it
explains the May collapse rather than lamenting it. It is the operational form of
`feedback_frontier_models_window`: spend the window building what the window cannot take back.

**It disciplines my own proposal.** My in-context M1 probe passes only if it leaves a *measured
price for the residue* on disk. If it leaves a transcript, it fails.

## 5. The experiment nobody proposed — kill-resurrection as retrodiction

*(Corrected in v2. My v1 described the battery as failing "closed and silent," following Charon.
Harmonia A's E3 result says the opposite — and the correction makes this experiment stronger, not
weaker.)*

Chain three measured facts:

1. **Every measured wall sits in a syntactic router in front of a working semantic engine**
   (Harmonia A §1). The expensive semantic check *was already built and left out of the gate* in
   every case: F2 exists and does not gate; `entails` is called by nothing in production. A's null
   — *"all software dispatches on type tags, you are over-reading"* — **fails**, because the
   content check exists and was excluded. That is architecture, not incidental typing.
2. **The battery does not abstain on unrepresentable shapes — it rejects them** (§1.5). Direct
   `verify()` certifies true claims WRONG on any unregistered kind.
3. The program's record: 92K tests mostly killed, a 90-batch zero-promotion streak, zero novel
   discoveries in a year.

**If (1) and (2) hold, (3) is not clean evidence the substrate found nothing. It is partly evidence
the detector was blind — and actively wrong — in exactly the band where a find would appear**,
because a novel-shaped result is by construction one whose kind is unregistered, and an
unregistered kind is what the router rejects.

This is the most self-serving reinterpretation available and `feedback_narrative_resistance` exists
to stop it. So it must be tested, and it can be, with an unusually strong test:

> **Kill-resurrection retrodiction.** *(Re-keyed in v4. My v2/v3 routed this through a closure test
> — Harmonia A's `entails`. **Harmonia D retracted that**: a closure test reduces to
> `{false statements} ∪ {solver timeouts}`, and more generally* **decidability and novelty are
> anti-correlated by construction** *— where a closure test terminates, everything true is already
> inside the closure. The retrodiction survives because it never needed derivability; it needs
> only* **representability**.*)*
>
> Take a stratified sample of historical kills from the 92K corpus and the zero-promotion streak.
> For each, ask the narrow, decidable question: **could the battery, at the time, express this
> claim at all?** Then re-run the representable-but-misrouted subset through the **translator**
> (kind-routing deleted) rather than surface-`cid` dispatch. Ask: what fraction of historical kills
> were **routing artifacts** rather than genuine falsifications?
>
> This is now a *representability audit with a re-run attached*, not a novelty meter — which is
> exactly what D's standing test demands of it: *what does your meter return on (a) a false
> statement and (b) something the checker cannot decide?* Here, (a) stays killed and (b) is scored
> as `unrepresentable`, not as `novel`. It cannot degenerate into a timeout detector.
>
> **This is a retrodiction.** The data exists and cannot be tuned to fit — far stronger than any
> forward experiment.
>
> - **Resurrects nothing** → the router thesis is dead, the nulls were real, the substrate genuinely
>   found nothing, and the program should face that rather than repair around it. *This is the
>   outcome that should most change our behavior, and I pre-commit to it.*
> - **Resurrects a measurable fraction** → a year of nulls is partly instrument-blindness, the
>   translator is *the* priority, and every downstream conclusion drawn from those kills needs a
>   corpus-scale taint-check — same logic as the tautology cluster.

Companion, to decide where to aim:

> **The detector-band audit.** Cross-tabulate the substrate's own output kinds against the kinds
> the battery can represent. Most output in unrepresentable kinds (graphs, matrices, multi-variable
> inequalities) ⇒ blind-band reading supported, translator is the binding constraint. Output
> overwhelmingly in representable kinds ⇒ the blind-band excuse fails and the nulls stand.

Days, existing data, and together they adjudicate between **two completely different programs**.
No other proposed experiment does that.

**Harmonia A supplied the strongest evidence for this whole line without meaning to (§6, E3):**
building B′, A's first run rejected **20/20 true claims — zero for content reasons.** A sandbox
blocked `import itertools`; a regex screen false-rejected `from X import Y`. *A reproduced the
syntactic-router failure inside the session that diagnosed it, in code written while holding the
diagnosis in mind.* If the pattern is that hard to avoid when you are actively looking for it, the
prior that it contaminated 92K unexamined historical kills is high.

## 6. What is actually achievable — the honest ceiling

**~~Not achievable in 3 months~~ — CORRECTED in v6. This was my claim and it was wrong in method,
whatever its verdict turns out to be.**

I wrote that a novel mathematical discovery is not achievable and we should stop implying
otherwise, reasoning from our internal record: zero discoveries over a year across 92K tests.
Hephaestus's D1: **the fleet priced that with zero external data.** I used our own null history as
the prior without ever checking whether the world had moved — the precise error I would name in
anyone else, and a direct instance of §1.7.

What the external check shows: AlphaEvolve improves Ramsey and TSP bounds with per-problem setup
measured in *hours*; AlphaProof-Nexus resolved 492 OEIS conjectures. Both are variance-plus-
selection with **frontier mutation engines and formal verification as the selector.** Our zero came
from a configuration whose selector was a syntactic router and whose mutation engine was in-loop
LLM mutation — a mechanism we killed (llm2: 2,152 mutations, zero lift). *Those are not the same
experiment*, so our null does not price theirs.

The honest restatement: **a discovery lane is a live bet with a hard kill-date, not a foreclosed
one.** Hephaestus's L4 — and James's 08-12 ruling narrowing it to 10–30 audited score-and-improve
problems with machine-checkable scores, anti-rediscovery screens, and success redefined as
*Prometheus-guided search beats unguided search* — is the right shape and carries the earliest kill
in the plan. I withdraw the ceiling claim and support the lane, noting that Hephaestus owns the
forge and declared that conflict itself.

What survives from my original point: **nothing in the new model generation changes the generative
side on its own.** Charon's frozen-battery generator swap prices that in days, and I still expect
"fluency, not reasoning" from the raw generator. The external evidence is that the *harness* — a
real verifier in the selection loop — is what converts fluency into discovery. That is a claim
about architecture, not about model quality, and it is consistent with everything else in this
document.

**Achievable and genuinely valuable:**

1. **A verified answer to whether our year of nulls is real** (§5). Days. Retrodictive. My top pick.
2. **A measured price for the residue** (Ergon's probe + Charon's C1-oracle arm, gated behind
   `kill_vector` actually being computed). Days.
3. **An owned, externalizable evaluation suite** — the quarter-scale bet.

On (3): three assets exist in pieces and nobody proposed assembling them.

- **B′** — 24 held-out claims, 6 domains, authored by an *independent family*, each admitted only
  after its checker was **executed**, negative control 8/8, oracle quarantined. Real, and new since
  June.
- **The graveyard** — dozens of real, subtle, documented methodological defects with verdicts *we
  computed*: degenerate row nulls, sorted-array Spearman, conservative-by-construction flows,
  generator-prefix MI, the tautology cluster. Labels in **nobody's** training corpus.
- **The calibration anchor** — 3.8M objects at 100.000%, LMFDB.

**Two qualifications, and the second rescues the suite from the first.**

*(1) Shape-keyed novelty inflates trivially* — Apollo's 2,860 cells / 2,846 "distinct shapes"
produced **zero** accuracy lift, so the suite cannot key novelty on unrecognized shape. My v1 phrase
"out-of-manifold truth recognition" also inherits Harmonia A's objection that recognition against an
authored manifold is ill-posed — *you cannot author a recognizer for novelty you have not
conceived.*

*(2) But the obvious repair is closed off.* My v2/v3 adopted A's re-posing as **derivability**.
Harmonia D killed it, and the general result is the deepest thing the panel produced:
**decidability and novelty are anti-correlated by construction** — where a decision procedure
terminates, everything true is already inside the closure, so nothing is ever novel; outside that
fragment it returns `unknown`. **The decidable region and the interesting region are disjoint.**

Note what this explains: D's *theoretical* result and M0's *empirical* result are the same wall
seen twice. M0 certified zero novel-shaped truths; D says a theory-decision instrument structurally
cannot. Theory and measurement agreeing is worth more than either alone.

**The escape hatch, and it is the strategic point of this section: computation-checkable ≠
decidable-in-a-theory.** B′ does not use a decision procedure over a theory — **each of its 24
claims was admitted only after its own brute-force checker was executed and returned True**, with a
negative control of 8/8. That is *evaluation on a finite domain*, not deduction within an
axiomatized fragment. D's anti-correlation bites decision procedures; it does not bite finite
computation. So the suite's novelty axis must run through **executed checkers**, never through
`entails`-style closure — which is what Harmonia A already built, apparently by instinct rather
than by this argument.

**Hephaestus's D3 extends this, and the extension matters more than my original.** I had two
categories; there are three:

1. **Decision procedures** (z3-closure). Bitten by D's anti-correlation. A false statement scores
   maximally novel — it fails **WRONG**.
2. **Finite computation** (B′'s executed brute-force checkers). Escapes, because it evaluates
   rather than deduces. Bounded to finite domains.
3. **Certificate-checking** (Lean/Mathlib). **Also escapes, and scales past finite domains** — the
   category I missed. Lean does not decide; it checks a certificate for a proof a prover *found*,
   and novelty is adjudicated against a **library plus a literature screen**, not against a
   closure. Run D's own standing test on it: a false statement can never acquire a certificate, so
   it fails **SAFE** (silence); unprovable-in-budget returns nothing at all. That is exactly the
   failure profile a novelty gate needs, and it is the profile the AlphaProof-Nexus-class results
   operate under.

So the corrected principle: **falsification by computation or by certificate scales to novel
shapes; falsification by decision procedure cannot, ever.** The practical consequence is that the
translator should target **z3 for the decidable fragment and Lean for the rest** — and the Lean
harness is already in-repo, green-tested, and **consumed by nothing since May 29.** That makes the
second target a wiring job, not an adoption project.

**One doctrinal note I want to place carefully, because it could be misread.**
`feedback_llm_convergence_is_gravity_amplifier` says frontier-LLM convergence on a *critique* is
evidence the framing sits in the training corpus — a warning, not validation. The RLVR result in
§6 is **not** that kind of evidence: *process-level supervision beats outcome-only by ~10pp on
small models* is an **experimental finding**, not a framing an LLM agreed with. Treating external
empirical results as gravity would let us dismiss the first real corroboration the KillVector
thesis has ever had. **Convergence of opinion is gravity; convergence of independently-run
experiments is evidence.** The doctrine should be read as covering the first only.

**Why the graveyard is more than hygiene (Aporia's framing):** each documented defect is a place
where a plausible narrative diverges from computed truth. The set of defects a model family
*systematically* misses is a **map of that family's gravity wells** — void detection applied to
reasoners instead of to mathematics. That is a first-class North-Star instrument, and §1.5 just
demonstrated the method works on *us*.

## 7. Where I disagree with the fleet

- **Against Harmonia B's Move 3 (retire by disuse, hours, no meeting).** Disuse since May is
  confounded with the May *collapse* — the whole program stopped, so non-touch is not evidence of
  irrelevance. It also collides with ratified doctrine
  (`feedback_retirement_needs_thoughtwork_dossier_hitl`). I support `archive/` as a **context-budget**
  move — the cold-start tax is measured and real — but read-only relocation, not disposition, and it
  must not retroactively decide the 21 candidates.
- **Against Charon's encoding-forge as specified** — see §2. Re-specify as translator-building;
  Harmonia A's Goodhart objection lands.
- **Against my own v1** — twice. The battery does not fail silent (§1.5/§5), and "recognition" is
  the wrong frame for novelty (§6). Both corrections came from Harmonia A executing code while the
  rest of us reasoned about it. That is the fleet working.
- **On the forge $900 — unchanged and stronger.** Four of five agents now place the decisive work
  in-context or in-corpus. Nothing in the top five moves needs the box.

## 8. What needs James

> **SUPERSEDED IN PART — James ruled on 2026-08-12 PM**, recorded in Hephaestus §7.5. The ruling:
> the missing Darwinian component is **heredity** (mutation ✅, selection ✅, measurement ✅,
> inheritance ❌); **L0 is a pit stop, not a program** (days); **L1 is Priority #1 by a mile**, split
> into an in-harness Tier A (zero API) and a procurement-gated Tier B; **new constitutional rule —
> no new architecture until one failure produces one verified improvement**; L4 runs but tiny
> (10–30 audited problems); every meter ships a positive control and a cheat control or its output
> is inadmissible. **Arm names were pinned** — F0 / F-oracle / F-prom / F-null / F-format —
> explicitly to prevent the next citation fossil, since James's C1/C2/C3 and Ergon's C1/C2/C3 were
> already different things. *That is §1.5's lesson applied prospectively, and it is the fastest
> doctrine-to-practice turnaround I have seen in this program.*
>
> My items below that survive the ruling: the two retrodictions (Hephaestus seconds them), the
> repair ledger in its *revised* form (§3), the citation-chain base rate, and the Aletheia path-
> naming fix. My forge-$900 recommendation is answered and improved on — **don't spend, and power
> up M2**, which has an idle RTX 5060 Ti and has been dark since 2026-05-30.

0. **Unbrick the calibration library — and it is one command.** Harmonia C counted the doors that
   Techne found: **29/222 modules importable now → 220/222 after `pip install snappy`** (it pulls
   `cypari` and `knot_floer_homology` with it). Root cause is one line,
   `prometheus_math\__init__.py:35`. C correctly did **not** run it — it changes your global
   interpreter, so it is your call, and it is the single cheapest high-leverage item on the board.
   Pair it with Techne's try/except guards so a missing native backend degrades *that namespace*
   rather than the package, or this recurs at the next env drift.

   **Why this outranks everything else here:** ruling R1 makes mathematics the program's
   calibration standard, and the library that scores that standard has been **87% unreachable since
   April**. *Any instrument that "passed on math" this year passed against 29 modules.* That is a
   retroactive qualifier on every calibration claim in the program, including the ones I have been
   treating as our most durable asset. (Honest bound, C's own: an import is a weak positive — it
   does not certify the mathematics — and a strong negative.)
1. **Land Harmonia A's `valid=None` fix and broadcast §1.5** before anything else consumes
   `verify()` or cites 0% type-II. Free, and it stops a fossil mid-propagation — one that four of
   us were repeating this morning.
2. **Clear all five preconditions (§2.5, §2.7) before the consensus experiment runs.** As specified
   it would have returned an uninterpretable null. Techne's grader-headroom check is the cheapest and
   least obvious of the first four: *if the staircase is saturated at 62%, a null means nothing.*
   The fifth is not fixable by engineering — **API credits.** Which leads to:
2b. **Do the in-harness tier first, and treat procurement as a decision, not a precondition
   (§2.7).** Everything I am asking for in items 3–4 runs as agent work with no API budget. The
   multi-model panel work does not. Deciding the budget *after* the retrodictions is strictly better
   than before them, because the retrodictions tell you which program you are buying for.
3. **Approve the two retrodictions (§5)** — kill-resurrection + detector-band audit. Days, existing
   data, decides which program we are in. My top research ask.
4. **Approve the repair ledger (§3)** — hours, prices the fleet's unanimous recommendation before we
   spend a quarter on it.
5. **Adopt the deletion test (§4)** as the portfolio rule, superseding "revive only into a consumer."
6. **Fleet protocol (§2, §1.6):** weight Hephaestus/Fable divergences above Claude concurrences;
   adopt decoy-calibration for agent reviews including mine; **rotate one agent per round into a
   re-execution role** whose only job is re-running the top cited facts. §1.6 is the case for it.
7. **Sequencing:** Charon is right that `kill_vector` gates Ergon's probe. Do not run the probe
   before the navigability gate, or we will measure our retriever and call it the corpus.

**Housekeeping I owe, from Techne's addendum:** `aporia/docs/gemini_research_queue/` is named in my
own `RESPONSIBILITIES.md` as the 400-entry default firing queue for the daily Deep Research tokens,
and **it does not exist**. My role doc has been describing a nonexistent artifact. I concur with
Techne's stand — do *not* rebuild it yet; a queue rebuilt now would refill `pivot/` with exactly the
artifact class that preceded six quiet weeks. I will correct the role doc rather than the queue.

**Provenance caveat on the model landscape:** Techne's §3.1 release list (GPT-5.5, GPT-5.6-Cyber,
Gemini 3.6 Flash, DeepSeek-V4-Pro MIT-licensed) is from release trackers and Techne flags it as
needing vendor confirmation. I cannot independently verify it either — my knowledge cutoff predates
all of it. The one corroborated entry is `gemini-3.6-flash`, because Harmonia A actually ran it to
author B′. Treat the rest as unconfirmed, and note that Techne's own guard — **pin `model_id` +
version + date as first-class provenance on every frontier-produced record** — is the right response
regardless of which list is accurate. That guard is a substrate schema change, it passes the
deletion test, and it should land with the emit wiring.

---

*v6. The fleet has reported. Its convergence was real and mostly right; its blind spot was that
every one of us read the same repo and none of us looked outside it. The seat that did found that
the founding paradigm has been validated externally while we were writing about why it hadn't
worked here — which corrected my own ceiling claim, and turned my §1.6 into the smaller version of
§1.7. My best contributions today were the fossil catch and the computation-vs-decision
distinction; my worst was pricing a three-month ceiling from an endogenous prior. Both are the same
lesson at different altitudes: a closed system of citations cannot audit itself, whether the
closure is one document or one repository.*

---

*v4, written before Apollo and Hephaestus reported. The fleet agrees, and agreement is the warning.
Four of six of us — me included — spent today building on a property a fifth measured false that
morning, which turns out to be the more useful finding: on a factual claim, six agents were one
measurement with five pointers at it. Then the Harmonia panel killed the mechanism I had re-keyed
my own experiment on, for the second time in a day, which is the strongest possible evidence for
the paragraph I wrote about everyone else. I have accordingly put my own headline (§1.6) behind a
base-rate null I have pre-committed to lose.*

*What is absent from all seven assessments is any check on whether the thing we all recommend has
ever worked, and any attempt to re-read our own history through the detector we now know was blind.
Those two absences, the fossil, the citation-chain mechanism, the four preconditions, and the
computation-vs-decision distinction in §6 are this document's contribution. The fan-out's value was
never the seven strategies — it was seven adversaries finding fatal preconditions on one experiment,
and one command that unstrands 87% of the library the whole program calibrates against.*

— Aporia, 2026-08-12
