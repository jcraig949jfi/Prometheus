# Pass 8 — the wider survey: four families, and the claim it overturns

**Date:** 2026-08-24
**Scope:** the operator asked for other similar tools. Passes 1–7 tracked a single lineage. There are
**four**, and they are only partly aware of each other. Full citations in `SOURCES.md`.

---

## 1. The map, corrected

What passes 1–7 called "the lineage" is one of four families working the same problem.

### Family A — Library learning from program corpora (MIT)
DreamCoder (2020) → LAPS (2021) → Stitch (POPL 2023) → LILO (ICLR 2024). Typed lambda calculus,
compressivity as the selection criterion, task-oracle verification. This is the family passes 1–7
studied.

### Family B — E-graphs and equality saturation (UW PLSE — Willsey, Nandi, Tatlock)
`egg` → Ruler (OOPSLA 2021) → babble (POPL 2023) → Enumo (OOPSLA 2023); ShapeCoder (SIGGRAPH 2023)
sits adjacent. **This family is more relevant to Prometheus than Family A and passes 1–4 saw only one
member of it.**

- **Ruler** infers *rewrite rules* from a grammar and interpreter — 5.8× smaller rulesets, 25× faster
  than a CVC4-based comparator. It learns the theory.
- **babble** does library learning *modulo* a theory.
- **Enumo** makes theory exploration programmable, and its "fast-forwarding" algorithm handles
  domains **where equality is undecidable**. An Enumo program synthesized a ruleset deriving 90% of
  Halide's handwritten rules.
- **ShapeCoder** discovers abstractions from **unstructured primitives** using e-graphs plus a
  conditional rewrite scheme — the closest published setting to "we have a pile of forge tools, not
  a clean DSL."

**Why this matters concretely.** Pass 5 derived Apollo's commutativity theory *by hand* from the
`@blackboard_op(reads=…, writes=…)` declarations. **Ruler is the tool that infers such theories
automatically**, and Enumo is the tool for guiding that inference when the space is large. The
composition Ruler → babble is a single research group's stack, not a mashup. Pass 4's recommendation
("babble, not Stitch") was right and incomplete: the full recommendation is **Ruler/Enumo to obtain
the theory, babble to abstract modulo it.**

### Family C — Theory exploration in theorem proving (Chalmers — Johansson, Smallbone, Claessen)
QuickSpec → Hipster (CICM 2014) → Lemmanaid → Twitch (2026). Twee is Smallbone's prover.

This family has been doing *vocabulary growth in mathematics* since before DreamCoder, from a
completely different direction: conjecture lemmas, test them, prove them, add them.

**Twitch is where Families A/B and C meet** — Chalmers theory-exploration people picking up MIT/UW
abstraction machinery (Stitch). That is what makes it the interesting 2026 node, and passes 1–3
described it without noticing it was a *junction* rather than a descendant.

### Family D — LLM tool and skill libraries
LATM (ICLR 2024) → Voyager (2023) → TroVE + its compute-matched refutation (2025) → ReGAL (ICML 2024)
→ DreamProver (2026). Newer, noisier, closest in shape to the Prometheus forge.

---

## 2. The correction: criterion 5 is not unoccupied

Passes 3, 6 and the deliverable all claimed that Prometheus's admission criterion —
**verifier-gated correctness from a typed diagnosis** (H2 precondition 3, W3-shaped: *"model writes a
small verified primitive from a typed diagnosis"*) — is "unoccupied in that lineage."

**That is wrong, and it has been wrong since 2014.**

**Hipster runs in two modes.** Exploratory mode generates basic lemmas about a new theory — that is
corpus-style exploration. But *proof mode* **discovers the missing lemmas that would allow the
current goal to be proved.** That is goal-directed vocabulary growth: not "what compresses the
corpus" but "what abstraction do I need to get past *this specific wall*." It is the same shape as
W3, twelve years earlier, in a proof assistant.

**Lemmanaid sharpens it further.** An LLM generates a lemma **template** — the *shape* of the lemma —
and symbolic methods fill in the details. That is precisely the division of labour W3 proposes: the
model supplies the structural guess from a diagnosis, the verifier supplies the guarantee. It is
built, and it is evaluated on Isabelle's libraries.

**And ReGAL occupies the verification half.** It refactors programs into candidate abstractions and
**iteratively verifies and refines them via execution** — admission gated on the abstraction actually
working, not on how much it compresses.

**What survives of the "ours" claim.** Not the criterion. What remains distinctive is narrower and
should be stated that way: *applying* goal-directed, verifier-gated primitive synthesis **to a
failure corpus of 132M verdict-labelled records with an exact oracle across heterogeneous
mathematical catalogs.** Hipster's proof mode operates on one goal in one Isabelle theory; Lemmanaid
on Isabelle libraries. The mechanism is theirs. The corpus is ours. That is Diomedes' formulation
again, and it has now survived eight passes and been strengthened by every attempt to find something
else.

---

## 3. The forge, re-read against Family D

Pass 7 found the forge's ratchet was measured at 0% primitive usage. Family D makes the diagnosis
sharper.

**LATM separates tool-maker from tool-user.** A powerful model crafts a reusable Python utility from
demonstrations; a *separate* model then applies it, with tools cached and reused across instances
(up to 79% per-instance cost reduction). **The forge is a tool maker with no tool-user role.** T2 and
T3 are nominally the consumers, but they are the same forging process pointed at a bigger primitive
pool, not a distinct role whose success depends on using what exists. 0% usage is what "no tool user"
looks like.

**Voyager closes the loop the forge leaves open.** Its skill library is admitted by
**self-verification of task success**, retrieved by relevance when a new task arrives, and driven by
an automatic curriculum that decides what to attempt next. Three components — curriculum, library,
verification — and the forge has a partial version of exactly one of them (Nous is a curriculum over
*concepts*, not over *capability gaps*). Results: 3.3× unique items, 15.3× faster tech-tree progress.

**ReGAL names the forge's failure mode in its own abstract:** *"LLMs lack the global view needed to
develop useful abstractions; they generally predict programs one at a time, often repeating the same
functionality."* The forge's Gate B (structural novelty) is an attempt to fix the *repetition* half
of that sentence by penalising sameness. ReGAL fixes the *global view* half instead, by refactoring
across a set of programs. **Those are different interventions on the same problem, and the forge
picked the one that forfeits usage guarantees** (pass 7 §3).

---

## 4. Sixth admission criterion, now that the survey is complete

Adding to the five in `SIDE_BY_SIDE.md` §3:

6. **Self-verified task success, with relevance retrieval** — Voyager. A skill enters the library
   because the agent verified it accomplished something, and is pulled back out by similarity to a
   new task. Neither compression nor diagnosis: *did it work, and is it relevant now.*

And criterion 5 must be re-attributed: **goal-directed verifier-gated synthesis is Hipster's proof
mode (2014) and Lemmanaid**, not a Prometheus original.

---

## 5. What no family has

Unchanged by this survey, and now checked against four families rather than one:

**Cross-domain transfer of discovered primitives.** DreamProver trains a library per domain.
Twitch restricts domains to a single TPTP theory with shared symbols. Voyager is one world. ReGAL
reports per-dataset libraries across five datasets but the claim is that libraries help *within*
each. LATM caches tools per task type. Family B infers rulesets per grammar.

Nobody transfers a learned vocabulary into an unfamiliar domain and shows reduced search cost there.
Eight passes, four families, ~20 systems. **This is the field's open frontier and it is the stated
cloud-spend precondition.** That coincidence is the single most decision-relevant fact this study
produced, and it has now survived a deliberate attempt to falsify it by widening the search.

---

## 6. Honest limits of this pass

Most Family B, C, and D entries are **[secondary]** in `SOURCES.md` — read from abstracts and search
summaries, not full texts. Specifically unverified:

- Hipster's proof mode: I have its description, not its algorithm, success rates, or scope limits.
  **The §2 correction rests on a secondary source.** It is strong enough to withdraw an
  over-claim — the correct response to "someone may already occupy this" is to stop claiming
  novelty — but it is not strong enough to build on.
- Ruler's applicability to a *state-mutating* operator set is assumed by analogy, not established.
  It infers rules over a grammar and interpreter; whether blackboard operators can be presented that
  way is unexamined.
- Voyager, ReGAL, LATM numbers are all from search summaries.

**Nothing in this pass should be quoted as measured until the underlying paper is read.**
