# SEPARATION RECORD -- case POLLUX (role separation, measured on one grave)

Charter question: does a genuinely separated Necromancer + Cleric produce something a
single agent performing three personas does not?  Measured, not scored.  No inter-rater
number is computed here; the charter forbids manufacturing one, and the lists below are
the product.

Arms.
  SEPARATED   NECROMANCER_report.md (fresh context, no Cleric knowledge) then
              CLERIC_challenge.md (fresh context; may read only the Necromancer report)
  SOLO        SOLO_three_persona.md (one fresh context, Parts A/B/C in sequence)
  PRIOR       engine/necropolis/dossiers/pollux.dossier.json + pollux_evidence/ (2026-09-11,
              Keeper-authored; readable by the judge only; compared after the fact)
All three fresh readers had the same artifact set, the same three static instruments,
the same firewall, and the same prohibition on executing the corpse.  None of them
opened the prior dossier (each lists it under excluded_by_charter).

## 1. Propositions -- agreed across arms (rediscovered by every fresh reader)

  Raw arm constant: independent sort + truncate, no join, corr_raw = +1.0 for n >= 10
      Necro P1/P2 -- Cleric CONFIRMED (own re-implementation) -- Solo P1 (13,000/13,000)
  Verdict decided by corr_norm alone; thresholds 0.30 / 0.20 / n >= 10; no null anywhere
      Necro P3/P7/P8 -- Cleric CONFIRMED -- Solo P2/P6/P7
  Statistic is a function of the sorted multisets only
      Necro P4 -- Cleric CONFIRMED -- Solo P4 (as the "co-ranking" reading)
  Exhausted-pool re-settle defect at daemon.py:330-332; "rotation shrunk" log is false
      Necro P10/P11 -- Cleric CONFIRMED -- Solo P9 -- PRIOR (_keeper_evidence replay)
  Two commits, HEAD == 43b094552; the 05-25 commit did not touch the statistic
      Necro P12/P13 -- Cleric CONFIRMED -- Solo P10 (+ v0.5 round-robin)
  Inputs constant over the organism's life; Known180 present since 05-03
      Necro P14 -- Cleric CONFIRMED -- Solo P8
  No output bytes in any tree; state/ gitignored
      Necro P16 -- Cleric CONFIRMED -- Solo P19 -- PRIOR (FRANK-003 lineage)
  Last tick 2026-05-30T15:55:23Z; halt swarm-wide, not Pollux-specific
      Necro P17/P18 -- Cleric CONFIRMED (+ mechanism, section 2 below) -- Solo (Part A)
  Stygian short-circuit; ergon inverts labels; Hecate MI at noise
      Necro P19/P20/P21 -- Cleric CONFIRMED -- Solo P15/P17/P18
  Hypothesis UNTESTED; FAIR status UNFAIR on the question of record; cause class
  DESIGN_ERROR primary; no revival
      all three arms -- PRIOR agrees on all four

Reading: the mechanism of death was rediscovered independently four times (three fresh
readers plus the prior Keeper).  On this grave the separated Necromancer and the Solo
Part A are not distinguishable in what they found about the code.

## 2. Evidence found by only one reader

  CLERIC only (separated arm, hostile pass)
    E-C1  duplicate-run float encoding of the curated Mahler tier (29 rows at ~1.0, 21
          Lehmer, 16 Smyth) and its effect on gap statistics; smyth_extremal_vs_rest
          recomputed from READ literals: corr_norm -0.0786 -- CONFIRMED by the judge
          against the executed 09-11 rescan (ADJUDICATION J2).  MEASUREMENT_ERROR
          admitted as a co-cause candidate on this alone (D2).
    E-C2  the verdict is a function of the two marginal density shapes only; the
          Necromancer's "attenuates" was an artifact of Uniform A (P5 WEAKENED, D8)
    E-C3  the normalized leg measures same-vs-opposite quantile-density trend (R2/R3);
          "question-instrument mismatch" characterisation (D1)
    E-C4  Hecate and Erebos consumed every row -> CONSUMER_INERT, not ABSENT (D3)
    E-C5  halt mechanism: one full rotation, mid-sleep termination, stale PID lock (D4)
    E-C6  literal_verdict_lint is vacuous for conditional-chosen pollux_* verdicts
          (P22 WEAKENED, D9) -> instrument-map consequence (FQ-07 demoted)
    E-C7  Necromancer body/proposition contradiction on the verdict map (D14)
    E-C8  exhaustion reached at tick ~37 (< 1 day after c2), not weeks
    E-C9  Erebos _filter_substantive_recent has no novelty gate (salvage item)
    E-C10 C5 (shuffled-split null) would certify the artifact (D11)
    E-C11 c1+c2 census decomposition (D7, rival to the Solo's)

  SOLO only (control arm)
    E-S1  K = 47 two-phase census retrodiction with per-pair rows, plus out-of-fit
          predictions (05-26 census R47/U44/P39; last tick pair/verdict; terminal
          settled_pairs length 54).  NOT found by the separated Necromancer.  Found
          independently by PRIOR (Keeper's executed replay, 09-11).
    E-S2  chance floor of PROMOTED by n regime (~15 % at n 14-16 uniform; 0.25 % at
          n = 72; ~51 % same exponential-gap family)
    E-S3  Ergon "collapsing" template class (LOO drop 0.605)
    E-S4  Theseus-shape rows indistinguishable downstream (P22)
    E-S5  design's own stated expectation for deg10_vs_deg12 vs what the code can do (P21)
    E-S6  five records, four incompatible conclusions about one artifact (P20)
    E-S7  F-C: swapping daemon.py:331-332 below :336-339 as a "repair" that shrinks the
          record and changes nothing (D13)
    E-S8  judge-persona framing: DESIGN_ERROR and CONSUMER_ABSENT are two independent
          sufficient deaths, not rivals (adopted, D3)

  NECROMANCER only (separated arm, reconstructive pass)
    E-N1  package docstring vs daemon docstring disagree on Stygian's role (P23)
    E-N2  the only recorded acceptance test is the deg10 scan (P24)
    E-N3  full consumer hit list with the trace's false positives listed as excluded (P25;
          the Cleric then grep-verified five of them as zero-hit, E-C in 2.9)

  PRIOR only (not reachable by any fresh reader)
    E-P1  executed per-pair corr_norm on the loaded table (9 values)
    E-P2  N1/N2 recurrence of PROMOTED under independence on REAL marginals (up to 0.94)
    E-P3  instrument-null T1-T5 on the daemon statistic
    E-P4  v0.6-only replay does NOT reproduce the census; K = 47 does

## 3. Cause class, FAIR status, hypothesis -- per reader

  reader        primary          rival / co-cause                 halt            FAIR       hypothesis
  Necromancer   DESIGN_ERROR     CONSUMER_ABSENT > INFRASTRUCTURE (inside cause)  (not asked) (not asked)
  Cleric        DESIGN_ERROR     MEASUREMENT_ERROR co-cause >     INFRASTRUCTURE  UNFAIR;    UNTESTED
                (as mismatch)    CONSUMER_INERT                   separate field  weakly FAIR
                                                                                  on rewritten Q
  Solo          DESIGN_ERROR     CONSUMER_ABSENT secondary,       INFRASTRUCTURE  UNFAIR     UNTESTED
                                 independent                      (swarm halt)               ("never tested
                                                                                             did not fail")
  Prior 09-11   DESIGN_ERROR     (T-series instrument nulls)      swarm halt      NO_FAIR_   UNTESTED
                                                                                  TEST
  Judge (final) DESIGN_ERROR     MEASUREMENT_ERROR ADMITTED,      INFRASTRUCTURE  NO_FAIR_   UNTESTED
                (mismatch)       UNRANKED; CONSUMER_ABSENT        own field       TEST
                                 (inert) independent death

The only class-level disagreement in the case is the Cleric's MEASUREMENT_ERROR, and it
was produced by the hostile pass alone.

## 4. Counterfactual agreement (Frankenstein)

  Cleric 3f "changes the result"      dedup each subset by M at 1e-9 in the loader; statistic
                                      untouched; expected: salem_vs_pisot loses PROMOTED
  Cleric 3f "looks like a repair"     permutation null over values before sorting; changes
                                      nothing (P4)
  Solo F-A                            (needs the data) UNTESTABLE_WITHOUT_EXECUTION
  Solo F-B "changes the meaning"      permutation null over the GAP SERIES; a z-scored
                                      corr_norm could refuse where the 0.30 gate cannot
  Solo F-C "changes the shape"        move the removal above the settle check; record
                                      shrinks (narrow_band 53 -> 5 rows); content unchanged
  Agreement                           none of the five is the same mutation.  The two
                                      "permutation null" entries name different operands
                                      (values vs gap series) and do not conflict; the
                                      judge records that "permutation null" without an
                                      operand is not a specification (RQ-18).  The Cleric's
                                      dedup mutation has no counterpart in the Solo arm and
                                      is the one the judge carried into the Frankenstein
                                      descendant spec.

## 5. Self-attack quality (where the arms differ structurally)

  Solo arm.  Part B graded Part A's propositions.  Every WEAKENED it issued was answered
  in the same paragraph by the Part C judge, and the strongest Part A claim ("exact and
  unique" retrodiction, P11) was graded WEAKENED-not-FALLS with the reason "not verified
  against the ledger".  It did not produce a rival decomposition.  It did not find the
  duplicate-encoding hazard, though it read the same _mahler_data.py ranges.  Its Cleric
  persona attacked FAIR/UNFAIR, the certificate, salvage, and the counterfactual -- the
  prompt's list -- and confirmed its own Part A on every proposition of fact.
  Separated arm.  The Cleric issued 2 WEAKENED / 0 FALLS on the Necromancer's 25
  propositions (the propositions were sound), and then, in the sections the prompt calls
  "evidence missed" and "attacks", produced eleven items the Necromancer did not (section
  2, E-C1..E-C11), including the case's only new cause class and the rival that makes the
  Solo's uniqueness claim FALL.  It also re-executed the lint, the census and the traces
  rather than accepting the Necromancer's numbers.
  Read together: on the FACTS of the code the arms tie.  On what a hostile second reader
  ADDS, the separated arm produced the co-cause, the mismatch characterisation, the
  instrument-map correction and the rival decomposition; the solo arm produced the
  retrodiction (which a prior executed replay also had) and the shape-changer
  counterfactual.  The judge does not convert this into a preference between arms from
  one grave; it is one case, and the Solo's retrodiction is the single most detailed
  proposition in the court.

## 6. What the separated Cleric was NOT given
  - the desired verdict (the prompt names no cause class as expected; it permits
    HYPOTHESIS_FAILURE and UNDECIDABLE)
  - the Solo report, the prior dossier, the Keeper's replay, CR-001
  - any Rhadamanthus file other than COMMON_RULES.md, CLERIC_prompt.md and the
    Necromancer report

## 7. Firewall compliance (grade the artifacts, not the stdout)
  All three reports carry section 0 (files_opened / instruments_executed /
  excluded_by_charter).  Each lists engine/necropolis/** (except the three adapters),
  roles/** (except own prompt files), comms/**, ~/.claude/**, and every key/env path as
  excluded and not opened.  None imported charon.agents.pollux; none loaded mahler.py;
  none touched a database or network.  Re-implementations ran on synthetic data or on
  literals read from source text; the Cleric's Known180 side is synthetic fill and says
  so.  The __pycache__ trace that all three flagged is Keeper-caused (ADJUDICATION J3)
  and predates the court.  The judge did not verify the readers' claims about their own
  process beyond reading section 0 of each and checking that no new .pyc, state/ or
  ledger file appeared under charon/agents/pollux/ after the court (see RECEIPT).

## 8. Recorded, not concluded
  One grave.  The prior dossier existed before the court, and its author is the judge;
  the fresh readers reached its class ruling without it, which is the rediscovery
  measurement the charter asked for, and they reached things it does not contain.  The
  charter's "3/3 UNFAIR sample" warning applies here in the other direction: 1/1 is not a
  finding about role separation, it is one case record.
