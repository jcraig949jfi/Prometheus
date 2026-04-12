# Cellular Automata + Matched Filtering + Pragmatics

**Fields**: Computer Science, Signal Processing, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T00:15:59.068858
**Report Generated**: 2026-03-26T22:21:37.646942

---

## Nous Analysis

**Algorithm**  
1. **Token‑grid construction** – Split prompt and each candidate answer into a list of tokens (words, numbers, punctuation). Pad/truncate to a fixed length *L* and reshape into a 2‑D array of shape (1, L) so the text can be treated as a one‑dimensional cellular‑automaton (CA) lattice. Each cell holds an integer ID from a vocabulary built from the prompt (numpy array `state`).  
2. **Structural feature extraction** – Using only the standard library `re`, detect:  
   * negations (`not`, `n't`),  
   * comparatives (`more`, `less`, `-er`, `than`),  
   * conditionals (`if`, `unless`, `then`),  
   * numeric values (`\d+(\.\d+)?`),  
   * causal cues (`because`, `since`, `therefore`),  
   * ordering (`before`, `after`, `first`, `last`).  
   For each hit, set a binary mask `M` of shape (L,) where `M[i]=1` if token *i* participates in a detected relation.  
3. **CA propagation (Rule 110)** – Initialise the lattice with `state`. For *T* iterations (e.g., T=5) update each cell according to Rule 110 using its left, self, and right neighbor (numpy roll for boundaries). The mask `M` is applied after each step so that only cells involved in structural relations can change state; others remain fixed, thereby propagating truth‑values through the dependency graph implied by the detected constructs.  
4. **Template generation** – After CA stabilisation, the prompt’s final lattice `P_template` serves as the expected pattern.  
5. **Matched‑filter scoring** – For each candidate, run the same CA steps to obtain `C_state`. Compute the normalized cross‑correlation (numpy.correlate with `mode='same'`) between `C_state` and `P_template`, then take the peak value divided by the L2‑norm of both vectors – this is the matched‑filter output, maximal when the candidate’s propagated structure aligns with the prompt’s.  
6. **Pragmatic weighting** – Apply Grice’s maxims as scalar penalties/rewards:  
   * **Quantity** – subtract 0.1 per extra token beyond the prompt length,  
   * **Relevance** – add 0.2 if the candidate contains at least one token from each detected relation class,  
   * **Manner** – subtract 0.15 for ambiguous tokens (e.g., pronouns without antecedent detected via simple coreference regex),  
   * **Quality** – subtract 0.2 if a numeric claim contradicts a prompt numeric value (direct inequality check).  
   The final score = matched‑filter value + sum of pragmatic adjustments.  

**Structural features parsed** – negations, comparatives, conditionals, numeric values, causal claims, ordering relations (temporal/se‑quential).  

**Novelty** – While CA‑based language models and matched‑filter template matching exist separately, coupling a deterministic CA that propagates only syntactically‑extracted logical relations with a cross‑correlation detection stage and pragmatic maxim weighting is not described in the literature; it combines discrete dynamics, signal detection theory, and speech‑act theory in a novel way.  

**Ratings**  
Reasoning: 7/10 — The CA propagation captures logical dependencies, but limited depth may miss complex inference.  
Metacognition: 5/10 — The system has no explicit self‑monitoring; pragmatic adjustments are static heuristics.  
Hypothesis generation: 4/10 — No mechanism for generating alternative interpretations beyond the given candidates.  
Implementability: 9/10 — Uses only numpy and std‑library regex; all steps are straightforward array operations.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cellular Automata**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Matched Filtering**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Category Theory + Embodied Cognition + Pragmatics (accuracy: 0%, calibration: 0%)
- Causal Inference + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
