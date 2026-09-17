# Boot for a round 6 session (lanes B, C, D, E, R = predictor)

Currency: 2026-09-15, Nestor-A[m1-449a9e76]. DRAFT until the launch gate is green. The tool names marked
{G-REPL}, {G-BUDGET} and {H-AP2} are filled from the G and H DONE posts.

The plan is SWARM_R6.md (read it all). Operator authority: messages 21 (6 h end-to-end cap) and 22 (PRODUCTION
stage approved). The conductor's rules are SWARM_R6 s1. Replace <L>/<l> with your lane.

## Session boot

1. You are in F:/Prometheus-worktrees/nestor-r6-<l> (sparse, branch nestor/r6-<l>-2026-09-15).
   - Do not create worktrees.
   - Run `git fetch origin` and `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
2. Identity: `python -m comms boot Nestor --model <your model id> --capabilities any`, then
   `python -m comms instance` -> PM_TAG.
3. Environment:
   - PY=C:/Users/jcrai/lab/gw-venv/Scripts/python.exe
   - PM_LANE=<L>, PM_TAG=<tag>
   - Threads: do NOT set them. The CPU broker grants them per job (k* = 2 tokens host-wide).

   Then run:
   - `$PY -m primordial.ops.warmup`
   - `$PY -m pytest -q primordial/tests`
   - start your worker in the background: `$PY -m primordial.fabric.worker serve --lane <L>`
   - `$PY -m primordial.bus hello`
4. Read only:
   - SWARM_R6.md
   - roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md
   - `$PY -m primordial.bus inbox` (never piped through tail or head)
5. Loop: `/loop Nestor-<L> round 6 iteration: follow SWARM_R6.md s5 for your lane`
   - Every iteration: `bus beat`, `bus inbox`, at most one job through your worker, rows at every status,
     and a 3-8 line journal entry in journal/<L>.md.

## Hard rules (code enforces them; do not argue with a refusal)

- EVERY job carries a full envelope: `worker.submit(..., envelope={campaign_stage: "PRODUCTION"` (or
  `"REPLICATION"` for B's replication), wall_budget_s, cpu_budget_s, gpu_budget_s, expected_output_rows,
  checkpointable, required_controls, required_oracles, cohort: "<L>", predicate_id, experiment_class})`.
- Round 6 ceilings: cpu segment wall <= 2400 s (checkpointable jobs continue by segment); cpu_budget_s <= 14400; gpu
  <= 600 s; projected completion <= drain_ts.
- A STAGE_BUDGET_REFUSAL or NO_NEW_WORK_REFUSAL is a normal outcome. Never resubmit a smaller copy. File the
  measured cost with `envelope.file_candidate(...)`.
- Post the predicate BEFORE the job with
  `primordial.ops.predicate_ref.post_predicate(predicate_id, code_sha, subject, body)`.
  - It pins refs/pm/pred/<id> first and writes code_sha=<sha> as the body's first line.
  - Put the id in the envelope's predicate_id.
  - A receipt whose predicate has no code_sha, or whose ref does not verify, is refused (PREDICATE_CODE_UNREACHABLE).
  - predicate_id charset: [A-Za-z0-9._-].
- Sample fields are explicit: runs_total, rng_family_count, runs_per_family. Clause A verdicts need CANDIDATE_N
  (32 / 4 / 8).
- Every rows file you commit must be cited by a guarded receipt. The close sweep lists any other file as an
  UNRECEIPTED_OBSERVATION.
- After editing any harness module, the worker reloads or refuses by fingerprint. Still say so in your journal.
- The clock is code-owned:
  - 5 x 40 min epochs, T+0-200 (fewer epochs if the clock started late);
  - NO_NEW_WORK at T+200;
  - drain to T+220;
  - close at T+240.

  You never announce epochs and never extend.
- Receipts only after your rows are pushed (ops.push, push lock).
