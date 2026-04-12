# Chaos Theory + Property-Based Testing + Sensitivity Analysis

**Fields**: Physics, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:29:19.142126
**Report Generated**: 2026-03-27T23:28:38.423718

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions from a candidate answer:  
   - *Conditionals*: `if (.+?) then (.+)` → implication `A → B`.  
   - *Comparatives*: `(.+?) is (greater|less|equal) than (.+)` → ordered relation.  
   - *Negations*: `\bnot\b(.+)` or `no (.+)` → ¬P.  
   - *Causal verbs*: `(.+?) causes (.+)` → cause→effect.  
   - *Numeric values*: capture numbers with optional units.  
   Each proposition is stored as a record `{id, type, args, numeric?}`.  

2. **Constraint graph** – Build a Boolean adjacency matrix **M** (size N×N) where M[i,j]=1 if proposition i implies j (from conditionals, causals, transitivity of ordering).  

3. **Property‑based perturbation** – For each numeric premise, generate *k* random perturbations ε∈[−δ,δ] (δ small, e.g., 0.01 of the value) using a shrinking strategy: if a perturbation leads to a violation, halve δ and re‑test (mirroring Hypothesis’s shrinking).  

4. **Forward propagation** – Treat the truth vector **x** (binary) as **x₀** (truth of premises after perturbation). Compute **x₁ = sign(M·x₀)** (numpy dot, threshold >0). Iterate until fixed point (or max 10 steps) to obtain the conclusion set **x\***.  

5. **Sensitivity (Lyapunov‑like) metric** – For each conclusion j, compute Δout = |x\*_j − x̂_j| where x̂_j is the conclusion from the unperturbed premises. Compute Δin = ‖ε‖₂. Estimate exponent λ = (1/k) Σ log(Δout/Δin + ε₀). Low λ indicates robustness.  

6. **Property satisfaction** – Check invariants generated from the answer itself (e.g., no proposition and its negation both true, transitivity of ordering). Let p = proportion of perturbations that satisfy all invariants.  

7. **Score** – `score = exp(−λ) * p`. Higher scores mean the answer is logically stable under small input changes and respects its own internal properties.  

**Structural features parsed** – conditionals, comparatives, negations, causal verbs, ordering relations, numeric values with units, quantifiers (all/some) via regex patterns.  

**Novelty** – While property‑based testing and sensitivity analysis appear in verification and adversarial NLP, coupling them with a Lyapunov‑exponent‑style divergence measure to score reasoning stability is not present in existing QA or explanation‑scoring tools.  

Reasoning: 8/10 — captures logical consistency and sensitivity to perturbations.  
Metacognition: 6/10 — limited self‑reflection beyond stability checks.  
Hypothesis generation: 7/10 — generates perturbations as hypotheses to test robustness.  
Implementability: 9/10 — relies only on regex, numpy, and stdlib; no external models.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-27T22:09:26.669292

---

## Code

*No code was produced for this combination.*
