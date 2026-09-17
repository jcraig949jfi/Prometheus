# Nestor-A resume brief: after the 2026-09-14 reboot

Written ~19:50 local by Nestor-A[m1-449a9e76] (conductor) before an
operator-ordered reboot, which reloads the NVIDIA driver so builder Q's GPU
counters apply. Authority: operator message 11 (verbatim in
prompts/2026-09-14_graphworld_swarm/). This file is the resume point. The
conductor session transcript is the full record.

## 1. Who and where

- Conductor session: 449a9e76-4be1-4c39-b8a8-3a6d82aaffb5 (tag m1-449a9e76),
  project F:\Prometheus.
  Resume with:
  `claude --resume 449a9e76-4be1-4c39-b8a8-3a6d82aaffb5 --dangerously-skip-permissions --remote-control "Nestor A"`
  A one-shot Startup-folder launcher (nestor_resume_once.cmd) does this at the
  first logon and then deletes itself.
- Conductor worktree: F:/Prometheus-worktrees/nestor-sidequest-graphworld.
  Integration branch: nestor/sidequest-graphworld-2026-09-14 (never main).
- Python: C:/Users/jcrai/lab/gw-venv/Scripts/python.exe. Bus: Redis 6390
  (WSL docker gw-substrate, AOF on, restart unless-stopped).

## 2. State at reboot

Round 3 (build) builders, each in a worktree nestor-bld-<l>. Every lane was
told to quiesce, push and post "PAUSED for reboot":

| lane | package | state |
|---|---|---|
| F | fabric (O3 O5 O1 F7 F8 F14 F9 X F15) | GREEN, paused (tip 65fc14c9d) |
| G | metric (C2 C1 C4 M3 M1 floors abstain/fixed/random/gate) | green except M2 HELD for the operator; paused (179dfec6f) |
| H | measurement (F10 F12 F13 S1 S2 S3) | GREEN, paused (f8d1b34b3) |
| W | N3 Warp MVP | GREEN, paused (8639275d8) |
| Q | N2 Nsight MVP | GREEN with counter features BLOCKED; Q2c INDETERMINATE (regkey set, driver not reloaded) |
| U | N5 CUDA Graphs MVP | GREEN (fc173298b); U6 throughput receipt FAIL as posted (graph vs eager >= 5x in 4/6); U6b open |
| P | N1 precision MVP | GREEN, loop stopped 19:10 (P1-P4; fp16 the only free win, int8/fp8 buy bytes only; fp8 no kernel on cc 12.0 torch cu128; cutlass 4.2 fails on Blackwell). Pushed to origin/nestor/bld-p-2026-09-14 @ 03f16eb2c but NOT yet on the integration branch. After reboot: integrate P's branch (rebase onto integration, suite green, ff push) |
| T | N4 cuTensorNet MVP (WSL) | PAUSED for reboot 19:41, pushed 568bbf691: oracle 32/32, cheat 32/32, timing 28/36 shapes (cuTN faster 22/28), topology note; open: timing d64r16 B>=262k and d64r64 (resume with a per-cell watchdog) |

- Round 2 cohort sessions B-E are idle (worktrees nestor-r2-<l>). Do not
  relaunch them; round 4 gets fresh sessions.
- Critical finding: an always-abstain 0-byte policy beats every round 1
  baseline and every round 2 clause A cell. Held64: w4 107.75, w3 122.62,
  w1 88.28 (conductor reproduced it). A 4-byte gate on w1 scores 170.47.
  w3/w4 have no headroom above abstain. All 28 clause A record cells are
  BELOW_FLOOR. Round 4 clause A is ON HOLD.

## 3. Operator decisions still open

1. World screen + floor-relative clause A: keep only worlds where acting
   beats the best trivial policy, and score clause A relative to that floor.
   Recommended.
2. Budget split 35/25/25/15 (H's S2 triage rule: D +5 from B). Recommended
   for round 4.
3. Nsight: done at the registry level (RmProfilingAdminOnly=0). This reboot
   is the last step. Afterwards: relaunch Q with a Q2d brief (rerun the
   probe).

## 4. Post-reboot checklist (conductor)

1. Start WSL and the bus: `wsl.exe -e true`; wait for docker; check
   `docker ps` shows gw-substrate, gw-fabric, gw-sub-b/c/d/e.
   `redis-cli -p 6390 ping` (from the gw-venv python). pm:swarm XLEN should be
   >= the pre-reboot export in bus_export/.
2. `git fetch`; verify the integration tip contains every builder's
   "pushed=" sha from its reboot pause note; every nestor-bld-* worktree is
   clean.
3. Restart telemetry:
   - liveness in the background:
     `python -m primordial.ops.liveness --watch 60 --post`
   - the Monitor on pm:swarm for asks/results addressed to A.
4. Verify counters: HKLM NVTweak RmProfilingAdminOnly=0 and a new
   LastBootUpTime. Then relaunch Q only, via
   `python -m primordial.ops.schtask_launch launch Q --worktree F:/Prometheus-worktrees/nestor-bld-q --prompt-dir prompts_bld`,
   and post "Q2d go".
5. P and T: relaunch only if their reboot resume line lists unfinished
   MVP items the operator still wants.
6. SFE (daedalus-sfengine serve.py) and the Vivarium consumer belong to
   other seats. Nestor does NOT restart them; their owners were notified
   before the reboot.
7. Tell the operator it is resumed, and restate the open decisions in s3.
8. On their rulings: write SWARM_R4 (world screen, floor-relative clause A,
   split, all cohort jobs through the F7 worker so F13 can meter them),
   prompts_r4, prepare_worktrees --round r4, then launch via schtask_launch.

## 5. Rules learned today (also in memory)

- Never `git stash` in Prometheus worktrees (the stash is repo-global).
- Gate commits on the tool's own exit code, never on a pipe.
- Launch sessions via scheduled tasks and disable them after they run; write
  .cmd files with the Write tool.
- Read full bus bodies before acting (notifications truncate).
