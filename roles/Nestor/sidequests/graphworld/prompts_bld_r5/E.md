# Builder brief, lane E, round 5 phase P-BUILD (delivered to the live E session)

You are Nestor-E, WATCHMAKERS (tooling), round 5 P-BUILD. You stay in F:/Prometheus-worktrees/nestor-r4-e.
- First: `git fetch origin` then `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- No primary science.

Read:
- SWARM_R5.md (your items are s3 E-R5-1..3; s1 O1 and O6 bind them);
- prompt 19 s6 and s9;
- your E-R4-1 receipt (the rand_graft weakness).

STAGE: SMOKE-stage build, HARD CAP 2 h wall from this brief.

Order:
1. E-R5-1 hardened Clause B control, preregistered on the bus BEFORE coding.
   - Sham: a structure-preserving displaced graft for the linear genome. The donor weight matrix keeps norms, sparsity and
     decoder, but its observation-feature axis is permuted by a seeded permutation.
   - Also: equal-budget scratch and paired run seeds.
   - check-b PASS requires beating BOTH.
   - Validate on a planted positive (self graft) and a planted negative (random donor) before any live pair.
   - Record the control version id.
   - No live pair in P-BUILD. The live pair is a round 5 pilot job under the O1 donor rule.
2. E-R5-2 GPU queue + arbiter:
   - pm:gpu:jobs, max_gpu_wall_s 600, the lease held for every timing row;
   - recorded fields per prompt 19 s6;
   - timeout gives a checkpoint + PRODUCTION_CANDIDATE.
3. E-R5-3 GPU-1..3 harness wiring from the W (primordial/nv/warp), U (nv/cudagraph) and P (nv/precision) MVP code:
   - exactness oracle first;
   - numba at 1/2/4/8 threads;
   - transfer cost included unless resident.
   - Wiring and a 1-cell smoke only. The real GPU-1..3 runs happen in the pilot clock.
   - GPU venvs are nv-venv-w/u/p; never pip into gw-venv.

Coordinate the GPU queue with F's job envelope (gpu_budget_s, campaign_stage) before coding.

At 1 h 45 m post "E BUILD STATUS". At 2 h stop and post "E R5 BUILD DONE" with shas. Items not done become
PRODUCTION_CANDIDATE notes.

Tests gate commits; push via ops.push; journal E.md.
