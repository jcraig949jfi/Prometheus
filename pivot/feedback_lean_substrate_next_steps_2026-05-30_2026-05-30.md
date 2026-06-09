# Cross-pollination feedback — `aporia\doctrine\lean_substrate_next_steps_2026-05-30.md`

- generated_at: 2026-05-30T08:32:34.568168+00:00
- generated_by: Moros (charon/agents/moros/daemon.py)
- fanout_n_attempted: 3
- fanout_n_ok: 2
- providers_consulted: ['GitHub Models gpt-4o-mini', 'NVIDIA Nemotron-120B']
- artifact_size_bytes: 16109

## Critique 1 — GitHub Models gpt-4o-mini

1. **Structural Defect - Justification of Assumptions**: The document states, "the `#check` route is one Python function I can write today, and its parse-fragility is bounded," yet it does not provide empirical evidence or references to support the assertion that the parse-fragility is indeed bounded. This assumption appears to be critical for the success of Stand 1, yet lacks justification.

2. **Missing Citations or Evidence**: The claim, "the Lean-side helper survives as a fallback if `#check` parsing turns out to be load-bearing brittle," is made without any citations or examples of prior experiences that demonstrate the brittleness of similar parsing methods. This absence of evidence undermines the reliability of the proposed fallback strategy.

3. **Premature Closure of Alternative Framings**: The author dismisses the "Lean-side helper module exposing a custom `#extract_statement` command" as a viable alternative, stating, "that route is cleaner long-term." However, this dismissal lacks a thorough comparative analysis of the potential benefits of this route versus the selected approach. Other methods may yield more robust or scalable solutions that should be explored.

4. **Silent Collapsing of Terms - HARD-5 Violation**: The term "self-reference" in "Closure by `exact <self_name>` would be false success" is not defined or explored in detail. This lack of clarity around what constitutes self-reference in this context could lead to misunderstandings and misinterpretations of the guard's functionality.

5. **Overclaim Risk - Language vs. Evidence**: The statement, "If closure rate doesn't change, the guard is unnecessary on this corpus," implies a definitive conclusion about the necessity of the guard based solely on closure rates from limited tests. This overreaching claim does not account for other potential confounding factors that could influence closure rates and should be more cautiously framed.

6. **Assumption of Stability - Unsupported Claims**: The author states, "lean-repl emits messages in a stable format that hasn't shifted across the v4.x window." This assertion about stability lacks supporting evidence or citations to previous versions, creating a risk that future changes in Lean may invalidate this assumption.

7. **Lack of Clear Metrics for Success**: The phrase, "if 50 walk_1 theorems still take >30 min on warm pool, the bottleneck is somewhere else," presents a vague metric for success without specifying what constitutes an acceptable performance threshold for the session pool. Clear, quantifiable metrics are necessary to assess the performance accurately.

8. **Ambiguity in Measurement Matrix**: The measurement matrix states, "the interesting comparisons are PRM_v0-on-pool-N vs unscored-pool-N for each N." However, this comparison lacks clarity on what defines "interesting," and it does not specify how the results will be interpreted. Without clear criteria for evaluation, the findings may lead to ambiguous or inconclusive results.

## Critique 2 — NVIDIA Nemotron-120B

We need to produce 5-8 bullet points, each a concrete critique with a quote or paraphrase of the line the critique targets. Focus on structural defects, missing citations, alternative framings prematurely closed off, HARD-5 violations (terms or coordinates silently collapsed), overclaim risk.

We must not produce summary praise. Provide adversarial critique.

Let's read the artifact and identify issues.

Potential issues:

- Stand 1: assumption that #check introspection yields stable format across v4.x window; no citation or evidence. Also assumption that parse-fragility bounded; no justification.

- Kernel validator: assumption that validation via example : <extracted> := by exact @<full_name> catches all extraction errors; but there could be false positives if the extracted type is definitionally equal but not syntactically same? Might be okay.

- Stand 1.5: forbidding self-reference by checking candidate text contains full_name or known aliases; but there could be indirect self-reference via other definitions that unfold to same theorem; not covered.

- Stand 2: assumption that cold-import cost is 5 min on this machine; no citation; also assumption that session pool gives 50x speedup; no measurement.

- Latency histogram: assumption that silent slow-worker poisoning is the most likely failure mode; no evidence.

- Stand 3: claim that PRM v0 alone hit 47% (+22pp over random) – no citation to source; also claim that naive combinations worse than random; no citation.

- Measurement matrix: assumption that oracle step-local closure rate >50% indicates substrate measures proof search; but could be due to other factors.

- Stand 4: deferring other provers until Walk-Z validates; but could be premature closure of alternative framings: maybe testing with other provers early could reveal substrate flaws.

- Stand 5: watchdog only after first crash; assumption that SessionCrashed surface area small; no evidence.

- Hard-priority stands: claim of falsifiability but many stands rely on internal metrics that may not be observable.

- HARD-5 violations: terms like "behaviour delta", "load-bearing", "substrate", "scorer", "Walk-Z" may be silently collapsed; need to see if they are defined elsewhere. In this doc, they are used without definition; could be considered HARD-5.

- Overclaim risk: statements like "Pool-first is two days of work that buy us 50× speedup on the actually-interesting measurement." Overclaim without evidence.

- Also claim that "The Lean repl issue tracker has a documented case of 'REPL accepts incorrect proofs' via self-reference" – no citation.

- Also claim that "per feedback_no_naive_score_combination (2026-05-26), naive combinations of heads trained on heterogeneous candidate populations were worse than random; PRM v0 alone hit 47% (+22pp over random)" – no citation.

- Also claim that "The frontier review correctly identifies this as load-bearing for SMT adapters." – referencing unknown.

We need to produce 5-8 bullet points. Let's pick the strongest.

We'll produce maybe 6 bullet points.

Each bullet: quote or paraphrase, then critique.

Let's craft.

Bullet 1: Target Stand 1 assumption about #check stability.

Quote: "the #check route is one Python function I can write today, and its parse-fragility is bounded (lean-repl emits messages in a stable format that hasn't shifted across the v4.x window)."

Critique: No evidence provided; assumes stability without citation; potential HARD-5 collapse of "stable format".

Bullet 2: Target Stand 1.5 self-reference guard.

Quote: "the engine rejects any candidate tactic whose text contains that name (or known aliases)."

Critique: Only blocks direct textual self-reference; misses indirect self-reference via unfolding or aliasing; alternative framing (semantic equivalence check) prematurely closed off.

Bullet 3: Target Stand 2 speedup claim.

Quote: "Pool-first is two days of work that buy us 50× speedup on the actually-interesting measurement."

Critique: Overclaim; no measurement or citation; assumes linear scaling; ignores variance; HARD-5 collapse of "5

## Critique 3 — <failed_call_2>

_(cascade call 3 failed; provider returned no usable text)_

---

*v0.2 multi-provider cross-pollination per CHARTER §6. Convergence analysis in companion meta_analysis_*.md.*