# D-LEVEL ADJUDICATION

Ladder as issued:
  D0  no accessibility measurement
  D1  accessibility for selected individuals
  D2  population-wide snapshot
  D3  longitudinal population accessibility
  D4  longitudinal accessibility plus subsequent acquisition outcome
  D5  causal perturbation demonstrating accessibility change altered acquisition

Standing rule applied throughout: modularity, adaptation speed and network motifs are NOT
accessibility. They are translated into accessibility claims only where the paper itself
performs the translation with a measurement. Kashtan & Alon do perform it -- in 2008, and
only in 2008.

================================================================================
PAPER-BY-PAPER
================================================================================

KASHTAN & ALON 2005 .................................................... D0
  Measures: normalised modularity Q_m, network-motif Z-score profiles, generations to
  perfect solution, and the decay of seeded modularity under a fixed goal.
  Accessibility: absent. Verified by full-text search of the retrieved article.
  Note the paper nonetheless contains an intervention (seed modularity, remove the
  varying environment, watch it decay). It is a causal experiment about a STATE
  VARIABLE, not about accessibility, so it does not lift the D-level.

KASHTAN, NOOR & ALON 2007 .............................................. D1-adjacent
  Measures: time-to-solution across five substrates and five environment regimes;
  speedup scaling with goal complexity; sensitivity to switching period; and a FULL MAP
  of the fitness landscape for a 4-input version of model 2.
  Why not D0: the landscape mapping plus the finding that "each time that a goal changes,
  a positive local gradient for the new goal is generated" is a characterisation of the
  local neighbourhood of the population's current location. It is a real local
  measurement.
  Why not D2: it is a property of the landscape and the goal pair, not a measured
  distribution of offspring phenotypes emitted by an evolved variation operator. It says
  where the population is standing, not what it can throw. It also does not partition by
  individual or track a population distribution over time.
  Recorded as D1-adjacent with the qualifier stated, rather than forced onto a rung.

PARTER, KASHTAN & ALON 2008 ............................................ D4 (weak form)
  D1 satisfied: neighbourhoods computed for evolved genomes.
  D2 satisfied: computed over 500 best-fitness circuits per population, 30-40 independent
      runs per condition, not a single wild type.
  D3 satisfied: the FV measure is plotted AS A FUNCTION OF GENERATIONS under both FG and
      MVG, with the MVG trajectory rising significantly faster.
      QUALIFIED 2026-09-04 after a challenge from the Kouvaris seat (commit c98598f47),
      adjudicated in full in LONGITUDINALITY_ADJUDICATION.md. The scalar summary is
      longitudinal; the CONTENT-LEVEL characterisation of the neighbourhood is ENDPOINT
      ("end of the last G1-epoch population"), and that includes the entire NBVG
      comparison and the memory-in-the-neighbourhood result. So this specimen has a
      trajectory of HOW MUCH and a snapshot of WHAT, never both at once. D3 stands on
      Figure 9C. The finding this deep-dive calls its most consequential recovery, the
      NBVG dissociation, is an endpoint comparison and is now labelled as one.
  D4 satisfied in weak form: the same paper measures subsequent acquisition (adaptation
      to new-comb and novel-module goals, Figure 6) and finds MVG faster, plus competition
      experiments where MVG genomes take over in ~70% of runs on novel-module goals.
  Why WEAK: the accessibility result and the acquisition result are joined at the
      TREATMENT ARM, not within the run. Nobody asks whether the individual runs with
      the steepest FV rise are the individual runs that subsequently adapt fastest. A
      third variable that differs between arms could drive both. The paper does not
      report the within-run correlation, so the mediation is asserted structurally rather
      than estimated.

  PRECEDENCE HAZARD, added 2026-09-03 from commit d51d1fa82 and recorded against this
      seat's own award. A reverse-precedence control in a related substrate (RA-1's NC1)
      found that accessibility measured AFTER the outcome window tracked the outcome
      three to seven times better than accessibility measured BEFORE it, and concluded
      that "the detector behaves like a readout of where a run currently is, not a
      leading indicator of where it will go."
      D3 and D4 both presuppose that a longitudinal accessibility measurement is a
      PRECURSOR. If the measurement is instead concurrent with the state it appears to
      predict, a trajectory that looks like a leading indicator is a lagging one, and the
      rung is not earned. Parter 2008 never ran a reverse-precedence control, and neither
      did Toussaint's corpus or Kouvaris's.
      This does not retract the D4-weak award, because the award was already qualified on
      exactly this ground. It converts the qualifier from a methodological caution into a
      measured hazard with an effect size attached, and it supplies the cheapest possible
      first test of any reproduction: re-order the data you already have and check whether
      the detector leads or lags. That test costs nothing and no one in these three
      lineages has run it.
  D5 NOT satisfied: no perturbation of the accessibility structure. The genetic triggers
      are identified by mutual information and then never touched -- no knockout, no
      freezing, no transplant, no randomisation. The one perturbation that exists runs the
      other way: remove the varying environment and FV decays (Fig 9D). That manipulates
      the CAUSE and measures the MEDIATOR. D5 requires manipulating the MEDIATOR and
      measuring the OUTCOME.

PROGRAMME MAXIMUM ...................................................... D4 (weak)

================================================================================
THE MISSING D5 EXPERIMENT, STATED PRECISELY
================================================================================

The experiment that would have closed it, and which the historical record does not
contain:

  Take MVG-evolved genomes at generation T. Construct a matched set in which the trigger
  positions are disabled -- frozen, randomised, or recoded -- while HOLDING CONSTANT
  (i) fitness on the current goal and (ii) the modularity measure Q_m. Then present a
  novel-module goal and measure adaptation time against unmodified MVG genomes.

  Prediction if accessibility is the mediator: adaptation time collapses toward FG.
  Prediction if modularity per se is the mediator: adaptation time is preserved, because
  Q_m was held constant.

This experiment is cheap in the historical substrate -- B = 104 bits, populations of 5000,
and the triggers were "readily detected for all MVG cases tested". It was not run. That it
was affordable and not run is itself informative about what the programme took itself to be
establishing: a theory of facilitated variation supported by convergent signatures, not a
mediation analysis.

Prometheus can run it. It is registered as the highest-value single experiment recoverable
from this lineage and it is the point where HC-T01 can exceed the historical record rather
than duplicate it.

================================================================================
WHAT THIS DOES TO THE PROMETHEUS POSITION
================================================================================

Two axes must be scored separately or the adjudication goes wrong.

INSTRUMENT AXIS: preempted. A published, longitudinal, population-level accessibility
instrument with a phenotype-space distance metric and a useful/non-useful normalisation
has existed since 2008. HC-T01 does not get to claim the detector as novel.

PHENOMENON AXIS: not preempted, and not for a reason of rigour. The 2008 result is
rigorous. It is BOUNDED: the acquisition advantage exists only inside the goal language
the experimenter wrote down. The open question Prometheus is chasing -- whether the
accessible future can be EXPANDED rather than re-weighted within a fixed scheme -- is
untouched by this lineage, and the authors themselves supply the null that shows it is
untouched.

CAUSAL AXIS: open at exactly one rung. Nobody has perturbed the mediator.
