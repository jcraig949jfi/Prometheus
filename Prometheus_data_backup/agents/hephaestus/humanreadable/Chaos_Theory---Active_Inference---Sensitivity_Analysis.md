# Chaos Theory + Active Inference + Sensitivity Analysis

**Fields**: Physics, Cognitive Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T14:37:02.601156
**Report Generated**: 2026-04-01T20:30:44.040110

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Convert the question *Q* and each candidate answer *A* into a directed labeled graph *G = (V, E)*.  
   - Each node *vᵢ* stores a feature vector **fᵢ** = [type, polarity, numeric value (if any), unit]. Types are drawn from a fixed set: {negation, comparative, conditional, causal, ordering, quantifier, literal}.  
   - Edges encode logical relations extracted by regex patterns (e.g., “X → Y” for conditionals, “X ¬ Y” for negations, “X > Y” for comparatives, “X because Y” for causal). The adjacency matrix *A* (|V|×|V|) is a binary numpy array; edge types are stored in a parallel integer tensor *Etype*.  

2. **Baseline alignment** – Compute a structural similarity *S₀(Q,A)* = 1 – (GED(Q,A) / max(|V_Q|,|V_A|)), where GED is graph edit distance approximated by the Hungarian algorithm on node feature cosine similarity (numpy dot products).  

3. **Sensitivity perturbation** – For each numeric node, create a perturbed copy *A⁽ᵖ⁾* by adding ε = 1e‑3 to its value; for each negation/comparative node, flip its polarity. Re‑compute similarity *Sₚ*. The Jacobian approximation *J* = (Sₚ – S₀)/ε is a scalar; its absolute value measures local sensitivity.  

4. **Lyapunov‑like exponent** – λ = log(|J| + 1). Small λ indicates the answer’s logical structure is robust to tiny perturbations (chaos theory).  

5. **Active‑inference free energy** – Approximate expected free energy *F* = –S₀ + H(**f_A**), where *H* is the Shannon entropy of the distribution over node types in *A* (numpy histogram). Low *F* means the answer is both expected (high alignment) and parsimonious (low complexity).  

6. **Score** – *Score(A)* = –λ – F. Higher scores reward stability (low λ) and low free energy.  

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”, “equal to”), conditionals (“if … then …”, “unless”), causal verbs (“because”, “leads to”, “results in”), ordering relations (“first”, “before”, “after”), numeric values with units, quantifiers (“all”, “some”, “none”), and literal propositions.  

**Novelty**  
While graph‑based similarity and sensitivity analysis appear in QA evaluation, coupling a Lyapunov‑exponent‑like metric derived from logical‑graph perturbations with an active‑inference free‑energy term is not present in existing literature; the triple blend is therefore novel.  

**Ratings**  
Reasoning: 8/10 — captures dynamical stability and epistemic value via concrete numeric operations.  
Metacognition: 6/10 — the method can monitor its own sensitivity but lacks explicit self‑reflection loops.  
Hypothesis generation: 5/10 — focuses on scoring given hypotheses; generating new ones would require additional search.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and basic data structures; no external APIs or neural nets needed.

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
