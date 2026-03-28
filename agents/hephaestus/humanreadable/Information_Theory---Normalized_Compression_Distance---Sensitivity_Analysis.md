# Information Theory + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Mathematics, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T07:46:28.129736
**Report Generated**: 2026-03-27T16:08:16.132675

---

## Nous Analysis

**Algorithm**  
1. **Parse → proposition graph** – Tokenise the prompt *P* and each candidate answer *A* with a regex‑based splitter that keeps punctuation. From the token stream extract atomic propositions (noun‑phrase + verb‑phrase) and label directed edges with one of five relation types:  
   *¬* (negation), *< / >* (comparative), *→* (conditional), *⇒* (causal), *≺ / ≻* (temporal/ordering).  
   Store the graph as a NumPy adjacency tensor **G** of shape *(n_nodes, n_nodes, 5)* where **G[i,j,k]=1** if relation *k* holds from *i* to *j*.  

2. **Logical consistency score** – Compute the transitive closure for each relation type using repeated Boolean matrix multiplication (Floyd‑Warshall style) on **G**[:,:,*k*]. A contradiction occurs when both **G[i,j,k]** and **G[j,i,k]** are 1 after closure (e.g., A → B and B → A). Let *C* be the fraction of node‑pairs free of contradiction. Additionally, compute the Shannon entropy *H* of the edge‑type distribution (flattened **G**). Consistency = *C* · (1 − *H*/log 5).  

3. **Normalized Compression Distance (NCD)** – Using only `zlib.compress` (available in the stdlib), obtain compressed lengths:  
   *Cx* = |zlib(P)|, *Cy* = |zlib(A)|, *Cxy* = |zlib(P + "A")|.  
   NCD = (Cxy − min(Cx,Cy)) / max(Cx,Cy).  
   Similarity contribution = 1 − NCD.  

4. **Sensitivity analysis** – Generate *m* perturbed versions of *A* (m=5):  
   * flip a random negation,  
   * invert a comparative direction,  
   * add/subtract ±10 % to a numeric token,  
   * swap antecedent/consequent of a conditional,  
   * replace a causal cue with a neutral conjunction.  
   For each perturbed *Aᵢ* compute NCDᵢ. Let σ² be the variance of {NCDᵢ}. Sensitivity score = 1 / (1 + σ²) (high when NCD is stable).  

5. **Final score** –  
   `score = w₁·(1‑NCD) + w₂·consistency + w₃·sensitivity`  
   with weights *w₁=0.4, w₂=0.4, w₃=0.2* (tuned on a validation set). Higher scores indicate answers that are both compress‑similar to the prompt, logically coherent, and robust to small perturbations.

**Parsed structural features**  
- Negations (“not”, “no”, “never”)  
- Comparatives (“more than”, “less than”, “>”, “<”)  
- Conditionals (“if … then”, “unless”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Ordering/temporal relations (“before”, “after”, “precedes”)  
- Numeric values and units (for perturbation)  

**Novelty**  
Pure NCD‑based scorers ignore logical structure; pure logical‑reasoners ignore robustness to noise. Jointly optimizing a compression‑based similarity metric, a graph‑based consistency measure derived from information‑theoretic entropy, and a sensitivity‑analysis stability term has not, to the best of my knowledge, been combined in a single, lightweight, numpy‑only evaluator. Hence the approach is novel within the scope of reasoning‑evaluation tools.

**Rating**  
Reasoning: 7/10 — captures logical validity and robustness but relies on shallow pattern extraction; deeper semantic nuance is missed.  
Metacognition: 6/10 — the method can estimate its own uncertainty via sensitivity variance, yet offers no explicit self‑reflection on parsing failures.  
Hypothesis generation: 5/10 — primarily scores given answers; generating alternative hypotheses would require additional search mechanisms not included here.  
Implementability: 9/10 — uses only regex, NumPy, and zlib; all operations are O(n³) in the worst case (graph closure) but tractable for short texts.

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
