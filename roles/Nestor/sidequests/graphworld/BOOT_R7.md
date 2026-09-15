# Boot for a round 7 session (lanes B, C, D, E, R = predictor)

Currency: 2026-09-15, Nestor-A[m1-449a9e76]. DRAFT until the launch gate is green. The names marked {H-EVN},
{H-AP-R7} and {F-RESIDUE} are filled from the builders' DONE posts.

The plan is SWARM_R7.md (read it all). Operator authority: messages 22 (PRODUCTION) and 23 (12 h overnight;
CANDIDATE_N binds Clause B). The conductor's rules are SWARM_R7 s1. The operator is ASLEEP: never wait for an
operator answer. An unanswerable question becomes a production candidate (envelope.file_candidate) or an OPEN
note in your final post. Replace <L>/<l> with your lane.

## Session boot

1. You are in F:/Prometheus-worktrees/nestor-r7-<l> (sparse, branch nestor/r7-<l>-2026-09-15).
   - Do not create worktrees.
   - Run `git fetch origin` and `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
2. Identity: `python -m comms boot Nestor --model <your model id> --capabilities any`, then
   `python -m comms instance` -> PM_TAG.
3. Environment:
   - PY=C:/Users/jcrai/lab/gw-venv/Scripts/python.exe
   - PM_LANE=<L>, PM_TAG=<tag>
   - Threads: do NOT set them. The CPU broker grants them per job (k* from NODE_CAPACITY_PROFILE_R7).

   Then run:
   - `$PY -m primordial.ops.warmup`
   - `$PY -m pytest -q primordial/tests`
   - start your worker in the background, from THIS worktree: `$PY -m primordial.fabric.worker serve --lane <L>`.
     It registers pid + repo + round.
   - `$PY -m primordial.bus hello`
4. Read only:
   - SWARM_R7.md
   - roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md
   - `$PY -m primordial.bus inbox` (never piped through tail or head)
5. Loop: `/loop Nestor-<L> round 7 iteration: follow SWARM_R7.md s5 for your lane`
   - Every iteration: `bus beat`, `bus inbox`, at most one job through your worker, rows at every status,
     and a 3-8 line journal entry in journal/<L>.md.

## Hard rules (code enforces them; do not argue with a refusal)

- EVIDENCE_N_v1 ({H-EVN}):
  - A job whose experiment_class can emit a verdict must carry runs_total 32, rng_family_count 4,
    runs_per_family 8 and n_per_family 8/8/8/8 over 4 declared families.
  - Anything else is refused SAMPLE_RULE_MISMATCH at admission with zero simulation, unless the envelope
    declares evidence_class OBSERVATION. An OBSERVATION can never become PASS/FAIL.
  - Dry-run envelope.admit on your envelope BEFORE posting the predicate.
- Every job carries the full envelope: campaign_stage PRODUCTION (or REPLICATION), wall_budget_s, cpu_budget_s,
  gpu_budget_s, expected_output_rows, checkpointable, required_controls, required_oracles, cohort, predicate_id,
  experiment_class, sample block.
- Ceilings:
  - checkpointable cpu segment <= 2400 s, cpu_budget_s <= 36000;
  - NON-checkpointable cpu job <= 900 s wall;
  - gpu <= 600 s per lease segment.
- A STAGE_BUDGET_REFUSAL / NO_NEW_WORK_REFUSAL / SAMPLE_RULE_MISMATCH is a normal outcome.
  - Never resubmit a smaller copy.
  - Never relabel to OBSERVATION after a refusal to get a run through: the evidence class is decided in the
    predicate, before the first submit.
- Post predicates with `primordial.ops.predicate_ref.post_predicate(...)`: it pins the code and validates the sample
  block.
- After editing ANY harness module, restart your worker. The fingerprint now covers imports too; say so in your
  journal anyway.
- Every rows file you commit must be cited by a guarded receipt, or the close sweep lists it.
- The clock is code-owned:
  - 8 x 60 min epochs;
  - NO_NEW_WORK T+480;
  - drain T+510;
  - close T+540.

  You never announce epochs and never extend.
- At close: post ONE '<L> ROUND 7 FINAL' note to A (receipts, unreceipted rows, PCs, open claims, own errors),
  then stop your worker.
