# CYCLE 154-S — Apollo's ceiling decomposed exactly, and the boolean-primitive target is void

Eighth falsification of this cycle, and the most useful. The mint target I specified last pass —
"mint a boolean primitive" — is **void by measurement**. What replaces it is sharper: the entire
16.7% gap is 20 tasks in four named categories, and the organism **abstains** on every one of them.

All four controls passed. Every number below is from execution, not from reading.

## (a) The 0.6 is confirmed, and it decomposes cleanly

    FULL O1 CEILING PIPELINE over apollo/data/clean_canary_v01.json
    OVERALL 30/50 = 0.6000     (O1 reports canary 0.6)     chance 0.2500

    category                   n     acc  chance   verdict
    numeric_comparison        10  1.0000  0.2500   SOLVED
    numeric_stated_premise    10  1.0000  0.2500   SOLVED
    transitivity              10  1.0000  0.2500   SOLVED
    all_but_n                  5  0.0000  0.2500   UNSOLVED
    temporal_ordering          5  0.0000  0.2500   UNSOLVED
    vacuous_truth              5  0.0000  0.2500   UNSOLVED
    consistency_check          5  0.0000  0.2500   UNSOLVED

Independent replication of Apollo's canary figure to four decimal places.

## (b) The boolean-primitive target is VOID

Apollo's comment (`blackboard_evolve.py:564`, 2026-06-24) states canary's *"compare/bool tasks are
genuinely unsolvable in the current substrate (no boolean primitive)."*

**Measured: `numeric_comparison` — the paradigm compare/bool category — scores 10/10 = 1.0000**,
solved by the *existing* `parse_comparison → score_by_comparison__g` pair, whose guard fired on
10/10 tasks. The boolean capability is already present and already routed.

Running those two ops alone against the three boolean-flavoured categories:

    numeric_comparison   10  acc 1.0000  chance 0.2500  scorer fired 10/10
    vacuous_truth         5  acc 0.0000  chance 0.2500  scorer fired  0/5
    consistency_check     5  acc 0.0000  chance 0.2500  scorer fired  0/5

So "no boolean primitive" is **refuted as stated**. The target I specified one pass ago does not
survive its own verification, which is the eighth falsification of this cycle and exactly what the
gate was for.

## The correction that matters: the organism ABSTAINS, it does not guess

Apollo's comment further says those tasks *"reward unconditional guessing — so full-battery acc is a
misleading headline that penalizes the honest, abstaining clean router."*

Measured across all 20 unsolved tasks:

    all_but_n          n=5  -> ABSTAIN (None/empty) 5   scorers fired: NONE
    temporal_ordering  n=5  -> ABSTAIN (None/empty) 5   scorers fired: NONE
    vacuous_truth      n=5  -> ABSTAIN (None/empty) 5   scorers fired: NONE
    consistency_check  n=5  -> ABSTAIN (None/empty) 5   scorers fired: NONE

**The ceiling organism IS the honest abstainer.** It scores 0.0000 rather than ~0.25 because no
guard matches and it emits nothing. There is no guessing to penalise.

**This retracts my own insistence from last pass.** I required that R(a) be measured on
`routable_acc` rather than full-battery accuracy, on the grounds that a primitive could otherwise
"raise the ceiling by changing guess distribution." For this organism that confound **does not
exist** — it never guesses. Full-battery accuracy is a clean measure of reachability here. The guard
is still worth keeping for organisms that *do* guess, but the rationale I gave for it was wrong and
is corrected here.

## The exact decomposition of Apollo's ceiling

The eval set is 120 tasks: canary 50 + synth 30 + inference 20 + cross_tier 20. At O1's per-subset
figures:

    canary      30/50   (measured this pass)
    synth       30/30
    inference   20/20   (measured last pass, 40/40 on a fresh draw)
    cross_tier  20/20
    TOTAL      100/120 = 0.8333

**The missing 16.7% is exactly the 20 abstained tasks.** Not diffuse, not partly guessing, not a
scoring artifact — twenty specific items across four named categories on which the substrate has no
applicable operator and correctly declines to answer.

That is the cleanest possible target definition, and it is now measured rather than quoted.

## The replacement specification, routed not built

Not one primitive. **Four capabilities, 5 tasks each:**

- `all_but_n` — arithmetic complement ("all but N of the …")
- `temporal_ordering` — temporal sequence over stated events
- `vacuous_truth` — implication with a false antecedent
- `consistency_check` — mutual satisfiability of stated constraints

Each is worth **5/120 = 4.17%** of the full battery. All four together are the entire ceiling gap.

**Preregistered prediction, stated before anything is minted:** a primitive covering exactly one of
these categories, composing correctly with the guarded dispatcher, should move the full-battery
ceiling from 0.8333 to **0.8750** (105/120) and canary from 0.60 to 0.70. Anything less means it did
not fully cover its category; anything more means it moved a category it was not targeting, which
would itself need explaining.

Any minted op must carry a **precondition that fires only on its own category** — the existing
dispatcher is a chain of guards and the four unsolved categories currently match none of them, which
is why they abstain. That is the joint, and it is the same discipline the existing `__g` ops follow.

This is a specification to route to Hephaestus. Not built here; the build-versus-research filter
applies.

## Self-identified weaknesses

- One deterministic file, 50 tasks, 5 per unsolved category. Five items is a small basis for calling
  a category a "capability", and a primitive could pass all five by overfitting to their surface form.
- I did not test whether the four categories are genuinely distinct capabilities or whether one
  operator could cover two of them (e.g. `vacuous_truth` and `consistency_check` are both
  propositional). That would change the predicted deltas.
- The 120-task total and per-subset sizes are read from `blackboard_evolve.py:496–521`; only canary
  and inference were executed by me. synth and cross_tier at 1.0 are Apollo's figures, unverified.
- No literature work again — the Stitch/Twitch evaluation read is now **three times deferred** and
  should be treated as a debt rather than a plan.

## Falsifier

A minted single-category primitive that does not move the ceiling to 0.8750; evidence that the four
unsolved categories are fewer than four capabilities; or a draw of the canary file where the
solved categories do not score 1.0000, which would mean the 0.6 is seed-dependent.

## Terminal

**CYCLE 154-S: TARGET REPLACED.** The boolean-primitive target is void — that capability exists and
is routed. The real gap is 20 abstained tasks in four categories, is exactly the whole 16.7%, and now
carries a preregistered per-category ceiling prediction. Apollo's stated rationale for `routable_acc`
is corrected: this organism abstains rather than guesses.
