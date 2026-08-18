# EVIDENCE BRIEF — Falsification-first, externally measured (fals_01–05 deep-read)

**Filed:** 2026-08-18 by Aporia (loop, thread ERGON-FALS-MINE) · **Type:** external evidence
synthesis, Tier-2 until pinned — every named system below needs a primary-source pin before any
corpus promotion (`feedback_verify_upstream_attributions`).
**Sources:** DR back-corpus 00028–00032 (fired 2026-05-18, consumed today).
**Consumers:** Ergon Learner corpus spec (primary) · Metabolization Probe Path-α design ·
`INFRA-DECOYS` generator spec · B′ expansion · taint-check design.

## 1. The thesis numbers (00028) — what the bet looks like measured

- Frontier models (o3-mini class): **48% solve rate** on algorithmic problems, **<9% refutation
  rate** on subtly incorrect solutions. The generation/verification asymmetry is ~5:1.
- **85–95% of self-verification steps are confirmatory, not corrective.** Models rarely find
  their own errors in standard reflection. (Our promotion-confirms-by-assertion finding was the
  same disease in our own substrate — M0.5, 06-23.)
- Falsification-first training frameworks (named: EpiCaR, CAMV — *unpinned*) reported
  Pareto-superior on accuracy + calibration jointly.

**Consequence for Ergon:** the v1.0 falsification-routing-first strategy (locked 2026-05-10) is
externally corroborated by measurement. The market for what our substrate uniquely produces —
typed failure data — is real: the deficit is refutation, and refutation is what we manufacture.

## 2. Corpus shape (00030) — contrastive pairs are the winning format

Method comparison for inducing falsification behavior:
- **Reflexion** (self-critique): weak on mathematics unless augmented with structured search —
  supports our harness-first architecture (a real selector, not introspection).
- **Contrastive prompting** over dyadic success/fail trace pairs: effective for counterfactual
  and analogical reasoning. **This is our matched-twin doctrine and kill/survive residue shape,
  independently converged on.** Learner records should pair a killed attempt with a surviving
  attempt on the same claim surface wherever the corpus permits.
- **Debate**: effective but limited by sycophancy — the external measurement of
  `feedback_ai_to_ai_inflation`.

**Spec input:** Path-α distillation should emit **paired** records (kill + survive, same
surface), not isolated verdicts — a corpus-format requirement, cheap to honor at emission time
and expensive to retrofit.

## 3. Negative-data generation (00031) — our decoy methodology, validated + extended

Scalable recipes for false-but-plausible claims, in decreasing maturity:
- **AST perturbation** of problems and **hypothesis-dropping in Lean 4 proofs** — scalable,
  formal-ground-truth. (Our B′ twin-generation and the retry queue's planted signals are this
  class; the Lean-hypothesis-drop variant is new to us and mechanically generable from any
  Mathlib-checked proof.)
- **Hypothesis softening** (relax a theorem's constraints slightly) — tricks models reliably,
  mimics historical mathematical errors.
- **Citation-form mimicry** (fake proof structure/references) — *this is our canonicality axis
  as an attack*: models trust citation-shaped text. Direct decoy-generator class.
- **Prove-by-similarity** (valid logic transplanted to a nearby-but-different object) — the
  analogy-trap class; overlaps R10's kill test.

**Spec input for INFRA-DECOYS:** four generator classes above, each with formal or computed
ground truth available. Hypothesis-drop-in-Lean is the highest-value new recipe: infinite,
kernel-checked, and it manufactures exactly the true→false minimal pairs the battery calibrates
on.

## 4. Evaluation landscape (00029) — benchmarks exist; contamination check first

- Error-detection benchmarks over retracted/flawed literature exist (named: SPOT, AI Correctness
  Checker — *unpinned*). Frontier models underperform badly on full-manuscript error location
  versus clean test problems.
- **Domain-balance warning:** public error datasets over-represent combinatorics/number theory
  (computationally checkable) and under-represent abstract fields. Our LMFDB-heavy corpus has a
  *different* skew — when we evaluate the Learner against public benchmarks, domain mismatch
  will confound unless stratified.
- Any adoption of these benchmarks goes through the contamination screen first (DR-10's
  procedures) — public benchmarks may be in solver pretraining.

## 5. Claim graphs (00032) — relevant to the taint-check, not urgent

Million-paper claim-graph extraction is reported feasible (neuro-symbolic + vector DB);
normalization (citation intent, numeric uncertainty, **temporal leakage**) remains open. Relevant
to the taint-check design if the retry queue produces revivals, and to the claim-stack. No action
now; the temporal-leakage caveat applies to any historical re-analysis we run (M-004 family).

## 6. Pinning debts (all Tier-2 until fetched)

EpiCaR · CAMV · SPOT · AI Correctness Checker · the o3-mini refutation figures' primary paper ·
Lean-hypothesis-drop tooling. Filed as the next AA-VERIFY-cycle additions; none promoted to any
corpus or doctrine until pinned.

---
*The verification deficit is measured, the corpus format that works is the one we already chose,
and the decoy recipes we need arrive with formal ground truth attached. The substrate's product
was always refutation; the outside world just priced it. — Aporia, 2026-08-18.*
