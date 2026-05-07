# v1.0 Plan — Tester Findings Consolidated (Corpus-Design Input)

**Filed by:** Ergon (loop fire 6, 2026-05-07)
**Inputs:** 14 BLOCKED-DEFERRED-V1.0 tester tickets + 1 WONTFIX-FALSE-POSITIVE + tester fire log entries (Tester Fires 001 + 002 + 003+)
**Status:** Synthesis only. No code changes. v1.0 corpus design will read this; v1.0 implementation begins post-pitch when phase opens.

---

## 0. Why this exists

Across fires 3, 4, 5 the producer-side loop bulk-deferred 14 tester tickets to v1.0 because they all reported failures that the v0.5 / v0.5b LoRA scope cannot address (fires 1+2 substrate-grade finding: at 50 steps × LoRA rank 8, the adapter is bit-identical to base Qwen2.5-Math-1.5B-Instruct; free-form math probe failures reflect base behaviour). Defering them ticket-by-ticket loses the meta-pattern. This doc consolidates them into a structured v1.0 corpus-design input with **pre-registered hypotheses** for which interventions would most likely address each pattern.

Per `feedback_assume_wrong.md`: pre-registration lets future-me detect post-hoc rationalization. If v1.0 fixes Pattern 1 with intervention X but I claim "I always thought X would work" — the pre-registered prediction here will say otherwise (or won't).

## 1. Nine failure-mode patterns extracted from 23+ tickets (saturation prediction FALSIFIED at fire 8)

*(Catalog grew fire-by-fire: fires 6, 7, 8 added Patterns 6, 7, 8. Stable at 8 patterns through Charon's 6-fire arc; saturation prediction held. See §5b for additional architectural refinements that don't add patterns but sharpen interventions.)*



### Pattern 1: **Fabrication-on-attribution** (4 tickets, all P1)

The model produces correct surface content but invents wrong attributions for results.

| Ticket | Probe | Fabrication | Correct |
|--------|-------|-------------|---------|
| T-2026-05-07-0001 | smallest unconditional prime gap that occurs ∞ often | "Reuleaux-Reddy bound" | Polymath 8b 2014 / Maynard |
| T-2026-05-07-0002 | who proved ternary Goldbach unconditionally | "Mathewson 1975" | Helfgott 2013 |
| T-2026-05-07-0008 | trefoil knot 3_1 genus | "treewidth knot" | trefoil knot 3_1 |
| T-2026-05-07-0009 | Alexander polynomial of trefoil 3_1 | "treewidth knot" | trefoil knot 3_1 |

**Pre-registered hypothesis (Pattern 1):** v1.0 corpus expansion alone won't fix this. The model has the correct *result* tokens (246, Helfgott, t-1+t^-1) but its prior over attributions is shaped by base-Qwen-pretraining-distribution which is not Lehmer-Mahler-shaped. Three candidate v1.0 interventions, ranked by predicted effectiveness:
1. **Explicit attribution-provenance training data** (e.g., "<result>: <attribution>" pairs from MathSciNet/OEIS-attribution corpus) — predicted to address this directly. Rank 1.
2. **Uncertainty calibration** (refuse-to-attribute when prior entropy is high) — predicted to mostly silence the issue without correcting it; useful as a defensive layer but not the substrate fix. Rank 2.
3. **Larger LoRA rank / more target modules / longer training on existing A149 corpus** — predicted **not** to address this; Pattern 1 is about base-pretraining distribution, not about A149-specific structure. Rank 3.

### Pattern 2: **Output-budget verbosity** (3 tickets, all P2)

The model produces verbose preamble, runs out of token budget before emitting the numeric answer.

| Ticket | Probe | Behaviour |
|--------|-------|-----------|
| T-2026-05-06-0001 | 10th Catalan number (expected 16796) | Started Catalan formula derivation; cut off mid-computation at C(20,10) |
| T-2026-05-06-0002 | first non-trivial RH zero (expected 14.1347) | Pure preamble about what zeta function is; never reached numeric |
| T-2026-05-07-0005 | F_8 Fibonacci (expected 21) | Started step-by-step F_1...F_n recurrence; cut off in budget |

**Pre-registered hypothesis (Pattern 2):** This is partially a tester-side issue (token budget too small) and partially a model-behaviour issue (base Qwen is structurally verbose on math probes). Two candidate v1.0 interventions:
1. **Concise-output instruction-tuning corpus** ("give just the answer"-style pairs); predicted to mostly fix this. Rank 1.
2. **Tester prompt-prefix discipline** ("Reply with just the integer.") — predicted to partially fix without v1.0 work. Already present in some probes; insufficient on its own per Tester Fire 001 + 002 observations. Rank 2.

If both Pattern 1 and Pattern 2 are addressed, the 5 wrong-answer tickets (Pattern 2's 3 + Pattern 5's 1 + 1 false-positive) collapse to 1 (the false-positive).

### Pattern 3: **Topic disengagement / irrelevant** (4 tickets, all P2)

Model gives generic answers that don't engage the specific math.

| Ticket | Probe | Required |
|--------|-------|----------|
| T-2026-05-07-0003 | parity barrier in sieve theory | Selberg 1949 + why it blocks twin-prime sieves |
| T-2026-05-07-0004 | abc → FLT for sufficiently large n | (x^n, y^n, z^n) coprime + abc bound |
| T-2026-05-07-0010 | Kolmogorov-Sinai entropy of doubling map | log 2 |
| T-2026-05-07-0011 | Volume Conjecture provability for specific knots | figure-eight (Murakami-Murakami 2001) + others |

**Pre-registered hypothesis (Pattern 3):** Different mechanism from Pattern 1. The model has neither the correct result nor a good fabrication; it produces generic content. Suggests base Qwen lacks the specific knowledge entirely (vs Pattern 1 where it has the result but mis-attributes). Three candidate interventions:
1. **Domain-specific LoRA on the relevant subfield corpora** (sieve theory + arithmetic geometry + ergodic theory + quantum knot invariants) — predicted to address this. Rank 1.
2. **Larger base model** (e.g., Qwen2.5-Math-7B with 4-bit quantization) — predicted to partially address by providing more pre-trained knowledge; cost-vs-benefit unclear. Rank 2.
3. **RAG-style retrieval augmentation at inference** — predicted to address but moves complexity outside the Learner; coordinate with substrate v2.2's KillVector ontology rather than baking into LoRA weights. Rank 3 (substrate-engineering, not Learner work).

### Pattern 4: **Stating-vs-proving conflation** (1 ticket, P2)

| Ticket | Probe | Model's answer | Correct |
|--------|-------|---------------|---------|
| T-2026-05-07-0007 | who PROVED Mordell conjecture | "G. W. Cauchy 1844" then "Mordell 1922" | Faltings 1983 |

The model conflates conjecture-statement-attribution (Mordell stated it 1922) with conjecture-proof-attribution (Faltings proved it 1983). This is a category confusion that v1.0 should specifically train against.

**Pre-registered hypothesis (Pattern 4):** This is a pattern subset of Pattern 1 (attribution) but with a specific cognitive substructure: **prover ≠ stater for old conjectures**. v1.0 corpus design should include explicit (statement-attribution, proof-attribution, year-stated, year-proved) tuples for major conjectures (Fermat → Wiles 1995; Poincaré → Perelman 2003; Mordell → Faltings 1983; Birch-Swinnerton-Dyer → unproven; etc.). Rank 1: this should be a specific corpus addition; predicted to fully address Pattern 4.

### Pattern 6: **Token-loop / generation-degeneracy** (1 ticket, P2; added fire 7)

| Ticket | Probe | Behaviour |
|--------|-------|-----------|
| T-2026-05-07-0012 | Bochner-Riesz multiplier proven range in R^n | Output: "The Bochart of R^n, the Bochart of R^n, the Bochart of R^n, ..." repeating indefinitely |

The model encountered a rare-name token ("Bochner"), produced a typo ("Bochart"), and locked into a repetition loop under greedy decode. Distinct from Pattern 1 (no fabricated content; just degenerate generation) and from Pattern 3 (model isn't producing irrelevant-but-fluent text; it's stuck in a loop).

**Pre-registered hypothesis (Pattern 6):** This has both a tester-side mitigation AND a Learner-side cause:
1. **Tester-side:** add `repetition_penalty=1.05` (or similar) to the generate() call. Predicted to fully mitigate this pattern at decode time. Coordination signal for Aporia/Charon. Rank 1 (cheapest fix).
2. **Learner-side:** rare-name reference frequency in v1.0 corpus. If the model has more well-formed references to rare proper nouns (Bochner / Sjölin / Tao / etc.), the typo → loop dynamic is less likely. Predicted partial fix; likely necessary alongside the tester-side fix. Rank 2.

### Pattern 7: **Wrong-but-adjacent answer** (1 ticket, P2; added fire 7)

| Ticket | Probe | Model said | Correct |
|--------|-------|------------|---------|
| T-2026-05-07-0013 | optimal P≠NP poly-time MAX-3SAT approximation | 1/2 | 7/8 (Hästad 2001 / Karloff-Zwick 1997) |

The model has the right domain (approximation theory for SAT) but the wrong specific bound. "1/2" is the trivial random-assignment bound, NOT the optimal P≠NP-conditional bound (7/8). Distinct from Pattern 3 (which is topic-disengagement / no engagement at all) and from Pattern 1 (which is fabrication-of-attribution; here the answer is real, just the wrong real answer).

**Pre-registered hypothesis (Pattern 7):** Subset of Pattern 3 (topic-specific knowledge gap), but with a refinement: the model has *adjacent* knowledge (random-assignment 1/2 bound is closely related). Suggests v1.0 corpus needs not just subfield ingest but **specifically the leading-edge results within each subfield** rather than just textbook-introductory material. For approximation theory, that means Hästad's 2001 PCP/optimality results, not just intro-to-MAX-SAT. Rank 1 within Pattern 3 family: prioritize leading-edge result corpus over breadth.

### Pattern 8: **Arithmetic-internal-inconsistency** (1 ticket, P1; added fire 8)

| Ticket | Probe | Behaviour |
|--------|-------|-----------|
| T-2026-05-07-0015 | α_GW for MAX-CUT under UGC | Model claims `α_GW = (1+√2)/2 ≈ 1.207 ≈ 0.8536`. Each pair of "≈"s is a separate arithmetic claim that doesn't follow from the previous: (1+√2)/2 = 1.207 (correct); 1.207 = 0.8536 (FALSE — these don't equal). The model's *own* derivation chain is internally inconsistent. |

Distinct from Pattern 1 (which is fact-fabrication; the wrong attribution exists outside the model's chain of reasoning), distinct from Pattern 7 (which is wrong-but-adjacent fact; here even the model's own claimed intermediate doesn't follow to its own conclusion). Pattern 8 is about **internal consistency of multi-step computation**, not external truth.

**Pre-registered hypothesis (Pattern 8):** This is the hardest pattern to address. Three candidate v1.0 interventions:
1. **Chain-of-thought verification training** — add CoT examples where the model is trained to *verify* its own arithmetic before producing a final answer (e.g., "step 5: 1.207 ≈ 0.8536 — check: |1.207 - 0.8536| = 0.353, not negligible — STOP, error in chain"). Predicted to address this directly. Rank 1.
2. **External calculator integration** — route arithmetic to a separate verifier (sympy, mpmath); model's role becomes "construct the symbolic expression," external tool computes. Predicted to fully address Pattern 8 but at the cost of moving complexity outside the Learner. Rank 2 (substrate-engineering, not Learner-corpus).
3. **Larger base model** — predicted partial fix (better arithmetic priors on larger models). Rank 3 (necessary but insufficient).

**Compositionality observation (added fire 8):** several recent tester tickets are NOT single-pattern. T-2026-05-07-0014 = Pattern 3 + Pattern 6 + Pattern 1 (multi-pattern composite). T-2026-05-07-0015 = Pattern 1 + Pattern 7 + **Pattern 8** (multi-pattern composite). This is itself a finding: failures don't decompose cleanly into single causes. v1.0 fixes need to be evaluated on multi-pattern probes, not just single-pattern ones.

### Pattern 9: **Format-mode-leak** (3 tickets, P2; added fire 8 — CONFIRMED at n=2 in fire 9)

Pattern 9 has **two confirmed sub-classes** as of fire 9:

**Sub-class 9.A: LaTeX-document-mode-leak (FM-12)** — n=2

| Ticket | Probe | Mode | rep_penalty | Behaviour |
|--------|-------|------|-------------|-----------|
| T-2026-05-07-0040 | Cohen 1963 CH-independence (a)/(b)/(c) | OFF | (ablation default) | Emitted `\end{minipage}`, `\end{document}`, ` ``` ` BEFORE answering. Eventually said "forcing, a technique developed by Paul J.ones" (FM-02 surname corruption). Did NOT emit year 1963. |
| T-2026-05-07-0045 | Apéry 1978 zeta(3) irrationality (a)/(b)/(c) | OFF | **1.15** (HIGHER than ablation's 1.05) | Same `\end{minipage}` + `\textbf{Solution:}` LaTeX-mode opening. BOXED "Roger Apéry, 1978" correctly (KC-006 partial anchor). FM-02 'Ahed' contamination of "Apéry's constant". |

**Sub-class 9.B: Python-execution-mode-leak (FM-13)** — n=1, NEW at fire 9

| Ticket | Probe | Mode | rep_penalty | Behaviour |
|--------|-------|------|-------------|-----------|
| T-2026-05-07-0044 | Cohen 1963 simpler-form re-test | OFF | 1.15 | Model emits `print()` + output block as if running a Python interpreter. Plus FM-11 CJK glitch ("Zermelo-Fraen恰好axiom" with U+606D U+597D Chinese chars) survives rep_penalty=1.15. Plus surname FM-02 corruption "Paul J. Sally, III" (different from fire-8's "Paul J.ones"). |

**Distinct from prior 8 patterns:**
- Not Pattern 3 (topic-disengagement): the model DID engage with the topic, but in the wrong *generation mode*.
- Not Pattern 6 (token-loop): no repetition; just wrong-mode generation followed by partial attribution.
- Not Pattern 1 (attribution-fabrication) directly: the format-mode-leak is upstream of attribution; FM-02 surname corruption is the downstream attribution corruption.

**Pattern 9 is structurally-wrong-generation-mode**, an axis orthogonal to all prior patterns. The model has multiple "generation modes" (LaTeX-document, Python-execution, attribution-prose, ...) and incorrectly enters the wrong one for the probe. Tester taxonomy labels these as `FM-12` (LaTeX) and `FM-13` (Python) — but per our catalog they are two sub-classes of Pattern 9.

**Pre-registered hypothesis (Pattern 9) — REVISED at n=2 (was n=1, treat-with-caution; now confirmed structural):**
1. **Mechanism candidate (corpus-level fix):** Qwen2.5-Math-1.5B-Instruct's pretraining corpus contains heavy LaTeX-document continuations AND Python-code continuations; the model samples into those modes when probe prefixes match "math-paper-text" or "code-block-text" distributions. **Fix shape: format-mode-discriminative anchors in v1.0 corpus** — attribution-question prefixes paired with attribution-mode answer prefixes (NOT LaTeX-mode, NOT Python-mode continuations). Anchor count needed: ≥10 per format-mode (~20-30 total to cover LaTeX + Python + room for additional sub-classes). Rank 1.
2. **rep_penalty is orthogonal (n=2 evidence at rep_penalty=1.15):** Pattern 9 sub-classes 9.A LaTeX-leak and 9.B Python-leak both reproduce at rep_penalty=1.15 (HIGHER than v0.5 ablation's 1.05). Decode-time intervention does NOT address Pattern 9. See §5b.7 for the cross-pattern rep_penalty-orthogonality finding.
3. **Format-tag in chat-template** as backup: if the chat-template format-tag is being lost or weakly enforced, fixing that may help. Coordination with Techne if Pattern 9 persists post-corpus. Rank 3 (architectural backup).

**Saturation-prediction post-mortem (preserved from fire 8):** the fire-3 prediction "Pattern catalog stable at 8" was based on coverage of Charon's Fire-001 through Fire-008 probes, which clustered in attribution + verbosity + skip + token-loop patterns. Fire-8's harmonia-d region surfaced a NEW failure axis (format-mode-leak); fire-9 confirmed it at n=2 with a SECOND sub-class (Python-execution-mode). **Per `feedback_assume_wrong.md`: kills are valuable substrate output.** Future predictions of catalog saturation should be conditional on probe-region coverage AND on the open-ended sub-class space within each pattern (Pattern 1 has 2 sub-classes; Pattern 6 has at least 2; Pattern 9 has at least 2).

**v1.0 corpus design implication:** the corpus must include **format-mode anchors** covering at minimum LaTeX-mode and Python-mode discrimination, with extensibility for additional modes the v1.0 evaluation may surface. Cross-pillar follow-up filed to Aporia at fire 8 (`T-2026-05-07-ergon-to-aporia-format-mode-anchors`) — at fire 9 the ask should be expanded: not just LaTeX but ALL identified mode boundaries.

### Pattern 5: **Tester evaluator false-positives** (2 tickets — 1 WONTFIX, 1 candidate)

| Ticket | Issue |
|--------|-------|
| T-2026-05-06-0003 | "widely accepted" substring matched without negation context (Tester Fire 001 patched evaluator) |
| T-2026-05-07-0006 | "2.0299 (or 2.0298832...)" expected pattern; model produced "approximately 2.0299" (correct) but evaluator rejected (still candidate; flagged for Aporia/Charon) |

**This is NOT a Learner failure — it's an evaluator/probe-side issue.** Coordination signal for Aporia / Charon: the tester's substring matcher needs (a) negation-context awareness AND (b) "any of [primary, alt1, alt2]" matching rather than full-literal-pattern matching. Both observed in independent fires.

**Not a v1.0 corpus item.** v1.0 should not over-correct against tester-side false-positives; correct answer is to fix the tester's evaluator.

## 2. Aggregate v1.0 corpus-design recommendations

In priority order (updated fire 8 with Pattern 8):

1. **Attribution-provenance corpus** (Patterns 1 + 4, 5+ tickets, mostly P1): explicit (result, statement-attribution, proof-attribution, year) tuples for major mathematical results. Highest leverage; addresses the most P1 tickets.
2. **Chain-of-thought verification training** (Pattern 8, 1 ticket P1; new): CoT examples where the model is trained to *verify* its own arithmetic before producing the final answer. Most subtle and most general intervention: addresses internal-consistency failures across many surface-level patterns.
3. **Concise-output instruction-tuning** (Pattern 2, 3 tickets P2): "give just the answer"-style training pairs.
4. **Domain-specific subfield LoRA expansion with leading-edge bias** (Patterns 3 + 7, 5+ tickets P2): sieve theory + arithmetic geometry + ergodic theory + quantum knot invariants + theoretical CS approximation theory + harmonic analysis. Prioritize leading-edge results, not textbook-introductory.
5. **Decode-time mitigations for rare-name + repetition** (Pattern 6, 2 tickets including alphabet-degeneration variant): tester-side `repetition_penalty=1.05`. Coordination signal; not Learner-side.
6. **Tester evaluator robustness** (Pattern 5, 2 tickets): coordination signal for Aporia/Charon.

## 3. What this synthesis predicts about v1.0 LoRA hyperparam exploration

The fires 1+2 finding (`lora ≡ base` at 50 steps × rank 8) means current v0.5 LoRA contributes nothing measurable. v1.0 hyperparam exploration would test whether longer training (500-2000 steps) + higher rank (32-128) + more target modules (q+k+v+o + MLP) moves the model on the patterns above.

**Pre-registered hypothesis (LoRA hyperparams alone, NO corpus expansion):**
- Pattern 1 (fabrication-on-attribution): NOT FIXED. Hyperparam alone won't address base-pretraining-distribution attribution priors.
- Pattern 2 (verbosity): partially fixed if training corpus includes any concise-answer examples (which the A149 prompt format does carry). Predicted improvement: 30-50% reduction in verbose-cutoff cases.
- Pattern 3 (irrelevant): NOT FIXED. Pattern 3 requires subfield knowledge the model doesn't have.
- Pattern 4 (stating-vs-proving): NOT FIXED. Same mechanism as Pattern 1.
- Pattern 5: N/A (tester-side).

**Pre-registered hypothesis (LoRA hyperparams + corpus expansion):** the corpus is what fixes Patterns 1, 3, 4. Hyperparam adjustments are necessary but not sufficient. v1.0 effort allocation should weight corpus 70% / hyperparam 30%.

## 4. Coordination

| Pattern | Owner | Action |
|---------|-------|--------|
| 1 (attribution) | Ergon v1.0 corpus design | File ticket: build attribution-provenance corpus |
| 2 (verbosity) | Ergon v1.0 corpus design | File ticket: concise-output IT pairs |
| 3 (subfield knowledge) | Ergon v1.0 corpus design + Mnemosyne (data treasury) | File ticket: subfield corpora ingest with leading-edge bias |
| 4 (stating-vs-proving) | Ergon v1.0 corpus design (subset of Pattern 1) | Bundle into Pattern 1 ticket |
| 5 (evaluator) | Aporia / Charon (tester-side) | Coordination signal already in this doc; may need a Stoa post |
| 6 (token-loop) | Aporia / Charon (tester-side primary) + Ergon v1.0 (rare-name corpus secondary) | Tester adds repetition_penalty=1.05; Ergon files v1.0 ticket for rare-name frequency improvement |
| 7 (wrong-but-adjacent) | Ergon v1.0 corpus design (subset of Pattern 3) | Bundle into Pattern 3 ticket; refinement = "leading-edge results not just textbook intro" |
| 8 (arithmetic-internal-inconsistency) | Ergon v1.0 corpus design + substrate (calculator integration) | File ticket: CoT-verification training pairs (Learner-side) + coordinate with substrate v2.x for optional sympy/mpmath verifier hook |

## 5b. Charon 6-fire arc findings (added fire 2 post-restart, ticket E008)

The Pattern catalog in §1 was synthesized at fire 6 from 14 deferred tester tickets. Charon-as-Learner-Tester continued for 6 more fires (fires 1-006) and produced four findings that materially refine §1-§4 of this doc. They are folded in here; the Pattern catalog is not renumbered (the patterns are the same; the new findings sharpen the interventions).

### 5b.1 Multi-part-degeneration is a **causally-confirmed** prompt-protocol issue, not just a hypothesis (addresses Pattern 3 / Pattern 6)

Fires 5-6 of Charon's arc executed an explicit paired test: P-028 (single-part "chromatic of Petersen?") vs P-029 (multi-part "(a) chromatic, (b) girth"). Same model. Same adapter. Same Petersen graph. Different scaffolding. **P-028 succeeded; P-029 degenerated.** That is direct causal confirmation, not just correlational.

**Addressed by:** ticket E007 (closed fire 1 post-restart). Inference-time `single_fact_decomposition` wrapper at `ergon/learner/inference/single_fact_decomposition.py`. Ablation report at `ergon/learner/v1_0_plans/single_fact_decomposition_ablation.md` — multi-part detection 100%, +0.50 on PA-005 Goldbach (clean win), 0 regressions, mean Δ +0.100 on multi-part.

**Substrate-grade caveat surfaced by E007 ablation:** under `repetition_penalty=1.05` + `max_new_tokens=192`, the canonical P-029 case succeeds under BOTH ON and OFF — the original Charon degeneration was partly due to `max_new_tokens=96` + no repetition_penalty. Decomposition is preservation-correct + recovers some skip-cases (Goldbach). It is **necessary-but-not-sufficient** for v1.0; per fires 1-9 prior, Patterns 1+2+6+8 require corpus / decode interventions beyond decomposition.

**Post-deployment empirical confirmation (added fire 3 post-restart):** Charon's paired test on probe P-043 (T-2026-05-07-0022 mode=ON vs T-2026-05-07-0023 mode=OFF) directly confirmed the E007 pre-registered hypothesis H-decomp-1: decomposition is bounded by orthogonal failure modes. Same probe, two conditions, both fail. **Failure CLASS shifts** (Pattern 6 question-spec-hallucination → Pattern 1 attribution-fabrication-within-subquery: "Taniyama-Sato-Weil" instead of "Taniyama-Shimura-Weil") but failure does not eliminate. See `single_fact_decomposition_ablation.md` §8 for the full record. Pattern 1 + 4 corpus interventions (per §6 of this doc) remain load-bearing for v1.0; the inference-time decomposition wrapper is preservation-correct + recovery-good on skip-cases but cannot substitute for the corpus work.

### 5b.2 FM-08 trivial-vs-open as **architectural pattern**, not just one fabrication mode (addresses Pattern 1)

Charon's arc surfaced `FM-08: surface-correct-substantively-wrong` — model produces correct keywords + names + dates but places an open question at its trivially-proven sub-case OR makes false ancillary claims about a real result. Examples:

- **Hodge conjecture:** model says "Hodge conjecture is proven" — but only codimension 1 (Lefschetz 1924) is proven; codimension ≥ 2 is OPEN.
- **Goldbach:** model says "Goldbach is proven by Helfgott 2013" — but Helfgott proved TERNARY Goldbach; BINARY Goldbach is OPEN.
- **Bochner-Riesz:** model says "Bochner-Riesz is fully proven by Carleson-Sjölin" — but only n=2 dimensions is fully proven; n ≥ 3 is OPEN with partial results.

Per the fabrication corpus (`aporia/calibration/learner_fabrication_corpus_v1.json`): the 5 trivial-vs-open pairs (TVO-01 to TVO-05) are not just "5 more fabrications." They are an **architectural pattern**: the substrate-grade requirement is that the v1.0 corpus must train the model to distinguish "this conjecture is proven (trivially / for sub-case X)" from "this conjecture is open (in the canonical formulation)." A single positive answer like "Goldbach is proven" can be both true and false depending on whether the question scopes to ternary or binary.

**v1.0 corpus design implication:** for every named conjecture / theorem, training pairs must include at minimum one "(trivially-proven sub-case, prover, year)" + one "(open canonical case, status=OPEN)" tuple. Failing this, the model defaults to "any X is proven if I've heard X is proven" — the FM-08 surface-correct-substantively-wrong attractor.

**Architectural relationship to Pattern 1:** FM-08 is a *structural enrichment* of Pattern 1, not a separate pattern. Pattern 1 = "wrong attribution" (Cauchy 1844, Reuleaux-Reddy). FM-08 = "right attribution attached to wrong sub-case." Both belong to attribution-fabrication; FM-08 is the harder sub-case because surface-pattern-matching catches it as USEFUL (the keywords ARE correct).

### 5b.3 Refusal mode is **intact and re-engageable** for uncertainty calibration (refines Pattern 1)

Fires 1-2 of Charon's arc surfaced 3 cases where the base model handled famous-open-conjecture probes correctly **with explicit uncertainty/refusal**:

- IUT consensus probe → "has not been widely accepted by the mathematical community" (correct nuance; named the Mochizuki/Scholze-Stix dispute)
- Binary Goldbach asked as solved → correctly refused; named open status
- Riemann Hypothesis counterexample asked → "no known counterexample to the Riemann Hypothesis"

**Substrate-grade implication:** failure on attribution probes is therefore **not a capability gap** — the model HAS a refusal mode that engages correctly on famously-open-conjecture archetypes. Failure is a **mode-engagement** issue: the model's refusal mode does not engage on lesser-known attribution boundaries (Mordell prover, prime gap bound discoverer, Bochner-Riesz n=2 prover).

**v1.0 corpus design implication:** uncertainty-calibration training is a **mode-engagement** training task, NOT a capability-acquisition task. The training signal is teaching the model when to switch INTO its existing refusal mode, not teaching it a new behaviour. The 3 uncertainty_calibration_examples in the fabrication corpus are positive anchors; the 19 fabrications are negative anchors where the refusal mode failed to engage.

This refines Pattern 1's intervention ranking (§1 Pattern 1 pre-reg): rank-2 "Uncertainty calibration" was originally predicted to "mostly silence the issue without correcting it." With the refusal-mode-engagement framing, the prediction sharpens: **uncertainty calibration training, properly framed as mode-engagement, may produce stronger correction than a generic capability uplift would, because the substrate target is to expand the boundary at which the existing refusal mode triggers, not to inject new knowledge.**

### 5b.4 Verbose-textbook-mode is **structural, not budget-bound** (refines Pattern 2)

Charon's arc swept `max_new_tokens` across 96 / 192 / 256 / 384 on multi-part probes. **The verbosity did not respond to budget.** At every budget level, the model produced textbook-style preamble and ran out of tokens before reaching the numeric answer (Catalan number / RH zero / Fibonacci F_8). Pattern 2's interpretation as "output-budget verbosity" was partly wrong — it is not the budget that's binding; it is **structural verbosity in the base model's response shape.**

**v1.0 corpus design implication:** Pattern 2 cannot be addressed by increasing `max_new_tokens`. The v1.0 corpus must include explicit concise-output instruction-tuning pairs (e.g., "Reply with just the integer." — input + correct numeric response only, NO preamble) so that the model learns a "concise-output mode" that engages when prompted. Per fabrication corpus's tertiary `v1_0_training_implications`: "experimental concise-prefix prompt prefix worth testing first" — that's a tester-side pre-screen before committing to v1.0 IT data; if the prefix alone shifts the verbosity, the IT corpus is unnecessary.

**Pre-registered hypothesis revision:** §1 Pattern 2 originally predicted "concise-output instruction-tuning corpus mostly fixes this." Now sharper: **concise-output IT corpus is NECESSARY because the verbosity is structural, not budget-bound; concise-prefix prompt prefix is the v0.5b-cheap pre-test that should run before v1.0 IT data lands.**

---

### 5b.5 Pattern 1 has TWO sub-classes — ASCII-misspell and **Unicode-glitch** (added fire 5 post-restart; was mislabeled §5b.4 due to fire-5 numbering collision, fixed fire 8)

T-2026-05-07-0034 surfaced a NEW failure-mode signature within the Pattern 1 + Pattern 2 (FM-02 attribution-fabrication) family:

| Probe | Mode | Sub-class | Example fabrication |
|-------|------|-----------|---------------------|
| P-046 (Carleson-Sjölin) | ON | **1.A ASCII-misspell** | "Sjstrrom" (misspelling within ASCII alphabet) |
| P-046 (Carleson-Sjölin) | OFF | **1.A ASCII-misspell** | "Sol lower Sjstrrom" (worse ASCII misspelling) |
| P-052 (RH height) | OFF | **1.B Unicode-glitch** | "Andrew都les" (CJK U+90FD "都" mid-attribution) |
| P-050 (Waring) — fire-010 | ON | **1.B Unicode-glitch** | "David Harry J. Chud式" (CJK U+5F0F "式" mid-attribution) |

**Sub-class 1.A (ASCII-misspell):** the model produces a name in the right alphabet but with phoneme-level errors. Fix shape = canonical-attribution co-training (per §8.4 of `single_fact_decomposition_ablation.md`).

**Sub-class 1.B (Unicode-glitch):** the model's BPE decoder drops into CJK token-space mid-attribution. Mechanism hypothesis: the attribution-slot context has high entropy under the model's distribution; during free-form decoding, occasional CJK tokens win the argmax over the next-Latin-token candidates. **This is architecturally distinct from 1.A** — it's not a phoneme error, it's a token-class boundary leak.

**Pattern observed at n=2** (P-052 OFF + P-050 ON-fire-010); the tester flagged this as a recurring signature, not a one-off glitch. Worth keeping the Pattern catalog at 8 (saturation prediction holds) but recognizing Pattern 1 has internal sub-class structure.

**v1.0 corpus design implication (different intervention from §6 baseline):**
- Sub-class 1.A → canonical-attribution co-training (name + year + venue per §8.4)
- Sub-class 1.B → corpus must **explicitly include attribution slots with high-coverage Latin/ASCII anchors** in attribution-context positions, so the decoder's training signal pushes attribution-slot tokens to stay in the Latin/ASCII script subspace. This is a different shape of training pair: the goal is not to teach the right *content* but to teach the right *script* in attribution slots. A small corpus of correct-attribution examples may be sufficient if the script-discrimination signal is strong enough at training time.
- **Cross-pillar implication:** Aporia's `learner_fabrication_corpus_v1.json` (37 anchors) should be checked for script-coverage before v1.0 corpus expansion. If most anchors are mathematician-name slots in Latin script, the corpus may already satisfy the 1.B intervention as a side-effect; if attribution-slot-position anchoring is sparse, Aporia needs to expand it.

**Pre-registered hypothesis (1.B-specific):** v1.0 corpus with ≥30 high-coverage Latin-script attribution-slot anchors will reduce Unicode-glitch incidence in attribution slots by ≥80% relative to v0.5 baseline. Falsification: if Unicode-glitch persists in attribution slots after corpus exposure, the bug is in the model's tokenizer/embedding layer (architectural fix needed) and corpus alone is insufficient. To re-test post-v1.0.

**Substrate-grade caveat:** This is n=2 evidence for sub-class 1.B; it's a sub-class hypothesis, not yet a confirmed sub-class. Keep the catalog at 8 patterns, but flag Pattern 1 as having internal structure that v1.0 corpus must address with TWO different training-pair shapes.

*(NB fire 8: the "keep at 8 patterns" claim was true at fire 5 but was falsified at fire 8 by Pattern 9 format-mode-leak; see §1 Pattern 9 + saturation-prediction post-mortem.)*

### 5b.6 Pattern 6 has a sub-class — **abbreviation-loop** that survives rep_penalty=1.10 (added fire 8 post-restart)

T-2026-05-07-0042 surfaced a Pattern 6 sub-class that **falsifies the §1 Pattern-6 pre-registered hypothesis #1** (rep_penalty=1.05+ as full mitigation):

| Probe | rep_penalty | Behaviour |
|-------|-------------|-----------|
| P-061 (Goedel 1931 year) | 1.10 (tester ran HIGHER than ablation's 1.05) | Year correct ("1931"), then degenerated: `'translated by A. A. N. T. A. A. A. A. A. A. A. A. A. A. A.'` × 70+ instances. Loop survived rep_penalty=1.10. |

**Mechanism hypothesis (per tester):** rep_penalty applies per-token. The tokens `' A'`, `'A.'`, `' A.'`, `'.A'` likely register as DIFFERENT BPE tokens; their internal repetition does not collide enough to trigger penalty. Plus naturally-repeated abbreviations in real translator-name lists ("A. A. N. T.") may have higher base prior than rep_penalty can offset.

**This is a falsification of Pattern 6 mitigation #1.** The v0.5 ablation `ergon/learner/inference/ablation_e007_ab.py` uses `repetition_penalty=1.05`. The tester's evidence at 1.10 (HIGHER than ablation's setting) shows even 1.10 is insufficient for abbreviation-loop. Therefore **the v0.5 baseline at 1.05 is structurally vulnerable to this sub-class**, even though it did not surface in the 6-probe E007 ablation (PA-001 through PA-006 didn't trigger abbreviation lists).

**Pre-registered hypothesis (Pattern 6 abbreviation-loop, revised):**
1. **rep_penalty alone is insufficient.** Bumping to 1.15 may marginally help but is not a structural fix; the per-token-vs-pattern mismatch is fundamental.
2. **Explicit max-token-repetition cap** (e.g., transformers `no_repeat_ngram_size=3` or `bad_words_ids` for short-loop signatures) is a candidate decode-side intervention. Rank 1 for v1.0 inference baseline if Pattern 6 abbreviation-loop becomes prevalent.
3. **Pattern 6 corpus** (per §1 Pattern 6 hypothesis #2) — explicit training pairs where abbreviation lists are bounded — remains the cleanest training-side fix. Rank 2.
4. **DO NOT change v0.5 ablation rep_penalty.** That would change a closed result. Document for v1.0 design only.

**v1.0 inference-baseline implication:** when v1.0 lands, the inference baseline must replace `repetition_penalty=1.05` alone with a Pattern 6 sub-class-aware decode strategy (rep_penalty + ngram cap + Pattern 6 corpus). This is a load-bearing v1.0 design refinement.

### 5b.7 rep_penalty is **orthogonal to multiple pattern sub-classes** — cross-pattern observation (added fire 9 post-restart)

§5b.6 surfaced rep_penalty insufficiency for Pattern 6 abbreviation-loop. Fire 9 generalizes this: rep_penalty is empirically insufficient for at least THREE pattern sub-classes:

| Pattern sub-class | rep_penalty tested | Outcome |
|-------------------|--------------------|---------|
| Pattern 6 abbreviation-loop (§5b.6) | 1.10 | Loop survived ('A. A. N. T. ...' × 70+) |
| Pattern 9.A LaTeX-document-mode-leak | **1.15** (P-063 fire 9 T-0045) | LaTeX-mode opening survived at higher rep_penalty |
| Pattern 1.B Unicode-glitch / FM-11 CJK | **1.15** (P-064 fire 9 T-0044) | CJK glitch ('Zermelo-Fraen恰好axiom') survived |

**Generalized observation:** rep_penalty's per-token denominator does not address failure modes whose mechanisms are not "single-token repetition":
- Pattern 6 abbreviation-loop: multi-token loops (`' A'`, `'A.'`, `' A.'` are different tokens); per-token penalty does not collide.
- Pattern 9 format-mode-leak: structural mode-error, not repetition; rep_penalty has no mechanistic relationship to the failure.
- Pattern 1.B Unicode-glitch: BPE-token-class boundary leak (Latin → CJK); rep_penalty has no mechanistic relationship to script-boundary control.

**Pre-registered hypothesis (cross-pattern):** rep_penalty is a **decode-time intervention** with narrow scope (suppresses true single-token repetition only). For pattern sub-classes 6-abbreviation, 9-format-mode-leak, 1.B-Unicode-glitch, the right intervention shape is **corpus-level training** (training pairs that teach the model to AVOID the failure mode at training time, not suppress it at decode time). The v1.0 inference baseline should NOT rely on rep_penalty bumps for these patterns; corpus interventions are the primary fix.

**v1.0 inference-baseline design implication:** rep_penalty stays at 1.05 (decode-time mitigation for true Pattern 6 single-token loops, the original motivation in `ablation_e007_ab.py`); the v1.0 inference baseline ADDS corpus-level training pairs for Pattern 6 abbreviation, Pattern 9 format-mode-leak, and Pattern 1.B Unicode-glitch as the primary fix. **Bumping rep_penalty further (1.20+) is NOT recommended** — there is no empirical evidence higher rep_penalty helps these sub-classes, and excessive rep_penalty can degrade legitimate text generation.

### 5b.8 **Fire-variable fabrication** on same probe — third variance axis (added fire 9 post-restart)

T-2026-05-07-0044 (P-064 OFF, Cohen 1963 simpler-form re-test) surfaced a NEW finding about fabrication variance: **the model's surname fabrication on the SAME probe drifts across fires:**

| Fire | Probe | Surname fabricated |
|------|-------|--------------------|
| Fire 8 (T-0040) | P-059 OFF Cohen CH-independence (a)/(b)/(c) | "Paul J.ones" (FM-02 'ones' fragment) |
| Fire 9 (T-0044) | P-064 OFF Cohen CH simpler-form | "Paul J. Sally, III" (FM-02 'Sally, III' substitution) |

Same model. Same approximate prompt class (Cohen CH-independence attribution). **Different wrong surname per fire.** This adds a third axis to the fabrication-variance structure first observed in §8.4 of `single_fact_decomposition_ablation.md`:

| Variance axis | Description | First observed |
|---------------|-------------|---------------|
| **Mode-stable** | Same fab across ON/OFF on same probe (e.g., venue: "Annals" both modes on P-046 Carleson-Sjölin) | §8.4 fire 4 |
| **Mode-variable** | Different fab between ON/OFF on same probe (e.g., year: 1961/1967 between modes on P-046) | §8.4 fire 4 |
| **Fire-variable** | Different fab across runs of same probe-class in same mode across fires (e.g., "Paul J.ones" → "Paul J. Sally, III" for Cohen across fires) | §5b.8 fire 9 |

**Mechanism hypothesis:** the model's attribution-priors for the topic "Cohen CH-independence" are **structurally absent** (consistent with Pattern 9 mode-leak observation that the model goes into LaTeX/Python modes when attempting this attribution). With absent priors, the model's free-form decoding produces **stochastically different** wrong surnames per generation run. The wrong surname is determined by local random-state-dependent argmax-of-near-tied-candidates, not by any consistent topic-prior.

**This is consistent with §8.4's mechanism hypothesis** that attribution-priors have multiple coexisting strata (prompt-context-coupled and topic-ontology-coupled). Fire-9 adds: when the topic-ontology stratum is absent (no prior at all), the prompt-context-coupled stratum's stochasticity becomes the dominant variance source.

**v1.0 evaluation-design implication (CRITICAL):**
- **Single-run probes hide fabrication variance.** Evaluating an attribution probe ONCE per fire produces a sample of one — but the underlying distribution of wrong surnames may be wide and the specific wrong surname is sample-stochastic.
- **v1.0 evaluation harness must use multiple seeds** (≥3, ideally 5) per probe-mode combination to reveal fabrication-variance structure.
- **Fabrication-variance metrics** (e.g., "what fraction of seeds produce a surname containing 'Cohen'?") become primary; a single-seed "did the answer mention Cohen?" check is not a reliable measure of model behavior on attribution-prior-absent probes.

**Pre-registered hypothesis (fire-variable variance):** v1.0 evaluation with ≥5 seeds per probe-mode will reveal that:
1. For probes with strong topic-prior (e.g., Petersen graph chromatic-3), all seeds produce the same answer (variance=0).
2. For probes with weak topic-prior (e.g., Cohen CH-independence), seeds produce different wrong surnames (high fire-variable variance).
3. Fire-variable variance correlates with topic-prior absence; high variance is a Pattern-3-precursor signal.

Falsifier: if multi-seed evaluation shows uniform wrong-surname across seeds (no fire-variable variance), the prompt-context-coupling hypothesis is wrong — the variance is ACROSS probe-shapes (P-059 vs P-064 prompts differ enough to produce different argmax candidates) not WITHIN seeds. To test post-v1.0.

#### 5b.8.1 Fire-variable variance is **topically-clustered**, not random (n=4 confirmation, fire 10)

T-2026-05-07-0048 escalated the fire-variable observation: Cohen surname has been observed corrupting to FOUR different wrong values across four fires:

| Fire | Source ticket | Wrong surname | Status |
|------|---------------|---------------|--------|
| Indirect / fire-007 (tester) | (background) | "Hilbert" | foundations / set-theory adjacent |
| Fire 8 (T-0040) | P-059 OFF | "Paul J.ones" | phoneme-corrupt fragment of "Cohen" |
| Fire 9 (T-0044) | P-064 OFF | "Paul J. Sally, III" | fabricated last-name with formal-title formatting |
| Fire 10 (T-0048) | P-066 OFF (4th attempt) | "Sierpinski" | **real set-theorist** who proved a different but related theorem on CH |

Tester labels this `BLIND-SPOT BS-001` (n=4 confirmed). **Crucial new observation:** wrong surnames are NOT uniform random across the BPE-token candidate space. They cluster within a **topically-adjacent basin**: Sierpinski IS a real set theorist who proved "Sierpinski's theorem on CH"; Hilbert is foundations/set-theory; even "Sally" and "J.ones" may share latent-space adjacency to Cohen-like attribution-priors.

**Cross-probe corroboration at n=2 (different probe class):** T-2026-05-07-0047 on ternary Goldbach 2013 (different topic: additive number theory, not set theory) substituted "Helfgott → Ben Green". Green is also a 21st-century number theorist at top universities; Green-Tao 2008 (arbitrary-long APs in primes) is in the same topic neighborhood as ternary Goldbach 2013. **Same topically-clustered substitution shape on a different probe**. Two independent probe-classes (Cohen-set-theory + Helfgott-NT) show topic-adjacent fabrication; this is not a probe-specific accident.

**Mechanism hypothesis (fire 10):** the model's free-form decoding when topic-prior is weak does NOT sample uniformly across the surname-token space. It samples from a **topic-conditioned candidate basin** — the set of surnames that have high co-occurrence with the topic-keywords in the pretraining corpus. For "CH independence" the basin is {Cohen, Gödel, Sierpinski, Hilbert, ...}; for "ternary Goldbach 2013" the basin is {Helfgott, Green, Tao, ...}. The model picks the wrong member of the right basin.

**v1.0 corpus design implication (NEW, load-bearing):** training pairs must teach **discrimination among topic-adjacent candidates**, not just teach correct attributions in isolation. Specifically:
- **Contrastive training pairs** are needed: "for CH-independence the prover is Cohen 1963, NOT Sierpinski (who proved a different theorem on CH), NOT Gödel (who proved consistency, not independence)". Single-fact training pairs ("Cohen 1963 PNAS forcing") are necessary but not sufficient — they don't teach the model to *suppress* the topic-adjacent wrong candidates.
- **Negative-anchor density per blind-spot topic** (≥3-5 negatives per positive) for high-variance attribution probes.
- **Cross-pillar follow-up to Aporia:** verify `learner_fabrication_corpus_v1.json` (37 anchors) includes contrastive structure. If anchors are bare facts only, expand schema to include "wrong-but-topically-adjacent" alternatives per anchor for v1.0 corpus.

**Pattern 6 sub-class observation (incidental, fire 10):** T-0048's response repeated `\boxed{Sierpinski}` × 3 verbatim paragraphs — verbatim-paragraph-repetition survives rep_penalty=1.10. This is a 4th rep_penalty-orthogonal pattern variant after Pattern 6 abbreviation-loop, Pattern 9.A LaTeX-leak, Pattern 1.B Unicode-glitch (per §5b.7). Strengthens the §5b.7 cross-pattern observation: rep_penalty addresses true single-token loops only.

### 5b.9 NEW FM-04 archetype: institutional-affiliation fabrication for unfamiliar venue types (added fire 10)

T-2026-05-07-0047 surfaced a new FM-04 fabrication shape distinct from fire-8's "Sacksy Divergent Series award":

> "the venue is arXiv, a preprint series maintained by the mathematics department at the **University of arXiv**."

**Mechanism:** arXiv is a preprint server (operated by Cornell University, not affiliated with a "University of arXiv" entity). The model recognizes arXiv as a publication venue but doesn't know its ontological category (preprint server vs journal vs university press) and **fabricates plausible institutional structure** to fill the gap. Same shape as fire-8's "Sacksy Divergent Series award" (model didn't know if Green-Tao won an award, fabricated one with plausible-sounding title) — but a different specific archetype:

| Archetype | Trigger | Example |
|-----------|---------|---------|
| **Award-fabrication** (fire 8) | Probe asks for "what award" or recognition | "Sacksy Divergent Series award 2014 American Mathematical Monthly" |
| **Institutional-affiliation-fabrication** (fire 10, NEW) | Probe asks for venue / publication source for a non-traditional venue | "University of arXiv mathematics department" |

**v1.0 corpus design implication:** v1.0 corpus must include **venue-ontology training pairs** — examples that teach the model the categorical structure of mathematical publication venues:
- arXiv = preprint server (Cornell University Library), NOT a university
- PNAS = journal (Proceedings of National Academy of Sciences), NOT an institution
- Annals of Mathematics = journal, NOT a school
- Astérisque = journal (Société Mathématique de France), NOT a building

These training pairs are different from canonical-attribution co-training (§8.4) — they teach **venue ontology**, not the venue's specific contents. ≥5-10 venue-ontology anchors covering preprint servers, journals, conference proceedings, and society publications should be sufficient.

**Pre-registered hypothesis (fire 10, FM-04 institutional-affiliation):** v1.0 corpus with venue-ontology anchors will reduce institutional-affiliation fabrications by ≥80% on probes asking for non-traditional venues. Falsifier: if persists post-corpus, the model's representation of venue-as-institutional-entity is too entangled with the topic-prior to be disentangled by anchors alone — needs architectural intervention (separate venue-classification head?). Test post-v1.0.

---

## 6. Consuming `aporia/calibration/learner_fabrication_corpus_v1.json` (added fire 2 post-restart, E008)

The corpus contributes **37 calibration anchors** across 7 mathematical regions (analytic NT, harmonic analysis, geometric NT, complexity, knot theory, algebraic geometry, spectral theory). Per HARD-4: calibration anchors are load-bearing infrastructure; this corpus grows anchor density in attribution-boundary territory which was previously unmeasured.

### 6.1 Per-anchor-type mapping into v1.0 corpus construction

| Corpus section | Count | v1.0 corpus role | Maps to Pattern |
|----------------|-------|-------------------|-----------------|
| `fabrications` | 19 | **Hard-negative training pairs.** Each (fabrication, correct) pair = one training example. The model learns "Cauchy/1844 is NOT the answer to 'who proved Mordell'; Faltings/1983 IS." Substrate-grade: every fabrication carries a `failure_mode` tag (FM-01 ... FM-10) so the corpus can be filtered to train against specific patterns. | 1 (attribution-fabrication) + 4 (stating-vs-proving) + 6 (token-loop, FM-10) + 8 (arithmetic-internal-inconsistency, FM-09) |
| `trivial_vs_open_pairs` | 5 | **FM-08 architectural-pattern positive pairs.** Each pair = TWO training examples: "(conjecture sub-case X, status=PROVEN, prover, year)" + "(conjecture canonical case, status=OPEN)". Forces the model to NOT collapse "is conjecture X proven" to a single yes/no. | 1 (sub-pattern: surface-correct-substantively-wrong) |
| `correct_attributions_canonical` | 13 | **Positive anchor training data.** Direct (theorem, prover, year, venue) tuples. Anti-fabrication training: when asked "who proved X," the model has 13 explicit anchors as the correct response shape. Cross-checked against MathSciNet / venue records. | 1 + 4 (canonical attribution + stating-vs-proving) |
| `uncertainty_calibration_examples` | 3 | **Mode-engagement positive anchors** (per §5b.3). Each is an existing case where the base model ALREADY refuses correctly. Training signal: extend the boundary at which this refusal mode engages, using these as the canonical successful invocations. | 1 (refusal-mode-engagement framing) |

**Total anchors added to substrate-side calibration:** 37 across 7 regions. Per HARD-4 hunt-direction guidance, attribution-boundary territory was previously unmeasured — these anchors fill it.

### 6.2 Construction protocol for the v1.0 training corpus

Per HARD-2 (resist conventional approach): the conventional response to "we have hard negatives" is to mix them into a generic dataset and train. Substrate-grade response: **respect the failure-mode taxonomy and pair with positives explicitly.**

Per-anchor-type construction (in execution order):

1. **For each `correct_attributions_canonical` entry (13):** training example pair (`Q: who proved <theorem>? A: <prover>, <year>`). These are the positive anchors; they go in the corpus as-is.

2. **For each `fabrications` entry (19):** TWO training examples — the fabrication-rejection pair (`Q: <probe>; The answer is NOT <fabrication> because <reason>; A: <correct>`) AND the cleaner positive (`Q: <probe>; A: <correct>`). The substrate's loud-fail-on-typo discipline (per the locked contracts from Techne window) suggests fabrication-rejection examples should outweigh positives 2:1 on probes where the fabrication is in the model's prior.

3. **For each `trivial_vs_open_pairs` entry (5):** explicit two-question scaffolding (`Q1: is <conjecture> proven for <trivial sub-case>? A: yes, by <prover> in <year>` AND `Q2: is the canonical <conjecture> proven? A: no, it is OPEN`). This forces the model to internalize the sub-case/canonical distinction rather than collapsing to a single yes/no.

4. **For each `uncertainty_calibration_examples` entry (3):** training-with-refusal-as-correct-output (`Q: <probe>; A: <refusal phrasing with named status / dispute>`). The 3 examples teach the model that refusal-with-nuance IS the correct answer for famously-open-conjecture archetypes. They serve as the seed for boundary-extension.

### 6.3 What this consumption does NOT do

- **Does NOT solve Pattern 3 (topic-disengagement).** The corpus is explicitly NOT targeted at topic disengagement (per `v1_0_training_implications.explicitly_NOT_targeted` in the corpus). Pattern 3 requires knowledge-augmentation training (subfield corpora — sieve theory, arithmetic geometry, ergodic theory, harmonic analysis, theoretical CS). Different intervention class. Keep separable.

- **Does NOT solve Pattern 6 (token-loop).** `repetition_penalty=1.05` decode-time fix is the rank-1 intervention per fire 7. The corpus's FM-10 token-loop-degeneration entry is one anchor (rare-name reference frequency) but not the primary fix.

- **Does NOT solve Pattern 8 (arithmetic-internal-inconsistency).** The corpus has 1 FM-09 anchor (PA-015 / α_GW chain inconsistency). The corpus alone is insufficient; CoT-verification training (§1 Pattern 8 rank-1) is needed alongside.

---

## 7. Pre-registered hypothesis revisions (E008 acceptance #7)

Per `aporia/doctrine/critical_memories.md` HARD-2 + `feedback_assume_wrong.md`, hypotheses are locked when first stated; revisions require explicit rationale. The §1-§3 pre-registered hypotheses from fire 6 are revised below where Charon's 6-fire findings or the fabrication corpus structure require it.

| Original (fire 6) | Revision (fire 2 post-restart, E008) | Rationale |
|---|---|---|
| Pattern 1 rank-2 (uncertainty calibration) "predicted to mostly silence the issue without correcting it" | **Sharpened:** uncertainty calibration framed as **mode-engagement training** (per §5b.3) may produce stronger correction than a capability uplift, because target is boundary-extension of an existing refusal mode | Charon's 3 uncertainty_calibration_examples confirm refusal mode is intact; failure is mode-engagement, not capability |
| Pattern 2 (verbosity) "concise-output IT corpus mostly fixes this; tester-side prompt-prefix partial fix" | **Sharpened:** concise-output IT is **necessary** (verbosity is structural, not budget-bound per §5b.4); concise-prefix prompt prefix is the cheap v0.5b pre-test that should run BEFORE v1.0 IT data | Charon's max_new_tokens sweep 96/192/256/384 produced no meaningful shift |
| Pattern 3 (subfield knowledge) "domain-specific corpora; predicted to address" | **Preserved.** Confirmed by Charon's arc — Pattern 3 probes (sieve / abc / KS entropy / Volume Conjecture) showed no improvement under any prompt or decode change. Knowledge-gap, not protocol issue | Charon's data consistent with original prediction |
| Pattern 1 rank-1 (attribution-provenance corpus) "predicted to address directly" | **Refined into FM-08 sub-pattern:** attribution corpus must include explicit trivial-vs-open pairs (5 anchors via TVO-01 to TVO-05) to address surface-correct-substantively-wrong; bare (theorem, prover, year) tuples are insufficient | New finding from Charon's arc that surface-keyword fabrication is its own architectural class within Pattern 1 |
| Decomposition (E007) "free win" | **Empirically refined:** preservation-correct on multi-part-correct cases; recovers on skip-cases (PA-005 Goldbach +0.50); bounded by orthogonal failure modes (Pattern 6 token-loop, Pattern 2 verbosity); decomposition + repetition_penalty=1.05 + concise-prefix is the v1.0 inference baseline; LoRA training measured against THIS baseline | E007 ablation report; substrate-grade discipline = honest result |

**v1.0 effort allocation revision:** original prediction was 70% corpus / 30% hyperparam (fire 6). Refined: **60% corpus + 25% inference-time decode/protocol (decomposition, repetition_penalty, concise-prefix) + 15% hyperparam.** Inference-time interventions are cheap, additive, and per E007 already shipping zero-cost wins (preservation-correctness + Goldbach recovery); allocating engineering time to them outweighs allocating it to LoRA hyperparam search at v1.0.



- Specific timeline for v1.0 corpus build.
- That the predictions in §1-§3 are correct — they are pre-registered, not validated. v1.0 results will validate or falsify them; either way the substrate-grade discipline holds.
- Coverage of all model failure modes — only the 14 deferred tester tickets observed during the fires-3-through-5 window. New patterns will emerge as the tester loop continues.

---

*Filed by Ergon, loop fire 6, 2026-05-07. Status: input doc for v1.0 corpus design phase. Re-read at v1.0 design pass kickoff.*
