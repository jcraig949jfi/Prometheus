# CAUSAL INTERVENTION MAP

Every intervention the retrieved corpus contains, what it moved, what it held fixed, and
what a third variable could still explain. Then the two questions the assignment singles
out: the randomly-varying control, and switching frequency.

================================================================================
1. INVENTORY OF INTERVENTIONS
================================================================================

I1. FIXED GOAL (FG) -- baseline, all three papers
    changed: nothing varies. held: substrate, algorithm, fitness definition.
    modularity effect: low (Q_m 0.12 circuits, 0.15 neural).
    adaptation effect: slow (9,000 gens circuits; 21,000 neural).
    accessibility effect: FV rises with generations but significantly less than MVG.
    confound: in the 2008 FV comparison the FG arm carried a gate-minimisation pressure
      the MVG arm did not. Structural differences between arms are therefore not cleanly
      attributable to the goal regime alone. Unaddressed by the paper.

I2. MODULARLY VARYING GOALS (MVG) -- the treatment
    changed: the combining function f, every E=20 generations.
    held: subgoal identity, input partition, arity, algorithm, fitness form.
    modularity: high (Q_m 0.54 circuits, 0.35 neural).
    adaptation: 95x-700x speedup on hardest goals across five substrates (2007 Table 1).
    accessibility: FV trajectory rises significantly faster than FG; neighbourhood
      stocked with past-goal phenotypes; intra-module effect up, pleiotropy down.

I3. RANDOMLY VARYING GOALS (RVG) -- 2005 form
    changed: goal switches to a random function with NO shared subgoals.
    result: "do not seem to evolve modular structure ... the networks take a relatively
      long time to adapt to the new goal, as if it starts evolution from scratch."
    reading: structure of the variation, not variation as such, produces MODULARITY.

I4. RANDOMLY VARYING GOALS (RVG_v) -- 2007 form  *** LOAD-BEARING ***
    changed: same as I3, but the outcome measured is SPEED, not modularity.
    result: large speedups anyway -- 45x (model 1), 160x (model 2), 10x (model 3),
      3x (model 4), <1 (RNA).
    reading: see section 2 below. This dissociates speed from modularity.

I5. RVG_c -- random goal held constant per run
    result: <1 to 1.3x across all five models. Essentially no speedup.
    reading: it is the SWITCHING, not the randomness of the goal, that does the work.

I6. VG_0 -- goal alternates with NO SELECTION AT ALL (neutral epochs)  *** LOAD-BEARING ***
    changed: periodically remove fitness selection entirely.
    result: 2.5x, 190x, 1.5x, 3x, <1 across the five models.
    reading: in model 2, alternating with pure neutral drift delivers 190x against MVG's
      265x -- roughly three quarters of the effect with NO GOAL STRUCTURE WHATSOEVER.

I7. MODULARITY DECAY UNDER FG (2005, Fig 3) -- a true intervention
    changed: seed the population with a MODULAR circuit, then apply a fixed goal.
    held: the circuit's function.
    result: modularity decays within a few tens of generations.
    reading: modularity is actively maintained by the environment, not a ratchet.

I8. FV DECAY UNDER CONSTANT GOAL (2008, Fig 9D) -- the closest thing to a mediation test
    changed: take an end-of-MVG population at perfect fitness for G1, make the goal
      constant from generation zero.
    result: "Facilitated variation rapidly decays when goal becomes constant over time."
    reading: manipulates the CAUSE, measures the MEDIATOR. Does not manipulate the
      mediator, so it cannot establish that the mediator carries the outcome.

I9. NON-EVOLVED PHENOTYPE-MATCHED CONTROLS (2008, Fig 9B/9C)
    changed: obtain genomes with the target phenotype WITHOUT evolutionary history --
      inverse-fold algorithm (RNA, 200 genomes) and simulated annealing (circuits).
    held: the phenotype; the goal is satisfied.
    result: used as the baseline against which FG and MVG FV are read.
    reading: the correct control shape. Isolates history from task-satisfaction. Does NOT
      isolate structure from history, because the controls are not matched on modularity.

I10. COMPETITION EXPERIMENTS (2008, Fig 6D/6E insets)
    changed: seed a population 50/50 with FG and MVG genomes, present a new goal.
    result: MVG takes over ~70% of runs on novel-module goals; 50/50 on random goals.
    reading: a direct fitness-relevant readout of the advantage and its boundary.

I11. SUBSTRATE VARIATION (2007) -- five model systems
    result: MVG speedup in all five; the other regimes vary wildly by substrate.
    reading: the MVG effect is the only one robust across encodings.

I12. GOAL COMPLEXITY SWEEP (2007)
    result: speedup scales with goal difficulty, exponent alpha = 1.0 +- 0.2.

I13. SWITCHING PERIOD SWEEP (2007) -- see section 3.

I14. NEIGHBOURING VARYING GOALS (NBVG) -- 2008 Text S1 section 2.1  *** DECISIVE ***
    changed: switch every 20 generations between two goals that are NOT modularly
      related, but whose neutral networks are CLOSE in genotype space.
    held: everything else, including switch period.
    construction, verbatim: "we chose G2 goals that have close solutions to G1. That is
      G2 goals whose neutral networks come close to the G1 neutral network ... we scanned
      the phenotypic neighborhood of genomes sampled from the G1 neutral network and
      ranked the Boolean functions according to their appearance in the set of
      neighboring phenotypes. G2 was chosen such that it had an approximately median
      ranking and was not a trivial function or a modularly decomposable one."
      Worked pair: G1 = (x XOR y) AND (w XOR z); G2-NBVG = (x AND (w NAND z)) OR (w NOR z).
    result, verbatim: "We find that the evolutionary dynamics of NBVG is very similar to
      that of MVG, with respect to the rapid adaptation when environment changes. The
      design and the mechanisms that underlie this rapid adaptation are equivalent to
      that of MVG and include the location of genomes at the border of the neutral
      networks and the evolution of small number of genetic triggers (Fig. S3)."
    BUT ALSO, Figure S4 ("Distinct features of MVG and NBVG evolutions"): MVG and NBVG
      DIFFER on (a) modularity of genetic neighbours, (b) number of modular goals in the
      phenotypic neighbourhood, and (c) the FV measure.
    replication: 30 simulations in scenario 1, 15 in the others.
    reading: see section 2b. This is the most important single experiment in the corpus
      for Prometheus and it is in the supplement, not the paper.

INTERVENTIONS THAT DO NOT EXIST, searched for and absent:
  - direct manipulation of modularity while holding history constant
  - knockout, freezing, or transplant of genetic triggers
  - a training family and a test family built on DIFFERENT input partitions
  - any within-run coupling of accessibility trajectory to later acquisition speed

================================================================================
2. THE DISSOCIATION THAT WEAKENS THE STANDARD STORY
================================================================================

Put I3, I4 and I6 side by side. This comparison is not made in either paper's abstract and
it is the most adversarially useful thing in the corpus.

  regime   produces modularity?        produces speedup?
  ------   -------------------------   ---------------------------------------------
  FG       no (and destroys seeded)    no
  MVG      YES (Q_m 0.54)              YES (95-700x)
  RVG_v    NO (2005: "do not seem to   YES, large (45x, 160x, 10x, 3x) in 4 of 5
           evolve modular structure")     models
  VG_0     not measured                YES in model 2 (190x), no elsewhere
  RVG_c    not measured                NO (<1 to 1.3x)

Randomly varying goals produce NO modularity and yet produce large speedups. Therefore
modularity is NOT NECESSARY for the acceleration in these systems. The 2007 paper says as
much in its own mechanism section: RVG_v "seems to help by pushing the population in a
random direction, thereby rescuing it from fitness plateaus or local maxima" -- a generic
search-escape effect with no representational content at all.

Consequence for the assignment's section 10, which asks whether modularity is causal or a
visible correlate: in the SPEED channel, modularity is demonstrably not required, and a
substantial fraction of the effect is available from plateau escape. What modularity is
required for is the accessibility structure -- the 2008 neighbourhood results have no
RVG counterpart, and MVG is the only regime shown to stock the neighbourhood with
useful phenotypes.

The clean statement: 2007 measures a SEARCH-DYNAMICS effect largely obtainable without
structured environments; 2008 measures a REPRESENTATIONAL effect that appears to require
them. Conflating the two papers into "MVG makes evolution faster because it makes
organisms modular" is a claim the corpus does not support, and this deep-dive registers
it as the lineage's most commonly repeated overstatement.

================================================================================
2b. THE NBVG DISSOCIATION -- MODULARITY IS A CORRELATE, NOT THE MECHANISM
================================================================================

This is the most consequential recovery of the deep-dive and it is buried in Text S1.

The authors built a control that most readers of the main text never see: two goals that
are NOT modularly related, deliberately selected so that their NEUTRAL NETWORKS COME CLOSE
in genotype space. G2 was chosen by scanning the phenotypic neighbourhood of genomes
sampled from the G1 neutral network, ranking Boolean functions by how often they appear
there, and taking one of approximately MEDIAN rank that was neither trivial nor modularly
decomposable.

What happened, verbatim: "We find that the evolutionary dynamics of NBVG is very similar
to that of MVG, with respect to the rapid adaptation when environment changes. The design
and the mechanisms that underlie this rapid adaptation are equivalent to that of MVG and
include the location of genomes at the border of the neutral networks and the evolution of
small number of genetic triggers."

So the rapid-adaptation machinery -- neutral-network-border positioning plus a small set
of genetic triggers -- arises WITHOUT modular goal structure, provided successive goals are
close in genotype space. Modular decomposability is a SUFFICIENT way to guarantee that
closeness. It is not the mechanism.

But MVG and NBVG are not equivalent. Figure S4 is titled "Distinct features of MVG and
NBVG evolutions" and separates them on exactly three things: (a) modularity of the genetic
neighbours, (b) the number of modular goals in the phenotypic neighbourhood, and (c) the
FV measure. And Text S1 states the resulting ordering plainly: "Environments that change
in a non-random modular fashion enhance evolution of non-random, facilitated-variation.
Environments that change in a more random fashion evolve organisms with a more random,
un-biased phenotypic variation, with very low FV measures. Finally, environments that do
not change at all (FG) evolve organisms with a medium level of facilitated variation (due
to increased robustness)."

Note the FV ordering is NOT monotonic in how much the environment varies:
    MVG (structured variation)      HIGH FV
    FG  (no variation)              MEDIUM FV
    random variation                VERY LOW FV
Unstructured variation is WORSE than no variation for this property. That is a genuine
non-monotonicity and it is the strongest single argument in the corpus that structure --
not change -- is what builds the biased neighbourhood.

THE CLEAN TWO-LAYER READING, which is this deep-dive's answer to assignment section 10:

  layer 1  SPEED and MEMORY of previously seen goals
           caused by: successive goals having nearby solution sets, i.e. neutral networks
           that touch. Produced by MVG and equally by NBVG. Modularity NOT required.
           Mechanism: position at the neutral-network border plus a few genetic triggers.

  layer 2  BIASED NEIGHBOURHOOD and GENERALISATION to novel goals in the family
           caused by: the shared structure being MODULAR specifically. Produced by MVG and
           NOT by NBVG (they differ on exactly this in Fig S4).
           Mechanism: the neighbourhood becomes enriched with decomposable phenotypes --
           "the neighborhood of MVG-circuits is enriched (relative to FG) with circuits
           that compute decomposable Boolean functions".

Assignment section 10 offered three possibilities. The third is correct, with a
refinement: environmental switching causes a hidden representational property
(neutral-network-border positioning + triggers) that produces the speed; modularity is a
separate, additional consequence of the structure of the switching that produces the
generalisation. Modularity is a visible correlate of layer 1 and a genuine cause in
layer 2.

Anyone quoting "modularly varying goals speed up evolution because they make organisms
modular" is wrong on layer 1 by the authors' own control.

================================================================================
3. SWITCHING FREQUENCY -- THE GOLDILOCKS BAND
================================================================================

Verbatim (2007): "We find that speedup under MVG occurs for a wide range of switching
times ... For efficient speedup, the switching time of the goals should be larger than the
minimal time it takes to rewire the networks to achieve each new goal and shorter than the
time it takes to solve a fixed goal. In the present examples, the former is usually on the
order of a few generations, and the latter is usually 10^3 generations or larger."

  lower bound   time to rewire to the new goal          ~ a few generations
  upper bound   time to solve a fixed goal              ~ 10^3 generations or more
  band width    approximately three orders of magnitude
  value used    E = 20 generations throughout 2005, 2007, 2008

Stated without biological metaphor, as requested, and in the form a world-physics part
should take:

  PART: temporal alternation of the objective at a period bounded below by the
  reconfiguration time of the system under its own variation operator, and bounded above
  by the unaided solution time for a single objective. Within this band the system retains
  shared substructure across objectives instead of either (i) failing to reach any
  objective before the next arrives, or (ii) fully specialising to one objective.

Both bounds are properties the SFE can measure directly for any candidate world before
choosing a switch period: measure reconfiguration time, measure fixed-goal solution time,
place E between them. This is the most immediately portable part recovered from this
lineage and it does not depend on the modularity story being right.

================================================================================
4. THIRD-VARIABLE ACCOUNTS NOT EXCLUDED
================================================================================

T1. SIZE PRESSURE ASYMMETRY. The 2008 FG arm carried a gate-count penalty the MVG arm did
    not. Parsimony pressure alone is known to affect circuit structure. Not excluded.

T2. EFFECTIVE POPULATION EXPOSURE. MVG populations see more distinct fitness functions,
    hence more distinct selective sweeps, hence potentially more standing variation. The
    genetic-variance mechanism was tested and REJECTED by the authors (mechanism (c),
    reduced lethality, did not hold), which partially but not wholly closes this.

T3. PLATEAU ESCAPE. Established as a real and large effect by the RVG_v column. Any MVG
    result that does not have a matched varying-environment arm cannot separate
    representational restructuring from generic plateau escape.
    *** SELF-CORRECTION, 2026-09-03. An earlier draft of this file asserted that the 2008
    accessibility experiments had no such arm and named this the most serious unaddressed
    confound in the corpus. That was WRONG, and it was wrong because the draft was written
    before Text S1 was recovered. Text S1 sections 2.1 and 2.2 carry TWO non-modular
    varying-environment arms (NBVG for circuits, thermal fluctuation for RNA), and Figures
    S3 and S4 report the accessibility measurements for them. The confound is addressed by
    the historical record, and the answer it gives is more interesting than the objection
    was -- see section 2b. Recorded rather than silently edited, because the review's own
    error rate is data. ***

T4. SELECTION-INTENSITY DIFFERENCES. Exponential fitness scaling with a moving objective
    is not the same selective intensity as with a static one. Not analysed.

T3 is the one Prometheus should carry forward. It converts directly into a design
requirement: any accessibility comparison must include an unstructured-variation arm, not
only a fixed-environment arm.
