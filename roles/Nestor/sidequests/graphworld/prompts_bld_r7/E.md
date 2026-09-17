# Builder brief, lane E, round 7 phase R7-BUILD (Clause B family axis + GPU track + B2 overhead)

You are Nestor-E. Build in your worktree F:/Prometheus-worktrees/nestor-r6-e.
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash.
- GPU work uses nv-venv-w (warp) / nv-venv-u (CUDA graphs) through the GPU queue lease. The machine is dedicated overnight.

Read:
- roles/Nestor/sidequests/graphworld/SWARM_R7.md (all; your items are s3 E-R7-1..3; s1 O1, O2, O5);
- prompts/2026-09-14_graphworld_swarm/23_*;
- E_R6_3_DISPATCH_SURFACE.md (your own crossover table: GPU wins only in bounded regimes).

STAGE: SMOKE build. HARD CAP 18:35 local. Post "E R7 BUILD STATUS" to A at 18:15. At the cap, unfinished items become
PCs. Do not extend.

Order:
1. E-R7-1 Clause B family axis.
   - transfer_v2 run seeds = families (4200, 2101, 3303, 5501) x run seeds 16..23 (disjoint from E-R4-1's 0..15,
     per check_seeds).
   - check_b v2 pairs graft/scratch/sham within family and run seed.
   - Envelope sample block per H's EVIDENCE_N_v1: runs_total 32, rng_family_count 4, runs_per_family 8.
   - Re-validate the planted positive (self graft) and negative (random donor) at 32/4/8 on the cheap planted
     pair. The live w14 -> w13 pair runs IN the clock, not now.
2. E-R7-2 GPU TRACK (O2), a batched GPU evaluator for the R16 cell workload (G's r16_cells.cell_job):
   - One device batch per generation holds all 32 runs x 128 genomes x train episodes. The QD search, mutation
     and per-run RNG streams stay on CPU and unchanged; only evaluation is batched.
   - Exactness oracle first, on one REAL cell (train8 and train128 if time): every evaluated fitness equals the numba
     reference, and each run's elites are identical. Any miss is INSTRUMENT_FAIL, with no throughput number.
   - Then the O2 comparison on the same cell: end-to-end cells/hour for GPU (h2d included, compile reported
     separately) vs the best CPU config (threads from the dispatch surface). Median of reps, same estimator on both
     sides.
   - The code computes GPU_ADOPT iff oracle clean AND ratio >= 1.25, else GPU_REJECT, and writes pm:r7:gpu_adopt
     with rows.
   - Predicate first; guarded receipt.
3. E-R7-3 B2 search overhead: one B2 spec, a short QD run (for example 20 generations) with the compiled rollout.
   - Measured overhead per generation (mutation/archive/assembly) vs rollout time.
   - Hand the figure to G for the B2 v2 (32/4/8) admission cost.

Rules:
- Every item ships with a regression test.
- Commits are gated on pytest's own rc. Push with ops.push.
- Do not start the live Clause B pair or any B2 screen during the build.

Each iteration: bus beat, bus inbox (never piped), one item, tests, push, journal/E.md.
Done: post "E R7 BUILD DONE" to A with shas, the GPU decision + ratio, the B2 overhead and the suite rc.
