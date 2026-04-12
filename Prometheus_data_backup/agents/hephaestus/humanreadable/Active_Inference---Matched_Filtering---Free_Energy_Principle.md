# Active Inference + Matched Filtering + Free Energy Principle

**Fields**: Cognitive Science, Signal Processing, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:44:42.558860
**Report Generated**: 2026-03-31T18:13:45.755628

---

## Nous Analysis

The algorithm builds a deterministic generative model of the text and scores each candidate answer by the variational free energy that would result if the answer were the true observation.  

**Data structures**  
- `props`: list of parsed propositions, each a tuple `(subj, pred, obj, mod)` where `mod` encodes polarity (negation), modality (conditional, causal) and a numeric tag if present.  
- `feat_dict`: maps each unique lemma/predicate/numeric token to an integer index.  
- `E`: evidence matrix of shape `(n_props, n_feats)`, binary (1 if feature appears in a proposition, 0 otherwise).  
- For each candidate answer `c`, a template vector `T_c` of same shape is built by extracting the same features from the answer string.  

**Operations**  
1. **Parsing** – regex patterns extract:  
   - Negations (`not`, `n’t`) → flip polarity bit.  
   - Comparatives (`>`, `<`, `greater`, `less`) → add a `comparison` feature with direction.  
   - Conditionals (`if … then …`) → add `antecedent` and `consequent` feature groups.  
   - Causal claims (`because`, `leads to`, `results in`) → add `cause`/`effect` tags.  
   - Ordering relations (`before`, `after`, `first`, `last`) → add temporal tags.  
   - Numeric values → tokenized as `NUM_<value>` (rounded to nearest integer for stability).  
2. **Matched filtering** – compute the cross‑correlation between evidence and template:  
   `match = np.dot(E, T_c) / (np.linalg.norm(E)*np.linalg.norm(T_c)+eps)`.  
   This is the likelihood term (maximizing SNR).  
3. **Prediction error** – `err = np.linalg.norm(E - T_c)**2`.  
4. **Epistemic value (expected free energy component)** – approximate the reduction in uncertainty by the variance of features across propositions:  
   `info = 0.5 * np.log(np.linalg.det(np.cov(E.T)+eps*np.eye(n_feats)))`.  
5. **Free energy score** – `F = err - info` (lower is better). The final answer score is `-F`.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values, and quantifiers (via regex for “all”, “some”, “none”).  

**Novelty** – While variational free energy has been applied to language modeling and active inference to action selection, coupling it with a matched‑filter detection pipeline for answer scoring is not described in the literature; existing approaches use retrieval‑based similarity or neural likelihoods, not a joint SNR‑maximization and uncertainty‑reduction objective.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on linear approximations.  
Metacognition: 6/10 — epistemic term provides a rough self‑assessment of information gain, yet lacks deeper reflection on own uncertainty.  
Hypothesis generation: 5/10 — generates candidate‑specific predictions but does not propose new hypotheses beyond the given answers.  
Implementability: 8/10 — uses only regex, NumPy, and standard library; no external dependencies.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T18:11:24.951918

---

## Code

*No code was produced for this combination.*
