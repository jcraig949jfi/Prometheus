# FAILURE DATA RECOVERY

Where the mechanism failed to produce future adaptability. Assembled deliberately against
the grain of the papers' own narratives, from retrieved text only. For Daedalus this is
likely more useful than the success case, because it bounds the world-physics regime in
which the effect exists at all.

================================================================================
1. OUTRIGHT SLOWDOWNS -- varying environments making things WORSE
================================================================================

The 2007 Table 1 contains more sub-1.0 entries than above-1.0 entries once MVG is set
aside. S_max < 1 means the varying regime was SLOWER than a fixed goal on the hardest
goals.

  RVG_c (random goal, constant per run): <1 in models 1, 3, 4, 5; 1.3 +- 0.3 in model 2.
    Four outright slowdowns out of five substrates.
  VG_0 (alternation with no selection): <1 in RNA; 1.5 +- 1 in neural nets (indistinct
    from no effect).
  RVG_v: <1 in RNA.

RNA IS THE STANDOUT FAILURE SUBSTRATE. Verbatim: "Under MVG, the fitness increased
significantly faster than under a fixed goal ..., whereas all other scenarios showed
slowdown (Table 1)." In RNA secondary structure, EVERY form of environmental variation
except the modular one made evolution slower than a fixed goal, and even MVG's advantage
was the smallest of the five substrates (25x against 60-700x elsewhere).

Reading: environmental variation is not generically beneficial. In a substrate with a
rugged, highly epistatic genotype-phenotype map, it is generically HARMFUL, and only the
precisely structured form survives.

================================================================================
2. CONFUSION -- environments that destroy the ability to solve anything
================================================================================

Verbatim (2008): "We find that an environment that varies between randomly chosen goals
typically causes confusion, where no good solution is found that can rapidly adapt to both
goals."

Verbatim (2005): under randomly varying goals "the networks take a relatively long time to
adapt to the new goal, as if it starts evolution from scratch."

There is also a partial escape clause the 2008 authors state honestly: "It is possible,
however, to find pairs of goals which are not modular and yet which have soluti[ons] ..."
-- i.e. non-modular goal pairs can still admit shared solutions. The modular decomposition
is a SUFFICIENT way to get shared substructure, not the only way. Nobody characterised the
general condition.

FOR DAEDALUS: the failure mode of a badly-tuned varying world is not slow progress, it is
NO PROGRESS AT ALL. A world that switches between unrelated objectives produces populations
that never converge on anything. This is a distinct failure from mere inefficiency and it
should be detectable early.

================================================================================
3. FAILURE OF THE FIXED-GOAL ARM TO SOLVE AT ALL
================================================================================

2005, verbatim: perfect solutions found in "36 of 50 experiments" under FG, against
"all 50 experiments" under MVG. Fourteen fixed-goal runs never reached the goal within the
run cap.

This is a censored-data problem that propagates into 2007's headline metric: T is set to
G_max when the goal is not achieved, and S_max is computed only over goals with
T_FG > G_max/2. The FG denominator is therefore truncated from above, making the reported
speedups LOWER bounds on the hardest goals -- but also making the comparison one between a
measured quantity and a censored one. Neither paper discusses the censoring. Recorded as a
methodological weakness rather than an error.

================================================================================
4. MECHANISM LEGS THAT FAILED
================================================================================

F1. REDUCED LETHALITY DID NOT HOLD. Facilitated variation theory predicts three mutational
    properties. The paper tested all three and reported, verbatim: "MVG organisms in the
    present study follow the first two mechanisms, but not the third." The third is
    reduced mutational lethality / increased viable genetic variance. A named prediction
    of the framework failed in the framework's own showcase system.

F2. PLEIOTROPY REDUCTION DID NOT REPLICATE IN RNA. Table 1 inter-module effect: circuits
    0.04 -> 0.01 at p<1e-4; RNA 0.057 -> 0.053, NOT SIGNIFICANT. The authors report this
    plainly: "logic circuits showed more reduced pleiotropy, and RNA structures primarily
    showed more enhanced intra-module change." The mechanism is substrate-specific.

F3. THE RNA NOVEL-MODULE RESULT WAS NULL, and the failure is specific. Verbatim: "We
    also tested novel-module goals. Here, the RNA model did not show a significant
    difference between FG and MVG genomes. However, in the logic circuit model,
    MVG-populations adapted significantly faster also to novel-module goals."
    Precision matters here. The two novelty classes come apart by substrate:
      new-comb (recombination of seen subgoals): worked in BOTH -- MVG descendants took
        over in ~68% of RNA runs and ~75% of logic-circuit runs.
      novel-module (a previously unseen subgoal): worked in CIRCUITS ONLY (~70% takeover),
        NULL in RNA.
    So the weaker claim (recombination is cheaper) is two-substrate; the stronger claim
    (novel content is cheaper) rests on ONE substrate. Every use of this lineage to argue
    that MVG buys acquisition of genuinely new functional content is standing on the
    logic-circuit model alone.

F4. THE OUT-OF-LANGUAGE NULL. Already central elsewhere in this deep-dive: no advantage
    on difficulty-matched non-modular goals, and 50/50 competition outcomes.

================================================================================
5. THE PROPERTY IS LOST WHEN THE PRESSURE STOPS
================================================================================

Two decay experiments, one per paper:

  2005 Fig 3: an initially modular circuit loses modularity under a fixed goal within a
  few tens of generations.
  2008 Fig 9D: "Facilitated variation rapidly decays when goal becomes constant over
  time", starting from an end-of-MVG population at perfect fitness.

Neither the structure nor the accessibility property is retained without continued
environmental support. For a programme interested in compounding, this is the most
important failure in the corpus: the mechanism has NO MEMORY BEYOND THE PRESSURE THAT
CREATED IT. Anything built on it must supply its own persistence.

================================================================================
5b. THE FAILURE OUTSIDE THE CORPUS -- an independent replication reversed the sign
================================================================================

Added after the citation-archaeology pass; full treatment in
DESCENDANTS_AND_REPLICATION.md. Recorded here because it is the largest failure
associated with this specimen and this is the failure file.

Clune, Beckmann, McKinley & Ofria 2010 (GECCO '10, 635-642) attempted the RETINA arm with
a direct-encoding control and found "the MVG regimes performed worse than the FG-AND
regime, which was the opposite of what occurred in Kashtan and Alon's study." They tested
Kashtan's own switching rate, faster and slower rates, 20 runs per treatment, and ran to
30,000 generations.

Their attribution is a failure-mode statement Daedalus should treat as a world-design
constraint: the effect may require an encoding in which A SINGLE MUTATION CAN SWITCH
BETWEEN SOLUTIONS TO THE TWO GOALS. With continuous weights, if "such a switch requires
multiple mutations ... evolution may be unlikely to benefit from modular phenotypes because
it cannot quickly rearrange modules."

So the failure mode is: BUILD THE SAME WORLD WITH A FINER-GRAINED REPRESENTATION AND THE
EFFECT DIES. That is a sharper and more actionable failure than any inside the original
corpus, and it converges exactly with the NBVG finding -- both say the operative condition
is genotype-space proximity between successive objectives, not modular decomposability.

The NAND circuit arm, which carries every accessibility result, has never been
independently tested at all.

================================================================================
6. WHAT WAS NEVER OBSERVED BECAUSE IT WAS NEVER LOOKED FOR
================================================================================

Absent from the retrieved corpus, searched for explicitly:
  - any report of individual failed lineages or trapped subpopulations within a run
  - any per-run variance decomposition (only means +- SE across runs are given)
  - any analysis of runs where MVG performed worse than its own mean
  - any environmental schedule reported as destroying modularity other than the constant
    goal
  - any target family on which faster short-term adaptation later harmed transfer

The last one matters: the "fast now, worse later" failure the assignment asks about is
NOT in the record because no experiment measured adaptation twice in sequence. Every
transfer test in the corpus is single-step: evolve under a regime, then present one new
goal. There is no second hop. A lineage that adapts quickly to goal 2 and is thereby
crippled for goal 3 would be invisible to every experiment in this programme.

REGISTERED AS THE PROGRAMME'S BLIND SPOT: single-step transfer only. Prometheus should run
at least two sequential acquisitions before claiming anything about compounding, because
this lineage cannot have detected a compounding failure even if one occurred.
