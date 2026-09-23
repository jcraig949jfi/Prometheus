# Builder brief, lane G, round 5 phase P-BUILD (delivered to the live G session)

You are Nestor-G, the METRIC builder, round 5 P-BUILD. You stay in your worktree F:/Prometheus-worktrees/nestor-bld-g.
- First: `git fetch origin` then `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Your R16 re-screen stays PARKED (operator 18). Do not resume it.

Read:
- SWARM_R5.md (your items are s3 G-R5-1..4; s1 O2 and O4 bind them);
- prompt 19.

STAGE: SMOKE-stage build, HARD CAP 2 h wall from this brief.

Order:
1. G-R5-4 w13 eligibility lookup: B needs it at T+0.
2. G-R5-2 CANDIDATE_N.
3. G-R5-1 explicit seed schema (runs_total / rng_family_count / runs_per_family; invariant; lint that fails on "N x M" run
   counts in new receipts or tables).
4. G-R5-3 B2 admission rule, coded before any B2 data:
   - pilot sample runs_total 16, rng_family_count 2, runs_per_family 8;
   - floor suite + learned baseline top1_train;
   - the four verdicts exactly as SWARM_R5 s3;
   - never SURVIVED;
   - plus a cost estimate for a full B2 screen.

Coordinate field names with F (job envelope) and H (receipt guard) on the bus before coding.

At 1 h 45 m post "G BUILD STATUS". At 2 h stop and post "G R5 BUILD DONE" with shas. Items not done become
PRODUCTION_CANDIDATE notes.

Tests gate commits (pytest rc); push via ops.push; journal G.md.
