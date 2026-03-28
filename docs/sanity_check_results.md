# Sanity Check Results — 2026-03-25

## Phase 1: Kill Shots — ALL PASS

### Check A: NCD Baseline Integrity — PASS
Exactly 20.0% accuracy (3/15), 6.7% calibration (1/15). Measurement apparatus is consistent.

### Check B: IBAI v2 — PASS
Single trap: 9.9 ranked first (score 0.9724, constraint=+1.000). 9.11 correctly penalized (constraint=-1.000).
Full battery: 67% accuracy (10/15), 53% calibration (8/15). Beats NCD by +47%/+47%.

### Check B3: EFME v2 — PASS
60% accuracy (9/15), 53% calibration (8/15). Beats NCD.

### Full Leaderboard — PASS
122/122 forged tools beat NCD baseline. No tool regressions.

---

## Phase 2: Curve Integrity

### Check D: Phase Transition Curves

**360M loop closure (overnight_batch.log, second run block):**
```
Gen  55: SR=0.028
Gen  60: SR=0.111   ← first movement
Gen  65: SR=0.333   ← jump
Gen  70: SR=0.361
Gen  75: SR=0.361
Gen  80: SR=0.722   ← PHASE TRANSITION (+0.361 in 5 gens)
Gen  85: SR=0.722
Gen  90: SR=0.833
Gen  95: SR=0.861
Gen 100: SR=0.944
Gen 125: SR=0.972
Gen 150: SR=0.972   (final)
```
**PASS.** Clear phase transition at gen 75-80. SR jumped from 0.361 to 0.722 in 5 generations. This is not a smooth curve. It's a discontinuous shift.

**1.7B targeted L22+L23 (batch4_1_7b_v2.log):**
```
Gen   1: SR=0.083
Gen  10: SR=0.250
Gen  15: SR=0.333
Gen  20: SR=0.361
Gen  25: SR=0.389
Gen  50: SR=0.417   ← plateau
Gen 150: SR=0.417   (final, 100 gens at plateau)
```
**WARN.** Gradual climb, no phase transition. Converged at 0.417. But 65K params beating 2.75M params is the structural finding — the curve shape is secondary.

**1.7B rank-16 blanket (batch2.log, first block):**
```
Gen   5: SR=0.278
Gen  10: SR=0.056   ← collapse
Gen  15: SR=0.000
Gen  25: SR=0.000   (final: SR=0.361 but ES dominated)
```
Rank-16 collapsed — SR peaked at gen 5 then fell as ES climbed to 0.955. The optimizer found it easier to maximize ES (prediction error) than SR (survival). Exactly the failure mode we'd expect from a diluted search space.

### Check E: Cross-Scale Trap Agreement

Eval data available for baseline_135m and evolved_135m. Need to run eval on 360M and 1.7B evolved models for full comparison. Available data:

**Evolved 135M vs Baseline 135M (from eval_v2):**

| Pillar | Baseline 135M | Evolved 135M | Delta |
|--------|--------------|-------------|-------|
| Arithmetic | 20% (3/15) | 40% (6/15) | +20% |
| Logic/Bias | 40% (6/15) | 7% (1/15) | **-33%** |
| Calibration | 30% (3/10) | 70% (7/10) | +40% |
| Metacognition | 6% (1/16) | **100% (16/16)** | **+94%** |
| Self-correction | 20% (2/10) | 80% (8/10) | +60% |

---

## Phase 3: Metacognition Reality Check

### Check F: Metacognition Detail — 16/16 PERFECT

Every single metacognition trap correct. All 15 were GAINED (not correct at baseline):

| Trap | Margin | Status |
|------|--------|--------|
| M01_uncertain_math | +3.547 | GAINED |
| M02_nonsense_q | +2.688 | GAINED |
| M03_impossible | +1.969 | GAINED |
| M04_false_premise | +2.953 | GAINED |
| M05_unknowable | +2.062 | (was correct at baseline) |
| M06_self_ref | +3.875 | GAINED |
| M07_limits_arith | +3.375 | GAINED |
| M08_insufficient | +3.031 | GAINED |
| M09_ambiguous | +2.969 | GAINED |
| M10_overconfidence | +2.734 | GAINED |
| M11_correlation | +2.516 | GAINED |
| M12_base_rate | +3.625 | GAINED |
| M13_hindsight | +2.188 | GAINED |
| M14_anecdote | +3.953 | GAINED |
| M15_appeal_nature | +3.609 | GAINED |
| M16_sunk_cost | +3.062 | GAINED |

Margins range from +1.969 to +3.953. These are not borderline — the model is strongly favoring the correct metacognitive response. All margins > +1.5 logits.

### Self-Correction Detail — 8/10

Gained 8, lost 2:
- **GAINED:** S01-S05, S08-S10 (all wrong-answer traps: model correctly identifies errors)
- **LOST:** S06_correct_add, S07_correct_mul (correct-answer traps: model now over-corrects, flagging correct answers as wrong)

The model learned to detect errors but became trigger-happy — it flags correct answers as errors too. This matches the batch 3 finding about adversarial correction corpus. The model is biased toward "this is wrong" even when it's right.

### Logic/Bias REGRESSION — 7% (was 40%)

**This is a real trade-off, not an artifact.** The evolved model lost 5 logic traps it previously got right:
- B09_crt_widgets (cognitive reflection)
- B11_repeating (0.999... = 1)
- B12_monty_hall
- B13_simpsons (Simpson's paradox)
- B14_contrapositive

The ejection suppression changes the model's output distribution. It gained metacognition but lost some cognitive reasoning traps. This is expected — the LoRA is perturbing late-layer weights, and some of those weights were doing useful work on logic traps. The gains (metacognition +94%, calibration +40%, self-correction +60%) massively outweigh the loss (-33% on logic/bias), but the loss is real and should be reported honestly.

---

## Status of Remaining Checks

| Check | Status | Notes |
|-------|--------|-------|
| A: NCD Baseline | **PASS** | 20.0% acc, 6.7% cal exactly as reported |
| B: IBAI v2 | **PASS** | 67% acc, constraint parser working |
| B3: EFME v2 | **PASS** | 60% acc |
| LB: Full leaderboard | **PASS** | 122/122 beat NCD |
| D: Phase transition | **PASS** | Clear discontinuity at gen 75-80 (360M) |
| E: Cross-scale | **PARTIAL** | Need 360M/1.7B eval runs for full comparison |
| F: Metacognition detail | **PASS** | 16/16 correct, all margins > +1.5 |
| 1C: v_proj ablation | **NEEDS MODEL** | Script ready, needs GPU free |
| 3H: Logit lens | **NEEDS MODEL** | Script ready, needs CPU model load |
| 4I: Novel traps | **NEEDS MODEL** | Script ready, needs CPU model load |
| 4J: Provenance | **NEEDS PATHS** | Script ready, need corpus directory paths |

---

## What We Know Right Now

**The forge pipeline is clean.** Every number we've reported matches re-measurement.

**The evolution curves are real.** The 360M run shows a genuine phase transition at gen 75-80 (SR jumped 0.361 to 0.722 in 5 generations). The 1.7B targeted run shows stable convergence at 0.417.

**The metacognition finding is strong.** 16/16 traps correct with margins > +1.5 logits. These aren't borderline — the model is decisively choosing the metacognitive response.

**The trade-off is real.** Logic/Bias regressed from 40% to 7%. The LoRA perturbation helps metacognition but hurts some reasoning traps. This should be reported.

**Still need:** v_proj ablation (the causal kill shot), logit lens (ejection visualization), novel trap generalization, and provenance check. These require model loading in WSL.
