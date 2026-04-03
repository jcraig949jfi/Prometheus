# Topology + Sparse Autoencoders + Matched Filtering

**Fields**: Mathematics, Computer Science, Signal Processing
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T07:01:08.735307
**Report Generated**: 2026-04-02T08:39:55.235854

---

## Nous Analysis

**Algorithm: Topological Sparse Matched‑Filter Scorer (TSMFS)**  

1. **Parsing → logical graph**  
   - Use regex to extract triples *(subject, relation, object)* from the prompt and each candidate answer.  
   - Relations are drawn from a fixed set R = {equals, not‑equals, greater‑than, less‑than, implies, caused‑by, before, after, …}.  
   - Assign each unique entity an integer ID; each relation type gets a one‑hot vector r∈{0,1}^{|R|}.  
   - Build a directed adjacency tensor **A**∈ℕ^{V×V×|R|} where A[i,j,k]=1 if triple (i, relation_k, j) appears. This is the *topological* representation: nodes = entities, edges = relational ties, preserving connectivity and hole‑like structures (e.g., cycles indicate contradictory constraints).

2. **Sparse dictionary learning (numpy‑only OMP)**  
   - Flatten each adjacency tensor into a vector x∈ℝ^{V·V·|R|} (binary).  
   - Initialise a dictionary **D**∈ℝ^{n_features×n_atoms} with random unit columns (n_features = V·V·|R|).  
   - For each training example (prompt + known‑good answer) run Orthogonal Matching Pursuit:  
        * residual ← x  
        * while ‖residual‖₂ > ε and |support| < S:  
            – j ← argmax_i |D_iᵀ·residual|  
            – add j to support  
            – α_support ← (D_supportᵀ·D_support)⁻¹·D_supportᵀ·x  
            – residual ← x − D_support·α_support  
   - Store the learned **D**; it captures prototypical relational patterns (features) with sparsity S (typically 3‑5 non‑zeros per example).

3. **Matched‑filter scoring**  
   - For a candidate answer, obtain its sparse code α_c by running the same OMP with the fixed **D** (no dictionary update).  
   - Compute a *template* t = mean α over all verified correct answers in the training set.  
   - Score = (α_cᵀ·t) / (‖α_c‖₂·‖t‖₂) (the normalized cross‑correlation, i.e., matched filter output).  
   - Higher scores indicate the candidate’s relational topology aligns with the known‑good pattern, maximising SNR against noise (incorrect or irrelevant relations).

**Parsed structural features**  
- Negations (“not”, “no”) → relation = not‑equals.  
- Comparatives (“more than”, “less than”) → greater‑than/less‑than.  
- Conditionals (“if … then”) → implies.  
- Numeric values → attached to entities, enabling magnitude‑based comparatives.  
- Causal claims (“because”, “leads to”) → caused‑by.  
- Ordering/temporal (“before”, “after”) → before/after.  
These are all encoded as edges in **A**, allowing transitivity (e.g., A·A) and constraint propagation (modus ponens on implies‑edges) to be performed with plain NumPy matrix multiplies.

**Novelty**  
Sparse coding of sentence graphs appears in unsupervised representation learning; matched filtering is classic in signal detection; topological graph‑based reasoning is used in some logic‑taxi networks. The *joint* use of a fixed sparse dictionary learned from logical graphs, followed by a matched‑filter comparison of sparse codes, has not been described in the NLP‑evaluation literature to my knowledge, making the combination novel.

**Ratings**  
Reasoning: 8/10 — captures relational topology and can propagate constraints, but limited to pre‑defined relation set.  
Metacognition: 6/10 — can output a confidence‑like score, yet lacks explicit self‑reflection on uncertainty.  
Hypothesis generation: 5/10 — primarily scores given candidates; generating new hypotheses would require sampling from the sparse dictionary, which is non‑trivial.  
Implementability: 9/10 — all steps use only NumPy (matrix multiply, OMP loops, regex) and Python stdlib; no external libraries or GPUs needed.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
