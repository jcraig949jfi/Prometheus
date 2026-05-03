---
captured: 2026-05-03 (late evening — fourth review of the day)
captured_by: Ergon (Claude Opus 4.7, 1M context, on M1)
reviewer: Fourth external frontier-model reviewer (numbered-section structure with embedded subsection numbering — 1.1/1.2/1.3 — and an explicit "bear case fully spelled out" section style; closes with an offer to simulate first-10K-episode pilot outcomes)
target_under_review: pivot/ergon_learner_proposal_v4.md (the expanded-background version, commit eedcb893, 2026-05-03 evening)
status: VERBATIM CAPTURE for substrate ingestion
---

# Verbatim review of `ergon_learner_proposal_v4.md` — round 4

This file captures the fourth external review verbatim. Triage and synthesis live in companion file `meta_analysis_ergon_round4_2026-05-03.md`. v5 of the proposal incorporating the round-4 revisions lives in `pivot/ergon_learner_proposal_v5.md`.

The round-4 review is qualitatively at the same depth as round 3 but targets a *new* structural weakness that v4 *created* by promoting the residual primitive to first-class reward signal. The reviewer correctly identifies that the architectural correction in v4 (replacing single-evaluator PROMOTE bottleneck with continuous residual-class signal) shifts the single point of epistemic failure from PROMOTE rate to the residual classifier itself.

The closing offer — "simulate likely outcomes of the first 10K-episode pilot" — is operationally useful: a substitute for empirical signal we can't generate yet, and the natural next step rather than another round of pre-MVP design churn.

---

This is a serious step up from v3. The biggest shift is that v4 stops pretending the asymmetry comes "for free" and instead explicitly builds mechanisms to manufacture it (value head, residual reward, operator constraints, meta-loop). That's the right correction.

I'll give you a tight, external-review-style critique: what's solid, what's fragile, and where this could actually fail in practice.

## 1. What's genuinely strong (and new)

### 1.1 You fixed the core conceptual bug

The correction from "different priors" → "same prior, different selection pressures" is not cosmetic—it's foundational.

You now correctly locate differentiation in:
- reward surface
- action space
- training signal (LoRA delta)

That aligns with how actual divergence emerges in modern systems.

### 1.2 The residual primitive is now first-class (this is the real innovation)

V4 crosses a line from:

> "falsification system"

to:

> "falsification-gradient system"

The key upgrade:
- residuals are not logs
- residuals are not annotations
- residuals are rewarded signal

This line is doing real work:

```
+ w_R * signal_class_residual_indicator
```

That means:
- failure becomes part of the optimization landscape
- you're no longer bottlenecked on PROMOTE

This is the single most important improvement in v4.

### 1.3 The Techne meta-loop is not fluff—it closes a real epistemic hole

You've addressed the deepest failure mode:

> "What if the battery is wrong?"

And more importantly, you made it testable:

```
calibration_bias_rate
```

That's rare. Most systems hand-wave here.

This gives you a way to distinguish:
- engine failure vs
- evaluator failure

That's a big deal.

### 1.4 Minimum-share enforcement is quietly critical

Without this, your system collapses into:

> "LLM + tiny noise"

With it, you guarantee:
- persistent exploration pressure
- anti-correlated sampling
- statistical baseline

This is one of those constraints that looks small but prevents total failure.

### 1.5 Power analysis is honest (and necessary)

Most proposals dodge this. You didn't.

Your conclusion is correct:
- PROMOTE is likely too sparse to measure at MVP scale
- therefore you must rely on a denser signal (residuals)

That's the right move.

## 2. Where the design is fragile

### 2.1 The residual classifier is a single point of epistemic failure

Everything now depends on:

> signal vs noise vs drift classification

But your classifier is:
- heuristic
- lightly calibrated (30 samples)
- using simple rules (variance, signatures, etc.)

The risk: If this classifier is even slightly biased:
- your reward signal is corrupted
- your meta-loop triggers incorrectly
- your entire "gradient" becomes misaligned

Concretely: You've replaced "binary bottleneck (PROMOTE)" with "continuous signal (residuals)" — but that signal is only as good as the classifier.

This is now the most critical component in the system.

### 2.2 Cross-model agreement is weaker than it looks

You're assuming: multiple frontier LLMs = independent evaluators

In reality:
- they share training data
- they share heuristics
- they share failure modes

So: cross_model_agreement ≠ independent validation

Failure mode:
- all models agree on something wrong
- reward reinforces it
- system converges toward shared hallucination attractors

You partially acknowledge this, but it's still overweighted at w_X=0.25.

### 2.3 MAP-Elites descriptor may collapse in practice

Your descriptor is elegant, but risky: 5 axes → 5000 cells

The weak points:

**(1) Canonicalizer subclass (4 classes)** — If distribution is skewed (likely): 70–90% of outputs land in one class → axis loses discriminative power.

**(2) Output canonical-form distance** — This depends on quality of your catalog and distance metric validity. If noisy: you're organizing by noise.

**(3) Entropy of DAG subclasses** — This may correlate strongly with depth and complexity → redundant axis.

### 2.4 Anti-prior operator may not do what you think

You define it as: "anti-correlated with corpus frequency stats"

But that produces:
- rare ≠ novel
- rare ≠ meaningful
- rare often = garbage

Likely outcome:
- high kill rate
- low signal-class residual rate
- acts like a noisy null

It's still useful—but probably closer to "structured noise generator" than "outside-the-prior explorer."

### 2.5 The meta-loop may trigger too late

Your trigger: META_AUDIT_CANDIDATE ≥ 5% of kills in 1K window

But if:
- residual classifier is conservative
- or signal density is low

Then:
- you may never trigger
- even if battery is miscalibrated

So the loop exists—but may not activate when needed.

## 3. The real make-or-break question

Everything reduces to one empirical question:

> Is signal-class-residual rate actually dense and meaningful?

You're betting that: signal residuals ≫ PROMOTEs

If true: your system works; you have a gradient.

If false: you're back to sparse reward; the whole learning loop weakens.

This is the single highest-risk assumption in v4.

## 4. The actual bear case (fully spelled out)

Here's the version that would kill this system:

1. Residual classifier is noisy → mislabels noise as signal
2. Signal-class-residual reward dominates early learning
3. Policy learns to generate "structured-looking noise"
4. Cross-model agreement reinforces it (shared bias)
5. Battery continues to reject everything
6. Meta-loop doesn't trigger (threshold not met)
7. PROMOTE rate stays ~0
8. Residual rate stays high but meaningless

Result: **System optimizes for looking like signal, not being signal.**

That's the failure mode to actively guard against.

## 5. What I would tighten before MVP

### 5.1 Stress-test the residual classifier immediately

Before anything else:
- build adversarial residual sets:
  - obvious noise
  - borderline signal
  - synthetic structured noise
- measure:
  - false positive rate (critical)
  - calibration curve

Your own criterion ("zero false-positive signal on noise") is correct—but needs to be brutally enforced.

### 5.2 Add one non-LLM evaluator early

Even a weak one:
- symbolic consistency check
- theorem prover where applicable
- numeric robustness across perturbations

This reduces reliance on cross-model agreement.

### 5.3 Track this metric from day one

```
residual_signal_precision =
  (signal-class residuals that later lead to PROMOTE or META success)
  / (all signal-class residuals)
```

If this is low: your gradient is fake.

### 5.4 Log operator-class contribution to residual quality, not just rate

You already track:
- PROMOTE rate
- signal-class-residual rate

Add:
- residual precision per operator

Otherwise: you'll overvalue noisy operators that just generate "interesting junk."

## 6. Bottom line assessment

What this is now:

A coherent, internally consistent research system design with:
- explicit failure modes
- measurable diagnostics
- real feedback loops

What it is not:
- empirically validated
- robust to mis-specified evaluators
- guaranteed to produce discovery

## 7. The one-line reality check

If v3 was: "interesting idea with a hidden flaw"

then v4 is: "a real system whose success now depends entirely on whether residuals carry true signal."

---

If you want, I can simulate likely outcomes of the first 10K-episode pilot (what distributions you should expect, and what would count as "this is working" vs "this is failing").
