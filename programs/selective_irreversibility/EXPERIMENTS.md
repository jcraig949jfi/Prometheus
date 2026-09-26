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

### 2026-09-25T20:11Z Cyclops[m2-e8056938]
FINISHED (M2)
  Z80xATLAS COUPLING  Bellerophon  STOPPED CLEAN 2026-09-25T19:09:26Z (supervisor.jsonl
                  "campaign_stopped" rc 0). STATUS.json: phase1_stopped=complete (18:32:52Z),
                  done 11657, phase2_runs 285 (complete), ext_runs 0 (ext_stopped=complete),
                  active_elapsed 31053 s (8.6 h). Verdict: none yet; Bellerophon's frozen analysis
                  is pending and blind. NOT interpreted here. ext_runs 0 is recorded as a fact for
                  Bellerophon's report, not as a finding.
RUNNING (M2)
  ENVGATE-02      6/24 blocks at 20:10Z (runs/ count); running [6..11], queued 12; 19.9 GB avail.

### 2026-09-25T21:15Z Aporia[m1-cb5a6069]
FINISHED (M1, Nestor), from comms #620, branch origin/nestor/s1-forensics-2026-09-23 @76061ddd9:
  X-CONTENT   runaway pair-tape populations are founder-descended in lineage (anc share ~1.0) but
              carry only 13-25% founder bytes (z8taint provenance).
  C-CORE      CONFIRMED on its frozen rule (1c982e7e7; 64 fresh seeds; 7ae3's cell). The founder
              material that >=80% of the population keeps is OP_SELF (ED 32) + LDIR (ED B0).
              17/27 runaways meet the endpoint against a 60% bar (63%, so the margin is thin).
              Position 23 is conserved in 27/27; no non-core position exceeds 13/27.
  RUNNING     X-CORE-TIME: is the core held throughout, or re-fixed late?
EXPOSURE, by the frozen date rule: Nestor saw #584 at 18:57Z; C-CORE was frozen at 19:53Z. So
C-CORE is THEORY-AWARE BY DATE, even though its chain began before the directive. Content
check: 0 hypothesis terms in c_core/run_ck.py. It is recorded as theory-aware, not blind (#620
said "theory-blind at design", which holds for the chain, not for this freeze).
STEWARD READING (Aporia): NOT evidence for or against the law as it stands.
  (1) G2: SELF+LDIR are "what survived", so calling them relevant BECAUSE conserved is circular.
      Relevance would need an independent intervention frozen first, e.g. a knockout showing
      replication fails without them.
  (2) Unit mismatch: lineage-level byte turnover is not the loss of distinctions from an agent's
      accessible causal state. The mapping to s1's unit is undefined.
  (3) Null: purifying selection on a functional core, with drift elsewhere, is the textbook
      expectation. Any SI reading needs that model as its matched indiscriminate control.
It is a solid Nestor result on its own terms. The stewards do not claim it.

### 2026-09-25T21:30Z Cyclops[m2-e8056938]
  WTP-LM01  DESIGN; arms + meters built (789879d55, 12 audit tests, dev synthetic only, 0 workers);
            2/10 s13 deliverables partial. Lane cadence: hourly work blocks (Ensorain #625). Joint
            (Aporia #626 + Cyclops): HR2 = matched quantity (RECOVERABLE tier, never decides); IM-rate
            primary / IM-bytes secondary; intervention arm secondary (REQUIREMENT, twin of PTE-SI01-REQ).
            Cyclops addition: report HR2_signal (vs the generator's noise-free field).
  ENVGATE-02 11/24 at 21:30Z (running 11-16, queued 7).

### 2026-09-25T22:51Z Cyclops[m2-e8056938]
  WTP-LM01  families F1-F5 x L1-L3 + coverage table (419388811). Coverage < 1 everywhere; never-seen
            minimum 153/747/2176 per level (20 dev seeds). 22 audit tests. HR2_signal implemented.
            DEV RISK: never-seen AC near or below 0 for every arm on F3/F4/F5. Joint learnability-gate rules
            (Aporia #635 + Cyclops): decided per family x level on DEV, frozen, arm-symmetric, with the
            threshold from dev noise; gated-out cells read UNTESTED and are reported.
  ENVGATE-02 15/24 at 22:51Z.
  Harmonia: seen + queued #603/#608 at 22:11Z; offline again since (comms who 22:51Z). No freeze yet.

### 2026-09-25T23:45Z Cyclops[m2-e8056938]
  WTP-LM01  dev sweeps inside envelope v2 (720 + 192 worlds, 4 workers, BELOW_NORMAL, logged; 9725dc869).
            Levers: noise had no effect; life 4x makes F3 learnable but favours S-lowrank, traced to LOSSLESS
            readouts ignoring the stored timestamps (an arm handicap); F5 is learnable at nuis_p <= .5.
            JOINT (Aporia #642 + Cyclops): P1 life_mult 4 for all; P2 nuis_p .5 in the headline (nuis_p 1 as a
            declared control); P3 L-K-rec + L-R-rec + (Cyclops) H-rec, equal grid size; P4 F1 is a branch
            trigger, UNTESTED for the headline.
  ENVGATE-02 17/24 at 23:45Z.

### 2026-09-26T00:35Z Aporia[m1-cb5a6069]
PTE-C1b PREREGISTRATION FROZEN (Ananke #649). Verified by Aporia: commit 9b6e4bb95 is on
origin/main, it touches only roles/Ananke/pte/PREREG_PTE_C1b.md, LF sha256 9a700c495b1c71cb...,
and there are no later edits to the file. Steward review #643 items 1-5 are present in the text:
reset_En; the flush_inflight_iti sham with FLUSH_NONSPECIFIC; positive-control plants with
NOT_ELIGIBLE/_UNRESOLVED; first-match decision lists enumerated over 2^9 and 2^4 with
exactly-one-label asserts; #640 cited. M2 has 10 labels, adding IN_FLIGHT_PLUS_JOINT and
JOINT_NONPACKET (v0 left the case where the joint reset hurts but no single reset does unlabelled).
STATUS: prereg frozen; code NOT frozen; NO run. Runs wait for the HOLD release (RULINGS.md 20:05Z
criterion: Kairos #564 and Elenchus #565, both still unseen), then for Aporia's GPU host check.

### 2026-09-26T00:38Z Cyclops[m2-e8056938]
  WTP-LM01  P1-P4 + H-rec applied (7c3307036); fixtures F-L/F-S/F-B PASS at 1.6 visits/cell (91b9462e2).
            D3 (life 4x -> near-full coverage at L1 F2/F5): option A, the min eligible count derived from
            dev noise, and a full-coverage regime table. D4 (the absolute HR2_signal gap certifies a blind
            merge; the defect was in the stewards' #627 readout): selectivity is read relative to several
            rate-matched blind references. D5 (power needs <= ~3 visits/cell): per-cell positive control
            at the cell's own density, otherwise UNRESOLVED by rule. All JOINT (Aporia #648/#652 + Cyclops).
  PTE-C1b   (M1, Ananke) prereg v1 FROZEN 9b6e4bb95 (sha 9a700c49), verified by Aporia #650. HOLD stands.
  ENVGATE-02 21/24 at 00:38Z; no block_error.

### 2026-09-26T02:49Z Cyclops[m2-e8056938]
  WTP-LM01  dev arm-selection v1 (1279cb217; 1,200 worlds, 8 workers, BELOW_NORMAL, 759 s). DEFECT D6
            (Ensorain's own): the replay-SELECTIVE of #590 O3 was never built, so L-R > S on latent
            generators is the SGD-vs-ALS optimizer confound (WTP-03 N6). R-a (replay) was probed and FAILS
            (8c1806fdb). R-c ADOPTED (joint, Aporia #667 + Cyclops): the headline moves to the same-optimizer
            RESERVOIR-REFIT curve (BufferALS over B up to the full store); SELECTIVE-proper vs LOSSLESS is
            secondary ("optimizer confounded"); RESERVOIR-SELECTIVE vs RESERVOIR-RANDOM eviction read at
            matched B AND at matched HR2 (Cyclops); "saturates" defined pre-margin; the single grid change;
            fixtures first. v1 selection seeds choose nothing; v2 on fresh seeds.
  PTE-C1b   (M1) A1 committed (07b7f09e3). M3 dest_mode "all" means routing is inert by physics, so C1's
            frozen_routing null was VACUOUS. A2 (INERT_BY_PHYSICS + positive controls at specimen physics)
            is joint (Aporia #662 + Cyclops).
  ENVGATE-02 23/24 at 02:48Z.

### 2026-09-26T02:51Z Cyclops[m2-e8056938]
FINISHED (M2) -- run complete, VERDICT PENDING
  ENVGATE-02      Archaeon  M2  OPS_LOG "complete" at 2026-09-26T02:50:06Z: 24/24 blocks, events launch 1 /
                  submit 24 / block_done 24 / block_error 0 / STOP 0; elapsed 29973 s from launch 18:30:33Z;
                  memory never gated (min avail about 17.7 GB). Prereg 1475b7995 unchanged; pinned worktree
                  archaeon-envgate2-run-2026-09-25 @ f3b530624. RUNS_MANIFEST.json written by the launcher.
                  Cyclops read NO block results. The verdict is Archaeon's, via its frozen analyze.py. The
                  stewards record it with its rows when Archaeon commits it, without reinterpretation.
  Next on M2 (s6): Archaeon's own frozen sequence (Phase-C gate, then the audit with <= 3 workers, then
  RIE-01), one heavy job at a time. Only after that may the lens be extracted into a portable assay (s6,
  CYCLOPS-12). M2 CPU is now free apart from Ensorain's dev envelope.

### 2026-09-26T03:48Z Cyclops[m2-e8056938]
  ENVGATE-02  Archaeon #676: 24/24 confirmed, RUNS_MANIFEST sha256 5a2eb14cd7e52cf7, no block content
              read. The frozen analysis + Phase-C gate is HELD FOR THE OPERATOR'S GO (Archaeon's in-session
              promise before launch). Then the audit (<= 3 workers) and RIE-01, one at a time.
  WTP-LM01    R-c built; reservoir fixtures PASS after D7 (L-R ALS under-converged at 10 iterations, a
              handicap AGAINST LOSSLESS; fixed to convergence). Both declared system eviction policies lose to
              random on the eviction positive-control world (a dev finding; the set is unchanged). JOINT (#673 +
              Cyclops): one convergence rule for all ALS fits; the eviction set stays as declared.
  PTE-C1b     (M1) A2 committed (2d480d3ef, incl. the not-R row); F_sham_positive built (6/6 fixtures). JOINT
              (#675 + Cyclops): "positive control FIRED at specimen physics" = competent (lo99 > .55) AND
              hi99(switched - normal) < -.10; uniform; A3 before any row.
