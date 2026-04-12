# Causal Inference + Adaptive Control + Metamorphic Testing

**Fields**: Information Science, Control Theory, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T12:56:28.070438
**Report Generated**: 2026-03-31T14:34:56.041004

---

## Nous Analysis

**1. Algorithm**  
The scorer builds a weighted directed acyclic graph (DAG) \(G=(V,E,W)\) where each node \(v_i\) encodes a proposition extracted from the prompt and each edge \(e_{ij}\) encodes a causal claim “\(v_i\) → \(v_j\)”.  
- **Parsing** (regex + spaCy‑style token patterns, stdlib only) yields tuples \((\text{type},\text{content})\) for: conditionals (`if … then …`), causal verbs (`causes`, `leads to`), negations (`not`, `no`), comparatives (`more than`, `less than`), numeric literals (`\d+(\.\d+)?\s*\w+`), and ordering relations (`before`, `after`, `greater than`, `less than`).  
- **Node creation**: each unique proposition becomes a node; its feature vector \(f_i\) is a one‑hot over predicate type plus a scalar numeric value if present.  
- **Edge initialization**: for every causal pattern, add edge \(e_{ij}\) with weight \(w_{ij}=1.0\).  
- **Metamorphic relation (MR) library**: a set of functions \(M_k\) that map an input perturbation \(\Delta x\) to an expected output change \(\Delta y\). Examples:  
  *If the antecedent numeric value is doubled, the consequent numeric value should double* (linear MR).  
  *If the antecedent is negated, the consequent truth value flips* (negation MR).  
  *If two antecedents are ordered, the consequent ordering must be preserved* (order MR).  
  Each MR is expressed as a constraint on edge weights: e.g., for a linear MR on edge \(e_{ij}\), \(w_{ij}\) should satisfy \(|w_{ij} - 2| < \epsilon\) when the antecedent is doubled.  
- **Adaptive control loop** (self‑tuning regulator): for each candidate answer \(a\):  
  1. Propagate truth values forward using Boolean matrix multiplication \(T = \sigma(W \otimes T_{prev})\) (where \(\sigma\) is a step‑function threshold) to derive implied propositions.  
  2. Compute violation vector \(v = |M_k(T) - \text{expected}_k|\) across all MRs.  
  3. Update edge weights with a simple stochastic‑approximation rule:  
     \[
     w_{ij} \leftarrow w_{ij} - \eta \cdot \frac{\partial \|v\|_1}{\partial w_{ij}}
     \]
     where the gradient is approximated by finite differences on the violation score (no neural net).  
  4. After processing all candidates, the final score for answer \(a\) is  
     \[
     S(a) = -\|v_a\|_1
     \]
     (lower total violation → higher score). All operations use only `numpy` for matrix arithmetic and the standard library for regex and control flow.

**2. Structural features parsed**  
- Conditional antecedents/consequents (`if … then …`).  
- Causal verbs and nominalizations (`causes`, `leads to`, `results in`).  
- Negation markers (`not`, `no`, `never`).  
- Comparative quantifiers (`more than`, `less than`, `twice`, `half`).  
- Numeric literals with optional units.  
- Ordering/temporal markers (`before`, `after`, `greater than`, `less than`).  
- Equality/symmetry statements (`equals`, `same as`).  

These are extracted into proposition nodes; causal patterns become edges; MRs are attached to edges based on the feature types present.

**3. Novelty**  
Causal inference (DAGs, do‑calculus) and metamorphic testing (input‑output relations) are well‑studied separately. Adaptive control techniques for online parameter tuning exist in control theory, but their direct application to continuously refine edge weights of a causal graph using violation‑driven stochastic approximation has not been reported in the NLP or software‑testing literature. Thus the combination constitutes a novel algorithmic framework for scoring reasoning answers.

**4. Ratings**  
Reasoning: 8/10 — The algorithm explicitly models cause‑effect structure and propagates constraints, capturing multi‑step logical dependencies better than surface‑matching baselines.  
Metacognition: 6/10 — It monitors its own violation signals and adapts weights, offering a rudimentary form of self‑assessment, but lacks higher‑order reflection on its uncertainty.  
Hypothesis generation: 5/10 — While MRs generate expected outcomes under perturbations, the system does not propose novel causal hypotheses beyond those present in the prompt.  
Implementability: 9/10 — All components rely on regex, NumPy matrix ops, and simple update rules; no external libraries or training data are required, making it straightforward to code and run.

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
