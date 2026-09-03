# SFE MVG CALIBRATION PROPOSAL

Purpose, stated so it cannot drift: NOT to claim synthetic reasoning, and NOT to show that
Prometheus organisms become modular. The purpose is to ask whether the Serendipity Foundry
Engine can DETECT a known historical increase in future acquisition efficiency, blind.

This is a detector calibration, and the specimen is already on the house books: calibration
particle cal-08, "Modularity from modularly varying goals", system Kashtan-Alon (fam-161),
status UNVERIFIED, with the blind-recovery target recorded as "modularity onset tied to the
switching schedule".

================================================================================
1. FIRST, A CORRECTION TO cal-08 ITSELF
================================================================================

cal-08 currently carries the established causal structure as "environment-switching causes
modularity" and asks a detector to recover "modularity onset tied to the switching
schedule". On the evidence retrieved in this pass, that framing should be revised before
the particle is used to pass or fail any detector.

  (a) Its status is UNVERIFIED and all rows in the calibration set are MODEL_RECALL_
      UNVERIFIED. This pass upgrades cal-08 to PRIMARY_SOURCE_READ with three papers and
      one supplement in hand, hashed, in elenchus/kashtan-alon-mvg/sources/.
  (b) The causal structure as written is INCOMPLETE in a way that would make the particle
      score detectors wrongly. Modularity is not the mechanism of the speed effect. The
      authors' own NBVG control produces the same rapid adaptation and the same underlying
      machinery using goals chosen to be explicitly non-decomposable. A detector that
      correctly identifies neutral-network-border positioning and ignores modularity would
      be marked WRONG by cal-08 as currently written, and it would be right.
  (c) The blind target should be split, because the corpus contains two separable effects
      with different causes (CAUSAL_INTERVENTION_MAP.md section 2b).

PROPOSED REVISED PARTICLE:

  cal-08a  phenomenon: rapid re-adaptation on environment switch
           established cause: successive objectives with adjacent solution sets; position
             at the neutral-network border plus a small set of high-MI genomic positions
           blind target: the onset of the rapid-re-adaptation regime, and the fact that it
             does NOT require the objectives to be decomposable
           negative control built in: the NBVG arm, which a modularity-only detector will
             misclassify
  cal-08b  phenomenon: neighbourhood bias toward an authored family
           established cause: the shared structure across objectives being modular
           blind target: the FV trajectory rising faster under structured than unstructured
             variation, AND the non-monotonicity (unstructured variation scores BELOW
             static)
           blind target 2: the BOUNDARY -- that the advantage disappears on
             difficulty-matched out-of-family objectives

cal-08b's second blind target is the valuable one. A detector that reports an evolvability
gain without discovering its boundary is a post-hoc narrator in exactly the sense the
calibration protocol is designed to catch.

================================================================================
2. IS THIS A GOOD CALIBRATION SPECIMEN?
================================================================================

Scored against the six criteria in the assignment:

  small discrete physics ................ YES. Genomes of 76-104 bits, circuits of <=12
                                          NAND gates, 4-input truth-table phenotypes.
  strong historical replication ......... *** FAILS. *** This criterion was scored
                                          PARTIAL-pending in an earlier draft, with the
                                          note "do not describe this specimen as
                                          externally replicated until the descendant
                                          search returns". It returned. The only
                                          independent replication attempt of any arm --
                                          Clune, Beckmann, McKinley & Ofria 2010, on the
                                          retina arm, WITH a direct-encoding control --
                                          REVERSED THE SIGN: "the MVG regimes performed
                                          worse than the FG-AND regime, which was the
                                          opposite of what occurred in Kashtan and Alon's
                                          study." They tested Kashtan's own switching rate
                                          and ran to 30,000 generations. And the NAND
                                          circuit arm, the one we would actually use, has
                                          never been independently replicated or refuted
                                          by anyone. Within-paper replication is good
                                          (30-50 runs, SE reported); EXTERNAL replication
                                          is absent in one arm and negative in the other.
  known treatment effect ................ YES, and unusually well quantified: 95x-700x
                                          speedup on hardest goals; Q_m 0.12 -> 0.54;
                                          pleiotropy 0.04 -> 0.01; 1-2 mutations to
                                          re-adapt.
  measurable adaptation acceleration .... YES, in three independent units: generations,
                                          mutations, and competition takeover fraction.
  known negative controls ............... YES, and this is the specimen's best feature.
                                          FG, RVG_v, RVG_c, VG_0, NBVG, thermal
                                          fluctuation, non-evolved phenotype-matched
                                          controls, and a difficulty-matched
                                          out-of-family target class.
  affordable massive replication ........ YES. The historical work ran on a 60-CPU grid in
                                          2007. The 1-mutant neighbourhood is B
                                          evaluations, exhaustive, no sampling noise.

VERDICT, AMENDED AFTER THE REPLICATION FINDING:

  NOT YET USABLE AS A CALIBRATION PARTICLE. A calibration particle's job is to be a KNOWN
  answer against which a detector is scored blind. This specimen does not currently have
  one. In the arm that was independently tested the effect reversed; in the arm we would
  use, nobody has ever tested it. Scoring a Prometheus detector against cal-08 today would
  be scoring it against a single laboratory's unreplicated result, and a detector that
  disagreed might be right.

  cal-08 must therefore be marked CONTESTED, not merely UNVERIFIED, and held out of the
  detector-scoring set until the circuit arm is reproduced in house.

WHAT REMAINS EXCELLENT ABOUT IT: the CONTROL SET, which is unaffected by the replication
problem because it is a design, not a result. Most historical specimens give one treatment
and one control. This one gives a graded series of environment regimes -- FG, MVG, RVG_v,
RVG_c, VG_0, NBVG, thermal fluctuation, plus non-evolved phenotype-matched genomes and a
difficulty-matched out-of-family target class -- with a non-monotonic outcome. That design
is inheritable regardless of whether the original numbers replicate, and it is far harder
for a detector to fake its way through than a two-arm comparison.

The specimen's best use is therefore as a SOURCE OF EXPERIMENTAL DESIGN and as a
REPRODUCTION TARGET, not as a scoring key.

================================================================================
3. THE HARD PART: TRANSLATION INTO SFE, HONESTLY
================================================================================

Following the house rule from the Avida translation plan -- do not port the specimen into
SFE; first reproduce it faithfully, then state what SFE would add and where it CANNOT
represent the specimen honestly.

  historical primitive        SFE equivalent                    fidelity
  -------------------------   --------------------------------  -----------------------
  binary genome, 104 bits     bytecode VM genotype as            APPROXIMATE. Genotypes
                              interpreted data (stackvm-v1)      are programs, not
                                                                 fixed-length bit strings.
                                                                 1-mutant enumeration is
                                                                 still possible but the
                                                                 neighbourhood is over
                                                                 instruction edits.
  4-input Boolean phenotype   organism response over a fixed     GOOD, if the probe set is
                              probe set of channel inputs        frozen and small.
  goal = target truth table   WORLD channel produced by a        GOOD, and this is where
                              hidden generator program           SFE is BETTER: the goal
                                                                 is itself a program from
                                                                 a compositional
                                                                 distribution over the
                                                                 same instruction set.
  MVG goal alternation        switch the hidden generator every  GOOD.
                              E ticks within a fixed scheme
  fitness = fraction correct  *** CANNOT REPRESENT ***           SFE selection is
                                                                 MINIMAL-CRITERION and
                                                                 there is no fitness
                                                                 field. Viability is
                                                                 derived. The historical
                                                                 speed metric
                                                                 (generations to
                                                                 fitness=1) has NO
                                                                 faithful analogue.
  elite strategy, P_c, P_m    engine variation operators         NEEDS SPECIFICATION.
  phenotypic neighbourhood    enumerate 1-instruction-edit       GOOD, and this is the
                              variants, run each on the frozen   part worth building.
                              probe set, collect responses
  FV measure                  requires a "useful" predicate      *** DANGER. See below. ***

THE HONEST INCOMPATIBILITY: the historical specimen is a fitness-proportional optimisation
experiment with an explicit scalar objective. SFE is explicitly not that -- "SELECTION IS
MINIMAL-CRITERION, NOT FITNESS-PROPORTIONAL ... FITNESS IS NOT A FIELD." A faithful
reproduction of Kashtan/Alon inside SFE would require reintroducing the very thing the
Engine's physics excludes. Two options, and the choice must be made explicitly rather than
drifted into:

  OPTION A  Run the reproduction OUTSIDE SFE, as a standalone harness, exactly as Herakles
            did for HC-T01 (derived/hct01.c is standalone C, not an SFE world). Use SFE
            only for the DETECTOR calibration, by replaying recorded histories through it.
            Cost: low. Fidelity: high. Recommended.
  OPTION B  Build an SFE world with a derived-viability proxy for the goal. Cost: high.
            Fidelity: compromised at exactly the point the specimen is about. Not
            recommended, and if chosen must be labelled CONCEPTUAL_REPRODUCTION, not
            RECOVERED_SPECIMEN.

================================================================================
4. THE TAUTOLOGY WARNING, INHERITED FROM THE FV MEASURE
================================================================================

The FV measure defines "useful" as phenotypes sharing the authored modular structure. If
SFE imports that definition, the detector will measure alignment to the world designer's
own decomposition and will report a large effect by construction. That is the shape the
house has already named as a hazard: a gate scored by a classifier over the generator's own
output shapes measures the generator menu.

REQUIRED MITIGATION before any FV-like statistic is used in SFE: the usefulness predicate
must be supplied by something other than the hand that authored the world. Two concrete
routes, in order of preference:

  (1) Define usefulness by SUBSEQUENT REALISED ACQUISITION rather than by structure -- a
      neighbouring phenotype is useful if a later epoch's environment actually rewards it.
      This makes the detector prospective and removes the authored basis entirely.
  (2) Define usefulness against a held-out family generated by a DIFFERENT decomposition
      than the training family, which is the transfer test nobody in either lineage has
      run (INTERPOLATION_EXTRAPOLATION_ANALYSIS.md section 5).

================================================================================
5. WHAT SFE WOULD ADD THAT THE HISTORICAL WORK COULD NOT DO
================================================================================

One thing, and it is the thing this whole deep-dive converges on.

The historical mechanism is a MIRROR, not a ratchet: the property decays when the
environment stops supplying structure (2008 Fig 9D; 2005 Fig 3). It cannot compound,
because nothing carries the acquired structure forward except the continuing pressure that
created it.

SFE's World-0 physics contains the missing element: DEPOSIT channels, where organisms emit
into the medium at a cost, so that "yesterday's successful strategy thereby becomes part of
today's environment." That is a mechanism by which the environmental regularity which
selects for the aligned variation operator could be PRODUCED BY THE POPULATION ITSELF.

If a mirror is held up to its own reflection, the decay result predicts nothing -- the
historical experiments never had an endogenous environment and so are silent on it. This is
a genuine open question that the historical record poses and cannot answer, and it is the
strongest reason for Prometheus to care about this lineage at all.

Registered as the composition to test AFTER cal-08 calibration passes, not before, and not
as part of this proposal.

================================================================================
6. PROPOSED SEQUENCE
================================================================================

  step 0  *** NEW, AND IT IS NOW THE FIRST STEP. *** Mark cal-08 CONTESTED and remove it
          from the detector-scoring set, citing Clune/Beckmann/McKinley/Ofria 2010 and the
          absence of any independent test of the circuit arm. Cost: minutes. Prevents a
          detector being failed against an unreplicated key.
  step 1  Update cal-08 to cal-08a / cal-08b per section 1, and upgrade its provenance
          tier from MODEL_RECALL_UNVERIFIED to PRIMARY_SOURCE_READ. Note that the upgrade
          is in EVIDENCE QUALITY, not in confidence: we now know what the papers say and
          we also know the result is contested.
  step 2  Standalone reproduction (Option A) of the 2008 logic-circuit arm at reduced
          scale: B=104, N_pop=5000 is affordable; the arms are FG, MVG, NBVG. Target the
          three verified anchors -- Q_m separation, the FV ordering MVG > FG > NBVG, and
          the out-of-family null.
          THIS IS NO LONGER ONLY AN INTERNAL CALIBRATION STEP. Amended 2026-09-03 with
          what the retry search found: a partial reproduction of the circuit arm DOES
          exist, unpublished, at JBQuim/Boolean-Circuit-Evolution. It reproduces
          MVG-versus-fixed at Q_m = 0.42 +- 0.10 against the original 0.54 +- 0.02, and
          reproduces the modularity decay. It explicitly did NOT run the
          time-varying-random-goals arm, and its own README names what that omission
          costs: those experiments "were used to show that evolution under varying goals
          leads to shorter generation times and more modular solutions only if the goals
          share subgoals". The other reimplementation, freedmand/combinational, computes
          no modularity metric at all and is a time-to-solution reproduction only.
          THE CONSEQUENCE IS FAVOURABLE AND NARROWS THE JOB. The MVG-versus-fixed
          comparison has been reproduced once outside the original lab, informally, with
          a somewhat lower effect. What has NEVER been reproduced by anyone is the
          comparison that carries the causal claim: MVG against RANDOMLY VARYING goals.
          Prometheus should aim at that arm specifically rather than rebuilding the whole
          specimen, and may be able to start from the existing Python rather than from
          scratch. That is a far cheaper step 2 than this proposal originally assumed.
          Whichever way it comes out it is a result, and it settles whether the rest of
          this deep-dive describes a real phenomenon or one laboratory's encoding.
          Design requirement inherited from the failed replication: Clune et al. attribute
          the reversal to DISCRETENESS -- few discrete weights and thresholds, so that a
          single mutation can switch between goal solutions. Any reproduction must record
          the one-mutation switchability of its own encoding as a measured quantity, not
          assume it. If our encoding does not have it, a null tells us about our encoding
          and not about the claim.
  step 3  Blind detector test per the calibration protocol: give the detector the run
          history truncated before the transfer test; ask it to name the precursor and the
          window; score. A detector that names modularity and misses the NBVG dissociation
          fails. Only meaningful if step 2 reproduces; if step 2 fails to reproduce, the
          particle is dead and the finding is that it is dead.
  step 4  Only then consider the endogenous-environment composition of section 5.

Steps 2-4 are proposals requiring the standing compute gate to be cleared per specimen.
Nothing in this file authorises a run.
