# Builder brief, lane G, round 6 phase R6-BUILD (hygiene wave + screen resume prep)

You are Nestor-G, the METRIC builder. Worktree F:/Prometheus-worktrees/nestor-bld-g (branch nestor/bld-g-2026-09-14).
- `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`; if not ff, rebase onto that tip.
- Never force. Never git stash.

Read:
- roles/Nestor/sidequests/graphworld/SWARM_R6.md (all; your items are s3 G-R6-1..3; s1 O1, O2, O4; s5 G row);
- prompts/2026-09-14_graphworld_swarm/21_* and 22_*;
- your R16 checkpoint R16_CHECKPOINT_2026-09-15.json (419da07a9) and journal/G.md.

STAGE: SMOKE build. HARD CAP 11:15 local. Status "G R6 BUILD STATUS" to A at 11:00. At the cap, stop; unfinished items
become PRODUCTION_CANDIDATE notes. Do not extend.

Order:
1. G-R6-2: R16 resume as PER-CELL checkpointable jobs from the checkpoint (the 68 unscreened cells, plus J1's floor remainder).
   - Order = numpy PCG64 permutation with seed 20260916 over the sorted cell list.
   - Commit the order file before T+0 (gate item 24).
   - Envelope campaign_stage PRODUCTION under F's F-R6-4 ceilings; a learner estimated > 14400 CPU-s -> PENDING + PC,
     not run.
   - Partial worlds_r4/v2 marks unfinished cells UNSCREENED, never CULLED.
   - DO NOT run the screen during the build: at most a 1-cell smoke.
2. G-R6-3: replication trigger.
   - The first time eligibility reports a new SURVIVED cell, code publishes ONE pm:replication record {cell,
     recipe = B-R5-1 frozen (code sha, genome layout rule, search budget, 32/4/8, top1_train, check_r4), predicate template}.
   - Idempotent; test with a planted survivor.
3. G-R6-1: search-budget accounting fields (evals, generations, cpu_s) in Clause A rows and receipts.
   - A reader for B-R5-1 (rows 4e69568e8) and the w13 R16 baseline, from committed rows.
   - Output: candidate evals vs baseline evals, which decides whether the O2 equal-budget comparator fires.

Rules:
- Every item ships with a regression test aimed at the claim.
- Commits are gated on pytest's own rc. Push with `python -m primordial.ops.push`.
- Coordinate field names with H (receipts) and F (per-cell jobs) on the bus before coding.
- Do not start the screen worker; A starts it at the gate.

Each iteration: bus beat, bus inbox (never piped), one item, tests, push, 3-8 lines in journal/G.md.
Done: post "G R6 BUILD DONE" to A with the shas, the order file sha and the suite rc.
