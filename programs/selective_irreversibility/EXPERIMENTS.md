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

### 2026-09-25T18:30Z Cyclops[m2-e8056938]
QUEUED (M2)
  WTP-LM01        Ensorain  M2  Lossless Memorizer challenge (countermodel B). Directive: operator-
                  written, issued under Cyclops's name, verbatim at roles/Ensorain/prompts/
                  2026-09-25_wtp_lm01_directive/01_...verbatim.md (sha256 ab204631..., f3b530624).
                  Adopted by Cyclops at roles/Cyclops/prompts/2026-09-25_wtp_lm01/.
                  Supersedes WTP-04. State: DESIGNING (#590). No prereg yet. Launch is GATED on a
                  Cyclops launch prompt (directive s12), after the coupling campaign ends.
                  Joint steward rulings R1 and R2 (#591 + Cyclops concurrence); R3 dev envelope
                  ruled by Cyclops (01_RULINGS_R1_R3.md).
  ENVGATE-02      still 0/24 at 18:29Z. No reply from Archaeon to #585 yet (Archaeon last
                  online about 13:28 local). Bellerophon ACKed co-run (#589).

### 2026-09-25T18:54Z Cyclops[m2-e8056938]
RUNNING (M2), update
  ENVGATE-02      Archaeon  M2  RELAUNCHED UNCHANGED 18:30:33Z (comms #593). prereg 1475b7995, 6 workers,
                  pinned detached worktree archaeon-envgate2-run-2026-09-25 @ f3b530624, pid 8244.
                  OPS_LOG at 18:51:33Z: running [0..5], queued 18, avail 17.72 GB, commit avail
                  20.16 GB. 0/24 complete.

### 2026-09-25T19:35Z Aporia[m1-cb5a6069]
Source: Nestor comms #598 (18:57Z), commits on origin/nestor/s1-forensics-2026-09-23 tip 9fb737146.
CORRECTION to my 16:45Z entry: both children have CLOSED.
  C-SWAP-ACQUIRE  NOT_CONFIRMED. 9/240 GENOME vs 0/240 RANDOM, one-sided Fisher p = 0.0018.
                  The frozen rule required count difference >= 8 AND p < 0.001; the p bar
                  failed (its eligibility note put the minimum at 10 vs 0). It is recorded as a
                  NULL on the frozen rule. It is not read as support, and not as "almost confirmed".
  X-ACQUIRE       WEAK_SIGNAL, with a caveat: the anc marker may track slot lineage rather than bytes.
RUNNING (M1)
  X-CONTENT       Nestor, EXPLORE: byte-provenance check with z8taint, testing the anc caveat.
  Cosmos holdout D build  Nestor, worktree nestor-c3-d, branch nestor/c3-holdout-d-2026-09-25
                  from 815cdb32a, run as a parallel lane under the operator's ruling "take it,
                  parallel lane".
Nestor holds all DIRECT-lane SI work until the stewards map it (s6).

### 2026-09-25T20:05Z Aporia[m1-cb5a6069]
QUEUED (M1, Ananke), both gated on the HOLD release above:
  PTE-C1b   adjudicates C1's mechanisms M2 (delay-line memory) and M3 (self-modifying MAJ).
            Separate frozen prereg. NO SI-derived endpoints. Must finish before PTE-SI01.
  PTE-SI01  Causal-State Boundary Challenge. A repeated-task HOLD world; distinctions R
            (relevant), E (expired) and N (nuisance) with relevance from the task oracle;
            recoverability AND causal utility, each measured on the complete endogenous state;
            attacks A-D (externalized memory, stale history, indiscriminate loss, retentive arm);
            eight outcome classes. Launch only on Aporia's go after the s25 deliverables.
Relation to memo attack 3 (the DSA): PTE-SI01 is the PTE instance of it, extended with the
E class and with the causal-utility readout. The DSA's calibration standard (a fixture per
verdict branch, counter-based RNG, eligible counts first) applies to it.
