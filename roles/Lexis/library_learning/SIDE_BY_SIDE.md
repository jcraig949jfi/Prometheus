# Library learning: the neighbours vs Prometheus — consolidated side-by-side

**Date:** 2026-08-24 · **Passes 1–7** · Study only; no Apollo/Hephaestus code or plans were changed.

This is the deliverable. Passes 1–5 in `notes/` are the working record, including every claim I made
and later withdrew — §9 lists those explicitly.

---

## 1. The two programs, honestly stated

**The neighbours.** A five-year lineage, mostly out of MIT with a POPL/PL-theory wing and now two
2026 descendants in mathematics. The loop: solve problems → mine recurring structure from the
solutions → intern it as a named primitive → search again in the enlarged language. The
representation is typed lambda calculus over an explicit DSL. The corpus is *solutions*. The
verification is a task oracle (I/O examples, or a proof assistant). They have a working, published,
reproduced ratchet.

**Prometheus.** A failure-first program. The corpus is 132M verdict-labelled operator applications
with an exact oracle, 99.81% of them REJECTED. The representation is a state-mutating pipeline over
a semantic blackboard, or a forge-generated Python tool.

**Two halves, and they differ.** *Apollo has no ratchet* — `apollo/src/genome.py` says it in its own
docstring, *"primitives are fixed atoms"* — and O1 measured what that costs: 0.833 is the substrate's
ceiling, exhaustively, with 16.7% of its own battery unreachable in the vocabulary regardless of
search. *The forge does have one*, and says so: **"The forge is an evolutionary ratchet. Each tier's
output becomes the next tier's primitives."** T1 forges from scratch; T2's primitives are all passing
T1 tools; T3's are all passing T1+T2 tools. That is the DreamCoder recursion, built here
independently.

**The one-line comparison.** They grow the language and search it. Apollo searches a fixed language
very carefully and has just proved the language is the binding constraint — while the forge grows a
language whose promoted primitives, when last measured, went unused.

---

## 2. Component-by-component — the digital model

**The library itself.**
*Them:* DreamCoder's `Grammar` — `Primitive` and `Invented` programs with numerical weights, i.e. a
probability model over a DSL. It is simultaneously the vocabulary and the search prior. DreamProver's
is a curated set of Lean lemmas, capped under 100, LRU-evicted.
*Us:* the forge tool registry and the 27-operator blackboard set. Flat, unweighted, human-authored,
and fixed at runtime. No component promotes anything into it.

**The abstraction finder.**
*Them:* Stitch (Rust, POPL 2023) — corpus-guided top-down synthesis, 3–4 orders of magnitude faster
and 2 orders less memory than DreamCoder's own compression, per-abstraction arity/utility/usage
output. babble (POPL 2023, different group) — the same job modulo an equational theory, using
e-graphs and anti-unification.
*Us:* **nothing.** `apollo/src/gene_extractor.py` is the only candidate and it inverts the logic
(§9, correction 2).

**The proposer / search.**
*Them:* type-directed enumeration over the weighted grammar, guided by a neural recognition model
trained on real *and* dreamed tasks; LILO swaps in an LLM; DreamProver uses LLM sketching.
*Us:* deterministic mutation plus 30% crossover, MAP-Elites archive keyed on syntax. LLM mutation
tried and killed (llm2: 2,152 mutations, zero lift) — but see §9, correction 3.

**The verifier.**
*Them:* I/O examples (DreamCoder, LILO), Twee (Twitch), Lean+Mathlib (DreamProver). Compression runs
over an *already-verified* corpus in every case.
*Us:* exact oracle over the catalogs; forge battery; blackboard `_evaluate_acc`. Comparable rigour —
arguably better, since our oracle is exact rather than example-based.

**The failure channel.**
*Them:* Twitch mines failed partial proofs — scores derived lemmas by `s(l=r) := |T(l=r)| / |l=r|²`,
i.e. simple statements with long proofs, takes top k=50–100, feeds to Stitch. DreamProver routes
failed direct proofs into sketch → `sorry`-hole extraction → standalone intermediate theorems →
verification → library.
*Us:* the 132M-record REJECTED corpus, and the doctrine that failure is metabolized rather than
consumed. **Vastly more failure data, no mechanism that turns it into vocabulary.**

**Documentation.**
*Them:* LILO's AutoDoc names and docstrings each discovered abstraction from usage examples; the
documented library feeds back as **few-shot context for the synthesizer**, and the paper's claim is
that this improves performance, not just readability.
*Us:* nothing — and per §9 correction 4, it would not currently help.

---

## 3. Admission criteria — what actually gets into a library

Five distinct answers exist. This is the sharpest axis of comparison.

1. **Compressivity** — DreamCoder, Stitch, babble, LILO. Corpus cost improvement; MDL/Bayesian
   justification. Corpus-*relative*.
2. **Measured speedup on the target** — Twitch's `τ` re-verification threshold. A reachability proxy.
3. **Semantic clustering + verified provability under a small sampling budget + non-duplication by
   tree edit distance, LRU eviction, hard cap under 100** — DreamProver. Not compression at all: a
   curated bounded working set.
4. **LLM-judged conceptual salience over high-performing hypotheses** — LaSR (NeurIPS 2024).
   Natural-language concepts, no formal compression criterion.
5. **Verifier-gated correctness from a typed diagnosis** — Prometheus H2 precondition 3, W3-shaped.
   Untested locally; unoccupied in that lineage. Note it is *generative* — it governs how a candidate
   is produced, not merely which survive.

**The finding that killed the framing this study started with:** the field is not monolithically
compression-selected. Both mathematics-facing nodes — Twitch and DreamProver, both 2026 — moved off
compressivity independently, in the same year. "They compress yesterday, we reach tomorrow" was a
clean story and it is not true.

---

## 4. What they have settled that we have not

- **A working ratchet.** Discovered structure becomes vocabulary, recursively, and demonstrably
  improves later search. DreamProver: 58% of learned lemmas reused on test sets, contributing to
  proofs of 71% of all theorems it proved; +61% average over baseline; 48% fewer output tokens.
- **Cheap abstraction extraction.** Stitch made the expensive step 3–4 OOM cheaper. Off the shelf.
- **Failure-to-vocabulary conversion.** Both 2026 nodes do it. We have the doctrine and the corpus
  and no mechanism.
- **The discipline of naming.** LILO's demonstration that documentation is load-bearing for reuse.

## 5. What we have that they do not

- **The corpus.** 132M verdict-labelled records, failure-dense, cross-catalog, exact oracle. Twitch's
  comparator is 1,041 TPTP UEQ problems. Nobody in this lineage has an equivalent. *This is an asset
  claim about data, not a novelty claim about method* — Diomedes' formulation, and it survives six
  passes.
- **Ceiling measurement by construction.** O1 is unusual and good practice: exhaustive enumeration
  establishing that a plateau is representational rather than algorithmic. I have not found an
  equivalent in the lineage.
- **A generative admission criterion** (§3.5), if it can be made to work.
- **Adversarial discipline as standing practice.** O1 archived two invalid runs that would have
  produced a *false win for its own hypothesis*, and published the standing lesson. The field's own
  TroVE re-evaluation (§6) shows this is not universal over there.

## 6. What neither has — and it is the thing that decides spend

**Cross-domain transfer of discovered primitives.** DreamProver does not report it; each domain gets
its own dedicated library. Twitch's own limitation section says domains are "restricted to the same
TPTP theory with shared symbols." DreamCoder's compositional libraries are within-domain.

The operator's stated cloud-spend precondition — *structures discovered in earlier environments
become inherited primitives that reduce search complexity in later unfamiliar environments* — is
**unproven anywhere in this literature.** That cuts both ways:

- It is the strongest argument that this contact is worth more than a reading list. We would not be
  reinventing a solved thing; we would be entering the field's own open frontier with an unusual
  asset.
- If four labs over five years have not produced it, the prior that we get it by pointing a tool at
  our corpus should be low.

**And the field has already run the relevant negative control.** *A Compute-Matched Re-Evaluation of
TroVE on MATH* (2025) equalized budgets and found the library-induction advantage on MATH does not
survive; the gains were artifacts of unequal compute. **Any Prometheus library-learning result is
uninterpretable unless the no-library arm gets matched compute in a currency fixed before the run.**
O1 already models the right discipline — it chose organism-evaluations as the comparator and stated
openly that the metric flatters evolution while the engineering-cost comparison does not.

---

## 7. The tool-fit result, and its limit

**Stitch is the wrong tool for Apollo pipelines.** It consumes lambda terms with de Bruijn indices
and prunes by syntactic pattern matching. An Apollo pipeline is a state-mutating operator sequence.

**babble is the architecturally right one**, and pass 5 quantified why. A static audit of all 26
declared blackboard operators found **zero undeclared writes** (one undeclared *read*, in
`select_nth`), so a commutativity theory derived from the `@blackboard_op(reads=…, writes=…)`
decorators via Bernstein's conditions is sound. Over the ten transformers of O1's ceiling pipeline:

> **39 of 45 operator pairs commute freely. Only 6 are order-dependent.**

The six are the semantic spine — `counts`, `facts`/`rules`, `derived_facts`, and two paths into
`relations`. The sixth is the write-write hazard between `parse_names_and_relations` and
`relations_from_facts` — **exactly the bug that invalidated two of O1's runs**, and statically
derivable from metadata that was already in the tree. O1 sampled 48 orderings per subset against
166,320 because it treated ordering as opaque; enumerating equivalence-class representatives would
have been complete rather than sampled.

**The limit, held firmly.** All of this makes search over the *same bounded space* cheaper and more
complete. A better abstraction tool over a substrate whose ceiling is 0.833 by construction still
cannot exceed 0.833. Raising the ceiling requires growing the operator set, and none of this
machinery does that on its own. It is easy to let a good tool-fit result feel like progress toward
the goal; it is not.

---

## 8. Crossover vs decomposition — the answer to Apollo §9.2

Apollo asked what class of problem would justify evolution over enumeration or synthesis. The
comparison with DreamProver answers it sharply, because both are attempts to cross a valley single
edits cannot.

- **Apollo's crossover** is a *search operator over a fixed vocabulary*. It jumps far enough to land
  on a spike in a gradient-free landscape. RC1's own reading: a workaround for a landscape with no
  slope. Nothing it produces enlarges what is expressible.
- **DreamProver's recursive decomposition** takes a *failed* proof attempt, has the LLM produce a
  sketch, extracts the unproven `sorry` holes as standalone intermediate theorems, LLM-validates
  them, formally verifies, and **admits them to the library** — where they persist and are reused.
  When decomposition fails, the failure informs the next wake-sleep cycle rather than triggering a
  retry with more budget.

Same purpose, different level. Crossover jumps *within* a vocabulary; decomposition grows the
vocabulary *from a failure*. That is RC7 and O1's ceiling, restated as a mechanism the neighbours
already ship — and it is failure metabolization, our own doctrine, implemented.

---

## 9. Corrections ledger — claims made in this study and withdrawn

Recorded because a study that quietly patches itself is not a record.

1. **Pass 1/2: "compression of yesterday vs reachability of tomorrow" is the delta.** Withdrawn in
   pass 3. Both 2026 mathematics nodes had already left compressivity; the framing overstated a gap
   the field's frontier had closed.
2. **Pass 3: `gene_extractor.py` contains the O4 macro mechanism already.** Withdrawn in pass 4 after
   reading it. `compute_portability_score` is a corpus-blind anti-overfitting filter on source text,
   and the macro branch fires *because a tool scores badly* — bundling what cannot be decomposed.
   Library learning promotes structure because it recurs and pays for itself. Opposite selection
   pressure, same word.
3. **Pass 1: llm2's zero-lift result might be explained by a flat landscape.** Refined in pass 2 to
   something sharper and better evidenced — llm2 mutated a flat list of operator names, so it could
   only reorder existing operators. It tested LLM-as-arrangement-mutator, never
   LLM-as-primitive-author. H2 precondition 3 cites it for a claim about *menu growth* on a substrate
   where the menu cannot grow. The conclusion may hold; that evidence does not reach it. (The canon's
   own parenthetical already marks the W3 alternative "untested, not falsified" — the doctrine is
   more careful than its headline clause.)
4. **Pass 1: AutoDoc is the cheapest available steal.** Withdrawn this pass. AutoDoc's payoff channel
   is few-shot context for an **LLM synthesizer**. Apollo's search is deterministic mutation and
   crossover with no LLM consumer. Documentation of a library nothing reads buys nothing. It would
   pay in the forge, or in a W3-shaped "model writes a verified primitive from a typed diagnosis"
   loop — not in Apollo as it stands.
5. **Pass 2: the transfer experiment has positive prior art.** Withdrawn in pass 3. Within-domain
   reuse has prior art; cross-domain transfer does not (§6).
7. **Pass 6 deliverable: "There is no ratchet."** Withdrawn in pass 7. True of Apollo, false of the
   forge, whose tiered T1→T2→T3 design is the DreamCoder recursion built independently. The correct
   claim is narrower and more interesting: the forge's ratchet exists and its promoted primitives
   were measured at 0% usage.
6. **Pass 2: the C-vs-R experiment is the thing to run.** Withdrawn — it is not runnable on Apollo.
   `H` has no headroom: any macro built from the existing 27 operators is a re-expression of a
   pipeline already inside O1's enumerated space, so downstream gain on that battery is bounded at
   zero. A readout whose attainable range excludes the effect is not a readout.

---

## 9b. The forge half — the sharpest finding

`forge/ARCHITECTURE_T2_T3.md` §1, on why the previous T2/T3 ratchet failed:

> **Winning tools used 0% of their own primitive libraries — primitives were decoration.**

**Why compressivity would have prevented this, and novelty-gating invited it.** In the lineage, an
abstraction is admitted *because it already appears many times across the corpus* — that is what
compressivity measures. A promoted abstraction therefore cannot be unused: its usage is the evidence
that promoted it, observed before promotion. The forge admits on Gate A (beat the NCD baseline) and
**Gate B — structural novelty**, which explicitly rewards difference from the existing library:
*"a tool that scores 35% accuracy but uses Hebbian plasticity inside a model-checking BFS is more
valuable as substrate than a tool that scores 60% using the same regex pipeline everyone converges
on."*

Gate B is close to anti-compressive: it promotes what does *not* recur. Then the tool enters the
next tier's primitive pool with nothing connecting admission to subsequent use. 0% usage is the
predicted outcome of that design, and it is what was measured.

This is not a verdict that novelty-gating is wrong — it is a deliberate answer to monoculture, which
compression-gating would worsen, since compression rewards exactly the pipeline everyone converges
on. It is that **the two gates trade off on an axis nobody had named**, and the forge sits at the end
where unused primitives are the failure mode. Their libraries grow compositionally and narrowly; the
forge wanted diversity and got decoration.

**And the program already found the fix, independently.** `agents/hephaestus/STATUS.md`, recording
the 2026-06-22/23 reassessment: *"The forge succeeding" no longer means "pass a gate"; it means a
**consumer measurably improves because of your output, and that survives ablation.*** That is
held-out downstream gain as the admission criterion — the exact fix for 0% usage, and what the
neighbours actually report (DreamProver: 58% of learned lemmas reused, contributing to 71% of proofs).
Reached here in June 2026 from local failure analysis, two months before this contact. Unlike the
frontier-advisor's macro proposal — which is DreamCoder recalled without citation — this is genuine
convergence and should be counted as such.

**Where AutoDoc actually lands.** Pass 6 withdrew it as a steal *for Apollo*, which has no LLM
consumer of its library. The forge is nothing but an LLM consumer of a library — T2 forges ensembles
importing T1 tools, T3 composes T1+T2. Named, documented, usage-exemplified primitives are precisely
what a T2/T3 forging prompt needs, and "primitives were decoration" is the failure AutoDoc is
designed against. **This is the study's one cheap, concrete, well-evidenced steal, and it lands on
the forge, not Apollo.**

**Still absent on our side:** the compression step itself. Nothing mines recurring structure *out of*
the ~1,960-tool corpus. Every tier's primitives are whole admitted tools, never extracted
sub-structures. Stitch's entire job is the step the forge skips.

---

## 10. Bottom line

The contact is real and it is well-timed, but not for the reason it was first framed. It is not that
we found a field optimizing the wrong objective and can do better. It is that **we finished proving
our representation is the binding constraint one day before finding a five-year literature whose
entire purpose is growing representations** — and that the specific thing we would want from it,
cross-domain primitive transfer, is that field's open frontier too, not its solved core.

Three things follow that do not require a decision about Apollo's future:

- **Any library result here needs a compute-matched control**, in a currency fixed in advance. The
  field's own re-evaluation says so.
- **babble, not Stitch**, if this is ever attempted on the blackboard substrate — and the theory it
  needs is derivable today from declarations that already exist.
- **The interesting experiment is transfer, not compression.** Form structures on substrate A,
  measure search cost on unseen substrate B. It is the operator's stated spend precondition, it is
  unproven in the literature, and it is the only version whose positive result would mean something
  neither program has shown.
- **The cheapest actionable item is on the forge, not Apollo** — documentation plus usage exemplars
  on the primitive pool, against a measured 0%-usage failure, in the one place that already has an
  LLM consumer to read them. A babble deployment on Apollo's blackboard is more interesting and less
  useful: it is capped at 0.833 by construction.
