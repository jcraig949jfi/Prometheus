# v1.0 Plan — Tester Findings Consolidated (Corpus-Design Input)

**Filed by:** Ergon (loop fire 6, 2026-05-07)
**Inputs:** 14 BLOCKED-DEFERRED-V1.0 tester tickets + 1 WONTFIX-FALSE-POSITIVE + tester fire log entries (Tester Fires 001 + 002 + 003+)
**Status:** Synthesis only. No code changes. v1.0 corpus design will read this; v1.0 implementation begins post-pitch when phase opens.

---

## 0. Why this exists

Across fires 3, 4, 5 the producer-side loop bulk-deferred 14 tester tickets to v1.0 because they all reported failures that the v0.5 / v0.5b LoRA scope cannot address (fires 1+2 substrate-grade finding: at 50 steps × LoRA rank 8, the adapter is bit-identical to base Qwen2.5-Math-1.5B-Instruct; free-form math probe failures reflect base behaviour). Defering them ticket-by-ticket loses the meta-pattern. This doc consolidates them into a structured v1.0 corpus-design input with **pre-registered hypotheses** for which interventions would most likely address each pattern.

Per `feedback_assume_wrong.md`: pre-registration lets future-me detect post-hoc rationalization. If v1.0 fixes Pattern 1 with intervention X but I claim "I always thought X would work" — the pre-registered prediction here will say otherwise (or won't).

## 1. Five failure-mode patterns extracted from 14 tickets

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

### Pattern 5: **Tester evaluator false-positives** (2 tickets — 1 WONTFIX, 1 candidate)

| Ticket | Issue |
|--------|-------|
| T-2026-05-06-0003 | "widely accepted" substring matched without negation context (Tester Fire 001 patched evaluator) |
| T-2026-05-07-0006 | "2.0299 (or 2.0298832...)" expected pattern; model produced "approximately 2.0299" (correct) but evaluator rejected (still candidate; flagged for Aporia/Charon) |

**This is NOT a Learner failure — it's an evaluator/probe-side issue.** Coordination signal for Aporia / Charon: the tester's substring matcher needs (a) negation-context awareness AND (b) "any of [primary, alt1, alt2]" matching rather than full-literal-pattern matching. Both observed in independent fires.

**Not a v1.0 corpus item.** v1.0 should not over-correct against tester-side false-positives; correct answer is to fix the tester's evaluator.

## 2. Aggregate v1.0 corpus-design recommendations

In priority order:

1. **Attribution-provenance corpus** (Patterns 1 + 4, 5 tickets, mostly P1): explicit (result, statement-attribution, proof-attribution, year) tuples for major mathematical results. Highest leverage; addresses the most P1 tickets.
2. **Concise-output instruction-tuning** (Pattern 2, 3 tickets P2): "give just the answer"-style training pairs to suppress verbose preamble.
3. **Domain-specific subfield LoRA expansion** (Pattern 3, 4 tickets P2): sieve theory + arithmetic geometry + ergodic theory + quantum knot invariants corpora. Higher cost; lower priority.
4. **Tester evaluator robustness** (Pattern 5, 2 tickets): coordination ticket for Aporia/Charon; not a Learner-side fix.

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
| 3 (subfield knowledge) | Ergon v1.0 corpus design + Mnemosyne (data treasury) | File ticket: subfield corpora ingest |
| 4 (stating-vs-proving) | Ergon v1.0 corpus design (subset of Pattern 1) | Bundle into Pattern 1 ticket |
| 5 (evaluator) | Aporia / Charon (tester-side) | Coordination signal already in this doc; may need a Stoa post |

## 5. What this doc does NOT promise

- Specific timeline for v1.0 corpus build.
- That the predictions in §1-§3 are correct — they are pre-registered, not validated. v1.0 results will validate or falsify them; either way the substrate-grade discipline holds.
- Coverage of all model failure modes — only the 14 deferred tester tickets observed during the fires-3-through-5 window. New patterns will emerge as the tester loop continues.

---

*Filed by Ergon, loop fire 6, 2026-05-07. Status: input doc for v1.0 corpus design phase. Re-read at v1.0 design pass kickoff.*
