# HC-R01 CORRECTION NOTICE

**Issued 2026-09-03, after the neutral-network lane returned its full report and
after reading two sibling-seat commits that were already in this branch's history
when HC-R01 began and that this seat did not read.**

Three corrections. Two are to claims in
`HC_R01_RESEARCH_REVIEW_PACKET.txt`. One is to the EvCA design note. All three
are downgrades or reversals of things this seat asserted.

---

## CORRECTION 1: the MVG line DID measure the distribution, in 2008

`HC_R01_RESEARCH_REVIEW_PACKET.txt` section 6 states that the Kashtan and Alon
line is H1 and that all three papers "NEVER measured an offspring or variant
distribution. The dependent variable throughout is time-to-goal."

**That is wrong.** Parter, Kashtan and Alon 2008, "Facilitated variation", which
this seat's lane brief never listed and the lane therefore never screened,
measured it and more:

- **A-local and EXHAUSTIVE.** "Neutrality was defined as the fraction of
  1-mutant circuits that compute the same Boolean function as the wild-type."
  The genome is 104 bits, so the one-mutant neighbourhood is enumerated with no
  sampling error at all.
- **Multiple neighbourhood statistics**, not one: maximal next-goal fitness in
  the phenotypic neighbourhood, averaged modularity of neighbouring circuits,
  and counts of modular and non-modular goals within it.
- **In ALL THREE arms**, fixed-goal, modularly-varying-goal and the
  non-block-varying-goal control, with mean and standard error over 30
  simulations. Better statistical practice than Toussaint 2003 or Kouvaris 2017.
- **Tracked longitudinally** over 1e5 generations across 500 best-fitness
  circuits and 30 to 40 replicate runs, and linked to subsequent acquisition,
  per the Elenchus seat's reading.

The Ergon seat independently re-fetched the Text S1 from PLOS and its sha256
matches the Elenchus ledger byte for byte. Two seats, two retrievals, one file.

One disagreement between those two seats is **unresolved and is not resolved
here**: Elenchus reads the measurement as longitudinal and scores it D4-weak;
Ergon reads "genomes from the end of the last G1-epoch population were analyzed"
as endpoint-per-arm. That disagreement is recorded, not adjudicated.

**Consequence.** The local-longitudinal accessibility cell has not been empty
since 2008. The corrected answer to HC-R01 question 4 is that the conditioning
step, not the detector, has always been the scarce thing. And HC-T01's residual
novelty shrinks again, to an operator-side mechanism intervention plus a
quantified within-run acquisition link.

## CORRECTION 2: the MVG phenomenon is weaker than section 6 says, in a
different way than section 6 says

The packet's caveat was a single failed replication attempt. The Elenchus seat's
verdict is stronger and better evidenced: `MVG_EFFECT_IS_AUTHORED_CURRICULUM`.

- The authors' own difficulty-matched null: "MVG's outperformance occurred only
  toward goals within the modularity language. MVG adaptation toward non-modular
  goals was not significantly different from FG's." The advantage lives on about
  1e-4 of the phenotype space, and it is the part the experimenter wrote.
- Two dissociations break the standard causal story. Randomly varying goals
  produce no modularity yet give 45x to 160x speedups. Alternation with no
  selection at all gives 190x against MVG's 265x. Modularity is a correlate of
  the speed effect, not its cause.
- An independent replication REVERSED THE SIGN: Clune, Beckmann, McKinley and
  Ofria 2010, retina arm, with a direct-encoding control at Kashtan's own
  switching rate out to 30,000 generations.
- The NAND-circuit arm, which carries every accessibility result in the line,
  has never been independently replicated or refuted by anyone.

## CORRECTION 3, AND IT IS THE MOST USEFUL: why K7 fired

The Elenchus seat supplies a diagnosis of HC-T01's own failure that this seat
did not reach, and it is a repair rather than a post-mortem:

> the MVG detector is content-addressed, not a breadth statistic. Text S1 reports
> that organisms under unstructured variation vary MORE broadly and score LOWER.
> A breadth detector has no reason to beat fitness at predicting acquisition.
> Measuring WHICH phenotypes are reachable relative to a named target set is an
> inheritable repair.

HC-T01's modular degree, mutual information and neutral degree are all **breadth
or structure statistics**. None of them asks whether the reachable set contains
anything the population is trying to reach. On this reading K7 was not bad luck
and not a property of accessibility detectors in general. It was a consequence of
choosing a target-blind statistic.

**This overturns the primary detector recommendation in
`EVCA_HCA1_HCA2_DESIGN_NOTE.md` section 6.** That note recommended a
behavioural-distance cloud over the 128 one-bit neighbours as the primary
detector. A behavioural-distance cloud is a breadth statistic. By this diagnosis
it is the wrong choice and would reproduce K7.

**Corrected recommendation: the primary EvCA detector must be
CONTENT-ADDRESSED.** Not how widely the neighbourhood spreads, but how much of
it lands in a named target set: neighbours that classify a held-out density
regime correctly, or that exhibit a named particle interaction the parent lacks.
The breadth statistics become secondary descriptors, and mean neighbour
performance stays a cheap-state baseline.

---

## HOW THIS SEAT MISSED IT, WHICH IS THE TRANSFERABLE PART

The HC-R01 directive said, twice and explicitly, "Coordinate with Elenchus" and
"Coordinate with Ergon", and "do not duplicate its full historical review".

This seat coordinated with Ergon, by reading `ergon/kouvaris2017/` before
dispatching lanes. **It never looked at `elenchus/kashtan-alon-mvg/` at all**,
despite Priority A of the directive being the Kashtan and Alon line and despite
Elenchus's nineteen-deliverable review of exactly that line sitting two commits
below the HC-R01 directive in this same branch.

The lane brief this seat wrote listed Kashtan and Alon 2005, 2007 and 2009 and
did not list Parter et al. 2008. A lane cannot find what its brief excludes, and
the brief was drawn from this seat's own recall of the line rather than from the
sibling seat's committed inventory of it.

**The rule that follows: before writing a lane brief on a topic another seat has
reviewed, read that seat's committed deliverables and take the work inventory
from there.** `git log` on the shared branch is part of the literature search.
This is the second correction in one working session that arrived from a sibling
seat rather than from this seat's own searching, and both had the same cause.

---

## What is NOT changed

Sections 3, 4, 5, 7, 8, 9, 10, 11 and 14 of the packet stand. The Petak 2025
finding, the Kounios resolution, the Part C negative, the detector-stack
findings, the history-versus-hidden-state analysis, the neutral-network answer,
the parts verdict and the recommendation are unaffected by these corrections,
except that recommendation FIRST is now reinforced: Wagner 2023's conditioning
method matters more, not less, if the detectors were target-blind all along.

House consequence carried from the Elenchus verdict: calibration particle cal-08
must be marked CONTESTED and held out of the detector-scoring set.
