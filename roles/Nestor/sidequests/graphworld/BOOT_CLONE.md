# Boot for a Nestor clone (lanes B, C, D, E)

Currency: 2026-09-14. The operator pastes the short block from chat; it
points here. Replace <L> with your lane letter and <l> with lowercase.

1. Do not pull. In the canonical checkout: `git fetch origin`, then
   `git worktree add F:/Prometheus-worktrees/nestor-gw-<l> -b nestor/gw-<l>-2026-09-14 origin/nestor/sidequest-graphworld-2026-09-14`.
   Work only in that worktree from here on.
   IF THE BRANCH ALREADY EXISTS (a rebooted lane, e.g. D after 2026-09-14):
   `git worktree add F:/Prometheus-worktrees/nestor-gw-<l> nestor/gw-<l>-2026-09-14`
   (no -b), then in the worktree
   `git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
   The checkout is ~43k files on F: and takes minutes: run it in the
   foreground with a 600 s timeout, never backgrounded, and boot clones ONE
   AT A TIME. Concurrent adds failed twice on 2026-09-14 with
   `fatal: Could not reset index file to revision 'HEAD'`; git then deletes
   the directory but keeps the branch. Check `git worktree list` before
   step 2.
2. `python -m comms boot Nestor --model <your model id> --capabilities any`,
   then `python -m comms instance` -> your tag (m1-xxxxxxxx).
3. Read, in order: roles/Nestor/RESPONSIBILITIES.md (seat),
   roles/Nestor/sidequests/graphworld/SWARM.md (the plan; your lane section
   in s3 is your charter), primordial/core/contract.py, the operator
   directive in roles/Nestor/prompts/2026-09-14_graphworld_swarm/.
   Base-role doctrine applies as SWARM.md s0 narrows it for this side quest.
4. Environment for every command:
     PY=C:/Users/jcrai/lab/gw-venv/Scripts/python.exe
     PM_LANE=<L>  PM_TAG=<tag>  OMP_NUM_THREADS=3  NUMBA_NUM_THREADS=3
   Smoke: `$PY -m pytest -q primordial/tests` and `$PY -m primordial.bus hello`.
5. `$PY -m primordial.bus read`, then claim your first item and start the
   loop in SWARM.md s6. Run it self-paced with /loop:
     /loop Nestor-<L> graphworld iteration: follow SWARM.md s6 for lane <L>
6. First receipt target: your lane's item 1, with a cheat control, within
   the first two iterations. A KILL is a fine first receipt.

Liveness (added 2026-09-14 after lane D never booted and nobody noticed for
hours): post `python -m primordial.bus hello` within 10 minutes of the paste.
The conductor (lane A) checks for a hello from every lane and posts on the bus
when one is missing.
