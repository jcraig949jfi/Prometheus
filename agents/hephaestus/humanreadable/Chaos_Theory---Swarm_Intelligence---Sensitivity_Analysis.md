# Chaos Theory + Swarm Intelligence + Sensitivity Analysis

**Fields**: Physics, Biology, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:26:05.041970
**Report Generated**: 2026-03-27T17:21:24.865550

---

## Nous Analysis

**Algorithm**  
1. **Structural parsing** – Using only `re` we extract a set of atomic propositions from each candidate answer:  
   - *Predicates* (e.g., “X causes Y”, “X > Y”, “¬P”).  
   - *Numeric terms* (integers, floats, units).  
   - *Quantifiers* (“all”, “some”, “none”).  
   Each proposition is stored as a tuple `(type, args…)` and placed in a **feature vector** `f ∈ ℝ^d` where dimensions correspond to the presence/value of each proposition type (binary for logical flags, real for numbers).  

2. **Swarm initialization** – Create a particle swarm of `N` particles, each particle `p_i` initialized to the feature vector of a candidate answer plus a small random Gaussian noise (`numpy.random.normal`).  

3. **Fitness definition** – For a particle `x` we compute two sub‑scores:  
   - *Logical consistency* `C(x)`: a penalty derived from constraint propagation (transitivity of “>”, modus ponens on conditionals, contradiction detection via negation). Implemented as a sum of violated constraints, each weighted equally.  
   - *Sensitivity* `S(x)`: approximate Lyapunov exponent estimated by finite‑difference perturbation. For each dimension `j` we compute `Δx_j = ε·e_j` (ε=1e‑3), evaluate `C(x+Δx_j)`, and take the average absolute change `|C(x+Δx_j)-C(x)|/ε`. The exponent λ ≈ mean(log(|ΔC|/ε)). Lower λ ⇒ more robust.  

   Fitness `F(x) = -C(x) - α·λ(x)`, with α balancing terms (e.g., α=0.5).  

4. **Swarm update** – Standard PSO velocity‑position update:  
   `v_i ← w·v_i + c1·r1·(pbest_i - x_i) + c2·r2·(gbest - x_i)`  
   `x_i ← x_i + v_i`  
   where `w`, `c1`, `c2` are constants, `r1,r2∼U(0,1)`. After each iteration we recompute `C` and λ for the new position, update personal and global bests.  

5. **Scoring** – After `T` iterations the global best fitness `F(gbest)` is taken as the answer’s score; higher (less negative) indicates a robust, logically coherent response.  

**Parsed structural features** – negations (`not`, `¬`), comparatives (`>`, `<`, `=`), conditionals (`if … then …`), causal verbs (“causes”, “leads to”), numeric values with units, ordering relations (“first”, “last”), quantifiers (“all”, “some”, “none”).  

**Novelty** – While PSO and sensitivity analysis are known, coupling them with an explicit Lyapunov‑exponent estimate to measure robustness of logical propositions in a QA scoring setting has not been reported in the literature; the combination yields a differentiable‑free, purely algorithmic evaluator.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and sensitivity to perturbations, aligning with the required structural and numeric reasoning.  
Metacognition: 6/10 — the method can monitor its own swarm divergence (λ) but does not explicitly reason about uncertainty of its own estimates.  
Hypothesis generation: 5/10 — focuses on evaluating given answers; generating new candidate hypotheses would need an additional generative layer.  
Implementability: 9/10 — relies only on regex, NumPy arithmetic, and basic loops; no external libraries or APIs are needed.

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
