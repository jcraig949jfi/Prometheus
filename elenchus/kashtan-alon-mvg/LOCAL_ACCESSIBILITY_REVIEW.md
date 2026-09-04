# LOCAL ACCESSIBILITY REVIEW

The question this file exists to answer: did the Kashtan/Alon programme ever measure the
distribution of phenotypes reachable from a current genotype under its actual variation
operator -- or did it only measure modularity and adaptation speed and infer the rest?

The answer is not the one the Prometheus working hypothesis assumed. It was measured, it
was measured well, and it was measured longitudinally.

================================================================================
1. THE FINDING
================================================================================

Parter, Kashtan & Alon 2008 measured single-mutation phenotypic neighbourhoods directly.
Verbatim, from the retrieved publisher XML:

  "we considered the phenotypic neighborhood [37]-[39], defined as the set of phenotypes
   that are accessible from a given genotype by a single point mutation."

  "The genetic neighborhood is defined as the set of all genomes different in one
   position from the wild type genomes."

This is the adjacent-possible measurement, under the system's own variation operator, at
the level of the phenotype rather than the genotype. It is not an analogy to what HC-T01
proposes to measure. It is the same measurement.

They then went further and built a scalar summary of it, the facilitated variation (FV)
measure, verbatim:

  "The 'quantity' component is the probability of forming a potentially useful phenotype
   which is novel by a single point mutation; the 'quality' component is the average
   phenotypic distance between the wild-type and the potentially useful phenotypes
   within its phenotypic neighborhood. This measure is then normalized for its
   corresponding value with respect to non-useful neighboring phenotypes."

So: FV = (rate of useful novel phenotypes per mutation) x (mean phenotypic jump distance),
normalised against the same product computed over non-useful neighbours. Its exact
algebra lives in Text S1 section 8.1, which we do not hold -- flagged as a gap.

================================================================================
2. IS IT LONGITUDINAL?
================================================================================

Yes, and this was the single most surprising recovery of this deep-dive. From the Figure 9
legend, verbatim:

  "(C) Facilitated variation measure (mean+-SE) as a function of generations in logic
   circuits evolution."

  "Mean FV measure (+-SE) vs. generations of 500 best-fitness circuits in each population
   is shown. Statistics are for 30 independent experiments."

  "We find that the FV measure increases with generations under both FG and MVG evolution
   (Figure 9B and 9C ...). However, it increases significantly more under MVG."

Classification against the ladder in the assignment:

  NOT_MEASURED               ruled out
  SELECTED_INDIVIDUALS_ONLY  exceeded -- 500 best-fitness circuits per population, not
                             one wild type
  POPULATION_SNAPSHOT        exceeded -- it is a trajectory, not a snapshot
  LONGITUDINAL               YES. FV is plotted against generation across 30-40
                             independent runs, separately per condition.
  LINKED_TO_ACQUISITION      YES, but between-condition. The same paper shows MVG
                             populations adapt faster to novel-module goals (Figure 6D).
                             What is NOT shown is a within-run coupling: no analysis
                             asks whether the runs with the larger FV rise are the runs
                             that later adapt fastest. The link is at the level of the
                             treatment arm, not the individual lineage.
  CAUSALLY_PERTURBED         PARTIAL, and only on the environmental cause -- never on
                             the accessibility mediator. See section 4.

The honest one-line classification: LONGITUDINAL and LINKED_TO_ACQUISITION AT THE ARM
LEVEL, with the mediator never perturbed.

================================================================================
3. WHAT THE ACCESSIBILITY MEASUREMENT ACTUALLY SHOWED
================================================================================

Three separate results, all verified:

(a) MEMORY IN THE NEIGHBOURHOOD. "the phenotypic neighborhood of MVG-evolved genomes
    includes phenotypes that have high fitness to the past goals seen in their history
    ... This indicates that the evolved organism effectively remembers its past goals by
    storing information about it in its genome." The neighbourhood is not merely larger;
    it is stocked with specific, previously rewarded phenotypes.

(b) STRUCTURED MUTATIONAL EFFECTS. Table 1, verified exactly:

      quantity                     logic circuits            RNA
                                   FG        MVG    p        FG         MVG     p
      Intra-module effect        0.12+-.002 0.14+-.001 <1e-4  0.28+-.007 0.36+-.005 <1e-9
      Inter-module (pleiotropy)  0.04+-.005 0.01+-.001 <1e-4  0.057+-.005 0.053+-.005 NS

    MVG mutations act more strongly inside their own module and, in circuits, far less
    across modules. Note the RNA pleiotropy column is NOT SIGNIFICANT. The mechanism is
    substrate-dependent and the authors say so: "logic circuits showed more reduced
    pleiotropy, and RNA structures primarily showed more enhanced intra-module change."

(c) A NAMED CONTROL MECHANISM THAT FAILED. Facilitated variation theory predicts three
    things; the paper tested all three and reported that only two held, verbatim: "MVG
    organisms in the present study follow the first two mechanisms, but not the third."
    The third was reduced mutational lethality / increased viable genetic variance. This
    is a negative result the programme published against its own framework, and it is
    the kind of thing a review packet should carry forward rather than quietly drop.

================================================================================
4. THE PERTURBATION QUESTION
================================================================================

Two things in the corpus look like interventions. Only one of them is one, and neither is
the one that would close the causal chain.

INTERVENTION THAT EXISTS (2008, Figure 9D), verbatim:
  "Facilitated variation rapidly decays when goal becomes constant over time. Each
   simulation started from end-of MVG evolution population that had perfect fitness for
   the goal G1. At the generation marked zero, the population was placed [under a
   constant goal]"
This takes an MVG-evolved population and removes the varying environment. The
accessibility property then decays. It is a real manipulation and it establishes that FV
is actively MAINTAINED by the environment rather than being a one-way ratchet. The 2005
paper has the structural twin of this experiment: seed a modular circuit, apply a fixed
goal, and modularity decays within a few tens of generations.

INTERVENTION THAT DOES NOT EXIST: nothing perturbs the accessibility structure itself and
then measures acquisition. Specifically, the "genetic triggers" -- the genomic positions
identified by high mutual information with the goal -- are found observationally, verbatim:

  "The genetic triggers can thus be detected by evaluating the mutual information between
   the environment (goal) and the genomic content at each position ... Trigger positions
   were readily detected for all MVG cases tested."

They are never knocked out, frozen, randomised, or transplanted. There is no experiment of
the form: take an MVG genome, destroy its triggers while holding fitness and modularity
constant, and show that fast adaptation disappears. Without that, the claim "the enriched
neighbourhood causes the fast adaptation" remains an inference from co-occurrence, however
well-motivated.

This is precisely the gap that separates D4 from D5.

================================================================================
4b. THE THREE-ARM ACCESSIBILITY COMPARISON (recovered from Text S1)
================================================================================

The main text compares accessibility between MVG and FG only. The supplement adds a third
arm and it changes the interpretation. Sections 2.1 and 2.2 of Text S1 construct
non-modular varying environments -- NBVG for circuits, thermal fluctuation for RNA -- and
Figures S3 and S4 report the accessibility measurements across all three regimes.

Measured ordering of the FV measure, verbatim: structured modular variation gives high
facilitated variation; "Environments that change in a more random fashion evolve organisms
with a more random, un-biased phenotypic variation, with very low FV measures"; and
"environments that do not change at all (FG) evolve organisms with a medium level of
facilitated variation (due to increased in robustness)."

    MVG  (structured variation)   HIGH FV
    FG   (no variation)           MEDIUM FV
    NBVG (unstructured variation) VERY LOW FV

This is non-monotonic in environmental variability, and it is the strongest evidence in
the corpus that STRUCTURE rather than CHANGE builds the biased neighbourhood. It also
disposes of the obvious objection that the MVG neighbourhood is enriched simply because
MVG populations were exposed to more distinct selective regimes: NBVG populations were
too, and their neighbourhoods came out less biased than populations that saw one goal
forever.

Crucially, the same supplement shows MVG and NBVG SHARE the rapid-adaptation machinery
(neutral-network-border positioning plus genetic triggers, Fig S3) while DIFFERING on
neighbourhood composition and FV (Fig S4). The two-layer reading this forces is developed
in CAUSAL_INTERVENTION_MAP.md section 2b.

Section 7 of Text S1 is titled "Complete characterization of evolved phenotypic
neighborhoods" and reports the composition directly: "the neighborhood of MVG-circuits is
enriched (relative to FG) with circuits that compute decomposable Boolean functions ...
We also find that FG neighboring circuits are significantly less modular."

An earlier draft of this review recorded the absence of an unstructured-variation arm as
the corpus's most serious unaddressed confound. That was an error of retrieval, not of
reasoning, and it is corrected in place in CAUSAL_INTERVENTION_MAP.md rather than removed.

================================================================================
5. THE ONE CONTROL THAT DOES ISOLATE HISTORY
================================================================================

The programme did run a history-free, phenotype-matched control, and an earlier automated
reading of this paper wrongly reported that it had not. Verbatim:

  "(B) Facilitated variation measure (mean+-SE) in RNA model of MVG, FG and a random
   class of inverse-fold genomes (genomes generated by an algorithm to yield a desired
   fold) with G1 structure. Data are from 30 simulations in the case of FG and MVG and
   200 random genomes."

  "The random class (dashed line) includes circuits which achieve the goal but were
   generated by an optimization algorithm rather than by an evolutionary process
   (see Text S1 section 3.1)."

This is the right shape of control and it is rare in this literature: same phenotype,
same goal satisfied, no evolutionary history. It separates "being a circuit that computes
G1" from "being a circuit that arrived at G1 through a particular history". Prometheus
should inherit this control design directly; it is the cheapest available defence against
the objection that any structural property is just a consequence of solving the task.

Its limit: it controls for history-vs-no-history, not for structure-vs-history. It does
not construct a non-evolved genome MATCHED ON MODULARITY to the MVG genome. So it cannot
separate "modularity causes the neighbourhood enrichment" from "history causes both".
That distinction is exactly the one raised in section 10 of the assignment and it remains
open in the historical record.

================================================================================
6. WHAT 2005 AND 2007 DID NOT MEASURE
================================================================================

2005: no accessibility measurement of any kind. Searched the retrieved full text for
mutational neighbourhood, offspring distribution, one-mutant, reachable phenotype, neutral
network. Absent. The paper measures a network-structural state variable (Q_m), a motif
profile, and time-to-solution. D0.

2007: no per-genotype offspring distribution. What it has instead is stronger than nothing
and weaker than a neighbourhood measurement: the fitness landscape of a 4-input version of
model 2 was FULLY MAPPED, and the local fitness gradient at the population's location was
characterised after each goal switch. That is a statement about where the population
stands in a landscape, not about what its variation operator emits. It supports a claim
about ACCESSIBILITY OF FITNESS IMPROVEMENT, not about the diversity or novelty of the
reachable phenotype set. Classified D1-adjacent and argued in D_LEVEL_ADJUDICATION.md.

================================================================================
7. CONSEQUENCE FOR PROMETHEUS
================================================================================

On the INSTRUMENT axis, HC-T01 is substantially preempted. The single-mutation phenotypic
neighbourhood, the useful/non-useful normalisation, the intra-module vs pleiotropy
decomposition, and the mutual-information trigger detector are all prior art with
published definitions, and the FV trajectory is prior art for the longitudinal form. A
Prometheus detector that measures "the local adjacent possible" and does not cite this
work is reinventing a 2008 instrument.

On the PHENOMENON axis it is not preempted, for one reason only, developed in
INTERPOLATION_EXTRAPOLATION_ANALYSIS.md: the enriched neighbourhood buys nothing outside
the goal family the experimenter authored. The instrument is inheritable. The result is
bounded.
