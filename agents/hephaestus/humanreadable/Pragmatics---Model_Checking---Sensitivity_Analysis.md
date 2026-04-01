# Pragmatics + Model Checking + Sensitivity Analysis

**Fields**: Linguistics, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T05:33:36.121104
**Report Generated**: 2026-03-31T19:54:51.989140

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using a handful of regex patterns we extract from both the prompt and each candidate answer a set of *grounded triples* ⟨s, r, o⟩ together with three binary attributes: polarity (¬ if the sentence contains a negation affecting the triple), modality (assertion = 0, possibility = 1, necessity = 2), and, when present, a numeric value attached to the object (e.g., “≥5”, “< 10”). Each distinct entity gets an integer ID via a lookup dict; each relation type gets an ID as well. The result is a structured NumPy array `T` of shape `(n_triples, 5)` with fields `(subj, rel, obj, polarity, modality)` and a parallel float array `V` for numeric thresholds (NaN when absent).  

2. **State‑space construction** – From `T` we build three Boolean adjacency matrices of shape `(n_entities, n_entities)`:  
   - `A_pos` for asserted positive triples (`polarity=1 & modality=0`)  
   - `A_neg` for asserted negative triples (`polarity=-1 & modality=0`)  
   - `A_mod` for modal triples (possibility/necessity).  
   These matrices are stored as `uint8` arrays so that logical OR and AND can be performed with NumPy’s bitwise ops.  

3. **Constraint propagation (model checking core)** – We compute the transitive closure of the positive assertions using repeated squaring:  
   ```
   A_pos_closure = A_pos.copy()
   while True:
       new = np.logical_or(A_pos_closure, np.dot(A_pos_closure, A_pos) > 0)
       if np.array_equal(new, A_pos_closure): break
       A_pos_closure = new
   ```  
   The same is done for negative assertions to obtain `A_neg_closure`. A candidate answer is *model‑checked* by verifying that every triple extracted from the answer is entailed by the closure: a triple ⟨s,r,o⟩ passes if `A_pos_closure[s,o]` is true for its relation and polarity matches (or its negation is absent from `A_neg_closure`). The proportion of passed triples yields a base satisfaction score `S_base ∈ [0,1]`.  

4. **Sensitivity analysis** – For each numeric threshold in `V` we create a perturbed copy where the value is shifted by ±1 unit (or ±10 % for scale‑free cases). We rebuild the adjacency matrices (only the affected triples change) and recompute `S_base`. Let `Δ_i = |S_base – S_base^perturbed_i|`. The sensitivity penalty is the root‑mean‑square of all `Δ_i`: `Sens = sqrt(mean(Δ_i²))`. The final score for a candidate is:  
   ```
   Score = S_base – λ * Sens
   ```  
   with λ set to 0.2 (empirically balances reward vs. fragility).  

**Parsed structural features**  
- Negations (via “not”, “no”, “never”) → polarity flag.  
- Comparatives (“greater than”, “less than”, “at most”) → numeric thresholds in `V`.  
- Conditionals (“if … then …”) → modal triples with modality=possibility/necessity.  
- Causal verbs (“cause”, “lead to”, “results in”) → treated as a distinct relation type.  
- Ordering relations (“before”, “after”, “precedes”) → temporal relation type, handled like any other relation in the closure.  

**Novelty**  
The combination is not a direct replica of any existing system. Model checkers usually work on hand‑crafted state machines; here the state machine is *auto‑generated* from linguistic triples. Sensitivity analysis is routinely applied to numerical models, but coupling it with the discrete closure of a logic‑extracted text graph is unprecedented. Pragmatics enters only through polarity and modality flags, which are rarely integrated into exhaustive verification pipelines. Thus the approach is novel, though it borrows well‑studied components (regex‑based IE, Boolean closure, finite‑difference sensitivity).  

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical entailment, handles quantifiers and modality, and penalizes fragile answers, yielding strong discriminative power on multi‑step reasoning tasks.  
Metacognition: 6/10 — While sensitivity provides a crude self‑check of robustness, the method lacks explicit monitoring of its own parsing uncertainties or alternative interpretations.  
Hypothesis generation: 5/10 — The system verifies given candidates but does not generate new hypotheses; it only scores supplied answers.  
Implementability: 9/10 — All steps rely on regex, NumPy array operations, and basic Python containers; no external libraries or APIs are required, making it straightforward to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Model Checking + Pragmatics: negative interaction (-0.062). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:54:42.070330

---

## Code

*No code was produced for this combination.*
