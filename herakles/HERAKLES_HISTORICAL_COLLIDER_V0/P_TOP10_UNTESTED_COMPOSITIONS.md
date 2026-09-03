# P. TOP-10 UNTESTED COMPOSITIONS — **CANDIDATE POOL, NOT RANKED**

Combinations that appear scientifically interesting and, as far as model recall goes, have not been adequately tested together. **"Not adequately tested" is itself an unverified claim** and is the first thing the primary-source pass must attack: the most likely failure of this file is that someone tested a cell in 1997 and we did not find it.

Each entry states the missing cell in factorial terms and the specific non-additivity that would make it interesting (§2-D: Effect(A+B) ≠ Effect(A) + Effect(B), measured on an **acquisition** endpoint, not a fitness endpoint).

---

## comp-01 — duplication x protection, on an acquisition endpoint
`part-structural-duplication` + `part-innovation-protection`
Both live in NEAT; the ablations measured final fitness. Missing cell: the 2x2 with descendant-acquisition-rate as the endpoint. **Interesting if:** neither alone changes acquisition rate but the pair does. **Cost:** CHEAP.

## comp-02 — duplication x protection x reuse
`part-structural-duplication` + `part-innovation-protection` + `part-reusable-module`
The directive's own worked example (A+B+D). Nobody, as recalled, ran the full 2x2x2. **Interesting if:** the triple opens a regime the three pairs do not. **Cost:** CHEAP-MODERATE.

## comp-03 — neutral drift x environment coevolution
`part-neutral-drift-precursor` + `part-environment-coevolution`
Neutral drift changes *which* phenotypes are one step away; niche construction changes *which* phenotypes are valuable. Hypothesis: drift is useless under a fixed environment (nothing new becomes valuable) and decisive under a moving one. **Interesting if:** drift's effect is zero in fixed environments and positive in coevolving ones. **Cost:** CHEAP.

## comp-04 — self-modifying reproduction x innovation protection
`part-self-modifying-reproduction` + `part-innovation-protection`
Autoconstruction collapses. Hypothesis: novel reproduction machinery is eliminated before it stabilises, exactly the problem speciation solves for topologies. **Interesting if:** protection converts collapse into persistence. **Cost:** MODERATE. **This is the composition I would bet on first.**

## comp-05 — particle computation x transfer
`part-particle-computation` + `part-cross-context-transfer`
Are evolved CA particle strategies *composable primitives* for later tasks, or one-off solutions? Never tested as recalled. **Interesting if:** rules with particle strategies transfer to a second task better than fitness-matched rules without them. **Cost:** CHEAP. Directly extends the first experiment.

## comp-06 — robustness selection x duplication
`part-mutational-robustness-selection` + `part-structural-duplication`
High mutation rate selects flat lineages; duplication creates redundancy that *is* flatness. Are these the same mechanism seen twice, or do they compose? **Interesting if:** they are non-redundant (each adds accessibility the other does not). **Cost:** CHEAP. A null result here is valuable: it would collapse two registry parts into one.

## comp-07 — spatial isolation x innovation protection
`part-spatial-isolation` + `part-innovation-protection`
Suspected substitutes (edge-spatial-substitutes-protection). **Interesting if:** they are NOT substitutes, i.e. the pair beats both. **Cost:** TRIVIAL. Cheapest disconfirmation in the file.

## comp-08 — learning x environment coevolution
`part-learning-smooths-landscape` + `part-environment-coevolution`
Baldwin effect under a moving target. Classic separately; the joint case with a coevolving environment is thin as recalled. **Interesting if:** plasticity's benefit grows superlinearly with environmental novelty rate. **Cost:** MODERATE.

## comp-09 — failure-driven hidden variables x evolutionary search
`part-failure-driven-hidden-variable` + any evolutionary part
The cross-paradigm test. Can a Drescher-style "invent a state variable when prediction fails" operator be attached to an evolving population? **Interesting if:** it composes at all. **Cost:** MODERATE. **Highest chance of teaching us that the causal-function translation is unsound.**

## comp-10 — reward scaffold x neutral drift, with the scaffold removed midway
`part-reward-scaffold` + `part-neutral-drift-precursor`
Avida's scaffold is designer-imposed. If the scaffold is removed after intermediates exist, does neutral drift preserve them long enough to be used? **Interesting if:** drift substitutes for the scaffold after a critical point. **Cost:** MODERATE.

---

## The honest caveat

Ten cells, zero verified as untested. Each one needs a literature check in the *native vocabulary of both fields involved* before it can be called a missing cell, and comp-01, comp-06 and comp-07 are the ones most likely to already exist somewhere in the 1995-2010 workshop literature. Finding that they were tested is a good outcome: it converts a speculation into a recovered result.
