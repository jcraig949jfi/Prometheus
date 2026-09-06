# Expansion-design pass, step 1: the actual starting point

**Date:** 2026-09-06. **Seat:** Herakles. **Status:** measured, not recalled.

Everything below was read out of source on this pass. Where it corrects my own
earlier review packet, the correction is stated in full rather than folded in.

---

## 1. Pinned commits

The bench source is **NOT on main**. It lives on the working branch
`vivarium/v0-2026-09-05`. My 69 templates ARE on main, which means main
currently carries an inbox for a bench whose source is not there. That is not
harmful, but it means "on main" in my earlier packet referred to my artifacts
and never to the bench.

    reviewed branch      vivarium/v0-2026-09-05 @ 7a91054ad
    origin/main          c1f283a38  (no vivarium/, no archaeon/docs/)

    b70d7a665   vivarium/viv/kinds.py
    b70d7a665   vivarium/viv/executors.py
    b70d7a665   vivarium/viv/spec.py
    b70d7a665   vivarium/viv/runner.py
    fc156ae52   archaeon/docs/ROADMAP.md
    4bcf72dc9   archaeon/producer/contract.py
    4bcf72dc9   archaeon/producer/randomgen.py

    inbox contents sha256
    73b3ffa9d76b57876dab2b61d610dcb6cdbb8d577dd5bd1f4d81f95b5835e6d8

---

## 2. CORRECTION to my own review packet

My packet reported "1 of 69 runnable" and "68 of 69 named an executor that does
not exist". **Both figures were wrong, and the second was wrong by a factor of
seven.** The error was conflating two independent properties into one flag: my
"runnable" test required a template to carry NO flags at all, so a template
naming a real executor whose parameters had been damaged was silently counted
as naming a missing executor.

Recomputed, with the axes kept separate:

    EXECUTOR AVAILABILITY
      names a kind in the registry ............... 7
      names an IMPLEMENTED kind .................. 7
      names a RETIRED kind ....................... 0
      names a kind that does not exist ........... 62

    PARAMETER COMPLETENESS (independent of the above)
      param_space fully valued ................... 19
      param_space carries a destroyed value ...... 50

    JOINT
      implemented kind AND full parameters ....... 1
      implemented kind, damaged parameters ....... 6

The seven templates naming an implemented executor:

    template_id                        kind                params  field
    --------------------------------   -----------------   ------  ---------------
    evolcomp.fitness.v0                evaluate_bitstring  OK      Evolutionary Comp
    algorithm_discovery.v0             evaluate_bitstring  damaged Algorithm Discovery
    discovery_informatics.v0           evaluate_bitstring  damaged Discovery Informatics
    computational_mathematics_walk.v0  random_walk_v0      damaged Computational Maths
    computational_serendipity.v0       random_walk_v0      damaged Computational Serend.
    falsification_walk.v0              random_walk_v0      damaged Falsification Search
    pbt.stateful.walk.v0               random_walk_v0      damaged Property-Based Testing

**What this changes.** The bench is meaningfully less disjoint from the
disciplines than I reported. Six of these seven need only their damaged numbers
restored, which the re-fire already scheduled will do. The realistic near-term
admissible count is **up to 7, not 1**.

### The four axes, tracked separately from here on

    PARAMETER COMPLETENESS   are all declared axis values present and real?
    EXECUTOR AVAILABILITY    does the named kind exist, and is it implemented?
    DESIGN COMPLETENESS      is there a stated measurement, contrast and
                             informative-failure story? (mostly NOT yet; see
                             step 2)
    REFERENCE VERIFICATION   has origin.reference been checked against a
                             primary source? (currently ZERO of 69)

A value that was destroyed stays destroyed. Any number introduced from here is
a **NEW DESIGN CHOICE by Herakles** and is labelled as such, never presented as
recovered.

---

## 3. Semantics verified this pass

These were not in my earlier packet and they change what is designable.

### 3.1 Seeds: three derivations, and the target moves with them

`spec.repeat.seed_derivation` has three values, resolved in
`vivarium/viv/spec.py::repeat_plan`:

    constant       every repeat uses world.seed_root unchanged
    linear_index   seed_root + i
    sha256_index   int(sha256("<seed_root>:<i>")[:8])

The executor receives **the repeat's derived seed, not the world seed**, and
`evaluate_bitstring` derives its hidden target from that seed together with the
length. Comment in `executors.py`: "the REPEAT's derived seed, not the world's".

Consequence, and it is the most important single fact for design:

- Under `constant`, every repeat scores against the SAME hidden target.
- Under `sha256_index` or `linear_index`, every repeat scores against a
  **DIFFERENT** hidden target. Repeats are then independent landscapes, not
  repeated observations of one landscape.

### 3.2 The bench detects its own degenerate specs

`repeat_plan` computes `degenerate_by_construction` as arithmetic: constant
seed derivation, plus a stateless kind, plus `state = reset`, plus count > 1,
means every repeat is provably the identical computation and within-world
variance is zero before anything runs. Vivarium records that and runs it
anyway, as requested.

So for `evaluate_bitstring`, which is stateless: **repeat.count > 1 with a
constant seed is a declared-degenerate experiment.** Any template that wants
repeated observations must move the target, and moving the target changes the
scientific meaning from "sample the noise" to "sample the landscape".

### 3.3 evaluate_bitstring cannot express search

The payload is fixed for the whole spec. There is no mechanism for repeat N+1
to submit a different bitstring from repeat N. One spec is therefore ONE
candidate evaluated against one or more targets. Search, hill-climbing, and
population methods cannot happen inside a spec; they can only happen across
specs, which puts them in Archaeon's producer loop, not in a template.

This is a sharper statement of the gap my packet called "output-to-input
chaining", and it explains why so many evolutionary proposals named new kinds.

### 3.4 What each executor actually returns

    noop_v0              executed
    evaluate_bitstring   bits, score, solved      score continuous; solved = score >= 1.0
    random_walk_v0       position, start_position, displacement, steps,
                         step_scale, seed

`score` being continuous matters: an outcome rule can threshold it at any
value, so the bitstring kind is not the boolean instrument my packet implied.

### 3.5 Length is not restricted by the executor

`ALLOWED_LENGTHS = (16, 24, 32)` is a constant in Archaeon's PRODUCER contract,
not a limit in the executor. `executors.py` accepts any positive integer length
and rejects only non-integers and values <= 0. Length is therefore a free axis
for a template, subject to Archaeon's own declared space at draw time.

### 3.6 State

`random_walk_v0` is the only stateful kind, so it is the only one that may
declare `repeat.state = persist`. Its own docstring states the intent: under
`reset` the repeats are independent draws; under `persist` they are one
trajectory, "which is the difference a lag-1 within-world autocorrelation
reads".

---

## 4. Two analytic nulls that exist for free

Both follow from the semantics above, and both are exact rather than
simulated. They matter because step 7 asks for a null and a control on every
recommended experiment, and these two cost nothing to state.

**Bitstring, fixed string against random targets.** Under `sha256_index` with a
uniformly random target, each bit matches independently with probability 1/2,
so the raw match count is Binomial(length, 1/2) and the normalised score has
mean 0.5 and variance 1/(4 * length). This is INDEPENDENT of which bitstring
was submitted, by symmetry. Therefore a template that varies `bits` while
holding `length` should produce NO effect, and any measured effect is an
instrument defect. That is a free negative control for the whole bitstring
family.

**Walk, displacement after n steps.** Each increment is
`step_scale * (U(0,1) * 2 - 1)`, uniform on the interval of half-width
`step_scale`, mean 0, variance `step_scale^2 / 3`. After `steps` increments the
displacement has mean 0 and variance `steps * step_scale^2 / 3`. So the
diffusion law is exactly predicted: variance grows linearly in `steps` and
quadratically in `step_scale`. Any departure is an instrument defect.

**I have not executed either.** They are derived from the executor source
listed in section 1 and are predictions, not measurements.

---

## 5. What step 1 leaves open

- DESIGN COMPLETENESS is unassessed for all 69. That is step 2.
- REFERENCE VERIFICATION is zero for all 69. Not yet attempted.
- Whether aggregation across repeats is available to the detectors at analysis
  time, which my packet flagged as its own crux, is still unresolved and is now
  a named question for step 3.
