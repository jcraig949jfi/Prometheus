# DESCENDANTS, CORRECTIONS AND REPLICATION STATUS

Filed 2026-09-03, after the citation-archaeology pass returned. This file exists because
the deep-dive's other deliverables were drafted while it was still open, and its result is
strong enough to change how the specimen may be used.

Provenance note: the items below were verified from raw PDFs by text extraction, not from
summarising fetches. Two items that an earlier pass had flagged as challenges are
explicitly REMOVED as challenges here.

================================================================================
1. THE FAILED REPLICATION -- the strongest item against the lineage
================================================================================

Clune J, Beckmann BE, McKinley PK, Ofria C (2010). "Investigating Whether HyperNEAT
Produces Modular Neural Networks." GECCO '10, 635-642.
Retrieved: https://cse.msu.edu/~ofria/pubs/2010CluneEtAl.pdf (HTTP 200, 5.87 MB)

This is a direct attempt at Kashtan & Alon's RETINA problem, and it included a DIRECT
ENCODING CONTROL, which is what makes it a replication failure rather than a note that a
different representation behaved differently. Verbatim:

  "We tested whether HyperNEAT and a direct encoding control produce modular ANNs on a
   problem that has previously been shown by Kashtan and Alon [13] to generate modular ANNs
   with a different direct encoding neuroevolution algorithm. In contrast to those results,
   this problem did not encourage modularity in the direct encoding we tested, raising a
   question about the generality of Kashtan and Alon's results."

  "More important than the absolute difference between Kashtan & Alon's results and those
   of HyperNEAT and FT-NEAT is the qualitative difference: the MVG regimes performed worse
   than the FG-AND regime, which was the opposite of what occurred in Kashtan and Alon's
   study. Our result raises questions as to the generality of Kashtan and Alon's discovery
   that environments with MVG will generate the evolution of modular networks. While there
   are differences between Kashtan and Alon's experimental setups and our own, the
   differences are relatively small and should not preclude such a seemingly general
   result."

THE SIGN REVERSED. MVG did not merely fail to help; it did worse than the fixed goal.

Confounds they closed: both switching rates including Kashtan's own E = 20 (MVG-20 and
MVG-100, with faster and slower rates reported as "not qualitatively different"), 20 runs
per treatment, population 500, and runs extended to 30,000 generations with no qualitative
change.

THEIR DIAGNOSIS, which is the most useful thing in this file for Prometheus:

  "it appears that their inputs and outputs were binary, the activation functions of their
   neurons were step functions with only three possible thresholds, and their link weights
   consisted of a small set of discrete values. ... These differences, while seemingly
   minor, may explain the different qualitative results we observe"

  "One candidate explanation is that Kashtan and Alon's experiments have a smaller search
   space. ... Mutations between a few discrete values may have a larger effect on the
   network output, making it more likely that single mutations can switch between a
   solution to FG-OR and FG-AND. ... If such a switch requires multiple mutations in our
   implementation, or a single rare mutation, evolution may be unlikely to benefit from
   modular phenotypes because it cannot quickly rearrange modules."

Read that against the NBVG finding in CAUSAL_INTERVENTION_MAP.md section 2b. The two
converge on the SAME mechanism from opposite directions. Kashtan's own supplement says the
effect requires successive goals to have adjacent solution sets. Clune et al. say the
effect disappears when the encoding makes a one-mutation switch between goals unlikely.
These are the same statement. The MVG effect is a property of GENOTYPE-SPACE PROXIMITY
between successive objectives, and a representation that widens the gap destroys it.

AND A REPRODUCIBILITY ADMISSION, from the group that went on to lead this area:
  "the description of their model is not complete"
This is a 2010 statement that the 2005 paper could not be exactly reproduced from its own
text. It corroborates, from outside, this deep-dive's finding that the genotype-phenotype
map is UNSPECIFIED in the open record and that no code was ever released.

SCOPE LIMIT, and it cuts both ways: this is the RETINA / NEURAL NETWORK arm only.
Verbatim: "We chose their second problem as the test problem in this paper because
HyperNEAT was designed to evolve neural networks."

  *** THE NAND LOGIC-CIRCUIT ARM HAS NEVER BEEN INDEPENDENTLY REPLICATED OR REFUTED. ***

That is the arm carrying every accessibility result in this deep-dive. A second,
non-peer-reviewed failure (a 2022 Alignment Forum modularity project) reports the same
direction -- "Networks evolved to be non-modular messes both for fixed goals and Modularly
Varying Goals" -- and also skipped the circuit arm; it is corroboration of direction only.

Also confirmed independently by Clune et al.: Kashtan's retina FG time is "a median of
21,000 generations ... nearly an order of magnitude slower" than MVG. The real effect size
is ~10x, matching the worked example in the 2007 paper, NOT the headline 700x, which is
S_max conditioned on the hardest goals only.

================================================================================
2. TWO ITEMS THAT MUST NOT BE CITED AS CHALLENGES
================================================================================

REMOVED: Hintze & Adami 2008 (PLoS Comput Biol 4:e23). It reports lower modularity in
dynamic environments, but the authors explicitly disclaim it as a test of MVG, verbatim:
"Our dynamic environments change randomly, whereas Kashtan and Alon's environment changes
in a modular fashion, rewarding one or the other function in turn." Random variation is
precisely the condition Kashtan & Alon predicted would fail. This is a CONSISTENCY, not a
contradiction, and citing it as a challenge would be an error.

REMOVED: Crombach & Hogeweg 2008. Verified to contain zero occurrences of "modular" or
"module" in the body text and no sub-goal decomposition. Not a test of this claim.

Recording these two removals matters as much as recording the positive finding. An
adversarial review that accumulates anything sounding negative is not adversarial, it is
motivated.

================================================================================
3. THE LINEAGE'S OWN DESCENDANT REPORTS A NEGATIVE ON GENERALISATION
================================================================================

Kouvaris et al. 2017 -- the learning-theory reframing of exactly this phenomenon -- reports
that it could NOT obtain the generalisation result from environmental variation alone:

  "We find no rate of environmental variation capable of causing evolution by natural
   selection to evolve a developmental organisation that produces the entire class."

Memory of past environments: yes. Generalisation to the whole family: only with added
noise and regularisation.

This is decisive for the recurrence argument in MVG_VS_KOUVARIS_MATRIX.md and it makes
that argument STRONGER, not weaker. Two programmes, two substrates, twelve years apart:
the first found that generalisation stops at the edge of the authored language, the second
found it could not reach the whole authored language at all without extra machinery. In
neither case does structured environmental variation alone buy an expanding accessible
future.

================================================================================
4. REPRESENTATION-DEPENDENCE, CONCEDED BY THE ALON LAB
================================================================================

Friedlander et al. 2013 (Alon lab): with sum-rule mutations -- the mutation rule used in
Kashtan's own work -- modular goals "generally do not" produce modularity.

Combined with Clune et al. 2010, the picture is that the MVG-to-modularity effect is
strongly conditional on the mutation rule and the discreteness of the representation, and
that at least one of those conditions was never stated in the original papers.

Espinosa-Soto 2018 independently corroborates this deep-dive's decay finding: "Once
fluctuations stop, modularity drops abruptly."

Takemoto (2013, 2016): the field/biological evidence for the MVG account failed
replication twice; the proposed real driver is gene-duplication frequency.

MVG is also not necessary for modularity: four independent alternative routes exist,
including the connection-cost mechanism already on the house calibration set as cal-09.

================================================================================
5. THE TOUSSAINT COMPOSITION -- ASSERTED IN PRINT, NEVER RUN
================================================================================

The composition question is answered better than "not found".

Fernando C, Szathmary E, Husbands P (2012). "Selectionist and Evolutionary Approaches to
Brain Function: A Critical Appraisal." Front Comput Neurosci 6:24. Verbatim:

  "Parter et al. (2008) show that under certain conditions variation becomes facilitated:
   random genetic changes can be unexpectedly more frequent in directions of phenotypic
   usefulness. This occurs when different environments present selective goals composed of
   the same subgoals, but in different combinations. Evolving replicator populations can
   'learn' about the deep structure of the landscape so that their variation ceases to be
   entirely 'random' in the classical neo-Darwinian sense. This occurs if there is
   non-trivial neutrality as described by Toussaint (2003) and demonstrated for gene
   regulatory networks (Izquierdo and Fernando, 2008)."

Their reference list carries Toussaint's 2003 PhD thesis -- the same artifact the house
Toussaint specimen is built on.

So the composition Prometheus registered as a candidate is a STATED-BUT-UNTESTED HYPOTHESIS
in the published literature: Toussaint's non-trivial neutrality is asserted as the ENABLING
CONDITION for the Parter/Kashtan/Alon effect, and the demonstration offered is a different
paper on a different substrate. Nobody ran it on Kashtan/Alon's systems.

Near-miss checked and rejected: Reisinger & Miikkulainen 2006 "Selecting for Evolvable
Representations" cites both and generalises Kashtan's varying fitness function, but
Toussaint appears nowhere in its prose -- only as a reference, and for a different work.
Co-citation without composition was also confirmed in Kouvaris et al. 2017 and Watson &
Szathmary 2016: both cite Toussaint only inside bulk background brackets, with zero
occurrences of his name in body prose.

Residual uncertainty, stated: a full forward-citation sweep of the thesis was blocked by
HTTP 429, so a composition could hide in an unindexed conference paper.

Watson & Szathmary 2016, now retrieved in full via an open repository copy, positions this
lineage as the empirical precedent being re-explained rather than criticised: "evolvability
is to evolution as generalisation is to learning", and "an evolved memory can, as
illustrated by Parter et al. [8], also facilitate faster adaptation to new targets". Their
own figure runs the alternating-goal protocol directly.

================================================================================
6. CONSEQUENCES FOR THIS DEEP-DIVE
================================================================================

C1. THE VERDICT IS UNCHANGED. MVG_EFFECT_IS_AUTHORED_CURRICULUM rests on Figure 6E and the
    NBVG control, both in the 2008 circuits arm, both verified from retrieved bytes.
    Nothing here touches them. If anything, item 3 strengthens it.

C2. THE CALIBRATION PROPOSAL IS DOWNGRADED. A calibration particle requires a KNOWN
    treatment effect. The only independent replication attempt of any arm of this specimen
    reversed the sign, and the arm that carries the accessibility results has never been
    tested by anyone. SFE_MVG_CALIBRATION_PROPOSAL.md is amended accordingly: cal-08
    cannot be used to pass or fail a detector until the circuit arm is reproduced in house.

C3. A NEW AND BETTER TARGET APPEARS. The circuit arm is the open question in the field, not
    merely in Prometheus. Third-party reimplementations exist and report supporting results
    but are not peer-reviewed. A careful in-house reproduction of the NAND circuit arm would
    be a contribution to the external literature and not only to our own calibration -- the
    first independent test of the arm that everything rests on.

C4. THE MECHANISM CLAIM IS STRENGTHENED, NOT WEAKENED. Clune et al.'s diagnosis
    (discreteness, one-mutation switchability) and Kashtan's own NBVG control
    (goals with adjacent neutral networks) are the same finding reached independently. The
    part registered as PART-MVG-06 now has external corroboration from a paper that was
    trying to refute the lineage.
