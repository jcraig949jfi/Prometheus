# Information Theory + Dual Process Theory + Hebbian Learning

**Fields**: Mathematics, Cognitive Science, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T14:47:48.523740
**Report Generated**: 2026-03-31T14:34:56.124002

---

## Nous Analysis

The algorithm builds a lightweight semantic graph from the question and each candidate answer, then scores the answer with three complementary terms that map onto Information Theory, Dual‑Process Theory, and Hebbian Learning.

**Data structures**  
- `props`: list of extracted propositions, each a tuple `(subj, rel, obj, polarity, modality)` where `rel` is a regex‑captured relation (e.g., “>”, “=”, “causes”, “if‑then”).  
- `W`: a symmetric NumPy matrix of shape `(V,V)` (V = vocabulary size) holding Hebbian co‑occurrence weights; initialized to zero and updated online.  
- `q_vec`, `a_vec`: NumPy vectors of length V representing TF‑IDF‑style counts of tokens in the question and answer, respectively.

**Operations**  
1. **Structural parsing** – a set of regex patterns extracts negations (`not`, `no`), comparatives (`>`, `<`, `>=`, `<=`), conditionals (`if … then …`), causal verbs (`causes`, `leads to`), and numeric values. Each match yields a proposition appended to `props`.  
2. **Hebbian update** – for every sentence, increment `W[i,j]` by η when token i and token j co‑occur (η = 0.01). This implements “cells that fire together wire together.”  
3. **Information‑theoretic term** – compute the empirical distribution `p` over propositions in the question and `q` over propositions in the answer; calculate Shannon entropy `H(p)`, `H(q)` and mutual information `I(p;q) = H(p)+H(q)-H(p,q)`. The MI term rewards answers that share informative propositions with the question.  
4. **Dual‑process scoring** –  
   - *System 1* (fast): cosine similarity between `q_vec` and `a_vec` after weighting by `W` (i.e., `q_vec @ W @ a_vec`).  
   - *System 2* (deliberate): run a lightweight constraint‑propagation pass over `props` applying modus ponens and transitivity; count the proportion of constraints satisfied.  
5. **Final score** – `score = λ₁·I(p;q) + λ₂·System1 + λ₃·System2`, with λ’s normalized to sum to 1.

**Structural features parsed**  
Negations, comparatives, conditionals, numeric values, causal claims, and ordering relations (e.g., “X before Y”, “X ≥ Y”).

**Novelty**  
While mutual‑information‑based QA, Hebbian‑style term weighting, and dual‑process heuristics each appear separately, their joint integration in a single numpy‑only pipeline that couples entropy‑based relevance with fast similarity and slow logical propagation has not been described in the literature.

**Rating**  
Reasoning: 7/10 — captures relevance via MI and logical consistency, but simplistic propagation limits deep reasoning.  
Metacognition: 6/10 — System 1/System 2 split offers a rudimentary self‑monitoring mechanism, yet no explicit confidence calibration.  
Hypothesis generation: 5/10 — the model can propose answers but does not actively generate alternative hypotheses beyond scoring given candidates.  
Implementability: 9/10 — relies only on regex, NumPy arrays, and basic loops; easily fits the constraints.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
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
