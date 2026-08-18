# Charon Sprint Retrospective: What We Got Right, What We Got Wrong
## April 1-5, 2026

---

## The Journey

Day 1: First crossing. 133K objects. Zeros work. ARI = 0.55.
Day 2: Spectral tail finding. BSD wall. 3 kills.
Day 3: RMT hypothesis. Root number test. 3 more kills.
Day 4: Research battery. Council rounds. 22 experiments. "Sign inversion."
Day 5: Cross-family survey. Neron model narrative. Mean-spacing test.
       Everything collapses to scale.

## What We Got Right

1. **The basic measurement.** ARI = 0.55 for rank clustering in the
   spectral tail is real. K-means detects a difference. The difference
   is a uniform scale compression of ~0.7% within exact conductor.

2. **The cross-family survey.** Sending 5 agents to test 8 families
   was the right call. The boundary (algebraic parameters yes, analytic
   no) is a real measurement, even if the "why" turned out to be scale
   correlation rather than structural channels.

3. **The G2 dose-response.** 4 rank levels, monotonic, rho = -1.0.
   This is a clean measurement of how rank correlates with spectral
   scale across families.

4. **The G2 two-direction finding.** Rank compresses (negative d),
   torsion/endomorphism/ST expands (positive d). Both are scale effects,
   but the fact that they go in opposite directions IS interesting --
   it means different algebraic properties correlate with scale in
   different directions.

5. **Kill methodology.** Testing 16 mechanisms systematically was
   rigorous. Each kill showed orthogonality to rank. The mistake was
   not in the kills but in interpreting what "orthogonal to rank" means
   when rank itself is just a scale proxy.

6. **The disc normalization test.** This is what honest exploration
   looks like. We tested our own finding with an alternative
   normalization and it flipped. We reported it instead of burying it.

7. **The mean-spacing test.** Three lines of numpy that killed the
   entire structural narrative. Running this test was the most
   important thing we did in five days.

## What We Got Wrong

1. **Not running mean-spacing normalization on Day 1.** This should
   be the FIRST test for any spacing comparison. "Is this scale or
   shape?" is more fundamental than "what's the p-value?" We ran it
   on Day 5 after building an elaborate mechanism narrative.

2. **Building the "three channels" narrative.** When rank, regulator,
   and Tamagawa all showed negative d, we interpreted them as three
   independent channels reading the Neron model. The simpler
   explanation (they're all correlated with effective scale) was
   available but untested.

3. **The explicit formula derivation.** We asked an AI agent to derive
   a formula from the Guinand-Weil explicit formula. It produced a
   formula that was wrong in sign and magnitude. We treated this as
   "a heuristic that matches directionally" when it didn't match at all.

4. **Pivoting to paper drafts too early.** We wrote paper v1, v2, v3
   and fired 4 council rounds before the mean-spacing test. Each draft
   would have been embarrassed by subsequent findings. The instinct to
   "write up the result" is the enemy of the instinct to "test the
   result."

5. **Trusting conductor-normalized results as structural.** The KS
   normalization is standard, but it's not normalization-independent.
   We should have reported conductor-normalized AND mean-spacing-
   normalized d-values side by side from the beginning.

6. **Over-interpreting the RMT simulation.** The "sign inversion"
   (RMT predicts positive d, data shows negative) was comparing
   simulation at N=60 to data at effective N~1.3, under a normalization
   that creates apparent compression. The comparison was invalid.

## Where on the Tree We Should Have Branched Differently

### Branch Point 1: Day 4, After Gap Pattern Found
Actual path: ran 6 more experiments, fired council, built mechanism.
Better path: run mean-spacing normalization immediately. If it's zero
(as it turned out to be), the structured gap pattern is scale artifact.
This would have saved ~20 hours and prevented the entire "three
channels" narrative.

### Branch Point 2: Day 4, After First Council Round
Actual path: council demanded Tamagawa, we ran it, found "two-hump
fingerprint," declared an independent channel.
Better path: after Tamagawa shows d ~ -0.08, immediately test: is
this just correlated with conductor/scale? (We did test conductor
matching, but not mean-spacing.) Would have caught the scale
explanation immediately.

### Branch Point 3: Day 5, After Cross-Family Survey
Actual path: built Neron model narrative, ran explicit formula
derivation, declared mechanism.
Better path: run mean-spacing test on the G2 dose-response before
declaring it structural. Three lines of numpy would have shown it's
100% scale.

### Branch Point 4: Day 4, The Regulator Finding
This was the most seductive wrong turn. Within rank-1, regulator
quartiles showed d = -0.10 to -0.23 with rho = -1.0. We declared
this a second independent channel. But it's entirely scale: higher
regulator correlates with different effective normalization scale.
The mean-spacing d is -0.0002.

## What Remains Genuinely Interesting

1. **The 0.7% within-conductor compression.** This is real, significant
   (p = 1e-42), and scales as ~36/log(N). It's a finite-conductor
   correction to the KS normalization. It vanishes asymptotically but
   is measurable at conductor < 5000. Understanding its exact form
   from the density formula would be a modest but genuine contribution.

2. **The cross-family boundary.** Algebraic parameters (rank, Hecke dim)
   correlate with scale; analytic parameters (character order, spectral
   parameter) don't. This is a real observation about which properties
   affect the effective spectral scale, even if the mechanism is simpler
   than we thought.

3. **The G2 two-direction pattern.** Rank compresses scale, torsion/
   endomorphism expands scale. Both are scale effects, but the opposite
   directions mean different algebraic properties have opposite
   correlations with the effective normalization. Why?

4. **Universal gap shape.** The positive finding: gap shape is universal
   across all ranks and all arithmetic invariants, confirming RMT
   universality at the distributional level. The KS normalization
   doesn't fully remove scale, but the shape is exactly universal.

## Lessons for Future Exploration

1. **Scale vs shape is the first test.** Always. Before anything else.
2. **Multiple normalizations.** Report at least two (conductor and
   mean-spacing) for any spacing comparison.
3. **Don't build mechanism narratives on one normalization.** If the
   effect only appears under one normalization, it's not structural.
4. **Simpler explanations first.** "It's all scale" should be tested
   before "three channels reading the Neron model."
5. **Explore, don't narrate.** The exploration was valuable. The
   narration was the error. Every test taught us something. The
   mistake was weaving tests into a story before the story was earned.
6. **Negative results are the most valuable.** The disc normalization
   test and the mean-spacing test are the two most important results
   of the sprint. Both are negative (they killed claims).
7. **The council is useful for identifying tests but amplifies
   narrative bias.** Every council round demanded tests that confirmed
   the narrative. None demanded the mean-spacing test that killed it.
   The forcing function for rigor must come from internal methodology,
   not external review.
