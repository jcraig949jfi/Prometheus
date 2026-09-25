# Running and queued experiments

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

Sections: RUNNING, QUEUED, FINISHED. Each row: id, seat, host, frozen prereg
path + hash, class, stopping gate, expected end, source. Frozen work
finishes under its own prereg (s6); nothing here changes it.

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T16:45Z Aporia[m1-cb5a6069]
Source: read-only M1 audit 16:28-16:35Z (process list, schtasks, git log in
nestor-s1-forensics, origin/main at 0a9f5614d); comms #561 read by Aporia 16:44Z.

RUNNING (M1)
  C-SWAP-ACQUIRE  Nestor  M1  CONFIRM lane, frozen in 82b6caeb3 (nestor/s1-forensics-2026-09-23,
                  NOT yet on origin/main). schtask NestorCSA -> PID 6692 run_csa.py, 10 workers.
                  97/480 runs at 16:34Z, resumable (run_csa.py:94). ETA ~18:20Z INFERRED from rate.
  X-ACQUIRE       Nestor  M1  EXPLORE. schtask NestorXA -> PID 18148 run_xa.py, 2 workers. Attempt 1
                  crashed (IndexError, 16:23Z); relaunched 16:24Z under amendment A1 (76db1e5b0,
                  corrected 82fa0d822). 1/2 rows at 16:29Z.
FINISHED (M1, today)
  X-DONOR-SWAP    Nestor  WEAK_SIGNAL (df5b6d18b). Interrupted at 66/96 by the reboot, resumed by
                  schtask NestorDS, EXIT 0 12:45Z, 96/96. 3/11 foreign cells gave runaways vs the
                  preregistered SIGNAL bar of 4/11; own-cell positive control 3/8. Prereg: run_ds.py
                  docstring, 3ca20cd21, before launch.
  X-SWAP-ORIGIN   Nestor  CLEAN_NULL (6103ede92); labels corrected 7e6497d3a.
  X-ATOMIC-RANDOM Nestor  SIGNAL (random implant 0/80 vs genome 46/80).
  X-SWAP-ANCESTRY Nestor  SIGNAL (82b6caeb3).
  PTE-C1          Ananke  DONE 00:06Z; schtask disabled.
NOTE: directive s6 names X-DONOR-SWAP as M1's unfinished first priority. It had
finished 3 h before the directive reached this record. Its s6 intent (finish
frozen work, preserve the causal sequence) now applies to C-SWAP-ACQUIRE and
X-ACQUIRE.

### 2026-09-25T18:07Z Cyclops[m2-e8056938]
Source: read-only M2 audit 18:00-18:12Z (Win32_Process, Get-ScheduledTask(Info), port 8811, nvidia-smi, Win32_OperatingSystem, C:/Users/James/z80atlas_coupling_2026-09-24/STATUS.json + memory.jsonl, archaeon/envgate2/ in worktree archaeon-postcampaign-2026-09-23), origin/main fbe4d8071.

RUNNING (M2)
  Z80xATLAS COUPLING  Bellerophon  M2  prometheus.z80atlas.coupling_campaign (frozen code copy
                  in the workdir; plan sha256 a3bc8c8e...; Amendment 1 6607b3cb5 = active-runtime
                  caps, operational only). Supervisor PID 9504 + campaign PID 6796, 20 workers,
                  launched 12:11:44Z (3rd segment). done=8610 at 18:05:54Z. Caps PHASE1 18 h /
                  TOTAL 22 h ACTIVE runtime; active_elapsed 27241 s (7.6 h) at last write, so
                  ~14.4 h active remain (INFERRED from the caps in coupling_campaign.py @436510e55).
                  Class: pre-directive discovery lane, never told the hypothesis (see BLIND_LANES).
NOT RUNNING, FROZEN, MUST FINISH (M2)
  ENVGATE-02      Archaeon  M2  prereg 1475b7995 (digest 9e3fb887a4aeaa84), 24 blocks x 5 arms.
                  runs/ EMPTY (0/24), no OPS_LOG.jsonl anywhere under Prometheus-worktrees/*:
                  never relaunched after the 2026-09-24 21:23Z reap. Relaunch = python -m
                  archaeon.envgate2.launch_ops (6 workers, pauses <4.0 GB avail, stops <2.0 GB).
                  RESUME.md said "check commit_avail_gb first": at 18:0xZ avail_phys 22.0 GB,
                  commit_avail 24.6 GB. Memory no longer blocks it. Directive s6: M2 first priority.
IDLE / DOWN (M2)
  AGE (Aether)    no process, no pods (Aether STATUS 09-25: halted cleanly for reboot).
  CWE (Cosmos)    no process; BLOCKED on holdout D (Nestor, M1, comms #561).
  WTP (Ensorain)  no process; awaiting operator go/no-go on WTP-04.
  SFE 9.0.1       NOT SERVING: nothing listens on :8811; SFEngineM2Watchdog DISABLED.
  Vivarium        consumer not running; VivariumDeadmanM2 DISABLED; VivariumConsumerM2 never
                  ran (next run 2035). Outbox deliverer runs every 5 min, exit 0.
  Old Z80Atlas / DeepFrontier schtasks: last run 2026-09-19, no next run.
