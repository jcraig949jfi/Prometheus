# Matched Filtering + Compositionality + Maximum Entropy

**Fields**: Signal Processing, Linguistics, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:22:58.724194
**Report Generated**: 2026-03-31T19:12:22.147301

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Convert the question and each candidate answer into a typed dependency‑style parse tree using a deterministic rule‑based parser (regex‑based extraction of predicates, arguments, quantifiers, negation, comparative, conditional). Each node is stored as a dict `{type: str, args: list}` where `type` ∈ {pred, neg, comp, cond, num, causal, order}. The tree is flattened into a feature vector **v** ∈ ℝᵏ by one‑hot encoding each possible (type, position‑in‑tree) pair; k is the size of the universal predicate‑position vocabulary built from the training set.  
2. **Matched‑filter scoring** – Treat the question’s vector **q** as a known signal and each candidate vector **cᵢ** as a noisy observation. Compute the normalized cross‑correlation (dot product after ℓ₂‑norm):  
   `sᵢ = (q/‖q‖)·(cᵢ/‖cᵢ‖)`. This is the matched‑filter output, maximising SNR under Gaussian noise assumptions.  
3. **Maximum‑entropy weighting** – From the question extract a set of linear constraints (e.g., “if X then Y” → expectation of cond‑node = 1; numeric equality → expectation of num‑node = value). Solve the log‑linear maxent problem: find distribution **p** over possible parses that satisfies constraints and maximises entropy, yielding weights **w** = exp(**λ**·**f**) where **f** are constraint feature vectors and **λ** are Lagrange multipliers (computed with numpy’s `linalg.lstsq`). The final score is `Sᵢ = sᵢ * wᵢ`, where `wᵢ` is the weight assigned to the candidate’s parse under the maxent distribution.  
4. **Selection** – Return the candidate with highest `Sᵢ`.  

**Structural features parsed**  
- Negation (`not`, `no`) → `neg` node.  
- Comparatives (`greater than`, `less than`, `as … as`) → `comp` node with direction attribute.  
- Conditionals (`if … then …`, `unless`) → `cond` node.  
- Numeric values and units → `num` node with magnitude.  
- Causal claims (`because`, `leads to`) → `causal` node.  
- Ordering relations (`before`, `after`, `first`, `last`) → `order` node.  

**Novelty**  
While compositional semantic parsing and maximum‑entropy log‑linear models are standard in structured prediction, coupling them with a matched‑filter detection step—treating candidate parses as signals to be correlated with a question template—is not present in existing work. Prior approaches use hash similarity, bag‑of‑words, or pure CRF scoring; the explicit SNR‑maximising cross‑correlation combined with maxent priors is a novel algorithmic synthesis.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via compositional parsing and SNR‑optimal matching, handling multi‑step inference.  
Metacognition: 6/10 — provides a confidence‐like weight from the maxent distribution but lacks explicit self‑reflection on uncertainty.  
Hypothesis generation: 7/10 — the maxent distribution yields a set of weighted parses, enabling alternative hypotheses to be ranked.  
Implementability: 9/10 — relies only on regex parsing, numpy linear algebra, and basic data structures; no external libraries or neural components required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:10:13.439883

---

## Code

*No code was produced for this combination.*
