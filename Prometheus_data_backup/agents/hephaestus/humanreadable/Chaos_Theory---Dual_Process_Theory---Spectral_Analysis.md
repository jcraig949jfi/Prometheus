# Chaos Theory + Dual Process Theory + Spectral Analysis

**Fields**: Physics, Cognitive Science, Signal Processing
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T00:23:56.685690
**Report Generated**: 2026-04-01T20:30:43.409117

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Proposition Extraction** – Apply a set of regex patterns to the prompt and each candidate answer to extract atomic propositions \(p_i\) and label them with logical features: negation (`not/no`), comparative (`more/less`, `>`, `<`), conditional (`if … then`, `unless`), causal (`because`, `leads to`), ordering (`first`, `before`, `after`), and numeric tokens with units. Each proposition becomes a node in a directed graph \(G\).  
2. **Constraint‑Propagation Scoring (System 2)** – Build an adjacency matrix \(A\) where \(A_{ij}=1\) if \(p_i\) entails \(p_j\) (derived from conditionals, causals, transitivity). Compute the transitive closure via Floyd‑Warshall (numpy) to obtain reachability matrix \(R\). For each answer, count satisfied entailments (both prompt→answer and internal consistency) and divide by the total number of extracted entailments → \(S_{2}\in[0,1]\).  
3. **Heuristic Overlap Scoring (System 1)** – Compute a simple token‑overlap Jaccard index between prompt and answer (excluding stop‑words) → \(S_{1}\in[0,1]\).  
4. **Chaos‑Based Stability Measure** – Initialise a state vector \(x^{(0)}\) of length \(n\) (number of propositions) with \(x_i^{(0)} = S_{1}\) if \(p_i\) appears in answer else 0. Update with a logistic‑map‑style rule that incorporates the graph:  
   \[
   x^{(t+1)}_i = r\,x^{(t)}_i\bigl(1-x^{(t)}_i\bigr) + \alpha\sum_j A_{ji}x^{(t)}_j,
   \]  
   where \(r=3.9\) (chaotic regime) and \(\alpha=0.1\). Run for \(T=20\) iterations, compute the finite‑difference Jacobian approximation \(J\) and estimate the largest Lyapunov exponent \(\lambda\) via the log‑ratio of successive perturbation norms. Lower \(\lambda\) (more stable reasoning) yields a stability factor \(C = e^{-\lambda}\in(0,1]\).  
5. **Spectral Weighting** – Form a binary time‑series \(b_t\) indicating presence of any proposition at token position \(t\) (sliding window of 5 tokens). Apply numpy’s FFT to obtain power spectral density \(P(f)\). Compute the spectral centroid \(f_c = \sum f P(f) / \sum P(f)\). Low centroid → structured, deliberate answer → weight \(w_2 = 1 - f_c/f_{max}\); high centroid → noisy, intuitive answer → weight \(w_1 = f_c/f_{max}\). Normalize so \(w_1+w_2=1\).  
6. **Final Score** –  
   \[
   \text{Score}= w_1 S_{1} + w_2 S_{2}\, C .
   \]  
   All operations use only numpy and the Python standard library.

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations (temporal/seque ncing), and numeric values with units.

**Novelty**  
While logical‑form extraction and constraint propagation appear in prior QA scorers, coupling them with a chaos‑derived stability metric and using spectral analysis of token presence to dynamically balance intuitive vs. deliberative heuristic weights is not reported in existing literature; thus the combination is novel.

**Rating**  
Reasoning: 7/10 — captures logical consistency and sensitivity to perturbations but relies on simplified dynamical model.  
Metacognition: 6/10 — System 1/System 2 split mimics self‑monitoring, yet no explicit uncertainty calibration.  
Hypothesis generation: 5/10 — focuses on evaluating given answers; generating new hypotheses would require additional search.  
Implementability: 8/10 — all steps are concrete regex, numpy linear algebra, and FFT; feasible within constraints.

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
