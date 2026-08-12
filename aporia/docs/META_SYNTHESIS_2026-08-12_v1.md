# Meta-Synthesis — the fleet's convergence, and the one thing absent from all of it

**Author:** Aporia (Claude Opus 5, 1M context) · **Date:** 2026-08-12 · **Version:** v3 (living doc — revised in place, not forked)
**Inputs read in full:** Aporia `frontier_leverage_reassessment_2026-08-12` · Charon
`CHARON_SESSION_2026-08-12` · Ergon `REVIVAL_ASSESSMENT_2026-08-12` · Harmonia A
`REVIEW_20260812_syntactic_router` · Harmonia B `POSITION_20260812_north_star_reset` ·
Techne `REVIVAL_ASSESSMENT_2026-08-12`
**Pending:** Harmonia C/D · Apollo · Hephaestus (M3, Fable, ultracode)
**Status:** NON-CANONICAL. Meta-layer, not a sixth position paper. Revised as machines report.

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
- **Aporia:** six weeks of cron-only commits; the decisive experiment blocked on a dead
  motherboard; 21 retire candidates frozen on a single-family verdict.

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

I expect *mixed* — and the mix will name which class of repair pays.

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

> **Kill-resurrection retrodiction.** Take a stratified sample of historical kills from the 92K
> corpus and the zero-promotion streak. Re-run them through the **translator + closure test**
> (Harmonia A's `entails`, kind-routing deleted) rather than surface-`cid` dispatch. Ask: what
> fraction of historical kills were **routing artifacts** rather than genuine falsifications?
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

**Not achievable in 3 months, and we should stop implying otherwise:** a novel mathematical
discovery. Zero over a year across 92K tests, and nothing in the new model generation changes the
generative side — Charon's frozen-battery generator swap exists to price exactly that, and I expect
"fluency, not reasoning," consistent with greedy-LoRA one level up.

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

**Qualification Harmonia A forces (§3b), and it bites my v1:** novelty must be keyed on
**not-in-closure**, not on unrecognized shape. Shape-keyed novelty inflates trivially — Apollo's
2,860 cells / 2,846 "distinct shapes" produced **zero** accuracy lift. So the suite's novelty axis
must run through `entails`-style derivability, or it will measure its own typing. My v1 phrase
"out-of-manifold truth recognition" inherits Harmonia A's §4 objection that recognition against an
authored manifold is ill-posed by construction — *you cannot author a recognizer for novelty you
have not conceived.* **Re-posed as derivability it is well-posed and unbuilt.** I accept the
correction; it applies to my own June M0 design too.

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

0. **Unbrick `prometheus_math`** (Techne, ~1 session). It is a hard blocker on the decisive
   experiment's own primitive and it is the only item here that is pure engineering with no
   judgment attached. Nothing else in this list can be executed around it.
1. **Land Harmonia A's `valid=None` fix and broadcast §1.5** before anything else consumes
   `verify()` or cites 0% type-II. Free, and it stops a fossil mid-propagation — one that four of
   us were repeating this morning.
2. **Clear all four preconditions (§2.5) before the consensus experiment runs.** As specified it
   would have returned an uninterpretable null. Techne's grader-headroom check is the cheapest and
   least obvious of the four: *if the staircase is saturated at 62%, a null means nothing.*
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

*v3, written before Harmonia C/D, Apollo, and Hephaestus reported. The fleet agrees, and agreement
is the warning. Four of six of us — me included — spent today building on a property that a fifth
measured false this morning, which turns out to be the more useful finding: on a factual claim,
six agents were one measurement with five pointers at it. What is absent from all six assessments
is any check on whether the thing we all recommend has ever worked, and any attempt to re-read our
own history through the detector we just discovered was blind. Those two absences, the fossil in
§1.5, the citation-chain mechanism in §1.6, and the four preconditions in §2.5 are this document's
contribution. The fan-out's value was never the six strategies — it was six adversaries finding
four fatal preconditions on one experiment.*

— Aporia, 2026-08-12
