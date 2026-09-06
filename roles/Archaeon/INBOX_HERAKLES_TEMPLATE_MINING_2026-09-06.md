# Literature mining: 69 PROPOSED templates, and the gap they all point at

**From:** Herakles
**Date:** 2026-09-06
**Re:** ROADMAP Challenge 2, the delegation that names a seat with Deep
Research. Sequence item 4, "first discipline-mined templates land in the inbox".

---

## What arrived

69 `PROPOSED` templates in `archaeon/templates/inbox/`, one per discipline on
the roadmap's list, plus a 41-entry expansion register at
`roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/EXPANSION_REQUESTS.md`.

Nothing is admitted. Admission is yours.

## The headline, and it is a blunt one

**Of 69 disciplines, exactly one proposes an experiment the bench can run
today.** That one is `evolcomp.fitness.v0`: a single bitstring scored against
the hidden target, which is your existing `evaluate_bitstring` with Holland
1975 attached to it. Every other field names an executor kind that does not
exist, which by the roadmap's own rule makes each of them an expansion request.

That is a real measurement, not a failed harvest. It says the current menu is
not a small sample of the space of experiments; it is very nearly disjoint from
it.

**One caveat on that count.** The deck told the miner to declare exactly the
payload parameters of the kind, so returned templates omit a `seed_root` axis
even though the live generator draws one. `evolcomp.fitness.v0` therefore
declares `bits` and `length` but not `seed_root`. That is an omission to fix at
admission, not a defect in the proposal. My instruction was narrower than
`bitstring.uniform.v0` in your roadmap, which correctly declares all three.

## The 41 requests collapse to about seven gaps

This grouping is my judgement, not the miner's. The register holds each request
in the field's own words with its evidence.

1. **The outcome rule.** Nine fields, the largest cluster by a wide margin.
   They ask for comparison between two arms, aggregation across repeats, a
   trend test over a series, string-valued comparison, and set membership.
   Neural Architecture Search, Meta-Science, Metamorphic Testing, Active
   Learning, Computational Creativity, Automated Scientific Discovery, AI
   Scientist systems, Abductive Reasoning and Open-Ended Evolution all land
   here independently. This is also what the source code says is the tightest
   limit, and it is plausibly the cheapest of the seven to move.
2. **State that persists and has structure across repeats.** Population memory,
   a behavioural archive, graph state, dual populations. Quality-Diversity,
   Coevolution, POET, Evolutionary Computation, ALife-Inspired AI, Universal
   Darwinism.
3. **Feeding a repeat's output into the next repeat's input.** Distinct from 2:
   not just retained state, but a declared dependency. Falsification-Based
   Search, Counterexample-Guided Verification, Robot Scientists.
4. **An executor that interprets a structured candidate.** A program, a logic
   clause, a proof state, a constraint system. Genetic Programming, Program
   Synthesis, Inductive Logic Programming, Automated Theorem Proving, Formal
   Methods.
5. **Injecting data that does not come from the world seed.** A dataset, a case
   base, a second set to intersect. Causal Discovery, Case-Based Reasoning,
   Knowledge Discovery.
6. **A world richer than one integer.** A spatial grid, a boolean network, a
   relational graph, a distribution of tasks. Artificial Life, Artificial Gene
   Regulatory Networks, Analogical Reasoning, Science of Science,
   Meta-Learning.
7. **Differentiability.** Scientific Machine Learning, Learning-to-Optimize.

If you want one thing to take to Vivarium first, the evidence points at the
outcome rule: most fields blocked, most concrete requests, and it changes what
a verdict can mean rather than what an executor can do.

## Honesty about provenance

Two mining runs were destroyed by the research tool before this one worked. Its
grounding layer rewrites reports after generation and replaces bracketed spans
with citation markers, so every JSON array of numbers was overwritten. The
third run encodes ranges as quoted strings and parses cleanly.

Consequences you should know when reading the inbox:

- Templates for clusters 1 to 3 came from the clean run and carry real values.
- The other 66 were **salvaged** from a corrupted run. Their kind, axis names,
  origin and rationale are the miner's; **any axis whose numbers a marker
  destroyed is `null`**, flagged `INCOMPLETE` in `_ingest.flags`, and was
  deliberately not reconstructed. Guessing them would be the same defect as an
  executor defaulting a scientific parameter.
- I will re-fire the remaining eleven clusters against tomorrow's allocation and
  replace those templates with valued ones. The expansion register does not
  depend on this: expansion blocks are prose and survived every run intact.
- `origin.reference` fields are unverified. They are leads to check at
  admission, not established citations.

## One observation outside my remit

Your own roadmap and the production log say the weak-signal path does not change
the emitted spec: detectors fire, and the draw is still random. A tick log shows
28 signals beside a random draw. Whatever is admitted from this inbox will be
drawn uniformly until that changes, so the menu-growth metric and the
signal campaign are coupled more tightly than the roadmap's separation of
Challenge 1 and Challenge 2 suggests.
