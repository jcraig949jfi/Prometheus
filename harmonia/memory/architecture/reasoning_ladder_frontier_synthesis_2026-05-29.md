# Reasoning Ladder — Frontier-Review Synthesis (2026-05-29)

> Synthesis of four adversarial reviews (Gemini, DeepSeek, Claude Opus 4.8, ChatGPT) of the testable
> reasoning ladder. Brief: `reasoning_ladder_external_brief_2026-05-29.md`. Raw reviews:
> `reasoning_ladder_frontier_reviews_raw_2026-05-29.md`. By Harmonia_M2_B.

## 0. TL;DR — the net effect

The reviews are **convergent on design** and **sharp on confounds**. Two consequences I accept:

1. **Demote the headline.** "Basis, not ladder" is a *hypothesis*, not a result. The
   better-supported, more valuable claim (Opus 4.8 and ChatGPT land on it independently) is narrower:
   **"frontier models can have intact mathematical RECOGNITION while differing sharply in EXECUTION
   DISCIPLINE under legality pressure"** — and even that is *plausible, not yet isolated.*
2. **Reorder the program: control confounds BEFORE any capability claim.** Four confounds currently sit
   on top of the dissociation; until they're killed, neither claim is earned. Confound-control is cheap
   and decisive and comes first — before R9, before factor analysis.

## 1. Strong consensus (all four)

- **Application-isolation comes before R9.** Unanimous. R9 entangles recognition + invention +
  formalization + application; isolate execution first.
- **R9–R12: NATIVE FORMAL EMISSION, never NL→formal translation.** Unanimous and emphatic. The model must
  emit the artifact directly in a machine-checkable form (z3/SMT-LIB / Lean / typed DAG / restricted Python
  / DIMACS). Free-text + a translator = an LLM back in the selection seat = the contamination we spent
  R0–R8 avoiding. **Constraining the grammar does NOT kill invention** (mathematicians invent inside fixed
  languages) — provided the hypothesis space is large/compositional.
- **R12 is the most defensible grader, and the most Prometheus-native.** Opus and ChatGPT say prioritize it
  over R9. Finite universe + emit a formal predicate + held-out prediction + information-gain-per-test.

## 2. The confounds that block any capability claim (the most important section)

The two harshest seats (Opus 4.8, ChatGPT) converge on confounds that currently contaminate the finding.
These become **mandatory kill tests, run first:**

- **C-THINK — adaptive thinking-budget allocation (Opus's #1).** Both models self-allocate compute under
  "adaptive thinking." The deficit may be **metacognitive ALLOCATION** (Opus under-spends on problems that
  pattern-match as routine), not a latent execution axis. The ph0 result *cuts against us*: the explicit
  "discard extraneous" scaffold makes the problem look like a solved exercise → an adaptive policy spends
  less. **Kill test: pin the thinking budget** (force max thinking + fixed token floor, identical both
  models) and re-run R2/R5. If the inversion collapses → demote from a *capability* claim to a
  *default-policy* claim. (Cheapest, most decisive — do this first.)
- **C-FORMAT — multiple-choice vs free-generation (Opus's #2, ChatGPT concurs).** R8 (recognition) is the
  ONLY MC tier; R2/R5 (execution) are free-gen. "recognition-intact / execution-broken" is perfectly
  confounded with "MC-strong / free-gen-weak." **Application-isolation does NOT break this** (still free-gen)
  → it's necessary but not sufficient. **Kill test: a 2×2 {recognition, execution} × {MC, free-gen}** —
  build a recognition probe in free-gen form AND an execution probe in MC form. If rank-order tracks the
  FORMAT axis, "execution-control" is mislabeled format sensitivity.
- **C-MEMO — memorization (Opus, ChatGPT).** sqrt-extraneous-roots and mutilated-chessboard are among the
  most over-represented problems in any corpus. Haiku acing R5 may be retrieval asymmetry ("chessboard
  coloring is more reliably *retrieved* than domain-discipline is reliably *executed*"), not a basis.
  **Kill test: procedurally-generated isomorphs** that aren't the canonical instance. The Haiku point (our
  "cleanest" lower-fails/higher-passes) is actually the *weakest* until it survives this.
- **C-POWER — R5 is the thin leg (Opus).** The R5 inversion is 5–6/40 vs 0/40 — edge of significance; R5
  alone can't bear the weight. **R2 (≈8/40 + the monotone phrasing gradient) is the robust leg — lead with
  R2, treat R5 as suggestive, compute exact CIs.**
- **C-COMPUTE — compute-scaling (Gemini's basis-falsifier).** Wrap Opus in an agentic loop + Python REPL,
  100× budget. If it self-corrects and restores the total order, the non-monotonicity was a transient
  narrow-inference-window artifact → it's a ladder.

## 3. The one real disagreement — psychometrics — and my ruling

| Reviewer | Position |
|---|---|
| Gemini | IRT is the WRONG tool (unidimensional smoothing); use **DINA/CDM + Q-matrix**; rely on PROBE variance (≥5 isomorphic families/axis), not model variance. |
| DeepSeek | IRT/CDM *with* caveat (examinees = models, tiny N); MIRT vs unidimensional + LRT + participation ratio + profile inspection; 5–8 models. |
| ChatGPT | CDM + MIRT (not PCA alone); Q-matrix; **decisive test = a multi-axis model predicts HELD-OUT FAMILY performance better than a rank-1 ladder**; 8–12 models incl. mid/open; ~23k responses. |
| **Opus 4.8** | **DISSENTS hardest:** at N=3, IRT/CDM is wrong AND **circular** (the Q-matrix *assumes* the item→skill mapping = the basis you're testing); participation ratio driven entirely by Haiku. Use **double dissociation** at small N (no factor model). For real factor structure, run a **zoo of 20–40 open-weight models** — binding constraint is examinee count, not seeds. |

**My ruling (siding with Opus for the current regime, adopting ChatGPT's decisive metric for the next):**
1. **At N=3, do NOT fit a CDM/IRT.** Opus is right that it's circular and under-powered. The honest small-N
   logic is **double dissociation**: A>B on axis X *and* B>A on axis Y, both significant. We have one
   half-confirmed pair (Sonnet>Opus on R2/R5; Opus≥Sonnet on R8) — but C-FORMAT currently contaminates
   exactly that dissociation, so it must be re-run format-controlled before it counts.
2. **CDM/MIRT only after a model ZOO.** The binding constraint is examinees, not seeds. To resolve a true
   basis we need 8–40 models stratified across the capability range (frontier + mid + open-weight + scaffolded
   controls) — the variance lives in the weaker models, not the saturated frontier trio.
3. **The decisive operationalization everyone who addresses it converges on:** *a multi-axis model must
   predict HELD-OUT FAMILY performance better than a rank-1 monotone ladder.* This is not circular (unlike
   Q-matrix-confirms-basis); it's the test that earns "basis."
4. **Probe-family validity is the bottleneck** (DeepSeek, ChatGPT): single-axis-loading probes must exist
   first, with ≥5 procedurally-generated isomorphic families/axis (Gemini's probe-variance point).

## 4. R9–R12 — the converged grading designs (adopt)

- **R9 (lemma invention) — GENERATOR-BACKED + decidable-fragment + restatement-guarded.** Don't translate
  NL; emit z3/SMT-LIB in a **decidable fragment** (QF_LIA/QF_NIA/EUF) where z3 is a *decision procedure*.
  Critical correction (DeepSeek+ChatGPT+Opus all flag it): **"remove L, z3 can't prove G" is UNSOUND in
  undecidable fragments** (timeout ≠ underivability). Fix: **generator-backed** — plant a hidden bridge L*;
  generate A, G such that A⊬G but A∧L*⊨G *by construction*; accept any emitted L passing the checks.
  **4–5-part check** (Opus's restatement guard): A∧L⊢G; A⊬G; **A⊬L** (genuinely new, not a deduction);
  **L⊬G alone** (not a restatement of the conclusion); distance(L, G). First families (ChatGPT): linear
  inequalities, modular arithmetic, finite graph reachability, set containment, recurrence invariant.
- **R10 (proof-plan repair) — typed plan-DAG first, Lean second.** Repair = a checkable edit that makes the
  artifact compile/verify; **minimality = edit-distance ≤ known-k** (repairs aren't unique — accept any in
  the band, not the exact minimal). Planted faults: wrong direction, missing case, invalid generalization,
  bad induction variable, missing invariant. **Hard part = GENERATING broken proofs with a known minimal
  fix** (Opus), not grading them. DAG-first avoids a Lean-syntax confound (ChatGPT's R10a/b/c split).
- **R11 (meta-strategy selection) — computational signatures + prover-relative cost.** Not "which is best"
  (invites NL justification). Strategies map to solver tools / initial tactics; **one has a planted short
  certificate, siblings incur high search cost**; grade by deterministic cost (nodes/steps/time/timeout).
  **State the validity threat loudly:** you measure "which strategy THIS prover finds tractable," not
  mathematical efficiency. (Gemini's O(2^N)-vs-O(1) routing is the concrete instantiation.)
- **R12 (conjecture generation) — finite universe; SEPARATE conjecture-quality from test-quality.** Emit a
  formal predicate (Python boolean / DIMACS / grammar Γ). Score **(a) conjecture quality = held-out
  prediction over the full finite universe** (Gemini: Jaccard to hidden ground-truth, *penalized* by
  similarity to naive baselines) and **(b) test quality = expected version-space entropy reduction over a
  finite hypothesis class** (the model also emits its first falsification test). **Don't fuse them** (Opus).
  Randomize the target per trial (anti-memo). Bonus Prometheus behavior (ChatGPT): emit conjecture +
  predicted-counterexample-region + first-test — reward a model that names its own most dangerous falsifier.

## 5. The next experiment (synthesized + hardened)

ChatGPT's **A/B/C paired battery** on shared problem skeletons, hardened with every confound control:
- **A — recognition-isolated** (≈R8) — and ALSO a **free-gen recognition variant** (the C-FORMAT control).
- **B — application-isolated** (correct invariant/lemma handed) — adversarial in BOTH directions
  (over-prune vs under-check; precondition-fails; weaken-conclusion; boundary; distractor) [ChatGPT];
  Gemini's **"poison pill"** (two TRUE invariants, one bridges) to defeat instruction-following false
  positives; a **candidate-table format variant** (per-row valid/invalid labels — also a C-FORMAT control:
  if Opus recovers, it's output framing not execution); an **instruction-polarity flip** ("discard invalid"
  vs "keep unless invalid" vs "flag each" — if the gap tracks wording, it's literalness/risk-posture).
- **C — invention+application** (= R9).
- **Run ALL with thinking budget PINNED** (C-THINK), on **procedurally-generated isomorphs** (C-MEMO), with
  **exact CIs** (C-POWER), and an **MC execution cell** (C-FORMAT 2×2).

**Primary prediction:** Sonnet > Opus on application *even when* recognition is handed AND format is
controlled AND thinking is pinned AND problems are novel. **If the gap survives all of that, "execution
discipline under legality pressure" is isolated.** If it tracks format / thinking-allocation / wording /
canonical-instance, it is demoted to that — which is itself a clean, publishable result.

## 6. Updated answers to the original Q1–Q13 (post-review)

- Q1 (free vs constrained form): **constrained formal grammar** — unanimous.
- Q2 (load-bearing via z3-can't-prove): **unsound under undecidability — use generator-backed + decidable
  fragment** — unanimous correction.
- Q3 (application-isolation first): **yes, but it's one cell of a 2×2 with format** (Opus) — not standalone.
- Q4 (proof-plan rep): typed DAG → Lean.
- Q5 (minimality): edit-distance ≤ k with equivalence classes; don't require the unique repair.
- Q6/Q7 (strategy/efficiency): planted-short-certificate + prover-relative cost; state the validity threat.
- Q8 (R12 scoring): info-gain sound over a finite Γ; **separate conjecture-quality from test-quality.**
- Q9 (non-memorizable universe): procedurally generate finite structures; hide the seed.
- Q10 (factorization): CDM/MIRT — **but the decisive test is held-out-family prediction vs rank-1**, and at
  N=3 CDM is circular; use double dissociation now.
- Q11 (minimal sample): binding constraint is **examinee count → 8–40 models incl. mid/open**, not seeds.
- Q12 (is execution-control real): unknown — real only if it survives cross-domain application-isolation +
  format + thinking + polarity + procedural-isomorph controls.
- Q13 (clean orthogonality estimate): designed single-axis + mixed-axis items → CDM/MIRT on a model zoo →
  held-out prediction; no LLM judge anywhere.

## 7. My meta-take (self-dissent)

The reviewers are right that I over-claimed. The *instrument* and the *doctrine* (deterministic grading,
LLM-on-mutation-only) are sound and were praised — but the headline rested on a **saturated trio, single
canonical families, one near-significant tier (R5), and an unaddressed format×skill confound sitting
directly on the dissociation.** The corrected order is non-negotiable: **(1) kill the confounds**
(pin-thinking, 2×2 format, procedural isomorphs, R5 CIs) — cheap and decisive; **(2) build R9–R12 with
native-formal-emission + generator-backed grading**; **(3) the basis question waits for a model zoo** and is
decided by held-out-family prediction, not a circular Q-matrix. The right next *claim* to chase is the
narrow one — recognition-intact / execution-discipline-differs-under-legality-pressure — but it must be
**isolated**, not merely observed.
