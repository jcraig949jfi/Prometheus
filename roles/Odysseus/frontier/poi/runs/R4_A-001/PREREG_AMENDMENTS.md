R4_A-001 PREREGISTRATION AMENDMENTS (PREREG.md is unchanged)
==========================================================

A1 (2026-09-27, after the preregistered POS control ran and FAILED,
before any N/RW/RS/NEG result was inspected)
---------------------------------------------------------------------
Observed: POS as preregistered (planted 2-clobber summit, 16 N walkers,
P=4) found 0 improvements at every L = 1..6. PASS rule (>= 1 at L=2)
NOT MET. This is recorded as a FAILED preregistered control.

Diagnosis (diag_pos.py, diag_pos.json; replay of the 16 walk paths):
- From the 1-clobber genotype the true single-edit improvement rate
  under the probe distribution is 21/2,726 = 0.77%, so one depth of
  48 probes detects it with p ~ 0.29 (a POWER limit of P=4).
- The preregistered construction assumed the neutral step would be
  "remove one clobber". It mostly is not: only 5/80 accepted neutral
  steps lowered the clobber count (w1 step 1, w8 and w14 step 4, w7 and
  w11 step 5), and the walker that did it at
  step 1 (w1: deletion k=3 at instruction 13) also deleted the EQ/JZ
  key test, leaving a one-value memory with 0/1,197 improving
  neighbours. Neutral drift ERODES the unused second-slot machinery.
So the failure is partly power, partly a real landscape property of
the planted parent. Neither makes the harness unable to detect a
planted improvement, but the preregistered control did not show that.

Added (declared now, run after this file is written):
POS-F  forced-path positive control: the first step is FIXED to the
       clean clobber removal (delete exactly instruction 13, clobber B;
       neutral, verified), then the normal probe schedule at depth 1
       (P=4) with 32 independent probe seeds. Also 32 seeds at depth 0.
       PASS iff >= 1 improvement at L=2 AND the L=2 detection rate
       exceeds the L=1 rate. Expected (from 0.77%): ~29% of seeds at
       L=2, 0% at L=1.
POS-P  power curve: the detection probability per genotype as a function
       of probes, for a genotype whose true rate is 0.77%, reported so the
       main null can be read as a power-limited bound.
POS-E  erosion measurement: among 3,000 frozen-weight neutral-step
       proposals from the 2-clobber planted parent, the share of accepted
       neutral steps after which the ONE-EDIT FIX is still available
       (deleting the remaining clobber yields 1.0), vs the share after
       which the path to the summit is still two deletions away.
These additions do not change any N/RW/RS/NEG decision rule.

A2 (2026-09-27, after inspecting the N arm ONLY; RW, RS, NEG not yet
inspected -- RW was still running)
---------------------------------------------------------------------
Observed: N arm has exactly one D7 (parent 2e3e074cd6ff, walker 2,
L=3, randomization; train 0.531 -> 0.6875) and it "replicates" under
the preregistered REPL rule (64 held-out episodes: 0.539 -> 0.641).
Inspection of its answer vector shows a POSITIONAL two-value memory
(answers first-PUT value then second-PUT value, ignoring the tag) --
the same strategy as the two 0.6875 shelf parents. Such a program is
right on both asks iff the ask order equals the PUT order, which is a
fair coin per episode. The CRN train set has that order in 10/16
episodes and the preregistered REPL set (train/2/64) in 40/64 (both
skewed the same way by chance). On 2,000 fresh episodes the found
child scores 0.5285 vs its parent 0.5317, and the two 0.6875 parents
also score 0.5285: NOT an improvement.
So the preregistered REPL set was itself not independent enough of the
artefact it was meant to catch (a flaw of my prereg, recorded).

Added: LARGE-SAMPLE CHECK. Every D7 in every arm, and every parent, is
re-scored on 2,000 episodes (episodes_for(W2_K2, 20260921, "r4big", 1,
2000); 4,000 asks, SE ~0.008). A ROBUST improvement is child - parent >
1/16 there. The preregistered verdict (REPL rule) is reported as
written, and the robust verdict beside it. Nothing else changes.
