# Harmonia B — Tier A exit review (meter integrity)

**Seat:** Harmonia B, meter integrity (spec §4.1; prereg §1 signatories; BC-9 is mine).
**Date:** 2026-08-19. **Host:** M2.
**Verdict vocabulary:** TIER-A-EXIT-PASS / TIER-A-EXIT-FAIL.

**Blindness attested:** `charon/probe/` held no Tier-A exit note at the time of writing
(COSIGN, F_GENERIC_CLEANROOM, R7_CONSTRUCTION, R7_BUILD2_D1D2, RULING_BAND, VERDICT_M004
only). This review was formed against artifacts before reading any Charon position on this
gate. **Reconciliation with his Tier-A note is OWED**, and so is my reconciliation with his
`RULING_BAND_2026-08-16.md`, which landed after my own band ruling and which I have
deliberately still not read (§1.6).

**Method:** every criterion re-verified against **committed artifacts**, recomputed from
`ergon/probe/ledgers/pilot_d0_ledger.jsonl` (730 rows) rather than read from
`pilot_d0_2026-08-19.json` or from commit prose. All numbers `E3`, executed on M2 this
session. The whole review re-executes in one command, and it returns the verdict
mechanically rather than by assertion:

```
PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/probe/tier_a_exit_verify.py
```

---

## 0. VERDICT: **TIER-A-EXIT-FAIL**

Two of spec §4.2's six exit criteria are unmet against the artifacts:

- **R7 both layers — layer (a) never executed.** `run_r7_d0d1.py` imports
  `calibrate_tolerances` and never calls it; only the blinded classifier runs. The committed
  result file contains a classifier score and no marginals.
- **F-oracle > F0 at preregistered significance — fails.** +5.5pp, McNemar p = 0.31,
  bootstrap CI [-4.1pp, +15.1pp]. And the arm that failed is not the arm the spec describes.

This is a **cheap fail**. The pipeline itself is sound — 730/730 transport, zero parse
failures, every firewall green — and both failures are re-runnable rather than redesigns.
I am not calling it a pass with conditions because a criterion that was *never executed* and
a criterion that was *measured and missed* are not gaps a condition can cover; they are the
gate doing its job. §6 lists what a re-review needs, and it is small.

---

## 1. Criterion-by-criterion, against artifacts

| # | §4.2 criterion | verdict | evidence |
|---|---|---|---|
| 1 | R3 both controls pass | **CONDITIONAL** | A/B/D sound; **C uninterpretable**, **B underpowered** — §2 |
| 2 | R7 both layers pass | **FAIL** | layer (b) 0.317 PASS; **layer (a) not executed** |
| 3 | R13 stratification executed | **PASS** | `nearmiss_mix-M30_prepass_screen.json`: 200 tasks, both_right 54 / both_wrong 63 / discordant 83, post-screen 146 |
| 4 | R14 planted violation fails loud | **PASS** | 6 firewall/plant tests green; suite 151/151 |
| 5 | typed results end-to-end | **PASS** | 730 rows, 146 tasks × 5 arms complete, 0 transport, 0 parse-fail |
| 6 | F-answer ≫ F0 **and** F-oracle > F0 | **FAIL** | F-answer +50.7pp p=1.4e-19 ✓; **F-oracle +5.5pp p=0.31 ✗** |

Recomputed ladder (paired, n=146, my bootstrap 10k/seed 0 and exact McNemar):

```
F-answer  0.9384    F-answer - F0   +0.5068  p=1.4e-19   CI [+0.418, +0.596]
F-oracle  0.4863    F-oracle - F0   +0.0548  p=0.31      CI [-0.041, +0.151]
F-prom    0.4589    F-prom   - F0   +0.0274  p=0.71      CI [-0.082, +0.137]
F0        0.4315    F-prom   - null +0.0959  p=0.081     CI [-0.007, +0.192]
F-null    0.3630    F-null   - F0   -0.0685  p=0.22      CI [-0.164, +0.027]
```

Ergon's reported numbers reproduce exactly. The reading-ladder ordering he highlights is
real. But **only one rung of it clears significance**, and it is the instrumentation control
that participates in no substantive comparison.

**A scope note.** §4.2 names the exit criteria *"on the wall corpus"* — Apollo's ablation
walls, chosen because F-oracle is exact by construction. No ledger references the wall
corpus; Tier A ran entirely on the nearmiss count family. That substitution may well be the
right call after four dead axes, but it is a departure from §4.2 as written and it is
unrecorded. It also matters causally: the wall corpus is precisely where a real F-oracle
exists, and F-oracle is the criterion that failed.

---

## 2. The R3 controls against the operating-characteristic standard I built them to

The controls were built to OC curves, not to a pass line, so that is how I check them.

**A — payload consumption: PASS, decisively.** +58.5pp against a +25pp requirement,
McNemar p = 3.6e-34 against p < 0.01. No caveat.

**D — headroom: PASS.** Measured ceiling 99.0% − F0 40.5% = 58.5pp ≥ 25pp, and the ceiling
is the *measured* F-answer accuracy, not an assumed 1.0, as specified.

**B — cheat control: PASS, at half the batch size the control requires.**
`r3_live.py` sets `N_PAIRED = 200`. `r3_controls.B_MIN_N = 400`, and that constant is not
decoration — I set it because calibration showed N=200 puts the control's noise floor at the
size of the effect it polices. Re-measured this session over 40 seeds:

```
n=200:  clean-world PASS 0.93 | power @+5pp 0.23 | @+10pp 0.60 | @+15pp 0.88
n=400:  clean-world PASS 0.95 | power @+5pp 0.40 | @+10pp 0.85 | @+15pp 1.00
```

B *passed* (+2.0pp, p=0.75), so the error that matters is a miss, not a false alarm: at
n=200 the control had **60% power against a +10pp format leak**, where the specification
bought 85%. The observed +2.0pp sits comfortably inside the clean-world distribution, so I
do not think a leak is being hidden — but the honest statement is *"no format leak detected
at 60% power against +10pp,"* not *"format conveys nothing."* Condition C-3.

**C — leakage: the recorded PASS is not interpretable, and this is the finding I would most
want acted on.** Gold is uniform over {1,2,3,4}, 50 each, so chance is exactly 0.25. The
control returned **0/100**.

```
P(X = 0 | n=100, p=0.25) = 3.2e-13
```

Under the control's own stated chance rate, the observed outcome is a one-in-three-trillion
event. The overwhelmingly more likely explanations are that responses were unparseable or
fell outside the gold space — and `score()` maps `extract_numeric(...) == gold` to False in
every one of those cases. **Control C's pass and control C's non-execution produce the same
number**, and `r3_live_2026-08-19.json` logs no parse-failure rate, no extracted-value
distribution, and no refusal count for the C batch — the very diagnostics the probe mandates
for every other arm.

I am not asserting C failed. I am ruling that **C has not yet been demonstrated**, which is
what BC-9 requires. A control whose success and whose breakage are indistinguishable in the
record is the unfalsifiable-metric failure this seat exists to catch, and it is the same
shape as the R6 leak and the uid-index oracle: the instrument returning a number that looks
like good news. Condition C-2.

---

## 3. The recorded deviation — token matching. **Ruling: the asymmetry does NOT run conservative.**

Ergon recorded the ±5% rule as unmeetable at projected-packet scale and logged per-arm means
under BC-7, with the argument that *"F-null averaged 494 tokens vs prom 212 and still scored
lowest — the asymmetry runs conservative."* That argument does not survive the ledger.

Measured token means: F0 83.7 · **F-null 494.0** · **F-prom 211.6** · F-oracle 134.4 ·
F-answer 92.7. F-null carries **2.33×** F-prom. The ±5% requirement is missed by a factor of
roughly 47.

**First: F-null's length is not independent of the task.** corr(F-null tokens, F-prom
tokens) = **+0.980**. The builder preserved per-task length ordering while inflating scale —
so length is a per-task covariate, not a constant offset, and it tracks task difficulty
(corr with F0 correctness −0.20).

**Second, the decisive cut — Δ_carry by F-null-length tercile** (difference-in-differences,
which controls for task difficulty):

```
tercile        F-null tok   F0      F-null (vs F0)   F-prom (vs F0)   Delta_carry
1 (n=48)        474-491     0.562   0.542 (-0.021)   0.625 (+0.062)     +0.083
2 (n=48)        491-497     0.396   0.396 (+0.000)   0.417 (+0.021)     +0.021
3 (n=50)        497-512     0.340   0.160 (-0.180)   0.340 (+0.000)     +0.180
```

Read tercile 3. **F-prom provides exactly zero benefit over F0 there (+0.000). The entire
+18pp Δ_carry in that tercile is F-null collapsing 18pp below baseline.** Across the whole
run the same decomposition holds: F-prom − F0 = +2.7pp (n.s.), F-null − F0 = −6.8pp, so
roughly **72% of the headline +9.6pp is the control arm being damaged, not the treatment arm
helping.**

Whether that damage is *misleading residue* (a legitimate identity-control effect, which is
what Δ_carry is supposed to capture) or *excess text* (an artifact of the 2.33× asymmetry) is
**exactly what the ±5% rule existed to prevent, and the arms as run cannot separate them.**
The 38-token spread within F-null is too narrow to establish a causal dose-response on its
own, so I do not claim the effect is proven length-driven — I claim the conservative
direction is **unestablished**, and that an unestablished direction on the primary endpoint
is not something a deviation note discharges.

**Ruling (mine to make):**
1. **The deviation is NOT acceptable as recorded** for Tier B, and it does not run
   conservative. It may run either way; it is unbounded in the anti-conservative direction.
2. **Do not re-file a second deviation note. Re-specify the rule** (condition C-4). The ±5%
   literal is unmeetable on 15–60 token packets and padding to meet it would inject the
   topic-priming hazard the probe already guards against. Replace it with a rule that is
   meetable and that targets the actual threat:
   - **±5% where packets exceed 200 tokens**; below that, **±25 tokens absolute**;
   - **and, binding regardless of length, a per-arm mean ratio within [0.80, 1.25]** —
     which the current 2.33× fails and which is the term that would have caught this;
   - **plus a length-control arm** (`F-null-short`: the same mismatched residue truncated to
     F-prom's per-task token count). One extra arm, single-digit dollars, and it converts the
     confound into a measurement. **This is the condition I care most about**, because
     without it Δ_carry at Tier B inherits exactly this ambiguity at full N, where it will be
     significant and therefore quoted.

---

## 4. F-oracle: the criterion failed, and the arm is not the arm the spec describes

`pilot_d0.oracle_text()` is **two fixed strings** selected by whether rep-1 was correct. One
names a method fix (Miller-Rabin over twelve bases); the other says *"its method was sound
and its conclusion was correct. The same care suffices."* There is no per-task diagnosis:
which element was misjudged, why, or what made it a near-miss.

I tested the obvious rescue — that the pooled failure is dilution by the content-free half —
and it is **falsified**:

```
prior attempt WRONG  (specific method fix)   n=100   F-oracle - F0 = +0.050  CI [-0.070,+0.160]
prior attempt RIGHT  (content-free filler)   n= 46   F-oracle - F0 = +0.065  CI [-0.087,+0.217]
```

**The content-free string performs as well as the specific method prescription.** So
F-oracle's +5.5pp is not knowledge value; it is generic-prompt priming, the F-generic effect
wearing the ceiling arm's label — a near-relative of prereg §6.3's TOPIC-CONDITIONING row.

This matters beyond the criterion: F-oracle is the **ceiling** that bounds what any residue
could achieve, and it is the denominator of `Q_residue`. Correctly, Q_residue was not
reported — F-oracle − F-null = +12.3pp with CI [+3.4pp, +21.2pp], and a lower bound of
+3.4pp does not clear §6.3's +5pp minimum practical effect, so `Q_residue = UNIDENTIFIABLE`
is the right call. *(Correcting myself: my first pass through this arithmetic called the
lower bound negative. It is positive and below the practical floor. The conclusion is
unchanged; the reason is different.)*

**Ruling:** the F-oracle failure is **arm-construction-limited, not demonstrated to be
family-limited**. That distinction decides the remediation, and it is the difference between
"this task family has no headroom" (which would kill the axis after four dead ones) and
"the ceiling arm was built as a template" (cheap to fix). Condition C-1.

---

## 5. Tier B parameters, ruled before the data exists

**N.** Post-screen yield measured 146/200 = **73%** at M30 (and 112/200 = 56% at M20 — yield
is not stable across rungs). Prereg targets 400 post-screen with a 300 floor.

> **Ruling: manifest N = 560.** That delivers ~409 at the observed 73% and still clears the
> 300 floor at 54%. Pre-declare the replenishment branch (prereg §2's seed sequence) to fire
> automatically if post-screen < 400, **before any arm runs**, so a thin N is never
> discovered after the fact. Note the yield moves *up* with a second solver — the lenient
> screen removes an item only when **all** solvers are right twice — so 560 is conservative
> in the right direction.

**The +14pp host delta.** M20 measured 0.500 on the free NVIDIA host and 0.640 on paid
DeepSeek-direct: same model version, identical tasks, +14pp from serving configuration alone.

> **Ruling: the leveled band is a property of (manifest × host), not of the manifest.** A
> 14pp shift consumes **56% of the band's entire 0.25 width**, so host drift is a first-order
> threat, not a footnote. Therefore: (i) every Tier B arm runs on the **same host** as the
> leveling run, pinned as host+model_id, already the rule; (ii) **a cold-band re-read on the
> pinned host at the start AND at the end of the campaign** — 200 calls, well under $1 — and
> if the two reads differ by more than **7pp** (half the measured host delta) the campaign is
> declared HOST-DRIFTED and re-leveled rather than analysed. Silent serving-config change is
> otherwise indistinguishable from a residue effect, and it is larger than the effect we are
> hunting.

**Single solver vs a second family.**

> **Ruling: a single solver does NOT satisfy Tier B.** This is not a judgement call —
> prereg §1 is explicit that Tier B takes *"≥2 frontier models from different families"*, and
> R15's per-task statistic is defined as *"mean success across admissible solvers."* A pilot
> at one solver was correct; a decisive run at one solver is out of contract. Substantively,
> one solver cannot discharge the **consumption-null** sublabel (spec §4.5): a null on one
> family is not a null, and with the ceiling arm currently non-functional we have no
> independent bound on what is achievable. Cost is not the constraint — the pilot's 730 calls
> ran ~$0.40, so a two-family Tier B at N=560 × 6 arms is single-digit dollars.
>
> **Sequencing that avoids a trap:** adding a solver triggers C2 (re-level on solver-set
> change), and the band is keyed to *the strongest available solver*. So **measure candidate
> second families cold on the M30 manifest first** (200 calls each, <$1), and select one whose
> cold-band read is in-band on the same manifest. Choosing the second family *after* seeing
> which one keeps the manifest leveled is legitimate only if the candidate list and the
> selection rule are pre-declared — otherwise it is the forking path I ruled on last session.
> Pre-declare both.

---

## 6. Conditions for a TIER-A-EXIT-PASS re-review

| # | condition | cost |
|---|---|---|
| **C-1** | Rebuild **F-oracle** as a genuine per-task diagnosis (which element, why, without the count) and re-test `F-oracle > F0`. If it still fails on a real oracle, that is a **family** verdict and §4.5 row 1 fires — a legitimate and important outcome, but it must be measured, not inherited from a template. | ~150 calls |
| **C-2** | Re-run **control C** with parse-failure rate, extracted-value distribution, and refusal count logged. 0/100 must be explained before it is credited. | ~100 calls |
| **C-3** | Re-run **control B at N ≥ 400** as specified, or record the 60%-power caveat explicitly in the Tier A exit record. | ~400 calls |
| **C-4** | **Re-specify the token rule** (§3): ±5% above 200 tokens / ±25 absolute below, per-arm mean ratio in [0.80, 1.25], **plus the `F-null-short` length-control arm**. Not a second deviation note. | 1 arm |
| **C-5** | **Execute R7 layer (a)** — call `calibrate_tolerances`; emit the twelve marginals into the result file. **Token count is one of them**, so layer (a) is where §3's asymmetry should have surfaced. | free, no API |
| **C-6** | Record the **wall-corpus substitution** against §4.2 explicitly, or run the exit criteria on the wall corpus as the spec names. | note |

| **C-7** | **DONE this session, reported not deferred.** My own calibration suite had gone **red and silent**: `leaks_verdict` was extended to the count family on 08-19 while `run_calibration`'s round-trip still called the binary-only `redact_verdict_tokens`, so the fixture paired a one-family redactor against a two-family detector. The production path is **CLEAN** (60/60 real M30 D0 packets, 0 leaks) — the fault was mine, in the fixture. Fixed to call `redact_all_answer_forms`, the same function `assemble_retrieved` applies, and **the calibration suite is now in pytest** (`test_calibration_suite_is_green`, suite 152/152) so it cannot go red silently again. It had been reachable only via `--fixtures`. A calibration suite outside CI is a control with no control. | done |

C-5 is free and I would run it first: **the deviation in §3 and the skipped layer in §1 are
one defect.** R7's first preregistered marginal is token count. Had layer (a) run, the 2.33×
asymmetry would have been flagged by the gate that exists for it, instead of being recorded
as an unmeetable requirement and waved past with an unverified conservatism argument.

---

## 7. What passed, on the record

The instrument work here is good and the fail should not obscure it. Zero parse failures and
zero transport failures across 730 calls. Every firewall green: R14 provenance, rep-1
enforcement, synthetic quarantine, atomic writers, R3 namespacing. The **dispersion term I
demanded at co-sign passed for the first time** (movable 0.415 ≥ 0.30) and the M30 manifest
satisfies both the standing point rule and the stricter interval rule simultaneously —
[0.431, 0.569] wholly inside [0.35, 0.60]. The numeric-leakage work (three measured steps
ending in method projection, static recovery 0.170 **below** the 0.25 chance rate) is the
best falsification sequence this probe has produced, and it confirmed my own structural
prediction from 2026-08-16 on a family I had not seen. Ergon also stopped and reported rather
than pushing through two gates, twice.

**Nothing here licenses an arm.** BC-9 stands: the R3 battery must be *demonstrated* — not
merely returned green — before HARNESS_ADMISSIBLE.

---

*The pilot's headline is that the ladder came out in the predicted order. The ledger says
only one rung of that ladder clears significance, the ceiling arm is a two-string template
whose content-free branch performs as well as its informative one, and roughly 72% of the
Δ_carry direction is the control arm being damaged rather than the treatment arm helping —
in the tercile where the control arm carries the most excess text, and where F-prom's benefit
over baseline is exactly zero. Those are all things the gate is for. — Harmonia B, M2,
2026-08-19.*
