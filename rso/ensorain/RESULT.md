# C-016-T050 -- Ensorain confirmatory run (PREREGISTRATION v1.1.0 s10): RESULT

Author: Argus[harry1-92a4e0d8], claude-sonnet-5-5 (Q2), headless on harry1 (M4), 2026-10-11. Base 9c4f61e0e (claim 1dd345ec3).
Executed once, exactly as PREREGISTRATION s10 / TASK.json `problem`; nothing changed in code, seeds, subjects or world.
`python -B -m rso.ensorain.freeze check` printed OK; `python -B -m rso.ensorain.assay confirm rso/ensorain/runs/CONFIRM.json
--n 400 --subjects rso/ensorain/SUBJECTS.json --cleared-by "C-016-T042 integrated (Palamedes, merge dfaf48d07; REPORT
rso/ensorain/challenge/R2/REPORT.md)"` exited 0 (stderr empty). Seeds 16_330_001..400, spec C-R2-desert, K 64, N 400,
one process, python 3.12.10, numpy 2.4.3. Read under PREREGISTRATION s5 and REPORT R2 s4 only. Raw: runs/CONFIRM.json,
runs/confirm_stdout.txt. Verdict format below: W:L:T = wins:losses:ties (wins = revised in full arm, not in control).

## 1. Qualification (read first)

Q-a True, Q-b True, Q-c True, Q-d True, Q-e True; `qualified` True. The run is NOT DETECTION_UNQUALIFIED, so subject
verdicts are read. Controls: smuggler, smuggler_decorative, constant_plus, constant_minus = REFUSED_FIXED_PRIOR;
memoryless_plus = REVISION_NOT_SHOWN; jitter = REVISION_NOT_SHOWN; learns_pre = REVISION_HISTORY_DEPENDENT.
Qualification cannot detect drift (L5, s5).

## 2. Family P (reference): REVISION_HISTORY_DEPENDENT

G_PRE True (400/400 pre-competent; threshold 217). G_R5 True (400/400 keep role 5; threshold 371).
- K1f (full vs frozen): 232:0:168, p = 1/6.9e69.   K1n (full vs noise): 230:0:170, p = 1/1.7e69.
  K1 = max (intersection-union) = 1/1.7e69; Holm 1.16e-69.
- K2 (full vs shuffle): 183:30:187; Holm p = 2.84e-28.
- Revised lives per arm [full, frozen, noise, shuffle, newlife, noswitch] = [232, 0, 2, 79, 43, 400]; late-window accuracy
  .626 / 0 / .343 / .415 / .702 / .977.
- noswitch: 400 of 400 lives late-window majority-correct under the unchanged law (no flip without a switch).
- Registered directional prediction (newlife pre-switch accuracy below full's) is descriptive and not a decision input; the
  reference newlife pre-switch accuracy = 39713/78278 = .507 (CONFIRM.json `newlife_pre`); the full-arm comparison value was not extracted here, so the prediction is not scored in this RESULT.

## 3. Search accessibility (REPORT R2 L2; scope: arm L, C-R2-desert, 16,000 evaluations, these 8 seeds; not a rate claim)

1 testable subject, 7 not: 5 with no plastic key (searched_16310001..005: NOT_TESTED_PARAMETER_FREE), 2 with a dead plastic
parameter (007, 008: REVISION_NOT_SHOWN by construction, not evidence about search). Holm over the 6 registered family-S tests.
searched_16310006 (the only live one), read at the alpha/6 worst case: REVISION_NOT_HISTORY_DEPENDENT.
- G_PRE True, G_R5 True (400/400 each).
- K1f 362:0:38; K1n 362:0:38; K1 Holm p = 6.4e-109 (holds).   K2 (vs shuffle) 36:34:330; Holm p = 1.0 (not shown).
- Revised lives [full, frozen, noise, shuffle, newlife, noswitch] = [362, 0, 0, 360, 261, 400]; late accuracy
  .909 / 0 / 0 / .920 / .917 / 1.000. noswitch 400/400.
- 007, 008: all arms 0 revised lives, K1/K2 0:0:400.
Reading: 006 passes K1 (it differs from its frozen and noise-matched versions) but its shuffle arm revises as often as its full
arm (362 vs 360), so history-dependence is not shown. Under L1 this label does NOT license "revises" or "responds to the
switch" (see s4). noswitch 400/400 says its late behaviour does not flip spontaneously in the no-switch arm; that does not
turn the K1-only label into a K2 result.

## 4. L1 carried (REPORT R2 s4)

A K1-only label (REVISION_NOT_HISTORY_DEPENDENT or REVISION_WITHOUT_RETAINED_COMPETENCE) does NOT license "revises". It
covers a law-blind drift (walker: 48/0/0/43 of 200, noswitch 142/200) and a halt-on-success search (ratchet 53/0/0/52,
noswitch 200/200), and a genuine learner whose K2 is underpowered. Only REVISION_HISTORY_DEPENDENT excludes drift. Here that
applies to searched_16310006 (noswitch printed beside the label: 400/400).

## 5. Other limitations carried

- L3: ETA_NOISE = 1e-9 is an absolute floor (assay.py:33); a genome whose own eta is <= 1e-9 is its own noise arm and cannot
  pass K1; false negatives only. No registered subject is near the floor (family S smallest eta .059). jitter is that case by
  design: K1f alone 14:0:386 (p 1/16384), K1n 0:0:400, so REVISION_NOT_SHOWN.
- L4: G_R5 = significantly more than 9 lives in 10 (>= 371 of 400) keep >= 90% of post-switch role-5 gates.
- L5: Q-a..Q-e cannot detect a drift subject; no drift control is registered (one would fail under v1.1.0).
- O1: the reference's revisability depends on the PLASTIC_BOUND clip; "bounded" is part of the mechanism, not a safety margin
  (unbounded ref_tiny: 8/200 revised vs 121/200 on the same seeds).
- O2 (freeze check pins only listed files) is harmless here.

## 6. Scope

What is shown: revision, within a life, of a genome-initialised or lifetime-learned plastic parameter, for the reference and
its labelled controls under the registered rule. NOT shown: that the pre-switch value was "learned in life" (innate vs
learned not distinguished, s1). NOT retention: no tested Ensorain world demands retention, which is itself a finding.

## 7. Resources and ambiguity

- Wall: about 255-265 s (shell timestamps 14:00:21Z before the freeze check .. 14:04:46Z after the run). CPU-seconds and peak
  memory were NOT instrumented in this session (no wrapper was added: nothing was to be changed), so they are not reported;
  the preregistered expectation was ~370 CPU-s (s9) and the observed wall is below that.
- Processes: one; no ubu006; no paid compute.
- rows_sha256 (assay-internal) = dcdf8a42ffc10706cf3a8072fed656f43b328c3a445811a53faea53ff79f5d08.
  File sha256 of runs/CONFIRM.json = f4a3b3f818307d3104092d4eca211d10c076c034a36303e185fa49e6e96766fc (14,152,592 bytes).
- Ambiguity under the registered rule: none found; every verdict follows from the printed counts.
- No re-run, no subject selection, no world change.
