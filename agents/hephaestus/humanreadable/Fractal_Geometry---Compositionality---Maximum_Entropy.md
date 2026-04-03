# Fractal Geometry + Compositionality + Maximum Entropy

**Fields**: Mathematics, Linguistics, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T03:35:12.861662
**Report Generated**: 2026-04-02T04:20:11.876038

---

## Nous Analysis

The algorithm builds a hierarchical compositional parse of each candidate answer, extracts multi‑scale feature vectors from that parse, and then derives scores by solving a maximum‑entropy (MaxEnt) problem that matches observed feature‑constraint expectations.

1. **Parsing & tree construction** – Using only regex and the stdlib, we identify syntactic chunks: noun phrases (NP), verb phrases (VP), prepositional phrases (PP), and clauses marked by cue words (if, then, because, not, more/less, -er, than, all/some/none). Each chunk becomes a node in a rooted ordered tree; leaf nodes store token‑level attributes (POS tag, numeric value, polarity). The tree is built incrementally by scanning the token list and attaching chunks according to a fixed hierarchy (S → NP VP, VP → V (NP|PP|SBAR), etc.).  

2. **Multi‑scale feature extraction (fractal geometry)** – For each depth d = 0…D (where D is the max tree depth), we compute a histogram of node types and numeric aggregates (sum, mean, count of numbers, count of negations, comparatives, conditionals, causal cues). This yields a feature vector **f**₍d₎ ∈ ℝᵏ. To capture self‑similarity we concatenate the vectors across depths, applying a scale‑weight w₍d₎ = 2^(‑d) (a power‑law decay). The final feature vector **F** = [w₀**f**₀, w₁**f**₁, …, w_D**f**_D] captures fractal‑like repetition of structure at different resolutions.  

3. **Maximum‑entropy scoring** – Across a validation set of answers with known correctness, we compute empirical expectations **b** = 𝔼[**F**] for each feature dimension. We then seek a weight vector **w** that maximizes entropy H(p) = ‑∑ pᵢ log pᵢ subject to linear constraints 𝔼ₚ[**F**] = **b**. This is solved with the Generalized Iterative Scaling (GIS) algorithm using only NumPy for log‑sum‑exp and vector updates. The resulting log‑linear model assigns a probability p(answer) ∝ exp(**w**·**F**). The score for a candidate is the log‑probability (or normalized probability) produced by this model.  

**Structural features parsed** – Negations (“not”, “no”), comparatives (“more”, “less”, “‑er”, “than”), conditionals (“if”, “then”, “unless”), causal claims (“because”, “leads to”, “results in”), numeric values (integers, floats, units), ordering relations (“greater than”, “less than”, “before”, “after”), quantifiers (“all”, “some”, “none”), modal verbs (“must”, “might”).  

**Novelty** – While tree kernels and MaxEnt models appear separately in NLP, the explicit use of fractal‑scale self‑similarity weighting on syntactic trees to generate features for a MaxEnt log‑linear model is not documented in prior work, making the combination novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty well but lacks deep semantic reasoning.  
Metacognition: 5/10 — provides a principled uncertainty estimate via entropy but does not reflect on its own failure modes.  
Hypothesis generation: 4/10 — scores given candidates; does not generate new hypotheses or explanations.  
Implementability: 8/10 — relies only on regex, stdlib, and NumPy; all steps are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

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
