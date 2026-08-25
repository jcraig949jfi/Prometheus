# Apollo — ten experiments, prioritized, for review before a 48-hour run

> **From:** Apollo (M2), 2026-08-25 · **For:** James (HITL) and the shadowing frontier reviewer
> **Status:** nothing has been run. This is the plan, submitted for attack before execution.
> **Budget authorised:** 10 experiments, up to 48 hours, CPU-only, no paid API.
> **What I want back:** a re-ranking with reasons, kills on any experiment that cannot
> produce an interpretable negative, and — most valuable — **an eleventh experiment I have
> not thought of.** If the honest answer is "run three of these and stop," say that.

---

## 0. Constraint I am flagging rather than silently resolving

The Lexis library-learning study carries an explicit operator instruction dated 2026-08-24:
*"do not hand this to Apollo or Hephaestus, and do not adjust their code or plans on the
strength of it."* I have therefore built this list on **Apollo's own measurements** plus
Aporia's direct measurements **of Apollo**. Where an item touches the library-learning
literature (E6, E7) I mark it `[LEXIS-ADJACENT]` and it should be treated as blocked until
James rules on whether the 2026-08-25 instruction supersedes the 2026-08-24 one.

## 1. What changed since the last review

The reviewer has been shadowing, so this is deltas only.

- **O1 ran.** Verdict by the pre-committed rule: `EVOLUTION_MORE_EFFICIENT` — enumeration
  reached 0.833 in 1,687,896 evaluations against evolution's 3,144 (537×). Kill condition
  did not fire. **But the secondary result was larger:** enumeration's ceiling is *also*
  exactly 0.833, identical per-subset profile, across 1.74M type-correct pipelines.
- **Two earlier O1 runs were invalid and would have produced FALSE WINS for Apollo**
  (guard-tails capped at 3 when the winning shape needs 5; 4 orderings sampled when the
  known subset has 166,320 orderings of which 27.3% succeed). Archived, not deleted.
- **The ceiling was independently decomposed by another seat.** Aporia replicated canary 0.6
  and showed the missing 16.7% is *precisely* 20 **abstained** tasks in four categories at
  five each: `all_but_n`, `temporal_ordering`, `vacuous_truth`, `consistency_check`.
- **Two of my claims died.** (a) "canary needs a boolean primitive" is VOID — the existing
  pair scores 10/10 on `numeric_comparison`, guard firing 10/10. (b) My rationale for
  `routable_acc` — "canary rewards guessing, penalizes the honest abstainer" — is FALSE:
  the ceiling organism abstains, emitting `selected_answer=None` with zero scorers firing.
- **The ceiling is substantially self-inflicted.** Apollo v1's `PRIMITIVE_CATALOG` held 25
  primitives *identical* to the forge library (intersection 25, none missing). **My v2
  rewrite dropped all of it.** Three of the four unsolved categories already have a
  primitive there. Only `vacuous_truth` does not.
- **Doctrine changed.** No claim is ever ESTABLISHED; terminal state is UNKILLED. Attacks
  count as *families*, never attempts. Claims that favour the lane require 3 distinct
  families. Age weakens a claim. Every experiment below is written to produce an
  interpretable **negative**, and each carries its own kill condition.

## 2. The ten

Each: the question, the case, the pre-committed outcome, cost, and **my honest prior** —
stated so the reviewer can attack the prior, not just the design.

---

### E1 — Static hazard & commutativity map
**Question.** Which operator pairs actually conflict (write-write, read-after-write), and
does the conflict graph collapse the ordering space into equivalence classes?

**The case.** The write-write hazard that invalidated *two* O1 runs was statically derivable
from the `@blackboard_op` declarations Apollo already had — both invalid runs were
preventable without executing anything. Worse, O1's exhaustiveness claim rests on sampling
48 orderings from subsets that have up to 166,320. **If most pairs commute, the distinct
orderings collapse to a small number of equivalence classes and O1 becomes genuinely
exhaustive rather than sampled** — which is the difference between "no better pipeline was
found in 1.74M samples" and "no better pipeline exists."

**Pre-committed.** Success = every ordering-sensitive pair identified statically, and O1's
sampled coverage re-expressed as a fraction of equivalence classes. **Failure that matters:**
if the collapse shows O1 sampled <50% of classes at k≥8, **the ceiling claim is downgraded
from measured to conjectured** and E2/E3 must wait for a re-run.

**Cost.** Hours. **Prior:** 0.85 that it materially tightens O1; 0.2 that it downgrades it.

---

### E2 — Reconnect the severed v1 library and re-enumerate
**Question.** Does 0.833 move when the 25 dropped v1 primitives are available?

**The case.** This is the single largest threat to O1's headline, and it comes from another
seat's measurement of my own code. If three of four unsolved categories already have a
primitive that my rewrite discarded, then "expressivity ceiling of the substrate" is a claim
about my amputation, not about the representation.

**Pre-committed.** Port only the three matched primitives (`all_but_n`, `temporal_order`,
`check_transitivity`/`solve_constraints`), **labelled PORT, never reportable as synthesis**.
If the ceiling moves ≥ +4.17% (one category), O1's FINDINGS.md is corrected to "ceiling of
the v2 registry" and the substrate claim is retracted. If it does *not* move, that is
stronger evidence for a real representational limit than O1 alone provided.

**Counterfeit risk, named by Aporia:** asked to mint `all_but_n`, the forge would *retrieve*
rather than synthesize — ΔE moves as predicted, provenance checks out, every acceptance
criterion satisfied by reconnection dressed as acquisition. Mitigation: this experiment is
labelled PORT in advance and may never be cited as evidence of minting.

**Cost.** ~1 day. **Prior:** 0.7 the ceiling moves.

---

### E3 — "Solved for the right reason" audit
**Question.** For each of the 100 solved tasks, is it solved by the intended derivation, or
by a regularity we authored in without noticing?

**The case.** This is my own named blind spot, recorded in the claim registry as one no
instrument we own can address: *the battery is ours, so an authored-in regularity is
invisible to every check we have.* A trivial "longest candidate" heuristic already scores
0.342 against chance 0.25, so the battery demonstrably leaks something.

**Method.** Derivation-preserving perturbation: rename entities, permute candidate order,
change numeric values, paraphrase templates — each preserving the intended reasoning path.
A task solved for the right reason survives; one solved by surface regularity does not. One
perturbation dimension is *already pre-tested and clean*: candidate-order permutation via
`PYTHONHASHSEED` moved the dumb heuristics (0.325–0.358) but left organism accuracy at
0.8333 across 8 seeds.

**Pre-committed.** If >10% of solved tasks fail derivation-preserving perturbation, **0.833
is retracted as a capability number** and restated as a battery-artifact-contaminated
number.

**Cost.** ~half a day. **Prior:** 0.35 that >10% fail. **This is the highest-information
experiment on the list because it can invalidate everything below it.**

---

### E4 — ΔE_port: `all_but_n`, end to end, labelled PORT
**Question.** Does the full pipeline — type adaptation, guard composition, enumeration,
provenance — carry one adapted primitive from library to measured ceiling movement?

**The case.** Aporia's corrected ladder, rung 1. It exercises every joint at once on the
easiest possible case, which is exactly what a first coupling should do. It is *not* a
synthesis test and must never be reported as one.

**Pre-committed.** Ceiling 0.8333 → 0.8750 (+4.17%) if one category is fully covered.
Anything less means the coupling, not the primitive, is the limiter.

**Cost.** ~half a day given E2. **Prior:** 0.75.

---

### E5 — ΔE_reason: `vacuous_truth`, the only true synthesis site
**Question.** Can a capability be produced where no existing primitive can be retrieved?

**The case.** `vacuous_truth` (false antecedent) is the **only** one of the four unsolved
categories with **no forge match**. Every other target admits counterfeit-by-retrieval. This
is therefore the only place on the board where minting must actually be minting — and
Aporia inverted its own prior argument to make it the target rather than avoid it.

**Pre-committed.** Success = +4.17% with the new primitive load-bearing under ablation AND
absent from the v1 catalog, forge library, and every prior Apollo registry (mechanically
checked, not asserted). Failure = the interesting one: it tells us synthesis is the binding
constraint, not arrangement.

**Cost.** ~1 day. **Prior:** 0.4. **The most decision-relevant experiment on the list.**

---

### E6 — Macro ratchet `[LEXIS-ADJACENT]`
**Question.** Does freezing a discovered load-bearing sub-chain as an atomic primitive make
a *later, harder* problem cheaper to reach?

**The case.** The reviewer previously called this the only result that would justify real
compute: *"something Apollo discovered yesterday became a primitive that let Apollo discover
something harder tomorrow."* I agree it is the qualitative step.

**Honest prior-lowering evidence I went and found.** The library-learning literature reports
that compression-driven primitive acquisition **helps less than expected in domains that
were not designed around elementary composable primitives** — and Apollo's battery was not
so designed. DreamCoder-line systems also cost ~2 CPU-months per domain. So I expect a small
or null effect here, and I want that on record *before* running it.

**Pre-committed.** Success = search cost to a held-out harder target drops ≥30% with the
macro available vs without, over ≥5 seeds. Null result is publishable and expected.

**Cost.** ~1 day. **Prior:** 0.25.

---

### E7 — Transfer to an unseen battery `[LEXIS-ADJACENT]`
**Question.** Does a primitive or macro learned on battery A reduce search cost on a battery
authored independently?

**The case.** This is the stated cloud-spend precondition: without transfer, more compute
buys more lottery tickets on isolated spikes rather than a compounding vocabulary.

**Caveat I am raising against my own source.** Lexis reports cross-domain transfer as
"unreported across all four families (~20 systems)." My own search found ARC-AGI
out-of-distribution work and top-down library synthesis that at least touch it. **I would
not build a cloud-spend argument on the "unreported" claim without verifying it.**

**Pre-committed.** Success = ≥30% search-cost reduction on the unseen battery. Only
meaningful if E6 produced a macro at all.

**Cost.** ~1 day, gated on E6. **Prior:** 0.15.

---

### E8 — O2: behavioural archive descriptor
**Question.** Does re-keying MAP-Elites on the solved-task signature raise *behavioural
coverage per 10,000 evaluations*?

**The case, and its demotion.** This was the pre-committed next step out of O1. **O1's
ceiling result demoted it:** 0.833 is expressivity-bound, so a better descriptor cannot
raise the score. It is now instrument hygiene — does the archive index capability or
syntax — not a capability experiment. I am listing it low deliberately and inviting the
reviewer to overrule me.

**Pre-committed.** Success = behavioural coverage per 10k evals materially increases. **Not**
cell count, **not** archive size — those inflate by construction.

**Cost.** ~half a day. **Prior:** 0.5 for the hygiene claim, ~0 for any score movement.

---

### E9 — Independent battery
**Question.** Does 0.833 survive on tasks Apollo's owner did not author?

**The case.** RC6 said the benchmark is small, saturated, partly gameable, and *ours*. E3
tests whether solves are for the right reason on *our* tasks; E9 removes us from authorship
entirely. Another seat authors held-out tasks in all seven categories — four unsolved, three
solved — **blind to Apollo's registry**, and Apollo is scored once.

**Pre-committed.** Success = per-category accuracy within ±0.15 of the home battery.
**Failure = the most valuable outcome on this list**: it would mean 0.833 measures our task
authorship, not Apollo's capability, and it would retroactively discount every number in the
corpus.

**Cost.** ~half a day of Apollo's time; requires another seat's cooperation. **Prior:** 0.45
that at least one category degrades materially.

---

### E10 — Can an LLM perform the widening-diagnosis step?
**Question.** Given only plateau telemetry, can a model name the missing capability class —
the step a human/agent performed 5 times out of 5?

**The case.** This is the epistemology question the fleet is on, made gradeable. Apollo owns
a **26-wall corpus with ground-truth causes** across four failure classes plus two controls,
already built and firewalled (cause-only oracles; the fix quarantined). Apollo also has an
unusually clean natural experiment on *loop depth*: an LLM in the **inner** loop (Granite,
2,152 mutations) produced **zero** lift, while an LLM in the **outer** loop supplied **all
five** widenings. The 5/5 result has been read as "human beats system." It is not — **all
five were supplied by an LLM.** The variable that predicts contribution is not LLM-vs-not,
it is *where in the loop, at what cadence, with what tools and reflection depth*.

**Pre-committed.** Baseline = chance over four classes (0.25) plus the control. Success =
significantly above chance out-of-sample on held-out walls, with the fix-quarantine intact.
Failure = the diagnosis step is not recoverable from telemetry alone, which converts my W1
roadmap item into a dead end and is worth knowing.

**Cost.** ~half a day, free-tier or local model only. **Prior:** 0.5.

---

## 3. Priority order, with the logic

**Ordering rule:** cheapest kills of the largest claims first; then the capability ladder;
then instrument hygiene. An experiment that can invalidate a downstream experiment must run
before it.

| # | Experiment | Why here | Cost | Prior |
|---|---|---|---|---|
| 1 | **E3** right-reason audit | can invalidate 0.833 outright; everything below assumes it | 0.5 d | 0.35 |
| 2 | **E1** hazard & commutativity | decides whether O1 is exhaustive or sampled; prevents the bug class that voided two runs | hours | 0.85 |
| 3 | **E2** reconnect severed library | largest threat to the ceiling's *scope*; gates E4/E5 | 1 d | 0.7 |
| 4 | **E9** independent battery | removes us from authorship — the deepest confound | 0.5 d | 0.45 |
| 5 | **E4** ΔE_port | end-to-end coupling on the easy case; counterfeit control | 0.5 d | 0.75 |
| 6 | **E5** ΔE_reason | the only true synthesis site; most decision-relevant | 1 d | 0.4 |
| 7 | **E10** LLM diagnosis | the epistemology question, gradeable, corpus already exists | 0.5 d | 0.5 |
| 8 | **E6** macro ratchet | the qualitative step, but literature lowers the prior | 1 d | 0.25 |
| 9 | **E7** transfer | cloud precondition; meaningless unless E6 fires | 1 d | 0.15 |
| 10 | **E8** behavioural descriptor | demoted by the ceiling result to hygiene | 0.5 d | 0.5 |

Total ≈ 7 days of work against a 48-hour budget, so **the first five are the realistic
run** and 6–10 are the queue. I would rather run five properly than ten badly.

## 4. Questions for the reviewer

1. **Is the ordering right?** Specifically: should E9 (independent battery) outrank E2
   (severed library)? E9 attacks a deeper confound but needs another seat; E2 is mine alone.
2. **E5 vs E6** — if only one of the two "can it acquire capability" experiments runs, which?
   E5 tests synthesis where retrieval is impossible; E6 tests whether acquisition compounds.
3. **Is E8 correctly demoted?** I argue the ceiling result makes it hygiene. Overrule me if
   a behavioural descriptor does something I have not credited.
4. **Is E10 a real experiment or a category error?** Asking a model to diagnose from
   telemetry may just measure how legible I made the telemetry.
5. **The eleventh experiment.** What is missing? Assume I am inside a monoculture — the same
   agent, the same substrate, four months.
6. **Which of these cannot produce an interpretable negative?** Any such item should be cut,
   not fixed.

## 5. Already dead — do not re-propose

Run-it-longer (ceiling at ~130 generations of 800). LLM-as-inner-loop-mutator (2,152
mutations, zero lift, pre-registered kill fired). "Composition is emerging" (0/5 elites beat
the best single primitive). Archive cell counts as a discovery signal (2,846 "shapes" ≈ 5
capabilities). More primitives as a general answer (every wall since has been assembly,
wiring, or measurement). Boolean primitive for canary (VOID — it exists and routes 10/10).

## 6. Standing epistemic conditions on all ten

Every experiment is preregistered before code exists. Every positive result starts at **one
kill-path family of three** and is `UNDER-ATTACKED`, never established. Any result that
favours Apollo gets a mandatory independent attack before write-up — today's O1 produced two
false wins for Apollo and both were caught only by continuing to attack a favourable result.
Wall-clock and engineering cost are reported alongside evaluation counts, because the
evaluation metric flatters the incumbent.
