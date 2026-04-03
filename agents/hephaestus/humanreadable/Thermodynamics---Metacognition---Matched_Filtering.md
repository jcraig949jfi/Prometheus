# Thermodynamics + Metacognition + Matched Filtering

**Fields**: Physics, Cognitive Science, Signal Processing
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T11:17:12.179789
**Report Generated**: 2026-04-02T11:44:50.696910

---

## Nous Analysis

The algorithm builds a **thermodynamic‑matched‑filter scorer** that treats each candidate answer as a signal to be detected against a template derived from the prompt’s logical structure.  

1. **Data structures**  
   - `prop_graph`: a directed graph where nodes are extracted propositions (e.g., “X > Y”, “if A then B”) and edges represent logical relations (negation, comparatives, conditional, causal, ordering).  
   - `token_weights`: a NumPy array of shape *(n_tokens,)* where each token’s weight is `w_i = –ΔG_i`, approximated from a pre‑defined lexical energy table (e.g., negations ↑ energy, numbers ↓ entropy).  
   - `candidate_vec`: NumPy array of the same length, built by summing `token_weights` for tokens present in the candidate answer.  
   - `template_vec`: NumPy array built from `prop_graph` by assigning each proposition a base weight equal to its negative free energy (more stable propositions get lower energy → higher weight) and spreading it to constituent tokens via a uniform distribution over the proposition’s token span.  

2. **Operations**  
   - **Matched filtering**: compute the normalized cross‑correlation (dot product) `s = np.dot(candidate_vec, template_vec) / (np.linalg.norm(candidate_vec)*np.linalg.norm(template_vec))`. This maximizes SNR, yielding a detection score analogous to matched‑filter output.  
   - **Entropy‑based metacognition**: calculate the Shannon entropy `H = -∑ p_i log p_i` where `p_i` is the normalized weight of token *i* in the candidate. High entropy indicates diffuse, unsupported content. Compute confidence `c = 1 - (H / H_max)`.  
   - **Final score**: `score = s * c`. The thermodynamic part (`s`) rewards energy‑low, well‑structured matches; the metacognitive part (`c`) penalizes answers with high uncertainty, implementing error monitoring and confidence calibration.  

3. **Structural features parsed** (via regex and lightweight dependency parsing):  
   - Negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`), numeric values with units, causal cues (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `first`, `last`), and equality/identity statements. Each detected feature becomes a proposition node in `prop_graph`.  

4. **Novelty**  
   Pure matched‑filter detectors and energy‑based scoring exist separately in IR and ML literature, and metacognitive confidence calibration appears in self‑assessment models. Combining all three — using thermodynamic free energy as the template energy, matched‑filter dot‑product for detection, and entropy‑driven confidence calibration — has not been reported as a unified scoring pipeline for reasoning answers, making the combination novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure via constraint‑derived templates but still relies on shallow lexical weighting.  
Metacognition: 6/10 — entropy‑based confidence is a principled proxy yet ignores deeper self‑reflection on strategy use.  
Hypothesis generation: 5/10 — the method scores given candidates; it does not generate new hypotheses autonomously.  
Implementability: 8/10 — uses only NumPy, regex, and basic graph operations; feasible to code in <200 lines.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
