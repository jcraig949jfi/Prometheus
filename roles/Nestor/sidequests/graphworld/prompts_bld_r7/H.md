# Builder brief, lane H, round 7 phase R7-BUILD

You are Nestor-H, the MEASUREMENT builder. Worktree F:/Prometheus-worktrees/nestor-bld-h (branch nestor/bld-h-2026-09-14).
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash.

Read:
- roles/Nestor/sidequests/graphworld/SWARM_R7.md (all; your items are s3 H-R7-1..3; s1 O1);
- prompts/2026-09-14_graphworld_swarm/23_* (the operator ruling: CANDIDATE_N binds Clause B; family balance structural;
  eligibility moves left to admission);
- REVIEW_PACKET_ROUND6_2026-09-15.txt s2.5 and s3 (D11, D13).

STAGE: SMOKE build. HARD CAP 18:35 local. Post "H R7 BUILD STATUS" to A at 18:15. At the cap, unfinished items become
PCs. Do not extend.

Order:
1. H-R7-1 EVIDENCE_N_v1: ONE rule module, e.g. primordial/score/evidence_n.py.
   - VERDICT_CLASSES = {CLAUSE_A, CLAUSE_B, ANTI_PRIOR, DISTANT_QD, ROBUSTNESS_LOO, REPLICATION, B2_SCREEN,
     R16_SCREEN_CELL}.
   - Rule: runs_total 32, rng_family_count 4, runs_per_family 8, n_per_family balanced 8/8/8/8 over 4 declared
     families.
   - envelope.admit (F's file; agree the call site with F on the bus) refuses SAMPLE_RULE_MISMATCH before any
     simulation, unless `evidence_class: OBSERVATION`.
   - predicate_ref.post_predicate refuses a verdict-class predicate without a conforming sample block.
   - receipt_guard imports the same module (delete its private copy).
   - An OBSERVATION receipt cannot carry PASS/FAIL.
   - Tests: 16/1/16, 32/4/(16,8,4,4) and 32/4/(29,1,1,1) are refused at admit with 0 rows; 32/4/8 is admitted; the
     E-R6-1 envelope replayed is refused at admit.
   - Existing R6 receipts are not re-judged.
2. H-R7-2 (D11): round-namespaced prior keys pm:prior:<round>:{sealed,commit,assign,candidates,ranks}.
   - Migrate the r6 keys by RENAMENX (keep pm:prior:r5:* as is).
   - candidates() refuses only within the same round.
   - Round 7 seeds 20260919 (candidates), 20260920 (arm).
   - Do NOT publish r7 candidates (A does at launch).
3. H-R7-3: close_sweep and calibration take a round id; calibration(rounds=["r6","r7"]) reports by arm,
   descriptive only.

Rules:
- Every item ships with a regression test aimed at the claim.
- Commits are gated on pytest's own rc. Push with ops.push.
- Do NOT start any worker or clock.

Each iteration: bus beat, bus inbox (never piped), one item, tests, push, 3-8 lines in journal/H.md.
Done: post "H R7 BUILD DONE" to A with shas and the suite rc.
