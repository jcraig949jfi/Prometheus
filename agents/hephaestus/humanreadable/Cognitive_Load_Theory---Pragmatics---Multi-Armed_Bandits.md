# Cognitive Load Theory + Pragmatics + Multi-Armed Bandits

**Fields**: Cognitive Science, Linguistics, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:11:48.358983
**Report Generated**: 2026-03-25T09:15:27.723882

---

## Nous Analysis

Combining the three ideas yields a **Pragmatic Cognitive‑Load‑Aware Multi‑Armed Bandit (PC‑MAB)**. Each hypothesis to be tested is treated as an arm; pulling an arm corresponds to gathering evidence (e.g., running an experiment or querying a data source). The bandit’s reward signal is not raw accuracy but a **pragmatically enriched utility**: the likelihood of the observation is updated using a Gricean‑style relevance model (quantity, quality, relation, manner) so that only context‑appropriate implicatures count as evidence. Simultaneously, a cognitive‑load term penalizes arms that would exceed the agent’s working‑memory capacity. Intrinsic load is proportional to the hypothesis’s structural complexity (number of chunks required), extraneous load is estimated from irrelevant background information filtered out by the pragmatic relevance function, and germane load is rewarded when the arm’s outcome reduces uncertainty about the agent’s goal. The agent selects arms using a **Thompson‑sampling rule** whose posterior is tempered by a load‑aware temperature: τ = τ₀ · exp(λ·L), where L is the estimated total load and λ controls how strongly load suppresses exploration. This mechanism lets the system dynamically allocate its limited working memory to the most promising, context‑relevant hypotheses while still exploring enough to avoid local optima.

**Advantage for self‑hypothesis testing:** The PC‑MAB automatically balances exploration (trying new hypotheses) with exploitation (refining promising ones) while respecting memory limits, preventing overload from irrelevant details, and focusing on inferences that are pragmatically warranted in the current context. This yields faster convergence to high‑utility hypotheses and reduces wasted cognitive effort on low‑reward or incoherent tests.

**Novelty:** Resource‑constrained or budgeted bandits exist, and pragmatic language models (e.g., Rational Speech Acts) have been coupled with reinforcement learning. However, explicitly integrating Gricean maxims as a likelihood modifier together with a three‑component cognitive‑load penalty inside a Thompson‑sampling bandit is not a standard formulation, making the combination relatively novel, though it builds on known sub‑fields.

**Ratings**  
Reasoning: 7/10 — provides a principled, constraint‑aware decision rule but relies on approximations of pragmatic relevance.  
Metacognition: 8/10 — the load‑aware temperature gives the system explicit monitoring of its own cognitive capacity.  
Hypothesis generation: 7/10 — exploration is guided by both uncertainty and pragmatic informativeness, steering generation toward relevant candidates.  
Implementability: 6/10 — requires building a pragmatic likelihood module, estimating load per hypothesis, and integrating them with Thompson sampling; feasible with current probabilistic programming tools but nontrivial.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 6/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Pragmatics**: Strong primary driver of forge success. Make this concept the core architectural pattern of the evaluate() method. Historical forge rate: 76%. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Sparse Autoencoders + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Causal Inference + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Chaos Theory + Metacognition + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
