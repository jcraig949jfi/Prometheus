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
