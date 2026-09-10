# Steps 5 to 7: reusable capabilities, the dependency graph, and a portfolio

**Date:** 2026-09-06. **Seat:** Herakles. Built from `MATRIX.md` (69 of 69
covered) and the findings in `02_FINDINGS_EXISTING_MACHINERY.md`.

---

## 0. The counts the directive asked to be kept separate

    templates ............................. 69
    DISTINCT MECHANISMS ................... 31
    distinct executor kinds named ......... 60
    proposed CAPABILITIES below ............ 6

    preferred route per template
      R-NOW ........  4    runs today
      R-REPAIR .....  6    runs once parameters are chosen
      R-COMPOSE .... 22    several specs plus downstream analysis
      R-BACKEND .... 22    an external tool the engine orchestrates
      R-EXECUTOR ... 10    a new executor or adapter
      R-SUBSTRATE ..  4    new state or control flow
      R-WORLD ......  1    a new world or organism type
      R-ARCH .......  0

**R-ARCH is zero.** Not one of 69 disciplines needs a different architecture.
The sealed-spec, recorded-observation shape is not the constraint. That is the
single most encouraging number in the pass, and it was not knowable before the
templates were read one at a time.

**44 of 69 are reachable without any new bench internals**, by composing specs
or by orchestrating a tool the engine already knows how to fossilize.

Mechanism concentration, which is where reuse comes from:

    search_over_candidates ......... 9 disciplines
    accumulate_trajectory .......... 8
    maintain_archive ............... 5
    score_fixed_candidate .......... 4
    two_population_interaction ..... 4
    interpret_program .............. 4

Nine disciplines that never cite each other reduce to one mechanism. That is
the pass's central structural result: the corpus is far more redundant than
its discipline labels suggest.

---

## 1. Existing assets, inspected before proposing anything

The directive is explicit about this, and it changed two proposals.

    ergon/avida2003/ ........ PRESENT. Recovered Avida material with artifacts
                              and build deliverables. The Tierra and Avida
                              templates route here, not to a new executor.
    ludus/ .................. PRESENT. atlas_of_worlds, arena, baselines. The
                              obvious home for any grid or arena world before
                              anyone writes one.
    incubation/ ............. PRESENT. Substrate and world machinery with a
                              passed gate history.
    proteus/ ................ PRESENT. Player generation and specimens.
    theseus/corpus/ ......... PRESENT, and CLOSED for navigation per memory.

**Consequence:** the R-BACKEND route is not hypothetical for at least the
digital-evolution family. Recommending a new executor there would have been
proposing a replacement for something the repository already holds.

---

## 2. Six reusable capabilities

Ordered by templates unlocked per unit of work. Each names its smallest
interface, its dependencies, its likely owner, its resource needs and what it
unblocks.

### C-0. The fixed-seed template pattern. COST: ZERO.

Not a capability. A pattern nobody had written down, and the reason four
templates are R-NOW rather than blocked.

A template may pin the world seed to a single value:

    "world": {"seed_root": {"choices": "424242"}}

Every draw is then a new candidate against the SAME hidden target, so a series
of specs is a series of queries in one game. Verified in
`03_LEADING_DESIGN_VERSION_SPACE.md`.

**Unlocks:** version-space search, query-by-committee, case-based retrieval,
Mastermind, active learning. Six templates by my count, using only the existing
draw vocabulary, executor and outcome rule.
**Owner:** Archaeon, as a documented pattern in the registry README.
**Resources:** none.

### C-1. A relatedness axis between worlds. COST: SMALL. HIGHEST UNLOCK.

Today a target is `sha256("target:<seed>:<length>")`. Any two worlds are
therefore unrelated by construction and expected transfer between them is
exactly zero. Two analysts reached this independently, from POET and from MAML.

**Smallest interface:** a new kind, `evaluate_bitstring_related_v0`, with
payload `bits`, `length`, `target_offset`. The target is the seed's target with
`target_offset` positions flipped, the positions chosen by a second hash of the
seed. `target_offset = 0` reproduces present behaviour exactly.

**It must be a NEW KIND, not an edit.** Kinds declare an exact parameter set,
and the frozen baseline template is content-hashed. Adding a parameter to
`evaluate_bitstring` would break both. This constraint is the registry working
as designed.

**Unlocks:** transfer, curriculum, stepping stones, meta-learning, POET,
minimal-criterion coevolution, generalisation. Eight to twelve templates, and
it is the only thing that makes any of them non-vacuous.
**Owner:** SFE for the executor, Vivarium for the kind entry.
**Resources:** trivial CPU. One hash and a flip loop.
**Depends on:** nothing.

### C-2. Return the witness, not only the count. COST: SMALL.

`evaluate_bitstring` returns a match COUNT. Every counterexample-guided method
needs to know WHICH positions disagreed. Without it, refinement is blind
generate-and-test, which is the method with its mechanism removed.

**Smallest interface:** add `first_mismatch` (an integer index, or -1) to the
result. A full mask is nicer and strictly more useful; the index alone is
enough to make CEGAR-style refinement measurable.

**Unlocks:** counterexample-guided abstraction refinement, counterexample-guided
synthesis, bounded model checking, learning-to-search, property-based
shrinking. Five templates.
**Owner:** SFE.
**Resources:** none.
**Measurable payoff:** rounds-to-proof with a scalar oracle against
rounds-to-proof with a witness oracle. That prices the capability in rounds
before it is built, which is the evidence Challenge 3 wants.

### C-3. A declared landscape family. COST: MEDIUM.

The scorer is onemax: single-peaked, additive, noiseless, undeceptive. Three
analysts independently warned that hill climbing, MAP-Elites, illumination and
novelty search all succeed or fail trivially on it, and that apparent success
is a shared confound across at least four templates.

**Smallest interface:** a kind whose payload names a landscape family and its
parameter, for example `family` in `onemax | needle | royal_road | nk` with a
`k`. Everything else stays identical.

**Unlocks:** quality-diversity, novelty search, illumination, search-based
software engineering, and any claim about search difficulty. Eight templates,
and it converts four existing ones from confounded to interpretable.
**Owner:** SFE.
**Resources:** small.
**Note:** this is the capability that makes the DIFFERENCE between search
methods visible. On onemax there is nothing for them to differ about.

### C-4. An orchestrated external backend. COST: MEDIUM. LARGEST COUNT.

Twenty-two templates prefer R-BACKEND: the science exists as a tool, and the
bench needs only to call it, bound its budget, and fossilize what came back.

**Smallest interface:** a kind `external_backend_v0` with payload
`tool_id`, `input_digest`, `budget_seconds`, whose executor runs a registered
tool, records the exit status, a digest of the output, and a declared
reproducibility grade. The tool registry is data, like the template registry.

**Unlocks:** 22 templates by preferred route, including the Avida and Tierra
families that already have material in `ergon/avida2003/`.
**Owner:** Vivarium.
**Resources:** the backends', not the bench's. Needs a declared budget and a
reproducibility grade per tool, because most will not be BIT_DETERMINISTIC.
**Risk to name:** this is the capability most likely to import
irreproducibility. The grade must be recorded per observation, not per tool.

### C-5. A place to record a cross-observation statistic. COST: SMALL, MOSTLY POLICY.

Twenty-two templates prefer R-COMPOSE. Their measurement exists across
observations, and the single-scalar outcome rule cannot express it. My earlier
packet called this the largest gap; the matrix says it is instead the largest
ROUTE, which is a different and better thing.

Nothing is blocked from RUNNING. What is missing is a declared home for the
derived statistic and a rule about who computes it.

**Smallest interface:** a convention, not an executor. A named analysis
artifact keyed by the set of spec hashes it consumed, with the statistic, the
attainable range, and the null it was compared against.
**Owner:** Harmonia for the adjudication rule, Archaeon for the computation.
**Resources:** none.
**Why it is not an outcome-rule change:** making the rule aggregate would move
adjudication inside the sealed spec, which is exactly the boundary the bench
was built to hold.

### C-6. Cross-axis constraints in the registry. COST: SMALL. SAFETY, NOT REACH.

From F-3 and F-3a. `bits` and `length` can be drawn incoherently, and the
executor then scores silently against a lowered ceiling.

**Smallest interface:** a declared constraint per template, initially just
`len(bits) == length`, checked at admission and at draw.
**Owner:** Archaeon, with the executor-side rejection in SFE as the belt to
this braces.
**Unlocks:** nothing. Prevents a class of corrupted observations.

---

## 3. The dependency graph

Nodes are concrete capabilities or demonstrations. `==>` is a required
dependency; `-->` is helpful but not required. Effort is rough: S is under a
day, M is a few days, L is longer.

    [BENCH TODAY]  3 kinds, 1 informative walk axis, onemax scorer,
                   one scalar outcome rule, no relatedness
        |
        |== C-0 fixed-seed pattern .................... S, zero code
        |      ==> E1 VERSION-SPACE GAME ............... S   modality: numeric
        |      ==> E3 EXCHANGEABILITY NULL ............. S   modality: numeric
        |      --> active learning, CBR retrieval, QBC
        |
        |== C-6 cross-axis constraint ................. S   (safety gate)
        |      ==> every bitstring template below is trustworthy
        |
        |== E2 DIFFUSION CALIBRATION .................. S   modality: time series
        |      (needs only F-5 discipline and a steps ladder)
        |      --> the only exercise of state=persist
        |
        |== C-2 witness in the result ................. S
        |      ==> CEGAR / CEGIS / bounded model checking       5 templates
        |      ==> learning-to-search
        |
        |== C-1 relatedness axis ...................... S/M   THE KEY EDGE
        |      ==> transfer curve E4                    modality: numeric
        |      ==> meta-learning, MAML                  8-12 templates
        |      ==> curriculum, POET, MCC
        |      --> C-3 makes the transfer curve interpretable
        |
        |== C-3 landscape family ...................... M
        |      ==> quality-diversity, novelty, illumination     8 templates
        |      ==> honest search-difficulty claims
        |      --> without it, four templates are confounded
        |
        |== C-5 cross-observation statistic ........... S, policy
        |      ==> 22 R-COMPOSE templates become adjudicable
        |      ==> M-SIGNAL's endpoint has a home
        |
        |== C-4 external backend ...................... M
               ==> 22 R-BACKEND templates             modality: symbolic,
               ==> Avida/Tierra via ergon/avida2003/   programmatic, spatial
               --> ludus/ for grid and arena worlds
               --> incubation/ for substrate worlds

**Modalities reached.** Today: numeric scalars and one time series. C-1 adds a
metric relation between worlds, which is the first geometry the bench has had.
C-3 adds landscape structure. C-4 is the only route to symbolic, programmatic
and spatial modalities, and it reaches them by orchestration rather than by
reimplementation, which is why it is cheap despite being large.

**What an organism could newly observe or act on**, which the directive asks
for specifically rather than a discipline label:

    today          nothing. One candidate, one score, no action, no memory.
    with C-0       its own prior scores, across specs, via the producer.
    with C-2       WHICH position was wrong. The first actionable signal.
    with C-1       how far this world is from the last one.
    with C-3       whether the landscape rewards exploitation or exploration.
    with C-4       whatever the backend exposes, at the cost of the bench's
                   own reproducibility guarantee.

**Uncertainty, stated.** The C-5 policy question is the one I could not settle:
whether a derived cross-observation statistic can carry a verdict without
moving adjudication inside the sealed spec. Everything downstream of C-5 in
this graph inherits that uncertainty.

---

## 4. The portfolio: three cheap, one stretch

### E1. The version-space game. R-NOW, zero new code.

**Minimal implementation.** One template, seed pinned to a single value, length
pinned, bits uniform. Fire N specs. Downstream, compute the surviving
hypothesis count after each query.
**Budget.** 60 specs, 3 seeds, 20 queries each. Well inside the daily cadence.
**Null and control.** The random arm is the frozen baseline drawing uniformly.
The informed arm chooses by maximum expected elimination. Equal budget,
separate lanes, orders committed before execution.
**Deterministic evaluation.** Queries-to-target, and surviving count after a
fixed budget. Both exact. The information-theoretic floor is L / log2(L+1),
about 5.2 queries at L = 24, so the gate is shown reachable before freezing.
**Expected failure evidence.** If the informed arm does not beat random here,
where the oracle is exact and the theory closed-form, the defect is in the
selection machinery and not the science. That is a strong cheap negative.
**Stop condition.** Stop when the two arms separate by more than the binomial
standard error at 3 seeds, or when 3 seeds are exhausted with no separation.
**Why it advances the agenda.** It is an M-SIGNAL rehearsal on a substrate that
cannot lie about the answer.

### E2. Diffusion calibration of the bench's own randomness. R-REPAIR, zero new code.

**Minimal implementation.** One walk template, `step_scale` HELD FIXED per
F-5, `steps` on a ladder of 100, 400, 1600, 6400, repeats under sha256_index.
**Budget.** 4 rungs, 200 repeats. Minutes.
**Null.** Analytic, not simulated: displacement has mean 0 and variance
`steps * step_scale^2 / 3`. The prediction is exact.
**Deterministic evaluation.** Observed variance against predicted, per rung.
**Expected failure evidence.** Any departure is an instrument defect in the
bench's random source or its seed derivation, which is worth knowing before any
result rests on either.
**Stop condition.** One pass. It either matches or it does not.
**Why it advances the agenda.** It is the only exercise of the `state=persist`
path, and it converts F-4 and F-5 from arguments into measurements.

### E3. The exchangeability null. R-NOW, zero new code.

**Minimal implementation.** A template varying `bits` across literals at fixed
length and seed distribution. It MUST show no effect.
**Budget.** Trivial.
**Null.** The template IS the null. Mean 0.5, standard deviation sqrt(1/(4L)),
independent of the candidate. Confirmed at L = 16 across 4000 targets.
**Expected failure evidence.** Any detected effect is an instrument defect, a
seeding fault, or a leak. This is a live detector-calibration probe that costs
nothing.
**Stop condition.** One pass per corpus regime change.
**Why it advances the agenda.** It gives the detector battery a case where the
right answer is known to be null. Two inbox templates were built as though this
axis were informative; admitting one deliberately as a null converts a defect
into an instrument.

### E4. STRETCH: the transfer curve. Needs C-1.

**Minimal implementation.** `evaluate_bitstring_related_v0` with
`target_offset`. Sweep the offset from 0 to L/2. For each offset, a candidate
optimised against the seed target is scored against the offset target.
**Budget.** One new executor, small. Then a sweep of 8 offsets by 3 seeds.
**Null and control.** At `target_offset = L/2` the targets are independent, so
expected transfer is exactly 0.5, the exchangeability result of E3. At
`target_offset = 0` transfer is perfect. Both ends are known in closed form,
so the curve is pinned at both ends before it is measured.
**Deterministic evaluation.** Score against offset, compared to the analytic
line interpolating the two pinned ends.
**Expected failure evidence.** If measured transfer follows the analytic line
exactly, the axis adds no structure beyond distance and the capability has been
priced honestly at low value. That is a real possible negative and it should be
stated before the sweep.
**Stop condition.** Stop after 3 seeds if the measured curve lies within
sampling error of the analytic line at every offset.
**Why it advances the agenda.** It is the first geometry the bench has ever
had, and it is the precondition for every transfer, curriculum and
stepping-stone experiment in the corpus.

### The adjacent idea the field-first framing would have missed

E3. Nothing in the discipline list asks for an exchangeability null; no field
proposes an experiment whose purpose is to show that its own axis is dead. It
appeared only because the pass ran the machinery and computed the analytic
distribution. It is the cheapest item in the portfolio and the only one whose
correct answer is known in advance, which is exactly what a detector battery
needs and does not have.

---

## 5. Build order, against the milestones I was told to preserve

M-ELIGIBLE needs comparable measurements with arm identity preserved and enough
variation to distinguish groups. M-SIGNAL needs a probe template per probe
kind, parameterised by region coordinates, and states none exists.

    now, no code       C-0, C-6, E3, E2          instrument trust
    next, small        C-2, then E1              M-SIGNAL rehearsal
    then               C-1, then E4              the first geometry
    then               C-5 policy question       M-SIGNAL endpoint's home
    later              C-3, C-4                  reach and modalities

**The gap none of the 69 fills.** M-SIGNAL wants templates parameterised by
region coordinates. My mining asked disciplines what they would run; it never
asked for a region-targeted probe. That is a mining defect, not a corpus
defect, and it is fixed by asking the bench-first question rather than the
field-first one. C-0 is the mechanism that makes such a template expressible,
because a region is a constraint on the drawn parameters, and a template that
pins a seed is already a template that constrains a region.
