# Cognitive Load Theory + Matched Filtering + Free Energy Principle

**Fields**: Cognitive Science, Signal Processing, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T13:06:32.978999
**Report Generated**: 2026-03-27T16:08:16.459669

---

## Nous Analysis

**Algorithm**  
1. **Chunk extraction** – Using a small set of regex patterns we parse the prompt and each candidate answer into propositional chunks of the form ⟨entity, relation, entity⟩ (e.g., “The cat chased the mouse”). Relations capture negations, comparatives (“more than”), conditionals (“if … then”), causal cues (“because”, “leads to”), numeric comparisons, and temporal/spatial ordering (“before”, “above”). Each unique chunk gets an integer ID; we store a dictionary `chunk2id`.  
2. **Signal vectors** – For a text we build a binary numpy array `s ∈ {0,1}^D` where `D = len(chunk2id)`. `s[i]=1` if chunk *i* appears.  
3. **Expected distribution** – From the prompt we compute a prior probability vector `p = normalize(histogram(s_prompt))`. This represents the brain’s prediction about which chunks should occur (Free Energy Principle).  
4. **Matched‑filter score** – The candidate’s signal `s_ans` is correlated with the prompt signal: `corr = np.dot(s_prompt, s_ans)`. The noise variance is estimated as `σ² = 0.25` (maximum variance of a binary variable). The SNR‑like matched‑filter output is `M = corr² / (np.linalg.norm(s_prompt)**2 * σ²)`.  
5. **Free‑energy (prediction error)** – Precision is set to the inverse variance of each chunk: `π_i = 1 / (p_i * (1-p_i) + ε)`. Free energy is `F = Σ_i π_i * (s_ans[i] - p_i)²`. Lower `F` means better prediction.  
6. **Cognitive‑load penalty** – Working‑memory capacity is approximated by `C = 4` chunks. If `np.sum(s_ans) > C` we add a load term `L = λ * (np.sum(s_ans) - C)²`; otherwise `L = 0`.  
7. **Final score** – `Score = M - α * F - β * L` (α,β are small constants, e.g., 0.5). Higher scores indicate answers that match the prompt’s signal, respect its predictive structure, and stay within working‑memory limits.

**Structural features parsed**  
- Negations (“not”, “no”)  
- Comparatives (“greater than”, “less than”, “more … than”)  
- Conditionals (“if … then”, “unless”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Numeric values and arithmetic relations  
- Ordering/temporal relations (“before”, “after”, “above”, “below”)  
- Simple subject‑verb‑object triples (entities and their attributes)

**Novelty**  
Matched filtering is classic in signal detection; the Free Energy Principle has been applied to perception but rarely to textual propositional analysis; Cognitive Load Theory’s chunk‑size constraint is seldom used as a hard penalty in scoring. While TF‑IDF and cosine similarity exist, the explicit combination of a matched‑filter SNR term, a precision‑weighted prediction‑error free‑energy term, and a working‑memory load penalty is not present in current NLP evaluation tools, making the approach novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and predictive error but relies on shallow regex parsing.  
Metacognition: 5/10 — does not explicitly model self‑monitoring of uncertainty beyond precision terms.  
Hypothesis generation: 6/10 — can rank alternatives but does not generate new hypotheses.  
Implementability: 8/10 — uses only numpy and std‑lib; regex and vector ops are straightforward.

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
