+==========================================================================+
|  HARMONIA[m2-f541bed9] -- REVIEW PACKET                                  |
|  comms #8 (four items) and the #215 handover                             |
|                                                                          |
|  Author:  Harmonia[m2-f541bed9], audit/qualification seat, M2 SPECTREX5  |
|  Date:    2026-09-14                                                     |
|  For:     James (HITL), Archaeon, Charon, Herakles, external reviewers   |
|  Status:  #8 CLOSED; two items leave work on Archaeon                    |
|  Self-contained: no repo access needed; every load-bearing number inline |
+==========================================================================+

--------------------------------------------------------------------------
0. SUMMARY
--------------------------------------------------------------------------

Two Harmonia instances booted on M2 in the same minute. The queue gave
#215 (Daedalus contract step) to m2-54a6d694 and #8 (Archaeon's four
items) to this instance. Outcomes:

  #215  handover   the contract step as delegated was a cycle: the
                   generator refuses an undeployed build, and a contract
                   landed before the restart reads DRIFT for both
                   consumers. Sibling staged it and closed #215.
  #8.1  NO-GO      C3-3 preflight: a printed gate was a constant, false
                   at the declared corpus. My own 3a/3b were also wrong.
  #8.2  NULL-SHAPE H1/H0 phase 2 measures the instrument, not H0.
  #8.3  SPLIT      d3.v2 admitted at the live geometry, refused at small n.
  #8.4  DONE       charter rewritten; April files preserved verbatim.

Four of my own prior statements were corrected this pass (section 6).

--------------------------------------------------------------------------
1. WHAT WAS COMMITTED BEFORE MEASUREMENT
--------------------------------------------------------------------------

  H1/H0 analysis plan   6d276c53f  (before the run; declares it is NOT
                        blind -- the table was already read -- so every
                        scale and censoring treatment is reported)
  d3.v2 calibration plan 2cdd60c4f (before any v2 rate; rules A1-A4 with
                        thresholds from downstream need, INDETERMINATE
                        branch)
  The C3-3 check and region recompute had no separate plan commit; they
  re-derive numbers another seat printed.

--------------------------------------------------------------------------
2. ITEM 1 -- C3-3 PREFLIGHT (be82cdd8b)
--------------------------------------------------------------------------

  Printed:  "regions with >= 8 non-degenerate expected = 10" at corpus 120.
  Code:     expected_per_region = corpus*f/10; regions_ge8 = 10 if >= 8.
  Measured: popcount "deciles" of Binomial(128,1/2) cannot be equal.
            Exact masses .1252 .0880 .1161 .1355 .0704 .0693 .1274 .1027
            .0731 .0923 (two bins are single popcount values 64 and 65).
            Expected regions >= 8 at 120: 8.46. P(all 10 >= 8): 0.123 (MC).

  Remedies (MC 4000):
    option                     corpus reg P(all>=8) D3 band chance floor
    A as declared                120   10   0.123        0.379
    B corpus raised              180   10   0.834        0.136
    C merge 64/65                120    9   0.396        0.261
    D merge + raised             156    9   0.843        0.132
  Ruling: A, C refused; B recommended (changes no declared population);
  D admissible if the merge is committed before any row is read.

  Constants, executed on all four IC samples (24/24 incl. negative and
  cheat controls): location = the sample's majority share (0.52 0.49 0.52
  0.47; all_one its exact complement), dispersion = sqrt(p(1-p)) (0.4991-
  0.4999). My 09-10 ruling said "exactly 0.5, dispersion structurally
  ZERO"; Archaeon's amendment said "dispersion exactly 0.5". Both wrong.
  Six baseline rules are THREE measurements (centre_00=all_zero,
  centre_11=all_one, centre_01=centre_10, exact at every seed).

--------------------------------------------------------------------------
3. ITEM 2 -- H1/H0 PHASE-2 CONTRASTS (341a92b89)
--------------------------------------------------------------------------

  Provenance, printed first: S00 ran in sets p2/p2-r1 with NO allowance;
  S10, S01, S11 in p2b under reservation. Every contrast vs S00 crosses
  a deploy (CROSS-DEPLOY, reported, not estimated).

  Solve fraction, 12 blocks:
    G = S11-S00   +0.0833 [-0.130, +0.297]   1 block (tgt-11, the planted
                                              MAJ3-subterm control)
    I, transport  NOTHING_COULD_FIRE
  11 blocks (control out): every contrast NOTHING_COULD_FIRE.
  vm_ops, three censoring treatments, G signs: solved-only +, cap -,
  rank +  -> CENSORING-DETERMINED. Solved-only n = 2.
  Charon's A2 (eligible count 0 of 11) and A3 (censoring sets the sign)
  confirmed by execution. Confirmation sizing from these variances refused.

  Incidents: run 1 crashed in the positive control (my guessed field
  names); run 2 was aborted by the CHEAT control (S11:=S00 gave G=+0.167
  on the rank scale -- positional ranks on ties). Both fixed before any
  estimate was read. Plan deviation: shared-arm correlation not computed
  on vm_ops scales (undefined on solve scale). Stated, not repaired.

--------------------------------------------------------------------------
4. ITEM 3 -- d3.v2 CALIBRATION (ca0dd0fd7)
--------------------------------------------------------------------------

  Real detector code, v1 and v2 on the same corpora, 30 cells x 600.
  Harness controls: stub-always 1.000, stub-never 0.000, positive 0.98.

    geometry           A1 no cost on iid    A2 removes trend    verdict
    LIVE  36 vs 4x36   0.0002 vs 0.0004     0.000 vs 0.000      ADMITTED
    FLOOR  8 vs 4x8    0.1125 vs 0.0898 F   pass                REFUSED
    UNEQUAL 8 vs 4x40  0.0117 vs 0.0067 F   0.577: +0.040 F     REFUSED
  (A3 between-means immunity and A4 power pass everywhere.)
  Exact F references agree: FLOOR v1 0.0883/F(7,28) 0.0857, v2
  0.1167/F(6,24) 0.1122 -- the fitted slope costs one df per group.

  What v2 is for, at LIVE: trended null -- v1 fires 0.530, v2 0.000;
  real low-dispersion region that trends -- v1 detects 0.028, v2 0.997.

  Findings in Archaeon's code (not edited): P-DF df not adjusted; P-LIN a
  perfectly linear region fires LOWER at ratio 0.0; P-LAB a v2 signal's
  exchangeability label is computed on raw rows (reported serial_r 0.801
  where the tested residuals have 5e-17).
  My 09-10 "nine detrended survivors" used /(n-2); the admitted v2 uses
  /(n-1) -> survivors and watch-list PROVISIONAL. Live eligibility count
  cannot be rebuilt from the committed dossier (fired regions only):
  delegated to Archaeon (#260).

--------------------------------------------------------------------------
5. ITEM 4 AND #215
--------------------------------------------------------------------------

  HARM-36 (c0f0641af): RESPONSIBILITIES/CHARTER rewritten for the audit
  seat; April files git-mv'd, blobs unchanged; April queue classified
  0 STILL_LIVE, 8 PARKED, 2 SUPERSEDED; three items NOT_EXAMINED rather
  than guessed. Charter principles each cite a committed ruling.
  #215 handover (c4ea5840b): live /v2/version 5380cb90 vs candidate
  726275da; generator line 171 refuses; conformance_check reads an extra
  contract route as a removal (state 1); engine_instance_id is ledger
  meta so a staged contract can carry production's id.

--------------------------------------------------------------------------
6. DEFECTS AND PROCESS HOLES (mine)
--------------------------------------------------------------------------

  - Three of my prior ruling statements were wrong (3a/3b constants, 3e
    "near-certain null" is asymptotic -- 0.379 at n=120, 5b procedure
    not the admitted detector). Annotated beside the originals.
  - D-23 s5 lapse: one push of a merge before re-running tests on the
    merged tree; repaired after (11/11), and the chain now re-tests.
  - Five defects in my own scripts caught before results were read
    (field names, rank ties, refusal keyed on observables, two harness
    bugs). The H1/H0 plan was written after seeing the rows.
  - SE(diff) in d3.v2 rules is independent-binomial (conservative); a
    paired SE would narrow margins, and could not turn a FAIL to PASS.

--------------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH
--------------------------------------------------------------------------

  DOES: C3-3 cannot issue as printed; phase 2 carries no H0/H1 evidence;
  d3.v2 behaves correctly on synthetic Gaussian rows at n~36.
  DOES NOT: that live rows are Gaussian or near 36 per region; that the
  allowance mechanism changes CEGIS outcomes (untested); anything about
  whether H0, H1 or H2 are true.

--------------------------------------------------------------------------
8. DECISIONS
--------------------------------------------------------------------------

  Archaeon: choose B or D and re-run the preflight (G1-G6 mechanical);
            produce the v2 live dossier; decide on P-DF/P-LIN/P-LAB.
  Operator: whether C3-3 is worth issuing at all. Lean: only if H2 has a
            consumer; phase 2 shows this design family can end as
            "instrument works, question unanswerable".
  Harmonia: HARM-30 (shared-arm correlation) remains open.

--------------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
--------------------------------------------------------------------------

  1. Is refusing FLOOR a false economy? Live regions near the floor
     would then run v1, whose trended false-fire rate is 0.53.
  2. Is "report every treatment, headline none" an adequate substitute
     for blindness, or does it just move the forking paths to the reader?
  3. Should phase 2's null shape stop the H1/H0 line at 3-input tasks
     entirely, rather than asking for a better corpus?
  4. Is the A2 FAIL at |r| 0.577 (margin 0.004, non-monotone) a rule
     working or a rule too tight to mean anything at 600 corpora?

--------------------------------------------------------------------------
10. ARTIFACTS (repo-relative, all on origin/main)
--------------------------------------------------------------------------

  c4ea5840b  prompts/2026-09-14_m2-f541bed9_sibling/01_NOTE_...215.md  #254
  be82cdd8b  rulings/RULING_3B_C3_3_PREFLIGHT_2026-09-14.md            #255
             science/c3_3_{baseline_ic_sample_check,region_recompute,
             region_remedies}.py + ledgers
  6d276c53f  qualification/h0h5/h1h0_phase2_analysis_plan_2026-09-14.md
  341a92b89  rulings/RULING_H1H0_PHASE2_CONTRASTS_2026-09-14.md        #257
             qualification/h0h5/h1h0_phase2_analysis.py + ledger
  2cdd60c4f  science/d3v2_calibration_plan_2026-09-14.md (main 916e2ff24)
  ca0dd0fd7  rulings/RULING_D3V2_CALIBRATION_2026-09-14.md             #259
             science/d3v2_{calibration,adjudicate}.py + ledgers
             prompts/2026-09-14_m2-f541bed9_d3v2/01_DELEGATION_...      #260
  c0f0641af  RESPONSIBILITIES.md, CHARTER.md, superseded/, report      #261
  (paths under roles/Harmonia/; journal journal/2026-09-14_m2-f541bed9.md)

+==========================================================================+
|  END. "Not worth continuing" is a first-class answer -- for C3-3, for    |
|  the 3-input H1/H0 line, and for d3.v2 below n=36.                       |
+==========================================================================+
