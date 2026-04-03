# Causal Inference + Compositional Semantics + Sensitivity Analysis

**Fields**: Information Science, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:39:32.212283
**Report Generated**: 2026-04-02T04:20:11.833038

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a directed acyclic graph (DAG) \(G=(V,E)\) where nodes are atomic propositions (e.g., “X increases Y”, “¬Z”) extracted with regex patterns for negations, comparatives, conditionals, and causal verbs (“cause”, “lead to”, “result in”). Edges represent causal assertions; each edge carries a weight \(w_{ij}\in[0,1]\) initialized from a cue‑strength lexicon (e.g., “strongly” → 0.9, “may” → 0.4).  
2. **Compositional semantics** builds complex propositions by applying logical operators (AND, OR, NOT) to child nodes; the resulting node’s truth value is computed via deterministic functions:  
   - \(t_{\text{AND}} = \min(t_a,t_b)\)  
   - \(t_{\text{OR}} = \max(t_a,t_b)\)  
   - \(t_{\text{NOT}} = 1-t_a\)  
   These are stored in a NumPy array \(T\) aligned with a topological order of \(V\).  
3. **Causal inference** propagates truth values along edges using a linear‑threshold model: for each node \(v_j\),  
   \[
   t_j = \sigma\Big(\sum_{i\in\text{pa}(j)} w_{ij}\,t_i\Big),\quad \sigma(x)=\frac{1}{1+e^{-x}}
   \]  
   where \(\text{pa}(j)\) are parents in the DAG. This implements a soft do‑calculus: setting a node to 0 or 1 (intervention) overwrites its \(t\) before propagation.  
4. **Sensitivity analysis** perturbs each edge weight by \(\Delta w\sim\mathcal{U}[-\epsilon,\epsilon]\) (e.g., \(\epsilon=0.1\)) and recomputes \(T\) \(K\) times (K=20). The variance \(\mathrm{Var}(t_j)\) across runs quantifies robustness.  
5. **Scoring**: for each candidate answer, extract its target proposition node \(v_{ans}\). Compute the mean truth \(\bar t_{ans}\) over the K sensitivity runs and its standard deviation \(s_{ans}\). The final score is  
   \[
   S = \bar t_{ans} - \lambda\, s_{ans}
   \]  
   with \(\lambda=0.5\) to penalize fragile answers. Higher \(S\) indicates a answer that is both likely true under the causal model and robust to small specification changes.

**Parsed structural features** – negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then …”, “unless”), numeric thresholds (“>5”, “≤3”), causal verbs (“cause”, “lead to”, “result in”), ordering relations (“before”, “after”), and quantifiers (“all”, “some”).

**Novelty** – While causal DAGs with weighted edges resemble Markov Logic Networks and Probabilistic Soft Logic, the explicit integration of compositional truth‑functional propagation, do‑style interventions, and a sensitivity‑variance penalty for scoring answers is not present in existing open‑source reasoning scorers. It thus constitutes a novel combination.

**Ratings**  
Reasoning: 8/10 — captures causal logic and uncertainty quantitatively.  
Metacognition: 6/10 — algorithm does not monitor its own parsing errors.  
Hypothesis generation: 5/10 — limited to propagating given structures; no open‑ended hypothesis search.  
Implementability: 9/10 — relies only on regex, NumPy, and basic graph operations; straightforward to code.

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
