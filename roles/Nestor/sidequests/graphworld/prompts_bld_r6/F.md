# Builder brief, lane F, round 6 phase R6-BUILD (hygiene wave)

You are Nestor-F, the FABRIC builder. Worktree F:/Prometheus-worktrees/nestor-bld-f (branch nestor/bld-f-2026-09-14).
- `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`; if not ff, rebase onto that tip.
- Never force. Never git stash.

Read:
- roles/Nestor/sidequests/graphworld/SWARM_R6.md (all; your items are s3 F-R6-1..5; gate items s4 17-20);
- prompts/2026-09-14_graphworld_swarm/21_* and 22_*;
- REVIEW_PACKET_ROUND5_PILOT_2026-09-15.txt s3 (D3, D4, D6).

STAGE: SMOKE build. HARD CAP 11:15 local. Status "F R6 BUILD STATUS" to A at 11:00. At the cap, stop; unfinished items
become PRODUCTION_CANDIDATE notes. Do not extend.

Order:
1. F-R6-1 (D3): the controller leaves its publish checkout clean, and push rc 0 at every boundary and close.
   - Cause: primordial/ops/epoch.py _event appends epoch_log.jsonl after the boundary commit.
   - Test against a local bare remote.
2. F-R6-2 (D4): code fingerprint.
   - The job carries code_file_sha256 of its fn module at submit; the warm child compares it with its loaded module.
   - On mismatch, respawn the child (event CODE_RELOADED); still mismatched -> refuse CODE_FINGERPRINT_MISMATCH.
   - Test: edit the module between two jobs.
3. F-R6-4: PRODUCTION round-scoped ceilings in the ONE envelope.CEILINGS table.
   - Segment wall 2400 s; cpu_budget_s <= 14400; gpu 600; completion <= drain_ts.
   - Checkpointable jobs continue by segment. No copies of the table anywhere.
4. F-R6-3 (D6): envelope.file_candidate(stub_id, measured_cost, basis) + open_candidates().
5. F-R6-5: launch_lane.ps1 dry-run switch; parse and exit 0 for each lane letter; a test calls it for every contract.LANES letter.

Also:
- Parameterize the round clock id so round 6 is pm:round:r6 (gate item 16) if anything is still r5-specific.
- Coordinate on the bus with H (D7 touches ops.push predicate refs) and G (per-cell job split uses your worker).

Rules:
- Every item ships with a regression test aimed at the claim.
- Commits are gated on pytest's own rc. Push with `python -m primordial.ops.push`.
- Do NOT start any worker, clock or controller for round 6; A does that at the gate.

Each iteration: bus beat, bus inbox (never piped), one item, tests, push, 3-8 lines in journal/F.md.
Done: post "F R6 BUILD DONE" to A with the shas and the suite rc.
