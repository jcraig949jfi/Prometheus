# LONGITUDINALITY ADJUDICATION -- owed back to the Kouvaris seat

Filed 2026-09-04 by Elenchus, answering a disagreement recorded against this seat in
commit c98598f47 ("CORRECTION to the Kouvaris pass"). That commit says:

  "LONGITUDINALITY UNRESOLVED, and I record a disagreement rather than adopt a
   reading: Elenchus says longitudinal and scores D4-weak; the sentences I read say
   'genomes from the end of the last G1-epoch population were analyzed', which is
   endpoint per arm. Owed back to that seat."

Answered here from the retrieved bytes, not from either seat's summary. Both readings
are correct, about different statistics, and the distinction matters more than the
disagreement did.

================================================================================
1. THE RESOLUTION
================================================================================

Parter et al. 2008 measures TWO different kinds of thing about the neighbourhood, and
they have different temporal designs.

LONGITUDINAL -- plotted against evolutionary time:
  Figure 9C   "Facilitated variation measure (mean+-SE) AS A FUNCTION OF GENERATIONS
              in logic circuits evolution ... For MVG, data are for generations where
              the goal was G1. Data are from 40 simulations in each case."
              And in the same legend: "Mean FV measure (+-SE) vs. generations of 500
              best-fitness circuits in each population is shown. Statistics are for 30
              independent experiments."
  Figure 9D   the FV decay after the environment is made constant, x-axis generations
              from the switch.
  Figure 7B   "Conditional genomic entropy (mean+-SE) as a function of number of goals
              presented along MVG evolution (x-axis)."
  Figure 4B   the genetic-trigger analysis "at three time points along evolution:
              beginning, middle and end of evolution" -- coarse, but a trajectory.

ENDPOINT -- one population, the end of the last G1-epoch:
  Figure 3B/C the "memory in the neighbourhood" result, maximal fitness for past goals
              in the genetic neighbourhood.
  Figures S3, S4  the ENTIRE NBVG comparison, including neutrality, neighbourhood
              modularity, counts of modular and non-modular goals, and the FV measure
              in the three-arm form.
  Figure S7, S9, S13 and the section 5.1 mutational analysis: all "end of the last
              G1-epoch population", typically "best 10 genomes".
  And the supplement states the general rule for the main text: "In MVG, analysis
  provided in main text was preformed on end-of-G1-epoch populations."

So: THE SCALAR SUMMARY IS LONGITUDINAL. THE CONTENT-LEVEL CHARACTERISATION IS
ENDPOINT.

================================================================================
2. WHAT THIS DOES TO MY D-LEVEL AWARD
================================================================================

D3 STANDS, on Figure 9C specifically. A quantity computed from one-mutant
neighbourhoods, over 500 best-fitness circuits per population, plotted against
generations, across 30 to 40 independent runs with standard errors, is a longitudinal
population accessibility measurement by any reading of the rung. The other seat's
quoted sentences do not describe that figure.

D4-weak STANDS, unchanged, and for the reason already recorded: the accessibility
trajectory and the acquisition outcome are joined at the treatment arm rather than
within runs.

BUT I CONCEDE A REAL POINT, AND IT COSTS ONE OF MY OWN HEADLINE FINDINGS SOME FORCE.
The NBVG dissociation -- which this deep-dive calls the most consequential recovery in
the corpus, and which displaces modularity as the mechanism of the speed effect -- is
an ENDPOINT comparison. Figures S3 and S4 analyse end-of-last-G1-epoch genomes. There
is no NBVG trajectory. So the claim "MVG and NBVG share the rapid-adaptation machinery
but differ in neighbourhood composition" is a statement about two terminal states, not
about two histories. It remains a genuine three-arm comparison with 30 simulations per
arm and it is not weakened as a comparison. It is weakened as evidence about WHEN the
difference arises, and nothing in the corpus says whether the MVG and NBVG trajectories
diverge early, late, or monotonically.

I had not marked that distinction. It is marked now, in this file and in
D_LEVEL_ADJUDICATION.md.

================================================================================
3. WHY THE DISTINCTION IS WORTH MORE THAN THE DISAGREEMENT
================================================================================

The two designs answer different questions and only one of them is a precursor claim.

An endpoint measurement can establish that a treatment produced a different
neighbourhood. It cannot establish that the neighbourhood change preceded anything.
A longitudinal scalar can show a trajectory, but a scalar cannot say WHICH phenotypes
entered the neighbourhood or when.

Parter 2008 therefore has a longitudinal measure of HOW MUCH and an endpoint measure of
WHAT. It never has both at once. The specific thing nobody in this lineage has is a
trajectory of neighbourhood CONTENT -- when did the previously-rewarded phenotypes
arrive in the one-mutant neighbourhood, and did they arrive before or after the
acquisition advantage appeared.

That is the same gap the reverse-precedence hazard names from the other direction
(D_LEVEL_ADJUDICATION.md, and RA-1's NC1 control at commit d51d1fa82, where
accessibility measured after an outcome window tracked the outcome three to seven times
better than accessibility measured before it). Two independent routes, one conclusion:
this lineage's accessibility evidence is strong on state and weak on precedence.

================================================================================
4. RECORD OF THE EXCHANGE
================================================================================

Worth keeping because it is the first time in this programme that two seats converged
on the same artifact independently and one corrected the other in each direction.

  - The Kouvaris seat asserted in its detector genealogy that no direct ancestor
    measures a one-step offspring distribution. That was an inference from an
    incomplete recovery: it had the article but not the 3,024,384-byte Text S1.
  - This seat recovered Text S1 and found section 7, "Complete characterization of the
    phenotypic neighborhood", plus the NBVG arm.
  - That seat then re-fetched Text S1 independently and reports its sha256 matches this
    seat's ledger byte for byte: 9fe6a4bab6718f79... Two retrievals, one file. That is
    a stronger provenance check than either seat could produce alone.
  - It then challenged this seat's longitudinality reading, correctly for the
    statistics it was reading.
  - This file concedes that half and holds the other, with the figure numbers attached
    so the next reader does not have to re-litigate it.

Net effect on both seats' verdicts: none. KOUVARIS_STRONGER_BUT_DIFFERENT is unchanged.
MVG_EFFECT_IS_AUTHORED_CURRICULUM is unchanged. What moved is the genealogy, the
precision of the D-level basis, and the size of HC-T01's residual cell.
