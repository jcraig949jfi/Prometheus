# Pass 2 — Apollo crossmap: the ceiling O1 measured is the ceiling this literature exists to break

**Date:** 2026-08-24
**Trigger:** operator supplied Apollo's revival review (written 2026-08-23, *before* DreamCoder was
found) plus a frontier-advisor response to it. Both are reproduced in session context, not in-repo.
**New primary evidence read this pass:** `apollo/cycles/o1_enumeration/PREREGISTRATION.md`,
`FINDINGS.md`, and the two archived invalid runs.

---

## 1. O1 has already run, and its result reframes this entire study

Preregistered 2026-08-23 before the enumerator ran; stop rule ratified by James in advance.

**Verdict by the pre-committed rule:** `EVOLUTION_MORE_EFFICIENT`. Enumeration reached 0.833 but
needed **1,687,896** organism-evaluations against evolution's **3,144** — a 537× ratio. The kill
condition (enumeration reaching the ceiling in *fewer* evaluations) did not fire. Apollo survives O1
and proceeds to a bounded O2.

**But the finding that matters is the secondary one.** 1,737,000 type-correct pipelines were
enumerated in 3,000 s, and:

> Enumeration's ceiling is also exactly 0.833 — with an identical per-subset profile
> (canary 0.6 / synth 1.0 / inference 1.0 / cross_tier 1.0). Nothing in 1.74 million type-correct
> pipelines beats the organism evolution found. Not one.

Apollo's own reading, quoted:

> **So 0.833 is the substrate's ceiling, not evolution's.** The remaining 16.7% is not reachable by
> *any* pipeline in this representation — it is an **expressivity limit**, now measured by
> construction rather than inferred from a plateau.
>
> **No search improvement can pass 0.833.** … Any plan whose deliverable is "a better search" is
> capped before it starts.

Apollo also states its own honest counterweights: the enumerator is the dumbest possible baseline
(breadth-first, uniform 48-ordering sample, no pruning, no best-first), so 537× bounds evolution's
advantage over *unguided* search, not over *competent* search; wall-clock tells the opposite story
(brute force found the same organism in 50 minutes of laptop CPU with none of the four months of
engineering); and RC7 is untouched. Two invalid earlier runs — guard-tails capped at 3, orderings
capped at 4 — are archived rather than deleted, both of which would have produced a *false win for
evolution*.

---

## 2. The central connection

Apollo's genome is a flat ordered list over a **fixed 27-operator vocabulary**. O1 proved
exhaustively that no arrangement of that vocabulary exceeds 0.833. The ceiling is representational,
not algorithmic.

**The only way past a representational ceiling is to change the representation.** That is precisely
and exactly what "library learning" denotes in the DreamCoder lineage: discovered abstractions are
interned as `Invented` primitives, enter the `Grammar`, and become available for further composition
— recursively, so the language in which solutions are expressed grows with experience. DreamCoder's
abstract states the property directly: *"Concepts are built compositionally from those learned
earlier, yielding multi-layered symbolic representations."*

So the two documents describe the same wall from opposite sides:

- **Apollo, RC7 (representational closure):** "Every computational action available to the organism
  already exists in the human-designed operator set. Mutation can change which known operations
  occur and where. It cannot invent a new transformation."
- **DreamCoder's premise:** expertise means *acquiring the language*, not searching harder within a
  fixed one.

O1 is the measurement that converts RC7 from an analytic objection into a number: **16.7% of the
battery is unreachable in this vocabulary, by construction.**

This is a coincidence of timing, not of causation — O1 ran 08-23, Aporia surfaced DreamCoder 08-24.
But it means the literature contact arrived at the exact moment the program had finished proving it
needed what that literature sells.

---

## 3. Correction to Pass 1 §8.2 — the llm2 question is now settled, and differently than I framed it

Pass 1 asked whether llm2's "2,152 mutations, zero lift" was measured on a landscape where lift was
possible. Answer, from Apollo's review §2/§5 plus O1:

- llm2 mutated **the genome — a flat ordered list of operator names.** By construction it could only
  reorder, insert, remove, or swap *existing* operators. It could not author a new one.
- O1 then established that the maximum attainable by *any* arrangement of that vocabulary is 0.833.

Therefore llm2 tested **LLM-as-arrangement-mutator**. It did not, and could not, test
**LLM-as-primitive-author**. H2 precondition 3 in `aporia/doctrine/reasoning_ladder.md` cites it as
evidence for a claim about **menu growth**:

> The menu must grow — but in-loop LLM mutation is falsified (llm2: 2,152 mutations, zero lift), so
> admission must be verifier-gated…

The cited experiment operated on a substrate where the menu **cannot grow at all**. This is the
wrong-population pattern: a result measured on arrangement quoted as a property of vocabulary
growth. The verifier-gated conclusion may well be correct — but this evidence does not reach it.

**In fairness to the canon:** precondition 3's own parenthetical already marks the alternative as
"W3-shaped: model writes a small verified primitive *from a typed diagnosis* — **untested, not
falsified**." The doctrine is more careful than its headline clause. The fix is to stop citing llm2
in support of that clause, not to change the conclusion.

---

## 4. Option-by-option crossmap: Apollo's §7 against the neighbours' five years

**O1 — type-directed enumeration.** *Already run, and the lineage answered this question in 2020.*
DreamCoder's wake phase **is** type-directed enumeration over a weighted grammar, guided by a neural
recognition model. The lineage's settled position is that enumeration is the right substrate and the
open problem is *what you enumerate over* — hence library learning. Apollo's 537× result measures
unguided enumeration; DreamCoder never proposed unguided enumeration.

**O2 — behavioural archive descriptor.** *No analogue.* MAP-Elites and quality-diversity are absent
from this lineage entirely; DreamCoder keeps a `Frontier` per task, not an archive over behaviour
space. Nothing to steal here, and nothing in the literature contradicts it. Proceed on its own
merits as the bounded test already scheduled.

**O3 — give the landscape a slope.** *The lineage sidesteps this.* Because enumeration + learned
proposal replaces hill-climbing, no gradient is required. Worth noting that Apollo's own advisor
ranked O3 last for risk of self-deception ("manufacture a gradient and then congratulate evolution
for climbing the gradient you manufactured"). The literature's existence is an argument that O3 is
optional rather than necessary.

**O4 — macros / abstraction.** *This is the whole field.* Concretely available off the shelf:
- **Stitch** (`mlb2251/stitch`, Rust, POPL 2023) does exactly the "freeze load-bearing sub-chain into
  a named macro" operation, as corpus-guided top-down synthesis, at **3–4 orders of magnitude faster
  and 2 orders of magnitude less memory than DreamCoder's own compression step**. `--max-arity`,
  `--iterations`, per-abstraction arity/utility/usage-count output.
- **Recursive formation** — the property the advisor called the difference between compression and
  a real ratchet — is native to the lineage, not an extension of it. Inventions compose into further
  inventions.
- **LILO's AutoDoc** shows that *naming and documenting* a discovered abstraction measurably improves
  downstream synthesis, not just readability.

**O5 — change the search to fit the landscape.** *This is DreamCoder's architecture, roughly.*
"Type-directed synthesis for reachability plus quality-diversity over behaviours for coverage" is
DreamCoder minus QD, plus a learned recognition model and a growing library.

**O6 — replay/regression harness.** *No analogue; do it regardless.* Independent of this study.

**O7 — retire climber, keep instrument.** *Unaffected by the literature.* Still live.

---

## 5. An important caveat about the advisor's "independent" convergence

The frontier-advisor response re-derives, from Apollo's document alone, a macro mechanism with
declared typed inputs/outputs, frozen internals, atomicity under mutation, retained provenance, and
**recursive macro formation** — and calls that "the beginnings of open-ended vocabulary growth."

That is DreamCoder's mechanism, specified accurately, without citation.

Per `feedback_llm_convergence_is_gravity_amplifier`, this must **not** be counted as independent
validation. A frontier model reproducing a well-known published architecture from 2020 is corpus
gravity, not convergent discovery. It does not weaken the recommendation — the mechanism is
sound and the field has five years of evidence for it — but the recommendation's evidential weight
comes from **DreamCoder/Stitch/LILO's published results**, not from a second opinion having
independently arrived at it.

The same caution applies in reverse to any comfort taken from "two reviewers agreed."

---

## 6. What is genuinely ours after this pass

Narrowed from Pass 1's three-way split, now that the Apollo evidence is in:

1. **Verifier-gated admission from a typed diagnosis** (H2 precondition 3, W3-shaped). Untested
   here, and — as far as passes 1–2 can see — unoccupied in that lineage, whose admission criterion
   is compressivity over an already-verified corpus. Note this is a *generative* criterion: it
   governs how a candidate primitive is produced, not merely which survive.
2. **Failure-dense corpus with an exact oracle.** Twitch mines failed partial proofs, so the
   *instinct* is shared; but its corpus is Twee proof attempts on TPTP UEQ (1,041 problems). Ours is
   132M verdict-labelled operator applications across catalogs. Diomedes' framing holds: this is an
   asset claim about data, not a novelty claim about method.
3. **Reachable-ceiling measurement by construction.** O1 is exactly this, and it is real — but note
   what it actually is: an *exhaustive enumeration of a small fixed vocabulary on a 120-task
   authored battery*. It measured a ceiling; it did not measure `R(a)` for a candidate abstraction
   `a`. The machinery for scoring an abstraction by reachability gain **still does not exist**
   (Pass 1 §4 stands). What exists is one ceiling measurement for one fixed vocabulary.

---

## 7. Consequence for the C-vs-R experiment as originally proposed

The proposed experiment — measure `C(a)` compression gain, `R(a)` reachability gain, `H(a)` held-out
solve gain, and test whether `R` predicts `H` after conditioning on `C` — is **not runnable on
Apollo's substrate as it stands**, for a reason O1 supplies directly:

`H` has no headroom. The battery's attainable maximum in this representation is 0.833, measured. Any
abstraction `a` formed from the existing 27 operators is, by definition, a re-expression of a
pipeline already inside the enumerated space — so its downstream solve gain on this battery is
bounded at zero. You cannot measure whether reachability predicts future utility on a battery whose
future utility is provably exhausted.

**This is a gate-reachability failure of exactly the kind the program has logged before:** a metric
whose attainable range excludes the effect you intend to detect. Compute the attainable range before
designing the readout.

What *would* be runnable: form macros on substrate A, then measure search cost to reach solutions on
an **unseen substrate B** where the macro is useful but insufficient. That is the advisor's Pass-3
proposal, it is the transfer criterion the operator named as the cloud-spend precondition, and it is
the one experiment whose positive result exists in the literature already (DreamCoder's multi-layered
libraries; Twitch's domain abstractions transferring from easy problems to hard ones in the same
theory — ~25 more problems inside 300 s, runtime roughly halved).

---

## 8. Carried forward to pass 3

1. Reconcile the Twitch rating-1 vs rating ≥ 0.9 discrepancy (carried from pass 1, still open).
2. Pre-DreamCoder roots (EC / explore-compress) and side branches (LAPS; LaSR `arXiv:2409.09359`).
3. Stitch's cost/utility function from source rather than docs prose — needed to state precisely
   what `C(a)` is.
4. **Representation mismatch, the real engineering question:** Stitch consumes lambda-calculus
   corpora with de Bruijn indices. Apollo's genome is a flat op list over a semantic blackboard with
   ~25 named slots. What would it take to express Apollo pipelines in a form Stitch can compress —
   and does that translation preserve what makes them work? This is the concrete adoption question
   and no pass has touched it.
5. Citation graph: who else has taken Stitch into mathematics besides Twitch.
