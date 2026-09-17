# Boot for a round 4 cohort session (lanes B, C, D, E)

Currency: 2026-09-14. The plan is SWARM_R4.md; SWARM_R2.md s4 rules apply
except where SWARM_R4 s6 changes them. Replace <L>/<l> with your lane letter.

## Conductor (operator on mobile)

1. P0 launch gate green (SWARM_R4 s2).
2. Worktrees: `python -m primordial.ops.prepare_worktrees --lanes b,c,d,e --round r4`,
   then each worktree is fast-forwarded to the gate tip.
3. Liveness: `python -m primordial.ops.liveness --watch 60 --post --export-every-min 10`.
4. ONE lane at a time:
   `python -m primordial.ops.schtask_launch launch <L> --worktree F:/Prometheus-worktrees/nestor-r4-<l> --prompt-dir prompts_r4`.
   Wait for its `hello` before the next.

## Session boot

1. You are in F:/Prometheus-worktrees/nestor-r4-<l> (sparse, branch
   nestor/r4-<l>-2026-09-14).
   - Do not pull or create worktrees.
   - `git fetch origin`; `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
2. `python -m comms boot Nestor --model <your model id> --capabilities any`;
   `python -m comms instance` -> PM_TAG.
3. Environment:
   - PY=C:/Users/jcrai/lab/gw-venv/Scripts/python.exe
   - PM_LANE=<L>, PM_TAG=<tag>
   - OMP_NUM_THREADS = NUMBA_NUM_THREADS = your cores (SWARM_R4 s1: B 4, C 3, D 3, E 2)

   Then:
   - `$PY -m primordial.ops.warmup`
   - `$PY -m pytest -q primordial/tests`
   - start your worker in the background: `$PY -m primordial.fabric.worker serve --lane <L>`
   - `$PY -m primordial.bus hello`
4. Read only: SWARM_R4.md (all), roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md,
   primordial/ledger/qd/worlds_r4.json, then `$PY -m primordial.bus inbox`.
5. Loop:
   `/loop Nestor-<L> round 4 iteration: follow SWARM_R4.md s5 (your cohort) and s6`

   Every iteration:
   - `bus beat`, `bus inbox`;
   - one job through your F7 worker;
   - rows at every status;
   - a 3-8 line journal entry in roles/Nestor/sidequests/graphworld/journal/<L>.md.
