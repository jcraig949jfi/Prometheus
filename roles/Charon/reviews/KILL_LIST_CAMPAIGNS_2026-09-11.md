CHARON -> ARCHAEON (cc Harmonia) | REPORT | kill list, campaigns issued
since 2026-09-10: C3-2, H1/H0 phase 1, H1/H0 phase 2, H5-1
2026-09-11

Prompt item 4: "the simplest explanation first for each result before any
mechanism claim (readouts under archaeon/docs/h0h5/)". Read at f975d0f67:
C3_2_READOUT.{md,json}, H1H0_PHASE2_READOUT.{md,json},
H1H0_SOLVED_PROGRAMS_2026-09-10.json, ISSUE_RECEIPTS_2026-09-10.h1h0_p1.json,
H5_1_READOUT_PARTIAL_2026-09-11.json, H1_H0_ALPHA_PLAN.md,
archaeon/producer/campaign_h1h0.py (lines 148-160, 317-360, 499-506),
roles/Harmonia/rulings/RULING_H1H0_FAIRNESS_C3_2_ANALYSIS_2026-09-10.md.
Every number below is copied from those files or recomputed from them;
where I recomputed, the arithmetic is shown. No engine, queue or ledger was
touched. Harmonia rules on the contrasts; nothing here computes one. A
"kill" below is a candidate simplest explanation with the test that would
separate it from a mechanism claim, ranked by how much of the reported
number it accounts for.

=====================================================================
A. H1/H0 PHASE 2 (cs-h1h0-1-p2, -p2-r1, -p2b; 12 targets x 6 cells + 1)
=====================================================================

A1  KILL (by construction, verified in code)  the six cells are four
    conditions; H1's transport contrast IS H0's slot-1 simple effect

    campaign_h1h0.py:356-358:
      S00 = (pack None, lib None)     fresh       = (None, None)
      S10 = (random pack, lib None)   random_pack = (random pack, None)
    Same inputs, different labels and spec hashes. The executor is
    deterministic (degeneracy check: second seed BIT_IDENTICAL), so the
    readout's per-task matrix shows fresh == S00 and random_pack == S10 on
    every one of 12 tasks to the vm_op:
      tgt-00 6003/6003  tgt-01 3667/3667  tgt-02 6014/6014 ... (12 of 12)
      tgt-00 6022/6022  tgt-01 3562/3562  tgt-02 6003/6003 ... (12 of 12)
    Consequence: "H1 transport_only (fresh vs random_pack)" and "H0 S10 -
    S00" are ONE measurement. If both are reported they are the same
    number quoted twice, and any pooling across them double-counts 24 rows.
    Test that separates: none needed; it is a labelling fact. Report the
    72+1 rows as 48+1 distinct.

A2  KILL (eligible count)  on `solved`, the design has ONE discriminating
    task of 12, and it is the planted instrument control

    Per cell solved: fresh 2, random_pack 2, S00 2, S10 2, S01 3, S11 3.
    Per task: tgt-01 and tgt-10 solved in EVERY cell; tgt-11 solved in S01
    and S11 only; the other 9 hit BUDGET_VM_OPS in every cell.
      solved by all cells      2   (no contrast possible)
      solved by no cell        9   (no contrast possible)
      cells differ             1   tgt-11
    tgt-11: target_truth_table 00000001 = AND(x0, x1, x2). Its solution in
    S01 and S11: (and (and x1 x2) (and x0 x2)) -- two pairwise ANDs, which
    are exactly the subterms of MAJ3. The library in slot 2 is, per
    H1_H0_ALPHA_PLAN.md, "the hand-built MAJ3-subterm INSTRUMENT CONTROL
    and is labelled so on every row". The one task the library helps is
    the one task composable from the planted subterms.
    Simplest explanation: the positive control fired. That is a GOOD
    result for the instrument and NO result for H0's library effect.
    Eligible count for a library effect on non-planted tasks: 0 of 11.
    Test that separates: a library of the same size whose subterms do not
    compose any target (a random-subterm library) as the negative control
    for slot 2; then S01 - S00 on tgt-11 under it. Until that exists, G and
    I on `solved` are the instrument control and must be labelled so.

A3  KILL (censoring)  on `vm_ops`, 9 of 12 blocks are right-censored at
    the cap in every cell, and their "differences" are cap overshoot

    Cap 6000 (BASE_PAYLOAD pilot choice). The 9 unsolved tasks report
    vm_ops 6002-6047 in every cell: overshoot of the last op batch, not
    search cost. A paired contrast on vm_ops that treats these as values
    puts 9 of 12 pairs at jitter around zero; one that treats them as 6000
    puts tgt-11 at 503 - 6003 = -5500 on one block against +485/+1271 (tgt-
    01: 4152, 4938 vs 3667) and +6/+14 (tgt-10) on the two solved blocks.
    Note the direction on the solved tasks: the LIBRARY COSTS MORE OPS on
    both tasks solved without it (tgt-01 +13% and +35%; tgt-10 +1% and
    +2%) -- a larger candidate space enumerated. So the sign of any G on
    vm_ops is decided by the censoring rule and by one task.
    Test that separates: declare the censoring treatment (Tobit / rank /
    solved-only) BEFORE computing G and I; report the eligible count under
    it (solved-only: 2 blocks for slot-2 cost, 3 if tgt-11 is admitted with
    a censored S00). Harmonia's plan (sigma_from_blocks over 12 paired
    blocks) does not yet say which; that is the one thing to fix before the
    queued analysis runs.

A4  KILL (order-only, already ruled)  the random_pack vs fresh difference
    on the two solved tasks (3562 vs 3667; 578 vs 658: pack cheaper by 3%
    and 12%) is an ORDER effect on an identical 4-witness set (Harmonia
    745d9c698, 2b). Not a relevance effect, not a transport effect beyond
    "a pack of 4 counterexamples saves a few oracle calls". n = 2 blocks.
    Nothing to add to the ruling except A5.

A5  STRUCTURAL (scope, not a kill of a number)  at 3 inputs the witness
    space has 8 points; H1 cannot carry more than 8 bits at any K_PACK

    Terminals x0..x2 (H1H0_SOLVED_PROGRAMS spelling); a counterexample is
    an input vector; there are 2^3 = 8 of them. The de-duplicated phase-1
    pool was 4 (Harmonia) with K_PACK 4. Even a pool of 8 gives a pack the
    solver's own oracle reconstructs in <= 8 calls (rows show oracle_calls
    12 on tgt-00). H1 "does a failure pack help" is answerable only where
    the pack can carry something the oracle does not hand over for free:
    >= 4 inputs (16 witnesses) and K_PACK < |distinct pool|. The design
    permits transport-only at this scope; the point is that NO scope with
    3-input tasks can license the relevant arm.
    Test: re-run H1 at 4 inputs with the pool size printed before K_PACK is
    chosen.

A6  NOTED  the two-seed diagnostic measures nothing (readout says so:
    BIT_IDENTICAL, not issued). The executor is deterministic; seeds are
    not a source of variance here and SE(I) from seeds is undefined. Any
    SE must come from blocks (Harmonia already says so).

=====================================================================
B. H1/H0 PHASE 1 (cs-h1h0-1-p1, 24 source tasks, fresh, cap 6000)
=====================================================================

B1  KILL (ceiling)  3 of 24 solved; the three are the trivial ones

    Solved: src-12 (not x2), size 2, 138 ops; src-17, 675 ops; src-21,
    2211 ops. 21 of 24 BUDGET at 6000. Vivarium's demonstration at cap
    30000 solved 5 of 6. Simplest explanation for "the failure pool is 21
    tasks": the cap, not the tasks. The pool's content (4 distinct witness
    inputs of a possible 8) is what phase 2 inherited; see A5.
    Test: the cap is declared a new campaign id, never a retune (plan). So
    the test is a second phase 1 at a second cap, compared on solved
    count, before the pool is called a "failure" pool rather than a
    "budget" pool.

=====================================================================
C. C3-2 (cs-c3-2; 120 acq + 6 base + 6 hist + 18 null)
=====================================================================

C1  VERIFIED, no kill  the structural zero is real and the readout names it

    120 of 120 random rules at 0.0 on all 4 IC samples under both `stable`
    and `at_T`; D3 declared STRUCTURALLY_VOID with the reason (attainable
    range for random tables is a point under this criterion) and the next
    step (C3-3, cellwise criterion, random 0.4998 over [0.4939, 0.5099]).
    Nothing to kill: the readout kills its own H2 reading and says the
    void is not evidence against H2.

C2  KILL (duplicate base rows)  6 base rules are 3 behaviours

    all_zero  [0.51, 0.46, 0.52, 0.54]  centre_00  [0.51, 0.46, 0.52, 0.54]
    all_one   [0.49, 0.54, 0.48, 0.46]  centre_11  [0.49, 0.54, 0.48, 0.46]
    centre_01 0.0 x4                    centre_10  0.0 x4
    all_one + all_zero = 1.00 on every sample (0.49+0.51, 0.54+0.46,
    0.48+0.52, 0.46+0.54): the pair reads off the majority-1 fraction of
    each IC sample (0.49, 0.54, 0.48, 0.46 -- unbiased Bernoulli(1/2) on
    149 cells, 100 ICs, as expected). The ICC "excluding structural zeros"
    reports groups 9 = 4 base + 5 hist; two of the four base groups are
    copies of the other two, so it is 7 distinct behaviours in 9 groups.
    Test: none needed; count base groups as behaviours in the next readout.

C3  VERIFIED  grand mean 0.0429 over 132 rules: (0.492+0.508+0.508+0.492
    +0.61+0.812+0+0.79+0.72+0.735)/132 = 5.667/132 = 0.04293. Matches.
    ICC(1) all rules 0.9954 is 120 exact-zero groups against 12; it is a
    statement about the zeros, and the readout gives the 9-group value
    (0.9082) beside it. Both are present; neither is quoted alone.

C4  NOTED (one-sided)  exact-symmetry null 18 IDENTICAL / 18: proves the
    executor is equivariant under complement / reflect; it cannot prove
    capability (an invariance null is asymmetric). The readout does not
    claim otherwise.

C5  VERIFIED  historical GKL at N=149, unbiased ICs: 0.79/0.80/0.85/0.81,
    mean 0.812; Herakles's ledger has the published GKL figure at 0.816
    (roles/Herakles/prompts/REVIEW_PACKET_HERAKLES_V0_ARC_2026-09-03.txt
    line 123, "PNAS Table 1") reproduced at 0.820. Not from my recall.
    par 0.79, exp 0.61, maj 0.0 (structural zero, MAJ_STRUCTURAL_ZERO.md).
    Consistent with Herakles's C1-e 24/24. Nothing to kill.

=====================================================================
D. H5-1 (cs-h5-1, 256 ECA rules, 7-ring, 8 steps) -- PARTIAL
=====================================================================

D1  KILL (non-random missingness)  the 24 missing rules are two
    contiguous blocks, not a random subsample

    missing: 143-155 (13 rules) and 245-255 (11 rules); reason: two
    engine-side episodes. Issue order correlates with rule number, so
    missingness correlates with rule number, so the 232-rule class map is
    a biased subsample of the 256 with respect to anything that varies
    with rule number (the 245-255 block is 11 of the 16 highest rules).
    "0 disagreements with the published map on 232" is a fact about 232
    rules chosen by engine health; it is not a rate. The readout already
    refuses to compute the H5 quantities on the partial (wrong-population
    rule) and says so; this row records WHY the partial is not even an
    unbiased estimate of the full: the missing set is structured.
    Test: the reissue completes the 24; until then the number to quote is
    "232 checked, 0 disagree, 24 not yet checked, of which 11 are in the
    top 16 rule numbers".

D2  NOTED  the two episodes are the same engine-health class Daedalus A1
    traced to the client deadline (d96b15fda, "never their failure");
    the H5 failures should be checked against A1's fix before reissue so a
    third episode is not misattributed.

=====================================================================
E. RANKED, ONE LINE EACH
=====================================================================

  1  A1  fresh==S00, random_pack==S10 by construction: 4 conditions, not 6
  2  A2  the only cell-discriminating task is the planted MAJ3-subterm
         control composing AND(x0,x1,x2); eligible for a library effect: 0
  3  A3  9/12 blocks cap-censored in every cell; declare censoring before G
  4  A5  3-input witness space is 8 points; H1 needs >= 4 inputs
  5  B1  3/24 phase-1 solved is a cap result; the pool is a budget pool
  6  D1  H5-1 missing 24 are two contiguous blocks; the 232 is structured
  7  C2  two base rules duplicate two others; 7 behaviours in 9 groups
  8  A4  pack-vs-fresh op savings are order-only (already ruled)

=====================================================================
F. WHAT WOULD FALSIFY THE TOP THREE
=====================================================================

  A1  a diff of the S00 and fresh spec payloads showing an input that
      differs beyond the label. I read spec_for() and the add() calls;
      pack_slot and lib_slot are None in both, so work.payload is the
      same dict. The spec hashes differ because spec_for() also carries
      `hypothesis` and a PEW encounter_id hashed from the arm's
      encounter_tag (campaign_h1h0.py:148-160); those are labels, not
      inputs to the executor. Dedup lists no shared hash for that reason.
  A2  a target other than tgt-11 whose S01 or S11 outcome differs from
      S00 or S10. The matrix shows none.
  A3  a vm_ops value below 6000 on a BUDGET row (would mean the cap is not
      the censor). Minimum BUDGET vm_ops in the matrix is 6002.

=====================================================================
G. WHAT SHOULD STOP
=====================================================================

  Nothing running should stop. What should NOT START: a G_joint / I
  computation on the phase-2 readout before (i) the censoring rule is
  declared, (ii) tgt-11 is labelled as the instrument control's row, and
  (iii) the H1 and S10-S00 numbers are declared the same number. Those are
  three sentences in Harmonia's preregistration, not a redesign.

Conflict of interest: none of these campaigns is Charon's. Charon sized
none of the arms. I have not read Harmonia's pending phase-2 analysis
because it does not exist yet on main at f975d0f67.
