+==============================================================================+
| E-BEL-REPL-02 RESULT + REVIEW PACKET: adversarial transformations of the     |
| E-BEL-REPL-01 residue (state-freedom under a partial register scaffold)      |
| Author: Bellerophon (M2 / SPECTREX5)            Date: 2026-09-30              |
| For: HITL operator + external reviewers + Aporia (CWO-B in-flight close)      |
| Status: CLOSED -- RESIDUE_NOT_REPLICATED (ABSENT), frozen                     |
| Self-contained: no repo access needed; every load-bearing number is inline.   |
+==============================================================================+

-----
0. SUMMARY
-----
The claim under test is the E-BEL-REPL-01 residue: "in BEE, a partial register
scaffold (zero reset with p = 0.9, else registers carried) makes state-free
genomes come to DOMINATE the population more often than an always-present
scaffold (ZERO)".

It was re-read LABEL-FREE on fresh seeds and put through transformations M1-M6.

Frozen verdict (tools/falsify_analysis.py, one run):
RESIDUE_NOT_REPLICATED (ABSENT).
- M1 BASE: dominance P90 1/50 vs ZERO 0/50.
- M3 COPY: 0 vs 0. M4 MUTLO: 1 vs 0. M5 strict ruler: 1 vs 0.
- M2 no founders: INCONCLUSIVE_POWER (8 and 9 of 200 runs alive at the end).
- M6 RANDOM (intended as the positive control): 0/50, with only 8/50 alive.
  NON_MONOTONE.

Every precommitment was lost. I expected M1, M4 and M5 to HOLD, M3 to break,
and M6 to be MONOTONE.

-----
1. WHAT WAS FROZEN (4d1a7c885, FREEZE_MANIFEST_02.json)
-----
- PREREG_02.md, falsify_run.py, falsify_analysis.py.
- The REPL-01 ruler (state_free.py) and a new strict ruler. Before the freeze,
  the strict ruler accepted the planted self-initialising replicator and
  rejected the planted zero-dependent copier.
- The analysis was checked on planted synthetic records.
- Design: 750 runs, 9 arms. Seeds 33,000,000 + s. P90 and ZERO paired within
  each transformation.

-----
2. EXECUTION AND CUSTODY
-----
- Attempt 1 was reaped by the host at 82/750 (Claude Code background reaper;
  M2 had 4.6/31.8 GB free). Relaunched on the operator's word after a check
  (CPU 53%, 14.2 GB free). The runner is resumable.
- 750/750 unique (arm, pair) records, 0 errors.
- Seal: bb8c66fd2 (concat sha256 004ddea7...), committed before the analysis.
  The frozen files were verified unchanged.
- Leases:
  * lse-4e19412ded95 expired on its TTL (token lost; reported #1077).
  * lse-ede8c1ed2167 was acquired with its token kept, and RELEASED.

-----
3. THE CAVEAT I OWE (same defect class as REPL-01's K3)
-----
The DOMINANCE readout was never shown to be reachable on real data. The arm
meant to show it, RANDOM, went extinct in 42/50 runs and never dominated.
"ABSENT" therefore means "never observed". It does not mean "shown impossible
to observe". This is the calibration lesson recorded at 6879b2236, and I
repeated it here in a prereg written before that lesson was written down.

-----
4. POST-HOC (labelled; written after the verdict; feeds nothing)
-----
A. Continuous readout (production_02/POSTHOC_SHARE_02.json).
   Among runs alive at the end, runs with ANY state-free organism:

     BASE P90 2/36   ZERO 1/47   (mean share 0.017 vs 0.0006)
     COPY     3/37 vs 0/37
     MUTLO    3/30 vs 0/41
     NOFND    2/8  vs 1/9

   Paired sign tests all have p >= 0.125.

B. What REPL-01's K1 signal actually was
   (production_02/POSTHOC_REPL01_EVENT_TIMING.json, from REPL-01's sealed
   data). REPL-01's frozen EVENT scores "the LAST checkpoint with >= 1
   state-free genome", which need not be the final checkpoint.

     arm   events  median event tick  events with state-free at tick 2000
     P90     57         1400                        7
     P75     36         1900                       16
     ZERO    18         1000                        3

   Runs with any state-free genome at the end: P90 8/100, P75 17/100,
   ZERO 4/100.

   So REPL-01's K1 (93/200 vs 18/100) was mostly TRANSIENT appearance of
   state-free genomes under a partial scaffold, not persistence or takeover.

-----
5. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES:
- The residue as a DOMINANCE claim is not supported in BEE under any tested
  transformation.
- REPL-01's surviving K1 signal describes TRANSIENT appearance (more frequent
  under a partial scaffold). Persistence to tick 2000 is rare in every arm:
  4-17%.
DOES NOT:
- Show that dominance is impossible. The readout's reachability was not
  demonstrated.
- Say anything about NPE.
- Resolve descent (REPL-01 ERRATA R1: UNRESOLVED).

-----
6. DISPOSITION
-----
- CWO-B in-flight set complete. E-BEL-BUILD-01 is NOT promoted (CWO-B s1).
- The seat goes READY for Aporia.
- Residue update for Tyche: "transient state-free appearance under a partial
  register scaffold (P75 > P90 > ZERO for persistence to the end)". Weak, and
  not a dominance phenomenon.
- Compute today: REPL-01 ~12.6 core-h; REPL-02 ~6.5 core-h (2 attempts).
  Total ~19 core-h, inside MWO-0004 R2 (<= 16 per item, <= 48 per day).

-----
7. QUESTIONS FOR THE REVIEWER (please try to disagree)
-----
1. Is ABSENT fair when the positive arm (RANDOM) mostly died? Should the
   verdict be INCONCLUSIVE (readout unreachable) instead?
2. REPL-01's frozen EVENT allowed an early checkpoint to count. Does that make
   REPL-01's K1 "SURVIVES" itself an overstatement, even though the rule was
   applied as frozen?
3. Is anything left here worth a campaign, or is "not worth continuing" the
   right answer for this line?

-----
8. ARTIFACTS
-----
roles/Bellerophon/repl_2026-09-30/:
- PREREG_02.md, FREEZE_MANIFEST_02.json (4d1a7c885)
- production_02/PRODUCTION_SEAL_02.json (bb8c66fd2)
- production_02/ANALYSIS_02.json
- production_02/POSTHOC_SHARE_02.json
- production_02/POSTHOC_REPL01_EVENT_TIMING.json
- tools/falsify_*.py, tools/posthoc_repl02_share.py
Branch bellerophon/repl-internalize-2026-09-30.

+==============================================================================+
| END. "Not worth continuing" is a first-class answer.                          |
+==============================================================================+
