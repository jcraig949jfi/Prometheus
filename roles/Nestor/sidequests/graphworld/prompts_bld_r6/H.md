# Builder brief, lane H, round 6 phase R6-BUILD (hygiene wave)

You are Nestor-H, the MEASUREMENT builder. Worktree F:/Prometheus-worktrees/nestor-bld-h (branch nestor/bld-h-2026-09-14).
- `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`; if not ff, rebase onto that tip.
- Never force. Never git stash.

Read:
- roles/Nestor/sidequests/graphworld/SWARM_R6.md (all; your items are s3 H-R6-1..3; s1 O3; gate items s4 21-23);
- prompts/2026-09-14_graphworld_swarm/21_* and 22_*;
- REVIEW_PACKET_ROUND5_PILOT_2026-09-15.txt s3 (D7, D10) and s2.6.

STAGE: SMOKE build. HARD CAP 11:15 local. Status "H R6 BUILD STATUS" to A at 11:00. At the cap, stop; unfinished items
become PRODUCTION_CANDIDATE notes. Do not extend.

Order:
1. H-R6-1 (D7): predicate code stays reachable forever.
   - At predicate post, push refs/pm/pred/<predicate_id> -> the cited commit.
   - The receipt guard refuses PREDICATE_CODE_UNREACHABLE unless that ref exists on origin and resolves to the cited sha,
     or the patch-id matches.
   - Test: a rebase orphans the branch commit, and verify still passes via the ref.
   - Coordinate with F (ops.push owner).
2. H-R6-2 (D10): close sweep.
   - Every rows file committed in the round window is cited by a guarded receipt, or an UNRECEIPTED_OBSERVATION event
     names it.
   - Planted unreceipted file test.
3. H-R6-3 anti-prior v2 (O3): candidates n=48 with seed 20260917.
   - The ledger stores prior_p_pass AND rank/quantile among the sealed set; ties are broken by seeded order and recorded.
   - assign() decides the arm by seeded Bernoulli(0.25) with seed 20260918: calibration = top rank quartile, anti-prior =
     bottom quartile.
   - calibration() reports by arm. R is never told the arms.
   - Do NOT publish candidates for round 6 during the build (A publishes once at launch).

Rules:
- Every item ships with a regression test aimed at the claim.
- Commits are gated on pytest's own rc. Push with `python -m primordial.ops.push`.
- Do NOT start any worker or clock.

Each iteration: bus beat, bus inbox (never piped), one item, tests, push, 3-8 lines in journal/H.md.
Done: post "H R6 BUILD DONE" to A with the shas and the suite rc.
