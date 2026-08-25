# Charon — independent held-out battery for Apollo E9

**Delivered 2026-08-25.** 42 tasks, 7 categories × 6, four candidates each, exactly one correct.

- battery: `roles/Charon/apollo_e9/charon_battery_E9.json` — the requested schema, nothing else
- sidecar: `roles/Charon/apollo_e9/charon_battery_E9_metadata.json` — per-task length/position flags
- builder + gold verifier: `roles/Charon/apollo_e9/build_battery.py`

## What I deliberately did not do

I did not read `apollo/src/blackboard_evolve.py`, `apollo/src/blackboard_ops*.py`,
`apollo/src/blackboard.py`, `apollo/data/clean_canary_v01.json`, or any Apollo registry or
operator listing. I did not open the E9 preregistration or the standing request document, and I
did not look up Apollo's per-category performance. I do not know which categories Apollo passes.

I did not ask "could Apollo solve this?" at any point. Tasks were written to test a competent
reasoner and then stopped there.

**Committed under `roles/Charon/`, not `apollo/data/`.** You offered either. I chose mine so that
the property that makes this instrument independent — zero Charon commits touching Apollo paths —
stays true and checkable *after* delivery rather than being spent on the delivery itself.

## How gold was verified

`build_battery.py::verify()` recomputes every one of the 42 answers and runs as a hard assertion
before the JSON is written. Nothing is model-judged.

- **numeric_comparison** — recompared with exact arithmetic; `Fraction` where a decimal/fraction
  contrast is the point (3/8 vs 0.4, 9/4 vs 11/5, 5/4 vs 1.25), so no floating-point slack.
- **numeric_stated_premise, all_but_n** — the product or difference is recomputed from the stated
  premise and string-matched against the gold token.
- **transitivity** — the stated strict pairs are closed transitively, then the unique maximum (or
  minimum) is read off. The one underdetermined task is verified by the closure yielding *more
  than one* maximal element, not by my say-so.
- **temporal_ordering** — the order is materialised as a sequence and indexed. The underdetermined
  task is verified as having no derivable first element.
- **vacuous_truth** — each task carries its domain as explicit `(antecedent_holds,
  consequent_holds)` pairs and the quantifier is evaluated by enumeration:
  `all(c for a, c in domain if a)` for universals, `any(a and c ...)` for the existential. The
  vacuous cases come out true because the antecedent set is empty, not because I asserted it.
- **consistency_check** — decided by exhaustive search over each finite model space (permutations
  of ranks; permutations of Mon–Wed under the three day exclusions; boolean assignments for the
  syllogism) or solved exactly for the linear system. No constraint set is hand-waved.

Two bugs in my own verifier surfaced during this and were fixed before delivery: the
lowest-element predicate was returning the highest element, and the quantifier checks were
assertions rather than enumerations. Both would have passed unnoticed if I had trusted the first
run.

## Controls

**Position** — the correct answer's slot is drawn from a fixed multiset (11, 11, 10, 10) shuffled
under a fixed seed, decorrelated from category order. Measured: 11 / 11 / 10 / 10, i.e.
0.262 / 0.262 / 0.238 / 0.238.

**Length** — measured, then corrected. My first build had the correct answer shortest in **31 of
42** tasks, giving "pick the shortest candidate" **0.375**: a leak as large as the one this
experiment is probing, merely inverted. Cause: my correct answers are short names and numbers
while my uncertainty options were long phrases.

Fixed with a single meaning-preserving knob. The "no determinate answer" option has several
exactly equivalent phrasings of different lengths (`undetermined` … `not determinable from the
statements given`); a small coordinate-descent picks one per task to drive both trivial heuristics
toward chance. **Prompts, gold answers and substantive distractors were not touched** — only the
phrasing of the uncertainty option, and only in tasks that already had one.

## The number you asked for

```
expected "pick the longest candidate"   0.2599
expected "pick the shortest candidate"  0.2560
chance floor                            0.25
Apollo home battery, pick-longest       0.342
```

Ties are resolved as 1/k rather than being counted as hits, so these are expected scores, not
best-case ones. Per-task flags (`correct_is_longest`, `correct_is_strictly_longest`,
`correct_is_shortest`, `correct_is_strictly_shortest`, tie counts) are in the sidecar so you can
recompute the floor under whatever tie convention you prefer.

**This battery's trivial-heuristic floor is 0.2599 against your 0.342.** That gap is a measurement
about your battery, not about Apollo, and it is now measurable rather than assumed — which was the
point of asking for it.

## Caveats I want on the record

- **Six per category is coarse and I did not pad it.** Per-category readings are exploratory by
  construction; the aggregate is the endpoint. I added no tasks to make any category look
  decisive, including after I noticed which categories had more natural distractors available.
- **Category difficulty is not equalised across categories.** Nothing in the request asked for it
  and I had no principled scale to equalise on. A per-category spread is therefore not by itself
  evidence about Apollo's capability profile.
- **These are surface-varied but not adversarial.** They test whether a competent reasoner handles
  stated premises, not whether it resists traps. Distractors are plausible, not maximally
  deceptive. If Apollo scores near its home battery this shows robustness to authorship, not
  robustness in general.
- **I am one author.** Whatever idiosyncrasies I have are now baked into this instrument, exactly
  as yours are into yours. A second independent author would be a stronger test than a second tier
  from me.

## On the optional second tier

I have not built the matched-style tier and would rather not build it myself. Its purpose is to
separate "Apollo lacks the capability" from "Apollo's parsers are coupled to our phrasing" — but if
the same author writes both tiers, the contrast is confounded by that author's style drift between
them. It is a cleaner experiment in a different pair of hands, or from me after this tier is scored
and the result is public, so that seeing the format cannot influence how I write it.
