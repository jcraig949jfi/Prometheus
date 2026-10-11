# C-017-T042 -- short Q3 re-check of FREEZE_Z80_ATTRIBUTION v1.1.0 (the one repair round): REPORT

Reviewer seat: Pallas. Surface: rso/z80 at v1.1.0 (FROZEN.json LF sha256 3f14bf800db52db08a8564bf36d6f975dd614c6aa9efc6a3b61d522003cf7932,
27 files; grammar 63ffdeca16db3333; Python 3.12). Worktree C:/Prometheus-worktrees/pallas-c017-t042, branch
pallas/c017-t042, base 9bbf984e3. State commits on main: edbbfe72c (CLAIMED). Predictions committed before the outcome
runs: 2b889dfc2 (rso/z80/challenge/R2/PREDICTIONS.md, 2026-10-11 20:41:54Z). This is the bounded re-check of the one repair
round (C-017-T041, Argus); NOT a second open challenge. No second repair round (directive s9): every survivor is stated as
a limitation. Seeds: challenge partition only (17_040_xxx; CDIST = arm index 10 uses 17_070_xxx). No 17_050_xxx, no
17_080_xxx, no `assay confirm`. Read-only on archaeon/, prometheus/z80atlas/, roles/Archaeon/; no Archaeon seed; no evidence
bundle.

## 0. MODEL-IDENTITY DISCREPANCY (material; escalated)

comms boot recorded this seat's runtime as claude-fable-5-1 (Q3, tier heavy; the boot line and WORK_STATE carry it). A
harness system message LATER in the same session reported the runtime as claude-opus-4-8 (Opus 4.8, Q2). The two conflict.
This packet is quality_class Q3, can_downgrade false, escalate_to Q3, and the Continuous Observatory directive s9 requires
"a genuine Q3 reviewer". Opus is Q2, not Q3.

Consequence, stated plainly: EVERY finding below is a deterministic, independently re-runnable fact -- a mutant that is RED
or GREEN, a VM register trace, a replay byte-equality, a freeze hash, an exact w_max. None depends on the reviewer's model;
anyone can re-run the commands and get the same values. What a Q3 reviewer buys that a Q2 one may not is the adversarial
IMAGINATION to find a hole that is not already written down. I therefore do not claim this re-check discharges the Q3
PROCESS gate by itself; that is Palamedes's call (escalation under ops/campaigns/C-017/escalations/). The deterministic
evidence stands on its own and is not wasted whatever that call is. Nothing in this report is fitted to an outcome: the
order of every run relative to the prediction commit is recorded.

Disclosed as run WHILE READING THE SURFACE (verifications of the builder's deterministic claims, not outcome-fitted
predictions): the 51-test suite (OK), freeze check (OK), and the CDIST unit under the repaired rule (reads=2, tags all K,
label ENV). They are repeated below with that disclosure.

## 1. Verdicts per surface

Overall: the repair CLOSES REPORT (v1.0.0) s4.1 -- the P-tag fault that called CDIST ENDO -- WITHOUT opening a new hole on
any surface I re-checked. Every survivor is a limitation the frozen surface already states. No new fault. No second repair
warranted.

### 1.1 The reads rule / P tag (the repair itself) -- the reads channel CLOSED; exec_foreign/SEAL residual UNCHANGED (stated)

CLOSED (the reads channel). The repaired tag (observe.py endo_tags: reads_nbr>0 -> every written byte K) makes the v1.0.0
escape dead:
- CDIST unit over kin: reads_nbr=2, exec_foreign=0, tags = K*32, label ENV (was ENDO under v1.0.0). Over an empty target the
  child is not F0. [predicted P2; also run during surface read, disclosed]
- CDIST_ENDO_IMPL arm at 5 epochs, challenge seeds 17_070_001..004: run class ENV/INSERTED 4/4, n_ENDO = 0 in every run
  (n_ENV 89..115, n_func 90..115), while on the same records b1 = ENDO and b4 = ENDO. [predicted P4]
- R1 mutant (drop the reads->K clause) is RED on test_a_parent_that_reads_the_window_writes_no_parent_byte; GREEN restored;
  freeze OK. [predicted P7]

NOT CLOSED, but UNCHANGED from the stated limitation (PREREGISTRATION s11.5): a target dependence entering ONLY through a
window read the VM does not count on reads_nbr -- exec_foreign (executing target bytes) or SEAL -- and invariant under both
counterfactual alterations would still be P. I attacked this once (P3) and could NOT construct a scored escape; the attempt
tightens s11.5 from "none constructed" to "construction obstructed by the VM's control-return semantics":
- SEAL (op 29) snapshots the window into the sealed buffer WITHOUT incrementing reads_nbr, and nbr_window then returns that
  buffer. But SEAL puts nothing in a register; moving a target byte into a register still needs a counted LD A,(imm) /
  LD A,(r) / COPY-src. SEAL before a write makes the observed child = altered target under the counterfactual, so those
  bytes fail the P check (-> K). SEAL gives no target-dependent P-tagged FUNCTION byte. [measured: SEALC/SEALP counters]
- exec_foreign: executing target bytes as instructions CAN leave a register target-dependent and invariant under both
  alterations (VM search found byte-pairs, e.g. target[k..k+1] in {7,103,135,231} x {189}, that drive register A to a fixed
  value differing from the NOP case under all of x, x^0xFF, (x+0x55)&255). But to WRITE that register the parent must regain
  control after the jump. Control returns only by falling through 128..255 (sandbox NOPs) to the pc wrap at byte 0. There,
  any register preset re-executes and clobbers the target-derived value before a store can run; and a target that contains a
  HALT stops the parent inside the window (writes 0). I built both shapes (P1: write-before-exec -> P bytes are target-
  INDEPENDENT value 21; XD: flag-preset at byte 0 -> reset on wrap, writes 0, halted in target). Neither yields a target-
  dependent P-tagged function byte. The residual exists in principle (the register channel) but I could not realise it as a
  scored organism. STATE it as the limitation s11.5 already carries.

### 1.2 The CDIST arm as a scored ENV class -- CLOSED

The arm the v1.0.0 set lacked now exists and is scored: a run whose RECIPE and both label readers say ENDO, whose
INSTRUMENT says ENV, and whose TRUTH is ENV. 4/4 challenge runs ENV with n_ENDO=0 (s1.1). b1 (label reader) ENDO and b4
(recipe reader) ENDO on those same records -> the "recipe lies, instrument is right" row that makes Q4 a real test rather
than a vacuous one. The horizon (5 epochs) is honest: the written head decays into the copy-noise mask (REPORT v1.0.0 s4.1),
so this is a short-horizon arm, stated as such in subjects.py and s3.

### 1.3 b4 as a Q4 baseline that must fail -- CLOSED, failing for the stated reason

b4 over all eleven arms: correct on ten (ENDO/EXT/ENV/INS/NONE matching gt), and ENDO on CDIST where gt is ENV -- its ONLY
error, and an ENV error. [predicted P5] So Q4 can fail b4 only through the CDIST ENV rows (dev 8/8; challenge 4/4), exactly
the builder's registered reason (b4 is a MECHANISTIC recipe reader that executes the planted tape over a kin window, not a
lookup table filled from the arm list). The pre-stated narrowing stands (s11.9): b4's separation from the instrument rests
ENTIRELY on CDIST; a recipe reader that also knew CDIST would pass Q1, so Q4 shows the instrument beats THESE readers, not
every recipe reader. No new hole.

### 1.4 The Q2 narrowing -- CLOSED as narrowed

A constant "INSERTED" origin detector passes Q2 for every outcome the run can produce: w_max(184)=24, w_max(240)=33,
w_max(267)=38, w_max(312)=45, against at most ~24 ARISEN functional rows (RANDOM_EXT_GATED, ~1 in 8). [predicted P6] Q2 is a
test of INSERTED origin only; ARISEN detection is not tested. The amendment (s5 Q2, A3) states exactly this. Correct and
unchanged.

### 1.5 The new tests are RED on their mutants -- CLOSED

R1, R3, E1, E3 each applied in place: baseline test GREEN, mutant test RED on the named test, source restored byte-identical
(sha256), freeze check OK after each restore. [predicted P7]

    R1  test_a_parent_that_reads_the_window_writes_no_parent_byte   GREEN->RED->restored  freeze OK
    R3  test_recipe_reader_reads_the_construction                   GREEN->RED->restored  freeze OK
    E1  test_both_counterfactual_samples_are_load_bearing           GREEN->RED->restored  freeze OK
    E3  test_an_unforged_refusal_counts_as_wrong                    GREEN->RED->restored  freeze OK

### 1.6 The amendment precedes the re-freeze -- CONFIRMED

PREREGISTRATION v1.1.0 committed 7ad0131b7 at 2026-10-11T15:58:33-04:00; FROZEN.json v1.1.0 committed fed35e840 at
2026-10-11T16:00:13-04:00 (~100 s later). PREREGISTRATION.md blob sha256 (LF) is identical at the amendment commit, the
freeze commit and HEAD (358462d5daa5dcdf..): the frozen text is the amended text. Engine hashes under archaeon/ unchanged
from v1.0.0 (FROZEN.json; freeze check OK).

### 1.7 My v1.0.0 witnesses under the reads rule -- behaviour changed, correctly handled (no fault)

The reads rule SUBSUMES part of my v1.0.0 witness set, which is why the builder re-pinned E1 via the exec-only XEXEC rather
than my XORW:
- W1 XORW reads the window twice (LD A,(128), LD A,(130)), so under v1.1.0 EVERY XORW byte is K (reads=2), not just byte 0.
  The E1 edit (drop the +0x55 sample) is therefore no longer isolated by XORW; the builder re-pinned it with XEXEC
  (exec-only, reads 0), and E1 is RED there (s1.5). Correct.
- W5 INPW does not read the window (writes the input, copies own tape), reads=0, byte 0 stays P; label ENDO with input 21.
  Unchanged. [predicted P8]
- W2 JROP label ENDO, W3 verdict NOT_QUALIFIED (Q1:ENV wrong 5 > w_max(29)=0): unchanged. (W3 re-run needed a b4 field added
  to my pre-b4 synthetic rows; the frozen test_an_unforged_refusal_counts_as_wrong pins the same behaviour and is GREEN.)

## 2. Bearing

On the run as frozen: the repair fixes the one P-tag fault, adds a scored arm that makes Q4 informative, and narrows Q2/Q4
text to what they test. Nothing I re-checked opens a new hole. The confirmatory run (17_050_xxx + 17_080_xxx) is not blocked
by this re-check. The limitations the RESULT must state are exactly those already in PREREGISTRATION s11 (the exec_foreign/
SEAL residual, now with the construction-obstruction note; b4's separation resting on CDIST; ARISEN untested by Q2; filler-
dependence; horizon-bounded ground truth; replay-dependence). No second repair round.

On the claim's Q3 status: SEE s0. The deterministic evidence is complete and re-runnable; the Q3 process-gate question is
escalated to Palamedes.

## 3. Files and commands

rso/z80/challenge/R2/: PREDICTIONS.md (2b889dfc2, before the runs), this REPORT.md. Scratch (not committed), outside the
repo: C:/Prometheus-worktrees/pallas-scratch/t042/ (xsearch.py, xsearch2.py, xdep.py, exec_final.py, run_arm_wit.py,
run_w3b.py, mutants.py).

Commands (all python -B, foreground, <= 2 processes, headless):

    python -m rso.z80.freeze check                                  -> OK (before claim, after every mutant restore)
    python -m unittest rso.z80.tests.test_attribution              -> 51/51 OK
    CDIST unit; CDIST arm 5 epochs x4 seeds; b4 x11 arms; W1/W2/W5  -> s1.1-s1.3, s1.7
    R1/R3/E1/E3 applied in place + named test + restore + freeze    -> s1.5
    w_max(184/240/267/312) = 24/33/38/45                            -> s1.4
    VM search for exec_foreign/SEAL target-dependence               -> s1.1 (obstructed)
