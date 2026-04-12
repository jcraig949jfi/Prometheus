# Cognitive Load Theory + Matched Filtering + Pragmatics

**Fields**: Cognitive Science, Signal Processing, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:42:15.691778
**Report Generated**: 2026-04-02T04:20:11.715041

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a list of *propositional tuples* `(entity₁, relation, entity₂, polarity, modality)`. Relations are extracted with regex patterns for:  
   - Negations (`not`, `no`) → `polarity = -1`  
   - Comparatives (`greater than`, `less than`, `≥`, `≤`) → relation encoded as a comparative operator  
   - Conditionals (`if … then …`) → modality = `conditional`  
   - Causal cues (`because`, `leads to`, `results in`) → modality = `causal`  
   - Ordering (`before`, `after`) → modality = `temporal`  
   - Numeric literals → stored as a separate float field.  
   The parser returns a NumPy structured array `P` with fields: `rel_id` (int), `arg1_id`, `arg2_id` (int from a vocabulary), `polarity` (±1), `modality` (enum), `value` (float or NaN).  

2. **Feature vector** `v` is built by one‑hot encoding `rel_id` and concatenating normalized `value` fields; modality and polarity are added as extra dimensions.  

3. **Cognitive Load estimation** (intrinsic, extraneous, germane):  
   - *Intrinsic load* `L_i = ‖v‖₀` (number of non‑zero propositions).  
   - *Extraneous load* `L_e = α·count(stop‑words) + β·length(punctuation)` (penalties for irrelevant tokens).  
   - *Germane load* `L_g = v·w·v_ref` where `w` is a diagonal weighting matrix derived from Grice’s maxims: higher weight for relations that satisfy **Relevance** (present in the prompt), **Quantity** (matching expected number of arguments), and **Manner** (clear, unambiguous predicates).  

4. **Matched‑filter scoring**: treat the reference answer vector `v_ref` as the known signal and the candidate vector `v` as the observation in noise. Compute the cross‑correlation via `np.correlate(v, v_ref, mode='valid')` and take the peak magnitude `C_max`. Normalize by the energy of the reference: `SNR = C_max / (‖v_ref‖₂²)`.  

5. **Final score** for a candidate:  

```
score = (L_g * SNR) / (L_i + L_e + ε)
```

where ε prevents division by zero. Higher scores indicate answers that impose low extraneous load, high germane (pragmatically relevant) load, and strong matched‑filter alignment with the reference.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, temporal ordering, numeric values, quantifiers, and polarity‑flipped relations.

**Novelty** – While semantic parsing and kernel‑based similarity (e.g., string kernels, SMV) exist, explicitly coupling Cognitive Load Theory’s load components with a matched‑filter detection framework and pragmatics‑driven weighting is not documented in current literature; it combines three disparate theories into a single, computable scoring function.

**Ratings**  
Reasoning: 7/10 — captures logical structure and pragmatic relevance but lacks deep inference chaining.  
Metacognition: 5/10 — provides load estimates but does not explicitly monitor or adapt its own processing.  
Hypothesis generation: 6/10 — can rank candidates; generating new hypotheses would require additional search mechanisms.  
Implementability: 8/10 — relies only on regex, NumPy, and stdlib; all steps are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
