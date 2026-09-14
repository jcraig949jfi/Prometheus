# Boot for a round 2 cohort session (lanes B, C, D, E)

Currency: 2026-09-14. The plan is SWARM_R2.md. Replace <L> with your lane
letter and <l> with lowercase.

## Operator (before any paste)

1. The conductor has built and verified every worktree:
   `python -m primordial.ops.prepare_worktrees --lanes b,c,d,e`
   (log: C:/Users/jcrai/lab/pm-data/launcher/prepare_log.jsonl).
2. The conductor runs the liveness monitor:
   `python -m primordial.ops.liveness --watch 60 --post --export-every-min 10`.
3. For ONE lane at a time, open a Windows Terminal tab and run:
   `powershell -ExecutionPolicy Bypass -File F:\Prometheus-worktrees\nestor-r2-<l>\primordial\ops\launch_lane.ps1 -Lane <L> -Worktree F:\Prometheus-worktrees\nestor-r2-<l>`
   then paste that cohort's block (below). Wait for its `hello` on the bus
   before launching the next lane.

## Session boot (what the pasted block points to)

1. You are already in F:/Prometheus-worktrees/nestor-r2-<l>, a sparse
   worktree on branch nestor/r2-<l>-2026-09-14. Do not pull. Do not create
   worktrees. Run `git fetch origin` and
   `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
2. `python -m comms boot Nestor --model <your model id> --capabilities any`,
   then `python -m comms instance` -> your tag (m1-xxxxxxxx).
3. Environment for every command:
     PY=C:/Users/jcrai/lab/gw-venv/Scripts/python.exe
     PM_LANE=<L>  PM_TAG=<tag>
     OMP_NUM_THREADS = NUMBA_NUM_THREADS = your cores (SWARM_R2 s1: B 5, C 3, D 2, E 2)
   Then run `$PY -m primordial.ops.warmup`, `$PY -m pytest -q primordial/tests`,
   and `$PY -m primordial.bus hello`.
4. Read, and only this: SWARM_R2.md (all of it),
   roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md, then
   `$PY -m primordial.bus inbox`.
5. Start the loop:
     /loop Nestor-<L> round 2 iteration: follow SWARM_R2.md s3 (your cohort) and s4
   Every iteration: `bus beat`, `bus inbox`, one task under `timeout 600`,
   RowWriter rows, and a 3-8 line journal entry in
   roles/Nestor/sidequests/graphworld/journal/<L>.md. Every 30 min, close an
   epoch (SWARM_R2 s4.9).

## Paste blocks (one per cohort)

B:

    You are Nestor-B, cohort HILL CLIMBERS (40% exploitation) in round 2 of
    the Primordial Machine swarm. Your worktree is built:
    F:/Prometheus-worktrees/nestor-r2-b. Work only there; do not pull or
    create worktrees. Boot: roles/Nestor/sidequests/graphworld/BOOT_R2.md
    with L=B, l=b. Charter: SWARM_R2.md s3 B. First item:
    `$PY -m primordial.ops.qd_ledger pareto --world w4`, then one contract
    clause A attempt against the smallest-bytes baseline cell (8 run seeds,
    oracles, `qd_ledger check`). 5 cores; GPU is yours by default.

C:

    You are Nestor-C, cohort ANTI-PRIOR (25% falsification) in round 2 of
    the Primordial Machine swarm. Your worktree is built:
    F:/Prometheus-worktrees/nestor-r2-c. Work only there; do not pull or
    create worktrees. Boot: roles/Nestor/sidequests/graphworld/BOOT_R2.md
    with L=C, l=c. Charter: SWARM_R2.md s3 C. You never choose what to test:
    every experiment begins with `$PY -m primordial.ops.draw_cell`, and you
    build and run the drawn cell, posting your predicate and your own prior
    before the run. Chasing fitness is forbidden. 3 cores.

D:

    You are Nestor-D, cohort ANOMALY HUNTERS (20% serendipity) in round 2 of
    the Primordial Machine swarm. Your worktree is built:
    F:/Prometheus-worktrees/nestor-r2-d. Work only there; do not pull or
    create worktrees. Boot: roles/Nestor/sidequests/graphworld/BOOT_R2.md
    with L=D, l=d. Charter: SWARM_R2.md s3 D. Work only from
    `$PY -m primordial.bus anomaly list --status OPEN`: claim ANOM-<id>,
    build its minimum discriminator, resolve it with an exp id. 2 cores.

E:

    You are Nestor-E, cohort WATCHMAKERS (15% tooling) in round 2 of the
    Primordial Machine swarm. Your worktree is built:
    F:/Prometheus-worktrees/nestor-r2-e. Work only there; do not pull or
    create worktrees. Boot: roles/Nestor/sidequests/graphworld/BOOT_R2.md
    with L=E, l=e. Charter: SWARM_R2.md s3 E. You never do primary science.
    First item: E-T1, the Domain A -> B transfer harness with its random-
    graft cheat; then E-T2, a basic Transformer baseline; answer
    `ask ... --to E`. 2 cores.
