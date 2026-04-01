# Cognitive Load Theory + Compositional Semantics + Sensitivity Analysis

**Fields**: Cognitive Science, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T13:18:04.541828
**Report Generated**: 2026-03-31T23:05:19.138271

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositional Semantics)** – Convert each candidate answer into a directed labeled graph \(G=(V,E)\).  
   - Each clause becomes a node \(v_i\) with a feature dict: `{polarity∈{+1,−1}, type∈{fact,conditional,causal}, numeric∈ℝ∪{None}, quantifier∈{∀,∃,None}}`.  
   - Edges encode logical relations extracted via regex patterns:  
     * `if … then …` → edge \(v_i \xrightarrow{\text{cond}} v_j\)  
     * `because …` → edge \(v_i \xrightarrow{\text{cause}} v_j\)  
     * comparatives (`>`, `<`, `≥`, `≤`) → edge \(v_i \xrightarrow{\text{comp}} v_j\) with attached threshold.  
   - Store adjacency lists and a list of numeric constraints \(C=\{ (v_i,op,v_j,val) \}\).

2. **Constraint Propagation (Cognitive Load Theory – chunking)** – Perform a bounded forward‑chaining pass:  
   - Initialize a work‑list with all fact nodes.  
   - At each iteration, pop up to **K** nodes (working‑memory chunk size, e.g., K=4).  
   - For each popped node, apply unit‑propagation rules:  
     * Modus ponens on conditional edges → add consequent as fact if antecedent true.  
     * Transitivity on ordering/comparative edges → derive new comparatives.  
     * Consistency check: if a node receives both polarities +1 and −1, mark a conflict.  
   - Track **load penalty** \(L = \sum_{t} \max(0, |W_t|-K)\) where \(W_t\) is the work‑list size at step t.  

3. **Sensitivity Analysis** – Generate **M** perturbed copies of the original graph:  
   - Randomly flip polarity of a subset of nodes (negation sensitivity).  
   - Add Gaussian noise \(\mathcal{N}(0,\sigma^2)\) to each numeric value (numeric sensitivity).  
   - Re‑run the bounded propagation on each copy, obtaining satisfaction scores \(s^{(m)}\) (fraction of constraints satisfied).  
   - Compute sensitivity term \(S = \operatorname{std}\{s^{(m)}\}_{m=1}^M\).  

4. **Scoring Logic** – Base consistency score \(B = 1 - \frac{\#\text{conflicts}}{|V|}\).  
   Final score for a candidate answer:  
   \[
   \text{Score}= B - \lambda_L \frac{L}{L_{\max}} - \lambda_S S,
   \]
   where \(\lambda_L,\lambda_S\) are weighting hyper‑parameters (set to 0.3 each) and \(L_{\max}\) is the worst‑case load observed across all candidates.

**Structural Features Parsed** – negations, comparatives, conditionals (`if‑then`), causal cues (`because`, `leads to`), ordering/temporal relations (`before`, `after`), numeric values with units, quantifiers (`all`, `some`, `none`), conjunction/disjunction markers.

**Novelty** – While semantic‑graph parsing and constraint propagation appear separately in NLP‑reasoning work, the explicit integration of a working‑memory chunking penalty (Cognitive Load Theory) together with a sensitivity‑analysis robustness term is not present in existing public tools; most systems either score logical consistency or compute perturbation robustness, but not both within a single bounded‑memory algorithm.

**Rating**  
Reasoning: 8/10 — captures logical consistency, chaining, and robustness in a principled way.  
Metacognition: 6/10 — load penalty mimics awareness of resource limits but lacks explicit self‑monitoring.  
Hypothesis generation: 5/10 — the algorithm evaluates given candidates; it does not propose new hypotheses.  
Implementability: 9/10 — relies only on regex, numpy for numeric ops, and stdlib data structures; easily coded in <200 lines.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T21:52:22.899422

---

## Code

*No code was produced for this combination.*
