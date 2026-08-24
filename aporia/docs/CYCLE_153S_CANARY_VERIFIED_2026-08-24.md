# CYCLE 153-S — hypothesis refuted, wrong subset tested, and the real target is better than the one I invented

Four hypotheses about canary's 0.6 cap have now been raised and **all four falsified**. The fourth
was falsified by execution, which is what this pass was armed to do. The target nevertheless
**survives**, for a reason Apollo documented two months ago and I rediscovered the long way round.

## What was tested, and what it refuted

Preregistered claim: `score_by_derivability__g` skips when `ordered` is non-empty, and
`relations_from_facts → op_build_ordering` populate `ordered` before the scorers, so the derivability
scorer is hijacked by `select_nth__g`.

Executed over 40 tasks from the production generator, instrumenting every op:

    C1 generator fidelity      40 tasks, 0 malformed                        PASS
    C2 solver path present     parse_rules/forward_chain/derivability__g    PASS
    C3 positive control        solver alone 40/40 = 1.0000                  PASS
    C4 preconditions introspectable                                          PASS

    FULL CEILING PIPELINE on inference canary: 40/40 = 1.0000
    `ordered` at the derivability guard: median 0, max 0, zero in 40/40
    derivability guard HELD in 40/40 · op_build_ordering guard SKIPPED in 40/40

**REFUTED.** No collision occurs. `op_build_ordering` never even fires — its guard fails first.
`relations_from_facts` writes nothing. The derivability scorer fires and answers correctly every
time.

## The seventh scope error, and why it is not a wasted pass

I tested `inference_canary`. **The subset O1 reports at 0.6 is not that.** The eval set has four
subsets (`apollo/src/blackboard_evolve.py:496–521`):

    canary      apollo/data/clean_canary_v01.json     50 tasks   <- the 0.6 one
    synth       build_synthetic_canary(n_each=15)                <- O1: 1.0
    inference   build_inference_canary(n=20)                     <- O1: 1.0   I TESTED THIS
    cross_tier  build_cross_tier_canary(n=20)                    <- O1: 1.0

My 40/40 on the inference subset **confirms O1's `inference: 1.0`** rather than contradicting it.
The measurement is sound; it was aimed at the wrong subset. That is the seventh scope claim of mine
to fail and the rule adopted at 149-M — *enumerate the inventory first* — would have caught it,
because the inventory here is four named subsets in one function.

## The real deficit, and Apollo already knew

`clean_canary_v01.json`, 50 tasks:

    numeric_comparison 10 · numeric_stated_premise 10 · transitivity 10
    all_but_n 5 · temporal_ordering 5 · vacuous_truth 5 · consistency_check 5

And `blackboard_evolve.py:564`, dated 2026-06-24:

> *"Routable task indices = every subset EXCEPT canary. canary's compare/bool tasks are genuinely
> unsolvable in the current substrate (**no boolean primitive**) yet reward unconditional guessing —
> so full-battery acc is a misleading headline that penalizes the honest, abstaining clean router.
> routable_acc is the genuine-capability metric the LLM run should be judged on."*

So the deficit is **a missing boolean primitive**, it is a genuine expressivity gap rather than an
artifact, and Apollo diagnosed it two months before I started. Sample task: *"Is 3.06 larger than
5.92?"* with four padded yes/no/cannot-determine distractors. Nothing in the ISA answers a boolean
question, so those 20–25 items are guessed. The solvable remainder (transitivity, temporal_ordering)
is what lifts the subset to 0.6.

**The target survives and is now precisely specified:** mint a boolean primitive, measure whether
canary moves. That is exactly the Hephaestus→Apollo loop, with a documented gap and a working assay.

## The consequence that matters more, and it is a correction to the arc

Apollo's own code says **`0.8333` is a misleading headline**. It is full-battery accuracy over a
battery containing items that are unsolvable-but-guessable, and Apollo introduced `routable_acc`
precisely because of it.

**This changes the selector experiment.** R(a) — reachable-ceiling gain — must be measured on
`routable_acc`, not on full-battery accuracy. Measuring R against a metric that rewards guessing on
structurally unsolvable items would let a primitive "raise the ceiling" by changing guess
distribution. That would have been a silent confound in the C-vs-R design, and it is now closed
before the experiment is built.

## What I got wrong, stated plainly

Four hypotheses, four falsifications, in one cycle: depth bound (false — genuine fixpoint),
multi-premise rules (false — single-premise only), missing dispatch (false — guarded scorers *are* a
dispatcher), guard collision (false — executed, no collision). Plus the wrong ISA at 152-S
(archived v1) and the wrong subset here. **Two of those six were caught only because I checked my
own falsifier rather than shipping the claim**, which is the process working; the other four were
caught by reading code I should have read before hypothesising.

The honest summary of my hit rate this cycle: **zero for four on mechanism, and the pass still
produced the right target.** That is what a falsification battery is for, and it is the argument for
running one rather than trusting a chain of plausible reasoning.

## Self-identified weaknesses

- 40 tasks from one seed on the inference subset. The clean-canary subset was **read, not executed** —
  I have not run the ceiling pipeline over `clean_canary_v01.json` and confirmed 0.6 myself.
- The "no boolean primitive" claim is Apollo's, quoted from a code comment, not independently
  verified against the ISA. A `parse_comparison`/`score_by_comparison` pair exists; whether it can
  answer a yes/no question was not tested.
- The mapping from 0.6 to "solvable remainder plus guessing" is arithmetic plausibility, not a
  per-category measurement.
- No literature work this pass; the Stitch/Twitch evaluation read remains outstanding.

## Falsifier

Running the ceiling pipeline over `clean_canary_v01.json` and finding it does not score ~0.6; or
finding that `score_by_comparison` can answer the boolean items, which would mean the gap is
routing rather than expressivity after all.

## Terminal

**CYCLE 153-S: REFUTED-BUT-TARGET-SURVIVES.** The guard-collision mechanism is dead. The canary
deficit is real, is a missing boolean primitive, and was documented by Apollo on 2026-06-24. The
organism's first mint target is specified. And R must be measured on `routable_acc`, not the 0.8333
headline — a confound closed before the selector experiment is built.
