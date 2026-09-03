# TOUSSAINT vs KASHTAN/ALON MVG -- COMPARISON MATRIX

Toussaint column sourced from the house specimen at
`herakles/specimens/spec-toussaint-exploration/` (detector part DP-TOUSSAINT-XI-SIGMA,
HC_T01_PREREGISTRATION.md, HC_T01_EXECUTION_REVIEW_PACKET.txt), not from independent
recall. MVG column sourced from this deep-dive's retrieved primaries.

Note on status: HC-T01 has been EXECUTED as of 2026-09-03, and its kill condition K7 fired
("the detector predicts acquisition no better than current fitness does"). This matrix is
written against that outcome, not against HC-T01 as a proposal.

================================================================================
THE MATRIX
================================================================================

  ROW                      TOUSSAINT (SRC-PHD-2003)          KASHTAN/ALON MVG
  ----------------------   -------------------------------   ---------------------------
  representation           string/rule genetic system with    fixed-length binary genome
                           a variable, rewritable genotype    encoding NAND circuits, or
                           structure; genome length is        RNA sequence. Genome
                           itself evolvable (->11 by gen 200) structure is FIXED.
  variation operator       EVOLVABLE. 2nd-type mutations      FIXED BY EXPERIMENTER.
                           rewrite the representation         Per-locus P_m and crossover
                           phenotype-neutrally; beta is the   P_c, constant all run.
                           control parameter                  Never itself evolves.
  environmental structure  essentially static target;         THE INDEPENDENT VARIABLE.
                           environment is not the             Goal alternation every
                           independent variable               E=20 generations.
  selection                standard fitness selection         elite + fitness-proportional
                                                              (t=30); exponential scaling
  self-adaptation          YES -- the representation adapts   NO -- the genotype-phenotype
                           its own exploration distribution   MAP shifts, but no mechanism
                                                              adapts the operator itself
  local offspring          YES. Xi_sigma: distribution over   YES. Phenotypic neighbourhood:
    detector               offspring phenotype of a fixed     all phenotypes one point
                           parent, Monte Carlo 2000 samples   mutation away. EXHAUSTIVE
                           per individual per generation      (B evaluations), not sampled.
  population-wide          YES, every member of the           YES, 500 best-fitness circuits
    detector               offspring population               per population
  longitudinal detector    YES, per generation over           YES, FV measure vs generations
                           1000-2000 generations              over 1e5 generations
  modularity               measured as "modular degree",      measured as normalised
                           hand-tailored to a period-5        Newman-Girvan Q_m; emergent,
                           target of length 25                never rewarded
  neutral structure        neutral degree n = Xi_sigma(parent CENTRAL, and recovered only
                           phenotype); rises 0.45 -> 0.70     from Text S1: "location of
                                                              genomes at the border of the
                                                              neutral networks"
  mechanism ablation       YES, and clean: beta = 0 removes   YES, but on the ENVIRONMENT:
                           2nd-type mutations entirely.       make the goal constant and
                           A 2x2 design exists.               watch FV decay (Fig 9D).
                                                              The operator is never ablated.
  future acquisition       measured in HC-T01 execution;      measured: generations AND
                           K7 fired                           MUTATIONS to reach new goals;
                                                              plus competition takeover rate
  within-run precursor     NO. The detector was never run     NO. Accessibility and
                           inside the ablation -- that is     acquisition are joined at the
                           the "missing cell". HC-T01 ran it  ARM, never within a run.
                           and the detector failed K7.
  held-out target          NO. Single target family.          YES. Two novelty classes
                                                              (new-comb, novel-module) plus
                                                              an out-of-family class.
  target novelty class     n/a -- no transfer test            TYPE I and TYPE II tested;
                                                              TYPE IV tested and NULL;
                                                              TYPE III never constructed
  authored decomposition   the modular degree statistic is    SEVERE. Composition scheme
                           hand-tailored to the target's      f(g(x,y),h(w,z)) authored,
                           period-5 structure -- authored in  fixed, and also used as the
                           the DETECTOR                       analysis basis. Authored in
                                                              the ENVIRONMENT and the METRIC.
  D-level                  D3 (detector); the ablation adds   D0 (2005), D1-adjacent (2007),
                           no D-level because the detector    D4 weak (2008)
                           was never measured inside it
  strongest causal claim   "having had the knob moves the     "environments that change in a
                           detector by 2.4 -- same phenotype, systematic, modular fashion
                           same fitness, different reachable  seem to promote facilitated
                           futures" (HC-T01 execution)        variation and allow evolution
                                                              to generalize to novel
                                                              conditions"
  key confound             TRAP 1, declared LIVE: beta        PLATEAU ESCAPE. Addressed by
                           parameterises the variation        the NBVG/RVG arms, and the
                           operator that induces the          answer dissociates speed from
                           detector, so "ablation moves the   modularity. Residual: FG arm
                           detector" risks being true by      carried a gate-count penalty
                           construction                       the MVG arm did not.
  statistical discipline   no uncertainty reported on the     30-40 independent runs per
                           historical detector; no noise      condition, mean +- SE
                           floor exists                       throughout, p-values reported

================================================================================
WHAT HC-T01 MEASURES THAT KASHTAN/ALON DID NOT
================================================================================

1. THE VARIATION OPERATOR AS THE THING THAT CHANGES. In MVG the operator is a constant of
   the experiment; what moves is the genotype-phenotype map. Toussaint's 2nd-type mutations
   make the representation itself the mutable object, and beta gives a direct handle on it.
   MVG has no analogue and cannot acquire one without changing the algorithm.

2. A PHENOTYPE-PRESERVING INTERVENTION. HC-T01's execution reports "same phenotype, same
   fitness, different reachable futures". MVG has no intervention that holds phenotype and
   fitness fixed while moving accessibility. Its interventions all move the environment,
   which moves everything downstream.

3. A SAMPLED ESTIMATOR WITH AN ESTIMATOR-NOISE PROBLEM. Xi_sigma is Monte Carlo at 2000
   samples; the MVG neighbourhood is EXHAUSTIVE over B single mutations. MVG therefore has
   no estimator noise at all on this quantity -- a genuine advantage that HC-T01's own
   ESTIMATOR_NOISE_PROTOCOL exists to manage.

================================================================================
WHAT KASHTAN/ALON ESTABLISHED THAT HC-T01 CANNOT
================================================================================

1. AN INTERVENTION THAT IS NOT TAUTOLOGICAL. This is the important one. HC-T01's TRAP 1 is
   declared LIVE: the ablated parameter directly parameterises the variation operator that
   induces the detector, so moving the detector by ablation risks being true by
   construction, and a mechanical-effect null is mandatory. MVG has NO such trap. Its
   intervention is on the GOAL SCHEDULE -- an object causally remote from the mutation
   operator, which is untouched. Any change in the phenotypic neighbourhood under MVG is
   mediated by the evolved genome, never by the experimenter's hand on the operator.
   ON THE TAUTOLOGY AXIS, THE 2008 DESIGN IS STRICTLY CLEANER THAN HC-T01.

2. A TRANSFER TEST WITH A NEGATIVE RESULT. MVG has held-out target families, an in-family
   positive and an out-of-family null, with difficulty matching. Toussaint's design has a
   single target family and no transfer test at all, so it cannot say whether any
   accessibility change buys anything beyond the target it was selected on.

3. REPLICATION AND UNCERTAINTY. 30-40 runs per condition with SE reported throughout,
   against a historical Toussaint record with no reported uncertainty and no noise floor.

4. A THREE-ARM ENVIRONMENTAL DESIGN with a non-monotonic outcome (MVG high FV, static
   medium, unstructured very low). Toussaint has no environmental arm.

================================================================================
BEARING ON HC-T01, GIVEN THAT K7 FIRED
================================================================================

HC-T01's executed result is that its detector predicts acquisition no better than current
fitness does. The MVG corpus is directly relevant to why, and offers one repair.

The MVG detector is not a scalar summary of exploration breadth. It is a CONTENT-ADDRESSED
question: is THIS SPECIFIC previously-useful phenotype one mutation away? The 2008 result
is not "MVG organisms explore more" -- Text S1 explicitly reports that organisms under
unstructured variation explore more randomly and score LOWER. The result is that the
neighbourhood is stocked with particular, identifiable, useful phenotypes.

A breadth-like detector has no reason to beat fitness at predicting acquisition, because
breadth is not what carries the acquisition. If HC-T01 wants a detector that survives K7,
the MVG lineage says to measure WHICH phenotypes are reachable relative to a named target
set, not HOW MANY. That is a concrete, inheritable repair and it costs nothing but a
redefinition of the statistic over the same sampled offspring.
