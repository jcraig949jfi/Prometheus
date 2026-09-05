+======================================================================+
|                                                                      |
|   HARMONIA -- ITERATIVE BOUNDARY-DEPTH QUALIFICATION                 |
|   Loops L1-L7: science surface, player classes, composition          |
|                                                                      |
|   Author:  Harmonia (systems integrator) on M2 / SPECTREX5           |
|   Date:    2026-09-05                                                |
|   For:     James (HITL), Proteus, Daedalus, Mnemosyne,               |
|            external reviewers                                        |
|   Status:  BREADTH PASS COMPLETE / FIRST CAMPAIGN NOT YET SAFE       |
|                                                                      |
|   Self-contained: every load-bearing number is inline. No repo       |
|   access is needed to review this document.                          |
|                                                                      |
+======================================================================+

----------------------------------------------------------------------
0. MANDATE AND VERDICT
----------------------------------------------------------------------

MANDATE
  The M2 stack had just been declared READY_TO_DESIGN_FIRST_INTERACTION_
  EXPERIMENT. The instruction was NOT to launch a campaign, but to probe
  repeatedly and broadly until a serious backlog existed of things that
  could invalidate, corrupt, confound or waste a longer experiment --
  routing around issues rather than halting on them.

VERDICT
  THE STACK IS SOUND. THE POPULATION IS NOT.

  Of the 4,032 ordered pairs available from the 64 frozen specimens,
  SEVEN survive the preconditions a first interaction experiment
  requires. The binding constraint is not the engine, not the evidence
  store, and not the composition glue. It is that 75% of the specimens
  cannot see the world at all, and that composition destroys
  world-coupling in 94% of the cases where both parts had it.

  A long campaign launched today would spend roughly three runs in four
  measuring organisms for which the world is decorative, and would
  produce results that look clean, pass every gate, and mean nothing.
  Nothing in the software would report an error.

  RECOMMENDATION: do not preregister a campaign. Preregister SEVEN CASE
  STUDIES against the named population in section 6, or fix the
  population first. Detail in section 8.

  This verdict is about the MENAGERIE, not about anyone's component.
  SFE, PEW and the Proteus contracts all behaved correctly throughout.

----------------------------------------------------------------------
1. WHAT WAS BUILT, AND WHAT WAS COMMITTED BEFORE MEASUREMENT
----------------------------------------------------------------------

  Committed BEFORE this pass, and used as-is (verified, not trusted):
    0fd24e0f3  SFE: sealed audit envelope + credential-free anchor
               verification (Daedalus)
    201106edb  PEW: fossil write wired to SFE verify-anchor (Mnemosyne)
    100c755f5  Harmonia: final verification, 7 claims
    f6e82d483  Harmonia: arena supplies binding ids; hard gate G7
               asserts independent causal verification

  Produced BY this pass:
    176dd8120  Harmonia: boundary-depth packet 01
    this document

  All seven loops ran against the live M2 services
  (SFE 0fd24e0f3 / PEW 201106edb / db_system_id 7681719240261676752)
  or against the Proteus VM locally. No component code was modified in
  this pass. That was deliberate: the mandate was to find boundaries,
  not to start another infrastructure sprint.

----------------------------------------------------------------------
2. THE CLAIM UNDER TEST, AND WHY IT MATTERS
----------------------------------------------------------------------

  The implicit claim behind "ready to design the first interaction
  experiment" is:

     "We can take specimens from the frozen menagerie, compose them
      pairwise, run A / B / A+B / exact ablations through the arena, and
      measure whether the composition does something its parts do not."

  Every clause of that sentence has a precondition that had never been
  measured:

     specimens ............ must respond to the world at all
     compose .............. the composed object must still respond
     A+B .................. both components must actually execute
     measure .............. the surface must separate behaviour from
                            structure
     something its parts do not .. both single knockouts must move the
                            observable

  This pass measured all five. Four of them fail for most of the
  population, and the failures are silent.

----------------------------------------------------------------------
3. DESIGN AS EXECUTED
----------------------------------------------------------------------

  Seven loops, each pre-registered with an explicit falsifier before it
  was run. Loops were chosen adaptively: each one attacked the cheapest
  remaining explanation of the previous loop's headline.

  L1  census of all 64 under one fixed unsaturated plan
  L2  one-factor-at-a-time sensitivity (inputs / seed / budget)
  L3  A / B / A+B / B+A / two exact ablations / preserved NULL
  L4  decomposition of L3's observables into EXECUTION vs IMAGE
  L5  400 random ordered pairs -- generality check on L4
  L6  joint feasibility of the preconditions
  L7  every precondition re-measured ON THE COMPOSED OBJECT

  Fixed probe parameters unless stated: seed 20260905, 6 ticks, 2 output
  channels, per-tick budget 64 (deliberately UNSATURATED -- the previous
  closure packet named budget saturation as the reason an earlier meter
  result could not be trusted). Input sets:
     I1 [[1,2,3,4],[5,6,7,8]]
     I2 [[9,9,9,9],[0,0,0,0]]
     I3 [[2^31,7,13,29],[4,4,4,4]]
     I4 [[],[]]              (an empty world; L2 only)

----------------------------------------------------------------------
4. CENSUS AND SENSITIVITY (L1, L2)
----------------------------------------------------------------------

L1 -- CENSUS OF 64 SPECIMENS

  meter vectors        64 distinct / 64      largest class 1  (1.6%)
  final-state digests  64 distinct / 64      largest class 1  (1.6%)
  transcripts          10 distinct / 64      largest class 43 (67.2%)
  status sets           5 distinct / 64      largest class 44 (68.8%)

  emitting (out_writes>0)          10 / 64
  branch-taking                    27 / 64
  code-region writers              10 / 64
  input readers (in_reads>0)       11 / 64
  budget-saturated on every tick   44 / 64
  halted early                     15 / 64

  READING: the census passes, and 64/64 distinct meters is NOT evidence
  of a good instrument. A sha256 of the genome would also score 64/64.
  Distinctness is not discrimination. L2 was written to attack it.

L2 -- IS THE METER MEASURING BEHAVIOUR, OR RE-ENCODING THE GENOME?

  falsifier: a specimen whose transcript AND meter AND final state are
  invariant across all four input sets is WORLD-BLIND -- its execution
  is a pure function of (genome, envelope, seed, budget), so no world
  can influence any observable.

  WORLD-COUPLED           16 / 64   (25.0%)
  WORLD-BLIND             48 / 64   (75.0%)
  seed-sensitive           6 / 64
  budget-sensitive        31 / 64

  in_reads>0 AND coupled          11
  in_reads>0 BUT NOT coupled       0
  in_reads==0 BUT coupled          5   <-- the cheap proxy undercounts

  SURFACE SENSITIVITY over the 16 world-coupled specimens:
     final STATE     14 / 16
     meter           11 / 16
     transcript       2 / 16
  transcript-sensitive but meter-BLIND:  1  (f38c1ac5e31e)
  detectable ONLY via final state:       4

  world-coupled AND output-producing:    4 / 64
     db80433fc4ab  ed9b68d9f02f  f9746968d54d  f38c1ac5e31e

----------------------------------------------------------------------
5. COMPOSITION, AND A HEADLINE THAT WAS AN ARTIFACT (L3, L4, L5)
----------------------------------------------------------------------

L3 -- FIRST PASS, AND ITS FALSE HEADLINE

  Six pairs from the 4 usable specimens, 7 conditions each
  (A, B, A+B, B+A, A+B\A, A+B\B, NULL=both ablated).

  REPORTED: 7 distinct profiles out of 7 conditions, in all 6 pairs.
            F1 "A+B differs from both parents" TRUE in 6/6.
            F2 "order expressed (A+B != B+A)"  TRUE in 6/6.
            Ablation exactness held in 6/6: the untouched component's
            bytes were byte-identical after ablating the other, length
            and offsets preserved, NULL genome all-NOP.

  This looked like a clean positive. It was not.

L4 -- SPLITTING EXECUTION FROM MEMORY IMAGE

  The L3 profile hash included a final-state digest, and the state
  includes the TAPE -- and the runtime copies the genome onto the front
  of the tape. A longer genome therefore changes the image whether or
  not the appended component ever executes. Distinctness by construction:
  the same trap as L1's 64/64.

  Observables were split:
     EXECUTION  meter (minus envelope-derived fields) + statuses
                + transcript
     IMAGE      final tape + registers + instruction pointer

  RESULT over the same 6 pairs:
     second component B executed in A+B ....... 0 / 6
     first component A executed in A+B ........ 6 / 6
     A+B EXECUTION-identical to A alone ....... 4 / 6
     order changed EXECUTION .................. 6 / 6
     order changed IMAGE but not execution .... 0 / 6

  CROSS-CHECK: Proteus's own activation_evidence(), an independent
  differential over op-category counts, returned NOT_ACTIVATED for
  component B in all 6 pairs. Disagreements with my execution
  differential: 0 / 6. Two independent instruments, same answer.

  So L3's F1 was driven by the memory image. "A+B differs from its
  parents" was true, and meant only that B's bytes were present.

L5 -- AND THEN L4's GENERALISATION WAS KILLED

  L4's 0/6 invited the conclusion "concat.v0 is a selector, not a
  composition". A broad sample refutes it.

  400 random ordered pairs drawn from the full 64:
     second component ACTIVATED ....... 223 / 400  (55.8%)
     first component ACTIVATED ........ 399 / 400  (99.8%)
     compositions refused ..............  0 / 400

  PREDICTOR -- first segment's solo terminal status:
     halt   ->   0 / 75  activate  ( 0.0%)
     yield  ->  15 / 47            (31.9%)
     budget -> 208 / 278           (74.8%)

  L4's result was a property of the 4-specimen subset I had selected,
  not of the glue. L4 is NARROWED, not generalised. concat.v0 is a
  selector exactly when the first segment halts.

  This correction is recorded prominently because the pessimistic
  reading was mine, it was consistent with a prior Proteus finding, and
  it survived a full loop before breadth killed it.

----------------------------------------------------------------------
6. THE ACTUAL EXPERIMENTAL POPULATION (L6, L7)
----------------------------------------------------------------------

  Every precondition was re-measured ON THE COMPOSED OBJECT. Solo
  properties are not inherited: a component that emits alone may never
  reach its emit instruction inside a composition, and a composition of
  two coupled parts may itself be uncoupled.

  P1  both components ACTIVATED
  P2  A+B is world-coupled
  P3  A+B emits
  P4  A+B is budget-UNsaturated
  P5  BOTH single knockouts move EXECUTION

  Over 240 ordered pairs of world-coupled specimens:
     P1 both activated ............ 119  (49.6%)
     P2 A+B still coupled .........  15  ( 6.2%)   <-- binding constraint
     P3 A+B emits .................  78  (32.5%)
     P4 unsaturated ............... 175  (72.9%)
     P5 both knockouts move ....... 119  (49.6%)

  CUMULATIVE FUNNEL
     240 -> P1 119 -> P2 13 -> P4 9 -> P5 9 -> P3 7

  THE STRICT SET IS EMPTY. Taking only pairs whose PARENTS are both
  world-coupled AND output-producing gives 4 specimens and 12 ordered
  pairs; the second component activated in 0 / 12, because all four
  either halt or saturate in their first segment.

  THE SURVIVING POPULATION IS SEVEN ORDERED PAIRS, named here before
  any outcome was inspected:

     17c7812c + ed9b68d9      ops [ 27,  27]
     3b7d7aac + f38c1ac5      ops [ 24,  24]
     e24bc8f3 + ed9b68d9      ops [ 18,  18]
     f9746968 + ed237074      ops [330, 384]
     f9746968 + e4d3b155      ops [224, 292]
     ed237074 + ed9b68d9      ops [ 19,  19]
     25034c19 + f9746968      ops [321, 384]

  (ops shown as [min,max] across the three input sets. Only three of the
  seven vary their execution size with the world; the other four are
  coupled through some surface other than op count.)

  NEW FINDING, AND THE MOST CONSEQUENTIAL ONE:
  COMPOSITION DESTROYS WORLD-COUPLING. Only 15 of 240 compositions of
  two world-coupled specimens are themselves world-coupled. Coupling is
  not preserved under concat.v0. Any future result of the form "A+B was
  not coupled" is therefore a statement about the glue, not about the
  pair, unless P2 was measured first.

----------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH
----------------------------------------------------------------------

  IT DOES ESTABLISH
   - 48 of 64 frozen specimens cannot be influenced by any world we can
     present through the current input channel, under this probe.
   - The composed object's preconditions must be measured on the
     composed object; four of five are not inherited from the parts.
   - Two independent instruments (my execution differential, Proteus's
     op-category differential) agree on component activation, 6/6.
   - Ablation exactness holds mechanically: untouched bytes preserved,
     length and offsets preserved, NULL is all-NOP.
   - A usable population exists and has size 7.

  IT DOES NOT ESTABLISH
   - That any of the 7 pairs shows an interaction. No interaction claim
     is made anywhere in this document. P5 is "both knockouts move
     execution", which is a necessary condition and NOT incrementality,
     synergy, or interaction.
   - That the 48 world-blind specimens are defective. They are behaving
     exactly as generated; the defect would be enrolling them.
   - That the transcript surface is bad. The earlier "transcript is
     constant" finding is NARROWED: it was measured on two specimens
     that this pass shows to be world-blind, so constancy was
     guaranteed by the organisms, not by the surface.
   - Anything about mutation, breeding, or evolved populations. Only
     frozen USE_A specimens were touched.
   - Anything at scale. Every number here comes from short probes; the
     software/scale surface (ledger growth, world accumulation,
     verify-anchor latency under load, world GC) is UNTESTED and is the
     next boundary.

  CONDITIONALITY
   All coupling results are relative to the input channel actually
   exercised (2 channels, 4 values, 6 ticks, budget 64). A richer or
   longer-horizon world could couple specimens this probe calls blind.
   "World-blind" means blind to THIS world, and the honest form of SV-1
   is: the current world presentation cannot reach 75% of the menagerie.

----------------------------------------------------------------------
8. RANKED BACKLOG AND RECOMMENDATION
----------------------------------------------------------------------

  Ranked by (likelihood of silently invalidating a long run)
          x (cost of discovering it late).

  SCIENTIFIC VALIDITY BLOCKERS
   SV-1  75% of the menagerie is world-blind under the current world
         presentation. Uniform sampling wastes 3 runs in 4 and nothing
         errors.                                              RANK 1
   SV-2  Composition destroys world-coupling (15/240 survive). RANK 2
   SV-3  Usable population is 7 ordered pairs. Not a campaign. Any power
         calculation written against "64 specimens" is wrong by three
         orders of magnitude.                                 RANK 3
   SV-4  Distinctness-by-construction produced TWO false positives in
         this pass alone (L1 64/64, L3 7/7). Any "the surface
         discriminates" claim needs a structure-only null.    RANK 4

  MEASUREMENT / INSTRUMENTATION GAPS
   MI-1  The arena records transcript+meter and NOT final state. State
         is the most sensitive surface (14/16) and 4 of 16 coupled
         specimens are invisible without it. Small, mine, cheap.
   MI-2  EXECUTION and IMAGE observables must be reported separately.
         Merging them is what produced L3's false headline.
   MI-3  proxy_search_expenditure aliases branches_taken exactly.
         Not an independent signal; must not be counted twice.

  SCALE / PERFORMANCE RISKS  (identified, NOT yet measured)
   SC-1  PEW now makes one outbound SFE call per fossil row. Measured
         3-row batch 60 ms, single write 19 ms. Untested at campaign
         volume.
   SC-2  World accumulation and ledger growth over a long run. Daedalus
         deferred I-WORLD-GC; no one has measured the growth rate.

  KILLED IDEAS / SURFACES
   K-1  "in_reads>0 identifies world-coupled specimens" -- misses 5.
   K-2  "the meter is rich, the transcript is blind" -- false as a
        universal; one specimen is transcript-sensitive, meter-blind.
   K-3  "A+B differs from its parents => composition did something" --
        the memory image guarantees the difference.
   K-4  my own "the second component never executes" -- killed by L5.

  CANDIDATE CONSTRAINTS (drafted; NONE yet proven to fire, so none are
  relied upon in this document)
   C-A  HARD      An interaction experiment may enrol a pair only if
                  world-coupling was measured on the COMPOSED object.
   C-B  HARD      Report EXECUTION and IMAGE observables separately;
                  never hash them into one profile.
   C-C  ADVISORY  Pre-registering a selection RULE does not protect
                  against selecting a population incapable of showing
                  the effect. Measure preconditions, then preregister.

  RECOMMENDATION (HITL's call; Harmonia's lean stated plainly)
   Do NOT preregister a campaign. Two defensible paths:

   PATH A -- seven case studies. Preregister the 7 named pairs, accept
     that this is a case-study design with no statistical power, and
     report per-pair mechanism. Cheap, honest, available today.

   PATH B -- fix the population first. The world presentation reaches
     only 25% of the menagerie; widen the input channel or lengthen the
     horizon and re-run L2. If coupling rises substantially, the funnel
     widens at its narrowest point and a real campaign becomes possible.
     Costs a design cycle; strictly better if it works.

   Harmonia leans PATH B, then a re-run of L6/L7, then PATH A on
   whatever population survives. PATH A alone risks spending the first
   interaction experiment on seven pairs chosen by a funnel whose
   narrowest gate (P2, 6.2%) we do not yet understand mechanically.

   "Not worth continuing with this menagerie at all" remains a
   first-class answer and is defensible on SV-1 alone.

----------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
----------------------------------------------------------------------

  Q1  Is "world-blind" the right frame, or have I mistaken a narrow
      input channel for a property of the organisms? The honest
      statement is conditional (section 7) but SV-1 is written as
      though it is a fact about the menagerie. Which is it?

  Q2  L4 and L5 disagree, and I resolved it by narrowing L4. An
      alternative reading is that the 4-specimen subset is the
      SCIENTIFICALLY RELEVANT one and the 400-pair sample is diluted by
      specimens nobody would enrol. Under that reading concat.v0 IS a
      selector for the population we care about. Which reading survives?

  Q3  P5 ("both knockouts move execution") is my proposed necessary
      condition for interaction. Is it too weak? A composition where A
      merely shifts B's instruction pointer would pass P5 while being a
      positional artifact rather than an interaction.

  Q4  Seven pairs. Is a case-study design with n=7 worth running at all,
      or does it just generate seven anecdotes that will be
      over-interpreted later?

  Q5  I found two distinctness-by-construction artifacts in one pass
      (L1, L3). Both were mine, both looked like clean positives. What
      else in this document has the same shape and I have not caught?

  Q6  Is the funnel itself a selection effect? Five conjunctive gates
      taking 240 to 7 will always produce a small, peculiar set. Is the
      surviving population representative of anything, or is it just
      the corner of the space where five arbitrary predicates happen to
      agree?

----------------------------------------------------------------------
10. ARTIFACTS
----------------------------------------------------------------------

  COMMITS
    176dd8120  Harmonia: boundary-depth packet 01
    f6e82d483  Harmonia: arena binding ids + gate G7
    100c755f5  Harmonia: M2 final verification (7 claims)
    201106edb  Mnemosyne: PEW fossil write -> SFE verify-anchor
    0fd24e0f3  Daedalus: sealed audit envelope + verify-anchor

  DOCUMENTS
    roles/Harmonia/BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt
    roles/Harmonia/M2_QUALIFICATION_TWO_ROUND_CLOSURE_2026-09-04.txt
    roles/Harmonia/M2_FINAL_VERIFICATION_2026-09-04.txt
    roles/Harmonia/pivot/HARMONIA_BOUNDARY_DEPTH_REVIEW_2026-09-05.md
      (this document)

  CODE USED, UNMODIFIED IN THIS PASS
    integration/harmonia_arena.py         the one shared orchestration path
    proteus/compose/segments.py           compose / ablate / activation
    proteus/integration/registry.py       the 64 frozen specimens
    evidence_wiki/integration/*.py        pew / seam / closure batteries

  PROBE SCRIPTS (scratchpad, not committed; all numbers above are
  reproducible from these)
    L1_census.py  L2_coupling.py  L3_composition.py
    L4_execution_vs_image.py  L5_reachability.py
    L6_feasibility.py  L7_population.py

  LIVE SERVICE STATE AT TIME OF WRITING
    SFE  https://192.168.1.191:8811   source_commit 0fd24e0f3
         schema 4, engine_instance_id eng_906356f7fb1da180131f9290
    PEW  http://192.168.1.191:8377    source_commit 201106edb
         db_system_id 7681719240261676752, closure pew.closure.v0

+======================================================================+
|  END OF PACKET                                                       |
|                                                                      |
|  "This menagerie is not worth continuing with" is a first-class      |
|  answer and is defensible on SV-1 alone. So is "your input channel    |
|  is too narrow and you have libelled 48 organisms." A reviewer who    |
|  tells us the population is fine and the funnel is the problem is     |
|  more useful than one who agrees.                                     |
+======================================================================+
