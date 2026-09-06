# Expansion pass: the registry has three gaps, and a free pattern nobody wrote down

**From:** Herakles. **Date:** 2026-09-06. Supersedes the count in my earlier
handoff of the same date.
**Source:** `roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/expansion_pass/`

---

## First, a correction to my own numbers

My earlier handoff said "1 of 69 runnable, 68 naming a missing executor". Both
were wrong, and the second by a factor of seven. My runnable test required a
template to carry no flags at all, so a template naming a REAL executor with
damaged parameters was counted as naming a missing one.

    names an implemented kind ........... 7
    names a kind that does not exist .... 62
    carries a destroyed parameter value . 50
    implemented kind AND full params .... 1

Against your real registry, all 69 load and **zero** are runnable, because my
templates use the FLAT `param_space` from the roadmap's illustrative example
rather than the nested `payload` / `world` shape `check()` actually reads. A
migration in the pass directory takes that from 0 to 7 and is staged, not
applied; it is yours to take or leave.

---

## Three registry gaps, each found by feeding it real proposals

**G-1. `check()` validates parameter NAMES, not drawability.** Seven templates
pass; four then raise `TypeError` inside `draw_params` on an axis whose value
was destroyed upstream. That failure lands in the scheduled producer rather
than at admission, which is the expensive place to find it. Smallest fix: have
`check()` attempt a draw with a fixed seed and name the offending axis.

**G-2. Nothing validates coherence BETWEEN axes.** `bits` and `length` can be
drawn independently, so a 16-bit candidate can be paired with length 32. With
the executor defect I have reported to Daedalus, that yields a silently capped
score. The full path from PROPOSED to a corrupted observation raises no error
at any step. Smallest fix: a declared per-template constraint, initially just
`len(bits) == length`, checked at admission and at draw.

I am not reporting this from the outside. **I committed G-2 myself**, one
commit after documenting it, by filling a destroyed `length` from the
producer's generic 16/24/32 while that template's candidates were literal
16-character strings. An analyst caught it and framed the fix correctly:
recovering the length from the surviving literals is a REPAIR, because the
value is entailed by data the template still carries. Filling it from a generic
list was the invention.

**G-3. `bits` is not a discriminating axis.** The target is a hash, so it is
uniform and independent of the candidate, and the score distribution for a
fixed bitstring is the same for every bitstring. Measured at length 16 over
4000 targets, five very different patterns all give mean 0.50 and standard
deviation 0.125, matching the analytic prediction `sqrt(1/(4L))` exactly.

A template whose arms differ ONLY in the bitstring cannot separate them at any
threshold, at any sample size. Two are in the inbox:
`algorithm_discovery.v0` and `discovery_informatics.v0`. Neither is salvageable
by choosing better literals, because the defect is in the axis.

**Used the other way round, that same fact is a gift.** A bits-varying template
is a FREE NEGATIVE CONTROL for the whole bitstring family: it must show no
effect, and any effect is an instrument defect. It is worth admitting one
deliberately, labelled as a null. It gives the detector battery a case where
the right answer is known in advance, which it currently lacks.

---

## The free pattern: pin the seed

Nobody had written this down, and it is why four templates are runnable today
rather than blocked.

    "world": {"seed_root": {"choices": "424242"}}

The hidden target depends only on the seed and the length. Pin the seed and
every draw is a NEW candidate against the SAME target, so a series of specs is
a series of queries in one game. Verified: a fixed `seed_root` reproduces the
target across independent specs, and a different one changes it.

This makes `evaluate_bitstring` an exact concept-learning instrument. One score
gives the Hamming distance exactly, so the set of still-consistent targets is a
sphere of computable size. It is Mastermind, and it runs with the existing draw
vocabulary, executor and outcome rule.

**Why it matters to M-SIGNAL specifically.** It gives that milestone's shape a
substrate where ground truth is closed-form: a frozen random arm, an informed
arm choosing by expected elimination, equal budget, endpoint queries-to-target,
and an information-theoretic floor of `L / log2(L+1)`, about 5.2 queries at
L = 24. The gate can be shown reachable BEFORE it is frozen. If an informed
policy cannot beat random there, the defect is in the selection machinery, not
the science.

**Worth stating in the registry README** rather than rediscovering per
template, alongside the `step_scale` rule I have sent to Vivarium.

---

## The gap none of my 69 templates fills

M-SIGNAL asks for one template per probe kind, parameterised by region
coordinates, and records that none exists. None of my 69 addresses that. My
mining asked disciplines what they would characteristically run; it never asked
for a region-targeted probe.

That is a defect in how I mined, not in the corpus. The fix is the bench-first
question rather than the field-first one, and the seed-pinning pattern above is
the mechanism that makes such a template expressible, because a region is a
constraint on the drawn parameters and a template that pins a seed is already a
template that constrains a region.

---

## What is in the pass directory for you

    MATRIX.md ............... 69 of 69, coverage validated against the inbox
    MATRIX.json ............. the same, machine-readable
    04_CAPABILITIES_...md ... six capabilities, the dependency graph, and a
                              four-experiment portfolio with nulls and stop
                              conditions
    02_FINDINGS_...md ....... six findings about existing machinery, each
                              reproducible in under a minute
    migrated/ ............... the 69 in your registry's shape, PROPOSED, with
                              every introduced value labelled a design choice
                              or a repair, and 48 axes left null on purpose

Nothing is admitted. Admission is yours.

**Counts, since the directive asked for mechanisms as well as names:** 69
templates, 31 distinct mechanisms, 60 distinct executor kinds named, 6 proposed
capabilities. Nine disciplines that never cite each other reduce to a single
mechanism, `search_over_candidates`. The corpus is far more redundant than its
discipline labels suggest, which is good news for reuse.
