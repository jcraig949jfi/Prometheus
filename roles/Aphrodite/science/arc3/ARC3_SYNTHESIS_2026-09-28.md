# ARC3 SYNTHESIS -- ABSTRACTION ACQUISITION, COMPOUNDING, REUSE AND IMPROVER EVOLUTION
# Aphrodite (M4), research principal. 2026-09-28, 05:08Z -> 14:50Z. Plain ASCII.
# Branch aphrodite/arc3-2026-09-28. Baseline: the compounding synthesis at f6d60364a.
# Historical labels unchanged. No BOUNDED_RSI label written. Campaign 1 frozen.

==============================================================================
1. CURRENT COMPOUNDING MODEL (what we now believe happens, G1 -> selection -> reuse)
==============================================================================
  (a) ACCESS. An inherited schema S reaches new structure only through the composition
      move. Composition is a designer edit to the improver (W4). It needs a depth-3 world
      (W5) for compositions to have extent.
  (b) SELECTION. Paired validation picks what pays on the few validation families.
        - C2: each G1 selection rested on ONE cross-group validation family (W6).
        - Reusable compositions existed in 6/8 C2 replicates, but validation carried no
          signal for them.
        - When validation SHOWS the recurring structure (2 validation instances per
          motif, A22/A23), selection picks a composition of S in most replicates.
  (c) REUSE. It happens when the selected composition's EXTENSIONAL class covers held-out
      families of the SAME recurring structure (T_SAME). It essentially does not transfer
      to a different composition of the same schema (T_OTHER ~0): reuse is
      structure-specific.
  (d) CAPABILITY. It is budget-relative. The start library and PRISTINE fail even at 10M
      because the walk has a coverage cliff (151,920) and 83.9M fallback blocks (W2). Any
      library holding an early extensional equivalent gains 10^3-10^4x on a typical
      uncovered family. The "capability" rung therefore measures "brought the right
      equivalence class to the front of the walk".
  (e) GENERICITY. In A22 (forensic) the mechanism worked for G1 AND for all three clean
      shams at similar rates, and never for the no-composition, PRISTINE or OFF controls.
      It is a property of inheritance + composition + recurrence, not of G1.
      A23 CONFIRMED it under the frozen verdict: G1 YES and GENERIC 3/3. Composition is
      NECESSARY: G1_NC reached 0/10. Scope: MECHANISM UNDER CONSTRUCTED RECURRENCE only.
      It is not natural open-endedness and is not retroactive RSI evidence.
  (f) SECOND ORDER. G2 = wrap(G1) consumes the grammar depth, and G3 = wrap(G2) has no
      extent in W5. Promoting G2 to a one-node primitive gives 30 G3 candidates extent and
      novelty (PKG-5). The chain breaks at REPRESENTATION, not at search or selection
      (untested beyond representable).

==============================================================================
2. WHAT WAS FALSIFIED (ARC3 starting assumptions)
==============================================================================
  - "Accessibility is solved; reliable reuse is THE bottleneck" (the baseline). SPLIT:
      * the composition-horizon rival is killed (W6 R1);
      * the non-specificity rival is killed (W6 R3);
      * the C2 reuse failure was mainly a selection/validation valley: reusable
        compositions existed but validation could not see them (W6 R2);
      * the frozen REUSABLE rung was near-unreachable by design (W3, W6);
      * reuse had been measured in the wrong unit (literal vs extensional; W2, W3).
  - "The natural T4 world is bimodal": it is the INSTRUMENT (escrow x walk cliff) that is
    bimodal. The window count is U-shaped in escrow and minimal at the frozen 250k (W2).
  - "CON1 = a G1 stepping stone": G1 is route-sufficient, not necessary. The credit
    belongs to G1's extensional class, shared with its sign re-expression SHAM_0 (W3, W6,
    W7, CON1 forensics). CON1's ">= 190x" is the generic cliff ratio (W2).
  - "16% chance-novelty base rate": that is G4. W5 is 23-25% (W3, W7).
  - "Literals first" for DSL extension: refuted (W5).
  - W1's claim that C2's G1 selections were paid by efficiency: not reproduced (W6).

==============================================================================
3. REUSE-CONTROLLED ASSAY (Block B) -- the primary lane
==============================================================================
  C3 (A20)        UNTESTABLE (supply). The OBSERVE learnability floor collided with the
                  escrow cliff (0/8 fillable).
  C3R (A21)       INVALID_DESIGN_DEFECT. The motif rule admitted inert identity wraps:
                  genuine motifs G1 2/8, SHAM_1/2 0/8. Stopped by PID; no verdict.
  C3R2 (A22)      UNTESTABLE (supply, 5/8 < 6). FORENSIC: G1 reused with capability in
                  3/5; shams 2-4/5; controls 0/5; T_OTHER ~0.
  C3R2-CONFIRM (A23)  G1_RECURRENT_STEPPING_STONE = YES; GENERIC = 3/3. n = 10 fillable
                  of 12 (replicates 0 and 6 unfillable, both counted as failures);
                  k = ceil(0.58 n) = 6.

                    arm          SELECTED  SOLVED  REUSED  CAPABILITY  REUSED_OTHER
                    G1                  8       7       7           7             0
                    SHAM_0             10       9       8           8             1
                    SHAM_1              9       9       9           9             0
                    SHAM_2             10      10      10          10             0
                    G1_NC               0       0       0           0             0
                    P                   0       0       0           0             0
                    OFF_0               1       0       0           0             0

                  Sign tests: G1 vs each of G1_NC / P / OFF_0 p = 0.0078; the shams
                  p <= 0.004.
                  PRINCIPAL ATTACK (engine/A23_C3R2C/A23_C3R2C_RESULT_2026-09-28.json):
                    (i) The selected composition EQUALS the planted motif literally in
                        G1 7/8 and in the shams 5-7; it covers the motif extensionally
                        in 7-10. So the donor mostly RECOVERS the planted structure.
                        The non-trivial content is:
                          - selection among ~60 candidate compositions from 2
                            validation families;
                          - transfer to different instances;
                          - necessity of composition (G1_NC 0);
                          - structure-specificity (REUSED_OTHER ~0);
                          - sham symmetry.
                    (ii) The median capability ratio vs PRISTINE's 10M ladder is >= 330-447x.
                        That is budget-relative, a W2 walk-cliff quantity, and not a
                        capability measure that holds apart from the instrument (T53).
                    (iii) OFFPATH gains of 8-12 cells in P and OFF come from LGG
                        re-derivation on motif families: a known leakage, and not
                        counted.
  Process lesson: 3 of 4 consecutive assays failed on design or supply (the seat's).
  Countermeasure: a mandatory pre-freeze supply screen (T49).

==============================================================================
4. NATURAL CURRICULA (Block C; W1, W8)
==============================================================================
  W1: memory/lineage generators (LIN) produce ~35x the recurrence of uniform sampling,
  with emergent identity (cross-seed Jaccard 0), and without writing any abstraction into
  the generator. G1-specific recurrence is a lottery across seeds, which gives a natural
  dose-response experiment. T4 itself enriches G1 compositions 6-15x (a smuggling channel
  to report).
  W8 (independent re-implementation, 24 LIN / 24 STAR / 6 U seeds, N = 144):
    - LIN yields GENUINE recurrence: P_reuse .135, which is 14x U and 16x STAR.
    - It FAILS W1's own "natural recurrence exists" criteria:
      - dup .43 > .35;
      - the genuine X_G1 spread is 3/24 seeds >= .10.
      - The dup-guarded LIND fixes dup (0) but breaks Jaccard (.167). The criteria
        trade off against each other.
    - Two findings matter most:
      (i) Recurrence lands where the instrument cannot see it. Families carrying
          recurring structure are MORE often unreachable by PRISTINE than non-carriers
          (p0 .77 vs .61 at 250k). The 250k window holds ~2% of families in EVERY
          generator.
      (ii) G1 is not privileged by natural lineage. The frequency-matched sham
           ({H} + v) recurs 3x more than G1 (genuine X .152 vs .051).
    - Task-side freeze: FEASIBLE, with conditions. Use a pooled dose-response slope over
      a 5-schema panel. Scoring at 250k is FORBIDDEN (30k/1M or a per-stratum escrow
      instead), and there are stop rules for dose range and window fraction. A
      G1-specific natural hypothesis is not supportable.

5. CON1 -- survived attack in reduced form (see s2).

6. LEARNABILITY FRONTIER (W2) -- bimodality = coverage membership x escrow position. The
   controllable smooth variable is the equivalence-class multiplicity D (closed-form
   solve probability, 94% cell agreement). Curricula can target a D. Escrow should be
   chosen per stratum.

7. NOVELTY (W3, W7)
   The scalar is retired. Use four judgements plus a provenance tag:
     J1 behavioural novelty (with the world base rate);
     J2 reach;
     J3 budget-relative capability, net of losses;
     J4 causal dependence (sufficient vs necessary);
     TAG EQUAL / REFINES / COMPOSES (closed).
   Ruler v2.1 drafted (errors 14 -> 8). Novelty cannot establish value; the base rate is
   ~1 in 4 in W5.

8. SECOND-GENERATION (Block G): depth wall; primitive promotion restores extent and
   novelty; the next rungs (solved/selected) are untested (PKG-5 next step).

9. IMPROVER EVOLUTION (W4): not justified as a full program now. One bounded GO/STOP
   probe is designed (genome transfer correlation; PKG-4). Reset-to-PRISTINE transplant
   gives no signal here. Composition is already an improver edit.

10. TRANSPLANTATION (W4): a clean assay design exists: fixed common start library,
    variance-matched and shuffled-trace shams, widening-gap endpoint, operator-disjoint
    strata as unseen domains. Hyperagents/STOP lack these controls.

11. DSL (W5)
    Not the first-order limit. It IS the second-order limit (depth; promotion).
    Extensions re-base every budget number. Triggers are defined. PARKED, per the
    operator, until a first-order mechanism positive. A23 IS that positive, so the
    trigger condition is now met for SECOND order (see s18). Nothing was extended.

12. PRIOR ART (workers W1, W4, W5)
    - Hyperagents / STOP: the only frozen-improver transplants, with no variance-matched
      controls.
    - "Library Learning Doesn't": reuse is extremely infrequent.
    - Wu et al. 2021: curricula matter mainly under budget limits.
    - Lenski 2003: no single essential intermediate.
    - Stitch / LILO: an abstraction exists only if it recurs.
    - LES / AutoML-Zero / RAISE: learned improvers overfit their development
      distribution.


13. INDEPENDENT WORKERS (W1-W8; manifest WORKER_MANIFEST.md)
    Workers were fresh-context background subagents told to ATTACK the principal's
    readings. Isolation is imperfect: they share the filesystem. W1-W3 and W5-W7 could not
    write REPORT.md (the harness blocked it), so the principal deposited their text
    verbatim.
    Findings that CHANGED the principal's position:
      - W6: the reuse failure in C2 was a selection/validation valley, not a horizon or
        non-specificity problem.
      - W2: bimodality comes from the instrument.
      - W3/W7: the chance-novelty base rate is 23-25%, and the ruler has defects.
      - W5: literals-first is refuted.
      - W4: composition is already an improver edit.
    DISAGREEMENTS (left as they are; they were not harmonised):
      - W1 vs W6 on E1. W1 read C2's G1 selections as paid by efficiency; W6 could not
        reproduce this. The principal sides with W6, because W6 used the frozen rows.
        The disagreement stays recorded.
      - W5 vs RB-5 on literals first. W5 refuted the ranking for EC; RB-5 had it first.
        The ranking was demoted.
      - W2 vs CON1 on ">= 190x". W2 shows it is the generic cliff ratio. CON1's
        capability survives only in reduced form (generalising, route-sufficient, not
        G1-specific).
      - W7 vs A22/A23 instruments. T4's query window (1-2) differs from dev for ~1.7%
        of families. A23 was run on the frozen, unrepaired T4. The bridge re-score is
        T47.
      - W8 vs the principal. The principal's model said natural worlds RARELY present
        recurrence. W8: lineage generators produce plenty of it; what is rare is
        recurrence that is ALSO learnable in the assay window (A1/A2). ADOPTED: the
        bottleneck for natural compounding is recurrence x visibility, not recurrence
        alone.
      - W8 vs W1. Non-root edits (CG-1 text) give P_reuse .21, against .45 in W1's
        probe, which allowed root edits. Syntactic counting inflates G1 reuse 1.7x.
        W8 also contradicts W1's C4 pass under the genuine reading.
      - W8 made a stale claim: that the A23 foundry (PID 7948) was running at its
        close. The principal verified 0 python processes. It is recorded in the
        REPORT provenance.

14. BACKLOG CHANGES (science/compounding/BACKLOG_COMPOUNDING.md)
    ANSWERED: T17 and T23 (A23), T32 (CON1), T50 (generic 3/3).
    CLOSED: T35 (horizon), T37 (non-specificity).
    SHARPENED: T33, T34, T39, T45.
    NEW this arc:
      - T47 instrument versioning;
      - T55 recurrence x visibility (W8);
      - T48 keyed role assignment;
      - T49 seat design-defect rate (countermeasure worked in A23);
      - T51 natural-recurrence donor stage;
      - T52 validation-multiplicity dose response;
      - T53 budget-free (D-stratified) capability endpoint;
      - T54 motif recovery vs abstraction.
    Consumed: C3, C3R, C3R2, C3R2C (4 amendments: 20-23), 8 worker studies, CON1
    forensics, G3 reach, and PKG-5 promotion.

15. LEASES / QUEUE
    Every Aphrodite lease was released, the last being abb30c3c at 14:29Z. W8's lease
    bbf2e885 EXPIRED without an explicit release (the worker stalled while waiting on a
    monitor). The ledger recorded the expiry, and no process was left running. At close:
    lease list = {}, python processes = 0. Stale work was cancelled by PID in two cases
    (the C3R transfer stage, and orphaned worker processes).

16. RESEARCH-READY INVENTORY (ARC3_RESEARCH_PACKAGES.md)
    PKG-1 window-by-design instrument (M->L)
    PKG-2 extensional reuse re-measurement (S)
    PKG-3 LIN natural recurrence, WP-2 = T51 (M->L)
    PKG-4 improver genome transfer probe (L; separate P2)
    PKG-5 promoted-primitive fixture (S; gated)
    PKG-6 T4 v1a (S/M)
    PKG-7 ruler v2.1 (S)
    PKG-8 propagation (L; gated)
    T52 / T53 cheap A23 follow-ups (S)
    RB-7..RB-10 carried over from the compounding synthesis

    NEXT AUTONOMOUS ARC, prepared, with no new spend and no representation change:
      (1) T53 re-score of A23, followed by T52 validation dose response;
      (2) PKG-6 + PKG-7 frozen together, with a bridge re-score (T47);
      (3) T51 natural-recurrence donor stage on the W8 supply (the decisive
          "natural vs constructed" test), frozen per W8 s6:
            - a pooled 5-schema dose-response;
            - the 250k escrow is not allowed;
            - stop rules F6;
            - ~16 core-hours under a lease;
      (4) PKG-2.

17. SHOULD THIS LINE CONTINUE?
    YES, narrowed. The mechanism question is answered: under recurrence that validation
    can see, inheritance + composition is a reliable, generic, structure-specific
    stepping stone. The open questions are the two the positive does NOT answer:
      (a) does recurrence occur NATURALLY, visibly enough for the mechanism to fire (T51);
      (b) does it CHAIN (second order), which needs a representation change.
    W8 sharpens (a): lineage worlds DO recur. The open question is whether recurrence
    and learnability co-occur (A2), and the donor stage must be scored at an escrow
    where they can.
    Stop condition for (a): if a fair T51 with LIN supply yields no selection of
    recurring compositions, the compounding line reduces to "works only when recurrence
    is supplied", and the North-Star value then rests on curriculum construction.

18. HITL
    One DIRECTION FORK is offered; it is not blocking. The operator's DSL-extension
    condition ("the compounding mechanism works but is constrained by expressivity") is
    now met for SECOND-order compounding:
      - G3 has no extent in W5 (depth wall);
      - primitive promotion restores extent (PKG-5).
    Promotion is a representation change. It re-bases every budget number and breaks
    comparability with historical results. Options:
      (A) authorise the PKG-5 promotion fixture as a separately versioned world (W5P),
          with historical results untouched;
      (B) keep the DSL parked and pursue natural recurrence (T51) first.
    Without a ruling the seat proceeds with (B), which needs no decision. Otherwise:
    No operator decision required. The next autonomous research arc is already prepared.
