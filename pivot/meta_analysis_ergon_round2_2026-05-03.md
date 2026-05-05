# Meta-Analysis: Round 2 External Review of Ergon Learner Proposal v1

**Date:** 2026-05-03 (afternoon)
**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Subject:** Round 2 external adversarial review of [`pivot/ergon_learner_proposal_v1.md`](ergon_learner_proposal_v1.md). Reviewer was given v1; some critiques were already addressed in v2 (commit 73718700).
**Companions:**
- [`pivot/feedback_ergon_review_round2_2026-05-03.md`](feedback_ergon_review_round2_2026-05-03.md) — verbatim capture
- [`pivot/ergon_learner_proposal_v3.md`](ergon_learner_proposal_v3.md) — v3 incorporating round-2 revisions
- [`pivot/meta_analysis_ergon_review_2026-05-03.md`](meta_analysis_ergon_review_2026-05-03.md) — round-1 meta-analysis (morning)
- [`pivot/feedback_ergon_proposal_review_2026-05-03.md`](feedback_ergon_proposal_review_2026-05-03.md) — round-1 verbatim

---

## Frame: convergence vs. independence across reviewers

Round 1 (morning, single Claude session, bullet-heavy markdown style) produced three load-bearing critiques: specification gaming, fitness predictor as gatekeeper, ontology bias in features.

Round 2 (afternoon, different reviewer — numbered sections, formal tone) addresses v1 directly via the §12 open questions Q1–Q3 and produces three different load-bearing critiques: shared semantic prior, MAP-Elites axis correlation, Task A↔B echo chamber.

**Two reviewers. Six critiques. Zero overlap.** That is itself a finding. The critiques are independent and load-bearing — both reviewers identified real gaps that v1 didn't address. Round 2's gaps are partially-but-not-fully addressed in v2:

| Round 2 critique | v2 status | v3 work needed |
|---|---|---|
| (1B) Shared semantic prior | Partial — v2's six operator classes diversify the proposer pool but don't address LLM-prior contamination at the policy layer | Yes — anti-prior operator + coverage-pressure reweighting + periodic prior-detox |
| (2B) MAP-Elites axes 1, 2, 4 will correlate | Not addressed | Yes — swap two structural axes for output-space axes |
| (3B) Task A↔B echo chamber | Partial — v2's no-pruning sweeps + predictor_recall catch this *after* it happens | Yes — disjoint training partitions + periodic from-scratch retraining + independence assertion |

So v3 is warranted. Three additional load-bearing revisions.

## Triage of round-2 critiques

### (1B) LOAD-BEARING — high-priority revision

**The shared semantic prior at the corpus layer.**

Reviewer's framing:
> While your *action spaces* (Lean tactics vs. typed DAG compositions) are uncorrelated, your *semantic priors* are deeply entangled. … The neural policy will still steer the evolutionary engine toward the same well-trodden mathematical attractors Silver is exploring, just expressed through a different modality.

This is a sharper version of v1's Q1 ("Is the action space genuinely uncorrelated with Silver's likely Lean-tactic action space, or is the prior shared at a deeper level…?"). The reviewer's answer: yes, the prior is shared at the *training corpus* layer, and the action-space asymmetry doesn't help.

The critique applies specifically to Tasks A (mutation policy) and C (conjecture generation) of the neural policy head. Task B (fitness predictor) is less affected because it's a discriminator, not a generator — it learns from substrate verdicts, not from corpus statistics.

v2 partially mitigated by adding `structured_null` as a sixth operator class (gives non-LLM proposals a first-class architectural slot). v3 needs more:

- **Anti-prior operator class** — explicitly construct mutations that violate corpus-derived patterns. For polynomial generation, sample coefficient distributions deliberately uncorrelated with Mathlib polynomial frequency statistics. Lineage tag: `anti_prior`.
- **Coverage-pressure reweighting in cell selection** — when the MAP-Elites cell-selection policy samples a cell already heavily filled by `neural` or `external_llm` operators, downweight; when sampling a cell only filled by `structural` / `symbolic` / `uniform` / `structured_null` / `anti_prior`, upweight. Forces the search away from LLM-prior attractors.
- **Periodic prior detox** — every K iterations (default K=20), freeze the neural policy weights and run only `structural` / `symbolic` / `uniform` / `structured_null` / `anti_prior` for M=500 episodes. Measure archive coverage delta. If non-LLM operators discover new cells the LLM-augmented run hadn't filled, the LLM prior is constraining; rebalance operator weights toward non-LLM in the next cycle.
- **Honest acknowledgment in §11**: even with mitigations, the neural policy's discovery contribution may saturate at the LLM-prior boundary. The substrate's value at v1.0+ may come primarily from non-LLM operator classes; the neural policy's role may be optimizing within prior-shaped subdomains rather than expanding the discovery surface.

Promotes as Tier-3 candidate symbol: `PATTERN_SHARED_PRIOR_AT_TRAINING_LAYER`.

### (2B) LOAD-BEARING — high-priority revision

**MAP-Elites axes 1, 2, 4 will correlate; the descriptor space collapses.**

Reviewer's framing:
> DAG depth (Axis 1), DAG width (Axis 2), and Total cost tier (Axis 4) will strongly correlate during active mutation. A larger, wider DAG will naturally hit a higher cost tier. If these three axes move in lockstep, your effective search space collapses from five dimensions to three.

This is sharp and correct. I should have caught this. The Phase 2b sanity check (max cross-correlation < 0.6) was on synthetic optimization landscapes where width / depth / cost vary independently because the landscape generator doesn't couple them. In a *typed-composition mutation environment*, depth and width and cost are mechanically coupled — a DAG of depth 8 and width 5 is structurally bigger and structurally costlier.

The reviewer's specific suggestion is the right fix: swap structural axes for output-space axes. Forces diversity in *what the genome produces*, not just *how it's structured*.

v3 revised 5-axis descriptor:
1. **DAG depth** (structural — kept; correlated but useful as one structural axis)
2. **Equivalence-class entropy** (categorical — kept; not strongly correlated with size)
3. **Output-type signature** (categorical — kept)
4. **Output magnitude bucket** (NEW — log-binned over numerical output magnitude; for non-numerical outputs, surrogate via coefficient norm or analogue)
5. **Output canonical-form distance** (NEW — distance to nearest catalog entry under canonical-form transformation, quantile-binned)

Removed: DAG width, Cost tier (both correlated with depth).

This better separates "what was searched" (axes 1–3) from "what was found" (axes 4–5). The archive forces diversity in output space rather than just composition space.

A check on this: when the four-counts pilot from §6.2 of `discovery_via_rediscovery.md` runs at 10K episodes, the per-axis fill rate should be measured. If depth/equiv-entropy/output-type/output-magnitude/output-distance independently span their quantile bins, the archive is not collapsing. If two or more axes lock to the same diagonal, the archive is collapsing and v3.5 needs different axes.

Promotes as Tier-3 candidate symbol: `PATTERN_BEHAVIOR_DESCRIPTOR_COLLAPSE`.

### (3B) LOAD-BEARING — high-priority revision

**Task A and Task B form a feedback loop that becomes an echo chamber.**

Reviewer's framing:
> If Task B begins to confidently predict "survival" for a specific, narrow class of structural motifs, the neural mutation operator will heavily over-sample that motif. … your compute budget will be burned evaluating highly confident, completely useless claims generated by a feedback loop between Task A and Task B.

Correct. v2's no-pruning sweeps and predictor_recall meta-metric *detect* the failure mode but don't *prevent* it. Prevention requires structural decoupling between A and B's training distributions.

v3 mitigations:

- **Disjoint training data partitions.** Episodes 1, 3, 5, … (odd) train Task A. Episodes 2, 4, 6, … (even) train Task B. Both heads see the same substrate but don't share specific examples. Co-evolution proceeds with offset training distributions.
- **Periodic Task B retraining from scratch.** Every K iterations (default K=10), Task B is retrained from random initialization on the full substrate history, not continually fine-tuned. Breaks accumulated bias on specific motifs.
- **Cross-validation on held-out cells.** A randomly-sampled 10% of MAP-Elites cells are reserved for Task B evaluation only. Genomes from these cells never train Task B; they only validate.
- **Independence assertion at inference time.** Task A's inference does not condition on Task B's predictions. Task B independently scores Task A's proposals; both are routed to BindEvalKernelV2 in parallel, and the kernel's verdict is the source of truth.
- **Predictor downweighting on bias detection.** When Task B's per-cell false-positive rate (claims it predicted will survive but the kernel rejects) exceeds threshold (default 30%), Task B's weight in the routing decision drops to zero for that cell until retrained.

Promotes as Tier-3 candidate symbol: `PATTERN_TASK_A_TASK_B_ECHO_CHAMBER`.

### Round-2 closing assessment is praise, not critique

The reviewer's §4 ("The Value of the Bear Case") is positive feedback on v1's existing framing. v2 retained and strengthened the bear case; v3 keeps it. No revision needed.

## New candidate symbols filed

Three new Tier-3 candidates from round 2:

1. **PATTERN_SHARED_PRIOR_AT_TRAINING_LAYER** — when an LLM-derived component inherits a corpus prior, action-space asymmetry does not protect against semantic-prior contamination at the policy layer. Mitigation: anti-prior operator class, coverage-pressure reweighting, periodic prior detox.

2. **PATTERN_BEHAVIOR_DESCRIPTOR_COLLAPSE** — quality-diversity archives whose behavior axes are structurally coupled collapse to a lower-dimensional submanifold during active search. Mitigation: replace correlated structural axes with output-space axes that are mechanically independent of search dynamics.

3. **PATTERN_TASK_A_TASK_B_ECHO_CHAMBER** — multi-head systems whose generator and discriminator share training data develop confident-but-wrong mutual reinforcement. Mitigation: disjoint training partitions, periodic from-scratch retraining, cross-validation on held-out cells, independence at inference.

These complement the three from round 1 (`PATTERN_SPECIFICATION_GAMING`, `PATTERN_FILTER_AS_GATEKEEPER`, `PATTERN_ONTOLOGY_BIAS_IN_FEATURES`) and the five from the v2-thesis review.

## Total candidate-symbol harvest from this design cycle

| Source | Candidates produced |
|---|---|
| v2-thesis review (5 frontier models, 2026-05-02) | 5 |
| Round 1 ergon-proposal review (2026-05-03 morning) | 3 |
| Round 2 ergon-proposal review (2026-05-03 afternoon) | 3 |
| **Total** | **11 Tier-3 candidates** |

These are substrate-grade output. The reviews IS the discovery process for which substrate-level patterns the architecture has to defend against. The cost was three review cycles + ~$0 in compute. The value: 11 candidate symbols mechanically tracked as substrate components.

This is the meta-pattern worth naming: **adversarial review at architectural-design layer is itself substrate compounding.** Every review surfaces patterns the substrate now has to defend against; surviving the review IS substrate work.

## Recommendation: design freeze after v3

Two days, two rounds of revisions, six load-bearing architectural changes. Each cycle the proposal gets sharper, but the MVP hasn't started building. The reviewer's bottom-line praise is still operative: *the architecture is sound; the economics are highly asymmetric; the progression is cleanly phased.* The fundamentals haven't changed; the mitigations have accumulated.

**Recommendation: ship v3, then design freeze.**

Build the MVP. Run it for 2-4 weeks. Let the observed archive coverage, observed false-positive rate, observed cell-fill distribution inform what's actually load-bearing in practice rather than continuing to anticipate failure modes.

If MVP results surface a new architectural problem the design didn't anticipate, that's substrate-grade evidence and warrants v4. If MVP runs clean within the v3 envelope, the design is operative; further critiques become v0.5 or v1.0 issues.

Two more rounds of design review without empirical anchoring would be the *correlated-mutation* failure mode the v2-thesis flagged: convergent text-layer reasoning across LLMs, none of it grounded in actual substrate behavior. The reviews were valuable; further reviews without MVP data would compound design-layer narrative without compounding substrate-layer evidence.

## Action items

1. Ship v3 (this round's revisions) as `pivot/ergon_learner_proposal_v3.md`.
2. Add three new candidates to `harmonia/memory/symbols/CANDIDATES.md` (PATTERN_SHARED_PRIOR_AT_TRAINING_LAYER, PATTERN_BEHAVIOR_DESCRIPTOR_COLLAPSE, PATTERN_TASK_A_TASK_B_ECHO_CHAMBER).
3. Design freeze. MVP build begins from v3.
4. After MVP runs (week 4–5), assess whether v3 envelope held; ship v4 only if MVP empirically falsifies a v3 commitment.

— Ergon
