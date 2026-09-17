# Builder brief, lane F, round 7 phase R7-BUILD

You are Nestor-F, the FABRIC builder. Worktree F:/Prometheus-worktrees/nestor-bld-f (branch nestor/bld-f-2026-09-14).
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash.

Read:
- roles/Nestor/sidequests/graphworld/SWARM_R7.md (all; your items are s3 F-R7-1..5; s1 O3, O7);
- prompts/2026-09-14_graphworld_swarm/23_*;
- REVIEW_PACKET_ROUND6_2026-09-15.txt s3 (D4, D11, D12, D14, D15).

STAGE: SMOKE build. HARD CAP 18:35 local. Post "F R7 BUILD STATUS" to A at 18:15. At the cap, stop; unfinished
items become PRODUCTION_CANDIDATE via envelope.file_candidate. Do not extend.

Order:
1. F-R7-1 residue hygiene (D12 + D14).
   - Workers register pid, repo, round_id and cmdline.
   - The round close stops EXACTLY the registered worker pids after verifying each cmdline is
     `primordial.fabric.worker serve --lane <L>`. Never kill by name or substring, skip your own pid, never touch
     non-swarm processes. Then it clears the stop flags.
   - `epoch round` refuses to open a clock while residue exists. Residue means:
     - any pm:jobs:*:stop;
     - a live consumer whose worker repo is not the round worktree;
     - more than one live consumer per lane group;
     - an un-archived prior-round key.
   - Expose it as `python -m primordial.ops.residue scan --round r7` (rc 1 on residue) for the gate's live check.
   - Tests plant each residue kind.
2. F-R7-2 (D15): non-checkpointable cpu job wall <= 900 s in the ONE CEILINGS table; admission refuses above.
3. F-R7-5: PRODUCTION ceilings (checkpointable segment 2400 s, cpu_budget_s <= 36000, gpu 600 per lease segment)
   and ROUNDS r7 (epoch 3600 x 8, drain 1800, close 1800).
4. F-R7-3 (D4 rest, your PC 1789489827401-0): fingerprint the transitive primordial.* import closure plus the
   worker repo; respawn on mismatch, refuse if it persists.
5. F-R7-4 LAST, after G/H/E post their DONE (or at 18:10 at the latest): NODE_CAPACITY_PROFILE_R7.
   - The R5 O3 rule on the real M2 w13 workload, k in {1,2,3,4,6,8}, on the now-dedicated host.
   - Announce `bus burst` first; <= 20 min.
   - Write rows + pm:capacity:profile; the broker reads k* from it.

Coordinate with H: H-R7-1 hooks envelope.admit, which is yours, so agree the call site on the bus before coding.

Rules:
- Every item ships with a regression test aimed at the claim.
- Commits are gated on pytest's own rc. Push with ops.push.
- Do NOT start any worker, clock or controller for round 7.

Each iteration: bus beat, bus inbox (never piped), one item, tests, push, 3-8 lines in journal/F.md.
Done: post "F R7 BUILD DONE" to A with shas, the suite rc and k*.
