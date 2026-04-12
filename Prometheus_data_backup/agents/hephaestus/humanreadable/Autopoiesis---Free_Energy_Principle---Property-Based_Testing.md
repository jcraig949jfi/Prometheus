# Autopoiesis + Free Energy Principle + Property-Based Testing

**Fields**: Complex Systems, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T12:29:55.830998
**Report Generated**: 2026-03-31T17:15:56.401561

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a directed‑hypergraph \(G=(V,E)\).  
   - Nodes \(v_i\) are atomic propositions extracted with regex patterns for: negation (`not`, `no`), comparatives (`>`, `<`, `>=`, `<=`), conditionals (`if … then …`), causal cues (`because`, `leads to`), numeric literals, and ordering tokens (`first`, `before`, `after`).  
   - Hyper‑edges \(e_j\) encode the logical relation implied by the cue (e.g., a conditional yields an edge from antecedent node to consequent node).  
   - Store node features in a NumPy array \(F\in\mathbb{R}^{|V|\times d}\) (one‑hot for type, normalized numeric value, polarity).  
   - Store adjacency as a sparse Boolean matrix \(A\) where \(A_{ij}=1\) if there is an edge \(i\rightarrow j\).

2. **Autopoiesis closure score** – compute the proportion of nodes that have at least one incoming edge:  
   \[
   C_{\text{auto}} = \frac{1}{|V|}\sum_i \mathbb{1}\big[\sum_j A_{ji}>0\big].
   \]  
   Low closure indicates the answer produces propositions not supported by any other proposition (lack of self‑production).

3. **Free‑energy prediction error** – treat the prompt graph \(G_p\) as a generative model. For each node \(v_i\) in the candidate, compute the expected truth value \(\hat{t}_i\) by propagating truth values from prompt nodes through \(A_p\) (using linear threshold: \(\hat{t}= \text{sign}(A_p^\top t_p)\)).  
   - Let \(t_i\in\{0,1\}\) be the candidate’s asserted truth (1 if the node appears unnegated, 0 if negated).  
   - Prediction error per node: \(\epsilon_i = (t_i-\hat{t}_i)^2\).  
   - Free energy: \(F = \frac{1}{|V|}\sum_i \epsilon_i\).  
   Lower \(F\) means the candidate minimizes surprisal relative to the prompt.

4. **Property‑based testing robustness** – generate \(N\) random perturbations of the candidate graph (flip negation, add/subtract a small constant to numeric nodes, swap antecedent/consequent). For each perturbation compute \(F\). Apply a shrinking loop: repeatedly halve the perturbation magnitude until the change in \(F\) falls below a threshold \(\tau\). Record the minimal perturbation magnitude \(\delta_{\min}\) that yields a free‑energy increase > \(\theta\).  
   - Robustness score: \(R = \exp(-\lambda\,\delta_{\min})\) (larger \(R\) = more robust).

5. **Final score** (weighted sum, weights sum to 1):  
   \[
   S = w_1(1-F) + w_2 C_{\text{auto}} + w_3 R .
   \]  
   All operations use only NumPy (matrix multiplies, reductions) and the standard library (regex, random).

**Structural features parsed**  
Negations, comparatives, conditionals, causal cues, numeric values, ordering tokens, and conjunction/disjunction boundaries. These give the hyper‑edge types needed for constraint propagation (modus ponens on conditionals, transitivity on ordering, arithmetic propagation on numerics).

**Novelty**  
Using the free‑energy principle as a textual prediction‑error measure, autopoiesis‑derived closure as a self‑production metric, and property‑based testing’s shrinking to probe robustness is not found in existing literature; prior work treats each idea in isolation (e.g., logic‑based scoring, similarity metrics, or Bayesian surprise) but never combines them into a single scoring loop.

**Ratings**  
Reasoning: 7/10 — captures logical consistency and prediction error but relies on shallow regex parsing.  
Metacognition: 5/10 — closure provides a basic self‑monitoring signal, yet no higher‑order reflection on the scoring process itself.  
Hypothesis generation: 8/10 — property‑based testing actively creates and shrinks counter‑examples, yielding rich hypothesis probes.  
Implementability: 6/10 — all components are feasible with NumPy and stdlib, though robust hyper‑graph building and shrinking loops add non‑trivial engineering effort.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 6/10 |
| **Composite** | **6.67** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T17:13:50.200432

---

## Code

*No code was produced for this combination.*
