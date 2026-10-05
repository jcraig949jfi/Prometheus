# Aether host handoff: BUCKKEEP -> SPECTREX5 (M2), 2026-10-05 ~10:25Z

From: Aether[buckkeep-5c60d0f5]. To: Aether[m2-95eba442]. The single writer on aether/mwo0001-2026-09-28 from this
commit onward is Aether[m2-95eba442].

## State at handoff
- Cycle 3 is closed. TEST-3 is MECHANISM_SUPPORTED at P1 only (not propagation). DEV-4 has NOT been opened.
  Next window: DEV-4 at 2026-10-05T11:37Z, then TEST-4 at 15:37Z.
- **Read first: Aether/V2B/TEST-3/OPERATOR_REVIEW.md.** It holds the operator's in-session TEST-3 review and the
  ACCEPTED DEV-4 design: a decodability impulse response vs exchange-only, single-site restore for causal
  generations, an own-history predictor, hand-worked fixtures, a not_before guard, and energy aim fixed at e=0.
  Before this commit it existed only in the BUCKKEEP session. The CAMPAIGN_STATE dev4_* fields predate the review;
  OPERATOR_REVIEW.md supersedes them.
- Runner and verifier used for TEST-3: Aether/V2B/TEST-3/tools/t3native.py (wave driver, waves of 3, skips finished
  units) and t3verify.py (hash recompute, per-law majority class, primary rule, P3 reduce). Both have
  BUCKKEEP-specific paths at the top.

## (a) Processes, crons, loops
- BUCKKEEP runs the self-paced /loop (ScheduleWakeup, hourly). There is no OS cron and no 4-hour window cron: windows
  are opened by the loop checking the clock. I am stopping that loop now. No background processes are running.

## (b) BUCKKEEP-only state
- Leases: none held. buckkeep:cpu8 lse-2c2b3c71f570 was released at 07:50Z.
- Pinned worktrees: none. aether-v2b-t1/t2/t3 and aether-e009-pin were all removed. Only the aether-mwo worktree
  remains.
- C:/Prometheus-data/aether (13 MB): native-run outputs for TEST-1/2/3 and C-002. Every result JSON is also committed
  under the repo's attempts/ dirs, so nothing is lost.
- C:/Prometheus-data/runpod_artifacts/aether-units-20260927T165531Z (8.9 MB): the 2026-09-27 RunPod unit artifacts.
  Receipts are committed; the raw artifacts exist only here. Ask if you want them shipped.
- Session scratchpad (temp dir): heartbeat/report body drafts, MWO/CWO copies, the promexec broker_r2.py review copy,
  and pilot outputs (dev3pilot, pilot128, e009..e012, t1/tasks.json). Nothing there is needed: results and decisions
  are committed. t1/tasks.json was the TEST-1 Fabric task list; those tasks are finished.
- Venv quirks: system python with numpy; pytest needs --basetemp outside the repo (Windows temp permissions); run
  comms from the worktree (the canonical C:/Prometheus checkout is stale: never pull or checkout there); set
  EW_DB_HOST=192.168.1.202 before comms.
- BUCKKEEP C: is nearly full (~11 GB free; reported #1525/#1526). This is an operator matter, not Aether's.

## (c) In flight with others
- promexec round 2: BLOCKED on the operator installing broker 3cf32a64...0df3 (Odysseus #1043/#1049). It stays
  EXPERIMENTAL / UNVERIFIED / NOT ENABLED. Nothing is owed from Aether until the install happens.
- Fabric: the ubu001 numpy workers have been stale since 2026-10-02 (#1439). TEST-1/2/3 used the MWO-0004 R3 native
  fallback. Unanswered.
- Heartbeats to Aporia under CWO-C: last #1553 at 09:53Z; next due by 11:23Z (<=90 min). Reports for TEST-3: #1541
  (operator + Artemis). Disk: #1525/#1526.
- Raise with Odysseus in the DEV-4 report: Fabric/RunPod should enforce not_before (operator request).

## (d) What I would do differently next window
- Run a not_before guard in the driver: TEST-3 started 2 minutes early (harmless, recorded).
- Fixture-test every new ruler with hand-worked answers BEFORE piloting. In DEV-3 a shadow self-check passed vacuously
  because the physics and the shadow shared a flag-index bug.
- With a GPU, snapshot-and-branch twins can batch many perturbation values per origin. Keep CPU and GPU results
  bit-identical, or declare the semantics change in the preregistration.
- main moves often: merge origin/main into the branch before pushing to main. Never rewrite history.
