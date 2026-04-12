# Theory of Mind + Matched Filtering + Free Energy Principle

**Fields**: Cognitive Science, Signal Processing, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:52:26.702320
**Report Generated**: 2026-03-27T05:13:39.732279

---

## Nous Analysis

**Algorithm: Belief‑Signal Matched Filter (BSMF)**  
The tool represents each candidate answer as a set of *belief propositions* extracted from the text (e.g., “Agent A believes P”, “Agent B desires Q”). Each proposition is encoded as a binary feature vector v ∈ {0,1}^F where dimensions correspond to structural primitives (negation, comparative, conditional, causal link, ordering, numeric constraint).  

1. **Theory of Mind layer** – Build a *mental model* M of the question’s implicit agents and their attitudes. M is a dictionary mapping agent IDs to lists of proposition vectors that the question entails (derived via rule‑based parsing of the prompt).  
2. **Free Energy Principle layer** – Compute prediction error ε for each answer a as the squared L2 distance between its proposition set V_a and the mental model M, after aligning propositions by agent ID:  
   ε_a = Σ_{agent i} ‖ Σ_{p∈V_a,i} v_p – Σ_{q∈M,i} v_q ‖².  
   This is the variational free‑energy surrogate: lower ε means the answer’s inferred beliefs better match the expected mental states, minimizing surprise.  
3. **Matched Filtering layer** – Treat each proposition vector as a *signal* s_i and the noise as the residual variance of unused feature dimensions. The matched filter output for answer a is the cross‑correlation:  
   y_a = Σ_i (s_i · h_i) / σ_i², where h_i is the template vector from M for agent i and σ_i² is the empirical variance of that feature across a development set.  
   The final score combines both terms: Score_a = –ε_a + λ·y_a (λ balances belief fidelity vs. signal detection).  

**Parsed structural features** – Negations (¬), comparatives (> , <), conditionals (if‑then), causal claims (because, leads to), ordering relations (before/after), numeric values and units, quantifiers (all, some, none), and modal operators (must, might). Regex patterns extract these into the feature vectors.  

**Novelty** – The combination mirrors predictive coding accounts of Theory of Mind (Friston 2010) but adds a explicit matched‑filter detection step that is uncommon in cognitive‑science inspired NLP scorers. Existing work uses either Bayesian belief tracking or template matching, not both jointly.  

**Ratings**  
Reasoning: 7/10 — Captures multi‑agent belief inference and error minimization, but relies on hand‑crafted rules that may miss deep semantic nuance.  
Metacognition: 6/10 — The free‑energy term provides a self‑assessment of prediction error, yet the model lacks explicit monitoring of its own parsing confidence.  
Hypothesis generation: 5/10 — Generates candidate belief structures via parsing, but does not propose alternative hypotheses beyond the given answers.  
Implementability: 8/10 — Uses only numpy for vector ops and stdlib regex; no external libraries or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Matched Filtering**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
