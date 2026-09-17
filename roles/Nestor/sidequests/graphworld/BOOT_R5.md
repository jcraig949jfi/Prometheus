# Boot for a round 5 pilot session (lanes B, C, D, E, R = predictor)

Currency: 2026-09-15, Nestor-A[m1-449a9e76]. DRAFT until the launch gate is green; the tool names
marked {H-LEDGER} and {E-GPUQ} are filled from H's and E's DONE posts.

The plan is SWARM_R5.md (read it all). Operator authority is message 19; the conductor's overrides are
SWARM_R5 s1. Replace <L>/<l> with your lane.

## Session boot

1. You are in F:/Prometheus-worktrees/nestor-r5-<l> (sparse, branch nestor/r5-<l>-2026-09-15).
   - Do not create worktrees.
   - Run `git fetch origin` and `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
2. Identity: `python -m comms boot Nestor --model <your model id> --capabilities any`, then
   `python -m comms instance` -> PM_TAG.
3. Environment:
   - PY=C:/Users/jcrai/lab/gw-venv/Scripts/python.exe
   - PM_LANE=<L>, PM_TAG=<tag>
   - Threads: do NOT set them yourself. The CPU broker (NODE_CAPACITY_PROFILE_R5, pm:capacity:profile)
     grants them per job.

   Then run:
   - `$PY -m primordial.ops.warmup`
   - `$PY -m pytest -q primordial/tests`
   - start your worker in the background: `$PY -m primordial.fabric.worker serve --lane <L>`
   - `$PY -m primordial.bus hello`
4. Read only:
   - SWARM_R5.md
   - roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md
   - `$PY -m primordial.bus inbox`
5. Loop: `/loop Nestor-<L> round 5 pilot iteration: follow SWARM_R5.md s5 for your lane`
   - Every iteration: `bus beat`, `bus inbox`, at most one job through your worker, rows at every status,
     and a 3-8 line journal entry in journal/<L>.md.

## Hard rules (code enforces them; do not argue with a refusal)

- EVERY job is submitted with a full envelope: `worker.submit(..., envelope={campaign_stage: "PILOT",
  wall_budget_s, cpu_budget_s, gpu_budget_s, expected_output_rows, checkpointable, required_controls,
  required_oracles, cohort: "<L>", predicate_id, experiment_class})`.
- A STAGE_BUDGET_REFUSAL or NO_NEW_WORK_REFUSAL is a normal outcome.
  - Do not resubmit a smaller copy to get around it.
  - File the PRODUCTION_CANDIDATE that F's admission writes, with your measured cost.
- Post the predicate BEFORE the job, and put its bus id in predicate_id. The receipt guard refuses a
  receipt whose predicate is later than the run.
- Sample fields are explicit: runs_total, rng_family_count, runs_per_family. Never write "N x M" for
  run counts.
- Clause A verdicts require CANDIDATE_N (runs_total >= 32, rng_family_count >= 4,
  runs_per_family >= 8). Anything smaller is labelled PILOT, and the real judge refuses it. That refusal
  is expected, not a failure.
- The clock is code-owned:
  - epochs T+0-25, 25-50, 50-75, 75-100;
  - NO_NEW_WORK at T+100;
  - drain to T+110;
  - close at T+120.

  You never announce epochs and never extend.
- Receipts only after your rows are pushed (ops.push, push lock). The guard checks everything else.
