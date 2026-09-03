# MVG vs KOUVARIS 2017 -- COMPARISON MATRIX AND GENEALOGY

Kouvaris column sourced from the house specimen at `ergon/kouvaris2017/`
(C_HISTORICAL_PHYSICS_SPEC.md, D_HISTORICAL_DETECTOR_SPEC.md, E_D_LEVEL_ADJUDICATION.md),
which was built from the article XML, S1 Appendix, and the author's recovered MATLAB.
MVG column from this deep-dive's retrieved primaries.

Kouvaris NP, Clune J, Kounios L, Brede M, Watson RA (2017). "How evolution learns to
generalise: Using the principles of learning theory to understand the evolution of
developmental organisation." PLoS Comput Biol 13(4):e1005358.

================================================================================
1. THE MATRIX
================================================================================

  ROW                      KASHTAN/ALON MVG (2005-08)        KOUVARIS ET AL 2017
  ----------------------   -------------------------------   ---------------------------
  substrate                NAND logic circuits; RNA           gene-regulatory network:
                           secondary structure                genotype is a pair [G, B]
  what evolves             the genome encoding a circuit      B, the matrix of regulatory
                                                              interactions (development)
  population               YES. N_pop = 5000 (circuits),      NONE. Single genotype under
                           500 (RNA), with standing           strong-selection-weak-mutation,
                           variation                          chosen so the result "does not
                                                              require lineage-level selection"
  environmental structure  goals alternate every E=20 gens    3 training targets selected;
                           within an authored composition     class of 8 defined as all
                           scheme f(g(x,y),h(w,z))            combinations of 4 independent
                                                              binary modules
  held-out targets         new-comb, novel-module, and an     THE 5 CLASS MEMBERS NEVER
                           out-of-family random class         SELECTED FOR
  detector                 phenotypic neighbourhood: set of   distribution over adult
                           phenotypes ONE POINT MUTATION      phenotypes obtained by
                           away from a given genotype         developing 5000 Sobol-sampled
                                                              UNIFORMLY RANDOM embryonic
                                                              phenotypes through fixed B
  detector locality        LOCAL and OUTBOUND. Indexed to an  GLOBAL. Not indexed to any
                           individual genotype; measures      genotype the lineage occupies.
                           what THIS organism can reach.      The house adjudication calls
                                                              this "the detector over-covers".
  detector exhaustiveness  EXHAUSTIVE over 1-mutants          SAMPLED, 5000 Sobol points
                           (B evaluations, B=104 or 76)
  detector statistic       FV = (rate of useful novel         chi-squared lack of fit between
                           phenotypes) x (mean phenotypic     induced phenotype distribution
                           jump), normalised by the same      and the distribution over all 8
                           over non-useful neighbours         class members; plus Shannon
                                                              entropy (16 -> 4 bits)
  longitudinal             YES, FV vs generations             YES, train/test chi-sq error
                                                              vs evolutionary time (Fig 3)
  acquisition outcome      generations AND mutations to a     generations-to-target with B
                           new goal; competition takeover     frozen and G re-randomised,
                                                              1000 runs per environment
  intervention             on the ENVIRONMENT (goal schedule; on SELECTION (K, kappa) and on
                           MVG / NBVG / FG / thermal)         REGULARISATION (lambda_L1/L2)
  train/test split         YES, but by NOVELTY CLASS rather   YES, and cleaner: an explicit
                           than by a formal split             held-out set of 5 of 8
  overfitting analysis     NONE                               YES, explicit: training error
                                                              falls while test error rises;
                                                              "early stopping would be ideal"
  replication              30-40 independent runs per         NONE STATED ANYWHERE. The
                           condition; mean +- SE; p-values    house spec records no replicate
                                                              loop in GRN.m and no uncertainty
                                                              on any longitudinal figure.
  D-level                  D0 / D1-adjacent / D4 weak         D2, D3, D4 at arm level;
                                                              not D5
  house verdict            (this file) MVG_EFFECT_IS_         KOUVARIS_STRONGER_BUT_DIFFERENT
                           AUTHORED_CURRICULUM
  key confound             plateau escape (addressed via      mediation not identified: the
                           NBVG); FG arm carried a gate       intervention changes B, and BOTH
                           penalty MVG did not                readouts are functionals of the
                                                              same frozen B, so the link is
                                                              close to definitional

================================================================================
2. IS KOUVARIS A DESCENDANT?
================================================================================

Genealogically the two programmes are the same phenomenon with different vocabulary, and
the structural correspondence is close enough to be worth stating precisely:

  MVG                                    KOUVARIS
  ------------------------------------   ------------------------------------------
  authored composition scheme            class of 8 targets defined as all
  f(g(x,y), h(w,z))                      combinations of 4 independent binary modules
  goals alternate within the scheme      3 of the 8 selected during evolution
  new-comb / novel-module goals          the 5 class members never selected for
  facilitated variation measure          chi-squared fit of the induced phenotype
                                         distribution to the class
  "generalize to new environments"       "generalisation" in the learning-theory sense
  modularity Q_m of the network          developmental organisation B

Both programmes: author a compositional family, train on a subset, test on the remainder,
and report that the evolved system reaches the unselected members faster. Kouvaris makes
the learning-theory reading explicit and adds the machinery that reading brings --
train/test error curves, overfitting, early stopping, regularisation as an intervention.

Classification, stated as the assignment requires rather than assumed:

  a conceptual descendant .................... YES
  a mechanistic extension .................... PARTLY -- it adds an explicit inductive-bias
                                               account and a regularisation intervention
                                               that MVG has no analogue for
  a different substrate realization .......... YES -- GRN with development, no population
  substantially the same phenomenon
    reframed through learning theory ......... LARGELY YES, and this is the honest headline

CITATION TRACING, resolved: the correspondence above is established STRUCTURALLY, from the
two physics specs side by side, and it REMAINS structural after a citation pass. Kouvaris
2017 cites Toussaint only inside a bulk background bracket with zero occurrences of his
name in body prose, and the same pass found co-citation-without-composition to be the norm
across this literature. The Kouvaris house spec independently records that the authors
gloss their own evolvability definition as "facilitated variation" and contrast it with
"just canalisation of past selected" phenotypes -- facilitated variation being the
framework the 2008 paper is an explicit demonstration of. That is strong indirect lineage
evidence and is not a citation check. The genealogy is therefore CONCEPTUAL AND STRUCTURAL,
asserted here on the correspondence table, not on a reference list.

Watson & Szathmary 2016, the framing paper for the Kouvaris line, does position this
lineage explicitly as the empirical precedent being re-explained rather than challenged:
"an evolved memory can, as illustrated by Parter et al., also facilitate faster adaptation
to new targets", and "evolvability is to evolution as generalisation is to learning". Their
own demonstration figure runs the alternating-goal protocol directly.

================================================================================
3. THE RECURRENCE, AND WHY IT MATTERS MORE THAN EITHER PAPER
================================================================================

The assignment asks what it means if both programmes independently demonstrate the shape

  modular environmental history -> modular/developmental representation -> future adaptation

They do. And the recurrence is more interesting than either result, for a reason neither
paper states: BOTH PROGRAMMES FOUND THE SAME BOUNDARY, and both reported it honestly.

  MVG:      "MVG's outperformance occurred only toward goals within the modularity
             language. MVG adaptation toward non-modular goals was not significantly
             different from FG's."
  KOUVARIS: the class is "defined by construction as all combinations of 4 independent
             binary modules", and generalisation is measured as fit to THAT class. There
             is no out-of-class arm at all.

And Kouvaris reports something stronger against the shared story, which the citation pass
recovered: environmental variation alone did not even reach the WHOLE AUTHORED CLASS.
Verbatim: "We find no rate of environmental variation capable of causing evolution by
natural selection to evolve a developmental organisation that produces the entire class."
Memory of past environments: obtained. Generalisation across the family: obtained only with
added noise and regularisation -- machinery MVG has no analogue for.

So MVG tested outside the authored family and found nothing; Kouvaris did not test outside
it AND could not reach all of the inside of it without extra help. Two independent
programmes, two substrates, twelve years apart, and neither one produced evidence that the
acquired bias helps against a decomposition its author did not supply. The recurrence is
not a recurrence of open-ended improvement. It is a recurrence of CURRICULUM-ALIGNED
INDUCTIVE BIAS, which is exactly what learning theory would predict and exactly what
Kouvaris says it is.

That is a stronger and more useful conclusion than either paper alone licenses, and it is
this deep-dive's principal contribution to the Historical Collider: the phenomenon has been
independently demonstrated twice, the boundary has been demonstrated once and assumed once,
and NOBODY HAS EVER TESTED TRANSFER ACROSS DECOMPOSITIONS.

================================================================================
4. WHAT EACH HAS THAT THE OTHER LACKS
================================================================================

MVG HAS AND KOUVARIS LACKS:
  - a genuinely LOCAL, individual-indexed, outbound accessibility measure. Kouvaris's
    detector over-covers: it samples what B can express from anywhere, including regions no
    lineage visits. This matters against the Q-registry definitional trap, which warns that
    inbound/global and outbound/local "accessibility" are different quantities and matching
    on the word mis-classifies work in both directions. MVG is on the correct side of that
    trap; Kouvaris is on the other side of it.
  - replication and uncertainty on every reported figure.
  - a population, hence a claim that survives without strong-selection-weak-mutation.
  - an out-of-family negative control with difficulty matching.
  - a non-modular-but-nearby control (NBVG) that dissociates the mechanism from modularity.

KOUVARIS HAS AND MVG LACKS:
  - a formal held-out set and an explicit overfitting/early-stopping analysis. MVG never
    plots a test curve against a training curve and so cannot see the moment at which
    specialisation begins to cost.
  - regularisation as a direct intervention on the bias.
  - a mediation critique already written against itself (both readouts are functionals of
    the same frozen B).
  - recovered author source code. MVG has none; no code availability statement exists in
    any of its three papers.

================================================================================
5. CONSEQUENCE
================================================================================

Ergon's verdict on Kouvaris was KOUVARIS_STRONGER_BUT_DIFFERENT with D3 outright and D4 at
arm level. This deep-dive reaches D4-weak for Parter 2008 on a LOCAL detector with
replication, which on the accessibility axis specifically is at least as strong and
arguably stronger.

The Historical Collider should therefore stop treating the local-longitudinal-accessibility
cell as empty. It has been occupied since 2008, by an experiment with a non-tautological
intervention, exhaustive one-step neighbourhoods, and 30-40 replicates. What remains empty
is the cell above it: nobody, in either lineage, has perturbed accessibility itself and
measured what was subsequently acquired.
