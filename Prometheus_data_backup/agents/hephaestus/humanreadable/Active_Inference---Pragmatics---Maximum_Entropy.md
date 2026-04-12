# Active Inference + Pragmatics + Maximum Entropy

**Fields**: Cognitive Science, Linguistics, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:37:24.034572
**Report Generated**: 2026-03-31T19:17:41.453790

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – For each candidate answer *a* we run a fixed set of regex patterns to obtain a binary‑count feature vector **fₐ** ∈ ℕᵈ. Dimensions correspond to:  
   - Negations (`\bnot\b|\bnever\b`)  
   - Comparatives (`\bmore\b|\bless\b|\b>\b|\b<\b`)  
   - Conditionals (`\bif\b.*\bthen\b|\bunless\b`)  
   - Causal markers (`\bbecause\b|\bleads to\b|\bresults in\b`)  
   - Ordering/temporal (`\bbefore\b|\bafter\b|\bfirst\b|\bsecond\b`)  
   - Numeric tokens (`\d+(\.\d+)?`)  
   - Vague modifiers (`\babout\b|\broughly\b|\bkind of\b`)  
   - Speech‑act cues (`\bI think\b|\bIn fact\b|\bAccording to\b`).  
   The result is a matrix **X** ∈ ℕⁿˣᵈ for *n* candidates.

2. **Maximum‑Entropy prior** – From the prompt we derive expected counts **µ** (e.g., the prompt contains two conditionals, so we expect µ_conditionals = 2). We solve for Lagrange multipliers **λ** that satisfy **Xᵀp = µ** under the MaxEnt principle, which yields the exponential‑family distribution  
   \[
   p(\mathbf{f}) = \frac{\exp(\boldsymbol{\lambda}^\top \mathbf{f})}{Z(\boldsymbol{\lambda})},
   \]  
   where **λ** is found by iterative scaling (numpy‑only: repeated updates λ ← λ + α·(µ – Xᵀp)). The log‑likelihood of a candidate is `logpₐ = λ·fₐ – logZ`.

3. **Pragmatics penalty** – We evaluate Grice‑style maxims as deterministic checks:  
   - **Quantity**: |fₐ[length] – expected_info|  
   - **Quality**: mismatch between asserted causal/factual triples and those entailed by the prompt (checked via simple rule‑based chaining).  
   - **Relevance**: cosine similarity between prompt‑derived causal graph and answer‑derived graph (numpy dot product).  
   - **Manner**: count of vague modifiers.  
   The total penalty is a weighted sum `penₐ = w·[quantity, quality, relevance, manner]·[fₐ]`.

4. **Expected free energy score** – Following Active Inference, the score combines extrinsic fit (log‑likelihood) and intrinsic value (information gain ≈ –penₐ):  
   \[
   Sₐ = \underbrace{\log pₐ}_{\text{extrinsic}} \;-\; \beta \underbrace{\text{pen}_ₐ}_{\text{intrinsic}}.
   \]  
   Higher *S* indicates a better answer. All operations use only `numpy` and the Python standard library.

**Structural features parsed** – negations, comparatives, conditionals, causal markers, ordering/temporal relations, numeric quantities, quantifiers, vague modifiers, and explicit speech‑act markers.

**Novelty** – While MaxEnt models, pragmatic filters, and active‑inference‑style expected free energy have appeared separately, their joint use as a scoring function for candidate answers—where MaxEnt supplies a principled prior, pragmatics provides constraint‑based penalties, and the EFE formulation unifies them—is not present in existing open‑source reasoning tools. It bridges rational‑speech‑act ideas with information‑theoretic action selection without neural components.

**Rating**  
Reasoning: 7/10 — captures logical structure well but lacks deep inference beyond local constraints.  
Metacognition: 5/10 — limited self‑monitoring; penalty approximates reflection but no iterative belief revision.  
Hypothesis generation: 6/10 — can sample from the MaxEnt distribution to propose alternatives, yet generation is rudimentary.  
Implementability: 9/10 — relies solely on regex, numpy linear algebra, and simple loops; easy to code and debug.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Active Inference + Pragmatics: strong positive synergy (+0.236). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Phase Transitions + Pragmatics + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:16:42.800434

---

## Code

*No code was produced for this combination.*
