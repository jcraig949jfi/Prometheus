# Reasoning Ladder — External Frontier-Review Brief (2026-05-29)

> The fixed briefing sent to Gemini, DeepSeek, Claude Opus 4.8, and ChatGPT for adversarial review.
> Responses archived in `reasoning_ladder_frontier_reviews_raw_2026-05-29.md`; synthesis in
> `reasoning_ladder_frontier_synthesis_2026-05-29.md`. Keep this version fixed so later rounds diff against it.

## 1. Background / frame
Prometheus treats FAILURE as the primary product. Doctrine: LLMs are mutation/generation engines, never
the selector/judge — all grading is deterministic (sympy + z3 + exact match). We are testing whether the
"Reasoning Ladder" R0–R12 is a single vertical staircase or a BASIS of partially-orthogonal capability
axes ("spanning, not climbing").

Operational tier definition: `capability = operation + perturbation + failure_mode + evidence_artifact`.
A system is at tier R_k only if it passes tier-k probes under perturbation + adversarial + transfer AND
emits the expected artifact. Each probe is generated in 4 versions: clean / iso / adversarial / transfer.

## 2. The ladder (built: R0–R3, R5, R6, R7, R8; designed: R9–R12)
R0 pattern-match · R1 rule-application · R2 constraint-tracking · R3 multi-step · R4 representation-shift
(not built) · R5 invariant-detection · R6 counterexample/falsification · R7 proof-repair (numbered-step,
integer grade) · R8 lemma-selection (5 lemmas incl. a tempting false one) · R9 lemma-invention (design) ·
R10 proof-plan-repair (design) · R11 meta-strategy-selection (design) · R12 conjecture-generation under
falsification (design).

## 3. Tests (Opus 4.8, Sonnet 4.6, Haiku 4.5; structured outputs → 0 parse failures; z3+sympy verifier)
- **3-model R0–R7 (n=8):** Haiku plateaus at R2 (extraneous-root, 0/8) and fails R7, but aces R5 →
  lower-fails/higher-passes. Opus & Sonnet clear R0–R7 (suite saturates vs frontier). R2 sharpest:
  Haiku 0 → Opus .75 → Sonnet 1.0.
- **Experiment A (n=40, Opus vs Sonnet, R2+R5, verifier 40/0):** inversion confirmed & widened —
  Sonnet 1.00/1.00, Opus 0.82/0.85. Morphology: R2 Opus OVER-REFUSES (drops valid roots), worst under the
  explicit "discard extraneous" phrasing (ph0 0.71); R5 Opus names the right invariant then mis-applies it.
- **R8 (n=30):** inversion flips — Opus 1.00 best; over-reach hypothesis unsupported.
- **Refined finding:** Opus's deficit is in EXECUTION/APPLICATION, not RECOGNITION/SELECTION
  ("capability ≠ control"). Caveats: small N, one probe-family/tier, frontier saturation, memorization risk.

## 4. What we asked the reviewers
1. Best deterministic (no-LLM-judge) grading for R9–R12, esp. R12.
2. Is application-isolation the right next probe before R9?
3. Is IRT / cognitive-diagnosis the right tool for basis-vs-ladder, and the minimal design?
4. What would FALSIFY "strength is not ladder-monotone" and "execution-control is a distinct axis"?
   (We asked for kill tests, not confirmation.)
