# INTERPOLATION / EXTRAPOLATION ANALYSIS

Two jobs: freeze what "faster evolution" historically meant, and classify how novel the
future targets actually were. Both are done against retrieved text only.

================================================================================
1. THE FROZEN HISTORICAL METRIC
================================================================================

"Faster evolution" is not one metric across this lineage. Freezing each:

  2005  GENERATIONS TO A PERFECT SOLUTION, from an initially random population, with
        success rate reported alongside (36/50 FG vs 50/50 MVG). Not mutations, not
        evaluations.

  2007  T = GENERATIONS until fitness = 1, censored at G_max ("If the fitness was not
        achieved in G_max generations, T was set at G_max"). Speedup S = T_FG / T_MVG.
        Headline figures use S_max, defined over THE HARDEST GOALS ONLY -- "all goals
        with T_FG > G_max/2". This is a conditioned subpopulation. Quoting "700x" without
        that condition is a wrong-population error of the kind this programme's own
        doctrine names.
        Note the censoring interacts with the conditioning: goals where FG never solved
        get T_FG = G_max, a floor on the true FG time, so S_max is a LOWER bound on the
        hardest goals and the ratio's denominator distribution is truncated. The papers
        do not discuss this.

  2008  Three distinct readouts, and they are not interchangeable:
        (i)  generations to adapt to a new goal;
        (ii) NUMBER OF MUTATIONS -- "require about five times more mutations on average";
             adaptation to previously seen goals is "usually only 1-2 mutations" and
             "often within a single generation";
        (iii) COMPETITION OUTCOME -- fraction of runs in which MVG genomes take over a
             mixed population (~70% on novel-module goals; 50% on random goals).

  Not used anywhere in the retrieved corpus: fitness evaluations as a budget unit, path
  length in genotype space, final fitness at a fixed budget, or immediate zero-shot
  performance on a new target. The systems always re-evolve; nothing is measured
  zero-shot.

The metric that matters most for Prometheus is (ii). "One to two mutations, often within a
single generation, for a phenotypic change of about half the truth table" is a statement
about the STEP SIZE of useful change, and it is the historical quantity closest to
cost-of-acquisition.

================================================================================
2. TARGET NOVELTY CLASSIFICATION
================================================================================

Using the four types as issued:

  TYPE I   new combinations of already experienced subproblems
           -> TESTED. This is the "new-comb" class, verbatim: "a goal that presents
              previously seen subgoals but in a new combination".
           -> RESULT: MVG faster, IN BOTH SUBSTRATES. "the descendants of MVG-evolved
              genomes took over the population in about 68% of the RNA model runs ...
              Logic circuits showed similar behavior, where MVG-genomes took over the
              population in about 75% of the runs".

  TYPE II  novel variations within the same structural family
           -> TESTED. This is the "novel-module" class: "goals where one of the subgoals
              is a previously unseen one, while the other subgoals are kept unchanged",
              e.g. replacing a XOR module by a previously unseen AND or NOR.
           -> RESULT: SUBSTRATE-SPLIT, and this is load-bearing. In logic circuits, MVG
              faster across 20 novel-module goals, 30 simulations each, ~70% competition
              takeover, and "the harder the novel-module goal (the more generations needed
              to solve it 'from scratch'), the more MVG organisms out-perform FG
              organisms". In RNA: "the RNA model did not show a significant difference
              between FG and MVG genomes."
           -> NOTE: this class contains genuinely unseen functional content. It is not
              recombination. It is new filler in an old slot. But the positive result
              exists in ONE of the two substrates only.

  TYPE III targets containing genuinely new functional structure
           -> NOT TESTED as a family. No experiment presents a target requiring a
              different arity, a different input partition, or a different slot topology
              from the training language. Searched for; absent.

  TYPE IV  out-of-family targets
           -> TESTED, and this is where the effect dies. Random 4-input 1-output truth
              tables, difficulty-matched. Verbatim: "MVG adaptation toward non-modular
              goals was not significantly different from FG's."

================================================================================
3. GENERALISATION REGIME -- THE ADJUDICATION
================================================================================

  INTERPOLATION                      ESTABLISHED (Type I, new-comb)
  COMPOSITIONAL EXTRAPOLATION        ESTABLISHED (Type I and the recombination half of
                                     Type II)
  STRUCTURAL EXTRAPOLATION           PARTIAL, and this is the contested cell.
                                     Type II introduces structure never seen -- a new
                                     Boolean primitive -- and MVG acquires it faster.
                                     But the structure enters through a slot the
                                     experimenter fixed. The compositional scheme does
                                     not extrapolate; only its contents do.
                                     Recorded as: CONTENT-LEVEL STRUCTURAL EXTRAPOLATION
                                     WITHIN A FIXED SCHEME. Not credited as full
                                     structural extrapolation, because the null at
                                     Type IV shows the scheme is doing the work.
  OPEN-DIMENSION INNOVATION          NOT ESTABLISHED, and evidenced against. Figure 6E
                                     is the direct measurement: outside the authored
                                     language there is no advantage at all.

The programme therefore establishes a strictly bounded generalisation: cheap acquisition
of novel content inside an authored compositional scheme, and nothing beyond it.

================================================================================
4. WHY THE TYPE II RESULT MUST NOT BE OVERSOLD OR UNDERSOLD
================================================================================

Undersold version, which this review rejects: "MVG only recombines modules it was taught."
False. A previously unseen 2-input Boolean function is acquired faster, and the harder the
novel module, the larger the advantage.

Oversold version, which this review also rejects: "MVG organisms generalise to novel
environments." The paper's title says "generalize to new environments" and the abstract
says organisms "generalize to future environments, exhibiting high adaptability to novel
goals". Taken alone that phrasing licenses a far broader reading than Figure 6E supports.
The qualifier "within the modularity language" appears in the results and not in the
abstract. This is a real gap between headline and boundary condition, and it is the single
most likely route by which a downstream reader inherits an inflated version of this result.

The accurate compression, for reuse in Prometheus documents:

  MVG-evolved organisms acquire novel FUNCTIONAL CONTENT more cheaply, provided the new
  target decomposes the same way their history did. The saving is in the module, not in
  the architecture. When the decomposition changes, the saving is zero.

================================================================================
5. WHAT WOULD HAVE TO BE SHOWN FOR OPEN-DIMENSION INNOVATION
================================================================================

A target family whose decomposition is not the training decomposition, with the advantage
surviving. Concretely, in the historical substrate and affordable at its scale:

  train on   u = f(g(x,y), h(w,z))          partition A
  test on    u = f(g(x,w), h(y,z))          partition B, same operators, same arity
             and separately, a 3-module or different-arity family

If MVG organisms retain an advantage on partition B, the system learned to decompose. If
they do not -- which this reviewer expects, given Figure 6E -- the system learned THIS
decomposition, and the phenomenon is correctly named facilitated reuse under authored
structure. Either result is publishable inside Prometheus and neither has been run.
